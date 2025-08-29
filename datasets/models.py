from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class MetaData(models.Model):
    """
    Representa un conjunto de datos subido por un usuario.

    Campos:
      - owner: relación a User; el dueño del dataset.
      - name: nombre descriptivo (máx. 100 caracteres).
      - description: texto opcional para más detalles.
      - file: archivo subido, guardado en MEDIA_ROOT/datasets/.
      - created_at: timestamp de creación automática.
    """
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='datasets')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='data/datasets/') #colocar la ruta asignada para los datasets
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.owner.email})"
