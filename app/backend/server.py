#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Máquina Orquestadora de IA - Backend MVP
Sistema simple y rápido para producción con soporte mobile
"""

from fastapi import FastAPI, CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uvicorn
import json
import os

# Modelos
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

# App
app = FastAPI(
    title="Orquesta IA GL Strategic",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Variables globales
conversation_history = []

# Rutas
@app.get("/")
async def root():
    return {
        "name": "Máquina Orquestadora de IA GL Strategic",
        "version": "2.0.0",
        "status": "online",
        "endpoints": ["GET /", "POST /ask", "GET /health"]
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/ask")
async def ask(request: OrchestrationRequest):
    """Procesa pregunta y retorna respuesta"""
    global conversation_history
    
    try:
        # Guardar en historial
        conversation_history.append({
            "role": "user",
            "content": request.text,
            "timestamp": datetime.now().isoformat()
        })
        
        # Generar respuesta (simulado - aquí iría integración real con IAs)
        response_text = await generate_response(request.text, request.context or [])
        
        emotion = await analyze_emotion(request.text)
        
        # Guardar respuesta en historial
        conversation_history.append({
            "role": "assistant",
            "content": response_text,
            "emotion": emotion,
            "timestamp": datetime.now().isoformat()
        })
        
        return OrchestrationResponse(
            response=response_text,
            emotion=emotion,
            timestamp=datetime.now()
        )
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.get("/app")
async def serve_frontend():
    """Servir el frontend"""
    return FileResponse("app/frontend/index.html")

# Funciones auxiliares
async def generate_response(user_input: str, context: List[Message]) -> str:
    """Genera respuesta (MVP simple)"""
    # Aquí iría la integración real con Claude, OpenAI, etc.
    # Por ahora, respuesta simulada que parece natural
    
    responses = [
        f"He entendido: '{user_input}'. Procesando...",
        f"Excelente pregunta sobre '{user_input}'. Déjame analizar esto.",
        f"Interesante. Respecto a '{user_input}'...",
        f"Creo que entiendo lo que dices con '{user_input}'."
    ]
    
    import random
    base_response = random.choice(responses)
    
    # Análisis simple del contexto
    if len(context) > 0:
        return f"{base_response} Considerando el contexto anterior, puedo decir que esto es relevante."
    return base_response

async def analyze_emotion(text: str) -> str:
    """Analiza emoción del input (MVP simple)"""
    emotions = ["thoughtful", "curious", "engaged", "confident"]
    import random
    return random.choice(emotions)

# Main
if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        log_level="info"
    )
