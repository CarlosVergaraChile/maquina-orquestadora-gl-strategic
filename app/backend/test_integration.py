#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pruebas de integración para Máquina Orquestadora v2.3

Este módulo prueba la integración completa:
- Claude API real (o fallback)
- Persistencia SQLite
- Endpoints FastAPI
- Flujo end-to-end usuario -> Claude -> BD
"""

import pytest
import asyncio
import tempfile
from pathlib import Path
from datetime import datetime

try:
    from fastapi.testclient import TestClient
except ImportError:
    pytest.skip("FastAPI not installed", allow_module_level=True)

from app.backend.server import app, db, orchestrator
from app.backend.database import Database
from app.backend.claude_integration import ClaudeOrchestrator


class TestDatabaseIntegration:
    """Pruebas de integración con la base de datos SQLite"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup para cada test"""
        # Usar BD temporal para tests
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.db_path = self.temp_db.name
        self.temp_db.close()
        self.db = Database(self.db_path)
        yield
        # Cleanup
        Path(self.db_path).unlink()
    
    def test_save_and_retrieve_messages(self):
        """Test guardar y recuperar mensajes"""
        # Guardar mensaje de usuario
        user_msg_id = self.db.save_message(
            user_id="test_user",
            role="user",
            content="Hola, ¿cómo estoy?"
        )
        assert user_msg_id is not None
        
        # Guardar respuesta del asistente
        assistant_msg_id = self.db.save_message(
            user_id="test_user",
            role="assistant",
            content="Estoy bien, gracias por preguntar!",
            emotion="happy",
            model="claude-3-5-sonnet"
        )
        assert assistant_msg_id is not None
        
        # Recuperar historial
        history = self.db.get_conversation_history(user_id="test_user")
        assert len(history) >= 2
        assert history[0]["content"] == "Estoy bien, gracias por preguntar!"
    
    def test_multiple_users_isolation(self):
        """Test aislamiento entre usuarios"""
        # Usuario 1
        self.db.save_message(
            user_id="user1",
            role="user",
            content="Pregunta del usuario 1"
        )
        
        # Usuario 2
        self.db.save_message(
            user_id="user2",
            role="user",
            content="Pregunta del usuario 2"
        )
        
        # Verificar aislamiento
        history_user1 = self.db.get_conversation_history(user_id="user1")
        history_user2 = self.db.get_conversation_history(user_id="user2")
        
        assert len(history_user1) == 1
        assert len(history_user2) == 1
        assert history_user1[0]["content"] == "Pregunta del usuario 1"
        assert history_user2[0]["content"] == "Pregunta del usuario 2"
    
    def test_metrics_generation(self):
        """Test generación de métricas"""
        # Añadir varios mensajes
        for i in range(5):
            self.db.save_message(
                user_id="test_user",
                role="user" if i % 2 == 0 else "assistant",
                content=f"Mensaje {i}"
            )
        
        # Obtener métricas
        metrics = self.db.get_metrics()
        assert metrics is not None
        assert "total_messages" in metrics or "message_count" in metrics


class TestClaudeIntegration:
    """Pruebas de integración con Claude API"""
    
    def test_orchestrator_initialization(self):
        """Test inicialización del orquestador"""
        # Orchestrator sin API key (fallback mode)
        orch = ClaudeOrchestrator(api_key="")
        assert orch is not None
        # client será None en fallback mode
        assert orch.client is None or orch.api_key == ""
    
    @pytest.mark.asyncio
    async def test_fallback_response(self):
        """Test respuesta fallback cuando no hay API key"""
        orch = ClaudeOrchestrator(api_key="")
        result = await orch.generate_response("Hola, ¿cómo estoy?")
        
        assert result is not None
        assert "response" in result
        assert "emotion" in result
        assert "model" in result
        # En fallback, el modelo debe ser "fallback-simulator"
        assert result["model"] == "fallback-simulator"


class TestServerEndpoints:
    """Pruebas de endpoints FastAPI"""
    
    @pytest.fixture(autouse=True)
    def client(self):
        """Cliente de test FastAPI"""
        return TestClient(app)
    
    def test_root_endpoint(self, client):
        """Test endpoint raíz"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "online"
        assert "version" in data
        assert "features" in data
        assert "endpoints" in data
    
    def test_health_endpoint(self, client):
        """Test endpoint health check"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "database" in data
        assert "claude_api" in data
        assert "components" in data
    
    @pytest.mark.asyncio
    async def test_ask_endpoint(self, client):
        """Test endpoint /ask"""
        response = client.post(
            "/ask",
            json={
                "text": "Hola, ¿cómo estoy?",
                "user_id": "test_user"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "emotion" in data
        assert "timestamp" in data
        assert "model" in data
    
    def test_history_endpoint(self, client):
        """Test endpoint /history"""
        # Primero hacer una pregunta
        client.post(
            "/ask",
            json={
                "text": "Test pregunta",
                "user_id": "test_user"
            }
        )
        
        # Recuperar historial
        response = client.get("/history?user_id=test_user&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert "messages" in data
        assert "count" in data
    
    def test_users_endpoint(self, client):
        """Test endpoint /users"""
        response = client.get("/users")
        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        assert "count" in data


class TestCompleteFlow:
    """Pruebas de flujo completo end-to-end"""
    
    @pytest.fixture(autouse=True)
    def client(self):
        """Cliente de test FastAPI"""
        return TestClient(app)
    
    def test_complete_conversation_flow(self, client):
        """Test flujo completo: usuario -> Claude -> BD"""
        user_id = "integration_test_user"
        
        # Paso 1: Hacer primera pregunta
        response1 = client.post(
            "/ask",
            json={
                "text": "Qué es la orquestación de IA?",
                "user_id": user_id
            }
        )
        assert response1.status_code == 200
        data1 = response1.json()
        assert data1["response"] != ""
        
        # Paso 2: Hacer segunda pregunta
        response2 = client.post(
            "/ask",
            json={
                "text": "Y cómo se relaciona con Claude API?",
                "user_id": user_id
            }
        )
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["response"] != ""
        
        # Paso 3: Verificar historial
        response_history = client.get(f"/history?user_id={user_id}")
        assert response_history.status_code == 200
        history_data = response_history.json()
        
        # Debe haber al menos 2 mensajes del usuario + 2 del asistente
        assert history_data["count"] >= 4
        
        # Paso 4: Limpiar historial
        response_clear = client.delete(f"/clear/{user_id}")
        assert response_clear.status_code == 200
        
        # Paso 5: Verificar que se limpió
        response_history_after = client.get(f"/history?user_id={user_id}")
        assert response_history_after.status_code == 200
        history_after = response_history_after.json()
        assert history_after["count"] == 0


if __name__ == "__main__":
    pytest.main(["-v", __file__])
