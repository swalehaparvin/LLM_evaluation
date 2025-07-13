import gdown, zipfile, os, json, requests
from pathlib import Path

RAW = Path("datasets/raw")
RAW.mkdir(exist_ok=True, parents=True)

def pull_cic_ids2017():
    url = "https://www.unb.ca/cic/datasets/ids2017.html"
    # Mirror link; change if unb.ca blocks Replit IPs
    gdown.download(url, str(RAW/"cic-ids2017.zip"), quiet=False)
    with zipfile.ZipFile(RAW/"cic-ids2017.zip") as z:
        z.extractall(RAW/"cic-ids2017/")

def pull_cti_llm():
    from datasets import load_dataset
    ds = load_dataset("ibm/cti-llm", split="train")
    ds.save_to_disk(str(RAW/"cti-llm"))

def pull_misp_galaxy():
    repo = "https://github.com/MISP/misp-galaxy/archive/refs/heads/main.zip"
    gdown.download(repo, str(RAW/"misp-galaxy.zip"), quiet=False)
    with zipfile.ZipFile(RAW/"misp-galaxy.zip") as z:
        z.extractall(RAW)

if __name__ == "__main__":
    pull_cti_llm()
    pull_misp_galaxy()
    # pull_cic_ids2017()  # uncomment if you want PCAP→CSV later