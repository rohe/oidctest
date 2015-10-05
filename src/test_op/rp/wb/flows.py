#!/usr/bin/env python
from aatest.operation import Note
from aatest.operation import TimeDelay
from aatest.status import WARNING
from aatest.status import ERROR
from oic.oauth2.message import ErrorResponse
from oic.oic import AccessTokenResponse
from oic.oic import OpenIDSchema
from oic.oic import AuthorizationResponse
from oidctest.oper import Webfinger
from oidctest.oper import DisplayUserInfo
from oidctest.oper import AccessToken
from oidctest.oper import UserInfo
from oidctest.oper import AsyncAuthn
from oidctest.oper import Discovery
from oidctest.oper import Registration
from oidctest.oper import ReadRegistration
from oidctest.oper import FetchKeys
from oidctest.oper import RotateSigKeys
from oidctest.oper import RefreshAccessToken
from oidctest.oper import RotateEncKeys
from oidctest.testfunc import set_request_args
from oidctest.testfunc import set_op_args

from .func import set_webfinger_resource, request_in_file
from .func import specific_acr_claims
from .func import sub_claims
from .func import multiple_return_uris
from .func import redirect_uris_with_query_component
from .func import redirect_uris_with_fragment
from .func import login_hint
from .func import ui_locales
from .func import claims_locales
from .func import acr_value
from .func import set_expect_error
from .func import id_token_hint
from .func import set_principal
from .func import set_uri
from .func import static_jwk
from .func import store_sector_redirect_uris
from .func import redirect_uri_with_query_component
from .func import set_response_where
from .func import check_support
from .func import set_discovery_issuer

__author__ = 'roland'

USERINFO_REQUEST_AUTH_METHOD = (
    UserInfo, {
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
            (AsyncAuthn, {
                set_request_args: {"response_type": [""]},
                set_response_where: {},
                set_expect_error: {"error": ["invalid_request",
                                             "unsupported_response_type"]}})
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
        "profile": "...",
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
        "profile": "....s",
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
        "profile": "C.T.T.T.n",
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
        "profile": "CI,CIT...",
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
        "profile": "...T.s.+",
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
        "profile": "...T.s.+",
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
        "profile": "...T.se.+",
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
        "profile": "...",
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
        "profile": "...T",
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
        "profile": "...",
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
        "profile": "C,IT,CI,CT,CIT...",
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
        "profile": "C,IT,CI,CT,CIT...",
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
        "profile": "C,IT,CI,CT,CIT...",
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
        "profile": "C,IT,CI,CT,CIT...T.s",
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
        "profile": "C,IT,CI,CT,CIT....e.+",
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
        "profile": "C,IT,CI,CT,CIT....se.+",
        "tests": {
            "encrypted-userinfo": {},
            "asym-signed-userinfo": {"alg": "RS256"},
            "verify-response": {"response_cls": [OpenIDSchema]}},
    },
    'OP-ClientAuth-Basic-Dynamic': {
        "desc": 'Access token request with client_secret_basic authentication '
                '[Basic, Hybrid]',
        # Registration token_endpoint_auth_method=client_secret_basic
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
        "profile": "C,CI,CIT,CT...T",
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
        "profile": "C,CI,CIT,CT...F",
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
        "profile": "C,CI,CIT,CT...T",
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
        "profile": "C,CI,CIT,CT...F",
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
        "profile": "C,CI,CT,CIT....s.+",
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
        "profile": "C,CI,CT,CIT....s.+",
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
        "profile": "..T..s",
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
        "profile": "..T.",
        "mti": {"Dynamic": "SHOULD"}
    },
    'OP-Discovery-JWKs': {
        "desc": 'Keys in OP JWKs well formed [Config, Dynamic]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
        ],
        "profile": "..T.",
        "tests": {"verify-base64url": {"err_status": ERROR},
                  "check-http-response": {}},
        "mti": {"Dynamic": "MUST"}
    },
    'OP-Discovery-WebFinger-Email': {
        "desc": 'Can discover identifiers using e-mail syntax [Dynamic]',
        "profile": "..T...+",
        "sequence": [
            (Webfinger, {set_principal: {"param": "webfinger_email"}})
        ],
        "tests": {},
    },
    'OP-Discovery-WebFinger': {
        "desc": 'Can discover identifiers using URL syntax [Dynamic]',
        "profile": "..T...+",
        "sequence": [
            (Webfinger, {set_principal: {"param": "webfinger_url"}})
        ],
        "tests": {},
    },
    'OP-Registration-Endpoint': {
        "desc": 'Verify that registration_endpoint is published [Dynamic]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
        ],
        "profile": "..T.T",
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
        "profile": "...T",
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
        "profile": "...T",
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
        "profile": "...T",
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
        "profile": "C,CI,CT,CIT...T",
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
        "profile": "C,CI,CT,CIT...T",
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
        "desc": 'Registrationing and then reading the registered client '
                'metadata '
                '[Extra]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            Registration,
            ReadRegistration
        ],
        "profile": "...T..+",
        "tests": {"check-http-response": {}},
    },
    'OP-Registration-Sub-Public': {
        "desc": 'Registration of wish for public sub [Extra]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            (Registration, {
                set_request_args: {"subject_type": "public"},
                check_support: {ERROR: {"subject_types_supported": "public"}}
            }),
            (AsyncAuthn, {set_response_where: {}}),
            AccessToken
        ],
        "profile": "...T..+",
        "tests": {"verify-response": {"response_cls": [AuthorizationResponse,
                                                       AccessTokenResponse]}},
    },
    'OP-Registration-Sub-Pairwise': {
        "desc": 'Registration of wish for pairwise sub [Extra]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            (Registration, {
                set_request_args: {"subject_type": "pairwise"},
                check_support: {ERROR: {"subject_types_supported": "pairwise"}}
            }),
            (AsyncAuthn, {set_response_where: {}}),
            AccessToken
        ],
        "profile": "...T..+",
        "tests": {"verify-response": {"response_cls": [AuthorizationResponse,
                                                       AccessTokenResponse]}},
    },
    'OP-Registration-Sub-Differ': {
        "desc": 'Public and pairwise sub values differ [Extra]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            (Registration, {
                set_request_args: {"subject_type": "public"},
                check_support: {ERROR: {"subject_types_supported": "public"}}
            }),
            (AsyncAuthn, {set_response_where: {}}),
            AccessToken,
            (Registration, {
                set_request_args: {"subject_type": "pairwise"},
                check_support: {ERROR: {"subject_types_supported": "pairwise"}}
            }),
            (AsyncAuthn, {set_response_where: {}}),
            AccessToken
        ],
        "profile": "...T..+",
        'tests': {"different_sub": {},
                  "verify-response": {"response_cls": [AuthorizationResponse,
                                                       AccessTokenResponse]}}
    },
    'OP-OAuth-2nd': {
        "desc": 'Trying to use authorization code twice should result in an '
                'error ['
                'Basic, Hybrid]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            Registration,
            (AsyncAuthn, {set_response_where: {}}),
            AccessToken,
            AccessToken,
        ],
        "profile": "C,CI,CT,CIT...",
        "tests": {
            "verify-response": {
                "response_cls": [ErrorResponse],
                "error": ["invalid_grant", "access_denied"],
                "status": WARNING,
            }},
        "mti": {"all": "SHOULD"},
        "reference": "http://tools.ietf.org/html/draft-ietf-oauth-v2-31"
                     "#section-4.1",
    },
    'OP-OAuth-2nd-Revokes': {
        "desc": 'Trying to use authorization code twice should result in '
                'revoking '
                'previously issued access tokens [Basic, Hybrid]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            Registration,
            (AsyncAuthn, {set_response_where: {}}),
            AccessToken,
            (AccessToken, {
                set_expect_error: {"error": ["invalid_grant", "access_denied"],
                                   "stop": False}}),
            USERINFO_REQUEST_AUTH_METHOD
        ],
        "profile": "C,CI,CT,CIT...",
        "tests": {
            "verify-response": {
                "response_cls": [ErrorResponse],
                "error": ["access_denied", "invalid_token"],
                "status": WARNING}},
        "mti": {"all": "SHOULD"},
        "reference": "http://tools.ietf.org/html/draft-ietf-oauth-v2-31"
                     "#section-4.1",
    },
    'OP-OAuth-2nd-30s': {
        "desc": 'Trying to use authorization code twice with 30 seconds in '
                'between uses must result in an error [Basic, Hybrid]',
        "sequence": [
            Note,
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            Registration,
            (AsyncAuthn, {set_response_where: {}}),
            AccessToken,
            TimeDelay,
            AccessToken,
        ],
        "profile": "C,CI,CT,CIT...",
        "tests": {
            "verify-response": {
                "response_cls": [ErrorResponse],
                "error": ["access_denied", "invalid_grant"],
                "status": ERROR}},
        "mti": {"all": "SHOULD"},
        "note": "A 30 second delay is added between the first and the second "
                "use of the authorization code.",
        "reference": "http://tools.ietf.org/html/draft-ietf-oauth-v2-31"
                     "#section-4.1",
    },
    'OP-Req-NotUnderstood': {
        "desc": 'Request with extra query component [Basic, Implicit, Hybrid]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            Registration,
            (AsyncAuthn, {set_response_where: {},
                          set_request_args: {"extra": "foobar"}})
        ],
        "profile": "...",
        'tests': {"verify-authn-response": {}},
        "mti": {"all": "MUST"},
    },
    'OP-Req-id_token_hint': {
        "desc": 'Using prompt=none with user hint through id_token_hint ['
                'Basic, Implicit, Hybrid]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            Registration,
            (AsyncAuthn, {set_response_where: {}}),
            AccessToken,
            (AsyncAuthn, {set_response_where: {},
                          set_request_args: {"prompt": "none"},
                          id_token_hint: None}),
            AccessToken,
        ],
        "profile": "...",
        'tests': {"same-authn": {},
                  "verify-response": {
                      "response_cls": [AuthorizationResponse,
                                       AccessTokenResponse]}},
        "mti": {"all": "SHOULD"},
    },
    'OP-Req-login_hint': {
        "desc": 'Providing login_hint [Basic, Implicit, Hybrid]',
        "sequence": [
            Note,
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            Registration,
            (AsyncAuthn, {set_response_where: {},
                          login_hint: None})
        ],
        "note": "Please remove any cookies you may have received from the "
                "OpenID Provider before proceeding. This test requests that "
                "you log in as "
                "a specific user, so a fresh login page is needed.",
        "profile": "...",
        'tests': {"verify-authn-response": {}},
        "mti": {"all": "No err"},
        "result": "You should be requested to log in as a predefined user"
    },
    'OP-Req-ui_locales': {
        "desc": 'Providing ui_locales [Basic, Implicit, Hybrid]',
        "sequence": [
            Note,
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            Registration,
            (AsyncAuthn, {set_response_where: {},
                          ui_locales: None})
        ],
        "note": "Please remove any cookies you may have received from the "
                "OpenID Provider before proceeding. You need to do this so "
                "you can check that the "
                "login page is displayed using one of the requested locales. "
                "The use of this parameter in the request must not cause an "
                "error at the OP.",
        "profile": "...",
        'tests': {"verify-authn-response": {}},
        "mti": {"all": "No err"}
    },
    'OP-Req-claims_locales': {
        "desc": 'Providing claims_locales [Basic, Implicit, Hybrid]',
        "sequence": [
            Note,
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            Registration,
            (AsyncAuthn, {set_response_where: {},
                          claims_locales: None}),
            AccessToken,
            USERINFO_REQUEST_AUTH_METHOD,
            DisplayUserInfo
        ],
        "note": "This test requests that claims be returned using the "
                "specified locale(s). "
                "The use of this parameter in the request must not cause an "
                "error at the OP.",
        "profile": "...",
        'tests': {"check-http-response": {}},
        "mti": {"all": "No err"}
    },
    'OP-Req-acr_values': {
        "desc": 'Providing acr_values [Basic, Implicit, Hybrid]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            Registration,
            (AsyncAuthn, {set_response_where: {},
                          acr_value: None}),
            AccessToken,
        ],
        "mti": {"all": "No err"},
        "profile": "...",
        'tests': {"used-acr-value": {},
                  "verify-response": {"response_cls": [AuthorizationResponse,
                                                       AccessTokenResponse]}}
    },
    'OP-Req-max_age=10000': {
        "desc": 'Requesting ID Token with max_age=10000 seconds restriction ['
                'Basic, Implicit, Hybrid]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            Registration,
            (AsyncAuthn, {set_response_where: {}}),
            AccessToken,
            (AsyncAuthn, {set_response_where: {},
                          set_request_args: {"max_age": 10000}}),
            AccessToken,
        ],
        "profile": "...",
        "tests": {"same-authn": {},
                  "verify-response": {
                      "response_cls": [AccessTokenResponse,
                                       AuthorizationResponse]},
                  "claims-check": {"id_token": ["auth_time"],
                                   "required": True},
                  "auth_time-check": {"max_age": 10000}},
        "mti": {"all": "MUST"}
    },
    'OP-Rotation-OP-Sig': {
        "desc": 'Can rotate OP signing keys [Dynamic]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            FetchKeys,
            Note,
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            FetchKeys,
        ],
        "note": "Please make your OP rotate its signing keys now. "
                "If you are not able to cause the server to rotate the keys "
                "while running the test, then you will have to self-assert "
                "that your deployment can do OP signing key rotation "
                "as part of your certification application.",
        "profile": "..T.T.s",
        # "profile": ".T.T.s.+",
        "tests": {"new-signing-keys": {},
                  "check-http-response": {}}
    },
    'OP-Rotation-RP-Sig': {
        "desc": 'Request access token, change RSA signing key and request '
                'another access token [Dynamic]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            (Registration, {
                set_request_args: {
                    "token_endpoint_auth_method": "private_key_jwt"},
                check_support: {
                    ERROR: {
                        "token_endpoint_auth_methods_supported":
                            "private_key_jwt"}}
            }),
            (AsyncAuthn, {set_response_where: {}}),
            (AccessToken, {set_op_args: {"authn_method": "private_key_jwt"}}),
            RotateSigKeys,
            (RefreshAccessToken, {set_op_args: {
                "authn_method": "private_key_jwt"}})
        ],
        "profile": "C,CI,CT,CIT...T.s",
        "tests": {"check-http-response": {}}
    },
    'OP-Rotation-OP-Enc': {
        "desc": 'Can rotate OP encryption keys [Extra]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            FetchKeys,
            Note,
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            FetchKeys,
        ],
        "note": "Please make your OP rotate its encryption keys now."
                "If you are not able to cause the server to rotate the keys "
                "while running the test, then you will have to self-assert "
                "that your deployment can do OP encryption key rotation "
                "as part of your certification application.",
        # "profile": ".T..e.+",
        "profile": "..T..e",
        "tests": {"new-encryption-keys": {}, "check-http-response": {}}
    },
    'OP-Rotation-RP-Enc': {
        # where is the RPs encryption keys used => userinfo encryption
        "desc": 'Request encrypted UserInfo, change RSA encryption key and '
                'request '
                'UserInfo again [Extra]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            (Registration,
             {
                 set_request_args: {
                     "userinfo_signed_response_alg": "none",
                     "userinfo_encrypted_response_alg": "RSA1_5",
                     "userinfo_encrypted_response_enc": "A128CBC-HS256"
                 },
                 check_support: {
                     WARNING: {
                         "userinfo_signing_alg_values_supported": "none",
                         "userinfo_encryption_alg_values_supported": "RSA1_5",
                         "userinfo_encryption_enc_values_supported":
                             "A128CBC-HS256"
                     }
                 }
             }
             ),
            (AsyncAuthn, {set_response_where: {}}),
            AccessToken,
            RotateEncKeys,
            UserInfo
        ],
        "profile": "C,CI,CT,CIT...T.se.+",
        "tests": {"check-http-response": {}}
    },
    'OP-claims-essential': {
        "desc": 'Claims request with essential name claim [Basic, Implicit, '
                'Hybrid]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            Registration,
            (AsyncAuthn, {
                set_response_where: {},
                set_request_args: {
                    "claims": {"userinfo": {"name": {"essential": True}}}}
            }),
            AccessToken,
            USERINFO_REQUEST_AUTH_METHOD
        ],
        "profile": "C,IT,CI,CT,CIT...",
        'tests': {"verify-claims": {"userinfo": {"name": None}},
                  "check-http-response": {}}
    },
    'OP-claims-sub': {
        "desc": 'Support claims request specifying sub value [Extra]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            Registration,
            (AsyncAuthn, {set_response_where: {}}),
            AccessToken,
            "cache",
            Note,
            (AsyncAuthn, {
                set_response_where: {},
                sub_claims: {}}),
            AccessToken,
        ],
        "note": "This test does one login to get a sub claim value. Then it "
                "does a fresh login using that sub value in a claims request. "
                "Please remove any cookies you received from the OpenID "
                "Provider before proceeding.",
        "profile": ".....+",
        "tests": {"verify-response": {"response_cls": [AuthorizationResponse,
                                                       AccessTokenResponse]},
                  "verify-sub-value": {}}
    },
    'OP-claims-IDToken': {
        "desc": 'Requesting ID Token with email claim [Extra]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            Registration,
            (AsyncAuthn, {
                set_response_where: {},
                set_request_args: {
                    "claims": {"id_token": {"email": {"essential": True}}}}}),
            AccessToken
        ],
        "profile": ".....+",
        'tests': {"verify-claims": {"id_token": {"email": None}},
                  "verify-response": {
                      "response_cls": [AccessTokenResponse,
                                       AuthorizationResponse]}}
    },
    'OP-claims-Split': {
        "desc": 'Supports returning different claims in ID Token and UserInfo '
                'Endpoint [Extra]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            Registration,
            (AsyncAuthn, {
                set_response_where: {},
                set_request_args: {
                    "claims": {
                        "id_token": {"email": {"essential": True}},
                        "userinfo": {"name": {"essential": True}}
                    }}}),
            AccessToken,
            USERINFO_REQUEST_AUTH_METHOD],
        "profile": "C,IT,CI,CIT,CT.....+",
        'tests': {"verify-claims": {"userinfo": {"name": None},
                                    "id_token": {"email": None}},
                  "check-http-response": {}}
    },
    'OP-claims-Combined': {
        "desc": 'Supports combining claims requested with scope and claims '
                'request parameter [Extra]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            Registration,
            (AsyncAuthn, {set_response_where: {},
                          set_request_args: {
                              "scope": ["openid", "phone"],
                              "claims": {
                                  "id_token": {"email": {"essential": True}},
                              }},
                          check_support: {
                              WARNING: {"scopes_supported": ["phone"]}}}),
            AccessToken,
            USERINFO_REQUEST_AUTH_METHOD
        ],
        "profile": "C,IT,CI,CIT,CT.....+",
        'tests': {"verify-claims": {"userinfo": {"phone": None},
                                    "id_token": {"email": None}},
                  "check-http-response": {}}
    },
    'OP-claims-voluntary': {
        "desc": 'Claims request with voluntary email and picture claims ['
                'Extra]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            Registration,
            (AsyncAuthn, {set_response_where: {},
                          set_request_args: {
                              "claims": {
                              "userinfo": {"picture": None, "email": None}}}}),
            AccessToken,
            USERINFO_REQUEST_AUTH_METHOD],
        "profile": "C,IT,CI,CIT,CT.....+",
        'tests': {"verify-claims": {"userinfo": {"picture": None,
                                                 "email": None}},
                  "check-http-response": {}}
    },
    'OP-claims-essential+voluntary': {
        "desc": (
            'Claims request with essential name and voluntary email and '
            'picture claims [Extra]'),
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            Registration,
            ((AsyncAuthn, {set_response_where: {}}), {
                set_request_args: {
                    "claims": {
                        "userinfo": {
                            "name": {"essential": True},
                            "picture": None,
                            "email": None}}}
            }),
            AccessToken,
            USERINFO_REQUEST_AUTH_METHOD
        ],
        "profile": "C,IT,CI,CIT,CT.....+",
        'tests': {"verify-claims": {"userinfo": {"picture": None,
                                                 "name": None,
                                                 "email": None}},
                  "check-http-response": {}}
    },
    'OP-claims-auth_time-essential': {
        "desc": 'Requesting ID Token with essential auth_time claim [Extra]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            Registration,
            (AsyncAuthn, {
                set_response_where: {},
                set_request_args: {
                    "claims": {"id_token": {"auth_time": {"essential": True}}}}
            }),
            AccessToken,
        ],
        "profile": ".....+",
        "mti": {"all": "MUST"},
        'tests': {"verify-claims": {"id_token": {"auth_time": None}},
                  "verify-response": {
                      "response_cls": [AccessTokenResponse,
                                       AuthorizationResponse]}}
    },
    'OP-claims-acr-essential': {
        "desc": 'Requesting ID Token with essential acr claim [Extra]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            Registration,
            (AsyncAuthn, {set_response_where: {},
                          set_request_args: {
                              "claims": {
                              "id_token": {"acr": {"essential": True}}}}}),
            AccessToken,
        ],
        "profile": ".....+",
        'tests': {"verify-claims": {"id_token": {"acr": None}},
                  "verify-response": {
                      "response_cls": [AccessTokenResponse,
                                       AuthorizationResponse]}}
    },
    'OP-claims-acr-voluntary': {
        "desc": 'Requesting ID Token with voluntary acr claim [Extra]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            Registration,
            (AsyncAuthn, {set_response_where: {},
                          set_request_args: {
                              "claims": {"id_token": {"acr": None}}}}),
            AccessToken,
        ],
        "profile": ".....+",
        'tests': {"verify-claims": {"id_token": {"acr": None}},
                  "verify-response": {
                      "response_cls": [AccessTokenResponse,
                                       AuthorizationResponse]}}
    },
    'OP-claims-acr=1': {
        "desc": 'Requesting ID Token with essential specific acr claim [Extra]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            Registration,
            (AsyncAuthn, {
                set_response_where: {},
                specific_acr_claims: {},
                check_support: {"error": {"acr_values_supported": ["1"]}}}),
            AccessToken,
        ],
        "profile": ".....+",
        'tests': {"verify-claims": {"id_token": {"acr": None}},
                  "verify-response": {
                      "response_cls": [AccessTokenResponse,
                                       AuthorizationResponse,
                                       ErrorResponse],
                      "error": ["access_denied"]}}
    },
    'OP-display-page': {
        "desc": 'Request with display=page [Basic, Implicit, Hybrid]',
        "sequence": [
            Note,
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            Registration,
            ('_login_',
             {
                 set_request_args: {"display": "page"},
                 check_support: {
                 "warning": {"display_values_supported": "page"}}
             })
        ],
        "note": "To make sure you get a login page, please remove any cookies "
                "you may have received from the OpenID Provider before "
                "proceeding. "
                "You should get a normal user agent login page view.",
        "profile": "...",
        'tests': {"verify-response": {"response_cls": [AuthorizationResponse]}},
        "mti": {"all": "No err"}
    },
    'OP-display-popup': {
        "desc": 'Request with display=popup [Basic, Implicit, Hybrid]',
        "sequence": [
            Note,
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            Registration,
            ('_login_',
             {
                 set_request_args: {"display": "popup"},
                 check_support: {
                 "warning": {"display_values_supported": "popup"}}
             })
        ],
        "note": "To make sure you get a login page, please remove any cookies "
                "you may have received from the OpenID Provider before "
                "proceeding. "
                "You should get a popup user agent login window.",
        "profile": "...",
        'tests': {"verify-response": {"response_cls": [AuthorizationResponse]}},
        "mti": {"all": "No err"}
    },
    'OP-prompt-login': {
        "desc": 'Request with prompt=login [Basic, Implicit, Hybrid]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            Registration,
            (AsyncAuthn, {set_response_where: {}}),
            '_accesstoken_',
            Note,
            ('_login_', {set_request_args: {"prompt": "login"}}),
            '_accesstoken_',
        ],
        "note": "You should be prompted to authenticate or re-authenticate. "
                "Please submit a screen shot of any authentication user "
                "interaction "
                "that occurred as part of your certification application.",
        "profile": "...",
        'tests': {
            "multiple-sign-on": {},
            "verify-response": {"response_cls": [AuthorizationResponse,
                                                 AccessTokenResponse]}},
        "mti": {"all": "MUST"},
        # "result": "The test passed if you were prompted to log in."
    },
    'OP-prompt-none-LoggedIn': {
        "desc": 'Request with prompt=none when logged in [Basic, Implicit, '
                'Hybrid]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            Registration,
            '_login_',
            '_accesstoken_',
            ('_login_', {set_request_args: {"prompt": "none"}}),
            '_accesstoken_'
        ],
        "mti": {"all": "MUST"},
        'tests': {"same-authn": {},
                  "verify-response": {"response_cls": [AuthorizationResponse,
                                                       AccessTokenResponse]}},
        "profile": "...",
        "result": "The test passed if you were not prompted to log in."
    },
    'OP-nonce-NoReq-code': {
        "desc": 'Login no nonce, code flow [Basic]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            Registration,
            ('_login_', {set_request_args: {"nonce": ""}})
        ],
        "profile": "C...",
        'tests': {"verify-response": {"response_cls": [AuthorizationResponse]}},
        "mti": {"all": "MUST"}
    },
    'OP-nonce-NoReq-noncode': {
        "desc": 'Reject requests without nonce unless using the code flow ['
                'Implicit, Hybrid]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            Registration,
            ('_login_', {set_request_args: {"nonce": ""}})
        ],
        "tests": {
            "verify-response": {
                "error": ["invalid_request"],
                "response_cls": [ErrorResponse]}},
        "profile": "I,IT,CI,CIT...",
        "mti": {"all": "MUST"}
    },
    'OP-nonce-code': {
        "desc": 'ID Token has nonce when requested for code flow [Basic]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            Registration,
            ('_login_', {set_request_args: {"nonce": "godmorgon"}}),
            '_accesstoken_'],
        "mti": {"all": "MUST"},
        "profile": "C...",
        "tests": {"verify-nonce": {},
                  "verify-response": {
                      "response_cls": [AccessTokenResponse,
                                       AuthorizationResponse]}}
    },
    'OP-nonce-noncode': {
        "desc": 'Request with nonce, verifies it was returned in ID Token ['
                'Implicit, Hybrid]',
        "sequence": ['_discover_', Registration, '_login_', '_accesstoken_'],
        "tests": {'check-idtoken-nonce': {},
                  "verify-response": {
                      "response_cls": [AccessTokenResponse,
                                       AuthorizationResponse]}},
        "profile": "I,IT,CI,CT,CIT...",
        "mti": {"all": "MUST"}
    },
    'OP-redirect_uri-NotReg': {
        "desc": 'Sent redirect_uri does not match a registered redirect_uri ['
                'Basic, Implicit, Hybrid]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            Registration,
            Note,
            (AsyncAuthn, {
                set_response_where: None,
                set_request_args: {
                    "redirect_uri": "https://foo.example.se/authz_cb"}})
        ],
        "profile": "...",
        "note": "This test should result in the OpenID Provider "
                "displaying an error message in your user agent. "
                "You should ignore the status of this test "
                "in the test tool, since it will be incomplete. "
                "You must submit a screen shot of the error shown "
                "as part of your certification application.",
        'tests': {"verify-response": {"response_cls": [ErrorResponse]}},
        "mti": {"all": "MUST"},
    },
    'OP-redirect_uri-Missing': {
        "desc": 'Reject request without redirect_uri when multiple registered '
                '[Dynamic]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            (Registration, {multiple_return_uris: None}),
            Note,
            (AsyncAuthn, {
                set_response_where: {},
                set_request_args: {"redirect_uri": ""}})
        ],
        "profile": "...T",
        'tests': {"verify-response": {"response_cls": [ErrorResponse]}},
        "note": "This test should result in the OpenID Provider "
                "displaying an error message in your user agent. "
                "You should ignore the status of this test "
                "in the test tool, since it will be incomplete. "
                "You must submit a screen shot of the error shown "
                "as part of your certification application.",
        "mti": {"all": "MUST"},
    },
    'OP-redirect_uri-Query-OK': {
        "desc": 'Request with a redirect_uri with a query component '
                'when a redirect_uri with the same query component is '
                'registered [Dynamic]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            (Registration, {
                redirect_uris_with_query_component: {"foo": "bar"}}),
            (AsyncAuthn, {
                set_response_where: {},
                redirect_uri_with_query_component: {"foo": "bar"}})
        ],
        "profile": "...T",
        "mti": {"all": "MUST"},
        "reference": "http://tools.ietf.org/html/draft-ietf-oauth-v2-31"
                     "#section-3.1.2",
        'tests': {"verify-response": {"response_cls": [AuthorizationResponse]},
                  "check-query-part": {"foo": "bar"}},
    },
    'OP-redirect_uri-Query-Mismatch': {
        "desc": 'Rejects redirect_uri when query parameter does not match '
                'what is registed [Dynamic]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            (Registration, {redirect_uris_with_query_component: {"foo": "bar"}}),
            Note,
            (AsyncAuthn, {
                set_response_where: {},
                # different from the one registered
                redirect_uri_with_query_component: {"bar": "foo"}})
        ],
        "profile": "...T",
        "reference": "http://tools.ietf.org/html/draft-ietf-oauth-v2-31"
                     "#section-3.1.2",
        "note": "This test should result in the OpenID Provider "
                "displaying an error message in your user agent. "
                "You should ignore the status of this test "
                "in the test tool, since it will be incomplete. "
                "You must submit a screen shot of the error shown "
                "as part of your certification application.",
        'tests': {
            "verify-response": {
                "response_cls": [ErrorResponse],
                "error": ["access_denied"]}},
        "mti": {"all": "MUST"},
    },
    'OP-redirect_uri-RegFrag': {
        "desc": 'Reject registration where a redirect_uri has a fragment ['
                'Dynamic]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            (Registration, {redirect_uris_with_fragment: {"foo": "bar"}})
        ],
        "profile": "...T",
        'tests': {
            "verify-response": {
                "response_cls": [ErrorResponse],
                "error": ["invalid_request",
                          "invalid_configuration_parameter",
                          "invalid_redirect_uri"]}},
        "mti": {"all": "MUST"},
        "reference": "http://tools.ietf.org/html/draft-ietf-oauth-v2-31"
                     "#section-3.1.2",
    },
    'OP-redirect_uri-MissingOK': {
        "desc": 'No redirect_uri in request with one registered [Extra]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            Registration,
            Note,
            (AsyncAuthn, {
                set_response_where: {},
                set_request_args: {"redirect_uri": ""}})
        ],
        "note": "This test may result in the OpenID Provider "
                "displaying an error message in your user agent. "
                "You should ignore the status of this test "
                "in the test tool if this happens, since it will be "
                "incomplete. "
                "It is also legal for the OP to successfully process "
                "this authentication request.",
        "profile": ".....+",
        'tests': {
            "verify-response": {"response_cls": [AuthorizationResponse]}},
    },
    'OP-request_uri-Support': {
        "desc": 'Support request_uri request parameter [Dynamic]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
        ],
        "profile": "...T",
        "tests": {"check-http-response": {},
                  "check-request_uri-parameter-supported-support": {}}
    },
    'OP-request_uri-Unsigned': {
        "desc": 'Support request_uri request parameter with unsigned request '
                '[Basic, Implicit, Hybrid]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            (Registration,
             {
                 set_request_args: {
                     "request_object_signing_alg": "none"},
                 check_support: {
                     WARNING: {
                         "request_uri_parameter_supported": True,
                         "request_object_signing_alg_values_supported": "none"}}
             }),
            (AsyncAuthn, {set_response_where: {},
                          set_op_args: {"request_method": "file",
                                        "local_dir": "export",
                                        "request_object_signing_alg": "none"},
                          request_in_file: None})
        ],
        "profile": "...F",
        "tests": {"authn-response-or-error": {
            "error": ["request_uri_not_supported"]}}
    },
    'OP-request_uri-Unsigned-Dynamic': {
        "desc": 'Support request_uri request parameter with unsigned request '
                '[Basic, Implicit, Hybrid, Dynamic]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            (Registration,
             {
                 set_request_args: {
                     "request_object_signing_alg": "none"},
                 check_support: {
                     "error": {
                         "request_uri_parameter_supported": True,
                         "request_object_signing_alg_values_supported": "none"}}
             }),
            (AsyncAuthn, {set_response_where: {},
                          set_op_args: {"request_method": "file",
                                        "local_dir": "export",
                                        "request_object_signing_alg": "none"},
                          request_in_file: None})
        ],
        "profile": "...T",
        "tests": {"verify-response": {"response_cls": [AuthorizationResponse]}}
    },
    'OP-request_uri-Sig': {
        "desc": 'Support request_uri request parameter with signed request ['
                'Dynamic]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            (Registration,
             {
                 set_request_args: {
                     "request_object_signing_alg": "RS256"},
                 check_support: {
                     "warning": {
                         "request_uri_parameter_supported": True,
                         "request_object_signing_alg_values_supported": "RS256"
                     }}
             }),
            (AsyncAuthn, {set_response_where: {},
                          set_op_args: {
                              "request_method": "file",
                              "local_dir": "export",
                              "request_object_signing_alg": "RS256"},
                          request_in_file: None})
        ],
        "profile": "...T.s",
        "tests": {"authn-response-or-error": {
            "error": ["request_uri_not_supported"]}}
    },
    'OP-request_uri-Enc': {
        "desc": 'Support request_uri request parameter with encrypted request '
                '[Extra]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            ("oic-registration",
             {
                 set_request_args: {
                     "request_object_signing_alg": "none",
                     "request_object_encryption_alg": "RSA1_5",
                     "request_object_encryption_enc": "A128CBC-HS256"
                 },
                 check_support: {
                     "warning": {
                         "request_uri_parameter_supported": True,
                         "request_object_signing_alg_values_supported": "none",
                         "request_object_encryption_alg_values_supported":
                             "RSA1_5",
                         "request_object_encryption_enc_values_supported":
                             "A128CBC-HS256"}
                 }
             }
             ),
            (AsyncAuthn, {set_response_where: {},
                          set_op_args: {
                              "request_method": "file",
                              "local_dir": "export",
                              "request_object_signing_alg": "none",
                              "request_object_encryption_alg": "RSA1_5",
                              "request_object_encryption_enc": "A128CBC-HS256"},
                          request_in_file: None})
        ],
        "profile": "...T.se.+",
        "tests": {"authn-response-or-error": {
            "error": ["request_uri_not_supported"]}}
    },
    'OP-request_uri-SigEnc': {
        "desc": 'Support request_uri request parameter with signed and '
                'encrypted request [Extra]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            ("oic-registration",
             {
                 set_request_args: {
                     "request_object_signing_alg": "RS256",
                     "request_object_encryption_alg": "RSA1_5",
                     "request_object_encryption_enc": "A128CBC-HS256"
                 },
                 check_support: {
                     "warning": {
                         "request_uri_parameter_supported": True,
                         "request_object_signing_alg_values_supported": "RS256",
                         "request_object_encryption_alg_values_supported":
                             "RSA1_5",
                         "request_object_encryption_enc_values_supported":
                             "A128CBC-HS256"}
                 }
             }
             ),
            (AsyncAuthn, {set_response_where: {},
                          set_op_args: {
                              "request_method": "file",
                              "local_dir": "export",
                              "request_object_signing_alg": "RS256",
                              "request_object_encryption_alg": "RSA1_5",
                              "request_object_encryption_enc": "A128CBC-HS256"},
                          request_in_file: None})
        ],
        "profile": "...T.se.+",
        "tests": {"authn-response-or-error": {
            "error": ["request_uri_not_supported"]}}
    },
    'OP-request-Support': {
        "desc": 'Support request request parameter [Extra]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            # (Registration,
            # {check_support: {"warning": {"request_parameter_supported":
            # True}}}),
            # ((AsyncAuthn, {set_response_where: {}}), {set_op_args: {
            # "request_method": "request"}})
        ],
        "profile": ".....+",
        "tests": {"check-http-response": {},
                  "check-request-parameter-supported-support": {}}
    },
    'OP-request-Unsigned': {
        "desc": 'Support request request parameter with unsigned request ['
                'Basic, Implicit, Hybrid, Dynamic]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            (Registration,
             {
                 set_request_args: {
                     "request_object_signing_alg": "none"},
                 check_support: {
                     "warning": {
                         "request_parameter_supported": True,
                         "request_object_signing_alg_values_supported": "none"}}
             }),
            (AsyncAuthn, {set_response_where: {},
                          set_op_args: {
                              "request_method": "request",
                              "request_object_signing_alg": "none"}})
        ],
        "profile": "...",
        "tests": {"authn-response-or-error": {
            "error": ["request_not_supported"]}}
    },
    'OP-request-Sig': {
        "desc": 'Support request request parameter with signed request [Extra]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            (Registration,
             {
                 set_request_args: {
                     "request_object_signing_alg": "RS256"},
                 check_support: {
                     "warning": {
                         "request_parameter_supported": True,
                         "request_object_signing_alg_values_supported": "RS256"
                     }}
             }),
            (AsyncAuthn, {set_response_where: {},
                          set_op_args: {
                              "request_method": "request",
                              "request_object_signing_alg": "RS256"}})
        ],
        "profile": "....s.+",
        "tests": {"authn-response-or-error": {
            "error": ["request_not_supported"]}}
    },
    'OP-scope-profile': {
        "desc": 'Scope requesting profile claims [Basic, Implicit, Hybrid]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            Registration,
            (AsyncAuthn, {
                set_response_where: {},
                set_request_args: {"scope": ["openid", "profile"]},
                check_support: {"warning": {"scopes_supported": ["profile"]}}}),
            AccessToken,
            (UserInfo, {
                set_op_args: {"authn_method": "bearer_header"},
                "method": "GET"
            })
        ],
        "profile": "...",
        "mti": {"all": "No err"},
        'tests': {"verify-response": {"response_cls": [OpenIDSchema,
                                                       AuthorizationResponse]},
                  "verify-scopes": {},
                  "check-http-response": {}}
    },
    'OP-scope-email': {
        "desc": 'Scope requesting email claims [Basic, Implicit, Hybrid]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            Registration,
            (AsyncAuthn, {
                set_response_where: {},
                set_request_args: {"scope": ["openid", "email"]},
                check_support: {"warning": {"scopes_supported": ["email"]}}
            }),
            AccessToken,
            (UserInfo, {
                set_op_args: {"authn_method": "bearer_header"},
                "method": "GET"
            })
        ],
        "profile": "...",
        "mti": "No err",
        'tests': {"verify-response": {"response_cls": [OpenIDSchema,
                                                       AuthorizationResponse]},
                  "verify-scopes": {},
                  "check-http-response": {}}
    },
    'OP-scope-address': {
        "desc": 'Scope requesting address claims [Basic, Implicit, Hybrid]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            Registration,
            (AsyncAuthn, {
                set_response_where: {},
                set_request_args: {"scope": ["openid", "address"]},
                check_support: {"warning": {"scopes_supported": ["address"]}}
            }),
            AccessToken,
            (UserInfo, {
                set_op_args: {"authn_method": "bearer_header"},
                "method": "GET"
            })
        ],
        "profile": "...",
        "mti": "No err",
        'tests': {"verify-response": {"response_cls": [OpenIDSchema,
                                                       AuthorizationResponse]},
                  "verify-scopes": {},
                  "check-http-response": {}}
    },
    'OP-scope-phone': {
        "desc": 'Scope requesting phone claims [Basic, Implicit, Hybrid]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            Registration,
            (AsyncAuthn, {
                set_response_where: {},
                set_request_args: {"scope": ["openid", "phone"]},
                check_support: {"warning": {"scopes_supported": ["phone"]}}
            }),
            AccessToken,
            (UserInfo, {
                set_op_args: {"authn_method": "bearer_header"},
                "method": "GET"
            })
        ],
        "profile": "...",
        "mti": "No err",
        'tests': {"verify-response": {"response_cls": [OpenIDSchema,
                                                       AuthorizationResponse]},
                  "verify-scopes": {},
                  "check-http-response": {}}
    },
    'OP-scope-All': {
        "desc": 'Scope requesting all claims [Basic, Implicit, Hybrid]',
        "sequence": [
            (Webfinger, {set_webfinger_resource: {}}),
            (Discovery, {set_discovery_issuer: {}}),
            Registration,
            (AsyncAuthn, {
                set_response_where: {},
                set_request_args: {"scope": ["openid", "profile", "email",
                                             "address", "phone"]},
                check_support: {
                    "warning": {"scopes_supported": ["profile", "email",
                                                     "address", "phone"]}}
            }),
            AccessToken,
            (UserInfo, {
                set_op_args: {"authn_method": "bearer_header"},
                "method": "GET"
            })
        ],
        "profile": "...",
        "mti": "No err",
        'tests': {"verify-response": {"response_cls": [OpenIDSchema,
                                                       AuthorizationResponse]},
                  "verify-scopes": {},
                  "check-http-response": {}}
    },
}
