import os

BASEDIR = os.path.abspath(os.path.dirname(__file__))

SERVER_CERT = "./certs/cert.pem"
SERVER_KEY = "./certs/key.pem"
CERT_CHAIN = None

VERIFY_SSL = False

BASE_URL = 'http://localhost'
TEMPLATE_DIR = '../heart_mako'
ENT_PATH = '../entities'
ENT_INFO = '../entity_info'

FLOWS = ['../flows.yaml']

PATH2PORT = '../path2port.csv'
PORT_MIN = 9100
PORT_MAX = 9149

TEST_TOOL_BASE = 'http://localhost'