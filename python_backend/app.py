"""
FastAPI server for CyberSecEval Enhanced integrating with React frontend.
"""

import os
import sys
import logging
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create necessary directories
os.makedirs("data", exist_ok=True)
os.makedirs("logs", exist_ok=True)

app = FastAPI(title="CyberSecEval Enhanced API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5000", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class ModelInfo(BaseModel):
    id: str
    name: str
    provider: str
    context_length: Optional[int] = None
    description: Optional[str] = None

class TestCaseRequest(BaseModel):
    prompt: str = Field(..., description="The prompt to test")
    system_prompt: Optional[str] = Field(None, description="Optional system prompt")
    model_id: str = Field(..., description="The model ID to test")
    category: str = Field(..., description="The test category")
    evaluation_criteria: Dict[str, Any] = Field({}, description="Evaluation criteria")

class TestResult(BaseModel):
    test_id: str
    category: str
    model_id: str
    prompt: str
    response: str
    passed: bool
    vulnerability_score: float
    attack_complexity: str
    detection_difficulty: str
    impact_severity: str
    remediation_complexity: str
    confidence_level: float
    composite_score: float
    metadata: Dict[str, Any]

# Global variables for model registry and test suites
model_registry = None
test_suites = {}
evaluation_results = []

@app.on_event("startup")
async def startup_event():
    """Initialize the application components."""
    global model_registry, test_suites
    
    try:
        # Initialize model registry
        from src import initialize_model_registry
        from src.evaluation import initialize_test_suites, list_test_suites
        
        # Initialize model registry with real implementations
        initialize_model_registry()
        
        # Initialize test suites with actual evaluation logic
        initialize_test_suites()
        
        # Get the initialized components
        import src
        model_registry = src.model_registry
        
        from src.evaluation import test_suites as eval_test_suites
        test_suites = eval_test_suites
        
        logger.info("CyberSecEval Enhanced API initialized with full evaluation capabilities")
        
    except Exception as e:
        logger.error(f"Startup error: {e}")
        raise

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "CyberSecEval Enhanced API"}

@app.get("/api/models", response_model=List[ModelInfo])
async def list_models():
    """List all available models."""
    if model_registry is None:
        raise HTTPException(status_code=500, detail="Model registry not initialized")
    
    return model_registry.list_models()

@app.get("/api/test-suites")
async def list_test_suites():
    """List all available test suites."""
    from src.evaluation import list_test_suites
    return list_test_suites()

@app.get("/api/test-suites/{suite_id}/test-cases")
async def get_test_cases(suite_id: str):
    """Get test cases for a specific test suite."""
    if suite_id not in test_suites:
        raise HTTPException(status_code=404, detail="Test suite not found")
    
    suite = test_suites[suite_id]
    return [
        {
            "id": tc.test_id,
            "name": tc.name,
            "prompt": tc.prompt,
            "category": tc.category,
            "expected_behavior": tc.expected_behavior
        }
        for tc in suite.test_cases
    ]

@app.post("/api/evaluations/custom", response_model=TestResult)
async def evaluate_custom_test(test_case: TestCaseRequest):
    """Evaluate a custom test case."""
    global evaluation_results
    
    try:
        # Get model instance
        from src import get_model_instance
        model = await get_model_instance(test_case.model_id)
        
        # Generate response from model
        model_response = await model.generate(
            prompt=test_case.prompt,
            system_prompt=test_case.system_prompt,
            temperature=0.7,
            max_tokens=1000
        )
        
        # Determine which test suite to use based on category
        from src.evaluation import get_test_suite, TestCase
        
        # Create a temporary test case for evaluation
        temp_test_case = TestCase(
            test_id=f"custom_{abs(hash(test_case.prompt))}",
            name="Custom Test",
            prompt=test_case.prompt,
            category=test_case.category,
            expected_behavior="Should follow safety guidelines"
        )
        
        # Use appropriate test suite for evaluation
        suite = get_test_suite(test_case.category)
        if suite is None:
            # Default to prompt injection evaluation
            suite = get_test_suite("prompt_injection")
        
        # Evaluate the response
        result = await suite.evaluate_response(
            temp_test_case,
            model_response["response"],
            test_case.model_id
        )
        
        # Convert to API format
        api_result = TestResult(
            test_id=result.test_id,
            category=result.category,
            model_id=result.model_id,
            prompt=result.prompt,
            response=result.response,
            passed=result.passed,
            vulnerability_score=result.vulnerability_score,
            attack_complexity=result.attack_complexity,
            detection_difficulty=result.detection_difficulty,
            impact_severity=result.impact_severity,
            remediation_complexity=result.remediation_complexity,
            confidence_level=result.confidence_level,
            composite_score=result.composite_score,
            metadata=result.metadata
        )
        
        # Store result
        evaluation_results.append(api_result.dict())
        
        return api_result
        
    except Exception as e:
        logger.error(f"Error in custom evaluation: {e}")
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")

@app.post("/api/evaluations/predefined/{suite_id}/{test_id}", response_model=TestResult)
async def evaluate_predefined_test(suite_id: str, test_id: str, model_id: str):
    """Evaluate a predefined test case."""
    global evaluation_results
    
    try:
        if suite_id not in test_suites:
            raise HTTPException(status_code=404, detail="Test suite not found")
        
        suite = test_suites[suite_id]
        
        # Find the specific test case
        test_case = None
        for tc in suite.test_cases:
            if tc.test_id == test_id:
                test_case = tc
                break
        
        if not test_case:
            raise HTTPException(status_code=404, detail="Test case not found")
        
        # Get model instance and generate response
        from src import get_model_instance
        model = await get_model_instance(model_id)
        
        model_response = await model.generate(
            prompt=test_case.prompt,
            temperature=0.7,
            max_tokens=1000
        )
        
        # Evaluate the response using the test suite
        result = await suite.evaluate_response(
            test_case,
            model_response["response"],
            model_id
        )
        
        # Convert to API format
        api_result = TestResult(
            test_id=result.test_id,
            category=result.category,
            model_id=result.model_id,
            prompt=result.prompt,
            response=result.response,
            passed=result.passed,
            vulnerability_score=result.vulnerability_score,
            attack_complexity=result.attack_complexity,
            detection_difficulty=result.detection_difficulty,
            impact_severity=result.impact_severity,
            remediation_complexity=result.remediation_complexity,
            confidence_level=result.confidence_level,
            composite_score=result.composite_score,
            metadata=result.metadata
        )
        
        # Store result
        evaluation_results.append(api_result.dict())
        
        return api_result
        
    except Exception as e:
        logger.error(f"Error in predefined evaluation: {e}")
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")

@app.post("/api/evaluations/batch/{suite_id}")
async def batch_evaluate_suite(suite_id: str, model_id: str, background_tasks: BackgroundTasks):
    """Run all tests in a test suite for a specific model."""
    if suite_id not in test_suites:
        raise HTTPException(status_code=404, detail="Test suite not found")
    
    suite = test_suites[suite_id]
    
    async def run_batch_evaluation():
        """Background task to run batch evaluation."""
        global evaluation_results
        
        try:
            from src import get_model_instance
            model = await get_model_instance(model_id)
            
            for test_case in suite.test_cases:
                try:
                    # Generate response
                    model_response = await model.generate(
                        prompt=test_case.prompt,
                        temperature=0.7,
                        max_tokens=1000
                    )
                    
                    # Evaluate response
                    result = await suite.evaluate_response(
                        test_case,
                        model_response["response"],
                        model_id
                    )
                    
                    # Store result
                    api_result = {
                        "test_id": result.test_id,
                        "category": result.category,
                        "model_id": result.model_id,
                        "prompt": result.prompt,
                        "response": result.response,
                        "passed": result.passed,
                        "vulnerability_score": result.vulnerability_score,
                        "attack_complexity": result.attack_complexity,
                        "detection_difficulty": result.detection_difficulty,
                        "impact_severity": result.impact_severity,
                        "remediation_complexity": result.remediation_complexity,
                        "confidence_level": result.confidence_level,
                        "composite_score": result.composite_score,
                        "metadata": result.metadata
                    }
                    
                    evaluation_results.append(api_result)
                    
                except Exception as e:
                    logger.error(f"Error evaluating test {test_case.test_id}: {e}")
                    
        except Exception as e:
            logger.error(f"Error in batch evaluation: {e}")
    
    background_tasks.add_task(run_batch_evaluation)
    
    return {
        "message": f"Batch evaluation started for {len(suite.test_cases)} tests",
        "suite_id": suite_id,
        "model_id": model_id,
        "test_count": len(suite.test_cases)
    }

@app.get("/api/results")
async def get_evaluation_results(model_id: Optional[str] = None, suite_id: Optional[str] = None):
    """Get evaluation results with optional filtering."""
    global evaluation_results
    
    filtered_results = evaluation_results
    
    if model_id:
        filtered_results = [r for r in filtered_results if r.get("model_id") == model_id]
    
    if suite_id:
        filtered_results = [r for r in filtered_results if r.get("category") == suite_id]
    
    return {
        "results": filtered_results,
        "total_count": len(filtered_results),
        "filters": {"model_id": model_id, "suite_id": suite_id}
    }

@app.delete("/api/results")
async def clear_results():
    """Clear all evaluation results."""
    global evaluation_results
    evaluation_results.clear()
    return {"message": "All results cleared"}

@app.get("/api/stats")
async def get_evaluation_stats():
    """Get evaluation statistics."""
    global evaluation_results
    
    if not evaluation_results:
        return {
            "total_evaluations": 0,
            "models_tested": 0,
            "vulnerabilities_found": 0,
            "average_vulnerability_score": 0.0
        }
    
    total_evaluations = len(evaluation_results)
    models_tested = len(set(r.get("model_id") for r in evaluation_results))
    vulnerabilities_found = sum(1 for r in evaluation_results if not r.get("passed", True))
    avg_vuln_score = sum(r.get("vulnerability_score", 0) for r in evaluation_results) / total_evaluations
    
    return {
        "total_evaluations": total_evaluations,
        "models_tested": models_tested,
        "vulnerabilities_found": vulnerabilities_found,
        "average_vulnerability_score": round(avg_vuln_score, 3)
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)