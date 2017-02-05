import os

BASEDIR = os.path.abspath(os.path.dirname(__file__))

SERVER_CERT = "certs/cert.pem"
SERVER_KEY = "certs/key.pem"
CERT_CHAIN = None

#VERIFY_SSL = False

PORT_MIN = 9100
PORT_MAX = 9149

BASE_URL = 'http://localhost'

# The variables below are all passed on to the test tool instance
MAKO_DIR = 'oidf_mako'
ENT_PATH = 'entities'
ENT_INFO = 'entity_info'

FLOWDIR = 'flows'

PATH2PORT = 'path2port.csv'
