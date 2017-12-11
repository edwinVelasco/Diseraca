/**
 * Created by wolf on 10/12/17.
 */

app.controller('BecasAdminContoller', function ($scope, $http) {
    $scope.listReporteBecas = [];
    $scope.listDetalleReporte = [];
    $scope.beca = "";


    $scope.getReporteBecas = function () {
        $http.get('get_report_becas')
            .then(function(response) {
                $scope.listReporteBecas = response.data.msg;

            }, function(response) {
                //Second function handles error
                $scope.content = "Something went wrong";
            });
    };

    $scope.verMasInfoTarde = function (id, nick) {
        $scope.beca = nick + " (LLegadas tarde)";
        $http.get('get_asistencias_tarde?id='+id)
            .then(function(response) {
                $scope.listDetalleReporte = response.data.msg;

            }, function(response) {
                //Second function handles error
                $scope.content = "Something went wrong";
            });
    };

    $scope.getReporteBecas();
    $scope.verMasInfoIn = function (id, nick) {
        $scope.beca = nick + " (Inasistencias)";
        $http.get('get_inasistencias_beca?id='+id)
            .then(function(response) {
                $scope.listDetalleReporte = response.data.msg;

            }, function(response) {
                //Second function handles error
                $scope.content = "Something went wrong";
            });
    }
});