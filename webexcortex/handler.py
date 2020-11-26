import dataclasses
import abc
from typing import Any, List, Dict, Protocol, Iterable

from .datatypes import RoomAction, Fields, RoomID, Room, Member, MemberID


class IRequest(Protocol):

    @abc.abstractproperty
    def action(self) -> RoomAction: ...

    @abc.abstractproperty
    def roomid(self) -> RoomID: ...

    @abc.abstractproperty
    def title(self) -> str: ...

    @abc.abstractproperty
    def guests(self) -> Iterable[str]: ...

    @abc.abstractproperty
    def owners(self) -> Iterable[str]: ...


class IClient(Protocol):
    
    def create_room(self, title: str) -> Room: ...

    def delete_room(self, roomid: RoomID): ...

    def get_room(self, roomid: RoomID) -> Room: ...

    def get_rooms(self) -> Iterable[Room]: ...

    def add_members(self, roomID: RoomID, memberMails: Iterable[str], isModerator: bool = False) -> Iterable[Member]: ...
        
    def remove_members(self, roomID: RoomID, memberIDs : Iterable[MemberID]): ...

    def get_members(self, roomID: RoomID) -> Iterable[Member]: ...


@dataclasses.dataclass
class FullReport:
    message: str
    fields: Fields = dataclasses.field(default_factory=Fields)
    tags: List[str] = dataclasses.field(default_factory=list)
    events: List[Dict[str, Any]] = dataclasses.field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'message': self.message,
            'fields': self.fields.to_dict(),
            'tags': self.tags,
            'events': self.events
        }


class RoomExistsError(RuntimeError):
    pass


def _room_found(room: Room):
    return {"room found" : room.to_dict()}

def _room_created(room: Room):
    return {"room create" : room.to_dict()}

def _room_deleted(room: Room):
    return {"room deleted" : room.to_dict()}

def _owners_added(members: Iterable[Member]):
    return { "owners added" : [member.to_dict() for member in members] }

def _members_in_room(members: Iterable[Member]):
    return { "members in room" : [member.to_dict() for member in members] }

def _guests_in_room(members: Iterable[Member]):
    return { "guests in room" : [member.to_dict() for member in members] }

def _guests_added(members: Iterable[Member]):
    return { "guests added" : [member.to_dict() for member in members] }

def _guests_removed(members: Iterable[Member]):
    return { "guests removed" : [member.to_dict() for member in members] }

def _guests_not_in_room(guestmails: Iterable[str]):
    return { "guests not in room" : guestmails }



class Handler:
    def __init__(self, client: IClient) -> None:
        self.client = client

    def create_room(self, req: IRequest):
        actions = []

        # Testing that either we don't have a roomid, or if the provided roomid doesn't exists
        try:
            room = self.client.get_room(req.roomid)
        except Exception:
            pass
        else:
            raise Exception(f"Room already exists with title [{room.Title}]")
            
        # Create room
        room = self.client.create_room(req.title)
        actions.append(_room_created(room))

        # Add owners
        owners_added = self.client.add_members(room.ID, req.owners, isModerator=True)
        actions.append(_owners_added(owners_added))

        # Add guests
        guests_added = self.client.add_members(room.ID, req.guests, isModerator=False)
        actions.append(_guests_added(guests_added))

        # Return report
        return FullReport(
            message=f"Room created {room.Title}",
            fields=Fields(
                roomid=room.ID
            ),
            events=actions
        )

    def delete_room(self, req: IRequest):
        actions = []

        room = self.client.get_room(req.roomid)
        actions.append(_room_found(room))

        self.client.delete_room(room.ID)
        actions.append(_room_deleted(room))

        return FullReport(
            message=f"Room deleted {req.roomid}",
            fields=Fields(
                roomid=""
            ),
            events=actions
        )

    def add_guests(self, req: IRequest):
        
        actions = []

        room = self.client.get_room(req.roomid)
        actions.append(_room_found(room))

        members = self.client.get_members(room.ID)
        actions.append(_members_in_room(members))

        membermails = [m.Mail for m in members]
        guestmails = [guestmail for guestmail in req.guests if guestmail not in membermails]
        actions.append(_guests_not_in_room(guestmails))
        
        guests_added = self.client.add_members(room.ID, guestmails, isModerator=False)
        actions.append(_guests_added(guests_added))

        # Return report
        return FullReport(
            message=f"Guests added to {room.Title}",
            events=actions
        )

    def remove_guests(self, req: IRequest):
        actions = []

        room = self.client.get_room(req.roomid)
        actions.append(_room_found(room))

       
        members = self.client.get_members(room.ID)
        actions.append(_members_in_room(members))

        guests = [member for member in members if member.Mail in req.guests]
        actions.append(_guests_in_room(guests))

        self.client.remove_members(room.ID, [g.ID for g in guests])
        actions.append(_guests_removed(guests))

        # Return report
        return FullReport(
            message=f"Guests removed from {room.Title}",
            events=actions
        )

    def handle(self, req: IRequest):
        action = req.action
        if action == RoomAction.CREATE:
            return self.create_room(req)
        if action == RoomAction.DELETE:
            return self.delete_room(req)
        if action == RoomAction.ADD_GUESTS:
            return self.add_guests(req)
        if action == RoomAction.REMOVE_GUESTS:
            return self.remove_guests(req)
        raise Exception(f"Invalid action {action}")


__all__ = [cls.__name__ for cls in [
    Handler,
    RoomExistsError,
]]