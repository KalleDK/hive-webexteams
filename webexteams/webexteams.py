#!/usr/bin/env python3
# encoding: utf-8

import json

from cortexutils.responder import Responder

class WebexTeams(Responder):
    def __init__(self):
        Responder.__init__(self)
        self.tmpPath          = self.get_param('config.webexteams_data')
    
    def run(self):
        with open(self.tmpPath + "/data.json", "w") as fp:
            json.dump(self._input, fp, indent=4)
