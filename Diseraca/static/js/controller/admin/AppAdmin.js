/**
 * Created by wolf on 16/09/17.
 */
var app = angular.module('AppAdmin',[])
  .controller('TurnoController', function ($scope, $http) {
    $scope.newTurno = { model: "Diseraca.turno", pk: 0, fields: {dia: null, time_start: null, time_end: null, estado: 0} };
    $scope.dataTurnos = [];
    $scope.estado = ['Activo', 'Inactivo'];
    $scope.listEdif = [];
    $scope.newEdif = {model: null, pk: 0, fields: {codigo: null, nombre: null}};
    $scope.newSala = {model: null, pk: 0, fields: {edificio: null, codigo: null,  capacidad: 1, tipo: null, estado: null}};
    $scope.listSalas = [];
    $scope.estadoSalas = ["Activo", "Mantenimiento", "Fuera de Serv."];
    $scope.tiposSalas = ["Sala de Clase", "Aula virtual", "Auditorio"];
    $scope.verhasta = true;
    $scope.estadoSalaTurno = ["Activado", "Desactivado", "Temporal"];
    $scope.listTurnosSala = [];
    $scope.lisDias = ["Lun", "Mar", "Mie", "Jue", "Vie", "Sab"];
    $scope.showPagination = [0, 9];
    $scope.newSalaTurno = {"pk": 0, "fields": {"estado": "", "desde": null,
                            "hasta": null, "sala": {"codigo": "", "edificio": "", "pk": ""},
                            "turno": {"time_start": "", "time_end": "", "dia": "", "pk": ""}}};

    $scope.turn_day_sala = 0;

    $scope.get_turn_day = function (day) {
        $http.get('get_turno_dia?dia='+day)
            .then(function(response) {
                $scope.dataTurnos = response.data;
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
    $scope.edit_turn = function (obj) {
        $('#dia').material_select('destroy');
        //$('#dia').html(null);

        $scope.newTurno = obj[0][0];
        $('#dia').val(String($scope.newTurno.fields.dia));
        $('#dia').material_select();

    };
    $scope.saveTurno = function (obj) {
            $('#dia').material_select('destroy');
            console.log($('#dia').val());
            $scope.newTurno.fields.dia = $('#dia').val();

            $http.post("save_turno", {turno: $scope.newTurno})
                .then( function(data){
                    $scope.newTurno= { model: "Diseraca.turno", pk: 0, fields:
                        {"dia": null, time_start: null, time_end: null, estado: 0}
                    };
                    console.log(data);
                    $('#dia').val("0");
                    $('#dia').material_select();
                    if ("Notification" in window){
                        let ask = Notification.requestPermission();
                        ask.then(permission => {
                            if (permission ==='granted') {
                                let msg = new Notification('bienvenido/a', {
                                    body: data.data,
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
    $scope.newTurnoFrom = function () {
        $scope.newTurno = { model: "Diseraca.turno", pk: 0, fields: {dia: null, time_start: null, time_end: null, estado: 0} };
        $('#dia').material_select('destroy');
        $('#dia').val(String($scope.newTurno.fields.dia));
        $('#dia').material_select();
    };


    //gestion de edificios.
    $scope.get_edif = function () {
        $http.get('get_edificios')
            .then(function(response) {
                $('#edif').material_select('destroy');
                $('#edif_sala_turno').material_select('destroy');
                $('#edif').html("");
                $('#edif_sala_turno').html("");
                $('#edif').append("<option value=\"\" disabled selected>Seleccione</option>");
                $('#edif_sala_turno').append("<option value=\"\" disabled selected>Seleccione</option>");
                $scope.listEdif = response.data;
                for(edif in $scope.listEdif){
                    $('#edif').append("<option value=\""+$scope.listEdif[edif].pk+"\">"+$scope.listEdif[edif].fields.codigo+"</option>");
                    $("#edif_sala_turno").append("<option value=\""+$scope.listEdif[edif].pk+"\">"+$scope.listEdif[edif].fields.codigo+"</option>");
                }
                $('#edif').material_select();
                $('#edif_sala_turno').material_select();

            }, function(response) {
                //Second function handles error
                $scope.content = "Something went wrong";
            });
    };
    $scope.saveEdif = function () {
        $http.post("save_edificio", {edif: $scope.newEdif})
            .then( function(data){
                $scope.newEdifFunct()
                console.log(data);
                $scope.get_edif();
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
                $('#dia').material_select();
            })
    };
    $scope.newEdifFunct = function () {
        $scope.newEdif = {model: null, pk: 0, fields: {codigo: null, nombre: null}};
    };

    //gestion de Salas
    $scope.get_salas = function (edif) {
        $scope.newEdif = edif;
        $http.get('get_salas?pk='+edif.pk)
            .then(function(response) {
                $scope.listSalas = response.data;
            }, function(response) {
                //Second function handles error
                $scope.content = "Something went wrong";
            });
    };
    $scope.newSalaFunct = function () {
        $scope.newSala = {model: null, pk: 0, fields: {edificio: null, codigo: null,  capacidad: 1, tipo: null, estado: null}};
        $('#edif').material_select('destroy');
        $('#tipo_sala').material_select('destroy');
        $('#estado_sala').material_select('destroy');

        $('#edif').val($scope.newSala.fields.edificio);
        $('#tipo_sala').val($scope.newSala.fields.tipo);
        $('#estado_sala').val($scope.newSala.fields.estado);

        $('#edif').material_select();
        $('#tipo_sala').material_select();
        $('#estado_sala').material_select();
      };
    $scope.edit_sala = function (obj) {
        $scope.newSala = obj;
        $('#edif').material_select('destroy');
        $('#tipo_sala').material_select('destroy');
        $('#estado_sala').material_select('destroy');

        $('#edif').val($scope.newSala.fields.edificio);
        $('#tipo_sala').val($scope.newSala.fields.tipo);
        $('#estado_sala').val($scope.newSala.fields.estado);

        $('#edif').material_select();
        $('#tipo_sala').material_select();
        $('#estado_sala').material_select();
    };
    $scope.save_sala = function () {
        $scope.newSala.fields.edificio = $("#edif").val();
        $scope.newSala.fields.tipo = $("#tipo_sala").val();
        $scope.newSala.fields.estado = $("#estado_sala").val();
        $http.post("save_sala", {sala: $scope.newSala})
            .then( function(data){
                $scope.newSalaFunct()
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

    $scope.get_turn_day(0);
    $scope.get_edif();
    $("#edif_sala_turno").change(function() {
        $http.get('get_salas?pk='+$(this).val())
            .then(function(response) {
                $("#sala_sala_turno").material_select('destroy');
                $("#sala_sala_turno").html("");
                $('#sala_sala_turno').append("<option value=\"\" disabled selected>Seleccione</option>");
                for(sala in response.data){
                    $('#sala_sala_turno').append("<option value=\""+response.data[sala].pk+"\">"+response.data[sala].fields.codigo+"</option>");
                }
                $('#sala_sala_turno').material_select();
            }, function(response) {
                //Second function handles error
                $scope.content = "Something went wrong";
            });
    });
    $('#dia_sala_turno').change(function () {
         $http.get('get_turno_dia?dia='+$(this).val())
            .then(function(response) {
                $("#turno_sala_turno").material_select('destroy');
                $("#turno_sala_turno").html("");
                $('#turno_sala_turno').append("<option value=\"\" disabled selected>Seleccione</option>");
                for(turno in response.data){
                    $('#turno_sala_turno').append("<option value=\""+response.data[turno].pk+"\">"+response.data[turno].fields.time_start+" a "+response.data[turno].fields.time_end+"</option>");
                }
                $('#turno_sala_turno').material_select();
            }, function(response) {
                //Second function handles error
                $scope.content = "Something went wrong";
            });

    });
    $("#estado_sala_turno").change(function () {
        console.log($(this).val());
        if($(this).val()==2){
            $scope.verhasta = false;
        }
        else{
            console.log("else");
            $scope.verhasta = true;
        }

    });
    $scope.get_turn_sala = function (sala) {
        $http.get('get_turno_sala?sala='+sala)
            .then(function(response) {
                $scope.listTurnosSala = response.data;
                $scope.get_turn_day_sala(0);
            }, function(response) {
                //Second function handles error
                $scope.content = "Something went wrong";
            });
    };
    $scope.newSalaTurnoFrom = function () {
        $scope.newSalaTurno = {"pk": 0, "fields": {"estado": "", "desde": null, "hasta": null, "sala": {"codigo": "", "edificio": "", "pk": ""},
                            "turno": {"time_start": "", "time_end": "", "dia": "", "pk": ""}}};
        $scope.get_edif();
        $('#sala_sala_turno').material_select('destroy');
        $('#dia_sala_turno').material_select('destroy');
        $('#turno_sala_turno').material_select('destroy');
        $('#estado_sala_turno').material_select('destroy');

        $('#sala_sala_turno').html("");
        $('#dia_sala_turno').val("");
        $('#estado_sala_turno').val("");
        $('#turno_sala_turno').html("");

        $('#sala_sala_turno').material_select();
        $('#dia_sala_turno').material_select();
        $('#turno_sala_turno').material_select();
        $('#estado_sala_turno').material_select();
    };

    $scope.edit_sala_turno = function (obj) {
        $scope.newSalaTurno = obj;
        $('#edif_sala_turno').material_select('destroy');
        $('#edif_sala_turno').val(obj.fields.sala.edificio);
        $("#edif_sala_turno").change();
        $('#edif_sala_turno').material_select();

        $('#dia_sala_turno').material_select('destroy');
        $('#dia_sala_turno').val(obj.fields.turno.dia);
        $("#dia_sala_turno").change();
        $('#dia_sala_turno').material_select();

        $('#estado_sala_turno').material_select('destroy');
        $('#estado_sala_turno').val(obj.fields.estado);
        $('#estado_sala_turno').material_select();
        //$scope.edit_sala_turno_2();
        setTimeout(function(){$scope.edit_sala_turno_2()},300);
    };

    $scope.edit_sala_turno_2 = function () {
        $('#sala_sala_turno').material_select('destroy');
        $('#sala_sala_turno').val($scope.newSalaTurno.fields.sala.pk);
        $('#sala_sala_turno').material_select();

        $('#turno_sala_turno').material_select('destroy');
        $('#turno_sala_turno').val($scope.newSalaTurno.fields.turno.pk);
        $('#turno_sala_turno').material_select();
    };

    $scope.get_turn_day_sala = function (day) {
        $scope.turn_day_sala = day;
        $("#pag_turn_day_sala_0").removeAttr('class', 'active');
        $("#pag_turn_day_sala_1").removeAttr('class', 'active');
        $("#pag_turn_day_sala_2").removeAttr('class', 'active');
        $("#pag_turn_day_sala_3").removeAttr('class', 'active');
        $("#pag_turn_day_sala_4").removeAttr('class', 'active');
        $("#pag_turn_day_sala_5").removeAttr('class', 'active');
        $("#pag_turn_day_sala_"+day).attr('class', 'active');
    };

    $scope.saveSalaTurnoFrom = function () {
        $scope.newSalaTurno.fields.sala.edificio = $('#edif_sala_turno').val();
        $scope.newSalaTurno.fields.turno.dia = $('#dia_sala_turno').val();
        $scope.newSalaTurno.fields.estado = $('#estado_sala_turno').val();
        $scope.newSalaTurno.fields.sala.pk = $('#sala_sala_turno').val();
        $scope.newSalaTurno.fields.turno.pk = $('#turno_sala_turno').val();
        $scope.newSalaTurno.fields.hasta= $('#hasta_sala_turno').val();
        $scope.newSalaTurno.fields.desde= $('#desde_sala_turno').val();
        $http.post("save_salaTurno_turno", {data: $scope.newSalaTurno})
            .then( function(data){
                $scope.newSalaTurnoFrom();
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


});

     app.config(['$interpolateProvider', '$httpProvider',function ($interpolateProvider, $httpProvider) {
        //configuramos los símbolos
         $interpolateProvider.startSymbol('[[');
         $interpolateProvider.endSymbol(']]');
         //configuramos el CSRFTOKEN para las peticiones con ANGULARJS
         $httpProvider.defaults.xsrfCookieName = 'csrftoken';
         $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
         $httpProvider.defaults.withCredentials = true;
         $httpProvider.defaults.cache=false;
         $httpProvider.defaults.headers.post['Content-Type'] = 'application/x-www-form-urlencoded;charset=utf-8';
         //función para compatibilidad de transmisión de datos JSON por POST
         var param = function(obj) {
             var query = '', name, value, fullSubName, subName, subValue, innerObj, i;
             for(name in obj) {
                 value = obj[name];
                if(value instanceof Array) {
                    for(i=0; i<value.length; ++i) {
                      subValue = value[i];
                      fullSubName = name + '[' + i + ']';
                      innerObj = {};
                      innerObj[fullSubName] = subValue;
                      query += param(innerObj) + '&';
                    }
                    }
                else if(value instanceof Object) {
                    for(subName in value) {
                      subValue = value[subName];
                      fullSubName = name + '[' + subName + ']';
                      innerObj = {};
                      innerObj[fullSubName] = subValue;
                      query += param(innerObj) + '&';
                    }
                }
                else if(value !== undefined && value !== null)
                    query += encodeURIComponent(name) + '=' + encodeURIComponent(value) + '&';
                }
             return query.length ? query.substr(0, query.length - 1) : query;
         };

         // Override $http service's default transformRequest
         $httpProvider.defaults.transformRequest = [function(data) {
             return angular.isObject(data) && String(data) !== '[object File]' ? param(data) : data;
            }];
     }]);