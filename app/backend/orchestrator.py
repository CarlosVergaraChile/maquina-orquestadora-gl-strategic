"""Orquestador Central - Sistema de Control, Verificación y Autosuperación de IAs"""
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Any, Callable
import hashlib

logger = logging.getLogger(__name__)

class AIGovernance:
    """Sistema de Gobernanza para verificación mutua entre IAs"""
    
    def __init__(self):
        self.ai_instances = {}  # {ia_name: {config, performance, history}}
        self.consensus_threshold = 0.7  # 70% de acuerdo requerido
        self.audit_log = []
        self.anomaly_detection_enabled = True
        
    def register_ai(self, name: str, ai_type: str, validator: Callable):
        """Registra una IA en el sistema de gobernanza"""
        self.ai_instances[name] = {
            'type': ai_type,
            'validator': validator,
            'performance': {'accuracy': 0.0, 'response_time': 0, 'error_rate': 0.0},
            'health': 'healthy',
            'last_check': None,
            'consecutive_errors': 0
        }
        self._audit(f'IA registrada: {name} ({ai_type})')
    
    def verify_output(self, ai_name: str, output: Dict[str, Any]) -> Dict[str, Any]:
        """Verifica output de una IA contra otras"""
        if ai_name not in self.ai_instances:
            return {'valid': False, 'reason': 'IA no registrada'}
        
        # 1. VALIDACIÓN INTERNA
        validator = self.ai_instances[ai_name]['validator']
        internal_check = validator(output)
        
        if not internal_check['valid']:
            self._handle_invalid_output(ai_name, output, internal_check)
            return internal_check
        
        # 2. VALIDACIÓN CRUZADA (si hay más IAs)
        if len(self.ai_instances) > 1:
            cross_validation = self._cross_validate(ai_name, output)
            if cross_validation['anomaly_detected']:
                self._handle_anomaly(ai_name, output, cross_validation)
                return {'valid': False, 'reason': 'Anomalía detectada', 'details': cross_validation}
        
        return {'valid': True, 'confidence': 0.95}
    
    def _cross_validate(self, source_ai: str, output: Dict) -> Dict:
        """Valida cruzada: otras IAs verifican el output"""
        validations = []
        
        for ia_name, ia_config in self.ai_instances.items():
            if ia_name == source_ai:
                continue
            
            # Cada IA verifica de forma independiente
            result = ia_config['validator'](output)
            validations.append(result['valid'])
        
        if not validations:
            return {'anomaly_detected': False}
        
        agreement_rate = sum(validations) / len(validations)
        anomaly = agreement_rate < self.consensus_threshold
        
        return {
            'anomaly_detected': anomaly,
            'agreement_rate': agreement_rate,
            'required_threshold': self.consensus_threshold
        }
    
    def _handle_invalid_output(self, ai_name: str, output: Dict, check: Dict):
        """Maneja output inválido de una IA"""
        self.ai_instances[ai_name]['consecutive_errors'] += 1
        
        if self.ai_instances[ai_name]['consecutive_errors'] >= 3:
            self.ai_instances[ai_name]['health'] = 'degraded'
            self._audit(f'ALERTA: {ai_name} entra en modo degradado (3+ errores)')
            self._attempt_recovery(ai_name)
    
    def _handle_anomaly(self, ai_name: str, output: Dict, anomaly_info: Dict):
        """Maneja anomalías detectadas"""
        self._audit(f'ANOMALÍA: {ai_name} - Consenso: {anomaly_info["agreement_rate"]:.2%}')
        
        # Estrategia: rollback o request feedback
        if anomaly_info['agreement_rate'] < 0.3:  # Muy diferente
            self._audit(f'ROLLBACK: {ai_name} - Desacuerdo severo')
        else:
            self._audit(f'FEEDBACK: {ai_name} - Requiere revisión (consenso bajo)')
    
    def _attempt_recovery(self, ai_name: str):
        """Intenta recuperar una IA en modo degradado"""
        self.ai_instances[ai_name]['consecutive_errors'] = 0
        self._audit(f'RECOVERY: Reiniciando {ai_name}')

class SelfExamination:
    """Sistema de Autoexamen y Autosuperación"""
    
    def __init__(self):
        self.performance_history = []  # [{timestamp, metric, value}]
        self.error_patterns = {}
        self.improvement_targets = []
        self.learning_rate = 0.1
        
    def analyze_performance(self, metrics: Dict[str, float]) -> Dict[str, Any]:
        """Analiza su propio desempeño"""
        timestamp = datetime.now().isoformat()
        
        # Guardar métricas
        for metric_name, value in metrics.items():
            self.performance_history.append({
                'timestamp': timestamp,
                'metric': metric_name,
                'value': value
            })
        
        # Detectar tendencias
        trends = self._detect_trends()
        
        # Auto-diagnóstico
        diagnosis = self._self_diagnose(trends)
        
        return {
            'timestamp': timestamp,
            'trends': trends,
            'diagnosis': diagnosis,
            'improvement_plan': self._generate_improvement_plan(diagnosis)
        }
    
    def _detect_trends(self) -> Dict[str, str]:
        """Detecta tendencias en el desempeño"""
        trends = {}
        
        # Agrupar por métrica
        metrics_by_type = {}
        for entry in self.performance_history[-10:]:  # Últimas 10 muestras
            metric = entry['metric']
            if metric not in metrics_by_type:
                metrics_by_type[metric] = []
            metrics_by_type[metric].append(entry['value'])
        
        # Analizar cada métrica
        for metric, values in metrics_by_type.items():
            if len(values) < 2:
                trends[metric] = 'insufficient_data'
                continue
            
            avg_change = (values[-1] - values[0]) / values[0] if values[0] != 0 else 0
            
            if avg_change > 0.1:
                trends[metric] = 'improving'
            elif avg_change < -0.1:
                trends[metric] = 'declining'
            else:
                trends[metric] = 'stable'
        
        return trends
    
    def _self_diagnose(self, trends: Dict[str, str]) -> Dict[str, Any]:
        """Autodiagnóstico basado en tendencias"""
        issues = []
        strengths = []
        
        for metric, trend in trends.items():
            if trend == 'declining':
                issues.append(f'{metric} en declive')
            elif trend == 'improving':
                strengths.append(f'{metric} mejorando')
        
        return {'issues': issues, 'strengths': strengths}
    
    def _generate_improvement_plan(self, diagnosis: Dict) -> List[str]:
        """Genera plan de mejora basado en autodiagnóstico"""
        plan = []
        
        for issue in diagnosis['issues']:
            if 'response_time' in issue:
                plan.append('Optimizar latencia: revisar algoritmo de procesamiento')
            elif 'accuracy' in issue:
                plan.append('Mejorar precisión: aumentar datos de entrenamiento')
            elif 'error_rate' in issue:
                plan.append('Reducir errores: implementar validaciones adicionales')
        
        return plan

class Orchestrator:
    """Orquestador Central - Coordina IAs, Gobernanza y Autosuperación"""
    
    def __init__(self):
        self.governance = AIGovernance()
        self.self_exam = SelfExamination()
        self.operational_log = []
        self.deployed_at = datetime.now()
        
    def process_request(self, user_input: str, ia_chain: List[Callable]) -> Dict[str, Any]:
        """Procesa request a través de la cadena de IAs"""
        request_id = hashlib.md5(f'{user_input}{time.time()}'.encode()).hexdigest()[:8]
        start_time = time.time()
        
        results = []
        for ia_func in ia_chain:
            ia_output = ia_func(user_input)
            ia_name = ia_func.__name__
            
            # Verificación
            verification = self.governance.verify_output(ia_name, {'output': ia_output})
            
            if not verification['valid']:
                logger.warning(f'[{request_id}] Output inválido de {ia_name}: {verification}')
                continue
            
            results.append({'ia': ia_name, 'output': ia_output})
        
        elapsed = time.time() - start_time
        
        # Recopilar métricas
        metrics = {
            'response_time': elapsed,
            'ias_executed': len(results),
            'success_rate': len(results) / len(ia_chain) if ia_chain else 0
        }
        
        # Autoexamen
        self_analysis = self.self_exam.analyze_performance(metrics)
        
        return {
            'request_id': request_id,
            'results': results,
            'metrics': metrics,
            'self_analysis': self_analysis,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_health_report(self) -> Dict[str, Any]:
        """Reporte de salud del sistema"""
        return {
            'timestamp': datetime.now().isoformat(),
            'uptime_seconds': (datetime.now() - self.deployed_at).total_seconds(),
            'ias_registered': len(self.governance.ai_instances),
            'governance_status': {name: config['health'] for name, config in self.governance.ai_instances.items()},
            'performance_trend': self.self_exam._detect_trends(),
            'audit_log_size': len(self.governance.audit_log)
        }

# Instancia global
orchestrator = Orchestrator()
