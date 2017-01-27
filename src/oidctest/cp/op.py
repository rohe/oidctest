import cherrypy
import logging
from cherrypy import url
from future.backports.urllib.parse import urlparse

from oic.utils import webfinger
from oic.utils.keyio import key_summary

from oidctest.cp.op_handler import OPHandler

from otest.events import Event
from otest.events import EV_EXCEPTION
from otest.events import EV_REQUEST
from otest.events import EV_REQUEST_ARGS
from otest.events import Operation

logger = logging.getLogger(__name__)


def handle_error():
    cherrypy.response.status = 500
    cherrypy.response.body = [
        "<html><body>Sorry, an error occured</body></html>"
    ]


class WebFinger(object):
    def __init__(self, srv):
        self.srv = srv

    @cherrypy.expose
    def index(self, resource, rel):
        if rel != 'http://openid.net/specs/connect/1.0/issuer':
            raise cherrypy.NotFound()

        p = urlparse(resource)
        if p[0] == 'acct':
            loc, dom = p[2].split('@')  # Should I check dom ?
            ids = loc.split('.')
            if len(ids) != 2:
                raise cherrypy.HTTPError(
                    400, "local part must consist of <rp_id>.<test_id>")

            _path = '/'.join(ids)
        elif p[0] in ['http', 'https']:
            _path = p[2]
        else:
            raise cherrypy.HTTPError(400,
                                     'unknown scheme in webfinger resource')

        subj = resource
        href = '{}/{}/{}'.format(cherrypy.request.base, _path,
                                 '.well-known/openid-configuration')
        return self.srv.response(subj, href)


class Provider(object):
    _cp_config = {'request.error_response': handle_error}

    def __init__(self, op_handler, flows):
        self.op_handler = op_handler
        self.flows = flows

    def wrap(self, func, events):
        # kwargs = extract_from_request(environ)
        #
        # kwargs['test_cnf'] = session_info['test_conf']
        # try:
        #     oos = kwargs['test_cnf']['out_of_scope']
        # except KeyError:
        #     pass
        # else:
        #     if func.__name__ in oos:
        #         resp = error_response(
        #             error='incorrect_behavior',
        #             descr='You should not talk to this endpoint in this test')
        #         resp.add_header(CORS_HEADERS)
        #         return resp(environ, start_response)
        kwargs = {}
        events.store(EV_REQUEST_ARGS, kwargs["request"])
        #jlog.info({'operation': func.__name__, 'kwargs': kwargs})
        try:
            args = func(**kwargs)
        except Exception as err:
            events.store(EV_EXCEPTION, err)
            raise

    def configuration(self, op):
        _ev = Operation("ProviderConfiguration", path=url)
        #_ev.query = cherrypy.request.
        op.events.store(EV_REQUEST, _ev)
        logger.info('OP keys:{}'.format(key_summary(op.keyjar, '')))
        return op.providerinfo_endpoint

    def authorization(self, op):
        pass

    def token(self, op):
        pass

    def userinfo(self, op):
        pass

    def _cp_dispatch(self, vpath):
        #ent = cherrypy.request.remote.ip

        if len(vpath) >= 2:
            oper_id = vpath.pop(0)
            test_id = vpath.pop(0)

            # verify test_id
            try:
                self.flows[test_id]
            except KeyError:
                raise cherrypy.HTTPError(400, 'Unknown TestID')

            if len(vpath):
                endpoint = '/'.join(vpath[:])
                op = self.op_handler.get(oper_id, test_id, Event(), endpoint)

                if len(vpath) == 1:
                    if endpoint == 'authorization':
                        return self.authorization(op)
                    elif endpoint == 'token':
                        return self.token(op)
                    elif endpoint == 'userinfo':
                        return self.token(op)
                    else:  # Shouldn't be any other
                        raise cherrypy.NotFound()
                if len(vpath) == 2:
                    if endpoint == '.well-known/openid-configuration':
                        return self.configuration(op)


if __name__ == '__main__':
    from oidctest.rp import provider

    cherrypy.tree.mount(WebFinger(webfinger.WebFinger()),
                        '/.well-known/webfinger')

    op_args = com_args = test_conf = {}
    op_handler = OPHandler(provider.Provider, op_args, com_args, test_conf)
    cherrypy.tree.mount(Provider(op_handler), '/')

    cherrypy.engine.start()
    cherrypy.engine.block()

