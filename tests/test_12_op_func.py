import json

from oic import rndstr
from oic.utils.keyio import build_keyjar
from otest.check import ERROR
from otest.test_setup import setup_conv

from oidctest.op.func import check_support
from oidctest.op.func import claims_locales
from oidctest.op.func import login_hint
from oidctest.op.func import store_sector_redirect_uris
from oidctest.op.func import sub_claims
from oidctest.op.func import ui_locales
from oidctest.op.func import set_response_where
from oidctest.op.func import set_state
from oidctest.op.func import static_jwk
from oidctest.op.func import set_discovery_issuer
from oidctest.op.func import set_essential_arg_claim
from oidctest.op.func import set_principal
from oidctest.op.func import multiple_return_uris
from oidctest.op.func import redirect_uri_with_query_component
from oidctest.op.func import redirect_uris_with_fragment
from oidctest.op.func import request_in_file
from oidctest.op.func import check_config
from oidctest.op.func import conditional_execution
from oidctest.op.func import essential_and_specific_acr_claim
from oidctest.op.func import id_token_hint
from oidctest.op.func import set_webfinger_resource
from oidctest.op.oper import AsyncAuthn
from oidctest.op.oper import Webfinger

from otest.events import EV_CONDITION
from otest.events import EV_PROTOCOL_RESPONSE
from otest.events import EV_RESPONSE

from oic.oic.message import AccessTokenResponse

KEYDEFS = [
    {"type": "RSA", "key": '', "use": ["sig"]},
    {"type": "EC", "crv": "P-256", "use": ["sig"]}
]


def test_set_webfinger_resource():
    _info = setup_conv()

    # set tool_config
    _info['conv'].tool_config['webfinger_url'] = 'https://example.com/diana'

    oper = Webfinger(_info['conv'], _info['io'], None, profile='C.T.T.T')
    # inut.profile_handler.webfinger(self.profile)
    set_webfinger_resource(oper, None)

    assert oper.resource == 'https://example.com/diana'


def test_check_support():
    _info = setup_conv()
    _info['conv'].entity.provider_info[
        'token_endpoint_auth_methods_supported'] = ["private_key_jwt"]
    oper = AsyncAuthn(_info['conv'], _info['io'], None)

    check_support(oper, {"WARNING": {
        "token_endpoint_auth_methods_supported": "private_key_jwt"}})

    assert oper.fail is False

    check_support(oper, {"WARNING": {
        "token_endpoint_auth_methods_supported": "client_secret_jwt"}})

    assert oper.fail is False
    assert len(oper.conv.events) == 1

    check_support(oper, {"ERROR": {
        "token_endpoint_auth_methods_supported": "client_secret_jwt"}})

    assert oper.fail is True


def test_check_support_strings():
    _info = setup_conv()
    _info['conv'].entity.provider_info[
        'token_endpoint_auth_methods_supported'] = ["private_key_jwt"]
    _info['conv'].entity.provider_info.__class__.c_param['token_endpoint_auth_methods_supported'] = (str, None)

    oper = AsyncAuthn(_info['conv'], _info['io'], None)

    check_support(oper, {"WARNING": {
        "token_endpoint_auth_methods_supported": "private_key_jwt"}})
    assert oper.fail is False
    assert len(oper.conv.events) == 1


def test_check_config():
    _info = setup_conv()
    # set tool_config
    _info['conv'].tool_config['login_hint'] = 'diana'
    oper = AsyncAuthn(_info['conv'], _info['io'], None)
    check_config(oper, {"login_hint": None})
    ev = oper.conv.events.get(EV_CONDITION)
    assert ev == []


def test_check_config_missing():
    _info = setup_conv()
    oper = AsyncAuthn(_info['conv'], _info['io'], None)
    check_config(oper, {"login_hint": None})

    ev = oper.conv.events.get(EV_CONDITION)
    assert len(ev) == 1
    assert ev[0].data.status == ERROR
    assert oper.unsupported


def test_conditional_execution_true():
    _info = setup_conv()
    oper = AsyncAuthn(_info['conv'], _info['io'], None)
    oper.profile = ['C', 'T', 'T', 'T']
    conditional_execution(oper, {"return_type": ["CIT", "CI", "C", "CT"]})
    assert oper.skip is False


def test_conditional_execution_false():
    _info = setup_conv()
    oper = AsyncAuthn(_info['conv'], _info['io'], None)
    oper.profile = ['I', 'T', 'T', 'T']
    conditional_execution(oper, {"return_type": ["CIT", "CI", "C", "CT"]})
    assert oper.skip is True


def test_essential_and_specific_acr_claim_pi():
    _info = setup_conv()
    oper = AsyncAuthn(_info['conv'], _info['io'], None)
    _acrs = ['pinfo']
    oper.conv.entity.provider_info = {'acr_values_supported': _acrs}
    essential_and_specific_acr_claim(oper, ['one'])

    assert 'acr_values' not in oper.req_args
    assert oper.req_args['claims']['id_token']['acr'] == {"value": _acrs[0],
                                                          'essential': True}


def test_essential_and_specific_acr_claim_tc():
    _info = setup_conv()
    oper = AsyncAuthn(_info['conv'], _info['io'], None)
    _acrs = ['passwd']
    _info['conv'].tool_config['acr_value'] = _acrs
    essential_and_specific_acr_claim(oper, ['one'])

    assert 'acr_values' not in oper.req_args
    assert oper.req_args['claims']['id_token']['acr'] == {"value": _acrs[0],
                                                          'essential': True}


def test_id_token_hint_json():
    _info = setup_conv()
    oper = AsyncAuthn(_info['conv'], _info['io'], None)

    # test specific setup
    atr = {
        "access_token":
            "ZDZjNWFmNzgtN2IxMi00YTY1LTk2NTEtODIyZjg5YmRlZThm0iWAl1VJQBnLcBFYdzkwuyh9TGyf9QDx86DZUn6ho3Pbtr5VPxMihwXpO1AAfxas5XSNNdhFAf3bqATAh2BkuQ",
        "expires_in": 7200,
        "id_token":
            "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InIxTGtiQm8zOTI1UmIyWkZGckt5VTNNVmV4OVQyODE3S3gwdmJpNmlfS2MifQ.eyJzdWIiOiJmYmVmOGUzYWQ4ZjVjOGY4MTcxYzYyNDM5ZDk5MjU0MDRiMDY1OWZkM2E4NGQ0MjRiNDcyMWE5ZjNlMWUxMmNmIiwibm9uY2UiOiIwUlBNTENUUGo1OWNvbGwyIiwiYXRfaGFzaCI6Ing2b2ZUYXlUQWZrRlB1QVB2emstNWciLCJzaWQiOiIxNmVlNzlkMi1kNDcxLTRlMzMtODk3OC04OTYwMjBjOGFiNjAiLCJpYXQiOjE0OTI3OTY3OTYsImV4cCI6MTQ5MjgwMzk5NiwiYXVkIjoiNjNjNzQzNTAtOWE0ZS00YWE4LTlhYjItNWM5YzcwOWJiYjY0IiwiaXNzIjoiaHR0cHM6Ly9ndWFyZGVkLWNsaWZmcy04NjM1Lmhlcm9rdWFwcC5jb20ifQ.ZhpdAoaUXWSHN3UtTXabdZcm5LsbgHt48uTPXXPs62R4d9wrKeEF_vAqrxlBZVJ49p_FlRbmm-ItCgVDh3MJE6l2L8wFswH-htEiATNVMUT8a4BzW5NyRz63Dj0REBvfDfLXi80A0_gcfbzBk4KXfRdGYV-_hwJNNztRvRm2KJPWvC6UNaFgnuu0OwvDzoEqboAa3zvWv9AgzoIjPB6yqYlwpcPQuABAzgjl2ERzYw1dtrkKOQEL4oGZ38Q9hZyzs9RjeGq1MYPuNSBzr3EyeI_v1rKaN9WRu_h4nH0YOpL5YUdkeYSB2G929gpXtx6jBYvMloozDv3FEiUELOQItA",
        "token_type": "Bearer"}

    _info['conv'].events.store(EV_RESPONSE, json.dumps(atr))
    args = None
    id_token_hint(oper, args)
    assert oper.req_args["id_token_hint"] == atr['id_token']


def test_id_token_hint_dict():
    _info = setup_conv()
    oper = AsyncAuthn(_info['conv'], _info['io'], None)

    # test specific setup
    atr = {
        "access_token":
            "ZDZjNWFmNzgtN2IxMi00YTY1LTk2NTEtODIyZjg5YmRlZThm0iWAl1VJQBnLcBFYdzkwuyh9TGyf9QDx86DZUn6ho3Pbtr5VPxMihwXpO1AAfxas5XSNNdhFAf3bqATAh2BkuQ",
        "expires_in": 7200,
        "id_token":
            "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InIxTGtiQm8zOTI1UmIyWkZGckt5VTNNVmV4OVQyODE3S3gwdmJpNmlfS2MifQ.eyJzdWIiOiJmYmVmOGUzYWQ4ZjVjOGY4MTcxYzYyNDM5ZDk5MjU0MDRiMDY1OWZkM2E4NGQ0MjRiNDcyMWE5ZjNlMWUxMmNmIiwibm9uY2UiOiIwUlBNTENUUGo1OWNvbGwyIiwiYXRfaGFzaCI6Ing2b2ZUYXlUQWZrRlB1QVB2emstNWciLCJzaWQiOiIxNmVlNzlkMi1kNDcxLTRlMzMtODk3OC04OTYwMjBjOGFiNjAiLCJpYXQiOjE0OTI3OTY3OTYsImV4cCI6MTQ5MjgwMzk5NiwiYXVkIjoiNjNjNzQzNTAtOWE0ZS00YWE4LTlhYjItNWM5YzcwOWJiYjY0IiwiaXNzIjoiaHR0cHM6Ly9ndWFyZGVkLWNsaWZmcy04NjM1Lmhlcm9rdWFwcC5jb20ifQ.ZhpdAoaUXWSHN3UtTXabdZcm5LsbgHt48uTPXXPs62R4d9wrKeEF_vAqrxlBZVJ49p_FlRbmm-ItCgVDh3MJE6l2L8wFswH-htEiATNVMUT8a4BzW5NyRz63Dj0REBvfDfLXi80A0_gcfbzBk4KXfRdGYV-_hwJNNztRvRm2KJPWvC6UNaFgnuu0OwvDzoEqboAa3zvWv9AgzoIjPB6yqYlwpcPQuABAzgjl2ERzYw1dtrkKOQEL4oGZ38Q9hZyzs9RjeGq1MYPuNSBzr3EyeI_v1rKaN9WRu_h4nH0YOpL5YUdkeYSB2G929gpXtx6jBYvMloozDv3FEiUELOQItA",
        "token_type": "Bearer"}

    _info['conv'].events.store(EV_RESPONSE, atr)
    args = None
    id_token_hint(oper, args)
    assert oper.req_args["id_token_hint"] == atr['id_token']


def test_multiple_return_uris():
    _info = setup_conv()
    oper = AsyncAuthn(_info['conv'], _info['io'], None)

    oper.conv.entity.redirect_uris = ['https://example.org/authzcb']
    oper.conv.entity.base_url = 'https://example.org'
    _ruris = len(oper.conv.entity.redirect_uris)
    args = None
    multiple_return_uris(oper, args)

    assert len(oper.req_args["redirect_uris"]) == _ruris + 1


def test_redirect_uri_with_query_component():
    _info = setup_conv()
    oper = AsyncAuthn(_info['conv'], _info['io'], None)

    oper.conv.entity.registration_response = {'redirect_uris': [
        'https://example.org/authzcb']}

    redirect_uri_with_query_component(oper, {'foo': 'bar'})

    assert oper.req_args["redirect_uri"][0].endswith('?foo=bar')


def test_redirect_uris_with_fragment():
    _info = setup_conv()
    oper = AsyncAuthn(_info['conv'], _info['io'], None)

    oper.conv.entity.registration_info = {'redirect_uris': [
        'https://example.org/authzcb']}

    redirect_uris_with_fragment(oper, {'fragment': 'one'})

    assert oper.req_args["redirect_uris"][0].endswith('#fragmentone')


def test_request_in_file():
    _info = setup_conv()
    oper = AsyncAuthn(_info['conv'], _info['io'], None)

    args = None
    request_in_file(oper, args)

    assert oper.op_args['base_path'].endswith('export/')


def test_set_discovery_issuer_dyn():
    _info = setup_conv()
    oper = AsyncAuthn(_info['conv'], _info['io'], None)
    oper.dynamic = True

    args = None
    set_discovery_issuer(oper, args)

    assert 'issuer' in oper.op_args


def test_set_discovery_issuer_static():
    _info = setup_conv()
    oper = AsyncAuthn(_info['conv'], _info['io'], None)

    oper.dynamic = False

    args = None
    set_discovery_issuer(oper, args)

    assert 'issuer' not in oper.op_args


def test_set_essential_arg_claim_rt_i():
    _info = setup_conv()
    oper = AsyncAuthn(_info['conv'], _info['io'], None)
    oper.tool_conf = {'profile': 'I.T.T.T'}
    args = 'email'
    set_essential_arg_claim(oper, args)

    assert oper.req_args["claims"] == {"id_token": {args: {"essential": True}}}


def test_set_essential_arg_claim_rt_non_i():
    _info = setup_conv()
    oper = AsyncAuthn(_info['conv'], _info['io'], None)
    oper.tool_conf = {'profile': 'C.T.T.T'}
    args = 'email'
    set_essential_arg_claim(oper, args)

    assert oper.req_args["claims"] == {"userinfo": {args: {"essential": True}}}


def test_set_principal():
    _info = setup_conv()
    oper = AsyncAuthn(_info['conv'], _info['io'], None)

    oper.conv.tool_config = {'foo': 'bar'}
    args = {'param': 'foo'}
    set_principal(oper, args)

    assert oper.req_args["principal"] == oper.conv.tool_config['foo']


def test_set_response_where_code():
    _info = setup_conv()
    oper = AsyncAuthn(_info['conv'], _info['io'], None)

    oper.req_args['response_type'] = ['code']
    args = None
    set_response_where(oper, args)

    assert oper.response_where != "fragment"


def test_set_response_where_implicit():
    _info = setup_conv()
    oper = AsyncAuthn(_info['conv'], _info['io'], None)

    oper.req_args['response_type'] = ['id_token']
    args = None
    set_response_where(oper, args)

    assert oper.response_where == "fragment"


def test_set_state():
    _info = setup_conv()
    oper = AsyncAuthn(_info['conv'], _info['io'], None)
    oper.conv.state = rndstr(16)
    args = None
    set_state(oper, args)

    assert oper.op_args['state'] == oper.conv.state


def test_static_jwk():
    _info = setup_conv()
    oper = AsyncAuthn(_info['conv'], _info['io'], None)

    oper.conv.entity.keyjar = build_keyjar(KEYDEFS)[1]
    oper.req_args["jwks_uri"] = 'https://example.org/jwks_uri'
    args = None
    static_jwk(oper, args)

    assert 'jwks_uri' not in oper.req_args
    assert 'jwks' in oper.req_args


def test_store_sector_redirect_uris():
    _info = setup_conv()
    oper = AsyncAuthn(_info['conv'], _info['io'], None)

    store_sector_redirect_uris(oper, {"other_uris": [
        "https://example.com/op"
    ]})

    assert oper.req_args["sector_identifier_uri"].endswith('export/siu.json')
    _siu = json.loads(open('export/siu.json').read())
    assert _siu


def test_sub_claims():
    _info = setup_conv()
    oper = AsyncAuthn(_info['conv'], _info['io'], None)

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
    _info['conv'].events.store(EV_PROTOCOL_RESPONSE,
                               AccessTokenResponse(**atr))
    _sub = atr["id_token"]["sub"]
    args = None
    sub_claims(oper, args)

    assert oper.req_args["claims"] == {"id_token": {"sub": {"value": _sub}}}


def test_ui_locales():
    _info = setup_conv()
    oper = AsyncAuthn(_info['conv'], _info['io'], None)
    oper.conv.tool_config = {'ui_locales': ['es']}
    args = None
    ui_locales(oper, args)

    assert oper.req_args["ui_locales"] == ['es']


def test_set_response_where_code_args():
    _info = setup_conv()
    oper = AsyncAuthn(_info['conv'], _info['io'], None)

    oper.req_args['response_type'] = ['id_token token']

    args = {'response_type': ['id_token token'], 'where': 'fragment'}
    set_response_where(oper, args)

    assert oper.response_where == "fragment"


def test_acr_value():
    _info = setup_conv()
    oper = AsyncAuthn(_info['conv'], _info['io'], None)
    _acrs = ['pinfo']
    oper.conv.entity.provider_info = {'acr_values_supported': _acrs}
    essential_and_specific_acr_claim(oper, ['one'])

    assert 'acr_values' not in oper.req_args
    assert oper.req_args['claims']['id_token']['acr'] == {"value": _acrs[0],
                                                          'essential': True}


def test_claims_locales():
    _info = setup_conv()
    oper = AsyncAuthn(_info['conv'], _info['io'], None)

    oper.conv.tool_config = {'claims_locales': ['ch']}
    args = None
    claims_locales(oper, args)

    assert oper.req_args["claims_locales"] == ['ch']


def test_login_hint_with_domain():
    _info = setup_conv()
    oper = AsyncAuthn(_info['conv'], _info['io'], None)

    oper.conv.entity.provider_info = {'issuer': 'https://example.com'}
    oper.conv.tool_config = {'login_hint': 'diana@example.org'}
    args = None
    login_hint(oper, args)

    assert oper.req_args["login_hint"] == 'diana@example.org'


def test_login_hint_with():
    _info = setup_conv()
    oper = AsyncAuthn(_info['conv'], _info['io'], None)

    oper.conv.entity.provider_info = {'issuer': 'https://example.com'}
    oper.conv.tool_config = {'login_hint': 'diana'}
    args = None
    login_hint(oper, args)

    assert oper.req_args["login_hint"] == 'diana'


def test_login_hint_without():
    _info = setup_conv()
    oper = AsyncAuthn(_info['conv'], _info['io'], None)

    oper.conv.entity.provider_info = {'issuer': 'https://example.com'}
    args = None
    login_hint(oper, args)

    assert oper.req_args["login_hint"] == 'buffy@example.com'

