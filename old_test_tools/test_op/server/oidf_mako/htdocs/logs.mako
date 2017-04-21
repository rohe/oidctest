<%
  import os

  def display_log(logs, issuer, profile, base):
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
            el += '<li><a href="{}{}" download="{}.html">{}</a>'.format(base, path, name, name)
    elif 'issuer':
        for name, path in logs:
            _tarfile = "{}{}.tar".format(base,path.replace("log", "tar"))
            el += '<li><a href="{}{}">{}</a> tar file:<a href="{}">Download logs</a>'.format(
                base, path, name, _tarfile)
    else:
        for name, path in logs:
            el += '<li><a href="{}{}">{}</a>' % (base, path, name)
    el += "</ul>"
    return el
%>

<!DOCTYPE html>
<html>
<head>
  <title>OpenID Certification OP Test</title>
</head>
<body>
<div class="container">
  <!-- Main component for a primary marketing message or call to action -->
  <h1>OpenID Certification OP Test logs</h1>
  ${display_log(logs, issuer, profile, base)}
</body>
</html>