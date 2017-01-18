<%!

from future.backports.urllib.parse import unquote_plus

def iss_table(base, issuers):
    line = ["<table>"]
    for iss in issuers:
        _item = '<a href="{}/list/{}">{}</a>'.format(base, iss, unquote_plus(iss))
        line.append("<tr><td>{}</td></tr>".format(_item))

    line.append("</table>")
    return '\n'.join(line)

%>

<!DOCTYPE html>

<html>
  <head>
    <title>Issuer list</title>
  </head>
  <body>
    <h1>Issuer list</h1>
        ${iss_table(base, issuers)}
  </body>
</html>