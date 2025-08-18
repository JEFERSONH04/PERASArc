from django.db import models

# Create your models here.

from django.db import models
from django.conf import settings
from datasets.models import MetaData

class PreprocessingJob(models.Model):
    """
    Registra un trabajo de preprocesamiento de un Dataset.
    
    Atributos:
      - dataset: referencia al Dataset original.
      - owner: usuario que lanza el job (mismo que dataset.owner).
      - status: ciclo de vida del job (PENDING → RUNNING → SUCCESS/FAILED).
      - created_at: timestamp de creación en base de datos.
      - started_at: marca cuando el worker comienza a ejecutarlo.
      - finished_at: marca cuando finaliza (éxito o fallo).
      - log: detalle de pasos, advertencias y errores.
      - result_file: (opcional) CSV/JSON con el dataset procesado.
      - error_message: mensaje breve si falla el proceso.
    """

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pendiente'
        RUNNING = 'RUNNING', 'En ejecución'
        SUCCESS = 'SUCCESS', 'Completado'
        FAILED  = 'FAILED',  'Fallido'

    dataset       = models.ForeignKey(
        MetaData,
        on_delete=models.CASCADE,
        related_name='preprocessing_jobs'
    )
    owner         = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='preprocessing_jobs'
    )
    status        = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING
    )
    created_at    = models.DateTimeField(auto_now_add=True)
    started_at    = models.DateTimeField(null=True, blank=True)
    finished_at   = models.DateTimeField(null=True, blank=True)
    log           = models.TextField(blank=True)
    result_file   = models.FileField(
        upload_to='preprocessed/',
        null=True,
        blank=True
    )
    error_message = models.TextField(blank=True)

    def __str__(self):
        return f"Job {self.id} [{self.status}] para Dataset {self.dataset.id}"

