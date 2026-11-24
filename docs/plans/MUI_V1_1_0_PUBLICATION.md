# Approved GitHub publication handoff

The owner approves the exact final Version 1.1 manuscript and corresponding
source/reproducibility archives from commit 43ab2a71ab1436ce397d44f528645254943e6a9e.
Publish GitHub v1.1.0 only; never publish Zenodo or run experiments/revisions.

Verify the three payload hashes and regenerate the identical outer manifest.
Keep all four approved asset bytes unchanged. Update only repository-facing
README/CITATION and publication documentation so the latest metadata points to
Version 1.1 / package v1.1.0 with reserved DOI 10.5281/zenodo.24500468.
Record a resulting publication commit, push it fast-forward to the designated
Memory-Under-Interference remote, and create v1.1.0 targeting that exact commit.
Upload all four assets to a draft before making the GitHub release public/latest.

Before publication check repository hooks for unintended Zenodo automation.
Snapshot previous tags/releases/assets and verify them unchanged afterward.
Verify unauthenticated public downloads, SHA-256, sizes, tag peeled commit,
release title/body/DOI, latest status and repository metadata. Do not amend the
old releases or move old tags. Store verification outside the frozen artifacts.

Any archived preparation reports describe the pre-publication snapshot and stay
unchanged inside the approved archives; current publication verification is a
separate record. No compilation or scientific reanalysis is needed or authorized.
