# -*- coding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
STOP_RENDERING = runtime.STOP_RENDERING
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 10
_modified_time = 1480322099.857781
_enable_loop = True
_template_filename = 'heart_mako/htdocs/new_iss.mako'
_template_uri = 'new_iss.mako'
_source_encoding = 'utf-8'
_exports = []


def render_body(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        base = context.get('base', UNDEFINED)
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

        def form_action(base):
            return '<form action="{}/create">'.format(base)
        
        
        __M_locals_builtin_stored = __M_locals_builtin()
        __M_locals.update(__M_dict_builtin([(__M_key, __M_locals_builtin_stored[__M_key]) for __M_key in ['form_action'] if __M_key in __M_locals_builtin_stored]))
        __M_writer('\n\n<!DOCTYPE html>\n<html>\n<head>\n  <title>OpenID Certification OP Test Tool Configuration</title>\n  <meta name="viewport" content="width=device-width, initial-scale=1.0">\n  <!-- Bootstrap -->\n  ')
        __M_writer(str(boot_strap(base)))
        __M_writer('\n  <!-- HTML5 shim and Respond.js IE8 support of HTML5 elements and media queries -->\n  <!--[if lt IE 9]>\n  <script src="../../assets/js/html5shiv.js"></script>\n  <script src="../../assets/js/respond.min.js"></script>\n  <![endif]-->\n  <style>\n    h3 {\n      background-color: lightblue;\n    }\n\n    h4 {\n      background-color: lightcyan;\n    }\n\n    @media (max-width: 768px) {\n      .jumbotron {\n        border-radius: 10px;\n        margin-left: 4%;\n        margin-right: 4%;\n      }\n    }\n\n    @media (min-width: 768px) and (max-width: 1600px) {\n      .jumbotron {\n        border-radius: 10px;\n        margin-left: 10%;\n        margin-right: 10%;\n      }\n    }\n\n    @media (min-width: 1600px) {\n      .jumbotron {\n        border-radius: 10px;\n        margin-left: 20%;\n        margin-right: 20%;\n      }\n    }\n  </style>\n</head>\n<body>\n<!-- Main component for a primary marketing message or call to action -->\n<div class="jumbotron">\n  <h2>OpenID Connect Provider Certification</h2>\n        <br>\n\n        <p>\n            This is a tool used for testing the compliance of an OpenID Connect Provider with the\n            OpenID Connect specifications. In order to start testing you need to configure a test\n            instance. Enter the issuer URL to the OpenID Connect Provider you want to test.\n        </p>\n        <br>\n  ')
        __M_writer(str(form_action(base)))
        __M_writer('\n    <h3>Issuer URL (without .well-known):</h3>\n    <input type="text" name="iss">\n    <br>\n    <h3>An identifier of this specific configuration in the case that you want to have more then one</h3>\n    <input type="text" name="tag" value="default">\n  <br>\n    <p>\n      Choose what your OP supports:\n      <table border="1">\n            <tr><th>WebFinger</th><td style="width:30px"><input type="checkbox" name="webfinger"></td></tr>\n    </table>\n    <input type="hidden" name="discovery" value="on">\n    <input type="hidden" name="registration" value="\'on">\n  <br>\n  <h3>Choose a return type</h3>\n  <br>\n    <table broder="1">\n            <tr><th style="width:100px">Return type</th><td>\n                <input type="radio" name="return_type" value="C"> Code <br>\n                <input type="radio" name="return_type" value="I"> IdToken <br>\n                <input type="radio" name="return_type" value="IT"> IdToken Token <br>\n                <input type="radio" name="return_type" value="CI"> Code IdToken <br>\n                <input type="radio" name="return_type" value="CT"> Code Token <br>\n                <input type="radio" name="return_type" value="CIT"> Code IdToken Token\n            </td></tr>\n        </table>\n      </p>\n    <input type="submit" value="Submit">\n  </form>\n</div>\n<script src="/static/jquery.min.1.9.1.js"></script>\n<script src="/static/bootstrap/js/bootstrap.min.js"></script>\n</body>\n</html>')
        return ''
    finally:
        context.caller_stack._pop_frame()


"""
__M_BEGIN_METADATA
{"filename": "heart_mako/htdocs/new_iss.mako", "uri": "new_iss.mako", "line_map": {"16": 0, "53": 25, "22": 1, "55": 33, "56": 85, "57": 85, "54": 33, "45": 20, "46": 22, "63": 57}, "source_encoding": "utf-8"}
__M_END_METADATA
"""
