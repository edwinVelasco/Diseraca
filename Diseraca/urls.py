from django.conf.urls import include, url
from . import views

urlpatterns = [
    # para prueba
    #url(r'^cargar_turnos_iniciales$', views.cargar_turnos_iniciales),
    #url(r'^asignar_asistencias_semestre$', views.asignar_asistencias_semestre),

    #fuera del login
    url(r'^$', views.index),
    url(r'^disponibilidad$', views.disponibilidad),
    url(r'^get_edificios$', views.get_edificios),
    url(r'^get_salas_disponibilidad$', views.get_salas_disponibilidad),
    url(r'^inicio$', views.inicio),
    url(r'^iniciar_sesion$', views.iniciar_sesion),
    url(r'^cerrar$', views.cerrar),
    #becas
    url(r'^ver_horario_edificio$', views.ver_horario_edificio),
    url(r'^llegada_docente$', views.llegada_docente),
    url(r'^registrar_asistencia$', views.registrar_asistencia),

    #docente
    url(r'^buscar_salas_horario_docente$', views.buscar_salas_horario_docente),
    url(r'^add_prestamo_docente$', views.add_prestamo_docente),
    url(r'^desactivar_prestamo_docente$', views.desactivar_prestamo_docente),

    #admin
        #admin-prestamos-docente
        url(r'^buscar_salas_admin$', views.buscar_salas_admin),
        url(r'^get_carga_docente$', views.get_carga_docente),
        url(r'^add_prestamo_docente_admin$', views.add_prestamo_docente_admin),
        url(r'^get_prestamos_activos_docente$', views.get_prestamos_activos_docente),
        #admin-prestamos-sustentacion
        url(r'^add_prestamo_sustentacion_admin$', views.add_prestamo_sustentacion_admin),
        url(r'^buscar_salas_admin_sustentacion$', views.buscar_salas_admin_sustentacion),

        #admin-prestamos-cursos
        url(r'^add_prestamo_cursos_admin$', views.add_prestamo_cursos_admin),

        #Turnos de salas
        url(r'^horarios$', views.view_turnos),
        url(r'^get_turno_dia$', views.get_turno_dia),
        url(r'^save_turno$', views.save_turno),
        url(r'^get_turno_sala', views.get_turno_sala),
        url(r'^save_sala_turno', views.save_sala_turno),


        #edificios
        url(r'^save_edificio$', views.save_edificio),
        url(r'^get_salas$', views.get_salas),
        url(r'^save_sala$', views.save_sala),

        #salaTurnos
        url(r'^save_salaTurno_turno$', views.save_salaTurno_turno),

        #gestion docente
        url(r'^get_docentes$', views.get_docentes),
        url(r'^get_turnos_docente$', views.get_turnos_docente),
        url(r'^get_dptos$', views.get_dptos),
        url(r'^save_docente$', views.save_docente),
        url(r'^save_docente_csv$', views.save_docente_csv),

    #admin-becas
        url(r'^view_becas$', views.view_becas),
        url(r'^add_beca$', views.add_beca),
        url(r'^asignar_turno_beca$', views.asignar_turno_beca),
        url(r'^delete_turno_beca$', views.delete_turno_beca),
        url(r'^desactivar_beca_admin$', views.desactivar_beca_admin),
        url(r'^get_beca_edit_admin$', views.get_beca_edit_admin),
        url(r'^editar_beca$', views.editar_beca),
        #admin-ip
        url(r'^desactivar_ip_admin$', views.desactivar_ip_admin),
        url(r'^get_edit_ip_admin$', views.get_edit_ip_admin),

    #admin-docentes
    url(r'^view_docentes$', views.view_docentes),
        #actualizacion base de docentes

        #reportes de inasistencia
    ]