# -*- coding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
STOP_RENDERING = runtime.STOP_RENDERING
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 10
_modified_time = 1476347801.345651
_enable_loop = True
_template_filename = 'heart_mako/htdocs/testinfo.mako'
_template_uri = 'testinfo.mako'
_source_encoding = 'utf-8'
_exports = []




from otest.check import STATUSCODE
from otest import summation

def do_assertions(out):
  return summation.condition(out, True)



def trace_output(trace):
    """

    """
    element = ["<h3>Trace output</h3>", "<pre><code>"]
    for item in trace:
        element.append("%s" % item)
    element.append("</code></pre>")
    return "\n".join(element)


def render_body(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        trace = context.get('trace', UNDEFINED)
        events = context.get('events', UNDEFINED)
        base = context.get('base', UNDEFINED)
        result = context.get('result', UNDEFINED)
        profile = context.get('profile', UNDEFINED)
        __M_writer = context.writer()
        __M_writer('\n\n')
        __M_writer('\n\n')

        def profile_output(pinfo):
            element = []
            for key, val in pinfo.items():
                element.append("<em>%s:</em> %s<br>" % (key,val))
        
            return "\n".join(element)
        
        
        __M_locals_builtin_stored = __M_locals_builtin()
        __M_locals.update(__M_dict_builtin([(__M_key, __M_locals_builtin_stored[__M_key]) for __M_key in ['profile_output'] if __M_key in __M_locals_builtin_stored]))
        __M_writer('\n\n')

        LINK_INFO = [
        {
            'href':"{}/static/bootstrap/css/bootstrap.min.css",
            'rel':"stylesheet",
            'media':"screen"},
        {
            'href':"{}/static/style.css",
            'rel':"stylesheet",
            'media':"all"}
        ]
        
        def boot_strap(base):
            line = []
            for d in LINK_INFO:
                _href = d['href'].format(base)
                line.append('<link href={href} rel={rel} media={media}>'.format(
                     href=_href,rel=d['rel'],media=d['media']))
            return "\n".join(line)
        
        
        __M_locals_builtin_stored = __M_locals_builtin()
        __M_locals.update(__M_dict_builtin([(__M_key, __M_locals_builtin_stored[__M_key]) for __M_key in ['boot_strap','LINK_INFO'] if __M_key in __M_locals_builtin_stored]))
        __M_writer('\n\n')

        SCRIPT_INFO = ["{}/static/jquery.min.1.9.1.js", "{}/static/bootstrap/js/bootstrap.min.js"]
        
        def postfix(base):
            line = []
            for d in SCRIPT_INFO:
                _src = d.format(base)
                line.append('<script src={}></script>'.format(_src))
            return "\n".join(line)
        
        
        
        __M_locals_builtin_stored = __M_locals_builtin()
        __M_locals.update(__M_dict_builtin([(__M_key, __M_locals_builtin_stored[__M_key]) for __M_key in ['postfix','SCRIPT_INFO'] if __M_key in __M_locals_builtin_stored]))
        __M_writer('\n\n<!DOCTYPE html>\n\n<html>\n  <head>\n    <title>HEART OIDC OP Test</title>\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n    <!-- Bootstrap -->\n    ')
        __M_writer(str(boot_strap(base)))
        __M_writer('\n    <!-- HTML5 shim and Respond.js IE8 support of HTML5 elements and media queries -->\n    <!--[if lt IE 9]>\n      <script src="../../assets/js/html5shiv.js"></script>\n      <script src="../../assets/js/respond.min.js"></script>\n    <![endif]-->\n  </head>\n  <body>\n\n    <div class="container">\n     <!-- Main component for a primary marketing message or call to action -->\n        <h2>Test info</h2>\n        ')
        __M_writer(str(profile_output(profile)))
        __M_writer('\n        <hr>\n        ')
        __M_writer(str(do_assertions(events)))
        __M_writer('\n        <hr>\n        ')
        __M_writer(str(trace_output(trace)))
        __M_writer('\n        <hr>\n        <h3>Result</h3>')
        __M_writer(str(result))
        __M_writer('\n    </div> <!-- /container -->\n    ')
        __M_writer(str(postfix(base)))
        __M_writer('\n  </body>\n</html>')
        return ''
    finally:
        context.caller_stack._pop_frame()


"""
__M_BEGIN_METADATA
{"line_map": {"16": 1, "84": 50, "85": 52, "25": 10, "111": 91, "101": 71, "99": 62, "100": 71, "37": 0, "102": 83, "103": 83, "104": 85, "105": 85, "106": 87, "107": 87, "108": 89, "109": 89, "110": 91, "47": 8, "48": 20, "49": 22, "117": 111, "60": 29, "61": 31}, "source_encoding": "utf-8", "filename": "heart_mako/htdocs/testinfo.mako", "uri": "testinfo.mako"}
__M_END_METADATA
"""
