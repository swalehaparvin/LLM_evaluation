from transformers import (
    AutoTokenizer, AutoModelForCausalLM,
    Trainer, TrainingArguments, DataCollatorForLanguageModeling)
from datasets import load_dataset, concatenate_datasets

MODEL_NAME = "microsoft/DialoGPT-medium"   # or any base
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, use_fast=True)
tokenizer.pad_token = tokenizer.eos_token

# 1. Load the 3 JSONL files
ds1 = load_dataset("json", data_files="datasets/processed/cti_ioc.jsonl")["train"]
ds2 = load_dataset("json", data_files="datasets/processed/misp_attack.jsonl")["train"]
ds3 = load_dataset("json", data_files="datasets/processed/adversarial.jsonl")["train"]
ds = concatenate_datasets([ds1, ds2, ds3]).shuffle(seed=42)

# 2. Tokenize
def tokenize(batch):
    model_inputs = tokenizer(
        batch["prompt"] + tokenizer.eos_token + batch["completion"],
        truncation=True, max_length=256)
    model_inputs["labels"] = model_inputs["input_ids"].copy()
    return model_inputs
tokenized = ds.map(tokenize, remove_columns=ds.column_names)

# 3. Training
training_args = TrainingArguments(
    output_dir="./cyber-ft",
    per_device_train_batch_size=4,
    num_train_epochs=3,
    fp16=True,
    save_steps=500,
    logging_steps=50,
    report_to=None
)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized,
    data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False)
)
trainer.train()
trainer.save_model("cyber-ft")
tokenizer.save_pretrained("cyber-ft")