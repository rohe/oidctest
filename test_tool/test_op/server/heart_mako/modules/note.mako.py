# -*- coding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
STOP_RENDERING = runtime.STOP_RENDERING
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 10
_modified_time = 1476350778.097182
_enable_loop = True
_template_filename = 'heart_mako/htdocs/note.mako'
_template_uri = 'note.mako'
_source_encoding = 'utf-8'
_exports = []



def link(url):
    return "<a href='%s'>link</a>" % url


def render_body(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        url = context.get('url', UNDEFINED)
        base = context.get('base', UNDEFINED)
        back = context.get('back', UNDEFINED)
        note = context.get('note', UNDEFINED)
        __M_writer = context.writer()
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
        __M_locals.update(__M_dict_builtin([(__M_key, __M_locals_builtin_stored[__M_key]) for __M_key in ['SCRIPT_INFO','postfix'] if __M_key in __M_locals_builtin_stored]))
        __M_writer('\n\n<!DOCTYPE html>\n\n<html>\n  <head>\n    <title>HEART OIDC OP Test</title>\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n    <!-- Bootstrap -->\n    ')
        __M_writer(str(boot_strap(base)))
        __M_writer('\n    <!-- HTML5 shim and Respond.js IE8 support of HTML5 elements and media queries -->\n    <!--[if lt IE 9]>\n      <script src="../../assets/js/html5shiv.js"></script>\n      <script src="../../assets/js/respond.min.js"></script>\n    <![endif]-->\n  </head>\n  <body>\n    <div class="container">\n     <!-- Main component for a primary marketing message or call to action -->\n      <div class="jumbotron">\n        <h1>HEART OIDC OP Test</h1>\n        ')
        __M_writer(str(note))
        __M_writer('\n        <br>\n        To continue click this ')
        __M_writer(str(link(url)))
        __M_writer('.<br>\n        To go back click this ')
        __M_writer(str(link(back)))
        __M_writer('.\n      </div>\n\n    </div> <!-- /container -->\n    ')
        __M_writer(str(postfix(base)))
        __M_writer('\n  </body>\n</html>')
        return ''
    finally:
        context.caller_stack._pop_frame()


"""
__M_BEGIN_METADATA
{"uri": "note.mako", "filename": "heart_mako/htdocs/note.mako", "line_map": {"69": 37, "70": 46, "71": 46, "72": 58, "73": 58, "74": 60, "75": 60, "76": 61, "77": 61, "78": 65, "79": 65, "16": 1, "85": 79, "21": 0, "54": 25, "55": 27, "30": 4, "31": 6}, "source_encoding": "utf-8"}
__M_END_METADATA
"""
