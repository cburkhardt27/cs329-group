#import "../lib.typ": *

#show: template.with(
  title: [Presupposition Projection in LLMs: \ A Multilingual Perspective],
  description: [Literature Review and Dataset Survey],
  authors: (
    (name: "Coralynn Yang"),
  ),
  accent: "#5B6DAE",
  h1-prefix: "Section",
  bibliography_file: none,
)

= Introduction

Presupposition projection is a core phenomenon in formal pragmatics: certain linguistic constructions carry background assumptions that survive embedding under negation, questions, and modal operators. For example, the sentence _"Claire stopped practicing piano"_ presupposes that she was practicing before, and this assumption persists when the sentence is negated (_"Claire didn't stop"_) or questioned (_"Did Claire stop?"_). Identifying whether a presupposition is triggered and whether it survives projection is non-trivial even for humans trained in linguistics, and represents a significant challenge for large language models (LLMs).

This document surveys the literature on presupposition projection as it intersects with natural language inference (NLI) and LLM evaluation, first focusing on English-language work, then turning to the substantially thinner literature on multilingual presupposition. We conclude with a survey of datasets relevant to a multilingual presupposition projection benchmark.

= Presupposition Projection in English: The Unsolved Problem

== Linguistic Background

The formal study of presupposition dates to Frege and Russell, but the projection problem was crystallized by Karttunen (1973). Karttunen identified a taxonomy of _presupposition plugs_, _holes_, and _filters_: plugs block projection (e.g., verbs of saying), holes allow it through (negation, questions, modals), and filters pass presuppositions through only under certain conditions (conditionals, conjunctions). This taxonomy remains the basis for modern computational treatments.

Factivity is a closely related phenomenon: factive predicates such as _know_, _realize_, and _regret_ presuppose the truth of their complement, while non-factive predicates such as _believe_ and _think_ do not. The sentence _"Maya knows that the project succeeded"_ entails the project succeeded; _"Maya believes that the project succeeded"_ does not. Levinson (1983) provides a thorough overview of presupposition in pragmatic theory, distinguishing semantic from pragmatic presupposition and laying out the problem of presupposition failure.

== NLI Models and Pragmatic Competence

The dominant paradigm for evaluating LLM understanding of logical and pragmatic relationships is Natural Language Inference (NLI): given a premise and a hypothesis, classify the relationship as _entailment_, _neutral_, or _contradiction_. Large-scale benchmarks such as SNLI and MultiNLI drove progress in encoder models but were not designed to test pragmatic competence. Early targeted probing (Jeretic et al., 2020; White & Rawlins, 2018) established that NLI models perform near chance on presupposition triggers despite high aggregate accuracy — a baseline failure that has not been resolved by scale alone.

More recent work confirms the gap persists in frontier LLMs. Sravanthi et al. (2024) introduce PUB, a 28,000-item pragmatics understanding benchmark spanning fourteen phenomena including presupposition; GPT-4 and comparable models lag significantly behind human performance on presupposition-specific items. Azin et al. (2025) release CONFER, an 18,000-pair NLI dataset targeting conditional inference and presupposition, and show that both fine-tuned NLI models and instruction-tuned LLMs struggle substantially with the task. Sieker et al. (2025) take a targeted approach, showing that LLMs systematically fail to challenge false presuppositions in high-stakes queries — the model treats presupposed content as given even when the presupposition is factually wrong. Ma et al. (2025) survey the full landscape of pragmatics evaluation for LLMs and identify presupposition projection as one of the most persistently underperformed categories, attributing the gap to the absence of large-scale, construction-specific training signal.

White & Rawlins (2018) focused specifically on factivity, proposing a dataset of factive and non-factive predicate constructions for NLI and showing that models systematically fail to distinguish the two classes. Their annotation protocol, which codes verb-specific projection behavior, has influenced subsequent dataset construction.

== Cleft Constructions and Embedded Questions

Cleft constructions are particularly diagnostic for presupposition projection. In _"It was Ramlah who found the bug,"_ the cleft presupposes that someone found the bug and asserts only the identity of that person. When embedded as a question — _"Was it Ramlah who found the bug?"_ — the identity is questioned but the existence of the bug-finding event remains presupposed. LLMs consistently misclassify this relationship as _neutral_, reasoning that the question makes the event uncertain, when the gold label is _entailment_ with respect to the existential presupposition.

This failure is not merely academic. It represents the model conflating _questioning the focus_ (who did it) with _questioning the presupposition_ (whether it happened) — a distinction that requires sensitivity to both information structure and the semantics of question formation. Current LLM performance on cleft projection tasks hovers around 35–70%, compared to human accuracy of approximately 95% (Jeretic et al., 2020).

== Why the Problem Persists

Several structural factors contribute to persistent LLM underperformance on presupposition:

+ *Training data bias.* Standard NLI corpora contain few examples of presupposition triggers in embedded contexts. Models trained on SNLI/MNLI learn to exploit surface-level cues (negation words, quantifiers) rather than deeper pragmatic structure. Ma et al. (2025) document this directly, noting that pragmatic phenomena are systematically underrepresented in pre-training and instruction-tuning corpora.

+ *Annotation artifacts.* Gururangan et al. (2018) demonstrated that NLI datasets contain distributional artifacts that models exploit as shortcuts. Presupposition datasets are small enough that models may not generalize beyond training artifacts.

+ *Evaluation conflation.* Many benchmarks group presupposition with entailment without distinguishing the mechanism, obscuring where exactly models fail. Sravanthi et al. (2024) address this in PUB by separating presupposition from other pragmatic phenomena, enabling finer-grained diagnosis.

+ *Lack of fine-grained probing.* Probing studies tend to focus on syntax (agreement, binding) rather than the semantics-pragmatics interface. Presupposition sits precisely at this interface, making it difficult to attribute failures to a single representational deficiency. Yu et al. (2025) find that pragmatic competence does emerge across training stages but does not scale reliably to presupposition projection specifically.

= Presupposition Across Languages: An Understudied Frontier

== Cross-Lingual Challenges

Presupposition is not uniform across languages. Languages differ in:

- *Morphological encoding of factivity.* Languages like Turkish use evidential morphology that grammaticalizes information source, creating complex interactions with presupposition that English lacks.
- *Cleft availability.* French _c'est...qui/que_ clefts have different distributional properties than English _it_-clefts; Mandarin lacks a direct structural equivalent.
- *Question formation.* Languages with topic-prominent structure (Mandarin, Japanese) form embedded questions differently, affecting how presuppositions project across clausal boundaries.
- *Definiteness.* Presuppositions of existence tied to definite descriptions (the classic _"The present king of France"_ problem) interact with how languages grammaticalize definiteness — many languages (Russian, Mandarin, Hindi) have no overt definite article.

These cross-lingual differences mean that an LLM trained primarily on English may have learned presupposition handling strategies that are language-specific, not universal.

== Existing Multilingual Work

Research on presupposition projection beyond English is limited. The most directly relevant work is surveyed below, organized by region and language family.

*Romance languages.* Caudal & Nicolas (2009) investigated French factive and semi-factive predicates, noting that verbs like _savoir_ (know) and _remarquer_ (notice) have subtly different projection profiles than their English counterparts. Quer (2007) examined presupposition in Spanish embedded questions, with attention to the interaction between mood (indicative vs. subjunctive) and projection — Spanish subjunctive morphology is itself a presupposition trigger in certain environments, a morphosyntactic signal absent from English.

*Slavic languages.* Kobyliński et al. (2023) present the most complete non-English presupposition dataset to date: a Polish factivity corpus of 2,432 verb-complement pairs spanning 309 unique verbs, annotated by linguists with >90% inter-annotator agreement. Available at #link("https://github.com/grant-TraDA/factivity-classification"), it is the most methodologically rigorous non-English factivity resource identified in this survey.

*Arabic.* Alhafni et al. (2025) introduce ALPS (Arabic Linguistic & Pragmatic Suite), a 531-item expert-curated diagnostic benchmark covering 15 linguistic tasks including a presupposition submodule (20 items). While small, ALPS is the only dataset identified that directly annotates presupposition in a non-Indo-European language. Human performance on ALPS is 84.6% single-pass; best LLM performance trails by a significant margin.

*Germanic languages.* MultiPragEval (Park et al., 2024) evaluates pragmatic competence in four languages — English, German, Korean, and Mandarin Chinese — using 1,200 multiple-choice items based on Grice's cooperative maxims. It does not specifically annotate presupposition projection, but it is the only dataset to include non-Romance, non-Slavic languages (Korean, Chinese) in a comparative pragmatics evaluation. Results show substantial cross-lingual performance variation, with models performing best in English and worst in Korean.

*Multilingual NLI infrastructure.* The XNLI benchmark (Conneau et al., 2018) extends MultiNLI to 15 languages via expert translation, covering Arabic, Chinese, Hindi, Turkish, Russian, Swahili, and others. XNLI items are not presupposition-targeted, but the infrastructure for parallel NLI evaluation is directly applicable to inserting presupposition-specific items.

== The Research Gap

Despite the recent growth of pragmatics benchmarks, the landscape for presupposition projection specifically remains sparse outside English. The situation for non-Romance, non-Slavic languages is particularly thin:

- *Arabic* has 20 presupposition-annotated items (ALPS) — too small for LLM evaluation
- *Korean and Mandarin* have multilingual pragmatics data (MultiPragEval) but no presupposition-specific annotation
- *Japanese, Hindi, Turkish, Russian, Hebrew* have no identified presupposition or factivity datasets at all

No existing work has constructed parallel presupposition projection items across multiple languages, evaluated the same LLM cross-lingually on presupposition, or investigated whether languages with morphological presupposition triggers (Turkish evidentials, Spanish subjunctive, Korean sentence-final particles) systematically affect LLM performance. This is the gap our project targets.

= Dataset Survey

The following datasets are relevant to constructing a multilingual presupposition projection benchmark. We organize them by their primary utility.

== Presupposition and Pragmatics Benchmarks

=== English Presupposition Datasets

#table(
  columns: (auto, auto, 1fr),
  inset: 7pt,
  stroke: 0.5pt + luma(200),
  align: (left, left, left),
  table.header(
    [*Dataset*], [*Size*], [*Description*]
  ),
  [FraCaS], [80 items], [Formal reasoning test suite, Section 5. Gold-standard presupposition items; small but widely cited.],
  [IMPPRES \ #text(size: 8pt)[Jeretic et al., 2020]], [25,000+ pairs], [Semi-automatically generated NLI pairs for presupposition (9 subfamilies incl. clefts, change-of-state, factives) and scalar implicature. NLI format.],
  [White & Rawlins \ #text(size: 8pt)[2018]], [~1,000 pairs], [NLI pairs for factive/non-factive predicates. Foundational factivity annotation protocol.],
  [PUB \ #text(size: 8pt)[Sravanthi et al., 2024]], [28,000 items], [14 pragmatics tasks including presupposition, as MCQA. ACL 2024.],
  [CONFER \ #text(size: 8pt)[Azin et al., 2025]], [18,000 pairs], [NLI for conditional inference and presupposition; both fine-tuned and LLM baselines reported. CAIAC 2025.],
  [UPHILL \ #text(size: 8pt)[Kaur et al., 2024]], [~1,000 items], [Health-domain queries with false presuppositions; tests whether LLMs reject misinformation. ACL 2024.],
)

=== Multilingual and Non-English Datasets

#table(
  columns: (auto, auto, auto, 1fr),
  inset: 7pt,
  stroke: 0.5pt + luma(200),
  align: (left, left, left, left),
  table.header(
    [*Dataset*], [*Languages*], [*Size*], [*Description*]
  ),
  [XNLI \ #text(size: 8pt)[Conneau et al., 2018]], [15 languages \ (incl. Arabic, Chinese, \ Hindi, Turkish, \ Russian, Korean)], [7,500 pairs], [Expert-translated MultiNLI dev/test. Not presupposition-targeted but widely used NLI infrastructure.],
  [Polish Factivity \ #text(size: 8pt)[Kobyliński et al., 2023]], [Polish], [2,432 pairs \ (309 verbs)], [Expert-annotated factivity classification; >90% inter-annotator agreement. Most rigorous non-English factivity resource.],
  [ALPS \ #text(size: 8pt)[Alhafni et al., 2025]], [Arabic], [531 items \ (20 presupposition)], [Diagnostic benchmark for Arabic linguistic and pragmatic reasoning; includes a presupposition submodule. Expert-curated.],
  [MultiPragEval \ #text(size: 8pt)[Park et al., 2024]], [English, German, \ Korean, Chinese], [1,200 items \ (300/language)], [Gricean pragmatics evaluation across 4 languages. Not presupposition-specific but the only dataset including Korean and Mandarin in a comparative pragmatics framework. GenBench workshop, EMNLP 2024.],
)

== Multilingual Parallel Corpora (for Example Generation)

#table(
  columns: (auto, 1fr, auto),
  inset: 7pt,
  stroke: 0.5pt + luma(200),
  align: (left, left, left),
  table.header(
    [*Dataset*], [*Description*], [*Languages*]
  ),
  [Tatoeba], [Large collection of sentence pairs with community translations. Useful for identifying parallel presupposition triggers.], [300+],
  [OPUS / Europarl], [Parallel parliamentary proceedings. Rich in cleft constructions and embedded questions (political register).], [21 EU languages],
  [Universal Dependencies], [Syntactically annotated corpora; clefts and relative clauses can be extracted via dependency patterns.], [100+],
  [World Atlas of Language Structures (WALS)], [Typological database; useful for identifying which languages grammaticalize features relevant to presupposition (definiteness, evidentiality, mood).], [2,662 languages],
)

== Proposed Dataset Structure

For a multilingual presupposition projection benchmark, we propose the following item structure, adapted across languages:

#table(
  columns: (auto, 1fr),
  inset: 7pt,
  stroke: 0.5pt + luma(200),
  align: (left, left),
  table.header(
    [*Field*], [*Description*]
  ),
  [`premise`], [Sentence containing a presupposition trigger (cleft, factive verb, change-of-state verb, definite description)],
  [`hypothesis`], [The presupposed proposition, stated as a bare declarative],
  [`label`], [`entailment` (presupposition projects) or `neutral` (projection blocked)],
  [`trigger_type`], [Categorical: `cleft`, `factive`, `change_of_state`, `definite`, `embedded_question`],
  [`embedding`], [Categorical: `affirmative`, `negation`, `polar_question`, `wh_question`, `modal`, `conditional`],
  [`language`], [ISO 639-1 code],
  [`translation_source`], [Whether the item was expert-translated, machine-translated, or natively constructed],
)

Target languages for initial construction: English (baseline), French, Spanish, Polish, and one non-Indo-European language (Mandarin or Turkish) to test typologically distinct presupposition mechanisms.

= Baseline Experiments: Polish Factivity Dataset

To establish a cross-lingual reference point, we ran baselines on the Polish factivity corpus (Kobyliński et al., 2023). The task is binary classification: given a Polish premise embedding a verb complement, predict whether the verb is factive (_True_) or non-factive (_False_).

== Data Leakage in the Original Split

We first ran a verb-lookup classifier on the dataset's original train/test split — for each test item, look up the verb's majority label in the training set, falling back to majority class for unseen verbs. This achieved 98.6% accuracy and F1 = 0.965, which is inflated. Inspection reveals two problems:

- *Verb overlap:* 144 of 171 unique test verbs (84.2%) also appear in training, so 94.0% of test rows are decided by memorized lookup with no generalization.
- *Duplicate premises:* 34 premises appear verbatim in both splits.

The 98.6% measures lexical memorization, not presupposition competence.

== Verb-Held-Out Split

We re-split the full corpus (2,432 items, 309 verbs) by verb: verbs were stratified by majority label and partitioned 80/20, with all instances of each verb assigned entirely to one split (zero overlap guaranteed).

#table(
  columns: (auto, auto, auto, auto),
  inset: 7pt,
  stroke: 0.5pt + luma(200),
  align: (left, right, right, right),
  table.header([], [*Verbs*], [*Rows*], [*Factive rows*]),
  [Train], [247], [1,919], [525 (27.4%)],
  [Test],  [62],  [513],   [82 (16.0%)],
)

== Baselines and Results

Three baselines on the verb-held-out test set:

#table(
  columns: (1fr, auto, auto, auto, auto),
  inset: 7pt,
  stroke: 0.5pt + luma(200),
  align: (left, right, right, right, right),
  table.header([*Baseline*], [*Acc*], [*P*], [*R*], [*F1*]),
  [Majority class (always non-factive)],  [0.840], [0.000], [0.000], [0.000],
  [Verb-lookup (all fallback to majority)],[0.840], [0.000], [0.000], [0.000],
  [Morphology/stem heuristic],            [0.881], [0.657], [0.537], [0.591],
)

*Majority class* (always non-factive): 84.0% accuracy, F1 = 0.000 — cannot identify factive verbs at all.

*Verb-lookup*: since no test verb appears in training, every prediction falls back to majority class. Identical to majority — confirming that lexical lookup provides zero signal on genuinely unseen verbs.

*Morphology/stem heuristic*: a hand-crafted classifier using Polish verb stem patterns associated with factivity (e.g. _wiedzie\__ "know", _zauważ\__ "notice", _widać\__ "it is seen") and non-factivity (e.g. _myśl\__ "think", _twierdzi\__ "claim", _wydaje się\__ "seems"). No training data is used.

== Analysis

The morphology heuristic achieves F1 = 0.591 on unseen verbs, well above zero, showing that verb morphology carries partial signal for factivity. But precision (0.657) and recall (0.537) both leave substantial room — a system with genuine presupposition competence should exceed this clearly.

Error analysis shows the harder cases are verbs whose factivity is opaque from form alone. *False negatives* (factive verbs missed) include _zdawać sobie sprawę, że\__ ("be aware that"), _wyjść na jaw, że\__ ("come to light that"), and _uświadomić komuś, że\__ ("make someone realize") — factive but without obvious perceptual stems. *False positives* (non-factive mislabelled factive) include _odpowiedzieć, że\__ ("answer that") and _zapowiedzieć, że\__ ("announce that"), which contain perception-like stems but are used non-factively.

On negated premises (n=22), the heuristic achieves F1 = 0.667, slightly above the full-set figure, consistent with the theoretical expectation that factive verbs retain projection under negation — though the subset is too small for firm conclusions.

== Implications for LLM Evaluation

The verb-held-out protocol sets a meaningful floor: a system scoring below F1 = 0.591 is outperformed by a zero-training-data stem heuristic. Scores in the 0.60–0.80 range would suggest partial morphological generalization; scores above ~0.85 would indicate access to deeper semantic knowledge beyond surface form. This framing transfers naturally to other languages: English datasets like IMPPRES (Jeretic et al., 2020) likely have the same verb-leakage issue in their original splits, and applying a consistent verb-held-out protocol across languages would make cross-lingual factivity comparison meaningful.

== Note on the Arabic Dataset

The ALPS benchmark (Alhafni et al., 2025) is the only identified dataset with presupposition-annotated items in a non-Indo-European language. The paper promises a CC-BY-4.0 release, but as of writing no repository or HuggingFace upload exists. The authors' profiles (#link("https://github.com/balhafni")[github.com/balhafni], #link("https://github.com/CAMeL-Lab")[CAMeL-Lab]) can be monitored for release.

= Conclusion

Presupposition projection remains an open problem for LLMs even in English, where performance trails human accuracy by 25–60 percentage points. The multilingual dimension is almost entirely unstudied computationally. Our verb-held-out baseline on Polish factivity establishes a morphological heuristic ceiling of F1 = 0.591 for genuinely unseen verbs — the relevant target for evaluating LLMs on this task. Existing multilingual NLI infrastructure (XNLI, OPUS) and language-specific work (French factivity, Spanish subjunctive, Polish morphology, Arabic ALPS) provide a foundation for a targeted cross-lingual benchmark. Such a benchmark would determine whether LLM presupposition failures are English-specific or reflect deeper deficiencies in modeling the semantics-pragmatics interface.

= References

#set par(hanging-indent: 1.5em)

Alhafni, B., et al. (2025). ALPS: A diagnostic challenge set for Arabic linguistic & pragmatic reasoning. _arXiv:2602.17054_.

Azin, T., Dumitrescu, D., Inkpen, D., & Singh, R. (2025). Let's CONFER: A dataset for evaluating natural language inference models on conditional inference and presupposition. _Proceedings of the 38th Canadian Conference on Artificial Intelligence (CAIAC 2025)_.

Caudal, P., & Nicolas, D. (2009). Types of degrees and types of event structures. In C. Maienborn & A. Wöllstein (Eds.), _Event Arguments: Foundations and Applications_. Niemeyer.

Conneau, A., Rinott, R., Lample, G., Williams, A., Bowman, S., Schwartz, R., & Stoyanov, V. (2018). XNLI: Evaluating cross-lingual sentence representations. _EMNLP 2018_.

Gururangan, S., Swayamditta, S., Levy, O., & Smith, N. A. (2018). Annotation artifacts in natural language inference data. _NAACL 2018_.

Jeretic, P., Warstadt, A., Bhooshan, S., & Williams, A. (2020). Are natural language inference models IMPPRESsive? Probing the IMPPRES dataset. _Proceedings of ACL 2020_.

Karttunen, L. (1973). Presuppositions of compound sentences. _Linguistic Inquiry_, 4(2), 169–193.

Kaur, N., Choudhury, M., & Pruthi, D. (2024). Evaluating large language models for health-related queries with presuppositions. _Findings of ACL 2024_.

Kobyliński, Ł., et al. (2023). Polish natural language inference and factivity: An expert-based dataset and benchmarks. _Natural Language Engineering_, Cambridge Core.

Levinson, S. C. (1983). _Pragmatics_. Cambridge University Press.

Ma, B., Li, Y., Zhou, W., Gong, Z., Liu, Y. J., Jasinskaja, K., Friedrich, A., Hirschberg, J., Kreuter, F., & Plank, B. (2025). Pragmatics in the era of large language models: A survey on datasets, evaluation, opportunities and challenges. _Proceedings of ACL 2025_.

Park, D., et al. (2024). MultiPragEval: Multilingual pragmatic evaluation of large language models. _Proceedings of the GenBench Workshop at EMNLP 2024_.

Quer, J. (2007). Subjunctive and clausal presuppositions in Spanish embedded questions. _Lingua_, 117(3), 526–542.

Sieker, J., Lachenmaier, C., & Zarrieß, S. (2025). LLMs struggle to reject false presuppositions when misinformation stakes are high. _arXiv:2505.22354_.

Sravanthi, S. L., Doshi, M., Kalyan, T. P., Murthy, R., Bhattacharyya, P., & Dabre, R. (2024). PUB: A pragmatics understanding benchmark for assessing LLMs' pragmatics capabilities. _Findings of ACL 2024_.

White, A. S., & Rawlins, K. (2018). The lexical semantics of factivity as natural language inference. In _Proceedings of SALT 28_.

Williams, A., Nangia, N., & Bowman, S. (2018). A broad-coverage challenge corpus for sentence understanding through inference. _NAACL 2018_.

Yu, K., Zeng, Q., Xuan, W., Li, W., Wu, J., & Voigt, R. (2025). The pragmatic mind of machines: Tracing the emergence of pragmatic competence in large language models. _Proceedings of EACL 2025_.
