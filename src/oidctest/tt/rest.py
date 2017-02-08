import json
import logging
import os
import sys

from urllib.parse import quote_plus
from urllib.parse import unquote_plus

from oic.utils.http_util import BadRequest, NotFound
from oic.utils.http_util import Created
from oic.utils.http_util import Response

logger = logging.getLogger(__name__)


class NoSuchFile(Exception):
    pass


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

        typ, _econf = self.read_conf(qiss, qtag)

        if _econf is None:
            raise Exception('No configuration for {}:{}'.format(qiss, qtag))

        if _econf['tool']['profile'].split('.')[-1] == 'T':
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
                raise ValueError(dirname)

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
                    raise NoSuchFile(fname)
                    #return self.list_dir(fname, qiss)

            try:
                _data = open(fname, 'r').read()
            except Exception as err:
                if sys.version[0] == '2':
                    if isinstance(err, IOError):
                        return None
                    else:
                        raise NoSuchFile(fname)
                elif isinstance(err, FileNotFoundError):
                    return None
                else:
                    raise NoSuchFile(fname)
            try:
                return 'json', json.loads(_data)
            except Exception as err:
                logger.error(err)
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

    def replace(self, qiss, qtag, info):
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
