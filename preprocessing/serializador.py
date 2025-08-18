# preprocessing/serializers.py

from rest_framework import serializers
from django.contrib.auth import get_user_model

from preprocessing.models import PreprocessingJob
from datasets.models import MetaData

User = get_user_model()

class PreprocessingJobSerializer(serializers.ModelSerializer):
    """
    Serializador para PreprocessingJob.

    - dataset: permite pasar solo el ID del Dataset; valida que el usuario
      autenticado sea el propietario de ese Dataset.
    - owner: solo lectura, muestra el email del usuario que creó el job.
    - status, timestamps, log, result_file y error_message son de solo lectura.
    """
    dataset = serializers.PrimaryKeyRelatedField(

        queryset=MetaData.objects.all(),
        help_text="ID del Dataset a preprocesar"
    )
    owner = serializers.ReadOnlyField(source='owner.email')

    class Meta:
        model = PreprocessingJob
        fields = [
            'id',
            'dataset',
            'owner',
            'status',
            'created_at',
            'started_at',
            'finished_at',
            'log',
            'result_file',
            'error_message',
        ]
        read_only_fields = [
            'id',
            'owner',
            'status',
            'created_at',
            'started_at',
            'finished_at',
            'log',
            'result_file',
            'error_message',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Sacamos el request del contexto que pasa la ViewSet automáticamente
        request = self.context.get("request", None)
        if request and request.user and request.user.is_authenticated:
            # Solo mostramos datasets cuyo owner es el user actual
            self.fields["dataset"].queryset = MetaData.objects.filter(
                owner=request.user
            )
