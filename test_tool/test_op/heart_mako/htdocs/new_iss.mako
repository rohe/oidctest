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
    def form_action(base):
        return '<form action="{}/create">'.format(base)
%>

<!DOCTYPE html>
<html>
<head>
  <title>OpenID Certification OP Test Tool Configuration</title>
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
  <h2>OpenID Connect Provider Certification</h2>
        <br>

        <p>
            This is a tool used for testing the compliance of an OpenID Connect Provider with the
            OpenID Connect specifications. In order to start testing you need to configure a test
            instance. Enter the issuer URL to the OpenID Connect Provider you want to test.
        </p>
        <br>
  ${form_action(base)}
    <h3>Issuer URL (without .well-known):</h3>
    <input type="text" name="iss">
    <br>
    <h3>An identifier of this specific configuration in the case that you want to have more then one</h3>
    <input type="text" name="tag" value="default">
  <br>
    <p>
      Choose what your OP supports:
      <table border="1">
            <tr><th>WebFinger</th><td style="width:30px"><input type="checkbox" name="webfinger"></td></tr>
    </table>
    <input type="hidden" name="discovery" value="on">
    <input type="hidden" name="registration" value="'on">
  <br>
  <h3>Choose a return type</h3>
  <br>
    <table broder="1">
            <tr><th style="width:100px">Return type</th><td>
                <input type="radio" name="return_type" value="C"> Code <br>
                <input type="radio" name="return_type" value="I"> IdToken <br>
                <input type="radio" name="return_type" value="IT"> IdToken Token <br>
                <input type="radio" name="return_type" value="CI"> Code IdToken <br>
                <input type="radio" name="return_type" value="CT"> Code Token <br>
                <input type="radio" name="return_type" value="CIT"> Code IdToken Token
            </td></tr>
        </table>
      </p>
    <input type="submit" value="Submit">
  </form>
</div>
<script src="/static/jquery.min.1.9.1.js"></script>
<script src="/static/bootstrap/js/bootstrap.min.js"></script>
</body>
</html>