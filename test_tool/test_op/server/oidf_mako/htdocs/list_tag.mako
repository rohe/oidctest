<%!

from future.backports.urllib.parse import unquote_plus

def item_table(base, qiss, items):
    line = ["<table>"]
    for item in items:
        _item = '<a href="{}/list/{}/{}">{}</a>'.format(base, qiss, item, unquote_plus(item))
        line.append("<tr><td>{}</td></tr>".format(_item))

    line.append("</table>")
    return '\n'.join(line)

%>

<!DOCTYPE html>

<html>
  <head>
    <title>Tag list</title>
  </head>
  <body>
    <h1>List of tags for '${iss}'</h1>
        ${item_table(base, qiss, items)}
  </body>
</html>