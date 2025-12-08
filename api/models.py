from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator

class Rol(models.Model):
    """Roles de usuario en el sistema"""
    ROLE_CHOICES = [
        ('admin', 'Administrador'),
        ('operador', 'Operador'),
    ]
    
    nombre = models.CharField(max_length=50, choices=ROLE_CHOICES, unique=True)
    descripcion = models.TextField(blank=True)
    
    def __str__(self):
        return self.get_nombre_display()
    
    class Meta:
        verbose_name = "Rol"
        verbose_name_plural = "Roles"


class Departamento(models.Model):
    """Departamentos o zonas del sistema de acceso"""
    nombre = models.CharField(
        max_length=100,
        validators=[MinLengthValidator(3)],
        unique=True
    )
    descripcion = models.TextField(blank=True)
    ubicacion = models.CharField(max_length=200, blank=True)
    activo = models.BooleanField(default=True)
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = "Departamento"
        verbose_name_plural = "Departamentos"
        ordering = ['nombre']


class Usuario(models.Model):
    """Extensión del modelo User de Django"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    rol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True)
    departamento = models.ForeignKey(Departamento, on_delete=models.SET_NULL, null=True, blank=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.rol.get_nombre_display() if self.rol else 'Sin Rol'}"
    
    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering = ['-fecha_creacion']


class Sensor(models.Model):
    """Sensores RFID del sistema"""
    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
        ('bloqueado', 'Bloqueado'),
        ('perdido', 'Perdido'),
    ]
    
    uid = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="UID/MAC",
        help_text="Identificador único del sensor RFID"
    )
    nombre = models.CharField(
        max_length=100,
        validators=[MinLengthValidator(3)]
    )
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='activo')
    departamento = models.ForeignKey(
        Departamento,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sensores'
    )
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sensores'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.nombre} ({self.uid})"
    
    class Meta:
        verbose_name = "Sensor"
        verbose_name_plural = "Sensores"
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['uid']),
            models.Index(fields=['estado']),
        ]


class Barrera(models.Model):
    """Control de barrera de acceso"""
    ESTADO_CHOICES = [
        ('abierta', 'Abierta'),
        ('cerrada', 'Cerrada'),
    ]
    
    nombre = models.CharField(max_length=100, unique=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='cerrada')
    departamento = models.OneToOneField(
        Departamento,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='barrera'
    )
    fecha_ultimo_cambio = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.nombre} - {self.get_estado_display()}"
    
    class Meta:
        verbose_name = "Barrera"
        verbose_name_plural = "Barreras"


class Evento(models.Model):
    """Eventos de acceso del sistema"""
    TIPO_EVENTO_CHOICES = [
        ('acceso_intentado', 'Acceso Intentado'),
        ('acceso_permitido', 'Acceso Permitido'),
        ('acceso_denegado', 'Acceso Denegado'),
        ('barrera_abierta', 'Barrera Abierta Manual'),
        ('barrera_cerrada', 'Barrera Cerrada Manual'),
    ]
    
    sensor = models.ForeignKey(
        Sensor,
        on_delete=models.CASCADE,
        related_name='eventos'
    )
    tipo = models.CharField(max_length=30, choices=TIPO_EVENTO_CHOICES)
    barrera = models.ForeignKey(
        Barrera,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='eventos'
    )
    usuario_accion = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='eventos_generados'
    )
    mensaje = models.TextField(blank=True)
    fecha_evento = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.sensor.nombre} - {self.get_tipo_display()} ({self.fecha_evento})"
    
    class Meta:
        verbose_name = "Evento"
        verbose_name_plural = "Eventos"
        ordering = ['-fecha_evento']
        indexes = [
            models.Index(fields=['-fecha_evento']),
            models.Index(fields=['sensor', '-fecha_evento']),
        ]
