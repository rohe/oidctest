#!/usr/bin/env python
from oidctest.oper import Webfinger
from oidctest.oper import Discovery
from oidctest.oper import Registration
from oidctest.oper import SyncAuthn
from cl.func import set_webfinger_resource
from cl.func import set_discovery_issuer

__author__ = 'roland'

USERINFO_REQUEST_AUTH_METHOD = (
    "_userinfo_", {
        "kwargs_mod": {"authn_method": "bearer_header"},
        "method": "GET"
    })

ORDDESC = ["OP-Response", "OP-IDToken", "OP-UserInfo", "OP-nonce", "OP-scope",
           "OP-display", "OP-prompt", "OP-Req", "OP-OAuth", "OP-redirect_uri",
           "OP-ClientAuth", "OP-Discovery", "OP-Registration", "OP-Rotation",
           "OP-request_uri", "OP-request", "OP-claims"]

DESC = {
    "Response": "Response Type & Response Mode",
    "IDToken": "ID Token",
    "UserInfo": "Userinfo Endpoint",
    "nonce": "nonce Request Parameter",
    "scope": "scope Request Parameter",
    "display": "display Request Parameter",
    "prompt": "prompt Request Parameter",
    "Req": "Misc Request Parameters",
    "OAuth": "OAuth behaviors",
    "redirect_uri": "redirect_uri",
    "ClientAuth": "Client Authentication",
    "Discovery": "Discovery",
    "Registration": "Dynamic Client Registration",
    "Rotation": "Key Rotation",
    "request_uri": "request_uri Request Parameter",
    "request": "request Request Parameter",
    "claims": "claims Request Parameter",
}

FLOWS = {
    'OP-Response-code': {
        "desc": 'Request with response_type=code [Basic]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            Registration,
            SyncAuthn
        ],
        "profile": "C...",
        'tests': {"verify-authn-response": {}},
        "mti": {"all": "MUST"}
    },
}