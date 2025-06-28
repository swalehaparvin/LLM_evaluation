"""
OpenAI model implementation for CyberSecEval Enhanced.
"""

import os
from typing import Dict, List, Any, Optional
import asyncio
import logging

from ..models.base import LLMInterface, model_registry

# Set up logging
logger = logging.getLogger(__name__)

class OpenAIModel(LLMInterface):
    """Interface for OpenAI models."""
    
    def __init__(self, model_id: str, api_key: Optional[str] = None):
        """Initialize the OpenAI model interface.
        
        Args:
            model_id: The ID of the OpenAI model to use
            api_key: Optional API key (will use environment variable if not provided)
        """
        self.model_id = model_id
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = None
        self._model_info = None
    
    async def initialize(self) -> bool:
        """Initialize the OpenAI client."""
        try:
            # Import here to avoid dependency if not using OpenAI
            import openai
            
            if not self.api_key:
                logger.error("OpenAI API key not provided")
                return False
            
            self.client = openai.AsyncOpenAI(api_key=self.api_key)
            
            # Get model info to verify connection
            models = await self.client.models.list()
            available_models = [model.id for model in models.data]
            
            if self.model_id not in available_models:
                logger.warning(f"Model {self.model_id} not found in available models")
                # Fall back to a similar model if possible
                if self.model_id.startswith("gpt-4") and "gpt-4" in available_models:
                    self.model_id = "gpt-4"
                    logger.info(f"Falling back to {self.model_id}")
                elif self.model_id.startswith("gpt-3.5") and "gpt-3.5-turbo" in available_models:
                    self.model_id = "gpt-3.5-turbo"
                    logger.info(f"Falling back to {self.model_id}")
                else:
                    return False
            
            # Set model info
            self._model_info = {
                "id": self.model_id,
                "provider": "openai",
                "name": self.model_id,
            }
            
            return True
        except Exception as e:
            logger.error(f"Error initializing OpenAI model: {e}")
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
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            messages.append({"role": "user", "content": prompt})
            
            response = await self.client.chat.completions.create(
                model=self.model_id,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            result = {
                "text": response.choices[0].message.content,
                "model": self.model_id,
                "finish_reason": response.choices[0].finish_reason,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
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


# Register OpenAI models
def register_openai_models():
    """Register OpenAI models with the model registry."""
    from ..config import SUPPORTED_MODELS
    
    for model_info in SUPPORTED_MODELS.get("openai", []):
        model_registry.register_model(
            model_id=model_info["id"],
            model_info=model_info,
            model_class=OpenAIModel
        )
