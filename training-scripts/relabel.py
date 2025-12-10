import pandas as pd, pathlib, json, random
from validators_mena import validate_mena

# Load the TSV file from Kaggle (not CSV)
kaggle_path = pathlib.Path("/home/runner/.cache/kagglehub/datasets/abedkhooli/arabic-100k-reviews/versions/4")
tsv_file = kaggle_path / "ar_reviews_100k.tsv"

df = pd.read_csv(tsv_file, sep='\t', usecols=["text"]).dropna().sample(5_000, random_state=42)

labels = []
for txt in df["text"]:
    res = validate_mena(txt)
    labels.append(res["flags"][0] if res["flags"] else "clean")

df["label"] = labels
df_interesting = df[df["label"] != "clean"]   # keep only the **interesting** rows
df_clean = df[df["label"] == "clean"].sample(min(500, len(df[df["label"] == "clean"])), random_state=42)  # add 500 clean

# Combine interesting and clean samples
df_final = pd.concat([df_interesting, df_clean])

out_path = pathlib.Path("datasets/mena_guardrails_kaggle_fixed.jsonl")
pathlib.Path("datasets").mkdir(exist_ok=True)
with open(out_path, "w", encoding="utf-8") as f:
    for _, row in df_final.iterrows():
        f.write(json.dumps({"text": row["text"], "label": row["label"]}, ensure_ascii=False) + "\n")

print("Fixed dataset:", out_path, "rows:", len(df_final))

# Show label distribution
label_counts = df_final["label"].value_counts()
print("\nLabel distribution:")
for label, count in label_counts.items():
    print(f"  {label}: {count} ({count/len(df_final)*100:.1f}%)")

# Show sample from each category
print("\nSample from each category:")
for label in label_counts.index:
    sample = df_final[df_final["label"] == label].iloc[0]
    print(f"\n{label.upper()}:")
    print(f"  Text: {sample['text'][:100]}...")
    result = validate_mena(sample['text'])
    print(f"  Validation: {result['message']}")
    print(f"  Flags: {result['flags']}")
    if result['redacted'] != sample['text']:
        print(f"  Redacted: {result['redacted'][:100]}...")