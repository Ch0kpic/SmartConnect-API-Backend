from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    info_endpoint, login_view, registro_view,
    RolViewSet, DepartamentoViewSet, UsuarioViewSet,
    SensorViewSet, BarreraViewSet, EventoViewSet,
    simular_lectura_sensor, simular_intento_acceso,
    simular_cierre_barrera, simular_cambio_estado_sensor,
    estado_sistema
)

router = DefaultRouter()
router.register(r'roles', RolViewSet)
router.register(r'departamentos', DepartamentoViewSet)
router.register(r'usuarios', UsuarioViewSet)
router.register(r'sensores', SensorViewSet)
router.register(r'barreras', BarreraViewSet)
router.register(r'eventos', EventoViewSet)

urlpatterns = [
    # Info y autenticación
    path('info/', info_endpoint, name='info'),
    path('login/', login_view, name='login'),
    path('registro/', registro_view, name='registro'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # API endpoints CRUD
    path('', include(router.urls)),
    
    # Endpoints de simulación IoT (sin necesidad de hardware real)
    path('simular/lectura-sensor/', simular_lectura_sensor, name='lectura-sensor'),
    path('simular/intento-acceso/', simular_intento_acceso, name='intento-acceso'),
    path('simular/cierre-barrera/', simular_cierre_barrera, name='cierre-barrera'),
    path('simular/cambio-estado/', simular_cambio_estado_sensor, name='cambio-estado'),
    path('simular/estado-sistema/', estado_sistema, name='estado-sistema'),
]
