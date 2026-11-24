"""Owner-approved first-person wording edits; no numerical or scientific revisions."""

# Exact source/target prose is kept together for review.
# ruff: noqa: E501
VOICE_EDITS = {
    "The later studies use the original fixed 40-task roster for both models. They": "In our later studies, we use the original fixed 40-task roster for both models. We",
    "The audit preserves failed requests and capped generations.": "We preserve failed requests and capped generations.",
    "The study is revised and partly exploratory.": "Our study is revised and partly exploratory.",
    "The results concern two small quantized models, one code benchmark and one CPU": "Our results concern two small quantized models, one code benchmark and one CPU",
    "The existing MemoryGraph implementation is audited at commit": "We audited our existing MemoryGraph implementation at commit",
    "Its saved synthetic evaluation contains 600 labelled query--memory pairs,": "Our saved synthetic evaluation contains 600 labelled query--memory pairs,",
    "The HumanEval+ study and this synthetic benchmark are never pooled.": "We do not pool our HumanEval+ study with this synthetic benchmark.",
    "The audit re-extracts saved outputs using the frozen extractor and checks native": "We re-extract saved outputs using the frozen extractor and check native",
    "Internal IDs are retained here to connect the narrative to frozen protocols.": "We retain internal IDs here to connect our narrative to the frozen protocols.",
    "The author will complete Zenodo publication separately.": "We will complete Zenodo publication separately.",
    "Zenodo publication\nis left to the author and is not performed by this GitHub handoff.": "We will complete Zenodo publication separately; this GitHub handoff does not publish it.",
    "AI assistance supported setup, autonomous Ollama execution,": "We used AI assistance for setup, autonomous Ollama execution,",
    "AI-generated constructions were subject\nto the recorded reference/witness checks;": "We subjected AI-generated constructions\nto the recorded reference/witness checks;",
    "The broad starting claims about load, replay and a possible recognition--generation\ngap motivated the project but are not all tested by this release.": "Our broad starting claims about load, replay and a possible recognition--generation\ngap motivated this project, but we do not test all of them in this release.",
    "HumanEval/32's original oracle anomaly is retained, with an exclusion\nsensitivity.": "We retain HumanEval/32's original oracle anomaly and report an exclusion\nsensitivity.",
    "Original block baselines, drift flags and time/power windows remain in the\nexport.": "We retain the original block baselines, drift flags and time/power windows in our\nexport.",
    "The pinned MemoryGraph source snapshot includes local CRUD, ranking, a fixed": "Our pinned MemoryGraph source snapshot includes local CRUD, ranking, a fixed",
    "These examples are selected saved requests for HumanEval/0 on 0.5B, not new\nprompt variants.": "We selected these saved requests for HumanEval/0 on 0.5B; they are not new\nprompt variants.",
    "The release's\nrelated-work table records each publication's design, overlap and the limited\ndistinction supported here.": "Our related-work\ntable records each publication's design, overlap and the limited distinction\nsupported here.",
}


def first_person(text: str) -> str:
    for before, after in VOICE_EDITS.items():
        text = text.replace(before, after)
    return text
