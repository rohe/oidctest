import urllib.request, urllib.parse, urllib.error
import urllib.parse
from mako.lookup import TemplateLookup
from oic.oic import RegistrationResponse
from oic.oic import AuthorizationResponse
from oic.oic import AccessTokenResponse
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
parser.add_argument(dest="config")
args = parser.parse_args()

COM_ARGS, OP_ARG, config = main_setup(args, LOOKUP)

mode, endpoint = extract_mode(OP_ARG["baseurl"])

ENVIRON = {}

_op = setup_op(mode, COM_ARGS, OP_ARG, Trace())

##### rp-scope-contains_openid_scope/_/_/_/normal

# REGISTRATION

info = {
    'token_endpoint_auth_method': 'client_secret_post',
    'redirect_uris': [
        'https://connect.openid4.us:5443/phpRp/index.php/callback',
        'https://connect.openid4.us:5443/phpRp/authcheck.php/authcheckcb'],
    'jwks_uri': 'https://connect.openid4.us:5443/phpRp/rp/rp.jwk',
    'contacts': ['me@example.com'],
    'application_type': 'web',
    'client_name': 'ABRP-17',
    'grant_types': ['authorization_code', 'implicit'],
    'post_logout_redirect_uris': [
        'https://connect.openid4.us:5443/phpRp/index.php/logoutcb'],
    'subject_type': 'public',
    'response_types': ['code', 'token', 'id_token', 'code token',
                       'code id_token', 'id_token token',
                       'code id_token token'],
    'policy_uri': 'https://connect.openid4.us:5443/phpRp/index.php/policy',
    'request_object_signing_alg': 'RS256',
    'logo_uri': 'https://connect.openid4.us:5443/phpRp/media/logo.png'}

JWKS = {
    "keys": [
        {
            "e": "AQAB",
            "kty": "RSA",
            "n": "-Rpu7T6ytNNJ5G5crCkiplIEbPqPpoG"
                 "-zISyRDrRzBTMZuUJxxWF83NR97ZT_oajkHaAClYO"
                 "-OJLiYoI971WL0ZlbqdZ37MvsnF04oBAmzQLpASkuHpdI5sUDZ_ue7-TSU"
                 "-7X6qtxIPZpRqHSn_7O1Hxq6MawrC_Ibv"
                 "-UVh3USZb9edY8IvE977T5n6AlXVorhZhYom"
                 "-59F5IlAocqWylhMHBRqk2X8w0re4A0QyJS4MTBaFjJPlcNoGkkc09pBOst4esiWYr9muTNI3OMY7Yd7kPHjs01WR2XUBdhqb6XxinIkq9ax4z70-HFUHGczCABNv5l1PUVkj4FIwmAmwRw",
            "kid": "fyoue4377oTyV5g9rI2yu91pHR3P8H1Wa186nWd1G3A",
            "use": "sig"
        },
        {
            "e": "AQAB",
            "kty": "RSA",
            "n":
                "3RjNJx9wSGO5uQSqn_lOVj6i6sGK9ZPMHsz8R7v9NUXDdDWFsl4mcbavQTi_euz2RtDgZJhoCaVU2jgrCaPTrDJ8B8VpQjE1-TangJIDrkYh4r-Qi4SeqlFmTXjahpSLvzjzk0uMwywKZg1c0qfp0RcxH1KfYl3lSAsag1UJhffK2DJU7RqEY1TuWVnjVazADt42PtN-Uz71tTz9I-fUKzmiwdoYnfNNzx3Eu_E5X_ZZnosTKJ3RbHDWMJfN67gtAOByd7QYBVJWG7qBt8nOhtRSh9feDZ3bLbkfhQMazcesWctCIC1U7KGAtRN9ytyX2RkZiX2qBf9EbM9Q0wI71Q",
            "kid": "oQpTLDsGJ6FG_iSjrWdr6baDEwFw3r2dfqPPvHBjgyY",
            "use": "enc"
        }
    ]
}

RESP = {
    'client_id_issued_at': 1441245832,
    'token_endpoint_auth_method': 'client_secret_post',
    'redirect_uris': [
        'https://connect.openid4.us:5443/phpRp/index.php/callback',
        'https://connect.openid4.us:5443/phpRp/authcheck.php/authcheckcb'],
    'jwks_uri': 'https://connect.openid4.us:5443/phpRp/rp/rp.jwk',
    'contacts': ['me@example.com'],
    'application_type': 'web',
    'client_name': 'ABRP-17',
    'registration_client_uri':
        'https://rp.certification.openid.net:8080/rp-key_rotation'
        '-rp_enc_key/_/_/updkeys/normal/registration?client_id'
        '=rwfQ8i71ZGet',
    'registration_access_token': '8YRkQz7pSw4EaI4UJicMLVkPypunl2i1',
    'post_logout_redirect_uris': [
        'https://connect.openid4.us:5443/phpRp/index.php/logoutcb'],
    'subject_type': 'public',
    'response_types': ['code', 'token', 'id_token', 'code token',
                       'code id_token', 'id_token token',
                       'code id_token token'],
    'client_id': 'rwfQ8i71ZGet',
    'policy_uri': 'https://connect.openid4.us:5443/phpRp/index.php/policy',
    'grant_types': ['authorization_code', 'implicit'],
    'client_secret':
        'b646c21fb4d2abaf378454aa3497b01b638c8722cb958871efaf422e',
    'id_token_encrypted_response_alg': 'RSA1_5',
    'id_token_encrypted_response_enc': 'A128CBC-HS256',
    'logo_uri': 'https://connect.openid4.us:5443/phpRp/media/logo.png',
    'client_secret_expires_at': 1441332232
}

ruris = []
for ruri in RESP["redirect_uris"]:
    base, query = urllib.parse.splitquery(ruri)
    if query:
        ruris.append((base, urllib.parse.parse_qs(query)))
    else:
        ruris.append((base, query))

rr = RegistrationResponse(**RESP)
drr = rr.to_dict()
drr["redirect_uris"] = ruris

_op.cdb[RESP["client_id"]] = drr
_op.keyjar[RESP["client_id"]] = KeyBundle(keys=JWKS["keys"])
_op.keyjar.add_symmetric(issuer=RESP["client_id"], key=RESP["client_secret"],
                         usage=["sig"])

# AUTHZ REQ

AREQ = 'state=6d464d007f2dab07118932556d7dbf01&redirect_uri=https%3A%2F' \
       '%2Fconnect.openid4.us%3A5443%2FphpRp%2Findex.php%2Fcallback' \
       '&response_type=code&client_id=rwfQ8i71ZGet&nonce' \
       '=44a5b7ef45135233e8095a136be39a33&scope=openid+profile' \
       '&code_challenge_method=S256&code_challenge' \
       '=SM8WBlkhIbkjpg8oexuF6IfrdhOjyuqoXKOIO2dYzmY'

resp = _op.authorization_endpoint(AREQ)

parts = urllib.parse.urlparse(resp.message)

aresp = AuthorizationResponse().from_urlencoded(parts.query)

TPAT = "client_id=rwfQ8i71ZGet&code={" \
       "}&redirect_uri=https%3A%2F%2Fconnect.openid4.us%3A5443%2FphpRp" \
       "%2Findex.php%2Fcallback&grant_type=authorization_code&code_verifier" \
       "=fEQ2jENiGEOF3XtW6GxecZ6kbqzFAqknz3cQ4AQWSGk&client_secret={}"
TREQ = TPAT.format(urllib.parse.quote(aresp["code"]), RESP["client_secret"])

_resp = _op.token_endpoint(TREQ)

tresp = AccessTokenResponse().from_json(_resp.message)

authn = "Bearer {}".format(tresp["access_token"])

ui_resp = _op.userinfo_endpoint("", authn=authn)
print(ui_resp.message)
