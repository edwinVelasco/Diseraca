

app.controller('PrestamosAdminContoller', function ($scope, $http) {
    $scope.listEdif = [];
    $scope.listSalas = [];


    $('#dia_sala_turno').change(function () {
         $http.get('get_turno_dia_sala?dia='+$(this).val()+"&sala="+$("#sala").val())
            .then(function(response) {
                $("#turno_sala_turno").material_select('destroy');
                $("#turno_sala_turno").html("");
                $('#turno_sala_turno').append("<option value=\"\" disabled selected>Seleccione</option>");
                for(turno in response.data){
                    $('#turno_sala_turno').append("<option value=\""+response.data[turno].id+"\">"+response.data[turno].time_start+" a "+response.data[turno].time_end+"</option>");
                }
                $('#turno_sala_turno').material_select();
            }, function(response) {
                //Second function handles error
                $scope.content = "Something went wrong";
            });

    });

    $scope.get_edif = function () {
        $http.get('get_edificios')
            .then(function(response) {
                $('#edificio').material_select('destroy');
                $('#edificio').html("");
                $('#edificio').append("<option value=\"\" disabled selected>Seleccione</option>");
                $scope.listEdif = response.data;
                for(edif in $scope.listEdif){
                    $('#edificio').append("<option value=\""+$scope.listEdif[edif].pk+"\">"+$scope.listEdif[edif].fields.codigo+"</option>");
                }
                $('#edificio').material_select();

            }, function(response) {
                //Second function handles error
                $scope.content = "Something went wrong";
            });
    };

    $('#edificio').change(function () {

        $http.get('get_salas?pk='+$(this).val())
            .then(function(response) {
                $scope.listSalas = response.data;

                $('#sala').material_select('destroy');
                $('#sala').html("");
                $('#sala').append("<option value=\"\" disabled selected>Seleccione</option>");

                for(sala in $scope.listSalas){
                    $('#sala').append("<option value=\""+$scope.listSalas[sala].pk+"\">"+
                        $scope.listSalas[sala].fields.codigo+"("+$scope.listSalas[sala].fields.capacidad+")"+"</option>");
                }
                $('#sala').material_select();
            }, function(response) {
                //Second function handles error
                $scope.content = "Something went wrong";
            });

    });

    $scope.get_edif();

    $scope.save_prestamo_masivo = function () {
        $http.post("save_prestamo_masivo", $("#formPrestamoMasivo").serialize())
            .then( function(data){
                if ("Notification" in window){
                    let ask = Notification.requestPermission();
                    ask.then(permission => {
                        if (permission ==='granted') {
                            let msg = new Notification('Mensaje', {
                                body: data.data.msg,
                                icon:"/static/img/ufps.jpg"
                            });
                        }
                    });
                }
            }, function(err){
                console.log(err);
                $('#dia').material_select();
            })
    };


});