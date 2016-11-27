import os

BASEDIR = os.path.abspath(os.path.dirname(__file__))

SERVER_CERT = "./certs/cert.pem"
SERVER_KEY = "./certs/key.pem"
CERT_CHAIN = None

VERIFY_SSL = False

BASE_URL = 'http://localhost'
TEMPLATE_DIR = './'
ENT_PATH = '../entities'
ENT_INFO = '../entity_info'
