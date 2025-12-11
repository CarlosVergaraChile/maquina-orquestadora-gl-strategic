"""Multi-model AI support for Máquina Orquestadora.

Provides abstraction for multiple AI model providers including
Claude, GPT-4, and extensible support for custom models.
"""
from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional, Dict, Any, List
import os
import aiohttp
import json
from dataclasses import dataclass
from datetime import datetime

class ModelProvider(str, Enum):
    """Supported AI model providers."""
    CLAUDE = "claude"
    GPT4 = "gpt4"
    GPT35 = "gpt-3.5"
    OPENAI = "openai"
    CUSTOM = "custom"

@dataclass
class ModelConfig:
    """Configuration for AI models."""
    provider: ModelProvider
    model_name: str
    api_key: str
    temperature: float = 0.7
    max_tokens: int = 2000
    timeout: int = 30

class BaseAIModel(ABC):
    """Base class for AI model implementations."""
    
    def __init__(self, config: ModelConfig):
        self.config = config
        self.provider = config.provider
        self.model_name = config.model_name
        
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate response from model."""
        pass
    
    @abstractmethod
    async def validate_credentials(self) -> bool:
        """Validate API credentials."""
        pass

class ClaudeModel(BaseAIModel):
    """Claude AI model implementation."""
    
    async def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate response using Claude API."""
        try:
            from anthropic import AsyncAnthropic
            
            client = AsyncAnthropic(api_key=self.config.api_key)
            message = await client.messages.create(
                model=self.config.model_name,
                max_tokens=self.config.max_tokens,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.config.temperature,
            )
            
            return {
                "content": message.content[0].text,
                "model": self.config.model_name,
                "provider": ModelProvider.CLAUDE.value,
                "usage": {
                    "input_tokens": message.usage.input_tokens,
                    "output_tokens": message.usage.output_tokens
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            raise RuntimeError(f"Claude API error: {str(e)}")
    
    async def validate_credentials(self) -> bool:
        """Validate Claude API key."""
        if not self.config.api_key:
            return False
        try:
            from anthropic import AsyncAnthropic
            client = AsyncAnthropic(api_key=self.config.api_key)
            await client.messages.create(
                model=self.config.model_name,
                max_tokens=10,
                messages=[{"role": "user", "content": "test"}]
            )
            return True
        except Exception:
            return False

class GPT4Model(BaseAIModel):
    """GPT-4 model implementation."""
    
    async def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate response using OpenAI API."""
        try:
            headers = {
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.config.model_name,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": self.config.temperature,
                "max_tokens": self.config.max_tokens
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=self.config.timeout)
                ) as response:
                    data = await response.json()
                    
                    return {
                        "content": data["choices"][0]["message"]["content"],
                        "model": self.config.model_name,
                        "provider": ModelProvider.GPT4.value,
                        "usage": data.get("usage", {}),
                        "timestamp": datetime.utcnow().isoformat()
                    }
        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {str(e)}")
    
    async def validate_credentials(self) -> bool:
        """Validate OpenAI API key."""
        if not self.config.api_key:
            return False
        try:
            headers = {
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json"
            }
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://api.openai.com/v1/models",
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    return response.status == 200
        except Exception:
            return False

class ModelFactory:
    """Factory for creating AI model instances."""
    
    _models: Dict[ModelProvider, type] = {
        ModelProvider.CLAUDE: ClaudeModel,
        ModelProvider.GPT4: GPT4Model,
    }
    
    @classmethod
    def create(cls, config: ModelConfig) -> BaseAIModel:
        """Create model instance based on config."""
        model_class = cls._models.get(config.provider)
        if not model_class:
            raise ValueError(f"Unknown provider: {config.provider}")
        return model_class(config)
    
    @classmethod
    def register(cls, provider: ModelProvider, model_class: type) -> None:
        """Register custom model provider."""
        cls._models[provider] = model_class

class MultiModelOrchestrator:
    """Orchestrates multiple AI models."""
    
    def __init__(self):
        self.models: Dict[str, BaseAIModel] = {}
        self.default_model: Optional[str] = None
    
    def add_model(self, name: str, config: ModelConfig) -> None:
        """Add model to orchestrator."""
        self.models[name] = ModelFactory.create(config)
        if not self.default_model:
            self.default_model = name
    
    async def generate(self, prompt: str, model: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Generate response using specified or default model."""
        model_name = model or self.default_model
        if not model_name or model_name not in self.models:
            raise ValueError(f"Model {model_name} not found")
        
        return await self.models[model_name].generate(prompt, **kwargs)
    
    async def generate_parallel(self, prompt: str) -> List[Dict[str, Any]]:
        """Generate responses from all models in parallel."""
        import asyncio
        tasks = [
            model.generate(prompt) for model in self.models.values()
        ]
        return await asyncio.gather(*tasks)
    
    async def validate_all(self) -> Dict[str, bool]:
        """Validate all configured models."""
        import asyncio
        results = {}
        for name, model in self.models.items():
            results[name] = await model.validate_credentials()
        return results
