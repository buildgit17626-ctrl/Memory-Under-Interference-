"""Explicit draft materials for the revised study; no inference or implicit choices."""

from collections.abc import Callable
from itertools import product

R1_POLICIES = (
    "full_history",
    "no_history",
    "verbatim_replay",
    "compact_summary",
    "oracle_selective",
)


def condition_matrix(
    experiment: str,
    task_ids: list[str],
    models: list[str],
    *,
    ks: tuple[int, ...] = (2, 3, 4, 6),
    lengths: tuple[int, ...] = (1000, 2000),
    positions: tuple[str, ...] = ("beginning", "end"),
) -> list[dict]:
    """Count actual cells rather than borrowing provisional call allocations."""
    if len(set(task_ids)) != len(task_ids) or len(set(models)) != len(models):
        raise ValueError("Task and model IDs must be unique")
    cells = []
    if experiment == "M1":
        if not ks or any(k not in {2, 3, 4, 6} for k in ks) or len(set(ks)) != len(ks):
            raise ValueError("Invalid K grid")
        cells = [{"k": k, "mode": mode} for k, mode in product(ks, ("passive", "active", "filler"))]
    elif experiment == "R1":
        cells = [{"policy": policy} for policy in R1_POLICIES]
    elif experiment == "M3R2_v2":
        if any(n <= 0 for n in lengths) or any(
            p not in {"beginning", "middle", "end"} for p in positions
        ):
            raise ValueError("Invalid interference grid")
        cells = [
            {"filler_tokens": n, "similarity": kind, "position": position}
            for n, kind, position in product(
                lengths, ("irrelevant", "related", "near_duplicate"), positions
            )
        ]
    else:
        raise ValueError("Unknown revised experiment")
    return [
        {"experiment": experiment, "task_id": tid, "model": model, **cell}
        for tid, model, cell in product(task_ids, models, cells)
    ]


def m1_prompt(
    target: dict,
    companions: list[dict],
    mode: str,
    target_position: int,
    *,
    filler: str | None = None,
    count: Callable[[str], int] | None = None,
) -> dict:
    """Use specifications only; keep target and bundle success distinguishable."""
    tasks = list(companions)
    if not 0 <= target_position <= len(tasks):
        raise ValueError("Invalid counterbalanced target position")
    tasks.insert(target_position, target)
    names = [t["entry_point"] for t in tasks]
    if len(set(names)) != len(names) or any(not n.isidentifier() for n in names):
        raise ValueError("Bundle entry points must be distinct")
    if len(tasks) not in {2, 3, 4, 6}:
        raise ValueError("Invalid bundle size")
    if mode not in {"passive", "active", "filler"}:
        raise ValueError("Unknown multitask condition")
    name = target["entry_point"]
    instruction = f"Read the background. Complete only {name}. Return only Python code.\n"
    passive_parts = [
        "[TARGET]\n" + t["prompt"] if t is target else "[BACKGROUND TASK]\n" + t["prompt"]
        for t in tasks
    ]
    passive = instruction + "\n".join(passive_parts)
    if mode == "filler":
        if filler is None or count is None:
            raise ValueError("Explicit independently length-matched filler is required")
        if target_position not in {0, len(companions)}:
            raise ValueError("Interior target needs separately matched before/after filler")
        parts = ["[TARGET]\n" + target["prompt"]]
        parts.insert(0 if target_position == len(companions) else 1, filler)
        prompt = instruction + "\n".join(parts)
        if count(prompt) != count(passive):
            raise ValueError("Complete rendered filler/passive inputs are not token-matched")
    elif mode == "active":
        prompt = "Implement every named function below. Return only Python code.\n" + "\n".join(
            t["prompt"] for t in tasks
        )
    else:
        prompt = passive
    outputs = tasks if mode == "active" else [target]
    return {
        "prompt": prompt,
        "entries": [t["entry_point"] for t in outputs],
        "task_ids": [t["task_id"] for t in outputs],
        "target_task_id": target["task_id"],
        "bundle_task_ids": [t["task_id"] for t in tasks],
        "target_position": target_position,
        "num_predict": 2048 * len(outputs),
    }


def r1_prompt(material: dict, policy: str) -> str:
    """Require reviewed summaries; selection is explicitly oracle retention."""
    if policy not in R1_POLICIES:
        raise ValueError("Unknown memory policy")
    target, query = material["target"], material["query"]
    if not target.strip() or not query.strip():
        raise ValueError("Every condition needs task information and a query")
    before, preference, after = (material[k] for k in ("before", "preference", "after"))
    if policy == "no_history":
        parts = [target, query]
    elif policy == "oracle_selective":
        parts = [target, preference, query]
    elif policy == "compact_summary":
        if material.get("summary_reviewed") is not True or not material.get("summary", "").strip():
            raise ValueError("A reviewed task-complete summary is required")
        parts = [material["summary"], query]
    else:
        parts = [target, before, preference, after]
        if policy == "verbatim_replay":
            parts.append(target)
        parts.append(query)
    return "\n".join(parts)


def interference_prompt(
    target: str,
    filler: str,
    position: str,
    *,
    similarity: str,
    expected_filler_tokens: int,
    count: Callable[[str], int],
    distractor_review: dict | None = None,
) -> str:
    """New near-duplicate conditions require an auditable discrimination review."""
    if count(filler) != expected_filler_tokens:
        raise ValueError("Filler token count mismatch")
    if similarity not in {"irrelevant", "related", "near_duplicate"}:
        raise ValueError("Unknown semantic category")
    if similarity == "near_duplicate" and (
        not distractor_review
        or not all(
            distractor_review.get(k)
            for k in ("compatible_signature", "distinguishing_case_ids", "audit_path")
        )
    ):
        raise ValueError("Compatible signatures and validated distinguishing cases required")
    if position not in {"beginning", "end"}:
        raise ValueError("Middle requires separately validated token-position material")
    return "\n".join([target, filler] if position == "beginning" else [filler, target])
