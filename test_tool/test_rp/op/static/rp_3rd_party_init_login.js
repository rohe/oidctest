var app = angular.module('main', []);

app.controller('IndexCtrl', function ($scope, $log) {
    $scope.login_url = "";
    $scope.$log = $log;

    $scope.init_login = function (url) {
        var op_adress = window.location.href
        op_adress = op_adress.split("/")
        op_adress = op_adress[0] + "//" + op_adress[2] + "/rp-support_3rd_party_init_login/_/_/_/normal"
        var init_login_req = url + "?iss=" + op_adress
        //$scope.$log.log(init_login_req)
        window.location.href = init_login_req;
    };
})