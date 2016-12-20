import importlib
import json
import logging
import os
import re
import subprocess

import sys

import time
from future.backports.urllib.parse import parse_qs
from future.backports.urllib.parse import quote_plus
from future.backports.urllib.parse import unquote_plus
from jwkest import as_unicode

from oic.oic import ProviderConfigurationResponse
from oic.oic import RegistrationResponse
from oic.utils.http_util import get_post
from oic.utils.http_util import BadRequest
from oic.utils.http_util import Created
from oic.utils.http_util import ServiceError
from oic.utils.http_util import NotFound
from oic.utils.http_util import Response
from oic.utils.http_util import SeeOther
from otest.rp.setup import read_path2port_map

logger = logging.getLogger(__name__)


class OutOfRange(Exception):
    pass


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
    dictionaries
    
    :param info: dictionary 
    :return: dictionary of dictionaries
    """

    res = {}
    for key, val in info.items():
        a, b = key.split(':')
        if len(val) == 1:
            val = val[0]
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
    p = profile.split('.')
    res['tool']['profile'] = profile
    res['tool']['issuer'] = 'Your OPs issuer id goes here'

    res['tool']['tag'] = tag
    if p[2] == 'F':
        econf = empty_conf(ProviderConfigurationResponse)
        try:
            res['client']['provider_info'] = econf
        except KeyError:
            res['client'] = {'provider_info': econf}

    if p[3] == 'F':
        econf = empty_conf(RegistrationResponse)
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
        _conf = json.loads(
            open('{}/common.json'.format(self.entinfo), 'r').read())
        try:
            _econf = self.read_conf(qiss, qtag)
        except NoSuchFile:
            raise

        if _econf is None:
            raise Exception('No configuration for {}:{}'.format(qiss, qtag))

        if _econf['tool']['profile'].split('.')[-1] == 'T':
            reg_info = json.loads(
                open('{}/registration_info.json'.format(
                    self.entinfo), 'r').read())
            _conf['client']['registration_info'] = reg_info['registration_info']
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
            _url = '{}{}/{}'.format(self.base_url,qiss,quote_plus(file))
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
        except NoSuchFile:
            resp = NotFound('Could not find {}'.format(path))
        else:
            if info:
                if typ == 'json':
                    resp = Response(json.dumps(info), content='application/json')
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
        _conf = self.rest.read_conf(qiss, qtag)
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
    def __init__(self, baseurl, lookup, ent_path, ent_info, flows, test_script,
                 path2port=None, mako_dir='', port_min=60000, port_max=61000,
                 test_tool_conf=''):
        self.baseurl = baseurl
        self.lookup = lookup
        self.ent_info = ent_info
        self.flows = flows
        self.path2port = path2port
        self.mako_dir = mako_dir
        self.port_min = port_min
        self.port_max = port_max
        self.test_tool_conf = test_tool_conf
        self.test_script = test_script

        try:
            _ass = open('assigned_ports.json').read()
        except Exception as err:
            if sys.version[0] == '2':
                if isinstance(err, IOError):
                    self.assigned_ports = {}
                else:
                    raise
            elif isinstance(err, FileNotFoundError):
                self.assigned_ports = {}
            else:
                raise
        else:
            self.assigned_ports = json.loads(_ass)

        self.running_processes = {}
        # self.ent_path = ent_path
        self.rest = REST(baseurl, ent_path, ent_info)

        sys.path.insert(0, ".")
        ttc = importlib.import_module(test_tool_conf)
        self.test_tool_base = ttc.BASE
        if not self.test_tool_base.endswith('/'):
            self.test_tool_base += '/'

        try:
            byt = subprocess.check_output(['pgrep', '-f', '-l', 'optest.py'],
                                          universal_newlines=True)
        except subprocess.CalledProcessError:
            pass
        else:
            lin = as_unicode(byt)
            for l in lin.split('\n'):
                m = port_pattern.search(l)
                if m:
                    _port = m.group(1)
                    _pid = l.split(' ')[0]
                    try:
                        for key, val in self.assigned_ports.items():
                            if val == _port:
                                self.running_processes[key] = _pid
                                break
                    except KeyError:
                        logger.warning('unregistered optest process')

    def get_port(self, iss, tag):
        _key = '{}:{}'.format(iss, tag)
        try:
            _port = self.assigned_ports[_key]
        except KeyError:
            if self.assigned_ports == {}:
                _port = self.port_min
                self.assigned_ports[_key] = _port
            else:
                pl = list(self.assigned_ports.values())
                pl.sort()
                if pl[0] != self.port_min:
                    _port = self.port_min
                    self.assigned_ports[_key] = _port
                else:
                    _port = self.port_min
                    for p in pl:
                        if p == _port:
                            _port += 1
                            continue
                        else:
                            break
                    if _port > self.port_max:
                        raise OutOfRange('Out of ports')
                    self.assigned_ports[_key] = _port
            fp = open('assigned_ports.json', 'w')
            fp.write(json.dumps(self.assigned_ports))
            fp.close()
        return _port

    def return_port(self, iss, tag):
        _key = '{}:{}'.format(iss, tag)
        try:
            del self.assigned_ports[_key]
        except KeyError:
            pass

    def run_test_instance(self, iss, tag):
        _port = self.get_port(iss, tag)
        args = [self.test_script, "-i", unquote_plus(iss), "-t",
                unquote_plus(tag), "-p", str(_port), "-M", self.mako_dir]
        for _fl in self.flows:
            args.extend(["-f", _fl])
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

        _econf = self.rest.read_conf(iss, tag)
        if _econf['tool']['insecure']:
            args.append('-k')

        args.append(self.test_tool_conf)

        _key = '{}:{}'.format(iss, tag)
        # If already running - kill
        try:
            pid = self.running_processes[_key]
        except KeyError:
            pass
        else:
            logger.info('kill {}'.format(pid))
            subprocess.call(['kill', pid])

        logger.info(args)

        # spawn independent process
        with open('err.log', 'w') as OUT:
            pid = subprocess.Popen(args, stdin=OUT, stdout=OUT,
                                   stderr=subprocess.STDOUT, close_fds=True).pid
        # continues immediately
        logger.info("process id: {}".format(pid))
        self.running_processes['{}:{}'.format(iss, tag)] = pid

        time.sleep(5)
        return url

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

    def basic_entity_configuration(self, io):
        q = parse_qs(io.environ.get('QUERY_STRING'))

        # construct profile
        ppiece = [q['return_type'][0]]
        for p in ['webfinger', 'discovery', 'registration']:
            if p in q:
                ppiece.append('T')
            else:
                ppiece.append('F')

        profile = '.'.join(ppiece)
        _ent_conf = create_model(profile, ent_info_path=self.ent_info)

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
