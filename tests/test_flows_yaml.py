from otest.parse_cnf import parse_yaml_conf
from oidctest.op import oper
from oidctest.op import func

__author__ = 'roland'


def test_flows():
    cls_factories = {'': oper.factory}
    func_factory = func.factory
    x = parse_yaml_conf('oidc_flows.yaml', cls_factories, func_factory)
    assert len(x['Flows']) == 103


def test_cflows():
    cls_factories = {'': oper.factory}
    func_factory = func.factory
    x = parse_yaml_conf('oidc_cflows.yaml', cls_factories, func_factory)
    assert len(x['Flows']) == 55
