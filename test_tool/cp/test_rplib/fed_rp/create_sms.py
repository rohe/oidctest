import importlib
import json
import os
import sys
from urllib.parse import quote_plus, unquote_plus

from oic.federation.bundle import FSJWKSBundle, keyjar_to_jwks_private
from oic.utils.keyio import build_keyjar

sys.path.insert(0, ".")
config = importlib.import_module('sms_conf')

BASE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "fo_keys"))

KEYDEFS = [
    {"type": "RSA", "key": '', "use": ["sig"]},
    {"type": "EC", "crv": "P-256", "use": ["sig"]}
]


def make_jwks_bundle(iss, fo_liss, sign_keyjar, keydefs, base_path=''):
    jb = FSJWKSBundle(iss, sign_keyjar, 'fo_jwks',
                      key_conv={'to': quote_plus, 'from': unquote_plus})

    # Need to save the private parts
    jb.bundle.value_conv['to'] = keyjar_to_jwks_private

    for entity, _name in fo_liss.items():
        fname = os.path.join(base_path, "{}.key".format(_name))
        _keydef = keydefs[:]
        _keydef[0]['key'] = fname

        _jwks, _keyjar, _kidd = build_keyjar(_keydef)
        jb[entity] = _keyjar

    return jb

_liss = {}
for o, val in config.ORG.items():
    for ent in ['OA','LO','EO']:
        if ent in val:
            if ent in ['OA']:
                item = val[ent]
                _item = item.replace('/','_')
                _liss[item] = _item
            else:
                for item in val[ent]:
                    _item = item.replace('/','_')
                    _liss[item] = _item

_jb = make_jwks_bundle(config.TOOL_ISS, _liss, None, KEYDEFS, './')

