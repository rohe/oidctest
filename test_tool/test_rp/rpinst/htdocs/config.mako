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
    LINK_INFO = [
    {
        'href':"{}/static/bootstrap/css/bootstrap.min.css",
        'rel':"stylesheet",
        'media':"screen"},
    {
        'href':"{}/static/style.css",
        'rel':"stylesheet",
        'media':"all"}
    ]

    def boot_strap(base):
        line = []
        for d in LINK_INFO:
            _href = d['href'].format(base)
            line.append('<link href={href} rel={rel} media={media}>'.format(
                 href=_href,rel=d['rel'],media=d['media']))
        return "\n".join(line)
%>

<%
    SCRIPT_INFO = ["{}/static/jquery.min.1.9.1.js", "{}/static/bootstrap/js/bootstrap.min.js"]

    def postfix(base):
        line = []
        for d in SCRIPT_INFO:
            _src = d.format(base)
            line.append('<script src={}></script>'.format(_src))
        return "\n".join(line)

    %>

<%
    def form_action(base):
        return '<form action="{}/list" method="post">'.format(base)
%>

<!DOCTYPE html>
<html>
<head>
  <title>HEART OIDC RP Tests</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <!-- Bootstrap -->
  ${boot_strap(base)}
  <!-- HTML5 shim and Respond.js IE8 support of HTML5 elements and media queries -->
  <!--[if lt IE 9]>
  <script src="../../assets/js/html5shiv.js"></script>
  <script src="../../assets/js/respond.min.js"></script>
  <![endif]-->
  <style>
    h3 {
      background-color: lightblue;
    }

    h4 {
      background-color: lightcyan;
    }

    @media (max-width: 768px) {
      .jumbotron {
        border-radius: 10px;
        margin-left: 4%;
        margin-right: 4%;
      }
    }

    @media (min-width: 768px) and (max-width: 1600px) {
      .jumbotron {
        border-radius: 10px;
        margin-left: 10%;
        margin-right: 10%;
      }
    }

    @media (min-width: 1600px) {
      .jumbotron {
        border-radius: 10px;
        margin-left: 20%;
        margin-right: 20%;
      }
    }
  </style>
</head>
<body>
<!-- Main component for a primary marketing message or call to action -->
<div class="jumbotron">
  ${form_action(base)}
    <input type="hidden" name="test_id" value="${test_id}">
    <b>Issuer:</b> ${issuer}
    <p>
      Service provider start page:<br>
      <input type="text" name="start_page" value="${start_page}" size="60"><br>
    </p>
    <p>
      If the relying party can be told to contact a specific Authorization
      Server it is ursually done using query parameters to the initial
      service all. This is where you can enter the parameter/-s.<br>
      If you need to enter the issuers URL you can use &lt;issuer&gt; as
      a short cut.<br>
      Like this: issuer=&lt;issuer&gt; assuming that the parameters name is
      'issuer'<br>
    </p>
    <p>
      Query parameter/-s:<br>
      <input type="text" name="params" value="${params}" size="60">
    </p>
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
    <input type="submit" value="Submit">
  </form>
</div>
${postfix(base)}
</body>
</html>