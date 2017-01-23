
<%
  ball = '<img src="/static/red-ball-16.png" alt="Red Ball">'

  def do_line(grp, key, val, req=False):
    if req:
      _b = ball
    else:
      _b = ''

    if val is False or val is True:
      if val == "True":
        _choice = " ".join(['True <input type="radio" name="{}:{}" value="True" checked>'.format(grp,key),
                            'False <input type="radio" name="{}:{}" value="False">'.format(grp,key)])
      else:
        _choice = " ".join(['True <input type="radio" name="{}:{}" value="True">'.format(grp,key),
                            'False <input type="radio" name="{}:{}" value="False" checked>'.format(grp,key)])
      return '<tr><th align="left">{}</th><td>{}</td><td>{}</td></tr>'.format(key, _choice, _b)
    elif key in ['profile', 'issuer', 'tag']:
      l = ['<tr><th align="left">{}</th><td>{}</td><td>{}</td></tr>'.format(key, val, _b),
           '<input type="hidden" name="{}:{}" value="{}"'.format(grp,key,val)]
      return '\n'.join(l)
    else:
      return '<tr><th align="left">{}</th><td><input type="text" name="{}:{}" value="{}" class="str"></td><td>{}</td></tr>'.format(key,grp,key,val,_b)

  def display_form(headline, grp, dic, state):
    lines = ['<h3>{}</h3>'.format(headline), '<table>']
    keys = list(dic.keys())
    keys.sort()
    if grp in state:
      for param in state[grp]['immutable']:
        val = dic[param]
        lines.append('<tr><th align="left">{}</th><td>{}</td><td>{}</td></tr>'.format(param, val, ball))
        lines.append('<input type="hidden" name="{}:{}" value="{}"'.format(grp, param, val))
        keys.remove(param)
      for param in state[grp]['required']:
        val = dic[param]
        lines.append(do_line(grp, param, val, True))
        keys.remove(param)
    for key in keys:
      val = dic[key]
      lines.append(do_line(grp, key, val, False))
    lines.append('</table>')
    return lines

  headline = {
    'tool': "Test tool configuration",
    "registration_response": "",
    "provider_info": ""
    }

  def display(base, iss, tag, dicts, state):
    lines = ['<form action="{}/run/{}/{}" method="post">'.format(base,iss,tag)]
    for grp, info in dicts.items():
      lines.append('<br>')
      lines.extend(display_form(headline[grp], grp, info, state))
    lines.append('<button type="submit" value="configure" class="button">Save & Start</button>')
    lines.append('<button type="submit" value="abort" class="abort">Abort</button>')
    lines.append('</form>')
    return "\n".join(lines)
  %>

<!DOCTYPE html>
<html>
<head>
  <title>OpenID Connect OP Test Tool Configuration</title>
  <link rel="stylesheet" type="text/css" href="${base}/static/theme.css">
</head>
<body>
  <h2>OpenID Connect OP Testing</h2>
    <br>
        <p>
            On this page you are expected to configure your instance of the test tool
        </p>
  <p>
    <img src="/static/red-ball-16.png" alt="Red ball"> means that parameter <em>MUST</em>
    have a value.
  </p>
        <br>
    <div class="inp">
      ${display(base, iss, tag, dicts, state)}
    </div>
</body>
</html>