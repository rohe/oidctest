from otest import prof_util
from otest.result import get_issuer
from otest.time_util import in_a_while

__author__ = 'roland'

RESPONSE = 0
WEBFINGER = 1
DISCOVER = 2
REGISTER = 3
CRYPTO = 4
EXTRAS = 5


def from_code(code):
    # Of the form <typ>.<webf>.<disc>.<reg>.*['+'/'n'/'s'/'se']
    # for example:
    # C.T.T.T..  - code response_type, webfinger & dynamic discovery &
    #                                   registration
    # CIT.F.T.F.. - response_type=["code","id_token","token"],
    #               No webfinger support,
    #               does dynamic discovery
    #               and static client registration

    p = code.split('.')

    _prof = {"profile": p[RESPONSE],
             "webfinger": (p[WEBFINGER] == 'T'),
             "discover": (p[DISCOVER] == 'T'),
             "register": (p[REGISTER] == 'T'),
             "extra": False,
             "sub": None}

    if len(p) > REGISTER:
        if '+' in p[CRYPTO]:
            _prof["extra"] = True
        if 'n' in p[CRYPTO]:
            _prof["sub"] = "none"
        elif 's' in p[CRYPTO] and 'e' in p[CRYPTO]:
            _prof["sub"] = "sign and encrypt"
        elif 's' in p[CRYPTO]:
            _prof["sub"] = "sign"

    return _prof


def to_code(pdict):
    code = pdict["profile"]

    for key in ["webfinger", "discover", "register"]:
        if pdict[key]:
            code += ".T"
        else:
            code += ".F"

    try:
        if pdict["extra"]:
            code += ".+"
    except KeyError:
        if pdict["sub"]:
            code += ".." + pdict["sub"]
    else:
        if pdict["sub"]:
            code += "." + pdict["sub"]

    return "".join(code)


def _cmp_prof(a, b):
    """

    :param a: list of strings
    :param b: list of strings
    :return: True/False if a maps to b
    """
    # basic, implicit, hybrid
    if b[RESPONSE] != "":
        if a[RESPONSE] not in b[RESPONSE].split(','):
            return False

    try:
        # dynamic discovery & registry
        for n in [WEBFINGER, DISCOVER, REGISTER]:
            if b[n] != "":
                if a[n] != b[n]:
                    return False
    except IndexError:
        print("Too short a:{}, b:{}".format(a, b))
        raise

    if len(a) > CRYPTO:
        if len(b) > CRYPTO:
            if b[CRYPTO] != '':
                if not set(a[CRYPTO]).issuperset(set(b[CRYPTO])):
                    return False

    if len(b) == EXTRAS:
        if len(a) == EXTRAS:
            if a[EXTRAS] != b[EXTRAS]:
                return False
        elif len(a) < EXTRAS:
            return False

    return True


def map_prof(a, b):
    if a == b:
        return True

    if isinstance(b, list):
        return _cmp_prof(a, b)
    elif '.' in b:
        b = b.split('.')
        if '.' in a:
            a = a.split('.')
        return _cmp_prof(a, b)
    else:
        if b == '*':
            return True
        else:
            bl = b.split(',')
            if isinstance(a, list):
                if a[0] in bl:
                    return True
                else:
                    return False
            elif a in bl:
                return True
            else:
                return False


def flows(code, ordered_list, flows_):
    res = []
    p = code.split('.')

    for key in ordered_list:
        sp = flows_[key]["profile"].split('.')

        if map_prof(p, sp):
            res.append(key)

    return res


def _update(dic1, dic2):
    for key in ["request_args", "kw", "req_tests", "resp_tests"]:
        if key not in dic1:
            try:
                dic1[key] = {}
                for _k, _v in list(dic2[key].items()):
                    dic1[key][_k] = _v
            except KeyError:
                pass
        elif key not in dic2:
            pass
        else:
            for k, v in list(dic2[key].items()):
                if k not in dic1[key]:
                    dic1[key][k] = dic2[key][k]

    return dic1


def extras(flow_set, profile_map):
    _all = list(flow_set.keys())
    for prof in ["Basic", "Implicit", "Hybrid"]:
        for _flow in profile_map[prof]["flows"]:
            if _flow in _all:
                _all.remove(_flow)

        for mode in ["Discover", "Register"]:
            for _flow in profile_map[mode]["flows"]:
                if _flow in _all:
                    _all.remove(_flow)
            try:
                for _flow in profile_map[mode]["flow"][prof]:
                    if _flow in _all:
                        _all.remove(_flow)
            except KeyError:
                pass

    _all.sort()
    return _all


RT = {"C": "code", "I": "id_token", "T": "token", "CT": "code token",
      'CI': 'code id_token', 'IT': 'id_token token',
      'CIT': 'code id_token token'}
OC = {"T": "config", "F": "no-config"}
REG = {"T": "dynamic", "F": "static"}
CR = {"n": "none", "s": "sign", "e": "encrypt"}
EX = {"+": "extras"}
ATTR = ["response_type", "openid-configuration", "registration", "crypto",
        "extras"]


class ProfileHandler(prof_util.ProfileHandler):
    def get_profile_info(self, test_id=None):
        try:
            _conv = self.session["conv"]
        except KeyError:
            pass
        else:
            try:
                iss = _conv.entity.provider_info["issuer"]
            except (TypeError, KeyError):
                iss = get_issuer(_conv)

            profile = self.to_profile("dict")

            if test_id is None:
                try:
                    test_id = self.session["testid"]
                except KeyError:
                    return {}

            return {"Issuer": iss, "Profile": profile,
                    "Test ID": test_id,
                    "Test description": self.session.test_flows[test_id]['desc'],
                    "Timestamp": in_a_while()}

        return {}

    def to_profile(self, representation="list"):
        p = self.session["profile"].split(".")
        prof = ["+".join([RT[x] for x in p[0]])]
        try:
            prof.append("%s" % OC[p[1]])
        except IndexError:
            pass
        else:
            try:
                prof.append("%s" % REG[p[2]])
            except IndexError:
                pass

        try:
            prof.append("%s" % "+".join([CR[x] for x in p[3]]))
        except (KeyError, IndexError):
            pass
        else:
            try:
                prof.append("%s" % EX[p[4]])
            except (KeyError, IndexError):
                pass

        if representation == "list":
            return prof
        elif representation == "dict":
            ret = {}
            for r in range(0, len(prof)):
                ret[ATTR[r]] = prof[r]

            if "extras" in ret:
                ret["extras"] = True
            return ret


class SimpleProfileHandler(ProfileHandler):
    @staticmethod
    def webfinger(profile):
        return True

    @staticmethod
    def discover(profile):
        return True

    @staticmethod
    def register(profile):
        return True


def make_list(flows, profile, **kw_args):
    f_names = list(flows.keys())
    f_names.sort()
    flow_names = []
    for k in kw_args["order"]:
        k += '-'
        l = [z for z in f_names if z.startswith(k)]
        flow_names.extend(l)

    res = []
    sprofile = profile.split(".")
    for tid in flow_names:
        _flow = flows[tid]

        if map_prof(sprofile, _flow["profile"].split(".")):
            res.append(tid)

    return res
