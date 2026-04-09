# Lemmatization Data

Source: [UniMorph English](https://unimorph.github.io/) — morphological paradigm tables for English.

---

## Files

### `eng` — Inflectional morphology (652,477 rows)
Tab-separated: `lemma \t inflected_form \t tag`

```
eat    eating    V;V.PTCP;PRS
eat    ate       V;PST
eat    eats      N;PL
```

Tags use UniMorph schema: part of speech + features separated by `;`.
Common tags: `N;PL`, `V;PST`, `V;V.PTCP;PRS`, `V;V.PTCP;PST`, `V;PRS;3;SG`.

---

### `eng.args` — Inflectional morphology, richer verb paradigms (115,523 rows)
Same format as `eng` but from a different source. Verb-focused, with additional tags:
- `V;NFIN` — non-finite / base form (lemma = word itself)
- `V;PRS;NOM(3,SG)` — 3rd person singular present

---

### `eng.segmentations` — Inflection + morpheme boundaries (649,594 rows)
Extends `eng` with a 4th column: `lemma \t inflected_form \t tag \t segmentation`

```
eat    eating    V|V.PTCP;PRS    eat|ing
eat    ate       V;PST           -
```

`|` marks morpheme boundaries. Irregular forms get `-`.
Same underlying rows as `eng` — **splits are shared**.

---

### `eng.derivations.tsv` — Derivational morphology (225,131 rows)
Tab-separated: `base_word \t derived_word \t pos_pair \t affix`

```
connote    connotation    V:N     -ation
abandon    abandonee      N:N     -ee
back       aback          ADV:ADV  a-
```

Different task from the others (how new words are coined from existing ones, not how a word inflects). Evaluated and trained separately.

---

## Tasks

| File | Task | Input | Target |
|------|------|-------|--------|
| `eng` | Lemmatization | `inflected_form + tag` | `lemma` |
| `eng.args` | Lemmatization | `inflected_form + tag` | `lemma` |
| `eng.segmentations` | Segmentation | `inflected_form + tag` | `segmentation` |
| `eng.derivations.tsv` | Derivation | `base_word + pos_pair + affix` | `derived_word` |

The core challenge in lemmatization is irregular inflection (e.g., `ate` → `eat`, `went` → `go`) and tag ambiguity (e.g., `reads` is N;PL or V;PRS;3;SG). The meaningful comparison axis is **model tier** (Haiku vs. Sonnet vs. Opus) — not access tier (free vs. paid), since the same model gives the same results regardless.

---

## Baselining

### How many samples?

Three stratified samples of 150 rows each per file. This gives:
- A mean ± range across samples to account for sampling variance
- ~±6 percentage point confidence interval per sample (sufficient to distinguish models)
- 12 uploads per model (3 samples × 4 files) — feasible manually

The answer key is kept separate from the input so the model never sees gold labels.

### Workflow

1. Generate mini CSVs (one-time):
   ```bash
   python scripts/make_mini.py
   ```
   Creates 4 input files and 4 answer key files in `mini/`.

2. **Send 4 separate messages** (one per task) using the prompts below — paste the CSV content
   directly into each message rather than attaching files. Save each response as:
   ```
   mini/eng_predictions_<model>.csv
   mini/args_predictions_<model>.csv
   mini/seg_predictions_<model>.csv
   mini/deriv_predictions_<model>.csv
   ```

3. Score all four at once:
   ```bash
   python scripts/score_baseline.py --model sonnet
   ```
   Repeat step 2–3 for each model (e.g. `--model haiku`, `--model gpt4o`).

Scores are saved to:
- `results/<model>_scores.csv` — per-sample breakdown (shows variance across the 3 samples)
- `results/summary.csv` — all models side by side, updated automatically each run

---

## Prompts

Send each prompt as a **separate message**. Paste the contents of the input CSV directly
after the prompt text (open the file, select all, paste).

### Lemmatization — use for `eng_input.csv` and `args_input.csv` (send separately)

For `eng_input.csv`, replace `[filename]` with `eng_predictions_[model]` (e.g. `eng_predictions_sonnet`).
For `args_input.csv`, use `args_predictions_[model]`.

```
For each row, predict the base lemma of the inflected word. Return ONLY a CSV saved as [filename].csv with columns: sample_id,id,predicted_lemma. No explanation. Do not skip rows.

Tag reference: V;PST=past tense, V;V.PTCP;PRS=present participle, N;PL=plural noun, V;NFIN=base form.

Data:
[paste CSV contents here]
```

### Segmentation — use for `seg_input.csv`

```
For each row, split the inflected word into morphemes using | as the boundary marker. Use - for irregular forms that cannot be cleanly segmented (e.g. ate, went). Return ONLY a CSV saved as seg_predictions_[model].csv with columns: sample_id,id,predicted_segmentation. No explanation. Do not skip rows.

Examples: eating→eat|ing, plays→play|s, geese→-

Data:
[paste CSV contents here]
```

### Derivation — use for `deriv_input.csv`

```
For each row, apply the affix to the base word to form the derived word. pos_pair shows the part-of-speech change (e.g. V:N = verb to noun). Affixes with a leading - are suffixes; with a trailing - are prefixes. Return ONLY a CSV saved as deriv_predictions_[model].csv with columns: sample_id,id,predicted_derived_word. No explanation. Do not skip rows.

Data:
[paste CSV contents here]
```

---

## Fine-tuning Splits

For training models, use the full lemma-based splits (80/10/10):

```bash
python scripts/make_splits.py
```

Splits are written to `splits/{eng,eng.args,eng.seg,eng.deriv}/train.tsv` etc.

**Split logic**: all inflected forms of the same lemma are kept together in one split, so the test set contains only lemmas unseen during training. `eng` and `eng.segmentations` share the same split (same underlying lemmas).
