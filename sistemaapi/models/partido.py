
from django.db import models

from sistemaapi.models import Equipo, Liga


class Partido(models.Model):
    ESTADO_CHOICES = [
        (0, 'Pendiente'),
        (1, 'En Juego'),
        (2, 'Finalizado'),
        (3, 'Cancelado'),
    ]

    equipo1 = models.ForeignKey(Equipo, related_name='partidos_equipo1', on_delete=models.CASCADE)
    equipo2 = models.ForeignKey(Equipo, related_name='partidos_equipo2', on_delete=models.CASCADE)
    liga = models.ForeignKey(Liga, on_delete=models.CASCADE)
    marcador1 = models.IntegerField(default=0)
    marcador2 = models.IntegerField(default=0)
    fecha_hora = models.DateTimeField()
    duracion_minutos = models.IntegerField()
    estado = models.IntegerField(choices=ESTADO_CHOICES, default=0)

    def __str__(self):
        return f"{self.equipo1.nombre} vs {self.equipo2.nombre}"