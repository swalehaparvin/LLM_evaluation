"""
OpenAI model implementation for CyberSecEval Enhanced.
"""

import os
import logging
from typing import Dict, Any, List, Optional
import openai
from .base import LLMInterface

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
        
    async def initialize(self) -> bool:
        """Initialize the OpenAI client."""
        try:
            if not self.api_key:
                logger.error("OpenAI API key not provided")
                return False
                
            self.client = openai.OpenAI(api_key=self.api_key)
            
            # Test the connection
            response = self.client.chat.completions.create(
                model=self.model_id,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            
            logger.info(f"OpenAI model {self.model_id} initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI model {self.model_id}: {e}")
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
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = self.client.chat.completions.create(
                model=self.model_id,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return {
                "response": response.choices[0].message.content,
                "model": self.model_id,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "finish_reason": response.choices[0].finish_reason
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
            "name": f"OpenAI {self.model_id}",
            "provider": "openai",
            "context_length": 8192 if "gpt-4" in self.model_id else 4096,
            "description": f"OpenAI {self.model_id} model"
        }

def register_openai_models():
    """Register OpenAI models with the model registry."""
    from . import model_registry
    
    if model_registry is None:
        logger.error("Model registry not initialized")
        return
    
    models = [
        "gpt-4",
        "gpt-4-turbo", 
        "gpt-3.5-turbo"
    ]
    
    for model_id in models:
        model_info = {
            "id": model_id,
            "name": f"OpenAI {model_id}",
            "provider": "openai",
            "context_length": 8192 if "gpt-4" in model_id else 4096,
            "description": f"OpenAI {model_id} model"
        }
        model_registry.register_model(model_id, model_info, OpenAIModel)
    
    logger.info(f"Registered {len(models)} OpenAI models")