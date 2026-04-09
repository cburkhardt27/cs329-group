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

## Tasks

| File                | Task          | Input                  | Target         |
| ------------------- | ------------- | ---------------------- | -------------- |
| `eng.args`          | Lemmatization | `inflected_form` only  | `lemma`        |
| `eng.segmentations` | Segmentation  | `inflected_form + tag` | `segmentation` |

`eng` overlaps with `eng.args` and is not used for evaluation.

The core challenge in lemmatization is irregular inflection (e.g., `ate` → `eat`, `went` → `go`) and tag ambiguity (e.g., `reads` is N;PL or V;PRS;3;SG). The meaningful comparison axis is **model tier** (Haiku vs. Sonnet vs. Opus) — not access tier (free vs. paid), since the same model gives the same results regardless.

---

## Baselining

### How many samples?

Three stratified samples of 300 rows each per file (900 rows total per file). This gives:

- A mean ± range across samples to account for sampling variance
- ~±4 percentage point confidence interval per sample
- 2 uploads per model — very feasible manually

The answer key is kept separate from the input so the model never sees gold labels.

### Workflow

1. Generate mini CSVs (one-time):

   ```bash
   python scripts/make_mini.py
   ```

   Creates 4 input files and 4 answer key files in `mini/`.

2. **Send 2 separate messages** (one per task) using the prompts below — paste the CSV content
   directly into each message rather than attaching files. Save each response as:

   ```
   mini/args_predictions_<model>.csv
   mini/seg_predictions_<model>.csv
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

Send **2 separate messages** — one per task. Paste the CSV contents directly after the prompt.

### Message 1 — Lemmatization (`args_input.csv`)

```
For each row, predict the base lemma (dictionary headword) of the inflected word. Return ONLY a CSV saved as args_predictions_[model].csv with columns: sample_id,id,predicted_lemma. No explanation. Do not skip rows.

Examples: eating→eat, went→go, mice→mouse, runs→run

Data:
[paste CSV contents here]
```

### Message 2 — Segmentation (`seg_input.csv`)

```
For each row, split the inflected word into morphemes using | as the boundary marker. Use - for irregular forms that cannot be cleanly segmented (e.g. ate, went). Return ONLY a CSV saved as seg_predictions_[model].csv with columns: sample_id,id,predicted_segmentation. No explanation. Do not skip rows.

Examples: eating→eat|ing, plays→play|s, geese→-

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
