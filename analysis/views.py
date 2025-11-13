from django.shortcuts import render

# Create your views here.

"""
analysis/views.py

Define el ViewSet para exponer endpoints de creación,
listado y detalle de análisis mediante la API REST.
"""
from django.conf import settings
import json
import os
from django.http import FileResponse, Http404, HttpResponse
from rest_framework import viewsets, permissions, authentication, mixins, generics
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView
from django_filters.rest_framework import DjangoFilterBackend
from .models import MLModel, HyperparameterDefinition
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializador import MLModelSerializer
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from .models import AnalysisResult, UserAnalysis, MapeoResultado
from .serializador import LaunchAnalysisSerializer, AnalysisResultSerializer, HyperparameterSerializer, UserAnalysisSerializer
from .filtros import AnalysisResultFilter
from .reportes import SimpleReportGenerator
from datasets.permissions import IsOwner
from .tasks import launch_analysis_task

class AnalysisViewSet(viewsets.GenericViewSet):
    """
    ViewSet genérico que delega en serializers diferentes
    según la acción: creación vs. consulta de resultados.
    """
    queryset = AnalysisResult.objects.all()
    authentication_classes = [
        authentication.SessionAuthentication,
        authentication.BasicAuthentication,
        authentication.TokenAuthentication,
        JWTAuthentication,
    ] 
    permission_classes = [IsAuthenticated]

    """
    Selecciona LaunchAnalysisSerializer para la acción 'create',
    o AnalysisResultSerializer para 'list' y 'retrieve'.
    """
    def get_serializer_class(self):
        if self.action == "create":
            return LaunchAnalysisSerializer
        return AnalysisResultSerializer

    def create(self, request, *arg, **kwargs):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        # Creamos el registro con parámetros enviados
        analysis = serializer.save(status="PENDING")
        # Encolamos la tarea
        print(type(request.data), request.data)
        launch_analysis_task.delay(analysis.id)

        output = AnalysisResultSerializer(analysis).data
        return Response(output, status=status.HTTP_202_ACCEPTED)
      
    def list(self, request):
        """
        Lista todos los análisis del usuario autenticado,
        ordenados por fecha de creación descendente.
        """
        user = request.user
        qs = self.queryset.filter(dataset__owner=user).order_by("-created_at")[:10]
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = AnalysisResultSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = AnalysisResultSerializer(qs, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """
        Recupera un análisis específico asegurando que el usuario
        sea el dueño del dataset subyacente.
        """
        instance = self.get_object()
        if instance.dataset.owner != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)

        serializer = AnalysisResultSerializer(instance)
        return Response(serializer.data)


class ResultController(viewsets.GenericViewSet,
                       mixins.ListModelMixin,
                       mixins.RetrieveModelMixin):
    """
    GET  /api/results/         → Lista con filtros
    GET  /api/results/{id}/    → Recupera un resultado
    GET  /api/results/report/  → Devuelve un informe (CSV/PDF/JSON)
    """
    queryset = AnalysisResult.objects.select_related('model','dataset').all()
    serializer_class = AnalysisResultSerializer
    filter_backends  = [DjangoFilterBackend]
    filterset_class  = AnalysisResultFilter

    @action(detail=False, methods=['get'], url_path='reporte-sencillo')
    def reporte_sencillo(self, request):
        qs  = self.filter_queryset(self.get_queryset())
        gen = SimpleReportGenerator(qs)
        pdf = gen.generate_pdf()
        name = gen.filename()
        resp = HttpResponse(pdf, content_type='application/pdf')
        resp['Content-Disposition'] = f'attachment; filename="{name}"'
        return resp
    
    @action(detail=True, methods=['get'], url_path='download')
    def download(self, request, pk=None):
        """
        GET  /api/results/{id}/download/
        Devuelve el archivo generado en output_path como adjunto.
        """
        analysis = self.get_object()

        # 1) Verificar que exista output_path
        if not analysis.output_path:
            return Response(
                {"detail": "No hay archivo de salida disponible."},
                status=status.HTTP_404_NOT_FOUND
            )

        # 2) Construir ruta absoluta si output_path es relativo
        file_path = analysis.output_path
        if not os.path.isabs(file_path):
            # Asumiendo que usas MEDIA_ROOT para guardar outputs
            file_path = os.path.join(settings.MEDIA_ROOT, file_path)

        # 3) Intentar abrir el fichero
        if not os.path.exists(file_path):
            raise Http404("Archivo de salida no encontrado.")

        file_handle = open(file_path, 'rb')

        # 4) Devolver FileResponse con el nombre original
        filename = os.path.basename(file_path)
        response = FileResponse(file_handle, as_attachment=True, filename=filename)

        # 5) Opcional: ajustar Content-Type si conoces el formato
        # response['Content-Type'] = 'application/json'
        return response



class MLModelViewSet(viewsets.ModelViewSet):
    queryset = MLModel.objects.all()
    authentication_classes = [
        authentication.SessionAuthentication,
        # Si usas tokens o JWT, añádelos aquí:
        authentication.TokenAuthentication,
        JWTAuthentication,
    ]
    permission_classes     = [permissions.IsAuthenticated]
    serializer_class       = MLModelSerializer

class HyperparameterListView(ListAPIView):
    authentication_classes = [
        authentication.SessionAuthentication,
        # Si usas tokens o JWT, añádelos aquí:
        authentication.TokenAuthentication,
        JWTAuthentication,
    ]
    permission_classes     = [permissions.IsAuthenticated]
    serializer_class       = MLModelSerializer
    serializer_class = HyperparameterSerializer

    def get_queryset(self):
        # Get the model_id from the URL kwargs (keyword arguments)
        model_id = self.kwargs['model_id']
        
        # Filter the hyperparameters by the model_id and order them by position
        return HyperparameterDefinition.objects.filter(
            model_id=model_id
        ).order_by('position')
    
class UserAnalysisAPIView(generics.RetrieveAPIView):
    """
    Vista de API que permite a un usuario ver los detalles de un análisis específico,
    leyendo la predicción de un archivo JSON y mapeándola a texto.
    """
    queryset = UserAnalysis.objects.all()
    serializer_class = UserAnalysisSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [
        authentication.SessionAuthentication,
        # Si usas tokens o JWT, añádelos aquí:
        authentication.TokenAuthentication,
        JWTAuthentication,
    ]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        try:
            # 1. Obtiene la instancia de UserAnalysis
            instance = self.get_object()
            analysis_result = instance.analysis
            
            # 2. Lee el archivo JSON del resultado
            file_path = os.path.join(settings.MEDIA_ROOT, analysis_result.output_path)
            
            if not os.path.exists(file_path):
                return Response({"error": "Archivo de resultado no encontrado."}, status=status.HTTP_404_NOT_FOUND)
            
            with open(file_path, 'r') as f:
                resultado_data = json.load(f)

            # 3. Extrae la predicción numérica del JSON. 
            # Asume que la predicción está en una clave 'prediccion' o similar.
            predictions_list = resultado_data 

            # Create a list to hold the mapped text labels
            resultados_mapeados = []

            for pred_num in predictions_list:
                try:
                    # Get the mapping for each number
                    mapeo = MapeoResultado.objects.get(
                        model=analysis_result.model,
                        valor_prediccion=pred_num
                    )
                    # Add the text label to the list
                    resultados_mapeados.append(mapeo.etiqueta_texto)
                except MapeoResultado.DoesNotExist:
                    resultados_mapeados.append("Mapeo no encontrado")
            
            if predictions_list is None:
                return Response({"error": "Formato de archivo de resultado inválido."}, status=status.HTTP_400_BAD_REQUEST)

            # 5. Prepara los datos de la respuesta
            data = {
                "id": instance.id,
                "analysis_id": analysis_result.id,
                "model_name": analysis_result.model.name,
                "status": analysis_result.status,
                "resultado_numerico": predictions_list,
                "resultado_texto": resultados_mapeados,
                "created_at": analysis_result.created_at,
            }
            return Response(data, status=status.HTTP_200_OK)
        
        except UserAnalysis.DoesNotExist:
            return Response({"error": "Análisis no encontrado."}, status=status.HTTP_404_NOT_FOUND)
        except MapeoResultado.DoesNotExist:
            return Response({"error": "Mapeo de resultado no encontrado para esta predicción."}, status=status.HTTP_404_NOT_FOUND)
        except json.JSONDecodeError:
            return Response({"error": "Error al parsear el archivo JSON."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class UserAnalysisListAPIView(generics.ListAPIView):
    """
    Vista de API que lista todos los análisis de un usuario autenticado.
    """
    queryset = UserAnalysis.objects.all()
    serializer_class = UserAnalysisSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [
        authentication.SessionAuthentication,
        # Si usas tokens o JWT, añádelos aquí:
        authentication.TokenAuthentication,
        JWTAuthentication,
    ]

    def get_queryset(self):
        """
        Sobrescribe el queryset para devolver solo los análisis del
        usuario que realiza la solicitud.
        """
        return self.queryset.filter(user=self.request.user).order_by('-analysis__created_at')[:10]

class LastUserAnalysisAPIView(generics.RetrieveAPIView):
    """
    Vista de API que devuelve el último análisis de un usuario autenticado.
    """
    queryset = UserAnalysis.objects.all()
    serializer_class = UserAnalysisSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [
        authentication.SessionAuthentication,
        # Si usas tokens o JWT, añádelos aquí:
        authentication.TokenAuthentication,
        JWTAuthentication,
    ]
    def get_object(self):
        """
        Retorna el último análisis del usuario autenticado.
        Lanza un error 404 si no se encuentra ninguno.
        """
        try:
            # Filtra por el usuario y obtiene el último registro por fecha de creación
            # Se asume que AnalysisResult tiene un campo 'created_at' o similar
            return self.get_queryset().latest('analysis__created_at')
        except UserAnalysis.DoesNotExist:
            raise status.HTTP_404_NOT_FOUND("No se encontró ningún análisis para este usuario.")

    def retrieve(self, request, *args, **kwargs):
        """
        Personaliza la respuesta para mostrar solo el ID del último análisis.
        """
        instance = self.get_object()
        data = {
            "last_analysis_id": instance.pk
        }
        return Response(data, status=status.HTTP_200_OK)

