
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from sistemaapi.api.serializers import LigaSerializer, PartidoSerializer
from sistemaapi.models import Liga, Partido

class LigaViewSet(viewsets.ModelViewSet):
    queryset = Liga.objects.all()
    serializer_class = LigaSerializer

    def check_admin_partido(self, groups):
        if "administrador de partidos" not in groups:
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN
            )
        return None

    def check_client(self, groups):
        if "cliente" not in groups:
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


    # Nuevo endpoint para obtener ligas por deporte con sus partidos asociados
    @action(detail=False, methods=['get'], url_path='deporte/(?P<deporte_id>\d+)')
    def listar_ligas_por_deporte(self, request, deporte_id=None):
        response = self.check_client(request.groups)
        if response:
            return response

        try:
            # Filtrar ligas por el id del deporte
            ligas = Liga.objects.filter(deporte_id=deporte_id)

            # Obtener la fecha y hora actual
            now = timezone.now()

            # Serializar las ligas y sus partidos asociados
            data = []
            for liga in ligas:
                partidos = Partido.objects.filter(liga=liga, fecha_hora__gte=now).order_by('fecha_hora')
                liga_data = LigaSerializer(liga).data
                liga_data['partidos'] = PartidoSerializer(partidos, many=True).data
                data.append(liga_data)

            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"detail": f"Error retrieving data: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )