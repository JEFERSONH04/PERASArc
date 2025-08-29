from django.db import models

"""
analysis/models.py

Define los modelos para representar modelos de machine learning y
los resultados de análisis asociados a un dataset.
"""

from django.db import models
from django.conf import settings

class MLModel(models.Model):
    """
    Representa un modelo de machine learning que puede ejecutarse
    sobre datasets del sistema.

    Atributos:
        name (str): Nombre descriptivo del modelo.
        description (str): Explicación opcional sobre el propósito del modelo.
        created_at (datetime): Fecha y hora de creación del registro.
        updated_at (datetime): Fecha y hora de última actualización.
    """
    name  = models.CharField(max_length=100)
    version = models.CharField(max_length=50)
    file = models.FileField(
        upload_to='models/',
        help_text='Carga el archivo .pt, .joblib, .h5'
    )
    framework   = models.CharField(
        max_length=20,
        choices=[
            ('sklearn', 'scikit-learn'),
            ('pytorch', 'PyTorch'),
            ('tensorflow', 'TensorFlow'),
            ('onnx', 'ONNX'),
        ],
    )
    # Solo el superuser (owner) podrá crear/editar estos registros
    owner        = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at   = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        Devuelve una representación legible del modelo como nombre y version,
        útil en interfaces de administración y logs.
        """
        return f"{self.name} v{self.version}"
    
class HyperparameterDefinition(models.Model):
    """
    Define un campo de entrada para un modelo.
    position: orden (1..n) que determina cómo se arma el vector.
    dtype: cómo convertir el string (int, float, str).
    help_text: guía que verá el usuario en el frontend/admin.
    """
    DTYPE_CHOICES = [
        ('int', 'Entero'),
        ('float', 'Decimal'),
        ('str', 'Texto'),
    ]

    model     = models.ForeignKey(MLModel, on_delete=models.CASCADE, related_name='hyperparams')
    position  = models.PositiveIntegerField(help_text='Orden del parámetro (1..n)')
    key_hint  = models.CharField(max_length=100, help_text='Nombre sugerido')
    dtype     = models.CharField(max_length=10, choices=DTYPE_CHOICES, default='int')
    required  = models.BooleanField(default=True)
    help_text = models.CharField(max_length=200, blank=True)

    class Meta:
        unique_together = (('model', 'position'),)
        ordering = ['position']

    def __str__(self):
        return f'{self.model} | #{self.position} ({self.key_hint})'

class AnalysisResult(models.Model):
    """
    Almacena la ejecución y resultados de un análisis
    realizado sobre un dataset con un modelo específico.

    Atributos:
        STATUS_CHOICES (tuple): Estados permitidos para el ciclo de vida.
        dataset (ForeignKey): Enlace al objeto Dataset analizado.
        model (ForeignKey): Enlace al MLModel que procesó los datos.
        parameters (JSONField): Parámetros usados durante el análisis.
        status (str): Estado actual (pending, running, success, failure).
        metrics (JSONField): Resultados cuantitativos del análisis.
        output_path (str): Ruta al archivo o recurso generado.
        error_message (str): Mensaje de error en caso de fallo.
        created_at (datetime): Fecha de creación del registro.
        updated_at (datetime): Fecha de última actualización.
    """
    STATUS_CHOICES = [
        ("PENDING", "Pendiente"),
        ("RUNNING", "En ejecución"),
        ("SUCCESS", "Éxito"),
        ("FAILURE", "Fallo"),
    ]

    dataset       = models.ForeignKey("datasets.metadata", on_delete=models.CASCADE)
    model         = models.ForeignKey(MLModel, on_delete=models.CASCADE)
    parameters    = models.JSONField()  # aquí van los hiperparámetros enviados por el usuario
    status        = models.CharField(max_length=10, choices=STATUS_CHOICES, default="PENDING")
    metrics       = models.JSONField(null=True, blank=True)
    output_path   = models.CharField(max_length=255, null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

