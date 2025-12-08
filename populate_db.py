import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartconnect_backend.settings')
django.setup()

from django.contrib.auth.models import User
from api.models import Rol, Departamento, Usuario, Sensor, Barrera

# Crear roles
print("Creando roles...")
admin_rol, _ = Rol.objects.get_or_create(
    nombre='admin',
    defaults={'descripcion': 'Administrador del sistema'}
)
operador_rol, _ = Rol.objects.get_or_create(
    nombre='operador',
    defaults={'descripcion': 'Operador del sistema'}
)

# Crear usuarios de prueba
print("Creando usuarios...")
admin_user, _ = User.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'admin@smartconnect.com',
        'first_name': 'Admin',
        'last_name': 'Usuario'
    }
)
if admin_user.password == '':
    admin_user.set_password('admin123456')
    admin_user.is_staff = True
    admin_user.is_superuser = True
    admin_user.save()

# Crear perfil admin
Usuario.objects.get_or_create(
    user=admin_user,
    defaults={'rol': admin_rol}
)

# Crear usuario operador
operador_user, _ = User.objects.get_or_create(
    username='operador',
    defaults={
        'email': 'operador@smartconnect.com',
        'first_name': 'Operador',
        'last_name': 'Usuario'
    }
)
if operador_user.password == '':
    operador_user.set_password('operador123456')
    operador_user.save()

# Crear perfil operador
Usuario.objects.get_or_create(
    user=operador_user,
    defaults={'rol': operador_rol}
)

# Crear departamentos
print("Creando departamentos...")
departamento1, _ = Departamento.objects.get_or_create(
    nombre='Entrada Principal',
    defaults={
        'descripcion': 'Puerta principal de acceso',
        'ubicacion': 'Planta baja'
    }
)

departamento2, _ = Departamento.objects.get_or_create(
    nombre='Sala de Servidores',
    defaults={
        'descripcion': 'Área de infraestructura IT',
        'ubicacion': 'Sótano'
    }
)

departamento3, _ = Departamento.objects.get_or_create(
    nombre='Oficinas Ejecutivas',
    defaults={
        'descripcion': 'Área administrativa',
        'ubicacion': 'Piso 3'
    }
)

# Crear sensores
print("Creando sensores...")
Sensor.objects.get_or_create(
    uid='AA:BB:CC:DD:EE:01',
    defaults={
        'nombre': 'Tarjeta Acceso 001',
        'estado': 'activo',
        'departamento': departamento1,
    }
)

Sensor.objects.get_or_create(
    uid='AA:BB:CC:DD:EE:02',
    defaults={
        'nombre': 'Llavero RFID 002',
        'estado': 'activo',
        'departamento': departamento2,
    }
)

Sensor.objects.get_or_create(
    uid='AA:BB:CC:DD:EE:03',
    defaults={
        'nombre': 'Pulsera RFID 003',
        'estado': 'bloqueado',
        'departamento': departamento3,
    }
)

# Crear barreras
print("Creando barreras...")
Barrera.objects.get_or_create(
    nombre='Barrera Entrada Principal',
    defaults={
        'estado': 'cerrada',
        'departamento': departamento1,
    }
)

Barrera.objects.get_or_create(
    nombre='Barrera Sala Servidores',
    defaults={
        'estado': 'cerrada',
        'departamento': departamento2,
    }
)

Barrera.objects.get_or_create(
    nombre='Barrera Oficinas',
    defaults={
        'estado': 'cerrada',
        'departamento': departamento3,
    }
)

print("✓ Base de datos poblada exitosamente!")
print(f"  - Roles: {Rol.objects.count()}")
print(f"  - Usuarios: {Usuario.objects.count()}")
print(f"  - Departamentos: {Departamento.objects.count()}")
print(f"  - Sensores: {Sensor.objects.count()}")
print(f"  - Barreras: {Barrera.objects.count()}")
print("\nCredenciales de prueba:")
print("  Admin: admin / admin123456")
print("  Operador: operador / operador123456")
