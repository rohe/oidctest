<%!
  def test_list(args, grps):
    """
    Creates list of test descriptions
    """
    line = [
        '<table>',
        '<tr><th>Status</th><th>Description</th><th>Info</th></tr>']

    for pgrp in grps:
        h = False
        for tid, desc, result, grp in args:
            if pgrp == grp:
                if h is False:
                    line.append(
                        '<tr style><td colspan="3" class="center"><b>{}</b></td></tr>'.format(grp))
                    h = True

                line.append(
                    '<tr><td style="white-space:nowrap">{}</td><td>{}</td><td>{}</td></tr>'.format(
                        tid, desc, result))
    line.append('</table>')
    return '\n'.join(line)
%>


<!DOCTYPE html>

<html>
  <head>
      <style>
td {
    text-align: left;
}
th {
    background-color: #4CAF50;
    color: white;
    white-space: nowrap;
    text-align: left;
}
table, th, td {
    border: 1px solid black;
}
td.center {
    text-align: center;
    background-color: #a4aeaf;
}
      </style>
    <title>List of OIDC RP tests</title>
  </head>
  <body>
  <h1>List of OIDC RP library tests for profile: "<i>${response_type}</i>"</h1>
    <h2>Mandatory to implement</h2>
    ${test_list(mandatory, grps)}
    <h2>Optional</h2>
    ${test_list(optional, grps)}
  </body>
</html>