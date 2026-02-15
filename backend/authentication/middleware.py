from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import User
from django.http import JsonResponse
import jwt
from django.conf import settings


class JWTAuthenticationMiddleware(MiddlewareMixin):
    """
    Middleware for JWT authentication
    Authenticates user based on JWT token in Authorization header
    """
    
    def process_request(self, request):
        """Process incoming request and authenticate user"""
        
        # Skip authentication for certain paths
        exempt_paths = [
            '/api/authentication/login/',
            '/api/authentication/register/',
            '/api/authentication/refresh/',
            '/admin/',
            '/health/',
            '/csrf/',
        ]
        
        if any(request.path.startswith(path) for path in exempt_paths):
            return None
        
        # Get authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if not auth_header.startswith('Bearer '):
            return None
        
        # Extract token
        token = auth_header.split(' ')[1]
        
        try:
            # Decode token
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=['HS256']
            )
            
            # Verify token type
            if payload.get('type') != 'access':
                return JsonResponse({'error': 'Token inválido'}, status=401)
            
            # Get user
            user_id = payload.get('user_id')
            user = User.objects.filter(id=user_id, is_active=True).first()
            
            if not user:
                return JsonResponse({'error': 'Usuario no encontrado'}, status=401)
            
            # Attach user to request
            request.user = user
            
        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token expirado'}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Token inválido'}, status=401)
        except Exception:
            return JsonResponse({'error': 'Error de autenticación'}, status=401)
        
        return None
