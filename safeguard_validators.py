#!/usr/bin/env python3
"""
SafeguardLLM MENA Validators
Custom security validators for MENA region content validation
"""
import json
import re
import random
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load authentic Arabic dataset from Kaggle (fixed version)
dataset_path = Path("datasets/mena_guardrails_kaggle_fixed.jsonl")
DATASET = []
if dataset_path.exists():
    with open(dataset_path, encoding='utf-8') as f:
        DATASET = [json.loads(line) for line in f]
    logger.info(f"Loaded {len(DATASET)} samples from fixed authentic Arabic dataset")
else:
    logger.warning("Fixed dataset not found. Run relabel.py first.")

def get_random_test_suite(n=4):
    """Get random test samples from the authentic Arabic dataset"""
    if not DATASET:
        return []
    return random.sample(DATASET, min(n, len(DATASET)))

class ValidationResult:
    """Result of validation check"""
    def __init__(self, passed: bool, error_message: str = None, sanitized_text: str = None):
        self.passed = passed
        self.error_message = error_message
        self.sanitized_text = sanitized_text

class ArabicToxicityValidator:
    """Validator for Arabic toxicity detection"""
    
    def __init__(self, threshold: float = 0.7):
        self.threshold = threshold
        
        # Common Arabic toxic patterns
        self.toxic_patterns = [
            r'كلب',  # Dog (derogatory)
            r'حمار',  # Donkey (derogatory)
            r'غبي',  # Stupid
            r'أحمق',  # Fool
            r'لعين',  # Cursed
            r'قذر',  # Dirty
            r'وسخ',  # Filthy
            r'خنزير',  # Pig (derogatory)
            r'جاهل',  # Ignorant
            r'متخلف',  # Backward
        ]
        
        # Compile regex patterns
        self.compiled_patterns = [re.compile(pattern) for pattern in self.toxic_patterns]
    
    def validate(self, text: str) -> ValidationResult:
        """Validate Arabic text for toxicity"""
        if not isinstance(text, str):
            return ValidationResult(False, "Input must be a string")
        
        # Check for toxic patterns
        toxic_matches = []
        for pattern in self.compiled_patterns:
            matches = pattern.findall(text)
            if matches:
                toxic_matches.extend(matches)
        
        if toxic_matches:
            sanitized = self._sanitize_text(text)
            return ValidationResult(
                False, 
                f"Arabic toxic content detected: {', '.join(toxic_matches)}", 
                sanitized
            )
        
        return ValidationResult(True)
    
    def _sanitize_text(self, text: str) -> str:
        """Remove toxic content from text"""
        sanitized = text
        for pattern in self.compiled_patterns:
            sanitized = pattern.sub("***", sanitized)
        return sanitized

class ReligiousInsultValidator:
    """Validator for religious insults in multiple languages"""
    
    def __init__(self, languages: List[str] = ["ar", "en", "fa", "ur"]):
        self.languages = languages
        
        # Religious insult patterns by language
        self.religious_patterns = {
            "ar": [
                r'كافر',  # Infidel
                r'مرتد',  # Apostate
                r'ملحد',  # Atheist (when used derogatorily)
                r'نجس',  # Impure
                r'مشرك',  # Polytheist (derogatory)
                r'زنديق',  # Heretic
            ],
            "en": [
                r'\binfidel\b',
                r'\bheretic\b',
                r'\bheathen\b',
                r'\bblasphemer\b',
                r'\bapostate\b',
                r'\bunbeliever\b',
            ],
            "fa": [  # Persian/Farsi
                r'کافر',
                r'مرتد',
                r'بی‌دین',
                r'زندیق',
            ],
            "ur": [  # Urdu
                r'کافر',
                r'مرتد',
                r'بے دین',
                r'زندیق',
            ]
        }
        
        # Compile patterns
        self.compiled_patterns = {}
        for lang, patterns in self.religious_patterns.items():
            if lang in self.languages:
                self.compiled_patterns[lang] = [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
    
    def validate(self, text: str) -> ValidationResult:
        """Validate text for religious insults"""
        if not isinstance(text, str):
            return ValidationResult(False, "Input must be a string")
        
        # Check for religious insults across languages
        detected_insults = []
        for lang, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                matches = pattern.findall(text)
                if matches:
                    detected_insults.extend([(lang, match) for match in matches])
        
        if detected_insults:
            insult_details = [f"{lang}:{match}" for lang, match in detected_insults]
            sanitized = self._sanitize_religious_content(text)
            return ValidationResult(
                False, 
                f"Religious insults detected: {', '.join(insult_details)}", 
                sanitized
            )
        
        return ValidationResult(True)
    
    def _sanitize_religious_content(self, text: str) -> str:
        """Remove religious insults from text"""
        sanitized = text
        for lang, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                sanitized = pattern.sub("[REMOVED]", sanitized)
        return sanitized

class MENAPIIValidator:
    """Validator for MENA region PII detection"""
    
    def __init__(self):
        # PII patterns for MENA region
        self.pii_patterns = {
            "saudi_id": r'\b\d{10}\b',  # Saudi National ID
            "uae_id": r'\b784-\d{4}-\d{7}-\d{1}\b',  # UAE ID
            "egyptian_id": r'\b\d{14}\b',  # Egyptian National ID
            "phone_gcc": r'\+971\d{9}|\+966\d{9}|\+973\d{8}|\+974\d{8}|\+965\d{8}|\+968\d{8}',  # GCC phones
            "iban_mena": r'\b[A-Z]{2}\d{2}[A-Z0-9]{4}\d{7}([A-Z0-9]?){0,16}\b',  # IBAN format
            "arabic_name": r'[\u0600-\u06FF\s]{2,50}',  # Arabic names (simplified)
            "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email addresses
            "credit_card": r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',  # Credit card numbers
        }
        
        # Compile patterns
        self.compiled_patterns = {
            name: re.compile(pattern) for name, pattern in self.pii_patterns.items()
        }
    
    def validate(self, text: str) -> ValidationResult:
        """Validate text for MENA region PII"""
        if not isinstance(text, str):
            return ValidationResult(False, "Input must be a string")
        
        # Check for PII patterns
        detected_pii = []
        for pii_type, pattern in self.compiled_patterns.items():
            matches = pattern.findall(text)
            if matches:
                detected_pii.extend([(pii_type, match) for match in matches])
        
        if detected_pii:
            pii_details = [f"{pii_type}:{match}" for pii_type, match in detected_pii]
            sanitized = self._sanitize_pii(text)
            return ValidationResult(
                False, 
                f"MENA PII detected: {', '.join(pii_details)}", 
                sanitized
            )
        
        return ValidationResult(True)
    
    def _sanitize_pii(self, text: str) -> str:
        """Remove PII from text"""
        sanitized = text
        for pii_type, pattern in self.compiled_patterns.items():
            sanitized = pattern.sub("[REDACTED]", sanitized)
        return sanitized

class MENASecurityValidator:
    """Combined MENA security validator"""
    
    def __init__(self):
        self.arabic_toxicity = ArabicToxicityValidator()
        self.religious_insult = ReligiousInsultValidator()
        self.mena_pii = MENAPIIValidator()
    
    def validate_comprehensive(self, text: str) -> Dict[str, Any]:
        """Comprehensive validation using all MENA validators"""
        results = {
            "text": text,
            "overall_passed": True,
            "validations": {},
            "sanitized_text": text,
            "errors": []
        }
        
        # Run all validators
        validators = {
            "arabic_toxicity": self.arabic_toxicity,
            "religious_insult": self.religious_insult,
            "mena_pii": self.mena_pii
        }
        
        for validator_name, validator in validators.items():
            result = validator.validate(text)
            results["validations"][validator_name] = {
                "passed": result.passed,
                "error_message": result.error_message,
                "sanitized_text": result.sanitized_text
            }
            
            if not result.passed:
                results["overall_passed"] = False
                results["errors"].append(result.error_message)
                if result.sanitized_text:
                    results["sanitized_text"] = result.sanitized_text
        
        return results
    
    def validate_malware_analysis(self, analysis_text: str) -> Dict[str, Any]:
        """Validate malware analysis text specifically"""
        # Focus on PII and religious content for malware analysis
        results = {
            "text": analysis_text,
            "analysis_safe": True,
            "validations": {},
            "sanitized_text": analysis_text,
            "recommendations": []
        }
        
        # Check for PII in malware analysis
        pii_result = self.mena_pii.validate(analysis_text)
        results["validations"]["pii_check"] = {
            "passed": pii_result.passed,
            "error_message": pii_result.error_message,
            "sanitized_text": pii_result.sanitized_text
        }
        
        if not pii_result.passed:
            results["analysis_safe"] = False
            results["recommendations"].append("Remove PII from malware analysis")
            if pii_result.sanitized_text:
                results["sanitized_text"] = pii_result.sanitized_text
        
        # Check for religious insults
        religious_result = self.religious_insult.validate(analysis_text)
        results["validations"]["religious_check"] = {
            "passed": religious_result.passed,
            "error_message": religious_result.error_message,
            "sanitized_text": religious_result.sanitized_text
        }
        
        if not religious_result.passed:
            results["analysis_safe"] = False
            results["recommendations"].append("Remove religious insults from analysis")
            if religious_result.sanitized_text:
                results["sanitized_text"] = religious_result.sanitized_text
        
        return results

def main():
    """Main demonstration function"""
    print("🛡️  SafeguardLLM MENA Validators Demonstration")
    print("=" * 60)
    
    # Initialize validator
    validator = MENASecurityValidator()
    
    # Test cases
    test_cases = [
        {
            "name": "Clean Security Analysis",
            "text": "This malware sample shows typical trojan behavior with network connections to C2 servers.",
            "expected": "pass"
        },
        {
            "name": "Arabic Toxic Content",
            "text": "هذا المستخدم كلب وحمار ولا يفهم شيئاً",
            "expected": "fail"
        },
        {
            "name": "PII in Analysis",
            "text": "Contact the analyst at john.doe@company.com or call +971501234567 for more details.",
            "expected": "fail"
        },
        {
            "name": "Religious Insults",
            "text": "The user is clearly a kafir and heretic based on the analysis.",
            "expected": "fail"
        },
        {
            "name": "Clean Malware Analysis",
            "text": "SHA-256 hash analysis shows Mirai botnet characteristics with IoT targeting capabilities.",
            "expected": "pass"
        }
    ]
    
    print("\n📋 Running Validation Tests:")
    print("-" * 40)
    
    total_tests = len(test_cases)
    passed_tests = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['name']}")
        print(f"Text: {test_case['text'][:80]}...")
        
        # Run comprehensive validation
        result = validator.validate_comprehensive(test_case['text'])
        
        print(f"Result: {'PASS' if result['overall_passed'] else 'FAIL'}")
        
        if not result['overall_passed']:
            print(f"Errors: {len(result['errors'])}")
            for error in result['errors']:
                print(f"  - {error}")
        
        if result['overall_passed']:
            passed_tests += 1
    
    print(f"\n📊 Summary:")
    print(f"  Total tests: {total_tests}")
    print(f"  Passed: {passed_tests}")
    print(f"  Failed: {total_tests - passed_tests}")
    print(f"  Pass rate: {passed_tests/total_tests:.1%}")
    
    # Test with authentic Arabic dataset
    print(f"\n🔍 Testing with Authentic Arabic Dataset:")
    print("-" * 40)
    
    if DATASET:
        # Get random test samples from the authentic dataset
        test_samples = get_random_test_suite(10)
        
        dataset_results = {"clean": 0, "religious_hate": 0, "pii": 0, "prompt_injection": 0}
        validation_results = {"passed": 0, "failed": 0}
        
        for i, sample in enumerate(test_samples, 1):
            text = sample["text"]
            label = sample["label"]
            
            # Run validation
            result = validator.validate_comprehensive(text)
            
            print(f"\nDataset Sample {i}:")
            print(f"  Label: {label}")
            print(f"  Text: {text[:80]}...")
            print(f"  Validation: {'PASS' if result['overall_passed'] else 'FAIL'}")
            
            if not result['overall_passed']:
                print(f"  Errors: {', '.join(result['errors'])}")
            
            # Track results
            dataset_results[label] += 1
            if result['overall_passed']:
                validation_results["passed"] += 1
            else:
                validation_results["failed"] += 1
        
        print(f"\n📊 Dataset Testing Summary:")
        print(f"  Total samples tested: {len(test_samples)}")
        print(f"  Validation passed: {validation_results['passed']}")
        print(f"  Validation failed: {validation_results['failed']}")
        print(f"  Success rate: {validation_results['passed']/len(test_samples):.1%}")
        
        print(f"\n📋 Sample Distribution:")
        for label, count in dataset_results.items():
            print(f"  {label}: {count}")
    else:
        print("  No authentic dataset available. Run data preparation first.")
    
    # Test malware analysis specific validation
    print(f"\n🔍 Malware Analysis Validation:")
    print("-" * 40)
    
    malware_text = "Analysis of SHA-256 hash abc123def456 shows Mirai characteristics. Contact analyst at user@domain.com."
    malware_result = validator.validate_malware_analysis(malware_text)
    
    print(f"Analysis safe: {malware_result['analysis_safe']}")
    if malware_result['recommendations']:
        print("Recommendations:")
        for rec in malware_result['recommendations']:
            print(f"  - {rec}")
    
    # Save results
    report = {
        "validator_type": "MENA Security Validators",
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "failed_tests": total_tests - passed_tests,
        "pass_rate": passed_tests / total_tests,
        "test_results": [],
        "malware_analysis_test": malware_result
    }
    
    for i, test_case in enumerate(test_cases):
        result = validator.validate_comprehensive(test_case['text'])
        report["test_results"].append({
            "test_name": test_case['name'],
            "text": test_case['text'],
            "expected": test_case['expected'],
            "actual": "pass" if result['overall_passed'] else "fail",
            "errors": result['errors'],
            "validations": result['validations']
        })
    
    report_path = Path("mena_validators_report.json")
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Validation report saved to: {report_path}")
    print("\n🎯 MENA validators ready for SafeguardLLM integration!")

if __name__ == "__main__":
    main()