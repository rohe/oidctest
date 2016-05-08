## index.html
<%inherit file="base.mako"/>

<%block name="script">
</%block>

<%block name="css">
  <!-- Add more css imports here! -->
  <link rel="stylesheet" type="text/css" href="/static/rp_test_list.css">
</%block>

<%block name="title">
  OpenID Certification OP Test Tool Configuration
</%block>

<%block name="header">
  ${parent.header()}
</%block>

<%block name="headline">
  <div ng-controller="IndexCtrl">
</%block>


<%block name="body">

  <div class="header">
    <h1>Third-party initiated login</h1>
    Add the RP initiate login endpoint to the textfield and click Login
    <div>
      <input type="text" class="form-control" ng-model="login_url">
      <div>
        <button type="button" class="btn btn-primary"
                ng-click="init_login(login_url)">Login
        </button>
      </div>
    </div>
  </div>

</%block>

<%block name="footer">
  </div>

  <script type="text/javascript"
          src="/static/rp_3rd_party_init_login.js"></script>

  ${parent.footer()}
</%block>