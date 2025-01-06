
from rest_framework import viewsets, status
from rest_framework.response import Response

from sistemaapi.api.serializers import DeporteSerializer
from sistemaapi.models import Deporte

class DeporteViewSet(viewsets.ModelViewSet):
    queryset = Deporte.objects.all()
    serializer_class = DeporteSerializer

    def check_admin_partido(self, groups):
        if "administrador de partidos" not in groups:
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN
            )
        return None

    def list(self, request, *args, **kwargs):

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