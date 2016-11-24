import logging
import os

from future.backports.urllib.parse import quote
from oic.utils.http_util import Response, NotFound

logger = logging.getLogger(__name__)


def get_iss_and_tag(path):
    p = path.split('/')
    try:
        iss = p[2]
    except IndexError:
        iss = ''
    try:
        tag = p[3]
    except IndexError:
        tag = ''

    return iss, tag


class IO(object):
    def __init__(self, environ, start_response, lookup, entpath='entities'):
        self.environ = environ
        self.start_response = start_response
        self.lookup = lookup
        self.entpath = entpath

    def get_entity_conf(self, iss, tag):
        if iss:
            qiss = quote(iss)
            if tag:
                fname = os.path.join(self.entpath, qiss, quote(tag))
            else:
                fname = os.path.join(self.entpath, qiss)
            return open(fname).read()
        else:
            return None

    def static(self, path):
        logger.info("[static]sending: %s" % (path,))

        try:
            text = open(path, 'rb').read()
            if path.endswith(".ico"):
                self.start_response('200 OK', [('Content-Type',
                                                "image/x-icon")])
            elif path.endswith(".html"):
                self.start_response('200 OK', [('Content-Type', 'text/html')])
            elif path.endswith(".json"):
                self.start_response('200 OK', [('Content-Type',
                                                'application/json')])
            elif path.endswith(".jwt"):
                self.start_response('200 OK', [('Content-Type',
                                                'application/jwt')])
            elif path.endswith(".txt"):
                self.start_response('200 OK', [('Content-Type', 'text/plain')])
            elif path.endswith(".css"):
                self.start_response('200 OK', [('Content-Type', 'text/css')])
            else:
                self.start_response('200 OK', [('Content-Type', "text/plain")])
            return [text]
        except IOError:
            resp = NotFound()
            return resp(self.environ, self.start_response)

    def get_iss(self):
        resp = Response(mako_template="new_iss.mako",
                        template_lookup=self.lookup,
                        headers=[])

        return resp(self.environ, self.start_response)

    def new_instance(self, iss, tag):
        resp = Response(mako_template="new_instance.mako",
                        template_lookup=self.lookup,
                        headers=[])

        arg = {}

        return resp(self.environ, self.start_response)

    def update_instance(self, iss, tag):
        resp = Response(mako_template="new_instance.mako",
                        template_lookup=self.lookup,
                        headers=[])

        fname = ''
        arg = {}
        return resp(self.environ, self.start_response, **arg)

    def delete_instance(self, iss, tag):
        resp = Response(mako_template="new_instance.mako",
                        template_lookup=self.lookup,
                        headers=[])

        arg = {}
        return resp(self.environ, self.start_response, **arg)


class Application(object):
    def __init__(self, lookup):
        self.lookup = lookup

    def form_handling(self, path, io):
        iss, tag = get_iss_and_tag(path)

        if path == 'form/init':
            return io.get_iss()
        elif path.startswith('form/create'):
            return io.new_instance(iss, tag)
        elif path.startswith('form/update'):
            return io.update_instance(iss, tag)
        elif path.startswith('form/delete'):
            return io.delete_instance(iss, tag)
        else:
            resp = NotFound()
            return resp(io.environ, io.start_response)

    def application(self, environ, start_response):
        logger.info("Connection from: %s" % environ["REMOTE_ADDR"])

        path = environ.get('PATH_INFO', '').lstrip('/')
        logger.info("path: %s" % path)

        _io = IO(environ=environ, start_response=start_response,
                 lookup=self.lookup)

        if path == "robots.txt":
            return _io.static("static/robots.txt")
        elif path == "favicon.ico":
            return _io.static("static/favicon.ico")
        elif path.startswith("static/"):
            return _io.static(path)
        elif path.startswith("export/"):
            return _io.static(path)

        if path.startswith(''):
            return _io.get_iss()
        elif path.startswith('form/'):
            return self.form_handling(path, _io)
