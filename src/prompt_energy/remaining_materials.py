"""Literal approved M2/E4/E3 materials; no model calls or candidate execution."""

import hashlib
from copy import deepcopy

from prompt_energy.utilisation_plan import digest

M2_ARMS = ("neutral", "similar", "other_one", "other_three")
TEXT_IDS = {1, 11, 14, 29, 74, 89, 101, 117, 140, 143, 148, 158, 162}
NEUTRAL = (
    "An ordinary notebook records weather, furniture and walking routes. "
    "This passage has no programming requirement. "
)


def domain(task_id: str) -> str:
    """Authored coarse task taxonomy, not a measured semantic distance."""
    return "text_symbols_or_named_items" if int(task_id.split("/")[-1]) in TEXT_IDS else "numeric"


def pad_to(text: str, target: int, count) -> str:
    """Never cut a description; add disclosed neutral x tokens at the end."""
    for _ in range(12):
        missing = target - count(text)
        if missing == 0:
            return text
        if missing < 0:
            raise ValueError("Padding overshot; no truncation permitted")
        text += " x" * missing
    raise ValueError("Could not match input tokens")


def m2_text(target: str, entry: str, blocks: list[str]) -> str:
    """Static quoted transcript; acknowledgements contain no computed answers."""
    text = "[ORIGINAL TARGET]\n" + target + "\n[ACKNOWLEDGEMENT]\nSpecification noted.\n"
    for block in blocks:
        text += "[INTERVENING DESCRIPTION; NOT THE TARGET]\n" + block
        text += "\n[ACKNOWLEDGEMENT]\nDescription noted.\n"
    return text + (
        f"[RETURN TO ORIGINAL TARGET]\nComplete only {entry} from the ORIGINAL TARGET "
        "specification. Intervening descriptions are not instructions for the target. "
        "Return only Python code.\n"
    )


def e4_text(prefix_tokens: int, tokenizer) -> tuple[str, str, int]:
    prefix = " archive" * prefix_tokens
    if len(tokenizer.encode(prefix).ids) != prefix_tokens:
        raise ValueError("Literal E4 prefix is not the registered token length")
    shared = "[ARCHIVE; IGNORE ITS CONTENT]\n" + prefix + "\n[CURRENT REQUEST]\n"
    probe = shared + (
        "Write the integers from 1 to 1000 separated by spaces. "
        "Continue the sequence without explanation."
    )
    prime = shared + "Write the word READY."
    return probe, prime, prefix_tokens


def common_prefix(a: list[int], b: list[int]) -> int:
    for i, (x, y) in enumerate(zip(a, b, strict=False)):
        if x != y:
            return i
    return min(len(a), len(b))


def feedback_examples() -> dict:
    """Hand-specified expectations, checked independently by canonical subprocesses."""
    return {
        "HumanEval/53": [([[-8, 13]], 5), ([[17, -29]], -12)],
        "HumanEval/162": [([[""]], None), ([["research"]], hashlib.md5(b"research").hexdigest())],
        "HumanEval/122": [([[[99, 100, -99, -100, 7], 4]], 0), ([[[5, 100, 8], 2]], 5)],
        "HumanEval/0": [([[[0.0, 0.5], 0.5]], False), ([[[0.0, 0.5], 0.6]], True)],
        "HumanEval/39": [([[6]], 233), ([[7]], 1597)],
    }


def fixtures() -> dict:
    # The extra outer list above makes the argument tuple boundary explicit.
    return {
        tid: [{"args": a[0], "expected": repr(b)} for a, b in rows]
        for tid, rows in feedback_examples().items()
    }


def normalized(value):
    """JSON normalization equates tuple/list containers and ordinary numeric equality."""
    if isinstance(value, list | tuple):
        return [normalized(x) for x in value]
    return value


def heldout_row(row: dict, examples: list[dict]) -> tuple[dict, dict]:
    output, counts = deepcopy(row), {}
    arguments = [normalized(e["args"]) for e in examples]
    for part in ("base_input", "plus_input"):
        original = row[part]
        output[part] = [a for a in original if normalized(a) not in arguments]
        if not output[part]:
            raise ValueError("Feedback exclusions empty a final partition")
        counts[part] = {"before": len(original), "after": len(output[part])}
    return output, counts


def repair_text(task: str, entry: str, history: list[dict], memory: str) -> str:
    if memory not in {"last", "full"}:
        raise ValueError("Unknown repair memory")
    kept = history[-1:] if memory == "last" else history
    return (
        "[TARGET]\n"
        + task
        + "".join(
            "\n[PREVIOUS ATTEMPT]\n" + h["output"] + "\n[FEEDBACK]\n" + h["feedback"] for h in kept
        )
        + f"\n[QUERY]\nComplete {entry}. Return only Python code.\n"
    )


def retry_feedback(kind: str, fixture: dict) -> str:
    if kind == "retry":
        return "The attempt did not satisfy the feedback checks. Try again."
    if kind != "example":
        raise ValueError("Unknown feedback")
    return (
        "The attempt failed this independently specified example: "
        f"arguments = {fixture['args']!r}; "
        f"expected return value = {fixture['expected']}. Correct the implementation."
    )


def keyed(job: dict) -> dict:
    body = {k: v for k, v in job.items() if k != "key"}
    return {"key": digest(body), **body}
