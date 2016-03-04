from oic import oic
from aatest.events import EV_RESPONSE

__author__ = 'roland'


class Client(oic.Client):
    def __init__(self, *args, **kwargs):
        oic.Client.__init__(self, *args, **kwargs)
        self.conv = None

    def store_response(self, clinst, text):
        self.conv.events.store(EV_RESPONSE, (clinst, text))
        self.conv.trace.response(clinst)