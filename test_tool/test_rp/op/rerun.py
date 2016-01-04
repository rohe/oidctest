import copy
import json
import re
import urllib.request, urllib.parse, urllib.error
import urllib.parse
from mako.lookup import TemplateLookup
from oic.oauth2 import rndstr
from oic.oic import RegistrationResponse
from oic.oic import AccessTokenResponse
from oic.oic import AuthorizationResponse
from oic.oic import AccessTokenRequest
from oic.utils.keyio import KeyBundle

from oidctest.mode import extract_mode
from oidctest.mode import setup_op
from src.oidctest.common import Trace

__author__ = 'roland'

ROOT = './'

LOOKUP = TemplateLookup(directories=[ROOT + 'templates', ROOT + 'htdocs'],
                        module_directory=ROOT + 'modules',
                        input_encoding='utf-8', output_encoding='utf-8')

import argparse

from setup import main_setup

parser = argparse.ArgumentParser()
parser.add_argument('-v', dest='verbose', action='store_true')
parser.add_argument('-d', dest='debug', action='store_true')
parser.add_argument('-p', dest='port', default=80, type=int)
parser.add_argument('-k', dest='insecure', action='store_true')
parser.add_argument('-l', dest='logfile')
parser.add_argument('-t', dest='timestamp')
parser.add_argument(dest="config")
args = parser.parse_args()

COM_ARGS, OP_ARG, config = main_setup(args, LOOKUP)

mode, endpoint = extract_mode(OP_ARG["baseurl"])

ENVIRON = {}

PROVIDER = setup_op(mode, COM_ARGS, OP_ARG, Trace())


def get_response(line):
    parts = urllib.parse.urlparse(line)
    if parts.query:
        return parts.query

    return parts.fragment

def get_request(line):
    if re.match(r'^[A-Z]*:', line):
        return ""

    return line


op_map = {
    "registration": [
        (" <-- ", json.loads, "resp"),
        (" Client JWKS: ", eval, "jwks")
    ],
    "authorization": {
        (' --> METHOD: ', copy.copy, "method"),
        (' --> ', get_request, "req"),
        (" Client JWKS: ", eval, "jwks"),
        (" <-- ", get_response, "resp"),
    },
    "token": {
        ('--> HTTP_AUTHORIZATION: ', copy.copy, "authz"),
        (" <-- ", json.loads, "resp"),
    },
    "userinfo": []
}


def parse_lines(lines, spec):
    res = {}
    for line in lines:
        for pattern, func, key in spec:
            if pattern in line:
                time, info = line.split(pattern)
                _val = func(info)
                if _val:
                    res[key] = _val
                break
    return res


def client_registration(lines, state):
    info = parse_lines(lines, op_map["registration"])

    _resp = info["resp"]
    ruris = []
    for ruri in _resp["redirect_uris"]:
        base, query = urllib.parse.splitquery(ruri)
        if query:
            ruris.append((base, urllib.parse.parse_qs(query)))
        else:
            ruris.append((base, query))

    rr = RegistrationResponse(**_resp)
    drr = rr.to_dict()
    drr["redirect_uris"] = ruris
    drr["client_salt"] = rndstr(8)

    _cid = str(_resp["client_id"])
    PROVIDER.cdb[_cid] = drr
    PROVIDER.keyjar[_cid] = KeyBundle(keys=info["jwks"]["keys"])
    PROVIDER.keyjar.add_symmetric(issuer=_cid, key=_resp["client_secret"],
                                  usage=["sig"])

    return 'client_info', rr


def authorization(lines, state):
    info = parse_lines(lines, op_map["authorization"])

    if "jwks" in info:
        _cid = [c for c in list(PROVIDER.keyjar.issuer_keys.keys()) if c != ''][0]
        PROVIDER.keyjar[_cid].append(KeyBundle(keys=info["jwks"]["keys"]))

    resp = PROVIDER.authorization_endpoint(info["req"])

    parts = urllib.parse.urlparse(resp.message)

    if parts.query:
        aresp = AuthorizationResponse().from_urlencoded(parts.query)
    else:
        aresp = AuthorizationResponse().from_urlencoded(parts.fragment)

    return 'authorization', aresp


def token(lines, state):
    info = parse_lines(lines, op_map["token"])
    _authz = state["authorization"]
    _cinfo = state["client_info"]

    treq = AccessTokenRequest(
        client_id=_cinfo["client_id"],
        code=_authz["code"],
        redirect_uri="",
        grant_type="authorization_code",
        client_secret=_cinfo["client_secret"]
    )

    _resp = PROVIDER.token_endpoint(treq)

    tresp = AccessTokenResponse().from_json(_resp.message)

    return "token", tresp


def userinfo(lines, state):
    _ = parse_lines(lines, op_map["userinfo"])
    tresp = state["token"]
    authn = "Bearer {}".format(tresp["access_token"])

    return "user_info",  PROVIDER.userinfo_endpoint("", authn=authn)


OP = {
    "registration": client_registration,
    "authorization": authorization,
    "token": token
}
# every request response log begins with a line with "Trace init"

exchange = []
lines = []
op = ""
start = False
for l in open(args.logfile).readlines():
    if not start:
        if args.timestamp in l:
            start = True
        else:
            continue
    l = l.strip("\r\n")
    if l.startswith("Trace init:"):
        exchange.append((op, lines))
        lines = []
    else:
        if "PATH:" in l:
            _, op = l.split(' PATH: ')
        lines.append(l)

# end of file
exchange.append((op, lines))

state = {}
for op, lin in exchange:
    if not op:
        continue
    print(op)

    try:
        key, val = OP[op](lin, state)
    except KeyError as err:
        if '.well-known/openid-configuration' in op:
            mode, _ = extract_mode(op)
            # PROVIDER.behavior_type = mode["behavior"]
        continue

    if key:
        try:
            state[key].append(val)
        except KeyError:
            state[key] = [val]
