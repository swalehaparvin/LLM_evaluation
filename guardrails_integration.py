#!/usr/bin/env python3
"""
SafeguardLLM Guardrails Integration with MENA Validators
Enhanced security validation for multilingual and regional content
"""
import json
import re
import os
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import logging

try:
    import guardrails as gd
    from guardrails.validators import Validator, ValidationResult
    from guardrails import Guard
    GUARDRAILS_AVAILABLE = True
except ImportError:
    GUARDRAILS_AVAILABLE = False
    print("Warning: Guardrails AI not available. Install with: pip install guardrails-ai")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set Guardrails API key
GUARDRAILS_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJnb29nbGUtb2F1dGgyfDEwOTY0NjkyMTE2MDUxMzQ5MjQ1MiIsImFwaUtleUlkIjoiOTg1N2E4NzktNmEwYy00N2U0LTllMmEtNjZkMzQ3ZGQwODU4Iiwic2NvcGUiOiJyZWFkOnBhY2thZ2VzIiwicGVybWlzc2lvbnMiOltdLCJpYXQiOjE3NTI0MTU4MTcsImV4cCI6MTc2MDE5MTgxN30.BUrjGH4ux8fENmShUkpB9ffB9UqTbdWkjgSiLptDO2w"
os.environ["GUARDRAILS_API_KEY"] = GUARDRAILS_API_KEY

class ArabicToxicityValidator(Validator):
    """Custom validator for Arabic toxicity detection"""
    
    def __init__(self, threshold: float = 0.7):
        super().__init__()
        self.threshold = threshold
        
        # Common Arabic toxic patterns (simplified for demo)
        self.toxic_patterns = [
            r'كلب',  # Dog (derogatory)
            r'حمار',  # Donkey (derogatory)
            r'غبي',  # Stupid
            r'أحمق',  # Fool
            r'لعين',  # Cursed
            r'قذر',  # Dirty
            r'وسخ',  # Filthy
        ]
        
        # Compile regex patterns
        self.compiled_patterns = [re.compile(pattern) for pattern in self.toxic_patterns]
    
    def validate(self, value: str, metadata: Dict[str, Any] = None) -> ValidationResult:
        """Validate Arabic text for toxicity"""
        if not isinstance(value, str):
            return ValidationResult(
                outcome="fail",
                error_message="Input must be a string"
            )
        
        # Check for toxic patterns
        toxic_matches = []
        for pattern in self.compiled_patterns:
            matches = pattern.findall(value)
            if matches:
                toxic_matches.extend(matches)
        
        if toxic_matches:
            return ValidationResult(
                outcome="fail",
                error_message=f"Arabic toxic content detected: {', '.join(toxic_matches)}",
                fix_value=self._sanitize_text(value)
            )
        
        return ValidationResult(outcome="pass")
    
    def _sanitize_text(self, text: str) -> str:
        """Remove toxic content from text"""
        sanitized = text
        for pattern in self.compiled_patterns:
            sanitized = pattern.sub("***", sanitized)
        return sanitized

class ReligiousInsultValidator(Validator):
    """Custom validator for religious insults in multiple languages"""
    
    def __init__(self, languages: List[str] = ["ar", "en", "fa", "ur"]):
        super().__init__()
        self.languages = languages
        
        # Religious insult patterns by language
        self.religious_patterns = {
            "ar": [
                r'كافر',  # Infidel
                r'مرتد',  # Apostate
                r'ملحد',  # Atheist (when used derogatorily)
                r'نجس',  # Impure
            ],
            "en": [
                r'\binfidel\b',
                r'\bheretic\b',
                r'\bheathen\b',
                r'\bblasphemer\b',
            ],
            "fa": [  # Persian/Farsi
                r'کافر',
                r'مرتد',
                r'بی‌دین',
            ],
            "ur": [  # Urdu
                r'کافر',
                r'مرتد',
                r'بے دین',
            ]
        }
        
        # Compile patterns
        self.compiled_patterns = {}
        for lang, patterns in self.religious_patterns.items():
            if lang in self.languages:
                self.compiled_patterns[lang] = [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
    
    def validate(self, value: str, metadata: Dict[str, Any] = None) -> ValidationResult:
        """Validate text for religious insults"""
        if not isinstance(value, str):
            return ValidationResult(
                outcome="fail",
                error_message="Input must be a string"
            )
        
        # Check for religious insults across languages
        detected_insults = []
        for lang, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                matches = pattern.findall(value)
                if matches:
                    detected_insults.extend([(lang, match) for match in matches])
        
        if detected_insults:
            insult_details = [f"{lang}:{match}" for lang, match in detected_insults]
            return ValidationResult(
                outcome="fail",
                error_message=f"Religious insults detected: {', '.join(insult_details)}",
                fix_value=self._sanitize_religious_content(value)
            )
        
        return ValidationResult(outcome="pass")
    
    def _sanitize_religious_content(self, text: str) -> str:
        """Remove religious insults from text"""
        sanitized = text
        for lang, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                sanitized = pattern.sub("[REMOVED]", sanitized)
        return sanitized

class MENAPIIValidator(Validator):
    """Custom validator for MENA region PII detection"""
    
    def __init__(self):
        super().__init__()
        
        # PII patterns for MENA region
        self.pii_patterns = {
            "saudi_id": r'\b\d{10}\b',  # Saudi National ID
            "uae_id": r'\b784-\d{4}-\d{7}-\d{1}\b',  # UAE ID
            "egyptian_id": r'\b\d{14}\b',  # Egyptian National ID
            "phone_gcc": r'\+971\d{9}|\+966\d{9}|\+973\d{8}|\+974\d{8}|\+965\d{8}|\+968\d{8}',  # GCC phone numbers
            "iban_mena": r'\b[A-Z]{2}\d{2}[A-Z0-9]{4}\d{7}([A-Z0-9]?){0,16}\b',  # IBAN format
            "arabic_name": r'[\u0600-\u06FF\s]{2,50}',  # Arabic names (simplified)
        }
        
        # Compile patterns
        self.compiled_patterns = {
            name: re.compile(pattern) for name, pattern in self.pii_patterns.items()
        }
    
    def validate(self, value: str, metadata: Dict[str, Any] = None) -> ValidationResult:
        """Validate text for MENA region PII"""
        if not isinstance(value, str):
            return ValidationResult(
                outcome="fail",
                error_message="Input must be a string"
            )
        
        # Check for PII patterns
        detected_pii = []
        for pii_type, pattern in self.compiled_patterns.items():
            matches = pattern.findall(value)
            if matches:
                detected_pii.extend([(pii_type, match) for match in matches])
        
        if detected_pii:
            pii_details = [f"{pii_type}:{match}" for pii_type, match in detected_pii]
            return ValidationResult(
                outcome="fail",
                error_message=f"MENA PII detected: {', '.join(pii_details)}",
                fix_value=self._sanitize_pii(value)
            )
        
        return ValidationResult(outcome="pass")
    
    def _sanitize_pii(self, text: str) -> str:
        """Remove PII from text"""
        sanitized = text
        for pii_type, pattern in self.compiled_patterns.items():
            sanitized = pattern.sub("[REDACTED]", sanitized)
        return sanitized

class SafeguardLLMGuardrailsManager:
    """Manager for SafeguardLLM Guardrails integration"""
    
    def __init__(self):
        self.guards = {}
        self.validators = {}
        self.setup_validators()
        self.setup_guards()
    
    def setup_validators(self):
        """Initialize custom validators"""
        self.validators = {
            "arabic_toxicity": ArabicToxicityValidator(threshold=0.7),
            "religious_insult": ReligiousInsultValidator(languages=["ar", "en", "fa", "ur"]),
            "mena_pii": MENAPIIValidator(),
        }
        
        logger.info("✅ Custom MENA validators initialized")
    
    def setup_guards(self):
        """Setup Guardrails guards with custom validators"""
        if not GUARDRAILS_AVAILABLE:
            logger.warning("⚠️  Guardrails AI not available. Using mock guards.")
            self.guards = {
                "mena_security": self._create_mock_guard(),
                "arabic_content": self._create_mock_guard(),
                "multilingual": self._create_mock_guard(),
            }
            return
        
        # Create guards with custom validators
        self.guards = {
            "mena_security": Guard().use(
                self.validators["mena_pii"],
                self.validators["religious_insult"]
            ),
            "arabic_content": Guard().use(
                self.validators["arabic_toxicity"],
                self.validators["religious_insult"]
            ),
            "multilingual": Guard().use(
                self.validators["religious_insult"],
                self.validators["mena_pii"]
            ),
        }
        
        logger.info("✅ Guardrails guards configured")
    
    def _create_mock_guard(self):
        """Create mock guard when Guardrails is not available"""
        class MockGuard:
            def validate(self, text: str) -> Dict[str, Any]:
                return {
                    "validated_output": text,
                    "validation_passed": True,
                    "reask": None,
                    "error": None
                }
        
        return MockGuard()
    
    def validate_text(self, text: str, guard_type: str = "mena_security") -> Dict[str, Any]:
        """Validate text using specified guard"""
        if guard_type not in self.guards:
            raise ValueError(f"Unknown guard type: {guard_type}")
        
        guard = self.guards[guard_type]
        
        if GUARDRAILS_AVAILABLE:
            try:
                result = guard.validate(text)
                return {
                    "validated_output": result.validated_output,
                    "validation_passed": result.validation_passed,
                    "reask": result.reask,
                    "error": result.error
                }
            except Exception as e:
                logger.error(f"Validation error: {e}")
                return {
                    "validated_output": text,
                    "validation_passed": False,
                    "reask": None,
                    "error": str(e)
                }
        else:
            # Use custom validators directly
            validation_results = []
            for validator_name, validator in self.validators.items():
                result = validator.validate(text)
                validation_results.append({
                    "validator": validator_name,
                    "outcome": result.outcome,
                    "error_message": result.error_message if hasattr(result, 'error_message') else None,
                    "fix_value": result.fix_value if hasattr(result, 'fix_value') else None
                })
            
            # Check if all validations passed
            all_passed = all(result["outcome"] == "pass" for result in validation_results)
            
            return {
                "validated_output": text,
                "validation_passed": all_passed,
                "validation_results": validation_results,
                "reask": None,
                "error": None if all_passed else "Some validations failed"
            }
    
    def validate_malware_analysis(self, analysis_text: str) -> Dict[str, Any]:
        """Validate malware analysis text for MENA compliance"""
        return self.validate_text(analysis_text, "mena_security")
    
    def validate_arabic_content(self, arabic_text: str) -> Dict[str, Any]:
        """Validate Arabic content for toxicity and religious insults"""
        return self.validate_text(arabic_text, "arabic_content")
    
    def validate_multilingual_content(self, text: str) -> Dict[str, Any]:
        """Validate multilingual content"""
        return self.validate_text(text, "multilingual")
    
    def generate_validation_report(self, test_cases: List[Dict[str, str]]) -> Dict[str, Any]:
        """Generate comprehensive validation report"""
        report = {
            "total_tests": len(test_cases),
            "passed": 0,
            "failed": 0,
            "results": [],
            "summary": {}
        }
        
        for i, test_case in enumerate(test_cases):
            text = test_case.get("text", "")
            guard_type = test_case.get("guard_type", "mena_security")
            
            result = self.validate_text(text, guard_type)
            
            test_result = {
                "test_id": i + 1,
                "text": text[:100] + "..." if len(text) > 100 else text,
                "guard_type": guard_type,
                "validation_passed": result["validation_passed"],
                "error": result.get("error"),
                "details": result.get("validation_results", [])
            }
            
            report["results"].append(test_result)
            
            if result["validation_passed"]:
                report["passed"] += 1
            else:
                report["failed"] += 1
        
        # Generate summary
        report["summary"] = {
            "pass_rate": report["passed"] / report["total_tests"] if report["total_tests"] > 0 else 0,
            "fail_rate": report["failed"] / report["total_tests"] if report["total_tests"] > 0 else 0,
            "validators_used": list(self.validators.keys()),
            "guards_configured": list(self.guards.keys())
        }
        
        return report

def main():
    """Main demonstration function"""
    print("🛡️  SafeguardLLM Guardrails Integration with MENA Validators")
    print("=" * 70)
    
    # Initialize guardrails manager
    manager = SafeguardLLMGuardrailsManager()
    
    # Test cases for validation
    test_cases = [
        {
            "text": "This is a clean security analysis of malware sample ABC123.",
            "guard_type": "mena_security",
            "expected": "pass"
        },
        {
            "text": "هذا النص يحتوي على محتوى مسيء: كلب وحمار",
            "guard_type": "arabic_content",
            "expected": "fail"
        },
        {
            "text": "Contact details: +971501234567 and ID: 784-1234-1234567-1",
            "guard_type": "mena_security",
            "expected": "fail"
        },
        {
            "text": "The user is a kafir and heretic according to analysis.",
            "guard_type": "multilingual",
            "expected": "fail"
        },
        {
            "text": "Clean malware analysis with no sensitive content.",
            "guard_type": "mena_security",
            "expected": "pass"
        }
    ]
    
    # Generate validation report
    report = manager.generate_validation_report(test_cases)
    
    print(f"\n📊 Validation Report:")
    print(f"  Total tests: {report['total_tests']}")
    print(f"  Passed: {report['passed']}")
    print(f"  Failed: {report['failed']}")
    print(f"  Pass rate: {report['summary']['pass_rate']:.1%}")
    
    print(f"\n🔧 Validators Available:")
    for validator in report['summary']['validators_used']:
        print(f"  • {validator}")
    
    print(f"\n🛡️  Guards Configured:")
    for guard in report['summary']['guards_configured']:
        print(f"  • {guard}")
    
    # Save report
    report_path = Path("guardrails_validation_report.json")
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Validation report saved to: {report_path}")
    print("\n🎯 Guardrails integration ready for SafeguardLLM deployment!")

if __name__ == "__main__":
    main()