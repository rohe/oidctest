from oidctest.prof_util import ProfileHandler

TESTS = {
    'C.T.T.T': {'extra': False, 'enc': False, 'webfinger': True,
                'return_type': 'C', 'sig': False, 'none': False,
                'register': True, 'discover': True},
    'C.T.T.T..+': {'extra': True, 'enc': False, 'webfinger': True,
                   'return_type': 'C', 'sig': False, 'none': False,
                   'register': True, 'discover': True},
    'C.T.T.T.e.+': {'extra': True, 'enc': True, 'webfinger': True,
                    'return_type': 'C', 'sig': False, 'none': False,
                    'register': True, 'discover': True},
    'C.T.T.T.ens': {'extra': False, 'enc': True, 'webfinger': True,
                    'return_type': 'C', 'sig': True, 'none': True,
                    'register': True, 'discover': True},
    'C.T.T.T.es': {'extra': False, 'enc': True, 'webfinger': True,
                   'return_type': 'C', 'sig': True, 'none': False,
                   'register': True, 'discover': True},
    'C.T.T.T.s': {'extra': False, 'enc': False, 'webfinger': True,
                  'return_type': 'C', 'sig': True, 'none': False,
                  'register': True, 'discover': True},
    'CIT.F.F.F.s': {'extra': False, 'enc': False, 'webfinger': False,
                    'return_type': 'CIT', 'sig': True, 'none': False,
                    'register': False, 'discover': False},
    'I.F.T.F': {'extra': False, 'enc': False, 'webfinger': False,
                'return_type': 'I', 'sig': False, 'none': False,
                'register': False, 'discover': True},
    'I.T.T.T': {'extra': False, 'enc': False, 'webfinger': True,
                'return_type': 'I', 'sig': False, 'none': False,
                'register': True, 'discover': True}
}

TKEYS = list(TESTS.keys())
TKEYS.sort()


def test_return_type_handler():
    ph = ProfileHandler({'profile': TKEYS[0]})
    s = ph.to_profile()
    assert s == ['code', 'webfinger', 'discovery', 'dynamic']

    ph = ProfileHandler({'profile': TKEYS[2]})
    s = ph.to_profile()
    assert s == ['code', 'webfinger', 'discovery', 'dynamic', 'encrypt',
                 'extras']

    ph = ProfileHandler({'profile': TKEYS[3]})
    s = ph.to_profile()
    assert s == ['code', 'webfinger', 'discovery', 'dynamic',
                 'encrypt+none+sign']

    ph = ProfileHandler({'profile': TKEYS[6]})
    s = ph.to_profile()
    assert s == ['code+id_token+token', 'no-webfinger', 'no-discovery',
                 'static', 'sign']
