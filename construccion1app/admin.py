# construccion1app/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Empresa, Proyecto,Nivel,Espacio,Actividad

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    model = Usuario
    list_display = ('username', 'first_name', 'last_name', 'email', 'tipo_usuario', 'cargo', 'empresa')
    list_filter = ('tipo_usuario', 'cargo', 'empresa')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Información Personal', {'fields': ('first_name', 'last_name', 'email')}),
        ('Datos Laborales', {'fields': ('tipo_usuario', 'cargo', 'empresa')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas Importantes', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'first_name', 'last_name', 'email', 'tipo_usuario', 'cargo', 'empresa', 'password1', 'password2', 'is_active', 'is_staff')
        }),
    )


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'rut', 'razon_social', 'activo', 'administrador_empresa')
    list_filter = ('activo',)
    search_fields = ('nombre', 'rut', 'razon_social')





# admin.py
from django.contrib import admin
from .models import Proyecto, Nivel, Espacio, Actividad


@admin.register(Proyecto)
class ProyectoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "calcular_avance")
    search_fields = ("nombre",)
    list_filter = ()
    ordering = ("nombre",)


@admin.register(Nivel)
class NivelAdmin(admin.ModelAdmin):
    list_display = ("nombre", "proyecto", "incidencia", "calcular_avance_ponderado")
    search_fields = ("nombre",)
    list_filter = ("proyecto",)
    ordering = ("proyecto", "nombre")


@admin.register(Espacio)
class EspacioAdmin(admin.ModelAdmin):
    list_display = ("nombre", "nivel", "incidencia", "calcular_avance_ponderado")
    search_fields = ("nombre",)
    list_filter = ("nivel",)
    ordering = ("nivel", "nombre")


@admin.register(Actividad)
class ActividadAdmin(admin.ModelAdmin):
    list_display = ("nombre", "espacio", "avance", "incidencia", "calcular_avance_ponderado")
    search_fields = ("nombre",)
    list_filter = ("espacio",)
    ordering = ("espacio", "nombre")
