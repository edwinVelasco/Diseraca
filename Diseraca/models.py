from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Departamento(models.Model):
    codigo = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=70)

    def __unicode__(self):
        return str(self.codigo)+', '+self.nombre


class Carrera(models.Model):
    departamento = models.ForeignKey('Departamento')
    codigo = models.CharField(max_length=3, primary_key=True)
    nombre = models.CharField(max_length=70)

    def __unicode__(self):
        return self.codigo+', '+self.nombre


class Carga(models.Model):
    carrera = models.ForeignKey('Carrera')
    profesor = models.ForeignKey('Profesor')
    codigo = models.CharField(max_length=7)#codigo de la materia
    nombre = models.CharField(max_length=45)#nombre de la materia
    grupo = models.CharField(max_length=1)
    matriculados = models.IntegerField()

    def __unicode__(self):
        return self.codigo+', '+self.nombre+', '+str(self.matriculados)


class Edificio(models.Model):
    nombre = models.CharField(max_length=25)
    codigo = models.CharField(max_length=5, unique=True)

    def __unicode__(self):
        return self.codigo


class Sala(models.Model):
    '''
        tipo = corresponde a si es sala de clase -->0, aula virtual -> 1 y auditorio --> 2
        estado = activo --> 0, mantenimiento --> 1, fuera de servicio --> 2
    '''
    tipos = (
        (0, 'Sala de clase'),
        (1, 'Aula virtual'),
        (2, 'Auditorio'),
    )
    estados = (
        (0, 'Activo'),
        (1, 'Mantenimiento'),
        (2, 'Fuera de servicio'),
    )
    edificio = models.ForeignKey('Edificio')
    codigo = models.CharField(max_length=10)
    capacidad = models.IntegerField()
    tipo = models.IntegerField(default=0, choices=tipos)
    estado = models.IntegerField(default=0, choices=estados)
    #['Sala de clase', 'Aula virtual', 'Auditorio']

    def __unicode__(self):
        return self.codigo+'. ' +['Activo', 'Mantenimiento', 'Fuera de servicio'][self.estado]+', '+self.edificio.nombre


class Turno(models.Model):
    days = (
        (0, 'Lunes'),
        (1, 'Martes'),
        (2, 'Miercoles'),
        (3, 'Jueves'),
        (4, 'Viernes'),
        (5, 'Sabado'),
    )
    estados = (
        (0, 'Activado'),
        (1, 'Desactivado'),
    )
    time_start = models.TimeField()# hora de inicio
    time_end = models.TimeField()# hora de fin
    # dia lunes -> 0, martes ->1, miercoles ->2, jueves ->3, viernes ->4 y sabado ->5.
    dia = models.IntegerField(choices=days)
    estado = models.IntegerField(default=0, help_text='activo --> 0, desactivado --> 1', choices=estados)
    def __unicode__(self):
        return str(self.time_start)+' a '+str(self.time_end)+'. '+['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado'][self.dia]


class Turno_Sala(models.Model):
    turno = models.ForeignKey('Turno')
    sala = models.ForeignKey('Sala')
    estados = (
        (0, 'Activado'),
        (1, 'Desactivado'),
        (2, 'Temporal'),
    )
    estado = models.IntegerField(default=0, choices=estados)
    hasta = models.DateField(null=True, help_text='hasta cuando se desactivara el turno', blank=True)

    def __unicode__(self):
        return 'Turno: '+str(self.turno)+' - Sala: '+str(self.sala)+' - '+['Activado', 'Desactivado', 'Temporal'][self.estado]


class Prestamo(models.Model):
    #carga = models.ForeignKey('Carga')
    '''estos datos se sacan de la carga para ser guardados en el historial de prestamos'''

    carrera = models.ForeignKey('Carrera')
    profesor = models.ForeignKey('Profesor', null=True)
    codigo = models.CharField(max_length=7, null=True)  # codigo de la materia
    nombre = models.CharField(max_length=45, null=True)  # nombre de la materia
    grupo = models.CharField(max_length=1, null=True)

    turno_sala = models.ForeignKey('Turno_Sala')
    date_prestamo = models.DateTimeField(auto_now=True)
    date_turno = models.DateField()
    ip = models.GenericIPAddressField()
    usuario = models.CharField(max_length=50)#nombre del que hizo el prestamo
    estados = (
        (0, 'Activo'),
        (1, 'Entregado'),
        (2, 'Cancelado'),
        (3, 'Anulado'),
    )
    estado = models.IntegerField(default=0, choices=estados)
    tipos = (
        (0, 'Audiovisuales'),
        (1, 'Sustentacion'),
        (2, 'Curso'),
        (3, 'Reunion')
    )
    tipo = models.IntegerField(default=0, choices=estados)
    beca = models.ForeignKey('Beca', null=True)
    #para las sustentaciones, cursos y reuniones
    solicitante = models.CharField(max_length=50, null=True)
    tel = models.CharField(max_length=12, null=True)
    detalle = models.CharField(max_length=50, null=True)

    def __unicode__(self):
        return ['Activo', 'Entregado', 'Cancelado', 'Anulado'][self.estado]+', '+str(self.date_prestamo)+', '+\
               self.usuario+', '+self.ip+', '+str(self.date_turno)+', '+str(self.turno_sala)


class Persona(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tipos = (
        (0, 'Profesor'),
        (1, 'Beca'),
        (2, 'Admin'),
    )
    tipo = models.IntegerField(default=0, choices=tipos)

    def __unicode__(self):
        return self.user.username+[', Prefesor', ', Beca', ', Admin'][self.tipo]


class Profesor(models.Model):
    persona = models.ForeignKey('Persona')
    departamento = models.ForeignKey('Departamento')
    tel = models.CharField(max_length=20, null=True)

    def __unicode__(self):
        return self.persona.user.username + ', '+self.persona.user.first_name


class Beca(models.Model):
    persona = models.ForeignKey('Persona')
    tel = models.CharField(max_length=20)
    nick = models.CharField(max_length=12)
    cc = models.CharField(max_length=10)

    def __unicode__(self):
        return self.persona.user.username+', '+self.persona.user.first_name


class Ip_Registro(models.Model):
    ip = models.GenericIPAddressField(unique=True)
    estados = (
        (True, 'Activar'),
        (False, 'Desactivar'),
    )
    estado = models.BooleanField(default=True, choices=estados)

    def __unicode__(self):
        return self.ip


class Asistencia(models.Model):
    beca_turno = models.ForeignKey('Beca_Turno')
    ip = models.ForeignKey('Ip_Registro', null=True)
    tipos = (
        (0, 'Sin Asistencia'),
        (1, 'Retardo'),
        (2, 'Asistencia exitosa'),
    )
    tipo = models.IntegerField(default=0)
    date_turno = models.DateField()
    datetime_registro = models.DateTimeField(null=True)

    def __unicode__(self):
        return str(self.beca_turno.turno.time_start)+' a '+str(self.beca_turno.turno.time_end)+', '


class Beca_Turno(models.Model):
    beca = models.ForeignKey('Beca')
    turno = models.ForeignKey('Turno')


class Semestre(models.Model):
    nombre = models.CharField(max_length=10)
    date_start = models.DateField()
    date_end = models.DateField()

    def __unicode__(self):
        return self.nombre+' desde:'+str(self.date_start)+' hasta:'+str(self.date_end)


class Sancion(models.Model):
    profesor = models.ForeignKey('Profesor')
    date_start = models.DateField()
    date_end = models.DateField()
    motivo = models.TextField()
    responsable = models.CharField(max_length=40)

    def __unicode__(self):
        return self.profesor+', desde: '+str(self.date_start)+' hasta: '+str(self.date_end)




'''
class Restriccion(models.Model):
    sala = models.ForeignKey('Sala')
    turno = models.IntegerField(null=True)
    dia = models.DateField()
    #estado = grupo = models.CharField(max_length=1)
    #si es 1 bloque el dia y si es 0 bloquea un turno
'''