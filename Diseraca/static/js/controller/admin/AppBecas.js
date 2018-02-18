/**
 * Created by wolf on 10/12/17.
 */

app.controller('BecasAdminContoller', function ($scope, $http) {
    $scope.listReporteBecas = [];
    $scope.listDetalleReporte = [];
    $scope.beca = "";
    $scope.listBecas = [];
    $scope.listIp = [];
    $scope.ipAdd = {id:0, ip: ""};
    $scope.becaAdd = {id: 0, tel: "", nick: "", cc: "", persona: {nombre: "", codigo: "", email: ""}};
    $scope.adminAdd = {id: 0, codigo: "", nombre: "", email: ""};
    $scope.listAdmin = [];

    $scope.getReporteBecas = function () {
        $http.get('get_report_becas')
            .then(function(response) {
                $scope.listReporteBecas = response.data.msg;

            }, function(response) {
                //Second function handles error
                $scope.content = "Something went wrong";
            });
    };

    $scope.getIps = function () {
        $http.get('get_ips')
            .then(function(response) {
                $scope.listIp = response.data.msg;

            }, function(response) {
                //Second function handles error
                $scope.content = "Something went wrong";
            });
    };

    $scope.getBecas = function () {
        $http.get('get_becas')
            .then(function(response) {
                $scope.listBecas = response.data.msg;
                $("#beca_asignar_turno").material_select('destroy');
                $("#beca_asignar_turno").html("");
                $("#beca_asignar_turno").append("<option value=\"\" disabled selected>Seleccione</option>");
                for(beca in $scope.listBecas){
                    if($scope.listBecas[beca].persona.is_active)
                        $("#beca_asignar_turno").append("<option value=\""+$scope.listBecas[beca].id+"\">"+$scope.listBecas[beca].nick+"</option>");
                }
                $("#beca_asignar_turno").material_select();


            }, function(response) {
                //Second function handles error
                $scope.content = "Something went wrong";
            });
    };

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

    $scope.getBecas();
    $scope.getReporteBecas();
    $scope.getIps();

    $scope.verMasInfoIn = function (id, nick) {
        $scope.beca = nick + " (Inasistencias)";
        $http.get('get_inasistencias_beca?id='+id)
            .then(function(response) {
                $scope.listDetalleReporte = response.data.msg;

            }, function(response) {
                //Second function handles error
                $scope.content = "Something went wrong";
            });
    };

    $scope.delete_turno_beca = function(id){
        var r = confirm("Desea eliminar el turno?");
        if (r == true) {
            document.location='/delete_turno_beca?id='+id
        }
    }

    $scope.deactivate_beca_admin = function(id){
        var r = confirm("Desea desactivar el Beca-Trabajo?");
        if (r == true) {
            $http.get('desactivar_beca_admin?id='+id)
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

    $scope.active_beca_admin = function (id) {
        var r = confirm("Desea activar el Beca-Trabajo?");
        if (r == true) {
            $http.get('activar_beca_admin?id='+id)
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

    $scope.editar_beca = function (obj) {
        $scope.becaAdd = obj
    };

    $scope.edit_ip_admin = function (obj) {
        $scope.ipAdd = obj;
    };

    $scope.newIpFunct = function () {
        $scope.ipAdd = {id:0, ip: ""};
    };
    $scope.save_beca = function () {
        $http.post("add_beca", $scope.becaAdd)
            .then( function(data){
                $scope.newBecaFunct();
                if ("Notification" in window)
                {
                    var ask = Notification.requestPermission();
                    ask.then(permission => {
                        if (permission ==='granted') {
                            var msg = new Notification('Mensaje', {
                                body: data.data.msg,
                                icon:"/static/img/ufps.jpg"
                            });
                        }
                    })
                }
                $scope.getBecas();

            }, function(err){
                console.log(err);
            })
    };

    $scope.save_ips = function () {
        $http.post("add_ip", $scope.ipAdd)
            .then( function(data){
                $scope.newBecaFunct();
                if ("Notification" in window)
                {
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
                $scope.getIps();
                $scope.edit_ip_admin();

            }, function(err){
                console.log(err);
            })
    };

    $scope.newBecaFunct = function () {
        $scope.becaAdd = {id: 0, tel: "", nick: "", cc: "", persona: {nombre: "", codigo: "", email: ""}};
    };

    $scope.deactivate_ip_admin = function(id){
        var r = confirm("Desea desactivar la IP?");
        if (r == true) {

            $http.get('desactivar_ip_admin?id='+id)
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
                $scope.getIps();

            }, function(response) {
                //Second function handles error
                $scope.content = "Something went wrong";
            });
        }
    };

    $scope.activate_ip = function (id) {
        var r = confirm("Desea activar la IP?");
        if (r == true) {

            $http.get('activar_ip_admin?id='+id)
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
                $scope.getIps();

            }, function(response) {
                //Second function handles error
                $scope.content = "Something went wrong";
            });
        }
    };


    $scope.getAdmin = function () {
        $http.get('get_admins')
            .then(function(response) {
                $scope.listAdmin = response.data.msg;

            }, function(response) {
                //Second function handles error
                $scope.content = "Something went wrong";
            });
    };
    $scope.getAdmin();

    $scope.save_admin = function () {
        $http.post("add_admin", $scope.adminAdd)
            .then( function(data){
                $scope.newBecaFunct();
                if ("Notification" in window)
                {
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
                $scope.getAdmin();
                $scope.newAdminFunct();

            }, function(err){
                console.log(err);
            })
    };

    $scope.newAdminFunct = function () {
        $scope.adminAdd = {id: 0, codigo: "", nombre: "", email: ""};
         $("#code_id").attr("disabled", false)
    };
    $scope.editar_admin = function (obj) {
        $scope.adminAdd = obj;
        $("#code_id").attr("disabled", true);
    };
    $scope.deactivte_admin = function (id, estado) {
        if (estado)
            var r = confirm("Desea desactivar el administrador??");
        else
            var r = confirm("Desea activar el administrador??");
        if (r == true) {

            $http.get('deactivte_admin?id='+id)
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
                $scope.getAdmin();

            }, function(response) {
                //Second function handles error
                $scope.content = "Something went wrong";
            });
        }
    };

});