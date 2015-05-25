from oidctest.oper import Webfinger
from oidctest.oper import AccessToken
from oidctest.oper import Discovery
from oidctest.oper import Registration
from oidctest.oper import Authn
from oidctest.testfunc import resource
from oidctest.testfunc import set_jwks_uri
from oidctest.testfunc import set_op_args
from oidctest.testfunc import expect_exception
from oidctest.testfunc import set_request_args

from oic.exception import IssuerMismatch

__author__ = 'roland'

ORDDESC = ["rp-webfinger", "rp-discovery", "rp-dynamic_registration", "rp-response_type", "rp-response_mode",
           "rp-token_endpoint", "rp-id_token"]

FLOWS = {
    # "rp-discovery-webfinger_url": {
    #     "sequence": [Webfinger],
    #     "desc": "Can Discover Identifiers using URL Syntax",
    #     "profile": ".T..",
    # },
    # "rp-discovery-webfinger_acct": {
    #     "sequence": [(Webfinger, {resource: {"pattern": "acct:{}@{}"}})],
    #     "desc": "Can Discover Identifiers using acct Syntax",
    #     "profile": ".T..",
    # },
    # "rp-discovery-openid_configuration": {
    #     "sequence": [
    #         Webfinger,
    #         Discovery
    #     ],
    #     "profile": "..T.",
    #     "desc": "Uses openid-configuration Discovery Information"
    # },
    # "rp-discovery-issuer_not_matching_config": {
    #     "sequence": [
    #         Webfinger,
    #         (Discovery, {expect_exception: IssuerMismatch})
    #     ],
    #     "profile": "..T.",
    #     "desc": "Retrieve openid-configuration information for OpenID Provider from the .well-known/openid-configuration path. Verify that the issuer in the openid-configuration matches the one returned by WebFinger"
    # },
    # "rp-discovery-jwks_uri_keys": {
    #     "sequence": [
    #         Webfinger,
    #         Discovery
    #     ],
    #     "profile": "..T.",
    #     "desc": "Can read and understand jwks_uri",
    #     "tests": {
    #         "providerinfo-has-jwks_uri": {},
    #         "bare-keys": {}
    #     }
    # },
    # "rp-discovery-mismatching_issuers": {
    #     "sequence": [
    #         Webfinger,
    #         (Discovery, {expect_exception: IssuerMismatch})
    #     ],
    #     "profile": "..T.",
    #     "desc": "Will detect a faulty issuer claim in OP config"
    # },
    # "rp-registration-dynamic": {
    #     "sequence": [
    #         Webfinger,
    #         Discovery,
    #         Registration
    #     ],
    #     "profile": "...T",
    #     "desc": "Uses Dynamic Registration"
    # },
    # "rp-response_type-code": {
    #     "sequence": [
    #         Webfinger,
    #         Discovery,
    #         Registration,
    #         Authn
    #     ],
    #     "profile": "C...",
    #     "desc": "Can Make Request with 'code' Response Type"
    # },
    #  "rp-response_type-id_token": {
    #     "sequence": [
    #         Webfinger,
    #         Discovery,
    #         (Registration,
    #          {set_request_args: {"id_token_signed_response_alg": "RS256"}}),
    #         Authn
    #     ],
    #     "desc": "Can Make Request with 'id_token' Response Type",
    #     "profile": "I...",
    # },
    # "rp-response_type-id_token+token": {
    #     "sequence": [
    #         Webfinger,
    #         Discovery,
    #         (Registration,
    #          {set_request_args: {"id_token_signed_response_alg": "RS256"}}),
    #         Authn
    #     ],
    #     "profile": "I,IT...",
    #     "desc": "Can Make Request with 'id_token token' Response Type"
    # },
    # "rp-response_mode-form_post": {
    #     "sequence": [
    #         Webfinger,
    #         Discovery,
    #         (Registration,
    #          {set_request_args: {"id_token_signed_response_alg": "RS256"}}),
    #         (Authn, {set_request_args: {"response_mode": ["form_post"]}})
    #     ],
    #     "profile": "I,IT...",
    #     "desc": "Can Make Request with response_mode=form_post"
    # },
    # "rp-token_endpoint-client_secret_basic": {
    #     "sequence": [
    #         Webfinger,
    #         Discovery,
    #         Registration,
    #         Authn,
    #         (AccessToken,
    #          {set_request_args: {"authn_method": "client_secret_basic"}})
    #     ],
    #     "profile": "C,CI,CIT...",
    #     "desc": "Can Make Access Token Request with 'client_secret_basic' "
    #             "Authentication"
    # },
    # #client_secret_post
    # "rp-token_endpoint-client_secret_post": {
    #     "sequence": [
    #         Webfinger,
    #         Discovery,
    #         (Registration,
    #          {set_request_args: {
    #              "token_endpoint_auth_method": "client_secret_post"}}),
    #         Authn,
    #         (AccessToken,
    #          {set_request_args: {"authn_method": "client_secret_post"}})
    #     ],
    #     "profile": "C,CI,CIT...",
    #     "desc": "Can Make Access Token Request with 'client_secret_post' "
    #             "Authentication"
    # },
    # # client_secret_jwt
    # "rp-token_endpoint-client_secret_jwt": {
    #     "sequence": [
    #         Webfinger,
    #         Discovery,
    #         (Registration,
    #          {set_request_args: {
    #              "token_endpoint_auth_method": "client_secret_jwt"}}),
    #         Authn,
    #         (AccessToken,
    #          {set_request_args: {"authn_method": "client_secret_jwt"}})
    #     ],
    #     "profile": "C,CI,CIT...",
    #     "desc": "Can Make Access Token Request with 'client_secret_jwt' "
    #             "Authentication"
    # },
    # # private_key_jwt
    # "rp-token_endpoint-private_key_jwt": {
    #     "sequence": [
    #         Webfinger,
    #         Discovery,
    #         (Registration,
    #          {set_request_args: {
    #              "token_endpoint_auth_method": "private_key_jwt",
    #              "jwks_uri": "https://localhost:8088/static/jwk.json"}}),
    #         Authn,
    #         (AccessToken,
    #          {set_request_args: {"authn_method": "private_key_jwt"}})
    #     ],
    #     "profile": "C,CI,CIT...",
    #     "desc": "Can Make Access Token Request with 'private_key_jwt' "
    #             "Authentication"
    # },
    # "rp-id_token-sig+enc": {
    #     "sequence": [
    #         Webfinger,
    #         Discovery,
    #         (Registration, {
    #             set_request_args: {
    #                 "id_token_signed_response_alg": "HS256",
    #                 "id_token_encrypted_response_alg": "RSA1_5",
    #                 "id_token_encrypted_response_enc": "A128CBC-HS256"},
    #             set_jwks_uri: {}
    #         }),
    #         (Authn, {set_op_args: {"response_type": ["id_token"]}}),
    #     ],
    #     "profile": "I...T",
    #     "desc": "Can Request and Use Signed and Encrypted ID Token Response",
    # },
}
