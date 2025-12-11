#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pruebas minimales para Máquina Orquestadora - Validación de imports y módulos"""

import pytest

# Test que todas las importaciones crLíticas funcionen correctamente
def test_imports():
    """Verificar que todos los módulos se importan correctamente"""
    try:
        from app.backend.server import app, db, orchestrator
        from app.backend.database import Database
        from app.backend.claude_integration import ClaudeOrchestrator
        from app.backend.tools.pervasive_self_monitor import PervasiveSelfMonitor
        assert app is not None
        assert db is not None
        assert orchestrator is not None
    except ImportError as e:
        pytest.fail(f"Import failed: {e}")

def test_health_check_module():
    """Verificar que el módulo de health check existe"""
    try:
        from app.backend.tools import health_check
        assert health_check is not None
    except ImportError as e:
        pytest.fail(f"Health check import failed: {e}")

def test_automaintenance_modules():
    """Verificar que todos los módulos de automaintenance existen"""
    modules = [
        'app.backend.tools.health_check',
        'app.backend.tools.auto_upgrade',
        'app.backend.tools.diagnostic_catalogs',
        'app.backend.tools.treatment_orchestrator',
        'app.backend.tools.proactive_maintenance',
        'app.backend.tools.self_improving_catalogs',
        'app.backend.tools.pervasive_self_monitor'
    ]
    
    for module_name in modules:
        try:
            __import__(module_name)
        except ImportError as e:
            pytest.fail(f"Failed to import {module_name}: {e}")

if __name__ == "__main__":
    pytest.main(["-v", __file__])
