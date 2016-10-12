<%!
    IMG = [
        {'src':"{}/static/black.png",'alt':"Black"},
        {'src':"{}/static/green.png", 'alt':"Green"},
        {'src':'{}/static/yellow.png', 'alt':"Yellow"},
        {'src':"{}/static/red.png", 'alt':"Red"},
        {'src':"{}/static/qmark.jpg", 'alt':"QuestionMark"},
        {'src':"/static/greybutton", 'alt':'Grey'}
    ]

    def op_choice(base, nodes, test_info, headlines):
        """
        Creates a list of test flows
        """

        _grp = "_"
        color_pat = '<img src="{src}" alt="{alt}">'
        element = "<ul>"

        for node in nodes:
            # 4 or more parts
            typ, grp, spec = node.name.split("-", 2)
            if not grp == _grp:
                _grp = grp
                element += "<hr size=2><h3 id='%s'>%s</h3>" % (_grp, headlines[_grp])
            _src = IMG[node.state]['src'].format(base)
            _col = color_pat.format(src=_src,alt=IMG[node.state]['alt'])
            element += "<li><a href='%s/%s'>%s</a>%s (%s) " % (base,
                node.name, _col, node.desc, node.name)

            if node.rmc:
                element += '<img src="{}/static/delete-icon.png">'.format(base)
            if node.experr:
                element += '<img src="{}/static/beware.png">'.format(base)
            if node.name in test_info:
                element += "<a href='%s/test_info/%s'><img src='%s/static/info32.png'></a>" % (
                        base, node.name, base)
            #if node.mti == "MUST":
            #    element += '<img src="static/must.jpeg">'

        element += "</select>"
        return element
%>

<%!

    ICONS = [
    ('<img src="{}/static/black.png" alt="Black">',"The test has not been run"),
    ('<img src="{}/static/green.png" alt="Green">',"Success"),
    ('<img src="{}/static/yellow.png" alt="Yellow">',
    "Warning, something was not as expected"),
    ('<img src="{}/static/red.png" alt="Red">',"Failed"),
    ('<img src="{}/static/qmark.jpg" alt="QuestionMark">',
    "The test flow wasn't completed. This may have been expected or not"),
    ('<img src="{}/static/info32.png">',
    "Signals the fact that there are trace information available for the test"),
    ]

    def legends(base):
        element = "<table border='1' id='legends'>"
        for icon, txt in ICONS:
            element += "<tr><td>%s</td><td>%s</td></tr>" % (icon.format(base), txt)
        element += '</table>'
        return element
%>

<%
    def results(tests, testresults):
        res = dict([(s, 0) for s in testresults.keys()])
        res[0] = 0

        for test in tests:
            res[test.state] += 1

        el = []
        for i in range(1, len(res)):
            el.append("<p>%s: %d</p>" % (testresults[i], res[i]))
        el.append("<p>Not run: %d</p>" % res[0])

        return "\n".join(el)
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
    <h1>HEART OIDC RP Tests</h1>
    <em>Explanations of legends at <a href="#legends">end of page</a></em>
    <hr class="separator">
    <h3>Run <a href="${base}/all">all</a> or chose the next test flow you want to
        run from this list:
    </h3>
    ${op_choice(base, tests, test_info, headlines)}
    <hr class="separator">
    <h3>Legends</h3>
    ${legends(base)}
</div>
${postfix(base)}
</body>
</html>