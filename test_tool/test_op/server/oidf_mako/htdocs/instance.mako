<%
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
%>

<%
  def display_form(headline, dic):
    lines = ['<h3>{}</h3>'.format(headline)]
    lines.append('<table>')
    for key, val in dic.items():
      lines.append('<tr><th>{}</th><td><input type="text" name="{}" value="{}"></td></tr>'.format(key,key,val))
    lines.append('</table>')
    return lines

  headline = {
    'tool': "",
    "registration_response": "",
    "provider_info": ""
    }

  def display(base, iss, tag, dicts):
    lines = []
    lines.append('<form action="{}/{}/{}" method="post">'.format(base,iss,tag))
    for item, info in dicts.items():
      lines.append('<br>')
      lines.extend(display_form(headline[item], info))
    lines.append('<input type="submit" value="Submit">')
    lines.append('</form>')
    return "\n".join(lines)
  %>

<!DOCTYPE html>
<html>
<head>
  <title>OpenID Certification OP Test Tool Configuration</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <!-- Bootstrap -->
  ${boot_strap(base)}
  <!-- HTML5 shim and Respond.js IE8 support of HTML5 elements and media queries -->
  <!--[if lt IE 9]>
  <script src="../../assets/js/html5shiv.js"></script>
  <script src="../../assets/js/respond.min.js"></script>
  <![endif]-->
  <style>
    h3 {
      background-color: lightblue;
    }

    h4 {
      background-color: lightcyan;
    }

    @media (max-width: 768px) {
      .jumbotron {
        border-radius: 10px;
        margin-left: 4%;
        margin-right: 4%;
      }
    }

    @media (min-width: 768px) and (max-width: 1600px) {
      .jumbotron {
        border-radius: 10px;
        margin-left: 10%;
        margin-right: 10%;
      }
    }

    @media (min-width: 1600px) {
      .jumbotron {
        border-radius: 10px;
        margin-left: 20%;
        margin-right: 20%;
      }
    }
  </style>
</head>
<body>
<!-- Main component for a primary marketing message or call to action -->
<div class="jumbotron">
  <h2>OpenID Connect Provider Certification</h2>
        <br>
        <p>
            On this page you are expected to configure your instance of the test tool
        </p>
        <br>
      ${display(base, iss, tag, dicts)}
</div>
<script src="/static/jquery.min.1.9.1.js"></script>
<script src="/static/bootstrap/js/bootstrap.min.js"></script>
</body>
</html>