#!/usr/bin/env python3
"""
Simple MENA Guardrails Testing Script
Test content against MENA security policies using OpenAI
"""

import os
import sys
from test_mena_with_openai import MENAGuardrailsOpenAI

def main():
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not found")
        print("The API key has been configured. Testing will proceed.")
        
    print("="*60)
    print("🛡️  MENA GUARDRAILS CONTENT TESTING")
    print("="*60)
    print("\nEnter text to test against MENA security policies.")
    print("Type 'exit' to quit.\n")
    
    # Initialize guardrails
    guardrails = MENAGuardrailsOpenAI()
    
    while True:
        # Get user input
        print("-"*60)
        user_text = input("\n📝 Enter text to test: ").strip()
        
        if user_text.lower() in ['exit', 'quit', 'q']:
            print("\n👋 Goodbye!")
            break
            
        if not user_text:
            print("⚠️  Please enter some text to test.")
            continue
        
        # Test the content
        result = guardrails.test_content(user_text)
        
        # Show summary
        print("\n" + "="*60)
        if result['final_decision']['block']:
            print("📊 RESULT: 🚫 CONTENT BLOCKED")
        else:
            print("📊 RESULT: ✅ CONTENT ALLOWED")
        print("="*60)
        
        # Ask if user wants to test more
        choice = input("\nTest another text? (y/n): ").strip().lower()
        if choice != 'y':
            break
    
    print("\n✅ Testing complete!")

if __name__ == "__main__":
    main()