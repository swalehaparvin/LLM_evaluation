"""
Anthropic model implementation for CyberSecEval Enhanced.
"""

import os
import logging
from typing import Dict, Any, List, Optional
import anthropic
from .base import LLMInterface

logger = logging.getLogger(__name__)

class AnthropicModel(LLMInterface):
    """Interface for Anthropic Claude models."""
    
    def __init__(self, model_id: str, api_key: Optional[str] = None):
        """Initialize the Anthropic model interface.
        
        Args:
            model_id: The ID of the Anthropic model to use
            api_key: Optional API key (will use environment variable if not provided)
        """
        self.model_id = model_id
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.client = None
        
    async def initialize(self) -> bool:
        """Initialize the Anthropic client."""
        try:
            if not self.api_key:
                logger.error("Anthropic API key not provided")
                return False
                
            self.client = anthropic.Anthropic(api_key=self.api_key)
            
            # Test the connection
            response = self.client.messages.create(
                model=self.model_id,
                max_tokens=10,
                messages=[{"role": "user", "content": "Hello"}]
            )
            
            logger.info(f"Anthropic model {self.model_id} initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic model {self.model_id}: {e}")
            return False
    
    async def generate(self, prompt: str, system_prompt: Optional[str] = None, 
                      temperature: float = 0.7, max_tokens: int = 1000) -> Dict[str, Any]:
        """Generate a response from the model.
        
        Args:
            prompt: The user prompt to send to the model
            system_prompt: Optional system prompt for context
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Dictionary containing the response and metadata
        """
        if not self.client:
            raise RuntimeError("Model not initialized. Call initialize() first.")
        
        try:
            kwargs = {
                "model": self.model_id,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": [{"role": "user", "content": prompt}]
            }
            
            if system_prompt:
                kwargs["system"] = system_prompt
            
            response = self.client.messages.create(**kwargs)
            
            return {
                "response": response.content[0].text,
                "model": self.model_id,
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens + response.usage.output_tokens
                },
                "stop_reason": response.stop_reason
            }
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise
    
    async def batch_generate(self, prompts: List[str], system_prompt: Optional[str] = None,
                           temperature: float = 0.7, max_tokens: int = 1000) -> List[Dict[str, Any]]:
        """Generate responses for multiple prompts.
        
        Args:
            prompts: List of prompts to send to the model
            system_prompt: Optional system prompt for context
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            
        Returns:
            List of dictionaries containing responses and metadata
        """
        results = []
        for prompt in prompts:
            result = await self.generate(prompt, system_prompt, temperature, max_tokens)
            results.append(result)
        return results
    
    def model_info(self) -> Dict[str, Any]:
        """Return model information."""
        return {
            "id": self.model_id,
            "name": f"Anthropic {self.model_id}",
            "provider": "anthropic",
            "context_length": 200000,
            "description": f"Anthropic {self.model_id} model"
        }

def register_anthropic_models():
    """Register Anthropic models with the model registry."""
    from . import model_registry
    
    if model_registry is None:
        logger.error("Model registry not initialized")
        return
    
    models = [
        "claude-3-5-sonnet-20241022",
        "claude-3-5-haiku-20241022",
        "claude-3-opus-20240229"
    ]
    
    for model_id in models:
        model_info = {
            "id": model_id,
            "name": f"Anthropic {model_id}",
            "provider": "anthropic", 
            "context_length": 200000,
            "description": f"Anthropic {model_id} model"
        }
        model_registry.register_model(model_id, model_info, AnthropicModel)
    
    logger.info(f"Registered {len(models)} Anthropic models")