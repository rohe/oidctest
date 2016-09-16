# from oic.oic.provider import Provider
import json

from oic import rndstr
from oic.oic import OIDCONF_PATTERN
from oic.utils.sdb import SessionDB
from oic.utils.webfinger import WF_URL
from oidctest import UnknownTestID
from oidctest.rp.provider import Provider

__author__ = 'roland'

OIDC_PATTERN = OIDCONF_PATTERN[3:]
WEB_FINGER = WF_URL[11:]
NP = 6


def extract_mode(path):
    # path = <oper_id>/<test_id>/<sign_alg>/<encrypt>/<behaviortype/<claims>/
    #          <endpoint>

    if path == "":
        return {}, ""

    if path[0] == '/':
        path = path[1:]

    if path == WEB_FINGER:
        return None, path

    part = path.split("/", NP)

    mod = {'oper_id': part[0], "test_id": part[1].lower()}

    plen = len(part)
    if plen == 4 and path.endswith(OIDC_PATTERN):
        return mod, OIDC_PATTERN

    if plen >= 6:
        if part[5] != "_":
            try:
                mod["claims"] = part[5].split(",")
            except ValueError:
                pass
    if plen >= 5:
        if part[4] != "_":
            try:
                mod["behavior"] = part[4].split(",")
            except ValueError:
                pass

    if plen >= 4:
        if part[3] != "_":
            try:
                _enc_alg, _enc_enc = part[3].split(":")
            except ValueError:
                pass
            else:
                mod.update({"enc_alg": _enc_alg, "enc_enc": _enc_enc})

    if plen >= 3:
        if part[2] != "_":
            mod["sign_alg"] = part[2]

    if plen == NP or plen == 2:
        return mod, ""
    else:
        return mod, part[-1]


def mode2path(mode):
    # oper_id/test_id/<sig-alg>/<enc-alg>/<behavior>/<userinfo>[/<endpoint>]
    if mode is None:
        mode = {}

    noop = "_/"
    try:
        path = '{}/{}/'.format(mode['oper_id'], mode["test_id"])
    except KeyError:
        path = ""

    try:
        path += "{}/".format(mode["sign_alg"])
    except KeyError:
        path += noop

    try:
        path += "{}}:{}/".format(mode["enc_alg"], mode["enc_enc"])
    except KeyError:
        path += noop

    try:
        path += "{}/".format(",".join(mode["behavior"]))
    except KeyError:
        path += noop

    try:
        path += ",".join(mode["claims"])
    except KeyError:
        path += "normal"

    return path


def setup_op(mode, com_args, op_arg, trace, test_conf):
    op = Provider(sdb=SessionDB(com_args["baseurl"]), **com_args)
    op.trace = trace

    for _authn in com_args["authn_broker"]:
        _authn.srv = op

    for key, val in list(op_arg.items()):
        setattr(op, key, val)

    _name = "jwks_{}.json".format(rndstr())
    filename = "./static/{}".format(_name)
    with open(filename, "w") as f:
        f.write(json.dumps(op_arg["jwks"]))
    f.close()

    op.jwks_uri = "{}static/{}".format(op_arg["baseurl"], _name)
    op.jwks_name = filename

    if op.baseurl.endswith("/"):
        div = ""
    else:
        div = "/"

    op.name = op.baseurl = "{}{}{}/{}".format(op.baseurl, div, mode['oper_id'],
                                              mode['test_id'])

    try:
        _tc = test_conf[mode['test_id']]
    except KeyError:
        raise UnknownTestID(mode['test_id'])

    for _typ in ["signing_alg", "encryption_alg", "encryption_enc"]:
        try:
            _alg = _tc[_typ]
        except (TypeError, KeyError):
            for obj in ["id_token", "request_object", "userinfo"]:
                op.jwx_def[_typ][obj] = ''
        else:
            for obj in ["id_token", "request_object", "userinfo"]:
                op.jwx_def[_typ][obj] = _alg

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
