<%!

from future.backports.urllib.parse import unquote_plus

def item_table(base, qiss, items, active):
    line = ["<table>", "<tr><th>Tag</th><th>Status</th><th>Actions</th></tr>"]
    _del = '<button name="action" type="submit" value="delete" class="choice">delete</button>'
    _rst = '<button name="action" type="submit" value="restart" class="choice">restart</button>'
    _cnf = '<button name="action" type="submit" value="configure" class="choice">reconfigure</button>'

    for item in items:
        _url = "{}entity/{}/{}".format(base, qiss, item)
        _action = '\n'.join(['<form action="{}/action" method="get">'.format(_url),
                             _del, _rst, _cnf])
        if active[item]:
            _ball = '<img src="/static/green-ball-32.png" alt="Green">'
        else:
            _ball = '<img src="/static/red-ball-32.png" alt="Red">'
        #_item = '<a href="{}">{}</a>'.format(_url, unquote_plus(item))
        line.append("<tr><td>{}</td><td>{}</td><td>{}</td></tr>".format(item, _ball, _action))

    line.append("</table>")
    return '\n'.join(line)

%>

<!DOCTYPE html>

<html>
  <head>
    <title>Tag list</title>
   <link rel="stylesheet" type="text/css" href="${base}/static/theme.css">
  </head>
  <body>
    <h1>All the tags registered for the Issuer: '<i>${iss}</i>'</h1>
        ${item_table(base, qiss, items, active)}
  </body>
</html>