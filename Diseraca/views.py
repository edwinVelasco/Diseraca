# -*- coding: utf-8 -*-
import datetime
import json
import csv as csv
import threading
import re

from django.shortcuts import render, redirect
from django.core import serializers
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages

from .models import Edificio, Sala, Turno_Sala, Prestamo, Profesor, Carga, \
    Persona, Beca, Turno, \
    Beca_Turno, Asistencia, Ip_Registro, Carrera, Departamento, Semestre


def index(request):
    print(request.client_ip)
    # print(request.GET['hola'])
    print(request.client_ip)

    if request.method == 'GET':
        if 'msg' in request.session:
            msg = request.session['msg']
            del request.session['msg']
            return render(request, 'diseraca/login.html', {'msg': msg})

        if 'id' in request.GET:
            request.session['tmp'] = request.GET['id']
        return render(request, 'diseraca/login.html', {})


def disponibilidad(request):
    return render(request, 'diseraca/disponibilidad.html', {})


def get_edificios(request):
    edificios = Edificio.objects.all().order_by('codigo')

    data = serializers.serialize('json', edificios,
                                 fields=('codigo', 'nombre'))
    return HttpResponse(data, content_type='application/json')


def get_salas_disponibilidad(request):
    if 'id' in request.GET and 'fecha' in request.GET:

        edificio = Edificio.objects.get(id=request.GET['id'])
        salas = Sala.objects.filter(edificio=edificio).exclude(
            estado=2).order_by('tipo')
        ahora = datetime.datetime.now()
        date = request.GET['fecha'].split('-')
        fecha = datetime.date(day=int(date[2]), month=int(date[1]),
                              year=int(date[0]))

        if len(salas) == 0:
            text = '<h3 class="accent-1 red-text">%s Sin salas disponibles</h3>' % (
            edificio.nombre)
            return HttpResponse(text)

        tablas = """<div class="row">"""
        conta_tablas = 0
        for s in salas:
            if conta_tablas%3 == 0:
                tablas += """
                    </div>
                    <div class="row">
                """

            head = """
                <div class="col s4">
                <table class="card centered bordered" border>
                    <thead>
                        <tr class="red darken-1 white-text">
                            <th colspan=2>%s (%s)</th>
                        </tr>
                        <tr>
                            <th>Turno</th>
                            <th>Detalle</th>                            
                        </tr>
                    </thead>
                """ % (s.codigo.upper(), s.capacidad)
            sala_turnos = Turno_Sala.objects.filter(sala=s).filter(
                turno__dia=(fecha.isoweekday() - 1)).exclude(
                estado=1).order_by('turno__time_start')
            if len(sala_turnos) == 0:
                body = """
                    <tbody>
                        <tr>
                            <td colspan=2>Sala sin turnos, Contectenos para mas detalles</td>                            
                        </tr>
                    </tbody>
                </table>
                </div>

                """
                tablas += head + body
            else:
                tr = ""
                for st in sala_turnos:
                    if (st.estado == 2 and not st.hasta and fecha > st.hasta) \
                            or st.estado == 0:

                        prestamos = Prestamo.objects.filter(
                            date_turno=fecha).filter(turno_sala=st).filter(
                            estado=0)
                        if len(prestamos) == 0:
                            if st.turno.time_start > ahora.time() \
                                    or fecha > ahora.date():
                                tr += """
                                    <tr>
                                        <td>%s a %s</td>
                                        <td>
                                            Libre
                                            <!--<a onclick="add_login('%s', 
                                            '%s')" 
                                            class="waves-effect waves-circle
                                            waves-light btn-floating 
                                            secondary-content">
                                                <i class="material-icons">
                                                    add
                                                </i>
                                            </a>
                                            -->
                                        </td>
                                    </tr>""" % (str(st.turno.time_start)[:5],
                                                str(st.turno.time_end)[:5],
                                            request.GET['fecha'], str(st.id))
                            else:
                                tr += '''
                                    <tr>
                                        <td>%s a %s</td>
                                        <td>No fue utilizado</td>
                                    </tr>''' % (str(st.turno.time_start)[:5],
                                                str(st.turno.time_end)[:5])
                        else:
                            if prestamos[0].tipo == 1:
                                tr += u"""
                                <tr class="green lighten-5">
                                    <td>%s a %s</td>
                                    <td>Sustentación de %s de %s</td>
                                </tr>""" % (str(st.turno.time_start)[:5],
                                            str(st.turno.time_end)[:5],
                                            prestamos[0].solicitante.lower(),
                                            prestamos[0].carrera.nombre.lower())
                            elif prestamos[0].tipo == 2:
                                tr += """
                                <tr class="green lighten-5">
                                    <td>%s a %s</td>
                                    <td>Curso de %s  %s</td>
                                </tr>""" % (str(st.turno.time_start)[:5],
                                            str(st.turno.time_end)[:5],
                                            prestamos[0].solicitante.lower(),
                                            prestamos[0].detalle.lower())
                            elif prestamos[0].tipo == 3:
                                tr += '''
                                <tr class="green lighten-5">
                                    <td>%s a %s</td>
                                    <td>Reunion de %s  %s</td>
                                </tr>''' % (str(st.turno.time_start)[:5],
                                            str(st.turno.time_end)[:5],
                                            prestamos[0].solicitante.lower(),
                                            prestamos[0].detalle.lower())
                            else:
                                tr += """
                                <tr class="green lighten-5">
                                    <td>%s a %s</td>
                                    <td>%s, %s, %s-%s</td>
                                </tr>""" % (str(st.turno.time_start)[:5],
                                            str(st.turno.time_end)[:5],
                                            prestamos[0].profesor.persona.user.first_name.lower(),
                                            prestamos[0].nombre.lower(),
                                            prestamos[0].codigo.lower(),
                                            prestamos[0].grupo.upper())

                body = """
                    <tbody>
                        %s
                    </tbody>
                </table>
                </div>                
                """ % tr
                tablas += head + body
            conta_tablas += 1
        if conta_tablas % 3 != 0:
            tablas += "</div>"
        return HttpResponse(tablas.encode('utf-8'))


@login_required(login_url='/')
def inicio(request):
    if request.user.is_authenticated():
        persona = Persona.objects.get(
            user__username=request.session['usuario'])
        ahora = datetime.datetime.now()
        # 0 docente, 1 beca, 2 admin
        if persona.tipo == 0:
            p = Profesor.objects.get(persona=persona)
            prestamos = Prestamo.objects.filter(profesor=p, estado=0,
                                                date_turno__gte=ahora.date())

            edificios = Edificio.objects.all().order_by('codigo')
            cargas = Carga.objects.filter(profesor=p)

            if 'tmp' in request.session:
                # print 'tmp', request.session['tmp']
                tmp = request.session['tmp'].split('.')
                del request.session['tmp']
                date = tmp[0].split('-')
                f = datetime.date(day=int(date[2]), month=int(date[1]),
                                  year=int(date[0]))
                fecha_p = f - datetime.timedelta(days=7)
                fecha_s = f + datetime.timedelta(days=7)

                # prestamos pasados
                turno_sala = Turno_Sala.objects.get(id=tmp[1])
                p_p = Prestamo.objects.filter(profesor=p, date_turno=fecha_p,
                                              turno_sala__turno=turno_sala.turno)
                p_s = Prestamo.objects.filter(profesor=p, date_turno=fecha_s,
                                              turno_sala__turno=turno_sala.turno)
                p_d = Prestamo.objects.filter(profesor=p, date_turno=f,
                                              turno_sala__turno=turno_sala.turno)

                if len(p_s) == 0 and len(p_p) == 0 and len(p_d) == 0:
                    return render(request, 'diseraca/docente.html',
                                  {'edificios': edificios,
                                   'prestamos': prestamos,
                                   'fecha': str(tmp[0]),
                                   'sala_turno': tmp[1],
                                   'docente': persona, 'opcion': 'a',
                                   'cargas': cargas})
                else:
                    # aca es porque el turno no es valido
                    return render(request, 'diseraca/docente.html',
                                  {'edificios': edificios,
                                   'prestamos': prestamos,
                                   'docente': persona, 'opcion': 'b',
                                   'fecha': '', 'cargas': cargas})

            fecha = '%s-%s-%s' % (ahora.year, ahora.month, ahora.day)
            # aca es un unicio normal
            if 'msg' in request.session:
                msg = request.session['msg']
                del request.session['msg']
                return render(request, 'diseraca/docente.html',
                              {'edificios': edificios,
                               'prestamos': prestamos,
                               'docente': persona, 'fecha': fecha,
                               'cargas': cargas,
                               'opcion': 'c', 'msg': msg})
            if len(prestamos) == 3:
                return render(request, 'diseraca/docente.html',
                              {'edificios': edificios,
                               'prestamos': prestamos,
                               'docente': persona, 'fecha': fecha,
                               'cargas': cargas,
                               'opcion': 'c',
                               'msg': 'ya tiene los turnos activos permitidos'})

            return render(request, 'diseraca/docente.html',
                          {'edificios': edificios, 'prestamos': prestamos,
                           'docente': persona, 'fecha': fecha,
                           'cargas': cargas,
                           'opcion': 'c'})
        elif persona.tipo == 1:
            ip = request.client_ip
            b = Beca.objects.get(persona=persona)
            edificios = Edificio.objects.all().order_by('codigo')
            turnos = Turno.objects.filter(dia=(ahora.isoweekday()-1),
                                          time_start__lte=ahora.time(),
                                          time_end__gt=ahora.time(),
                                          estado=0)
            prestamos_turnos = list()
            for turno in turnos:
                prestamos = Prestamo.objects.filter(turno_sala__turno=turno,
                                                    date_turno=ahora.date(),
                                                    estado=0)
                # print prestamos
                for pres in prestamos:
                    prestamos_turnos.append(pres)
            if b.persona.user.username == '1611028':
                messages.success(request, "hola mi vida, :*")
            if 'msg' in request.session:
                msg = request.session['msg']
                del request.session['msg']
                return render(request, 'diseraca/beca/beca.html',
                              {'edificios': edificios, 'beca': b, 'msg': msg,
                               'prestamos': prestamos_turnos, 'ip': ip})

            return render(request, 'diseraca/beca/beca.html',
                          {'edificios': edificios, 'beca': b,
                           'prestamos': prestamos_turnos, 'ip': ip})
        elif persona.tipo == 2:
            edificios = Edificio.objects.all().order_by('codigo')
            carreras = Carrera.objects.all().order_by('codigo')
            if 'msg' in request.session:
                msg = request.session['msg']
                del request.session['msg']
                return render(request, 'diseraca/admin/prestamos.html',
                              {'edificios': edificios, 'admin': persona,
                               'msg': msg, 'carreras': carreras})

            return render(request, 'diseraca/admin/prestamos.html',
                          {'edificios': edificios, 'admin': persona,
                           'carreras': carreras})
    else:
        return HttpResponseRedirect('/')


def iniciar_sesion(request):
    if request.method == 'POST' and 'codigo' in request.POST and 'password' in request.POST:
        username = request.POST['codigo']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                request.session['usuario'] = username
                if request.POST['password'] == request.POST['codigo']:
                    return HttpResponseRedirect('view_init_password')

                return HttpResponseRedirect('inicio')

            else:
                request.session['msg'] = "Usuario Desactivado"
                return HttpResponseRedirect('/')
        else:
            request.session['msg'] = "codigo o contraseña erroneos"
            return HttpResponseRedirect('/')
    else:
        return HttpResponseRedirect('/')


@login_required(login_url='/')
def cerrar(request):
    if request.user.is_authenticated():
        del request.session['usuario']
        logout(request)
    return HttpResponseRedirect('/')


@login_required(login_url='/')
def view_init_password(request):
    if request.method == 'GET':
        return render(request, 'diseraca/cambiar_password.html',
                      {'correo': request.user.email,
                       'msg': u'Cambiar contraseña inicial y correo'})

    if request.method == 'POST':
        if request.POST['password1'] == request.POST['password2']:
            patronMay = r"[A-Z]{1}"
            patronNum = r"\d{2}"
            if re.search(patronMay, request.POST['password1']) and re.search(
                    patronNum, request.POST['password1']) and \
                    len(request.POST['password1']) >= 8:
                user = request.user
                user.email = request.POST['email']
                user.set_password(request.POST['password1'])
                user.save()
                del request.session['usuario']
                logout(request)
                request.session[
                    'msg'] = "Contraseña y correo cambiado exitosamente"
                return HttpResponseRedirect('/')
            else:
                return render(request, 'diseraca/cambiar_password.html',
                              {'correo': request.POST['email'],
                               'msg': u'La nueva contraseña no cumple con el patron requerido'})
        else:
            return render(request, 'diseraca/cambiar_password.html',
                          {'correo': request.POST['email'],
                           'msg': u'La nueva contraseña no coincide'})


# --------------def Docentes-------------------


@login_required(login_url='/')
def buscar_salas_horario_docente(request):
    if request.user.is_authenticated():
        if 'id' in request.GET and 'fecha' in request.GET:
            date = request.GET['fecha'].split('-')
            fecha = datetime.date(day=int(date[2]), month=int(date[1]),
                                  year=int(date[0]))

            ahora = datetime.datetime.now()
            edificio = Edificio.objects.get(id=request.GET['id'])
            salas = Sala.objects.filter(edificio=edificio, tipo=0).exclude(
                estado=2).order_by('tipo')
            if len(salas) == 0:
                text = '<h3 class="accent-1 red-text">%s Sin salas disponibles</h3>' % (
                edificio.nombre.lower())
                return HttpResponse(text)

            p = Profesor.objects.get(
                persona__user__username=request.session['usuario'])
            tablas = '''
                <h3 class="accent-1 red-text">%s, %s</h3>
                Solo se muestran las salas y turnos disponibles para 
                usted 
                <a target="_blank"  href="informacion" class="">
                    <i class="material-icons">info_outline</i>
                </a>
                <div class="row">''' % (
            edificio.nombre.upper(), fecha)
            #mismo dia pero en la semana anterior
            fecha_p = fecha - datetime.timedelta(days=7)
            #mismo dia pero semana siguiente
            fecha_s = fecha + datetime.timedelta(days=7)

            conta_tablas = 0
            for s in salas:
                if conta_tablas % 4 == 0:
                    tablas += """
                            </div>
                            <div class="row">
                        """
                head = """
                    <div class="col s3">
                    <table class="card centered highlight" border>
                        <thead>
                            <tr class="red darken-1 white-text">
                                <th colspan=2>Sala %s (%s)</th>
                            </tr>
                            <tr>
                                <th>Turno</th>
                                <th>Detalle</th>                            
                            </tr>
                        </thead>
                    """ % (s.codigo, s.capacidad)
                #si el prestamo es es para despues del hoy
                if fecha > ahora.date():
                    sala_turnos = Turno_Sala.objects.\
                        filter(sala=s, turno__dia=(fecha.isoweekday()-1))\
                        .exclude(estado=1).order_by('turno__time_start')
                else:
                    sala_turnos = Turno_Sala.objects.\
                        filter(sala=s, turno__dia=(fecha.isoweekday() - 1),
                               turno__time_start__gte=ahora.time()) \
                        .exclude(estado=1).order_by('turno__time_start')

                if len(sala_turnos) == 0:
                    body = """
                        <tbody>
                            <tr>
                                <td>Sala sin turnos</td>
                                <td>Contectenos para mas detalles</td>                            
                            </tr>
                        </tbody>
                    </table>
                    </div>

                    """
                    tablas += head + body
                else:
                    tr = ""
                    j = 0
                    for st in sala_turnos:
                        if (st.estado == 2 and st.hasta
                            and fecha > st.hasta) or st.estado == 0:

                            #prestamos del turno st
                            p_turno = Prestamo.objects.filter(
                                date_turno=fecha, turno_sala=st)\
                                .exclude(estado=2)

                            #Prestamos pasados del profesor en ese turno
                            p_p = Prestamo.objects.\
                                filter(profesor=p,
                                       date_turno=fecha_p,
                                       turno_sala__turno=st.turno)\
                                .exclude(estado=2)

                            # prestamos siguientes del profesor en ese turno
                            p_s = Prestamo.objects.\
                                filter(profesor=p,
                                       date_turno=fecha_s,
                                       turno_sala__turno=st.turno)\
                                .exclude(estado=2)

                            # prestamos para el dia del prestamo, en las
                            # siguiente bloque que no sea cancelado
                            p_d2 = Prestamo.objects.\
                                filter(profesor=p,date_turno=fecha,
                            turno_sala__turno__time_end=st.turno.time_start) \
                                .exclude(estado=2)

                            #prestamos para el dia del prestamo en el
                            # bloque siguiente que no sean canceladas
                            p_d1 = Prestamo.objects.\
                                filter(profesor=p, date_turno=fecha,
                            turno_sala__turno__time_end=st.turno.time_start) \
                                .exclude(estado=2)

                            # prestamos siguientes

                            if not p_turno and not p_p and not p_s and not\
                                    p_d2 and not p_d1:
                                tr += """
                                    <tr>
                                        <td>%s a %s</td>
                                        <td>
                                            Libre
                                            <a onclick="add_form_prestamo_docente('%s','%s')"
                                                class="waves-effect waves-circle 
                                                waves-light btn-floating secondary-content">
                                                <i class="material-icons">add</i>
                                            </a>
                                        </td>
                                    </tr>""" % (str(st.turno.time_start)[:5],
                                                str(st.turno.time_end)[:5],
                                                request.GET['fecha'], str(st.id))
                                j += 1

                    if j == 0:
                        tr += """
                        <tr>                            
                            <td colspan=2>Sala sin turnos, contactenos para mas detalles</td>
                        </tr>"""

                    body = """
                        <tbody>
                            %s
                        </tbody>
                    </table>
                    </div>                
                    """ % tr
                    tablas += head + body
                conta_tablas += 1

            if conta_tablas % 4 != 0:
                tablas += "</div>"

            return HttpResponse(tablas.encode('utf-8'))
    else:
        return HttpResponseRedirect('/')


@login_required(login_url='/')
def add_prestamo_docente(request):
    if request.user.is_authenticated():
        if request.method == 'POST':
            date = request.POST['fecha'].split('-')
            fecha = datetime.date(day=int(date[2]), month=int(date[1]),
                                  year=int(date[0]))
            ahora = datetime.datetime.now()
            carga = Carga.objects.get(id=request.POST['carga'])
            turno_sala = Turno_Sala.objects.get(
                id=request.POST['sala_turno'])

            if carga.matriculados > turno_sala.sala.capacidad:
                request.session['msg'] = 'supera la capacidad de la sala'
                return HttpResponseRedirect('inicio')

            prestamos_activos = Prestamo.objects.filter(
                profesor=carga.profesor, estado=0,
                date_turno__gte=ahora.date())
            if len(prestamos_activos) == 3:
                request.session[
                    'msg'] = 'ya tiene los turnos activos permitidos, 3'
                return HttpResponseRedirect('inicio')

            prestamo = Prestamo()
            prestamo.carrera = carga.carrera
            prestamo.profesor = carga.profesor
            prestamo.codigo = carga.codigo
            prestamo.nombre = carga.nombre
            prestamo.grupo = carga.grupo
            prestamo.turno_sala = turno_sala
            prestamo.date_turno = fecha
            prestamo.matriculados = carga.matriculados
            prestamo.ip = request.client_ip
            prestamo.usuario = Profesor.objects.get(
                persona__user__username=request.session['usuario']). \
                persona.user.first_name
            prestamo.save()
            request.session['msg'] = 'prestamo registrado con exito'
            return HttpResponseRedirect('inicio')
    else:
        return HttpResponseRedirect('/')


@login_required(login_url='/')
def desactivar_prestamo_docente(request):
    if request.user.is_authenticated():
        if 'id' in request.GET:
            prestamo = Prestamo.objects.get(id=request.GET['id'])
            prestamo.estado = 2
            prestamo.save()
        return HttpResponseRedirect('inicio')
    else:
        return HttpResponseRedirect('/')


# -------------------end def Docentes--------------


# --------------def Becas-------------------
@login_required(login_url='/')
def llegada_docente(request):
    if request.user.is_authenticated():
        if 'id' in request.GET:
            prestamo = Prestamo.objects.get(id=request.GET['id'])
            prestamo.estado = 1
            prestamo.beca = Beca.objects.get(
                persona__user__username=request.session['usuario'])
            prestamo.save()
        return HttpResponseRedirect('inicio')
    else:
        return HttpResponseRedirect('/')


@login_required(login_url='/')
def ver_horario_edificio(request):
    if request.user.is_authenticated():
        if 'id' in request.GET:
            edificio = Edificio.objects.get(id=request.GET['id'])
            ahora = datetime.datetime.now()
            turnos = Turno.objects.filter(dia=(ahora.isoweekday() - 1),
                                          time_start__lte=ahora.time(),
                                          time_end__gte=ahora.time())
            prestamos_envio = []
            for turno in turnos:
                prestamos = Prestamo.objects.filter(date_turno=ahora.date(),
                                                    turno_sala__turno=turno).exclude(
                    estado=2)
                for pres in prestamos:
                    prestamos_envio.append(pres)

            if 'bool' in request.GET:
                if len(prestamos_envio) > 0:
                    total = 0
                    data = '''
                        <table class="bordered centered">
                        <thead>
                          <tr>
                              <th data-field="sala">Sala</th>
                              <th data-field="docente">Docente</th>
                              <th data-field="materia">Materia</th>
                              <th data-field="horario">Horario</th>
                          </tr>
                        </thead>

                        <tbody>
                    '''
                    for pres_envio in prestamos_envio:
                        if pres_envio.estado == 1:
                            data += '<tr class="white-text green">'
                            total += pres_envio.matriculados
                        else:
                            data += '<tr class="white-text red">'

                        data += '<td>%s</td>' % (
                        pres_envio.turno_sala.sala.codigo)
                        data += '<td>%s</td>' % (
                        pres_envio.profesor.persona.user.first_name)
                        data += '<td>%s - %s</td>' % (
                        pres_envio.nombre, pres_envio.grupo)
                        if pres_envio.estado == 1:
                            data += '''
                                <td>%s a %s<a class="waves-effect waves-circle waves-light btn-floating
                                secondary-content green darken-4"><i class="material-icons">done_all</i>
                                            </a>
                                </td>
                            ''' % (pres_envio.turno_sala.turno.time_start,
                                   pres_envio.turno_sala.turno.time_end)
                        else:
                            data += '''
                                <td>%s a %s<a class="waves-effect waves-circle waves-light btn-floating
                                secondary-content red darken-4">
                                                <i class="material-icons">done</i>
                                            </a>
                                </td>

                            ''' % (pres_envio.turno_sala.turno.time_start,
                                   pres_envio.turno_sala.turno.time_end)
                        data += '</tr>'

                    data += '</tbody></table>'
                    msg = {'data': data,
                           'total': 'Personas: ' + str(total)}
                    res = json.dumps(msg)
                    return HttpResponse(res, content_type='application/json')
                msg = {
                    'data': '''<h2 class="green-text col l12 ">Turno Libre</h2>''',
                    'total': 'Personas: 0'}
                res = json.dumps(msg)
                return HttpResponse(res, content_type='application/json')

            return render(request, 'diseraca/horario_sala.html',
                          {'edificio': edificio,
                           'prestamos': prestamos_envio})

    else:
        return HttpResponseRedirect('/')


@login_required(login_url='/')
def registrar_asistencia(request):
    if request.user.is_authenticated() and 'usuario' in request.session:
        # print request.client_ip
        beca = Beca.objects.get(
            persona__user__username=request.session['usuario'])
        ahora = datetime.datetime.now()
        asistencia = Asistencia.objects.filter(date_turno=ahora.date(),
                                               beca_turno__beca=beca,
                                               beca_turno__turno__time_start__lt=ahora.time(),
                                               beca_turno__turno__time_end__gt=ahora.time(),
                                               tipo=0)

        # turno_ahora = Asistencia.objects.filter(date_turno=ahora.date(), beca_turno__beca=beca, datetime_registro=None)
        if len(asistencia) > 0:
            if asistencia[0].datetime_registro != None and asistencia[
                0].ip != None:
                request.session[
                    'msg'] = u'Ya se había registrado en este turno, como inasistencia'
                return HttpResponseRedirect('inicio')

            if datetime.time(
                    hour=asistencia[0].beca_turno.turno.time_start.hour,
                    minute=15, second=00) < ahora.time() \
                    < datetime.time(
                hour=asistencia[0].beca_turno.turno.time_start.hour,
                minute=50, second=00):
                try:
                    ip = Ip_Registro.objects.get(ip=request.client_ip)
                    if not ip.estado:
                        request.session[
                            'msg'] = 'IP desactivada, no se registro la llegada'
                        return HttpResponseRedirect('inicio')

                    asistencia[0].ip = ip
                    asistencia[0].tipo = 1
                    asistencia[0].datetime_registro = ahora
                    asistencia[0].save()
                    request.session['msg'] = 'Registro con Retraso'
                    return HttpResponseRedirect('inicio')

                except Ip_Registro.DoesNotExist:
                    request.session['msg'] = 'Ip no valida'
                    return HttpResponseRedirect('inicio')
            elif ahora.time() < datetime.time(
                    hour=asistencia[0].beca_turno.turno.time_start.hour,
                    minute=15, second=00):
                try:
                    ip = Ip_Registro.objects.get(ip=request.client_ip)
                    asistencia[0].ip = ip
                    asistencia[0].tipo = 2
                    asistencia[0].datetime_registro = ahora
                    asistencia[0].save()
                    request.session['msg'] = 'Registro Exitoso'
                    return HttpResponseRedirect('inicio')

                except Ip_Registro.DoesNotExist:
                    request.session['msg'] = 'Ip no valida'
                    return HttpResponseRedirect('inicio')
            else:
                try:
                    ip = Ip_Registro.objects.get(ip=request.client_ip)
                    asistencia[0].ip = ip
                    asistencia[0].datetime_registro = ahora
                    asistencia[0].save()
                    request.session['msg'] = 'Se registro como inasistencia'
                    return HttpResponseRedirect('inicio')

                except Ip_Registro.DoesNotExist:
                    request.session['msg'] = 'Ip no valida'
                    return HttpResponseRedirect('inicio')
        request.session['msg'] = 'No tiene turno de beca'
        return HttpResponseRedirect('inicio')
    else:
        return HttpResponseRedirect('/')


# ------------admin-----------
@login_required(login_url='/')
def buscar_salas_admin(request):
    if 'id' in request.GET and 'fecha' in request.GET and 'docente' in request.GET:
        try:
            profesor = Profesor.objects.get(
                persona__user__username=request.GET['docente'])
        except Profesor.DoesNotExist:
            text = '<h3 class="accent-1 red-text">No existe el docente</h3>'
            return HttpResponse(text)

        # se obtiene el mes en numero
        date = request.GET['fecha'].split('-')

        fecha = datetime.date(day=int(date[2]), month=int(date[1]),
                              year=int(date[0]))
        edificio = Edificio.objects.get(id=request.GET['id'])
        salas = Sala.objects.filter(edificio=edificio).exclude(
            estado=2).order_by('tipo')
        ahora = datetime.datetime.now()
        if len(salas) == 0:
            text = '<h3 class="accent-1 red-text">%s Sin salas disponibles</h3>' % (
            edificio.nombre)
            return HttpResponse(text)

        tablas = """
            <h3 class="accent-1 red-text">%s, %s</h3>
        <div class="row">
        """ % (edificio.nombre, fecha)
        conta_tablas = 0
        for s in salas:
            if conta_tablas % 3 == 0:
                tablas += """
                    </div>
                    <div class="row">
                """
            head = """
                <div class="col s4">
                <table class="card centered highlight" border>
                    <thead>
                        <tr class="red darken-1 white-text">
                            <th colspan=2>%s (%s), %s</th>
                        </tr>
                        <tr>
                            <th>Turno</th>
                            <th>Detalle</th>                            
                        </tr>
                    </thead>
                """ % (s.codigo, s.capacidad, ['Audiovisuales',
                                               'Aula virtual',
                                               'Auditorio'][s.tipo])

            sala_turnos = Turno_Sala.objects.filter(sala=s).filter(
                turno__dia=(fecha.isoweekday() - 1)).exclude(
                estado=1).order_by('turno__time_start')

            if len(sala_turnos) == 0:
                body = """
                    <tbody>
                        <tr>
                            <td colspan=2>Sala sin turnos, 
                                Contectenos para mas detalles
                            </td>                                
                        </tr>
                    </tbody>
                </table>
                </div>

                """
                tablas += head + body
            else:
                tr = ""
                for st in sala_turnos:
                    if (st.estado == 2 and st.hasta !=
                        None and fecha > st.hasta) or st.estado == 0:
                        prestamos = Prestamo.objects.\
                            filter(date_turno=fecha, turno_sala=st, estado=0)
                        ahora_delta = ahora - datetime.timedelta(hours=1)
                        if len(prestamos) == 0:
                            if st.turno.time_start > ahora_delta.time() \
                                    or fecha > ahora.date():
                                tr += """
                                <tr>
                                    <td>%s a %s</td>
                                    <td>
                                        Libre
                                        <a onclick="ver_form('%s')" 
                                        class="waves-effect waves-circle
                                        waves-light btn-floating secondary-content">
                                            <i class="material-icons">add</i>
                                        </a>
                                    </td>
                                </tr>""" % (str(st.turno.time_start)[:5],
                                            str(st.turno.time_end)[:5],
                                            str(st.id))
                        else:
                            if prestamos[0].tipo == 0:
                                tr += """
                                    <tr>
                                        <td>%s a %s</td>
                                        <td>%s, %s-%s</td>
                                    </tr>
                                """ % (str(st.turno.time_start)[:5],
                                       str(st.turno.time_end)[:5],
                                       prestamos[0].profesor.persona.user.first_name.lower(),
                                       prestamos[0].nombre.lower(),
                                       prestamos[0].grupo.upper())
                            elif prestamos[0].tipo == 1:
                                tr += u"""
                                <tr>
                                    <td>%s a %s</td>
                                    <td>Sustentación de %s, %s</td>
                                </tr>
                                """ % (str(st.turno.time_start)[:5],
                                       str(st.turno.time_end)[:5],
                                       prestamos[0].solicitante.lower(),
                                       prestamos[0].carrera.nombre.lower())
                            else:
                                tr += """
                                    <tr>
                                        <td>%s a %s</td>
                                        <td>%s de %s, %s</td>
                                    </tr>
                                """ % (str(st.turno.time_start)[:5],
                                      str(st.turno.time_end)[:5],
                                      ["","Sustentacion", "Curso",
                                        u"Reunión"][prestamos[0].tipo],
                                      prestamos[0].solicitante.lower(),
                                      prestamos[0].detalle.lower())

                body = """
                    <tbody>
                        %s
                    </tbody>
                </table>
                </div>                
                """ % tr
                tablas += head + body
            conta_tablas += 1
        if conta_tablas % 3 != 0:
            tablas += "</div>"
        return HttpResponse(tablas.encode('utf-8'))


@login_required(login_url='/')
def get_carga_docente(request):
    if 'docente' in request.GET:
        try:
            profesor = Profesor.objects.get(
                persona__user__username=request.GET['docente'])
            carga = Carga.objects.filter(profesor=profesor)
            data = '''<option value="" disabled selected>Seleccione</option>'''
            for c in carga:
                data += '''<option value="%s">%s, %s-%s, Matriculados: %s</option>''' % (
                c.id, c.nombre.lower(), c.codigo.upper(), c.grupo.upper(),
                c.matriculados)

            data = json.dumps({'code': 200, 'msg': data,
                               'docente': profesor.persona.user.first_name.lower()})
            return HttpResponse(data, content_type='application/json')

        except Profesor.DoesNotExist:
            return HttpResponse('not')


@login_required(login_url='/')
def add_prestamo_docente_admin(request):
    if request.user.is_authenticated():
        if request.method == 'POST':
            date = request.POST['fecha'].split('-')
            fecha = datetime.date(day=int(date[2]), month=int(date[1]),
                                  year=int(date[0]))
            carga = Carga.objects.get(id=request.POST['carga'])
            turno_sala = Turno_Sala.objects.get(
                id=request.POST['sala_turno'])

            if carga.matriculados > turno_sala.sala.capacidad:
                request.session['msg'] = 'supera la capacidad de la sala'

            prestamos_activos = Prestamo.objects.filter(
                profesor=carga.profesor, estado=0)
            if len(prestamos_activos) == 3:
                request.session[
                    'msg'] = 'ya tiene los turnos activos permitidos'

            prestamo = Prestamo()
            prestamo.carrera = carga.carrera
            prestamo.profesor = carga.profesor
            prestamo.codigo = carga.codigo
            prestamo.nombre = carga.nombre
            prestamo.grupo = carga.grupo
            prestamo.turno_sala = turno_sala
            prestamo.date_turno = fecha
            prestamo.matriculados = carga.matriculados
            prestamo.ip = request.client_ip
            prestamo.usuario = Persona.objects.get(
                user__username=request.session['usuario']).user.first_name
            prestamo.save()

            if 'msg' not in request.session:
                request.session['msg'] = 'Prestamo reaizado con exito'

            return HttpResponseRedirect('inicio')
    else:
        return HttpResponseRedirect('/')


@login_required(login_url='/')
def get_prestamos_activos_docente(request):
    if request.user.is_authenticated():
        if 'docente' in request.GET:
            try:
                p = Profesor.objects.get(
                    persona__user__username=request.GET['docente'])
            except Profesor.DoesNotExist:
                return HttpResponse(
                    '<h4 class="accent-1 red-text" hidden>No existe el docente :(</h4>')
            ahora = datetime.datetime.now()
            prestamos = Prestamo.objects.filter(profesor=p, estado=0,
                                                date_turno__gte=ahora.date())
            if len(prestamos) > 0:
                data = '''
                    <h4 class="accent-1 red-text">Prestamos Activos</h4>
                        <table class="highlight centered responsive-table">
                            <thead>
                              <tr>
                                  <th data-field="price">Sala-Edificio</th>
                                  <th data-field="id">Fecha</th>
                                  <th data-field="name">Horario</th>
                                  <th data-field="price">Materia-Grupo</th>
                              </tr>
                            </thead>
                            <tbody>
                        '''
                for prestamo in prestamos:
                    data += '''
                            <tr>
                                <td>%s - %s</td>
                                <td>%s</td>
                                <td>%s a %s</td>
                                <td>%s  G-%s
                                    <a onclick="desactivar_prestamo_docente(%s)"
                                       class="waves-effect waves-circle waves-light btn-floating secondary-content red">
                                    <i class="material-icons">delete</i>
                                  </a>
                                </td>
                            </tr>

                    ''' % (prestamo.turno_sala.sala.codigo,
                           prestamo.turno_sala.sala.edificio.codigo,
                           prestamo.date_turno,
                           prestamo.turno_sala.turno.time_start,
                           prestamo.turno_sala.turno.time_end,
                           prestamo.nombre,
                           prestamo.grupo, prestamo.id)
                data += '</tbody></table>'
            else:
                data = '''<h4 class="accent-1 red-text">No tiene prestamos Activos</h4>'''

            return HttpResponse(data)
    else:
        return HttpResponseRedirect('/')


@login_required(login_url='/')
def view_becas(request):
    if request.user.is_authenticated():
        turnos = Turno.objects.filter(id__lte=48, estado=0).order_by(
            'time_start')
        beca_turnos_lunes = Beca_Turno.objects.filter(turno__dia=0,
                                                      status=True,
                                                      beca__persona__user__is_active=True)
        beca_turnos_martes = Beca_Turno.objects.filter(turno__dia=1,
                                                       status=True,
                                                       beca__persona__user__is_active=True)
        beca_turnos_miercoles = Beca_Turno.objects.filter(turno__dia=2,
                                                          status=True,
                                                          beca__persona__user__is_active=True)
        beca_turnos_jueves = Beca_Turno.objects.filter(turno__dia=3,
                                                       status=True,
                                                       beca__persona__user__is_active=True)
        beca_turnos_viernes = Beca_Turno.objects.filter(turno__dia=4,
                                                        status=True,
                                                        beca__persona__user__is_active=True)
        beca_turnos_sabado = Beca_Turno.objects.filter(turno__dia=5,
                                                       status=True,
                                                       beca__persona__user__is_active=True)

        persona = Persona.objects.get(
            user__username=request.session['usuario'])
        # ips = Ip_Registro.objects.filter(estado=True)

        return render(request, 'diseraca/admin/becas.html',
                      {'turnos': turnos,
                       'beca_turnos_lunes': beca_turnos_lunes,
                       'beca_turnos_martes': beca_turnos_martes,
                       'beca_turnos_miercoles': beca_turnos_miercoles,
                       'beca_turnos_jueves': beca_turnos_jueves,
                       'beca_turnos_viernes': beca_turnos_viernes,
                       'beca_turnos_sabado': beca_turnos_sabado,
                       'admin': persona})
    else:
        return HttpResponseRedirect('/')


# -------crud becas--------

@login_required(login_url='/')
def add_beca(request):
    if request.user.is_authenticated():
        try:
            beca = Beca.objects.get(id=request.POST['id'])
            beca.persona.user.username = request.POST['persona[codigo]']
            beca.persona.user.first_name = request.POST['persona[nombre]']
            beca.persona.user.email = request.POST['persona[email]']
            beca.persona.user.save()
            beca.tel = request.POST['tel']
            beca.nick = request.POST['nick']
            beca.cc = request.POST['cc']
            beca.save()
            res = json.dumps({'code': 200, 'msg': "Editado con exito"})
            return HttpResponse(res, content_type='application/json')
        except Beca.DoesNotExist:
            user = User()
            user.username = request.POST['persona[codigo]']
            user.first_name = request.POST['persona[nombre]']
            user.email = request.POST['persona[email]']
            user.set_password(request.POST['persona[codigo]'])
            user.save()
            persona = Persona()
            persona.user = user
            persona.tipo = 1
            persona.save()
            beca = Beca()
            beca.persona = persona
            beca.tel = request.POST['tel']
            beca.nick = request.POST['nick']
            beca.cc = request.POST['cc']
            beca.save()
            res = json.dumps({'code': 200, 'msg': "Registrado con exito"})
            return HttpResponse(res, content_type='application/json')
    else:
        return HttpResponseRedirect('/')


@login_required(login_url='/')
def asignar_turno_beca(request):
    if request.user.is_authenticated():
        if request.method == 'POST':
            if 'turno' in request.POST and 'beca' in request.POST:

                try:
                    beca = Beca.objects.get(id=request.POST['beca'])
                    turno = Turno.objects.get(id=request.POST['turno'])
                    try:
                        beca_turno = Beca_Turno.objects.get(beca=beca,
                                                            turno=turno)
                    except Beca_Turno.DoesNotExist:
                        beca_turno = Beca_Turno()
                    finally:
                        beca_turno.beca = beca
                        beca_turno.turno = turno
                        beca_turno.status = True
                        beca_turno.save()
                        messages.success(request,
                                         "Turno agregado con exito.")
                        return HttpResponseRedirect('view_becas')
                except Beca.DoesNotExist or Turno.DoesNotExist:
                    return HttpResponseRedirect('inicio')
    else:
        return HttpResponseRedirect('/')


@login_required(login_url='/')
def delete_turno_beca(request):
    if request.user.is_authenticated():
        if request.method == 'GET':
            if 'id' in request.GET:
                try:
                    beca_turno = Beca_Turno.objects.get(id=request.GET['id'])
                    beca_turno.status = False
                    beca_turno.save()
                    beca_turno.remove_asistencias()
                    messages.success(request, "Turno eliminado.")
                    return HttpResponseRedirect('view_becas')
                except Beca_Turno.DoesNotExist:
                    return HttpResponseRedirect('inicio')

    else:
        return HttpResponseRedirect('/')


@login_required(login_url='/')
def asignar_asistencias_semestre(request):
    if request.user.is_authenticated():
        """
        se hizo para cumplir las 16 semanas que se deben cumplir la beca
        ahora = datetime.datetime.now()
        fecha_ini = None
        
        if (ahora.isoweekday() - 1) == 0:
            fecha_ini = ahora + datetime.timedelta(days=7)
        elif (ahora.isoweekday() - 1) == 1:
            fecha_ini = ahora + datetime.timedelta(days=6)
        elif (ahora.isoweekday() - 1) == 2:
            fecha_ini = ahora + datetime.timedelta(days=5)
        elif (ahora.isoweekday() - 1) == 3:
            fecha_ini = ahora + datetime.timedelta(days=4)
        elif (ahora.isoweekday() - 1) == 4:
            fecha_ini = ahora + datetime.timedelta(days=3)
        elif (ahora.isoweekday() - 1) == 5:
            fecha_ini = ahora + datetime.timedelta(days=2)
        else:
            fecha_ini = ahora + datetime.timedelta(days=1)
    
        fecha_ini = ahora + datetime.timedelta(days=-5)
        """
        date = request.POST['fecha_start'].split('-')
        fecha_ini = datetime.date(day=int(date[2]), month=int(date[1]),
                                  year=int(date[0]))

        for i in range(0, 6):
            beca_turnos = Beca_Turno.objects.filter(turno__dia=i,
                                                    status=True)
            fecha_ini2 = fecha_ini + datetime.timedelta(days=i)

            for beca_turno in beca_turnos:
                fecha = fecha_ini2  # lunea
                for i in range(0, int(request.POST['semanas'])):
                    try:
                        asistencia = Asistencia()
                        asistencia.beca_turno = beca_turno
                        asistencia.date_turno = fecha
                        asistencia.save()
                        fecha = fecha + datetime.timedelta(days=7)
                    except Exception as e:
                        print(e)

        messages.success(request,
                         "Las asistencias se registraron exitosamente.")
        return HttpResponseRedirect('view_becas')


@login_required(login_url='/')
def desactivar_beca_admin(request):
    if request.user.is_authenticated() and 'id' in request.GET:
        try:
            beca = Beca.objects.get(id=request.GET['id'])
            beca.persona.user.is_active = False
            beca.persona.user.save()
            beca.delete_asistencias()
            beca.delete_turnos()

            # 'Beca desactivado, recuerde que solo el webmaster puede activar usuarios'

            res = json.dumps({'code': 200, 'msg': "Beca desactivado"})
            return HttpResponse(res, content_type='application/json')
        except Beca.DoesNotExist:
            res = json.dumps({'code': 404, 'msg': "Beca no existe"})
            return HttpResponse(res, content_type='application/json')
    else:
        return HttpResponseRedirect('/')


@login_required(login_url='/')
def activar_beca_admin(request):
    if request.user.is_authenticated() and 'id' in request.GET:
        try:
            beca = Beca.objects.get(id=request.GET['id'])
            beca.persona.user.is_active = True
            beca.persona.user.save()
            res = json.dumps({'code': 200, 'msg': "Beca activado"})
            return HttpResponse(res, content_type='application/json')
        except Beca.DoesNotExist:
            res = json.dumps({'code': 404, 'msg': "Beca no existe"})
            return HttpResponse(res, content_type='application/json')
    else:
        return HttpResponseRedirect('/')


@login_required(login_url='/')
def get_becas(request):
    if request.user.is_authenticated():
        becas = Beca.objects.all()

        t = [{'id': w.id, 'tel': w.tel, 'nick': w.nick, 'cc': w.cc,
              'persona': {'nombre': w.persona.user.first_name,
                          'codigo': w.persona.user.username,
                          'email': w.persona.user.email,
                          'is_active': w.persona.user.is_active}} for w in
             becas]
        # data = json.dumps(t)

        res = json.dumps({'code': 200, 'msg': t})
        return HttpResponse(res, content_type='application/json')
    else:
        return HttpResponseRedirect('/')


# ----crud ip-----------

@login_required(login_url='/')
def get_ips(request):
    ips = Ip_Registro.objects.all()
    t = [{'id': w.id, 'ip': w.ip, 'estado': w.estado} for w in ips]

    res = json.dumps({'code': 200, 'msg': t})
    return HttpResponse(res, content_type='application/json')


@login_required(login_url='/')
def add_ip(request):
    if request.user.is_authenticated():
        try:
            ip = Ip_Registro.objects.get(id=request.POST['id'])
            ip.ip = request.POST['ip']
            ip.estado = True
            ip.save()
            res = json.dumps({'code': 200, 'msg': "IP Editada"})
            return HttpResponse(res, content_type='application/json')
        except Ip_Registro.DoesNotExist:
            ip = Ip_Registro()
            ip.ip = request.POST['ip']
            ip.estado = True
            ip.save()
            res = json.dumps({'code': 200, 'msg': "IP Registrada"})
            return HttpResponse(res, content_type='application/json')
    else:
        return HttpResponseRedirect('/')


@login_required(login_url='/')
def desactivar_ip_admin(request):
    if request.user.is_authenticated() and 'id' in request.GET:
        try:
            ip = Ip_Registro.objects.get(id=request.GET['id'])
            ip.estado = False
            ip.save()
            res = json.dumps({'code': 200, 'msg': "IP desactivada"})
            return HttpResponse(res, content_type='application/json')
        except Ip_Registro.DoesNotExist:
            res = json.dumps({'code': 404, 'msg': "IP no encontrada"})
            return HttpResponse(res, content_type='application/json')
    else:
        return HttpResponseRedirect('/')


@login_required(login_url='/')
def activar_ip_admin(request):
    if request.user.is_authenticated() and 'id' in request.GET:
        try:
            ip = Ip_Registro.objects.get(id=request.GET['id'])
            ip.estado = True
            ip.save()
            res = json.dumps({'code': 200, 'msg': "IP activada"})
            return HttpResponse(res, content_type='application/json')
        except Ip_Registro.DoesNotExist:
            res = json.dumps({'code': 404, 'msg': "IP no encontrada"})
            return HttpResponse(res, content_type='application/json')
    else:
        return HttpResponseRedirect('/')


@login_required(login_url='/')
def editar_ip(request):
    if request.user.is_authenticated():
        try:
            ip = Ip_Registro.objects.get(id=request.POST['id'])
            ip.ip = request.POST['ip']
            ip.save()
            request.session['opcion'] = 4
            request.session['msg'] = 'IP editada con exito'
            return HttpResponseRedirect('view_becas')
        except Beca.DoesNotExist:
            return HttpResponseRedirect('inicio')
    else:
        return HttpResponseRedirect('/')


# ----------prestar salar sustentaciones, cursos y reuniones
@login_required(login_url='/')
def buscar_salas_admin_sustentacion(request):
    if request.user.is_authenticated():
        # se obtiene el mes en numero
        date = request.GET['fecha'].split('-')
        fecha = datetime.date(day=int(date[2]), month=int(date[1]),
                              year=int(date[0]))
        edificio = Edificio.objects.get(id=request.GET['id'])
        salas = Sala.objects.filter(edificio=edificio).exclude(
            estado=2).order_by('tipo')
        ahora = datetime.datetime.now()

        if len(salas) == 0:
            text = '<h3 class="accent-1 red-text">%s Sin salas disponibles</h3>' % (
            edificio.codigo.upper())
            return HttpResponse(text)

        tablas = """
            <h3 class="accent-1 red-text">%s, %s</h3>
            <div class="row">
        """ % (edificio.codigo.upper(), fecha)
        conta_tablas = 0

        for s in salas:
            if conta_tablas % 3 == 0:
                tablas += """
                    </div>
                    <div class="row">
                """

            head = """
                <div class="col s4">
                <table class="card centered highlight" border>
                    <thead>
                        <tr class="red darken-1 white-text">
                            <th colspan=2>%s (%s), %s</th>
                        </tr>
                        <tr>
                            <th>Turno</th>
                            <th>Detalle</th>                            
                        </tr>
                    </thead>
                """ % (s.codigo, s.capacidad, ['Audiovisuales',
                                               'Aula virtual',
                                               'Auditorio'][s.tipo])

            sala_turnos = Turno_Sala.objects.filter(sala=s).filter(
                turno__dia=(fecha.isoweekday() - 1)).exclude(
                estado=1).order_by('turno__time_start')

            if len(sala_turnos) == 0:
                body = """
                    <tbody>
                        <tr>
                            <td colspan=2>
                                Sala sin turnos, Contectenos para mas detalles
                            </td>                            
                        </tr>
                    </tbody>
                </table>
                </div>

                """
                tablas += head + body
            else:
                tr = ""
                for st in sala_turnos:
                    if (
                            st.estado == 2 and st.hasta != None and fecha > st.hasta) or st.estado == 0:
                        prestamos = Prestamo.objects.filter(
                            date_turno=fecha).filter(turno_sala=st).filter(
                            estado=0)
                        if len(prestamos) == 0:
                            if st.turno.time_start > ahora.time() or fecha > ahora.date():
                                # la opcion viene de buscar salas para prestamos de cursos/reuniones
                                if 'opcion' in request.GET:
                                    tr += """
                                    <tr>
                                        <td>%s a %s</td>
                                        <td>
                                        Libre
                                            <a onclick="ver_form_cursos('%s')" 
                                            class="waves-effect waves-circle
                                            waves-light btn-floating secondary-content">
                                                <i class="material-icons">add</i>
                                            </a>
                                        </td>
                                    </tr>
                                    """ % (str(st.turno.time_start)[:5],
                                                str(st.turno.time_end)[:5],
                                                str(st.id))
                                else:
                                    tr += """
                                    <tr>
                                        <td>%s a %s</td>
                                        <td>
                                            Libre
                                            <a onclick="ver_form_sustentacion('%s')" 
                                            class="waves-effect waves-circle
                                            waves-light btn-floating 
                                            secondary-content">
                                                <i class="material-icons">add</i>
                                            </a>
                                        </td>
                                    </tr>
                                    """ % (str(st.turno.time_start)[:5],
                                                str(st.turno.time_end)[:5],
                                                str(st.id))
                        else:
                            # la opcion viene de buscar salas para prestamos de cursos/reuniones
                            if prestamos[0].tipo == 1 and not 'opcion' in request.GET:
                                tr += u"""
                                <tr>
                                    <td>%s a %s</td>
                                    <td>
                                        Sustentación de %s de %s
                                        <a onclick="desactivar_prestamo_docente('%s')"
                                        class="waves-effect waves-circle 
                                        waves-light btn-floating 
                                        secondary-content red">
                                            <i class="material-icons">delete</i>
                                        </a>
                                    </td>
                                </tr>
                                """ % (str(st.turno.time_start)[:5],
                                       str(st.turno.time_end)[:5],
                                       prestamos[0].solicitante,
                                       prestamos[0].carrera.nombre,
                                       prestamos[0].id)
                            elif 'opcion' in request.GET:
                                # curso
                                if prestamos[0].tipo == 2:
                                    tr += """
                                    <tr>
                                        <td>%s a %s</td>
                                        <td>
                                            Curso de %s de %s
                                            <a onclick="desactivar_prestamo_docente('%s')" 
                                            class="waves-effect waves-circle
                                            waves-light btn-floating 
                                            secondary-content red">
                                                <i class="material-icons">delete</i>
                                            </a>
                                        </td>
                                    </tr>
                                """ % (str(st.turno.time_start)[:5],
                                       str(st.turno.time_end)[:5],
                                       prestamos[0].solicitante,
                                       prestamos[0].carrera.nombre,
                                       prestamos[0].id)
                                # reunion
                                elif prestamos[0].tipo == 3:
                                    tr += u"""
                                    <tr>
                                        <td>%s a %s</td>
                                        <td>
                                            Reunión de %s para %s
                                            <a onclick="desactivar_prestamo_docente('%s')" 
                                            class="waves-effect waves-circle 
                                            waves-light btn-floating 
                                            secondary-content red">
                                            <i class="material-icons">delete</i>
                                            </a>
                                        </td>
                                    </tr>
                                    """ % (str(st.turno.time_start)[:5],
                                           str(st.turno.time_end)[:5],
                                           prestamos[0].solicitante,
                                           prestamos[0].detalle,
                                           prestamos[0].id)

                body = """
                    <tbody>
                        %s
                    </tbody>
                </table>
                </div>                
                """ % tr
                tablas += head + body
            conta_tablas += 1
        if conta_tablas % 3 != 0:
            tablas += "</div>"
        return HttpResponse(tablas.encode('utf-8'))
    else:
        return HttpResponseRedirect('/')


@login_required(login_url='/')
def add_prestamo_sustentacion_admin(request):
    if request.user.is_authenticated():
        date = request.POST['fecha_sustentacion'].split('-')
        fecha = datetime.date(day=int(date[2]), month=int(date[1]),
                              year=int(date[0]))
        carrera = Carrera.objects.get(codigo=request.POST['carrera'])
        turno_sala = Turno_Sala.objects.get(
            id=request.POST['sala_turno_sustentacion'])
        prestamo = Prestamo()
        prestamo.carrera = carrera
        prestamo.turno_sala = turno_sala
        prestamo.date_turno = fecha
        prestamo.ip = request.client_ip
        prestamo.solicitante = request.POST['solicitante']
        prestamo.tel = request.POST['tel']
        prestamo.tipo = 1
        prestamo.matriculados = turno_sala.sala.capacidad
        prestamo.usuario = Persona.objects.get(
            user__username=request.session['usuario']).user.first_name
        prestamo.save()

        if 'msg' not in request.session:
            request.session[
                'msg'] = 'Prestamo para sustentacion realizado con exito'

        return HttpResponseRedirect('inicio')
    else:
        return HttpResponseRedirect('/')


@login_required(login_url='/')
def add_prestamo_cursos_admin(request):
    if request.user.is_authenticated():
        date = request.POST['fecha_curso'].split('-')
        fecha = datetime.date(day=int(date[2]), month=int(date[1]),
                              year=int(date[0]))
        carrera = Carrera.objects.get(codigo=request.POST['carrera_cursos'])
        turno_sala = Turno_Sala.objects.get(
            id=request.POST['sala_turno_curso'])
        prestamo = Prestamo()
        prestamo.carrera = carrera
        prestamo.turno_sala = turno_sala
        prestamo.date_turno = fecha
        prestamo.ip = request.client_ip
        prestamo.detalle = request.POST['descripcion']
        prestamo.solicitante = request.POST['solicitante']
        prestamo.tel = request.POST['tel']
        prestamo.tipo = request.POST['tipo']
        prestamo.matriculados = turno_sala.sala.capacidad
        prestamo.usuario = Persona.objects.get(
            user__username=request.session['usuario']).user.first_name
        prestamo.save()

        if 'msg' not in request.session:
            request.session['msg'] = 'Prestamo realizado con exito'

        return HttpResponseRedirect('inicio')
    else:
        return HttpResponseRedirect('/')


@login_required(login_url='/')
def save_prestamo_masivo(request):
    if request.user.is_authenticated():

        date = request.POST['fecha_inicial'].split('-')
        fecha_inicial = datetime.date(day=int(date[2]), month=int(date[1]),
                                      year=int(date[0]))
        date = request.POST['fecha_final'].split('-')
        fecha_final = datetime.date(day=int(date[2]), month=int(date[1]),
                                    year=int(date[0]))

        if fecha_inicial >= fecha_final:
            res = json.dumps({'code': 200,
                              'msg': "la fecha inicial debe ser mayor a la final"})
            return HttpResponse(res, content_type='application/json')

        carrera = Carrera.objects.get(
            codigo=request.POST['carrera_cursos_masivo'])
        turno_sala = Turno_Sala.objects.get(id=request.POST['turno'])

        while fecha_inicial.isoweekday() - 1 != turno_sala.turno.dia:
            fecha_inicial = fecha_inicial + datetime.timedelta(days=1)

        registros = 0
        salida = ""
        while fecha_inicial <= fecha_final:
            prestamos_turno = Prestamo.objects.filter(
                date_turno=fecha_inicial, turno_sala=turno_sala, estado=0)
            if len(prestamos_turno) == 0:
                prestamo = Prestamo()
                prestamo.carrera = carrera
                prestamo.turno_sala = turno_sala
                prestamo.date_turno = fecha_inicial
                prestamo.ip = request.client_ip
                prestamo.detalle = request.POST['descripcion']
                prestamo.solicitante = request.POST['solicitante']
                prestamo.tel = request.POST['tel']
                prestamo.tipo = request.POST['tipo']
                prestamo.matriculados = turno_sala.sala.capacidad
                prestamo.usuario = Persona.objects.get(
                    user__username=request.session[
                        'usuario']).user.first_name
                prestamo.save()
                registros += 1
            else:
                salida += "{0},".format(fecha_inicial)
            fecha_inicial = fecha_inicial + datetime.timedelta(days=7)

        if salida != "":
            res = json.dumps({'code': 200,
                              'msg': "{0} registrados, no registrados {1}".format(
                                  registros, salida)})
        else:
            res = json.dumps(
                {'code': 200, 'msg': "{0} registrados".format(registros)})
        return HttpResponse(res, content_type='application/json')
    else:
        return HttpResponseRedirect('/')


# -----------------end prestar salar sustentaciones, cursos y reuniones


# --------------------Crud Turnos---------------

@login_required(login_url='/')
def view_turnos(request):
    if request.user.is_authenticated():
        persona = Persona.objects.get(
            user__username=request.session['usuario'])
        # turnos = Turno.objects.filter(dia=0)
        # return render(request, 'diseraca/admin/turnos.html', {'admin': persona, 'turnos': turnos})
        return render(request, 'diseraca/admin/turnos.html',
                      {'admin': persona})
    else:
        return HttpResponseRedirect('/')


@login_required(login_url='/')
def get_turno_dia(request):
    if request.user.is_authenticated() and 'dia' in request.GET:
        turnos = Turno.objects.filter(dia=request.GET['dia']).order_by(
            'time_start')
        data = serializers.serialize('json', turnos, fields=('time_start',
                                                             'time_end',
                                                             'estado',
                                                             'dia'))
        return HttpResponse(data, content_type='application/json')
    else:
        # print "no esta el dia"
        return HttpResponseRedirect('/')


@login_required(login_url='/')
def save_turno(request):
    if request.user.is_authenticated():
        try:
            turno = Turno.objects.get(id=request.POST["turno[pk]"])
            turno.time_start = request.POST["turno[fields][time_start]"]
            turno.time_end = request.POST["turno[fields][time_end]"]
            turno.estado = request.POST["turno[fields][estado]"]
            turno.dia = request.POST["turno[fields][dia]"]
            # print request.POST["turno[fields][dia]"], 'editar'
            turno.save()
            return HttpResponse("Editado Exitosamente")
        except Turno.DoesNotExist:
            turno = Turno()
            turno.time_start = request.POST["turno[fields][time_start]"]
            turno.time_end = request.POST["turno[fields][time_end]"]
            turno.estado = request.POST["turno[fields][estado]"]
            turno.dia = request.POST["turno[fields][dia]"]
            # print request.POST["turno[fields][dia]"], 'nuevo'
            turno.save()
            return HttpResponse("Creado con exito")
    else:

        return HttpResponseRedirect('/')


@login_required(login_url='/')
def view_docentes(request):
    if request.user.is_authenticated():
        persona = Persona.objects.get(
            user__username=request.session['usuario'])
        if 'msg' in request.session:
            msg = request.session['msg']
            del request.session['msg']
            return render(request, 'diseraca/admin/docentes.html',
                          {'admin': persona, 'msg': msg})
        return render(request, 'diseraca/admin/docentes.html',
                      {'admin': persona})
    else:
        return HttpResponseRedirect('/')


@login_required(login_url='/')
def get_turno_sala(request):
    if request.user.is_authenticated() and 'sala' in request.GET:
        x = Turno_Sala.objects.filter(sala_id=request.GET["sala"])
        t = [
            {"pk": w.id, "fields": {"estado": w.estado, "hasta": str(w.hasta)
                , "sala": {"codigo": w.sala.codigo, "edificio":
                    w.sala.edificio_id, "pk": w.sala_id},
                                    "turno": {"time_start": str(
                                        w.turno.time_start),
                                              "time_end": str(
                                                  w.turno.time_end),
                                              "dia": w.turno.dia,
                                              "pk": w.turno_id}}} for w in x]
        data = json.dumps(t)
        return HttpResponse(data, content_type='application/json')
    else:
        return HttpResponseRedirect('/')


@login_required(login_url='/')
def get_turno_dia_sala(request):
    if request.user.is_authenticated() and 'sala' in request.GET:
        x = Turno_Sala.objects.filter(sala_id=request.GET["sala"],
                                      turno__dia=request.GET[
                                          'dia']).order_by(
            'turno__time_start')
        t = [{"id": w.id, "time_start": str(w.turno.time_start),
              "time_end": str(w.turno.time_end)} for w in x]
        data = json.dumps(t)
        return HttpResponse(data, content_type='application/json')
    else:
        return HttpResponseRedirect('/')


# --------------------end Crud Turnos---------------


# -------------CRUD Edificios------------

@login_required(login_url='/')
def save_edificio(request):
    if request.user.is_authenticated():
        try:
            edif = Edificio.objects.get(id=request.POST["edif[pk]"])
            edif.codigo = request.POST["edif[fields][codigo]"]
            edif.nombre = request.POST["edif[fields][nombre]"]
            edif.save()
            return HttpResponse("Editado Exitosamente")
        except Edificio.DoesNotExist:
            edif = Edificio()
            edif.codigo = request.POST["edif[fields][codigo]"]
            edif.nombre = request.POST["edif[fields][nombre]"]
            edif.save()
            return HttpResponse("Creado con exito")
    else:
        return HttpResponseRedirect('/')


@login_required(login_url='/')
def get_salas(request):
    if request.user.is_authenticated():
        salas = Sala.objects.filter(edificio_id=request.GET["pk"])
        data = serializers.serialize('json', salas, fields=(
        'edificio', 'codigo', 'capacidad', 'tipo', 'estado'))
        return HttpResponse(data, content_type='application/json')
    else:
        return HttpResponseRedirect('/')


@login_required(login_url='/')
def save_sala(request):
    if request.user.is_authenticated():
        try:
            sala = Sala.objects.get(id=request.POST["sala[pk]"])
            sala.codigo = request.POST["sala[fields][codigo]"]
            sala.edificio_id = request.POST["sala[fields][edificio]"]
            sala.capacidad = request.POST["sala[fields][capacidad]"]
            sala.tipo = request.POST["sala[fields][tipo]"]
            sala.estado = request.POST["sala[fields][estado]"]
            sala.save()
            return HttpResponse("Editado Exitosamente")
        except Sala.DoesNotExist:
            sala = Sala()
            sala.codigo = request.POST["sala[fields][codigo]"]
            sala.edificio_id = request.POST["sala[fields][edificio]"]
            sala.capacidad = request.POST["sala[fields][capacidad]"]
            sala.tipo = request.POST["sala[fields][tipo]"]
            sala.estado = request.POST["sala[fields][estado]"]
            sala.save()
            return HttpResponse("Creado con exito")
    else:
        return HttpResponseRedirect('/')


@login_required(login_url='/')
def save_sala_turno(request):
    if request.user.is_authenticated():
        try:
            sala = Sala.objects.get(id=request.POST["sala[pk]"])
            sala.codigo = request.POST["sala[fields][codigo]"]
            sala.edificio_id = request.POST["sala[fields][edificio]"]
            sala.capacidad = request.POST["sala[fields][capacidad]"]
            sala.tipo = request.POST["sala[fields][tipo]"]
            sala.estado = request.POST["sala[fields][estado]"]
            sala.save()
            return HttpResponse("Editado Exitosamente")
        except Sala.DoesNotExist:
            sala = Sala()
            sala.codigo = request.POST["sala[fields][codigo]"]
            sala.edificio_id = request.POST["sala[fields][edificio]"]
            sala.capacidad = request.POST["sala[fields][capacidad]"]
            sala.tipo = request.POST["sala[fields][tipo]"]
            sala.estado = request.POST["sala[fields][estado]"]
            sala.save()
            return HttpResponse("Creado con exito")
    else:
        return HttpResponseRedirect('/')


@login_required(login_url='/')
def save_salaTurno_turno(request):
    if request.user.is_authenticated():
        try:
            salaTurno = Turno_Sala.objects.get(id=request.POST["data[pk]"])
            salaTurno.sala_id = request.POST.get('data[fields][sala][pk]')
            salaTurno.turno_id = request.POST.get('data[fields][turno][pk]')
            salaTurno.estado = request.POST.get('data[fields][estado]', 0)
            if request.POST.get('data[fields][hasta]', None) == '':
                salaTurno.hasta = None
            else:
                salaTurno.hasta = request.POST.get('data[fields][hasta]')
            salaTurno.save()
            return HttpResponse("Editado Exitosamente")
        except Turno_Sala.DoesNotExist:
            salaTurno = Turno_Sala()
            salaTurno.sala_id = request.POST.get('data[fields][sala][pk]')
            salaTurno.turno_id = request.POST.get('data[fields][turno][pk]')
            salaTurno.estado = request.POST.get('data[fields][estado]', 0)
            if request.POST.get('data[fields][hasta]', None) == '':
                salaTurno.hasta = None
            else:
                salaTurno.hasta = request.POST.get('data[fields][hasta]')
            salaTurno.save()
            return HttpResponse("Creado con exito")
    else:
        return HttpResponseRedirect('/')


@login_required(login_url='/')
def get_docentes(request):
    if request.user.is_authenticated():
        x = Profesor.objects.all().order_by('persona__user__username')
        t = [{"pk": w.id, 'tel': w.tel,
              "persona": {"nombre": w.persona.user.first_name,
                          'email': w.persona.user.email,
                          "codigo": w.persona.user.username},
              'dpto': {'codigo_dpto': w.departamento.codigo,
                       'nombre_dpto': w.departamento.nombre}} for w in x]
        data = json.dumps(t)
        return HttpResponse(data, content_type='application/json')
    else:
        return HttpResponseRedirect('/')


@login_required(login_url='/')
def get_turnos_docente(request):
    if request.user.is_authenticated():
        try:
            user = User.objects.get(username=request.GET['docente'])
            x = Prestamo.objects.filter(profesor__persona__user=user,
                                        date_turno__lte=request.GET[
                                            'fecha_fin'],
                                        date_turno__gte=request.GET[
                                            'fecha_inicio'])
            t = [{'pk': w.id, 'nom_materia': w.nombre,
                  'cod_materia': w.carrera.codigo + w.codigo,
                  'mat_grupo': w.grupo,
                  'fecha_prestamo': str(w.date_prestamo)[:16],
                  'fecha_turno': str(w.date_turno), 'usuario': w.usuario,
                  'sala': w.turno_sala.sala.codigo,
                  'turno': str(w.turno_sala.turno.time_start) + '-' + str(
                      w.turno_sala.turno.time_end),
                  'ip': w.ip, 'estado': w.estado} for w in x]

            res = json.dumps(
                {'code': 200, 'msg': t, 'docente': user.first_name.upper()})
            return HttpResponse(res, content_type='application/json')

        except Profesor.DoesNotExist:
            print('error de docente')
        except Exception as e:
            print (e.message)
    else:
        return HttpResponseRedirect('/')


@login_required(login_url='/')
def get_dptos(request):
    if request.user.is_authenticated():
        dptos = Departamento.objects.all()
        t = [{'codigo': w.codigo, 'nombre': w.nombre} for w in dptos]
        data = json.dumps(t)
        return HttpResponse(data, content_type='application/json')
    else:
        return HttpResponseRedirect('/')


@login_required(login_url='/')
def save_docente(request):
    if request.user.is_authenticated():
        try:
            docente = Profesor.objects.get(id=request.POST['data[pk]'])
            docente.tel = request.POST['data[tel]']
            docente.persona.user.first_name = request.POST[
                'data[persona][nombre]'].lower()
            docente.persona.user.email = request.POST[
                'data[persona][email]'].lower()
            docente.departamento_id = request.POST['data[dpto][codigo_dpto]']
            docente.persona.user.save()
            docente.save()
            return HttpResponse('Profesor Editado exitosamente')

        except Profesor.DoesNotExist:
            try:
                docente = Profesor()
                docente.persona.user.username = request.POST[
                    'data[persona][codigo]']
                docente.tel = request.POST['data[tel]']
                docente.persona.user.first_name = request.POST[
                    'data[persona][nombre]'].lower()
                docente.persona.user.email = request.POST[
                    'data[persona][email]'].lower()
                docente.departamento_id = request.POST[
                    'data[dpto][codigo_dpto]']
                docente.persona.user.save()
                docente.save()
            except (User.DoesNotExist, Persona.DoesNotExist):
                user = User()
                user.username = request.POST['data[persona][codigo]']
                user.first_name = request.POST[
                    'data[persona][nombre]'].lower()
                user.email = request.POST['data[persona][email]'].lower()
                user.save()
                persona = Persona()
                persona.user = user
                persona.tipo = 0
                persona.save()

                profesor = Profesor()
                profesor.persona = persona
                profesor.departamento_id = request.POST[
                    'data[dpto][codigo_dpto]']
                profesor.tel = request.POST['data[tel]']
                profesor.save()

            return HttpResponse('Profesor Guardado exitosamente')

    else:
        return HttpResponseRedirect('/')


def unicode_csv_reader(utf8_data, dialect=csv.excel, **kwargs):
    csv_reader = csv.reader(utf8_data, dialect=dialect, delimiter=";",
                            **kwargs)
    for row in csv_reader:
        yield [unicode(cell, 'utf-8', errors='ignore') for cell in row]


@login_required(login_url='/')
def save_docente_csv(request):
    if request.user.is_authenticated():
        #
        h = threading.Thread(target=background_docente,
                             args=(request.FILES.get('file_docente'),))
        h.start()
        messages.success(request, 'Se esta procesando el archivo en '
                                  'background')
        return HttpResponseRedirect('view_docentes')
    else:
        return HttpResponseRedirect('/')


def background_docente(file):
    data = unicode_csv_reader(file)
    add = 0
    update = 0
    for COD_PROFESOR, NOMBRES, COD_DPTO, EMAIL, NOMDPTO in data:
        try:
            dpto = Departamento.objects.get(codigo=str(COD_DPTO))
            user = User.objects.get(username=str(COD_PROFESOR))
            profesor = Profesor.objects.get(persona__user=user)
            profesor.departamento = dpto
            profesor.persona.user.first_name = NOMBRES.lower()
            profesor.persona.user.save()
            update += 1
        except Departamento.DoesNotExist:
            try:
                dpto = Departamento()
                dpto.codigo = str(COD_DPTO)
                dpto.nombre = NOMDPTO.lower()
                dpto.save()
                profesor = Profesor.objects.get(
                    persona__user__username=str(COD_PROFESOR))
                profesor.persona.user.email = EMAIL.lower()
                profesor.persona.user.first_name = NOMBRES.lower()
                profesor.persona.user.save()
                update += 1
            except Profesor.DoesNotExist:
                user = User()
                user.username = str(COD_PROFESOR)
                user.email = EMAIL.lower()
                user.first_name = NOMBRES.lower()
                user.set_password(str(COD_PROFESOR))
                user.save()
                persona = Persona()
                persona.user = user
                persona.save()

                profesor = Profesor()
                profesor.persona = persona
                dpto = Departamento.objects.get(codigo=str(COD_DPTO))
                profesor.departamento = dpto
                profesor.tel = '0000000000'
                profesor.save()
                add += 1
        except User.DoesNotExist:
            user = User()
            user.username = str(COD_PROFESOR)
            user.email = EMAIL.lower()
            user.first_name = NOMBRES[:29].lower()
            user.set_password(str(COD_PROFESOR))
            user.save()
            persona = Persona()
            persona.user = user
            persona.save()

            profesor = Profesor()
            profesor.persona = persona
            dpto = Departamento.objects.get(codigo=COD_DPTO)
            profesor.departamento = dpto
            profesor.tel = '0000000000'
            profesor.save()
            add += 1
        except Profesor.DoesNotExist:
            user = User.objects.get(username=str(COD_PROFESOR))
            persona = Persona.objects.get(user=user)
            profesor = Profesor()
            profesor.persona = persona
            dpto = Departamento.objects.get(codigo=COD_DPTO)
            profesor.departamento = dpto
            profesor.tel = '0000000000'
            profesor.save()
            add += 1

    print add, 'add'
    print update, 'update'


@login_required(login_url='/')
def save_carga_docentes_csv(request):
    if request.user.is_authenticated():
        h = threading.Thread(target=background_carga_docente,
                             args=(request.FILES.get('file_carga_docente'),))
        h.start()
        messages.success(request, 'Se esta procesando el archivo en '
                                  'background')
        return HttpResponseRedirect('view_docentes')
    else:
        return HttpResponseRedirect('/')


def background_carga_docente(file):
    data = unicode_csv_reader(file)
    add = 0
    update = 0
    imposible = 0
    for COD_CARRERA, COD_DPTO, COD_MATERIA, NOMMATE, GRUPO, COD_PROFESOR, \
        MATRICULADOS, NOM_CARRERA in data:
        try:
            carrera = Carrera.objects.get(codigo=COD_CARRERA)
            carrera.nombre = NOM_CARRERA
            carrera.save()
            carga = Carga.objects.get(carrera=carrera,
                                      codigo=COD_MATERIA
                                      , grupo=GRUPO.lower())

            profesor = Profesor.objects.get(
                persona__user__username=COD_PROFESOR)
            carga.profesor = profesor
            carga.matriculados = MATRICULADOS
            carga.grupo = GRUPO.lower()
            carga.save()
            update += 1
        except Profesor.DoesNotExist:
            imposible += 1
        except Carrera.DoesNotExist:
            try:
                carrera = Carrera()
                carrera.codigo = COD_CARRERA
                dpto = Departamento.objects.get(codigo=COD_DPTO)
                carrera.departamento = dpto
                carrera.nombre = NOM_CARRERA.lower()
                carrera.save()
                carga = Carga()
                carga.carrera = carrera
                profesor = Profesor.objects.get(
                    persona__user__username=COD_PROFESOR)
                carga.profesor = profesor
                carga.matriculados = MATRICULADOS
                carga.codigo = COD_MATERIA
                carga.nombre = NOMMATE.lower()
                carga.grupo = GRUPO.lower()
                carga.save()
                add += 1
            except (Profesor.DoesNotExist, Departamento.DoesNotExist):
                imposible += 1
        except Carga.DoesNotExist:
            carga = Carga()
            carrera = Carrera.objects.get(codigo=COD_CARRERA)
            carga.carrera = carrera
            try:
                profesor = Profesor.objects.get(
                    persona__user__username=COD_PROFESOR)
                carga.profesor = profesor
                carga.matriculados = MATRICULADOS
                carga.codigo = COD_MATERIA
                carga.nombre = NOMMATE.lower()
                carga.grupo = GRUPO.lower()
                carga.save()
                add += 1
            except Profesor.DoesNotExist:
                imposible += 1

    print add, 'add'
    print update, 'update'
    print imposible, 'imposible'


@login_required(login_url='/')
def save_carga_docente(request):
    if request.user.is_authenticated() and request.method == 'POST':
        print(request.POST, 'post')
        try:
            carga = Carga.objects.get(id=request.POST['id'])
            carga.carrera = Carrera.objects.get(
                codigo=request.POST['carrera'])
            docente = Profesor.objects.get(
                persona__user__username=request.POST['profesor'])
            carga.profesor = docente
            carga.codigo = request.POST['codigo']
            carga.nombre = request.POST['nombre']
            carga.grupo = request.POST['grupo']
            carga.matriculados = request.POST['matriculados']
            carga.save()
            data = json.dumps({'type': 200,
                               'msg': 'Carga editada exitosamente'})
            return HttpResponse(data, content_type='application/json')

        except (Carga.DoesNotExist, ValueError):
            carga = Carga()
            carga.carrera = Carrera.objects.get(
                codigo=request.POST['carrera'])
            docente = Profesor.objects.get(
                persona__user__username=request.POST['profesor'])
            # print docente
            carga.profesor = docente
            carga.codigo = request.POST['codigo']
            carga.nombre = request.POST['nombre']
            carga.grupo = request.POST['grupo']
            carga.matriculados = request.POST['matriculados']
            carga.save()
            data = json.dumps({'type': 200, 'msg': 'Carga creada '
                                                   'exitosamente'})
            return HttpResponse(data, content_type='application/json')
        except Carrera.DoesNotExist:
            data = json.dumps({'type': 200, 'msg': 'La carrera no existe'})
            return HttpResponse(data, content_type='application/json')

    else:
        return HttpResponseRedirect('/')


@login_required(login_url='/')
def buscar_carga_docente(request):
    if request.user.is_authenticated() and 'docente' in request.GET:
        docente = Profesor.objects.get(persona__user__username=str(
            request.GET['docente']))
        cargas = Carga.objects.filter(profesor=docente)
        t = [{'codigo': w.codigo, 'nombre': w.nombre.upper(),
              'grupo': w.grupo,
              'matriculados': w.matriculados, 'id': w.id, 'carrera':
                  w.carrera.codigo, 'profesor': w.profesor.id,
              'carrera': w.carrera.codigo} for w in cargas]
        data = json.dumps({'code': 200, 'msg': t,
                           'docente': docente.persona.user.first_name.upper()})
        return HttpResponse(data, content_type='application/json')
    else:
        return HttpResponseRedirect('/')


@login_required(login_url='/')
def get_carreras(request):
    if request.user.is_authenticated():
        carreras = Carrera.objects.all()
        t = [{'codigo': w.codigo, 'nombre': w.nombre, 'departamento':
            {'codigo': w.departamento.codigo,
             'nombre': w.departamento.nombre}
              } for w in carreras]
        data = json.dumps(t)
        return HttpResponse(data, content_type='application/json')
    else:
        return HttpResponseRedirect('/')


# ------------crud semestre---------------

@login_required(login_url='/')
def view_estadisticas(request):
    if request.user.is_authenticated():
        persona = Persona.objects.get(
            user__username=request.session['usuario'])
        return render(request, 'diseraca/admin/estadisticas.html',
                      {'admin': persona})
    else:
        return HttpResponseRedirect('/')


@login_required(login_url='/')
def save_semester(request):
    if request.user.is_authenticated():
        if request.method == 'POST':
            if 'id' in request.POST:
                semestre = Semestre.objects.get(id=request.POST['id'])
                msg = "Editado con exito"
            else:
                semestre = Semestre()
                msg = "Creado con exito"
            date = request.POST['fecha_inicio'].split('-')
            fecha_inicio = datetime.date(day=int(date[2]),
                                         month=int(date[1]),
                                         year=int(date[0]))

            date = request.POST['fecha_fin'].split('-')
            fecha_fin = datetime.date(day=int(date[2]), month=int(date[1]),
                                      year=int(date[0]))

            semestre.nombre = request.POST['semestre']
            semestre.fecha_inicio = fecha_inicio
            semestre.fecha_fin = fecha_fin
            semestre.save()

        res = json.dumps({'code': 200, 'msg': msg})
        return HttpResponse(res, content_type='application/json')

    else:
        return HttpResponseRedirect('/')


@login_required(login_url='/')
def get_semestres(request):
    if request.user.is_authenticated():
        semestres = Semestre.objects.all().order_by('nombre')
        t = [{'id': w.id, 'semestre': w.nombre,
              'fecha_inicio': str(w.fecha_inicio),
              'fecha_fin': str(w.fecha_fin)} for w in semestres]

        res = json.dumps({'code': 200, 'msg': t})
        return HttpResponse(res, content_type='application/json')
    else:
        return HttpResponseRedirect('/')


# ---------------end crud semestre---------


# ------------------reporte de becas por inasistencia o retardos----

@login_required(login_url='/')
def get_report_becas(request):
    if request.user.is_authenticated():
        becas = Beca.objects.filter(persona__user__is_active=True)
        list_reportes = list()
        hoy = datetime.datetime.now().date()
        for beca in becas:
            inasistencias = 0
            tardes = 0
            asistencias = Asistencia.objects.filter(beca_turno__beca=beca,
                                                    date_turno__lt=hoy)
            for asis in asistencias:
                if asis.tipo == 0:
                    inasistencias += 1
                elif asis.tipo == 1:
                    tardes += 1
            total = inasistencias * 2 + tardes
            reporte = {'id': beca.id, 'nick': beca.nick,
                       'inasistencias': inasistencias,
                       'tarde': tardes, 'total': total}
            list_reportes.append(reporte)

        res = json.dumps({'code': 200, 'msg': list_reportes})
        return HttpResponse(res, content_type='application/json')
    else:
        return HttpResponseRedirect('/')


@login_required(login_url='/')
def get_inasistencias_beca(request):
    if request.user.is_authenticated():
        try:
            hoy = datetime.datetime.now().date()
            beca = Beca.objects.get(id=request.GET['id'])
            asistencias = Asistencia.objects.filter(beca_turno__beca=beca,
                                                    date_turno__lt=hoy,
                                                    tipo=0)
            msg = [{'date_turno': str(w.date_turno),
                    'datetime_registro': str(w.datetime_registro)[:16],
                    'ip': str(w.ip), 'turno': u"{0}-{1}".format(
                    str(w.beca_turno.turno.time_start)[:5],
                    str(w.beca_turno.turno.time_end)[:5])} for w in
                   asistencias]
            res = json.dumps({'code': 200, 'msg': msg})
            return HttpResponse(res, content_type='application/json')
        except Exception as e:
            # print e.message
            res = json.dumps({'code': 404, 'msg': e.message})
            return HttpResponse(res, content_type='application/json')
    else:
        return HttpResponseRedirect('/')


@login_required(login_url='/')
def get_asistencias_tarde(request):
    if request.user.is_authenticated():
        try:
            hoy = datetime.datetime.now().date()
            beca = Beca.objects.get(id=request.GET['id'])
            asistencias = Asistencia.objects.filter(beca_turno__beca=beca,
                                                    date_turno__lte=hoy,
                                                    tipo=1)
            msg = [{'date_turno': str(w.date_turno),
                    'datetime_registro': str(w.datetime_registro)[:16],
                    'ip': str(w.ip.ip), 'turno': u"{0}-{1}".format(
                    str(w.beca_turno.turno.time_start)[:5],
                    str(w.beca_turno.turno.time_end)[:5])} for w in
                   asistencias]
            res = json.dumps({'code': 200, 'msg': msg})
            return HttpResponse(res, content_type='application/json')
        except Exception as e:
            # print e.message
            res = json.dumps({'code': 404, 'msg': e})
            return HttpResponse(res, content_type='application/json')
    else:
        return HttpResponseRedirect('/')


# ------------------fin reporte de becas por inasistencia o retardos----


@login_required(login_url='/')
def mis_turnos(request):
    if request.user.is_authenticated():
        persona = Persona.objects.get(
            user__username=request.session['usuario'])
        beca = Beca.objects.get(persona=persona)
        turnos = Beca_Turno.objects.filter(beca=beca, status=True)
        hoy = datetime.datetime.now().date()
        asistencias = Asistencia.objects.filter(beca_turno__beca=beca,
                                                date_turno__lt=hoy).exclude(
            tipo=2)
        return render(request, 'diseraca/beca/turnos.html',
                      {'beca': beca, 'turnos': turnos,
                       'asistencias': asistencias,
                       'ip': request.client_ip})
    else:
        return HttpResponseRedirect('/')


# ----------crud admin-----------------

@login_required(login_url='/')
def get_admins(request):
    if request.user.is_authenticated():
        admins = Persona.objects.filter(tipo=2).exclude(
            user__username="06337")

        t = [{'id': w.id, 'codigo': w.user.username,
              'nombre': w.user.first_name,
              'email': w.user.email, 'is_active': w.user.is_active} for w in
             admins]
        data = json.dumps({'code': 200, 'msg': t})
        return HttpResponse(data, content_type='application/json')
    else:
        return HttpResponseRedirect('/')


@login_required(login_url='/')
def add_admin(request):
    if request.user.is_authenticated():
        print request.POST
        try:
            p = Persona.objects.get(user__username=request.POST['codigo'])
            p.user.first_name = request.POST['nombre']
            p.user.email = request.POST['email']
            p.user.set_password(request.POST['codigo'])
            p.user.save()
            p.tipo = 2
            p.save()

            res = json.dumps({'code': 200, 'msg': "Editado correctamente"})
            return HttpResponse(res, content_type='application/json')
        except Persona.DoesNotExist:
            user = User()
            user.username = request.POST['codigo']
            user.first_name = request.POST['nombre']
            user.email = request.POST['email']
            user.set_password(request.POST['codigo'])
            user.save()

            p = Persona()
            p.user = user
            p.tipo = 2
            p.save()

            res = json.dumps({'code': 200, 'msg': "nuevo creado con exito"})
            return HttpResponse(res, content_type='application/json')
    else:
        return HttpResponseRedirect('/')


@login_required(login_url='/')
def deactivte_admin(request):
    if request.user.is_authenticated():
        try:
            persona = Persona.objects.get(id=request.GET['id'])
            if persona.user.is_active:
                persona.user.is_active = False
                persona.user.save()
                res = json.dumps({'code': 200, 'msg': "Admin desactivado"})
                return HttpResponse(res, content_type='application/json')
            else:
                persona.user.is_active = True
                persona.user.save()
                res = json.dumps({'code': 200, 'msg': "Admin activado"})
                return HttpResponse(res, content_type='application/json')

        except Persona.DoesNotExist:
            res = json.dumps({'code': 200, 'msg': "Admin no encontrado"})
            return HttpResponse(res, content_type='application/json')
    else:
        return HttpResponseRedirect('/')


@login_required(login_url='/')
def cambiar_password(request):
    if request.user.is_authenticated() and request.GET['codigo']:
        user = User.objects.get(username=request.GET['codigo'])
        user.set_password(request.GET['codigo'])
        user.save()
        res = json.dumps({'code': 200, 'msg': "Contaseña cambiada con "
                                              "exito"})
        return HttpResponse(res, content_type='application/json')
    else:
        return HttpResponseRedirect('/')
# ----------fin crud admin-----------------
'''
@login_required(login_url='/')
def view_docentes(request):
    if request.user.is_authenticated():
        
        res = json.dumps({'code': 200, 'msg': "Mensaje o datos"})
        return HttpResponse(res, content_type='application/json')
    else:
        return HttpResponseRedirect('/')
        
        t = [{'codigo': w.codigo, 'nombre': w.nombre} for w in dptos]
        data = json.dumps(t)
        return HttpResponse(data, content_type='application/json')
'''
