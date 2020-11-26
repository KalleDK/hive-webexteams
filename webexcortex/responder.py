import json
from typing import List, NoReturn, Protocol, TypeVar, Type, cast, Sized, Any, Dict

from .datatypes import Fields, RoomID, RoomAction


#region Protocols

class IParams(Protocol):
    def get_param(self, name: str, default: Any = None) -> Any: ...


class IReport(Protocol):
    fields: Fields

    def to_dict(self) -> Dict[str, Any]: ...


class IWorker(IParams, Protocol):
    def report(self, output, ensure_ascii=False): ...

    def error(self, message, ensure_ascii=False) -> NoReturn: ...

T = TypeVar('T')

#endregion


#region Param Helper

class ParamError(RuntimeError):
    pass


def _get_param(resp: IParams, name: str, cls: Type[T], empty_ok: bool = False) -> T:
    val = resp.get_param(name, default=None)
    if val is None:
        raise ParamError(f'Missing parameter: "{name}"')

    if not isinstance(val, cls):
        raise ParamError(f'Invalid parameter type: "{name}" is [{type(val).__name__}] expected [{cls.__name__}]')

    if not empty_ok and isinstance(val, Sized) and len(val) == 0:
        raise ParamError(f'Invalid parameter value: "{name}" must not be empty')
        
    return cast(T, val)

#endregion


class Request:

    resp: IParams

    def __init__(self, resp: IParams) -> None:
        self.resp = resp

   
    @property
    def roomid(self):
        return RoomID(_get_param(self.resp, 'data.customFields.webexroomid.string', str))

    @property
    def case_title(self):
        return _get_param(self.resp, 'data.title', str)
    
    @property
    def case_id(self):
        return _get_param(self.resp, 'data.caseId', int)
    
    @property
    def organization(self):
        return _get_param(self.resp, 'config.organization', str)

    @property
    def title(self):
        return f"{self.organization} #{self.case_id} - {self.case_title}"
    
    @property
    def tags(self) -> List[str]:
        return _get_param(self.resp, 'data.tags', list)

    @property
    def guests(self) -> List[str]:
        prefix = "wbx="
        prefix_len = len(prefix)
        return [ json.loads(tag[prefix_len:]) for tag in self.tags if tag.startswith(prefix) ]
    
    @property
    def owners(self):
        return [ _get_param(self.resp, 'data.owner', str) ]
    
    @property
    def action(self):
        return RoomAction(_get_param(self.resp, 'data.customFields.webexteams.string', str))


class Config:

    resp: IParams

    def __init__(self, resp: IParams) -> None:
        self.resp = resp

    @property
    def webex_bot_token(self):
        return _get_param(self.resp, 'config.webex_bot_token', str)


class Responder():

    worker: IWorker

    def __init__(self, worker: IWorker) -> None:
        self.worker = worker

    @property
    def request(self):
        return Request(self.worker)
    
    @property
    def config(self):
        return Config(self.worker)

    @staticmethod
    def add_fields_ops(ops: List[Any], fields: Fields):
        if fields.roomid is not None:
            ops.append(
                {
                    "type": 'AddCustomFields',
                    "name": 'webexroomid',
                    "value": fields.roomid,
                    "tpe": "string"
                }
            )
          
    def report(self, report: IReport, ensure_ascii: bool = False):
        operations = []

        self.add_fields_ops(operations, report.fields)
        
        output = {
            'success': True,
            'full': report.to_dict(),
            'operations': operations
        }

        self.worker.report(
            output=output,
            ensure_ascii=ensure_ascii
        )

    def error(self, e: Exception, ensure_ascii: bool = False):
        self.worker.error(message=f"{str(e)}", ensure_ascii=ensure_ascii)


__all__ = [cls.__name__ for cls in [
    ParamError,
    Request,
    Config,
    Responder
]]