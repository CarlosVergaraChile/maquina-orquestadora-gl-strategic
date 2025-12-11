"""Utilidades reutilizables para testing - Módulo base para todos los tests."""

import asyncio
import jwt
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from functools import wraps
from unittest.mock import AsyncMock, MagicMock


class TestSecurityUtils:
    """Utilidades para testing de seguridad (reutilizable en múltiples tests)."""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hashea una contraseña usando passlib."""
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verifica contraseña hasheada."""
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def create_test_jwt_token(
        user_id: str = "test_user_123",
        username: str = "testuser",
        expires_delta: Optional[timedelta] = None,
        secret_key: str = "test_secret_key_12345"
    ) -> str:
        """Crea un JWT token de prueba reutilizable."""
        if expires_delta is None:
            expires_delta = timedelta(hours=1)
        
        expire = datetime.utcnow() + expires_delta
        to_encode = {
            "user_id": user_id,
            "username": username,
            "exp": expire
        }
        encoded_jwt = jwt.encode(to_encode, secret_key, algorithm="HS256")
        return encoded_jwt

    @staticmethod
    def validate_jwt_token(
        token: str,
        secret_key: str = "test_secret_key_12345"
    ) -> Dict[str, Any]:
        """Valida y decodifica JWT token."""
        try:
            payload = jwt.decode(token, secret_key, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Token expirado")
        except jwt.InvalidTokenError:
            raise ValueError("Token inválido")


class TestEmailUtils:
    """Utilidades para testing de emails (reutilizable)."""

    @staticmethod
    def validate_email(email: str) -> str:
        """Valida email usando email-validator."""
        from email_validator import validate_email, EmailNotValidError
        try:
            valid = validate_email(email)
            return valid.normalized
        except EmailNotValidError as e:
            raise ValueError(f"Email inválido: {e}")

    @staticmethod
    def is_valid_email(email: str) -> bool:
        """Verifica si email es válido."""
        try:
            TestEmailUtils.validate_email(email)
            return True
        except ValueError:
            return False


class TestAsyncUtils:
    """Utilidades para testing async (reutilizable)."""

    @staticmethod
    def run_async(coro):
        """Ejecuta coroutine sincronamente para testing."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()

    @staticmethod
    def async_test(func):
        """Decorator para ejecutar async tests."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            return TestAsyncUtils.run_async(func(*args, **kwargs))
        return wrapper


class TestMockUtils:
    """Utilidades para crear mocks reutilizables."""

    @staticmethod
    def create_mock_user(user_id: str = "123", username: str = "testuser") -> Dict[str, Any]:
        """Crea un usuario mock reutilizable."""
        return {
            "user_id": user_id,
            "username": username,
            "email": f"{username}@example.com",
            "is_active": True
        }

    @staticmethod
    def create_mock_websocket():
        """Crea un WebSocket mock reutilizable."""
        mock_ws = MagicMock()
        mock_ws.accept = AsyncMock()
        mock_ws.send_text = AsyncMock()
        mock_ws.send_json = AsyncMock()
        mock_ws.receive_json = AsyncMock()
        mock_ws.receive_text = AsyncMock()
        mock_ws.close = AsyncMock()
        return mock_ws

    @staticmethod
    def create_mock_claude_response(text: str = "Test response") -> Dict[str, Any]:
        """Crea una respuesta Claude mock reutilizable."""
        return {
            "content": [{"type": "text", "text": text}],
            "model": "claude-3-5-sonnet",
            "usage": {"input_tokens": 100, "output_tokens": 50}
        }


class TestDataFactory:
    """Factory para crear datos de test reutilizables."""

    @staticmethod
    def create_test_question(question: str = "Test question", context: Optional[str] = None) -> Dict[str, Any]:
        """Crea una pregunta de test."""
        return {
            "question": question,
            "context": context or "Default context"
        }

    @staticmethod
    def create_test_auth_headers(token: str) -> Dict[str, str]:
        """Crea headers de autenticación de test."""
        return {"Authorization": f"Bearer {token}"}
