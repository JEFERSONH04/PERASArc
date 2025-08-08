from rest_framework import permissions

class IsOwner(permissions.BasePermission):
    """
    Permite acceso a un objeto solo si request.user es su owner.
    """

    def has_object_permission(self, request, view, obj):
        """
        Permite acciones CRUD solo al propietario del dataset.
        """
        # Sólo el owner puede ver, actualizar o borrar el dataset
        return obj.owner == request.user
