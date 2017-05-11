from future.backports.urllib.parse import quote_plus

from oidctest.app_conf import Application
from oidctest.app_conf import OutOfRange


def test_port():
    pmin = 60000
    pmax = 60004
    app = Application('', None, '', '', None, path2port='path2port.csv',
                      port_min=pmin, port_max=pmax)

    _port1 = app.get_port(quote_plus('https://example.com'), 'one')
    assert _port1 == pmin

    _port2 = app.get_port(quote_plus('https://example.com'), 'two')
    assert _port2 != _port1
    assert pmin < _port2 <= pmax

    _port3 = app.get_port(quote_plus('https://example.com'), 'three')
    assert _port3 not in [_port1, _port2]
    assert pmin < _port3 <= pmax

    _port4 = app.get_port(quote_plus('https://example.com'), 'four')
    assert _port4 not in [_port1, _port2, _port3]
    assert pmin < _port4 <= pmax

    _port5 = app.get_port(quote_plus('https://example.com'), 'five')
    assert _port5 not in [_port1, _port2, _port3, _port4]
    assert pmin < _port4 <= pmax

    try:
        _ = app.get_port(quote_plus('https://example.com'), 'six')
    except OutOfRange:
        assert True
    else:
        assert False

    app.return_port(quote_plus('https://example.com'), 'three')
    _port6 = app.get_port(quote_plus('https://example.com'), 'six')
    assert _port6 not in [_port1, _port2, _port4, _port5]
    assert pmin < _port4 <= pmax
