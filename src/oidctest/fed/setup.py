import importlib
import os
import sys
from urllib.parse import unquote_plus
from urllib.parse import quote_plus

from fedoidc.bundle import FSJWKSBundle
from fedoidc.bundle import keyjar_to_jwks_private
from fedoidc.file_system import FileSystem
from fedoidc.operator import Operator
from fedoidc.signing_service import Signer
from fedoidc.signing_service import SigningService
from fedoidc.test_utils import make_fs_jwks_bundle
from fedoidc.test_utils import make_signed_metadata_statement
from oic.utils.keyio import build_keyjar


def create_signers(jb, ms_path, csms_def, fos):
    signers = {}
    for sig, use_def in csms_def.items():
        ms_spec = {}
        for usage, spec in use_def.items():
            ms_spec[usage] = os.path.join(ms_path, quote_plus(sig), usage)
        signers[sig] = Signer(SigningService(sig, jb[sig]), ms_spec)

    for fo in fos:
        signers[fo] = Signer(SigningService(fo, jb[fo]),
                             {"discovery":ms_path, "response":ms_path})

    return signers


def setup(keydefs, tool_iss, liss, csms_def, oa, ms_path):
    sig_keys = build_keyjar(keydefs)[1]
    key_bundle = make_fs_jwks_bundle(tool_iss, liss, sig_keys, keydefs, './')

    sig_keys = build_keyjar(keydefs)[1]
    jb = FSJWKSBundle(tool_iss, sig_keys, 'fo_jwks',
                      key_conv={'to': quote_plus, 'from': unquote_plus})

    # Need to save the private parts
    jb.bundle.value_conv['to'] = keyjar_to_jwks_private
    jb.bundle.sync()

    operator = {}

    for entity, _keyjar in jb.items():
        operator[entity] = Operator(iss=entity, keyjar=_keyjar)

    signers = {}
    for sig, sms_def in csms_def.items():
        ms_dir = os.path.join(ms_path, sig)
        metadata_statements = FileSystem(ms_dir)
        for name, spec in sms_def.items():
            res = make_signed_metadata_statement(spec, operator)
            metadata_statements[name] = res['ms']
        _iss = oa[sig]
        signers[_iss] = Signer(
            SigningService(_iss, operator[_iss].keyjar), ms_dir)

    return signers, key_bundle


def fed_setup(args):
    sys.path.insert(0, ".")
    config = importlib.import_module(args.fed_config)

    _liss = []
    _liss.extend(list(config.FO.values()))
    _liss.extend(list(config.OA.values()))
    _liss.extend(list(config.IA.values()))
    _liss.extend(list(config.EO.values()))

    return setup(config.KEY_DEFS, config.TOOL_ISS, _liss, config.SMS_DEF,
                 config.OA, args.ms_path)