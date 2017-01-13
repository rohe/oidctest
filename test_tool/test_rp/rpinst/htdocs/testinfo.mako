<%!

  from otest.check import STATUSCODE
  from otest import summation

  def do_assertions(out):
      return summation.condition(out, True)
%>

<%!

  from otest.events import layout, row

  def trace_output(events):
    """

    """
    element = ["<h3>Trace output</h3>", '<div class="trace"><table>']
    start = 0
    for event in events:
        if not start:
            start = event.timestamp
        # element.append(layout(start, event))
        element.append(row(start, event))
    element.append("</table></div>")
    return "\n".join(element)
%>

<%
  def profile_output(pinfo):
    element = ['<div class="profile">']
    for key, val in pinfo.items():
        element.append("<em>%s:</em> %s<br>" % (key,val))
    element.append('</div>')
    return "\n".join(element)
%>

<!DOCTYPE html>

<html>
  <head>
    <title>HEART OIDC OP Test</title>
    <style>
      .profile {
        background-color: aquamarine;
      }

      tr.phase {
        background-color: #4cae4c;
      }

      table, th, td {
        border: 1px solid black;
      }

      table {
        table-layout: fixed;
        white-space: normal !important;
        width: 1200px;
        text-align: left;
        vertical-align: top;
        padding: 5px;
      }

      td {
        word-wrap: break-word;
      }

      td.left {
        width: 10%;
      }

      td.mid {
        width: 20%;
      }
    </style>

  </head>
  <body>
    <h2>Test info</h2>
      ${profile_output(profile)}
    <hr>
      ${do_assertions(events)}
    <hr>
      ${trace_output(events)}
    <hr>
    <h3>Result</h3>${result}
  </body>
</html>