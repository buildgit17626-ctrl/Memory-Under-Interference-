"""Literal preference histories and observable format adherence, not mental states."""

import ast
import re

POLICIES = ("no_preference", "immediate", "buried", "replayed", "corrected")
PREFERENCE = (
    "[USER PREFERENCE]\nFor future coding tasks, return only Python code, without explanation."
)
CONFLICT = (
    "[EARLIER USER PREFERENCE]\nFor future coding tasks, explain your solution before the code."
)
CORRECTION = (
    "[USER CORRECTION]\nReplace my earlier preference for an explanation: "
    "return only Python code, without explanation."
)


def preference_prompt(target: str, query: str, history: list[str], policy: str) -> str:
    """Keep target, history and query identical; vary literal preference placement."""
    if policy not in POLICIES or len(history) != 8 or not target or not query:
        raise ValueError("Require a registered policy, target/query and eight history items")
    prefix = [target]
    if policy in {"buried", "replayed"}:
        prefix.append(PREFERENCE)
    elif policy == "corrected":
        prefix.append(CONFLICT)
    prefix.extend(history)
    if policy in {"immediate", "replayed"}:
        prefix.append(PREFERENCE)
    elif policy == "corrected":
        prefix.append(CORRECTION)
    return "\n".join([*prefix, query])


def format_adherence(raw: str | None, entry: str) -> dict:
    """Strict unfenced parse/entry proxy; comments/docstrings are not semantic prose checks."""
    raw = raw or ""
    fenced = bool(re.search(r"(?m)^\s*```", raw))
    try:
        tree = ast.parse(raw.strip())
    except (SyntaxError, ValueError, RecursionError):
        return {"plain_code": False, "has_fence": fenced, "parseable": False, "entry_found": False}
    found = any(isinstance(n, ast.FunctionDef) and n.name == entry for n in tree.body)
    return {
        "plain_code": bool(raw.strip()) and not fenced and found,
        "has_fence": fenced,
        "parseable": True,
        "entry_found": found,
    }
