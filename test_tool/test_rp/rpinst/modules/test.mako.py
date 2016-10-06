# -*- coding:utf-8 -*-
from mako import runtime, filters, cache

UNDEFINED = runtime.UNDEFINED
STOP_RENDERING = runtime.STOP_RENDERING
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 10
_modified_time = 1462266322.836814
_enable_loop = True
_template_filename = 'htdocs/test.mako'
_template_uri = 'test.mako'
_source_encoding = 'utf-8'
_exports = []


def op_choice(base, nodes, test_info, headlines):
    """
    Creates a list of test flows
    """
    # colordict = {
    #    "OK":'<img src="static/green.png" alt="Green">',
    #    "WARNING":'<img src="static/yellow.png" alt="Yellow">',
    #    "ERROR":'<img src="static/red.png" alt="Red">',
    #    "CRITICAL":'<img src="static/red.png" alt="Red">'
    # }
    _grp = "_"
    color = ['<img src="static/black.png" alt="Black">',
             '<img src="static/green.png" alt="Green">',
             '<img src="static/yellow.png" alt="Yellow">',
             '<img src="static/red.png" alt="Red">',
             '<img src="static/qmark.jpg" alt="QuestionMark">',
             '<img src="static/greybutton" alt="Grey">',
             ]
    element = "<ul>"

    for node in nodes:
        # 4 or more parts
        typ, grp, spec = node.name.split("-", 2)
        if not grp == _grp:
            _grp = grp
            element += "<hr size=2><h3 id='%s'>%s</h3>" % (
            _grp, headlines[_grp])
        element += "<li><a href='%s/%s'>%s</a>%s (%s) " % (base,
                                                           node.name,
                                                           color[node.state],
                                                           node.desc, node.name)

        if node.rmc:
            element += '<img src="static/delete-icon.png">'
        if node.experr:
            element += '<img src="static/beware.png">'
        if node.name in test_info:
            element += "<a href='%s/test_info/%s'><img " \
                       "src='static/info32.png'></a>" % (
                base, node.name)
            # if node.mti == "MUST":
            #    element += '<img src="static/must.jpeg">'

    element += "</select>"
    return element


ICONS = [
    ('<img src="static/black.png" alt="Black">', "The test has not been run"),
    ('<img src="static/green.png" alt="Green">', "Success"),
    ('<img src="static/yellow.png" alt="Yellow">',
     "Warning, something was not as expected"),
    ('<img src="static/red.png" alt="Red">', "Failed"),
    ('<img src="static/qmark.jpg" alt="QuestionMark">',
     "The test flow wasn't completed. This may have been expected or not"),
    ('<img src="static/info32.png">',
     "Signals the fact that there are trace information available for the "
     "test"),
]


def legends():
    element = "<table border='1' id='legends'>"
    for icon, txt in ICONS:
        element += "<tr><td>%s</td><td>%s</td></tr>" % (icon, txt)
    element += '</table>'
    return element


def render_body(context, **pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        test_info = context.get('test_info', UNDEFINED)
        headlines = context.get('headlines', UNDEFINED)
        len = context.get('len', UNDEFINED)
        base = context.get('base', UNDEFINED)
        dict = context.get('dict', UNDEFINED)
        tests = context.get('tests', UNDEFINED)
        range = context.get('range', UNDEFINED)
        s = context.get('s', UNDEFINED)
        __M_writer = context.writer()
        __M_writer('\n\n')
        __M_writer('\n\n')

        def results(tests, testresults):
            res = dict([(s, 0) for s in testresults.keys()])
            res[0] = 0

            for test in tests:
                res[test.state] += 1

            el = []
            for i in range(1, len(res)):
                el.append("<p>%s: %d</p>" % (testresults[i], res[i]))
            el.append("<p>Not run: %d</p>" % res[0])

            return "\n".join(el)

        __M_locals_builtin_stored = __M_locals_builtin()
        __M_locals.update(__M_dict_builtin(
            [(__M_key, __M_locals_builtin_stored[__M_key]) for __M_key in
             ['results'] if __M_key in __M_locals_builtin_stored]))
        __M_writer(
            '\n\n<!DOCTYPE html>\n<html>\n<head>\n    <title>OIDC RP '
            'Tests</title>\n    <meta name="viewport" '
            'content="width=device-width, initial-scale=1.0">\n    <!-- '
            'Bootstrap -->\n    <link '
            'href="static/bootstrap/css/bootstrap.min.css" rel="stylesheet" '
            'media="screen">\n    <link href="static/style.css" '
            'rel="stylesheet" media="all">\n\n    <!-- HTML5 shim and '
            'Respond.js IE8 support of HTML5 elements and media queries -->\n '
            '   <!--[if lt IE 9]>\n    <script '
            'src="../../assets/js/html5shiv.js"></script>\n    <script '
            'src="../../assets/js/respond.min.js"></script>\n    <!['
            'endif]-->\n    <style>\n        @media (max-width: 768px) {\n    '
            '        .jumbotron {\n                border-radius: 10px;\n     '
            '           margin-left: 4%;\n                margin-right: 4%;\n '
            '           }\n        }\n        @media (min-width: 768px) and ('
            'max-width: 1600px){\n            .jumbotron {\n                '
            'border-radius: 10px;\n                margin-left: 10%;\n        '
            '        margin-right: 10%;\n            }\n        }\n        '
            '@media (min-width: 1600px){\n            .jumbotron {\n          '
            '      border-radius: 10px;\n                margin-left: 20%;\n  '
            '              margin-right: 20%;\n            }\n        }\n    '
            '</style>\n</head>\n<body>\n    <!-- Main component for a primary '
            'marketing message or call to action -->\n    <div '
            'class="jumbotron">\n        <h1>OIDC RP Tests</h1>\n        '
            '<em>Explanations of legends at <a href="#legends">end of '
            'page</a></em>\n        <hr class="separator">\n        <h3>Run '
            '<a href="')
        __M_writer(str(base))
        __M_writer(
            '/all">all</a> or chose the next test flow you want to run from '
            'this list:\n        </h3>\n        ')
        __M_writer(str(op_choice(base, tests, test_info, headlines)))
        __M_writer(
            '\n        <hr class="separator">\n        <h3>Legends</h3>\n     '
            '   ')
        __M_writer(str(legends()))
        __M_writer(
            '\n    </div>\n    <!-- jQuery (necessary for Bootstrap\'s '
            'JavaScript plugins) -->\n    <script '
            'src="/static/jquery.min.1.9.1.js"></script>\n    <!-- Include '
            'all compiled plugins (below), or include individual files as '
            'needed -->\n    <script '
            'src="/static/bootstrap/js/bootstrap.min.js"></script>\n\n</body'
            '>\n</html>')
        return ''
    finally:
        context.caller_stack._pop_frame()


"""
__M_BEGIN_METADATA
{"filename": "htdocs/test.mako", "source_encoding": "utf-8", "uri": "test.mako", "line_map": {"96": 44, "97": 66, "98": 68, "128": 122, "16": 1, "83": 0, "116": 82, "117": 128, "118": 128, "119": 130, "120": 130, "121": 133, "122": 133, "61": 46}}
__M_END_METADATA
"""
