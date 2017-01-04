<%!
  def test_list(args):
    """
    Creates list of test descriptions
    """
    line = [
        '<table>',
        '<tr><th>TestID</th><th>Description</th><th>Expected result</th></tr>']

    for tid, desc, result in args:
        line.append('<tr><td style="white-space:nowrap">{}</td><td>{}</td><td>{}</td></tr>'.format(tid,
        desc, result))
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
      </style>
    <title>List of OIDC RP tests</title>
  </head>
  <body>
  <h1>List of OIDC RP library tests for profile: "<i>${response_type}</i>"</h1>
    <h2>Mandatory to implement</h2>
    ${test_list(mandatory)}
    <h2>Optional</h2>
    ${test_list(optional)}
  </body>
</html>