#!/usr/bin/env python3
import inspect
import json
import os
from json import JSONDecodeError

from otest.check import CriticalError as check_critical_error
from otest.check import Error as check_error
from otest.check import ExpectedError as check_expected_error
from otest.check import Warnings as check_warning
from otest.conf_setup import OP_ORDER
from otest.flow import FlowState
from otest.prof_util import ProfileHandler

from oidctest.op import func
from oidctest.op import oper
from oidctest.op.check import factory as check_factory
from oidctest.op.func import factory as func_factory


def flows(flowdir, display_order=None):
    cls_factories = {'': oper.factory}
    func_factory = func.factory

    if display_order is None:
        display_order = OP_ORDER

    return FlowState(flowdir, profile_handler=ProfileHandler,
                     cls_factories=cls_factories,
                     func_factory=func_factory,
                     display_order=display_order)


RT_MAP = {
    'C': 'Code',
    'CI': 'Code IDtoken',
    'CT': 'Code Token',
    'I': 'IDToken',
    'IT': 'IDToken Token',
    'CIT': 'Code IDToken Token'
}

ass_pattern = '<a href="#{href}">{id}</a>'

GITHUB_URL = "https://github.com/rohe/oidctest/blob/master/test_tool/cp/test_op/flows"

desc_pattern = """
<h1 id="{href}">2.{nr}. {id}</h1>
<p><em>{doc}</em></p>
<p></p>

<table>
    <tbody>
    <tr>
        <td>JSON description</td>
        <td>{json}</td>
    </tr>
    <tr>
        <td>In-flow checks</td>
        <td>{cond}</td>
    </tr>
    <tr>
        <td>Assertions</td>
        <td>{ass}</td>
    </tr>
    <tr>
        <td>Group</td>
        <td>{group}</td>
    </tr>
    <tr>
        <td>Return Types</td>
        <td>{rtypes}</td>
    </tr>
    <tr>
        <td>Link to specification</td>
        <td>{ref}</td>
    </tr>
    {extra}    
    </tbody>
</table>

<p>
Java Implementation Status: Status TDB
</p>
<p>
Link to Java code: Link TBD
</p>
<p></p>
"""

NOTE = """    <tr>
        <td>Note</td>
        <td>{}</td>
    </tr>
"""


def get_func(name):
    obj = func_factory(name)
    if obj is None:
        print(name)
    _doc_str = obj.__doc__
    if _doc_str:
        _doc = {'Context:': [], "Action:": [], "Args:": [], "Example:": []}
        _dkeys = list(_doc.keys())
        section = ""
        for dline in _doc_str.split('\n'):
            d = dline.strip()
            if not d:
                continue

            for sec_name in _dkeys:
                if d.startswith(sec_name):
                    section = sec_name
                    break

            if section == "Example:":
                _doc[section].append(dline)
            else:
                _doc[section].append(d)
    else:
        _doc = None

    _link = name.replace('-', '_')

    return {
        "id": name,
        "link": _link,
        "doc": _doc,
        'line_nr': inspect.getsourcelines(obj)[1],
        'src_file': inspect.getsourcefile(obj)
    }


def get_check(name):
    obj = check_factory(name)

    _doc_str = obj.__doc__
    if _doc_str:
        _doc = []
        for dline in _doc_str.split('\n'):
            d = dline.strip()
            if not d or d[0] == ':':
                continue
            else:
                _doc.append(d)
        _doc = "\n".join(_doc)
    else:
        _doc = ""

    _link = obj.cid.replace('-', '_')
    _mro = inspect.getmro(obj)
    if check_error in _mro:
        _outcome = "Error"
    elif check_warning in _mro:
        _outcome = "Warning"
    elif check_expected_error in _mro:
        _outcome = "Error"
    elif check_critical_error in _mro:
        _outcome = "Error"
    else:
        _outcome = "Undefined"

    try:
        _desc = obj.doc
    except AttributeError:
        _desc = ''

    return {
        "id": obj.cid,
        "link": _link,
        "doc": _doc,
        'line_nr': inspect.getsourcelines(obj)[1],
        'src_file': inspect.getsourcefile(obj),
        'parameter_desc': _desc,
        "outcome": _outcome
    }


def construct_desc(flowdir, testname, return_types, checks, funcs):
    desc = json.loads(open(os.path.join(flowdir, testname + '.json')).read())
    href = testname.replace('-', '_')

    _in_flow_check = {}
    for operation in desc['sequence']:
        if isinstance(operation, str):
            continue
        else:
            _check = []
            _oper = ''
            for _oper, _spec in operation.items():
                for attr, val in _spec.items():
                    if attr not in funcs:
                        funcs[attr] = get_func(attr)
                        funcs[attr]['usage'] = [href + ':' + _oper]
                    else:
                        funcs[attr]['usage'].append(href + ':' + _oper)

                    try:
                        _in_flow_check[_oper].append(attr)
                    except KeyError:
                        _in_flow_check[_oper] = [attr]

    try:
        ass = list(desc['assert'].keys())
    except KeyError:
        ass = ""
    else:
        for a in ass:
            if a not in checks:
                checks[a] = get_check(a)

    rtypes = "<br>\n".join([RT_MAP[r] for r in return_types])

    try:
        _ref = []
        for _url in desc['reference']:
            _ref.append('<a href="{}">{}</a>'.format(_url, _url))
        _ref = "<br>\n".join(_ref)
    except KeyError:
        _ref = ''

    try:
        _exp = desc['result']
    except KeyError:
        _exp = "Success"

    try:
        _note = desc["note"]
    except KeyError:
        _extra = ""
    else:
        _extra = NOTE.format(_note)

    return {"id": testname, "href": href, "group": desc['group'], "ass": ass, "rtypes": rtypes,
            "doc": desc['desc'], "ref": _ref, "exp": _exp, "extra": _extra,
            "in_flow_check": _in_flow_check}


# =================================================================================================

DONE = [
    "OP-IDToken-C-Signature", "OP-IDToken-none", "OP-prompt-none-LoggedIn", "OP-Discovery-JWKs"
]

FLOWDIR = "../test_tool/cp/test_op/flows"


def get_tests_by_profile(flow_dir, profile, response_types=None):
    fl = flows(flow_dir)
    res = {}

    if response_types is None:
        # Do all response types
        response_types = ['C', 'I', 'IT', 'CI', 'CT', 'CIT']

    for rt in response_types:
        _prof = '{}.{}'.format(rt, profile)
        tests = fl.matches_profile(_prof)
        for t in tests:
            try:
                res[t].append(rt)
            except KeyError:
                res[t] = [rt]
    return res


def all_tests(flow_dir):
    tests = {}

    for f in os.listdir(flow_dir):
        fname = os.path.join(flow_dir, f)
        if os.path.isfile(fname):
            try:
                flow = json.loads(open(fname).read())
            except JSONDecodeError:
                print("JSON decode failed on:", fname)
                raise
            try:
                resp_type = flow['usage']['return_type']
            except KeyError:
                resp_type = ['C', 'I', 'IT', 'CI', 'CT', 'CIT']
            tests[f.split('.')[0]] = resp_type
    return tests


def make_test_desc(flow_dir, done, checks, funcs, profile=""):
    if profile:
        res = get_tests_by_profile(flow_dir, profile)
    else:  # get all
        res = all_tests(flow_dir)

    tt = list(res.keys())
    tt.sort()
    test_desc = []

    for t in tt:
        if t in done:
            continue

        test_desc.append(construct_desc(flow_dir, t, res[t], checks, funcs))

    return test_desc


# ================================================================================================

def make_test_toc(desc):
    _toc = []
    nr = 1
    for d in desc:
        _toc.append('<li>2.{nr}. <a href="#{href}">{id}</a></li>'.format(
            nr=nr, id=d['id'], href=d['href']))
        nr += 1

    return _toc


def print_in_flow(desc, funcs):
    if not desc['in_flow_check']:
        return ''

    _cond = ['<dl>']
    for req, ops in desc['in_flow_check'].items():
        _cond.append("<dt>{}<dt>".format(req))
        _list = []
        for op in ops:
            func_desc = funcs[op]
            _list.append('<a href="#{}">{}</a>'.format(func_desc['link'], func_desc['id']))
        _cond.append('<dd>{}</dd>'.format("<br>\n".join(_list)))

    _cond.append('</dl>')
    return "\n".join(_cond)


def print_assertions(desc, checks):
    _l = ['<a href="#{}">{}</a>'.format(checks[a]['link'], checks[a]['id']) for a in desc['ass']]
    return "<br>\n".join(_l)


def do_url(desc, lnk_pattern):
    for pat, url in lnk_pattern.items():
        if desc["src_file"].endswith(pat):
            return url
    raise ValueError()


def do_test_desc(desc, checks, funcs, nr):
    _in_flow = print_in_flow(desc, funcs)
    desc['ass'] = print_assertions(desc, checks)
    json_url = '<a href="{url}/{id}.json">{id}</a>'.format(url=GITHUB_URL, **desc)
    return desc_pattern.format(cond=_in_flow, nr=nr, json=json_url, **desc)


pattern = """
<h1 id="{link}">3.{nr}. {id}</h1>
<p>{doc}</p>{para_desc}
<p>Possible outcome: {outcome}<p>
<p><a href="{url}#L{line_nr}">Link to code</a></p>
<p>
Java Implementation Status: Status TDB
</p>
<p>
Link to Java code: Link TBD
</p>
"""
param_desc = """
<pre>
Parameter description:<br>
{}
</pre>
"""

toc_2_pattern = """<li>3.{nr}. <a href="#{link}">{id}</a></li>"""
toc_3_pattern = """<li>4.{nr}. <a href="#{link}">{id}</a></li>"""


def do_check_desc(check, nr):
    if check["parameter_desc"]:
        p_desc = param_desc.format(check['parameter_desc'])
    else:
        p_desc = ""
    _url = do_url(check, URL)
    return pattern.format(nr=nr, url=_url, para_desc=p_desc, **check)


def do_check_toc(check, nr):
    return toc_2_pattern.format(nr=nr, **check)


func_pattern = """
<h1 id="{link}">4.{nr}. {id}</h1>
{docs}
<p></p>
{usages}
<p></p>
<p><a href="{url}#L{line_nr}">Link to code</a></p>
<p>
Java Implementation Status: Status TDB
</p>
<p>
Link to Java code: Link TBD
</p>
"""


def do_func_desc(func, nr, nr_of_tests):
    url = do_url(func, URL)
    if func['doc']:
        _strlist = []
        for key, values in func['doc'].items():
            if len(values) > 1:
                _strlist.append("<dt>{}</dt>".format(key[:-1]))
                if key == "Example:":
                    _strlist.append("<dd><pre>{}</pre></dd>".format("\n".join(values[1:])))
                else:
                    _strlist.append("<dd>{}</dd>".format("\n".join(values[1:])))
        docs = "<dl>{}</dl>".format("\n".join(_strlist))
    else:
        docs = ""

    if len(func['usage']) == nr_of_tests:
        _usage = "<dl><dt>Test usage:</dt><dd>ALL</dd></dl>"
    else:
        _usage = ["<dl><dt>Test usage:</dt>"]
        _usage.append('<dd>{}</dd>'.format("<br>\n".join(func['usage'])))
        _usage.append("</dl>")
        _usage = "\n".join(_usage)

    return func_pattern.format(nr=nr, url=url, docs=docs, usages=_usage, **func)


def do_func_toc(func, nr):
    return toc_3_pattern.format(nr=nr, **func)


# ================================================================================================

# git log | head -n 1
# Will give you the commit ID
#

toc_4_pattern = """<li>4.{nr}. <a href="#{link}">{id}</a></li>"""

if __name__ == "__main__":
    REPO = "https://github.com/rohe"
    OTEST_BLOB = "610e12f573736b80edf12047ae98908d5f2245a6"
    OIDCTEST_BLOB = "c2c666bbc0a59f26cfa677436ac7cc1ccd1a2b0a"

    URL = {
        "otest/check.py": "{}/otest/blob/{}/src/otest/check.py".format(REPO, OTEST_BLOB),
        "otest/aus/check.py": "{}/otest/blob/{}/src/otest/aus/check.py".format(REPO, OTEST_BLOB),
        "otest/func.py": "{}/otest/blob/{}/src/otest/func.py".format(REPO, OTEST_BLOB),
        "oidctest/op/check.py": "{}/oidctest/blob/{}/src/oidctest/op/check.py".format(REPO,
                                                                                      OIDCTEST_BLOB),
        "oidctest/op/func.py": "{}/oidctest/blob/{}/src/oidctest/op/func.py".format(REPO,
                                                                                    OIDCTEST_BLOB)}

    # The flow specs
    checks = {}
    funcs = {}
    # _test_desc = make_test_desc(FLOWDIR, [], checks, funcs, profile="T.T.T")
    _test_desc = make_test_desc(FLOWDIR, [], checks, funcs)
    _nr_of_tests = len(_test_desc)

    # Print document

    _head = open('head.html').read()
    print(_head)

    print("""    <li><a href="#test_description">1. Test description file</a></li>
    <ul>
""")
    _flow_toc = open("flow_toc.html").read()
    print(_flow_toc)
    print("</ul>")

    print("""    <li>2. <a href="#section.2">Tests</a></li>
    <ul>
""")
    for t in make_test_toc(_test_desc):
        print(t)
    print("</ul>")
    print("""    <li>3. <a href="#section.3">Assertions</a></li>
    <ul>

    """)
    nr = 1
    ckeys = list(checks.keys())
    ckeys.sort()
    for c in ckeys:
        print(do_check_toc(checks[c], nr))
        nr += 1
    print("</ul>")
    print("""    <li>4. <a href="#section.4">In-flow functions</a></li>
    <ul>

    """)
    fkeys = list(funcs.keys())
    fkeys.sort()
    nr = 1
    for f in fkeys:
        print(do_func_toc(funcs[f], nr))
        nr += 1
    print("</ul></ul>")

    # Description of the JSON format that is used in the test description files.
    _fdesc = open('flow_description.html').read()
    print(_fdesc)

    print('<h1 id="section.2">2. Tests</h1>')
    nr = 1
    for d in _test_desc:
        print(do_test_desc(d, checks, funcs, nr))
        nr += 1
    print("<p></p>")
    print('<h1 id="section.3">3. Assertions</h1>')
    nr = 1
    for c in ckeys:
        print(do_check_desc(checks[c], nr))
        nr += 1
    print('<h1 id="section.4">4. In-flow functions</h1>')
    nr = 1
    for d in fkeys:
        print(do_func_desc(funcs[d], nr, _nr_of_tests))
        nr += 1
    print("</body></html>")
