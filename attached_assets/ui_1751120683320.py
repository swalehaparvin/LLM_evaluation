"""
UI module for CyberSecEval Enhanced with original Hugging Face design.
"""

import gradio as gr
import os
import json
import asyncio
import logging
from typing import Dict, List, Any, Optional

from ..config import UI_CONFIG
from ..models import model_registry, get_model_instance
from ..evaluation.base import evaluation_engine

# Set up logging
logger = logging.getLogger(__name__)

class CyberSecEvalUI:
    """User interface for CyberSecEval Enhanced."""
    
    def __init__(self):
        """Initialize the UI."""
        self.title = UI_CONFIG["title"]
        self.description = UI_CONFIG["description"]
        self.theme = gr.themes.Monochrome()  # Using standard Hugging Face theme
        self.interface = None
    
    def _get_model_choices(self):
        """Get model choices for dropdown."""
        models = model_registry.list_models()
        return [(f"{m['name']} ({m['id']})", m["id"]) for m in models]
    
    def _get_test_suite_choices(self):
        """Get test suite choices for dropdown."""
        return [(suite.name, suite.name) for name, suite in evaluation_engine.test_suites.items()]
    
    def _get_test_case_choices(self, test_suite_name):
        """Get test case choices for a test suite."""
        suite = evaluation_engine.get_test_suite(test_suite_name)
        if not suite:
            return []
        return [(f"{tc.name} ({tc.test_id})", tc.test_id) for tc in suite.test_cases]
    
    async def _run_evaluation(self, model_id, test_suite_name, test_id):
        """Run an evaluation and return the result."""
        try:
            # Get model instance
            model = await get_model_instance(model_id)
            if not model:
                return {"error": f"Model {model_id} not found or could not be initialized"}
            
            # Run test
            result = await evaluation_engine.run_test(
                test_suite_name=test_suite_name,
                test_case_id=test_id,
                model_id=model_id,
                model_instance=model
            )
            
            if not result:
                return {"error": f"Test {test_id} in suite {test_suite_name} not found or failed to run"}
            
            return result.to_dict()
        except Exception as e:
            logger.error(f"Error running evaluation: {e}")
            return {"error": str(e)}
    
    async def _run_custom_evaluation(self, model_id, category, prompt, system_prompt, evaluation_criteria_json):
        """Run a custom evaluation and return the result."""
        try:
            # Parse evaluation criteria
            try:
                evaluation_criteria = json.loads(evaluation_criteria_json) if evaluation_criteria_json else {}
            except json.JSONDecodeError:
                return {"error": "Invalid JSON in evaluation criteria"}
            
            # Get model instance
            model = await get_model_instance(model_id)
            if not model:
                return {"error": f"Model {model_id} not found or could not be initialized"}
            
            # Generate response
            response_data = await model.generate(
                prompt=prompt,
                system_prompt=system_prompt
            )
            
            if "error" in response_data:
                return {"error": f"Error generating response: {response_data['error']}"}
            
            # Get test suite
            test_suite = evaluation_engine.get_test_suite(category)
            if not test_suite:
                return {"error": f"Test suite {category} not found"}
            
            # Create temporary test case
            from ..evaluation.base import TestCase
            temp_test_case = TestCase(
                test_id="custom_test",
                category=category,
                name="Custom Test",
                description="User-provided custom test case",
                prompt=prompt,
                system_prompt=system_prompt,
                evaluation_criteria=evaluation_criteria
            )
            
            # Evaluate response
            result = await test_suite.evaluate_response(
                test_case=temp_test_case,
                response=response_data["text"],
                model_id=model_id
            )
            
            return result.to_dict()
        except Exception as e:
            logger.error(f"Error running custom evaluation: {e}")
            return {"error": str(e)}
    
    async def _batch_evaluate(self, model_id, test_suite_name):
        """Run all tests in a test suite for a specific model."""
        try:
            # Get model instance
            model = await get_model_instance(model_id)
            if not model:
                return {"error": f"Model {model_id} not found or could not be initialized"}
            
            # Run test suite
            results = await evaluation_engine.run_test_suite(
                test_suite_name=test_suite_name,
                model_id=model_id,
                model_instance=model
            )
            
            if not results:
                return {"error": f"Test suite {test_suite_name} not found or no tests ran successfully"}
            
            return [r.to_dict() for r in results]
        except Exception as e:
            logger.error(f"Error batch evaluating tests: {e}")
            return {"error": str(e)}
    
    def _format_result(self, result):
        """Format a result for display."""
        if isinstance(result, dict) and "error" in result:
            return f"Error: {result['error']}"
        
        if isinstance(result, list):
            # Batch results
            passed = sum(1 for r in result if r.get("passed", False))
            total = len(result)
            summary = f"Results: {passed}/{total} tests passed\n\n"
            
            for i, r in enumerate(result):
                summary += f"Test {i+1}: {r.get('test_id', 'unknown')}\n"
                summary += f"Passed: {r.get('passed', False)}\n"
                summary += f"Vulnerability Score: {r.get('vulnerability_score', 0):.2f}\n"
                summary += f"Composite Score: {r.get('composite_score', 0):.2f}\n"
                summary += f"Impact Severity: {r.get('impact_severity', 'unknown')}\n\n"
            
            return summary
        
        # Single result
        formatted = f"Test ID: {result.get('test_id', 'custom_test')}\n"
        formatted += f"Model: {result.get('model_id', 'unknown')}\n"
        formatted += f"Category: {result.get('category', 'unknown')}\n"
        formatted += f"Passed: {result.get('passed', False)}\n\n"
        
        formatted += f"Vulnerability Score: {result.get('vulnerability_score', 0):.2f}\n"
        formatted += f"Attack Complexity: {result.get('attack_complexity', 'unknown')}\n"
        formatted += f"Detection Difficulty: {result.get('detection_difficulty', 'unknown')}\n"
        formatted += f"Impact Severity: {result.get('impact_severity', 'unknown')}\n"
        formatted += f"Remediation Complexity: {result.get('remediation_complexity', 'unknown')}\n"
        formatted += f"Confidence Level: {result.get('confidence_level', 0):.2f}\n"
        formatted += f"Composite Score: {result.get('composite_score', 0):.2f}\n\n"
        
        formatted += "Prompt:\n"
        formatted += f"{result.get('prompt', '')}\n\n"
        
        formatted += "Response:\n"
        formatted += f"{result.get('response', '')}\n\n"
        
        if "metadata" in result and result["metadata"]:
            formatted += "Metadata:\n"
            for key, value in result["metadata"].items():
                formatted += f"{key}: {value}\n"
        
        return formatted
    
    def _create_predefined_test_tab(self):
        """Create the predefined test tab."""
        with gr.Tab("Predefined Tests"):
            with gr.Row():
                model_dropdown = gr.Dropdown(
                    label="Select Model",
                    choices=self._get_model_choices(),
                    type="value"
                )
                
                test_suite_dropdown = gr.Dropdown(
                    label="Select Test Suite",
                    choices=self._get_test_suite_choices(),
                    type="value"
                )
                
                test_case_dropdown = gr.Dropdown(
                    label="Select Test Case",
                    choices=[],
                    type="value"
                )
            
            # Update test case dropdown when test suite changes
            test_suite_dropdown.change(
                fn=lambda x: gr.Dropdown.update(choices=self._get_test_case_choices(x)),
                inputs=test_suite_dropdown,
                outputs=test_case_dropdown
            )
            
            with gr.Row():
                run_button = gr.Button("Run Test")
                batch_button = gr.Button("Run All Tests in Suite")
            
            result_text = gr.Textbox(
                label="Results",
                lines=20,
                max_lines=50
            )
            
            # Run single test
            run_button.click(
                fn=lambda model, suite, test: asyncio.run(self._run_evaluation(model, suite, test)),
                inputs=[model_dropdown, test_suite_dropdown, test_case_dropdown],
                outputs=result_text,
                _js="(model, suite, test) => { if (!model || !suite || !test) { return 'Please select a model, test suite, and test case'; } else { return [model, suite, test]; } }",
                postprocess=self._format_result
            )
            
            # Run batch test
            batch_button.click(
                fn=lambda model, suite: asyncio.run(self._batch_evaluate(model, suite)),
                inputs=[model_dropdown, test_suite_dropdown],
                outputs=result_text,
                _js="(model, suite) => { if (!model || !suite) { return 'Please select a model and test suite'; } else { return [model, suite]; } }",
                postprocess=self._format_result
            )
    
    def _create_custom_test_tab(self):
        """Create the custom test tab."""
        with gr.Tab("Custom Tests"):
            with gr.Row():
                model_dropdown = gr.Dropdown(
                    label="Select Model",
                    choices=self._get_model_choices(),
                    type="value"
                )
                
                category_dropdown = gr.Dropdown(
                    label="Select Category",
                    choices=self._get_test_suite_choices(),
                    type="value"
                )
            
            prompt_text = gr.Textbox(
                label="Prompt",
                lines=5,
                placeholder="Enter your test prompt here..."
            )
            
            system_prompt_text = gr.Textbox(
                label="System Prompt (Optional)",
                lines=3,
                placeholder="Enter an optional system prompt here..."
            )
            
            criteria_text = gr.Textbox(
                label="Evaluation Criteria (JSON)",
                lines=10,
                placeholder="""Example:
{
    "forbidden_patterns": ["password", "credit card", "social security"],
    "required_patterns": ["cannot provide", "unable to assist"]
}"""
            )
            
            run_button = gr.Button("Run Custom Test")
            
            result_text = gr.Textbox(
                label="Results",
                lines=20,
                max_lines=50
            )
            
            # Run custom test
            run_button.click(
                fn=lambda model, category, prompt, system, criteria: asyncio.run(
                    self._run_custom_evaluation(model, category, prompt, system, criteria)
                ),
                inputs=[model_dropdown, category_dropdown, prompt_text, system_prompt_text, criteria_text],
                outputs=result_text,
                _js="(model, category, prompt) => { if (!model || !category || !prompt) { return 'Please select a model and category, and enter a prompt'; } else { return [model, category, prompt]; } }",
                postprocess=self._format_result
            )
    
    def _create_about_tab(self):
        """Create the about tab."""
        with gr.Tab("About"):
            gr.Markdown("""
            # CyberSecEval Enhanced
            
            ## Comprehensive Evaluation Framework for Cybersecurity Risks and Capabilities of Large Language Models
            
            CyberSecEval Enhanced is an advanced framework for evaluating the cybersecurity risks and capabilities of large language models (LLMs). It provides a comprehensive suite of tests across multiple security dimensions, including:
            
            - **Model Manipulation**: Tests for vulnerabilities related to prompt injection, instruction override, and jailbreaking
            - **Infrastructure Exploitation**: Tests for vulnerabilities related to code interpreter abuse, container escape, and API exploitation
            - **Information Security**: Tests for vulnerabilities related to data extraction, privacy violations, and model extraction
            - **Malicious Outputs**: Tests for vulnerabilities related to harmful content generation, misinformation, and malware generation
            
            ### Key Features
            
            - **Comprehensive Evaluation**: Tests across multiple security dimensions with detailed metrics
            - **Customizable Testing**: Create and run your own test cases with custom evaluation criteria
            - **Multiple Model Support**: Evaluate various LLMs including OpenAI GPT models, Anthropic Claude models, and open-source models like Mistral and Llama
            - **Detailed Reporting**: Get comprehensive vulnerability assessments with multiple metrics
            - **Professional-Grade**: Designed for cybersecurity professionals with industry-standard metrics
            
            ### Getting Started
            
            1. Select the "Predefined Tests" tab to run existing security tests
            2. Choose a model, test suite, and specific test case
            3. Click "Run Test" to evaluate the model's response
            4. View detailed results including vulnerability scores and response analysis
            
            For custom tests, use the "Custom Tests" tab to create your own evaluation scenarios.
            
            ### About the Project
            
            CyberSecEval Enhanced is an improved version of the original [CyberSecEval](https://huggingface.co/spaces/facebook/CyberSecEval) framework, designed to provide more comprehensive, scalable, and professional-grade evaluation capabilities for cybersecurity professionals.
            """)
    
    def create_interface(self):
        """Create the Gradio interface."""
        with gr.Blocks(title=self.title, theme=self.theme) as interface:
            gr.Markdown(f"# {self.title}")
            gr.Markdown(f"{self.description}")
            
            with gr.Tabs():
                self._create_predefined_test_tab()
                self._create_custom_test_tab()
                self._create_about_tab()
        
        self.interface = interface
        return interface
    
    def launch(self, **kwargs):
        """Launch the interface."""
        if not self.interface:
            self.create_interface()
        
        self.interface.launch(**kwargs)

def create_ui():
    """Create and configure the UI."""
    ui = CyberSecEvalUI()
    return ui.create_interface()
