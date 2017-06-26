# -*- coding: utf-8 -*-

baseurl = "https://localhost:8080"

keys = [
    {"type": "RSA", "key": "keys/pyoidc_enc", "use": ["enc"]},
    {"type": "RSA", "key": "keys/pyoidc_sig", "use": ["sig"]},
    {"type": "EC", "crv": "P-256", "use": ["sig"]},
    {"type": "EC", "crv": "P-256", "use": ["enc"]}
]

GRPS = ["Single SMS", "Multiple SMS"]

#
AUTHENTICATION = {
    "NoAuthn": {"ACR": "PASSWORD", "WEIGHT": 1, "user": "diana"}
}

COOKIENAME = 'pyoic'
COOKIETTL = 4 * 60  # 4 hours
SYM_KEY = "SoLittleTime,Got"

SERVER_CERT = "certs/cert.pem"
SERVER_KEY = "certs/key.pem"
#CA_BUNDLE="certs/chain.pem"
CA_BUNDLE = None

CLIENT_DB = "client_db"

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
    }
}
