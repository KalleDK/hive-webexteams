import unittest

from webexteamssdk.api import organizations

from webexteams.datatypes import Member, MemberID, RoomAction, RoomID, Room
from webexteams.responder import Config, Request
from unittest.mock import MagicMock, patch, call

class TestConfig(unittest.TestCase):
    @patch('webexteams.responder.IParams', autospec=True, spec_set=True)
    def test_get_members(self, params_cls):
        
        params_mock = params_cls()
        params_mock.get_param.side_effect = [
            "token"
        ]
        
        uut = Config(params_mock)
        self.assertEqual(uut.webex_bot_token, "token")

    @patch('webexteams.responder.IParams', autospec=True, spec_set=True)
    def test_get_members(self, params_cls):
        
        values = {
            "data.owner": "me@org.com",
            "data.customFields.webexteams.string": "Open room",
            "data.caseId": 42,
            "data.title": "cstitle",
            "config.organization": "org",
            "data.customFields.webexroomid.string": "validroomid",
            "data.tags": ["flaf", "wbx=\"user@com.org\""]
        }

        params_mock = params_cls()
        params_mock.get_param.side_effect = lambda x, default : values[x]
       
        
        uut = Request(params_mock)
        self.assertEqual(uut.action, RoomAction.CREATE)
        self.assertEqual(uut.case_id, 42)
        self.assertEqual(uut.case_title, "cstitle")
        self.assertEqual(uut.organization, "org")
        self.assertEqual(uut.title, "org #42 - cstitle")
        self.assertEqual(uut.roomid, "validroomid")
        self.assertListEqual(uut.tags, ["flaf", "wbx=\"user@com.org\""])
        self.assertListEqual(uut.guests, ["user@com.org"])
        self.assertListEqual(uut.owners, ["me@org.com"])

    @patch('webexteams.responder.IParams', autospec=True, spec_set=True)
    def test_get_members_exception(self, params_cls):
        
        values = {
            "data.owner": 32,
            "data.title": "",
        }

        params_mock = params_cls()
        params_mock.get_param.side_effect = lambda x, default : values[x]
       
        
        uut = Request(params_mock)
        with self.assertRaises(Exception):
            uut.owners

        with self.assertRaises(Exception):
            uut.case_title
        

if __name__ == '__main__':
    unittest.main()