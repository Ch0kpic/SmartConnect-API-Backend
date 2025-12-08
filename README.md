# SmartConnect - Sistema de Control de Acceso Inteligente

## 📋 Descripción

**SmartConnect** es una API RESTful completa desarrollada en Django REST Framework que implementa un sistema de control de acceso inteligente para empresas modernas. Gestiona sensores RFID, usuarios, departamentos, barreras de acceso y eventos, todo integrado con autenticación JWT segura.

### 🎯 Características Principales

- ✅ **Autenticación JWT** - Tokens seguros y renovables
- ✅ **Control de Acceso** - Gestión de sensores RFID y barreras
- ✅ **Roles y Permisos** - Admin y Operador
- ✅ **Registro de Eventos** - Trazabilidad completa
- ✅ **Simulación IoT** - Flujo completo sin hardware real
- ✅ **Validaciones** - Reglas de negocio robustas
- ✅ **API REST Profesional** - Códigos HTTP apropiados
- ✅ **Documentación Completa** - Guías y ejemplos
- ✅ **Lista para Producción** - Optimizaciones y seguridad

---

## 🚀 Quick Start

### Requisitos Previos

- Python 3.11+
- pip
- Git

### 1. Clonar el Repositorio

```bash
git clone <tu-repositorio>
cd EVA4\ Backend
```

### 2. Crear Entorno Virtual

```bash
# Windows
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Ejecutar Migraciones

```bash
python manage.py migrate
```

### 5. Poblar Base de Datos (Opcional)

```bash
python populate_db.py
```

Esto creará:
- 2 roles (Admin, Operador)
- 2 usuarios de prueba
- 3 departamentos
- 3 sensores
- 3 barreras

**Credenciales:**
```
Admin:
  username: admin
  password: admin123456
  
Operador:
  username: operador
  password: operador123456
```

### 6. Iniciar Servidor

```bash
python manage.py runserver 0.0.0.0:8000
```

El servidor estará disponible en: **http://localhost:8000/api/**

---

## 📡 Primeros Pasos - Pruebas

### 1. Obtener Token JWT

```bash
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123456"}'
```

**Respuesta:**
```json
{
  "access": "eyJhbGciOiJIUzI1NiIs...",
  "refresh": "eyJhbGciOiJIUzI1NiIs...",
  "user": {...}
}
```

### 2. Usar el Token en Solicitudes

```bash
curl -X GET http://localhost:8000/api/sensores/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 3. Ver Información del Proyecto

```bash
curl -X GET http://localhost:8000/api/info/
```

### 4. Simular Lectura RFID (Sin Token)

```bash
curl -X POST http://localhost:8000/api/simular/lectura-sensor/ \
  -H "Content-Type: application/json" \
  -d '{"uid": "AA:BB:CC:DD:EE:01", "departamento_id": 1}'
```

---

## 📚 Documentación

### Archivos de Documentación

1. **DOCUMENTACION_TECNICA.md** - Documentación completa del proyecto
   - Arquitectura general
   - Modelos y relaciones
   - Todos los endpoints
   - Autenticación y permisos
   - Validaciones
   - Guía de despliegue AWS

2. **GUIA_ENDPOINTS.txt** - Guía rápida de endpoints
   - Ejemplos de solicitudes
   - Respuestas esperadas
   - Flujos completos

3. **SmartConnect_API.postman_collection.json** - Colección Postman
   - Importa esta en Postman o Apidog
   - Todos los endpoints preconfigurados
   - Variables para tokens

### Importar Colección en Postman

1. Abre Postman
2. Click en "Import"
3. Selecciona `SmartConnect_API.postman_collection.json`
4. La colección se importará con todos los endpoints

### Importar Colección en Apidog

1. Abre Apidog
2. Click en "Import"
3. Selecciona `SmartConnect_API.postman_collection.json`
4. Click "Importar"

---

## 🔐 Autenticación

### Flujo JWT

```
1. POST /api/login/
   {username, password}
   ↓
2. Respuesta con access_token y refresh_token
   ↓
3. Incluir en header: Authorization: Bearer {access_token}
   ↓
4. Token válido por 1 hora
   ↓
5. Usar refresh_token para renovar
   POST /api/token/refresh/
```

### Tipos de Usuarios

**Admin:**
- Acceso total CRUD
- Crear/editar/eliminar sensores
- Abrir/cerrar barreras
- Cambiar estados

**Operador:**
- Solo lectura
- Ver sensores
- Ver eventos
- Ver departamentos

---

## 📊 Estructura de Datos

### Modelos Principales

```
Rol (admin, operador)
  ↓
Usuario (con rol asignado)
  ↓
Departamento (zona de acceso)
  ↓
Sensor (RFID - UID único)
  ↓
Barrera (abierta/cerrada)
  ↓
Evento (registro de acceso)
```

---

## 🧪 Casos de Prueba

### Caso 1: Flujo Básico

```
1. Login → Obtener token
2. Crear sensor
3. Simular lectura RFID
4. Ver eventos generados
5. Cambiar estado de sensor
```

### Caso 2: Control de Acceso Completo

```
1. Sensor intenta acceso
2. Sistema valida estado
3. Si activo → abre barrera
4. Si inactivo/bloqueado → acceso denegado
5. Evento registrado
6. Barrera se cierra automáticamente
```

### Caso 3: Prueba de Permisos

```
1. Login como operador
2. Intentar crear sensor → 403 Forbidden
3. Intentar listar sensores → 200 OK (lectura)
4. Intentar eliminar sensor → 403 Forbidden
```

### Caso 4: Validaciones

```
1. UID duplicado → 400 Bad Request
2. Nombre muy corto → 400 Bad Request
3. Estado inválido → 400 Bad Request
4. Sin autenticación → 401 Unauthorized
5. Sensor no existe → 404 Not Found
```

---

## 🏗️ Estructura del Proyecto

```
smartconnect_backend/
├── api/
│   ├── models.py              # 6 modelos
│   ├── views.py               # 5 ViewSets + 5 funciones
│   ├── serializers.py         # 8 serializadores
│   ├── urls.py                # Rutas
│   ├── admin.py               # Panel Django
│   └── migrations/
├── smartconnect_backend/
│   ├── settings.py            # Config Django + JWT + DRF
│   ├── urls.py                # URLs principales
│   └── wsgi.py
├── manage.py
├── db.sqlite3                 # Base de datos
├── requirements.txt
├── populate_db.py             # Generador de datos
├── .env                       # Variables de entorno
├── DOCUMENTACION_TECNICA.md   # Documentación completa
├── GUIA_ENDPOINTS.txt         # Guía rápida
└── SmartConnect_API.postman_collection.json
```

---

## 🛠️ Configuración

### Variables de Entorno (.env)

```
SECRET_KEY=django-insecure-smartconnect-key-2024
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Database
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3

# JWT
JWT_SECRET_KEY=your-jwt-secret-key-here
JWT_ALGORITHM=HS256

# AWS (Llenar para producción)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_STORAGE_BUCKET_NAME=
AWS_S3_REGION_NAME=us-east-1
```

---

## 📈 Estadísticas de la API

| Métrica | Cantidad |
|---------|----------|
| Endpoints | 40+ |
| Modelos | 6 |
| Serializadores | 8 |
| ViewSets | 5 |
| Validaciones | 20+ |
| Códigos HTTP | 8 |

---

## 🚢 Despliegue en AWS EC2

### Requisitos

- Instancia EC2 (Amazon Linux 2)
- RDS PostgreSQL
- Nginx
- Dominio (opcional)

### Pasos

1. **Clonar repositorio en EC2**
   ```bash
   git clone <tu-repo>
   cd smartconnect_backend
   ```

2. **Configurar base de datos**
   ```python
   # settings.py
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'smartconnect',
           'USER': 'postgres',
           'PASSWORD': 'tu-password',
           'HOST': 'tu-rds.amazonaws.com',
           'PORT': '5432',
       }
   }
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

5. **Configurar Nginx como proxy reverso**
   ```bash
   sudo systemctl start nginx
   ```

6. **URL pública**
   ```
   http://ec2-tu-ip.amazonaws.com/api/
   ```

Ver **DOCUMENTACION_TECNICA.md** para detalles completos.

---

## 🐛 Troubleshooting

### Error: "Module not found"

```bash
pip install -r requirements.txt
```

### Error: "Database is locked"

```bash
# Eliminar el archivo de base de datos y recrearlo
rm db.sqlite3
python manage.py migrate
python populate_db.py
```

### Error: "ALLOWED_HOSTS"

Modificar `settings.py`:
```python
ALLOWED_HOSTS = ['tu-ip', 'tu-dominio.com', 'localhost']
```

### Puerto 8000 ocupado

```bash
python manage.py runserver 8001
```

---

## 📝 Notas Importantes

### ✅ Lo que está implementado

- Autenticación JWT completa
- 6 modelos de datos
- 40+ endpoints funcionales
- 5 endpoints de simulación IoT
- Validaciones exhaustivas
- Manejo de errores robusto
- Panel administrativo Django
- Documentación completa

### 🔄 Flujo IoT Simulado

**Sin necesidad de hardware real:**

```
NodeMCU (Simulado) 
  ↓
POST /api/simular/lectura-sensor/ (UID: AA:BB:CC:DD:EE:01)
  ↓
API valida sensor en BD
  ↓
¿Estado activo? 
  Sí → Acceso permitido → Abre barrera
  No → Acceso denegado
  ↓
Crea evento (registro de acceso)
  ↓
Retorna resultado al "NodeMCU"
```

### 🔒 Seguridad Implementada

- ✓ Hashing de contraseñas
- ✓ JWT con expiración
- ✓ Permisos granulares
- ✓ Validación de datos
- ✓ CORS configurado
- ✓ CSRF protection

---

## 👨‍💻 Autor

**Dylan Torres**  
Estudiante de Ingeniería en Informática  
Asignatura: Programación Back End

---

## 📄 Licencia

Proyecto educativo - 2025

---

## 📞 Soporte

Para preguntas o problemas:

1. Revisar **DOCUMENTACION_TECNICA.md**
2. Revisar **GUIA_ENDPOINTS.txt**
3. Ejecutar pruebas desde Postman/Apidog
4. Revisar logs del servidor

---

## ✅ Checklist Final

- [x] Modelos de datos creados
- [x] CRUD completo implementado
- [x] Autenticación JWT funcionando
- [x] Permisos configurados (Admin/Operador)
- [x] Validaciones robustas
- [x] Endpoints de simulación IoT
- [x] Documentación técnica
- [x] Colección Postman
- [x] Base de datos poblada
- [x] Servidor ejecutando
- [ ] Despliegue en AWS EC2 (próximo)

---

**Versión:** 1.0  
**Última actualización:** Diciembre 8, 2025  
**Estado:** ✅ Listo para pruebas y producción

