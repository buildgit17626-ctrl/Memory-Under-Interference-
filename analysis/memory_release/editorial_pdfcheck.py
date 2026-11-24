"""Run with the bundled PDF Python; inspect text, citations and page bounds."""

import json
import re
from pathlib import Path

import pdfplumber
from pypdf import PdfReader

BASE = Path(__file__).resolve().parents[2] / "releases/v1.1"


def main():
    path = BASE / "manuscript/main.pdf"
    reader = PdfReader(path)
    fonts = {}
    visited = set()

    def inspect_resources(resources):
        resources = resources.get_object()
        for entry in (
            resources.get("/Font", {}).get_object().values() if resources.get("/Font") else []
        ):
            font = entry.get_object()
            descendants = font.get("/DescendantFonts")
            base = descendants[0].get_object() if descendants else font
            descriptor = base.get("/FontDescriptor")
            descriptor = descriptor.get_object() if descriptor else {}
            fonts[str(font["/BaseFont"])] = any(
                key in descriptor for key in ("/FontFile", "/FontFile2", "/FontFile3")
            )
        objects = resources.get("/XObject")
        for entry in objects.get_object().values() if objects else []:
            key = (getattr(entry, "idnum", None), getattr(entry, "generation", None))
            if key in visited:
                continue
            visited.add(key)
            obj = entry.get_object()
            if obj.get("/Resources"):
                inspect_resources(obj["/Resources"])

    for page in reader.pages:
        inspect_resources(page["/Resources"])
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
    # Owner's PDF review removed the byline, affiliation/date and contribution paragraph.
    byline_hits = [
        value for value in ("Dhruv Brahmbhatt", "IIT Madras", "24 November 2026") if value in text
    ]
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
        "removed_byline_text_hits": byline_hits,
        "pdf_author_metadata": reader.metadata.get("/Author"),
        "authorship_metadata_correct": reader.metadata.get("/Author") == "Dhruv Brahmbhatt",
        "pdf_title": reader.metadata.get("/Title"),
        "pdf_subject": reader.metadata.get("/Subject"),
        "pdf_keywords": reader.metadata.get("/Keywords"),
        "embedded_fonts": fonts,
        "all_fonts_embedded": all(fonts.values()),
        "times_new_roman_embedded": any("TimesNewRomanPSMT" in name for name in fonts),
        "bold_times_new_roman_embedded": any("TimesNewRomanPS-BoldMT" in name for name in fonts),
        "font_scope": (
            "Times New Roman prose; TeX Gyre Termes Math; Latin Modern Mono code; "
            "unchanged figure labels use DejaVu Serif."
        ),
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
        or byline_hits
        or citations - entries
        or status["undefined_reference_warnings"]
        or bounds
        or status["overfull_boxes"]
        or not status["authorship_metadata_correct"]
        or not status["all_fonts_embedded"]
        or not status["times_new_roman_embedded"]
        or not status["bold_times_new_roman_embedded"]
    ):
        raise ValueError("Manuscript PDF quality gate failed")


if __name__ == "__main__":
    main()
