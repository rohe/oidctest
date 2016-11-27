# -*- coding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
STOP_RENDERING = runtime.STOP_RENDERING
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 10
_modified_time = 1480250992.718381
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



from oic.oauth2 import Message
from otest import jsonconv

def print_events(events):
  elements = ['<style> table { table-layout: fixed; table th, table td { overflow: hidden; } </style>', '<table class="table table-bordered">', "<thead>", '<tr><th style="width: 5%">Elapsed time</th>', '<th style="width: 15%">Event</th>', '<th style="width: 50%">Info</th></tr></thead>']
  for cl,typ,data in events:
    if isinstance(data, Message):
      _dat = jsonconv.json2html.convert(data.to_json())
        # root_table_attributes='class="table table-bordered"')
      elements.append('<tr><td>{}</td><td>{}</td><td>{}</td></tr>'.format(
        round(cl,3),typ,_dat))
    else:
      elements.append('<tr>')
      if typ == 'http request':
        elements.append('<div class="bg-success text-white">')
      elements.append('<td>{}</td><td>{}</td><td>{}</td>'.format(
        round(cl,3),typ,data))
      if typ == 'http request':
        elements.append('</div>')
      elements.append('</tr>')
  elements.append('</table')
  return "\n".join(elements)


def render_body(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        result = context.get('result', UNDEFINED)
        base = context.get('base', UNDEFINED)
        events = context.get('events', UNDEFINED)
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
        __M_locals.update(__M_dict_builtin([(__M_key, __M_locals_builtin_stored[__M_key]) for __M_key in ['LINK_INFO','boot_strap'] if __M_key in __M_locals_builtin_stored]))
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
        __M_writer('\n\n')
        __M_writer('\n\n\n<!DOCTYPE html>\n<html>\n<head>\n  <title>HEART OIDC RP Tests</title>\n  <!-- <meta name="viewport" content="width=device-width, initial-scale=1.0"> -->\n  <meta name="viewport" content="initial-scale=1.0">\n  ')
        __M_writer(str(boot_strap(base)))
        __M_writer('\n  <!-- HTML5 shim and Respond.js IE8 support of HTML5 elements and media queries -->\n  <!--[if lt IE 9]>\n  <script src="../../assets/js/html5shiv.js"></script>\n  <script src="../../assets/js/respond.min.js"></script>\n  <![endif]-->\n  <style>\n    h3 {\n      background-color: lightblue;\n    }\n\n    h4 {\n      background-color: lightcyan;\n    }\n\n    @media (max-width: 768px) {\n      .jumbotron {\n        border-radius: 10px;\n        margin-left: 4%;\n        margin-right: 4%;\n      }\n    }\n\n    @media (min-width: 768px) and (max-width: 1600px) {\n      .jumbotron {\n        border-radius: 10px;\n        margin-left: 10%;\n        margin-right: 10%;\n      }\n    }\n\n    @media (min-width: 1600px) {\n      .jumbotron {\n        border-radius: 10px;\n        margin-left: 20%;\n        margin-right: 20%;\n      }\n    }\n  </style>\n</head>\n<body>\n<!-- Main component for a primary marketing message or call to action -->\n<div class="jumbotron">\n  ')
        __M_writer(str(print_dict(profile)))
        __M_writer('\n  <p>\n  ')
        __M_writer(str(print_events(events)))
        __M_writer('\n  <p>\n  <b>')
        __M_writer(str(result))
        __M_writer('</b>\n</div>\n')
        __M_writer(str(postfix(base)))
        __M_writer('\n</body>\n</html>')
        return ''
    finally:
        context.caller_stack._pop_frame()


"""
__M_BEGIN_METADATA
{"source_encoding": "utf-8", "line_map": {"128": 122, "71": 1, "16": 34, "28": 46, "94": 20, "95": 22, "37": 55, "109": 32, "110": 44, "111": 53, "112": 78, "113": 87, "114": 87, "115": 130, "116": 130, "117": 132, "118": 132, "119": 134, "120": 134, "121": 136, "122": 136, "62": 0}, "uri": "testinfo.mako", "filename": "htdocs/testinfo.mako"}
__M_END_METADATA
"""
