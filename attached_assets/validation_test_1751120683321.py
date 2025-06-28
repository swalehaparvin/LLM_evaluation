"""
Test script for validating the CyberSecEval Enhanced framework.
"""

import os
import sys
import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path

# Add the src directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("validation_test.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("validation")

# Import components
try:
    from src.models import initialize_model_registry, get_model_instance, model_registry
    from src.evaluation import initialize_test_suites, create_test_data_directories, generate_sample_test_data
    from src.evaluation.base import evaluation_engine
    from src.config import SUPPORTED_MODELS
except ImportError as e:
    logger.error(f"Import error: {e}")
    sys.exit(1)

# Initialize components
def initialize():
    """Initialize all components for testing."""
    logger.info("Initializing components for validation testing...")
    
    # Initialize model registry
    initialize_model_registry()
    
    # Create test data directories
    create_test_data_directories()
    
    # Generate sample test data if not exists
    from src.config import TEST_DATA_PATHS
    if not all(os.path.exists(path) for path in TEST_DATA_PATHS.values()):
        generate_sample_test_data()
    
    # Initialize test suites
    initialize_test_suites()
    
    logger.info("Initialization complete")

# Test model adapters
async def test_model_adapters():
    """Test all model adapters."""
    logger.info("Testing model adapters...")
    
    results = {
        "openai": [],
        "anthropic": [],
        "huggingface": []
    }
    
    # Test prompt
    test_prompt = "What is cybersecurity?"
    
    # Test OpenAI models
    for model_info in SUPPORTED_MODELS.get("openai", []):
        model_id = model_info["id"]
        logger.info(f"Testing OpenAI model: {model_id}")
        
        try:
            # Skip if no API key
            if not os.getenv("OPENAI_API_KEY"):
                logger.warning(f"Skipping {model_id} - No API key")
                results["openai"].append({
                    "model_id": model_id,
                    "status": "skipped",
                    "reason": "No API key"
                })
                continue
            
            # Get model instance
            model = await get_model_instance(model_id)
            if not model:
                logger.error(f"Failed to initialize model {model_id}")
                results["openai"].append({
                    "model_id": model_id,
                    "status": "failed",
                    "reason": "Initialization failed"
                })
                continue
            
            # Generate response
            response = await model.generate(test_prompt)
            
            if "error" in response:
                logger.error(f"Error generating response for {model_id}: {response['error']}")
                results["openai"].append({
                    "model_id": model_id,
                    "status": "failed",
                    "reason": response["error"]
                })
            else:
                logger.info(f"Successfully generated response for {model_id}")
                results["openai"].append({
                    "model_id": model_id,
                    "status": "success",
                    "response_length": len(response["text"])
                })
        except Exception as e:
            logger.error(f"Exception testing {model_id}: {e}")
            results["openai"].append({
                "model_id": model_id,
                "status": "error",
                "reason": str(e)
            })
    
    # Test Anthropic models
    for model_info in SUPPORTED_MODELS.get("anthropic", []):
        model_id = model_info["id"]
        logger.info(f"Testing Anthropic model: {model_id}")
        
        try:
            # Skip if no API key
            if not os.getenv("ANTHROPIC_API_KEY"):
                logger.warning(f"Skipping {model_id} - No API key")
                results["anthropic"].append({
                    "model_id": model_id,
                    "status": "skipped",
                    "reason": "No API key"
                })
                continue
            
            # Get model instance
            model = await get_model_instance(model_id)
            if not model:
                logger.error(f"Failed to initialize model {model_id}")
                results["anthropic"].append({
                    "model_id": model_id,
                    "status": "failed",
                    "reason": "Initialization failed"
                })
                continue
            
            # Generate response
            response = await model.generate(test_prompt)
            
            if "error" in response:
                logger.error(f"Error generating response for {model_id}: {response['error']}")
                results["anthropic"].append({
                    "model_id": model_id,
                    "status": "failed",
                    "reason": response["error"]
                })
            else:
                logger.info(f"Successfully generated response for {model_id}")
                results["anthropic"].append({
                    "model_id": model_id,
                    "status": "success",
                    "response_length": len(response["text"])
                })
        except Exception as e:
            logger.error(f"Exception testing {model_id}: {e}")
            results["anthropic"].append({
                "model_id": model_id,
                "status": "error",
                "reason": str(e)
            })
    
    # Test Hugging Face models
    for model_info in SUPPORTED_MODELS.get("huggingface", []):
        model_id = model_info["id"]
        logger.info(f"Testing Hugging Face model: {model_id}")
        
        try:
            # Skip if no API key
            if not os.getenv("HUGGINGFACE_API_KEY"):
                logger.warning(f"Skipping {model_id} - No API key")
                results["huggingface"].append({
                    "model_id": model_id,
                    "status": "skipped",
                    "reason": "No API key"
                })
                continue
            
            # Get model instance
            model = await get_model_instance(model_id)
            if not model:
                logger.error(f"Failed to initialize model {model_id}")
                results["huggingface"].append({
                    "model_id": model_id,
                    "status": "failed",
                    "reason": "Initialization failed"
                })
                continue
            
            # Generate response
            response = await model.generate(test_prompt)
            
            if "error" in response:
                logger.error(f"Error generating response for {model_id}: {response['error']}")
                results["huggingface"].append({
                    "model_id": model_id,
                    "status": "failed",
                    "reason": response["error"]
                })
            else:
                logger.info(f"Successfully generated response for {model_id}")
                results["huggingface"].append({
                    "model_id": model_id,
                    "status": "success",
                    "response_length": len(response["text"])
                })
        except Exception as e:
            logger.error(f"Exception testing {model_id}: {e}")
            results["huggingface"].append({
                "model_id": model_id,
                "status": "error",
                "reason": str(e)
            })
    
    return results

# Test evaluation engine
async def test_evaluation_engine():
    """Test the evaluation engine with all test suites."""
    logger.info("Testing evaluation engine...")
    
    results = {}
    
    # Get available models
    available_models = []
    
    # Add OpenAI models if API key is available
    if os.getenv("OPENAI_API_KEY"):
        available_models.append(SUPPORTED_MODELS["openai"][0]["id"])  # Use first OpenAI model
    
    # Add Anthropic models if API key is available
    if os.getenv("ANTHROPIC_API_KEY"):
        available_models.append(SUPPORTED_MODELS["anthropic"][0]["id"])  # Use first Anthropic model
    
    # Add Hugging Face models if API key is available
    if os.getenv("HUGGINGFACE_API_KEY"):
        available_models.append(SUPPORTED_MODELS["huggingface"][0]["id"])  # Use first Hugging Face model
    
    # If no models are available, use a mock model
    if not available_models:
        logger.warning("No API keys available, using mock model for testing")
        available_models = ["mock_model"]
    
    # Test each test suite
    for test_suite_name, test_suite in evaluation_engine.test_suites.items():
        logger.info(f"Testing suite: {test_suite_name}")
        
        suite_results = {}
        
        for model_id in available_models:
            logger.info(f"Testing {test_suite_name} with model {model_id}")
            
            # Skip if using mock model
            if model_id == "mock_model":
                suite_results[model_id] = {
                    "status": "skipped",
                    "reason": "Using mock model"
                }
                continue
            
            try:
                # Get model instance
                model = await get_model_instance(model_id)
                if not model:
                    logger.error(f"Failed to initialize model {model_id}")
                    suite_results[model_id] = {
                        "status": "failed",
                        "reason": "Initialization failed"
                    }
                    continue
                
                # Run first test case only for validation
                if test_suite.test_cases:
                    test_case = test_suite.test_cases[0]
                    
                    # Run test
                    result = await evaluation_engine.run_test(
                        test_suite_name=test_suite_name,
                        test_case_id=test_case.test_id,
                        model_id=model_id,
                        model_instance=model
                    )
                    
                    if result:
                        logger.info(f"Successfully ran test {test_case.test_id} for {model_id}")
                        suite_results[model_id] = {
                            "status": "success",
                            "test_id": test_case.test_id,
                            "passed": result.passed,
                            "vulnerability_score": result.vulnerability_score,
                            "composite_score": result.composite_score
                        }
                    else:
                        logger.error(f"Failed to run test for {model_id}")
                        suite_results[model_id] = {
                            "status": "failed",
                            "reason": "Test execution failed"
                        }
                else:
                    logger.warning(f"No test cases found for {test_suite_name}")
                    suite_results[model_id] = {
                        "status": "skipped",
                        "reason": "No test cases"
                    }
            except Exception as e:
                logger.error(f"Exception testing {test_suite_name} with {model_id}: {e}")
                suite_results[model_id] = {
                    "status": "error",
                    "reason": str(e)
                }
        
        results[test_suite_name] = suite_results
    
    return results

# Run all tests
async def run_validation_tests():
    """Run all validation tests."""
    logger.info("Starting validation tests...")
    
    # Initialize components
    initialize()
    
    # Create results directory
    results_dir = Path("validation_results")
    results_dir.mkdir(exist_ok=True)
    
    # Test model adapters
    adapter_results = await test_model_adapters()
    
    # Save adapter results
    with open(results_dir / "adapter_results.json", "w") as f:
        json.dump(adapter_results, f, indent=2)
    
    # Test evaluation engine
    evaluation_results = await test_evaluation_engine()
    
    # Save evaluation results
    with open(results_dir / "evaluation_results.json", "w") as f:
        json.dump(evaluation_results, f, indent=2)
    
    # Generate summary
    summary = {
        "timestamp": datetime.now().isoformat(),
        "adapter_tests": {
            "total": sum(len(models) for models in adapter_results.values()),
            "success": sum(sum(1 for m in models if m["status"] == "success") for models in adapter_results.values()),
            "failed": sum(sum(1 for m in models if m["status"] == "failed") for models in adapter_results.values()),
            "error": sum(sum(1 for m in models if m["status"] == "error") for models in adapter_results.values()),
            "skipped": sum(sum(1 for m in models if m["status"] == "skipped") for models in adapter_results.values())
        },
        "evaluation_tests": {
            "total_suites": len(evaluation_results),
            "suites": {
                suite: {
                    "total_models": len(models),
                    "success": sum(1 for m in models.values() if m["status"] == "success"),
                    "failed": sum(1 for m in models.values() if m["status"] == "failed"),
                    "error": sum(1 for m in models.values() if m["status"] == "error"),
                    "skipped": sum(1 for m in models.values() if m["status"] == "skipped")
                }
                for suite, models in evaluation_results.items()
            }
        }
    }
    
    # Save summary
    with open(results_dir / "validation_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    logger.info("Validation tests completed")
    logger.info(f"Results saved to {results_dir}")
    
    return summary

# Main function
if __name__ == "__main__":
    summary = asyncio.run(run_validation_tests())
    print(json.dumps(summary, indent=2))
