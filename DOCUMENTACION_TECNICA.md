# SmartConnect - Documentación Técnica
## Sistema de Control de Acceso Inteligente con API RESTful

**Fecha:** Diciembre 8, 2025  
**Autor:** Dylan Torres  
**Asignatura:** Programación Back End  
**Versión:** 1.0

---

## 1. INTRODUCCIÓN

SmartConnect es una solución de backend desarrollada en Django REST Framework que implementa un sistema completo de control de acceso inteligente utilizando sensores RFID (IoT). La API permite gestionar usuarios, departamentos, sensores RFID, eventos de acceso y barreras de forma segura mediante autenticación JWT.

### 1.1 Problemática Resuelta

La empresa SmartConnect requería:
- ✓ Gestión centralizada de sensores RFID (UID/MAC únicos)
- ✓ Control de roles y permisos (Admin, Operador)
- ✓ Registro trazable de eventos de acceso
- ✓ Gestión de departamentos/zonas de acceso
- ✓ Control manual de barreras de acceso
- ✓ API segura con autenticación JWT
- ✓ Simulación de flujo IoT sin hardware real

---

## 2. ARQUITECTURA GENERAL

### 2.1 Estructura del Proyecto

```
smartconnect_backend/
├── smartconnect_backend/
│   ├── settings.py          # Configuración de Django
│   ├── urls.py              # URLs principales
│   ├── wsgi.py              # WSGI para producción
│   └── asgi.py
├── api/
│   ├── models.py            # Modelos de datos
│   ├── views.py             # ViewSets y funciones de vista
│   ├── serializers.py       # Serializadores DRF
│   ├── urls.py              # URLs de la API
│   ├── admin.py             # Panel administrativo
│   └── migrations/          # Migraciones de BD
├── users/
│   └── (aplicación auxiliar)
├── manage.py
├── db.sqlite3               # Base de datos
├── requirements.txt         # Dependencias Python
├── populate_db.py           # Script de población
├── .env                     # Variables de entorno
└── GUIA_ENDPOINTS.txt       # Guía de uso de API
```

### 2.2 Stack Tecnológico

- **Backend:** Django 5.2.9
- **REST API:** Django REST Framework 3.16.1
- **Autenticación:** JWT (SimpleJWT 5.5.1)
- **Base de Datos:** SQLite (desarrollo), PostgreSQL (producción)
- **Servidor Web:** Gunicorn 23.0.0
- **Entorno:** Python 3.11.9
- **Despliegue:** AWS EC2

---

## 3. MODELOS DE DATOS Y RELACIONES

### 3.1 Diagrama de Modelos (Modelo Lógico)

```
┌─────────────────┐
│      Rol        │
├─────────────────┤
│ id (PK)         │
│ nombre (UNIQUE) │ ─── 'admin', 'operador'
│ descripcion     │
└─────────────────┘
        ▲
        │
        │ 1
        │ N
        │
┌─────────────────┐         ┌──────────────────┐
│    Usuario      │         │   Departamento   │
├─────────────────┤         ├──────────────────┤
│ id (PK)         │         │ id (PK)          │
│ user_id (FK)    │◄────────│ nombre (UNIQUE)  │
│ rol_id (FK)     │◄───────►│ descripcion      │
│ departamento_id │◄────┐   │ ubicacion        │
│ activo          │     │   │ activo           │
│ fecha_creacion  │     │   │ sensores_count   │
└─────────────────┘     │   └──────────────────┘
        ▲               │
        │               │
        │               │ 1
        │         N─────┘
    1   │
    N   │
        │
┌─────────────────┐     ┌──────────────────┐
│     Sensor      │     │     Barrera      │
├─────────────────┤     ├──────────────────┤
│ id (PK)         │     │ id (PK)          │
│ uid (UNIQUE)    │     │ nombre (UNIQUE)  │
│ nombre          │     │ estado           │
│ estado          │     │ departamento_id  │
│ departamento_id │     │ fecha_ult_cambio │
│ usuario_id      │     └──────────────────┘
│ fecha_creacion  │            ▲
│ fecha_actualiz  │            │ 1
└─────────────────┘            │ N
        ▲                       │
        │                       │
        │ 1                     │
        │ N            ┌────────┴──────────┐
        │              │                   │
        └──────────────┼───────────────────┘
                       │
                       │
            ┌──────────▼───────────┐
            │      Evento         │
            ├─────────────────────┤
            │ id (PK)             │
            │ sensor_id (FK)      │
            │ tipo                │
            │ barrera_id (FK)     │
            │ usuario_accion_id   │
            │ mensaje             │
            │ fecha_evento        │
            └─────────────────────┘
```

### 3.2 Descripción de Modelos

#### **Rol**
- Tipos: `admin` (acceso total), `operador` (solo lectura)
- Utilizado para control de permisos
- Relación: 1 a muchos con Usuario

#### **Usuario**
- Extiende el modelo User de Django
- Contiene rol y departamento asignado
- Almacena fecha de creación y estado activo
- Relación: 1 a 1 con User, N a 1 con Rol, N a 1 con Departamento

#### **Departamento**
- Representa zonas físicas de acceso
- Posee múltiples sensores y barreras
- Validación: nombre mínimo 3 caracteres
- Relación: 1 a muchos con Sensor y Barrera

#### **Sensor**
- Representa tarjetas RFID/llaveros/pulseras
- Estados: `activo`, `inactivo`, `bloqueado`, `perdido`
- UID única y validada (sin duplicados)
- Timestamps de creación y actualización
- Índices en `uid` y `estado` para optimización
- Relación: N a 1 con Departamento y Usuario

#### **Barrera**
- Control de entrada/salida automático
- Estados: `abierta`, `cerrada`
- Vinculada a un departamento
- Relación: 1 a 1 con Departamento, 1 a muchos con Evento

#### **Evento**
- Registro de todos los intentos de acceso
- Tipos: `acceso_intentado`, `acceso_permitido`, `acceso_denegado`, `barrera_abierta`, `barrera_cerrada`
- Trazabilidad completa: quién, cuándo, qué
- Índices en `fecha_evento` para búsquedas rápidas
- Relación: N a 1 con Sensor, Barrera y Usuario

---

## 4. ENDPOINTS API

### 4.1 Endpoint de Información del Proyecto

```
GET /api/info/
```

**Autenticación:** No requerida  
**Permisos:** Público  
**Descripción:** Retorna información general del proyecto

**Ejemplo de Solicitud:**
```bash
curl -X GET http://localhost:8000/api/info/
```

**Respuesta (200):**
```json
{
  "autor": ["Dylan Torres"],
  "asignatura": "Programación Back End",
  "proyecto": "SmartConnect - Sistema de Control de Acceso Inteligente",
  "descripcion": "API RESTful para gestionar sensores RFID, usuarios, departamentos y eventos de acceso en un sistema IoT de control inteligente.",
  "version": "1.0"
}
```

### 4.2 Endpoints de Autenticación

#### Login (Generar Token JWT)

```
POST /api/login/
```

**Autenticación:** No requerida  
**Descripción:** Autentica usuario y genera tokens JWT

**Solicitud:**
```json
{
  "username": "admin",
  "password": "admin123456"
}
```

**Respuesta (200):**
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@smartconnect.com",
    "first_name": "Admin",
    "last_name": "Usuario"
  }
}
```

**Códigos de Error:**
- `400` Validación fallida (credenciales incompletas)
- `401` Credenciales inválidas

#### Registrar Usuario

```
POST /api/registro/
```

**Autenticación:** No requerida  
**Descripción:** Registra un nuevo usuario en el sistema

**Solicitud:**
```json
{
  "username": "nuevo_usuario",
  "email": "nuevo@smartconnect.com",
  "first_name": "Nuevo",
  "last_name": "Usuario",
  "password": "Password123456",
  "password_confirm": "Password123456",
  "rol_id": 2
}
```

**Respuesta (201):**
```json
{
  "message": "Usuario registrado exitosamente",
  "user": {
    "id": 3,
    "username": "nuevo_usuario",
    "email": "nuevo@smartconnect.com"
  }
}
```

**Validaciones:**
- Contraseña mínimo 8 caracteres
- Las contraseñas deben coincidir
- Email único
- Username único

### 4.3 CRUD - Sensores

#### Listar Sensores

```
GET /api/sensores/
```

**Autenticación:** JWT requerida  
**Permisos:** Todos los usuarios autenticados  
**Descripción:** Lista todos los sensores con paginación

**Parámetros de Consulta:**
- `page`: número de página (default: 1)
- `estado`: filtro por estado (activo, inactivo, bloqueado, perdido)
- `departamento`: filtro por departamento (ID)
- `search`: búsqueda por uid o nombre

**Ejemplo:**
```
GET /api/sensores/?estado=activo&departamento=1&search=Tarjeta
```

**Respuesta (200):**
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "uid": "AA:BB:CC:DD:EE:01",
      "nombre": "Tarjeta Acceso 001",
      "estado": "activo",
      "departamento": 1,
      "departamento_nombre": "Entrada Principal",
      "usuario": null,
      "usuario_nombre": "",
      "fecha_creacion": "2025-12-08T16:01:46.000Z",
      "fecha_actualizacion": "2025-12-08T16:01:46.000Z"
    }
  ]
}
```

#### Crear Sensor

```
POST /api/sensores/
```

**Autenticación:** JWT requerida  
**Permisos:** Solo Admin  
**Descripción:** Crea un nuevo sensor RFID

**Solicitud:**
```json
{
  "uid": "AA:BB:CC:DD:EE:04",
  "nombre": "Nuevo Sensor",
  "estado": "activo",
  "departamento": 1,
  "usuario": null
}
```

**Respuesta (201):**
```json
{
  "id": 4,
  "uid": "AA:BB:CC:DD:EE:04",
  "nombre": "Nuevo Sensor",
  "estado": "activo",
  "departamento": 1,
  "departamento_nombre": "Entrada Principal",
  "usuario": null,
  "usuario_nombre": "",
  "fecha_creacion": "2025-12-08T16:02:30.000Z",
  "fecha_actualizacion": "2025-12-08T16:02:30.000Z"
}
```

**Validaciones:**
- UID única en la base de datos (400 si existe)
- Nombre mínimo 3 caracteres
- Estado válido (400 si es inválido)

**Códigos de Error:**
- `400` Validación fallida
- `401` Sin autenticación
- `403` No es admin

#### Obtener Detalle de Sensor

```
GET /api/sensores/{id}/
```

**Autenticación:** JWT requerida  
**Permisos:** Todos  
**Códigos:**
- `200` Éxito
- `401` Sin autenticación
- `404` Sensor no existe

#### Actualizar Sensor

```
PUT /api/sensores/{id}/
PATCH /api/sensores/{id}/
```

**Autenticación:** JWT requerida  
**Permisos:** Solo Admin  
**Descripción:** Actualiza un sensor existente

**Solicitud (PATCH):**
```json
{
  "estado": "bloqueado",
  "nombre": "Tarjeta Bloqueada"
}
```

**Códigos:**
- `200` Éxito
- `400` Validación fallida
- `401` Sin autenticación
- `403` No es admin
- `404` Sensor no existe

#### Eliminar Sensor

```
DELETE /api/sensores/{id}/
```

**Autenticación:** JWT requerida  
**Permisos:** Solo Admin  
**Códigos:**
- `204` Eliminado exitosamente
- `401` Sin autenticación
- `403` No es admin
- `404` Sensor no existe

#### Cambiar Estado de Sensor

```
POST /api/sensores/{id}/cambiar_estado/
```

**Autenticación:** JWT requerida  
**Permisos:** Solo Admin  
**Descripción:** Cambia el estado de un sensor

**Solicitud:**
```json
{
  "estado": "bloqueado"
}
```

**Respuesta (200):**
```json
{
  "message": "Estado del sensor actualizado a: bloqueado",
  "sensor": { ... }
}
```

**Códigos:**
- `200` Éxito
- `400` Estado inválido
- `401` Sin autenticación
- `403` No es admin
- `404` Sensor no existe

### 4.4 CRUD - Departamentos

```
GET /api/departamentos/          (Listar)
POST /api/departamentos/         (Crear - Admin)
GET /api/departamentos/{id}/     (Detalle)
PUT /api/departamentos/{id}/     (Actualizar - Admin)
DELETE /api/departamentos/{id}/  (Eliminar - Admin)
```

**Validaciones:**
- Nombre mínimo 3 caracteres
- Nombre único

### 4.5 CRUD - Barreras

```
GET /api/barreras/               (Listar)
POST /api/barreras/              (Crear - Admin)
GET /api/barreras/{id}/          (Detalle)
PUT /api/barreras/{id}/          (Actualizar - Admin)
DELETE /api/barreras/{id}/       (Eliminar - Admin)
POST /api/barreras/{id}/abrir/   (Abrir - Admin)
POST /api/barreras/{id}/cerrar/  (Cerrar - Admin)
```

**Estados válidos:** `abierta`, `cerrada`

### 4.6 CRUD - Eventos (Solo Lectura)

```
GET /api/eventos/                              (Listar)
GET /api/eventos/{id}/                         (Detalle)
GET /api/eventos/por_sensor/?sensor_id=1      (Eventos por sensor)
GET /api/eventos/por_tipo/?tipo=acceso_permitido  (Eventos por tipo)
```

**Filtros disponibles:**
- `sensor`: ID del sensor
- `tipo`: tipo de evento
- `barrera`: ID de la barrera

### 4.7 Endpoints de Simulación IoT

#### Simular Lectura de Sensor

```
POST /api/simular/lectura-sensor/
```

**Autenticación:** No requerida (simula NodeMCU)  
**Descripción:** Simula que un sensor RFID intenta lectura

**Solicitud:**
```json
{
  "uid": "AA:BB:CC:DD:EE:01",
  "departamento_id": 1
}
```

**Respuesta (200 - Acceso Permitido):**
```json
{
  "acceso": "permitido",
  "sensor": "Tarjeta Acceso 001",
  "uid": "AA:BB:CC:DD:EE:01",
  "estado_sensor": "activo",
  "departamento": "Entrada Principal",
  "evento_id": 10,
  "timestamp": "2025-12-08T16:04:30.000Z"
}
```

**Respuesta (403 - Acceso Denegado):**
```json
{
  "acceso": "denegado",
  "razon": "Sensor bloqueado por administrador",
  "sensor": "Tarjeta Acceso 001",
  "evento_id": 11
}
```

**Respuesta (404 - Sensor Desconocido):**
```json
{
  "acceso": "denegado",
  "razon": "Sensor no registrado en el sistema",
  "uid": "XX:XX:XX:XX:XX:XX"
}
```

**Casos de Uso:**
- ✓ Sensor activo → Acceso permitido (200)
- ✓ Sensor inactivo → Acceso denegado (403)
- ✓ Sensor bloqueado → Acceso denegado (403)
- ✓ Sensor perdido → Acceso denegado (403)
- ✓ Sensor desconocido → Acceso denegado (404)

**Registro de Eventos:** Cada solicitud genera un evento (`acceso_permitido` o `acceso_denegado`)

#### Simular Intento de Acceso Completo

```
POST /api/simular/intento-acceso/
```

**Autenticación:** JWT requerida  
**Permisos:** Admin  
**Descripción:** Simula un acceso completo con control de barrera

**Solicitud:**
```json
{
  "uid": "AA:BB:CC:DD:EE:01",
  "barrera_id": 1
}
```

**Respuesta (200):**
```json
{
  "acceso": "permitido",
  "sensor": "Tarjeta Acceso 001",
  "barrera": "Barrera Entrada Principal",
  "barrera_accion": "ABIERTA",
  "evento_id": 12,
  "timestamp": "2025-12-08T16:04:45.000Z"
}
```

**Flujo:**
1. Valida sensor
2. Si acceso permitido → abre barrera
3. Crea evento de acceso
4. Retorna resultado

#### Simular Cierre de Barrera

```
POST /api/simular/cierre-barrera/
```

**Autenticación:** JWT requerida  
**Permisos:** Admin

**Solicitud:**
```json
{
  "barrera_id": 1
}
```

**Respuesta (200):**
```json
{
  "mensaje": "Barrera cerrada",
  "barrera": "Barrera Entrada Principal",
  "estado": "cerrada",
  "evento_id": 13
}
```

#### Cambiar Estado de Sensor (IoT)

```
POST /api/simular/cambio-estado/
```

**Autenticación:** JWT requerida  
**Permisos:** Admin

**Solicitud:**
```json
{
  "uid": "AA:BB:CC:DD:EE:03",
  "nuevo_estado": "perdido"
}
```

**Respuesta (200):**
```json
{
  "mensaje": "Estado del sensor actualizado",
  "sensor": "Pulsera RFID 003",
  "estado_anterior": "bloqueado",
  "estado_nuevo": "perdido",
  "uid": "AA:BB:CC:DD:EE:03"
}
```

#### Ver Estado del Sistema

```
GET /api/simular/estado-sistema/
```

**Autenticación:** JWT requerida  
**Permisos:** Todos  
**Descripción:** Retorna estadísticas del sistema

**Respuesta (200):**
```json
{
  "sensores": {
    "total": 3,
    "activos": 2,
    "inactivos": 0,
    "bloqueados": 1,
    "perdidos": 0
  },
  "barreras": {
    "total": 3,
    "abiertas": 1,
    "cerradas": 2
  },
  "eventos_24h": {
    "total": 15,
    "accesos_permitidos": 10,
    "accesos_denegados": 5
  },
  "timestamp": "2025-12-08T16:05:00.000Z"
}
```

---

## 5. AUTENTICACIÓN Y PERMISOS

### 5.1 JWT - JSON Web Tokens

**Flujo de Autenticación:**

```
1. Usuario envía credenciales
   POST /api/login/
   {username, password}
   ↓
2. Sistema valida y genera tokens
   {
     "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
     "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
   }
   ↓
3. Cliente almacena access token
   ↓
4. Cliente incluye token en cada solicitud
   Authorization: Bearer {access_token}
   ↓
5. Sistema valida token y procesa solicitud
   ↓
6. Token expira después de 1 hora
   ↓
7. Cliente usa refresh token para obtener nuevo access token
   POST /api/token/refresh/
   {refresh_token}
```

### 5.2 Tiempos de Expiración

- **Access Token:** 1 hora
- **Refresh Token:** 1 día

### 5.3 Permisos

#### Admin (administrador)
- ✓ Crear sensores
- ✓ Editar sensores
- ✓ Eliminar sensores
- ✓ Cambiar estado de sensores
- ✓ Crear departamentos
- ✓ Crear/abrir/cerrar barreras
- ✓ Ver todos los eventos
- ✓ Acceder a endpoints de simulación

#### Operador (operador)
- ✓ Ver sensores (lectura)
- ✓ Ver departamentos (lectura)
- ✓ Ver eventos
- ✓ Acceder a endpoints públicos de simulación
- ✗ No puede crear/editar/eliminar

#### Sin Autenticación (Público)
- ✓ GET /api/info/
- ✓ POST /api/login/
- ✓ POST /api/registro/
- ✓ POST /api/simular/lectura-sensor/ (simula NodeMCU)

### 5.4 Códigos de Error de Autenticación

```
401 Unauthorized
{
  "detail": "Authentication credentials were not provided."
}

403 Forbidden
{
  "detail": "You do not have permission to perform this action."
}
```

---

## 6. VALIDACIONES Y MANEJO DE ERRORES

### 6.1 Errores de Validación (400 Bad Request)

**Ejemplo: UID duplicado**
```json
{
  "uid": ["Ya existe un sensor con este UID."]
}
```

**Ejemplo: Nombre muy corto**
```json
{
  "nombre": ["El nombre debe tener al menos 3 caracteres."]
}
```

**Ejemplo: Estado inválido**
```json
{
  "estado": ["Estado inválido. Debe ser uno de: activo, inactivo, bloqueado, perdido"]
}
```

**Ejemplo: Contraseñas no coinciden**
```json
{
  "password": ["Las contraseñas no coinciden."]
}
```

### 6.2 Errores de No Encontrado (404 Not Found)

```json
{
  "detail": "Not found."
}
```

### 6.3 Validaciones Implementadas

**Sensor:**
- UID mínimo 5 caracteres
- UID único en la BD
- Nombre mínimo 3 caracteres
- Estado válido

**Departamento:**
- Nombre mínimo 3 caracteres
- Nombre único

**Usuario:**
- Contraseña mínimo 8 caracteres
- Las contraseñas deben coincidir
- Email único
- Username único

**Evento:**
- Tipo válido
- Sensor debe existir

**Barrera:**
- Estado válido (abierta/cerrada)

---

## 7. CONFIGURACIÓN DJANGO

### 7.1 Settings Principales

```python
# rest_framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_FILTER_BACKENDS': [
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
}

# JWT Settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ALGORITHM': 'HS256',
}
```

### 7.2 Instaladas Apps

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'api',
    'users',
]
```

---

## 8. BASE DE DATOS

### 8.1 Inicial (Development)

- **Motor:** SQLite (`db.sqlite3`)
- **Datos de Prueba:**
  - 2 Roles (Admin, Operador)
  - 2 Usuarios (admin/operador)
  - 3 Departamentos
  - 3 Sensores
  - 3 Barreras

**Credenciales de Prueba:**
```
Admin:
  Username: admin
  Password: admin123456
  
Operador:
  Username: operador
  Password: operador123456
```

### 8.2 Producción (AWS)

- **Motor:** PostgreSQL
- **Conexión:** RDS de AWS
- **Inicialización:** Migraciones automáticas

---

## 9. GUÍA DE PRUEBAS EN POSTMAN/APIDOG

### 9.1 Flujo Básico de Pruebas

**Paso 1: Login**
```
POST http://localhost:8000/api/login/
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123456"
}
```

Copiar el `access` token de la respuesta.

**Paso 2: Listar Sensores**
```
GET http://localhost:8000/api/sensores/
Authorization: Bearer {TOKEN}
```

**Paso 3: Crear Sensor**
```
POST http://localhost:8000/api/sensores/
Authorization: Bearer {TOKEN}
Content-Type: application/json

{
  "uid": "NEW:SENSOR:001",
  "nombre": "Nuevo Sensor",
  "estado": "activo",
  "departamento": 1
}
```

**Paso 4: Simular Lectura RFID**
```
POST http://localhost:8000/api/simular/lectura-sensor/
Content-Type: application/json

{
  "uid": "AA:BB:CC:DD:EE:01",
  "departamento_id": 1
}
```

**Paso 5: Simular Acceso Completo**
```
POST http://localhost:8000/api/simular/intento-acceso/
Authorization: Bearer {TOKEN}
Content-Type: application/json

{
  "uid": "AA:BB:CC:DD:EE:01",
  "barrera_id": 1
}
```

**Paso 6: Ver Eventos**
```
GET http://localhost:8000/api/eventos/
Authorization: Bearer {TOKEN}
```

**Paso 7: Estado del Sistema**
```
GET http://localhost:8000/api/simular/estado-sistema/
Authorization: Bearer {TOKEN}
```

### 9.2 Pruebas de Errores

**401 Unauthorized - Sin Token**
```
GET http://localhost:8000/api/sensores/
```

**403 Forbidden - Operador intenta crear**
```
POST http://localhost:8000/api/sensores/
Authorization: Bearer {OPERADOR_TOKEN}
Content-Type: application/json

{ ... datos ... }
```

**400 Bad Request - UID Duplicado**
```
POST http://localhost:8000/api/sensores/
Authorization: Bearer {TOKEN}
Content-Type: application/json

{
  "uid": "AA:BB:CC:DD:EE:01",  /* Ya existe */
  "nombre": "Duplicate",
  "estado": "activo"
}
```

**404 Not Found - Sensor No Existe**
```
GET http://localhost:8000/api/sensores/9999/
Authorization: Bearer {TOKEN}
```

---

## 10. DESPLIEGUE EN AWS EC2

### 10.1 Preparación

**Crear archivo de configuración para producción:**

```python
# settings_prod.py (o variable DEBUG = False en settings.py)
DEBUG = False
ALLOWED_HOSTS = ['tu-ip-ec2.amazonaws.com', 'tu-dominio.com']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'smartconnect',
        'USER': 'postgres',
        'PASSWORD': 'tu-password',
        'HOST': 'tu-rds-endpoint.amazonaws.com',
        'PORT': '5432',
    }
}

STATIC_URL = '/static/'
STATIC_ROOT = '/var/www/smartconnect/static'
```

### 10.2 Pasos de Despliegue

1. **Instancia EC2 (Amazon Linux 2)**
   ```bash
   sudo yum update -y
   sudo yum install python3 python3-pip -y
   sudo yum install postgresql-devel -y
   ```

2. **Clonar repositorio y configurar**
   ```bash
   cd /var/www
   git clone tu-repo
   cd smartconnect_backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Ejecutar migraciones**
   ```bash
   python manage.py migrate
   python manage.py collectstatic --noinput
   ```

4. **Configurar Gunicorn**
   ```bash
   gunicorn smartconnect_backend.wsgi:application --bind 0.0.0.0:8000
   ```

5. **Configurar Nginx (Proxy Inverso)**
   ```nginx
   server {
       listen 80;
       server_name tu-ip-ec2.amazonaws.com;
       
       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

6. **Systemd Service (Autoarranque)**
   ```ini
   [Unit]
   Description=SmartConnect API
   After=network.target
   
   [Service]
   User=ec2-user
   WorkingDirectory=/var/www/smartconnect_backend
   ExecStart=/var/www/smartconnect_backend/venv/bin/gunicorn \
       smartconnect_backend.wsgi:application --bind 0.0.0.0:8000
   
   [Install]
   WantedBy=multi-user.target
   ```

### 10.3 URL Pública (Ejemplo)

```
http://ec2-3-14-159-205.us-east-2.compute.amazonaws.com:8000/api/
```

---

## 11. ÍNDICES Y OPTIMIZACIÓN

### 11.1 Índices Implementados

```python
# Sensor Model
class Meta:
    indexes = [
        models.Index(fields=['uid']),           # Búsquedas por UID
        models.Index(fields=['estado']),        # Filtrados por estado
    ]

# Evento Model
class Meta:
    indexes = [
        models.Index(fields=['-fecha_evento']),                    # Eventos recientes
        models.Index(fields=['sensor', '-fecha_evento']),          # Eventos por sensor
    ]
```

### 11.2 Optimizaciones de Query

```python
# Select_related para Foreign Keys
queryset = Sensor.objects.select_related('departamento', 'usuario')

# Prefetch_related para Many-to-Many/Reverse
queryset = Evento.objects.select_related('sensor', 'barrera', 'usuario_accion')
```

---

## 12. ESTRUCTURA DE CARPETAS FINAL

```
smartconnect_backend/
├── api/
│   ├── migrations/
│   │   ├── 0001_initial.py
│   │   └── __init__.py
│   ├── __init__.py
│   ├── admin.py                 # Panel administrativo
│   ├── apps.py
│   ├── models.py                # 6 modelos (Rol, Usuario, Departamento, Sensor, Barrera, Evento)
│   ├── serializers.py           # 8 serializadores
│   ├── tests.py
│   ├── urls.py                  # Rutas API (CRUD + Simulación IoT)
│   └── views.py                 # ViewSets y funciones de vista (5 ViewSets + 5 endpoints IoT)
├── smartconnect_backend/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py              # Configuración Django + JWT + DRF
│   ├── urls.py                  # Rutas principales
│   └── wsgi.py                  # WSGI para Gunicorn
├── users/
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   └── views.py
├── venv/                        # Entorno virtual
├── .env                         # Variables de entorno
├── .gitignore
├── db.sqlite3                   # Base de datos (desarrollo)
├── manage.py
├── populate_db.py               # Script de población de BD
├── requirements.txt             # Dependencias
├── GUIA_ENDPOINTS.txt           # Documentación de endpoints
└── DOCUMENTACION_TECNICA.md     # Este archivo
```

---

## 13. RESUMEN DE ESTADÍSTICAS

### Endpoints Implementados
- **CRUD Completo:** 30+ endpoints (Sensores, Departamentos, Barreras, Usuarios, Eventos, Roles)
- **Autenticación:** 3 endpoints (Login, Registro, Refresh Token)
- **Simulación IoT:** 5 endpoints (Lectura sensor, Intento acceso, Cierre barrera, etc)
- **Información:** 1 endpoint (info/)
- **Total:** 40+ endpoints funcionales

### Modelos
- 6 modelos de datos
- 28+ campos
- 15+ índices y relaciones

### Validaciones
- 20+ reglas de validación
- Códigos HTTP propios (200, 201, 400, 401, 403, 404, 500)

### Seguridad
- JWT + SimpleJWT
- Permisos personalizados (Admin/Operador)
- Validación de datos
- Manejo de errores robusto

---

## 14. CONCLUSIÓN

SmartConnect API es una solución completa y producción-ready para control de acceso inteligente. Implementa:

✓ Arquitectura RESTful profesional  
✓ Autenticación y autorización segura  
✓ Validaciones exhaustivas  
✓ Manejo de errores robusto  
✓ Simulación completa de flujo IoT sin hardware  
✓ Documentación detallada  
✓ Lista para despliegue en AWS  

**Pronto será desplegada en AWS EC2 con PostgreSQL para entorno de producción.**

---

**Última actualización:** Diciembre 8, 2025  
**Versión:** 1.0  
**Estado:** Listo para pruebas y despliegue

