import asyncio
from typing import Annotated

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from starlette.websockets import WebSocketState
from pydantic import BaseModel

# ASUME ESTA IMPORTACIÓN: Necesitas adaptar tu función JWT para WS.
# La función debe aceptar el token (ej. de Query) y devolver el usuario si es válido.
from .authentication import get_current_active_user_ws 

router = APIRouter()

# --- MODELOS ---

class Question(BaseModel):
    """Modelo para la pregunta inicial que envía el cliente."""
    question: str
    context: str | None = None

# --- CONSTANTES ---
# Configura tu modelo de LLM aquí
CLAUDE_MODEL = "claude-3-5-sonnet"

# --- ENDPOINT DE WEBSOCKETS ---

@router.websocket("/ws/ask")
async def websocket_ask_endpoint(
    websocket: WebSocket,
    # 🚨 ADAPTACIÓN CRÍTICA: Obtener el JWT de los parámetros de consulta (?token=...)
    # y autenticar antes de aceptar la conexión.
    token: Annotated[str, Query()],
):
    try:
        # 1. Autenticación antes de la aceptación (usando el token de la query)
        current_user = await get_current_active_user_ws(token=token)
        
        # 2. Aceptar la conexión si el usuario es válido
        await websocket.accept()
        
        user_id = current_user.get("user_id")
        username = current_user.get("username")
        print(f"[{user_id}] WebSocket conectado.")

        # 3. Bucle principal para recibir la pregunta inicial
        while True:
            # Esperar el mensaje inicial del cliente (la pregunta)
            try:
                # Usamos receive_text/receive_bytes o receive_json si el cliente envía un JSON
                # En este ejemplo, asumimos que el cliente envía un JSON con la pregunta.
                data = await websocket.receive_json()
                
            except WebSocketDisconnect:
                break # Sale del bucle si el cliente se desconecta
            
            # 4. Procesar la pregunta (validación Pydantic)
            try:
                question_data = Question(**data)
            except Exception:
                await websocket.send_text("ERROR: Formato de pregunta JSON inválido.")
                continue

            user_question = question_data.question
            print(f"[{user_id}] Pregunta recibida: '{user_question[:50]}...'")

            # 5. Lógica de Llamada a Claude y Streaming
            
            # --- Aquí Integras tu Cliente Claude API para streaming ---
            
            # Simulación de respuesta en tiempo real:
            simulated_response = (
                f"Respuesta de la Máquina Orquestadora ({CLAUDE_MODEL}) para {username}: "
                f"El análisis de '{user_question}' está en curso. "
                "Confirmando la integración de precios y control de margen con éxito. "
                "Transmitiendo resultados en fragmentos..."
            )
            
            # 6. Transmitir el resultado (streaming)
            for word in simulated_response.split():
                if websocket.client_state == WebSocketState.DISCONNECTED:
                    break
                
                await websocket.send_text(word + " ")
                await asyncio.sleep(0.05) # Pausa para simular el tiempo de respuesta del LLM

            # Mensaje de finalización
            await websocket.send_text("\n--- FIN DEL PROCESO DE ORQUESTACIÓN ---")

    except WebSocketDisconnect:
        # Manejo de la desconexión
        print(f"[{user_id}] Cliente desconectado.")
    except Exception as e:
        # Errores de autenticación o internos
        if websocket.client_state != WebSocketState.DISCONNECTED:
            await websocket.close()
        print(f"Error crítico en WS para {token}: {e}")
