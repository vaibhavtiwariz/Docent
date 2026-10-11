# eval.py
"""
Evaluate Intelli-Curate's metadata extraction accuracy.

Usage:
  1. Drop test PDFs into the `eval/` folder.
  2. Copy `eval/ground_truth.example.json` to `eval/ground_truth.json` and fill
     in the true title/authors for each PDF.
  3. Set HF_TOKEN in `.env`, then run:  python eval.py

Reports per-paper results plus summary accuracy:
  - title_accuracy: exact match after normalizing case/punctuation/whitespace
  - author precision/recall/F1 over the author name sets
"""

import glob
import json
import os
import re
import string

from core.parser import extract_text_from_pdf
from core.extractor import extract_metadata_from_text

EVAL_DIR = "eval"
GT_FILE = os.path.join(EVAL_DIR, "ground_truth.json")


def normalize(s: str) -> str:
    s = s.lower().translate(str.maketrans("", "", string.punctuation))
    return re.sub(r"\s+", " ", s).strip()


def score_authors(predicted: list, actual: list) -> tuple:
    p = {normalize(a) for a in predicted if a.strip()}
    a = {normalize(x) for x in actual if x.strip()}
    if not p and not a:
        return 1.0, 1.0, 1.0
    if not p or not a:
        return 0.0, 0.0, 0.0
    tp = len(p & a)
    precision = tp / len(p)
    recall = tp / len(a)
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    return precision, recall, f1


def main() -> None:
    if not os.getenv("HF_TOKEN"):
        print("HF_TOKEN is not set. Add it to .env first, then re-run.")
        return
    if not os.path.exists(GT_FILE):
        print(f"No {GT_FILE} found.")
        print("Copy eval/ground_truth.example.json to eval/ground_truth.json")
        print("and fill in the true title/authors for each test PDF.")
        return

    with open(GT_FILE) as f:
        ground_truth = json.load(f)

    pdfs = sorted(glob.glob(os.path.join(EVAL_DIR, "*.pdf")))
    if not pdfs:
        print(f"No PDFs found in {EVAL_DIR}/. Add test papers first.")
        return

    title_hits = 0
    f1_scores = []
    evaluated = 0

    for pdf_path in pdfs:
        name = os.path.basename(pdf_path)
        if name not in ground_truth:
            print(f"SKIP  {name}: no ground truth entry")
            continue
        gt = ground_truth[name]

        print(f"\n--- {name} ---")
        text = extract_text_from_pdf(pdf_path)
        if not text:
            print("  Could not extract text from PDF.")
            continue
        pred = extract_metadata_from_text(text)

        title_ok = normalize(pred.get("title", "")) == normalize(gt.get("title", ""))
        p, r, f1 = score_authors(pred.get("authors", []), gt.get("authors", []))

        print(f"  Predicted title : {pred.get('title', '')}")
        print(f"  Expected title  : {gt.get('title', '')}")
        print(f"  Title match     : {'YES' if title_ok else 'NO'}")
        print(f"  Predicted authors: {pred.get('authors', [])}")
        print(f"  Expected authors : {gt.get('authors', [])}")
        print(f"  Author P/R/F1   : {p:.2f} / {r:.2f} / {f1:.2f}")

        title_hits += int(title_ok)
        f1_scores.append(f1)
        evaluated += 1

    if evaluated:
        print("\n========== SUMMARY ==========")
        print(f"Papers evaluated : {evaluated}")
        print(f"Title accuracy   : {title_hits}/{evaluated} ({title_hits / evaluated:.0%})")
        print(f"Mean author F1   : {sum(f1_scores) / len(f1_scores):.2f}")
        print("=============================")


if __name__ == "__main__":
    main()
