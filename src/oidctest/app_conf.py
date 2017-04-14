from future.backports.urllib.parse import parse_qs
from future.backports.urllib.parse import quote_plus
from future.backports.urllib.parse import unquote_plus

import importlib
import json
import logging
import os
import re
import subprocess
import sys
import time

from oic.oic import ProviderConfigurationResponse
from oic.oic import RegistrationResponse
from oic.utils.http_util import BadRequest
from oic.utils.http_util import Created
from oic.utils.http_util import NotFound
from oic.utils.http_util import Response
from oic.utils.http_util import SeeOther
from oic.utils.http_util import ServiceError
from oic.utils.http_util import get_post
from otest.proc import find_test_instance
from otest.proc import isrunning
from otest.proc import kill_process
from otest.prof_util import do_discovery
from otest.prof_util import do_registration
from otest.prof_util import verify_profile
from otest.prof_util import return_type
from otest.prof_util import to_profile
from otest.rp.setup import read_path2port_map

from oidctest.ass_port import AssignedPorts

logger = logging.getLogger(__name__)


TYPE2CLS = {'provider_info': ProviderConfigurationResponse,
            'registration_response': RegistrationResponse}


class NoSuchFile(Exception):
    pass


port_pattern = re.compile('-p (\d*) ')

tool_conf = ['acr_values', 'claims_locales', 'issuer',
             'login_hint', 'profile', 'ui_locales', 'webfinger_email',
             'webfinger_url', 'insecure', 'tag']


def get_iss_and_tag(path):
    p = path.split('/')

    if len(p) == 1:
        return unquote_plus(p[0]), ''

    try:
        iss = p[-2]
    except IndexError:
        iss = ''
    try:
        tag = p[-1]
    except IndexError:
        tag = ''

    return unquote_plus(iss), unquote_plus(tag)


def expand_dict(info):
    """
    converts a dictionary with keys of the for a:b to a dictionary of 
    dictionaries. Also expands strings with ',' separated substring to a
    list of strings.
    
    :param info: dictionary 
    :return: dictionary of dictionaries
    """

    res = {}
    for key, val in info.items():
        a, b = key.split(':')
        if len(val) == 1:
            val = val[0]
            if ',' in val:
                val = [v.strip() for v in val.split(',')]
        else:
            if b == 'tag':
                val = val[0]
            else:
                val = ','.join(val)
        if val == 'False':
            val = False
        elif val == 'True':
            val = True
        try:
            res[a][b] = val
        except KeyError:
            res[a] = {b: val}
    return res


def implode_dict(dictdict):
    """
    converts a dictionary of dictionaries into a one level dictionary

    :param dictdict: dictionary
    :return: dictionary of dictionaries
    """

    res = {}
    for key, val in dictdict.items():
        for a, b in val.items():
            res['{}:{}'.format(key, a)] = val
    return res


def empty_conf(cls):
    return dict([(k, '') for k in cls.c_param.keys()])


def create_model(profile, tag='default', ent_info_path='entity_info'):
    """

    :param profile:  test instance profile
    :param tag:  test instance tag
    :return:  json document that can be used as a model for creating a
        test instance configuration
    """
    res = {}
    _tool = json.load(open('{}/tool.json'.format(ent_info_path), 'r'))

    res['tool'] = _tool['tool']
    res['tool']['profile'] = profile
    res['tool']['issuer'] = 'Your OPs issuer id goes here'

    res['tool']['tag'] = tag
    if not do_discovery(profile):
        econf = empty_conf(ProviderConfigurationResponse)
        try:
            res['client']['provider_info'] = econf
        except KeyError:
            res['client'] = {'provider_info': econf}

    if not do_registration(profile):
        econf = empty_conf(RegistrationResponse)
        try:
            res['client']['registration_response'] = econf
        except KeyError:
            res['client'] = {'registration_response': econf}

    return res


def verify_config(conf):
    """

    :param conf: Dictionary of dictionaries
    :return: True/False
    """

    for name, cls in TYPE2CLS.items():
        _inst = cls(**conf[name])
        if _inst.verify() is False:
            return False

    return True


def update(typ, conf):
    cls = TYPE2CLS[typ]
    for param in cls.c_param:
        if param not in conf:
            conf[param] = ''
    return conf


class REST(object):
    def __init__(self, base_url, entpath='entities', entinfo='entity_info'):
        self.base_url = base_url
        self.entpath = entpath
        self.entinfo = entinfo

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

    def construct_config(self, qiss, qtag):
        if not qtag:
            raise Exception('Missing "tag" value')

        _conf = json.loads(
            open('{}/common.json'.format(self.entinfo), 'r').read())

        try:
            typ, _econf = self.read_conf(qiss, qtag)
        except NoSuchFile:
            raise

        if _econf is None:
            raise Exception('No configuration for {}:{}'.format(qiss, qtag))

        if do_registration(_econf['tool']['profile']):
            reg_info = json.loads(
                open('{}/registration_info.json'.format(
                    self.entinfo), 'r').read())
            _conf['client']['registration_info'] = reg_info['registration_info']
        else:
            for typ in ['provider_info', 'registration_response']:
                try:
                    _conf['client'][typ] = _econf[typ]
                except KeyError:
                    pass

        _conf['tool'] = _econf['tool']
        return _conf

    def list_dir(self, dirname, qiss):
        if not os.path.isdir(dirname):
            if qiss.endswith('%2F'):  # try to remove
                qiss = qiss[:-3]
            else:  # else add
                qiss += '%2F'
            dirname = self.entity_file_name(qiss, '')
            if not os.path.isdir(dirname):
                raise NoSuchFile(dirname)

        iss = unquote_plus(qiss)
        res = ['<p>']
        for file in os.listdir(dirname):
            _url = '{}{}/{}'.format(self.base_url, qiss, quote_plus(file))
            res.append('<a href="{}">{}</a><br>'.format(_url, file))
        res.append('</p')
        _html = [
            '<html><head>List of tags for "{}"</head>'.format(iss),
            '<body>'
        ]
        _html.extend(res)
        _html.append('</body></html>')

        return 'html', '\n'.join(_html)

    def read_conf(self, qiss, qtag):
        """

        :param qiss: OP issuer qoute_plus converted
        :param qtag: test instance tag quote_plus converted
        :return: Returns the instance configuration as a dictionary
        """
        fname = self.entity_file_name(qiss, qtag)
        if fname:
            if not os.path.isfile(fname):
                if qiss.endswith('%2F'):  # try to remove
                    qiss = qiss[:-3]
                else:  # else add
                    qiss += '%2F'
                fname = self.entity_file_name(qiss, qtag)
                if not os.path.isfile(fname):
                    return self.list_dir(fname, qiss)

            try:
                _data = open(fname, 'r').read()
            except Exception as err:
                if sys.version[0] == '2':
                    if isinstance(err, IOError):
                        return None
                    else:
                        raise
                elif isinstance(err, FileNotFoundError):
                    return None
                else:
                    raise
            try:
                return 'json', json.loads(_data)
            except Exception as err:
                return None
        else:
            return None

    def read(self, qiss, qtag, path):
        """

        :param qiss: OP issuer qoute_plus converted
        :param qtag: test instance tag quote_plus converted
        :param path: The HTTP request path
        :return: A HTTP response
        """
        try:
            typ, info = self.read_conf(qiss, qtag)
        except (TypeError, NoSuchFile):
            resp = NotFound('Could not find {}'.format(path))
        else:
            if info:
                if typ == 'json':
                    resp = Response(json.dumps(info),
                                    content='application/json')
                else:
                    resp = Response(info, content='text/html')
            else:
                resp = NotFound('Could not find {}'.format(path))
        return resp

    def replace(self, qiss, qtag, info, path):
        # read entity configuration and replace if changed
        try:
            _js = json.loads(info)
        except Exception as err:
            return BadRequest(err)

        _js0 = self.read_conf(qiss, qtag)
        if _js == _js0:  # don't bother
            pass
        else:
            self.write(qiss, qtag, json.dumps(_js))

        return Response('OK')

    def store(self, qiss, qtag, info):
        """

        :param qiss: OP issuer qoute_plus converted
        :param qtag: test instance tag quote_plus converted
        :param info: test instance configuration as JSON document
        :return: HTTP Created is successful
        """
        self.write(qiss, qtag, info)
        fname = '{}{}/{}'.format(self.base_url, qiss, qtag)
        return Created(fname)

    def delete(self, qiss, qtag):
        fname = self.entity_file_name(qiss, qtag)
        if os.path.isfile(fname):
            os.unlink(fname)
        # If it doesn't exit don't tell because it leaks information.
        return Response('OK')

    def write(self, qiss, qtag, ent_conf):
        fdir = self.entity_dir(qiss)
        if os.path.isdir(fdir) is False:
            os.makedirs(fdir)

        fname = os.path.join(fdir, qtag)
        fp = open(fname, 'w')
        if isinstance(ent_conf, dict):
            json.dump(ent_conf, fp)
        else:
            fp.write(ent_conf)
        fp.close()


class IO(object):
    def __init__(self, rest, environ, start_response, lookup, baseurl,
                 entpath='entities'):
        self.rest = rest
        self.environ = environ
        self.start_response = start_response
        self.lookup = lookup
        self.baseurl = baseurl
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

    def new_iss(self):
        resp = Response(mako_template="new_iss.mako",
                        template_lookup=self.lookup,
                        headers=[])

        args = {'base': ''}
        return resp(self.environ, self.start_response, **args)

    def update_instance(self, *parts):
        resp = Response(mako_template="instance.mako",
                        template_lookup=self.lookup,
                        headers=[])

        lp = [unquote_plus(p) for p in parts]
        qp = [quote_plus(p) for p in lp]
        format, _conf = self.rest.read_conf(qp[0], qp[1])
        # provider_info and registration_response
        dicts = {'tool': _conf['tool']}
        for item in tool_conf:
            if item not in dicts['tool']:
                dicts['tool'][item] = ''

        for typ in ['provider_info', 'registration_response']:
            try:
                dicts[typ] = _conf['client'][typ]
            except KeyError:
                try:
                    dicts[typ] = update(typ, _conf[typ])
                except KeyError:
                    pass

        state = {'immutable': {}, 'required': {}}
        if 'registration_response' in dicts:
            state['registration_response'] = {
                'immutable': ['redirect_uris'],
                'required': ['client_id', 'client_secret']}

        if 'provider_info':
            state['provider_info'] = {
                'immutable': ['issuer'],
                'required': ['authorization_endpoint', 'jwks_uri',
                             'response_types_supported',
                             'subject_types_supported',
                             'id_token_signing_alg_values_supported']
            }

            if return_type(_conf['tool']['profile']) not in ['I', 'IT']:
                state['provider_info']['required'].append('token_endpoint')

        arg = {'base': '',
               'iss': qp[0],
               'tag': qp[1],
               'dicts': dicts,
               'state': state}

        return resp(self.environ, self.start_response, **arg)

    def delete_instance(self, parts, pid=0, app=None):
        lp = [unquote_plus(p) for p in parts]
        qp = [quote_plus(p) for p in lp]
        _key = app.assigned_ports.make_key(*lp)

        if pid:
            kill_process(pid)
            del app.running_processes[_key]

        os.unlink(os.path.join(self.entpath, *qp))
        # Remove issuer if out of tags
        if not os.listdir(os.path.join(self.entpath, qp[0])):
            os.rmdir(os.path.join(self.entpath, qp[0]))

        del app.assigned_ports[_key]

        resp = Response(mako_template='message.mako',
                        template_lookup=self.lookup,
                        headers=[])

        args = {'title': "Action performed", 'base': self.baseurl,
                'note':
                    'Your test tool instance <em>{} {}</em> has been '
                    'removed'.format(*lp)}
        return resp(self.environ, self.start_response, **args)

    def main(self):
        resp = Response(mako_template="main.mako",
                        template_lookup=self.lookup,
                        headers=[])
        arg = {'base': self.baseurl}
        return resp(self.environ, self.start_response, **arg)

    def list_iss(self):
        resp = Response(mako_template="list_iss.mako",
                        template_lookup=self.lookup,
                        headers=[])

        fils = os.listdir(self.entpath)
        # Remove examples
        fils.remove('https%3A%2F%2Fexample.com')
        args = {'base': self.baseurl, 'issuers': fils}
        return resp(self.environ, self.start_response, **args)

    def list_tag(self, iss):
        resp = Response(mako_template="list_tag.mako",
                        template_lookup=self.lookup,
                        headers=[])

        _iss = unquote_plus(iss)
        qiss = quote_plus(_iss)
        fils = os.listdir(os.path.join(self.entpath, qiss))

        active = dict([(fil, isrunning(_iss, fil)) for fil in fils])

        args = {'base': self.baseurl, 'items': fils,
                "qiss": qiss, "iss": _iss, 'active': active}
        return resp(self.environ, self.start_response, **args)

    def show_tag(self, part):
        resp = Response(mako_template="action.mako",
                        template_lookup=self.lookup,
                        headers=[])

        lp = [unquote_plus(p) for p in part[1:]]

        if find_test_instance(*lp):
            active = True
        else:
            active = False

        qp = [quote_plus(p) for p in lp]
        info = open(os.path.join(self.entpath, *qp), 'r').read()
        args = {'base': self.baseurl, 'info': json.loads(info),
                "qargs": qp, "largs": lp, 'active': active}
        return resp(self.environ, self.start_response, **args)

    def restart_instance(self, app, part):
        _iss = unquote_plus(part[0])
        _tag = unquote_plus(part[1])
        url = app.run_test_instance(quote_plus(_iss), quote_plus(_tag))
        if isinstance(url, Response):
            return url(self.environ, self.start_response)

        resp = Response(mako_template='message.mako',
                        template_lookup=self.lookup,
                        headers=[])

        if url:
            args = {
                'title': "Action performed", 'base': self.baseurl,
                'note': 'Your test instance "{iss}:{tag}" has been '
                        'restarted as <a href="{url}">{url}</a>'.format(
                    iss=_iss, tag=_tag, url=url)}
        else:
            args = {
                'title': "Action Failed", 'base': self.baseurl,
                'note': 'Could not restart your test instance'}

        return resp(self.environ, self.start_response, **args)


class Application(object):
    def __init__(self, base_url, lookup, ent_path, ent_info, flowdir,
                 test_script,
                 path2port=None, mako_dir='', port_min=60000, port_max=61000,
                 test_tool_conf=''):
        self.baseurl = base_url
        self.lookup = lookup
        self.ent_path = ent_path
        self.ent_info = ent_info
        self.flowdir = flowdir
        self.path2port = path2port
        self.mako_dir = mako_dir
        self.test_tool_conf = test_tool_conf
        self.test_script = test_script

        self.assigned_ports = AssignedPorts('assigned_ports.json', port_min,
                                            port_max)
        self.assigned_ports.load()
        self.running_processes = self.assigned_ports.sync(test_script)

        # self.ent_path = ent_path
        self.rest = REST(base_url, ent_path, ent_info)

        sys.path.insert(0, ".")
        ttc = importlib.import_module(test_tool_conf)
        self.test_tool_base = ttc.BASE
        if not self.test_tool_base.endswith('/'):
            self.test_tool_base += '/'

    def get_pid(self, parts):
        lp = [unquote_plus(p) for p in parts]
        qp = [quote_plus(p) for p in lp]
        try:
            return self.running_processes[self.key(*qp)]
        except KeyError:
            return 0

    def return_port(self, qiss, qtag):
        """
        Unmake an assignment. That is return an assigned port to the free list.
        :param qiss: quoted identifier
        :param qtag: quoted tag
        """
        try:
            del self.assigned_ports[self.assigned_ports.make_key(qiss, qtag)]
        except KeyError:
            pass

    def run_test_instance(self, iss, tag):
        _port = self.assigned_ports.register_port(iss, tag)
        args = [self.test_script, "-i", unquote_plus(iss), "-t",
                unquote_plus(tag), "-p", str(_port), "-M", self.mako_dir,
                "-f", self.flowdir]
        if self.path2port:
            args.extend(["-m", self.path2port])
            ppmap = read_path2port_map(self.path2port)
            try:
                _path = ppmap[str(_port)]
            except KeyError:
                _errtxt = 'Port not in path2port map file {}'.format(
                    self.path2port)
                logger.error(_errtxt)
                return ServiceError(_errtxt)
            url = '{}{}'.format(self.test_tool_base, _path)
        else:
            url = '{}:{}'.format(self.test_tool_base[:-1], _port)

        typ, _econf = self.rest.read_conf(iss, tag)
        if _econf['tool']['insecure']:
            args.append('-k')

        args.append(self.test_tool_conf)

        # If already running - kill
        try:
            pid = isrunning(unquote_plus(iss), unquote_plus(tag))
        except KeyError:
            pass
        else:
            if pid:
                logger.info('kill {}'.format(pid))
                subprocess.call(['kill', str(pid)])

        # Now get it running
        args.append('&')
        logger.info("Test tool command: {}".format(" ".join(args)))
        # spawn independent process
        os.system(" ".join(args))

        pid = 0
        for i in range(0,10):
            time.sleep(1)
            pid = isrunning(unquote_plus(iss), unquote_plus(tag))
            if pid:
                break

        if pid:
            logger.info("process id: {}".format(pid))
            self.running_processes[self.key(iss, tag)] = pid
            return url
        else:
            return None

    def form_handling(self, path, io):
        iss, tag = get_iss_and_tag(path)

        if path == 'form/init':
            resp = Response()
            return io.new_iss()
        elif path.startswith('form/create'):
            return io.new_instance(iss, tag)
        elif path.startswith('form/update'):
            return io.update_instance(iss, tag)
        elif path.startswith('form/delete'):
            return io.delete_instance(iss, tag, pid=self.get_pid([iss, tag]),
                                      app=self)
        else:
            resp = NotFound()
            return resp(io.environ, io.start_response)

    def basic_entity_configuration(self, io):
        q = parse_qs(io.environ.get('QUERY_STRING'))

        # construct profile
        profile = to_profile(q)
        _ent_conf = create_model(profile, ent_info_path=self.ent_info)
        state = {}

        if not do_discovery(profile):
            _ent_conf['client']['provider_info']['issuer'] = q['iss'][0]

        if not do_registration(profile):
            # need to create a redirect_uri, means I need to register a port
            _port = self.assigned_ports.register_port(q['iss'][0], q['tag'][0])
            _ent_conf['client']['registration_response'][
                'redirect_uris'] = '{}:{}/authz_cb'.format(
                self.test_tool_base[:-1], _port)

        _ent_conf['tool']['tag'] = q['tag'][0]
        _ent_conf['tool']['issuer'] = q['iss'][0]
        _ent_conf['tool']['profile'] = profile

        _qiss = quote_plus(q['iss'][0])
        _qtag = quote_plus(q['tag'][0])
        io.rest.write(_qiss, _qtag, _ent_conf)
        return '{}form/update/{}/{}'.format(self.baseurl, _qiss, _qtag)

    def application(self, environ, start_response):
        logger.info("Connection from: %s" % environ["REMOTE_ADDR"])

        path = environ.get('PATH_INFO', '').lstrip('/')
        logger.info("path: %s" % path)

        _io = IO(rest=self.rest, environ=environ, start_response=start_response,
                 lookup=self.lookup, baseurl=self.baseurl)

        if path == "robots.txt":
            return _io.static("static/robots.txt")
        elif path == "favicon.ico":
            return _io.static("static/favicon.ico")
        elif path.startswith("static/"):
            return _io.static(path)
        elif path.startswith("export/"):
            return _io.static(path)

        if path == '':
            return _io.main()
        if path == 'new':
            return _io.new_iss()
        if path == 'entity':
            return _io.list_iss()
        elif path.startswith('entity/'):
            p = path.split('/')
            while p[-1] == '':
                p = p[:-1]

            if len(p) == 2:
                return _io.list_tag(p[1])
            elif len(p) == 3:
                return _io.show_tag(p)
            elif len(p) == 4:
                _com = p[-1]
                if _com == 'action':
                    _qs = parse_qs(environ.get('QUERY_STRING'))
                    try:
                        _act = _qs['action'][0]
                    except KeyError:
                        resp = BadRequest('missing query parameter')
                        return resp(environ, start_response)

                    if _act == 'delete':
                        return _io.delete_instance(p[1:3],
                                                   pid=self.get_pid(p[1:3]),
                                                   app=self)
                    elif _act == 'restart':
                        return _io.restart_instance(self, p[1:3])
                    elif _act == 'configure':
                        return _io.update_instance(*p[1:3])
                    else:
                        resp = BadRequest('Unknown action')
                        return resp(environ, start_response)

        elif path.startswith('form/'):
            return self.form_handling(path, _io)
        elif path == 'create':
            loc = self.basic_entity_configuration(_io)
            resp = SeeOther(loc)
            return resp(_io.environ, _io.start_response)
        elif path.startswith('run/'):
            _iss, _tag = get_iss_and_tag(path)
            if _iss == '' or _tag == '':
                resp = BadRequest('Path must be of the form /run/<iss>/<tag>')
                return resp(environ, start_response)
            _qiss = quote_plus(_iss)
            _qtag = quote_plus(_tag)
            _info = parse_qs(get_post(environ))
            ent_conf = expand_dict(_info)
            if not verify_config(ent_conf):
                resp = BadRequest('Incorrect configuration')
            else:
                self.rest.write(_qiss, _qtag, ent_conf)
                resp = self.run_test_instance(_qiss, _qtag)
                if not isinstance(resp, Response):
                    resp = SeeOther(resp)
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
        elif path.startswith('register/'):
            _iss, _tag = get_iss_and_tag(path)
            _qiss = quote_plus(_iss)
            _qtag = quote_plus(_tag)
            _met = environ.get('REQUEST_METHOD')
            if _met == 'GET':
                return self.assigned_ports.register_port(_qiss, _qtag)
            elif _met == 'DELETE':
                return self.return_port(_qiss, _qtag)
        else:
            # check if this a REST request
            _iss, _tag = get_iss_and_tag(path)
            _qiss = quote_plus(_iss)
            _qtag = quote_plus(_tag)
            _path = '/{}/{}'.format(_qiss, _qtag)
            _met = environ.get('REQUEST_METHOD')
            if _met == 'GET':
                resp = self.rest.read(_qiss, _qtag, _path)
            elif _met == 'POST':
                resp = self.rest.replace(_qiss, _qtag, get_post(environ), _path)
            elif _met == 'PUT':
                resp = self.rest.store(_qiss, _qtag, get_post(environ))
            elif _met == 'DELETE':
                resp = self.rest.delete(_qiss, _qtag)
            else:
                resp = BadRequest('Unsupported request method')

            return resp(environ, start_response)
