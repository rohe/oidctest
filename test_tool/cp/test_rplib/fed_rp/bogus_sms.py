#!/usr/bin/env python3

import importlib
import os
from urllib.parse import quote_plus
from urllib.parse import unquote_plus

import sys

from fedoidc import MetadataStatement
from fedoidc.bundle import FSJWKSBundle
from fedoidc.file_system import FileSystem
from fedoidc.operator import Operator

from oic.utils.keyio import build_keyjar

sys.path.insert(0, ".")
config = importlib.import_module(sys.argv[1])

jb = FSJWKSBundle(config.TOOL_ISS, None, 'fo_jwks',
                  key_conv={'to': quote_plus, 'from': unquote_plus})
jb.bundle.sync()

operator = {}

for entity, _keyjar in jb.items():
    operator[entity] = Operator(iss=entity, keyjar=_keyjar)

name = 'https://bogus.example.org'

_dir = os.path.join('ms_dir', quote_plus(name))
metadata_statements = FileSystem(_dir, key_conv={'to': quote_plus,
                                                 'from': unquote_plus})

fo = "https://example.com"

# desc = FO['swamid']: [
#             {'request': {}, 'requester': OA['sunet'],
#              'signer_add': {}, 'signer': FO['swamid']},
#         ]

req = MetadataStatement()
_requester = operator[name]
_kj = build_keyjar(config.KEY_DEFS)[1]
req['signing_keys'] = {'keys': [x.serialize() for x in _kj.get_signing_key()]}
_signer = operator[fo]
ms = _signer.pack_metadata_statement(req)

metadata_statements[fo] = ms
