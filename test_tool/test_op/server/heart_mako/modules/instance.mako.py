# -*- coding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
STOP_RENDERING = runtime.STOP_RENDERING
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 10
_modified_time = 1480335869.399576
_enable_loop = True
_template_filename = '../heart_mako/htdocs/instance.mako'
_template_uri = 'instance.mako'
_source_encoding = 'utf-8'
_exports = []


def render_body(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        tag = context.get('tag', UNDEFINED)
        base = context.get('base', UNDEFINED)
        iss = context.get('iss', UNDEFINED)
        dicts = context.get('dicts', UNDEFINED)
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

        def display_form(headline, grp, dic):
          lines = ['<h3>{}</h3>'.format(headline), '<table>']
          for key, val in dic.items():
            lines.append('<tr><th>{}</th><td><input type="text" name="{}:{}" value="{}"></td></tr>'.format(key,grp,key,val))
          lines.append('</table>')
          return lines
        
        headline = {
          'tool': "Test tool configuration",
          "registration_response": "",
          "provider_info": ""
          }
        
        def display(base, iss, tag, dicts):
          lines = []
          lines.append('<form action="{}/run/{}/{}" method="post">'.format(base,iss,tag))
          for grp, info in dicts.items():
            lines.append('<br>')
            lines.extend(display_form(headline[grp], grp, info))
          lines.append('<input type="submit" value="Submit">')
          lines.append('</form>')
          return "\n".join(lines)
        
        
        __M_locals_builtin_stored = __M_locals_builtin()
        __M_locals.update(__M_dict_builtin([(__M_key, __M_locals_builtin_stored[__M_key]) for __M_key in ['display_form','display','headline'] if __M_key in __M_locals_builtin_stored]))
        __M_writer('\n\n<!DOCTYPE html>\n<html>\n<head>\n  <title>OpenID Certification OP Test Tool Configuration</title>\n  <meta name="viewport" content="width=device-width, initial-scale=1.0">\n  <!-- Bootstrap -->\n  ')
        __M_writer(str(boot_strap(base)))
        __M_writer('\n  <!-- HTML5 shim and Respond.js IE8 support of HTML5 elements and media queries -->\n  <!--[if lt IE 9]>\n  <script src="../../assets/js/html5shiv.js"></script>\n  <script src="../../assets/js/respond.min.js"></script>\n  <![endif]-->\n  <style>\n    h3 {\n      background-color: lightblue;\n    }\n\n    h4 {\n      background-color: lightcyan;\n    }\n\n    @media (max-width: 768px) {\n      .jumbotron {\n        border-radius: 10px;\n        margin-left: 4%;\n        margin-right: 4%;\n      }\n    }\n\n    @media (min-width: 768px) and (max-width: 1600px) {\n      .jumbotron {\n        border-radius: 10px;\n        margin-left: 10%;\n        margin-right: 10%;\n      }\n    }\n\n    @media (min-width: 1600px) {\n      .jumbotron {\n        border-radius: 10px;\n        margin-left: 20%;\n        margin-right: 20%;\n      }\n    }\n  </style>\n</head>\n<body>\n<!-- Main component for a primary marketing message or call to action -->\n<div class="jumbotron">\n  <h2>OpenID Connect Provider Certification</h2>\n        <br>\n        <p>\n            On this page you are expected to configure your instance of the test tool\n        </p>\n        <br>\n      ')
        __M_writer(str(display(base, iss, tag, dicts)))
        __M_writer('\n</div>\n<script src="/static/jquery.min.1.9.1.js"></script>\n<script src="/static/bootstrap/js/bootstrap.min.js"></script>\n</body>\n</html>')
        return ''
    finally:
        context.caller_stack._pop_frame()


"""
__M_BEGIN_METADATA
{"line_map": {"16": 0, "49": 22, "86": 80, "48": 20, "80": 102, "25": 1, "76": 45, "77": 53, "78": 53, "79": 102}, "source_encoding": "utf-8", "filename": "../heart_mako/htdocs/instance.mako", "uri": "instance.mako"}
__M_END_METADATA
"""
