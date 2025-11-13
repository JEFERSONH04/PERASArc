from rest_framework import serializers
from django.core.validators import FileExtensionValidator
from .models import MetaData
from rest_framework.response import Response
from asgiref.sync import async_to_sync

class DatasetSerializer(serializers.ModelSerializer):
    """
    Serializador para crear, listar y validar datasets.

    - owner: solo lectura; muestra el email del dueño.
    - file: comprueba extensión (.csv/.json) y tamaño ≤ 10 MB.
    - create(): asocia automáticamente request.user como owner.
    """
    # Sólo lectura: mostramos el email del owner, no puede modificarse desde la API
    owner = serializers.ReadOnlyField(source='owner.email')

        # Aplicamos FileExtensionValidator para CSV y JSON
    file = serializers.FileField(
        validators=[FileExtensionValidator(allowed_extensions=['csv', 'json'])]
    )

    class Meta:
        model = MetaData
        fields = [
            'id',
            'name',
            'description',
            'file',
            'owner',
            'created_at',
        ]
        read_only_fields = [
            'id',
            'owner',
            'created_at',
        ]
        extra_kwargs = {
            'file': {
                'validators': [
                    FileExtensionValidator(allowed_extensions=['csv', 'json'])
                ]
            }
        }

    def validate_name(self, value):
        """
        - No puede estar vacío ni sólo espacios.
        - Máximo 100 caracteres.
        """
        if not value.strip():
            raise serializers.ValidationError("El nombre no puede estar vacío.")
        if len(value) > 100:
            raise serializers.ValidationError("El nombre no puede exceder 100 caracteres.")
        return value

    def validate_description(self, value):
        """
        - Máximo 500 caracteres (ajusta según tu necesidad).
        """
        if len(value) > 500:
            raise serializers.ValidationError("La descripción no puede exceder 500 caracteres.")
        return value

    def validate(self, attrs):
        """
        Validación cruzada para el archivo:
        - Tamaño máximo 10 MB.
        """
        file_obj = attrs.get('file')
        max_size_mb = 150
        if file_obj.size > max_size_mb * 1024 * 1024:
            raise serializers.ValidationError(
                f"El archivo no puede superar {max_size_mb} MB."
            )
        return attrs

    def create(self, validated_data):
        """
        Asociar automáticamente el dataset al usuario autenticado.
        """
        user = self.context['request'].user
        return MetaData.objects.create(owner=user, **validated_data)
    


