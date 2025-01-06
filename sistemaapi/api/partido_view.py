from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
import requests

from sistemaapi.api.serializers import PartidoSerializer, EventoPartidoSerializer
from sistemaapi.models import Partido, Apuesta, EventoPartido, Equipo


class PartidoViewSet(viewsets.ModelViewSet):
    queryset = Partido.objects.all()
    serializer_class = PartidoSerializer

    def check_admin_partido(self, groups):
        print(groups)
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

    @action(detail=True, methods=['get'], url_path='multiplicadores')
    def obtener_multiplicadores(self, request, pk=None):
        try:
            partido = self.get_object()
            equipo1 = partido.equipo1
            equipo2 = partido.equipo2

            # Contar apuestas por equipo y empate en este partido
            apuestas_equipo1 = Apuesta.objects.filter(partido=partido, equipo=equipo1, tipo_apuesta=0).count()
            apuestas_equipo2 = Apuesta.objects.filter(partido=partido, equipo=equipo2, tipo_apuesta=0).count()
            apuestas_empate = Apuesta.objects.filter(partido=partido, tipo_apuesta=1).count()

            total_apuestas = apuestas_equipo1 + apuestas_equipo2 + apuestas_empate

            # Evitar divisiones por cero
            if total_apuestas == 0:
                multiplicador_equipo1 = 1.5
                multiplicador_equipo2 = 1.5
                multiplicador_empate = 3.0
            else:
                # Ejemplo de lógica para calcular multiplicadores (ajustar según tu criterio)
                multiplicador_equipo1 = round(1 + (total_apuestas / (apuestas_equipo1 + 1)), 2)
                multiplicador_equipo2 = round(1 + (total_apuestas / (apuestas_equipo2 + 1)), 2)
                multiplicador_empate = round(1 + (total_apuestas / (apuestas_empate + 1)), 2)

            return Response({
                "partido": f"{equipo1.nombre} vs {equipo2.nombre}",
                "multiplicadores": {
                    "equipo1": multiplicador_equipo1,
                    "equipo2": multiplicador_equipo2,
                    "Empate": multiplicador_empate
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], url_path='eventos')
    def obtener_partido_con_eventos(self, request, pk=None):

        try:
            # Obtener el partido por su ID
            partido = self.get_object()

            # Filtrar los eventos asociados al partido
            eventos = EventoPartido.objects.filter(partido=partido)

            # Serializar el partido y sus eventos
            partido_data = PartidoSerializer(partido).data
            partido_data['eventos'] = EventoPartidoSerializer(eventos, many=True).data

            return Response(partido_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"detail": f"Error retrieving data: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['patch'], url_path='iniciar')
    def iniciar_partido(self, request, pk=None):
        response = self.check_admin_partido(request.groups)
        if response:
            return response
        try:
            # Obtener el partido por su ID
            partido = self.get_object()

            # Cambiar el estado a "En Juego"
            partido.estado = 1  # 1 representa "En Juego"
            partido.save()

            # Emitir mensaje por WebSocket
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                'partidos',
                {
                    'type': 'send_notification',
                    'message': f"Marcadores actualizados: {str(partido)}"
                }
            )

            # Serializar el partido actualizado
            serializer = self.get_serializer(partido)

            return Response({
                "detail": f"El estado del partido '{partido}' se ha cambiado a 'En Juego'.",
                "partido": serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"detail": f"Error al cambiar el estado del partido: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['patch'], url_path='finalizar')
    def finalizar_partido(self, request, pk=None):
        response = self.check_admin_partido(request.groups)
        if response:
            return response

        try:
            # Obtener el partido por su ID
            partido = self.get_object()

            # Cambiar el estado del partido a "Finalizado"
            partido.estado = 2  # 2 representa "Finalizado"
            partido.save()

            # URL del endpoint de IngresoMovimiento en tu API de recarga
            ingreso_movimiento_url = "http://localhost:5286/api/Movimientos/Ingreso"

            apuestas_ganadoras = []
            apuestas_perdedoras = []
            # Buscar las apuestas ganadoras en función del resultado
            if partido.marcador1 > partido.marcador2:
                # Gana equipo1
                apuestas_ganadoras = Apuesta.objects.filter(partido=partido, equipo=partido.equipo1, tipo_apuesta=0)
                apuestas_perdedoras += Apuesta.objects.filter(partido=partido, equipo=partido.equipo2, tipo_apuesta=0)
                apuestas_perdedoras += Apuesta.objects.filter(partido=partido, tipo_apuesta=1)
            elif partido.marcador2 > partido.marcador1:
                # Gana equipo2
                apuestas_ganadoras = Apuesta.objects.filter(partido=partido, equipo=partido.equipo2, tipo_apuesta=0)
                apuestas_perdedoras += Apuesta.objects.filter(partido=partido, equipo=partido.equipo1, tipo_apuesta=0)
                apuestas_perdedoras += Apuesta.objects.filter(partido=partido, tipo_apuesta=1)
            elif partido.marcador1 == partido.marcador2:
                # Empate
                apuestas_ganadoras = Apuesta.objects.filter(partido=partido, tipo_apuesta=1)
                apuestas_perdedoras += Apuesta.objects.filter(partido=partido, tipo_apuesta=0)

            # Procesar las apuestas perdedoras
            for apuesta in apuestas_perdedoras:

                # Actualizar el estado de las apuestas perdedoras
                apuesta.estado = 2 # 2 representa "Perdedor"
                apuesta.save()

            # Procesar las apuestas ganadoras y crear los movimientos
            for apuesta in apuestas_ganadoras:

                # Actualizar el estado de las apuesta
                apuesta.estado = 1  # 1 representa "Ganador"
                apuesta.save()

                # Calcular la ganancia aplicando el multiplicador
                ganancia = float(apuesta.monto) * float(apuesta.multiplicador)

                # Crear el movimiento para el usuario
                movimiento_data = {
                    "tipo": 1,  # 1 representa Ingreso
                    "monto": ganancia,
                    "userId": apuesta.usuario_id,
                    "comprobante": "",
                    "descripcion": f"Ganancia por apuesta en el partido {partido}"
                }

                # Hacer la solicitud al endpoint de IngresoMovimiento
                try:
                    response = requests.post(
                        ingreso_movimiento_url,
                        json=movimiento_data,
                        headers={"Authorization": f"Bearer {request.token}"}
                    )
                    response.raise_for_status()  # Lanzar una excepción si la solicitud falla
                except requests.RequestException as e:
                    return Response(
                        {"detail": f"Error al crear el movimiento para la apuesta {apuesta.id}: {str(e)}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            # Emitir mensaje por WebSocket
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                'partidos',
                {
                    'type': 'send_notification',
                    'message': f"Marcadores actualizados: {str(partido)}"
                }
            )

            # Serializar el partido actualizado
            serializer = self.get_serializer(partido)

            return Response({
                "detail": f"El estado del partido '{partido}' se ha cambiado a 'Finalizado'. Se han procesado las apuestas ganadoras.",
                "partido": serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"detail": f"Error al finalizar el partido: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['patch'], url_path='cancelar')
    def cancelar_partido(self, request, pk=None):
        response = self.check_admin_partido(request.groups)
        if response:
            return response

        try:
            # Obtener el partido por su ID
            partido = self.get_object()

            # Cambiar el estado a "Cancelado"
            partido.estado = 3  # 3 representa "Cancelado"
            partido.save()

            # Buscar todas las apuestas asociadas al partido
            apuestas = Apuesta.objects.filter(partido=partido)

            for apuesta in apuestas:
                # Actualizar el estado de la apuesta a "Cancelado"
                apuesta.estado = 3  # 3 representa "Cancelado"
                apuesta.save()

                # Crear el movimiento para devolver el monto apostado
                movimiento_data = {
                    "tipo": 1,  # 1 representa Ingreso
                    "monto": float(apuesta.monto),
                    "userId": apuesta.usuario_id,
                    "comprobante": "",
                    "descripcion": f"Devolución de apuesta cancelada para el partido {partido}"
                }

                # Llamar al endpoint de IngresoMovimiento
                try:
                    response = requests.post(
                        "http://localhost:5286/api/Movimientos/Ingreso",
                        json=movimiento_data,
                        headers={"Authorization": f"Bearer {request.token}"}
                    )
                    response.raise_for_status()  # Lanzar una excepción si la solicitud falla
                except requests.RequestException as e:
                    return Response(
                        {"detail": f"Error al crear el movimiento: {str(e)}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # Emitir mensaje por WebSocket
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                'partidos',
                {
                    'type': 'send_notification',
                    'message': f"Marcadores actualizados: {str(partido)}"
                }
            )
            # Serializar el partido actualizado
            serializer = self.get_serializer(partido)

            return Response({
                "detail": f"El estado del partido '{partido}' se ha cambiado a 'Cancelado'. Se ha devuelto el monto de las apuestas.",
                "partido": serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"detail": f"Error al cambiar el estado del partido: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['patch'], url_path='actualizar-marcadores')
    def actualizar_marcadores(self, request, pk=None):
        response = self.check_admin_partido(request.groups)
        if response:
            return response
        try:
            # Obtener el partido por su ID
            partido = self.get_object()

            # Obtener los nuevos valores de los marcadores desde el cuerpo de la solicitud
            marcador1 = request.data.get('marcador1')
            marcador2 = request.data.get('marcador2')

            # Validar que los marcadores sean números enteros no negativos
            if marcador1 is None or marcador2 is None:
                return Response(
                    {"detail": "Se requieren 'marcador1' y 'marcador2'."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                marcador1 = int(marcador1)
                marcador2 = int(marcador2)

                if marcador1 < 0 or marcador2 < 0:
                    return Response(
                        {"detail": "Los marcadores no pueden ser negativos."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            except ValueError:
                return Response(
                    {"detail": "Los marcadores deben ser números enteros."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Actualizar los marcadores
            partido.marcador1 = marcador1
            partido.marcador2 = marcador2
            partido.save()

            # Emitir mensaje por WebSocket
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                'partidos',
                {
                    'type': 'send_notification',
                    'message': f"Marcadores actualizados: {str(partido)}"
                }
            )

            # Serializar el partido actualizado
            serializer = self.get_serializer(partido)

            return Response({
                "detail": f"Los marcadores del partido '{partido}' se han actualizado.",
                "partido": serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"detail": f"Error al actualizar los marcadores: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'], url_path='agregar-evento')
    def agregar_evento(self, request, pk=None):
        response = self.check_admin_partido(request.groups)
        if response:
            return response
        try:
            # Obtener el partido por su ID
            partido = self.get_object()

            # Extraer los datos del evento del request
            descripcion = request.data.get('descripcion')
            equipo_id = request.data.get('equipo_id')
            minuto = request.data.get('minuto')

            # Validar que los datos necesarios están presentes
            if not descripcion or not equipo_id or minuto is None:
                return Response(
                    {"detail": "Los campos 'descripcion', 'equipo_id' y 'minuto' son obligatorios."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validar que el equipo existe
            try:
                equipo = Equipo.objects.get(id=equipo_id)
            except Equipo.DoesNotExist:
                return Response(
                    {"detail": f"No existe un equipo con el ID {equipo_id}."},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Crear el nuevo evento
            evento = EventoPartido.objects.create(
                partido=partido,
                descripcion=descripcion,
                equipo=equipo,
                minuto=minuto
            )

            # Emitir mensaje por WebSocket
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                'partidos',
                {
                    'type': 'send_notification',
                    'message': f"Marcadores actualizados: {str(partido)}"
                }
            )

            # Serializar el evento creado
            serializer = EventoPartidoSerializer(evento)

            return Response({
                "detail": f"Se ha agregado el evento '{descripcion}' al partido '{partido}'.",
                "evento": serializer.data
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {"detail": f"Error al agregar el evento: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )