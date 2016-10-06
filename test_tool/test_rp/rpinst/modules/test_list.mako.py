# -*- coding:utf-8 -*-
from mako import runtime, filters, cache

UNDEFINED = runtime.UNDEFINED
STOP_RENDERING = runtime.STOP_RENDERING
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 10
_modified_time = 1457377793.167707
_enable_loop = True
_template_filename = 'htdocs/test_list.mako'
_template_uri = 'test_list.mako'
_source_encoding = 'utf-8'
_exports = []


def op_choice(key_list, test_spec, test_info):
    """
    Creates a list of tests
    """

    element = "<ul>"

    for key in key_list:
        _info = test_spec[key]
        element += "<li><a href='rp?id=%s'>%s</a>(%s) " % (
        key, _info['descr'], key)

        if key in test_info:
            element += "<a href='%stest_info/%s'><img " \
                       "src='static/info32.png'></a>" % (
                base, key)

    element += "</select>"
    return element


def render_body(context, **pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        key_list = context.get('key_list', UNDEFINED)
        test_spec = context.get('test_spec', UNDEFINED)
        test_info = context.get('test_info', UNDEFINED)
        __M_writer = context.writer()
        __M_writer(
            '\n\n\n<!DOCTYPE html>\n<html>\n<head>\n    <title>HEART OAuth2 '
            'RP Tests</title>\n    <meta name="viewport" '
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
            'class="jumbotron">\n        <h1>HEART OAuth2 RP Tests</h1>\n     '
            '   <h3>Chose the next test flow you want to run from this list: '
            '</h3>\n        ')
        __M_writer(str(op_choice(key_list, test_spec, test_info)))
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
{"uri": "test_list.mako", "source_encoding": "utf-8", "line_map": {"16": 1,
"53": 47, "37": 0, "45": 20, "46": 66, "47": 66}, "filename": "htdocs/test_list.mako"}
__M_END_METADATA
"""
