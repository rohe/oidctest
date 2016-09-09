from oidctest.rp.mode import extract_mode, mode2path


def test_extract_1():
    m = extract_mode('/foobar/RP-id_token-bad_c_hash')

    assert len(m) == 2
    assert m[0] == {'test_id': 'rp-id_token-bad_c_hash', 'oper_id': 'foobar'}
    assert m[1] == ''


def test_2path_1():
    m = extract_mode('/foobar/RP-id_token-bad_c_hash')
    path = mode2path(m[0])

    assert path == 'foobar/rp-id_token-bad_c_hash/_/_/_/normal'


def test_extract_2():
    m = extract_mode(
        'foobar/rp-id_token-bad_c_hash/_/_/ch/normal/.well-known/openid'
        '-configuration')

    assert len(m) == 2
    assert m[0] == {'claims': ['normal'], 'test_id': 'rp-id_token-bad_c_hash',
                    'oper_id': 'foobar', 'behavior': ['ch']}
    assert m[1] == '.well-known/openid-configuration'


def test_2path_2():
    m = extract_mode(
        'foobar/rp-id_token-bad_c_hash/_/_/ch/normal/.well-known/openid'
        '-configuration')

    path = mode2path(m[0])

    assert path == 'foobar/rp-id_token-bad_c_hash/_/_/ch/normal'


