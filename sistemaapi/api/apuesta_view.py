
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from django.db.models import Sum

from sistemaapi.api.serializers import ApuestaSerializer
from sistemaapi.models import Apuesta, Equipo, Partido
import requests



class ApuestaViewSet(viewsets.ModelViewSet):
    queryset = Apuesta.objects.all()
    serializer_class = ApuestaSerializer


    def check_admin_partido(self, groups):
        if "administrador de partidos" not in groups:
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN
            )
        return None

    def list(self, request, *args, **kwargs):

        #response = self.check_admin_partido(request.groups)
        #if response:
            #return response

        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):

        response = self.check_admin_partido(request.groups)
        if response:
            return response

        return super().retrieve(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):

        partido_id = request.data.get("partido_id")
        partido = Partido.objects.get(id=partido_id)
        if partido.estado != 0:
            raise ValidationError({"detail": "No se puede apostar en un partido que no está pendiente."})

        # Crear la apuesta
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        apuesta = serializer.instance

        # Datos del movimiento a enviar
        movimiento_data = {
            "tipo": 0,
            "monto": float(apuesta.monto),
            "userId": apuesta.usuario_id,
            "comprobante": "",
            "descripcion": f"Apuesta creada para el partido {apuesta.partido.__str__()} por el equipo {apuesta.equipo.nombre}",
        }

        try:
            # Hacer la solicitud POST al endpoint de movimientos
            response = requests.post(
                "http://localhost:5286/api/Movimientos/Salida",
                json=movimiento_data,
                headers={"Authorization": f"Bearer {request.token}"}
            )
            response.raise_for_status()  # Lanza una excepción si la solicitud no fue exitosa

        except requests.exceptions.RequestException as e:
            # Si falla la creación del movimiento, eliminar la apuesta para evitar inconsistencias
            apuesta.delete()
            return Response(
                {"detail": f"Error al crear el movimiento: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Devolver la respuesta con los datos de la apuesta creada
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        serializer.save()

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

    # Obtener el historial de apuestas de un usuario
    @action(detail=False, methods=['get'], url_path='historial/(?P<usuario_id>\\d+)')
    def historial_usuario(self, request, usuario_id=None):
        # Filtrar apuestas por el ID del usuario
        apuestas = Apuesta.objects.filter(usuario_id=usuario_id).order_by('-created_at')

        if not apuestas.exists():
            return Response(
                {"detail": f"No hay historial de apuestas para el usuario con ID {usuario_id}."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Serializar las apuestas y devolver la respuesta
        serializer = self.get_serializer(apuestas, many=True)
        return Response(serializer.data)

    #  Ver el monto total ganado o perdido para un partido
    @action(detail=False, methods=['get'], url_path='monto-total/(?P<partido_id>\\d+)/partido')
    def monto_total_partido(self, request, partido_id=None):
        response = self.check_admin_partido(request.groups)
        if response:
            return response
        # Filtrar las apuestas por el ID del partido
        apuestas = Apuesta.objects.filter(partido_id=partido_id)

        if not apuestas.exists():
            return Response(
                {"detail": f"No hay apuestas registradas para el partido con ID {partido_id}."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Calcular el monto total de las apuestas ganadas
        total_ganado = apuestas.filter(estado=1).aggregate(total=Sum('monto'))['total'] or 0

        # Calcular el monto total de las apuestas perdidas
        total_perdido = apuestas.filter(estado=2).aggregate(total=Sum('monto'))['total'] or 0

        print(total_ganado)
        print(total_perdido)

        return Response({
            "partido_id": partido_id,
            "total_ganado": float(total_ganado),
            "total_perdido": float(total_perdido),
        })

    # Ver el monto total ganado o perdido para un usuario
    @action(detail=False, methods=['get'], url_path='monto-total/(?P<usuario_id>\\d+)/usuario')
    def monto_total_usuario(self, request, usuario_id=None):
        response = self.check_admin_partido(request.groups)
        if response:
            return response
        # Filtrar las apuestas por el ID del usuario
        apuestas = Apuesta.objects.filter(usuario_id=usuario_id)

        if not apuestas.exists():
            return Response(
                {"detail": f"No hay apuestas registradas para el usuario con ID {usuario_id}."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Calcular el monto total de las apuestas ganadas
        total_ganado = apuestas.filter(estado=1).aggregate(total=Sum('monto'))['total'] or 0

        # Calcular el monto total de las apuestas perdidas
        total_perdido = apuestas.filter(estado=2).aggregate(total=Sum('monto'))['total'] or 0

        return Response({
            "usuario_id": usuario_id,
            "total_ganado": float(total_ganado),
            "total_perdido": float(total_perdido),
        })
