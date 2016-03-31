import logging

from aatest import exception_trace
from aatest.io import IO

__author__ = 'roland'

logger = logging.getLogger(__name__)


class ClIO(IO):
    def flow_list(self):
        pass

    def err_response(self, where, err):
        if err:
            exception_trace(where, err, logger)

        try:
            _tid = self.session["testid"]
            self.print_info(_tid)
        except KeyError:
            pass

