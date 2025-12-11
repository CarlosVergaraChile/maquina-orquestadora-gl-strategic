#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sistema de rate limiting para Máquina Orquestadora v2.3

Implementa protección contra abuso:
- Token bucket algorithm
- IP-based limiting
- User-based limiting
- Endpoint-specific limits
"""

import time
import logging
from typing import Dict, Optional, Tuple
from dataclasses import dataclass, field
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

# ===== CONFIGURACIÓN =====
DEFAULT_RATE_LIMIT = 100  # requests per minute
PREMIUM_RATE_LIMIT = 1000
API_RATE_LIMIT = 30  # más restrictivo para /ask
WHITELIST_IPS = ["127.0.0.1", "localhost"]

# ===== MODELOS =====

@dataclass
class TokenBucket:
    """Token bucket para rate limiting"""
    capacity: int  # máximo de tokens
    refill_rate: float  # tokens por segundo
    tokens: float = field(default_factory=lambda: 100.0)
    last_refill: float = field(default_factory=time.time)
    
    def consume(self, amount: int = 1) -> bool:
        """Intenta consumir tokens"""
        self._refill()
        if self.tokens >= amount:
            self.tokens -= amount
            return True
        return False
    
    def _refill(self):
        """Refill tokens basado en tiempo"""
        now = time.time()
        elapsed = now - self.last_refill
        tokens_to_add = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now

@dataclass
class RateLimitConfig:
    """Configuración de rate limiting por endpoint"""
    name: str
    requests_per_minute: int = 100
    burst_size: int = 10
    
    @property
    def refill_rate(self) -> float:
        """Tokens por segundo"""
        return self.requests_per_minute / 60.0

# ===== RATE LIMITER =====

class RateLimiter:
    """Gestor de rate limiting"""
    
    def __init__(self):
        self.ip_buckets: Dict[str, TokenBucket] = {}
        self.user_buckets: Dict[str, TokenBucket] = {}
        self.endpoint_configs: Dict[str, RateLimitConfig] = {
            "ask": RateLimitConfig("ask", requests_per_minute=API_RATE_LIMIT, burst_size=3),
            "history": RateLimitConfig("history", requests_per_minute=200),
            "health": RateLimitConfig("health", requests_per_minute=1000),
            "default": RateLimitConfig("default", requests_per_minute=DEFAULT_RATE_LIMIT),
        }
    
    def get_client_ip(self, request: Request) -> str:
        """Obtiene IP del cliente"""
        if request.client:
            return request.client.host
        return "unknown"
    
    def check_rate_limit(self, request: Request, endpoint: str, user_id: Optional[str] = None) -> Tuple[bool, Optional[str]]:
        """Verifica rate limit para request"""
        client_ip = self.get_client_ip(request)
        
        # Whitelist
        if client_ip in WHITELIST_IPS:
            return True, None
        
        # Obtener configuración del endpoint
        config = self.endpoint_configs.get(endpoint, self.endpoint_configs["default"])
        
        # Verificar rate limit por IP
        if not self._check_ip_limit(client_ip, config):
            msg = f"Rate limit excedido para IP {client_ip}"
            logger.warning(msg)
            return False, msg
        
        # Verificar rate limit por usuario (si aplica)
        if user_id:
            if not self._check_user_limit(user_id, config):
                msg = f"Rate limit excedido para usuario {user_id}"
                logger.warning(msg)
                return False, msg
        
        return True, None
    
    def _check_ip_limit(self, ip: str, config: RateLimitConfig) -> bool:
        """Verifica límite por IP"""
        if ip not in self.ip_buckets:
            self.ip_buckets[ip] = TokenBucket(
                capacity=config.burst_size,
                refill_rate=config.refill_rate
            )
        
        return self.ip_buckets[ip].consume()
    
    def _check_user_limit(self, user_id: str, config: RateLimitConfig) -> bool:
        """Verifica límite por usuario"""
        if user_id not in self.user_buckets:
            self.user_buckets[user_id] = TokenBucket(
                capacity=config.burst_size * 2,  # usuarios tienen más generoso
                refill_rate=config.refill_rate * 1.5
            )
        
        return self.user_buckets[user_id].consume()
    
    def get_status(self, client_ip: str, user_id: Optional[str] = None) -> Dict:
        """Obtiene estado de rate limiting"""
        status = {
            "ip": client_ip,
            "ip_limited": client_ip in self.ip_buckets
        }
        
        if client_ip in self.ip_buckets:
            bucket = self.ip_buckets[client_ip]
            status["ip_tokens_remaining"] = int(bucket.tokens)
            status["ip_capacity"] = bucket.capacity
        
        if user_id and user_id in self.user_buckets:
            bucket = self.user_buckets[user_id]
            status["user_tokens_remaining"] = int(bucket.tokens)
            status["user_capacity"] = bucket.capacity
        
        return status

# Instancia global
rate_limiter = RateLimiter()

# ===== MIDDLEWARE =====

async def rate_limit_middleware(request: Request, call_next):
    """Middleware de rate limiting para FastAPI"""
    # Obtener endpoint
    endpoint = request.url.path.split("/")[-1] or "default"
    endpoint = endpoint.split("?")[0]  # remover query params
    
    # Obtener user_id del token si existe
    user_id = None
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        # En producción, parsear el token JWT aquí
        pass
    
    # Verificar rate limit
    allowed, error_msg = rate_limiter.check_rate_limit(request, endpoint, user_id)
    
    if not allowed:
        return JSONResponse(
            status_code=429,
            content={
                "error": "Too Many Requests",
                "message": error_msg,
                "retry_after": 60
            }
        )
    
    # Agregar headers de rate limit a la respuesta
    response = await call_next(request)
    client_ip = rate_limiter.get_client_ip(request)
    status = rate_limiter.get_status(client_ip, user_id)
    
    response.headers["X-RateLimit-Limit"] = str(100)
    response.headers["X-RateLimit-Remaining"] = str(status.get("ip_tokens_remaining", 0))
    response.headers["X-RateLimit-Reset"] = str(int(time.time()) + 60)
    
    return response

# ===== DECORADORES =====

def require_rate_limit(endpoint: str = "default"):
    """Decorador para verificar rate limit en endpoint específico"""
    def decorator(func):
        async def wrapper(request: Request, *args, **kwargs):
            allowed, error_msg = rate_limiter.check_rate_limit(request, endpoint)
            if not allowed:
                raise HTTPException(status_code=429, detail=error_msg)
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator

if __name__ == "__main__":
    # Test
    logging.basicConfig(level=logging.INFO)
    
    limiter = RateLimiter()
    
    # Simular 150 requests en 60 segundos
    config = limiter.endpoint_configs["default"]
    print(f"Config: {config.requests_per_minute} req/min, burst {config.burst_size}")
    
    allowed_count = 0
    for i in range(150):
        bucket = TokenBucket(capacity=config.burst_size, refill_rate=config.refill_rate)
        if bucket.consume():
            allowed_count += 1
        if (i + 1) % 10 == 0:
            print(f"Request {i+1}: {allowed_count} permitidos")
    
    print(f"\nTotal permitidos: {allowed_count}/150")
