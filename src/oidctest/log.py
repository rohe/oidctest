import os
import logging
from urllib import unquote
from aatest import exception_trace, Break
from aatest.check import ERROR
from aatest.check import WARNING
from oic.utils.http_util import Response

__author__ = 'roland'

logger = logging.getLogger(__name__)


def with_or_without_slash(path):
    if os.path.isdir(path):
        return path

    if path.endswith("%2F"):
        path = path[:-3]
        if os.path.isdir(path):
            return path
    else:
        path += "%2F"
        if os.path.isdir(path):
            return path

    return None


def get_err_type(session):
    errt = WARNING
    try:
        if session["node"].mti == {"all": "MUST"}:
            errt = ERROR
    except KeyError:
        pass
    return errt


class Log(object):
    def __init__(self):
        pass

    def err_response(self, session, where, err):
        pass

    def sorry_response(self, homepage, err):
        pass

    def dump_log(self, session, test_id):
        pass

    def store_test_info(self, session):
        pass

    def log_fault(self, session, err, where):
        pass

    def display_log(self, root, issuer="", profile="", testid=""):
        pass


class WebLog(Log):
    def __init__(self, profile_info, lookup, page):
        Log.__init__(self)
        self.page = page
        self.profile_info = profile_info
        self.lookup = lookup

    def store_test_info(self, session, profile_info=None):
        _info = {
            "trace": session["conv"].trace,
            "test_output": session["conv"].test_output,
            "index": session["index"],
            "seqlen": len(session["seq_info"]["sequence"]),
            "descr": session["node"].desc
        }

        try:
            _info["node"] = session["seq_info"]["node"]
        except KeyError:
            pass

        if profile_info:
            _info["profile_info"] = profile_info
        else:
            try:
                _info["profile_info"] = self.profile_info(session,
                                                          session["testid"])
            except KeyError:
                pass

        session["test_info"][session["testid"]] = _info

    def _display(self, root, issuer, profile):
        item = []
        if profile:
            path = os.path.join(root, issuer, profile).replace(":", "%3A")
            argv = {"issuer": unquote(issuer), "profile": profile}

            path = with_or_without_slash(path)
            if path is None:
                return Response("No saved logs")

            for _name in os.listdir(path):
                if _name.startswith("."):
                    continue
                fn = os.path.join(path, _name)
                if os.path.isfile(fn):
                    item.append((unquote(_name), os.path.join(profile, _name)))
        else:
            if issuer:
                argv = {'issuer': unquote(issuer), 'profile': ''}
                path = os.path.join(root, issuer).replace(":", "%3A")
            else:
                argv = {'issuer': '', 'profile': ''}
                path = root

            path = with_or_without_slash(path)
            if path is None:
                return Response("No saved logs")

            for _name in os.listdir(path):
                if _name.startswith("."):
                    continue
                fn = os.path.join(path, _name)
                if os.path.isdir(fn):
                    item.append((unquote(_name), os.path.join(path, _name)))

        item.sort()
        argv["logs"] = item
        return Response(mako_template="logs.mako",
                        template_lookup=self.lookup,
                        headers=[])

    def display_log(self, root, issuer="", profile="", test_id=""):
        logger.info(
            "display_log root: '%s' issuer: '%s', profile: '%s' testid: '%s'" % (
                root, issuer, profile, test_id))
        if test_id:
            path = os.path.join(root, issuer, profile, test_id).replace(":",
                                                                        "%3A")
            return self.page["static"](path)
        else:
            if issuer:
                return self._display(root, issuer, profile)
            else:
                return Response("No saved logs")

    def log_fault(self, session, err, where, err_type=0):
        if err_type == 0:
            err_type = get_err_type(session)

        if "node" in session:
            if err:
                if isinstance(err, Break):
                    session["node"].state = WARNING
                else:
                    session["node"].state = err_type
            else:
                session["node"].state = err_type

        if "conv" in session:
            if err:
                if isinstance(err, basestring):
                    pass
                else:
                    session["conv"].trace.error("%s:%s" % (
                        err.__class__.__name__, str(err)))
                session["conv"].test_output.append(
                    {"id": "-", "status": err_type, "message": "%s" % err})
            else:
                session["conv"].test_output.append(
                    {"id": "-", "status": err_type,
                     "message": "Error in %s" % where})

    def err_response(self, session, where, err):
        if err:
            exception_trace(where, err, logger)

        self.log_fault(session, err, where)

        try:
            _tid = session["testid"]
            self.dump_log(session, _tid)
            self.store_test_info(session)
        except KeyError:
            pass

        return self.page["flow_list"](session)

    def sorry_response(self, homepage, err):
        resp = Response(mako_template="sorry.mako",
                        template_lookup=self.lookup,
                        headers=[])
        argv = {"htmlpage": homepage,
                "error": str(err)}
        return resp, argv
