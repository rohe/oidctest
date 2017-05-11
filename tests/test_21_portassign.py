from future.backports.urllib.parse import quote_plus

from oidctest.ass_port import AssignedPorts, OutOfRange


def test_port():
    pmin = 60000
    pmax = 60004
    # test_script, flowdir, rest, port_min, port_max,
    # test_tool_base, test_tool_conf, prehtml,
    app = AssignedPorts('assport', pmin, pmax)

    _port1 = app.register_port(quote_plus('https://example.com'), 'one')
    assert _port1 == pmin

    _port2 = app.register_port(quote_plus('https://example.com'), 'two')
    assert _port2 != _port1
    assert pmin < _port2 <= pmax

    _port3 = app.register_port(quote_plus('https://example.com'), 'three')
    assert _port3 not in [_port1, _port2]
    assert pmin < _port3 <= pmax

    _port4 = app.register_port(quote_plus('https://example.com'), 'four')
    assert _port4 not in [_port1, _port2, _port3]
    assert pmin < _port4 <= pmax

    _port5 = app.register_port(quote_plus('https://example.com'), 'five')
    assert _port5 not in [_port1, _port2, _port3, _port4]
    assert pmin < _port4 <= pmax

    try:
        _ = app.register_port(quote_plus('https://example.com'), 'six')
    except OutOfRange:
        assert True
    else:
        assert False

    del app[app.make_key('https://example.com', 'three')]
    _port6 = app.register_port(quote_plus('https://example.com'), 'six')
    assert _port6 not in [_port1, _port2, _port4, _port5]
    assert pmin < _port4 <= pmax
