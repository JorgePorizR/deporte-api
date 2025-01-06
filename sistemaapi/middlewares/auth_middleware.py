import json
import base64
import datetime
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

class JWTAuthCookieMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if 'Authorization' not in request.headers and 'access' in request.COOKIES:
            #request.META['HTTP_AUTHORIZATION'] = f"Bearer {request.COOKIES['access']}"

            token = request.COOKIES.get('access')  # Leer el token JWT desde la cookie 'access'
            print("Token: ", token)
            try:
                # El token JWT está en tres partes: header.payload.signature
                # Primero decodificamos el payload (la segunda parte del token JWT)
                payload = token.split('.')[1]  # Obtener la parte del payload
                decoded_payload = base64.b64decode(payload + '==')  # Decodificar la base64
                decoded_json = json.loads(decoded_payload)  # Convertirlo a JSON

                # Verificar si el token está expirado
                if decoded_json['exp'] < datetime.datetime.now().timestamp():
                    return JsonResponse(
                        {'detail': 'Token has expired', 'code': 'token_expired'},
                        status=401
                    )

                # Extraer los datos del payload
                user_id = decoded_json.get('user_id')
                username = decoded_json.get('username')
                email = decoded_json.get('email')
                groups = decoded_json.get('groups')

                # Guardar los datos del usuario en el request para usarlos más tarde
                request.user_id = user_id
                request.username = username
                request.email = email
                request.groups = groups
                request.token = token

            except Exception as e:
                return JsonResponse(
                    {'detail': f'Invalid or expired token: {str(e)}', 'code': 'token_invalid'},
                    status=401
                )
        #else:
            #return JsonResponse(
                #{'detail': 'No token provided', 'code': 'no_token_provided'},
                #status=401
            #)
    '''
    def process_request(self, request):
        token = request.COOKIES.get('access')  # Leer el token JWT desde la cookie 'access'

        print("Token: ", token)

        if token:
            try:
                # El token JWT está en tres partes: header.payload.signature
                # Primero decodificamos el payload (la segunda parte del token JWT)
                payload = token.split('.')[1]  # Obtener la parte del payload
                decoded_payload = base64.b64decode(payload + '==')  # Decodificar la base64
                decoded_json = json.loads(decoded_payload)  # Convertirlo a JSON

                # Verificar si el token está expirado
                if decoded_json['exp'] < datetime.datetime.now().timestamp():
                    return JsonResponse(
                        {'detail': 'Token has expired', 'code': 'token_expired'},
                        status=401
                    )

                # Extraer los datos del payload
                user_id = decoded_json.get('user_id')
                username = decoded_json.get('username')
                email = decoded_json.get('email')
                groups = decoded_json.get('groups')

                # Guardar los datos del usuario en el request para usarlos más tarde
                request.user_id = user_id
                request.username = username
                request.email = email
                request.groups = groups

            except Exception as e:
                return JsonResponse(
                    {'detail': f'Invalid or expired token: {str(e)}', 'code': 'token_invalid'},
                    status=401
                )
        else:
            return JsonResponse(
                {'detail': 'No token provided', 'code': 'no_token_provided'},
                status=401
            )
    '''
