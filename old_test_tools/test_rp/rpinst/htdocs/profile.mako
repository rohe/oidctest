<%!
  def inputs(spec, selected):
  """
  Creates list of choices
  """

  l = list(spec.keys())
  l.sort()

  element = []
  for key in l:
    if spec[key] == [True, False]:
      element.append("<p><b>{}</b>".format(key))
      for val in ['True', 'False']:
        _txt = "<input type=\"radio\" name=\"{}\" value=\"{}\"".format(key, val)
        if key in selected:
          if val == 'True' and selected[key]:
            _txt += ' checked'
          elif val == 'False' and not selected[key]:
            _txt += ' checked'
        _txt += ">{}".format(val)
        element.append(_txt)
      element.append("</p>")
    else:
      element.append("<p><b>{}</b><br>".format(key))
      element.append("<ul>")
      values = list(spec[key])
      values.sort()
      for v in values:
        _txt = "<li><input type=\"checkbox\" name=\"{}\" value=\"{}\"".format(
          key,v)
        if key in selected:
          if v in selected[key]:
            _txt += " checked"
        _txt += ">{}".format(v)
        element.append(_txt)
      element.append("</ul></p>")

  return "\n".join(element)
%>

<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>OP profile</title>
</head>
<body>
<form action="profile">
  <input type="hidden" name="_id_" value="${id}">
  ${inputs(specs, selected)}
  <input type="submit" value="Submit">
</form>
</body>
</html>