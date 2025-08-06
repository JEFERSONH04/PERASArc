from django.contrib.auth import get_user_model
from django.core import mail
from django.urls import reverse
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()
token_generator = PasswordResetTokenGenerator()


class PasswordResetTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='prueba',
            email='prueba@example.com',
            password='InitialPass123!'
        )
        self.request_url = reverse('accounts:password_reset')
        self.confirm_url = reverse('accounts:password_reset_confirm')

    def test_request_password_reset_success(self):
        """Al solicitar reset con email válido, se envía un email."""
        response = self.client.post(self.request_url, {'email': self.user.email}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Un solo email en outbox
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Restablecer tu contraseña', mail.outbox[0].subject)

    def test_request_password_reset_invalid_email(self):
        """Email inexistente debería retornar 400."""
        response = self.client.post(self.request_url, {'email': 'no@mail.com'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reset_password_confirm_success(self):
        """Con uid y token válidos, la contraseña se actualiza."""
        # Generar uid y token manualmente
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        token  = token_generator.make_token(self.user)

        data = {
            'uid': uidb64,
            'token': token,
            'new_password': 'NuevaPass123!',
            're_new_password': 'NuevaPass123!'
        }
        response = self.client.post(self.confirm_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verificar que la contraseña cambió
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NuevaPass123!'))

    def test_reset_password_confirm_invalid_token(self):
        """Token inválido devuelve 400."""
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        data = {'uid': uidb64, 'token': 'token-falso', 
                'new_password': 'Xyz123456', 're_new_password': 'Xyz123456'}
        response = self.client.post(self.confirm_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
