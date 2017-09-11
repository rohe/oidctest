from fedoidc.entity import FederationEntity
from oic.utils.keyio import build_keyjar
from oic.utils.keyio import key_summary
from oic.utils.sdb import create_session_db
from otest.conversation import Conversation

from oidctest import UnknownTestID
from oidctest.cp.op_handler import OPHandler
from oidctest.cp.op_handler import init_keyjar
from oidctest.cp.op_handler import write_jwks_uri


class FedOPHandler(OPHandler):
    def __init__(self, provider_cls, op_args, com_args, test_conf, folder,
                 fo_bundle, **kwargs):
        OPHandler.__init__(self, provider_cls, op_args, com_args, test_conf,
                           folder)
        self.key_defs = kwargs['key_defs']
        self.signers = kwargs['signers']
        self.fo_bundle = fo_bundle

    def get(self, oper_id, test_id, events, endpoint):
        # addr = get_client_address(environ)
        key = path = '{}/{}'.format(oper_id, test_id)

        try:
            _op = self.op[key]
            _op.events = events
            if endpoint == '.well-known/openid-configuration':
                init_keyjar(_op, self.op_args['keyjar'], self.com_args)
                write_jwks_uri(_op, self.op_args, self.folder)
        except KeyError:
            _op = self.setup_op(oper_id, test_id, self.com_args,
                                self.op_args, self.test_conf, events)
            _op.conv = Conversation(test_id, _op, None)
            _op.orig_keys = key_summary(_op.keyjar, '').split(', ')
            self.op[key] = _op

        return _op, path, key

    def setup_op(self, oper_id, test_id, com_args, op_arg, test_conf, events):
        _tc = test_conf[test_id]
        if not _tc:
            raise UnknownTestID(test_id)

        _sdb = create_session_db(com_args["baseurl"], 'automover', '430X', {})
        op = self.provider_cls(sdb=_sdb, **com_args)
        op.events = events
        op.oper_id = oper_id
        op.test_id = test_id
        try:
            op.ms_conf = _tc['metadata_statements']
        except KeyError:
            op.msu_conf = _tc['metadata_statement_uris']

        for _authn in com_args["authn_broker"]:
            _authn.srv = op

        for key, val in list(op_arg.items()):
            if key == 'keyjar':
                init_keyjar(op, val, com_args)
            else:
                setattr(op, key, val)

        write_jwks_uri(op, op_arg, self.folder)

        if op.baseurl.endswith("/"):
            div = ""
        else:
            div = "/"

        op.name = op.baseurl = "{}{}{}/{}".format(op.baseurl, div, oper_id,
                                                  test_id)
        op.signers = self.signers
        _kj = build_keyjar(self.key_defs)[1]

        op.federation_entity = FederationEntity(None, keyjar=_kj, iss=op.name,
                                                signer=None,
                                                fo_bundle=self.fo_bundle)
        op.federation_entity.httpcli = op

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
