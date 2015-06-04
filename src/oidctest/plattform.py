from oidctest.session import SessionHandler

__author__ = 'roland'

class PlattForm(object):
    def __init__(self, interface, **kwargs):
        self.interface = interface
        self.sh = SessionHandler(**kwargs)

    def run_sequence(self, **kwargs):
        pass