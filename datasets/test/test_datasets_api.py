import io
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from datasets.models import Dataset

User = get_user_model()

class DatasetAPITestCase(APITestCase):
    def setUp(self):
        # Creamos dos usuarios para probar permisos
        self.user1 = User.objects.create_user(
           username='prueba1', email='user1@example.com', password='pass1234'
        )
        self.user2 = User.objects.create_user(
           username='prueba2', email='user2@example.com', password='pass1234'
        )

        # URLs del listado y detalle
        self.list_url   = reverse('dataset-list')
        # Autenticamos user1 por defecto en este cliente
        self.client.force_authenticate(user=self.user1)

    def _make_file(self, name='data.csv', size_kb=1):
        """
        Genera un archivo CSV de tamaño aproximado size_kb.
        """
        header = b'col1,col2,col3\n'
        line   = b'1,2,3\n'
        content = header + line * (size_kb * 100)
        return SimpleUploadedFile(name, content, content_type='text/csv')

    def test_upload_valid_csv(self):
        """
        POST /datasets/ con CSV válido → 201 CREATED y owner asignado.
        """
        payload = {
            'name': 'Mi CSV',
            'description': 'Prueba de carga',
            'file': self._make_file(size_kb=1)
        }
        response = self.client.post(self.list_url, payload, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Dataset.objects.count(), 1)
        self.assertEqual(Dataset.objects.first().owner, self.user1)

    def test_upload_invalid_extension(self):
        """
        POST /datasets/ con extensión no permitida → 400 BAD REQUEST.
        """
        bad_file = SimpleUploadedFile(
            'malware.exe', b'data', content_type='application/octet-stream'
        )
        payload = {'name': 'Malware', 'file': bad_file}
        response = self.client.post(self.list_url, payload, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('file', response.data)

    def test_upload_exceed_size_limit(self):
        """
        POST /datasets/ con archivo >10MB → 400 BAD REQUEST.
        """
        big_file = self._make_file(size_kb=1100)  # ~11 MB
        payload = {'name': 'Gigante', 'file': big_file}
        response = self.client.post(self.list_url, payload, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('El archivo no puede superar', str(response.data))

    def test_list_only_owner_datasets(self):
        """
        GET /datasets/ muestra solo datasets del usuario autenticado.
        """
        # Creamos un dataset para user2 y otro para user1
        Dataset.objects.create(
            owner=self.user2, name='Otro', file=self._make_file()
        )
        ds = Dataset.objects.create(
            owner=self.user1, name='Mío', file=self._make_file()
        )

        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [item['name'] for item in response.data]
        self.assertIn('Mío', names)
        self.assertNotIn('Otro', names)

    def test_retrieve_and_delete_permissions(self):
        """
        GET/DELETE /datasets/{id}/:
        - Owner    → 200 / 204
        - No owner → 403 or 404
        """
        ds = Dataset.objects.create(
            owner=self.user1, name='SoloMío', file=self._make_file()
        )
        detail_url = reverse('dataset-detail', args=[ds.id])

        # Owner puede ver
        resp_get = self.client.get(detail_url)
        self.assertEqual(resp_get.status_code, status.HTTP_200_OK)

        # Owner puede eliminar
        resp_del = self.client.delete(detail_url)
        self.assertEqual(resp_del.status_code, status.HTTP_204_NO_CONTENT)

        # Autenticamos como otro usuario y probamos acceso denegado
        self.client.force_authenticate(user=self.user2)
        resp_forbidden = self.client.get(detail_url)
        self.assertIn(
            resp_forbidden.status_code,
            (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND)
        )
