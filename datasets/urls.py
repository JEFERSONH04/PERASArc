from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import DatasetViewSet

router = DefaultRouter()
router.register(r'datasets', DatasetViewSet, basename='dataset')

urlpatterns = [
    # /api/v1/datasets/  → list, create
    # /api/v1/datasets/{id}/ → retrieve, update, destroy
    path('', include(router.urls)),
]
