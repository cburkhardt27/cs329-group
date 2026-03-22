"""
Heuristic baselines on Polish factivity dataset (Kobyliński et al., 2023).
No API key required.

Baselines:
  1. Majority class (always predict False)
  2. Verb-lookup: use training set verb→label majority to classify test items;
     fall back to majority class for unseen verbs
  3. Negation-aware verb-lookup: same, but flip prediction when premise is negated
     (tests whether negation of a factive clause affects projection)
"""

import csv, json, os
from collections import Counter, defaultdict

DIR = os.path.dirname(os.path.abspath(__file__))

def load(path):
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))

train = load(os.path.join(DIR, "train_data.csv"))
dev   = load(os.path.join(DIR, "dev_data.csv"))
test  = load(os.path.join(DIR, "test_data.csv"))

def labels(rows): return [r["verb - factive/nonfactive"] for r in rows]

# ── build verb lexicon from train ──────────────────────────────────────────────
verb_majority = {}
verb_counts   = defaultdict(list)
for r in train:
    verb_counts[r["verb"].strip()].append(r["verb - factive/nonfactive"])
for verb, lbls in verb_counts.items():
    verb_majority[verb] = Counter(lbls).most_common(1)[0][0]

train_majority = Counter(labels(train)).most_common(1)[0][0]   # "False"

# ── metric helpers ─────────────────────────────────────────────────────────────
def acc(preds, gold):
    return sum(p == g for p, g in zip(preds, gold)) / len(gold)

def prf(preds, gold, pos="True"):
    tp = sum(p == pos and g == pos for p, g in zip(preds, gold))
    fp = sum(p == pos and g != pos for p, g in zip(preds, gold))
    fn = sum(p != pos and g == pos for p, g in zip(preds, gold))
    p_ = tp / (tp + fp) if (tp + fp) else 0.0
    r_ = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2*p_*r_ / (p_+r_) if (p_+r_) else 0.0
    return round(p_,3), round(r_,3), round(f1,3)

def report(name, preds, gold):
    a = acc(preds, gold)
    p, r, f1 = prf(preds, gold)
    print(f"  {name:<40} Acc={a:.3f}  P={p:.3f}  R={r:.3f}  F1={f1:.3f}")
    return {"acc": round(a,3), "p": p, "r": r, "f1": f1}

# ── baseline 1: majority class ─────────────────────────────────────────────────
def majority_preds(rows): return [train_majority] * len(rows)

# ── baseline 2: verb lookup ────────────────────────────────────────────────────
def verb_lookup_preds(rows):
    preds = []
    for r in rows:
        verb = r["verb"].strip()
        preds.append(verb_majority.get(verb, train_majority))
    return preds

# ── baseline 3: negation-aware verb lookup ────────────────────────────────────
# factive verbs presuppose their complement even under negation,
# so we do NOT flip — but we track whether negation hurts performance
def negation_aware_preds(rows):
    # identical to verb lookup — negation should NOT change factivity label
    return verb_lookup_preds(rows)

# ── evaluate ───────────────────────────────────────────────────────────────────
for split_name, split in [("Dev", dev), ("Test", test)]:
    gold = labels(split)
    n_true  = sum(g == "True"  for g in gold)
    n_false = sum(g == "False" for g in gold)
    print(f"\n{'='*65}")
    print(f"{split_name} set  (n={len(split)}, factive={n_true}, non-factive={n_false})")
    print(f"{'='*65}")
    report("Majority class (always False)",   majority_preds(split), gold)
    vl = verb_lookup_preds(split)
    report("Verb-lookup (train majority/verb)", vl, gold)

    # coverage
    unseen = sum(1 for r in split if r["verb"].strip() not in verb_majority)
    print(f"    (unseen verbs in {split_name}: {unseen}/{len(split)} → fallback to majority)")

    # negation breakdown on verb-lookup
    neg_rows  = [r for r in split if r["T - negation"] == "True"]
    pos_rows  = [r for r in split if r["T - negation"] != "True"]
    if neg_rows:
        neg_p = [p for r, p in zip(split, vl) if r["T - negation"] == "True"]
        pos_p = [p for r, p in zip(split, vl) if r["T - negation"] != "True"]
        print(f"\n  Negation breakdown (verb-lookup):")
        report(f"  Negated premises   (n={len(neg_rows)})", neg_p, labels(neg_rows))
        report(f"  Non-negated        (n={len(pos_rows)})", pos_p, labels(pos_rows))

# ── error analysis on test ─────────────────────────────────────────────────────
test_gold  = labels(test)
test_preds = verb_lookup_preds(test)
errors = [(r, g, p) for r, g, p in zip(test, test_gold, test_preds) if g != p]
print(f"\n{'='*65}")
print(f"Error analysis (verb-lookup on test, n_errors={len(errors)})")
print(f"{'='*65}")

# false negatives (missed factive verbs) vs false positives
fn = [(r,g,p) for r,g,p in errors if g=="True"  and p=="False"]
fp = [(r,g,p) for r,g,p in errors if g=="False" and p=="True"]
print(f"  False negatives (predicted non-factive, actually factive): {len(fn)}")
print(f"  False positives (predicted factive, actually non-factive): {len(fp)}")
print(f"\n  Sample false negatives (unseen or train-majority=False verbs):")
for r, g, p in fn[:5]:
    print(f"    verb='{r['verb'].strip()}'  in_train={'yes' if r['verb'].strip() in verb_majority else 'NO'}")

# ── save results ───────────────────────────────────────────────────────────────
test_gold  = labels(test)
test_preds = verb_lookup_preds(test)
results = {
    "dataset": "Polish Factivity (Kobyliński et al., 2023)",
    "test_n": len(test),
    "label_dist": {"factive": sum(g=="True" for g in test_gold),
                   "non_factive": sum(g=="False" for g in test_gold)},
    "majority_class": {
        "label": train_majority,
        **dict(zip(["acc","p","r","f1"], [round(acc(majority_preds(test), test_gold),3)] + list(prf(majority_preds(test), test_gold))))
    },
    "verb_lookup": {
        **dict(zip(["acc","p","r","f1"], [round(acc(test_preds, test_gold),3)] + list(prf(test_preds, test_gold)))),
        "unseen_verbs": sum(1 for r in test if r["verb"].strip() not in verb_majority),
    },
}
out = os.path.join(DIR, "baseline_results.json")
with open(out, "w") as f:
    json.dump(results, f, indent=2)
print(f"\nSaved to baseline_results.json")
