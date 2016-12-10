<%!

from otest.check import STATUSCODE

def test_output(out):
    """

    """
    element = ["<h3>Test output</h3>", "<pre><code>"]
    for item in out:
        if isinstance(item, tuple):
            element.append("__%s:%s__" % item)
        else:
            element.append("[%s]" % item["id"])
            element.append("\tstatus: %s" % STATUSCODE[item["status"]])
            try:
                element.append("\tdescription: %s" % (item["name"]))
            except KeyError:
                pass
            try:
                element.append("\tinfo: %s" % (item["message"]))
            except KeyError:
                pass
    element.append("</code></pre>")
    return "\n".join(element)
%>

<%!
from otest.events import layout

def trace_output(events):
    """

    """
    element = ["<h3>Trace output</h3>", "<pre><code>"]
    start = 0
    for event in events:
        if not start:
            start = event.timestamp
        element.append(layout(start, event))
    element.append("</code></pre>")
    return "\n".join(element)
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
     <h2>Result</h2>
       ${test_output(output)}
       ${trace_output(trace)}

    </div> <!-- /container -->
    $postfix(base)
  </body>
</html>