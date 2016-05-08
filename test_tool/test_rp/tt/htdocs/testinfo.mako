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
  <hr>
  % if http_result != '':
    % if http_result.startswith('4') or http_result.startswith('5'):
      <b style="color:red">${http_result}</b>
    % else:
      <b style="color:green">${http_result}</b>
    % endif
  % endif
  <hr>
  ${events}
</div>
<!-- jQuery (necessary for Bootstrap's JavaScript plugins) -->
<script src="/static/jquery.min.1.9.1.js"></script>
<!-- Include all compiled plugins (below), or include individual files as needed -->
<script src="/static/bootstrap/js/bootstrap.min.js"></script>

</body>
</html>