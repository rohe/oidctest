# -*- coding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 10
_modified_time = 1431431614.195723
_enable_loop = True
_template_filename = 'htdocs/opresult_repost.mako'
_template_uri = 'opresult_repost.mako'
_source_encoding = 'utf-8'
_exports = []


def render_body(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        __M_writer = context.writer()
        __M_writer('<!DOCTYPE html>\n\n<html>\n<head>\n    <title>OpenID Certification RP Test</title>\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n    <link href="static/opresultqr.css" rel="stylesheet" media="screen">\n\n    <!-- Bootstrap -->\n    <link href="static/bootstrap/css/bootstrap.min.css" rel="stylesheet" media="screen">\n\n    <!-- HTML5 shim and Respond.js IE8 support of HTML5 elements and media queries -->\n    <!--[if lt IE 9]>\n    <script src="../../assets/js/html5shiv.js"></script>\n    <script src="../../assets/js/respond.min.js"></script>\n    <![endif]-->\n\n    <script src="/static/jquery.min.1.9.1.js"></script>\n</head>\n<body onload="document.forms[0].submit()">\n<div class="container">\n    <div class="jumbotron">\n        <form class="repost" action="authz_post" method="post">\n            <input type="hidden" name="fragment" id="frag" value="x"/>\n            <script type="text/javascript">\n                if(window.location.hash) {\n                    var hash = window.location.hash.substring(1); //Puts hash in variable, and removes the # character\n                    document.getElementById("frag").value = hash;\n                }\n            </script>\n        </form>\n    </div>\n</div>\n</body>\n</html>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


"""
__M_BEGIN_METADATA
{"source_encoding": "utf-8", "line_map": {"26": 20, "20": 1, "15": 0}, "uri": "opresult_repost.mako", "filename": "htdocs/opresult_repost.mako"}
__M_END_METADATA
"""
