#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Máquina Orquestadora de IA GL Strategic - Backend v2.3
Arquitectura modular con Claude API + SQLite + mejoras P0
Server principal que orquesta las llamadas a Claude y persistencia
"""

import os
import logging
from datetime import datetime
from typing import Optional, List
from pathlib import Path

from fastapi import FastAPI, CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import uvicorn

# Importar módulos personalizados
from claude_integration import ClaudeOrchestrator
from database import Database

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ===== CONFIGURACIÓN =====
DB_PATH = Path("data/conversations.db")
DB_PATH.parent.mkdir(exist_ok=True)
API_KEY = os.getenv("CLAUDE_API_KEY", "")

# ===== MODELOS PYDANTIC =====
class Message(BaseModel):
    """Modelo de mensaje individual"""
    role: str
    content: str

class OrchestrationRequest(BaseModel):
    """Solicitud de orquestación"""
    text: str
    context: Optional[List[Message]] = None
    user_id: Optional[str] = "default"

class OrchestrationResponse(BaseModel):
    """Respuesta de orquestación"""
    response: str
    emotion: str
    timestamp: datetime
    model: str
    tokens_used: Optional[int] = None

# ===== FASTAPI APP =====
app = FastAPI(
    title="Orquesta IA GL Strategic v2.3",
    version="2.3.0",
    description="Backend modular con Claude API real e integración SQLite",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar componentes globales
logger.info("Initializing Database...")
db = Database(str(DB_PATH))

logger.info("Initializing Claude Orchestrator...")
orchestrator = ClaudeOrchestrator(API_KEY)

# ===== ENDPOINTS =====

@app.get("/")
async def root():
    """Endpoint raíz con estado general"""
    api_status = "ready" if orchestrator.client else "fallback"
    return {
        "name": "Máquina Orquestadora GL Strategic",
        "version": "2.3.0",
        "status": "online",
        "architecture": "modular",
        "claude_api": api_status,
        "database": "sqlite",
        "features": [
            "Claude API Real Integration",
            "SQLite Persistence",
            "Conversation History",
            "User Management",
            "Emotion Detection"
        ],
        "endpoints": {
            "health": "/health",
            "ask": "/ask",
            "history": "/history",
            "users": "/users",
            "docs": "/api/docs"
        }
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    db_status = "connected" if db.is_connected() else "error"
    api_status = "ready" if orchestrator.client else "not_configured"
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": db_status,
        "claude_api": api_status,
        "components": {
            "database": "operational",
            "orchestrator": "operational",
            "api": "operational"
        }
    }

@app.post("/ask")
async def ask(request: OrchestrationRequest) -> OrchestrationResponse:
    """Endpoint principal - Procesa pregunta con Claude API
    
    Args:
        request: OrchestrationRequest con texto, contexto y user_id
    
    Returns:
        OrchestrationResponse con respuesta, emoción, timestamp y modelo
    """
    try:
        logger.info(f"Request from user {request.user_id}: {request.text[:50]}...")
        
        # Guardar mensaje del usuario en BD
        user_msg_id = db.save_message(
            user_id=request.user_id,
            role="user",
            content=request.text
        )
        logger.info(f"User message saved with ID: {user_msg_id}")
        
        # Generar respuesta con Claude
        result = await orchestrator.generate_response(
            user_input=request.text,
            context=request.context
        )
        
        # Guardar respuesta en BD
        assistant_msg_id = db.save_message(
            user_id=request.user_id,
            role="assistant",
            content=result["response"],
            emotion=result.get("emotion", "neutral"),
            model=result.get("model", "claude")
        )
        logger.info(f"Assistant message saved with ID: {assistant_msg_id}")
        
        return OrchestrationResponse(
            response=result["response"],
            emotion=result.get("emotion", "neutral"),
            timestamp=datetime.now(),
            model=result.get("model", "claude"),
            tokens_used=result.get("tokens_used", None)
        )
        
    except Exception as e:
        logger.error(f"Error in /ask endpoint: {str(e)}", exc_info=True)
        # Guardar error en BD
        try:
            db.save_message(
                user_id=request.user_id,
                role="system",
                content=f"ERROR: {str(e)}"
            )
        except:
            pass
        
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "status": "error"
            }
        )

@app.get("/history")
async def get_history(user_id: str = "default", limit: int = 20):
    """Obtener historial de conversaciones de un usuario
    
    Args:
        user_id: ID del usuario (default: "default")
        limit: Número máximo de mensajes (default: 20)
    
    Returns:
        Lista de mensajes del usuario
    """
    try:
        history = db.get_conversation_history(user_id=user_id, limit=limit)
        return {
            "user_id": user_id,
            "messages": history,
            "count": len(history),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"History error: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.get("/users")
async def get_users():
    """Listar usuarios activos"""
    try:
        users = db.get_all_users()
        return {
            "users": users,
            "count": len(users),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Users error: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.delete("/clear/{user_id}")
async def clear_history(user_id: str):
    """Limpiar historial de un usuario"""
    try:
        db.delete_user_messages(user_id=user_id)
        return {
            "status": "cleared",
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Clear history error: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.get("/app")
async def serve_frontend():
    """Servir frontend"""
    try:
        return FileResponse("app/frontend/index.html")
    except FileNotFoundError:
        return JSONResponse(
            status_code=404,
            content={"error": "Frontend not found"}
        )

@app.get("/metrics")
async def get_metrics():
    """Obtener métricas del sistema"""
    try:
        metrics = db.get_metrics()
        return {
            "metrics": metrics,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Metrics error: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

# ===== MAIN =====
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "False").lower() == "true"
    
    logger.info("="*50)
    logger.info("Máquina Orquestadora v2.3 - Starting")
    logger.info("="*50)
    logger.info(f"Port: {port}")
    logger.info(f"Debug: {debug}")
    logger.info(f"Claude API: {'READY' if orchestrator.client else 'FALLBACK MODE'}")
    logger.info(f"Database: {DB_PATH}")
    logger.info("="*50)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info" if not debug else "debug",
        reload=debug
    )
