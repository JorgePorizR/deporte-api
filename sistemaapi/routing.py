# routing.py

from django.urls import re_path
from .consumers import PartidoConsumer

websocket_urlpatterns = [
    re_path('ws/partidos/', PartidoConsumer.as_asgi()),
]
