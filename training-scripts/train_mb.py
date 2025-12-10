#!/usr/bin/env python3
"""
Train SafeguardLLM on Malware-Bazaar samples.
Run `python train_mb.py` once; everything else is automatic.
"""
import os, csv, json, zipfile, pefile, hashlib, re, time, requests, pyzipper
from pathlib import Path
from tqdm import tqdm
from datasets import Dataset
from transformers import (AutoTokenizer, AutoModelForCausalLM,
                          TrainingArguments, Trainer, DataCollatorForLanguageModeling)
from peft import LoraConfig, get_peft_model, TaskType

# ------------------------------------------------------------------
# CONFIGURATION
# ------------------------------------------------------------------
CSV_URL   = "https://bazaar.abuse.ch/export/csv/recent/"
OUT_DIR   = Path("malware_bazaar")
JSONL_OUT = OUT_DIR / "mb_train.jsonl"
LORA_DIR  = Path("safeguard_mb_lora")
BASE_MODEL= "microsoft/DialoGPT-medium"        # 350 M params; swap for larger if GPU ok
API_KEY   = os.getenv("MALWARE_BAZAAR_API_KEY", "")
HEADERS   = {"API-KEY": API_KEY} if API_KEY else {}
ZIP_PASS  = b"infected"
MAX_FILES = 2_000          # cap for quick demo; remove for full run
# ------------------------------------------------------------------

# 1. Download CSV index ------------------------------------------------
OUT_DIR.mkdir(exist_ok=True)
csv_path = OUT_DIR / "index.csv"
print("⬇️  Downloading CSV index …")
with requests.get(CSV_URL, stream=True) as r:
    r.raise_for_status()
    csv_path.write_bytes(r.content)

# 2. Parse CSV ---------------------------------------------------------
samples = []
with open(csv_path, newline='', encoding="utf-8") as f:
    reader = csv.reader(f)
    for row in reader:
        if not row or row[0].startswith('#'): continue
        sha256 = row[1].strip()
        fname  = row[5].strip()
        sig    = row[8].strip() if len(row) > 8 else "unknown"
        samples.append((sha256, fname, sig))
samples = samples[:MAX_FILES]
print(f"📋 {len(samples)} samples queued")

# 3. Download ZIP samples ---------------------------------------------
session = requests.Session()
def download_sample(sha256):
    zip_path = OUT_DIR / f"{sha256}.zip"
    if zip_path.exists():
        return zip_path
    data = {"query": "get_file", "sha256_hash": sha256}
    try:
        r = session.post("https://mb-api.abuse.ch/api/v1/",
                         data=data, headers=HEADERS, timeout=30)
        r.raise_for_status()
        zip_path.write_bytes(r.content)
        return zip_path
    except Exception as e:
        tqdm.write(f"❌ {sha256}: {e}")
        return None

# 4. Feature extraction -------------------------------------------------
def extract_features(zip_path):
    """Return a dict with static features."""
    try:
        with pyzipper.AESZipFile(zip_path) as zf:
            zf.pwd = ZIP_PASS
            for name in zf.namelist():
                data = zf.read(name)
                break   # take first file
    except:
        return None

    try:
        pe = pefile.PE(data=data)
        imphash = pe.get_imphash()
        sections = [s.Name.decode(errors='ignore').strip('\x00') for s in pe.sections]
        strings = re.findall(rb"[\x20-\x7e]{4,}", data)
        strings_decoded = [s.decode(errors='ignore') for s in strings[:100]]
    except:
        imphash, sections, strings_decoded = "N/A", [], []

    return {
        "sha256": hashlib.sha256(data).hexdigest(),
        "size": len(data),
        "imphash": imphash,
        "sections": sections,
        "strings": strings_decoded
    }

# 5. Build JSONL dataset ----------------------------------------------
jsonl_path = JSONL_OUT
if not jsonl_path.exists():
    jsonl_path.parent.mkdir(parents=True, exist_ok=True)
    with open(jsonl_path, "w", encoding="utf-8") as f_out:
        for sha256, fname, sig in tqdm(samples, desc="Processing"):
            zip_path = download_sample(sha256)
            if not zip_path: continue
            feats = extract_features(zip_path)
            if not feats: continue
            prompt = (
                f"Analyze the Windows PE sample named {fname} "
                f"(SHA-256: {sha256}). "
                f"Provide malware family, packer, and notable characteristics."
            )
            completion = (
                f"Family: {sig}. "
                f"Imphash: {feats['imphash']}. "
                f"Sections: {', '.join(feats['sections'])}. "
                f"First 100 strings: {'; '.join(feats['strings'][:20])}"
            )
            f_out.write(json.dumps({"prompt": prompt, "completion": completion}, ensure_ascii=False) + "\n")
    print(f"✅ JSONL saved to {jsonl_path}")

# 6. Fine-tune ----------------------------------------------------------
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, use_fast=True)
tokenizer.pad_token = tokenizer.eos_token

raw_ds = Dataset.from_json(str(jsonl_path))

def tokenize(example):
    text = example["prompt"] + tokenizer.eos_token + example["completion"]
    return tokenizer(text, truncation=True, max_length=512)

tokenized = raw_ds.map(tokenize, remove_columns=raw_ds.column_names)

model = AutoModelForCausalLM.from_pretrained(BASE_MODEL)
lora_config = LoraConfig(
    task_type=TaskType.CAUSAL_LM,
    r=16, lora_alpha=32, lora_dropout=0.1,
    target_modules=["q_proj", "v_proj"]
)
model = get_peft_model(model, lora_config)

training_args = TrainingArguments(
    output_dir=str(LORA_DIR),
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
    num_train_epochs=2,
    fp16=True,
    save_steps=500,
    logging_steps=50,
    report_to=None
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized,
    data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False)
)
trainer.train()
trainer.save_model(str(LORA_DIR))
tokenizer.save_pretrained(str(LORA_DIR))

print("🎉 Training complete. Adapter saved to", LORA_DIR)