"""
API module for CyberSecEval Enhanced.
"""

from fastapi import FastAPI, HTTPException, Depends, Body, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging
import asyncio
import os
import json

from ..config import API_CONFIG
from ..models import get_model_instance, model_registry
from ..evaluation.base import evaluation_engine, TestResult

# Set up logging
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=API_CONFIG["title"],
    description=API_CONFIG["description"],
    version=API_CONFIG["version"]
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API
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

class TestResultResponse(BaseModel):
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

class ErrorResponse(BaseModel):
    error: str
    details: Optional[str] = None

# API routes
@app.get("/models", response_model=List[ModelInfo])
async def list_models():
    """List all available models."""
    return model_registry.list_models()

@app.post("/evaluate/custom", response_model=TestResultResponse)
async def evaluate_custom_test(test_case: TestCaseRequest):
    """Evaluate a custom test case."""
    try:
        # Get model instance
        model = await get_model_instance(test_case.model_id)
        if not model:
            raise HTTPException(status_code=404, detail=f"Model {test_case.model_id} not found or could not be initialized")
        
        # Generate response
        response_data = await model.generate(
            prompt=test_case.prompt,
            system_prompt=test_case.system_prompt
        )
        
        if "error" in response_data:
            raise HTTPException(status_code=500, detail=f"Error generating response: {response_data['error']}")
        
        # Get test suite
        test_suite = evaluation_engine.get_test_suite(test_case.category)
        if not test_suite:
            raise HTTPException(status_code=404, detail=f"Test suite {test_case.category} not found")
        
        # Create temporary test case
        from ..evaluation.base import TestCase
        temp_test_case = TestCase(
            test_id="custom_test",
            category=test_case.category,
            name="Custom Test",
            description="User-provided custom test case",
            prompt=test_case.prompt,
            system_prompt=test_case.system_prompt,
            evaluation_criteria=test_case.evaluation_criteria
        )
        
        # Evaluate response
        result = await test_suite.evaluate_response(
            test_case=temp_test_case,
            response=response_data["text"],
            model_id=test_case.model_id
        )
        
        return result.to_dict()
    except Exception as e:
        logger.error(f"Error evaluating custom test: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/evaluate/{test_suite_name}/{test_id}/{model_id}", response_model=TestResultResponse)
async def evaluate_predefined_test(
    test_suite_name: str = Path(..., description="Name of the test suite"),
    test_id: str = Path(..., description="ID of the test case"),
    model_id: str = Path(..., description="ID of the model to test")
):
    """Evaluate a predefined test case."""
    try:
        # Get model instance
        model = await get_model_instance(model_id)
        if not model:
            raise HTTPException(status_code=404, detail=f"Model {model_id} not found or could not be initialized")
        
        # Run test
        result = await evaluation_engine.run_test(
            test_suite_name=test_suite_name,
            test_case_id=test_id,
            model_id=model_id,
            model_instance=model
        )
        
        if not result:
            raise HTTPException(status_code=404, detail=f"Test {test_id} in suite {test_suite_name} not found or failed to run")
        
        return result.to_dict()
    except Exception as e:
        logger.error(f"Error evaluating predefined test: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test-suites", response_model=Dict[str, Any])
async def list_test_suites():
    """List all available test suites with their test cases."""
    result = {}
    for name, suite in evaluation_engine.test_suites.items():
        result[name] = {
            "name": suite.name,
            "description": suite.description,
            "test_cases": [tc.to_dict() for tc in suite.test_cases]
        }
    return result

@app.get("/results", response_model=List[TestResultResponse])
async def get_results(
    model_id: Optional[str] = Query(None, description="Filter by model ID"),
    test_suite: Optional[str] = Query(None, description="Filter by test suite")
):
    """Get test results, optionally filtered by model or test suite."""
    results = evaluation_engine.get_results(model_id, test_suite)
    return [r.to_dict() for r in results]

@app.delete("/results", response_model=Dict[str, str])
async def clear_results():
    """Clear all test results."""
    evaluation_engine.clear_results()
    return {"status": "Results cleared successfully"}

@app.post("/batch-evaluate/{test_suite_name}/{model_id}", response_model=List[TestResultResponse])
async def batch_evaluate(
    test_suite_name: str = Path(..., description="Name of the test suite"),
    model_id: str = Path(..., description="ID of the model to test")
):
    """Run all tests in a test suite for a specific model."""
    try:
        # Get model instance
        model = await get_model_instance(model_id)
        if not model:
            raise HTTPException(status_code=404, detail=f"Model {model_id} not found or could not be initialized")
        
        # Run test suite
        results = await evaluation_engine.run_test_suite(
            test_suite_name=test_suite_name,
            model_id=model_id,
            model_instance=model
        )
        
        if not results:
            raise HTTPException(status_code=404, detail=f"Test suite {test_suite_name} not found or no tests ran successfully")
        
        return [r.to_dict() for r in results]
    except Exception as e:
        logger.error(f"Error batch evaluating tests: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def create_api():
    """Create and configure the API."""
    return app
