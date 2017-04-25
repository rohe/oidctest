from oic.oic import AccessTokenResponse
from oic.oic import OpenIDSchema
from oidctest.op.check import VerifyClaims

from oidctest.test_setup import setup_conv
from otest.events import EV_PROTOCOL_RESPONSE, EV_REDIRECT_URL


def test_verify_claims():
    _info = setup_conv()
    conv = _info['conv']
    kwargs = {
        "id_token": {"email": None},
        "userinfo": {"phone": None}
    }

    # Add events
    _url = "https://guarded-cliffs-8635.herokuapp.com/auth?redirect_uri=https%3A%2F%2Fnew-op.certification.openid.net%3A60011%2Fauthz_cb&state=OzFXyxsdI0kuIwo6&claims=%7B%22id_token%22%3A+%7B%22email%22%3A+%7B%22essential%22%3A+true%7D%7D%7D&response_type=code&nonce=WZ3PuYEnGxcM6ddf&scope=openid+phone&client_id=cb19ff50-6423-4955-92a2-73bea88796b4"
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