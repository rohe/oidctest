<%!

  def op_choice(base, flows):
    """
    Creates a list of test flows
    """
    _grp = "_"
    color = ['<img src="/static/black.png" alt="Black">',
             '<img src="/static/green.png" alt="Green">',
             '<img src="/static/yellow.png" alt="Yellow">',
             '<img src="/static/red.png" alt="Red">',
             '<img src="/static/qmark.jpg" alt="QuestionMark">',
             '<img src="/static/greybutton" alt="Grey">',
             ]
    line = [
        '<table>',
        '<tr><th>Status</th><th>Description</th><th>Info</th></tr>']

    for grp, state, desc, tid in flows:
        b = tid.split("-", 2)[1]
        if not grp == _grp:
            _grp = grp
            _item = '<td colspan="3" class="center"><b>{}</b></td>'.format(_grp)
            line.append(
                '<tr id="{}">{}</tr>'.format(b, _item))

        if state:
            _info = "<a href='{}test_info/{}'><img src='/static/info32.png'></a>".format(
                    base, tid)
        else:
            _info = ''

        _stat = "<a href='{}{}'>{}</a>".format(base, tid, color[state])
        line.append(
            '<tr><td>{}</td><td>{} ({})</td><td>{}</td></tr>'.format(
                _stat, desc, tid, _info))
    line.append('</table>')

    return "\n".join(line)
%>

<%!

    ICONS = [
    ('<img src="/static/black.png" alt="Black">',"The test has not been run"),
    ('<img src="/static/green.png" alt="Green">',"Success"),
    ('<img src="/static/yellow.png" alt="Yellow">',
    "Warning, something was not as expected"),
    ('<img src="/static/red.png" alt="Red">',"Failed"),
    ('<img src="/static/qmark.jpg" alt="QuestionMark">',
    "The test flow wasn't completed. This may have been expected or not"),
    ('<img src="/static/info32.png">',
    "Signals the fact that there are trace information available for the test"),
    ]

    def legends(base):
        element = "<table border='1'>"
        for icon, txt in ICONS:
            element += "<tr><td>{}</td><td>{}</td></tr>".format(icon, txt)
        element += '</table>'
        return element
%>

<!DOCTYPE html>
<html>
<head>
    <title>HEART OAuth2 RP Tests</title>
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
td.center {
    text-align: center;
    background-color: #a4aeaf;
}
      </style>

</head>
<body>

    <h1>HEART OAuth2 RP Tests</h1>
    <em>Explanations of legends at <a href="#legends">end of page</a></em>
    <hr class="separator">
    <h3>Run <a href="${base}/all">all</a> or chose the next test flow you want to
        run from this list:
    </h3>
    ${op_choice(base, flows)}
    <hr class="separator">
    <h3 id='legends'>Legends</h3>
    ${legends(base)}
</body>
</html>