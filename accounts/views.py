from django.shortcuts import render

# Create your views here.

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from rest_framework.permissions import AllowAny
from .serializadores import RegisterSerializer,  PasswordResetRequestSerializer, PasswordResetConfirmSerializer, MyTokenObtainPairSerializer
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

User = get_user_model()
token_generator = PasswordResetTokenGenerator()

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

class LoginWithSessionView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        # 1. Generar JWT (access y refresh)
        response = super().post(request, *args, **kwargs)

        # 2. Autenticar al usuario en la sesión de Django
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            # Django añadirá automáticamente Set-Cookie: sessionid=…
        return response

class LogoutView(APIView):
    """
    Destruye la sesión de Django y elimina la cookie de JWT
    """
    permission_classes = []  # O IsAuthenticated para protegerla

    def post(self, request, *args, **kwargs):
        # 1. Logout de Django: destruye la sesión y rota sessionid
        logout(request)
        request.session.flush()  # Asegura que la sesión se invalida

        # 2. Construir respuesta y eliminar cookies
        response = Response(status=status.HTTP_204_NO_CONTENT)

        # Borra la cookie de sesión de Django
        response.delete_cookie('sessionid', path='/', domain=None)
        # Borra la cookie donde guardamos el JWT
        response.delete_cookie('jwt', path='/', domain=None)

        return response

class RefreshView(TokenRefreshView):
    permission_classes = [permissions.AllowAny]

class PasswordResetRequestView(generics.GenericAPIView):
    serializer_class = PasswordResetRequestSerializer

    def post(self, request, *args, **kwargs):
        """
        Recibe el email del usuario activo y envía un correo con el link de restablecimiento.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        try:
            user = User.objects.get(email=email, is_active=True)
        except User.DoesNotExist:
            # Esto no debería ocurrir, pues el serializer ya valida existencia
            return Response(
                {'detail': 'Usuario no encontrado o inactivo.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = token_generator.make_token(user)

        # Ajusta el dominio según tu entorno (dev/prod)
        reset_link = (
            f"http://localhost:8000/api/v1/accounts/"
            f"password-reset-confirm/?uid={uidb64}&token={token}"
        )

        send_mail(
            subject='Restablecer tu contraseña',
            message=(
                'Hola,\n\n'
                'Has solicitado restablecer tu contraseña. '
                'Usa el siguiente enlace:\n\n'
                f'{reset_link}\n\n'
                'Si no fuiste tú, ignora este mensaje.'
            ),
            from_email=None,  # Usa DEFAULT_FROM_EMAIL
            recipient_list=[user.email],
        )

        return Response(
            {'detail': 'Email de restablecimiento enviado.'},
            status=status.HTTP_200_OK
        )


class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request, *args, **kwargs):
        """
        Valida uid, token y contraseñas; actualiza la contraseña del usuario.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {'detail': 'Contraseña actualizada correctamente.'},
            status=status.HTTP_200_OK
        )

