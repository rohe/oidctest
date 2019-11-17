import importlib
import os

from oidctest.prof_util import ProfileHandler
from otest.conf_setup import OP_ORDER
from otest.flow import FlowState

from oidctest.op import func
from oidctest.op import oper
from oidctest.op import profiles

from oidctest.session import SessionHandler

__author__ = 'roland'

BASEDIR = os.path.abspath(os.path.dirname(__file__))


_flowdir = os.path.join(BASEDIR, 'flows')

cls_factories = {'': oper.factory}
func_factory = func.factory

display_order = OP_ORDER

flow_state = FlowState(_flowdir, profile_handler=ProfileHandler,
                       cls_factories=cls_factories,
                       func_factory=func_factory,
                       display_order=display_order)


def _eq(l1, l2):
    return set(l1) == set(l2)


def test_session_init():
    sh = SessionHandler(profiles, "C.T.T.T", flow_state, oper,
                        tool_conf={'profile': 'C.T.T.T'})
    sh.session_init()
    assert len(sh['tests']) == 54
    assert len(list(flow_state.keys())) > len(sh['tests'])


def test_session_setup():
    sh = SessionHandler(profiles, "C.T.T.T", flow_state, oper,
                        tool_conf={'profile': 'C.T.T.T'})
    sh.session_init()
    sh.session_setup(path="OP-claims-sub")
    assert sh['testid'] == "OP-claims-sub"
    assert len(sh['sequence']) == 10
    assert sh['index'] == 0
    assert sh['flow']['group'] == 'claims Request Parameter'
