from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from .models import Rol, Departamento, Usuario, Sensor, Barrera, Evento
from .serializers import (
    RolSerializer, DepartamentoSerializer, UsuarioSerializer,
    SensorSerializer, BarreraSerializer, EventoSerializer,
    LoginSerializer, RegistroUsuarioSerializer
)


class IsAdminOrReadOnly(permissions.BasePermission):
    """Permiso personalizado: Admin puede hacer todo, otros solo lectura"""
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Verificar si el usuario es admin
        try:
            usuario = request.user.perfil
            return usuario.rol.nombre == 'admin'
        except:
            return False


class IsAdmin(permissions.BasePermission):
    """Permiso que solo permite acceso a administradores"""
    
    def has_permission(self, request, view):
        try:
            usuario = request.user.perfil
            return usuario.rol.nombre == 'admin'
        except:
            return False


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def info_endpoint(request):
    """Endpoint de información del proyecto"""
    return Response({
        "autor": ["Dylan Barraza", "Cristobal Valenzuela"],
        "asignatura": "Programación Back End",
        "proyecto": "SmartConnect - Sistema de Control de Acceso Inteligente",
        "descripcion": "API RESTful para gestionar sensores RFID, usuarios, departamentos y eventos de acceso en un sistema IoT de control inteligente.",
        "version": "1.0"
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    """Endpoint de login - Genera token JWT"""
    serializer = LoginSerializer(data=request.data)
    
    if serializer.is_valid():
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        
        user = authenticate(username=username, password=password)
        
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response(
                {'error': 'Credenciales inválidas'},
                status=status.HTTP_401_UNAUTHORIZED
            )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def registro_view(request):
    """Endpoint de registro de nuevos usuarios"""
    serializer = RegistroUsuarioSerializer(data=request.data)
    
    if serializer.is_valid():
        try:
            user = serializer.save()
            return Response({
                'message': 'Usuario registrado exitosamente',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                }
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RolViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar roles"""
    queryset = Rol.objects.all()
    serializer_class = RolSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]


class DepartamentoViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar departamentos/zonas"""
    queryset = Departamento.objects.all()
    serializer_class = DepartamentoSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    search_fields = ['nombre', 'ubicacion']
    ordering_fields = ['nombre', 'fecha_creacion']


class UsuarioViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar usuarios"""
    queryset = Usuario.objects.select_related('user', 'rol', 'departamento')
    serializer_class = UsuarioSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    search_fields = ['user__username', 'user__email', 'user__first_name']


class SensorViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar sensores RFID"""
    queryset = Sensor.objects.select_related('departamento', 'usuario')
    serializer_class = SensorSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    search_fields = ['uid', 'nombre', 'estado']
    ordering_fields = ['nombre', 'estado', 'fecha_creacion']
    filterset_fields = ['estado', 'departamento']
    
    def perform_create(self, serializer):
        serializer.save()
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsAdmin])
    def cambiar_estado(self, request, pk=None):
        """Cambiar el estado de un sensor"""
        sensor = self.get_object()
        nuevo_estado = request.data.get('estado')
        
        valid_estados = ['activo', 'inactivo', 'bloqueado', 'perdido']
        if nuevo_estado not in valid_estados:
            return Response(
                {'error': f'Estado inválido. Debe ser uno de: {", ".join(valid_estados)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        sensor.estado = nuevo_estado
        sensor.save()
        
        return Response(
            {
                'message': f'Estado del sensor actualizado a: {nuevo_estado}',
                'sensor': SensorSerializer(sensor).data
            },
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsAdminOrReadOnly])
    def solicitar_acceso(self, request, pk=None):
        """Solicitar acceso con un sensor (registra evento)"""
        sensor = self.get_object()
        
        # Validaciones
        if sensor.estado != 'activo':
            return Response(
                {'error': f'Sensor no activo. Estado actual: {sensor.get_estado_display()}'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Crear evento de acceso intentado
        evento = Evento.objects.create(
            sensor=sensor,
            tipo='acceso_intentado',
            mensaje=f'Intento de acceso con sensor {sensor.uid}'
        )
        
        # Si el sensor está activo, permitir acceso
        evento.tipo = 'acceso_permitido'
        evento.mensaje = f'Acceso permitido. Sensor: {sensor.nombre}'
        evento.save()
        
        return Response(
            {
                'acceso': 'permitido',
                'sensor': sensor.nombre,
                'evento': EventoSerializer(evento).data
            },
            status=status.HTTP_200_OK
        )


class BarreraViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar barreras de acceso"""
    queryset = Barrera.objects.select_related('departamento')
    serializer_class = BarreraSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsAdmin])
    def abrir(self, request, pk=None):
        """Abrir la barrera manualmente"""
        barrera = self.get_object()
        barrera.estado = 'abierta'
        barrera.save()
        
        # Crear evento
        usuario = request.user.perfil if hasattr(request.user, 'perfil') else None
        Evento.objects.create(
            sensor=Sensor.objects.first(),  # Referencia genérica
            tipo='barrera_abierta',
            barrera=barrera,
            usuario_accion=usuario,
            mensaje=f'Barrera {barrera.nombre} abierta manualmente'
        )
        
        return Response(
            {
                'message': f'Barrera {barrera.nombre} abierta',
                'barrera': BarreraSerializer(barrera).data
            },
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsAdmin])
    def cerrar(self, request, pk=None):
        """Cerrar la barrera manualmente"""
        barrera = self.get_object()
        barrera.estado = 'cerrada'
        barrera.save()
        
        # Crear evento
        usuario = request.user.perfil if hasattr(request.user, 'perfil') else None
        Evento.objects.create(
            sensor=Sensor.objects.first(),  # Referencia genérica
            tipo='barrera_cerrada',
            barrera=barrera,
            usuario_accion=usuario,
            mensaje=f'Barrera {barrera.nombre} cerrada manualmente'
        )
        
        return Response(
            {
                'message': f'Barrera {barrera.nombre} cerrada',
                'barrera': BarreraSerializer(barrera).data
            },
            status=status.HTTP_200_OK
        )


class EventoViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para ver eventos (solo lectura)"""
    queryset = Evento.objects.select_related('sensor', 'barrera', 'usuario_accion')
    serializer_class = EventoSerializer
    permission_classes = [permissions.IsAuthenticated]
    ordering_fields = ['fecha_evento', 'tipo']
    filterset_fields = ['sensor', 'tipo', 'barrera']
    search_fields = ['sensor__nombre', 'sensor__uid', 'tipo']
    
    @action(detail=False, methods=['get'])
    def por_sensor(self, request):
        """Obtener eventos de un sensor específico"""
        sensor_id = request.query_params.get('sensor_id')
        
        if not sensor_id:
            return Response(
                {'error': 'sensor_id es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            sensor = Sensor.objects.get(id=sensor_id)
            eventos = Evento.objects.filter(sensor=sensor).order_by('-fecha_evento')
            serializer = self.get_serializer(eventos, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Sensor.DoesNotExist:
            return Response(
                {'error': 'Sensor no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def por_tipo(self, request):
        """Obtener eventos por tipo"""
        tipo = request.query_params.get('tipo')
        
        if not tipo:
            return Response(
                {'error': 'tipo es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        eventos = Evento.objects.filter(tipo=tipo).order_by('-fecha_evento')
        serializer = self.get_serializer(eventos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ==================== ENDPOINTS IoT SIMULATION ====================
# Estos endpoints simulan el comportamiento de un NodeMCU/Sensor RFID
# Permiten probar el flujo completo sin hardware real

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def simular_lectura_sensor(request):
    """
    Simula una lectura de sensor RFID (como si fuera un NodeMCU)
    
    POST /api/simular/lectura-sensor/
    
    Datos esperados:
    {
        "uid": "AA:BB:CC:DD:EE:01",
        "departamento_id": 1,
        "sensor_name": "Tarjeta Acceso 001"
    }
    
    Retorna:
    - 200: Acceso permitido
    - 403: Acceso denegado (sensor bloqueado/perdido)
    - 404: Sensor no encontrado
    """
    uid = request.data.get('uid')
    departamento_id = request.data.get('departamento_id')
    
    if not uid:
        return Response(
            {'error': 'uid es requerido'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        sensor = Sensor.objects.get(uid=uid)
    except Sensor.DoesNotExist:
        # Crear evento de intento fallido
        Evento.objects.create(
            sensor=Sensor.objects.first(),  # Referencia
            tipo='acceso_denegado',
            mensaje=f'Intento con sensor desconocido: {uid}'
        )
        return Response({
            'acceso': 'denegado',
            'razon': 'Sensor no registrado en el sistema',
            'uid': uid
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Validar estado del sensor
    if sensor.estado == 'inactivo':
        evento = Evento.objects.create(
            sensor=sensor,
            tipo='acceso_denegado',
            mensaje=f'Intento con sensor inactivo: {sensor.nombre}'
        )
        return Response({
            'acceso': 'denegado',
            'razon': 'Sensor inactivo',
            'sensor': sensor.nombre,
            'evento_id': evento.id
        }, status=status.HTTP_403_FORBIDDEN)
    
    elif sensor.estado == 'bloqueado':
        evento = Evento.objects.create(
            sensor=sensor,
            tipo='acceso_denegado',
            mensaje=f'Intento con sensor bloqueado: {sensor.nombre}'
        )
        return Response({
            'acceso': 'denegado',
            'razon': 'Sensor bloqueado por administrador',
            'sensor': sensor.nombre,
            'evento_id': evento.id
        }, status=status.HTTP_403_FORBIDDEN)
    
    elif sensor.estado == 'perdido':
        evento = Evento.objects.create(
            sensor=sensor,
            tipo='acceso_denegado',
            mensaje=f'Intento con sensor perdido: {sensor.nombre}'
        )
        return Response({
            'acceso': 'denegado',
            'razon': 'Sensor reportado como perdido',
            'sensor': sensor.nombre,
            'evento_id': evento.id
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Acceso permitido
    evento = Evento.objects.create(
        sensor=sensor,
        tipo='acceso_permitido',
        mensaje=f'Acceso permitido a: {sensor.nombre}'
    )
    
    return Response({
        'acceso': 'permitido',
        'sensor': sensor.nombre,
        'uid': sensor.uid,
        'estado_sensor': sensor.estado,
        'departamento': sensor.departamento.nombre if sensor.departamento else 'Sin asignar',
        'evento_id': evento.id,
        'timestamp': evento.fecha_evento
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, IsAdmin])
def simular_intento_acceso(request):
    """
    Simula un intento de acceso completo con manejo de barrera
    
    POST /api/simular/intento-acceso/
    
    Datos esperados:
    {
        "uid": "AA:BB:CC:DD:EE:01",
        "barrera_id": 1
    }
    
    Retorna:
    - 200: Acceso permitido, barrera abre
    - 403: Acceso denegado, barrera permanece cerrada
    """
    uid = request.data.get('uid')
    barrera_id = request.data.get('barrera_id')
    
    if not uid:
        return Response(
            {'error': 'uid es requerido'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        sensor = Sensor.objects.get(uid=uid)
    except Sensor.DoesNotExist:
        return Response({
            'acceso': 'denegado',
            'razon': 'Sensor no encontrado',
            'barrera_accion': 'permanece cerrada'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Validar sensor
    if sensor.estado != 'activo':
        evento = Evento.objects.create(
            sensor=sensor,
            tipo='acceso_denegado',
            mensaje=f'Intento denegado: sensor {sensor.estado}'
        )
        
        return Response({
            'acceso': 'denegado',
            'razon': f'Sensor {sensor.get_estado_display()}',
            'sensor': sensor.nombre,
            'barrera_accion': 'permanece cerrada',
            'evento_id': evento.id
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Acceso permitido - abrir barrera
    barrera = None
    if barrera_id:
        try:
            barrera = Barrera.objects.get(id=barrera_id)
            barrera.estado = 'abierta'
            barrera.save()
        except Barrera.DoesNotExist:
            pass
    
    evento = Evento.objects.create(
        sensor=sensor,
        tipo='acceso_permitido',
        barrera=barrera,
        mensaje=f'Acceso permitido - Barrera abierta para {sensor.nombre}'
    )
    
    return Response({
        'acceso': 'permitido',
        'sensor': sensor.nombre,
        'barrera': barrera.nombre if barrera else 'No asignada',
        'barrera_accion': 'ABIERTA' if barrera else 'N/A',
        'evento_id': evento.id,
        'timestamp': evento.fecha_evento
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, IsAdmin])
def simular_cierre_barrera(request):
    """
    Simula el cierre automático de la barrera después de un tiempo
    
    POST /api/simular/cierre-barrera/
    
    Datos esperados:
    {
        "barrera_id": 1
    }
    
    Retorna:
    - 200: Barrera cerrada correctamente
    """
    barrera_id = request.data.get('barrera_id')
    
    if not barrera_id:
        return Response(
            {'error': 'barrera_id es requerido'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        barrera = Barrera.objects.get(id=barrera_id)
        barrera.estado = 'cerrada'
        barrera.save()
        
        evento = Evento.objects.create(
            sensor=Sensor.objects.first(),
            tipo='barrera_cerrada',
            barrera=barrera,
            mensaje=f'Barrera {barrera.nombre} cerrada automáticamente'
        )
        
        return Response({
            'mensaje': 'Barrera cerrada',
            'barrera': barrera.nombre,
            'estado': barrera.estado,
            'evento_id': evento.id
        }, status=status.HTTP_200_OK)
    except Barrera.DoesNotExist:
        return Response({
            'error': 'Barrera no encontrada'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, IsAdmin])
def simular_cambio_estado_sensor(request):
    """
    Simula un cambio de estado en el NodeMCU (reporta sensor perdido, etc)
    
    POST /api/simular/cambio-estado/
    
    Datos esperados:
    {
        "uid": "AA:BB:CC:DD:EE:01",
        "nuevo_estado": "bloqueado"
    }
    """
    uid = request.data.get('uid')
    nuevo_estado = request.data.get('nuevo_estado')
    
    if not uid or not nuevo_estado:
        return Response(
            {'error': 'uid y nuevo_estado son requeridos'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    valid_estados = ['activo', 'inactivo', 'bloqueado', 'perdido']
    if nuevo_estado not in valid_estados:
        return Response({
            'error': f'Estado inválido. Debe ser uno de: {", ".join(valid_estados)}'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        sensor = Sensor.objects.get(uid=uid)
        estado_anterior = sensor.estado
        sensor.estado = nuevo_estado
        sensor.save()
        
        return Response({
            'mensaje': f'Estado del sensor actualizado',
            'sensor': sensor.nombre,
            'estado_anterior': estado_anterior,
            'estado_nuevo': nuevo_estado,
            'uid': sensor.uid
        }, status=status.HTTP_200_OK)
    except Sensor.DoesNotExist:
        return Response({
            'error': 'Sensor no encontrado',
            'uid': uid
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def estado_sistema(request):
    """
    Retorna el estado general del sistema (simulando dashboard del NodeMCU)
    
    GET /api/simular/estado-sistema/
    """
    from django.utils import timezone
    from datetime import timedelta
    
    # Estadísticas
    total_sensores = Sensor.objects.count()
    sensores_activos = Sensor.objects.filter(estado='activo').count()
    sensores_inactivos = Sensor.objects.filter(estado='inactivo').count()
    sensores_bloqueados = Sensor.objects.filter(estado='bloqueado').count()
    sensores_perdidos = Sensor.objects.filter(estado='perdido').count()
    
    total_barreras = Barrera.objects.count()
    barreras_abiertas = Barrera.objects.filter(estado='abierta').count()
    barreras_cerradas = Barrera.objects.filter(estado='cerrada').count()
    
    # Eventos en las últimas 24 horas
    hace_24h = timezone.now() - timedelta(hours=24)
    eventos_recientes = Evento.objects.filter(fecha_evento__gte=hace_24h).count()
    accesos_permitidos = Evento.objects.filter(
        tipo='acceso_permitido',
        fecha_evento__gte=hace_24h
    ).count()
    accesos_denegados = Evento.objects.filter(
        tipo='acceso_denegado',
        fecha_evento__gte=hace_24h
    ).count()
    
    return Response({
        'sensores': {
            'total': total_sensores,
            'activos': sensores_activos,
            'inactivos': sensores_inactivos,
            'bloqueados': sensores_bloqueados,
            'perdidos': sensores_perdidos
        },
        'barreras': {
            'total': total_barreras,
            'abiertas': barreras_abiertas,
            'cerradas': barreras_cerradas
        },
        'eventos_24h': {
            'total': eventos_recientes,
            'accesos_permitidos': accesos_permitidos,
            'accesos_denegados': accesos_denegados
        },
        'timestamp': timezone.now()
    }, status=status.HTTP_200_OK)
