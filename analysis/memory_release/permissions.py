"""Owner-selected licences and verified upstream notices; no tool/model binaries."""

import hashlib
import urllib.request

from analysis.memory_audit.records import save_json
from analysis.memory_release.common import RELEASE, ROOT, directories

MIT = """MIT License

Copyright (c) 2026 Dhruv Brahmbhatt

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


def main():
    directories()
    folder = RELEASE / "licenses"
    folder.mkdir(exist_ok=True)
    (folder / "MIT-ORIGINAL-CODE.txt").write_text(MIT, encoding="utf-8")
    (RELEASE / "code/LICENSE").write_text(MIT, encoding="utf-8")
    sources = {
        "EvalPlus-0.3.1-APACHE-2.0.txt": "https://raw.githubusercontent.com/evalplus/evalplus/v0.3.1/LICENSE",
        "HumanEvalPlus-APACHE-2.0.txt": "https://raw.githubusercontent.com/evalplus/humanevalplus_release/main/LICENSE",
        "CC-BY-4.0.txt": "https://creativecommons.org/licenses/by/4.0/legalcode.txt",
    }
    evidence = []
    for name, url in sources.items():
        path = folder / name
        if not path.exists():
            request = urllib.request.Request(
                url, headers={"User-Agent": "Research release notices"}
            )
            with urllib.request.urlopen(request, timeout=60) as response:
                path.write_bytes(response.read())
        evidence.append(
            {
                "notice": "licenses/" + name,
                "url": url,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
        )
    (folder / "HumanEval-MIT.txt").write_bytes((ROOT / "data/HumanEval.LICENSE").read_bytes())
    notice = """# Third-party notices and release licensing

Owner approved CC BY 4.0 for original report/data and MIT for original code
on 24 November 2026. These grants do not replace third-party rights.

- HumanEval: OpenAI MIT notice in licenses/HumanEval-MIT.txt.
- HumanEval+ release and EvalPlus: upstream Apache-2.0 notices retained. The
  Windows comparison adapter code/src/prompt_energy/utilisation_eval.py follows
  EvalPlus 0.3.1 conventions; this identifies that adaptation. Benchmark tasks,
  references and tests retain upstream notices, not a blanket owner-MIT/CC
  relicense. Verification URLs and hashes are in checks/permission-audit.json.
- Qwen2.5-Coder: model-family Apache-2.0 notices referenced in documentation;
  weights and Ollama binaries are not redistributed.
- all-MiniLM-L6-v2: no weights redistributed or rerun. Saved scores and the
  pinned embedding revision are supplied for the companion evaluation.
- HWiNFO: proprietary application, not redistributed. Energy exports contain
  the owner's numerical CPU Package Power/time observations, not the binary
  or full multi-channel CSVs.
- Python, NumPy, pandas, SciPy, matplotlib, NetworkX, scikit-learn, Streamlit,
  sentence-transformers, Tectonic and other runtimes remain separately licensed
  dependencies. No installed dependency binaries or pretrained weights bundled.
- Primary-publication HTML/PDF caches are excluded. Factual citation metadata,
  URLs and short original paraphrases are included, not publisher full text.

The pinned MemoryGraph snapshot is the author's original companion code.
Its original code is covered by the owner-approved MIT grant; external
libraries remain dependencies rather than vendored implementations.

No conference logo, acceptance, institutional endorsement or DOI is invented.
External publication requires the owner's final approval. Third-party exceptions
and any downstream rights in model-generated code remain explicit; this record
is not a legal opinion on every possible downstream use.
"""
    (RELEASE / "THIRD_PARTY_NOTICES.md").write_text(notice, encoding="utf-8")
    save_json(RELEASE / "checks/permission-audit.json", evidence)


if __name__ == "__main__":
    main()
