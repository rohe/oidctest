from oic.oic import AccessTokenResponse, AuthorizationRequest
from oic.oic import OpenIDSchema
from oic.utils.keyio import build_keyjar, KeyBundle
from oic.utils.time_util import utc_time_sans_frac

from oidctest.op.check import VerifyClaims
from oidctest.op.check import CheckHasClaimsSupported
from oidctest.op.check import VerifyOPEndpointsUseHTTPS
from oidctest.op.check import VerifyHTTPSUsage
from oidctest.op.check import VerifySubValue
from oidctest.op.check import VerifySignedIdTokenHasKID
from oidctest.op.check import VerifyScopes
from oidctest.op.check import VerifyOPHasRegistrationEndpoint
from oidctest.op.check import VerifyNonce
from oidctest.op.check import VerifySignedIdToken
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

from otest.check import ERROR, WARNING
from otest.check import OK
from otest.events import EV_PROTOCOL_RESPONSE, EV_RESPONSE, EV_PROTOCOL_REQUEST
from otest.events import EV_REDIRECT_URL
from otest.test_setup import setup_conv

KEYDEFS = [
    {"type": "RSA", "key": '', "use": ["sig"]},
    {"type": "EC", "crv": "P-256", "use": ["sig"]}
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
        "sub": "9842f9ae-eb3c-4eba-8e4c-979ecae15fa1"
    }
    conv.events.store(EV_PROTOCOL_RESPONSE, OpenIDSchema(**user_info))

    vc = VerifyClaims()
    vc._kwargs = kwargs
    res = vc._func(conv)

    assert list(res.keys()) == ['userinfo']
    assert set(res['userinfo']['returned claims']) == {'sub'}
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

    conv.events.store(EV_PROTOCOL_RESPONSE, ACCESS_TOKEN_RESPONSE_1)

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
        'nonce', 'sub', 'at_hash', 'iat', 'sid', 'aud', 'exp', 'iss',
        'phone_number', 'phone_number_verified'}
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


# def test_bare_keys():
#     """
#     arg=None
#     """
#     _info = setup_conv()
#     conv = _info['conv']
#     chk = BareKeys()
#     kwargs = {}
#     chk._kwargs = kwargs
#     res = chk._func(conv)
#     asssert chk._status == OK
#
#
# def test_check_http_response():
#     """
#     arg=None
#     """
#     _info = setup_conv()
#     conv = _info['conv']
#     chk = CheckHTTPResponse()
#     kwargs = {}
#     chk._kwargs = kwargs
#     res = chk._func(conv)
#     asssert chk._status == OK
#
#
# def test_check_idtoken_nonce():
#     """
#     arg=None
#     """
#     _info = setup_conv()
#     conv = _info['conv']
#     chk = CheckIdTokenNonce()
#     kwargs = {}
#     chk._kwargs = kwargs
#     res = chk._func(conv)
#     asssert chk._status == OK
#
#
# def test_check_query_part():
#     """
#     arg={'foo': 'bar'}
#     """
#     _info = setup_conv()
#     conv = _info['conv']
#     chk = CheckQueryPart()
#     kwargs = {}
#     chk._kwargs = kwargs
#     res = chk._func(conv)
#     asssert chk._status == OK
#
#
# def test_check_request_parameter_supported_support():
#     """
#     arg=None
#     """
#     _info = setup_conv()
#     conv = _info['conv']
#     chk = CheckRequestParameterSupported()
#     kwargs = {}
#     chk._kwargs = kwargs
#     res = chk._func(conv)
#     asssert chk._status == OK
#
#
# def test_check_request_uri_parameter_supported_support():
#     """
#     arg=None
#     """
#     _info = setup_conv()
#     conv = _info['conv']
#     chk = CheckRequestURIParameterSupported()
#     kwargs = {}
#     chk._kwargs = kwargs
#     res = chk._func(conv)
#     asssert chk._status == OK
#
#
# def test_claims_check():
#     """
#     arg={'required': True, 'id_token': ['auth_time']}
#     """
#     _info = setup_conv()
#     conv = _info['conv']
#     chk = ClaimsCheck()
#     kwargs = {}
#     chk._kwargs = kwargs
#     res = chk._func(conv)
#     asssert chk._status == OK
#
#
# def test_different_sub():
#     """
#     arg=None
#     """
#     _info = setup_conv()
#     conv = _info['conv']
#     chk = CheckUserID()
#     kwargs = {}
#     chk._kwargs = kwargs
#     res = chk._func(conv)
#     asssert chk._status == OK
#
#
# def test_encrypted_userinfo():
#     """
#     arg=None
#     """
#     _info = setup_conv()
#     conv = _info['conv']
#     chk = CheckEncryptedUserInfo()
#     kwargs = {}
#     chk._kwargs = kwargs
#     res = chk._func(conv)
#     asssert chk._status == OK
#
#
# def test_is_idtoken_signed():
#     """
#     arg={'alg': 'RS256'}
#     """
#     _info = setup_conv()
#     conv = _info['conv']
#     chk = IsIDTokenSigned()
#     kwargs = {}
#     chk._kwargs = kwargs
#     res = chk._func(conv)
#     asssert chk._status == OK
#
#
# def test_multiple_sign_on():
#     """
#     arg=None
#     arg={'status': 2}
#     """
#     _info = setup_conv()
#     conv = _info['conv']
#     chk = MultipleSignOn()
#     kwargs = {}
#     chk._kwargs = kwargs
#     res = chk._func(conv)
#     asssert chk._status == OK
#
#
# def test_new_encryption_keys():
#     """
#     arg=None
#     """
#     _info = setup_conv()
#     conv = _info['conv']
#     chk = NewEncryptionKeys()
#     kwargs = {}
#     chk._kwargs = kwargs
#     res = chk._func(conv)
#     asssert chk._status == OK
#
#
# def test_new_signing_keys():
#     """
#     arg=None
#     """
#     _info = setup_conv()
#     conv = _info['conv']
#     chk = NewSigningKeys()
#     kwargs = {}
#     chk._kwargs = kwargs
#     res = chk._func(conv)
#     asssert chk._status == OK
#
#
# def test_providerinfo_has_jwks_uri():
#     """
#     arg=None
#     """
#     _info = setup_conv()
#     conv = _info['conv']
#     chk = CheckHasJwksURI()
#     kwargs = {}
#     chk._kwargs = kwargs
#     res = chk._func(conv)
#     asssert chk._status == OK
#
#
# def test_same_authn():
#     """
#     arg=None
#     """
#     _info = setup_conv()
#     conv = _info['conv']
#     chk = SameAuthn()
#     kwargs = {}
#     chk._kwargs = kwargs
#     res = chk._func(conv)
#     asssert chk._status == OK
#
#
# def test_signed_encrypted_idtoken():
#     """
#     arg={'enc_alg': 'RSA1_5', 'sign_alg': 'RS256', 'enc_enc': 'A128CBC-HS256'}
#     """
#     _info = setup_conv()
#     conv = _info['conv']
#     chk = CheckSignedEncryptedIDToken()
#     kwargs = {}
#     chk._kwargs = kwargs
#     res = chk._func(conv)
#     asssert chk._status == OK
#
#
# def test_unsigned_idtoken():
#     """
#     arg=None
#     """
#     _info = setup_conv()
#     conv = _info['conv']
#     chk = VerifyUnSignedIdToken()
#     kwargs = {}
#     chk._kwargs = kwargs
#     res = chk._func(conv)
#     asssert chk._status == OK
#
#
# def test_used_acr_value():
#     """
#     arg=None
#     """
#     _info = setup_conv()
#     conv = _info['conv']
#     chk = UsedAcrValue()
#     kwargs = {}
#     chk._kwargs = kwargs
#     res = chk._func(conv)
#     asssert chk._status == OK
#
#
# def test_verify_authn_response():
#     """
#     arg=None
#     """
#     _info = setup_conv()
#     conv = _info['conv']
#     chk = VerifyAuthnResponse()
#     kwargs = {}
#     chk._kwargs = kwargs
#     res = chk._func(conv)
#     asssert chk._status == OK
#
#
# def test_verify_base64url():
#     """
#     arg={'err_status': 3}
#     """
#     _info = setup_conv()
#     conv = _info['conv']
#     chk = VerifyBase64URL()
#     kwargs = {}
#     chk._kwargs = kwargs
#     res = chk._func(conv)
#     asssert chk._status == OK
#
#
# def test_verify_claims():
#     """
#     arg={'id_token': {'auth_time': None}}
#     arg={'userinfo': {'name': None}}
#     arg={'userinfo': {'phone': None}, 'id_token': {'email': None}}
#     arg={'userinfo': {'picture': None, 'name': None, 'email': None}}
#     """
#     _info = setup_conv()
#     conv = _info['conv']
#     chk = VerifyClaims()
#     kwargs = {}
#     chk._kwargs = kwargs
#     res = chk._func(conv)
#     asssert chk._status == OK
#
#
# def test_verify_error_response():
#     """
#     arg={'error': ['invalid_request', 'invalid_configuration_parameter',
#          'invalid_redirect_uri']}
#     """
#     _info = setup_conv()
#     conv = _info['conv']
#     chk = VerifyErrorMessage()
#     kwargs = {}
#     chk._kwargs = kwargs
#     res = chk._func(conv)
#     asssert chk._status == OK
#
#
# def test_verify_idtoken_is_signed():
#     """
#     arg={'alg': 'RS256'}
#     """
#     _info = setup_conv()
#     conv = _info['conv']
#     chk = VerifySignedIdToken()
#     kwargs = {}
#     chk._kwargs = kwargs
#     res = chk._func(conv)
#     asssert chk._status == OK
#
#
# def test_verify_nonce():
#     """
#     arg=None
#     """
#     _info = setup_conv()
#     conv = _info['conv']
#     chk = VerifyNonce()
#     kwargs = {}
#     chk._kwargs = kwargs
#     res = chk._func(conv)
#     asssert chk._status == OK
#
#
# def test_verify_op_has_registration_endpoint():
#     """
#     arg=None
#     """
#     _info = setup_conv()
#     conv = _info['conv']
#     chk = VerifyOPHasRegistrationEndpoint()
#     kwargs = {}
#     chk._kwargs = kwargs
#     res = chk._func(conv)
#     asssert chk._status == OK
#
#
# def test_verify_response():
#     """
#     arg={'error': ['access_denied'], 'response_cls': ['ErrorResponse']}
#     arg={'response_cls': ['AccessTokenResponse', 'AuthorizationResponse']}
#     arg={'response_cls': ['AuthorizationResponse', 'AccessTokenResponse']}
#     arg={'status': 2, 'response_cls': ['OpenIDSchema']}
#     arg={'error': ['access_denied', 'invalid_token'], 'status': 2,
#          'response_cls': ['ErrorResponse']}
#     """
#     _info = setup_conv()
#     conv = _info['conv']
#     chk = VerifyResponse()
#     kwargs = {}
#     chk._kwargs = kwargs
#     res = chk._func(conv)
#     asssert chk._status == OK
#
#
# def test_verify_scopes():
#     """
#     arg=None
#     """
#     _info = setup_conv()
#     conv = _info['conv']
#     chk = VerifyScopes()
#     kwargs = {}
#     chk._kwargs = kwargs
#     res = chk._func(conv)
#     asssert chk._status == OK
#
#
# def test_verify_signed_idtoken_has_kid():
#     """
#     arg=None
#     """
#     _info = setup_conv()
#     conv = _info['conv']
#     chk = VerifySignedIdTokenHasKID()
#     kwargs = {}
#     chk._kwargs = kwargs
#     res = chk._func(conv)
#     asssert chk._status == OK


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

