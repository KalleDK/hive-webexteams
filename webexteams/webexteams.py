#!/usr/bin/env python3
# encoding: utf-8

import json
from sys import call_tracing
import tempfile

from cortexutils.responder import Responder

class WebexTeams(Responder):
    def __init__(self):
        Responder.__init__(self)
        self.tmpPath = self.get_param('config.webexteams_data')
    
    def run(self):
        try:
            with tempfile.NamedTemporaryFile(mode="wb", encoding="utf8", dir=self.tmpPath, delete=False) as fp:
                json.dump(self._input, fp, indent=4)
        except:
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf8", dir=self.tmpPath, delete=False) as fp:
                json.dump(self._input, fp, indent=2)
