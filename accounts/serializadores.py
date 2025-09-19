from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_str, force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

User = get_user_model()
token_generator = PasswordResetTokenGenerator()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'password')
    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class LoginSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        return token

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        # Agrega campos del usuario al payload
        data.update({
            'user': {
                'id':       self.user.id,
                'username': self.user.username,
                'email':    self.user.email
            }
        })
        return data
    
class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value, is_active=True).exists():
            raise serializers.ValidationError("No existe un usuario activo con este correo.")
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid  = serializers.CharField()
    token = serializers.CharField()
    new_password      = serializers.CharField(min_length=8, write_only=True)
    re_new_password   = serializers.CharField(min_length=8, write_only=True)

    def validate(self, data):
        if data['new_password'] != data['re_new_password']:
            raise serializers.ValidationError("Las contraseñas no coinciden.")
        return data

    def validate_uid(self, uid):
        try:
            uid_decoded = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=uid_decoded)
            self.user = user
        except (TypeError, ValueError, User.DoesNotExist):
            raise serializers.ValidationError("UID inválido.")
        # Guarda el user para validate_token y save()
        
        return uid

    def validate_token(self, token):
        if not token_generator.check_token(self.user, token):
            raise serializers.ValidationError("Token inválido o expirado.")
        return token

    def save(self):
        password = self.validated_data['new_password']
        self.user.set_password(password)
        self.user.save()
        return self.user
