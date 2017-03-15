#!/usr/bin/env python3

import importlib
import os
import sys
from urllib.parse import quote_plus
from urllib.parse import unquote_plus

from fedoidc.bundle import FSJWKSBundle
from fedoidc.file_system import FileSystem
from fedoidc.operator import Operator
from fedoidc.test_utils import make_signed_metadata_statement

if __name__ == "__main__":
    sys.path.insert(0, ".")
    config = importlib.import_module(sys.argv[1])

    jb = FSJWKSBundle(config.TOOL_ISS, None, 'fo_jwks',
                      key_conv={'to': quote_plus, 'from': unquote_plus})
    jb.bundle.sync()

    operator = {}

    for entity, _keyjar in jb.items():
        operator[entity] = Operator(iss=entity, keyjar=_keyjar)

    for name, spec in config.SMS_DEF.items():
        _dir = os.path.join('ms_dir', quote_plus(name))
        metadata_statements = FileSystem(_dir,
                                         key_conv={'to': quote_plus,
                                                   'from': unquote_plus})
        for fo, desc in spec.items():
            res = make_signed_metadata_statement(desc, operator)
            metadata_statements[fo] = res['ms']
            print(name, fo, res['ms'])
