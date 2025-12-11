"""USER LIFE PROFILER - Aprende TODO sobre el usuario para asesorarlo
Integra: LinkedIn, Facebook, YouTube, Gmail, Google Drive, Calendario, etc.
"""
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class CareerProfile:
    """Perfil profesional desde LinkedIn"""
    current_role: str
    company: str
    industry: str
    years_experience: int
    skills: List[str]
    education: List[Dict]
    certifications: List[str]
    languages: List[str]
    connections: int

@dataclass
class PersonalProfile:
    """Perfil personal desde Facebook/Instagram"""
    interests: List[str]
    hobbies: List[str]
    relationship_status: str
    location: str
    friends_count: int
    groups: List[str]
    pages_followed: List[str]

@dataclass
class ContentPreferences:
    """Preferencias de contenido desde YouTube, Spotify, etc."""
    favorite_creators: List[str]
    subscribed_channels: List[str]
    watch_history: List[str]
    playlists: List[str]
    preferred_genres: List[str]
    average_watch_time: float

@dataclass
class FinancialProfile:
    """Perfil financiero desde datos de gastos, suscripciones"""
    monthly_income_estimate: float
    monthly_expenses: float
    subscriptions: List[Dict]  # {service, cost, frequency}
    financial_goals: List[str]
    investments: List[Dict]

@dataclass
class HealthProfile:
    """Perfil de salud desde Google Fit, Waze, etc."""
    fitness_level: str
    workouts_per_week: int
    sleep_average: float
    health_goals: List[str]
    dietary_preferences: List[str]

class UserLifeProfiler:
    """
    ORQUESTA DE VIDA - Aprende COMPLETAMENTE sobre el usuario
    Para poder asesorarlo en CUALQUIER aspecto de su vida
    """
    
    def __init__(self, user_email: str):
        self.user_email = user_email
        self.career_profile: Optional[CareerProfile] = None
        self.personal_profile: Optional[PersonalProfile] = None
        self.content_preferences: Optional[ContentPreferences] = None
        self.financial_profile: Optional[FinancialProfile] = None
        self.health_profile: Optional[HealthProfile] = None
        self.created_at = datetime.now()
        self.last_updated = datetime.now()
        self.daily_routine = {}
        self.goals = []
        self.fears_and_concerns = []
        self.learning_style = ""
        self.personality_traits = []
        
    async def load_linkedin_profile(self, linkedin_data: Dict) -> CareerProfile:
        """Carga perfil profesional desde LinkedIn"""
        self.career_profile = CareerProfile(
            current_role=linkedin_data.get('current_role', ''),
            company=linkedin_data.get('company', ''),
            industry=linkedin_data.get('industry', ''),
            years_experience=linkedin_data.get('years_experience', 0),
            skills=linkedin_data.get('skills', []),
            education=linkedin_data.get('education', []),
            certifications=linkedin_data.get('certifications', []),
            languages=linkedin_data.get('languages', []),
            connections=linkedin_data.get('connections', 0)
        )
        logger.info(f'✅ Perfil LinkedIn cargado: {self.career_profile.current_role}')
        return self.career_profile
    
    async def load_facebook_profile(self, facebook_data: Dict) -> PersonalProfile:
        """Carga perfil personal desde Facebook"""
        self.personal_profile = PersonalProfile(
            interests=facebook_data.get('interests', []),
            hobbies=facebook_data.get('hobbies', []),
            relationship_status=facebook_data.get('relationship_status', 'Unknown'),
            location=facebook_data.get('location', ''),
            friends_count=facebook_data.get('friends_count', 0),
            groups=facebook_data.get('groups', []),
            pages_followed=facebook_data.get('pages_followed', [])
        )
        logger.info(f'✅ Perfil Facebook cargado: {len(self.personal_profile.interests)} intereses')
        return self.personal_profile
    
    async def load_youtube_preferences(self, youtube_data: Dict) -> ContentPreferences:
        """Carga preferencias desde YouTube Premium"""
        self.content_preferences = ContentPreferences(
            favorite_creators=youtube_data.get('favorite_creators', []),
            subscribed_channels=youtube_data.get('subscribed_channels', []),
            watch_history=youtube_data.get('watch_history', []),
            playlists=youtube_data.get('playlists', []),
            preferred_genres=youtube_data.get('preferred_genres', []),
            average_watch_time=youtube_data.get('average_watch_time', 0.0)
        )
        logger.info(f'✅ Preferencias YouTube cargadas: {len(self.content_preferences.subscribed_channels)} canales')
        return self.content_preferences
    
    async def load_financial_profile(self, financial_data: Dict) -> FinancialProfile:
        """Carga perfil financiero"""
        self.financial_profile = FinancialProfile(
            monthly_income_estimate=financial_data.get('monthly_income', 0),
            monthly_expenses=financial_data.get('monthly_expenses', 0),
            subscriptions=financial_data.get('subscriptions', []),
            financial_goals=financial_data.get('financial_goals', []),
            investments=financial_data.get('investments', [])
        )
        logger.info(f'✅ Perfil financiero: ${self.financial_profile.monthly_income_estimate}/mes')
        return self.financial_profile
    
    async def load_health_profile(self, health_data: Dict) -> HealthProfile:
        """Carga perfil de salud"""
        self.health_profile = HealthProfile(
            fitness_level=health_data.get('fitness_level', 'Unknown'),
            workouts_per_week=health_data.get('workouts_per_week', 0),
            sleep_average=health_data.get('sleep_average', 0.0),
            health_goals=health_data.get('health_goals', []),
            dietary_preferences=health_data.get('dietary_preferences', [])
        )
        logger.info(f'✅ Perfil de salud: {self.health_profile.fitness_level}')
        return self.health_profile
    
    def set_daily_routine(self, routine: Dict):
        """Define rutina diaria del usuario
        Ej: {'wake_up': '6:30', 'breakfast': '7:00', 'work_start': '9:00', ...}
        """
        self.daily_routine = routine
        logger.info(f'✅ Rutina diaria registrada')
    
    def set_goals(self, goals: List[str]):
        """Define objetivos del usuario"""
        self.goals = goals
        logger.info(f'✅ {len(goals)} objetivos registrados')
    
    def set_concerns(self, concerns: List[str]):
        """Define miedos y preocupaciones"""
        self.fears_and_concerns = concerns
        logger.info(f'✅ Preocupaciones registradas')
    
    def get_complete_profile(self) -> Dict[str, Any]:
        """Retorna perfil COMPLETO del usuario"""
        return {
            'user_email': self.user_email,
            'created_at': self.created_at.isoformat(),
            'last_updated': self.last_updated.isoformat(),
            'career': asdict(self.career_profile) if self.career_profile else None,
            'personal': asdict(self.personal_profile) if self.personal_profile else None,
            'content': asdict(self.content_preferences) if self.content_preferences else None,
            'financial': asdict(self.financial_profile) if self.financial_profile else None,
            'health': asdict(self.health_profile) if self.health_profile else None,
            'daily_routine': self.daily_routine,
            'goals': self.goals,
            'concerns': self.fears_and_concerns,
            'personality': self.personality_traits
        }
    
    def get_life_summary(self) -> str:
        """Genera resumen de vida del usuario para asesoramiento"""
        summary = f"""
=== RESUMEN DE VIDA: {self.user_email} ===

💼 CARRERA:
- Rol: {self.career_profile.current_role if self.career_profile else 'N/A'}
- Compañía: {self.career_profile.company if self.career_profile else 'N/A'}
- Años experiencia: {self.career_profile.years_experience if self.career_profile else 0}
- Skills: {', '.join(self.career_profile.skills) if self.career_profile else 'N/A'}

😋 PERSONAL:
- Intereses: {', '.join(self.personal_profile.interests) if self.personal_profile else 'N/A'}
- Ubicación: {self.personal_profile.location if self.personal_profile else 'N/A'}
- Estado: {self.personal_profile.relationship_status if self.personal_profile else 'N/A'}

🎥 PREFERENCIAS:
- Canales favoritos: {', '.join(self.content_preferences.subscribed_channels[:5]) if self.content_preferences else 'N/A'}
- Géneros: {', '.join(self.content_preferences.preferred_genres) if self.content_preferences else 'N/A'}

💰 FINANZAS:
- Ingresos mensuales: ${self.financial_profile.monthly_income_estimate if self.financial_profile else 0}
- Gastos: ${self.financial_profile.monthly_expenses if self.financial_profile else 0}
- Suscripciones: {len(self.financial_profile.subscriptions) if self.financial_profile else 0}

🏋️ SALUD:
- Nivel físico: {self.health_profile.fitness_level if self.health_profile else 'N/A'}
- Entrenamientos/semana: {self.health_profile.workouts_per_week if self.health_profile else 0}

🌟 OBJETIVOS:
{chr(10).join([f'- {g}' for g in self.goals])}

🛣️ PREOCUPACIONES:
{chr(10).join([f'- {c}' for c in self.fears_and_concerns])}
        """
        return summary
    
    async def generate_personalized_advice(self, topic: str) -> str:
        """Genera asesoramiento personalizado basado en el perfil COMPLETO del usuario"""
        profile = self.get_complete_profile()
        advice = f"""
=== ASESORAMIENTO PERSONALIZADO: {topic} ===

Basado en tu perfil:
- Carrera: {self.career_profile.current_role if self.career_profile else 'N/A'}
- Objetivos: {', '.join(self.goals) if self.goals else 'No definidos'}
- Presupuesto: ${self.financial_profile.monthly_income_estimate if self.financial_profile else '?'}
- Tu estilo: {self.learning_style if self.learning_style else 'No definido'}

Recomendación:
[IA genera consejo personalizado aquí]
        """
        return advice

# Instancia global
user_profiler = None

def initialize_profiler(email: str) -> UserLifeProfiler:
    global user_profiler
    user_profiler = UserLifeProfiler(email)
    logger.info(f'✅ UserLifeProfiler inicializado para {email}')
    return user_profiler
