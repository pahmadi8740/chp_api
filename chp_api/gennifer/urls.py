from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

# Create router and register viewsets
router = DefaultRouter()
router.register(r'datasets', views.DatasetViewSet, basename='dataset')
router.register(r'inference_studies', views.InferenceStudyViewSet, basename='inference_study')
router.register(r'inference_results', views.InferenceResultViewSet, basename='inference_result')

urlpatterns = [
    path('', include(router.urls)),
    path('run', views.run.as_view()),
    ]
