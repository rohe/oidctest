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

<%!
  def print_dict(obj):
    elements = ['<table>']
    for k,v in obj.items():
      elements.append('<tr><td>{}</td><td>{}</td></tr>'.format(k,v))
    elements.append('</table')
    return "\n".join(elements)
%>

<%!
  from oic.oauth2 import Message
  from otest import jsonconv

  def print_events(events):
    elements = ['<style> table { table-layout: fixed; table th, table td { overflow: hidden; } </style>', '<table class="table table-bordered">', "<thead>", '<tr><th style="width: 5%">Elapsed time</th>', '<th style="width: 15%">Event</th>', '<th style="width: 50%">Info</th></tr></thead>']
    for cl,typ,data in events:
      if isinstance(data, Message):
        _dat = jsonconv.json2html.convert(data.to_json())
          # root_table_attributes='class="table table-bordered"')
        elements.append('<tr><td>{}</td><td>{}</td><td>{}</td></tr>'.format(
          round(cl,3),typ,_dat))
      else:
        elements.append('<tr>')
        if typ == 'http request':
          elements.append('<div class="bg-success text-white">')
        elements.append('<td>{}</td><td>{}</td><td>{}</td>'.format(
          round(cl,3),typ,data))
        if typ == 'http request':
          elements.append('</div>')
        elements.append('</tr>')
    elements.append('</table')
    return "\n".join(elements)
%>


<!DOCTYPE html>
<html>
<head>
  <title>HEART OIDC RP Tests</title>
  <!-- <meta name="viewport" content="width=device-width, initial-scale=1.0"> -->
  <meta name="viewport" content="initial-scale=1.0">
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
  ${print_dict(profile)}
  <p>
  ${trace_output(events)}
</div>
${postfix(base)}
</body>
</html>