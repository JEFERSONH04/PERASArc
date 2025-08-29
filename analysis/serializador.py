"""
analysis/serializers.py

Define serializers para iniciar un análisis y para exponer
sus resultados a través de la API REST.
"""
import json
from rest_framework import serializers
from .models import AnalysisResult, HyperparameterDefinition, MLModel
from datasets.models import MetaData

class MLModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = MLModel
        fields = ("id", "name", "version", "file", "framework", "created_at")
        read_only_fields = ("id", "owner", "created_at")

    def create(self, validated_data):
        # El owner se deduce del superuser autenticado
        validated_data["owner"] = self.context["request"].user
        return super().create(validated_data)
    
def parse_value(value: str, dtype: str):
    value = value.strip()
    if dtype == 'int':
        return int(value)
    if dtype == 'float':
        return float(value.replace(',', '.'))
    return value  # str


class LaunchAnalysisSerializer(serializers.ModelSerializer):
    dataset = serializers.PrimaryKeyRelatedField(
        queryset=MetaData.objects.none()
    )
    model = serializers.PrimaryKeyRelatedField(
        queryset=MLModel.objects.all()
    )

    class Meta:
        model  = AnalysisResult
        # Sólo los campos del modelo; los param_i se inyectan dinámicamente
        fields = ('dataset', 'model')

    def get_fields(self):
        """
        Añade dataset, model y luego todos los campos param_{position}
        que defina el superusuario para ese modelo.
        """
        fields = super().get_fields()

        # limitar datasets al owner
        user = self.context['request'].user
        if user.is_authenticated:
            fields['dataset'].queryset = MetaData.objects.filter(owner=user)

        # detecta si viene model en GET o en POST
        request = self.context['request']
        model_id = (
            request.query_params.get('model') or
            getattr(self, 'initial_data', {}).get('model')
        )
        if model_id:
            try:
                mlm = MLModel.objects.get(pk=model_id)
            except MLModel.DoesNotExist:
                mlm = None

            if mlm:
                for hp in mlm.hyperparams.all().order_by('position'):
                    fields[f'param_{hp.position}'] = serializers.CharField(
                        required=hp.required,
                        help_text=hp.help_text or hp.key_hint,
                        label=f"{hp.position}. {hp.key_hint}"
                    )

        return fields

    def to_internal_value(self, data):
        """
        Primero valida dataset y model, luego deja pasar param_i crudos.
        """
        return super().to_internal_value(data)

    def create(self, validated_data):
        """
        1. Saca de validated_data todos los param_i.
        2. Parsealos según su dtype.
        3. Construye parameters={'raw':..., 'vector_2d':[...]}
        4. Crea el AnalysisResult sin los param_i.
        """
        mlm = validated_data['model']
        defs = list(mlm.hyperparams.all().order_by('position'))

        raw_inputs = {}
        parsed_row = []

        # 1) Extraer y parsear cada param_i
        for hp in defs:
            key = f'param_{hp.position}'
            raw_value = validated_data.pop(key, '').strip()
            if hp.required and raw_value == '':
                raise serializers.ValidationError({key: 'Este campo es obligatorio.'})
            raw_inputs[key] = raw_value

            # parseo según dtype
            if hp.dtype == 'int':
                try:
                    val = int(raw_value)
                except ValueError:
                    raise serializers.ValidationError({key: 'Debe ser un entero.'})
            elif hp.dtype == 'float':
                try:
                    val = float(raw_value.replace(',', '.'))
                except ValueError:
                    raise serializers.ValidationError({key: 'Debe ser un número decimal.'})
            else:  # 'str'
                val = raw_value

            parsed_row.append(val)

        # 2) Montar el campo 'parameters'
        parameters = {
            "vector_2d": [parsed_row],
        }

        # 3) Quitar status si lo definiste en serializer.save()
        status = validated_data.pop('status', 'PENDING')

        # 4) Crear el registro sin param_i
        analysis = AnalysisResult.objects.create(
            dataset=   validated_data['dataset'],
            model=     validated_data['model'],
            parameters=parameters,
            status=    'PENDING'
        )
        return analysis



    
class AnalysisResultSerializer(serializers.ModelSerializer):
    """
    Serializador para listar o detalle de AnalysisResult.
    Todos los campos son de solo lectura para proteger
    la integridad de los resultados.
    """
    dataset = serializers.PrimaryKeyRelatedField(read_only=True)
    model   = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = AnalysisResult
        fields = (
            "id",
            "dataset",
            "model",
            "parameters",
            "status",
            "metrics",
            "output_path",
            "error_message",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "dataset",
            "model",
            "parameters",
            "status",
            "metrics",
            "output_path",
            "error_message",
            "created_at",
            "updated_at",
        )

    