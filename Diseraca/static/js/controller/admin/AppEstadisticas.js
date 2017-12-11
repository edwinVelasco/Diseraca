/**
 * Created by wolf on 9/12/17.
 */

app.controller('EstadisticaAdminContoller', function ($scope, $http) {
    $scope.NewSemester = {};
    $scope.listSemestres = [];


    $scope.SaveNewSemester = function () {
        $scope.NewSemester.fecha_inicio = $("#fecha_inicio").val();
        $scope.NewSemester.fecha_fin = $("#fecha_fin").val();
        var data = JSON.constructor($scope.NewSemester);
        $http.post("save_semester", data)
            .then( function(data){
                //$scope.newDocenteFunct();
                if ("Notification" in window){
                        var ask = Notification.requestPermission();
                        ask.then(permission => {
                            if (permission ==='granted') {
                                var msg = new Notification('Mensaje', {
                                    body: data.data.msg,
                                    icon:"/static/img/ufps.jpg"
                                });
                            }
                        });
                    }
                $scope.clearFormNewSemestre();
                $scope.getSemestres();

            }, function(err){
                console.log(err);
            })
    };


    $scope.getSemestres = function () {
        $http.get('get_semestres')
            .then(function(response) {
                $scope.listSemestres = response.data.msg;

            }, function(response) {
                //Second function handles error
                $scope.content = "Something went wrong";
            });
    };

    $scope.editSemestre = function (obj) {
        $scope.NewSemester = obj;
        $("#buttonNewSemestre").val("Editar")
    };

    $scope.getSemestres();

    $scope.clearFormNewSemestre = function () {
        $scope.NewSemester = {};
        $("#buttonNewSemestre").val("Guardar");
    };

});