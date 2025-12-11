#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sistema de autenticación JWT para Máquina Orquestadora v2.3

Módulo que implementa:
- Generación de tokens JWT
- Validación de credenciales
- Gestión de usuarios y permisos
- Seguridad de contraseñas con bcrypt
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field

logger = logging.getLogger(__name__)

# ===== CONFIGURACIÓN =====
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production-12345")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Contexto de hash de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ===== MODELOS =====

class TokenPayload(BaseModel):
    """Payload del token JWT"""
    sub: str  # subject (user_id)
    exp: int  # expiration
    iat: int  # issued at
    type: str = "access"  # access o refresh
    permissions: list = []

class TokenResponse(BaseModel):
    """Respuesta con tokens de autenticación"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class User(BaseModel):
    """Modelo de usuario"""
    user_id: str
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    hashed_password: str
    is_active: bool = True
    permissions: list = Field(default_factory=list)
    created_at: Optional[datetime] = None

class UserLogin(BaseModel):
    """Credenciales de login"""
    username: str
    password: str

class UserRegister(BaseModel):
    """Datos de registro de usuario"""
    user_id: str
    email: EmailStr
    full_name: str
    password: str

class TokenData(BaseModel):
    """Datos extraí dos del token"""
    user_id: Optional[str] = None
    permissions: list = []

# ===== FUNCIONES DE SEGURIDAD =====

def hash_password(password: str) -> str:
    """Hash de contraseña con bcrypt"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica contraseña contra hash"""
    return pwd_context.verify(plain_password, hashed_password)

# ===== GESTIÓN DE TOKENS =====

def create_access_token(user_id: str, permissions: list = None, expires_delta: Optional[timedelta] = None) -> str:
    """Crea token JWT de acceso"""
    if permissions is None:
        permissions = []
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {
        "sub": user_id,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access",
        "permissions": permissions
    }
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    logger.info(f"Access token created for user {user_id}")
    return encoded_jwt

def create_refresh_token(user_id: str) -> str:
    """Crea token JWT de refresco"""
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {
        "sub": user_id,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    }
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    logger.info(f"Refresh token created for user {user_id}")
    return encoded_jwt

def create_token_pair(user_id: str, permissions: list = None) -> TokenResponse:
    """Crea par de tokens (acceso + refresco)"""
    access_token = create_access_token(user_id, permissions)
    refresh_token = create_refresh_token(user_id)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

def verify_token(token: str) -> Optional[TokenData]:
    """Verifica y decodifica token JWT"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        permissions: list = payload.get("permissions", [])
        token_type: str = payload.get("type", "access")
        
        if user_id is None:
            logger.warning("Token sin user_id")
            return None
        
        if token_type != "access":
            logger.warning(f"Token tipo incorrecto: {token_type}")
            return None
        
        return TokenData(user_id=user_id, permissions=permissions)
    
    except JWTError as e:
        logger.error(f"Error verificando token: {str(e)}")
        return None

def refresh_access_token(refresh_token: str) -> Optional[str]:
    """Crea nuevo access token desde refresh token"""
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type", "access")
        
        if token_type != "refresh":
            logger.warning(f"Token refresh incorrecto: {token_type}")
            return None
        
        if user_id is None:
            logger.warning("Refresh token sin user_id")
            return None
        
        new_access_token = create_access_token(user_id)
        logger.info(f"Access token refrescado para {user_id}")
        return new_access_token
    
    except JWTError as e:
        logger.error(f"Error refrescando token: {str(e)}")
        return None

# ===== PERMISOS =====

PERMISSION_LEVELS = {
    "admin": ["read", "write", "delete", "admin"],
    "editor": ["read", "write"],
    "viewer": ["read"],
    "guest": []
}

def has_permission(permissions: list, required_permission: str) -> bool:
    """Verifica si el usuario tiene permiso"""
    return required_permission in permissions

def get_permissions_for_role(role: str) -> list:
    """Obtiene lista de permisos para un rol"""
    return PERMISSION_LEVELS.get(role.lower(), [])

# ===== AUTENTICACIÓN DE USUARIO =====

class AuthenticationManager:
    """Gestor de autenticación de usuarios"""
    
    def __init__(self):
        # En producción, usar base de datos real
        self.users_db: Dict[str, User] = {}
    
    def register_user(self, user_data: UserRegister) -> tuple[bool, str]:
        """Registra nuevo usuario"""
        if user_data.user_id in self.users_db:
            return False, "Usuario ya existe"
        
        hashed_pwd = hash_password(user_data.password)
        user = User(
            user_id=user_data.user_id,
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hashed_pwd,
            permissions=get_permissions_for_role("viewer"),
            created_at=datetime.utcnow()
        )
        
        self.users_db[user_data.user_id] = user
        logger.info(f"Usuario {user_data.user_id} registrado")
        return True, "Usuario registrado exitosamente"
    
    def authenticate_user(self, credentials: UserLogin) -> Optional[TokenResponse]:
        """Autentica usuario y retorna tokens"""
        user = self.users_db.get(credentials.username)
        
        if not user:
            logger.warning(f"Intento de login con usuario inexistente: {credentials.username}")
            return None
        
        if not user.is_active:
            logger.warning(f"Intento de login con usuario inactivo: {credentials.username}")
            return None
        
        if not verify_password(credentials.password, user.hashed_password):
            logger.warning(f"Contraseña incorrecta para usuario: {credentials.username}")
            return None
        
        tokens = create_token_pair(user.user_id, user.permissions)
        logger.info(f"Usuario {credentials.username} autenticado exitosamente")
        return tokens
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Obtiene datos de usuario"""
        return self.users_db.get(user_id)
    
    def disable_user(self, user_id: str) -> bool:
        """Desactiva usuario"""
        if user_id in self.users_db:
            self.users_db[user_id].is_active = False
            logger.info(f"Usuario {user_id} desactivado")
            return True
        return False
    
    def update_permissions(self, user_id: str, permissions: list) -> bool:
        """Actualiza permisos de usuario"""
        if user_id in self.users_db:
            self.users_db[user_id].permissions = permissions
            logger.info(f"Permisos actualizados para {user_id}")
            return True
        return False

# Instancia global
auth_manager = AuthenticationManager()

if __name__ == "__main__":
    # Test básico
    logging.basicConfig(level=logging.INFO)
    
    # Registrar usuario de prueba
    test_user = UserRegister(
        user_id="testuser",
        email="test@example.com",
        full_name="Test User",
        password="testpass123"
    )
    
    success, msg = auth_manager.register_user(test_user)
    print(f"Registro: {msg}")
    
    # Autenticar
    login = UserLogin(username="testuser", password="testpass123")
    tokens = auth_manager.authenticate_user(login)
    
    if tokens:
        print(f"Tokens generados")
        print(f"Access token: {tokens.access_token[:50]}...")
        
        # Verificar token
        token_data = verify_token(tokens.access_token)
        if token_data:
            print(f"Token válido para usuario: {token_data.user_id}")
            print(f"Permisos: {token_data.permissions}")
