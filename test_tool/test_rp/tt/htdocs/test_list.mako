<%!

def op_choice(key_list, test_spec, test_info):
    """
    Creates a list of tests
    """

    element = "<ul>"

    for key in key_list:
        _info = test_spec[key]
        element += "<li><a href='rp?id=%s'>%s</a>(%s) " % (key, _info['descr'], key)

        if key in test_info:
            element += "<a href='%stest_info/%s'><img src='static/info32.png'></a>" % (
                    base, key)

    element += "</select>"
    return element
%>


<!DOCTYPE html>
<html>
<head>
    <title>HEART OAuth2 RP Tests</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <!-- Bootstrap -->
    <link href="static/bootstrap/css/bootstrap.min.css" rel="stylesheet" media="screen">
    <link href="static/style.css" rel="stylesheet" media="all">

    <!-- HTML5 shim and Respond.js IE8 support of HTML5 elements and media queries -->
    <!--[if lt IE 9]>
    <script src="../../assets/js/html5shiv.js"></script>
    <script src="../../assets/js/respond.min.js"></script>
    <![endif]-->
    <style>
        @media (max-width: 768px) {
            .jumbotron {
                border-radius: 10px;
                margin-left: 4%;
                margin-right: 4%;
            }
        }
        @media (min-width: 768px) and (max-width: 1600px){
            .jumbotron {
                border-radius: 10px;
                margin-left: 10%;
                margin-right: 10%;
            }
        }
        @media (min-width: 1600px){
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
        <h1>HEART OAuth2 RP Tests</h1>
        <h3>Chose the next test flow you want to run from this list: </h3>
        ${op_choice(key_list, test_spec, test_info)}
    </div>
    <!-- jQuery (necessary for Bootstrap's JavaScript plugins) -->
    <script src="/static/jquery.min.1.9.1.js"></script>
    <!-- Include all compiled plugins (below), or include individual files as needed -->
    <script src="/static/bootstrap/js/bootstrap.min.js"></script>

</body>
</html>