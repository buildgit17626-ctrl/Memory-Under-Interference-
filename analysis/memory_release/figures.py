"""Static scientific figures; every numerical mark has a saved source table."""

import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

from analysis.memory_release.common import AUDIT, MODELS, RELEASE, directories

POLICIES = [
    "full_history",
    "no_history",
    "verbatim_replay",
    "lossless_compaction",
    "oracle_selective",
]
NAMES = ["Full history", "Target/query", "Replay", "Compaction", "Oracle"]
COLORS = ["#334e68", "#c56b29", "#387c6d", "#88619a", "#b44f61"]


def save(fig, name, data=None):
    fig.savefig(RELEASE / "figures" / (name + ".pdf"), bbox_inches="tight")
    fig.savefig(RELEASE / "figures" / (name + ".png"), bbox_inches="tight", dpi=180)
    if data is not None:
        pd.json_normalize(data, sep=".").to_csv(RELEASE / "tables" / (name + ".csv"), index=False)
    plt.close(fig)


def arrows(ax, boxes, edges):
    for _name, (x, y, w, h, text) in boxes.items():
        ax.add_patch(
            FancyBboxPatch(
                (x, y),
                w,
                h,
                boxstyle="round,pad=0.02",
                facecolor="#edf2f7",
                edgecolor="#334e68",
                linewidth=1,
            )
        )
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=10)
    for first, second in edges:
        a, b = boxes[first], boxes[second]
        ax.add_patch(
            FancyArrowPatch(
                (a[0] + a[2], a[1] + a[3] / 2),
                (b[0], b[1] + b[3] / 2),
                arrowstyle="-|>",
                mutation_scale=12,
                color="#334e68",
            )
        )
    ax.set(xlim=(0, 12), ylim=(0, 4))
    ax.axis("off")


def main():
    directories()
    plt.rcParams.update(
        {
            "font.family": "DejaVu Serif",
            "font.size": 10,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )
    conditions = json.loads((AUDIT / "conditions.json").read_text())
    effects = json.loads((AUDIT / "paired-effects.json").read_text())
    fig, ax = plt.subplots(figsize=(11, 2.8))
    arrows(
        ax,
        {
            "a": (
                0.1,
                1,
                2.3,
                1.8,
                "Task specification\n+ controlled context\n(fixed literal prompts)",
            ),
            "b": (3.05, 1, 2.3, 1.8, "Sequential CPU\ncode generation\n0.5B / 1.5B"),
            "c": (
                6.05,
                1,
                2.3,
                1.8,
                "Restricted target tests\nalternative suites\nin the R2 audit",
            ),
            "d": (
                9.05,
                1,
                2.65,
                1.8,
                "Paired task outcomes\ntokens / latency\nCPU-package estimates",
            ),
        },
        [("a", "b"), ("b", "c"), ("c", "d")],
    )
    save(fig, "framework")

    fig, axes = plt.subplots(1, 2, figsize=(10, 3.2), sharey=True)
    rows = []
    for ax, model in zip(axes, MODELS, strict=True):
        for mode, color in zip(("passive", "active", "filler"), COLORS, strict=False):
            selected = [
                next(
                    r
                    for r in conditions
                    if r["stage"] == "M1"
                    and r["model"] == model
                    and r["condition"] == f"{mode}/K{k}"
                )
                for k in (2, 3, 4, 6)
            ]
            means = np.array([r["task_weighted_pass"]["estimate"] * 100 for r in selected])
            bounds = np.array([r["task_weighted_pass"]["ci95"] for r in selected]) * 100
            ax.errorbar(
                [2, 3, 4, 6],
                means,
                yerr=[means - bounds[:, 0], bounds[:, 1] - means],
                marker="o",
                color=color,
                label=mode.capitalize(),
                capsize=2,
            )
            rows.extend(selected)
        ax.set(
            title=model.split(":")[-1],
            xlabel="Number of task descriptions, K",
            ylim=(-3, 103),
            xticks=[2, 3, 4, 6],
        )
        ax.grid(axis="y", alpha=0.2)
    axes[0].set_ylabel("Focal-target pass rate (%)")
    axes[1].legend(fontsize=9)
    fig.tight_layout()
    save(fig, "m1", rows)

    cross = pd.read_csv(AUDIT / "cross-pass-per-response.csv")
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.3), sharey=True)
    rows = []
    cells = ["target_only", "distractor_only", "both_pass", "both_fail", "invalid_or_censored"]
    cell_names = ["Target only", "Distractor only", "Both pass", "Neither", "Censored/invalid"]
    for ax, model in zip(axes, MODELS, strict=True):
        base = cross[cross.model == model]
        bottom = np.zeros(3)
        for cell, label, color in zip(cells, cell_names, COLORS, strict=True):
            vals = []
            for group in ("isolated", "irrelevant_", "near_duplicate_"):
                g = base[
                    base.condition.eq(group)
                    if group == "isolated"
                    else base.condition.str.startswith(group)
                ]
                n = int(g.cell.eq(cell).sum())
                vals.append(n / len(g) * 100)
                rows.append(
                    {
                        "model": model,
                        "group": group,
                        "cell": cell,
                        "count": n,
                        "attempts": len(g),
                        "percent": vals[-1],
                    }
                )
            ax.bar(np.arange(3), vals, bottom=bottom, label=label, color=color, width=0.65)
            bottom += vals
        ax.set(
            xticks=np.arange(3),
            xticklabels=["Isolation\nN=40", "Irrelevant\nN=160", "Competing\nN=160"],
            title=model.split(":")[-1],
        )
    axes[0].set_ylabel("Share of saved requests (%)")
    axes[1].legend(bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=9)
    fig.tight_layout()
    save(fig, "cross_outcomes", rows)

    fig, axes = plt.subplots(1, 2, figsize=(10, 3), sharey=True)
    rows = []
    for ax, model in zip(axes, MODELS, strict=True):
        grid = []
        for filler in ("irrelevant", "related", "near_duplicate"):
            vals = []
            for suffix in ("1000_beginning", "1000_end", "2000_beginning", "2000_end"):
                row = next(
                    r
                    for r in conditions
                    if r["stage"] == "M3R2"
                    and r["model"] == model
                    and r["condition"] == filler + "_" + suffix
                )
                vals.append(row["successes"] / row["usable_correctness"] * 100)
                rows.append(row)
            grid.append(vals)
        im = ax.imshow(grid, vmin=0, vmax=100, cmap="YlGnBu", aspect="auto")
        for i in range(3):
            for j in range(4):
                ax.text(
                    j,
                    i,
                    f"{grid[i][j]:.1f}%",
                    ha="center",
                    va="center",
                    color="white" if grid[i][j] > 55 else "black",
                )
        ax.set(
            xticks=range(4),
            xticklabels=["1k/start", "1k/end", "2k/start", "2k/end"],
            yticks=range(3),
            yticklabels=["Irrelevant", "Related", "Competing"],
            title=model.split(":")[-1],
        )
        ax.tick_params(axis="x", labelsize=9)
    fig.colorbar(im, ax=axes, label="Target pass rate (%)", fraction=0.03, pad=0.02)
    save(fig, "interference_matrix", rows)

    fig, axes = plt.subplots(2, 2, figsize=(10, 6))
    rows = []
    for j, model in enumerate(MODELS):
        selected = [
            next(
                r
                for r in conditions
                if r["stage"] == "R1" and r["model"] == model and r["condition"] == policy
            )
            for policy in POLICIES
        ]
        x = np.arange(5)
        for i, field, scale, ylabel in (
            (0, "task_weighted_pass", 100, "Pass rate (%)"),
            (1, "net_wh_per_correct_covered", 1000, "Estimated net CPU-package mWh/correct"),
        ):
            vals = np.array([r[field]["estimate"] * scale for r in selected])
            bounds = np.array([r[field]["ci95"] for r in selected]) * scale
            axes[i, j].bar(x, vals, color=COLORS)
            axes[i, j].errorbar(
                x,
                vals,
                yerr=[vals - bounds[:, 0], bounds[:, 1] - vals],
                fmt="none",
                color="black",
                capsize=3,
            )
            axes[i, j].set(xticks=x, xticklabels=NAMES)
            axes[i, j].tick_params(axis="x", labelrotation=25, labelsize=9)
            axes[i, j].set_ylabel(ylabel, fontsize=9)
        axes[0, j].set_title(model.split(":")[-1] + "; 40 tasks/policy")
        rows.extend(selected)
    fig.tight_layout()
    save(fig, "r1_policies", rows)

    fig, axes = plt.subplots(1, 2, figsize=(10, 3.5), sharey=True)
    for ax, model in zip(axes, MODELS, strict=True):
        selected = [r for r in rows if r["model"] == model]
        points = []
        for r, name, color in zip(selected, NAMES, COLORS, strict=True):
            e, p = r["net_wh_per_correct_covered"], r["task_weighted_pass"]
            x, y = e["estimate"] * 1000, p["estimate"] * 100
            ax.errorbar(
                x,
                y,
                xerr=[[x - e["ci95"][0] * 1000], [e["ci95"][1] * 1000 - x]],
                yerr=[[y - p["ci95"][0] * 100], [p["ci95"][1] * 100 - y]],
                color=color,
                fmt="o",
                capsize=2,
                alpha=0.8,
            )
            offsets = {
                "Oracle": (7, 14),
                "Compaction": (7, -14),
                "Full history": (6, -14),
                "Replay": (6, 12),
                "Target/query": (6, 7),
            }
            ax.annotate(
                name,
                (x, y),
                xytext=offsets[name],
                textcoords="offset points",
                fontsize=8,
                arrowprops={"arrowstyle": "-", "color": color, "linewidth": 0.5},
            )
            points.append((x, y))
        frontier = sorted(
            (x, y)
            for x, y in points
            if not any(xx <= x and yy >= y and (xx < x or yy > y) for xx, yy in points)
        )
        ax.plot(
            [p[0] for p in frontier],
            [p[1] for p in frontier],
            ":",
            color="#777777",
            label="Observed point frontier",
        )
        ax.set(title=model.split(":")[-1], xlabel="Estimated net CPU-package mWh/correct")
        ax.grid(alpha=0.15)
    axes[0].set_ylabel("Target pass rate (%)")
    axes[1].legend(fontsize=8, loc="lower right")
    fig.tight_layout()
    save(fig, "pareto", rows)

    forest = []
    bounds = json.loads((RELEASE / "tables/cross-specification-sensitivities.json").read_text())
    for model in MODELS:
        for variant, label in (
            ("complete_case", "Cross-pass: complete case"),
            ("unknown_lower_bound", "Cross-pass: adverse bound"),
        ):
            r = next(
                r
                for r in bounds
                if r["model"] == model
                and r["variant"] == variant
                and r["comparison"] == "near-minus-irrelevant"
            )
            forest.append(r | {"label": model.split(":")[-1] + " " + label})
        for family, label in (("M3R2_primary_2", "Target accuracy: competing - irrelevant"),):
            r = next(
                r
                for r in effects
                if r["model"] == model and r["variant"] == "primary" and r["family"] == family
            )
            forest.append(r | {"label": model.split(":")[-1] + " " + label})
    fig, ax = plt.subplots(figsize=(10, 3.4))
    for i, r in enumerate(forest):
        point, low, high = r["estimate"] * 100, r["ci95"][0] * 100, r["ci95"][1] * 100
        ax.errorbar(
            point,
            i,
            xerr=[[point - low], [high - point]],
            fmt="o",
            capsize=3,
            color="#387c6d" if "1.5b" in r["model"] else "#334e68",
        )
        ax.text(25, i, f"n={r['n_units']}", va="center", fontsize=8)
    ax.set(
        yticks=range(len(forest)),
        yticklabels=[r["label"] for r in forest],
        xlabel="Paired difference (percentage points)",
        xlim=(-27, 31),
    )
    ax.axvline(0, color="gray", linewidth=0.8)
    ax.invert_yaxis()
    fig.tight_layout()
    save(fig, "paired_effects", forest)

    fig, ax = plt.subplots(figsize=(11, 3.2))
    arrows(
        ax,
        {
            "a": (
                0.05,
                1.1,
                2.2,
                1.8,
                "Local memory CRUD\nfictional preferences\nplain-text store",
            ),
            "b": (
                2.9,
                1.1,
                2.45,
                1.8,
                "TF-IDF / embeddings\n+ optional alias graph\nranked candidates",
            ),
            "c": (6, 1.1, 2.35, 1.8, "Human selection\nlimited conflict check\nexplicit approval"),
            "d": (
                9,
                1.1,
                2.7,
                1.8,
                "Optional local Ollama\nwith / without memory\nno integrated MG1",
            ),
        },
        [("a", "b"), ("b", "c"), ("c", "d")],
    )
    ax.text(
        6,
        0.35,
        "Separate synthetic retrieval evaluation: no HumanEval+ pooling or energy claims",
        ha="center",
        fontsize=10,
    )
    save(fig, "memorygraph_architecture")
    print(json.dumps({"figures_written": 8, "numerical_source_tables": 6}), flush=True)


if __name__ == "__main__":
    main()
