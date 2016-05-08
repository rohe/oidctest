import copy
import json
import re
import urllib.request, urllib.parse, urllib.error
import urllib.parse
from mako.lookup import TemplateLookup
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
parser.add_argument(dest="config")
args = parser.parse_args()

COM_ARGS, OP_ARG, config = main_setup(args, LOOKUP)

mode, endpoint = extract_mode(OP_ARG["baseurl"])

ENVIRON = {}

PROVIDER = setup_op(mode, COM_ARGS, OP_ARG, Trace())


def jwks(info, _):
    return "kb", KeyBundle(keys=info["keys"])


def registration_response(info, state):
    _resp = info
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

    _cid = str(_resp["client_id"])
    PROVIDER.cdb[_cid] = drr
    PROVIDER.keyjar[_cid] = state["kb"]
    del state["kb"]
    PROVIDER.keyjar.add_symmetric(issuer=_cid, key=_resp["client_secret"],
                                  usage=["sig"])

    return 'client_info', rr


def authorization(info, state):
    if "request_uri" in info:
        return None, None

    resp = PROVIDER.authorization_endpoint(info)

    parts = urllib.parse.urlparse(resp.message)

    if parts.query:
        aresp = AuthorizationResponse().from_urlencoded(parts.query)
    else:
        aresp = AuthorizationResponse().from_urlencoded(parts.fragment)

    return 'authorization', aresp


def authoriz2(info, state):
    if "authorization" in state:
        return None, None

    resp = PROVIDER.authorization_endpoint(info)

    parts = urllib.parse.urlparse(resp.message)

    if parts.query:
        aresp = AuthorizationResponse().from_urlencoded(parts.query)
    else:
        aresp = AuthorizationResponse().from_urlencoded(parts.fragment)

    return 'authorization', aresp


def token(info, state):
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


def userinfo(info, state):
    tresp = state["token"]
    authn = "Bearer {}".format(tresp["access_token"])

    return "user_info", PROVIDER.userinfo_endpoint("", authn=authn)


def behavior(info, state):
    mode, endpoint = extract_mode(info)

    for _typ in ["sign_alg", "enc_alg", "enc_enc"]:
        try:
            _alg = mode[_typ]
        except (TypeError, KeyError):
            for obj in ["id_token", "request_object", "userinfo"]:
                PROVIDER.jwx_def[_typ][obj] = ''
        else:
            for obj in ["id_token", "request_object", "userinfo"]:
                PROVIDER.jwx_def[_typ][obj] = _alg

    if mode:
        try:
            PROVIDER.claims_type = mode["claims"]
        except KeyError:
            pass

        try:
            PROVIDER.behavior_type = mode["behavior"]
            PROVIDER.server.behavior_type = mode["behavior"]
        except KeyError:
            pass

    return None, None


OP = {
    "jwks": jwks,
    "registration_response": registration_response,
    "authorization": authorization,
    "authzreq2": authoriz2,
    "token": token,
    "behavior": behavior
}


def list2dict(l):
    return eval("".join(l))


def eval_oneliner(l):
    return eval(l[0])


def oneliner(l):
    return l[0][1:-1]


def opkey(l):
    _, url = l[0].split(":")
    return url


CONTENT_MAP = [
    # ("@registration_endpoint: <<", ">>", "registration_request", list2dict),
    (" registration_response: ", "", "registration_response", eval_oneliner),
    (" Loaded JWKS: ", " from ", "jwks", list2dict),
    ("oic.oauth2.provider:DEBUG Request: ", "", "authorization", oneliner),
    ("oic.oic.provider:DEBUG AuthzRequest+oidc_request: ", "", "authzreq2",
     eval_oneliner),
    (" OP key: ", "", "behavior", opkey)
]

content = []
end = ""
item = ""
func = None

for l in open(args.logfile).readlines():
    l = l.strip("\r\n")
    if end:
        if end in l:
            info, _ = l.split(end)
            lines.append(info)
            end = ""
            content.append((item, func(lines)))
        else:
            lines.append(l)
        continue

    for start, stop, item, func in CONTENT_MAP:
        if start in l:
            _, info = l.split(start)
            lines = [info]
            if stop:
                end = stop
            else:
                content.append((item, func(lines)))
            break

state = {}
for op, lin in content:
    if not op:
        continue

    try:
        key, val = OP[op](lin, state)
    except KeyError as err:
        continue

    if key:
        try:
            state[key].append(val)
        except KeyError:
            state[key] = [val]

print("DONE!")
