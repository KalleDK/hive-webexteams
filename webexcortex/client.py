from typing import Iterable, Protocol, Optional, List

from .datatypes import MemberID, RoomID, Room, Member


#region Protocols for typing check

class WTRoom(Protocol):
    id: str
    title: str


class WTMembership(Protocol):
    id: str
    personEmail: str
    personDisplayName: str
    isModerator: bool


class RoomsAPI(Protocol):
    def create(self, title: str, teamId: Optional[str] = None) -> WTRoom: ...
    
    def delete(self, roomId: str) -> None: ...

    def list(self, type: str = None) -> Iterable[WTRoom]: ...

    def get(self, roomId: str) -> WTRoom: ...


class MembershipsAPI(Protocol):
    def create(self, roomId: str, personEmail: str, isModerator: bool = False) -> WTMembership: ...

    def delete(self, membershipId: str) -> None: ...

    def list(self, roomId: str) -> Iterable[WTMembership]: ...


class TeamsAPI(Protocol):
    rooms: RoomsAPI
    memberships: MembershipsAPI

#endregion


class Client:

    room_api: RoomsAPI
    membership_api: MembershipsAPI

    def __init__(self, room_api: RoomsAPI, memberships_api: MembershipsAPI) -> None:
        self.room_api = room_api
        self.membership_api = memberships_api
    
    def create_room(self, title: str):
        room = self.room_api.create(title=title)
        return Room(
            ID=RoomID(room.id),
            Title=room.title,
        )

    def delete_room(self, roomid: RoomID):
        if roomid is None or len(roomid) == 0:
            raise Exception(f"Invalid roomid [{roomid}]")
        self.room_api.delete(roomid)

    def get_room(self, roomid: RoomID):
        if roomid is None or len(roomid) == 0:
            raise Exception(f"Invalid roomid [{roomid}]")
        room: WTRoom = self.room_api.get(roomId=roomid)
        return Room(
            ID=RoomID(room.id),
            Title=room.title
        )

    def get_rooms(self) -> List[Room]:
        return [
            Room(
                ID=RoomID(r.id),
                Title=r.title,
            ) for r in self.room_api.list(type="group")
        ]

    def add_members(self, roomID: RoomID, memberMails: Iterable[str], isModerator: bool = False):
        return [
            Member(
                ID=MemberID(member.id),
                Mail=member.personEmail,
                IsModerator=member.isModerator,
                Name=member.personDisplayName,
            ) for member in [
                self.membership_api.create(roomId=roomID, personEmail=memberMail, isModerator=isModerator) for memberMail in memberMails
            ]
        ]
        
    def remove_members(self, roomID: RoomID, memberIDs : Iterable[MemberID]):
        for memberID in memberIDs:
            self.membership_api.delete(membershipId=memberID)

    def get_members(self, roomID: RoomID):
        return [
            Member(
                ID=MemberID(member.id),
                Mail=member.personEmail,
                Name=member.personDisplayName,
                IsModerator=member.isModerator
            ) for member in self.membership_api.list(roomId=str(roomID))
        ]
        

__all__ = [cls.__name__ for cls in [
    Client
]]