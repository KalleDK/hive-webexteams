import webexteamssdk
import cortexutils.worker
from .client import Client
from .responder import Responder, Config
from .handler import Handler



def make_handler(config: Config):
    api = webexteamssdk.WebexTeamsAPI(access_token=config.webex_bot_token)
    return Handler(
        client=Client(
            room_api=api.rooms,
            memberships_api=api.memberships,
        )
    )

def make_responder():
    worker = cortexutils.worker.Worker(job_directory=None)
    return Responder(
        worker=worker
    )    
    

def main():
    resp = make_responder()
    try:
        handler = make_handler(resp.config)
        report = handler.handle(resp.request)
        resp.report(report)
    except Exception as e:
        resp.error(e)
