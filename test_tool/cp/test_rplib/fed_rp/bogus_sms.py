#!/usr/bin/env python3

import importlib
import os
import sys
from urllib.parse import quote_plus
from urllib.parse import unquote_plus

from fedoidc import MetadataStatement
from fedoidc.bundle import FSJWKSBundle, JWKSBundle
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

_dir = os.path.join('ms_dir', quote_plus(name), 'discovery')
metadata_statements = FileSystem(_dir, key_conv={'to': quote_plus,
                                                 'from': unquote_plus})

fo = "https://edugain.com"

# What I want to create is something like

# (ms_OA + SK[X])
_kj = build_keyjar(config.KEY_DEFS)[1]
req = MetadataStatement(
    federation_usage='discovery',
    signing_keys={'keys': [x.serialize() for x in _kj.get_signing_key()]})

# FO(ms_OA + SK[X])
_fo_signer = operator[fo]
ms_0 = _fo_signer.pack_metadata_statement(req)

# OA(ms_IA + SK[IA] + FO(ms_OA + SK[X]))
_ia_signer = operator["https://bogus.example.org"]
req = MetadataStatement(
    tos_uri='https://example.org/tos',
    metadata_statements={fo: ms_0},
    signing_keys=_ia_signer.signing_keys_as_jwks()
)

oa = "https://example.org"
_oa_signer = operator[oa]
ms_1 = _oa_signer.pack_metadata_statement(req)

metadata_statements[fo] = ms_1


_jb = JWKSBundle('https://op.sunet.se')
_jb[_fo_signer.iss] = _fo_signer.signing_keys_as_jwks()

uninett_op = Operator(iss='https://op.sunet.se', jwks_bundle=_jb)
foo = uninett_op.unpack_metadata_statement(jwt_ms=ms_1)
print(foo)