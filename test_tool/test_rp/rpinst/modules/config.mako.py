# -*- coding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
STOP_RENDERING = runtime.STOP_RENDERING
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 10
_modified_time = 1475745255.607879
_enable_loop = True
_template_filename = 'htdocs/config.mako'
_template_uri = 'config.mako'
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


def render_body(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        params = context.get('params', UNDEFINED)
        start_page = context.get('start_page', UNDEFINED)
        profiles = context.get('profiles', UNDEFINED)
        issuer = context.get('issuer', UNDEFINED)
        base = context.get('base', UNDEFINED)
        __M_writer = context.writer()
        __M_writer('\n')

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

        def form_action(base):
            return '<form action="{}/list" method="post">'.format(base)
        
        
        __M_locals_builtin_stored = __M_locals_builtin()
        __M_locals.update(__M_dict_builtin([(__M_key, __M_locals_builtin_stored[__M_key]) for __M_key in ['form_action'] if __M_key in __M_locals_builtin_stored]))
        __M_writer('\n\n\n<!DOCTYPE html>\n<html>\n<head>\n  <title>HEART OAuth2 RP Tests</title>\n  <meta name="viewport" content="width=device-width, initial-scale=1.0">\n  <!-- Bootstrap -->\n  ')
        __M_writer(str(boot_strap(base)))
        __M_writer('\n  <!-- HTML5 shim and Respond.js IE8 support of HTML5 elements and media queries -->\n  <!--[if lt IE 9]>\n  <script src="../../assets/js/html5shiv.js"></script>\n  <script src="../../assets/js/respond.min.js"></script>\n  <![endif]-->\n  <style>\n    h3 {\n      background-color: lightblue;\n    }\n\n    h4 {\n      background-color: lightcyan;\n    }\n\n    @media (max-width: 768px) {\n      .jumbotron {\n        border-radius: 10px;\n        margin-left: 4%;\n        margin-right: 4%;\n      }\n    }\n\n    @media (min-width: 768px) and (max-width: 1600px) {\n      .jumbotron {\n        border-radius: 10px;\n        margin-left: 10%;\n        margin-right: 10%;\n      }\n    }\n\n    @media (min-width: 1600px) {\n      .jumbotron {\n        border-radius: 10px;\n        margin-left: 20%;\n        margin-right: 20%;\n      }\n    }\n  </style>\n</head>\n<body>\n<!-- Main component for a primary marketing message or call to action -->\n<div class="jumbotron">\n  ')
        __M_writer(str(form_action(base)))
        __M_writer('\n    <b>Issuer:</b> ')
        __M_writer(str(issuer))
        __M_writer('\n    <p>\n      Service provider start page:<br>\n      <input type="text" name="start_page" value="')
        __M_writer(str(start_page))
        __M_writer('" size="60"><br>\n    </p>\n    <p>\n      If the relying party can be told to contact a specific Authorization\n      Server it is ursually done using query parameters to the initial\n      service all. This is where you can enter the parameter/-s.<br>\n      If you need to enter the issuers URL you can use &lt;issuer&gt; as\n      a short cut.<br>\n      Like this: issuer=&lt;issuer&gt; assuming that the parameters name is\n      \'issuer\'<br>\n    </p>\n    <p>\n      Query parameter/-s:<br>\n      <input type="text" name="params" value="')
        __M_writer(str(params))
        __M_writer('" size="60">\n    </p>\n    <p>\n      Choose profile:\n      <select name="profile">\n')
        for v in profiles:
            __M_writer('          <option value="')
            __M_writer(str(v))
            __M_writer('">')
            __M_writer(str(v))
            __M_writer('</option>\n')
        __M_writer('      </select>\n    </p>\n    <input type="submit" value="Submit">\n  </form>\n</div>\n')
        __M_writer(str(postfix(base)))
        __M_writer('\n</body>\n</html>')
        return ''
    finally:
        context.caller_stack._pop_frame()


"""
__M_BEGIN_METADATA
{"line_map": {"77": 43, "78": 45, "16": 1, "85": 48, "86": 57, "87": 57, "88": 100, "89": 100, "90": 101, "91": 101, "92": 104, "93": 104, "94": 117, "95": 117, "96": 122, "97": 123, "98": 123, "99": 123, "100": 123, "101": 123, "38": 11, "39": 12, "104": 130, "28": 0, "103": 130, "110": 104, "102": 125, "62": 31, "63": 33}, "source_encoding": "utf-8", "uri": "config.mako", "filename": "htdocs/config.mako"}
__M_END_METADATA
"""
