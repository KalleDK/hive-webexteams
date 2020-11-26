import unittest
import json
import webexteams.__main__
from webexteams.main import main
from unittest.mock import MagicMock, patch, call, seal, PropertyMock


class TestMain(unittest.TestCase):
    @patch('webexteams.client.MembershipsAPI', autospec=True, spec_set=True)
    @patch("webexteams.client.RoomsAPI", autospec=True, spec_set=True)
    @patch('webexteamssdk.WebexTeamsAPI')
    @patch('cortexutils.worker.Worker', autospec=True, spec_set=True)
    def test_main(self, worker_cls, api_cls, room_cls, member_cls):
        self.maxDiff = None

        room_api = room_cls()
        room_api.get.return_value = MagicMock(id="validroomid", title="validtitle")

        member_api = member_cls()

        api = api_cls()
        type(api).rooms = PropertyMock(return_value=room_api)
        type(api).memberships = PropertyMock(return_value=member_api)
        seal(api)
        api_cls.return_value = api

        worker = worker_cls.return_value
        worker.get_param.side_effect = [
            "bottoken",
            "Delete room",
            "validroomid",
            "validroomid",
        ]
        

        main()
        
        self.assertListEqual(member_api.method_calls, [])
        self.assertListEqual(room_api.method_calls, [
            call.get(roomId='validroomid'),
            call.delete('validroomid')
        ])
        self.assertListEqual(worker_cls.method_calls, [
            call().get_param('config.webex_bot_token', default=None),
            call().get_param('data.customFields.webexteams.string', default=None),
            call().get_param('data.customFields.webexroomid.string', default=None),
            call().get_param('data.customFields.webexroomid.string', default=None),
            call().report(
                output={
                    'success': True,
                    'full': {
                        'message': 'Room deleted validroomid',
                        'fields': {'roomid': ''},
                        'tags': [],
                        'events': [
                            {'room found': {'ID': 'validroomid', 'Title': 'validtitle'}},
                            {'room deleted': {'ID': 'validroomid', 'Title': 'validtitle'}}
                        ]
                    },
                    'operations': [
                        {'type': 'AddCustomFields', 'name': 'webexroomid', 'value': '', 'tpe': 'string'}
                    ]
                }, ensure_ascii=False)
        ])


    @patch('webexteams.client.MembershipsAPI', autospec=True, spec_set=True)
    @patch("webexteams.client.RoomsAPI", autospec=True, spec_set=True)
    @patch('webexteamssdk.WebexTeamsAPI')
    @patch('cortexutils.worker.Worker', autospec=True, spec_set=True)
    def test_main_exception(self, worker_cls, api_cls, room_cls, member_cls):
        self.maxDiff = None

        room_api = room_cls()
        room_api.get.return_value = MagicMock(id="validroomid", title="validtitle")

        member_api = member_cls()

        api = api_cls()
        type(api).rooms = PropertyMock(return_value=room_api)
        type(api).memberships = PropertyMock(return_value=member_api)
        seal(api)
        api_cls.return_value = api

        worker = worker_cls.return_value
        worker.get_param.side_effect = [
            None
        ]
        
        main()
        
        self.assertListEqual(member_api.method_calls, [])
        self.assertListEqual(room_api.method_calls, [
            
        ])
        self.assertListEqual(worker_cls.method_calls, [
           call().get_param('config.webex_bot_token', default=None),
           call().error(message='Missing parameter: "config.webex_bot_token"', ensure_ascii=False)
        ])

    @patch.object(webexteams.__main__.sys,'exit')
    @patch.object(webexteams.__main__, "__name__", "__main__")
    @patch.object(webexteams.__main__, 'main', return_value=42)
    def test_init(self, main_mock, sys_mock):
        webexteams.__main__.init()
        assert sys_mock.call_args[0][0] == 42

if __name__ == '__main__':
    unittest.main()