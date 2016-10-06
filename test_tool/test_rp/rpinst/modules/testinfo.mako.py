# -*- coding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
STOP_RENDERING = runtime.STOP_RENDERING
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 10
_modified_time = 1475745370.065018
_enable_loop = True
_template_filename = 'htdocs/testinfo.mako'
_template_uri = 'testinfo.mako'
_source_encoding = 'utf-8'
_exports = []




def print_result(events):
  """
    Displays the test information
    """
  elements = []
  for event in events:
      elements.append('{}<br>'.format(event))
  return "\n".join(elements)



def print_dict(obj):
  elements = ['<table>']
  for k,v in obj.items():
    elements.append('<tr><td>{}</td><td>{}</td></tr>'.format(k,v))
  elements.append('</table')
  return "\n".join(elements)


def render_body(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        events = context.get('events', UNDEFINED)
        result = context.get('result', UNDEFINED)
        trace = context.get('trace', UNDEFINED)
        base = context.get('base', UNDEFINED)
        profile = context.get('profile', UNDEFINED)
        __M_writer = context.writer()

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
        __M_writer('\n\n')
        __M_writer('\n\n')
        __M_writer('\n\n\n<!DOCTYPE html>\n<html>\n<head>\n  <title>HEART OAuth2 RP Tests</title>\n  <meta name="viewport" content="width=device-width, initial-scale=1.0">\n  ')
        __M_writer(str(boot_strap(base)))
        __M_writer('\n  <!-- HTML5 shim and Respond.js IE8 support of HTML5 elements and media queries -->\n  <!--[if lt IE 9]>\n  <script src="../../assets/js/html5shiv.js"></script>\n  <script src="../../assets/js/respond.min.js"></script>\n  <![endif]-->\n  <style>\n    h3 {\n      background-color: lightblue;\n    }\n\n    h4 {\n      background-color: lightcyan;\n    }\n\n    @media (max-width: 768px) {\n      .jumbotron {\n        border-radius: 10px;\n        margin-left: 4%;\n        margin-right: 4%;\n      }\n    }\n\n    @media (min-width: 768px) and (max-width: 1600px) {\n      .jumbotron {\n        border-radius: 10px;\n        margin-left: 10%;\n        margin-right: 10%;\n      }\n    }\n\n    @media (min-width: 1600px) {\n      .jumbotron {\n        border-radius: 10px;\n        margin-left: 20%;\n        margin-right: 20%;\n      }\n    }\n  </style>\n</head>\n<body>\n<!-- Main component for a primary marketing message or call to action -->\n<div class="jumbotron">\n  ')
        __M_writer(str(print_dict(profile)))
        __M_writer('\n  <hr>\n')
        for item in trace:
            __M_writer('    ')
            __M_writer(str(item))
            __M_writer('<br>\n')
        __M_writer('  <hr>\n  ')
        __M_writer(str(events))
        __M_writer('\n  <hr>\n  ')
        __M_writer(str(result))
        __M_writer('\n</div>\n')
        __M_writer(str(postfix(base)))
        __M_writer('\n</body>\n</html>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


"""
__M_BEGIN_METADATA
{"line_map": {"70": 20, "71": 22, "101": 114, "16": 34, "85": 32, "86": 44, "87": 53, "88": 61, "89": 61, "90": 104, "91": 104, "92": 106, "93": 107, "94": 107, "95": 107, "96": 109, "97": 110, "98": 110, "99": 112, "100": 112, "37": 0, "102": 114, "28": 46, "108": 102, "47": 1}, "uri": "testinfo.mako", "filename": "htdocs/testinfo.mako", "source_encoding": "utf-8"}
__M_END_METADATA
"""
