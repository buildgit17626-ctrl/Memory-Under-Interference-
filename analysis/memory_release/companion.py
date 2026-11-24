"""Read pinned MemoryGraph sources and re-rank saved scores without inference."""

import hashlib
import json
import subprocess
import zipfile

import numpy as np
import pandas as pd

from analysis.memory_audit.records import save_json
from analysis.memory_release.common import MEMORYGRAPH, MG_COMMIT, RELEASE, directories


def retrieval(frame: pd.DataFrame, score: str) -> dict:
    values = []
    for query, group in frame.groupby("query_id", sort=False):
        ranked = group.sort_values(score, ascending=False, kind="stable")
        positions = np.flatnonzero(ranked.relevant.to_numpy() == 1)
        values.append(
            {
                "query_id": query,
                "rr": float(1 / (positions[0] + 1)) if len(positions) else 0,
                "p3": float(ranked.head(3).relevant.sum() / 3),
            }
        )
    return {
        "queries": len(values),
        "mrr": float(np.mean([r["rr"] for r in values])),
        "precision_at_3": float(np.mean([r["p3"] for r in values])),
        "per_query": values,
    }


def main() -> None:
    directories()
    commit = subprocess.check_output(
        ["git", "-C", str(MEMORYGRAPH), "rev-parse", "HEAD"], text=True
    ).strip()
    if commit != MG_COMMIT:
        raise ValueError("MemoryGraph checkout is not the approved pinned revision")
    paths = subprocess.check_output(
        ["git", "-C", str(MEMORYGRAPH), "ls-files"], text=True
    ).splitlines()
    hashes = {}
    with zipfile.ZipFile(
        RELEASE / "companion/memorygraph-source.zip", "w", compression=zipfile.ZIP_DEFLATED
    ) as archive:
        for name in paths:
            blob = subprocess.check_output(
                ["git", "-C", str(MEMORYGRAPH), "show", MG_COMMIT + ":" + name]
            )
            local = (MEMORYGRAPH / name).read_bytes().replace(b"\r\n", b"\n")
            if local != blob.replace(b"\r\n", b"\n"):
                raise ValueError("Modified pinned MemoryGraph source: " + name)
            hashes[name] = hashlib.sha256(blob).hexdigest()
            archive.writestr("MemoryGraph/" + name, blob)
    source_files = [
        "results/semantic_predictions.csv",
        "results/semantic_metrics.json",
        "results/predictions.csv",
        "results/baseline_metrics.json",
        "data/generated/synthetic_relevance.csv",
    ]
    provenance = []
    for name in source_files:
        source = MEMORYGRAPH / name
        target = RELEASE / "companion" / source.name
        target.write_bytes(source.read_bytes())
        provenance.append(
            {
                "source_relative": name,
                "public_file": target.name,
                "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            }
        )
    data = pd.read_csv(MEMORYGRAPH / "data/generated/synthetic_relevance.csv")
    scores = pd.read_csv(RELEASE / "companion/semantic_predictions.csv")
    metrics = json.loads((RELEASE / "companion/semantic_metrics.json").read_text())
    if (
        hashlib.sha256((RELEASE / "companion/synthetic_relevance.csv").read_bytes()).hexdigest()
        != metrics["dataset_sha256"]
    ):
        raise ValueError("MemoryGraph synthetic dataset hash mismatch")
    if len(data) != 600 or data.user_id.nunique() != 24:
        raise ValueError("Unexpected companion dataset population")
    output = {
        "commit": commit,
        "pairs": len(data),
        "fictional_users": data.user_id.nunique(),
        "queries": data.query_id.nunique(),
        "source_files": hashes,
        "recorded_data": provenance,
        "new_inference": 0,
        "methods": {},
    }
    for method, column in (("semantic", "semantic_score"), ("tfidf", "tfidf_score")):
        result = retrieval(scores, column)
        if not np.isclose(result["mrr"], metrics[method]["mrr"], atol=1e-12):
            raise ValueError("Saved semantic MRR does not reproduce")
        output["methods"][method] = result
    demos = []
    for path in sorted((MEMORYGRAPH / "results").glob("inference_demo_*.jsonl")):
        rows = [json.loads(line) for line in path.read_text().splitlines()]
        (RELEASE / "companion" / path.name).write_bytes(path.read_bytes())
        for row in rows:
            demos.append(
                {
                    "source": path.name,
                    "variant": row["variant"],
                    "prompt_tokens": row.get("prompt_tokens"),
                    "output_tokens": row.get("output_tokens"),
                    "capped": row.get("output_tokens") == row["max_output_tokens"],
                    "mentions_unittest": "import unittest" in row.get("response", ""),
                    "correctness": row.get("correctness"),
                    "energy": row.get("energy"),
                }
            )
    output["local_demonstrations"] = demos
    save_json(RELEASE / "tables/memorygraph-audit.json", output)
    print(
        json.dumps({k: output[k] for k in ("commit", "pairs", "fictional_users", "queries")}),
        flush=True,
    )


if __name__ == "__main__":
    main()
