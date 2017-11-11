var app = angular.module('AppAdmin',[])
  .controller('TurnoController', function ($scope, $http) {
    $scope.newTurno = {"id": "0", "time_start": null , "time_end": null, "dia": null , "estado": 0 };
    $scope.dataTurnos = [];

    $scope.get_turn_day = function (day) {
        $("#tablaTurnos").html("");
        $http.get('get_turno_dia?dia='+day)
            .then(function(response) {
                $scope.dataTurnos = response.data;

                for(i=0; i < response.data.length; i++){
                    x = '<tr><td>'+response.data[i].fields.time_start+'-'+ response.data[i].fields.time_end+'</td><td>';
                    if(response.data[i].fields.estado == 0){
                        x += 'Activo</td>';
                    }
                    else{
                        x += 'Inactivo</td>';
                    }
                    x += "<td>"+"<a class=\"green-text tooltipped\" data-position=\"bottom\" data-delay=\"50\" data-tooltip=\"Editar Turno\">"+
                                "<i class=\"material-icons\" ng-click='edit_turn("+response.data[i].pk+")'>edit</i></a></td></tr>";

                    angular.element("tablaTurnos").append(x);

                }
                $("#pag_0").removeAttr('class', 'active');
                $("#pag_1").removeAttr('class', 'active');
                $("#pag_2").removeAttr('class', 'active');
                $("#pag_3").removeAttr('class', 'active');
                $("#pag_4").removeAttr('class', 'active');
                $("#pag_5").removeAttr('class', 'active');

                $("#pag_"+day).attr('class', 'active');

            }, function(response) {
                //Second function handles error
                $scope.content = "Something went wrong";
            });
    };
    $scope.get_turn_day(0);

    $scope.edit_turn = function (id) {
        console.log("edit_turn");
        for(i=0; i < $scope.dataTurnos.length; i++){
            console.log($scope.dataTurnos[i]);
            if($scope.dataTurnos[i].pk == id){
                console.log($scope.dataTurnos[i]);
                $scope.newTurno.id = id;
                $scope.newTurno.time_start = $scope.dataTurnos[i].fields.time_start;
                $scope.newTurno.time_end = $scope.dataTurnos[i].fields.time_end;
                $scope.newTurno.dia = $scope.dataTurnos[i].fields.dia;
                $scope.newTurno.estado = $scope.dataTurnos[i].fields.estado;
                break
            }
        }

    };
});
     app.config(['$interpolateProvider', '$httpProvider',function ($interpolateProvider, $httpProvider) {
        //configuramos los símbolos
         $interpolateProvider.startSymbol('[[');
         $interpolateProvider.endSymbol(']]');
         //configuramos el CSRFTOKEN para las peticiones con ANGULARJS
         //$httpProvider.defaults.xsrfCookieName = 'csrftoken';
         //$httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
         //$httpProvider.defaults.withCredentials = true;
         //$httpProvider.defaults.cache=true;
         //$httpProvider.defaults.headers.post['Content-Type'] = 'application/x-www-form-urlencoded;charset=utf-8';

     }]);