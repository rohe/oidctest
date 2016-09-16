# Everything that is supposed to be the same for all instances

# If this server is supposed to handle https these has to be specified
SERVER_CERT = "./certs/server.crt"
SERVER_KEY = "./certs/server.key"
CA_BUNDLE = None
VERIFY_SSL = False
CERT_CHAIN = None

keys = [
    {
        "type": "RSA",
        "key": "keys/rp_enc_key",
        "use": ["enc"],
    },
    {
        "type": "RSA",
        "key": "keys/rp_sign_key",
        "use": ["sig"],
    },
    {"type": "EC", "crv": "P-256", "use": ["sig"]},
    {"type": "EC", "crv": "P-256", "use": ["enc"]}
]
