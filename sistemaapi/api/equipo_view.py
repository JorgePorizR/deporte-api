
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import models

from sistemaapi.api.serializers import EquipoSerializer, PartidoSerializer
from sistemaapi.models import Equipo, Partido


class EquipoViewSet(viewsets.ModelViewSet):
    queryset = Equipo.objects.all()
    serializer_class = EquipoSerializer

    def check_admin_partido(self, groups):
        if "administrador de partidos" not in groups:
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN
            )
        return None

    def list(self, request, *args, **kwargs):

        response = self.check_admin_partido(request.groups)
        if response:
            return response

        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):

        response = self.check_admin_partido(request.groups)
        if response:
            return response

        return super().retrieve(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):

        response = self.check_admin_partido(request.groups)
        if response:
            return response

        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):

        response = self.check_admin_partido(request.groups)
        if response:
            return response

        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):

        response = self.check_admin_partido(request.groups)
        if response:
            return response

        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):

        response = self.check_admin_partido(request.groups)
        if response:
            return response

        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['get'], url_path='partidos')
    def obtener_partidos_por_equipo(self, request, pk=None):

        try:
            # Obtener el equipo por su ID
            equipo = self.get_object()

            # Obtener la fecha y hora actual
            now = timezone.now()

            # Filtrar partidos donde el equipo es equipo1 o equipo2
            partidos_pasados = Partido.objects.filter(
                (models.Q(equipo1=equipo) | models.Q(equipo2=equipo)),
                fecha_hora__lt=now
            ).order_by('-fecha_hora')  # Orden descendente para mostrar los más recientes primero

            partidos_futuros = Partido.objects.filter(
                (models.Q(equipo1=equipo) | models.Q(equipo2=equipo)),
                fecha_hora__gte=now
            ).order_by('fecha_hora')  # Orden ascendente para mostrar los más cercanos primero

            # Serializar los datos del equipo y los partidos
            equipo_data = EquipoSerializer(equipo).data
            equipo_data['partidos_pasados'] = PartidoSerializer(partidos_pasados, many=True).data
            equipo_data['partidos_futuros'] = PartidoSerializer(partidos_futuros, many=True).data

            return Response(equipo_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"detail": f"Error retrieving data: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

