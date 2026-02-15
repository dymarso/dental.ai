import jwt
import uuid
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth.models import User
from .models import RefreshToken


# JWT Configuration
JWT_SECRET_KEY = settings.SECRET_KEY
JWT_ALGORITHM = 'HS256'
ACCESS_TOKEN_LIFETIME = timedelta(minutes=30)  # 30 minutes
REFRESH_TOKEN_LIFETIME = timedelta(days=7)  # 7 days


def generate_access_token(user):
    """Generate JWT access token for a user"""
    payload = {
        'user_id': user.id,
        'username': user.username,
        'email': user.email,
        'exp': datetime.utcnow() + ACCESS_TOKEN_LIFETIME,
        'iat': datetime.utcnow(),
        'type': 'access'
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def generate_refresh_token(user):
    """Generate JWT refresh token and store in database"""
    jti = uuid.uuid4()
    expires_at = datetime.utcnow() + REFRESH_TOKEN_LIFETIME
    
    payload = {
        'user_id': user.id,
        'username': user.username,
        'jti': str(jti),
        'exp': expires_at,
        'iat': datetime.utcnow(),
        'type': 'refresh'
    }
    
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    
    # Store refresh token in database
    RefreshToken.objects.create(
        user=user,
        token=token,
        jti=jti,
        expires_at=expires_at
    )
    
    return token


def decode_token(token):
    """Decode and validate JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError('Token has expired')
    except jwt.InvalidTokenError as e:
        raise ValueError(f'Invalid token: {str(e)}')


def get_user_from_token(token):
    """Get user from JWT token"""
    try:
        payload = decode_token(token)
        user_id = payload.get('user_id')
        user = User.objects.get(id=user_id)
        return user
    except (ValueError, User.DoesNotExist):
        return None


def verify_refresh_token(token):
    """Verify refresh token and check if it's revoked"""
    try:
        payload = decode_token(token)
        
        if payload.get('type') != 'refresh':
            raise ValueError('Not a refresh token')
        
        jti = payload.get('jti')
        
        # Check if token exists and is not revoked
        refresh_token = RefreshToken.objects.get(jti=jti, revoked=False)
        
        if refresh_token.is_expired:
            raise ValueError('Token has expired')
        
        return refresh_token.user
    except (ValueError, RefreshToken.DoesNotExist) as e:
        raise ValueError(f'Invalid refresh token: {str(e)}')


def revoke_refresh_token(token):
    """Revoke a refresh token"""
    try:
        payload = decode_token(token)
        jti = payload.get('jti')
        
        refresh_token = RefreshToken.objects.get(jti=jti)
        refresh_token.revoke()
        
        return True
    except (ValueError, RefreshToken.DoesNotExist):
        return False


def revoke_all_user_tokens(user):
    """Revoke all refresh tokens for a user"""
    tokens = RefreshToken.objects.filter(user=user, revoked=False)
    for token in tokens:
        token.revoke()
