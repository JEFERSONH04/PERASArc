from django.shortcuts import render

# Create your views here.

from django.conf import settings
from rest_framework import mixins, viewsets, permissions, authentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import MetaData
from .serializadorDataset import DatasetSerializer
from .permissions import IsOwner




class DatasetViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    """
    Provee endpoints para:
      - list:   listar datasets propios.
      - create: subir nuevos datasets.
      - retrieve: ver detalles si es owner.
      - update/partial_update: modificar atributos propios.
      - destroy: eliminar dataset propio.
    """
    authentication_classes = [
        authentication.SessionAuthentication,
        authentication.BasicAuthentication,
        # Si usas tokens o JWT, añádelos aquí:
        authentication.TokenAuthentication,
        JWTAuthentication,
    ]
    permission_classes     = [permissions.IsAuthenticated, IsOwner]
    serializer_class       = DatasetSerializer

    def get_queryset(self):
        return MetaData.objects.filter(owner=self.request.user)
    
    

