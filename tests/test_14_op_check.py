import json

from Cryptodome.PublicKey import RSA
from jwkest.jwe import factory
from jwkest.jwk import keyitems2keyreps
from oic.oic import AuthorizationResponse
from oic.oic import AuthorizationRequest
from oic.oic import AccessTokenResponse
from oic.oic import IdToken
from oic.oic import ProviderConfigurationResponse
from oic.oic import OpenIDSchema
from oic.utils.keyio import build_keyjar
from oic.utils.keyio import KeyBundle
from oic.utils.time_util import utc_time_sans_frac
from otest import as_unicode

from oidctest.op.check import VerifyClaims
from oidctest.op.check import CheckHasClaimsSupported
from oidctest.op.check import VerifyOPEndpointsUseHTTPS
from oidctest.op.check import VerifyHTTPSUsage
from oidctest.op.check import VerifySubValue
from oidctest.op.check import VerifySignedIdTokenHasKID
from oidctest.op.check import VerifyScopes
from oidctest.op.check import VerifyOPHasRegistrationEndpoint
from oidctest.op.check import VerifyBase64URL
from oidctest.op.check import UsedAcrValue
from oidctest.op.check import VerifyUnSignedIdToken
from oidctest.op.check import CheckSignedEncryptedIDToken
from oidctest.op.check import SameAuthn
from oidctest.op.check import CheckHasJwksURI
from oidctest.op.check import NewSigningKeys
from oidctest.op.check import NewEncryptionKeys
from oidctest.op.check import MultipleSignOn
from oidctest.op.check import IsIDTokenSigned
from oidctest.op.check import CheckEncryptedUserInfo
from oidctest.op.check import CheckUserID
from oidctest.op.check import ClaimsCheck
from oidctest.op.check import CheckRequestURIParameterSupported
from oidctest.op.check import CheckRequestParameterSupported
from oidctest.op.check import CheckQueryPart
from oidctest.op.check import CheckIdTokenNonce
from oidctest.op.check import BareKeys
from oidctest.op.check import AuthTimeCheck
from oidctest.op.check import CheckAsymSignedUserInfo

from otest.check import CRITICAL
from otest.check import ERROR
from otest.check import WARNING
from otest.check import OK
from otest.events import EV_PROTOCOL_RESPONSE
from otest.events import EV_PROTOCOL_REQUEST
from otest.events import EV_REDIRECT_URL
from otest.events import EV_RESPONSE
from otest.test_setup import setup_conv

KEYDEFS = [
    {"type": "RSA", "key": '', "use": ["sig"]},
    {"type": "RSA", "key": '', "use": ["enc"]},
    {"type": "EC", "crv": "P-256", "use": ["sig"]},
    {"type": "EC", "crv": "P-256", "use": ["enc"]}
]

KEYJAR = build_keyjar(KEYDEFS)[1]
kb = KeyBundle([{"kty": "oct", "key": "supersecret", "use": "sig"}])
KEYJAR.add_kb('', kb)

atr = {
    "access_token":
        "ZDZjNWFmNzgtN2IxMi00YTY1LTk2NTEtODIyZjg5YmRlZThm0iWAl1",
    "expires_in": 7200,
    "id_token": {
        "at_hash": "fZlM5SoE8mdM80zBWSOzDQ",
        "aud": [
            "cb19ff50-6423-4955-92a2-73bea88796b4"
        ],
        "email": "johndoe@example.com",
        "exp": 1493066674,
        "iat": 1493059474,
        "iss": "https://guarded-cliffs-8635.herokuapp.com",
        "nonce": "WZ3PuYEnGxcM6ddf",
        "phone_number": "+49 000 000000",
        "phone_number_verified": False,
        "sid": "be99eccf-965f-4ba4-b0e4-39b0c26868e1",
        "sub": "9842f9ae-eb3c-4eba-8e4c-979ecae15fa1",
        'auth_time': utc_time_sans_frac()
    },
    "token_type": "Bearer"
}
ACCESS_TOKEN_RESPONSE_1 = AccessTokenResponse(**atr)

atr['id_token']['auth_time'] = utc_time_sans_frac() - 3600

ACCESS_TOKEN_RESPONSE_OLD = AccessTokenResponse(**atr)

atr = {
    "access_token":
        "ZDZjNWFmNzgtN2IxMi00YTY1LTk2NTEtODIyZjg5Ym",
    "expires_in": 7200,
    "id_token": {
        "at_hash": "fZlM5SoE8mdM80zBWSOzDQ",
        "aud": [
            "cb19ff50-6423-4955-92a2-73bea88796b4"
        ],
        "exp": 1493066674,
        "iat": 1493059474,
        "iss": "https://guarded-cliffs-8635.herokuapp.com",
        "nonce": "WZ3PuYEnGxcM6ddf",
        "sid": "be99eccf-965f-4ba4-b0e4-39b0c26868e1",
        "sub": "9842f9ae-eb3c-4eba-8e4c-979ecae15fa1"
    },
    "token_type": "Bearer"
}
ACCESS_TOKEN_RESPONSE_2 = AccessTokenResponse(**atr)


class HTTPResponse(object):
    pass


class MockHttpClient(object):
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __call__(self, *args, **kwargs):
        resp = HTTPResponse()
        try:
            resp.status_code = self.kwargs['status']
        except KeyError:
            resp.status_code = 200

        _jwks = KEYJAR.export_jwks(issuer='')
        if 'error' in self.kwargs:
            if self.kwargs['error'] == 'broken_jwks':
                del _jwks['keys'][0]['e']

        resp.text = json.dumps(_jwks)
        return resp


def test_verify_claims_1():
    _info = setup_conv()
    conv = _info['conv']
    kwargs = {
        "id_token": {"email": None},
        "userinfo": {"phone": None}
    }

    # Add events
    _url = "https://guarded-cliffs-8635.herokuapp.com/auth?redirect_uri=https" \
           "%3A%2F%2Fnew-op.certification.openid.net%3A60011%2Fauthz_cb&state" \
           "=OzFXyxsdI0kuIwo6&claims=%7B%22id_token%22%3A+%7B%22email%22%3A" \
           "+%7B%22essential%22%3A+true%7D%7D%7D&response_type=code&nonce" \
           "=WZ3PuYEnGxcM6ddf&scope=openid+phone&client_id=cb19ff50-6423-4955" \
           "-92a2-73bea88796b4"
    conv.events.store(EV_REDIRECT_URL, _url)

    conv.events.store(EV_PROTOCOL_RESPONSE, ACCESS_TOKEN_RESPONSE_1)

    user_info = {
        "phone_number": "+49 000 000000",
        "phone_number_verified": False,
        "sub": "9842f9ae-eb3c-4eba-8e4c-979ecae15fa1"
    }
    conv.events.store(EV_PROTOCOL_RESPONSE, OpenIDSchema(**user_info))

    vc = VerifyClaims()
    vc._kwargs = kwargs
    res = vc._func(conv)

    assert res == {}


def test_verify_claims_2():
    _info = setup_conv()
    conv = _info['conv']
    kwargs = {
        "id_token": {"email": None},
        "userinfo": {"phone": None}
    }

    # Add events
    _url = "https://guarded-cliffs-8635.herokuapp.com/auth?redirect_uri=https" \
           "%3A%2F%2Fnew-op.certification.openid.net%3A60011%2Fauthz_cb&state" \
           "=OzFXyxsdI0kuIwo6&claims=%7B%22id_token%22%3A+%7B%22email%22%3A" \
           "+%7B%22essential%22%3A+true%7D%7D%7D&response_type=code&nonce" \
           "=WZ3PuYEnGxcM6ddf&scope=openid+phone&client_id=cb19ff50-6423-4955" \
           "-92a2-73bea88796b4"
    conv.events.store(EV_REDIRECT_URL, _url)

    conv.events.store(EV_PROTOCOL_RESPONSE, ACCESS_TOKEN_RESPONSE_2)

    user_info = {
        "phone_number": "+49 000 000000",
        "phone_number_verified": False,
        "sub": "9842f9ae-eb3c-4eba-8e4c-979ecae15fa1"
    }
    conv.events.store(EV_PROTOCOL_RESPONSE, OpenIDSchema(**user_info))

    vc = VerifyClaims()
    vc._kwargs = kwargs
    res = vc._func(conv)

    assert list(res.keys()) == ['idtoken']
    assert set(res['idtoken']['returned claims']) == {'nonce', 'sub', 'at_hash',
                                                      'iat', 'sid', 'aud',
                                                      'exp', 'iss'}
    assert res['idtoken']['required claims'] == ['email']


def test_verify_claims_3():
    _info = setup_conv()
    conv = _info['conv']
    kwargs = {
        "id_token": {"email": None},
        "userinfo": {"phone": None}
    }

    _arg = {
        "redirect_uri": "https://new-op.certification.openid.net:60011"
                        "/authz_cb",
        "state": "OzFXyxsdI0kuIwo6",
        "claims": {
            'id_token': {'email': {'essential': True}},
            'userinfo': {
                'sub': {'essential': True},
                'phone_number_verified': {'essential': True},
                'phone_number': {'essential': True},
            }
        },
        'response_type': 'code',
        'nonce': "WZ3PuYEnGxcM6ddf",
        'scope': ['openid', 'phone'],
        'client_id': 'cb19ff50-6423-4955'
    }
    ar = AuthorizationRequest(**_arg)
    # Add events
    _url = ar.request("https://guarded-cliffs-8635.herokuapp.com/auth")
    conv.events.store(EV_REDIRECT_URL, _url)

    conv.events.store(EV_PROTOCOL_RESPONSE, ACCESS_TOKEN_RESPONSE_1)

    user_info = {
        "sub": "9842f9ae-eb3c-4eba-8e4c-979ecae15fa1"
    }
    conv.events.store(EV_PROTOCOL_RESPONSE, OpenIDSchema(**user_info))

    vc = VerifyClaims()
    vc._kwargs = kwargs
    res = vc._func(conv)

    assert list(res.keys()) == ['userinfo']
    assert res['userinfo']['returned claims'] == ['sub']
    assert set(res['userinfo']['expected claims']) == {'phone_number_verified',
                                                       'phone_number', 'sub'}


def test_verify_claims_4():
    _info = setup_conv()
    conv = _info['conv']
    kwargs = {
        "id_token": {"email": None},
        "userinfo": {"phone": None}
    }

    # Add events
    _url = "https://guarded-cliffs-8635.herokuapp.com/auth?redirect_uri=https" \
           "%3A%2F%2Fnew-op.certification.openid.net%3A60011%2Fauthz_cb&state" \
           "=OzFXyxsdI0kuIwo6&claims=%7B%22id_token%22%3A+%7B%22email%22%3A" \
           "+%7B%22essential%22%3A+true%7D%7D%7D&response_type=code&nonce" \
           "=WZ3PuYEnGxcM6ddf&scope=openid+phone&client_id=cb19ff50-6423-4955" \
           "-92a2-73bea88796b4"
    conv.events.store(EV_REDIRECT_URL, _url)

    conv.events.store(EV_PROTOCOL_RESPONSE, ACCESS_TOKEN_RESPONSE_2)

    user_info = {
        "sub": "9842f9ae-eb3c-4eba-8e4c-979ecae15fa1"
    }
    conv.events.store(EV_PROTOCOL_RESPONSE, OpenIDSchema(**user_info))

    vc = VerifyClaims()
    vc._kwargs = kwargs
    res = vc._func(conv)

    assert set(res.keys()) == {'idtoken', 'userinfo'}
    assert set(res['userinfo']['returned claims']) == {'sub'}
    assert set(res['userinfo']['expected claims']) == {'phone_number_verified',
                                                       'phone_number', 'sub'}
    assert set(res['idtoken']['returned claims']) == {
        'nonce', 'sub', 'at_hash', 'iat', 'sid', 'aud', 'exp', 'iss'}
    assert res['idtoken']['required claims'] == ['email']


def test_providerinfo_has_claims_supported():
    _info = setup_conv()
    conv = _info['conv']
    conv.entity.provider_info = {'claims_supported': ['sub', 'email', 'phone']}

    c = CheckHasClaimsSupported()

    res = c._func(conv)
    assert res == {}
    assert c._status == OK


def test_providerinfo_has_claims_supported_false():
    _info = setup_conv()
    conv = _info['conv']
    conv.entity.provider_info = {
        'issuer': 'https://example.com',
        'authorization_endpoint': 'https://example.com/authz'}

    c = CheckHasClaimsSupported()

    res = c._func(conv)
    assert res == {}
    assert c._status == ERROR


def test_verify_op_endpoints_use_https():
    _info = setup_conv()
    conv = _info['conv']
    conv.entity.provider_info = {
        'issuer': 'https://example.com',
        'authorization_endpoint': 'https://example.com/authz',
        'token_endpoint': 'https://example.com/token',
        'userinfo_endpoint': 'https://example.com/userinfo',
    }

    v = VerifyOPEndpointsUseHTTPS()

    res = v._func(conv)
    assert res == {}
    assert v._status == OK


def test_verify_op_endpoints_use_https_false():
    _info = setup_conv()
    conv = _info['conv']
    conv.entity.provider_info = {
        'issuer': 'https://example.com',
        'authorization_endpoint': 'https://example.com/authz',
        'token_endpoint': 'https://example.com/token',
        'userinfo_endpoint': 'http://example.com/userinfo',
    }

    v = VerifyOPEndpointsUseHTTPS()

    res = v._func(conv)
    assert res == {}
    assert v._status == ERROR


def test_verify_https_usage():
    _info = setup_conv()
    conv = _info['conv']
    conv.entity.provider_info = {
        'issuer': 'https://example.com',
        'authorization_endpoint': 'https://example.com/authz',
        'token_endpoint': 'https://example.com/token',
        'userinfo_endpoint': 'http://example.com/userinfo',
        'jwks_uri': 'https://example.com/jwks.json'
    }

    v = VerifyHTTPSUsage()
    v._kwargs = {"endpoints": ["jwks_uri"]}
    res = v._func(conv)
    assert res == {}
    assert v._status == OK


def test_verify_https_usage_false():
    _info = setup_conv()
    conv = _info['conv']
    conv.entity.provider_info = {
        'issuer': 'https://example.com',
        'authorization_endpoint': 'https://example.com/authz',
        'token_endpoint': 'https://example.com/token',
        'userinfo_endpoint': 'http://example.com/userinfo',
        'jwks_uri': 'http://example.com/jwks.json'
    }

    v = VerifyHTTPSUsage()
    v._kwargs = {"endpoints": ["jwks_uri"]}
    res = v._func(conv)
    assert res == {}
    assert v._status == ERROR


def test_asym_signed_userinfo():
    """
    arg={'alg': 'RS256'}
    """
    _info = setup_conv()
    conv = _info['conv']
    user_info = {
        "sub": "9842f9ae-eb3c-4eba-8e4c-979ecae15fa1"
    }
    ui = OpenIDSchema(**user_info)
    jwt_key = KEYJAR.get_signing_key()
    jws = ui.to_jwt(key=jwt_key, algorithm="RS256")
    conv.events.store(EV_RESPONSE, jws)
    out = OpenIDSchema().from_jwt(jws, keyjar=KEYJAR)
    conv.events.store(EV_PROTOCOL_RESPONSE, out)

    chk = CheckAsymSignedUserInfo()
    kwargs = {}
    chk._kwargs = kwargs
    res = chk._func(conv)
    assert res == {}
    assert chk._status == OK


def test_asym_signed_userinfo_sym():
    """
    arg={'alg': 'RS256'}
    """
    _info = setup_conv()
    conv = _info['conv']
    user_info = {"sub": "9842f9ae-eb3c-4eba-8e4c-979ecae15fa1"}
    ui = OpenIDSchema(**user_info)
    jwt_key = KEYJAR.get_signing_key()
    jws = ui.to_jwt(key=jwt_key, algorithm="HS256")
    conv.events.store(EV_RESPONSE, jws)
    out = OpenIDSchema().from_jwt(jws, keyjar=KEYJAR)
    conv.events.store(EV_PROTOCOL_RESPONSE, out)

    chk = CheckAsymSignedUserInfo()
    kwargs = {}
    chk._kwargs = kwargs
    _ = chk._func(conv)
    assert chk._status == ERROR


def test_auth_time_check():
    """
    arg={'max_age': 10000, 'skew': 600}
    """
    _info = setup_conv()
    conv = _info['conv']

    # Need an AuthorizationRequest and a response with an IdToken
    ar = {
        'scope': 'openid',
        'redirect_uri': 'https://example.com/cb'
    }
    conv.events.store(EV_PROTOCOL_REQUEST, AuthorizationRequest(**ar))
    conv.events.store(EV_PROTOCOL_RESPONSE, ACCESS_TOKEN_RESPONSE_1)

    chk = AuthTimeCheck()
    kwargs = {'max_age': 10000, 'skew': 600}
    chk._kwargs = kwargs
    _ = chk._func(conv)
    assert chk._status == OK


def test_auth_time_check_to_old():
    """
    arg={'max_age': 10000, 'skew': 600}
    """
    _info = setup_conv()
    conv = _info['conv']

    # Need an AuthorizationRequest and a response with an IdToken
    ar = {
        'scope': 'openid',
        'redirect_uri': 'https://example.com/cb'
    }
    conv.events.store(EV_PROTOCOL_REQUEST, AuthorizationRequest(**ar))
    conv.events.store(EV_PROTOCOL_RESPONSE, ACCESS_TOKEN_RESPONSE_OLD)

    chk = AuthTimeCheck()
    kwargs = {'max_age': 300, 'skew': 600}
    chk._kwargs = kwargs
    _ = chk._func(conv)
    assert chk._status == WARNING


def test_bare_keys():
    """
    arg=None
    """
    _info = setup_conv()
    conv = _info['conv']

    pcr = {
        'jwks_uri': 'http://example.com/jwks.json'
    }
    # conv.events.store(EV_PROTOCOL_RESPONSE,
    #                   ProviderConfigurationResponse(**pcr))
    conv.entity.provider_info = ProviderConfigurationResponse(**pcr)
    conv.entity.http_request = MockHttpClient()

    chk = BareKeys()
    kwargs = {}
    chk._kwargs = kwargs
    _ = chk._func(conv)
    assert chk._status == OK


def test_bare_keys_status_400():
    """
    arg=None
    """
    _info = setup_conv()
    conv = _info['conv']

    pcr = {
        'jwks_uri': 'http://example.com/jwks.json'
    }
    # conv.events.store(EV_PROTOCOL_RESPONSE,
    #                   ProviderConfigurationResponse(**pcr))
    conv.entity.provider_info = ProviderConfigurationResponse(**pcr)
    conv.entity.http_request = MockHttpClient(status=400)

    chk = BareKeys()
    kwargs = {}
    chk._kwargs = kwargs
    _ = chk._func(conv)
    assert chk._status == WARNING


def test_bare_keys_status_broken_jwks():
    """
    arg=None
    """
    _info = setup_conv()
    conv = _info['conv']

    pcr = {
        'jwks_uri': 'http://example.com/jwks.json'
    }
    # conv.events.store(EV_PROTOCOL_RESPONSE,
    #                   ProviderConfigurationResponse(**pcr))
    conv.entity.provider_info = ProviderConfigurationResponse(**pcr)
    conv.entity.http_request = MockHttpClient(error='broken_jwks')

    chk = BareKeys()
    kwargs = {}
    chk._kwargs = kwargs
    _ = chk._func(conv)
    assert chk._status == WARNING


def test_check_idtoken_nonce():
    """
    arg=None
    """
    _info = setup_conv()
    conv = _info['conv']
    # Need AuthorizationRequest and IdToken
    _arg = {
        'scope': 'openid',
        'redirect_uri': 'https://example.com/cb',
        "nonce": "WZ3PuYEnGxcM6ddf",
        'state': 'some',
        'response_type': 'code',
        'client_id': 'cli'
    }
    _ar = AuthorizationRequest(**_arg)
    conv.events.store(EV_PROTOCOL_REQUEST, _ar)
    _url = _ar.request('https://guarded-cliffs-8635.herokuapp.com/auth')
    conv.events.store(EV_REDIRECT_URL, _url)
    conv.events.store(EV_PROTOCOL_RESPONSE, ACCESS_TOKEN_RESPONSE_1)

    chk = CheckIdTokenNonce()
    kwargs = {}
    chk._kwargs = kwargs
    res = chk._func(conv)
    assert chk._status == OK


def test_check_idtoken_nonce_mis():
    """
    arg=None
    """
    _info = setup_conv()
    conv = _info['conv']
    # Need AuthorizationRequest and IdToken
    _arg = {
        'scope': 'openid',
        'redirect_uri': 'https://example.com/cb',
        "nonce": "Somethingelse",
        'state': 'some',
        'response_type': 'code',
        'client_id': 'cli'
    }
    _ar = AuthorizationRequest(**_arg)
    conv.events.store(EV_PROTOCOL_REQUEST, _ar)
    _url = _ar.request('https://guarded-cliffs-8635.herokuapp.com/auth')
    conv.events.store(EV_REDIRECT_URL, _url)
    conv.events.store(EV_PROTOCOL_RESPONSE, ACCESS_TOKEN_RESPONSE_1)

    chk = CheckIdTokenNonce()
    kwargs = {}
    chk._kwargs = kwargs
    res = chk._func(conv)
    assert chk._status == ERROR


def test_check_query_part():
    """
    arg={'foo': 'bar'}
    """
    _info = setup_conv()
    conv = _info['conv']
    # Need AuthorizationResponse
    _arg = {
        'code': '12345678',
        'foo': 'bar',
        'state': 'some',
    }
    _ar = AuthorizationResponse(**_arg)
    conv.events.store(EV_PROTOCOL_RESPONSE, _ar)
    chk = CheckQueryPart()
    kwargs = {'foo': 'bar'}
    chk._kwargs = kwargs
    _ = chk._func(conv)
    assert chk._status == OK


def test_check_query_part_not():
    """
    arg={'foo': 'bar'}
    """
    _info = setup_conv()
    conv = _info['conv']
    # Need AuthorizationResponse
    _arg = {
        'code': '12345678',
        'state': 'some',
    }
    _ar = AuthorizationResponse(**_arg)
    conv.events.store(EV_PROTOCOL_RESPONSE, _ar)
    chk = CheckQueryPart()
    kwargs = {'foo': 'bar'}
    chk._kwargs = kwargs
    _ = chk._func(conv)
    assert chk._status == ERROR


def test_check_request_parameter_supported_support():
    """
    arg=None
    """
    _info = setup_conv()
    conv = _info['conv']
    # Need provider info
    pcr = {
        'jwks_uri': 'http://example.com/jwks.json',
        'request_parameter_supported': True
    }
    conv.entity.provider_info = ProviderConfigurationResponse(**pcr)

    chk = CheckRequestParameterSupported()
    kwargs = {}
    chk._kwargs = kwargs
    res = chk._func(conv)
    assert chk._status == OK


def test_check_request_parameter_supported_not_support():
    """
    arg=None
    """
    _info = setup_conv()
    conv = _info['conv']
    # Need provider info
    pcr = {
        'jwks_uri': 'http://example.com/jwks.json',
    }
    conv.entity.provider_info = ProviderConfigurationResponse(**pcr)

    chk = CheckRequestParameterSupported()
    kwargs = {}
    chk._kwargs = kwargs
    res = chk._func(conv)
    assert chk._status == CRITICAL


def test_check_request_uri_parameter_supported_support():
    """
    arg=None
    """
    _info = setup_conv()
    conv = _info['conv']
    # Need provider info
    pcr = {
        'jwks_uri': 'http://example.com/jwks.json',
        'request_uri_parameter_supported': True
    }
    conv.entity.provider_info = ProviderConfigurationResponse(**pcr)

    chk = CheckRequestURIParameterSupported()
    kwargs = {}
    chk._kwargs = kwargs
    res = chk._func(conv)
    assert chk._status == OK


def test_check_request_uri_parameter_supported_missing():
    """
    arg=None
    """
    _info = setup_conv()
    conv = _info['conv']
    # Need provider info
    pcr = {
        'jwks_uri': 'http://example.com/jwks.json',
    }
    _pr = ProviderConfigurationResponse(**pcr)
    # To deal with default values
    del _pr['request_uri_parameter_supported']
    conv.entity.provider_info = _pr

    chk = CheckRequestURIParameterSupported()
    kwargs = {}
    chk._kwargs = kwargs
    _ = chk._func(conv)
    # Missing value is interpreted as supported
    assert chk._status == OK


def test_check_request_uri_parameter_supported_not_support():
    """
    arg=None
    """
    _info = setup_conv()
    conv = _info['conv']
    # Need provider info
    pcr = {
        'jwks_uri': 'http://example.com/jwks.json',
        'request_uri_parameter_supported': False
    }
    conv.entity.provider_info = ProviderConfigurationResponse(**pcr)

    chk = CheckRequestURIParameterSupported()
    kwargs = {}
    chk._kwargs = kwargs
    res = chk._func(conv)
    assert chk._status == CRITICAL


def test_claims_check():
    """
    arg={'required': True, 'id_token': ['auth_time']}
    """
    _info = setup_conv()
    conv = _info['conv']
    # Need IdToken
    conv.events.store(EV_PROTOCOL_RESPONSE, ACCESS_TOKEN_RESPONSE_1)

    chk = ClaimsCheck()
    kwargs = {'required': True, 'id_token': ['auth_time']}
    chk._kwargs = kwargs
    res = chk._func(conv)
    assert chk._status == OK


def test_claims_check_missing():
    """
    arg={'required': True, 'id_token': ['auth_time']}
    """
    _info = setup_conv()
    conv = _info['conv']
    # Need IdToken
    conv.events.store(EV_PROTOCOL_RESPONSE, ACCESS_TOKEN_RESPONSE_2)

    chk = ClaimsCheck()
    kwargs = {'required': True, 'id_token': ['auth_time']}
    chk._kwargs = kwargs
    res = chk._func(conv)
    assert chk._status == ERROR


def test_different_sub():
    """
    arg=None
    """
    _info = setup_conv()
    conv = _info['conv']
    # Need 2 IdToken one with public and one pairwise sub
    atr = {
        "access_token":
            "ZDZjNWFmNzgtN2IxMi00YTY1LTk2NTEtODIyZjg5Ym",
        "expires_in": 7200,
        "id_token": {
            "aud": ["one"],
            "exp": 1493066674,
            "iat": 1493059474,
            "iss": "https://guarded-cliffs-8635.herokuapp.com",
            "nonce": "WZ3PuYEnGxcM6ddf",
            "sub": "public sub"
        },
        "token_type": "Bearer"
    }
    atr_pub = AccessTokenResponse(**atr)
    conv.events.store(EV_PROTOCOL_RESPONSE, atr_pub)
    atr = {
        "access_token":
            "ZDZjNWFmNzgtN2IxMi00YTY1LTk2NTEtODIyZjg5Ym",
        "expires_in": 7200,
        "id_token": {
            "aud": ["other"],
            "exp": 1493066674,
            "iat": 1493059474,
            "iss": "https://guarded-cliffs-8635.herokuapp.com",
            "nonce": "WZ3PuYEnGxcM6ddf",
            "sub": "pairwise sub"
        },
        "token_type": "Bearer"
    }
    atr_pw = AccessTokenResponse(**atr)
    conv.events.store(EV_PROTOCOL_RESPONSE, atr_pw)

    chk = CheckUserID()
    kwargs = {}
    chk._kwargs = kwargs
    chk._func(conv)
    assert chk._status == OK


def test_different_sub_same():
    """
    arg=None
    """
    _info = setup_conv()
    conv = _info['conv']
    # Need 2 IdToken one with public and one pairwise sub
    atr = {
        "access_token":
            "ZDZjNWFmNzgtN2IxMi00YTY1LTk2NTEtODIyZjg5Ym",
        "expires_in": 7200,
        "id_token": {
            "aud": ["one"],
            "exp": 1493066674,
            "iat": 1493059474,
            "iss": "https://guarded-cliffs-8635.herokuapp.com",
            "nonce": "WZ3PuYEnGxcM6ddf",
            "sub": "pairwise sub"
        },
        "token_type": "Bearer"
    }
    atr_pub = AccessTokenResponse(**atr)
    conv.events.store(EV_PROTOCOL_RESPONSE, atr_pub)
    atr = {
        "access_token":
            "ZDZjNWFmNzgtN2IxMi00YTY1LTk2NTEtODIyZjg5Ym",
        "expires_in": 7200,
        "id_token": {
            "aud": ["other"],
            "exp": 1493066674,
            "iat": 1493059474,
            "iss": "https://guarded-cliffs-8635.herokuapp.com",
            "nonce": "WZ3PuYEnGxcM6ddf",
            "sub": "pairwise sub"
        },
        "token_type": "Bearer"
    }
    atr_pw = AccessTokenResponse(**atr)
    conv.events.store(EV_PROTOCOL_RESPONSE, atr_pw)

    chk = CheckUserID()
    kwargs = {}
    chk._kwargs = kwargs
    chk._func(conv)
    assert chk._status == ERROR


def test_encrypted_userinfo():
    """
    arg=None
    """
    _info = setup_conv()
    conv = _info['conv']
    # Create encrypted UserInfo

    ui = OpenIDSchema(**{'sub': 'an identifier'})
    _keys = [k.key for k in
             KEYJAR.keys_by_alg_and_usage('', alg="RSA1_5", usage='enc')]
    _jwe = ui.to_jwe({'rsa': _keys}, alg="RSA1_5", enc="A128CBC-HS256")
    conv.events.store(EV_RESPONSE, _jwe)
    krs = keyitems2keyreps({'rsa': _keys})
    jwe = factory(_jwe)
    _res = jwe.decrypt(_jwe, krs)
    _ui = OpenIDSchema().from_json(as_unicode(_res))
    _ui.jwe_header = jwe.jwt.headers
    conv.events.store(EV_PROTOCOL_RESPONSE, _ui)
    chk = CheckEncryptedUserInfo()
    kwargs = {}
    chk._kwargs = kwargs
    chk._func(conv)
    assert chk._status == OK


def test_is_idtoken_signed():
    """
    arg={'alg': 'RS256'}
    """
    _info = setup_conv()
    conv = _info['conv']
    atr = {
        "access_token":
            "ZDZjNWFmNzgtN2IxMi00YTY1LTk2NTEtODIyZjg5Ym",
        "expires_in": 7200,
        "id_token": {
            "aud": ["one"],
            "exp": 1493066674,
            "iat": 1493059474,
            "iss": "https://guarded-cliffs-8635.herokuapp.com",
            "nonce": "WZ3PuYEnGxcM6ddf",
            "sub": "pairwise sub"
        },
        "token_type": "Bearer"
    }
    atr = AccessTokenResponse(**atr)
    # This is really cheating
    idt = IdToken(**atr['id_token'])
    idt.jws_header = {'alg': 'RSA'}
    atr['id_token'] = idt
    conv.events.store(EV_PROTOCOL_RESPONSE, atr)

    chk = IsIDTokenSigned()
    kwargs = {}
    chk._kwargs = kwargs
    chk._func(conv)
    assert chk._status == OK


def test_is_idtoken_signed_alg_none():
    """
    arg={'alg': 'RS256'}
    """
    _info = setup_conv()
    conv = _info['conv']
    atr = {
        "access_token": "ZDZjNWFmNzgtN2IxMi00YTY1LTk2NTEtODIyZjg5Ym",
        "expires_in": 7200,
        "id_token": {
            "aud": ["one"],
            "exp": 1493066674,
            "iat": 1493059474,
            "iss": "https://guarded-cliffs-8635.herokuapp.com",
            "nonce": "WZ3PuYEnGxcM6ddf",
            "sub": "pairwise sub"
        },
        "token_type": "Bearer"
    }
    atr = AccessTokenResponse(**atr)
    # This is really cheating
    idt = IdToken(**atr['id_token'])
    idt.jws_header = {'alg': 'none'}
    atr['id_token'] = idt
    conv.events.store(EV_PROTOCOL_RESPONSE, atr)

    chk = IsIDTokenSigned()
    kwargs = {}
    chk._kwargs = kwargs
    chk._func(conv)
    assert chk._status == OK
    assert chk._message == 'ID Token signed using alg=none'


def test_multiple_sign_on():
    """
    arg=None
    arg={'status': 2}
    """
    _info = setup_conv()
    conv = _info['conv']
    arg0 = {
        "access_token": "ZDZjNWFmNzgtN2IxMi00YTY1LTk2NTEtODIyZjg5Ym",
        "expires_in": 7200,
        "id_token": {
            "aud": ["one"],
            "exp": 1493066674,
            "iat": 1493059474,
            "iss": "https://guarded-cliffs-8635.herokuapp.com",
            "nonce": "WZ3PuYEnGxcM6ddf",
            "sub": "pairwise sub",
            'auth_time': 1493059470
        },
        "token_type": "Bearer"
    }
    atr0 = AccessTokenResponse(**arg0)
    conv.events.store(EV_PROTOCOL_RESPONSE, atr0)
    arg1 = {
        "access_token": "ZDZjNWFmNzgtN2IxMi00YTY1LTk2NTEtODIyZjg5Ym",
        "expires_in": 7200,
        "id_token": {
            "aud": ["one"],
            "exp": 1493066674,
            "iat": 1493059474,
            "iss": "https://guarded-cliffs-8635.herokuapp.com",
            "nonce": "WZ3PuYEnGxcM6ddf",
            "sub": "pairwise sub",
            'auth_time': 1493059480
        },
        "token_type": "Bearer"
    }
    atr1 = AccessTokenResponse(**arg1)
    conv.events.store(EV_PROTOCOL_RESPONSE, atr1)

    chk = MultipleSignOn()
    kwargs = {}
    chk._kwargs = kwargs
    res = chk._func(conv)
    assert chk._status == OK


def test_multiple_sign_on_same():
    """
    arg=None
    arg={'status': 2}
    """
    _info = setup_conv()
    conv = _info['conv']
    arg0 = {
        "access_token": "ZDZjNWFmNzgtN2IxMi00YTY1LTk2NTEtODIyZjg5Ym",
        "expires_in": 7200,
        "id_token": {
            "aud": ["one"],
            "exp": 1493066674,
            "iat": 1493059474,
            "iss": "https://guarded-cliffs-8635.herokuapp.com",
            "nonce": "WZ3PuYEnGxcM6ddf",
            "sub": "pairwise sub",
            'auth_time': 1493059470
        },
        "token_type": "Bearer"
    }
    atr0 = AccessTokenResponse(**arg0)
    conv.events.store(EV_PROTOCOL_RESPONSE, atr0)
    arg1 = {
        "access_token": "ZDZjNWFmNzgtN2IxMi00YTY1LTk2NTEtODIyZjg5Ym",
        "expires_in": 7200,
        "id_token": {
            "aud": ["one"],
            "exp": 1493066674,
            "iat": 1493059474,
            "iss": "https://guarded-cliffs-8635.herokuapp.com",
            "nonce": "WZ3PuYEnGxcM6ddf",
            "sub": "pairwise sub",
            'auth_time': 1493059470
        },
        "token_type": "Bearer"
    }
    atr1 = AccessTokenResponse(**arg1)
    conv.events.store(EV_PROTOCOL_RESPONSE, atr1)

    chk = MultipleSignOn()
    kwargs = {}
    chk._kwargs = kwargs
    res = chk._func(conv)
    assert chk._status == ERROR


def test_new_encryption_keys():
    """
    arg=None
    """
    _info = setup_conv()
    conv = _info['conv']
    rsa = RSA.generate(2048)
    kb0 = KeyBundle([{"kty": "rsa", "key": rsa, "use": "enc"}])
    conv.keybundle = [kb0]
    rsa = RSA.generate(2048)
    kb1 = KeyBundle([{"kty": "rsa", "key": rsa, "use": "enc"}])
    conv.keybundle.append(kb1)
    chk = NewEncryptionKeys()
    kwargs = {}
    chk._kwargs = kwargs
    chk._func(conv)
    assert chk._status == OK


def test_new_encryption_keys_same():
    """
    arg=None
    """
    _info = setup_conv()
    conv = _info['conv']
    # ----------------------
    rsa = RSA.generate(2048)
    kb0 = KeyBundle([{"kty": "rsa", "key": rsa, "use": "enc"}])
    conv.keybundle = [kb0]
    # rsa = RSA.generate(2048)
    kb1 = KeyBundle([{"kty": "rsa", "key": rsa, "use": "enc"}])
    conv.keybundle.append(kb1)
    # ----------------------
    chk = NewEncryptionKeys()
    kwargs = {}
    chk._kwargs = kwargs
    chk._func(conv)
    assert chk._status == WARNING


def test_new_signing_keys():
    """
    arg=None
    """
    _info = setup_conv()
    conv = _info['conv']
    # ----------------------
    rsa = RSA.generate(2048)
    kb0 = KeyBundle([{"kty": "rsa", "key": rsa, "use": "sig"}])
    conv.keybundle = [kb0]
    rsa = RSA.generate(2048)
    kb1 = KeyBundle([{"kty": "rsa", "key": rsa, "use": "sig"}])
    conv.keybundle.append(kb1)
    # ----------------------
    chk = NewSigningKeys()
    kwargs = {}
    chk._kwargs = kwargs
    res = chk._func(conv)
    assert chk._status == OK


def test_new_signing_keys_same():
    """
    arg=None
    """
    _info = setup_conv()
    conv = _info['conv']
    # ----------------------
    rsa = RSA.generate(2048)
    kb0 = KeyBundle([{"kty": "rsa", "key": rsa, "use": "sig"}])
    conv.keybundle = [kb0]
    kb1 = KeyBundle([{"kty": "rsa", "key": rsa, "use": "sig"}])
    conv.keybundle.append(kb1)
    # ----------------------
    chk = NewSigningKeys()
    kwargs = {}
    chk._kwargs = kwargs
    res = chk._func(conv)
    assert chk._status == WARNING


def test_providerinfo_has_jwks_uri():
    """
    arg=None
    """
    _info = setup_conv()
    conv = _info['conv']

    pcr = {
        'jwks_uri': 'http://example.com/jwks.json'
    }
    conv.entity.provider_info = ProviderConfigurationResponse(**pcr)

    chk = CheckHasJwksURI()
    kwargs = {}
    chk._kwargs = kwargs
    res = chk._func(conv)
    assert chk._status == OK


def test_providerinfo_has_jwks_uri_not():
    """
    arg=None
    """
    _info = setup_conv()
    conv = _info['conv']

    pcr = {
        'jwks': {'keys': [{'kty': 'oct'}]}
    }
    conv.entity.provider_info = ProviderConfigurationResponse(**pcr)

    chk = CheckHasJwksURI()
    kwargs = {}
    chk._kwargs = kwargs
    chk._func(conv)
    assert chk._status == ERROR


def test_same_authn():
    """
    arg=None
    """
    _info = setup_conv()
    conv = _info['conv']
    # ----------------------------------
    arg0 = {
        "access_token": "ZDZjNWFmNzgtN2IxMi00YTY1LTk2NTEtODIyZjg5Ym",
        "expires_in": 7200,
        "id_token": {
            "aud": ["one"],
            "exp": 1493066674,
            "iat": 1493059474,
            "iss": "https://guarded-cliffs-8635.herokuapp.com",
            "nonce": "WZ3PuYEnGxcM6ddf",
            "sub": "sub_id",
            'auth_time': 1493059470
        },
        "token_type": "Bearer"
    }
    atr0 = AccessTokenResponse(**arg0)
    conv.events.store(EV_PROTOCOL_RESPONSE, atr0)
    arg1 = {
        "access_token": "ZDZjNWFmNzgtN2IxMi00YTY1LTk2NTEtODIyZjg5Ym",
        "expires_in": 7200,
        "id_token": {
            "aud": ["one"],
            "exp": 1493066674,
            "iat": 1493059474,
            "iss": "https://guarded-cliffs-8635.herokuapp.com",
            "nonce": "WZ3PuYEnGxcM6ddf",
            "sub": "sub_id",
            'auth_time': 1493059470
        },
        "token_type": "Bearer"
    }
    atr1 = AccessTokenResponse(**arg1)
    conv.events.store(EV_PROTOCOL_RESPONSE, atr1)
    # ----------------------------------
    chk = SameAuthn()
    kwargs = {}
    chk._kwargs = kwargs
    chk._func(conv)
    assert chk._status == OK


def test_same_authn_not_same_time():
    """
    arg=None
    """
    _info = setup_conv()
    conv = _info['conv']
    # ----------------------------------
    arg0 = {
        "access_token": "ZDZjNWFmNzgtN2IxMi00YTY1LTk2NTEtODIyZjg5Ym",
        "expires_in": 7200,
        "id_token": {
            "aud": ["one"],
            "exp": 1493066674,
            "iat": 1493059474,
            "iss": "https://guarded-cliffs-8635.herokuapp.com",
            "nonce": "WZ3PuYEnGxcM6ddf",
            "sub": "sub_id",
            'auth_time': 1493059470
        },
        "token_type": "Bearer"
    }
    atr0 = AccessTokenResponse(**arg0)
    conv.events.store(EV_PROTOCOL_RESPONSE, atr0)
    arg1 = {
        "access_token": "ZDZjNWFmNzgtN2IxMi00YTY1LTk2NTEtODIyZjg5Ym",
        "expires_in": 7200,
        "id_token": {
            "aud": ["one"],
            "exp": 1493066674,
            "iat": 1493059474,
            "iss": "https://guarded-cliffs-8635.herokuapp.com",
            "nonce": "WZ3PuYEnGxcM6ddf",
            "sub": "sub_id",
            'auth_time': 1493059471
        },
        "token_type": "Bearer"
    }
    atr1 = AccessTokenResponse(**arg1)
    conv.events.store(EV_PROTOCOL_RESPONSE, atr1)
    # ----------------------------------
    chk = SameAuthn()
    kwargs = {}
    chk._kwargs = kwargs
    chk._func(conv)
    assert chk._status == ERROR


def test_same_authn_not_same_sub():
    """
    arg=None
    """
    _info = setup_conv()
    conv = _info['conv']
    # ----------------------------------
    arg0 = {
        "access_token": "ZDZjNWFmNzgtN2IxMi00YTY1LTk2NTEtODIyZjg5Ym",
        "expires_in": 7200,
        "id_token": {
            "aud": ["one"],
            "exp": 1493066674,
            "iat": 1493059474,
            "iss": "https://guarded-cliffs-8635.herokuapp.com",
            "nonce": "WZ3PuYEnGxcM6ddf",
            "sub": "sub_id1",
            'auth_time': 1493059470
        },
        "token_type": "Bearer"
    }
    atr0 = AccessTokenResponse(**arg0)
    conv.events.store(EV_PROTOCOL_RESPONSE, atr0)
    arg1 = {
        "access_token": "ZDZjNWFmNzgtN2IxMi00YTY1LTk2NTEtODIyZjg5Ym",
        "expires_in": 7200,
        "id_token": {
            "aud": ["one"],
            "exp": 1493066674,
            "iat": 1493059474,
            "iss": "https://guarded-cliffs-8635.herokuapp.com",
            "nonce": "WZ3PuYEnGxcM6ddf",
            "sub": "sub_id2",
            'auth_time': 1493059470
        },
        "token_type": "Bearer"
    }
    atr1 = AccessTokenResponse(**arg1)
    conv.events.store(EV_PROTOCOL_RESPONSE, atr1)
    # ----------------------------------
    chk = SameAuthn()
    kwargs = {}
    chk._kwargs = kwargs
    chk._func(conv)
    assert chk._status == ERROR


def test_signed_encrypted_idtoken():
    """
    arg={'enc_alg': 'RSA1_5', 'sign_alg': 'RS256', 'enc_enc': 'A128CBC-HS256'}
    """
    _info = setup_conv()
    conv = _info['conv']
    # -------------------------------------------------
    arg = {
        "access_token": "ZDZjNWFmNzgtN2IxMi00YTY1LTk2NTEtODIyZjg5Ym",
        "expires_in": 7200,
        "id_token": {
            "aud": ["one"],
            "exp": 1493066674,
            "iat": 1493059474,
            "iss": "https://guarded-cliffs-8635.herokuapp.com",
            "nonce": "WZ3PuYEnGxcM6ddf",
            "sub": "pairwise sub"
        },
        "token_type": "Bearer"
    }
    atr = AccessTokenResponse(**arg)
    # This is really cheating
    idt = IdToken(**atr['id_token'])
    idt.jws_header = {'alg': 'RS256'}
    idt.jwe_header = {'alg': 'RSA1_5', 'enc': 'A128CBC-HS256'}
    atr['id_token'] = idt
    conv.events.store(EV_PROTOCOL_RESPONSE, atr)
    # -------------------------------------------------
    chk = CheckSignedEncryptedIDToken()
    kwargs = {'enc_alg': 'RSA1_5', 'sign_alg': 'RS256',
              'enc_enc': 'A128CBC-HS256'}
    chk._kwargs = kwargs
    chk._func(conv)
    assert chk._status == OK


def test_signed_encrypted_idtoken_wrong_enc_alg():
    """
    arg={'enc_alg': 'RSA1_5', 'sign_alg': 'RS256', 'enc_enc': 'A128CBC-HS256'}
    """
    _info = setup_conv()
    conv = _info['conv']
    # -------------------------------------------------
    arg = {
        "access_token": "ZDZjNWFmNzgtN2IxMi00YTY1LTk2NTEtODIyZjg5Ym",
        "expires_in": 7200,
        "id_token": {
            "aud": ["one"],
            "exp": 1493066674,
            "iat": 1493059474,
            "iss": "https://guarded-cliffs-8635.herokuapp.com",
            "nonce": "WZ3PuYEnGxcM6ddf",
            "sub": "pairwise sub"
        },
        "token_type": "Bearer"
    }
    atr = AccessTokenResponse(**arg)
    # This is really cheating
    idt = IdToken(**atr['id_token'])
    idt.jws_header = {'alg': 'RS256'}
    idt.jwe_header = {'alg': 'RSA-OAEP', 'enc': 'A256GCM'}
    atr['id_token'] = idt
    conv.events.store(EV_PROTOCOL_RESPONSE, atr)
    # -------------------------------------------------
    chk = CheckSignedEncryptedIDToken()
    kwargs = {'enc_alg': 'RSA1_5', 'sign_alg': 'RS256',
              'enc_enc': 'A128CBC-HS256'}
    chk._kwargs = kwargs
    chk._func(conv)
    assert chk._status == ERROR


def test_signed_encrypted_idtoken_wrong_sig_alg():
    """
    arg={'enc_alg': 'RSA1_5', 'sign_alg': 'RS256', 'enc_enc': 'A128CBC-HS256'}
    """
    _info = setup_conv()
    conv = _info['conv']
    # -------------------------------------------------
    arg = {
        "access_token": "ZDZjNWFmNzgtN2IxMi00YTY1LTk2NTEtODIyZjg5Ym",
        "expires_in": 7200,
        "id_token": {
            "aud": ["one"],
            "exp": 1493066674,
            "iat": 1493059474,
            "iss": "https://guarded-cliffs-8635.herokuapp.com",
            "nonce": "WZ3PuYEnGxcM6ddf",
            "sub": "pairwise sub"
        },
        "token_type": "Bearer"
    }
    atr = AccessTokenResponse(**arg)
    # This is really cheating
    idt = IdToken(**atr['id_token'])
    idt.jws_header = {'alg': 'RS512'}
    idt.jwe_header = {'alg': 'RSA1_5', 'enc': 'A128CBC-HS256'}
    atr['id_token'] = idt
    conv.events.store(EV_PROTOCOL_RESPONSE, atr)
    # -------------------------------------------------
    chk = CheckSignedEncryptedIDToken()
    kwargs = {'enc_alg': 'RSA1_5', 'sign_alg': 'RS256',
              'enc_enc': 'A128CBC-HS256'}
    chk._kwargs = kwargs
    chk._func(conv)
    assert chk._status == ERROR


def test_unsigned_idtoken():
    """
    arg=None
    """
    _info = setup_conv()
    conv = _info['conv']
    # -------------------------------------------------
    arg = {
        "access_token": "ZDZjNWFmNzgtN2IxMi00YTY1LTk2NTEtODIyZjg5Ym",
        "expires_in": 7200,
        "id_token": {
            "aud": ["one"],
            "exp": 1493066674,
            "iat": 1493059474,
            "iss": "https://guarded-cliffs-8635.herokuapp.com",
            "nonce": "WZ3PuYEnGxcM6ddf",
            "sub": "pairwise sub"
        },
        "token_type": "Bearer"
    }
    atr = AccessTokenResponse(**arg)
    # This is really cheating
    idt = IdToken(**atr['id_token'])
    idt.jws_header = {'alg': 'none'}
    atr['id_token'] = idt
    conv.events.store(EV_PROTOCOL_RESPONSE, atr)
    # -------------------------------------------------
    chk = VerifyUnSignedIdToken()
    kwargs = {}
    chk._kwargs = kwargs
    chk._func(conv)
    assert chk._status == OK


def test_unsigned_idtoken_signed():
    """
    arg=None
    """
    _info = setup_conv()
    conv = _info['conv']
    # -------------------------------------------------
    arg = {
        "access_token": "ZDZjNWFmNzgtN2IxMi00YTY1LTk2NTEtODIyZjg5Ym",
        "expires_in": 7200,
        "id_token": {
            "aud": ["one"],
            "exp": 1493066674,
            "iat": 1493059474,
            "iss": "https://guarded-cliffs-8635.herokuapp.com",
            "nonce": "WZ3PuYEnGxcM6ddf",
            "sub": "pairwise sub"
        },
        "token_type": "Bearer"
    }
    atr = AccessTokenResponse(**arg)
    # This is really cheating
    idt = IdToken(**atr['id_token'])
    idt.jws_header = {'alg': 'RS256'}
    atr['id_token'] = idt
    conv.events.store(EV_PROTOCOL_RESPONSE, atr)
    # -------------------------------------------------
    chk = VerifyUnSignedIdToken()
    kwargs = {}
    chk._kwargs = kwargs
    chk._func(conv)
    assert chk._status == ERROR


def test_used_acr_value():
    """
    arg=None
    """
    _info = setup_conv()
    conv = _info['conv']
    # -------------------------------------------------
    ar = {
        'scope': 'openid',
        'redirect_uri': 'https://example.com/cb',
        'client_id': 'client',
        'response_type': 'code',
        'state': 'state',
        'acr_values': 'foo_bar'
    }
    _ar = AuthorizationRequest(**ar)
    _url = _ar.request('https://guarded-cliffs-8635.herokuapp.com/auth')

    conv.events.store(EV_REDIRECT_URL, _url)
    conv.events.store(EV_PROTOCOL_REQUEST, _ar)
    arg = {
        "access_token": "ZDZjNWFmNzgtN2IxMi00YTY1LTk2NTEtODIyZjg5Ym",
        "expires_in": 7200,
        "id_token": {
            "aud": ["one"],
            "exp": 1493066674,
            "iat": 1493059474,
            "iss": "https://guarded-cliffs-8635.herokuapp.com",
            "nonce": "WZ3PuYEnGxcM6ddf",
            "sub": "pairwise sub",
            'acr': 'foobar'
        },
        "token_type": "Bearer"
    }
    atr = AccessTokenResponse(**arg)
    idt = IdToken(**atr['id_token'])
    atr['id_token'] = idt
    conv.events.store(EV_PROTOCOL_RESPONSE, atr)
    # -------------------------------------------------
    chk = UsedAcrValue()
    kwargs = {}
    chk._kwargs = kwargs
    chk._func(conv)
    assert chk._status == WARNING


def test_used_acr_value_no_spec():
    """
    arg=None
    """
    _info = setup_conv()
    conv = _info['conv']
    # -------------------------------------------------
    ar = {
        'scope': 'openid',
        'redirect_uri': 'https://example.com/cb',
        'client_id': 'client',
        'response_type': 'code',
        'state': 'state',
        'acr_values': 'foo_bar'
    }
    _ar = AuthorizationRequest(**ar)
    _url = _ar.request('https://guarded-cliffs-8635.herokuapp.com/auth')

    conv.events.store(EV_REDIRECT_URL, _url)
    conv.events.store(EV_PROTOCOL_REQUEST, _ar)
    arg = {
        "access_token": "ZDZjNWFmNzgtN2IxMi00YTY1LTk2NTEtODIyZjg5Ym",
        "expires_in": 7200,
        "id_token": {
            "aud": ["one"],
            "exp": 1493066674,
            "iat": 1493059474,
            "iss": "https://guarded-cliffs-8635.herokuapp.com",
            "nonce": "WZ3PuYEnGxcM6ddf",
            "sub": "pairwise sub"
        },
        "token_type": "Bearer"
    }
    atr = AccessTokenResponse(**arg)
    idt = IdToken(**atr['id_token'])
    atr['id_token'] = idt
    conv.events.store(EV_PROTOCOL_RESPONSE, atr)
    # -------------------------------------------------
    chk = UsedAcrValue()
    kwargs = {}
    chk._kwargs = kwargs
    chk._func(conv)
    assert chk._status == WARNING


def test_used_acr_value_diff():
    """
    arg=None
    """
    _info = setup_conv()
    conv = _info['conv']
    # -------------------------------------------------
    ar = {
        'scope': 'openid',
        'redirect_uri': 'https://example.com/cb',
        'client_id': 'client',
        'response_type': 'code',
        'state': 'state',
        'acr_values': 'foo_bar'
    }
    _ar = AuthorizationRequest(**ar)
    _url = _ar.request('https://guarded-cliffs-8635.herokuapp.com/auth')

    conv.events.store(EV_REDIRECT_URL, _url)
    conv.events.store(EV_PROTOCOL_REQUEST, _ar)
    arg = {
        "access_token": "ZDZjNWFmNzgtN2IxMi00YTY1LTk2NTEtODIyZjg5Ym",
        "expires_in": 7200,
        "id_token": {
            "aud": ["one"],
            "exp": 1493066674,
            "iat": 1493059474,
            "iss": "https://guarded-cliffs-8635.herokuapp.com",
            "nonce": "WZ3PuYEnGxcM6ddf",
            "sub": "pairwise sub",
            'acr': 'barf'
        },
        "token_type": "Bearer"
    }
    atr = AccessTokenResponse(**arg)
    idt = IdToken(**atr['id_token'])
    atr['id_token'] = idt
    conv.events.store(EV_PROTOCOL_RESPONSE, atr)
    # -------------------------------------------------
    chk = UsedAcrValue()
    kwargs = {}
    chk._kwargs = kwargs
    chk._func(conv)
    assert chk._status == WARNING


def test_verify_base64url():
    """
    arg={'err_status': 3}
    """
    _info = setup_conv()
    conv = _info['conv']
    pcr = {
        'jwks_uri': 'http://example.com/jwks.json'
    }
    # conv.events.store(EV_PROTOCOL_RESPONSE,
    #                   ProviderConfigurationResponse(**pcr))
    conv.entity.provider_info = ProviderConfigurationResponse(**pcr)
    conv.entity.http_request = MockHttpClient()
    chk = VerifyBase64URL()
    kwargs = {}
    chk._kwargs = kwargs
    chk._func(conv)
    assert chk._status == OK


def test_verify_claims():
    """
    arg={'id_token': {'auth_time': None}}
    arg={'userinfo': {'name': None}}
    arg={'userinfo': {'phone': None}, 'id_token': {'email': None}}
    arg={'userinfo': {'picture': None, 'name': None, 'email': None}}
    """
    _info = setup_conv()
    conv = _info['conv']
    # ---------------------------------------
    ar = {
        'scope': 'openid',
        'redirect_uri': 'https://example.com/cb',
        'client_id': 'client',
        'response_type': 'code',
        'state': 'state',
        'acr_values': 'foo_bar',
        'claims': {
            'id_token': {'email': None},
            'userinfo': {'phone_number': None}
        }
    }
    _ar = AuthorizationRequest(**ar)
    _url = _ar.request('https://guarded-cliffs-8635.herokuapp.com/auth')

    conv.events.store(EV_REDIRECT_URL, _url)
    arg = {
        "access_token": "ZDZjNWFmNzgtN2IxMi00YTY1LTk2NTEtODIyZjg5Ym",
        "expires_in": 7200,
        "id_token": {
            "aud": ["one"],
            "exp": 1493066674,
            "iat": 1493059474,
            "iss": "https://guarded-cliffs-8635.herokuapp.com",
            "nonce": "WZ3PuYEnGxcM6ddf",
            "sub": "sub1",
            'acr': 'barf',
            'email': 'user@example.com'
        },
        "token_type": "Bearer"
    }
    atr = AccessTokenResponse(**arg)
    idt = IdToken(**atr['id_token'])
    atr['id_token'] = idt
    conv.events.store(EV_PROTOCOL_RESPONSE, atr)

    user_info = {
        "phone_number": "+49 000 000000",
        "sub": "sub1"
    }
    conv.events.store(EV_PROTOCOL_RESPONSE, OpenIDSchema(**user_info))

    # ---------------------------------------
    chk = VerifyClaims()
    kwargs = {'userinfo': {'phone': None}, 'id_token': {'email': None}}
    chk._kwargs = kwargs
    chk._func(conv)
    assert chk._status == OK


def test_verify_op_has_registration_endpoint():
    """
    arg=None
    """
    _info = setup_conv()
    conv = _info['conv']
    #
    pcr = {
        'jwks_uri': 'https://example.com/jwks.json',
        'registration_endpoint': 'https://example.com/register'
    }
    conv.entity.provider_info = ProviderConfigurationResponse(**pcr)
    #
    chk = VerifyOPHasRegistrationEndpoint()
    kwargs = {}
    chk._kwargs = kwargs
    chk._func(conv)
    assert chk._status == OK


def test_verify_scopes():
    """
    arg=None
    """
    _info = setup_conv()
    conv = _info['conv']

    # ---------------------------------------
    ar = {
        'scope': ['openid', 'email'],
        'redirect_uri': 'https://example.com/cb',
        'client_id': 'client',
        'response_type': 'code',
        'state': 'state',
    }
    _ar = AuthorizationRequest(**ar)
    _url = _ar.request('https://guarded-cliffs-8635.herokuapp.com/auth')

    conv.events.store(EV_REDIRECT_URL, _url)
    conv.events.store(EV_PROTOCOL_REQUEST, _ar)

    user_info = {
        "email": "sub@example.com",
        "email_verified": True,
        "sub": "sub1"
    }
    conv.events.store(EV_PROTOCOL_RESPONSE, OpenIDSchema(**user_info))

    # ---------------------------------------

    chk = VerifyScopes()
    kwargs = {}
    chk._kwargs = kwargs
    chk._func(conv)
    assert chk._status == OK


def test_verify_signed_idtoken_has_kid():
    """
    arg=None
    """
    _info = setup_conv()
    conv = _info['conv']
    #
    atr = {
        "access_token":
            "ZDZjNWFmNzgtN2IxMi00YTY1LTk2NTEtODIyZjg5Ym",
        "expires_in": 7200,
        "id_token": {
            "aud": ["one"],
            "exp": 1493066674,
            "iat": 1493059474,
            "iss": "https://guarded-cliffs-8635.herokuapp.com",
            "nonce": "WZ3PuYEnGxcM6ddf",
            "sub": "pairwise sub"
        },
        "token_type": "Bearer"
    }
    atr = AccessTokenResponse(**atr)
    # This is really cheating
    idt = IdToken(**atr['id_token'])
    idt.jws_header = {'alg': 'RSA', 'kid': 'keyID'}
    atr['id_token'] = idt
    conv.events.store(EV_PROTOCOL_RESPONSE, atr)
    #
    chk = VerifySignedIdTokenHasKID()
    kwargs = {}
    chk._kwargs = kwargs
    res = chk._func(conv)
    assert chk._status == OK


def test_verify_sub_value_OK():
    """
    arg=None
    """
    _info = setup_conv()
    conv = _info['conv']
    # Need an IdToken and an AuthorizationRequest with a claims request

    ar = {
        'scope': 'openid',
        'redirect_uri': 'https://example.com/cb',
        'client_id': 'client',
        'response_type': 'code',
        'state': 'state',
        'claims': {
            'id_token': {
                'sub': {'value': '9842f9ae-eb3c-4eba-8e4c-979ecae15fa1'}
            }
        }
    }
    _ar = AuthorizationRequest(**ar)
    _url = _ar.request('https://guarded-cliffs-8635.herokuapp.com/auth')

    conv.events.store(EV_REDIRECT_URL, _url)
    conv.events.store(EV_PROTOCOL_REQUEST, _ar)

    # Access token response with id_token with 'sub' claims
    conv.events.store(EV_PROTOCOL_RESPONSE, ACCESS_TOKEN_RESPONSE_2)

    chk = VerifySubValue()
    kwargs = {}
    chk._kwargs = kwargs
    _ = chk._func(conv)
    assert chk._status == OK


def test_verify_sub_value_NotOK_missing_claims():
    """
    arg=None
    """
    _info = setup_conv()
    conv = _info['conv']
    # Need an IdToken and an AuthorizationRequest with a claims request

    ar = {
        'scope': 'openid',
        'redirect_uri': 'https://example.com/cb',
        'client_id': 'client',
        'response_type': 'code',
        'state': 'state',
    }
    _ar = AuthorizationRequest(**ar)
    _url = _ar.request('https://guarded-cliffs-8635.herokuapp.com/auth')

    conv.events.store(EV_REDIRECT_URL, _url)
    conv.events.store(EV_PROTOCOL_REQUEST, _ar)

    # Access token response with id_token with 'sub' claims
    conv.events.store(EV_PROTOCOL_RESPONSE, ACCESS_TOKEN_RESPONSE_2)

    chk = VerifySubValue()
    kwargs = {}
    chk._kwargs = kwargs
    _ = chk._func(conv)
    assert chk._status == ERROR


def test_verify_sub_value_NotOK_wrong_sub():
    """
    arg=None
    """
    _info = setup_conv()
    conv = _info['conv']
    # Need an IdToken and an AuthorizationRequest with a claims request

    ar = {
        'scope': 'openid',
        'redirect_uri': 'https://example.com/cb',
        'client_id': 'client',
        'response_type': 'code',
        'state': 'state',
        'claims': {
            'id_token': {
                'sub': {'value': 'foo'}
            }
        }
    }
    _ar = AuthorizationRequest(**ar)
    _url = _ar.request('https://guarded-cliffs-8635.herokuapp.com/auth')

    conv.events.store(EV_REDIRECT_URL, _url)
    conv.events.store(EV_PROTOCOL_REQUEST, _ar)

    # Access token response with id_token with 'sub' claims
    conv.events.store(EV_PROTOCOL_RESPONSE, ACCESS_TOKEN_RESPONSE_2)

    chk = VerifySubValue()
    kwargs = {}
    chk._kwargs = kwargs
    _ = chk._func(conv)
    assert chk._status == ERROR
