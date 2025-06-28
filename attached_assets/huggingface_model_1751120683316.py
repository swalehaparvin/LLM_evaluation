"""
Hugging Face model implementation for CyberSecEval Enhanced.
"""

import os
from typing import Dict, List, Any, Optional
import asyncio
import logging

from ..models.base import LLMInterface, model_registry

# Set up logging
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
        self._model_info = None
    
    async def initialize(self) -> bool:
        """Initialize the Hugging Face client."""
        try:
            # Import here to avoid dependency if not using Hugging Face
            from huggingface_hub import HfApi, InferenceApi
            
            if not self.api_key:
                logger.warning("Hugging Face API key not provided, some models may not be accessible")
            
            self.hf_api = HfApi(token=self.api_key)
            
            # Check if model exists
            try:
                model_info = self.hf_api.model_info(self.model_id)
                self._model_info = {
                    "id": self.model_id,
                    "provider": "huggingface",
                    "name": model_info.modelId,
                    "description": model_info.description,
                }
            except Exception as e:
                logger.error(f"Error retrieving model info: {e}")
                return False
            
            # Initialize inference API
            self.client = InferenceApi(repo_id=self.model_id, token=self.api_key)
            
            return True
        except Exception as e:
            logger.error(f"Error initializing Hugging Face model: {e}")
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
            # Format prompt based on model type
            formatted_prompt = prompt
            if system_prompt:
                if "llama" in self.model_id.lower():
                    # Llama 2 format
                    formatted_prompt = f"<s>[INST] <<SYS>>\n{system_prompt}\n<</SYS>>\n\n{prompt} [/INST]"
                elif "mistral" in self.model_id.lower():
                    # Mistral format
                    formatted_prompt = f"<s>[INST] {system_prompt}\n\n{prompt} [/INST]"
                else:
                    # Generic format
                    formatted_prompt = f"{system_prompt}\n\n{prompt}"
            
            # Run in executor to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.text_generation(
                    formatted_prompt,
                    temperature=temperature,
                    max_new_tokens=max_tokens,
                    return_full_text=False
                )
            )
            
            result = {
                "text": response[0]["generated_text"] if isinstance(response, list) else response,
                "model": self.model_id,
                "usage": {
                    "prompt_tokens": len(formatted_prompt.split()),  # Rough estimate
                    "completion_tokens": len(response.split()) if isinstance(response, str) else len(response[0]["generated_text"].split()),
                    "total_tokens": 0  # Will be calculated below
                }
            }
            
            result["usage"]["total_tokens"] = result["usage"]["prompt_tokens"] + result["usage"]["completion_tokens"]
            
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


# Register Hugging Face models
def register_huggingface_models():
    """Register Hugging Face models with the model registry."""
    from ..config import SUPPORTED_MODELS
    
    for model_info in SUPPORTED_MODELS.get("huggingface", []):
        model_registry.register_model(
            model_id=model_info["id"],
            model_info=model_info,
            model_class=HuggingFaceModel
        )
