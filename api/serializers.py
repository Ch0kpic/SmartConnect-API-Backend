from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Rol, Departamento, Usuario, Sensor, Barrera, Evento


class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = ['id', 'nombre', 'descripcion']
        read_only_fields = ['id']


class DepartamentoSerializer(serializers.ModelSerializer):
    sensores_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Departamento
        fields = ['id', 'nombre', 'descripcion', 'ubicacion', 'activo', 'sensores_count']
        read_only_fields = ['id']
    
    def validate_nombre(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("El nombre debe tener al menos 3 caracteres.")
        return value
    
    def get_sensores_count(self, obj):
        return obj.sensores.count()


class UsuarioSerializer(serializers.ModelSerializer):
    user_detail = serializers.SerializerMethodField()
    rol_nombre = serializers.CharField(source='rol.get_nombre_display', read_only=True)
    departamento_nombre = serializers.CharField(source='departamento.nombre', read_only=True)
    
    class Meta:
        model = Usuario
        fields = [
            'id', 'user_detail', 'rol', 'rol_nombre', 'departamento', 
            'departamento_nombre', 'activo', 'fecha_creacion'
        ]
        read_only_fields = ['id', 'fecha_creacion', 'user_detail']
    
    def get_user_detail(self, obj):
        return {
            'id': obj.user.id,
            'username': obj.user.username,
            'first_name': obj.user.first_name,
            'last_name': obj.user.last_name,
            'email': obj.user.email,
        }


class SensorSerializer(serializers.ModelSerializer):
    departamento_nombre = serializers.CharField(source='departamento.nombre', read_only=True)
    usuario_nombre = serializers.CharField(source='usuario.user.get_full_name', read_only=True)
    
    class Meta:
        model = Sensor
        fields = [
            'id', 'uid', 'nombre', 'estado', 'departamento', 
            'departamento_nombre', 'usuario', 'usuario_nombre',
            'fecha_creacion', 'fecha_actualizacion'
        ]
        read_only_fields = ['id', 'fecha_creacion', 'fecha_actualizacion']
    
    def validate_uid(self, value):
        """Validar que el UID sea único y tenga formato válido"""
        if len(value) < 5:
            raise serializers.ValidationError("El UID debe tener al menos 5 caracteres.")
        
        # Si estamos actualizando, permitir el mismo UID
        if self.instance and self.instance.uid == value:
            return value
        
        # Verificar que no exista otro sensor con el mismo UID
        if Sensor.objects.filter(uid=value).exists():
            raise serializers.ValidationError("Ya existe un sensor con este UID.")
        
        return value
    
    def validate_nombre(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("El nombre debe tener al menos 3 caracteres.")
        return value
    
    def validate_estado(self, value):
        valid_estados = ['activo', 'inactivo', 'bloqueado', 'perdido']
        if value not in valid_estados:
            raise serializers.ValidationError(f"Estado inválido. Debe ser uno de: {', '.join(valid_estados)}")
        return value


class BarreraSerializer(serializers.ModelSerializer):
    departamento_nombre = serializers.CharField(source='departamento.nombre', read_only=True)
    
    class Meta:
        model = Barrera
        fields = [
            'id', 'nombre', 'estado', 'departamento', 
            'departamento_nombre', 'fecha_ultimo_cambio'
        ]
        read_only_fields = ['id', 'fecha_ultimo_cambio']
    
    def validate_estado(self, value):
        valid_estados = ['abierta', 'cerrada']
        if value not in valid_estados:
            raise serializers.ValidationError(f"Estado inválido. Debe ser uno de: {', '.join(valid_estados)}")
        return value


class EventoSerializer(serializers.ModelSerializer):
    sensor_nombre = serializers.CharField(source='sensor.nombre', read_only=True)
    sensor_uid = serializers.CharField(source='sensor.uid', read_only=True)
    barrera_nombre = serializers.CharField(source='barrera.nombre', read_only=True)
    usuario_accion_nombre = serializers.CharField(
        source='usuario_accion.user.get_full_name',
        read_only=True
    )
    
    class Meta:
        model = Evento
        fields = [
            'id', 'sensor', 'sensor_nombre', 'sensor_uid', 'tipo',
            'barrera', 'barrera_nombre', 'usuario_accion', 
            'usuario_accion_nombre', 'mensaje', 'fecha_evento'
        ]
        read_only_fields = ['id', 'fecha_evento', 'usuario_accion']
    
    def validate_tipo(self, value):
        valid_tipos = [
            'acceso_intentado', 'acceso_permitido', 'acceso_denegado',
            'barrera_abierta', 'barrera_cerrada'
        ]
        if value not in valid_tipos:
            raise serializers.ValidationError(f"Tipo inválido. Debe ser uno de: {', '.join(valid_tipos)}")
        return value


class LoginSerializer(serializers.Serializer):
    """Serializer para login de usuarios"""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class RegistroUsuarioSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)
    rol_id = serializers.IntegerField(required=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'password', 'password_confirm', 'rol_id'
        ]
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError(
                {"password": "Las contraseñas no coinciden."}
            )
        
        if len(data['password']) < 8:
            raise serializers.ValidationError(
                {"password": "La contraseña debe tener al menos 8 caracteres."}
            )
        
        return data
    
    def create(self, validated_data):
        rol_id = validated_data.pop('rol_id')
        validated_data.pop('password_confirm')
        
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        
        # Crear perfil de usuario
        rol = Rol.objects.get(id=rol_id)
        Usuario.objects.create(user=user, rol=rol)
        
        return user
