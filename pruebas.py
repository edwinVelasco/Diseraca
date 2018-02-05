import re

cadena1 = "Edwin1004"
cadena2 = "Edwin"
cadena3 = "edwin"
cadena4 = "edwin1004"

patronMay = r"[A-Z]{1}"
patronNum = r"\d{2}"

if re.search(patronMay, cadena1) and re.search(patronNum, cadena1):
    print "encuentra el patron"
else:
    print "No encuentra el patron"



'''

import datetime

def dif_time(hora):
    ahora = datetime.datetime.now()
    fecha_ini = ahora + datetime.timedelta(days=7)

    print fecha_ini
    print (ahora.isoweekday() - 1)

dif_time(datetime.time(hour=17, minute=15, second=00))

def ver_turnos():
    archivo = open('turnos_inicio.csv', 'r')

    while True:
        linea = archivo.readline()
        if not linea:
            break
        s = linea.split(',')
        ss = s[0].split(':')
        t = datetime.time(hour=int(ss[0]), minute=00, second=00)
        print t, type(t)
        print type(s[0]), type(s[1]), type(s[2])

ver_turnos()

{% if turnos|length == 0 %}
                        <h5>No hay turnos para este dia</h5>
                    {% else %}
                        <table>
                            <thead>
                                <tr>
                                    <th>Turnos</th>
                                    <th>Estado</th>
                                    <th>Opciones</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr ng-repeat="turno in turnos">

                                </tr>
                                {% for turno in turnos %}
                                    <tr>
                                        <td>{{ turno.time_start }}-{{ turno.time_end }}</td>
                                        <td>
                                            {% if turno.estado == 0 %}
                                                Activo
                                            {% else %}
                                                Inactivo
                                            {% endif %}
                                        </td>
                                        <td>

                                        </td>
                                    </tr>
                                {% endfor %}

                            </tbody>
                        </table>
                    {% endif %}
                    
'''