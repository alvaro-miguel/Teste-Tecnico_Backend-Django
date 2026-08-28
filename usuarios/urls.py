

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EspecialistaViewSet, MeuPerfilView, PacienteViewSet

router = DefaultRouter()
router.register(r'especialistas', EspecialistaViewSet)
router.register(r'pacientes', PacienteViewSet)

urlpatterns = [
    path('me/', MeuPerfilView.as_view(), name='meu-perfil'),
    path('', include(router.urls)),
]
