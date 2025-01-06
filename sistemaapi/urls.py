from django.urls import path, include
from rest_framework.routers import DefaultRouter

from sistemaapi.api import BetListView, EquipoViewSet, DeporteViewSet, LigaViewSet, PartidoViewSet, \
    EventoPartidoViewSet, ApuestaViewSet

router = DefaultRouter()
router.register(r'equipos', EquipoViewSet, basename='equipos')
router.register(r'deportes', DeporteViewSet, basename='deportes')
router.register(r'ligas', LigaViewSet, basename='ligas')
router.register(r'partidos', PartidoViewSet, basename='partidos')
router.register(r'eventos-partido', EventoPartidoViewSet, basename='eventos-partido')
router.register(r'apuestas', ApuestaViewSet, basename='apuestas')
urlpatterns = [
    path('', include(router.urls)),
    path('bets/', BetListView.as_view(), name='bet-list'),
]
