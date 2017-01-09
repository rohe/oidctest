__author__ = 'roland'

PORT = 8088
# BASE = "https://130.239.144.143:" + str(PORT) + "/"
BASE = "https://localhost:" + str(PORT) + "/"

# If BASE is https these has to be specified
SERVER_CERT = "../certs/cert.pem"
SERVER_KEY = "../certs/key.pem"
CA_BUNDLE = None
VERIFY_SSL = False

KEY_EXPORT_URL = "%sstatic/jwk.json" % BASE

KEYS = [
    {"type": "RSA", "key": "../keys/pyoidc_enc", "use": ["enc"]},
    {"type": "RSA", "key": "../keys/pyoidc_sig", "use": ["sig"]},
    {"type": "EC", "crv": "P-256", "use": ["sig"]},
    {"type": "EC", "crv": "P-256", "use": ["enc"]}
]

TOOL = {
    'issuer': "https://localhost:8080/",
    'webfinger_url': 'https://localhost:8080/'
}

CLIENT = {
    "registration_info": {
        "redirect_uris": ["%sauthz_cb" % BASE],
        "application_type": "web",
        "contact": ["foo@example.com"]
    },
    'requests_dir': 'requests'
    # registered
    # 'srv_discovery_url': ISSUER
    # provider_info
}
