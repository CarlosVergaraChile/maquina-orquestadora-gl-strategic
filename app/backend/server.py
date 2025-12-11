#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Máquina Orquestadora de IA GL Strategic - Backend v2.2
Integración REAL con Claude API + SQLite persistencia + mejoras P0
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

try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ===== CONFIGURACIÓN =====
DB_PATH = Path("data/conversations.db")
DB_PATH.parent.mkdir(exist_ok=True)
APIKEY = os.getenv("CLAUDE_API_KEY", "")

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
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO conversations (timestamp, role, content, emotion, model)
                VALUES (?, ?, ?, ?, ?)
            """, (datetime.now().isoformat(), role, content, emotion, model))
            conn.commit()
    
    def get_history(self, limit: int = 20) -> List[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT role, content, emotion FROM conversations
                ORDER BY timestamp DESC LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]

# ===== CLAUDE API INTEGRATION =====
class ClaudeOrchestrator:
    """Orquestador con Claude API REAL"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = None
        if Anthropic and api_key:
            try:
                self.client = Anthropic(api_key=api_key)
                logger.info("Claude API client initialized")
            except Exception as e:
                logger.warning(f"Failed to init Claude: {e}. Using fallback.")
    
    async def generate_response(self, user_input: str, context: List[Message] = None) -> Dict:
        """Genera respuesta usando Claude API real o fallback"""
        
        if self.client and self.api_key:
            try:
                # Construir historial para Claude
                messages = []
                if context:
                    for msg in context[-5:]:  # Últimos 5 mensajes para contexto
                        messages.append({"role": msg.role, "content": msg.content})
                messages.append({"role": "user", "content": user_input})
                
                # Llamar a Claude API
                response = self.client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1024,
                    messages=messages,
                    system="Eres una IA conversacional llamada Orquesta. Responde de manera concisa y útil en español."
                )
                
                response_text = response.content[0].text
                emotion = "confident"  # Claude siempre confiado
                model = "claude-3-5-sonnet-20241022"
                
                logger.info(f"Claude response: {response_text[:50]}...")
                
                return {
                    "response": response_text,
                    "emotion": emotion,
                    "model": model
                }
            
            except Exception as e:
                logger.error(f"Claude API error: {str(e)}")
                return self._fallback_response(user_input)
        
        return self._fallback_response(user_input)
    
    def _fallback_response(self, user_input: str) -> Dict:
        """Respuesta fallback cuando Claude no está disponible"""
        responses = [
            f"He entendido tu pregunta sobre '{user_input[:30]}...'. Este es un modo de fallback, por favor configura CLAUDE_API_KEY.",
            f"Respecto a '{user_input[:30]}...', en modo fallback no puedo procesar completamente. ¿Puedes proporcionar la clave API de Claude?",
        ]
        import random
        return {
            "response": random.choice(responses),
            "emotion": "thoughtful",
            "model": "fallback-simulator"
        }

# ===== FASTAPI APP =====
app = FastAPI(
    title="Orquesta IA GL Strategic v2.2",
    version="2.2.0",
    description="Backend con Claude API real integrada"
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
    api_status = "ready" if orchestrator.client else "fallback"
    return {
        "name": "Máquina Orquestadora GL Strategic",
        "version": "2.2.0",
        "status": "online",
        "claude_api": api_status,
        "features": ["Claude API Real", "SQLite persistence", "Conversation history"],
        "endpoints": ["/health", "/ask", "/history", "/app"]
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": "connected" if DB_PATH.exists() else "error",
        "claude_api": "ready" if orchestrator.client else "not_configured"
    }

@app.post("/ask")
async def ask(request: OrchestrationRequest) -> OrchestrationResponse:
    """Endpoint principal - Procesa pregunta con Claude API"""
    try:
        logger.info(f"Request: {request.text}")
        
        # Guardar mensaje del usuario
        db.save_message("user", request.text)
        
        # Generar respuesta con Claude
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
    logger.info(f"Starting server v2.2 on port {port}")
    logger.info(f"Claude API: {'READY' if orchestrator.client else 'FALLBACK MODE'}")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
