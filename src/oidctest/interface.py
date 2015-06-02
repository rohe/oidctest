import logging
import os
from urlparse import unquote
from aatest import exception_trace

from oic.utils.http_util import Response, NotFound
from oic.utils.time_util import in_a_while

from aatest.check import ERROR
from aatest.check import OK
from aatest.check import WARNING
from aatest.check import INCOMPLETE
from aatest.summation import represent_result
from aatest.summation import test_output
from aatest.summation import trace_output
from aatest.summation import create_tar_archive

from oidctest.utils import get_profile_info, log_path, with_or_without_slash, \
    get_test_info

__author__ = 'roland'

logger = logging.getLogger(__name__)

TEST_RESULTS = {OK: "OK", ERROR: "ERROR", WARNING: "WARNING",
                INCOMPLETE: "INCOMPLETE"}


class Interface(object):
    def __init__(self, lookup, conf, test_flows, cache, test_profile,
                 profiles, test_class, check_factory, environ=None,
                 start_response=None):
        self.lookup = lookup
        self.conf = conf
        self.test_flows = test_flows
        self.cache = cache
        self.test_profile = test_profile
        self.profiles = profiles
        self.test_class = test_class
        self.check_factory = check_factory
        self.environ = environ
        self.start_response = start_response

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
                _info["profile_info"] = get_profile_info(session,
                                                         session["testid"])
            except KeyError:
                pass

        session["test_info"][session["testid"]] = _info

    def flow_list(self, session):
        resp = Response(mako_template="flowlist.mako",
                        template_lookup=self.lookup,
                        headers=[])

        try:
            _tid = session["testid"]
        except KeyError:
            _tid = None

        self.dump_log(session, _tid)

        argv = {
            "flows": session["tests"],
            "profile": session["profile"],
            "test_info": session["test_info"].keys(),
            "base": self.conf.BASE,
            "headlines": self.test_flows.DESC,
            "testresults": TEST_RESULTS
        }

        return resp(self.environ, self.start_response, **argv)

    def dump_log(self, session, test_id=None):
        try:
            _conv = session["conv"]
        except KeyError:
            pass
        else:
            _pi = get_profile_info(session, test_id)
            if _pi:
                _tid = _pi["Test ID"]
                path = log_path(session, _tid)
                if not path:
                    return

                sline = 60*"="
                output = ["%s: %s" % (k, _pi[k]) for k in ["Issuer", "Profile",
                                                           "Test ID"]]
                output.append("Timestamp: %s" % in_a_while())
                output.extend(["", sline, ""])
                output.extend(trace_output(_conv.trace))
                output.extend(["", sline, ""])
                output.extend(test_output(_conv.test_output))
                output.extend(["", sline, ""])
                # and lastly the result
                self.store_test_info(session, _pi)
                _info = session["test_info"][_tid]
                output.append("RESULT: %s" % represent_result(_info, _tid))
                output.append("")

                f = open(path, "w")
                txt = "\n".join(output)

                try:
                    f.write(txt)
                except UnicodeEncodeError:
                    f.write(txt.encode("utf8"))

                f.close()
                pp = path.split("/")
                create_tar_archive(pp[1], pp[2])
                return path

    def profile_edit(self, session):
        resp = Response(mako_template="profile.mako",
                        template_lookup=self.lookup,
                        headers=[])
        argv = {"profile": session["profile"]}
        return resp(self.environ, self.start_response, **argv)

    def test_info(self, testid, session):
        resp = Response(mako_template="testinfo.mako",
                        template_lookup=self.lookup,
                        headers=[])

        info = get_test_info(session, testid)

        argv = {
            "profile": info["profile_info"],
            "trace": info["trace"],
            "output": info["test_output"],
            "result": represent_result(info, testid).replace("\n", "<br>\n")
        }

        return resp(self.environ, self.start_response, **argv)

    def not_found(self):
        """Called if no URL matches."""
        resp = NotFound()
        return resp(self.environ, self.start_response)

    def static(self, path):
        logger.info("[static]sending: %s" % (path,))

        try:
            text = open(path).read()
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

    def _display(self, root, issuer, profile):
        item = []
        if profile:
            path = os.path.join(root, issuer, profile).replace(":", "%3A")
            argv = {"issuer": unquote(issuer), "profile": profile}

            path = with_or_without_slash(path)
            if path is None:
                resp = Response("No saved logs")
                return resp(self.environ, self.start_response)

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
                resp = Response("No saved logs")
                return resp(self.environ, self.start_response)

            for _name in os.listdir(path):
                if _name.startswith("."):
                    continue
                fn = os.path.join(path, _name)
                if os.path.isdir(fn):
                    item.append((unquote(_name), os.path.join(path, _name)))

        resp = Response(mako_template="logs.mako",
                        template_lookup=self.lookup,
                        headers=[])

        item.sort()
        argv["logs"] = item
        return resp(self.environ, self.start_response, **argv)

    def display_log(self, root, issuer="", profile="", testid=""):
        logger.info(
            "display_log root: '%s' issuer: '%s', profile: '%s' testid: '%s'" % (
                root, issuer, profile, testid))
        if testid:
            path = os.path.join(root, issuer, profile, testid).replace(":",
                                                                       "%3A")
            return self.static(path)
        else:
            if issuer:
                return self._display(root, issuer, profile)
            else:
                resp = Response("No saved logs")
                return resp(self.environ, self.start_response)

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

        return self.flow_list(session)

    def sorry_response(self, homepage, err):
        resp = Response(mako_template="sorry.mako",
                        template_lookup=self.lookup,
                        headers=[])
        argv = {"htmlpage": homepage,
                "error": str(err)}
        return resp(self.environ, self.start_response, **argv)
