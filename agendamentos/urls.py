from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    EspecialidadeViewSet, 
    AgendaViewSet, 
    HorarioGeradoViewSet, 
    ConsultaViewSet
)

router = DefaultRouter()

router.register(r'especialidades', EspecialidadeViewSet)
router.register(r'agendas', AgendaViewSet)
router.register(r'horarios', HorarioGeradoViewSet)
router.register(r'consultas', ConsultaViewSet)

urlpatterns = [
    path('', include(router.urls)),
]