#!/usr/bin/env python3
"""
SafeguardLLM Demo Training Script - Simplified version for testing
"""
import os, json, hashlib, re, time
from pathlib import Path
from tqdm import tqdm

# Create demo malware analysis dataset
OUT_DIR = Path("malware_bazaar_demo")
OUT_DIR.mkdir(exist_ok=True)

# Sample malware signatures and analysis data
demo_samples = [
    {
        "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "filename": "trojan.exe",
        "signature": "Trojan.Win32.Agent",
        "sections": [".text", ".data", ".rsrc"],
        "imphash": "f34d5f2d4577ed6d9ceec516c1f5a744"
    },
    {
        "sha256": "cf83e1357eefb8bdf1542850d66d8007d620e4050b5715dc83f4a921d36ce9ce",
        "filename": "ransomware.exe", 
        "signature": "Ransom.Win32.Locky",
        "sections": [".text", ".rdata", ".data"],
        "imphash": "a1b2c3d4e5f6789012345678901234567890abcd"
    },
    {
        "sha256": "bda7ab3e4e5f6789012345678901234567890abcdef123456789012345678901234",
        "filename": "backdoor.exe",
        "signature": "Backdoor.Win32.Poison",
        "sections": [".text", ".data", ".rsrc", ".reloc"],
        "imphash": "deadbeef12345678901234567890abcdef123456"
    }
]

# Generate training data
jsonl_path = OUT_DIR / "demo_train.jsonl"
print("🔧 Creating demo training dataset...")

with open(jsonl_path, "w", encoding="utf-8") as f:
    for sample in tqdm(demo_samples, desc="Generating"):
        prompt = (
            f"Analyze the Windows PE sample named {sample['filename']} "
            f"(SHA-256: {sample['sha256']}). "
            f"Provide malware family, packer, and notable characteristics."
        )
        
        completion = (
            f"Family: {sample['signature']}. "
            f"Imphash: {sample['imphash']}. "
            f"Sections: {', '.join(sample['sections'])}. "
            f"Analysis: This is a {sample['signature'].split('.')[0].lower()} variant "
            f"with standard PE structure and typical evasion techniques."
        )
        
        f.write(json.dumps({
            "prompt": prompt, 
            "completion": completion
        }, ensure_ascii=False) + "\n")

print(f"✅ Demo dataset created: {jsonl_path}")

# Test basic imports
print("\n🔍 Testing package imports...")
try:
    import torch
    print(f"✅ PyTorch: {torch.__version__}")
except ImportError as e:
    print(f"❌ PyTorch import failed: {e}")

try:
    from transformers import AutoTokenizer
    print("✅ Transformers: Available")
except ImportError as e:
    print(f"❌ Transformers import failed: {e}")

try:
    from datasets import Dataset
    print("✅ Datasets: Available")
except ImportError as e:
    print(f"❌ Datasets import failed: {e}")

try:
    from peft import LoraConfig
    print("✅ PEFT: Available")
except ImportError as e:
    print(f"❌ PEFT import failed: {e}")

try:
    import pefile
    print("✅ PEFile: Available")
except ImportError as e:
    print(f"❌ PEFile import failed: {e}")

try:
    import pyzipper
    print("✅ PyZipper: Available")
except ImportError as e:
    print(f"❌ PyZipper import failed: {e}")

print("\n🎯 Package verification complete!")
print("📊 Demo dataset ready for training integration with SafeguardLLM")
print(f"📁 Location: {jsonl_path}")
print(f"📈 Records: {len(demo_samples)} malware analysis examples")

# Show dataset content
print("\n📋 Sample training data:")
with open(jsonl_path, 'r') as f:
    for i, line in enumerate(f, 1):
        if i <= 2:  # Show first 2 examples
            data = json.loads(line)
            print(f"\nExample {i}:")
            print(f"Prompt: {data['prompt'][:100]}...")
            print(f"Completion: {data['completion'][:100]}...")