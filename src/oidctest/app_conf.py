import json
import logging
import os

from future.backports.urllib.parse import parse_qs
from future.backports.urllib.parse import quote
from oic.oic import ProviderConfigurationResponse
from oic.oic import RegistrationRequest
from oic.utils.http_util import Response, NotFound, SeeOther

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


def empty_conf(cls):
    return dir([(k, '') for k in cls.c_param.keys()])


class IO(object):
    def __init__(self, environ, start_response, lookup, entpath='entities'):
        self.environ = environ
        self.start_response = start_response
        self.lookup = lookup
        self.entpath = entpath

    def entity_file_name(self, iss, tag):
        if iss:
            qiss = quote(iss)
            if tag:
                fname = os.path.join(self.entpath, qiss, quote(tag))
            else:
                fname = os.path.join(self.entpath, qiss)
            return ''
        else:
            return ''

    def entity_dir(self, iss):
        if iss:
            qiss = quote(iss)
            return os.path.join(self.entpath, qiss)
        else:
            return ''

    def get_entity_conf(self, iss, tag):
        fname = self.entity_file_name(iss, tag)
        if fname:
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

        args = {'base': ''}
        return resp(self.environ, self.start_response, **args)

    def new_instance(self, iss, tag):
        resp = Response(mako_template="new_instance.mako",
                        template_lookup=self.lookup,
                        headers=[])

        args = {'base': ''}
        return resp(self.environ, self.start_response, **args)

    def update_instance(self, iss, tag):
        resp = Response(mako_template="new_instance.mako",
                        template_lookup=self.lookup,
                        headers=[])

        fname = ''
        arg = {'base': ''}
        return resp(self.environ, self.start_response, **arg)

    def delete_instance(self, iss, tag):
        resp = Response(mako_template="new_instance.mako",
                        template_lookup=self.lookup,
                        headers=[])

        arg = {'base': ''}
        return resp(self.environ, self.start_response, **arg)


class Application(object):
    def __init__(self, baseurl, lookup, def_conf, ent_path):
        self.baseurl = baseurl
        self.lookup = lookup
        self.def_conf = def_conf
        self.ent_path = ent_path

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

    def do_entity_configuration(self, io):
        q = parse_qs(io.environ.get('QUERY_STRING'))
        fp = open(self.def_conf, 'r')
        _ent_conf = json.load(fp)
        fp.close()

        _ent_conf['TOOL']['instance_id'] = q['tag'][0]
        _ent_conf['TOOL']['issuer'] = q['iss'][0]
        profile = []
        for p in ['return_type', 'webfinger', 'discovery', 'registration']:
            if p in q:
                profile.append('T')
            else:
                profile.append('')

        _ent_conf['TOOL']['profile'] = '.'.join(profile)

        if 'registration' not in q:
            _ent_conf['CLIENT']['registration_response'] = empty_conf(
                RegistrationRequest)
        if 'discovery' not in q:
            _ent_conf['CLIENT']['provider_info'] = empty_conf(
                ProviderConfigurationResponse)

        fdir = io.entity_dir(q['iss'][0])
        if os.path.isdir(fdir) is False:
            os.mkdir(fdir)

        fname = os.path.join(fdir, tag=quote(q['tag'][0]))
        fp = open(fname, 'w')
        json.dump(_ent_conf, fp)
        return '{}/{}/{}'.format(self.baseurl, quote(q['iss'][0]), q['tag'][0])

    def application(self, environ, start_response):
        logger.info("Connection from: %s" % environ["REMOTE_ADDR"])

        path = environ.get('PATH_INFO', '').lstrip('/')
        logger.info("path: %s" % path)

        _io = IO(environ=environ, start_response=start_response,
                 lookup=self.lookup, entpath=self.ent_path)

        if path == "robots.txt":
            return _io.static("static/robots.txt")
        elif path == "favicon.ico":
            return _io.static("static/favicon.ico")
        elif path.startswith("static/"):
            return _io.static(path)
        elif path.startswith("export/"):
            return _io.static(path)

        if path == '':
            return _io.get_iss()
        elif path.startswith('form/'):
            return self.form_handling(path, _io)
        elif path == 'create':
            loc = self.do_entity_configuration(_io)
            resp = SeeOther(loc)
            return resp(_io.environ, _io.start_response)