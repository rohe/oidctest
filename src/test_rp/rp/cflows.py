from jwkest import BadSignature
from oidctest.oper import Webfinger
from oidctest.oper import UserInfo
from oidctest.oper import AccessToken
from oidctest.oper import Discovery
from oidctest.oper import Registration
from oidctest.oper import Authn
from oidctest.testfunc import set_op_args, set_jwks_uri, resource
from oidctest.testfunc import expect_exception
from oidctest.testfunc import set_request_args

from oic.exception import IssuerMismatch, PyoidcError

__author__ = 'roland'

ORDDESC = ["rp-webfinger", "rp-discovery", "rp-registration", "rp-response_type", "rp-response_mode",
           "rp-token_endpoint", "rp-id_token", "rp-claims_reqest"]

FLOWS = {
   # "rp-discovery-webfinger_url": {
   #      "sequence": [Webfinger],
   #      "desc": "Can Discover Identifiers using URL Syntax",
   #      "profile": ".T..",
   # },
   #  "rp-discovery-webfinger_acct": {
   #      "sequence": [(Webfinger, {resource: {"pattern": "acct:{}@{}"}})],
   #      "desc": "Can Discover Identifiers using acct Syntax",
   #      "profile": ".T..",
   # },
   # "rp-discovery-openid_configuration": {
   #      "sequence": [
   #          Webfinger,
   #          Discovery
   #      ],
   #      "profile": "..T.",
   #      "desc": "Uses openid-configuration Discovery Information"
   # },
   # "rp-discovery-issuer_not_matching_config": {
   #      "sequence": [
   #          Webfinger,
   #          (Discovery, {expect_exception: IssuerMismatch})
   #      ],
   #      "profile": "..T.",
   #      "desc": "Retrieve openid-configuration information for OpenID Provider from the .well-known/openid-configuration path. Verify that the issuer in the openid-configuration matches the one returned by WebFinger"
   # },
   # "rp-discovery-jwks_uri_keys": {
   #      "sequence": [
   #          Webfinger,
   #          Discovery
   #      ],
   #      "profile": "..T.",
   #      "desc": "Can read and understand jwks_uri",
   #      "tests": {
   #          "providerinfo-has-jwks_uri": {},
   #          "bare-keys": {}
   #      }
   # },
   # "rp-discovery-mismatching_issuers": {
   #      "sequence": [
   #          Webfinger,
   #          (Discovery, {expect_exception: IssuerMismatch})
   #      ],
   #      "profile": "..T.",
   #      "desc": "Will detect a faulty issuer claim in OP config"
   #  },
   #  "rp-registration-dynamic": {
   #      "sequence": [
   #          Webfinger,
   #          Discovery,
   #          Registration
   #      ],
   #      "profile": "...T",
   #      "desc": "Uses Dynamic Registration"
   #  },
   #  "rp-registration-redirect_uris": {
   #      "sequence": [
   #        Webfinger,
   #        Discovery,
   #        (Registration, {set_request_args: {"redirect_uris": [""]}, expect_exception: PyoidcError}),
   #        Registration
   #      ],
   #      "profile": "...T",
   #      "desc": "Sends redirect_uris value which only contains a empty string while doing a registration request. Then send a valid redirect_uris list"
   #  },
   #  "rp-registration-uses_https_endpoints": {
   #      "sequence": [
   #        Webfinger,
   #        Discovery,
   #        (Registration, {set_request_args: {"redirect_uris": ["http://test.com"]}, expect_exception: PyoidcError}),
   #        Registration
   #      ],
   #      "profile": "...T",
   #      "desc": "Sends a redirect_uri endpoint which does not use https. The a valid redirect_uri is sent to the OP"
   #  },
   #  "rp-registration-well_formed_jwk": {
   #      "sequence": [
   #          Webfinger,
   #          Discovery,
   #          (Registration, {set_request_args: {"jwks": {
   #              "keys": [{
   #                           "use": "sig",
   #                           "n": "tAAzYdbiWDAKI8Q3s1crQRuVp0QXpyGgnzx_sGItC2rhdug68gE9v5mfK-7SJCBpuZXzX1YevJ25B0LhNQSWqvb6gYwlNHs33G8VmSzjpqFazItnhKMPnEehCXmPl7iFi8VV0NCC5_uH9xP61TClWsE8B7i4CV6y9B0hZI22p2M",
   #                           "e": "AQAB",
   #                           "kty": "RSA",
   #                           "kid": "a1"
   #                       }]},
   #                                             "id_token_signed_response_alg": "RS256", }}),
   #          (Authn, {set_op_args: {"response_type": ["id_token"]}}),
   #      ],
   #      "profile": "...T",
   #      "desc": ""
   #  },
   #  "rp-response_type-code": {
   #      "sequence": [
   #          Webfinger,
   #          Discovery,
   #          Registration,
   #          Authn
   #      ],
   #      "profile": "C...",
   #      "desc": "Can Make Request with 'code' Response Type"
   # },
   # "rp-response_type-id_token": {
   #      "sequence": [
   #          Webfinger,
   #          Discovery,
   #          (Registration,
   #           {set_request_args: {"id_token_signed_response_alg": "RS256"}}),
   #          Authn
   #      ],
   #      "desc": "Can Make Request with 'id_token' Response Type",
   #      "profile": "I...",
   # },
   # "rp-response_type-id_token+token": {
   #      "sequence": [
   #          Webfinger,
   #          Discovery,
   #          (Registration,
   #           {set_request_args: {"id_token_signed_response_alg": "RS256"}}),
   #          Authn
   #      ],
   #      "profile": "I,IT...",
   #      "desc": "Can Make Request with 'id_token token' Response Type"
   # },
   # "rp-response_mode-form_post": {
   #      "sequence": [
   #          Webfinger,
   #          Discovery,
   #          (Registration,
   #           {set_request_args: {"id_token_signed_response_alg": "RS256"}}),
   #          (Authn, {set_request_args: {"response_mode": ["form_post"]}})
   #      ],
   #      "profile": "I,IT...",
   #      "desc": "Can Make Request with response_mode=form_post"
   # },
   # "rp-token_endpoint-client_secret_basic": {
   #      "sequence": [
   #          Webfinger,
   #          Discovery,
   #          Registration,
   #          Authn,
   #          (AccessToken,
   #           {set_request_args: {"authn_method": "client_secret_basic"}})
   #      ],
   #      "profile": "C,CI,CIT...",
   #      "desc": "Can Make Access Token Request with 'client_secret_basic' "
   #              "Authentication"
   #  },
   #  #client_secret_post
   #  "rp-token_endpoint-client_secret_post": {
   #      "sequence": [
   #          Webfinger,
   #          Discovery,
   #          (Registration,
   #           {set_request_args: {
   #               "token_endpoint_auth_method": "client_secret_post"}}),
   #          Authn,
   #          (AccessToken,
   #           {set_request_args: {"authn_method": "client_secret_post"}})
   #      ],
   #      "profile": "C,CI,CIT...",
   #      "desc": "Can Make Access Token Request with 'client_secret_post' "
   #              "Authentication"
   # },
   # # client_secret_jwt
   # "rp-token_endpoint-client_secret_jwt": {
   #      "sequence": [
   #          Webfinger,
   #          Discovery,
   #          (Registration,
   #           {set_request_args: {
   #               "token_endpoint_auth_method": "client_secret_jwt"}}),
   #          Authn,
   #          (AccessToken,
   #           {set_request_args: {"authn_method": "client_secret_jwt"}})
   #      ],
   #      "profile": "C,CI,CIT...",
   #      "desc": "Can Make Access Token Request with 'client_secret_jwt' "
   #              "Authentication"
   # },
   # # private_key_jwt
   # "rp-token_endpoint-private_key_jwt": {
   #      "sequence": [
   #          Webfinger,
   #          Discovery,
   #          (Registration,
   #           {set_request_args: {
   #               "token_endpoint_auth_method": "private_key_jwt",
   #               "jwks_uri": "https://localhost:8088/static/jwk.json"}}),
   #          Authn,
   #          (AccessToken,
   #           {set_request_args: {"authn_method": "private_key_jwt"}})
   #      ],
   #      "profile": "C,CI,CIT...",
   #      "desc": "Can Make Access Token Request with 'private_key_jwt' "
   #              "Authentication"
   # },
   # "rp-idt-asym_sig": {
   #      "sequence": [
   #          Webfinger,
   #          Discovery,
   #          (Registration, {
   #              set_request_args: {
   #                  "id_token_signed_response_alg": "RS256"
   #              }
   #          }),
   #          (Authn, {set_op_args: {"response_type": ["id_token"]}}),
   #      ],
   #      "profile": "I...T",
   #      "desc": "Accept Valid Asymmetric ID Token Signature"
   # },
   # "rp-idt-sym_sig": {
   #      "sequence": [
   #          Webfinger,
   #          Discovery,
   #          (Registration, {
   #              set_request_args: {
   #                  "id_token_signed_response_alg": "HS256"
   #              }
   #          }),
   #          (Authn, {set_op_args: {"response_type": ["id_token"]}})
   #      ],
   #      "profile": "I...T",
   #      "desc": "Accept Valid Symmetric ID Token Signature"
   # },
   # "rp-idt-invalid-asym_sig": {
   #      "sequence": [
   #          Webfinger,
   #          Discovery,
   #          (Registration, {
   #              set_request_args: {
   #                  "id_token_signed_response_alg": "RS256"
   #              }
   #          }),
   #          (Authn, {
   #              set_op_args: {"response_type": ["id_token"]},
   #              expect_exception: BadSignature
   #          }),
   #      ],
   #      "profile": "I...T",
   #      "desc": "Reject Invalid Asymmetric ID Token Signature"
   # },
   # "rp-idt-invalid-ec_sig": {
   #      "sequence": [
   #          Webfinger,
   #          Discovery,
   #          (Registration, {
   #              set_request_args: {
   #                  "id_token_signed_response_alg": "ES256"
   #              }
   #          }),
   #          (Authn, {
   #              set_op_args: {"response_type": ["id_token"]},
   #              expect_exception: BadSignature
   #          })
   #      ],
   #      "profile": "I...T",
   #      "desc": "Reject Invalid Asymmetric ID Token Signature"
   # },
   # "rp-idt-invalid-sym_sig": {
   #      "sequence": [
   #          Webfinger,
   #          Discovery,
   #          (Registration, {
   #              set_request_args: {
   #                  "id_token_signed_response_alg": "HS256"
   #              }
   #          }),
   #          (Authn, {
   #              set_op_args: {"response_type": ["id_token"]},
   #              expect_exception: BadSignature
   #          })
   #      ],
   #      "profile": "I...T",
   #      "desc": "Reject Invalid Symmetric ID Token Signature"
   # },
   # "rp-id_token-sig+enc": {
   #      "sequence": [
   #          Webfinger,
   #          Discovery,
   #          (Registration, {
   #              set_request_args: {
   #                  "id_token_signed_response_alg": "HS256",
   #                  "id_token_encrypted_response_alg": "RSA1_5",
   #                  "id_token_encrypted_response_enc": "A128CBC-HS256"},
   #              set_jwks_uri: {}
   #          }),
   #          (Authn, {set_op_args: {"response_type": ["id_token"]}}),
   #      ],
   #      "profile": "I...T",
   #      "desc": "Can Request and Use Signed and Encrypted ID Token Response",
   # },
   #  "rp-idt-none": {
   #      "sequence": [
   #          Webfinger,
   #          Discovery,
   #          (Registration, {
   #              set_request_args: {"id_token_signed_response_alg": "none"}
   #          }),
   #          (Authn, {set_op_args: {"response_type": ["code"]}}),
   #          AccessToken
   #      ],
   #      "profile": "C,CT,CIT...T",
   #      "desc": "Can Request and Use unSigned ID Token Response"
   #  },
    "rp-claims_reqest-id_token_claims": {
        "sequence": [
            Webfinger,
            Discovery,
            Registration,
            (Authn, {set_request_args: {"claims":
                                            {
                                                "id_token":
                                                    {
                                                        "auth_time": {"essential": True},
                                                        "email": {"essential": True},
                                                    }
                                            }
                                        }}),
        ],
        "profile": "...T",
        "desc": "The Relying Party can ask for a specific claim using the 'claims' request parameter. The claim should be returned in an ID Token"
   },
}
