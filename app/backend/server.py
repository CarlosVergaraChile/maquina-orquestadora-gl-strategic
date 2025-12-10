#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Máquina Orquestadora de IA GL Strategic - Backend v2.1
Integración con Claude API + SQLite persistencia + mejoras P0
"""

import os
import json
import sqlite3
import logging
from datetime import datetime
from typing import Optional, List, Dict
from pathlib import Path

from fastapi import FastAPI, CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import uvicorn

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ===== CONFIGURACIÓN =====
DB_PATH = Path("data/conversations.db")
DB_PATH.parent.mkdir(exist_ok=True)
APIKEY = os.getenv("CLAUDE_API_KEY", "sk-test")

# ===== MODELOS =====
class Message(BaseModel):
    role: str
    content: str

class OrchestrationRequest(BaseModel):
    text: str
    context: Optional[List[Message]] = None

class OrchestrationResponse(BaseModel):
    response: str
    emotion: str
    timestamp: datetime
    model: str

# ===== DATABASE =====
class ConversationDB:
    """Gestor de conversaciones con SQLite"""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Crear tablas si no existen"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY,
                    timestamp TEXT,
                    role TEXT,
                    content TEXT,
                    emotion TEXT,
                    model TEXT
                )
            """)
            conn.commit()
            logger.info(f"Database initialized at {self.db_path}")
    
    def save_message(self, role: str, content: str, emotion: str = None, model: str = "claude"):
        """Guardar mensaje en BD"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO conversations (timestamp, role, content, emotion, model)
                VALUES (?, ?, ?, ?, ?)
            """, (datetime.now().isoformat(), role, content, emotion, model))
            conn.commit()
    
    def get_history(self, limit: int = 20) -> List[Dict]:
        """Obtener historial de conversaciones"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT role, content, emotion FROM conversations
                ORDER BY timestamp DESC LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]

# ===== IA INTEGRATION =====
class ClaudeOrchestrator:
    """Orquestador con Claude API (simulado, reemplazar con real)"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        # TODO: Importar cliente real de Anthropic
        # from anthropic import Anthropic
        # self.client = Anthropic(api_key=api_key)
    
    async def generate_response(self, user_input: str, context: List[Message] = None) -> Dict:
        """Genera respuesta usando Claude (o simulado)"""
        # Por ahora, simulado. En producción:
        # response = self.client.messages.create(
        #     model="claude-3-5-sonnet-20241022",
        #     max_tokens=1024,
        #     messages=[...]
        # )
        
        # Respuesta simulada realista
        responses = [
            f"He entendido tu pregunta sobre '{user_input}'. Permíteme analizar esto...",
            f"Interesante observación sobre '{user_input}'. Mi análisis sugiere...",
            f"Respecto a '{user_input}', puedo ayudarte considerando...",
        ]
        
        import random
        response = random.choice(responses)
        emotion = random.choice(["thoughtful", "curious", "engaged", "confident"])
        
        return {
            "response": response,
            "emotion": emotion,
            "model": "claude-3-5-sonnet-20241022"
        }

# ===== FASTAPI APP =====
app = FastAPI(
    title="Orquesta IA GL Strategic v2.1",
    version="2.1.0",
    description="Backend mejorado con Claude API y SQLite"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar componentes
db = ConversationDB(DB_PATH)
orchestrator = ClaudeOrchestrator(APIKEY)

# ===== ENDPOINTS =====
@app.get("/")
async def root():
    return {
        "name": "Máquina Orquestadora GL Strategic",
        "version": "2.1.0",
        "status": "online",
        "features": ["Claude API", "SQLite persistence", "Conversation history"],
        "endpoints": ["/health", "/ask", "/history", "/app"]
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": "connected" if DB_PATH.exists() else "error"
    }

@app.post("/ask")
async def ask(request: OrchestrationRequest) -> OrchestrationResponse:
    """Endpoint principal - Procesa pregunta"""
    try:
        logger.info(f"Request: {request.text}")
        
        # Guardar mensaje del usuario
        db.save_message("user", request.text)
        
        # Generar respuesta
        result = await orchestrator.generate_response(request.text, request.context)
        
        # Guardar respuesta
        db.save_message("assistant", result["response"], result["emotion"], result["model"])
        
        return OrchestrationResponse(
            response=result["response"],
            emotion=result["emotion"],
            timestamp=datetime.now(),
            model=result["model"]
        )
    
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        db.save_message("error", str(e))
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.get("/history")
async def get_history(limit: int = 20):
    """Obtener historial de conversaciones"""
    try:
        history = db.get_history(limit)
        return {"messages": history, "count": len(history)}
    except Exception as e:
        logger.error(f"History error: {str(e)}")
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/app")
async def serve_frontend():
    """Servir frontend"""
    return FileResponse("app/frontend/index.html")

# ===== MAIN =====
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    logger.info(f"Starting server on port {port}")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
