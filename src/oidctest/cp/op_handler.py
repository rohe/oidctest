import copy
import json
import os

from oic import rndstr
from oic.utils.keyio import KeyJar
from oic.utils.keyio import key_summary
from oic.utils.sdb import create_session_db
from otest.conversation import Conversation

from oidctest import UnknownTestID


def write_jwks_uri(op, op_arg, folder):
    _name = "jwks_{}.json".format(rndstr())
    filename = os.path.join(folder,'static',_name)
    with open(filename, "w") as f:
        f.write(json.dumps(op_arg["jwks"]))
    f.close()

    op.jwks_uri = "{}static/{}".format(op_arg["baseurl"], _name)
    op.jwks_name = filename


def init_keyjar(op, kj, com_args):
    op.keyjar = KeyJar()
    try:
        op.keyjar.verify_ssl = com_args['verify_ssl']
    except KeyError:
        pass

    for kb in kj.issuer_keys['']:
        for k in kb.keys():
            k.inactive_since = 0
        op.keyjar.add_kb('', copy.copy(kb))


class OPHandler(object):
    def __init__(self, provider_cls, op_args, com_args, test_conf, folder):
        self.provider_cls = provider_cls
        self.op_args = op_args
        self.com_args = com_args
        self.test_conf = test_conf  # elsewhere called flows
        self.folder = folder
        self.op = {}

    def get(self, oper_id, test_id, events, endpoint):
        # addr = get_client_address(environ)
        key = path = '{}/{}'.format(oper_id, test_id)

        try:
            _op = self.op[key]
            _op.events = events
            if endpoint == '.well-known/openid-configuration':
                if test_id == 'rp-key-rotation-op-sign-key-native':
                    pass
                elif test_id == 'rp-id_token-kid-absent-multiple-jwks':
                    setattr(_op, 'keys', self.op_args['marg']['keys'])
                    _op_args = {
                        'baseurl': self.op_args['baseurl'],
                        'jwks': self.op_args['marg']['jwks']
                    }
                    write_jwks_uri(_op, _op_args, self.folder)
                else:
                    init_keyjar(_op, self.op_args['keyjar'], self.com_args)
                    _kj = _op.keyjar.export_jwks(True, '')
                    _op.keyjar.import_jwks(_kj, _op.name)
                    write_jwks_uri(_op, self.op_args, self.folder)
        except KeyError:
            if test_id in ['rp-id_token-kid-absent-multiple-jwks']:
                _op_args = {}
                for param in ['baseurl', 'cookie_name', 'cookie_ttl',
                              'endpoints']:
                    _op_args[param] = self.op_args[param]
                for param in ["jwks", "keys"]:
                    _op_args[param] = self.op_args["marg"][param]
                _op = self.setup_op(oper_id, test_id, self.com_args, _op_args,
                                    self.test_conf, events)
            else:
                _op = self.setup_op(oper_id, test_id, self.com_args,
                                    self.op_args, self.test_conf, events)
            _op.conv = Conversation(test_id, _op, None)
            _op.orig_keys = key_summary(_op.keyjar, '').split(', ')
            self.op[key] = _op

        return _op, path, key

    def setup_op(self, oper_id, test_id, com_args, op_arg, test_conf, events):
        _sdb = create_session_db(com_args["baseurl"], 'automover', '430X', {})
        op = self.provider_cls(sdb=_sdb, **com_args)
        op.events = events
        op.oper_id = oper_id
        op.test_id = test_id

        for _authn in com_args["authn_broker"]:
            _authn.srv = op

        for key, val in list(op_arg.items()):
            if key == 'keyjar':
                init_keyjar(op, val, com_args)
            else:
                setattr(op, key, val)

        if not op.cookie_path:
            op.cookie_path = '/'

        write_jwks_uri(op, op_arg, self.folder)

        if op.baseurl.endswith("/"):
            div = ""
        else:
            div = "/"

        op.name = op.baseurl = "{}{}{}/{}".format(op.baseurl, div, oper_id,
                                                  test_id)

        op.logout_verify_url = '{}/{}'.format(op.name, op.logout_path)

        _kj = op.keyjar.export_jwks(True, '')
        op.keyjar.import_jwks(_kj, op.name)

        _tc = test_conf[test_id]
        if not _tc:
            raise UnknownTestID(test_id)

        try:
            _capa = _tc['capabilities']
        except KeyError:
            pass
        else:
            op.capabilities.update(_capa)
            # update jwx
            for _typ in ["signing_alg", "encryption_alg", "encryption_enc"]:
                for item in ["id_token", "userinfo"]:
                    cap_param = '{}_{}_values_supported'.format(item, _typ)
                    try:
                        op.jwx_def[_typ][item] = _capa[cap_param][0]
                    except KeyError:
                        pass

        try:
            op.claims_type = _tc["claims"]
        except KeyError:
            pass

        try:
            op.behavior_type = _tc["behavior"]
            op.server.behavior_type = _tc["behavior"]
        except KeyError:
            pass

        return op
