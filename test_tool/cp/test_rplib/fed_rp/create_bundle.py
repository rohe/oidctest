#!/usr/bin/env python3

import importlib
import sys
import logging

from fedoidc.test_utils import make_fs_jwks_bundle

logger = logging.getLogger('')
LOGFILE_NAME = 'create_sms.log'
hdlr = logging.FileHandler(LOGFILE_NAME)
base_formatter = logging.Formatter(
    "%(asctime)s %(name)s:%(levelname)s %(message)s")

hdlr.setFormatter(base_formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.DEBUG)

KEYDEFS = [
    {"type": "RSA", "key": '', "use": ["sig"]},
    {"type": "EC", "crv": "P-256", "use": ["sig"]}
]

if __name__ == '__main__':
    sys.path.insert(0, ".")
    config = importlib.import_module(sys.argv[1])

    _liss = []
    _liss.extend(list(config.FO.values()))
    _liss.extend(list(config.OA.values()))
    _liss.extend(list(config.IA.values()))
    _liss.extend(list(config.EO.values()))

    _jb = make_fs_jwks_bundle(config.TOOL_ISS, _liss, None, KEYDEFS, './')
