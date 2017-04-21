<%!

def op_choice(base, nodes, test_info, headlines):
    """
    Creates a list of test flows
    """
    _grp = "_"
    IMG = [
        {'src':"{}/static/black.png",'alt':"Black"},
        {'src':"{}/static/green.png", 'alt':"Green"},
        {'src':'{}/static/yellow.png', 'alt':"Yellow"},
        {'src':"{}/static/red.png", 'alt':"Red"},
        {'src':"{}/static/qmark.jpg", 'alt':"QuestionMark"},
        {'src':"/static/greybutton", 'alt':'Grey'}
    ]
    element = ["<ul>"]
    color_pat = '<img src="{src}" alt="{alt}">'

    for node in nodes:
        # 4 or more parts
        p1, grp, spec = node.name.split("-", 2)
        if not grp == _grp:
            _grp = grp
            element.append("<hr size=2><h3 id='%s'>%s</h3>" % (_grp,
              headlines[_grp]))

        _src = IMG[node.state]['src'].format(base)
        _col = color_pat.format(src=_src,alt=IMG[node.state]['alt'])
        element.append("<li><a href='%s/%s'>%s</a>%s (%s) " % (base,
            node.name, _col, node.desc, node.name))

        if node.rmc:
            element.append('<img src="{}/static/delete-icon.png">'.format(base))
        if node.experr:
            element.append('<img src="{}/static/beware.png">'.format(base))
        if node.name in test_info:
            element.append("<a href='%stest_info/%s'><img src='static/info32.png'></a>" % (
                    base, node.name))

    element.append("</select>")
    return "\n".join(element)
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
    PMAP = {
        "C": "Basic (code)", "I": "Implicit (id_token)",
        "IT": "Implicit (id_token+token)",
        "CI": "Hybrid (code+id_token)", "CT": "Hybrid (code+token)",
        "CIT": "Hybrid (code+id_token+token)"
    }

    L2I = {"webfinger": 1, "discovery": 2, "registration": 3}
    CM = {"n": "none", "s": "sign", "e": "encrypt"}

    def display_profile(spec):
        el = ["<p><ul>"]
        p = spec.split('.')
        el.append("<li> %s" % PMAP[p[0]])
        for mode in ["webfinger", "discovery", "registration"]:
            if p[L2I[mode]] == "T":
                el.append("<li> Dynamic %s" % mode)
            else:
                el.append("<li> Static %s" % mode)
        if len(p) > 4:
            if p[4]:
                el.append("<li> crypto support %s" % [CM[x] for x in p[4]])
        if len(p) == 6:
            if p[5] == '+':
                el.append("<li> extra tests")
        el.append("</ul></p>")

        return "\n".join(el)
%>

<%
    def results(nodes, testresults):
        res = dict([(s, 0) for s in testresults.keys()])
        res[0] = 0

        for node in nodes:
            res[node.state] += 1

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
    <title>HEART OIDC OP Tests</title>
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
        <h1>HEART OIDC OP Tests</h1>
        <em>Explanations of legends at <a href="#legends">end of page</a></em>
        <hr class="separator">
        <h3><a href="${base}log">Logs</a> from earlier runs</h3>
        <h3>Chose the next test flow you want to run from this list: </h3>
        ${op_choice(base, flows, test_info, headlines)}
        <hr class="separator">
        <h3>Legends</h3>
        ${legends(base)}
    </div>
  ${postfix(base)}
</body>
</html>