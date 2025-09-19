from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MLModelViewSet, AnalysisViewSet, ResultController

router_models = DefaultRouter()
router_models.register(r"models", MLModelViewSet,  basename="mlmodel")

router_analysis = DefaultRouter()
router_analysis.register(r"analysis", AnalysisViewSet,  basename="analysis")

router_results = DefaultRouter()
router_results.register(r'results', ResultController, basename='results')




urlpatterns = [
    path("", include(router_models.urls)),
    path("", include(router_analysis.urls)),
    path("", include(router_results.urls)),

]

