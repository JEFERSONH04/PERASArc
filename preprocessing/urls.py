from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PreprocessingJobViewSet

router = DefaultRouter()
router.register(
    prefix='preprocessing-jobs', 
    viewset=PreprocessingJobViewSet, 
    basename='preprocessingjob'
)

urlpatterns = [
    path('', include(router.urls)),
]
