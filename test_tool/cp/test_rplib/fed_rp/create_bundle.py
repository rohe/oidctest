import importlib
import os
import sys
from urllib.parse import quote_plus
from urllib.parse import unquote_plus

import logging

import copy
from fedoidc.bundle import FSJWKSBundle
from fedoidc.bundle import keyjar_to_jwks_private
from fedoidc.operator import Operator
from oic.utils.keyio import build_keyjar

logger = logging.getLogger('')
LOGFILE_NAME = 'create_sms.log'
hdlr = logging.FileHandler(LOGFILE_NAME)
base_formatter = logging.Formatter(
    "%(asctime)s %(name)s:%(levelname)s %(message)s")

hdlr.setFormatter(base_formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.DEBUG)

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

    operator = {}

    for entity, _name in fo_liss.items():
        try:
            _keyjar = jb[entity]
        except KeyError:
            fname = os.path.join(base_path, 'keys', "{}.key".format(_name))
            _keydef = copy.deepcopy(keydefs)
            _keydef[0]['key'] = fname

            _jwks, _keyjar, _kidd = build_keyjar(_keydef)
            jb[entity] = _keyjar

        operator[entity] = Operator(iss=entity, keyjar=_keyjar)
    return jb, operator


if __name__ == '__main__':
    _liss = {}
    for fo in config.FO:
        _fo = fo.replace('/', '_')
        _liss[fo] = _fo

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

    _jb, operator = make_jwks_bundle(config.TOOL_ISS, _liss, None, KEYDEFS, './')
