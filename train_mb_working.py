#!/usr/bin/env python3
"""
SafeguardLLM Malware Bazaar Training Script - Working Version
"""
import os
import csv
import json
import hashlib
import re
import requests
from pathlib import Path
from tqdm import tqdm

# Configuration
CSV_URL = "https://bazaar.abuse.ch/export/csv/recent/"
OUT_DIR = Path("malware_bazaar")
JSONL_OUT = OUT_DIR / "mb_train.jsonl"
API_KEY = os.getenv("MALWARE_BAZAAR_API_KEY", "")
HEADERS = {"API-KEY": API_KEY} if API_KEY else {}
MAX_FILES = 50  # Reduced for demo

print("🚀 Starting SafeguardLLM Malware Bazaar Training Data Collection")
print(f"📊 Processing up to {MAX_FILES} samples")

# Create output directory
OUT_DIR.mkdir(exist_ok=True)

# Step 1: Download and parse CSV
csv_path = OUT_DIR / "index.csv"
print("\n⬇️ Downloading CSV index...")

try:
    with requests.get(CSV_URL, stream=True, timeout=30) as r:
        r.raise_for_status()
        csv_path.write_bytes(r.content)
    print(f"✅ CSV downloaded: {csv_path}")
except Exception as e:
    print(f"❌ CSV download failed: {e}")
    exit(1)

# Step 2: Parse CSV and extract sample metadata
samples = []
try:
    with open(csv_path, newline='', encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row or row[0].startswith('#'):
                continue
            if len(row) >= 9:
                sha256 = row[1].strip()
                fname = row[5].strip()
                sig = row[8].strip() if row[8].strip() else "unknown"
                samples.append((sha256, fname, sig))
    
    samples = samples[:MAX_FILES]
    print(f"📋 Parsed {len(samples)} samples from CSV")
    
    # Show sample data
    print("\n🔍 Sample data preview:")
    for i, (sha256, fname, sig) in enumerate(samples[:3]):
        print(f"  {i+1}. {fname} ({sig}) - {sha256[:16]}...")
        
except Exception as e:
    print(f"❌ CSV parsing failed: {e}")
    exit(1)

# Step 3: Create training dataset
print(f"\n🔧 Creating training dataset: {JSONL_OUT}")

training_data = []
session = requests.Session()

for sha256, fname, sig in tqdm(samples, desc="Processing samples"):
    try:
        # Create training example from metadata
        prompt = (
            f"Analyze the Windows PE sample named '{fname}' "
            f"with SHA-256 hash {sha256}. "
            f"Provide malware classification, family identification, and security analysis."
        )
        
        # Create comprehensive completion
        completion = (
            f"Malware Classification: {sig}\n"
            f"File Analysis: The sample '{fname}' is identified as {sig}.\n"
            f"Security Assessment: This is a known malware variant that requires immediate attention.\n"
            f"Recommended Actions: Quarantine the file, scan affected systems, and implement security measures.\n"
            f"Threat Level: High - This sample poses significant security risks."
        )
        
        training_example = {
            "prompt": prompt,
            "completion": completion,
            "metadata": {
                "sha256": sha256,
                "filename": fname,
                "signature": sig,
                "source": "malware_bazaar"
            }
        }
        
        training_data.append(training_example)
        
    except Exception as e:
        tqdm.write(f"❌ Error processing {sha256}: {e}")
        continue

# Step 4: Save training data
try:
    JSONL_OUT.parent.mkdir(parents=True, exist_ok=True)
    
    with open(JSONL_OUT, "w", encoding="utf-8") as f:
        for example in training_data:
            f.write(json.dumps(example, ensure_ascii=False) + "\n")
    
    print(f"✅ Training dataset saved: {JSONL_OUT}")
    print(f"📊 Total training examples: {len(training_data)}")
    
    # Save summary stats
    stats_file = OUT_DIR / "training_stats.json"
    
    # Count signature types
    sig_counts = {}
    for example in training_data:
        sig = example["metadata"]["signature"]
        sig_counts[sig] = sig_counts.get(sig, 0) + 1
    
    stats = {
        "total_samples": len(training_data),
        "signature_distribution": sig_counts,
        "unique_signatures": len(sig_counts),
        "data_source": "malware_bazaar",
        "api_key_used": bool(API_KEY)
    }
    
    with open(stats_file, "w") as f:
        json.dump(stats, f, indent=2)
    
    print(f"📈 Training statistics saved: {stats_file}")
    
    # Show sample training data
    print("\n📋 Sample training examples:")
    for i, example in enumerate(training_data[:2]):
        print(f"\nExample {i+1}:")
        print(f"Prompt: {example['prompt'][:100]}...")
        print(f"Completion: {example['completion'][:100]}...")
        print(f"Signature: {example['metadata']['signature']}")
    
    print(f"\n✅ SafeguardLLM training data collection complete!")
    print(f"📁 Output directory: {OUT_DIR}")
    print(f"🎯 Ready for model training integration")

except Exception as e:
    print(f"❌ Failed to save training data: {e}")
    exit(1)

# Step 5: Integration with adversarial data
print("\n🔗 Integrating with adversarial datasets...")

# Load adversarial data
adv_path = Path("datasets/adv.jsonl")
if adv_path.exists():
    adversarial_data = []
    with open(adv_path, 'r') as f:
        for line in f:
            if line.strip():
                adversarial_data.append(json.loads(line))
    
    # Create mixed training batch
    mixed_batch = []
    
    # Add malware data (90%)
    malware_portion = training_data[:int(len(training_data) * 0.9)]
    for item in malware_portion:
        mixed_batch.append({
            "prompt": item["prompt"],
            "completion": item["completion"],
            "category": "malware_analysis",
            "source": "malware_bazaar"
        })
    
    # Add adversarial data (10%)
    adv_portion = adversarial_data[:int(len(training_data) * 0.1)]
    for item in adv_portion:
        mixed_batch.append({
            "prompt": item["prompt"],
            "completion": item["completion"],
            "category": "adversarial_training",
            "source": "safeguard_llm"
        })
    
    # Save mixed batch
    mixed_path = OUT_DIR / "mixed_training_batch.jsonl"
    with open(mixed_path, "w") as f:
        for item in mixed_batch:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    
    print(f"✅ Mixed training batch created: {mixed_path}")
    print(f"📊 Mixed batch composition:")
    print(f"  • Malware analysis: {len(malware_portion)} examples")
    print(f"  • Adversarial training: {len(adv_portion)} examples")
    print(f"  • Total: {len(mixed_batch)} examples")
    
else:
    print("⚠️  Adversarial dataset not found. Run datasets/adversarial.py first.")

print("\n🎉 Training data preparation complete!")
print("📚 The dataset is now ready for SafeguardLLM model training.")