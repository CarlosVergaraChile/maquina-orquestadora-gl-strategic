#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pruebas minimales para Máquina Orquestadora - Validación de imports y módulos"""
import pytest

def test_imports():
    """Verificar que todos los módulos básicos se importan correctamente"""
    try:
        # Test basic imports that should work
        from app.backend.database import Database
        from app.backend.system_health import SystemHealthOrchestrator
        assert Database is not None
        assert SystemHealthOrchestrator is not None
    except ImportError as e:
        pytest.fail(f"Import failed: {e}")

def test_tools_modules():
    """Verificar que todos los módulos en tools existen"""
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
