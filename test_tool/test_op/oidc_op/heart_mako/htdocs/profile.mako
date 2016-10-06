<%
    PMAP = {
        "C": "Basic (code)", "I": "Implicit (id_token)",
        "IT": "Implicit (id_token+token)",
        "CI": "Hybrid (code+id_token)", "CT": "Hybrid (code+token)",
        "CIT": "Hybrid (code+id_token+token)"
    }
    PMAPL = ["C", "I", "IT", "CI", "CT", "CIT"]
    L2I = {"discovery": 1, "registration": 2}
    CRYPTSUPPORT = {"none": "n", "signing": "s", "encryption": "e"}

    def profile_form(prof):
        p = prof.split(".")
        el = ["<h3>Choose response_type:</h3>",
              '<form action="profile" method="POST">']
        for key in PMAPL:
            txt = PMAP[key]
            if key == p[0]:
                el.append('<input type="radio" name="rtype" value="%s" checked>%s<br>' % (key, txt))
            else:
                el.append('<input type="radio" name="rtype" value="%s">%s<br>' % (key, txt))
        el.append("<br>")
        el.append("These you can't change here:")
        el.append("<ul>")
        for mode in ["discovery", "registration"]:
            if p[L2I[mode]] == "T":
                el.append("<li>Dynamic %s" % mode)
            else:
                el.append("<li>Static %s" % mode)
        el.append("</ul><p>Cryptographic support:<br>")
        if len(p) == 3:
            vs = "sen"
        else:
            if p[3] == '':
                vs = "sen"
            else:
                vs = p[3]
        for name, typ in CRYPTSUPPORT.items():
            if typ in vs:
                el.append('<input type="checkbox" name="%s" checked>%s<br>' % (name, name))
            else:
                el.append('<input type="checkbox" name="%s">%s<br>' % (name, name))
        el.append("</p>")
        el.append('</ul><p>Check this if you want extra tests (not needed for any certification profiles): ')
        if len(p) == 5 and p[4] == "+":
            el.append('<input type="checkbox" name="extra" checked>')
        else:
            el.append('<input type="checkbox" name="extra">')
        el.append('</p>')
        el.append('<p><input type="submit" value="Continue"></p>')
        el.append('</form>')
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
    <title>HEART OIDC OP Test</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <!-- Bootstrap -->
    ${boot_strap(base)}
    <!-- HTML5 shim and Respond.js IE8 support of HTML5 elements and media queries -->
    <!--[if lt IE 9]>
      <script src="../../assets/js/html5shiv.js"></script>
      <script src="../../assets/js/respond.min.js"></script>
    <![endif]-->
  </head>
  <body>
    <div class="container">
     <!-- Main component for a primary marketing message or call to action -->
      <div class="jumbotron">
        <h1>HEART OIDC OP Test</h1>
          <h2>You can change the profile you are testing here:</h2>
          ${profile_form(profile)}
      </div>

    </div> <!-- /container -->
    ${postfix(base)}
  </body>
</html>