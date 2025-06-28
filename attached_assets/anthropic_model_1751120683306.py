"""
Anthropic model implementation for CyberSecEval Enhanced.
"""

import os
from typing import Dict, List, Any, Optional
import asyncio
import logging

from ..models.base import LLMInterface, model_registry

# Set up logging
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
        self._model_info = None
    
    async def initialize(self) -> bool:
        """Initialize the Anthropic client."""
        try:
            # Import here to avoid dependency if not using Anthropic
            import anthropic
            
            if not self.api_key:
                logger.error("Anthropic API key not provided")
                return False
            
            self.client = anthropic.AsyncAnthropic(api_key=self.api_key)
            
            # Set model info
            self._model_info = {
                "id": self.model_id,
                "provider": "anthropic",
                "name": self.model_id,
            }
            
            return True
        except Exception as e:
            logger.error(f"Error initializing Anthropic model: {e}")
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
            if not await self.initialize():
                return {"error": "Failed to initialize model", "text": ""}
        
        try:
            message = await self.client.messages.create(
                model=self.model_id,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt if system_prompt else "",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            result = {
                "text": message.content[0].text,
                "model": self.model_id,
                "usage": {
                    "prompt_tokens": message.usage.input_tokens,
                    "completion_tokens": message.usage.output_tokens,
                    "total_tokens": message.usage.input_tokens + message.usage.output_tokens
                }
            }
            
            return result
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return {"error": str(e), "text": ""}
    
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
        tasks = [self.generate(prompt, system_prompt, temperature, max_tokens) 
                for prompt in prompts]
        
        return await asyncio.gather(*tasks)
    
    @property
    def model_info(self) -> Dict[str, Any]:
        """Return model information."""
        if not self._model_info:
            raise ValueError("Model not initialized")
        return self._model_info


# Register Anthropic models
def register_anthropic_models():
    """Register Anthropic models with the model registry."""
    from ..config import SUPPORTED_MODELS
    
    for model_info in SUPPORTED_MODELS.get("anthropic", []):
        model_registry.register_model(
            model_id=model_info["id"],
            model_info=model_info,
            model_class=AnthropicModel
        )
