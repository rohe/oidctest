from oidctest.cp.op import parse_resource


def test_parse_resource():
    a,b = parse_resource('acct:op_id.test_id@domain')
    assert a == 'op_id'
    assert b == 'test_id'

    a,b = parse_resource(
        'https://example.com/openid-client/rp-discovery-webfinger-url/joe')
    assert a == 'openid-client'
    assert b == 'rp-discovery-webfinger-url'

    a,b = parse_resource('acct:op_id.test_id@domain@localhost')
    assert a == 'op_id'
    assert b == 'test_id'

    a,b = parse_resource('acct:op_id.X.test_id@domain')
    assert a == 'op_id.X'
    assert b == 'test_id'

    try:
        parse_resource('acct:op_id_test_id@domain')
    except ValueError:
        pass

    try:
        parse_resource('https://example.com/rp-discovery-webfinger-url')
    except ValueError:
        pass
