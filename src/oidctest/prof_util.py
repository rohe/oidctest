from aatest import prof_util
from aatest.time_util import in_a_while

__author__ = 'roland'


RESPONSE = 0
WEBFINGER = 1
DISCOVER = 2
REGISTER = 3
CRYPTO = 4
EXTRAS = 5

def from_code(code):
    # Of the form <typ>.<disc>.<reg>.*['+'/'n'/'s'/'se']
    # for example:
    # C.T.T..  - code response_type, dynamic discovery & registration
    # CIT.T.F.. - response_type=["code","id_token","token"], dynamic discovery
    #           and static client registration

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


def map_prof(a, b):
    if a == b:
        return True

    # basic, implicit, hybrid
    if b[RESPONSE] != "":
        if a[RESPONSE] not in b[RESPONSE].split(','):
            return False

    # dynamic discovery & registry
    for n in [WEBFINGER, DISCOVER, REGISTER]:
        if b[n] != "":
            if a[n] != b[n]:
                return False

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

RT = {"C": "code", "I": "id_token", "T": "token"}
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
            except TypeError:
                iss = ""

            profile = self.to_profile("dict")

            if test_id is None:
                try:
                    test_id = self.session["testid"]
                except KeyError:
                    return {}

            return {"Issuer": iss, "Profile": profile,
                    "Test ID": test_id,
                    "Test description": self.session["node"].desc,
                    "Timestamp": in_a_while()}

        return {}

    def to_profile(self, representation="list"):
        p = self.session["profile"].split(".")
        prof = [
            "+".join([RT[x] for x in p[0]]),
            "%s" % OC[p[1]],
            "%s" % REG[p[2]]]

        try:
            prof.append("%s" % "+".join([CR[x] for x in p[3]]))
        except KeyError:
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
