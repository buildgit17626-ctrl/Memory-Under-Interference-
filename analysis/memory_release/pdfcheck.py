"""Run with the bundled PDF Python; inspect text, citations and page bounds."""

import json
import re
from pathlib import Path

import pdfplumber
from pypdf import PdfReader

BASE = Path(__file__).resolve().parents[2] / "releases/v1"


def main():
    path = BASE / "manuscript/main.pdf"
    reader = PdfReader(path)
    texts = [p.extract_text() for p in reader.pages]
    text = "\n".join(texts)
    expected = [
        "5,528",
        "8.97",
        "76.5%",
        "67.4%",
        "0.7364",
        "0.5163",
        "325.38",
        "76.39",
        "154.16",
        "50.20",
    ]
    absent = [value for value in expected if value not in text]
    log = (BASE / "manuscript/main.log").read_text(encoding="utf-8")
    tex = (BASE / "manuscript/main.tex").read_text(encoding="utf-8")
    citations = set()
    for group in re.findall(r"\\cite[pt]?\{([^}]+)\}", tex):
        citations.update(group.split(","))
    bib = (BASE / "manuscript/references.bib").read_text(encoding="utf-8")
    entries = set(re.findall(r"@\w+\{([^,]+),", bib))
    references_page = next(
        (i + 1 for i, t in enumerate(texts) if re.search(r"(?:^|\n)References\n", t)), None
    )
    aux = (BASE / "manuscript/main.aux").read_text(encoding="utf-8")
    end_page = re.search(r"\\newlabel\{maintext:end\}\{\{[^}]*\}\{(\d+)\}", aux)
    bounds = []
    with pdfplumber.open(path) as pdf:
        for index, page in enumerate(pdf.pages):
            outside = [
                c
                for c in page.chars
                if c["x0"] < -1
                or c["x1"] > page.width + 1
                or c["top"] < -1
                or c["bottom"] > page.height + 1
            ]
            if outside:
                bounds.append({"page": index + 1, "characters_outside_page": len(outside)})
    status = {
        "pages": len(texts),
        "main_text_pages": int(end_page.group(1)) if end_page else references_page - 1,
        "references_start_page": references_page,
        "missing_key_numbers": absent,
        "missing_bibliography_entries": sorted(citations - entries),
        "cited_entries": len(citations),
        "verified_publications": len(entries),
        "undefined_reference_warnings": bool(re.search(r"(?:Citation|Reference).*undefined", log)),
        "overfull_boxes": len(re.findall("Overfull", log)),
        "page_bounds_flags": bounds,
        "underfull_layout_warnings": len(re.findall("Underfull", log)),
        "note": "Text/bounds checks complement, not replace, rendered page inspection.",
    }
    (BASE / "checks/pdf-quality.json").write_text(
        json.dumps(status, indent=2) + "\n", encoding="utf-8"
    )
    (BASE / "checks/pdf-extracted.txt").write_text(text, encoding="utf-8")
    print(json.dumps(status))
    if (
        absent
        or citations - entries
        or status["undefined_reference_warnings"]
        or bounds
        or status["overfull_boxes"]
    ):
        raise ValueError("Manuscript PDF quality gate failed")


if __name__ == "__main__":
    main()
