# -*- coding: utf-8 -*-
from oic.oic import ProviderConfigurationResponse
from oic.oic.provider import AuthorizationEndpoint
from oic.oic.provider import TokenEndpoint
from oic.oic.provider import RegistrationEndpoint
from oic.oic.provider import UserinfoEndpoint

from otest.parse_cnf import parse_yaml_conf
from otest.prof_util import SimpleProfileHandler
from otest.rp import operation
from otest.rp import check

from otest.rp.endpoints import authorization
from otest.rp.endpoints import css
from otest.rp.endpoints import op_info
from otest.rp.endpoints import registration
from otest.rp.endpoints import token
from otest.rp.endpoints import webfinger
from otest.rp.endpoints import userinfo
from otest.rp.setup import main_setup

from oidctest.rp import func
from oidctest.rp.provider import Provider

# baseurl = "https://130.239.200.165"
baseurl = "http://localhost"
issuer = "%s:%%d" % baseurl

keys = [
    {"type": "RSA", "key": "keys/pyoidc_enc", "use": ["enc"]},
    {"type": "RSA", "key": "keys/pyoidc_sig", "use": ["sig"]},
    {"type": "EC", "crv": "P-256", "use": ["sig"]},
    {"type": "EC", "crv": "P-256", "use": ["enc"]}
]

multi_keys = [
    {"type": "RSA", "use": ["enc"], "key": "keys/2nd_enc"},
    {"type": "RSA", "use": ["sig"], "key": "keys/2nd_sig"},
    {"type": "RSA", "use": ["enc"], "key": "keys/3rd_enc"},
    {"type": "RSA", "use": ["sig"], "key": "keys/3rd_sig"},
    {"type": "EC", "crv": "P-256", "use": ["sig"]},
    {"type": "EC", "crv": "P-256", "use": ["enc"]},
    {"type": "EC", "crv": "P-256", "use": ["sig"]},
    {"type": "EC", "crv": "P-256", "use": ["enc"]}
]

SERVICE_URL = "%s/verify" % issuer

AUTHENTICATION = {
    # Dummy authentication
    "NoAuthn": {"ACR": "PASSWORD", "WEIGHT": 1, "user": "diana"}
}

COOKIENAME = 'pyoic'
COOKIETTL = 4 * 60  # 4 hours
SYM_KEY = "SoLittleTime,Got"

SERVER_CERT = "certs/cert.pem"
SERVER_KEY = "certs/key.pem"
CERT_CHAIN = None
CA_BUNDLE = None

# =======  SIMPLE DATABASE ==============

USERINFO = "SIMPLE"

USERDB = {
    "diana": {
        "sub": "dikr0001",
        "name": "Diana Krall",
        "given_name": "Diana",
        "family_name": "Krall",
        "nickname": "Dina",
        "email": "diana@example.org",
        "email_verified": False,
        "phone_number": "+46 90 7865000",
        "address": {
            "street_address": "Umeå Universitet",
            "locality": "Umeå",
            "postal_code": "SE-90187",
            "country": "Sweden"
        },
    },
    "babs": {
        "sub": "babs0001",
        "name": "Barbara J Jensen",
        "given_name": "Barbara",
        "family_name": "Jensen",
        "nickname": "babs",
        "email": "babs@example.com",
        "email_verified": True,
        "address": {
            "street_address": "100 Universal City Plaza",
            "locality": "Hollywood",
            "region": "CA",
            "postal_code": "91608",
            "country": "USA",
        },
    },
    "upper": {
        "sub": "uppe0001",
        "name": "Upper Crust",
        "given_name": "Upper",
        "family_name": "Crust",
        "email": "uc@example.com",
        "email_verified": True,
    }
}

TARGET = 'https://localhost:8666/rp?issuer={}'

BEHAVIOR = {
    'client_registration': {
        'assign': {'token_endpoint_auth_method': 'private_key_jwt'}
    }
}

TOOL_ARGS = {
    'setup': main_setup,
    'check': check,
    'provider': Provider,
    'profile_handler': SimpleProfileHandler,
    'parse_conf': parse_yaml_conf,
    'cls_factories': {'': operation.factory},
    'chk_factory': check.factory,
    'func_factory': func.factory,
    'configuration_response': ProviderConfigurationResponse,
    'endpoints': [
        AuthorizationEndpoint(authorization),
        TokenEndpoint(token),
        RegistrationEndpoint(registration),
        UserinfoEndpoint(userinfo)
    ],
    'urls': [
        (r'^.well-known/openid-configuration', op_info),
        (r'^.well-known/webfinger', webfinger),
        (r'.+\.css$', css),
    ],
}
