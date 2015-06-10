#!/usr/bin/env python
from aatest.operation import Note
from aatest.status import WARNING
from oic.oic import AccessTokenResponse, AuthorizationResponse
from oidctest.oper import Webfinger, AccessToken
from oidctest.oper import AsyncAuthn
from oidctest.oper import Discovery
from oidctest.oper import Registration
from oidctest.testfunc import set_request_args

from func import set_webfinger_resource
from func import set_discovery_issuer
from src.oidctest.testfunc import cache_response, restore_response

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
            AsyncAuthn,
        ],
        "profile": "I...",
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
            AsyncAuthn
        ],
        "profile": "IT...",
        'tests': {"verify-authn-response": {}},
        "mti": {"dynamic": "MUST"}
    },
    'OP-Response-code+id_token': {
        "desc": 'Request with response_type=code id_token [Hybrid]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            Registration,
            AsyncAuthn
        ],
        "tests": {"verify-authn-response": {}, 'check-idtoken-nonce': {}},
        "profile": "CI...",
    },
    'OP-Response-code+token': {
        "desc": 'Request with response_type=code token [Hybrid]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            Registration,
            AsyncAuthn
        ],
        "profile": "CT...",
        'tests': {"verify-authn-response": {}},
    },
    'OP-Response-code+id_token+token': {
        "desc": 'Request with response_type=code id_token token [Hybrid]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            Registration,
            AsyncAuthn
        ],
        "profile": "CIT...",
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
            (AsyncAuthn, {set_request_args: {"response_type": []}})
        ],
        "tests": {
            "verify-error": {"error": ["invalid_request",
                                       "unsupported_response_type"]}},
        "note": "There are two acceptable outcomes: (1) returning an error "
                "response "
                "to the RP or (2) returning an error message to the End-User. "
                "In case (2), you must submit a screen shot of the error shown "
                "as part of your certification application.",
        "profile": "...",
        "mti": {"all": "MUST"}
    },
    'OP-Response-form_post': {
        "desc": 'Request with response_mode=form_post [Extra]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            Registration,
            (AsyncAuthn, {set_request_args: {"response_mode": ["form_post"]}})
        ],
        "profile": "....+",
        'tests': {"verify-authn-response": {}},
    },
    'OP-IDToken-RS256': {
        "desc": 'Asymmetric ID Token signature with RS256 [Dynamic]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            (Registration,
             {set_request_args: {"id_token_signed_response_alg": "RS256"}}),
            AsyncAuthn,
            AccessToken
        ],
        "profile": "..T.s",
        "mti": {"all": "MUST"},
        "tests": {"verify-idtoken-is-signed": {"alg": "RS256"},
                  "verify-response": {
                      "response_cls": [AccessTokenResponse,
                                       AuthorizationResponse]}}
    },
    'OP-IDToken-Signature': {
        # RS256 is MTI
        "desc": 'Does the OP sign the ID Token and with what [Basic, '
                'Implicit, Hybrid]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            AsyncAuthn,
            AccessToken
        ],
        "profile": "..F",
        "tests": {"is-idtoken-signed": {"alg": "RS256"},
                  "verify-response": {
                      "response_cls": [AccessTokenResponse,
                                       AuthorizationResponse]}}
    },
    'OP-IDToken-kid': {
        "desc": 'IDToken has kid [Basic, Implicit, Hybrid]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            Registration,
            AsyncAuthn,
            AccessToken
        ],
        "mti": {"all": "MUST"},
        "profile": "...s",
        "tests": {"verify-signed-idtoken-has-kid": {},
                  "verify-response": {
                      "response_cls": [AccessTokenResponse,
                                       AuthorizationResponse]}}
    },
    'OP-Req-max_age=1': {
        "desc": 'Requesting ID Token with max_age=1 seconds restriction ['
                'Basic, Implicit, Hybrid]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            Registration,
            AsyncAuthn,
            AccessToken,
            (Note, {cache_response: {}}),
            (Webfinger, {set_webfinger_resource: {},
                         restore_response: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            Registration,
            (AsyncAuthn, {set_request_args: {"max_age": 1}}),
            AccessToken
        ],
        "note": "Wait at least one second before proceeding so that the "
                "max_age=1 period expires. "
                "You should be prompted to authenticate or re-authenticate. "
                "Please submit a screen shot of any authentication user "
                "interaction that occurred as part of your certification "
                "application.",
        "profile": "..",
        "tests": {"multiple-sign-on": {"status": WARNING},
                  "verify-response": {
                      "response_cls": [AccessTokenResponse,
                                       AuthorizationResponse]},
                  "claims-check": {"id_token": ["auth_time"],
                                   "required": True},
                  "auth_time-check": {"max_age": 1}},
        "mti": {"all": "MUST"},
        "result": "The test passed if you were prompted to log in."
    },
}