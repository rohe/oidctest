from oic import oic
from aatest.events import EV_RESPONSE
from oic.utils.authn.client import CLIENT_AUTHN_METHOD

__author__ = 'roland'


class Client(oic.Client):
    def __init__(self, *args, **kwargs):
        oic.Client.__init__(self, *args, **kwargs)
        self.conv = None

    def store_response(self, clinst, text):
        self.conv.events.store(EV_RESPONSE, (clinst, text))
        self.conv.trace.response(clinst)


def make_client(**kw_args):
    c_keyjar = kw_args["keyjar"].copy()
    _cli = Client(client_authn_method=CLIENT_AUTHN_METHOD, keyjar=c_keyjar)
    _cli.kid = kw_args["kidd"]
    _cli.jwks_uri = kw_args["jwks_uri"]

    _cli_info = {}
    try:
        _cli_info = kw_args["conf"].INFO["client"]
    except KeyError:
        pass
    else:
        for arg, val in list(_cli_info.items()):
            setattr(_cli, arg, val)

    return _cli, _cli_info
