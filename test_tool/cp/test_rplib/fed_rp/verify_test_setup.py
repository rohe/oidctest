import importlib
import sys
from urllib.parse import quote_plus, unquote_plus

from fedoidc.bundle import FSJWKSBundle
from fedoidc.test_utils import MetaDataStore

from oidctest.fed.setup import create_signers

sys.path.insert(0, ".")
fed_conf = importlib.import_module(sys.argv[1])

keybundle = FSJWKSBundle(fed_conf.TOOL_ISS, None, 'fo_jwks',
                         key_conv={'to': quote_plus, 'from': unquote_plus})

print(40*'-')
print('Got keys for the following entities:')
for iss, kj in keybundle.items():
    print(10*'-',iss, 10*'-')
    for key in kj.get_issuer_keys(''):
        print("\ttype:{kty}, use:{use}, kid:{kid}".format(**key.serialize()))

print('')
signers = create_signers(keybundle, 'ms_path', fed_conf.SMS_DEF,
                         fed_conf.FO.values())

print(20*'=','stored metadata statements', 20*'=')
for iss, sign in signers.items():
    print(10*'-',iss, 10*'-')
    for typ, fs in sign.metadata_statements.items():
        if isinstance(fs,dict):
            continue
        fs.sync()
        l = list(fs.keys())
        print('\t', typ, l)

print('')
smsfs = MetaDataStore('ms_dir')
smsfs.sync()

print(20*'=','stored SIGNED metadata statements', 20*'=')
print('Keys:', list(smsfs.keys()))
