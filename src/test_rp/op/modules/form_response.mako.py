# -*- coding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 10
_modified_time = 1431513043.265439
_enable_loop = True
_template_filename = 'htdocs/form_response.mako'
_template_uri = 'form_response.mako'
_source_encoding = 'utf-8'
_exports = []



def inputs(form_args):
    """
    Creates list of input elements
    """
    element = ""
    for name, value in list(form_args.items()):
        element += "<input type=\"hidden\" name=\"%s\" value=\"%s\"/>" % (name,
                                                                          value)
    return element


def render_body(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        action = context.get('action', UNDEFINED)
        form_args = context.get('form_args', UNDEFINED)
        __M_writer = context.writer()
        __M_writer('\n\n<html>\n  <head>\n    <title>Submit This Form</title>\n  </head>\n  <body onload="javascript:document.forms[0].submit()">\n    <form method="post" action=')
        __M_writer(str(action))
        __M_writer('>\n        ')
        __M_writer(str(inputs(form_args)))
        __M_writer('\n    </form>\n  </body>\n</html>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


"""
__M_BEGIN_METADATA
{"source_encoding": "utf-8", "line_map": {"34": 11, "35": 18, "36": 18, "37": 19, "38": 19, "44": 38, "15": 1, "27": 0}, "uri": "form_response.mako", "filename": "htdocs/form_response.mako"}
__M_END_METADATA
"""
