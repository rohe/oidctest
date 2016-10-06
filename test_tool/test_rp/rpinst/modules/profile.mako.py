# -*- coding:utf-8 -*-
from mako import runtime, filters, cache

UNDEFINED = runtime.UNDEFINED
STOP_RENDERING = runtime.STOP_RENDERING
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 10
_modified_time = 1458029763.865661
_enable_loop = True
_template_filename = 'htdocs/profile.mako'
_template_uri = 'profile.mako'
_source_encoding = 'utf-8'
_exports = []


def inputs(spec, selected):
    """
    Creates list of choices
    """

    l = list(spec.keys())
    l.sort()

    element = []
    for key in l:
        if spec[key] == [True, False]:
            element.append("<p><b>{}</b>".format(key))
            for val in ['True', 'False']:
                _txt = "<input type=\"radio\" name=\"{}\" value=\"{}\"".format(
                    key, val)
                if key in selected:
                    if val == 'True' and selected[key]:
                        _txt += ' checked'
                    elif val == 'False' and not selected[key]:
                        _txt += ' checked'
                _txt += ">{}".format(val)
                element.append(_txt)
            element.append("</p>")
        else:
            element.append("<p><b>{}</b><br>".format(key))
            element.append("<ul>")
            values = list(spec[key])
            values.sort()
            for v in values:
                _txt = "<li><input type=\"checkbox\" name=\"{}\" value=\"{" \
                       "}\"".format(
                    key, v)
                if key in selected:
                    if v in selected[key]:
                        _txt += " checked"
                _txt += ">{}".format(v)
                element.append(_txt)
            element.append("</ul></p>")

    return "\n".join(element)


def render_body(context, **pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        specs = context.get('specs', UNDEFINED)
        selected = context.get('selected', UNDEFINED)
        id = context.get('id', UNDEFINED)
        __M_writer = context.writer()
        __M_writer(
            '\n\n<html lang="en">\n<head>\n  <meta charset="UTF-8">\n  '
            '<title>OP profile</title>\n</head>\n<body>\n<form '
            'action="profile">\n  <input type="hidden" name="_id_" value="')
        __M_writer(str(id))
        __M_writer('">\n  ')
        __M_writer(str(inputs(specs, selected)))
        __M_writer(
            '\n  <input type="submit" '
            'value="Submit">\n</form>\n</body>\n</html>')
        return ''
    finally:
        context.caller_stack._pop_frame()


"""
__M_BEGIN_METADATA
{"filename": "htdocs/profile.mako", "uri": "profile.mako", "source_encoding": "utf-8", "line_map": {"16": 1, "65": 40, "66": 49, "67": 49, "68": 50, "69": 50, "57": 0, "75": 69}}
__M_END_METADATA
"""
