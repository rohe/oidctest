import importlib
import sys
from urllib.parse import quote_plus
from urllib.parse import unquote_plus

from fedoidc.bundle import FSJWKSBundle
from fedoidc.bundle import keyjar_to_jwks_private
from fedoidc.file_system import FileSystem
from fedoidc.operator import Operator
from fedoidc.test_utils import make_signed_metadata_statement

if __name__ == "__main__":
    sys.path.insert(0, ".")
    config = importlib.import_module(sys.argv[1])

    jb = FSJWKSBundle(config.TOOL_ISS, None, 'fo_jwks',
                      key_conv={'to': quote_plus, 'from': unquote_plus})

    # Need to save the private parts
    jb.bundle.value_conv['to'] = keyjar_to_jwks_private
    jb.bundle.sync()

    operator = {}

    for entity, _keyjar in jb.items():
        operator[entity] = Operator(iss=entity, keyjar=_keyjar)

    metadata_statements = FileSystem('ms_dir')
    for name, spec in config.SMS_DEF.items():
        res = make_signed_metadata_statement(spec, operator)
        metadata_statements[name] = res['ms']
        print(name, res['ms'])
