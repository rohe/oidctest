#!/usr/bin/env python3
import inspect
import json
import os
import sys

from otest.aus import check as aus_check
from otest.check import Check
from otest.conf_setup import OP_ORDER
from otest.flow import FlowState
from otest.prof_util import ProfileHandler

from oidctest.op import check as op_check
from oidctest.op import func
from oidctest.op import oper
from oidctest.op.func import factory as func_factory
from oidctest.op.check import factory as check_factory


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
<h1 id="{href}">1.{nr}. {id}</h1>
<p><em>{doc}</em></p>
<p></p>

<table>
    <tbody>
    <tr>
        <td>JSON description</td>
        <td>
            <a href="{url}/{id}.json">{id}</a>
        </td>
    </tr>
    <tr>
        <td>Expected output</td>
        <td>{exp}</td>
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

<p></p>
"""

NOTE = """    <tr>
        <td>Note</td>
        <td>{}</td>
    </tr>
"""


def get_func(name):
    obj = func_factory(name)
    _doc_str = obj.__doc__
    if _doc_str:
        _doc = {'Context': [], "Action": [], "Args": [], "Example": []}
        _dkeys = list(_doc.keys())
        for dline in _doc_str.split('\n'):
            d = dline.strip()
            if not d:
                continue

            section = ""
            for sec_name in _dkeys:
                if sec_name in d:
                    section = sec_name
                    continue

                _doc[section].append(d)
    else:
        _doc = None

    _link = name.replace('-', '_')
    _src_info = inspect.getsourcelines(obj)
    line_nr = _src_info[1]

    return {
        "id": name,
        "link": _link,
        "doc": _doc,
        'line_nr': line_nr,
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
                _doc.append(dline)
        _doc = "\n".join(_doc)
    else:
        _doc = ""

    _link = obj.cid.replace('-', '_')
    line_nr = inspect.getsourcelines(obj)[1]

    try:
        _desc = param_desc.format(obj.doc)
    except AttributeError:
        _desc = ''

    return {
        "id": obj.cid,
        "link": _link,
        "doc": _doc,
        'line_nr': line_nr,
        'para_desc': _desc
    }

def construct_desc(flowdir, testname, return_types, funcs, checks, nr):
    desc = json.loads(open(os.path.join(flowdir, testname + '.json')).read())
    href = testname.replace('-', '_')

    _in_flow_check = {}
    for req in desc['sequence']:
        if isinstance(req, str):
            continue
        else:
            _check = []
            _type = ''
            for _type, _spec in req.items():
                for attr, val in _spec.items():
                    if attr not in funcs:
                        funcs[attr] = get_func(attr)

                    try:
                        _in_flow_check[_type].append(attr)
                    except KeyError:
                        _in_flow_check[_type] = [attr]

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
            "doc": desc['desc'], "ref": _ref, "exp": _exp, "extra": _extra}

    #                     _txt = '<a href="#{}">{}</a>'.format(_lnk, attr)
    #                     _check.append(_txt)
    #         if _check:
    #             _in_flow_check.append("<dt>{}<dt>".format(_type))
    #             _in_flow_check.append('<dd>{}</dd>'.format("<br>\n".join(_check)))
    #
    # if _in_flow_check:
    #     _cond = "<dl>{}</dl>".format(_in_flow_check)
    # else:
    #     _cond = ""


# =================================================================================================

DONE = [
    "OP-IDToken-C-Signature", "OP-IDToken-none", "OP-prompt-none-LoggedIn", "OP-Discovery-JWKs"
]

FLOWDIR = "../test_tool/cp/test_op/flows"


def make_test_desc(flow_dir, done, test_link, start_index=1):
    fl = flows(flow_dir)
    res = {}
    # profile = 'C.T.T.T.s.+'
    # Return_type, webfinger, discovery, registration, sign/enc ,extras
    RT = ['C', 'I', 'IT', 'CI', 'CT', 'CIT']
    for rt in RT:
        profile = '{}.T.T.T'.format(rt)
        tests = fl.matches_profile(profile)
        for t in tests:
            try:
                res[t].append(rt)
            except KeyError:
                res[t] = [rt]

    tt = list(res.keys())
    tt.sort()
    nr = start_index
    test_desc = []

    for t in tt:
        if t in done:
            continue

        test_desc.append(construct_desc(flow_dir, t, res[t], test_link, nr))
        nr += 1

    nr = start_index
    test_toc = []
    for t in tt:
        if t in DONE:
            continue

        test_toc.append('<li>1.{nr}. <a href="#{href}">{id}</a></li>'.format(
            nr=nr, id=t, href=t.replace('-', '_')))
        nr += 1

    return test_toc, test_desc


# ================================================================================================

pattern = """
<h1 id="{link}">3.{nr}. {id}</h1>
<p>{doc}</p>{para_desc}
<p><a href="{url}#L{line_nr}">Link to code</a></p>
"""

param_desc = """
<pre>
Parameter description:<br>
{}
</pre>
"""

toc_2_pattern = """<li>2.{nr}. <a href="#{link}">{id}</a></li>"""
toc_3_pattern = """<li>3.{nr}. <a href="#{link}">{id}</a></li>"""
toc_4_pattern = """<li>4.{nr}. <a href="#{link}">{id}</a></li>"""


def make_check_desc(module_name, url, done, nr=1):
    seen = []
    toc_list = []
    desc_list = []
    test_link = {}
    for name, obj in inspect.getmembers(sys.modules[module_name]):
        if inspect.isclass(obj) and issubclass(obj, Check):
            if obj.cid != 'check' and obj.cid not in done:
                if obj.cid in seen:
                    print("<!-- {} -->".format(obj.cid))
                    continue
                else:
                    seen.append(obj.cid)

                _doc_str = obj.__doc__
                if _doc_str:
                    _doc = []
                    for dline in _doc_str.split('\n'):
                        d = dline.strip()
                        if not d or d[0] == ':':
                            continue
                        else:
                            _doc.append(dline)
                    _doc = "\n".join(_doc)
                else:
                    _doc = ""

                _link = obj.cid.replace('-', '_')
                line_nr = inspect.getsourcelines(obj)[1]

                try:
                    _desc = param_desc.format(obj.doc)
                except AttributeError:
                    _desc = ''

                args = {
                    "id": obj.cid,
                    "link": _link,
                    "doc": _doc,
                    'nr': nr,
                    'url': url,
                    'line_nr': line_nr,
                    'para_desc': _desc
                }
                desc_list.append(pattern.format(**args))
                toc_list.append(toc_2_pattern.format(link=_link, id=obj.cid, nr=nr))
                test_link[obj.cid] = _link
                nr += 1

    return toc_list, desc_list, test_link


def make_func_descr(module_name, file_postfix, nr=1):
    func_desc = {}
    for name, obj in inspect.getmembers(sys.modules[module_name]):
        if inspect.isfunction(obj) and inspect.getsourcefile(obj).endswith(file_postfix):
            _doc_str = obj.__doc__
            if _doc_str:
                _doc = []
                para_desc = []
                example = []
                exp = False
                for dline in _doc_str.split('\n'):
                    d = dline.strip()
                    if not d:
                        continue

                    if exp:
                        example.append(d)
                        continue

                    if ":param" in d:
                        para_desc.append(d)
                    elif "Example" in d:
                        exp = True
                    else:
                        _doc.append(d)

                _doc = "<br>\n".join(_doc)
            else:
                _doc = ""

            _link = name.replace('-', '_')
            _src_info = inspect.getsourcelines(obj)
            line_nr = _src_info[1]

            args = {
                "id": name,
                "link": _link,
                "doc": _doc,
                'line_nr': line_nr,
                'para_desc': ''
            }
            func_desc[name] = args
            nr += 1

    return func_desc


if __name__ == "__main__":
    # https://github.com/rohe/oidctest/blob/cedb05b4c64597aaa4c277a6a34a2f8dafbd69ca/src/oidctest
    # /op/check.py#L76
    REPO = "https://github.com/rohe"
    OTEST_BLOB = "c72d8cefc19472a2967ecb00272c469a65b11"
    OIDCTEST_BLOB = "cedb05b4c64597aaa4c277a6a34a2f8dafbd69ca"

    GITHUB_OTEST_URL = "{}/otest/blob/{}/src/otest/check.py".format(REPO, OTEST_BLOB)
    GITHUB_OIDCTEST_URL = "{}/oidctest/blob/{}/src/oidctest/op/check.py".format(REPO, OIDCTEST_BLOB)
    GITHUB_OIDCTEST_FUNC_URL = "{}/oidctest/blob/{}/src/oidctest/op/func.py".format(REPO,
                                                                                    OIDCTEST_BLOB)

    # otest/aus/check
    # _toc2, _desc2, test_link_aus = make_check_desc(aus_check.__name__, GITHUB_OTEST_URL, [])
    # # oidctest
    # _toc21, _desc21, test_link_op = make_check_desc(op_check.__name__, GITHUB_OIDCTEST_URL, [])
    #
    # # oidctest/op/func.py
    # _toc_f, _desc_f, test_link_f = make_func_descr(func.__name__, 'oidctest/op/func.py')

    # The flow specs
    checks = {}
    funcs = {}
    _toc1, _desc1 = make_test_desc(FLOWDIR, [], checks, funcs)

    # Print document

    _head = open('head.html').read()
    print(_head)
    print("""    <li>1. <a href="#section.1">Tests</a></li>
    <ul>
""")
    for t in _toc1:
        print(t)
    print("</ul>")
    print("""    <li>2. <a href="#section.2">Assertions</a></li>
    <ul>

    """)
    for t in _toc2:
        print(t)
    for t in _toc21:
        print(t)
    print("</ul>")
    print("""    <li>3. <a href="#section.3">In-flow functions</a></li>
    <ul>

    """)
    for t in _toc_f:
        print(t)
    print("</ul></ul>")
    print('<h1 id="section.1">1. Tests</h1>')
    for d in _desc1:
        print(d)
    print("<p></p>")
    print('<h1 id="section.2">2. Assertions</h1>')
    for d in _desc2:
        print(d)
    for d in _desc21:
        print(d)
    print('<h1 id="section.3">3. In-flow functions</h1>')
    for d in _desc_f:
        print(d)
    print("</body></html>")
