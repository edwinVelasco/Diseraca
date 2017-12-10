/**
 * Created by wolf on 10/12/17.
 */

app.controller('BecasAdminContoller', function ($scope, $http) {
    $scope.listReporteBecas = [];
    $scope.listDetalleReporte = [];


    $scope.getReporteBecas = function () {
        $http.get('get_report_becas')
            .then(function(response) {
                $scope.listReporteBecas = response.data.msg;

            }, function(response) {
                //Second function handles error
                $scope.content = "Something went wrong";
            });
    };

    $scope.verMasInfo = function (obj) {
        $http.get('get_semestres')
            .then(function(response) {
                $scope.listSemestres = response.data.msg;

            }, function(response) {
                //Second function handles error
                $scope.content = "Something went wrong";
            });
    };

    $scope.getReporteBecas();
});