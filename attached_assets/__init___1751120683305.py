"""
Model initialization and registry module for CyberSecEval Enhanced.
"""

from typing import Dict, Any, Optional
import logging

from .base import model_registry
from .openai_model import register_openai_models
from .huggingface_model import register_huggingface_models
from .anthropic_model import register_anthropic_models

# Set up logging
logger = logging.getLogger(__name__)

def initialize_model_registry():
    """Initialize the model registry with all supported models."""
    register_openai_models()
    register_huggingface_models()
    register_anthropic_models()
    
    logger.info(f"Model registry initialized with {len(model_registry.list_models())} models")

async def get_model_instance(model_id: str, api_key: Optional[str] = None):
    """Get an initialized model instance.
    
    Args:
        model_id: The ID of the model to initialize
        api_key: Optional API key for the model provider
        
    Returns:
        An initialized model instance
    """
    model_class = model_registry.get_model_class(model_id)
    if not model_class:
        logger.error(f"Model {model_id} not found in registry")
        return None
    
    model = model_class(model_id, api_key)
    success = await model.initialize()
    
    if not success:
        logger.error(f"Failed to initialize model {model_id}")
        return None
    
    return model
