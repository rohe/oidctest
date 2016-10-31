import os

BASEDIR = os.path.abspath(os.path.dirname(__file__))

# If BASE is https these has to be specified
SERVER_CERT = "./certs/server.crt"
SERVER_KEY = "./certs/server.key"
CERT_CHAIN = "./certs/bundle.pem"
CA_BUNDLE = "./certs/bundle.pem"
VERIFY_SSL = False
