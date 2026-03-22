"""
Verb-held-out split + baseline experiments on Polish factivity dataset.

Strategy: split by verb (stratified by factivity label), so no verb
appears in both train and test. Baselines:
  1. Majority class
  2. Verb-lookup (will degrade to majority on all test items, since verbs are unseen)
  3. Verb-morphology heuristic: use substring cues in the verb lemma
     (e.g. presence of perception/cognition stems) to predict factivity
"""

import csv, json, os, random
from collections import defaultdict, Counter

random.seed(42)
DIR = os.path.dirname(os.path.abspath(__file__))

def load(path):
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))

all_rows = (load(os.path.join(DIR, "train_data.csv")) +
            load(os.path.join(DIR, "dev_data.csv")) +
            load(os.path.join(DIR, "test_data.csv")))

# ── group rows by verb ─────────────────────────────────────────────────────────
verb_rows = defaultdict(list)
for r in all_rows:
    verb_rows[r["verb"].strip()].append(r)

# ── stratified verb split (80/20 train/test by verb count) ────────────────────
# separate factive and non-factive verbs, then sample 20% of each for test
factive_verbs    = [v for v, rows in verb_rows.items()
                    if Counter(r["verb - factive/nonfactive"] for r in rows).most_common(1)[0][0] == "True"]
nonfactive_verbs = [v for v, rows in verb_rows.items()
                    if Counter(r["verb - factive/nonfactive"] for r in rows).most_common(1)[0][0] == "False"]

random.shuffle(factive_verbs)
random.shuffle(nonfactive_verbs)

n_fac_test    = max(1, round(0.20 * len(factive_verbs)))
n_nonfac_test = max(1, round(0.20 * len(nonfactive_verbs)))

test_verbs  = set(factive_verbs[:n_fac_test] + nonfactive_verbs[:n_nonfac_test])
train_verbs = set(factive_verbs[n_fac_test:] + nonfactive_verbs[n_nonfac_test:])

train_rows = [r for r in all_rows if r["verb"].strip() in train_verbs]
test_rows  = [r for r in all_rows if r["verb"].strip() in test_verbs]

train_gold = [r["verb - factive/nonfactive"] for r in train_rows]
test_gold  = [r["verb - factive/nonfactive"] for r in test_rows]

print(f"Verb-split: {len(train_verbs)} train verbs / {len(test_verbs)} test verbs")
print(f"  Train rows: {len(train_rows)}  (factive={train_gold.count('True')}, non-factive={train_gold.count('False')})")
print(f"  Test rows:  {len(test_rows)}   (factive={test_gold.count('True')}, non-factive={test_gold.count('False')})")
print(f"  Verb overlap: {len(train_verbs & test_verbs)}  (should be 0)")
print()

# ── metrics ───────────────────────────────────────────────────────────────────
def acc(preds, gold):
    return sum(p == g for p, g in zip(preds, gold)) / len(gold)

def prf(preds, gold, pos="True"):
    tp = sum(p == pos and g == pos for p, g in zip(preds, gold))
    fp = sum(p == pos and g != pos for p, g in zip(preds, gold))
    fn = sum(p != pos and g == pos for p, g in zip(preds, gold))
    p_ = tp / (tp + fp) if (tp + fp) else 0.0
    r_ = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2*p_*r_ / (p_+r_) if (p_+r_) else 0.0
    return round(p_, 3), round(r_, 3), round(f1, 3)

def report(name, preds, gold):
    a = acc(preds, gold)
    p, r, f1 = prf(preds, gold)
    print(f"  {name:<44} Acc={a:.3f}  P={p:.3f}  R={r:.3f}  F1={f1:.3f}")
    return {"acc": round(a,3), "p": p, "r": r, "f1": f1}

# ── baseline 1: majority class ────────────────────────────────────────────────
majority = Counter(train_gold).most_common(1)[0][0]
print(f"Majority class in train: {majority}")

maj_preds = [majority] * len(test_rows)

# ── baseline 2: verb-lookup (will always fall back since verbs are unseen) ────
train_verb_majority = {}
for r in train_rows:
    v = r["verb"].strip()
    if v not in train_verb_majority:
        train_verb_majority[v] = Counter()
    train_verb_majority[v][r["verb - factive/nonfactive"]] += 1
train_verb_majority = {v: c.most_common(1)[0][0] for v, c in train_verb_majority.items()}

vl_preds = [train_verb_majority.get(r["verb"].strip(), majority) for r in test_rows]
n_fallback = sum(1 for r in test_rows if r["verb"].strip() not in train_verb_majority)
print(f"Verb-lookup fallbacks: {n_fallback}/{len(test_rows)} (should equal total, verbs are held out)")

# ── baseline 3: morphology/substring heuristic ────────────────────────────────
# Known factive stems/patterns in Polish:
#  - wiedzieć/wiedzieć (know), zauważyć/zauważać (notice), zobaczyć (see/notice),
#    pamiętać (remember), żałować (regret), cieszyć się (be glad),
#    dziwić się (be surprised), rozumieć/zrozumieć (realize/understand),
#    odkryć/odkrywać (discover), stwierdzić (ascertain), udowodnić (prove),
#    pokazać/pokazywać (show/demonstrate), okazać się (turn out — factive in Polish),
#    dostrzec/dostrzegać (perceive), słyszeć/słychać (hear — perception factive),
#    czuć/poczuć (feel — factive for perception), widać/widzieć (see — perception)
FACTIVE_STEMS = [
    "wiedzie", "wiedzą",           # know
    "zauważ", "zauważać",          # notice
    "zobaczy", "zobaczył",         # see/notice
    "pamięt",                      # remember
    "żałow",                       # regret
    "cieszyć", "cieszył",          # be glad
    "dziw",                        # be surprised
    "rozumie", "zrozumie",         # understand/realize
    "odkry",                       # discover
    "stwierdzi",                   # ascertain
    "udowodni",                    # prove
    "pokazał", "pokazuj", "pokaz", # show/demonstrate
    "okazał", "okazuj",            # turn out
    "dostrzeż", "dostrzeg",        # perceive
    "słysze", "słychać",           # hear
    "czuć", "poczuł", "czuje",     # feel (perception)
    "widać", "widzie", "widzę",    # see
    "spostrzeż", "spostrzeg",      # perceive
    "przyzna",                     # admit
    "wykazał", "wykaz",            # demonstrate
    "dowiodł", "dowiódł",          # prove
    "przewidzi", "przewidział",    # foresee
    "przypomni", "przypomnij",     # remind/recall
    "wiadomo",                     # it is known
    "zaobserwow",                  # observe
    "dum",                         # be proud (być dumnym)
]

NON_FACTIVE_STEMS = [
    "myśl", "myśle",               # think
    "twierdzi",                    # claim
    "uważ",                        # consider/think
    "przypuszcz",                  # suppose
    "wydaje się", "wydawało",      # seem
    "sądzi",                       # judge/think
    "mówi", "mówił",               # say
    "stwierdza",                   # state (non-factive usage)
    "planow",                      # plan
    "chcieć", "chciał",            # want
    "liczy",                       # count on
    "obawia", "bać się",           # fear
    "oczekiw",                     # expect
    "wierzy",                      # believe
    "zarzuca",                     # accuse
    "deklarow",                    # declare
    "zapewnił", "zapewnia",        # assure
    "zobowiąz",                    # commit to
    "wniosk",                      # conclude (non-factive)
    "odnosi wrażenie", "mam wrażenie",  # have the impression
    "być pewnym", "być przekonan", # be certain (non-factive)
]

def morphology_predict(verb_str):
    v = verb_str.lower()
    fac_score = sum(stem.lower() in v for stem in FACTIVE_STEMS)
    nonfac_score = sum(stem.lower() in v for stem in NON_FACTIVE_STEMS)
    if fac_score > nonfac_score:
        return "True"
    elif nonfac_score > fac_score:
        return "False"
    else:
        return majority   # tie → majority

morph_preds = [morphology_predict(r["verb"].strip()) for r in test_rows]

# ── results ───────────────────────────────────────────────────────────────────
print(f"\n{'='*65}")
print(f"VERB-HELD-OUT TEST SET  (n={len(test_rows)})")
print(f"  factive={test_gold.count('True')}, non-factive={test_gold.count('False')}")
print(f"{'='*65}")
res_maj  = report("Majority class (always non-factive)", maj_preds, test_gold)
res_vl   = report("Verb-lookup (→ all fallback to majority)", vl_preds, test_gold)
res_morph = report("Morphology/stem heuristic", morph_preds, test_gold)

# negation breakdown (morphology baseline)
neg_rows = [r for r in test_rows if r["T - negation"] == "True"]
pos_rows = [r for r in test_rows if r["T - negation"] != "True"]
if neg_rows:
    neg_p = [morphology_predict(r["verb"].strip()) for r in neg_rows]
    pos_p = [morphology_predict(r["verb"].strip()) for r in pos_rows]
    print(f"\n  Negation breakdown (morphology):")
    report(f"  Negated    (n={len(neg_rows)})", neg_p, [r["verb - factive/nonfactive"] for r in neg_rows])
    report(f"  Non-negated (n={len(pos_rows)})", pos_p, [r["verb - factive/nonfactive"] for r in pos_rows])

# ── error analysis ────────────────────────────────────────────────────────────
errors = [(r, g, p) for r, g, p in zip(test_rows, test_gold, morph_preds) if g != p]
fn = [(r,g,p) for r,g,p in errors if g=="True"  and p=="False"]
fp = [(r,g,p) for r,g,p in errors if g=="False" and p=="True"]
print(f"\n  Morphology errors: {len(errors)} total  (FN={len(fn)}, FP={len(fp)})")
print(f"  Sample FNs (factive verbs missed):")
for r,g,p in fn[:6]:
    print(f"    '{r['verb'].strip()}'")
print(f"  Sample FPs (non-factive verbs mislabelled factive):")
for r,g,p in fp[:6]:
    print(f"    '{r['verb'].strip()}'")

# ── save ──────────────────────────────────────────────────────────────────────
results = {
    "split": "verb-held-out (stratified by factivity label)",
    "train_verbs": len(train_verbs),
    "test_verbs":  len(test_verbs),
    "test_n":      len(test_rows),
    "label_dist":  {"factive": test_gold.count("True"), "non_factive": test_gold.count("False")},
    "majority":    res_maj,
    "verb_lookup": res_vl,
    "morphology":  res_morph,
}
with open(os.path.join(DIR, "verb_split_results.json"), "w") as f:
    json.dump(results, f, indent=2)
print("\nSaved to verb_split_results.json")
