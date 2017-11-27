/**
 * Created by wolf on 7/10/17.
 */
/**
 * Created by wolf on 16/09/17.
 */

  app.controller('DocenteAdminContoller', function ($scope, $http) {
      $scope.listDocentes = [];
      $scope.listDptos = [];
      $scope.consultaTurnos = {'fecha_inicio': '', 'fecha_fin': '', 'docente': ''};
      $scope.newDocente = {"pk": 0, 'tel': '', "persona": {"nombre": '', "codigo": '', 'email': ''},
          'dpto': {'codigo_dpto': '', 'nombre_dpto': ''}};
      $scope.fileDocentes = {'name': '', 'file': ''};
      $scope.fileCargaDocente = {'name': '', 'file': ''};
      $scope.showTableTurnoDocente = false;
      $scope.listCargaDocente = [];

      $scope.consultarTurnosDocente = function () {
          $scope.consultaTurnos.fecha_inicio = $("#fecha_inicio").val();
          $scope.consultaTurnos.fecha_fin = $("#fecha_fin").val();

            var bool = false;
            for(pro in $scope.listDocentes){
                if ($scope.consultaTurnos.docente == $scope.listDocentes[pro].persona.codigo){
                    bool = true;
                    break
                }
            }
            if (bool){
                console.log($scope.consultaTurnos);
                $http.get('get_turnos_docente?docente='+ $scope.consultaTurnos.docente+'&fecha_inicio='+$scope.consultaTurnos.fecha_inicio+'&fecha_fin='+$scope.consultaTurnos.fecha_fin)
                .then(function(response) {
                    $scope.listPrestamosDocente = response.data;
                    if (response.data.length > 0)
                    {
                        $scope.showTableTurnoDocente = true;
                    }
                    else{
                        $scope.showTableTurnoDocente = false;
                        if ("Notification" in window){
                            let ask = Notification.requestPermission();
                            ask.then(permission => {
                                if (permission ==='granted') {
                                    let msg = new Notification('Mensaje', {
                                        body: 'El docente no tiene prestamos registrados para el rango de fechas indicadas',
                                        icon:"/static/img/ufps.jpg"
                                    });
                                }
                            });
                        }
                    }

                }, function(response) {
                    //Second function handles error
                    $scope.content = "Something went wrong";
                });
            }
            else{
                if ("Notification" in window){
                        let ask = Notification.requestPermission();
                        ask.then(permission => {
                            if (permission ==='granted') {
                                let msg = new Notification('Mensaje', {
                                    body: 'El docente no se encuentra registrado',
                                    icon:"/static/img/ufps.jpg"
                                });
                            }
                        });
                    }
            }
        };

    $scope.getDocentes = function () {
        $http.get('get_docentes')
            .then(function(response) {
                $scope.listDocentes = response.data;
            }, function(response) {
                //Second function handles error
                $scope.content = "Something went wrong";
            });
    };

    $scope.getDepartamentos = function () {
          $http.get('get_dptos')
            .then(function(response) {
                $scope.listDptos = response.data;
                $('#dpto_docente').html('');
                $('#dpto_docente').append("<option value=\"\" disabled selected>Seleccione</option>");
                for(i in $scope.listDptos){
                    $('#dpto_docente').append("<option value=\""+$scope.listDptos[i].codigo+"\">"+$scope.listDptos[i].nombre+"</option>");
                }
                $('#dpto_docente').material_select();
            }, function(response) {
                //Second function handles error
                $scope.content = "Something went wrong";
            });
    };

    $scope.buscarDocenteEditar = function () {
        cod = $('#codigo_docente_buscar').val();

        var bool = false;

        for(pro in $scope.listDocentes){
            if (cod == $scope.listDocentes[pro].persona.codigo){
                $scope.newDocente = $scope.listDocentes[pro];
                bool = true;
                break
            }
        }
        if (bool){
            $('#dpto_docente').material_select('destroy');
            $('#dpto_docente').val($scope.newDocente.dpto.codigo_dpto);
            $('#saveDocente').val('Editar');
            $('#dpto_docente').material_select();
        }
        else{
            if ("Notification" in window){
                    let ask = Notification.requestPermission();
                    ask.then(permission => {
                        if (permission ==='granted') {
                            let msg = new Notification('Mensaje', {
                                body: 'El docente no se encuentra registrado',
                                icon:"/static/img/ufps.jpg"
                            });
                        }
                    });
                }
        }
    };

    $scope.getDocentes();

    $scope.getDepartamentos();

    $scope.newDocenteFunct = function () {
        $scope.newDocente = {"pk": 0, 'tel': '', "persona": {"nombre": '', "codigo": '', 'email': ''},
          'dpto': {'codigo_dpto': '', 'nombre_dpto': ''}};
        $('#dpto_docente').material_select('destroy');
        $('#dpto_docente').val('');
        $('#saveDocente').val('Guardar');
        $('#dpto_docente').material_select();
    };

    $scope.saveDocente = function () {
        $scope.newDocente.dpto.codigo_dpto = $('#dpto_docente').val();
        $http.post("save_docente", {data: $scope.newDocente})
            .then( function(data){
                $scope.newDocenteFunct();
                if ("Notification" in window){
                        let ask = Notification.requestPermission();
                        ask.then(permission => {
                            if (permission ==='granted') {
                                let msg = new Notification('Mensaje', {
                                    body: data.data,
                                    icon:"/static/img/ufps.jpg"
                                });
                            }
                        });
                    }
            }, function(err){
                console.log(err);
            })
    };

    $scope.buscarCargaDocente = function () {
         $http.get('buscar_carga_docente?docente='+$("#codigo_docente_buscar_carga").val())
            .then(function(response) {
                $scope.listCargaDocente = response.data;
                console.log($scope.listCargaDocente)
                if ($scope.listCargaDocente.length > 0){

                }
                else{
                    if ("Notification" in window){
                        let ask = Notification.requestPermission();
                        ask.then(permission => {
                            if (permission ==='granted') {
                                let msg = new Notification('Mensaje', {
                                    body: 'El docente no tiene carga academica',
                                    icon:"/static/img/ufps.jpg"
                                });
                            }
                        });
                    }
                }


            }, function(response) {
                //Second function handles error
                $scope.content = "Something went wrong";
            });
    }
});