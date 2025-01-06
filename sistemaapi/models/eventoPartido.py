
from django.db import models

from sistemaapi.models import Partido, Equipo


class EventoPartido(models.Model):
    partido = models.ForeignKey(Partido, on_delete=models.CASCADE)
    descripcion = models.CharField(max_length=255)
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE)
    minuto = models.IntegerField()

    def __str__(self):
        return f"{self.descripcion} - {self.partido}"