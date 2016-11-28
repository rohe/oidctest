<%!
    def button(url):
        return "<a href='%s'>button</a>" % url
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
        <h1>HEART OIDC OP Test</h1>
        At this point you have to remove all cookies you have received from
        your OpenID Connect Provider. This since this test is simulating you
        login in from a second device while still being logged in at the first.
        So please remove the cookies and then hit this
        ${button(url)} to continue.
      </div>

    </div> <!-- /container -->
    ${postfix(base)}
  </body>
</html>