import enum
import dataclasses
from typing import Optional


class RoomID(str): pass


class Token(str): pass


class MemberID(str): pass


class RoomAction(enum.Enum):
    CREATE = "Open room"
    ADD_GUESTS = "Add guests"
    REMOVE_GUESTS = "Remove guests"
    DELETE = "Delete room"

@dataclasses.dataclass
class Fields:
    roomid: Optional[str] = None

    def to_dict(self):
        return self.__dict__


@dataclasses.dataclass
class Room:
    ID: RoomID
    Title: str

    def to_dict(self):
        return self.__dict__

@dataclasses.dataclass
class Member:
    ID: MemberID
    Name: str
    Mail: str
    IsModerator: bool

    def to_dict(self):
        return self.__dict__



__all__ = [cls.__name__ for cls in [
    RoomID,
    Token,
    MemberID,
    RoomAction,
    Fields,
    Room,
    Member
]]