"""SQLAlchemy ORM models for Máquina Orquestadora.

Defines core domain models for orchestration contexts, decisions,
model responses, and human feedback with advanced ORM patterns.
"""
from datetime import datetime
from typing import Optional, List
from uuid import uuid4
from sqlalchemy import (
    Column, String, Text, DateTime, Float, Integer, JSON,
    ForeignKey, create_engine, event, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, validates, synonym
from sqlalchemy.pool import StaticPool

Base = declarative_base()

class TimestampMixin:
    """Mixin providing timestamp columns."""
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

class OrchestrationContext(Base, TimestampMixin):
    """Represents an orchestration context."""
    __tablename__ = 'orchestration_contexts'
    __table_args__ = (
        Index('idx_name', 'name'),
    )

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    
    decisions = relationship('Decision', back_populates='context', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<OrchestrationContext({self.id}, {self.name})>'

class Decision(Base, TimestampMixin):
    """Represents a decision within an orchestration context."""
    __tablename__ = 'decisions'
    __table_args__ = (
        Index('idx_context_id', 'context_id'),
        Index('idx_decision_type', 'decision_type'),
    )

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    context_id = Column(String(36), ForeignKey('orchestration_contexts.id'), nullable=False)
    decision_type = Column(String(50), nullable=False)
    metadata = Column(JSON, nullable=True)

    context = relationship('OrchestrationContext', back_populates='decisions')
    model_responses = relationship('ModelResponse', back_populates='decision', cascade='all, delete-orphan')
    human_feedback = relationship('HumanFeedback', back_populates='decision', cascade='all, delete-orphan')

    @validates('decision_type')
    def validate_decision_type(self, key, value):
        """Validate decision type format."""
        if value and not value.replace('_', '').isalnum():
            raise ValueError(f'Invalid decision type: {value}')
        return value

    def __repr__(self):
        return f'<Decision({self.id}, {self.decision_type})>'

class ModelResponse(Base, TimestampMixin):
    """Represents a model response to a decision."""
    __tablename__ = 'model_responses'
    __table_args__ = (
        Index('idx_decision_id', 'decision_id'),
        Index('idx_model_name', 'model_name'),
    )

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    decision_id = Column(String(36), ForeignKey('decisions.id'), nullable=False)
    model_name = Column(String(100), nullable=False)
    response_text = Column(Text, nullable=False)
    confidence_score = Column(Float, nullable=True)

    decision = relationship('Decision', back_populates='model_responses')

    @validates('confidence_score')
    def validate_confidence(self, key, value):
        """Validate confidence score is between 0 and 1."""
        if value is not None and (value < 0 or value > 1):
            raise ValueError('Confidence score must be between 0 and 1')
        return value

    def __repr__(self):
        return f'<ModelResponse({self.model_name})>'

class HumanFeedback(Base, TimestampMixin):
    """Represents human feedback on a decision."""
    __tablename__ = 'human_feedback'
    __table_args__ = (
        Index('idx_decision_id', 'decision_id'),
    )

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    decision_id = Column(String(36), ForeignKey('decisions.id'), nullable=False)
    feedback_text = Column(Text, nullable=False)
    rating = Column(Integer, nullable=True)

    decision = relationship('Decision', back_populates='human_feedback')

    @validates('rating')
    def validate_rating(self, key, value):
        """Validate rating is between 1 and 5."""
        if value is not None and (value < 1 or value > 5):
            raise ValueError('Rating must be between 1 and 5')
        return value

    def __repr__(self):
        return f'<HumanFeedback({self.id}, rating={self.rating})>'

def create_db_engine(database_url: str = 'sqlite:///./orchestrator.db'):
    """Create SQLAlchemy engine."""
    if 'sqlite' in database_url:
        return create_engine(
            database_url,
            connect_args={'check_same_thread': False},
            poolclass=StaticPool
        )
    return create_engine(database_url, pool_pre_ping=True)
