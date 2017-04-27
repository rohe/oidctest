from oic.oic import AccessTokenResponse
from oic.oic import OpenIDSchema
from oidctest.op.check import VerifyClaims, CheckHasClaimsSupported, \
    VerifyOPEndpointsUseHTTPS, VerifyHTTPSUsage
from otest.check import OK, ERROR

from otest.test_setup import setup_conv
from otest.events import EV_PROTOCOL_RESPONSE
from otest.events import EV_REDIRECT_URL


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

    atr = {
        "access_token":
            "ZDZjNWFmNzgtN2IxMi00YTY1LTk2NTEtODIyZjg5YmRlZThm0iWAl1VJQBnLcBFYdzkwuyh9TGyf9QDx86DZUn6ho3Pbtr5VPxMihwXpO1AAfxas5XSNNdhFAf3bqATAh2BkuQ",
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
            "sub": "9842f9ae-eb3c-4eba-8e4c-979ecae15fa1"
        },
        "token_type": "Bearer"
    }
    conv.events.store(EV_PROTOCOL_RESPONSE, AccessTokenResponse(**atr))

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

    atr = {
        "access_token":
            "ZDZjNWFmNzgtN2IxMi00YTY1LTk2NTEtODIyZjg5YmRlZThm0iWAl1VJQBnLcBFYdzkwuyh9TGyf9QDx86DZUn6ho3Pbtr5VPxMihwXpO1AAfxas5XSNNdhFAf3bqATAh2BkuQ",
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
    conv.events.store(EV_PROTOCOL_RESPONSE, AccessTokenResponse(**atr))

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

    atr = {
        "access_token":
            "ZDZjNWFmNzgtN2IxMi00YTY1LTk2NTEtODIyZjg5YmRlZThm0iWAl1VJQBnLcBFYdzkwuyh9TGyf9QDx86DZUn6ho3Pbtr5VPxMihwXpO1AAfxas5XSNNdhFAf3bqATAh2BkuQ",
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
            "sub": "9842f9ae-eb3c-4eba-8e4c-979ecae15fa1"
        },
        "token_type": "Bearer"
    }
    conv.events.store(EV_PROTOCOL_RESPONSE, AccessTokenResponse(**atr))

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

    atr = {
        "access_token":
            "ZDZjNWFmNzgtN2IxMi00YTY1LTk2NTEtODIyZjg5YmRlZThm0iWAl1VJQBnLcBFYdzkwuyh9TGyf9QDx86DZUn6ho3Pbtr5VPxMihwXpO1AAfxas5XSNNdhFAf3bqATAh2BkuQ",
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
            "phone_number": "+49 000 000000",
            "phone_number_verified": False,
            "sid": "be99eccf-965f-4ba4-b0e4-39b0c26868e1",
            "sub": "9842f9ae-eb3c-4eba-8e4c-979ecae15fa1"
        },
        "token_type": "Bearer"
    }
    conv.events.store(EV_PROTOCOL_RESPONSE, AccessTokenResponse(**atr))

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

