
<%
  def display_form(headline, grp, dic):
    lines = ['<h3>{}</h3>'.format(headline), '<table>']
    keys = list(dic.keys())
    keys.sort()
    for key in keys:
      val = dic[key]
      if val is False or val is True:
        if val == "True":
          _choice = " ".join(['True <input type="radio" name="{}:{}" value="True" checked>'.format(grp,key),
                             'False <input type="radio" name="{}:{}" value="False">'.format(grp,key)])
        else:
          _choice = " ".join(['True <input type="radio" name="{}:{}" value="True">'.format(grp,key),
                             'False <input type="radio" name="{}:{}" value="False" checked>'.format(grp,key)])
        lines.append('<tr><th align="left">{}</th><td>{}</td></tr>'.format(key, _choice))
      elif key in ['profile', 'issuer', 'tag']:
        lines.append('<tr><th align="left">{}</th><td>{}</td></tr>'.format(key, val))
        lines.append('<input type="hidden" name="{}:{}" value="{}"'.format(grp,key,val))
      else:
        lines.append('<tr><th align="left">{}</th><td><input type="text" name="{}:{}" value="{}"></td></tr>'.format(key,grp,key,val))
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
    lines.append('<button type="submit" value="configure" class="button">Save & Start</button>')
    lines.append('</form>')
    return "\n".join(lines)
  %>

<!DOCTYPE html>
<html>
<head>
  <title>OpenID Connect OP Testing</title>
  <link rel="stylesheet" type="text/css" href="${base}/static/theme.css">
</head>
<body>
  <h2>OpenID Connect OP Testing</h2>
    <br>
        <p>
            On this page you are expected to configure your instance of the test tool
        </p>
        <br>
    <div class="inp">
      ${display(base, iss, tag, dicts)}
    </div>
</body>
</html>