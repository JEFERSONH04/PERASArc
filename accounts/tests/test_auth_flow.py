from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

class AuthenticationFlowTests(APITestCase):
    """
    Pruebas del flujo de autenticación JWT:
      - Login exitoso
      - Login fallido
      - Refresh exitoso
      - Refresh fallido
    """

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username='flowuser',
            email='flow@example.com',
            password='FlowPass123!'
        )
        # Nombres en accounts/urls.py
        self.login_url   = reverse('accounts:login')
        self.refresh_url = reverse('accounts:token_refresh')

    def test_login_success(self):
        """Credenciales válidas → status 200 + tokens."""
        """
        Verifica que al enviar credenciales válidas:
        - se reciba un HTTP 200 OK
        - la respuesta contenga 'access' y 'refresh' tokens
        """
        # Paso 1: Preparamos datos de login válidos
        response = self.client.post(
            self.login_url,
            {'username': 'flowuser', 'password': 'FlowPass123!'},
            format='json'
        )

        # Paso 3: Comprobaciones
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access',  response.data)
        self.assertIn('refresh', response.data)

    def test_login_failure(self):
        """Contraseña incorrecta → 401 Unauthorized."""
        """
        Comprueba que al enviar credenciales inválidas:
        - se reciba un HTTP 401 Unauthorized
        - no se devuelvan tokens en la respuesta
        """
        # Intentamos login con password incorrecta
        response = self.client.post(
            self.login_url,
            {'username': 'flowuser', 'password': 'WrongPass'},
            format='json'
        )

        # Validar que el acceso sea denegado
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn('access',  response.data)
        self.assertNotIn('refresh', response.data)

    def test_refresh_success(self):
        """Refresh válido → 200 + nuevo access."""
        """
            Asegura que al enviar un refresh token válido:
            - se reciba un HTTP 200 OK
            - se devuelva un nuevo access token
            - se devuelva un nuevo refresh
        """
        # Paso 1: Obtener primero un par de tokens
        login_resp   = self.client.post(
            self.login_url,
            {'username': 'flowuser', 'password': 'FlowPass123!'},
            format='json'
        )

        # Paso 2: Refrescamos el access token
        refresh_token = login_resp.data['refresh']
        response = self.client.post(
            self.refresh_url,
            {'refresh': refresh_token},
            format='json'
        )

        # Paso 3: Comprobaciones básicas
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_refresh_failure(self):
        """Refresh inválido → 401 Unauthorized."""
        """
        Verifica que al enviar un refresh token inválido:
        - se reciba un HTTP 401 Unauthorized
        - no se devuelva ningún token
        """
        
        response = self.client.post(
            self.refresh_url,
            {'refresh': 'invalid.token.here'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn('access', response.data)
