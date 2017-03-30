from future.backports.urllib.parse import quote_plus

import argparse

from oidctest.app_conf import REST
from oidctest.app_conf import create_model

parser = argparse.ArgumentParser()
parser.add_argument('-a', dest='acr_values', action='append')
parser.add_argument('-e', dest='enc', action='store_true')
parser.add_argument('-r', dest='entity_root', default='.')
parser.add_argument('--hint', dest='login_hint')
parser.add_argument('-i', dest='issuer')
parser.add_argument('-l', dest='ui_locales')
parser.add_argument('-L', dest='claims_locales')
parser.add_argument('-p', dest='profile', default='C.T.T.T')
parser.add_argument('-s', dest='sig', action='store_true')
parser.add_argument('-t', dest='tag')
parser.add_argument('-x', dest='extra', action='store_true')
parser.add_argument('-w', dest='webfinger_email')
parser.add_argument('-W', dest='webfinger_url')

args = parser.parse_args()

ent_info_path='{}/entity_info'.format(args.entity_root)

rest = REST('', '{}/entities'.format(args.entity_root), ent_info_path)
cnf = create_model(args.profile, ent_info_path)

for item in ['sig', 'enc', 'extra']:
    if getattr(args, item):
        cnf['tool'][item] = True

for item in ['acr_values', 'login_hint', 'ui_locales', 'claims_locales',
             'webfinger_url', 'webfinger_email', 'issuer', 'profile', 'tag']:
    v = getattr(args, item)
    if v:
        cnf['tool'][item] = v

qiss = quote_plus(cnf['tool']['issuer'])
qtag = cnf['tool']['tag']
rest.write(qiss, qtag, cnf)
