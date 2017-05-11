from otest import prof_util
from otest.prof_util import map_prof
from otest.prof_util import repr_profile
from otest.result import get_issuer
from otest.time_util import in_a_while

__author__ = 'roland'


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
                    "Test description": self.session.test_flows[test_id][
                        'desc'],
                    "Timestamp": in_a_while()}

        return {}

    def to_profile(self, representation="list", with_webfinger=True):
        """

        :param representation:
        :param with_webfinger:
        :return:
        """
        try:
            _prof = self.session["profile"].split(".")
        except KeyError:
            _prof = self.session.profile.split(".")

        return repr_profile(_prof, representation, with_webfinger)



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
