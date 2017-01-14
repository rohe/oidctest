<%!

  def print_result(events):
    """
    Displays the test information
    """
    elements = []
    for event in events:
        elements.append('{}<br>'.format(event))
    return "\n".join(elements)
%>
<%
  def form_action(base):
        return '<form action="{}/list" method="post">'.format(base)
%>

<%
  def response_types():
      line = ['select name="response_type"']
      for a,b,v in [('Basic - code', 'C', 1),
                    ('Implicit - id_token', 'I', 0)
                    ('Implicit - id_token,token', 'IT', 0)
                    ('Hybrid - code,id_token', 'CI', 0)
                    ('Hybrid - code,token', 'CT', 0)
                    ('Hybrid - code,id_token,token', 'CIT', 0)
                    ]:
          if v:
            line.append('<option value="${b}" selected>${a}</option>')
          else:
            line.append('<option value="${b}">${a}</option>')

      line.append('</select>')
      return '\n'.join(line)
  %>

<!DOCTYPE html>
<html>
<head>
  <title>HEART OAuth2 RP Tests</title>
  <style>
    h3 {
      background-color: lightblue;
    }

    h4 {
      background-color: lightcyan;
    }

    p.iss {
      background-color: antiquewhite;
    }

    p.spage {
      background-color: beige;
    }

    .para {
      background-color: blanchedalmond;
    }

    form {
      width: 1000px;
    }

    .button {
      background-color: #4CAF50;
      border: none;
      color: white;
      padding: 15px 32px;
      text-align: center;
      text-decoration: none;
      display: inline-block;
      font-size: 16px;
    }
    th {
      width: 100px;
    }
  </style>
</head>
<body>
<form action="${base}/list" method="post">
  <input type="hidden" name="test_id" value="${test_id}">
  <p class="iss">
    <b>Issuer:</b> ${issuer}
  </p>
  <h3>You have to provide two things:</h3>
  <table>
    <tr>
      <th rowspan="2">Start page</th>
      <td>This is where the test tool should send the initial request</td>
    <tr>
      <td>
        <label for="start_page">Service provider start page:</label>
        <input type="text" name="start_page" value="${start_page}" size="60"/>
      </td>
    </tr>
    </p>
    </tr>
  </table>

  <h3>and</h3>

  <table>
    <tr>
      <th rowspan="2">Query parameter/-s</th>
      <td>
        If the relying party can be told to contact a specific Authorization
        Server it is ursually done using query parameters to the initial
        service all. This is where you can enter the parameter/-s.
        If you need to enter the issuers URL you can use &lt;issuer&gt; as
        a short cut.<br>
        Like this: issuer=&lt;issuer&gt; assuming that the parameters name is
        'issuer'
      </td>
    <tr>
      <td>
    <label for="params">Query parameter/-s:</label>
    <input type="text" name="params" value="${params}" size="60">
      </td>
    </tr>
    </p>
    </tr>
  </table>
  <p>
    Choose profile:
    <select name="profile">
      % for v in profiles:
        % if v == selected:
          <option value="${v}" selected>${v}</option>
        % else:
          <option value="${v}">${v}</option>
        % endif
      % endfor
    </select>
  </p>
    <p>
    Choose response_type: ${response_types()}
  </p>
  <button type="submit" value="Submit" class="button">Submit</button>
</form>
</body>
</html>