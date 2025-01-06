
from django.db import models
from django.utils import timezone

from sistemaapi.models import Partido, Equipo


class Apuesta(models.Model):
    TIPO_APUESTA_CHOICES = [
        (0, 'Ganador'),
        (1, 'Empate'),
    ]

    ESTADO_CHOICES = [
        (0, 'Pendiente'),
        (1, 'Ganador'),
        (2, 'Perdedor'),
        (3, 'Cancelado'),
    ]

    usuario_id = models.IntegerField()
    partido = models.ForeignKey(Partido, on_delete=models.CASCADE)
    tipo_apuesta = models.IntegerField(choices=TIPO_APUESTA_CHOICES)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE)
    estado = models.IntegerField(choices=ESTADO_CHOICES, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    multiplicador = models.DecimalField(max_digits=6, decimal_places=2, default=1.0)

    def __str__(self):
        return f"Apuesta de {self.usuario.username} en {self.partido}"

    def calcular_ganancia(self):
        if self.estado == 1:  # Si la apuesta es ganadora
            return round(self.monto * self.multiplicador, 2)
        return 0.00