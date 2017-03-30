import os
from urllib.parse import unquote_plus, quote_plus

import cherrypy

import logging
from jwkest import as_bytes
from oic.utils.http_util import Response
from otest.events import EV_FAULT
from otest.events import EV_RESPONSE


logger = logging.getLogger(__name__)


BUT = '<button name="action" type="submit" value="{}" class="choice">{}</button>'


def conv_response(events, resp):
    if not isinstance(resp, Response):
        return resp

    _stat = int(resp._status.split(' ')[0])

    if _stat < 300:
        events.store(EV_RESPONSE, resp.message)
        for key, val in resp.headers:
            cherrypy.response.headers[key] = val
        return as_bytes(resp.message)
    elif 300 <= _stat < 400:
        events.store('Redirect', resp.message)
        raise cherrypy.HTTPRedirect(resp.message)
    else:
        events.store(EV_FAULT, resp.message)
        raise cherrypy.HTTPError(_stat, resp.message)


def unquote_quote(*part):
    uqp = [unquote_plus(p) for p in part]
    qp = [quote_plus(p) for p in uqp]
    return uqp, qp

