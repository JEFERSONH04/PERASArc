from django.shortcuts import render

# Create your views here.

from rest_framework import viewsets, authentication, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from preprocessing.models import PreprocessingJob
from preprocessing.serializador import PreprocessingJobSerializer
from preprocessing.task import process_preprocessing_job

class PreprocessingJobViewSet(viewsets.ModelViewSet):
    queryset = PreprocessingJob.objects.all()
    serializer_class = PreprocessingJobSerializer
    permission_classes = [IsAuthenticated]

        # Incluye la autenticación por sesión
    authentication_classes = [
        authentication.SessionAuthentication,
        authentication.BasicAuthentication,
        # Si usas tokens o JWT, añádelos aquí:
        authentication.TokenAuthentication,
        JWTAuthentication,
    ]
    permission_classes = [
        permissions.IsAuthenticated,      # solo usuarios logueados
        # o combina: DjangoModelPermissions, IsAdminUser, etc.
    ]

    def get_queryset(self):
        return self.queryset.filter(owner=self.request.user)

    def perform_create(self, serializer):
        job = serializer.save(owner=self.request.user)
        process_preprocessing_job.delay(job.id)


