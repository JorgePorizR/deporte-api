from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class BetListView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):

        # Acceder a los datos del token en el request
        user_id = request.user_id
        username = request.username
        email = request.email
        groups = request.groups

        # Verificar si el usuario tiene el grupo "administrador de partidos"
        if "administrador de partidos" not in groups:
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Si el usuario pertenece al grupo "administrador de partidos", retornar la respuesta esperada
        return Response({
            "user_id": user_id,
            "username": username,
            "email": email,
            "groups": groups
        })
