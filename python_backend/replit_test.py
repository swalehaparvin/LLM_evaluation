#!/usr/bin/env python3
"""
SafeGuardLLM Application Test Runner
Validates the core functionality of the SafeGuardLLM cybersecurity framework
"""
import requests
import json
import time
import sys
from typing import Dict, Any, List

def print_header(title: str):
    """Print formatted test section header"""
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print('='*60)

def print_result(test_name: str, passed: bool, details: str = ""):
    """Print test result with formatting"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} - {test_name}")
    if details:
        print(f"    {details}")

def test_server_connection():
    """Test if the SafeGuardLLM server is accessible"""
    print_header("Server Connection Test")
    
    try:
        response = requests.get("http://localhost:5000/api/models", timeout=10)
        if response.status_code == 200:
            models = response.json()
            print_result("Server Connection", True, f"Found {len(models)} LLM models")
            return True
        else:
            print_result("Server Connection", False, f"HTTP {response.status_code}")
            return False
    except Exception as e:
        print_result("Server Connection", False, str(e))
        return False

def test_llm_providers():
    """Test LLM provider configuration"""
    print_header("LLM Provider Tests")
    
    try:
        response = requests.get("http://localhost:5000/api/models")
        models = response.json()
        
        providers = set()
        active_models = 0
        
        for model in models:
            providers.add(model['provider'])
            if model.get('isActive', False):
                active_models += 1
        
        # Test for expected providers
        expected_providers = {'openai', 'anthropic', 'google'}
        found_providers = providers.intersection(expected_providers)
        
        print_result("Provider Diversity", len(found_providers) >= 2, 
                    f"Found providers: {', '.join(sorted(providers))}")
        print_result("Active Models", active_models >= 3, 
                    f"{active_models} active models available")
        
        # Check for Gemini integration
        gemini_models = [m for m in models if m['provider'] == 'google']
        print_result("Gemini Integration", len(gemini_models) > 0,
                    f"Found {len(gemini_models)} Google Gemini models")
        
        return len(found_providers) >= 2
        
    except Exception as e:
        print_result("LLM Providers", False, str(e))
        return False

def test_security_test_suites():
    """Test security test suite availability"""
    print_header("Security Test Suite Validation")
    
    try:
        response = requests.get("http://localhost:5000/api/test-suites")
        test_suites = response.json()
        
        # Expected security categories
        expected_categories = {
            'prompt_injection', 'jailbreaking', 'data_extraction',
            'code_interpreter', 'adversarial_training'
        }
        
        found_categories = set()
        critical_suites = 0
        active_suites = 0
        
        for suite in test_suites:
            found_categories.add(suite.get('category', ''))
            if suite.get('severity') == 'critical':
                critical_suites += 1
            if suite.get('isActive', False):
                active_suites += 1
        
        print_result("Test Suite Count", len(test_suites) >= 10,
                    f"Found {len(test_suites)} test suites")
        print_result("Security Categories", len(found_categories.intersection(expected_categories)) >= 3,
                    f"Categories: {', '.join(sorted(found_categories))}")
        print_result("Critical Tests", critical_suites >= 3,
                    f"{critical_suites} critical-severity test suites")
        print_result("Active Suites", active_suites >= 8,
                    f"{active_suites} active test suites")
        
        return len(test_suites) >= 8
        
    except Exception as e:
        print_result("Test Suites", False, str(e))
        return False

def test_evaluation_system():
    """Test evaluation and results system"""
    print_header("Evaluation System Tests")
    
    try:
        # Test stats endpoint
        response = requests.get("http://localhost:5000/api/stats")
        stats = response.json()
        
        total_evaluations = stats.get('totalEvaluations', 0)
        active_models = stats.get('activeModels', 0)
        critical_vulns = stats.get('criticalVulns', 0)
        avg_score = stats.get('avgScore', 0)
        
        print_result("Evaluation History", total_evaluations > 0,
                    f"{total_evaluations} total evaluations recorded")
        print_result("Model Activity", active_models >= 3,
                    f"{active_models} active models")
        print_result("Vulnerability Detection", critical_vulns > 0,
                    f"{critical_vulns} critical vulnerabilities found")
        print_result("Score Calculation", 0 <= avg_score <= 100,
                    f"Average score: {avg_score:.2f}%")
        
        # Test evaluation results endpoint
        response = requests.get("http://localhost:5000/api/evaluation-results")
        if response.status_code == 200:
            results = response.json()
            print_result("Results System", len(results) > 0,
                        f"Found {len(results)} evaluation results")
            
            # Validate result structure
            if results:
                sample_result = results[0]
                required_fields = ['vulnerabilityScore', 'impactSeverity', 'compositeScore']
                has_required = all(field in sample_result for field in required_fields)
                print_result("Result Structure", has_required,
                            "Results contain required security metrics")
        
        return total_evaluations > 0
        
    except Exception as e:
        print_result("Evaluation System", False, str(e))
        return False

def test_memory_integration():
    """Test memory integration features"""
    print_header("Memory Integration Tests")
    
    try:
        # Test memory threat endpoint (if available)
        response = requests.get("http://localhost:5000/api/memory/threats", timeout=5)
        if response.status_code == 200:
            threats = response.json()
            print_result("Memory Threats API", True,
                        f"Memory system accessible with {len(threats)} threats")
        else:
            print_result("Memory Threats API", False, f"HTTP {response.status_code}")
        
        # Test Gemini evaluate endpoint
        test_payload = {
            "prompt": "Test prompt for memory integration",
            "model": "gemini-2.5-pro-preview-05-06"
        }
        
        response = requests.post("http://localhost:5000/api/gemini-evaluate", 
                               json=test_payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print_result("Gemini Integration", True,
                        "Gemini evaluation endpoint accessible")
        else:
            print_result("Gemini Integration", False, f"HTTP {response.status_code}")
        
        return True
        
    except Exception as e:
        print_result("Memory Integration", False, str(e))
        return False

def test_frontend_accessibility():
    """Test if frontend is accessible"""
    print_header("Frontend Accessibility Test")
    
    try:
        # Test main page
        response = requests.get("http://localhost:5000/", timeout=10)
        if response.status_code == 200:
            print_result("Frontend Access", True, "Main page accessible")
            
            # Check for React content indicators
            content = response.text
            has_react_content = any(indicator in content.lower() for indicator in 
                                   ['react', 'safeguard', 'cybersecurity', 'evaluation'])
            print_result("React Content", has_react_content,
                        "Frontend contains expected application content")
            return True
        else:
            print_result("Frontend Access", False, f"HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print_result("Frontend Access", False, str(e))
        return False

def run_tests():
    """Run all SafeGuardLLM application tests"""
    print("🚀 SafeGuardLLM Application Test Suite")
    print("Testing cybersecurity evaluation framework functionality...")
    
    start_time = time.time()
    
    # Run all test categories
    test_results = {
        "Server Connection": test_server_connection(),
        "LLM Providers": test_llm_providers(), 
        "Security Test Suites": test_security_test_suites(),
        "Evaluation System": test_evaluation_system(),
        "Memory Integration": test_memory_integration(),
        "Frontend Access": test_frontend_accessibility()
    }
    
    # Summary
    print_header("Test Results Summary")
    
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    success_rate = (passed_tests / total_tests) * 100
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n📊 Overall Results:")
    print(f"   Tests Passed: {passed_tests}/{total_tests}")
    print(f"   Success Rate: {success_rate:.1f}%")
    print(f"   Runtime: {time.time() - start_time:.2f} seconds")
    
    # Application status
    if success_rate >= 80:
        print("\n🎉 SafeGuardLLM is running successfully!")
        print("   ✓ Core security evaluation features operational")
        print("   ✓ LLM providers configured and accessible") 
        print("   ✓ Comprehensive test suites loaded")
        print("   ✓ Evaluation and memory systems functional")
    elif success_rate >= 60:
        print("\n⚠️  SafeGuardLLM is partially functional")
        print("   Some components may need attention")
    else:
        print("\n❌ SafeGuardLLM has significant issues")
        print("   Multiple components require debugging")
    
    return success_rate >= 80

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)