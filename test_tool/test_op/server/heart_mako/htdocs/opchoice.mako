<%!
def op_choice(op_list):
    """
    Creates a dropdown list of OpenID Connect providers
    """
    element = "<select name=\"op\">"
    for name in op_list:
        element += "<option value=\"%s\">%s</option>" % (name, name)
    element += "</select>"
    return element
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

    <!-- Static navbar -->
    <div class="navbar navbar-default navbar-fixed-top">
        <div class="navbar-header">
          <a class="navbar-brand" href="#">HEART OIDC OP Test</a>
        </div>
    </div>

    <div class="container">
     <!-- Main component for a primary marketing message or call to action -->
      <div class="jumbotron">
        <form class="form-signin" action="rp" method="get">
        <h1>OP by UID</h1>
          <h3>Chose the OpenID Connect Provider: </h3>
            <p>From this list</p>
            ${op_choice(op_list)}
            <p> OR by providing your unique identifier at the OP. </p>
            <input type="text" id="uid" name="uid" class="form-control" placeholder="UID" autofocus>
            <button class="btn btn-lg btn-primary btn-block" type="submit">Start</button>
        </form>
      </div>

    </div> <!-- /container -->
    ${postfix(base)}
  </body>
</html>