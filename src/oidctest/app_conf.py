import json
import logging
import os

from future.backports.urllib.parse import parse_qs
from future.backports.urllib.parse import quote_plus
from future.backports.urllib.parse import unquote_plus
from oic.oic import ProviderConfigurationResponse
from oic.oic import RegistrationRequest
from oic.utils.http_util import get_post, BadRequest, ServiceError
from oic.utils.http_util import NotFound
from oic.utils.http_util import Response
from oic.utils.http_util import SeeOther

logger = logging.getLogger(__name__)

tool_conf = ['acr_values', 'claims_locales', 'instance_id', 'issuer',
             'login_hint', 'profile', 'ui_locales', 'webfinger_email',
             'webfinger_url']


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

    return unquote_plus(iss), unquote_plus(tag)


def empty_conf(cls):
    res = [(k, '') for k in cls.c_param.keys()]
    _dres = dict(res)
    return _dres


def create_model(profile, tag='default'):
    """

    :param profile:
    :return:
    """
    res = {}
    _tool = json.load(open('entity_info/tool.json', 'r'))
    res['tool'] = _tool['tool']
    p = profile.split('.')
    res['tool']['profile'] = profile
    res['tool']['issuer'] = 'Your OPs issuer id goes here'
    res['tool']['tag'] = 'default'

    if p[2] == 'F':
        econf = empty_conf(ProviderConfigurationResponse)
        try:
            res['client']['provider_info'] = econf
        except KeyError:
            res['client'] = {'provider_info': econf}

    if p[3] == 'F':
        econf = empty_conf(RegistrationRequest)
        try:
            res['client']['registration_response'] = econf
        except KeyError:
            res['client'] = {'registration_response': econf}

    return res


def verify_profile(profile):
    p = profile.split('.')
    if len(p) < 4:
        return False
    if p[0] not in ['C', 'I', 'IT', 'CT', 'CIT', 'CI']:
        return False
    for i in range(1, 4):
        if p[i] not in ['F', 'T']:
            return False
    return True


class REST(object):
    def __init__(self, entpath='entities'):
        self.entpath = entpath

    def entity_file_name(self, iss, tag):
        """

        :param iss: issuer ID quote_plus converted
        :param tag: issuer tag quote_plus converted
        :return:
        """
        if iss:
            if tag:
                fname = os.path.join(self.entpath, iss, tag)
            else:
                fname = os.path.join(self.entpath, iss)
            return fname
        else:
            return ''

    def entity_dir(self, iss):
        return os.path.join(self.entpath, iss)

    def read(self, iss, tag):
        fname = self.entity_file_name(iss, tag)
        if fname:
            fp = open(fname, 'r')
            _data = json.load(fp)
            fp.close()
            return _data
        else:
            return None

    def replace(self, qiss, qtag, info):
        # read entity configuration and replace if changed
        try:
            _js = json.loads(info)
        except Exception as err:
            resp = BadRequest(err)
            return
        else:
            self.write(qiss, qtag, _js)
            resp = Response()
        return resp

    def store(self, qiss, qtag, info):
        pass

    def delete(self, qiss, qtag):
        fname = self.entity_file_name(qiss, qtag)
        if os.path.isfile(fname):
            os.unlink(fname)
            return True
        else:
            return False

    def write(self, qiss, qtag, ent_conf):
        fdir = self.entity_dir(qiss)
        if os.path.isdir(fdir) is False:
            os.makedirs(fdir)

        fname = os.path.join(fdir, qtag)
        fp = open(fname, 'w')
        json.dump(ent_conf, fp)
        fp.close()


class IO(object):
    def __init__(self, rest, environ, start_response, lookup,
                 entpath='entities'):
        self.rest = rest
        self.environ = environ
        self.start_response = start_response
        self.lookup = lookup
        self.entpath = entpath

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
        resp = Response(mako_template="instance.mako",
                        template_lookup=self.lookup,
                        headers=[])

        qiss = quote_plus(iss)
        qtag = quote_plus(tag)
        _conf = self.rest.read(qiss, qtag)
        # provider_info and registration_response
        dicts = {'tool': _conf['tool']}
        for item in tool_conf:
            if item not in dicts['tool']:
                dicts['tool'][item] = ''

        for typ in ['provider_info', 'registration_response']:
            try:
                dicts[typ] = _conf['client'][typ]
            except KeyError:
                pass

        arg = {'base': '',
               'iss': qiss,
               'tag': qtag,
               'dicts': dicts}

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
        # self.ent_path = ent_path
        self.rest = REST(ent_path)

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

        _ent_conf['tool']['instance_id'] = q['tag'][0]
        _ent_conf['tool']['issuer'] = q['iss'][0]
        profile = [q['return_type'][0]]
        for p in ['webfinger', 'discovery', 'registration']:
            if p in q:
                profile.append('T')
            else:
                profile.append('F')

        _ent_conf['tool']['profile'] = '.'.join(profile)

        if 'registration' not in q:
            _ent_conf['client']['registration_response'] = empty_conf(
                RegistrationRequest)
        if 'discovery' not in q:
            _ent_conf['client']['provider_info'] = empty_conf(
                ProviderConfigurationResponse)

        _qiss = quote_plus(q['iss'][0])
        _qtag = quote_plus(q['tag'][0])
        io.rest.write(_qiss, _qtag, _ent_conf)
        return '{}form/update/{}/{}'.format(self.baseurl, _qiss, _qtag)

    def application(self, environ, start_response):
        logger.info("Connection from: %s" % environ["REMOTE_ADDR"])

        path = environ.get('PATH_INFO', '').lstrip('/')
        logger.info("path: %s" % path)

        _io = IO(rest=self.rest, environ=environ, start_response=start_response,
                 lookup=self.lookup)

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
        elif path.startswith('model/'):
            p = path.split('/')
            prof = p[1]
            if verify_profile(prof):
                info = create_model(prof)
                if info:
                    res = Response(json.dumps(info), content='applicaton/json')
                else:
                    res = ServiceError()
            else:
                res = BadRequest('Syntax error in profile specification')
            return res(environ, start_response)
        else:
            # check if this a REST request
            _iss, _tag = get_iss_and_tag(path)
            try:
                _conf = self.rest.read(
                    quote_plus(unquote_plus(_iss)),
                    quote_plus(unquote_plus(_tag)))
            except:
                resp = NotFound(path)
                return resp(environ, start_response)
            else:
                if environ.get('REQUEST_METHOD') == 'POST':
                    self.rest.replace(quote_plus(unquote_plus(_iss)),
                                      quote_plus(unquote_plus(_tag)),
                                      get_post(environ))
