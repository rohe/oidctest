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


<!DOCTYPE html>
<html>
<head>
  <title>HEART OAuth2 RP Tests</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <!-- Bootstrap -->
  <link href="static/bootstrap/css/bootstrap.min.css" rel="stylesheet"
        media="screen">
  <link href="static/style.css" rel="stylesheet" media="all">

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
  <form action="list" method="post">
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
          <option value="${v}">${v}</option>
        % endfor
      </select>
    </p>
    <input type="submit" value="Submit">
  </form>
</div>
<!-- jQuery (necessary for Bootstrap's JavaScript plugins) -->
<script src="/static/jquery.min.1.9.1.js"></script>
<!-- Include all compiled plugins (below), or include individual files as needed -->
<script src="/static/bootstrap/js/bootstrap.min.js"></script>

</body>
</html>