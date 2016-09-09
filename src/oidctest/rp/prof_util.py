import os

from otest.time_util import in_a_while

__author__ = 'roland'


class ProfileHandler(object):
    def __init__(self, session):
        self.session = session

    def to_profile(self, representation="list"):
        return self.session.profile

    def get_profile_info(self, test_id=None):
        try:
            _conv = self.session["conv"]
        except KeyError:
            pass
        else:
            profile = self.to_profile("dict")

            if test_id is None:
                try:
                    test_id = self.session["testid"]
                except KeyError:
                    return {}

            return {"Profile": profile,
                    "Test ID": test_id,
                    "Test description": self.session["node"].desc,
                    "Timestamp": in_a_while()}

        return {}

    def log_path(self, sid, test_id=None):
        _conv = self.session["conv"]

        path = os.path.join("log", sid)

        prof = ".".join(self.to_profile())

        if not os.path.isdir("{}/{}".format(path, prof)):
            os.makedirs("{}/{}".format(path, prof))

        if test_id is None:
            test_id = self.session["testid"]

        return "{}/{}/{}".format(path, prof, test_id)