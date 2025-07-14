import pandas as pd, pathlib, json, random

csv_path = pathlib.Path("datasets/arabic_reviews_100k.csv")
df = pd.read_csv(csv_path, usecols=["text"]).dropna().sample(5_000, random_state=42)

labels = []
for txt in df["text"]:
    res = validate_mena(txt)
    labels.append(res["flags"][0] if res["flags"] else "clean")

df["label"] = labels
df = df[df["label"] != "clean"]   # keep only the **interesting** rows
df = df.append(df[df["label"] == "clean"].sample(500, random_state=42))  # add 500 clean

out_path = pathlib.Path("datasets/mena_guardrails_kaggle_fixed.jsonl")
with open(out_path, "w", encoding="utf-8") as f:
    for _, row in df.iterrows():
        f.write(json.dumps({"text": row["text"], "label": row["label"]}, ensure_ascii=False) + "\n")

print("Fixed dataset:", out_path, "rows:", len(df))