"""
Create lemma-based train/dev/test splits for all four UniMorph English files.

Split logic:
  - Group rows by lemma (or base word for derivations).
  - Shuffle lemma groups with a fixed seed, then split 80/10/10.
  - eng and eng.segmentations share the same split (same lemmas).

Output layout:
  splits/
    eng/          train.tsv  dev.tsv  test.tsv
    eng.args/     train.tsv  dev.tsv  test.tsv
    eng.deriv/    train.tsv  dev.tsv  test.tsv
    eng.seg/      train.tsv  dev.tsv  test.tsv   (same lemma partition as eng/)
"""

import os
import random
from collections import defaultdict

SEED = 42
SPLIT = (0.80, 0.10, 0.10)
HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.dirname(HERE)
OUT_DIR = os.path.join(DATA_DIR, "splits")


def read_tsv(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            parts = line.rstrip("\n").split("\t")
            rows.append(parts)
    return rows


def write_tsv(rows, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write("\t".join(row) + "\n")


def lemma_split(rows, lemma_col=0):
    """Group rows by lemma, shuffle groups, split 80/10/10."""
    groups = defaultdict(list)
    for row in rows:
        groups[row[lemma_col]].append(row)

    lemmas = sorted(groups.keys())
    rng = random.Random(SEED)
    rng.shuffle(lemmas)

    n = len(lemmas)
    n_train = int(n * SPLIT[0])
    n_dev   = int(n * SPLIT[1])

    train_lemmas = set(lemmas[:n_train])
    dev_lemmas   = set(lemmas[n_train:n_train + n_dev])
    test_lemmas  = set(lemmas[n_train + n_dev:])

    train = [r for r in rows if r[lemma_col] in train_lemmas]
    dev   = [r for r in rows if r[lemma_col] in dev_lemmas]
    test  = [r for r in rows if r[lemma_col] in test_lemmas]
    return train, dev, test


def split_and_save(rows, out_subdir, lemma_col=0):
    train, dev, test = lemma_split(rows, lemma_col=lemma_col)
    base = os.path.join(OUT_DIR, out_subdir)
    write_tsv(train, os.path.join(base, "train.tsv"))
    write_tsv(dev,   os.path.join(base, "dev.tsv"))
    write_tsv(test,  os.path.join(base, "test.tsv"))
    n_lemmas = len(set(r[lemma_col] for r in rows))
    print(f"  {out_subdir:15s}  lemmas={n_lemmas:6d}  "
          f"train={len(train):7d}  dev={len(dev):6d}  test={len(test):6d}")


# ── eng (and shared lemma partition for eng.segmentations) ───────────────────
print("Reading eng ...")
eng_rows = read_tsv(os.path.join(DATA_DIR, "eng"))
print("Reading eng.segmentations ...")
seg_rows = read_tsv(os.path.join(DATA_DIR, "eng.segmentations"))

print("\nBuilding shared lemma split for eng / eng.segmentations ...")
eng_train, eng_dev, eng_test = lemma_split(eng_rows, lemma_col=0)

# derive which lemmas landed in each split
train_lemmas = set(r[0] for r in eng_train)
dev_lemmas   = set(r[0] for r in eng_dev)
test_lemmas  = set(r[0] for r in eng_test)

# apply the same partition to segmentations
seg_train = [r for r in seg_rows if r[0] in train_lemmas]
seg_dev   = [r for r in seg_rows if r[0] in dev_lemmas]
seg_test  = [r for r in seg_rows if r[0] in test_lemmas]

print("\nWriting splits:")
for subdir, (tr, dv, te) in [("eng", (eng_train, eng_dev, eng_test)),
                               ("eng.seg", (seg_train, seg_dev, seg_test))]:
    base = os.path.join(OUT_DIR, subdir)
    write_tsv(tr, os.path.join(base, "train.tsv"))
    write_tsv(dv, os.path.join(base, "dev.tsv"))
    write_tsv(te, os.path.join(base, "test.tsv"))
    n_lemmas = len(set(r[0] for r in tr + dv + te))
    print(f"  {subdir:15s}  lemmas={n_lemmas:6d}  "
          f"train={len(tr):7d}  dev={len(dv):6d}  test={len(te):6d}")

# ── eng.args ─────────────────────────────────────────────────────────────────
print("Reading eng.args ...")
args_rows = read_tsv(os.path.join(DATA_DIR, "eng.args"))
split_and_save(args_rows, "eng.args", lemma_col=0)

# ── eng.derivations.tsv ───────────────────────────────────────────────────────
print("Reading eng.derivations.tsv ...")
deriv_rows = read_tsv(os.path.join(DATA_DIR, "eng.derivations.tsv"))
split_and_save(deriv_rows, "eng.deriv", lemma_col=0)

print(f"\nAll splits written to {OUT_DIR}/")
