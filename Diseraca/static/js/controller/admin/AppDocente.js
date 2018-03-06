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
      $scope.listCargaDocenteShow = false;
      $scope.edit_carga_obj = {"carrera": "", "codigo": "", "grupo": "", "id": 0, "matriculados": 0, "nombre": ""};
      $scope.listCarreras = [];
      $scope.docenteCarga = "";
      $scope.cargaPk = 0;
      $scope.newCargaDocente = {};
      $scope.preload = true;
      $scope.docenteView = "";

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
                $http.get('get_turnos_docente?docente='+ $scope.consultaTurnos.docente+'&fecha_inicio='+$scope.consultaTurnos.fecha_inicio+'&fecha_fin='+$scope.consultaTurnos.fecha_fin)
                .then(function(response) {
                    $scope.listPrestamosDocente = response.data.msg;
                    $scope.docenteView = response.data.docente;
                    if (response.data.msg.length > 0)
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
                $scope.preload = false;
                $('#msg_inicial').modal('close');
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
                $scope.getDocentes();
                $scope.preload = true;
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

    $scope.saveCargaDocente = function () {
        //$scope.edit_carga_obj.carrera = $("#carreras_carga_docente").val();
        $('#register_carga_docente').modal('close');
        $http.post("save_carga_docente", $scope.edit_carga_obj)
            .then( function(data){
                console.log(data);
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
                $scope.buscarCargaDocente();
                $scope.edit_carga_obj = {"carrera": "", "codigo": "",
                    "grupo": "", "id": 0, "matriculados": 0, "nombre": ""};

            }, function(err){
                console.log(err);
            })
    };

    $scope.buscarCargaDocente = function () {

        $("#docente_carga").val($("#codigo_docente_buscar_carga").val());
         $http.get('buscar_carga_docente?docente='+$("#codigo_docente_buscar_carga").val())
            .then(function(response) {
                $scope.docenteView = response.data.docente;
                $scope.listCargaDocente = response.data.msg;
                if (response.data.length == 0){
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
                $scope.listCargaDocenteShow = true;
            }, function(response) {
                //Second function handles error
                $scope.content = "Something went wrong";
            });
    };

    $scope.get_carreras = function () {
        $http.get('get_carreras')
            .then(function(response) {
                $scope.listCarreras = response.data;
                $('#carreras_carga_docente').html('');
                //$('#carreras_carga_docente').append("<option disabled selected>Seleccione</option>");
                for(i in $scope.listCarreras){
                    $('#carreras_carga_docente').append("<option value=\""+$scope.listCarreras[i].codigo+"\">"+$scope.listCarreras[i].nombre+"</option>");
                }
                $('#carreras_carga_docente').material_select();

            }, function(response) {
                //Second function handles error
                $scope.content = "Something went wrong";
            });
    };
    $scope.get_carreras();

    $scope.new_register_carga = function () {
          $scope.edit_carga_obj = {"carrera": "", "codigo": "",
                    "grupo": "", "id": 0, "matriculados": 0, "nombre": "",
            "profesor": $("#codigo_docente_buscar_carga").val()};
          $scope.show_register_carga()
      };

    $scope.show_register_carga = function () {
        $('#register_carga_docente').modal('open');
    };

    $scope.edit_carga = function (obj) {
        //console.log(obj);
        $scope.edit_carga_obj = obj;
        $scope.edit_carga_obj.profesor = $("#codigo_docente_buscar_carga").val();
        //console.log($scope.edit_carga_obj);
        //console.log($scope.edit_carga_obj.id);
        //console.log($scope.edit_carga_obj.carrera);
          //$("#pk_carga").val(obj.id);
          //$("#carreras_carga_docente").val(obj.carrera);
          //$("#codigo_materia").val(obj.codigo);
          //$("#nombre_materia").val(obj.nombre);
          //$("#grupo_materia").val(obj.grupo);
          //$("#matriculados_materia").val(obj.matriculados);
          $scope.show_register_carga();
    };

    $scope.restaurar_password = function (codigo) {
        if($scope.newDocente.persona.codigo === ''){
            alert('Busque un docente');
            return
        }
        var r = confirm("Desea restaurar la contraseña, recuerde " +
            "que será el mismo codigo?");
        if (r == true) {
            $http.get('cambiar_password?codigo='+codigo)
            .then(function(response) {
                if ("Notification" in window){
                    let ask = Notification.requestPermission();
                    ask.then(permission => {
                        if (permission ==='granted') {
                            let msg = new Notification('Mensaje', {
                                body: response.data.msg,
                                icon:"/static/img/ufps.jpg"
                            });
                        }
                    });
                }
                $scope.getBecas();
            }, function(response) {
                //Second function handles error
                $scope.content = "Something went wrong";
            });
        }
    };


});