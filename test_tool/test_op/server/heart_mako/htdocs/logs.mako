<%
import os

def display_log(base, logs, issuer, profile):
    if issuer:
        if profile:
            el = "<h3>A list of tests that are saved on disk for this profile:</h3>"
        else:
            el = "<h3>A list of profiles that are saved on disk for this issuer:</h3>"
    else:
        el = "<h3>A list of issuers that are saved on disk for this test server:</h3>"

    el += "<ul>"

    if profile:
        for name, path in logs:
            el += '<li><a href="{}{}" download="{}/{}.html">{}</a>'.format(
                base, path, issuer, name, name)
    elif issuer:
        for name, path in logs:
            _tarfile = "{}{}.tar".format(base, path.replace("log", "tar"))
            el += '<li><a href="{}{}">{}</a> tar file:<a href="{}">Download logs</a>'.format(
                base, path, name, _tarfile)
    else:
        for name, path in logs:
            el += '<li><a href="{}{}">{}</a>'.format(base, path, name)
    el += "</ul>"
    return el
%>
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
    SCRIPT_INFO = ["{}/static/jquery.min.1.9.1.js", "{}/static/bootstrap/js/bootstrap.min.js"]

    def postfix(base):
        line = []
        for d in SCRIPT_INFO:
            _src = d.format(base)
            line.append('<script src={}></script>'.format(_src))
        return "\n".join(line)

    %>

<!DOCTYPE html>
<html>
  <head>
    <title>HEART OIDC OP Test</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <!-- Bootstrap -->
    ${boot_strap(base)}
    <!-- HTML5 shim and Respond.js IE8 support of HTML5 elements and media queries -->
    <!--[if lt IE 9]>
      <script src="../../assets/js/html5shiv.js"></script>
      <script src="../../assets/js/respond.min.js"></script>
    <![endif]-->
  </head>
  <body>
    <div class="container">
     <!-- Main component for a primary marketing message or call to action -->
      <div class="jumbotron">
        <h1>HEART OIDC OP Test logs</h1>
            ${display_log(base, logs, issuer, profile)}
      </div>

    </div> <!-- /container -->
    ${postfix(base)}
  </body>
</html>