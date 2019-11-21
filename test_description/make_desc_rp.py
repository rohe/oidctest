#!/usr/bin/env python3
import json
import os
import re

LINE_PATTERN = [
    'if "([^"]+)" in self.behavior_type:',
    "if '([^']+)' in self.behavior_type:",
]


def read_provider(source_file, modifier):
    nr = 1
    flag = False
    _name = ""
    fp = open(source_file, 'r')

    for line in fp.readlines():
        line = line.strip()
        if flag:
            if line.startswith('#'):
                modifier[_name]["doc"].append(line[2:])
                continue
            else:
                flag = False

        for p in LINE_PATTERN:
            m = re.search(p, line)
            if m:
                _name = m.group(1)
                try:
                    modifier[_name]['line'].append(nr)
                except KeyError:
                    try:
                        modifier[_name]['line'] = [nr]
                    except KeyError:
                        continue
                flag = True
                if "doc" not in modifier[_name]:
                    modifier[_name]["doc"] = []

        nr += 1
    return modifier


BASEDIR = "../test_tool/cp/test_rplib/rp/flows"


def read_tests():
    modifier = {}
    test = {}
    for f in os.listdir(BASEDIR):
        fname = os.path.join(BASEDIR, f)
        _id = f[:-5]
        if os.path.isfile(fname):
            desc = json.loads(open(fname).read())
            test[_id] = desc
            try:
                _behav = desc['behavior']
            except KeyError:
                continue

            for b in _behav:
                try:
                    modifier[b]['usage'].append(_id)
                except KeyError:
                    modifier[b] = {"usage": [_id]}
    return test, modifier


def do_dlist(subject, items):
    res = ["<dl><dt>" + subject + "<dt>"]
    for item in items:
        res.append("<dd>" + item + "</dd>")
    res.append("</dl>")
    return "\n".join(res)


def do_list(items):
    res = ["<ul>"]
    for item in items:
        res.append("<li>" + item + "</li>")
    res.append("</ul>")
    return "\n".join(res)


PATTERN = """
<h2 id="{link}">{sec}.{nr}. {id}</h2>
<p>{doc}</p>
<p>{links}
<p>{usage}
<p>
Java Implementation Status: Status TDB
</p>
<p>
Link to Java code: Link TBD
</p>
"""


def do_modifier(name, spec, nr, base_url, sec):
    args = {
        'link': name,
        'id': name,
        "nr": nr,
        'doc': "<br>\n".join(spec["doc"]),
        'links': do_dlist( "Links to code:",
            ['<a href="{url}#L{line_nr}">code</a>'.format(url=base_url, line_nr=l) for l in
                spec["line"]]),
        "usage": do_dlist("Used in tests:", spec["usage"]),
        "sec": sec
    }

    return PATTERN.format(**args)


DESC_PATTERN = """
<h2 id="{href}">{sec}.{nr}. {id}</h2>
<p><em>{doc}</em></p>
<p></p>

<table>
    <tbody>
    <tr>
        <td>Description</td>
        <td>{descr}</td>
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
        <td>Modifiers</td>
        <td>{modifiers}</td>
    </tr>
    <tr>
        <td>Expected result</td>
        <td>{expected}</td>
    </tr>
    <tr>
        <td>Link to specification</td>
        <td>{spec}</td>
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


def do_test(name, spec, nr, sec):
    kwargs = {
        "id": name,
        "nr": nr,
        "href": name.replace('-', '_'),
        "descr": spec["detailed_description"],
        "rtypes":
            do_list(spec["capabilities"]["response_types_supported"]),
        "group": spec["group"],
        "expected": spec["expected_result"],
        "extra": "",
        "sec": sec
    }
    try:
        kwargs["spec"] = do_list(spec["reference"])
    except KeyError:
        kwargs["spec"] = "MISSING"

    try:
        kwargs["modifiers"] = do_list(
            ['<a href="#{}">{}</a>'.format(b,b) for b in spec["behavior"]])
    except KeyError:
        kwargs["modifiers"] = "NONE"

    try:
        kwargs["doc"] = spec["short_description"]
    except KeyError:
        kwargs["doc"] = spec["detailed_description"]

    return DESC_PATTERN.format(**kwargs)


def do_groups(tests):
    groups = set()
    for key, spec in tests.items():
        groups.add(spec['group'])
    return list(groups)


FILE = "../src/oidctest/rp/provider.py"

REPO = "https://github.com/rohe"
OIDCTEST_BLOB = "a306ff8ccd02da456192b595cf48ab5dcfd3d15a"

CODE_URL = "{}/oidctest/blob/{}/src/oidctest/rp/provider.py".format(REPO, OIDCTEST_BLOB)

TOC_PATTERN = """<li>{section}.{nr}. <a href="#{link}">{id}</a></li>"""

if __name__ == "__main__":
    MOD_SEC = 4
    TEST_SEC = 3
    test, modifier = read_tests()
    modifier = read_provider(FILE, modifier)

    mod_keys = list(modifier.keys())
    mod_keys.sort()

    test_keys = list(test.keys())
    test_keys.sort()

    print_args = {
        "modifiers": [],
        "modifiers_toc": [],
        "test_desc_toc": [],
        "test_desc": []
    }

    nr = 1
    _mods = []
    for key in mod_keys:
        _mods.append(do_modifier(key, modifier[key], nr, CODE_URL, MOD_SEC))
        nr += 1
    print_args["modifiers"] = "\n".join(_mods)

    nr = 1
    _m_toc = []
    for key in mod_keys:
        _m_toc.append(TOC_PATTERN.format(section=MOD_SEC, nr=nr, link=key, id=key))
        nr += 1
    print_args["modifiers_toc"] = "\n".join(_m_toc)

    nr = 1
    _item = []
    for key in test_keys:
        _item.append(do_test(key, test[key], nr, TEST_SEC))
        nr += 1
    print_args["test_desc"] = "\n".join(_item)

    _toc = []
    nr = 1
    for key in test_keys:
        _toc.append(TOC_PATTERN.format(section=TEST_SEC, nr=nr, link=key, id=key))
        nr += 1
    print_args["test_desc_toc"] = "\n".join(_toc)

    _grp = do_groups(test)
    _grp.sort()
    print_args["groups"] = do_list(_grp)

    _head = open("rp_head.html").read()
    print(_head)
    _body = open("rp_body.html").read()
    print(_body.format(**print_args))
