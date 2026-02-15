from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import jwt
import uuid
from django.conf import settings

from .models import RefreshToken, AuditLog
from .serializers import (
    LoginSerializer,
    RefreshTokenSerializer,
    UserSerializer,
    RegisterSerializer
)


def get_client_ip(request):
    """Extract client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def create_audit_log(user, action, request, resource_type='User', resource_id=None, details=None):
    """Create audit log entry"""
    AuditLog.objects.create(
        user=user,
        username=user.username if user else 'Anonymous',
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        details=details
    )


def generate_tokens(user):
    """Generate access and refresh tokens for user"""
    
    # Access token expires in 1 hour
    access_token_exp = timezone.now() + timedelta(hours=1)
    access_payload = {
        'user_id': user.id,
        'username': user.username,
        'exp': access_token_exp.timestamp(),
        'iat': timezone.now().timestamp(),
        'type': 'access'
    }
    
    access_token = jwt.encode(
        access_payload,
        settings.SECRET_KEY,
        algorithm='HS256'
    )
    
    # Refresh token expires in 7 days
    refresh_token_exp = timezone.now() + timedelta(days=7)
    refresh_jti = uuid.uuid4()
    refresh_payload = {
        'user_id': user.id,
        'jti': str(refresh_jti),
        'exp': refresh_token_exp.timestamp(),
        'iat': timezone.now().timestamp(),
        'type': 'refresh'
    }
    
    refresh_token = jwt.encode(
        refresh_payload,
        settings.SECRET_KEY,
        algorithm='HS256'
    )
    
    # Store refresh token in database
    RefreshToken.objects.create(
        user=user,
        token=refresh_token,
        jti=refresh_jti,
        expires_at=refresh_token_exp
    )
    
    return {
        'access': access_token,
        'refresh': refresh_token,
        'access_expires_at': access_token_exp.isoformat(),
        'refresh_expires_at': refresh_token_exp.isoformat()
    }


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    Login endpoint
    Returns JWT tokens on successful authentication
    """
    serializer = LoginSerializer(data=request.data)
    
    if not serializer.is_valid():
        create_audit_log(
            None,
            'failed_login',
            request,
            details={'username': request.data.get('username'), 'errors': serializer.errors}
        )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    user = serializer.validated_data['user']
    tokens = generate_tokens(user)
    
    # Create audit log
    create_audit_log(user, 'login', request)
    
    return Response({
        'user': UserSerializer(user).data,
        'tokens': tokens
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """
    Logout endpoint
    Revokes the refresh token
    """
    try:
        refresh_token = request.data.get('refresh')
        
        if refresh_token:
            # Revoke the refresh token
            token_obj = RefreshToken.objects.filter(token=refresh_token, user=request.user).first()
            if token_obj:
                token_obj.revoke()
        
        # Create audit log
        create_audit_log(request.user, 'logout', request)
        
        return Response({'message': 'Logout exitoso'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def refresh(request):
    """
    Refresh token endpoint
    Returns new access token using refresh token
    """
    serializer = RefreshTokenSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    refresh_token = serializer.validated_data['refresh']
    
    try:
        # Decode refresh token
        payload = jwt.decode(
            refresh_token,
            settings.SECRET_KEY,
            algorithms=['HS256']
        )
        
        # Verify token type
        if payload.get('type') != 'refresh':
            return Response({'error': 'Token inválido'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if token exists and is not revoked
        token_obj = RefreshToken.objects.filter(
            jti=payload['jti'],
            revoked=False
        ).first()
        
        if not token_obj:
            return Response({'error': 'Token inválido o revocado'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if token is expired
        if token_obj.is_expired:
            return Response({'error': 'Token expirado'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get user
        user = token_obj.user
        
        if not user.is_active:
            return Response({'error': 'Usuario inactivo'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate new access token
        access_token_exp = timezone.now() + timedelta(hours=1)
        access_payload = {
            'user_id': user.id,
            'username': user.username,
            'exp': access_token_exp.timestamp(),
            'iat': timezone.now().timestamp(),
            'type': 'access'
        }
        
        access_token = jwt.encode(
            access_payload,
            settings.SECRET_KEY,
            algorithm='HS256'
        )
        
        return Response({
            'access': access_token,
            'access_expires_at': access_token_exp.isoformat()
        }, status=status.HTTP_200_OK)
        
    except jwt.ExpiredSignatureError:
        return Response({'error': 'Token expirado'}, status=status.HTTP_400_BAD_REQUEST)
    except jwt.InvalidTokenError:
        return Response({'error': 'Token inválido'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    """
    Get current user information
    """
    serializer = UserSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    Register new user
    """
    serializer = RegisterSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    user = serializer.save()
    tokens = generate_tokens(user)
    
    # Create audit log
    create_audit_log(user, 'create', request, resource_id=str(user.id))
    
    return Response({
        'user': UserSerializer(user).data,
        'tokens': tokens
    }, status=status.HTTP_201_CREATED)
