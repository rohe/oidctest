<%
  def display_info(info):

    line = ['<table>']
    keys = list(info['tool'].keys())
    keys.sort()
    for key in keys:
        val = info['tool'][key]
        line.append('<tr><th>{}</th><td>{}</td></tr>'.format(key, val))
    line.append('</table>')
    return '\n'.join(line)
%>

<!DOCTYPE html>

<html>
<head>
    <title>Test tool instance</title>
    <link rel="stylesheet" type="text/css" href="${base}static/theme.css">
</head>
<body>
<h1>What do you want to do with this test tool instance?</h1>
<p>
${display_info(info)}
</p>
<p>
  % if active:
    <div class="active">Running</div>
  % else:
    <div class="inactive">Inactive</div>
  % endif
</p>
<p>
<form action="${qargs[-1]}/action" method="get">
    <table>
        <tr>
            <td>
                <button name="action" type="submit" value="delete" class="button">delete</button>
            </td>
            <td>
                <button name="action" type="submit" value="restart" class="button">restart</button>
            </td>
            <td>
                <button name="action" type="submit" value="configure" class="button">reconfigure</button>
            </td>
        </tr>
    </table>
</form>
</p>
</body>
</html>