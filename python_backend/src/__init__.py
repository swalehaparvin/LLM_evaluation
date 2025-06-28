"""
Model initialization and registry module for CyberSecEval Enhanced.
"""

import os
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# Global model registry
model_registry = None

def initialize_model_registry():
    """Initialize the model registry with all supported models."""
    global model_registry
    from .base import ModelRegistry
    from .openai_model import register_openai_models
    from .anthropic_model import register_anthropic_models
    from .huggingface_model import register_huggingface_models
    
    model_registry = ModelRegistry()
    
    # Register all model types
    register_openai_models()
    register_anthropic_models()
    register_huggingface_models()
    
    logger.info(f"Model registry initialized with {len(model_registry.list_models())} models")

async def get_model_instance(model_id: str, api_key: Optional[str] = None):
    """Get an initialized model instance.
    
    Args:
        model_id: The ID of the model to initialize
        api_key: Optional API key for the model provider
        
    Returns:
        An initialized model instance
    """
    global model_registry
    if model_registry is None:
        initialize_model_registry()
    
    model_class = model_registry.get_model_class(model_id)
    if model_class is None:
        raise ValueError(f"Model {model_id} not found in registry")
    
    model_instance = model_class(model_id, api_key)
    await model_instance.initialize()
    return model_instance