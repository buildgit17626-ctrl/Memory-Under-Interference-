"""Lossless specification formatting; no semantic summary or reference content."""

import ast


def compact_specification(source: str, entry: str) -> str:
    """Join plain-prose docstring lines; preserve examples/quoted lines exactly."""
    tree = ast.parse(source)
    function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == entry)
    node = function.body[0].value
    if not isinstance(node, ast.Constant) or not isinstance(node.value, str):
        raise ValueError("Expected target docstring")
    lines = source.splitlines(keepends=True)
    start = sum(len(s) for s in lines[: node.lineno - 1]) + node.col_offset
    end = sum(len(s) for s in lines[: node.end_lineno - 1]) + node.end_col_offset
    literal = source[start:end]
    quote_at = min((i for i in (literal.find('"""'), literal.find("'''")) if i >= 0), default=-1)
    if quote_at < 0:
        raise ValueError("Expected triple-quoted task specification")
    head, body, tail = literal[: quote_at + 3], literal[quote_at + 3 : -3], literal[-3:]
    output, prose = [], []
    example = False

    def flush():
        if prose:
            output.append(" ".join(prose))
            prose.clear()

    protected = []
    for line in body.splitlines():
        if line.lstrip().startswith(">>>"):
            example = True
        keep = example or any(c in line for c in ('"', "'", "\\", "`"))
        if keep:
            flush()
            output.append(line)
            protected.append(line)
            if example and not line.strip():
                example = False
        elif line.strip():
            prose.append(line.strip())
        else:
            flush()
    flush()
    compact = "\n".join(output)
    if body.split() != compact.split() or any(line not in compact for line in protected):
        raise ValueError("Compaction lost words or protected example formatting")
    result = source[:start] + head + "\n" + compact + "\n" + tail + source[end:]
    ast.parse(result)
    return result
