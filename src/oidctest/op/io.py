import logging

from aatest import exception_trace
from aatest.check import ERROR
from aatest.check import OK
from aatest.check import WARNING
from aatest.check import INCOMPLETE
from aatest.io import IO
from aatest.summation import eval_state

from oidctest.utils import get_profile_info

__author__ = 'roland'

logger = logging.getLogger(__name__)

TEST_RESULTS = {OK: "OK", ERROR: "ERROR", WARNING: "WARNING",
                INCOMPLETE: "INCOMPLETE"}

SIGN = {OK: "+", WARNING: "!", ERROR: "-", INCOMPLETE: "?"}


class ClIO(IO):
    def flow_list(self):
        pass

    def result(self):
        _conv = self.session["conv"]
        info = {
            "events": _conv.events,
            "trace": _conv.trace
        }
        _state = eval_state(info)
        print("{} {}".format(SIGN[_state], self.session["node"].name))

    def err_response(self, where, err):
        if err:
            exception_trace(where, err, logger)

        try:
            _tid = self.session["testid"]
            self.print_info(_tid)
        except KeyError:
            pass

    def store_test_info(self, profile_info=None):
        _conv = self.session["conv"]
        _info = {
            "trace": _conv.trace,
            "events": _conv.events,
            "index": self.session["index"],
            "seqlen": len(self.session["sequence"]),
            "descr": self.session["node"].desc
        }

        try:
            _info["node"] = self.session["node"]
        except KeyError:
            pass

        if profile_info:
            _info["profile_info"] = profile_info
        else:
            try:
                _info["profile_info"] = get_profile_info(self.session,
                                                         self.session["testid"])
            except KeyError:
                pass

        self.session["test_info"][self.session["testid"]] = _info

