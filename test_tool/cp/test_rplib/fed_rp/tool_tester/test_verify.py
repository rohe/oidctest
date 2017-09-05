import json
import os

import shutil
from time import time
from urllib.parse import urlencode

import requests
from fedoidc import test_utils
from fedoidc.entity import FederationEntity
from fedoidc.provider import Provider
from oic import rndstr
from oic.utils.authn.authn_context import AuthnBroker
from oic.utils.authn.client import verify_client
from oic.utils.authn.user import UserAuthnMethod
from oic.utils.authz import AuthzHandling
from oic.utils.keyio import build_keyjar
from fedoidc.file_system import FileSystem
from oic.utils.sdb import create_session_db

TOOL_ISS = 'https://localhost'

FO = {'oidf': 'https://www.oidf.net'}
OA = {'catalogix': 'https://catalogix.se'}
IA = {}
EO = {}

SMS_DEF = {
    OA['catalogix']: {
        "discovery": {
            FO['oidf']: [
                {'request': {}, 'requester': OA['catalogix'],
                 'signer_add': {'federation_usage': 'discovery'},
                 'signer': FO['oidf'], 'uri': False},
            ]
        },
        "response": {
            FO['oidf']: [
                {'request': {}, 'requester': OA['catalogix'],
                 'signer_add': {'federation_usage': 'discovery'},
                 'signer': FO['oidf'], 'uri': False},
            ]
        }
    }
}

KEY_DEFS = [
    {"type": "RSA", "key": '', "use": ["sig"]},
    {"type": "EC", "crv": "P-256", "use": ["sig"]}
]

MS_DIR = 'ms_dir_10'
fs = FileSystem(MS_DIR)
fs.reset()

if os.path.isdir('mds'):
    shutil.rmtree('mds')

liss = list(FO.values())
liss.extend(list(OA.values()))

signer, keybundle = test_utils.setup(
    KEY_DEFS, TOOL_ISS, liss, ms_path=MS_DIR, csms_def=SMS_DEF,
    mds_dir='mds', base_url='https://localhost')

sunet_op = 'https://www.sunet.se/op'

_kj = build_keyjar(KEY_DEFS)[1]
fed_ent = FederationEntity(None, keyjar=_kj, iss=sunet_op,
                           signer=signer[OA['catalogix']])

# ------------------------------------------------------------
class DummyAuthn(UserAuthnMethod):
    def __init__(self, srv, user):
        UserAuthnMethod.__init__(self, srv)
        self.user = user

    def authenticated_as(self, cookie=None, **kwargs):
        if cookie == "FAIL":
            return None, 0
        else:
            return {"uid": self.user}, time()

AUTHN_BROKER = AuthnBroker()
AUTHN_BROKER.add("UNDEFINED", DummyAuthn(None, "username"))

# dealing with authorization
AUTHZ = AuthzHandling()
SYMKEY = rndstr(16)  # symmetric key used to encrypt cookie info

USERINFO = {}
# ------------------------------------------------------------

_sdb = create_session_db(sunet_op, 'automover', '430X', {})
op = Provider(sunet_op, _sdb, {},
                   AUTHN_BROKER, USERINFO,
                   AUTHZ, client_authn=verify_client, symkey=SYMKEY,
                   federation_entity=fed_ent)

fedpi = op.create_fed_providerinfo()

data = urlencode({
    'iss': FO['oidf'],
    'ms': fedpi['metadata_statements'][FO['oidf']],
    'jwks': json.dumps(keybundle[FO['oidf']].export_jwks(issuer=FO['oidf']))
})
r = requests.get('https://localhost:8080/verify?{}'.format(data), verify=False)
print(r.status_code)
print(r.text)