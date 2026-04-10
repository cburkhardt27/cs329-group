I have here four data sets of 774 of the same sentences for English, Amharic, Igbo, and Zulu.

For baselining, my intuition is to use all 774 sentences for each model (though that may be computaitonally expensive, open to changing this if necessary). For any model development, develop a train : test split strategy.

These sentences are fill-in-the-blank questions for pronoun resolution (there are two options given to the model per sentence). This should harmonize with *Wino-X* style data.

The data is pulled from https://github.com/InstituteforDiseaseModeling/Bridging-the-Gap-Low-Resource-African-Languages

This dataset provides a baseline for linguistic tasks; from the initial dataset, I filtered the given questions for sufficiently difficult pronoun resolution tasks according to these four conditions:

Criterion 1 — Both options are person names or animate entities. Check if both option1 and option2 start with a capital letter (proper names like Dennis/Logan, Emily/Carrie, Ian/Aaron). This alone would eliminate most object-blank items (garage/backyard, television/radio, shampoo/hair). It's the single highest-value filter.
Criterion 2 — Both options appear in the sentence before the blank. True anaphora means the pronoun refers back to an antecedent that was already introduced. If an option doesn't appear earlier in the sentence, it's not a referent — it's a new entity being introduced at the blank position.
Criterion 3 — The blank follows a discourse connective. Items where _ comes after "because", "so", "but", "since", "although", "when", "and", "after", "before" are the classic Winograd structure — a main clause introduces two entities, then a subordinate clause uses a pronoun that requires reasoning to resolve. This selects for the causally/contrastively ambiguous cases.
Criterion 4 — The blank is NOT preceded by a determiner. Your existing check — "the", "a", "an" before _ means it's a noun slot, not a pronoun slot. Keep this as a safety net.

This filtering produced the 774 sentences that are cross-comparable.

Baselining: Claude & Open AI, both free and the best paid model for each, with zeroshot and fewshot for each model.

ZEROSHOT PROMPT: 
    Fill in the blank for each sentence below. Just give me the number and your answer.

FEWSHOT PROMPT: (potentially compare difficulty of few-shot examples and whether they're given in english or the native langauge)

    Fill in the blank for each sentence. Here are some examples:

    Sentence: The city councilmen refused the demonstrators a permit because _ feared violence.
    Options: The city councilmen, The demonstrators
    Answer: The city councilmen

    Sentence: The trophy doesn't fit into the brown suitcase because _ is too large.
    Options: The trophy, suitcase
    Answer: The trophy

    Sentence: Joan made sure to thank Susan for all the help _ had received.
    Options: Joan, Susan
    Answer: Joan

    Now do the same for these: []


CLARIFIED PROMPT TASK: (We shoudl tinker around with some prompt curation to see if that affects the effectiveness of each task)
You are performing a pronoun resolution task. In each sentence below, the blank (_) represents a pronoun that has been removed. Your job is to determine which of the two provided options the pronoun originally referred to.
Use commonsense reasoning about the context to decide which entity is the correct referent of the missing pronoun.
For each item, respond with ONLY the number and the letter (A or B). Do not explain your reasoning.

