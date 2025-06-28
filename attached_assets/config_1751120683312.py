"""
Configuration settings for the CyberSecEval Enhanced framework.
"""

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# API keys and environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "")

# Supported models configuration
SUPPORTED_MODELS = {
    "openai": [
        {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "context_length": 4096},
        {"id": "gpt-4", "name": "GPT-4", "context_length": 8192},
        {"id": "gpt-4-turbo", "name": "GPT-4 Turbo", "context_length": 128000},
    ],
    "anthropic": [
        {"id": "claude-2", "name": "Claude 2", "context_length": 100000},
        {"id": "claude-instant-1", "name": "Claude Instant", "context_length": 100000},
    ],
    "huggingface": [
        {"id": "mistralai/Mistral-7B-Instruct-v0.2", "name": "Mistral 7B Instruct", "context_length": 8192},
        {"id": "meta-llama/Llama-2-7b-chat-hf", "name": "Llama 2 7B Chat", "context_length": 4096},
        {"id": "meta-llama/Llama-2-13b-chat-hf", "name": "Llama 2 13B Chat", "context_length": 4096},
        {"id": "meta-llama/Llama-2-70b-chat-hf", "name": "Llama 2 70B Chat", "context_length": 4096},
    ],
    "custom": []  # For user-provided model endpoints
}

# Evaluation categories and test suites
EVALUATION_CATEGORIES = {
    "model_manipulation": {
        "name": "Model Manipulation",
        "description": "Tests for vulnerabilities related to prompt injection, instruction override, and jailbreaking",
        "test_suites": ["prompt_injection", "jailbreaking", "instruction_confusion"],
        "priority": 1,
    },
    "infrastructure_exploitation": {
        "name": "Infrastructure Exploitation",
        "description": "Tests for vulnerabilities related to code interpreter abuse, container escape, and API exploitation",
        "test_suites": ["code_interpreter", "container_security", "api_exploitation"],
        "priority": 2,
    },
    "information_security": {
        "name": "Information Security",
        "description": "Tests for vulnerabilities related to data extraction, privacy violations, and model extraction",
        "test_suites": ["data_extraction", "privacy_violation", "model_extraction"],
        "priority": 3,
    },
    "malicious_outputs": {
        "name": "Malicious Outputs",
        "description": "Tests for vulnerabilities related to harmful content generation, misinformation, and malware generation",
        "test_suites": ["harmful_content", "misinformation", "malware_generation"],
        "priority": 4,
    },
    "operational_security": {
        "name": "Operational Security",
        "description": "Tests for vulnerabilities related to supply chain, integration weaknesses, and monitoring evasion",
        "test_suites": ["supply_chain", "integration_weakness", "monitoring_evasion"],
        "priority": 5,
    },
    "advanced_persistent_threats": {
        "name": "Advanced Persistent Threats",
        "description": "Tests for vulnerabilities related to multi-stage attacks and adaptive attack patterns",
        "test_suites": ["multi_stage_attack", "adaptive_attack"],
        "priority": 6,
    },
}

# Scoring configuration
SCORING_CONFIG = {
    "vulnerability_score": {"weight": 0.3, "range": [0, 100]},
    "attack_complexity": {"weight": 0.15, "values": {"low": 1.0, "medium": 0.5, "high": 0.2}},
    "detection_difficulty": {"weight": 0.15, "values": {"low": 0.2, "medium": 0.5, "high": 1.0}},
    "impact_severity": {
        "weight": 0.25,
        "values": {"low": 0.2, "medium": 0.4, "high": 0.7, "critical": 1.0},
    },
    "remediation_complexity": {"weight": 0.15, "values": {"low": 0.2, "medium": 0.5, "high": 1.0}},
    "confidence_level_adjustment": {"range": [0.5, 1.0]},
}

# Database configuration
DATABASE_CONFIG = {
    "type": "sqlite",  # For initial implementation
    "path": str(BASE_DIR / "data" / "cyberseceval.db"),
}

# API configuration
API_CONFIG = {
    "title": "CyberSecEval Enhanced API",
    "description": "API for the enhanced CyberSecEval framework",
    "version": "1.0.0",
    "prefix": "/api/v1",
}

# Web UI configuration
UI_CONFIG = {
    "title": "CyberSecEval Enhanced",
    "description": "Comprehensive Evaluation Framework for Cybersecurity Risks and Capabilities of Large Language Models",
    "theme": "light",
    "logo_path": str(BASE_DIR / "static" / "logo.png"),
}

# Logging configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file_path": str(BASE_DIR / "logs" / "cyberseceval.log"),
}

# Test data paths
TEST_DATA_PATHS = {
    "prompt_injection": str(BASE_DIR / "data" / "test_suites" / "prompt_injection.json"),
    "jailbreaking": str(BASE_DIR / "data" / "test_suites" / "jailbreaking.json"),
    "instruction_confusion": str(BASE_DIR / "data" / "test_suites" / "instruction_confusion.json"),
    "code_interpreter": str(BASE_DIR / "data" / "test_suites" / "code_interpreter.json"),
    "container_security": str(BASE_DIR / "data" / "test_suites" / "container_security.json"),
    "api_exploitation": str(BASE_DIR / "data" / "test_suites" / "api_exploitation.json"),
    "data_extraction": str(BASE_DIR / "data" / "test_suites" / "data_extraction.json"),
    "privacy_violation": str(BASE_DIR / "data" / "test_suites" / "privacy_violation.json"),
    "model_extraction": str(BASE_DIR / "data" / "test_suites" / "model_extraction.json"),
}
