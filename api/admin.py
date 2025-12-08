from django.contrib import admin
from .models import Rol, Departamento, Usuario, Sensor, Barrera, Evento


@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')
    search_fields = ('nombre',)


@admin.register(Departamento)
class DepartamentoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'ubicacion', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre', 'ubicacion')


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('user', 'rol', 'departamento', 'activo', 'fecha_creacion')
    list_filter = ('rol', 'activo', 'fecha_creacion')
    search_fields = ('user__username', 'user__email')


@admin.register(Sensor)
class SensorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'uid', 'estado', 'departamento', 'usuario')
    list_filter = ('estado', 'departamento', 'fecha_creacion')
    search_fields = ('nombre', 'uid')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')


@admin.register(Barrera)
class BarreraAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'estado', 'departamento', 'fecha_ultimo_cambio')
    list_filter = ('estado', 'departamento')
    search_fields = ('nombre',)
    readonly_fields = ('fecha_ultimo_cambio',)


@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ('sensor', 'tipo', 'barrera', 'usuario_accion', 'fecha_evento')
    list_filter = ('tipo', 'fecha_evento', 'sensor')
    search_fields = ('sensor__nombre', 'sensor__uid', 'tipo')
    readonly_fields = ('fecha_evento',)
    ordering = ('-fecha_evento',)
