"""
Baseline experiments on Polish factivity dataset (Kobyliński et al., 2023).

Task: given a Polish premise (T PL) embedding a verb complement,
      classify whether the verb is factive (True) or non-factive (False).

Baselines:
  1. Majority class (always predict False, the majority label)
  2. Claude claude-haiku-4-5-20251001 zero-shot (Polish, no translation)
  3. Claude claude-haiku-4-5-20251001 zero-shot (English translation prompt)
"""

import csv, os, json, time
from collections import Counter
import anthropic

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_FILE = os.path.join(DATA_DIR, "test_data.csv")

client = anthropic.Anthropic()  # uses ANTHROPIC_API_KEY from env

# ── load test set ──────────────────────────────────────────────────────────────
def load_csv(path):
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))

test_rows = load_csv(TEST_FILE)
gold = [r["verb - factive/nonfactive"] for r in test_rows]   # "True" / "False"

def accuracy(preds, gold):
    assert len(preds) == len(gold)
    return sum(p == g for p, g in zip(preds, gold)) / len(gold)

def precision_recall_f1(preds, gold, pos="True"):
    tp = sum(p == pos and g == pos for p, g in zip(preds, gold))
    fp = sum(p == pos and g != pos for p, g in zip(preds, gold))
    fn = sum(p != pos and g == pos for p, g in zip(preds, gold))
    prec = tp / (tp + fp) if (tp + fp) else 0.0
    rec  = tp / (tp + fn) if (tp + fn) else 0.0
    f1   = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
    return prec, rec, f1

# ── Baseline 1: majority class ─────────────────────────────────────────────────
majority_label = Counter(gold).most_common(1)[0][0]
majority_preds = [majority_label] * len(gold)
maj_acc = accuracy(majority_preds, gold)
maj_p, maj_r, maj_f1 = precision_recall_f1(majority_preds, gold)
print(f"[Majority class = {majority_label}]")
print(f"  Acc={maj_acc:.3f}  P={maj_p:.3f}  R={maj_r:.3f}  F1={maj_f1:.3f}")
print()

# ── Baseline 2: Claude zero-shot (Polish prompt) ───────────────────────────────
SYSTEM_PL = (
    "Jesteś ekspertem językoznawczym. Odpowiedz tylko 'True' lub 'False'.\n"
    "True = czasownik faktywny (treść zdania podrzędnego jest presupozycją, "
    "tzn. nadawca zakłada jej prawdziwość).\n"
    "False = czasownik niefaktywny (treść zdania podrzędnego NIE jest presupozycją)."
)

def classify_polish(row):
    prompt = (
        f"Zdanie (T): {row['T PL'].strip()}\n"
        f"Zdanie podrzędne (H): {row['H PL'].strip()}\n"
        f"Czy czasownik '{row['verb'].strip()}' jest faktywny? Odpowiedz True lub False."
    )
    msg = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=8,
        system=SYSTEM_PL,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = msg.content[0].text.strip()
    if "True" in raw:
        return "True"
    elif "False" in raw:
        return "False"
    else:
        return "False"   # default fallback

# ── Baseline 3: Claude zero-shot (English meta-prompt) ────────────────────────
SYSTEM_EN = (
    "You are an expert linguist specialising in Polish. "
    "Answer only 'True' or 'False'.\n"
    "True  = the verb is FACTIVE: the embedded clause is presupposed as true "
    "(e.g. 'wiedzieć' / 'know', 'zauważyć' / 'notice').\n"
    "False = the verb is NON-FACTIVE: the embedded clause is not presupposed "
    "(e.g. 'myśleć' / 'think', 'przypuszczać' / 'suppose')."
)

def classify_english_meta(row):
    prompt = (
        f"Polish sentence (T): {row['T PL'].strip()}\n"
        f"Embedded clause (H): {row['H PL'].strip()}\n"
        f"Verb: {row['verb'].strip()}\n"
        "Is this verb factive? Answer True or False."
    )
    msg = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=8,
        system=SYSTEM_EN,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = msg.content[0].text.strip()
    if "True" in raw:
        return "True"
    elif "False" in raw:
        return "False"
    else:
        return "False"

# ── run both Claude baselines ──────────────────────────────────────────────────
print("Running Claude baselines on test set...")
pl_preds, en_preds = [], []
errors = 0

for i, row in enumerate(test_rows):
    try:
        pl_preds.append(classify_polish(row))
        en_preds.append(classify_english_meta(row))
    except Exception as e:
        print(f"  Error on row {i}: {e}")
        pl_preds.append("False")
        en_preds.append("False")
        errors += 1
    if (i + 1) % 50 == 0:
        print(f"  {i+1}/{len(test_rows)} done...")
    # small sleep to avoid rate limits
    time.sleep(0.05)

print(f"Done. Errors: {errors}\n")

# ── results ───────────────────────────────────────────────────────────────────
pl_acc = accuracy(pl_preds, gold)
pl_p, pl_r, pl_f1 = precision_recall_f1(pl_preds, gold)

en_acc = accuracy(en_preds, gold)
en_p, en_r, en_f1 = precision_recall_f1(en_preds, gold)

print("=== RESULTS ===")
print(f"Test set: {len(test_rows)} items  (True={sum(g=='True' for g in gold)}, False={sum(g=='False' for g in gold)})")
print()
print(f"{'Baseline':<35} {'Acc':>6}  {'P':>6}  {'R':>6}  {'F1':>6}")
print("-" * 60)
print(f"{'Majority class (always False)':<35} {maj_acc:>6.3f}  {maj_p:>6.3f}  {maj_r:>6.3f}  {maj_f1:>6.3f}")
print(f"{'Claude Haiku (Polish prompt)':<35} {pl_acc:>6.3f}  {pl_p:>6.3f}  {pl_r:>6.3f}  {pl_f1:>6.3f}")
print(f"{'Claude Haiku (English meta-prompt)':<35} {en_acc:>6.3f}  {en_p:>6.3f}  {en_r:>6.3f}  {en_f1:>6.3f}")
print()

# per-verb-category breakdown for best model
best_preds = en_preds if en_acc >= pl_acc else pl_preds
print("=== NEGATION BREAKDOWN (best model) ===")
neg_gold   = [g for r, g in zip(test_rows, gold)   if r["T - negation"] == "True"]
neg_preds  = [p for r, p in zip(test_rows, best_preds) if r["T - negation"] == "True"]
pos_gold   = [g for r, g in zip(test_rows, gold)   if r["T - negation"] != "True"]
pos_preds  = [p for r, p in zip(test_rows, best_preds) if r["T - negation"] != "True"]
if neg_gold:
    print(f"  Negated premises   (n={len(neg_gold)}): Acc={accuracy(neg_preds, neg_gold):.3f}")
print(f"  Positive premises  (n={len(pos_gold)}): Acc={accuracy(pos_preds, pos_gold):.3f}")

# save results to json for document use
results = {
    "test_n": len(test_rows),
    "label_dist": {"True": sum(g=="True" for g in gold), "False": sum(g=="False" for g in gold)},
    "majority": {"acc": round(maj_acc,3), "p": round(maj_p,3), "r": round(maj_r,3), "f1": round(maj_f1,3)},
    "claude_pl": {"acc": round(pl_acc,3), "p": round(pl_p,3), "r": round(pl_r,3), "f1": round(pl_f1,3)},
    "claude_en": {"acc": round(en_acc,3), "p": round(en_p,3), "r": round(en_r,3), "f1": round(en_f1,3)},
    "negation_breakdown": {
        "negated_acc": round(accuracy(neg_preds, neg_gold), 3) if neg_gold else None,
        "negated_n": len(neg_gold),
        "positive_acc": round(accuracy(pos_preds, pos_gold), 3),
        "positive_n": len(pos_gold),
    }
}
with open(os.path.join(DATA_DIR, "baseline_results.json"), "w") as f:
    json.dump(results, f, indent=2)
print("\nResults saved to baseline_results.json")
