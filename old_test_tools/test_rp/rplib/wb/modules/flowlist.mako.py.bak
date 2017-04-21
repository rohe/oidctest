# -*- coding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 10
_modified_time = 1431336176.202667
_enable_loop = True
_template_filename = 'htdocs/flowlist.mako'
_template_uri = 'flowlist.mako'
_source_encoding = 'utf-8'
_exports = []



def op_choice(base, node, done):
    """
    Creates a dropdown list of test flows
    """
    #colordict = {
    #    "OK":'<img src="static/green.png" alt="Green">',
    #    "WARNING":'<img src="static/yellow.png" alt="Yellow">',
    #    "ERROR":'<img src="static/red.png" alt="Red">',
    #    "CRITICAL":'<img src="static/red.png" alt="Red">'
    #}

    keys = node.keys()
    keys.sort()
    element = "<ul>"
    for key in keys:
        element += "<li><a href='%s%s'>%s</a> (%s) " % (
            base, key, node[key]["desc"], key)
        if key in done:
            element += '<img src="static/pictures/Check_mark.png" alt="Check">'
    return element


def render_body(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        base = context.get('base', UNDEFINED)
        done = context.get('done', UNDEFINED)
        flows = context.get('flows', UNDEFINED)
        __M_writer = context.writer()
        __M_writer(u'\n\n<!DOCTYPE html>\n\n<html>\n  <head>\n    <title>OpenID Certification RP Test</title>\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n    <!-- Bootstrap -->\n    <link href="static/bootstrap/css/bootstrap.min.css" rel="stylesheet" media="screen">\n      <link href="static/style.css" rel="stylesheet" media="all">\n\n    <!-- HTML5 shim and Respond.js IE8 support of HTML5 elements and media queries -->\n    <!--[if lt IE 9]>\n      <script src="../../assets/js/html5shiv.js"></script>\n      <script src="../../assets/js/respond.min.js"></script>\n    <![endif]-->\n  </head>\n  <body>\n    <div class="container">\n     <!-- Main component for a primary marketing message or call to action -->\n      <div class="jumbotron">\n        <h1>RPTEST</h1>\n          <h3>Chose the next test flow you want to run from this list: </h3>\n            ')
        __M_writer(unicode(op_choice(base, flows, done)))
        __M_writer(u'\n      </div>\n\n    </div> <!-- /container -->\n    <!-- jQuery (necessary for Bootstrap\'s JavaScript plugins) -->\n    <script src="/static/jquery.min.1.9.1.js"></script>\n    <!-- Include all compiled plugins (below), or include individual files as needed -->\n    <script src="/static/bootstrap/js/bootstrap.min.js"></script>\n\n  </body>\n</html>')
        return ''
    finally:
        context.caller_stack._pop_frame()


"""
__M_BEGIN_METADATA
{"source_encoding": "utf-8", "line_map": {"38": 0, "46": 22, "47": 46, "48": 46, "54": 48, "15": 1}, "uri": "flowlist.mako", "filename": "htdocs/flowlist.mako"}
__M_END_METADATA
"""
