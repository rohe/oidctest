#!/usr/bin/env python
from aatest.operation import Note
from oidctest.oper import Webfinger
from oidctest.oper import AsyncAuthn
from oidctest.oper import Discovery
from oidctest.oper import Registration
from oidctest.testfunc import set_request_args

from func import set_webfinger_resource
from func import set_discovery_issuer

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
            AsyncAuthn
        ],
        "profile": "C...",
        'tests': {"verify-authn-response": {}},
        "mti": {"all": "MUST"}
    },
    'OP-Response-id_token': {
        "desc": 'Request with response_type=id_token [Implicit]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            Registration,
            (AsyncAuthn, {
                set_request_args: {"response_type": ["id_token"]}
            }),
        ],
        "profile": "I..",
        'tests': {"verify-authn-response": {}},
        "mti": {"dynamic": "MUST"},
        # "tests": {"check-authorization-response": {}},
    },
    'OP-Response-id_token+token': {
        "desc": 'Request with response_type=id_token token [Implicit]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            Registration,
            (AsyncAuthn, {
                set_request_args: {"response_type": ["id_token", "token"]}
            }),
        ],
        "profile": "IT..",
        'tests': {"verify-authn-response": {}},
        "mti": {"dynamic": "MUST"}
    },
    'OP-Response-code+id_token': {
        "desc": 'Request with response_type=code id_token [Hybrid]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            Registration,
            (AsyncAuthn, {
                set_request_args: {"response_type": ["code", "id_token"]}
            }),
        ],
        "tests": {"verify-authn-response": {}, 'check-idtoken-nonce': {}},
        "profile": "CI..",
    },
    'OP-Response-code+token': {
        "desc": 'Request with response_type=code token [Hybrid]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            Registration,
            (AsyncAuthn, {
                set_request_args: {"response_type": ["code", "token"]}
            }),
        ],
        "profile": "CT..",
        'tests': {"verify-authn-response": {}},
    },
    'OP-Response-code+id_token+token': {
        "desc": 'Request with response_type=code id_token token [Hybrid]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            Registration,
            (AsyncAuthn, {
                set_request_args: {
                    "response_type": ["code", "id_token", "token"]}
            }),
        ],
        "profile": "CIT..",
        'tests': {"verify-authn-response": {}},
    },
    'OP-Response-Missing': {
        "desc": 'Authorization request missing the response_type parameter ['
                'Basic, Implicit, Hybrid]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            Registration,
            Note,
            (AsyncAuthn, {
                set_request_args: {"response_type": []}
            }),
        ],
        "tests": {
            "verify-error": {"error": ["invalid_request",
                                       "unsupported_response_type"]}},
        "note": "There are two acceptable outcomes: (1) returning an error "
                "response "
                "to the RP or (2) returning an error message to the End-User. "
                "In case (2), you must submit a screen shot of the error shown "
                "as part of your certification application.",
        "profile": "..",
        "mti": {"all": "MUST"}
    },
    'OP-Response-form_post': {
        "desc": 'Request with response_mode=form_post [Extra]',
        "sequence": [
            '_discover_',
            '_register_',
            ('_login_',
             {"request_args": {"response_mode": ["form_post"]}})
        ],
        "profile": "....+",
        'tests': {"verify-authn-response": {}},
    },
}