import unittest
import json
from webexcortex.datatypes import Fields, Member, MemberID, RoomAction, RoomID, Room
from webexcortex.handler import FullReport, Handler
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

class TestHandler(unittest.TestCase):
    @patch('webexcortex.client.Client', autospec=True, spec_set=True)
    def test_delete_room(self, client_cls):
        req = MagicMock(
            action=RoomAction.DELETE,
            roomid=ValidRoomID
        )
        client_mock = client_cls(None, None)
        client_mock.get_room.return_value = ValidRoom
        
        uut = Handler(client_mock)
        report = uut.handle(req)

        self.assertListEqual(client_mock.method_calls, [
            call.get_room('validid'),
            call.delete_room('validid')
        ])

        want = FullReport(
            message='Room deleted validid',
            fields=Fields(roomid=''),
            events=[
                {'room found': {'ID': 'validid', 'Title': 'new title'}},
                {'room deleted': {'ID': 'validid', 'Title': 'new title'}}
            ]
        )

        self.assertEqual(report, want)

    @patch('webexcortex.client.Client', autospec=True, spec_set=True)
    def test_add_guests(self, client_cls):
        req = MagicMock(
            action=RoomAction.ADD_GUESTS,
            roomid=ValidRoomID,
            guests=[ExtraMemberMail],
        )
        client_mock = client_cls(None, None)
        client_mock.get_room.return_value = ValidRoom
        client_mock.get_members.return_value = [ValidMember]
        client_mock.add_members.return_value = [ExtraMember]
        
        uut = Handler(client_mock)
        report = uut.handle(req)

        self.assertListEqual(client_mock.method_calls, [
            call.get_room(ValidRoomID),
            call.get_members(ValidRoomID),
            call.add_members(ValidRoomID, [ExtraMemberMail], isModerator=False)
        ])

        want = FullReport(
            message=f'Guests added to new title',
            events=[
                {'room found': {'ID': 'validid', 'Title': 'new title'}},
                {'members in room': [
                        {'ID': 'validmemberid', 'Name': 'validname', 'Mail': 'valid@mail.com', 'IsModerator': True}
                ]},
                {'guests not in room': ['Extra@mail.com']},
                {'guests added': [
                    {'ID': 'Extramemberid', 'Name': 'Extraname', 'Mail': 'Extra@mail.com', 'IsModerator': False}
                ]}
            ]
        )

        self.assertEqual(report, want, msg=report.to_dict())

    @patch('webexcortex.client.Client', autospec=True, spec_set=True)
    def test_remove_guests(self, client_cls):
        req = MagicMock(
            action=RoomAction.REMOVE_GUESTS,
            roomid=ValidRoomID,
            guests=[ExtraMemberMail],
        )
        client_mock = client_cls(None, None)
        client_mock.get_room.return_value = ValidRoom
        client_mock.get_members.return_value = [ValidMember, ExtraMember]
        
        uut = Handler(client_mock)
        report = uut.handle(req)

        self.assertListEqual(client_mock.method_calls, [
            call.get_room(ValidRoomID),
            call.get_members(ValidRoomID),
            call.remove_members(ValidRoomID, [ExtraMemberID])
        ])

        want = FullReport(
            message=f'Guests removed from new title',
            events=[
                {'room found': {'ID': 'validid', 'Title': 'new title'}},
                {'members in room': [
                        {'ID': 'validmemberid', 'Name': 'validname', 'Mail': 'valid@mail.com', 'IsModerator': True},
                        {"ID": "Extramemberid", "Name": "Extraname", "Mail": "Extra@mail.com", "IsModerator": False}
                ]},
                {'guests in room': [
                    {"ID": "Extramemberid", "Name": "Extraname", "Mail": "Extra@mail.com", "IsModerator": False}
                ]},
                {'guests removed': [
                    {'ID': 'Extramemberid', 'Name': 'Extraname', 'Mail': 'Extra@mail.com', 'IsModerator': False}
                ]}
            ]
        )

        self.assertEqual(report, want, msg=json.dumps(report.to_dict(), indent=2))

    @patch('webexcortex.client.Client', autospec=True, spec_set=True)
    def test_create_room(self, client_cls):
        req = MagicMock(
            action=RoomAction.CREATE,
            roomid="",
            title=ValidRoomTitle,
            owners=[ValidMemberMail],
            guests=[ExtraMemberMail],
        )
        client_mock = client_cls(None, None)
        client_mock.get_room.side_effect = Exception("error")
        client_mock.create_room.return_value = ValidRoom
        client_mock.add_members.side_effect = [[ValidMember], [ExtraMember]]
        
        uut = Handler(client_mock)
        report = uut.handle(req)

        self.assertListEqual(client_mock.method_calls, [
            call.get_room(''),
            call.create_room('new title'),
            call.add_members('validid', ['valid@mail.com'], isModerator=True),
            call.add_members('validid', ['Extra@mail.com'], isModerator=False)
        ])

        want = FullReport(
            message='Room created new title',
            fields=Fields(roomid='validid'),
            events=[
                {'room create': {'ID': 'validid', 'Title': 'new title'}},
                {'owners added': [
                    {'ID': 'validmemberid', 'Name': 'validname', 'Mail': 'valid@mail.com', 'IsModerator': True}
                ]},
                {'guests added': [
                    {'ID': 'Extramemberid', 'Name': 'Extraname', 'Mail': 'Extra@mail.com', 'IsModerator': False}
                ]}
            ]
        )

        self.assertEqual(report, want, msg=repr(report))

    @patch('webexcortex.client.Client', autospec=True, spec_set=True)
    def test_create_room_exception(self, client_cls):
        req = MagicMock(
            action=RoomAction.CREATE,
            roomid=ValidRoomID,
            title=ValidRoomTitle,
            owners=[ValidMemberMail],
            guests=[ExtraMemberMail],
        )
        client_mock = client_cls(None, None)
        client_mock.get_room.side_effect = [ValidRoom]
        client_mock.create_room.return_value = ValidRoom
        client_mock.add_members.side_effect = [[ValidMember], [ExtraMember]]
        

        uut = Handler(client_mock)
        with self.assertRaises(Exception):
            uut.handle(req)

    @patch('webexcortex.client.Client', autospec=True, spec_set=True)
    def test_handle_exception(self, client_cls):
        req = MagicMock(
            action="fa"
        )
        client_mock = client_cls(None, None)        

        uut = Handler(client_mock)
        with self.assertRaises(Exception):
            uut.handle(req)

if __name__ == '__main__':
    unittest.main()