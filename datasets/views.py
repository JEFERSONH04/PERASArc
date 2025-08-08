from django.shortcuts import render

# Create your views here.

from django.conf import settings
from rest_framework import mixins, viewsets, permissions
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import MetaData
from .serializadorDataset import DatasetSerializer
from .permissions import IsOwner


class ManualJWTAuthMixin:
    """
    Si DEBUG=True y existe MANUAL_JWT_TOKEN, añade automáticamente
    la cabecera Authorization para las requests entrantes.
    """
    def initial(self, request, *args, **kwargs):
        if settings.DEBUG and getattr(settings, "MANUAL_JWT_TOKEN", None):
            auth_header = f"Bearer {settings.MANUAL_JWT_TOKEN}"
            # Solo inyecta si no hay ya una Authorization en la petición
            request.META.setdefault("HTTP_AUTHORIZATION", auth_header)
        return super().initial(request, *args, **kwargs)

class DatasetViewSet(
    ManualJWTAuthMixin,
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
    authentication_classes = [JWTAuthentication]
    permission_classes     = [permissions.IsAuthenticated, IsOwner]
    serializer_class       = DatasetSerializer

    def get_queryset(self):
        return MetaData.objects.filter(owner=self.request.user)
