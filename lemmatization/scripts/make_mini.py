"""
Generate mini evaluation sets for manual LLM baselining.

Creates one combined input CSV per file (3 x 150 = 450 rows, sample_id 1-3).
Upload the input CSV to a model, save its output as predictions, then score.

Output:
  mini/eng_input.csv       mini/eng_answers.csv
  mini/args_input.csv      mini/args_answers.csv
  mini/seg_input.csv       mini/seg_answers.csv
  mini/deriv_input.csv     mini/deriv_answers.csv

Run:
    python scripts/make_mini.py
"""

import os
import csv
import random
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.dirname(HERE)
OUT_DIR  = os.path.join(DATA_DIR, "mini")

SAMPLE_SIZE = 150
SEEDS = [42, 123, 7]


def read_tsv(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            rows.append(line.rstrip("\n").split("\t"))
    return rows


def stratified_sample(rows, n, tag_col, seed):
    by_tag = defaultdict(list)
    for row in rows:
        coarse = row[tag_col].split(";")[0].split("|")[0] if tag_col < len(row) else "UNK"
        by_tag[coarse].append(row)
    rng = random.Random(seed)
    tags = sorted(by_tag.keys())
    per_tag = max(1, n // len(tags))
    sample = []
    for tag in tags:
        bucket = list(by_tag[tag])
        rng.shuffle(bucket)
        sample.extend(bucket[:per_tag])
    rng.shuffle(sample)
    return sample[:n]


def write_csv(rows, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(rows)


os.makedirs(OUT_DIR, exist_ok=True)

# ── lemmatization files (eng, eng.args, eng.segmentations) ───────────────────
for prefix, filename in [("eng", "eng"), ("args", "eng.args")]:
    print(f"Processing {filename} ...")
    rows = read_tsv(os.path.join(DATA_DIR, filename))

    input_rows  = [["sample_id", "id", "inflected_form", "tag"]]
    answer_rows = [["sample_id", "id", "lemma"]]

    for sample_num, seed in enumerate(SEEDS, start=1):
        for row_id, row in enumerate(stratified_sample(rows, SAMPLE_SIZE, tag_col=2, seed=seed), start=1):
            lemma, word, tag = row[0], row[1], row[2]
            input_rows.append([sample_num, row_id, word, tag])
            answer_rows.append([sample_num, row_id, lemma])

    write_csv(input_rows,  os.path.join(OUT_DIR, f"{prefix}_input.csv"))
    write_csv(answer_rows, os.path.join(OUT_DIR, f"{prefix}_answers.csv"))
    print(f"  {len(input_rows)-1} rows  ({len(SEEDS)} samples x {SAMPLE_SIZE})")

# ── eng.segmentations — segmentation task (col 3, not col 0) ─────────────────
print("Processing eng.segmentations ...")
seg_rows = [r for r in read_tsv(os.path.join(DATA_DIR, "eng.segmentations")) if len(r) >= 4]

input_rows  = [["sample_id", "id", "inflected_form", "tag"]]
answer_rows = [["sample_id", "id", "segmentation"]]

for sample_num, seed in enumerate(SEEDS, start=1):
    for row_id, row in enumerate(stratified_sample(seg_rows, SAMPLE_SIZE, tag_col=2, seed=seed), start=1):
        word, tag, seg = row[1], row[2], row[3]
        input_rows.append([sample_num, row_id, word, tag])
        answer_rows.append([sample_num, row_id, seg])

write_csv(input_rows,  os.path.join(OUT_DIR, "seg_input.csv"))
write_csv(answer_rows, os.path.join(OUT_DIR, "seg_answers.csv"))
print(f"  {len(input_rows)-1} rows  ({len(SEEDS)} samples x {SAMPLE_SIZE})")

# ── derivations ───────────────────────────────────────────────────────────────
print("Processing eng.derivations.tsv ...")
deriv_rows = read_tsv(os.path.join(DATA_DIR, "eng.derivations.tsv"))

input_rows  = [["sample_id", "id", "base_word", "pos_pair", "affix"]]
answer_rows = [["sample_id", "id", "derived_word"]]

for sample_num, seed in enumerate(SEEDS, start=1):
    for row_id, row in enumerate(stratified_sample(deriv_rows, SAMPLE_SIZE, tag_col=2, seed=seed), start=1):
        base, derived, pos_pair, affix = row[0], row[1], row[2], row[3]
        input_rows.append([sample_num, row_id, base, pos_pair, affix])
        answer_rows.append([sample_num, row_id, derived])

write_csv(input_rows,  os.path.join(OUT_DIR, "deriv_input.csv"))
write_csv(answer_rows, os.path.join(OUT_DIR, "deriv_answers.csv"))
print(f"  {len(input_rows)-1} rows  ({len(SEEDS)} samples x {SAMPLE_SIZE})")

print(f"\nDone. Files in {OUT_DIR}/")
print("Upload each *_input.csv to a model, save output as *_predictions_<model>.csv")
