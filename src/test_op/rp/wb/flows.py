#!/usr/bin/env python
from aatest.operation import Note
from aatest.status import WARNING
from aatest.status import ERROR
from oic.oauth2.message import ErrorResponse
from oic.oic import AccessTokenResponse
from oic.oic import OpenIDSchema
from oic.oic import AuthorizationResponse
from oidctest.oper import Webfinger
from oidctest.oper import AccessToken
from oidctest.oper import UserInfo
from oidctest.oper import AsyncAuthn
from oidctest.oper import Discovery
from oidctest.oper import Registration
from oidctest.oper import ReadRegistration
from oidctest.testfunc import set_request_args
from oidctest.testfunc import set_op_args

from func import set_webfinger_resource
from func import set_principal
from func import set_uri
from func import static_jwk
from func import store_sector_redirect_uris
from func import redirect_uri_with_query_component
from func import set_response_where
from func import check_support
from func import set_discovery_issuer

__author__ = 'roland'

USERINFO_REQUEST_AUTH_METHOD = (
    "_userinfo_", {
        set_op_args: {"authn_method": "bearer_header"},
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
            (AsyncAuthn, {set_response_where: {}})
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
            (AsyncAuthn, {set_response_where: {}})
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
            (AsyncAuthn, {set_response_where: {}})
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
            (AsyncAuthn, {set_response_where: {}})
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
            (AsyncAuthn, {set_response_where: {}})
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
            (AsyncAuthn, {set_response_where: {}})
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
            (AsyncAuthn, {set_request_args: {"response_type": []},
                          set_response_where: {}})
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
            (AsyncAuthn, {set_request_args: {"response_mode": ["form_post"]},
                          set_response_where: {}})
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
            (AsyncAuthn, {set_response_where: {}}),
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
            (AsyncAuthn, {set_response_where: {}}),
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
            (AsyncAuthn, {set_response_where: {}}),
            AccessToken
        ],
        "mti": {"all": "MUST"},
        "profile": "...s",
        "tests": {"verify-signed-idtoken-has-kid": {},
                  "verify-response": {
                      "response_cls": [AccessTokenResponse,
                                       AuthorizationResponse]}}
    },
    'OP-IDToken-none': {
        "desc": 'Unsecured ID Token signature with none [Basic]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            (Registration,
             {
                 set_request_args: {"id_token_signed_response_alg": "none"},
                 check_support: {
                     ERROR: {"id_token_signing_alg_values_supported": "none"}},
             }
             ),
            (AsyncAuthn, {set_response_where: {}}),
            AccessToken
        ],
        "tests": {"unsigned-idtoken": {},
                  "verify-response": {
                      "response_cls": [AccessTokenResponse,
                                       AuthorizationResponse]}},
        "profile": "C.T.T.n",
    },
    'OP-IDToken-at_hash': {
        "desc": 'ID Token has at_hash when ID Token and Access Token returned '
                'from Authorization Endpoint [Implicit, Hybrid]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            Registration,
            (AsyncAuthn, {set_response_where: {}})
        ],
        "mti": {"all": "MUST"},
        "test": {"verify-authn-response": {}},
        "profile": "IT,CIT..",
    },
    'OP-IDToken-c_hash': {
        "desc": 'ID Token has c_hash when ID Token and Authorization Code '
                'returned from Authorization Endpoint [Hybrid]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            Registration,
            (AsyncAuthn, {set_response_where: {}})
        ],
        "tests": {"verify-authn-response": {}},
        "profile": "CI,CIT..",
        "mti": {"all": "MUST"}
    },
    'OP-IDToken-HS256': {
        "desc": 'Symmetric ID Token signature with HS256 [Extra]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            (Registration,
             {set_request_args: {"id_token_signed_response_alg": "HS256"}}),
            (AsyncAuthn, {set_response_where: {}}),
            AccessToken
        ],
        "profile": "..T.s.+",
        "tests": {"verify-idtoken-is-signed": {"alg": "HS256"},
                  "verify-response": {
                      "response_cls": [AccessTokenResponse,
                                       AuthorizationResponse]}}
    },
    'OP-IDToken-ES256': {
        "desc": 'Asymmetric ID Token signature with ES256 [Extra]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            (Registration,
             {set_request_args: {"id_token_signed_response_alg": "ES256"}}),
            (AsyncAuthn, {set_response_where: {}}),
            AccessToken
        ],
        "profile": "..T.s.+",
        "tests": {"verify-idtoken-is-signed": {"alg": "ES256"},
                  "verify-response": {
                      "response_cls": [AccessTokenResponse,
                                       AuthorizationResponse]}}
    },
    'OP-IDToken-SigEnc': {
        "desc": 'Signed and encrypted ID Token [Extra]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            (Registration,
             {
                 set_request_args: {
                     "id_token_signed_response_alg": "RS256",
                     "id_token_encrypted_response_alg": "RSA1_5",
                     "id_token_encrypted_response_enc": "A128CBC-HS256"
                 },
                 check_support: {
                     ERROR: {
                         "id_token_signing_alg_values_supported": "RS256",
                         "id_token_encryption_alg_values_supported": "RSA1_5",
                         "id_token_encryption_enc_values_supported":
                             "A128CBC-HS256"}
                 }
             }
             ),
            (AsyncAuthn, {set_response_where: {}}),
            AccessToken
        ],
        "profile": "..T.se.+",
        "tests": {"signed-encrypted-idtoken": {"sign_alg": "RS256",
                                               "enc_alg": "RSA1_5",
                                               "enc_enc": "A128CBC-HS256"},
                  "verify-response": {"response_cls": [AuthorizationResponse,
                                                       AccessTokenResponse]}}
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
            # (Note, {cache_response: {}}),
            Note,
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            Registration,
            # (AsyncAuthn, {restore_response: {},
            #               set_request_args: {"max_age": 1}}),
            (AsyncAuthn, {
                set_request_args: {"max_age": 1},
                set_response_where: {}}),
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
    'OP-redirect_uri-Query-Added': {
        "desc": "Request with redirect_uri with query component "
                "when registered redirect_uri has no query component "
                "[Dynamic]",
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            Registration,
            Note,
            (AsyncAuthn, {
                redirect_uri_with_query_component: {"foo": "bar"},
                set_response_where: {}})
        ],
        "profile": "..T",
        "note": "This test should result in the OpenID Provider "
                "displaying an error message in your user agent. "
                "You should ignore the status of this test "
                "in the test tool, since it will be incomplete. "
                "You must submit a screen shot of the error shown "
                "as part of your certification application.",
        "mti": {"all": "MUST"},
        'tests': {
            "verify-response": {
                "response_cls": [ErrorResponse],
                "error": ["access_denied"]}}
    },
    'OP-prompt-none-NotLoggedIn': {
        "desc": 'Request with prompt=none when not logged in [Basic, '
                'Implicit, Hybrid]',
        "sequence": [
            Note,
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            Registration,
            (AsyncAuthn, {
                set_request_args: {"prompt": "none"},
                set_response_where: {}})
        ],
        "note": "This tests what happens if the authentication request "
                "specifies that no interaction may occur with the End-User "
                "and no recent enough authentication is present to enable a "
                "silent login. "
                "Please remove any cookies you may have received from the "
                "OpenID Provider before proceeding.",
        "mti": {"all": "MUST"},
        "profile": "..",
        "tests": {"verify-error-response": {
            "error": ["login_required", "interaction_required",
                      "session_selection_required", "consent_required"]}},
    },
    'OP-UserInfo-Endpoint': {
        "desc": 'UserInfo Endpoint access with GET and bearer header [Basic, '
                'Implicit, Hybrid]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            Registration,
            (AsyncAuthn, {set_response_where: {}}),
            AccessToken,
            (UserInfo, {
                set_op_args: {"authn_method": "bearer_header",
                              "method": "GET"}})
        ],
        "profile": "C,IT,CI,CT,CIT..",
        'tests': {"verify-response": {"response_cls": [OpenIDSchema]}},
        "mti": {"all": "SHOULD"}
    },
    'OP-UserInfo-Header': {
        "desc": 'UserInfo Endpoint access with POST and bearer header [Basic, '
                'Implicit, Hybrid]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            Registration,
            (AsyncAuthn, {set_response_where: {}}),
            AccessToken,
            (UserInfo, {
                set_op_args: {"authn_method": "bearer_header",
                              "method": "POST"}})
        ],
        "profile": "C,IT,CI,CT,CIT..",
        'tests': {"verify-response": {"response_cls": [OpenIDSchema]}},
    },
    'OP-UserInfo-Body': {
        "desc": 'UserInfo Endpoint access with POST and bearer body [Basic, '
                'Implicit, Hybrid]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            Registration,
            (AsyncAuthn, {set_response_where: {}}),
            AccessToken,
            (UserInfo, {
                set_op_args: {"authn_method": "bearer_body",
                              "method": "POST"}})
        ],
        "profile": "C,IT,CI,CT,CIT..",
        'tests': {"verify-response": {"response_cls": [OpenIDSchema],
                                      "status": WARNING}},
        "mti": {"all": "MAY"}
    },
    'OP-UserInfo-RS256': {
        "desc": 'RP registers userinfo_signed_response_alg to signal that it '
                'wants signed UserInfo returned [Dynamic]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            (Registration, {
                set_request_args: {
                    "userinfo_signed_response_alg": "RS256"},
                check_support: {
                    WARNING: {
                        "userinfo_signing_alg_values_supported": "RS256"}}}),
            (AsyncAuthn, {set_response_where: {}}),
            AccessToken,
            (UserInfo, {
                set_op_args: {"authn_method": "bearer_header",
                              "method": "GET",
                              "ctype": "jwt"}})
        ],
        "tests": {"asym-signed-userinfo": {"alg": "RS256"},
                  "verify-response": {"response_cls": [OpenIDSchema]}},
        "profile": "C,IT,CI,CT,CIT..T.s",
        "mti": {"all": "MUST"}
    },
    'OP-UserInfo-Enc': {
        "desc": 'Can provide encrypted UserInfo response [Extra]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            (Registration, {
                set_request_args: {
                    "userinfo_signed_response_alg": "none",
                    "userinfo_encrypted_response_alg": "RSA1_5",
                    "userinfo_encrypted_response_enc": "A128CBC-HS256"
                },
                check_support: {
                    ERROR: {
                        "userinfo_signing_alg_values_supported": "none",
                        "userinfo_encryption_alg_values_supported": "RSA1_5",
                        "userinfo_encryption_enc_values_supported":
                            "A128CBC-HS256"
                    }}
            }
             ),
            (AsyncAuthn, {set_response_where: {}}),
            AccessToken,
            (UserInfo, {
                set_op_args: {
                    "authn_method": "bearer_header",
                    "method": "GET"}})
        ],
        "profile": "C,IT,CI,CT,CIT...e.+",
        "tests": {"encrypted-userinfo": {},
                  "verify-response": {"response_cls": [OpenIDSchema]}},
    },
    'OP-UserInfo-SigEnc': {
        "desc": 'Can provide signed and encrypted UserInfo response [Extra]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            (Registration, {
                set_request_args: {
                    "userinfo_signed_response_alg": "RS256",
                    "userinfo_encrypted_response_alg": "RSA1_5",
                    "userinfo_encrypted_response_enc": "A128CBC-HS256"},
                check_support: {
                    "error": {
                        "userinfo_signing_alg_values_supported": "RS256",
                        "userinfo_encryption_alg_values_supported": "RSA1_5",
                        "userinfo_encryption_enc_values_supported":
                            "A128CBC-HS256"}}}),
            (AsyncAuthn, {set_response_where: {}}),
            AccessToken,
            (UserInfo, {
                set_op_args: {
                    "authn_method": "bearer_header",
                    "method": "GET"}})
        ],
        "profile": "C,IT,CI,CT,CIT...se.+",
        "tests": {
            "encrypted-userinfo": {},
            "asym-signed-userinfo": {"alg": "RS256"},
            "verify-response": {"response_cls": [OpenIDSchema]}},
    },
    'OP-ClientAuth-Basic-Dynamic': {
        "desc": 'Access token request with client_secret_basic authentication '
                '[Basic, Hybrid]',
        # Register token_endpoint_auth_method=client_secret_basic
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            (Registration, {
                set_request_args: {
                    "token_endpoint_auth_method": "client_secret_basic"}}),
            (AsyncAuthn, {set_response_where: {}}),
            (AccessToken,
             {
                 set_op_args: {"authn_method": "client_secret_basic"},
                 check_support: {
                     WARNING: {
                         "token_endpoint_auth_methods_supported":
                             "client_secret_basic"}}
             }),
        ],
        "profile": "C,CI,CIT,CT..T",
        'tests': {"verify-response": {"response_cls": [AuthorizationResponse,
                                                       AccessTokenResponse]}},
    },
    'OP-ClientAuth-Basic-Static': {
        "desc": 'Access token request with client_secret_basic authentication '
                '[Basic, Hybrid]',
        # client_secret_basic is the default
        "sequence": [
            (Discovery, {set_discovery_issuer: {}}),
            (AsyncAuthn, {set_response_where: {}}),
            (AccessToken, {
                set_op_args: {"authn_method": "client_secret_basic"},
                check_support: {
                    WARNING: {
                        "token_endpoint_auth_methods_supported":
                            "client_secret_basic"}}}),
        ],
        "profile": "C,CI,CIT,CT..F",
        'tests': {"verify-response": {"response_cls": [AuthorizationResponse,
                                                       AccessTokenResponse]}},
    },
    'OP-ClientAuth-SecretPost-Dynamic': {
        "desc": 'Access token request with client_secret_post authentication '
                '[Basic, Hybrid]',
        # Should register token_endpoint_auth_method=client_secret_post
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            (Registration, {
                set_request_args: {
                    "token_endpoint_auth_method": "client_secret_post"}}),
            (AsyncAuthn, {set_response_where: {}}),
            (AccessToken, {
                set_op_args: {"authn_method": "client_secret_post"},
                check_support: {
                    WARNING: {
                        "token_endpoint_auth_methods_supported":
                            "client_secret_post"}}}),
        ],
        "profile": "C,CI,CIT,CT..T",
        'tests': {"verify-response": {"response_cls": [AuthorizationResponse,
                                                       AccessTokenResponse]}},
    },
    'OP-ClientAuth-SecretPost-Static': {
        "desc": 'Access token request with client_secret_post authentication '
                '[Basic, Hybrid]',
        # Should register token_endpoint_auth_method=client_secret_post
        "sequence": [
            (Discovery, {set_discovery_issuer: {}}),
            (AsyncAuthn, {set_response_where: {}}),
            (AccessToken, {
                set_op_args: {"authn_method": "client_secret_post"},
                check_support: {
                    WARNING: {
                        "token_endpoint_auth_methods_supported":
                            "client_secret_post"}}}),
        ],
        "profile": "C,CI,CIT,CT..F",
        'tests': {"verify-response": {"response_cls": [AuthorizationResponse,
                                                       AccessTokenResponse]}},
    },
    'OP-ClientAuth-PrivateJWT': {
        "desc": 'Access token request with private_key_jwt authentication ['
                'Extra]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            (AsyncAuthn, {set_response_where: {}}),
            (Registration, {
                set_request_args: {
                    "token_endpoint_auth_method": "private_key_jwt"}}),
            (AsyncAuthn, {set_response_where: {}}),
            (AccessToken, {
                set_op_args: {"authn_method": "private_key_jwt"},
                check_support: {
                    WARNING: {
                        "token_endpoint_auth_methods_supported":
                            "private_key_jwt"}}}),
        ],
        "profile": "C,CI,CT,CIT...s.+",
        'tests': {"verify-response": {"response_cls": [AuthorizationResponse,
                                                       AccessTokenResponse]}},
    },
    'OP-ClientAuth-SecretJWT': {
        "desc": 'Access token request with client_secret_jwt authentication ['
                'Extra]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            (AsyncAuthn, {set_response_where: {}}),
            (Registration, {
                set_request_args: {
                    "token_endpoint_auth_method": "client_secret_jwt"}}),
            (AsyncAuthn, {set_response_where: {}}),
            (AccessToken, {
                set_op_args: {"authn_method": "client_secret_jwt"},
                check_support: {
                    WARNING: {
                        "token_endpoint_auth_methods_supported":
                            "client_secret_jwt"}}}),
        ],
        "profile": "C,CI,CT,CIT...s.+",
        'tests': {"verify-response": {"response_cls": [AuthorizationResponse,
                                                       AccessTokenResponse]}},
    },
    'OP-Discovery-Config': {
        "desc": 'Publishes openid-configuration discovery information [Config, '
                'Dynamic]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
        ],
        "profile": ".T.",
        'tests': {"check-http-response": {}},
        "mti": {"Dynamic": "MUST"}
    },
    'OP-Discovery-jwks_uri': {
        "desc": 'Verify that jwks_uri is published ['
                'Config, Dynamic]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
        ],
        "tests": {"providerinfo-has-jwks_uri": {},
                  "bare-keys": {},
                  "check-http-response": {}},
        "profile": ".T..s",
        "mti": {"Dynamic": "SHOULD"}
    },
    'OP-Discovery-claims_supported': {
        "desc": 'Verify that claims_supported is published ['
                'Config, Dynamic]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
        ],
        "tests": {"providerinfo-has-claims_supported": {},
                  "check-http-response": {}},
        "profile": ".T.",
        "mti": {"Dynamic": "SHOULD"}
    },
    'OP-Discovery-JWKs': {
        "desc": 'Keys in OP JWKs well formed [Config, Dynamic]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
        ],
        "profile": ".T.",
        "tests": {"verify-base64url": {"err_status": ERROR},
                  "check-http-response": {}},
        "mti": {"Dynamic": "MUST"}
    },
    'OP-Discovery-WebFinger-Email': {
        "desc": 'Can discover identifiers using e-mail syntax [Dynamic]',
        "profile": ".T...+",
        "sequence": [
            (Webfinger, {set_principal, {"param": "webfinger_email"}})
        ],
        "tests": {},
    },
    'OP-Discovery-WebFinger': {
        "desc": 'Can discover identifiers using URL syntax [Dynamic]',
        "profile": ".T...+",
        "sequence": [
            (Webfinger, {set_principal, {"param": "webfinger_url"}})
        ],
        "tests": {},
    },
    'OP-Registration-Endpoint': {
        "desc": 'Verify that registration_endpoint is published [Dynamic]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
        ],
        "profile": ".T.T",
        "tests": {"verify-op-has-registration-endpoint": {}},
        "mti": {"Dynamic": "MUST"}
    },
    'OP-Registration-Dynamic': {
        "desc": 'Client registration request [Dynamic]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            Registration
        ],
        "profile": "..T",
        "tests": {"check-http-response": {}},
        "mti": {"Dynamic": "MUST"}
    },
    'OP-Registration-policy_uri': {
        "desc": 'Registration with policy_uri [Dynamic]',
        "sequence": [
            Note,
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            (Registration, {set_uri: ["policy_uri", "static/policy.html"]}),
            (AsyncAuthn, {set_response_where: {}}),
        ],
        "profile": "..T",
        "note": "This test verifies that an OP displays a link "
                "to the RP's policy document. "
                "To make sure you get a fresh login page, "
                "you need to remove any cookies you may have received from "
                "the OP before proceeding.",
        "tests": {"verify-authn-response": {}},
    },
    'OP-Registration-logo_uri': {
        "desc": 'Registration with logo_uri [Dynamic]',
        "sequence": [
            Note,
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            (Registration, {set_uri: ["logo.uri", "static/logo.png"]}),
            (AsyncAuthn, {set_response_where: {}}),
        ],
        "profile": "..T",
        "note": "This test verifies that an OP displays the RP's logo. "
                "To make sure you get a fresh login page, "
                "you need to remove any cookies you may have received from "
                "the OP before proceeding.",
        "tests": {"verify-authn-response": {}},
    },
    'OP-Registration-tos_uri': {
        "desc": 'Registration with tos_uri [Dynamic]',
        "sequence": [
            Note,
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            (Registration, {set_uri: ["tos_uri", "static/tos.html"]}),
            (AsyncAuthn, {set_response_where: {}}),
        ],
        "profile": "..T",
        "note": "This test verifies that an OP displays a link "
                "to the RP's terms of service. "
                "To make sure you get a fresh login page, "
                "you need to remove any cookies you may have received from "
                "the OP before proceeding.",
        "tests": {"verify-authn-response": {}},
    },
    'OP-Registration-jwks': {
        "desc": 'Uses keys registered with jwks value [Dynamic]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            (Registration, {
                set_request_args: {
                    "token_endpoint_auth_method": "private_key_jwt"},
                static_jwk: None}),
            (AsyncAuthn, {set_response_where: {}}),
            (AccessToken,
             {
                 set_op_args: {"authn_method": "private_key_jwt"},
                 check_support: {
                     WARNING: {
                         "token_endpoint_auth_methods_supported":
                             "private_key_jwt"}}
             }),
        ],
        "profile": "C,CI,CT,CIT..T",
        "tests": {"verify-response": {"response_cls": [AuthorizationResponse,
                                                       AccessTokenResponse]}},
    },
    'OP-Registration-jwks_uri': {
        "desc": 'Uses keys registered with jwks_uri value [Dynamic]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            (Registration, {
                set_request_args: {
                    "token_endpoint_auth_method": "private_key_jwt"}}),
            (AsyncAuthn, {set_response_where: {}}),
            (AccessToken, {
                set_op_args: {"authn_method": "private_key_jwt"},
                check_support: {
                    WARNING: {
                        "token_endpoint_auth_methods_supported":
                            "private_key_jwt"}}}),
        ],
        "profile": "C,CI,CT,CIT..T",
        'tests': {"verify-response": {"response_cls": [AuthorizationResponse,
                                                       AccessTokenResponse]}}
    },
    'OP-Registration-Sector-Bad': {
        "desc": 'Incorrect registration of sector_identifier_uri [Dynamic]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            (Registration, {
                 check_support: {
                     ERROR: {"subject_types_supported": "pairwise"}},
                 set_request_args: {},
                 store_sector_redirect_uris:
                     {"other_uris": ["https://example.com/op"]}})],
        "profile": "..T",
        "tests": {"verify-error": {
            "error": ["invalid_configuration_parameter",
                      "invalid_client_metadata"]},
            "verify-bad-request-response": {}},
    },
    'OP-Registration-Read': {
        "desc": 'Registering and then reading the registered client metadata '
                '[Extra]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            Registration,
            ReadRegistration
        ],
        "profile": "..T..+",
        "tests": {"check-http-response": {}},
    },
    'OP-Registration-Sub-Public': {
        "desc": 'Registration of wish for public sub [Extra]',
        "sequence": [
            '_discover_',
            ('_register_',
             {
                 set_request_args: {"subject_type": "public"},
                 check_support: {"error": {"subject_types_supported": "public"}}
             }),
            "_login_",
            "_accesstoken_"
        ],
        "profile": "..T..+",
        "tests": {"verify-response": {"response_cls": [AuthorizationResponse,
                                                       AccessTokenResponse]}},
    },
    'OP-Registration-Sub-Pairwise': {
        "desc": 'Registration of wish for pairwise sub [Extra]',
        "sequence": [
            '_discover_',
            ('_register_',
             {
                 set_request_args: {"subject_type": "pairwise"},
                 check_support: {
                 "error": {"subject_types_supported": "pairwise"}}
             }),
            "_login_",
            "_accesstoken_"
        ],
        "profile": "..T..+",
        "tests": {"verify-response": {"response_cls": [AuthorizationResponse,
                                                       AccessTokenResponse]}},
    },
    'OP-Registration-Sub-Differ': {
        "desc": 'Public and pairwise sub values differ [Extra]',
        "sequence": [
            '_discover_',
            ('_register_',
             {
                 set_request_args: {"subject_type": "public"},
                 check_support: {"error": {"subject_types_supported": "public"}}
             }),
            "_login_",
            "_accesstoken_",
            ('_register_',
             {
                 set_request_args: {"subject_type": "pairwise"},
                 check_support: {
                 "error": {"subject_types_supported": "pairwise"}}
             }),
            "_login_",
            "_accesstoken_"
        ],
        "profile": "..T..+",
        'tests': {"different_sub": {},
                  "verify-response": {"response_cls": [AuthorizationResponse,
                                                       AccessTokenResponse]}}
    },
}
