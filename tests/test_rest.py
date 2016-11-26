#!/usr/bin/env python
from urllib.parse import quote_plus

from oidctest.app_conf import create_model
from oidctest.app_conf import REST


def test_1():
    rest = REST('http://localhost')
    cnf = create_model('C.T.T.T')

    cnf['tool']['issuer'] = 'http://example.com/op'
    cnf['tool']['sig'] = True

    qiss = quote_plus(cnf['tool']['issuer'])
    qtag = cnf['tool']['tag']
    rest.write(qiss, qtag, cnf)

    _ecnf = rest.construct_config(qiss, qtag)

    assert set(_ecnf.keys()) == {'client', 'keys', 'tool'}
    assert set(_ecnf['client'].keys()) == {'behaviour', 'client_prefs',
                                           'registration_info'}
