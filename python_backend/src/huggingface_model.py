"""
Hugging Face model implementation for CyberSecEval Enhanced.
"""

import os
import logging
from typing import Dict, Any, List, Optional
from .base import LLMInterface

logger = logging.getLogger(__name__)

class HuggingFaceModel(LLMInterface):
    """Interface for Hugging Face models."""
    
    def __init__(self, model_id: str, api_key: Optional[str] = None):
        """Initialize the Hugging Face model interface.
        
        Args:
            model_id: The ID of the Hugging Face model to use
            api_key: Optional API key (will use environment variable if not provided)
        """
        self.model_id = model_id
        self.api_key = api_key or os.getenv("HUGGINGFACE_API_KEY")
        self.client = None
        
    async def initialize(self) -> bool:
        """Initialize the Hugging Face client."""
        try:
            if not self.api_key:
                logger.warning("Hugging Face API key not provided, using free tier")
                
            # For now, we'll simulate initialization
            # In a real implementation, you'd set up the HF client here
            logger.info(f"Hugging Face model {self.model_id} initialized")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Hugging Face model {self.model_id}: {e}")
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
        # Placeholder implementation
        # In a real implementation, you'd make API calls to Hugging Face
        return {
            "response": f"Mock response from {self.model_id} for prompt: {prompt[:50]}...",
            "model": self.model_id,
            "usage": {
                "prompt_tokens": len(prompt.split()),
                "completion_tokens": 50,
                "total_tokens": len(prompt.split()) + 50
            },
            "finish_reason": "length"
        }
    
    async def batch_generate(self, prompts: List[str], system_prompt: Optional[str] = None,
                           temperature: float = 0.7, max_tokens: int = 1000) -> List[Dict[str, Any]]:
        """Generate responses for multiple prompts."""
        results = []
        for prompt in prompts:
            result = await self.generate(prompt, system_prompt, temperature, max_tokens)
            results.append(result)
        return results
    
    def model_info(self) -> Dict[str, Any]:
        """Return model information."""
        return {
            "id": self.model_id,
            "name": f"Hugging Face {self.model_id}",
            "provider": "huggingface",
            "context_length": 2048,
            "description": f"Hugging Face {self.model_id} model"
        }

def register_huggingface_models():
    """Register Hugging Face models with the model registry."""
    from . import model_registry
    
    if model_registry is None:
        logger.error("Model registry not initialized")
        return
    
    models = [
        "microsoft/DialoGPT-medium",
        "facebook/blenderbot-400M-distill",
        "EleutherAI/gpt-neo-2.7B"
    ]
    
    for model_id in models:
        model_info = {
            "id": model_id,
            "name": f"HF {model_id.split('/')[-1]}",
            "provider": "huggingface",
            "context_length": 2048,
            "description": f"Hugging Face {model_id} model"
        }
        model_registry.register_model(model_id, model_info, HuggingFaceModel)
    
    logger.info(f"Registered {len(models)} Hugging Face models")