from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    EspecialidadeViewSet, 
    EspecialistaViewSet, 
    PacienteViewSet, 
    AgendaViewSet, 
    HorarioGeradoViewSet, 
    ConsultaViewSet
)

router = DefaultRouter()

router.register(r'especialidades', EspecialidadeViewSet)
router.register(r'especialistas', EspecialistaViewSet)
router.register(r'pacientes', PacienteViewSet)
router.register(r'agendas', AgendaViewSet)
router.register(r'horarios', HorarioGeradoViewSet)
router.register(r'consultas', ConsultaViewSet)

urlpatterns = [
    path('', include(router.urls)),
]