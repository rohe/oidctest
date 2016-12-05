import os

BASEDIR = os.path.abspath(os.path.dirname(__file__))

SERVER_CERT = "./certs/cert.pem"
SERVER_KEY = "./certs/key.pem"
CERT_CHAIN = None

#VERIFY_SSL = False

PORT_MIN = 9100
PORT_MAX = 9149

# The variables immediate below are all passed on to the test tool instance
BASE_URL = 'http://localhost'
MAKO_DIR = './heart_mako'
ENT_PATH = './entities'
ENT_INFO = './entity_info'

FLOWS = ['./flows.yaml']

PATH2PORT = './path2port.csv'
