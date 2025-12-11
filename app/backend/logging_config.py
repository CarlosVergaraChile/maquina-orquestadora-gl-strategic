#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sistema de logging estructurado para Máquina Orquestadora v2.3

Implementa JSON logging para:
- CloudWatch
- ELK Stack
- Datadog
- Splunk
"""

import json
import logging
import sys
from datetime import datetime
from typing import Any, Dict
import traceback

# ===== CONFIGURACIÓN =====
LOG_LEVEL = "INFO"
JSON_LOGS = True
INCLUDE_TRACEBACK = True

# ===== FORMATEADORES =====

class JSONFormatter(logging.Formatter):
    """Formateador personalizado para JSON output"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Convierte log record a JSON"""
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Añadir contexto adicional si existe
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        if hasattr(record, "endpoint"):
            log_data["endpoint"] = record.endpoint
        if hasattr(record, "ip_address"):
            log_data["ip_address"] = record.ip_address
        
        # Añadir excepción si existe
        if record.exc_info and INCLUDE_TRACEBACK:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": traceback.format_exception(*record.exc_info) if record.exc_info else None
            }
        
        # Añadir campos extra
        if record.extra if hasattr(record, "extra") else False:
            log_data.update(record.extra)
        
        return json.dumps(log_data, ensure_ascii=False)

class PlainFormatter(logging.Formatter):
    """Formateador simple para desarrollo local"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Formatea como texto plano"""
        timestamp = datetime.utcnow().isoformat()
        return f"[{timestamp}] {record.levelname:8s} {record.name:30s} {record.getMessage()}"

# ===== CONFIGURACIÓN DE LOGGING =====

def setup_logging(json_format: bool = JSON_LOGS, level: str = LOG_LEVEL) -> logging.Logger:
    """Configura logging para toda la aplicación"""
    
    # Crear root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level))
    
    # Remover handlers existentes
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Crear handler para stdout
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level))
    
    # Elegir formateador
    if json_format:
        formatter = JSONFormatter()
    else:
        formatter = PlainFormatter()
    
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Opcional: Handler para archivo
    try:
        file_handler = logging.FileHandler("logs/orquestadora.log")
        file_handler.setLevel(getattr(logging, level))
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    except OSError:
        # Si no se puede crear el archivo, solo usar stdout
        pass
    
    return root_logger

def get_logger(name: str) -> logging.Logger:
    """Obtiene logger para un módulo específico"""
    return logging.getLogger(name)

# ===== LOGGING HELPERS =====

class LogContext:
    """Context manager para logging con contexto de request"""
    
    def __init__(self, logger: logging.Logger, request_id: str = None, user_id: str = None):
        self.logger = logger
        self.request_id = request_id
        self.user_id = user_id
    
    def __enter__(self):
        self.logger.extra = {
            "request_id": self.request_id,
            "user_id": self.user_id
        }
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
    
    def info(self, message: str, **kwargs):
        """Log info con contexto"""
        self.logger.info(message, extra={**self.logger.extra, **kwargs} if hasattr(self.logger, "extra") else kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error con contexto"""
        self.logger.error(message, extra={**self.logger.extra, **kwargs} if hasattr(self.logger, "extra") else kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning con contexto"""
        self.logger.warning(message, extra={**self.logger.extra, **kwargs} if hasattr(self.logger, "extra") else kwargs)

# ===== EVENTOS ESPECIALES =====

def log_security_event(logger: logging.Logger, event_type: str, user_id: str = None, details: Dict = None):
    """Log eventos de seguridad"""
    log_data = {
        "event_type": event_type,
        "severity": "SECURITY",
        "user_id": user_id,
        "details": details or {}
    }
    logger.warning(f"SECURITY_EVENT: {event_type}", extra=log_data)

def log_performance_event(logger: logging.Logger, endpoint: str, duration_ms: float, status: int):
    """Log eventos de performance"""
    log_data = {
        "event_type": "PERFORMANCE",
        "endpoint": endpoint,
        "duration_ms": duration_ms,
        "status_code": status,
        "slow": duration_ms > 1000
    }
    logger.info(f"REQUEST_COMPLETED: {endpoint}", extra=log_data)

if __name__ == "__main__":
    # Test básico
    logger = setup_logging(json_format=True, level="DEBUG")
    test_logger = get_logger("test")
    
    test_logger.info("Mensaje de información")
    test_logger.warning("Mensaje de advertencia")
    test_logger.error("Mensaje de error")
    
    # Test con contexto
    with LogContext(test_logger, request_id="req-123", user_id="user-456"):
        test_logger.info("Mensaje con contexto de request")
    
    # Test evento de seguridad
    log_security_event(test_logger, "LOGIN_FAILED", user_id="attacker", details={"reason": "Invalid credentials"})
