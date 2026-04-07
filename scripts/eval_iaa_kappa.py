import os
import sys
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import spacy

def evaluate_chapter(nlp, text, gold_chars):
    doc = nlp(text[:50000])
    extracted = set([
        ent.text.strip().lower()
        for ent in doc.ents
        if ent.label_ == "PERSON"
        and 1 <= len(ent.text.split()) <= 2
        and ent.text[0].isupper()
        and ent.text.lower() not in {"i", "he", "she", "they", "we", "you"}
    ])
    gold = set([g.lower() for g in gold_chars])
    tp = len(gold & extracted)
    fn = len(gold - extracted)
    fp = len(extracted - gold)
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall    = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1        = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    return precision, recall, f1, tp, fn, fp, extracted

def main():
    dataset_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'dataset'))
    gold_file   = os.path.join(dataset_dir, "multi_chapter_gold.json")

    with open(gold_file, 'r', encoding='utf-8') as f:
        gold_data = json.load(f)

    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        nlp = spacy.load("en_core_web_md")

    print("Evaluating NER Precision / Recall / F1 vs. Gold Standard...\n")

    all_p, all_r, all_f1 = [], [], []

    for i in range(5):
        ch_num    = i + 1
        text_path = os.path.join(dataset_dir, f"chapter_{ch_num}.txt")
        if not os.path.exists(text_path):
            print(f"  Missing {text_path}, skipping.")
            continue

        with open(text_path, 'r', encoding='utf-8') as f:
            text = f.read()

        gold_chars = gold_data["gold_characters_per_chapter"][i]
        p, r, f1, tp, fn, fp, extracted = evaluate_chapter(nlp, text, gold_chars)

        all_p.append(p)
        all_r.append(r)
        all_f1.append(f1)

        print(f"Chapter {ch_num}:")
        print(f"  Gold Characters:     {gold_chars}")
        print(f"  Pipeline:            {len(extracted)} PERSON entities found")
        print(f"  True Positives:      {tp}  |  False Negatives (missed): {fn}")
        print(f"  Precision: {p:.3f}   Recall: {r:.3f}   F1: {f1:.3f}\n")

    if not all_p:
        print("No chapters were evaluated.")
        return

    macro_p  = sum(all_p)  / len(all_p)
    macro_r  = sum(all_r)  / len(all_r)
    macro_f1 = sum(all_f1) / len(all_f1)

    print("=" * 45)
    print("MACRO-AVERAGED RESULTS (5 chapters)")
    print("=" * 45)
    print(f"  Precision : {macro_p:.3f}")
    print(f"  Recall    : {macro_r:.3f}")
    print(f"  F1 Score  : {macro_f1:.3f}")

    if macro_r >= 0.90:
        print("\n  ✓ Recall >= 0.90: Pipeline captures all protagonist-tier characters.")
    else:
        print(f"\n  ✗ Recall = {macro_r:.3f} < 0.90: Some gold characters missed.")

if __name__ == "__main__":
    main()
