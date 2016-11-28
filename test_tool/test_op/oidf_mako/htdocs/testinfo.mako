<%!

  def do_conditions(events):
    element = ['<h3>Conditions</h3>','<ul>']
    for ev in events.get_data('condition'):
      element.append('<li>{}'.format(ev))
    element.append('</ul>')
    return "\n".join(element)
%>

<%!
  def trace_output(trace):
    """

    """
    element = ["<h3>Trace output</h3>", "<pre><code>"]
    for item in trace:
        element.append("%s" % item)
    element.append("</code></pre>")
    return "\n".join(element)
%>

<%
  def profile_output(pinfo):
    element = []
    for key, val in pinfo.items():
        element.append("<em>%s:</em> %s<br>" % (key,val))

    return "\n".join(element)
%>

<!DOCTYPE html>

<html>
<head>
  <title>OpenID Certification OP Test</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <!-- Bootstrap -->
  <link href="/static/bootstrap/css/bootstrap.min.css" rel="stylesheet"
        media="screen">
  <link href="/static/style.css" rel="stylesheet" media="all">

  <!-- HTML5 shim and Respond.js IE8 support of HTML5 elements and media queries -->
  <!--[if lt IE 9]>
  <script src="../../assets/js/html5shiv.js"></script>
  <script src="../../assets/js/respond.min.js"></script>
  <![endif]-->
</head>
<body>

<div class="container">
  <!-- Main component for a primary marketing message or call to action -->
  <h2>Test info</h2>
  ${profile_output(profile)}
  <hr>
  ${trace_output(trace)}
  <hr>
  ${do_conditions(events)}
  <hr>
  <h3>Result</h3>${result}
</div> <!-- /container -->
<!-- jQuery (necessary for Bootstrap's JavaScript plugins) -->
<script src="/static/jquery.min.1.9.1.js"></script>
<!-- Include all compiled plugins (below), or include individual files as needed -->
<script src="/static/bootstrap/js/bootstrap.min.js"></script>
</body>
</html>