# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Asistencia',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tipo', models.IntegerField(default=0)),
                ('date_turno', models.DateField()),
                ('datetime_registro', models.DateTimeField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Beca',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tel', models.CharField(max_length=20)),
                ('nick', models.CharField(max_length=12)),
                ('cc', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Beca_Turno',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('beca', models.ForeignKey(to='Diseraca.Beca')),
            ],
        ),
        migrations.CreateModel(
            name='Carga',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('codigo', models.CharField(max_length=7)),
                ('nombre', models.CharField(max_length=45)),
                ('grupo', models.CharField(max_length=1)),
                ('matriculados', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Carrera',
            fields=[
                ('codigo', models.CharField(max_length=3, serialize=False, primary_key=True)),
                ('nombre', models.CharField(max_length=70)),
            ],
        ),
        migrations.CreateModel(
            name='Departamento',
            fields=[
                ('codigo', models.IntegerField(serialize=False, primary_key=True)),
                ('nombre', models.CharField(max_length=70)),
            ],
        ),
        migrations.CreateModel(
            name='Edificio',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombre', models.CharField(max_length=25)),
                ('codigo', models.CharField(unique=True, max_length=5)),
            ],
        ),
        migrations.CreateModel(
            name='Ip_Registro',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ip', models.GenericIPAddressField(unique=True)),
                ('estado', models.BooleanField(default=True, choices=[(True, b'Activar'), (False, b'Desactivar')])),
            ],
        ),
        migrations.CreateModel(
            name='Persona',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tipo', models.IntegerField(default=0, choices=[(0, b'Profesor'), (1, b'Beca'), (2, b'Admin')])),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Prestamo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('codigo', models.CharField(max_length=7, null=True)),
                ('nombre', models.CharField(max_length=45, null=True)),
                ('grupo', models.CharField(max_length=1, null=True)),
                ('date_prestamo', models.DateTimeField(auto_now=True)),
                ('date_turno', models.DateField()),
                ('ip', models.GenericIPAddressField()),
                ('usuario', models.CharField(max_length=50)),
                ('estado', models.IntegerField(default=0, choices=[(0, b'Activo'), (1, b'Entregado'), (2, b'Cancelado'), (3, b'Anulado')])),
                ('tipo', models.IntegerField(default=0, choices=[(0, b'Activo'), (1, b'Entregado'), (2, b'Cancelado'), (3, b'Anulado')])),
                ('solicitante', models.CharField(max_length=50, null=True)),
                ('tel', models.CharField(max_length=12, null=True)),
                ('detalle', models.CharField(max_length=50, null=True)),
                ('beca', models.ForeignKey(to='Diseraca.Beca', null=True)),
                ('carrera', models.ForeignKey(to='Diseraca.Carrera')),
            ],
        ),
        migrations.CreateModel(
            name='Profesor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tel', models.CharField(max_length=20)),
                ('categoria', models.CharField(max_length=2)),
                ('departamento', models.ForeignKey(to='Diseraca.Departamento')),
                ('persona', models.ForeignKey(to='Diseraca.Persona')),
            ],
        ),
        migrations.CreateModel(
            name='Sala',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('codigo', models.CharField(max_length=10)),
                ('capacidad', models.IntegerField()),
                ('tipo', models.IntegerField(default=0, choices=[(0, b'Sala de clase'), (1, b'Aula virtual'), (2, b'Auditorio')])),
                ('estado', models.IntegerField(default=0, choices=[(0, b'Activo'), (1, b'Mantenimiento'), (2, b'Fuera de servicio')])),
                ('edificio', models.ForeignKey(to='Diseraca.Edificio')),
            ],
        ),
        migrations.CreateModel(
            name='Sancion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_start', models.DateField()),
                ('date_end', models.DateField()),
                ('motivo', models.TextField()),
                ('responsable', models.CharField(max_length=40)),
                ('profesor', models.ForeignKey(to='Diseraca.Profesor')),
            ],
        ),
        migrations.CreateModel(
            name='Semestre',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombre', models.CharField(max_length=10)),
                ('date_start', models.DateField()),
                ('date_end', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='Turno',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time_start', models.TimeField()),
                ('time_end', models.TimeField()),
                ('dia', models.IntegerField(choices=[(0, b'Lunes'), (1, b'Martes'), (2, b'Miercoles'), (3, b'Jueves'), (4, b'Viernes'), (5, b'Sabado')])),
                ('estado', models.IntegerField(default=0, help_text=b'activo --> 0, desactivado --> 1', choices=[(0, b'Activado'), (1, b'Desactivado')])),
            ],
        ),
        migrations.CreateModel(
            name='Turno_Sala',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('estado', models.IntegerField(default=0, choices=[(0, b'Activado'), (1, b'Desactivado'), (2, b'Temporal')])),
                ('hasta', models.DateField(help_text=b'hasta cuando se desactivara el turno', null=True, blank=True)),
                ('sala', models.ForeignKey(to='Diseraca.Sala')),
                ('turno', models.ForeignKey(to='Diseraca.Turno')),
            ],
        ),
        migrations.AddField(
            model_name='prestamo',
            name='profesor',
            field=models.ForeignKey(to='Diseraca.Profesor', null=True),
        ),
        migrations.AddField(
            model_name='prestamo',
            name='turno_sala',
            field=models.ForeignKey(to='Diseraca.Turno_Sala'),
        ),
        migrations.AddField(
            model_name='carrera',
            name='departamento',
            field=models.ForeignKey(to='Diseraca.Departamento'),
        ),
        migrations.AddField(
            model_name='carga',
            name='carrera',
            field=models.ForeignKey(to='Diseraca.Carrera'),
        ),
        migrations.AddField(
            model_name='carga',
            name='profesor',
            field=models.ForeignKey(to='Diseraca.Profesor'),
        ),
        migrations.AddField(
            model_name='beca_turno',
            name='turno',
            field=models.ForeignKey(to='Diseraca.Turno'),
        ),
        migrations.AddField(
            model_name='beca',
            name='persona',
            field=models.ForeignKey(to='Diseraca.Persona'),
        ),
        migrations.AddField(
            model_name='asistencia',
            name='beca_turno',
            field=models.ForeignKey(to='Diseraca.Beca_Turno'),
        ),
        migrations.AddField(
            model_name='asistencia',
            name='ip',
            field=models.ForeignKey(to='Diseraca.Ip_Registro', null=True),
        ),
    ]
