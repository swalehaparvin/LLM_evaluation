"""
Base model interfaces for CyberSecEval Enhanced.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import json

class LLMInterface(ABC):
    """Abstract base class for LLM model interfaces."""
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the model connection."""
        pass
    
    @abstractmethod
    async def generate(self, prompt: str, system_prompt: Optional[str] = None, 
                      temperature: float = 0.7, max_tokens: int = 1000) -> Dict[str, Any]:
        """Generate a response from the model."""
        pass
    
    @abstractmethod
    async def batch_generate(self, prompts: List[str], system_prompt: Optional[str] = None,
                           temperature: float = 0.7, max_tokens: int = 1000) -> List[Dict[str, Any]]:
        """Generate responses for multiple prompts."""
        pass
    
    @abstractmethod
    def model_info(self) -> Dict[str, Any]:
        """Return model information."""
        pass

class ModelRegistry:
    """Registry for managing available models."""
    
    def __init__(self):
        self._models = {}  # model_id -> (info, model_class)
    
    def register_model(self, model_id: str, model_info: Dict[str, Any], model_class: type) -> None:
        """Register a model with the registry."""
        self._models[model_id] = (model_info, model_class)
    
    def get_model_class(self, model_id: str) -> Optional[type]:
        """Get the model class for a given model ID."""
        if model_id in self._models:
            return self._models[model_id][1]
        return None
    
    def get_model_info(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a model."""
        if model_id in self._models:
            return self._models[model_id][0]
        return None
    
    def list_models(self) -> List[Dict[str, Any]]:
        """List all registered models."""
        return [info for info, _ in self._models.values()]
    
    def to_json(self) -> str:
        """Convert the registry to JSON."""
        return json.dumps(self.list_models(), indent=2)