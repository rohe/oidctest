<%!

from future.backports.urllib.parse import unquote_plus

def iss_table(base, issuers):
    issuers.sort()
    line = ["<table>"]
    for iss in issuers:
        _item = '<a href="{}/entity/{}">{}</a>'.format(base, iss, unquote_plus(iss))
        line.append("<tr><td>{}</td></tr>".format(_item))

    line.append("</table>")
    return '\n'.join(line)

%>

<!DOCTYPE html>

<html>
  <head>
    <title>This ia a list of all the registered Issuers</title>
    <link rel="stylesheet" type="text/css" href="${base}/static/theme.css">
  </head>
  <body>
    <h1>A list of all the registered Issuers</h1>
        ${iss_table(base, issuers)}
  </body>
</html>