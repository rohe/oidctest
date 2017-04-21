<%
  def choice(profiles):
    keys = list(profiles.keys())
    keys.sort()

    line = [
      '<table>',
      '<tr><th>Response type</th><th></th></tr>']
    for k in keys:
      line.append('<tr><td>{}</td><td><input type="radio" name="profile" value="{}"></td></tr>'.format(k,profiles[k]))
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
input[type=submit]{
    font-size:30px;
}
      </style>
    <title>The OIDC RP library test documentation</title>
  </head>
  <body>
  <h1>Welcome to the OpenID Foundation RP library test site</h1>
  <h3>Before you start testing please read the
    <a href="http://openid.net/certification/rp_testing/"
       target="_blank">"how to use the RPtest"</a>
    introduction guide</h3>
  <h3>For a list of OIDC RP library tests per response_type chose your preference:</h3>
  <form action="${path}list">
    ${choice(profiles)}
    <p></p>
    <input type="submit" value="Submit">
  </form>
  </body>
</html>