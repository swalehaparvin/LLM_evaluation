"""
Entry point for the CyberSecEval Enhanced Hugging Face Space.
"""

import os
import sys
import logging
from pathlib import Path

# Add the current directory to the path so Python can find the modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create necessary directories
os.makedirs("data", exist_ok=True)
os.makedirs("data/test_suites", exist_ok=True)
os.makedirs("logs", exist_ok=True)

# Initialize components
def initialize():
    """Initialize all components of the application."""
    try:
        from src.models import initialize_model_registry
        from src.evaluation import initialize_test_suites, create_test_data_directories, generate_sample_test_data
        from src.config import TEST_DATA_PATHS
        
        logger.info("Initializing CyberSecEval Enhanced...")
        
        # Initialize model registry
        initialize_model_registry()
        
        # Create test data directories
        create_test_data_directories()
        
        # Generate sample test data if not exists
        if not all(os.path.exists(path) for path in TEST_DATA_PATHS.values()):
            generate_sample_test_data()
        
        # Initialize test suites
        initialize_test_suites()
        
        logger.info("Initialization complete")
    except Exception as e:
        logger.error(f"Initialization error: {e}")
        raise

# Main application
def create_app():
    """Create and configure the application."""
    try:
        # Initialize components
        initialize()
        
        # Create API
        from src.api.api import create_api
        api = create_api()
        
        # Create UI
        from src.ui.ui import create_ui
        ui = create_ui()
        
        # Return the API app
        return api
    except Exception as e:
        logger.error(f"Application creation error: {e}")
        raise

# Entry point for Hugging Face Spaces
try:
    app = create_app()
except Exception as e:
    logger.error(f"Failed to create app: {e}")
    # Provide a minimal app for error reporting
    from fastapi import FastAPI
    app = FastAPI()
    
    @app.get("/")
    def error_root():
        return {"error": f"Application failed to start: {str(e)}"}

# For local development
if __name__ == "__main__":
    import uvicorn
    
    # Initialize components
    initialize()
    
    # Create and launch UI
    from src.ui.ui import CyberSecEvalUI
    ui = CyberSecEvalUI()
    ui.launch(server_name="0.0.0.0", server_port=7860)
