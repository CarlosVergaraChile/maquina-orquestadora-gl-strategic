"""Claude API Real Integration for Máquina Orquestadora GL Strategic v2.3

This module provides real integration with Anthropic's Claude API,
replacing mock responses with actual LLM calls.
"""

import os
import anthropic
from typing import Optional, Dict, Any, List, AsyncIterator
from datetime import datetime
import json
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class ModelType(str, Enum):
    """Available Claude models"""
    CLAUDE_3_OPUS = "claude-3-opus-20250219"
    CLAUDE_3_SONNET = "claude-3-5-sonnet-20241022"
    CLAUDE_3_HAIKU = "claude-3-5-haiku-20241022"


class ClaudeOrchestrator:
    """Real Claude API integration for multi-model orchestration"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: ModelType = ModelType.CLAUDE_3_SONNET,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ):
        """
        Initialize Claude orchestrator with real API
        
        Args:
            api_key: Anthropic API key (uses ANTHROPIC_API_KEY env var if not provided)
            model: Claude model version to use
            temperature: Generation temperature (0-1)
            max_tokens: Maximum tokens in response
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY environment variable not set. "
                "Please provide your API key to use Claude."
            )
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = model.value
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.conversation_history: List[Dict[str, str]] = []
        logger.info(f"Initialized Claude orchestrator with model: {self.model}")
    
    def ask(
        self,
        prompt: str,
        context: Optional[List[str]] = None,
        system_prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Send a prompt to Claude and get a real response
        
        Args:
            prompt: The user prompt
            context: Optional conversation context
            system_prompt: Optional system instructions
        
        Returns:
            Dict with response, metadata, and usage info
        """
        try:
            start_time = datetime.now()
            
            # Build messages
            messages = [
                {"role": "user", "content": prompt}
            ]
            
            # Add system prompt if provided
            system = system_prompt or self._default_system_prompt()
            
            # Call Claude API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=system,
                messages=messages,
                temperature=self.temperature,
            )
            
            end_time = datetime.now()
            latency_ms = (end_time - start_time).total_seconds() * 1000
            
            # Extract response text
            response_text = response.content[0].text if response.content else ""
            
            # Store in history
            self.conversation_history.append({"role": "user", "content": prompt})
            self.conversation_history.append({"role": "assistant", "content": response_text})
            
            return {
                "response": response_text,
                "model": self.model,
                "timestamp": datetime.now().isoformat(),
                "latency_ms": latency_ms,
                "tokens_used": response.usage.output_tokens,
                "input_tokens": response.usage.input_tokens,
                "stop_reason": response.stop_reason,
                "success": True,
            }
        except anthropic.AuthenticationError:
            logger.error("Invalid API key")
            return {
                "response": "Error: Invalid API key",
                "success": False,
                "error": "AUTHENTICATION_ERROR",
            }
        except anthropic.RateLimitError:
            logger.error("Rate limit exceeded")
            return {
                "response": "Error: Rate limit exceeded",
                "success": False,
                "error": "RATE_LIMIT",
            }
        except Exception as e:
            logger.error(f"Claude API error: {str(e)}")
            return {
                "response": f"Error: {str(e)}",
                "success": False,
                "error": "API_ERROR",
            }
    
    async def stream_ask(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
    ) -> AsyncIterator[str]:
        """
        Stream response from Claude (async)
        
        Args:
            prompt: User prompt
            system_prompt: Optional system instructions
        
        Yields:
            Response text chunks
        """
        system = system_prompt or self._default_system_prompt()
        
        with self.client.messages.stream(
            model=self.model,
            max_tokens=self.max_tokens,
            system=system,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature,
        ) as stream:
            for text in stream.text_stream:
                yield text
    
    def update_temperature(self, temperature: float) -> None:
        """Update generation temperature (0-1)"""
        if not 0 <= temperature <= 1:
            raise ValueError("Temperature must be between 0 and 1")
        self.temperature = temperature
        logger.info(f"Updated temperature to {temperature}")
    
    def update_max_tokens(self, max_tokens: int) -> None:
        """Update maximum response tokens"""
        if max_tokens < 1:
            raise ValueError("max_tokens must be positive")
        self.max_tokens = max_tokens
        logger.info(f"Updated max_tokens to {max_tokens}")
    
    def get_history(self) -> List[Dict[str, str]]:
        """Get conversation history"""
        return self.conversation_history.copy()
    
    def clear_history(self) -> None:
        """Clear conversation history"""
        self.conversation_history = []
        logger.info("Cleared conversation history")
    
    def _default_system_prompt(self) -> str:
        """Default system prompt for Claude"""
        return """You are Máquina Orquestadora, an advanced AI assistant for GL Strategic. 
You coordinate multiple AI models, analyze complex business problems, and provide 
actionable insights. Be precise, structured, and professional in your responses.

Your capabilities:
- Multi-model coordination and orchestration
- Real-time decision analysis
- Adaptive learning from interactions
- Human decision simulation

Always provide clear, well-structured responses."""


class MultiModelOrchestrator:
    """Orchestrates responses from multiple Claude instances"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize with multiple Claude instances"""
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.models = {
            "fast": ClaudeOrchestrator(
                api_key=self.api_key,
                model=ModelType.CLAUDE_3_HAIKU,
                temperature=0.5,
            ),
            "balanced": ClaudeOrchestrator(
                api_key=self.api_key,
                model=ModelType.CLAUDE_3_SONNET,
                temperature=0.7,
            ),
            "creative": ClaudeOrchestrator(
                api_key=self.api_key,
                model=ModelType.CLAUDE_3_OPUS,
                temperature=0.9,
            ),
        }
    
    def orchestrate(
        self,
        prompt: str,
        strategy: str = "balanced",
    ) -> Dict[str, Any]:
        """
        Get response from selected model strategy
        
        Args:
            prompt: User prompt
            strategy: Model strategy (fast/balanced/creative)
        
        Returns:
            Orchestrated response
        """
        if strategy not in self.models:
            raise ValueError(f"Unknown strategy: {strategy}")
        
        model = self.models[strategy]
        response = model.ask(prompt)
        response["strategy"] = strategy
        return response
    
    def orchestrate_all(
        self,
        prompt: str,
    ) -> Dict[str, Dict[str, Any]]:
        """
        Get responses from all model strategies and compare
        
        Args:
            prompt: User prompt
        
        Returns:
            Dict with responses from all strategies
        """
        responses = {}
        for strategy in self.models.keys():
            responses[strategy] = self.orchestrate(prompt, strategy)
        return responses


# Singleton instance for easy access
_orchestrator: Optional[ClaudeOrchestrator] = None


def get_orchestrator(
    api_key: Optional[str] = None,
    model: ModelType = ModelType.CLAUDE_3_SONNET,
) -> ClaudeOrchestrator:
    """Get or create global orchestrator instance"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = ClaudeOrchestrator(api_key=api_key, model=model)
    return _orchestrator


if __name__ == "__main__":
    # Example usage
    try:
        orchestrator = get_orchestrator()
        result = orchestrator.ask("What is the current status of AI in enterprise?")
        print(json.dumps(result, indent=2, default=str))
    except Exception as e:
        print(f"Error: {e}")
