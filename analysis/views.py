from django.shortcuts import render

# Create your views here.

"""
analysis/views.py

Define el ViewSet para exponer endpoints de creación,
listado y detalle de análisis mediante la API REST.
"""

from rest_framework import viewsets, permissions, authentication
from .models import MLModel
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializador import MLModelSerializer
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from .models import AnalysisResult
from .serializador import LaunchAnalysisSerializer, AnalysisResultSerializer
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
        qs = self.queryset.filter(dataset__owner=user).order_by("-created_at")
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = AnalysisResultSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = AnalysisResultSerializer(qs, many=True)
        return Response(serializer.data)

    def retrieve(self, request):
        """
        Recupera un análisis específico asegurando que el usuario
        sea el dueño del dataset subyacente.
        """
        instance = self.get_object()
        if instance.dataset.owner != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)

        serializer = AnalysisResultSerializer(instance)
        return Response(serializer.data)


class MLModelViewSet(viewsets.ModelViewSet):
    queryset = MLModel.objects.all()
    authentication_classes = [
        authentication.SessionAuthentication,
        # Si usas tokens o JWT, añádelos aquí:
        authentication.TokenAuthentication,
        JWTAuthentication,
    ]
    permission_classes     = [permissions.IsAdminUser]
    serializer_class       = MLModelSerializer

