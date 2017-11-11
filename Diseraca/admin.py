from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

# Register your models here.

from Diseraca.models import Departamento, Carrera, Edificio, Turno, Sala, Turno_Sala, Profesor, Prestamo, Carga\
    , Persona, Beca, Ip_Registro, Semestre
# Register your models here.

admin.site.register(Departamento)
admin.site.register(Carrera)
admin.site.register(Edificio)
admin.site.register(Turno)
admin.site.register(Sala)
admin.site.register(Turno_Sala)
admin.site.register(Profesor)
admin.site.register(Prestamo)
admin.site.register(Carga)
admin.site.register(Beca)
admin.site.register(Persona)
admin.site.register(Ip_Registro)
admin.site.register(Semestre)


class PersonaInline(admin.StackedInline):
    model = Persona
    can_delete = False
    verbose_name_plural = 'Personas'


class UserAdmin(BaseUserAdmin):
    inlines = (PersonaInline, )


admin.site.unregister(User)
admin.site.register(User, UserAdmin)

