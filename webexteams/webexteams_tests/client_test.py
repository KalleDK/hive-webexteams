import unittest

from webexteams.datatypes import Member, MemberID, RoomID, Room
from webexteams.client import Client
from unittest.mock import MagicMock, patch, call

InvalidRoomID = RoomID("")

ValidRoomID = RoomID("validid")
ValidRoomTitle = "new title"
ValidRoom = Room(ID=ValidRoomID, Title=ValidRoomTitle)

ExtraRoomID = RoomID("extraroomid")
ExtraRoomTitle = "extra room"
ExtraRoom = Room(
    ID=ExtraRoomID,
    Title=ExtraRoomTitle
)

ValidMemberID = MemberID("validmemberid")
ValidMemberMail = "valid@mail.com"
ValidMemberName = "validname"
ValidIsModerator = True
ValidMember = Member(
    ID=ValidMemberID,
    Name=ValidMemberName,
    Mail=ValidMemberMail,
    IsModerator=ValidIsModerator
)

ModMemberID = MemberID("Modmemberid")
ModMemberMail = "Mod@mail.com"
ModMemberName = "Modname"
ModIsModerator = True
ModMember = Member(
    ID=ModMemberID,
    Name=ModMemberName,
    Mail=ModMemberMail,
    IsModerator=ModIsModerator
)

ExtraMemberID = MemberID("Extramemberid")
ExtraMemberMail = "Extra@mail.com"
ExtraMemberName = "Extraname"
ExtraIsModerator = False
ExtraMember = Member(
    ID=ExtraMemberID,
    Name=ExtraMemberName,
    Mail=ExtraMemberMail,
    IsModerator=ExtraIsModerator
)

class TestClientRoom(unittest.TestCase):
    @patch('webexteams.client.MembershipsAPI', autospec=True, spec_set=True)
    @patch("webexteams.client.RoomsAPI", autospec=True, spec_set=True)
    def test_delete_room(self, room_cls, membership_cls):
        
        room_mock = room_cls()
        membership_mock = membership_cls()
        
        uut = Client(room_mock, membership_mock)
        uut.delete_room(ValidRoomID)

        assert membership_mock.mock_calls == []
        assert room_mock.method_calls == [
            call.delete(str(ValidRoomID))
        ]

    @patch('webexteams.client.MembershipsAPI', autospec=True, spec_set=True)
    @patch("webexteams.client.RoomsAPI", autospec=True, spec_set=True)
    def test_delete_room_invalidid(self, room_cls, membership_cls):
        
        room_mock = room_cls()
        membership_mock = membership_cls()
        
        uut = Client(room_mock, membership_mock)
        with self.assertRaises(Exception):
            uut.delete_room(InvalidRoomID)

        assert membership_mock.mock_calls == []
        assert room_mock.method_calls == []

    @patch('webexteams.client.MembershipsAPI', autospec=True, spec_set=True)
    @patch("webexteams.client.RoomsAPI", autospec=True, spec_set=True)
    def test_create_room(self, room_cls, membership_cls):
        
        room_mock = room_cls()
        room_mock.create.return_value = MagicMock(id=str(ValidRoomID), title=ValidRoomTitle)
        membership_mock = membership_cls()
        
        uut = Client(room_mock, membership_mock)
        room = uut.create_room(ValidRoomTitle)

        self.assertListEqual(membership_mock.mock_calls, [], "memberships should not be touched")
        self.assertListEqual(room_mock.method_calls, [call.create(title=ValidRoomTitle)], "only a single call to create")
        self.assertEqual(room, ValidRoom, "invalid room returned")

    @patch('webexteams.client.MembershipsAPI', autospec=True, spec_set=True)
    @patch("webexteams.client.RoomsAPI", autospec=True, spec_set=True)
    def test_get_room(self, room_cls, membership_cls):
        
        room_mock = room_cls()
        room_mock.get.return_value = MagicMock(id=str(ValidRoomID), title=ValidRoomTitle)
        membership_mock = membership_cls()
        
        uut = Client(room_mock, membership_mock)
        room = uut.get_room(ValidRoomID)

        self.assertListEqual(membership_mock.mock_calls, [], "memberships should not be touched")
        self.assertListEqual(room_mock.method_calls, [call.get(roomId=str(ValidRoomID))], "only a single call to get")
        self.assertEqual(room, ValidRoom, "invalid room returned")

    @patch('webexteams.client.MembershipsAPI', autospec=True, spec_set=True)
    @patch("webexteams.client.RoomsAPI", autospec=True, spec_set=True)
    def test_get_room_exception(self, room_cls, membership_cls):
        
        room_mock = room_cls()
        room_mock.get.return_value = MagicMock(id=str(ValidRoomID), title=ValidRoomTitle)
        membership_mock = membership_cls()
        
        uut = Client(room_mock, membership_mock)

        with self.assertRaises(Exception):
            uut.get_room(InvalidRoomID)

        assert membership_mock.mock_calls == []
        assert room_mock.method_calls == []

    @patch('webexteams.client.MembershipsAPI', autospec=True, spec_set=True)
    @patch("webexteams.client.RoomsAPI", autospec=True, spec_set=True)
    def test_get_rooms(self, room_cls, membership_cls):
        
        room_mock = room_cls()
        room_mock.list.return_value = [
            MagicMock(id=str(ValidRoomID), title=ValidRoomTitle),
            MagicMock(id=str(ExtraRoomID), title=ExtraRoomTitle)
            ]
        membership_mock = membership_cls()
        
        uut = Client(room_mock, membership_mock)
        rooms = uut.get_rooms()

        self.assertListEqual(membership_mock.mock_calls, [], "memberships should not be touched")
        self.assertListEqual(room_mock.method_calls, [call.list(type="group")], "only a single call to get")
        self.assertListEqual(rooms, [ValidRoom, ExtraRoom], "invalid rooms returned")


class TestClientMemberships(unittest.TestCase):
    @patch('webexteams.client.MembershipsAPI', autospec=True, spec_set=True)
    @patch("webexteams.client.RoomsAPI", autospec=True, spec_set=True)
    def test_get_members(self, room_cls, membership_cls):
        
        room_mock = room_cls()
        
        membership_mock = membership_cls()
        membership_mock.list.return_value = [
            MagicMock(
                id=str(ValidMemberID),
                personEmail=ValidMemberMail,
                personDisplayName=ValidMemberName,
                isModerator=ValidIsModerator
            ),
            MagicMock(
                id=str(ExtraMemberID),
                personEmail=ExtraMemberMail,
                personDisplayName=ExtraMemberName,
                isModerator=ExtraIsModerator
            ),
            MagicMock(
                id=str(ModMemberID),
                personEmail=ModMemberMail,
                personDisplayName=ModMemberName,
                isModerator=ModIsModerator
            ),
        ]

        uut = Client(room_mock, membership_mock)
        members = uut.get_members(ValidRoomID)

        self.assertListEqual(membership_mock.mock_calls, [call.list(roomId=str(ValidRoomID))], "only a single call to list")
        self.assertListEqual(room_mock.method_calls, [], "rooms should not be touched")
        self.assertListEqual(members, [ValidMember, ExtraMember, ModMember], "invalid members returned")

    @patch('webexteams.client.MembershipsAPI', autospec=True, spec_set=True)
    @patch("webexteams.client.RoomsAPI", autospec=True, spec_set=True)
    def test_add_members(self, room_cls, membership_cls):
        
        room_mock = room_cls()
        membership_mock = membership_cls()
        membership_mock.create.side_effect = [
            MagicMock(
                id=str(ExtraMemberID),
                personEmail=ExtraMemberMail,
                personDisplayName=ExtraMemberName,
                isModerator=False
            ),
        ]

        mails = [
            ExtraMemberMail
        ]
        uut = Client(room_mock, membership_mock)
        members = uut.add_members(ValidRoomID, mails, False)

        self.assertListEqual(membership_mock.mock_calls, [
            call.create(roomId=ValidRoomID, personEmail=ExtraMemberMail, isModerator=False)
        ], "only one call to create")
        self.assertListEqual(room_mock.method_calls, [], "rooms should not be touched")
        self.assertListEqual(members, [ExtraMember], "invalid members returned")

    @patch('webexteams.client.MembershipsAPI', autospec=True, spec_set=True)
    @patch("webexteams.client.RoomsAPI", autospec=True, spec_set=True)
    def test_add_members_mods(self, room_cls, membership_cls):
        
        room_mock = room_cls()
        membership_mock = membership_cls()
        membership_mock.create.side_effect = [
            MagicMock(
                id=str(ValidMemberID),
                personEmail=ValidMemberMail,
                personDisplayName=ValidMemberName,
                isModerator=True
            ),
            MagicMock(
                id=str(ModMemberID),
                personEmail=ModMemberMail,
                personDisplayName=ModMemberName,
                isModerator=True
            ),
        ]

        mails = [
            ValidMemberMail,
            ModMemberMail
        ]
        uut = Client(room_mock, membership_mock)
        members = uut.add_members(ValidRoomID, mails, True)

        self.assertListEqual(membership_mock.mock_calls, [
            call.create(roomId=ValidRoomID, personEmail=ValidMemberMail, isModerator=True),
            call.create(roomId=ValidRoomID, personEmail=ModMemberMail, isModerator=True)
        ], "only two calls to create")
        self.assertListEqual(room_mock.method_calls, [], "rooms should not be touched")
        self.assertListEqual(members, [ValidMember, ModMember], "invalid members returned")

    @patch('webexteams.client.MembershipsAPI', autospec=True, spec_set=True)
    @patch("webexteams.client.RoomsAPI", autospec=True, spec_set=True)
    def test_remove_members(self, room_cls, membership_cls):
        
        room_mock = room_cls()
        membership_mock = membership_cls()

        ids = [
            ValidMemberID,
            ModMemberID,
            ExtraMemberID
        ]
        uut = Client(room_mock, membership_mock)
        uut.remove_members(ValidRoomID, ids)

        self.assertListEqual(membership_mock.mock_calls, [
            call.delete(membershipId=ValidMemberID),
            call.delete(membershipId=ModMemberID),
            call.delete(membershipId=ExtraMemberID)
        ], "only three calls to create")
        self.assertListEqual(room_mock.method_calls, [], "rooms should not be touched")
        

if __name__ == '__main__':
    unittest.main()