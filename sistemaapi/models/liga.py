
from django.db import models

from sistemaapi.models import Deporte
import uuid
import os

def liga_image_upload_path(instance, filename):
    # Extraer la extensión del archivo original
    extension = os.path.splitext(filename)[1]
    # Crear un nombre único basado en un GUID
    new_filename = f"{uuid.uuid4()}{extension}"
    # Definir la ruta de subida
    return f"static/equipos/{new_filename}"

class Liga(models.Model):
    nombre = models.CharField(max_length=255)
    deporte = models.ForeignKey(Deporte, on_delete=models.CASCADE)
    logo = models.ImageField(
        upload_to=liga_image_upload_path,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.nombre