import calendar
import json
import time

from six.moves.urllib.parse import parse_qs

from oic.oic import message


__author__ = 'roland'

def utc_time_sans_frac():
    return int("%d" % calendar.timegm(time.gmtime()))


def get_provider_info(conv):
    _pi = conv.entity.provider_info
    if not _pi:
        _pi = conv.provider_info
    return _pi


def get_protocol_response(conv, cls):
    res = []
    for msg in conv.events.get_messages('response'):
        if isinstance(msg, cls):
            reply = conv.events.by_ref(msg.timestamp)
            if reply:
                res.append((reply[0], msg))
    return res


def get_id_tokens(conv):
    res = []
    # In access token responses
    for inst, msg in get_protocol_response(conv, message.AccessTokenResponse):
        _dict = json.loads(msg)
        jwt = _dict["id_token"]
        idt = inst["id_token"]
        res.append((idt, jwt))

    # implicit, id_token in authorization response
    for inst, msg in get_protocol_response(conv, message.AuthorizationResponse):
        try:
            idt = inst["id_token"]
        except KeyError:
            pass
        else:
            _info = parse_qs(msg)
            jwt = _info["id_token"][0]
            res.append((idt, jwt))

    return res