__author__ = 'roland'

PORT = 9100
BASE = "https://localhost"

# If BASE is https these has to be specified
SERVER_CERT = "./certs/server.crt"
SERVER_KEY = "./certs/server.key"
CA_BUNDLE = None
VERIFY_SSL = False
CERT_CHAIN = None

ISSUER = "https://localhost:8092/"
# ISSUER = "https://oictest.umdc.umu.se:8051/"

JWKS_NAME = 'jwk.json'

keys = [
    {
        "type": "RSA",
        "key": "../keys/rp_enc_key",
        "use": ["enc"],
    },
    {
        "type": "RSA",
        "key": "../keys/rp_sign_key",
        "use": ["sig"],
    },
    {"type": "EC", "crv": "P-256", "use": ["sig"]},
    {"type": "EC", "crv": "P-256", "use": ["enc"]}
]

REDIRECT_URIS_PATTERN = ["{}authz_cb"]

INFO = {
    "client": {
        #"redirect_uris": ["{}authz_cb"],
        "application_type": "web",
        "contact": ["foo@example.com"],
        "webfinger_url": "{}diana".format(ISSUER),
        "webfinger_email": "diana@localhost:8092"
    }
    # registered
    # srv_discovery_url
    # provider_info
}
