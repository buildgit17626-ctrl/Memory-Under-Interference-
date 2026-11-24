# GitHub v1.0.1 publication handoff, 24 November 2026

Start from verified commit 723cf5d139144f914023d0fa65b74d340cbcc943.
Owner approves scientific content and authorizes publishing GitHub v1.0.1 with
four research assets, marking it latest and marking the older release superseded.
Preserve v1.0.0 tag/history. The manuscript remains Version 1.0 and DOI
10.5281/zenodo.24500468 remains reserved. Zenodo publication, new experiments,
scientific revisions and MemoryGraph features are prohibited.

## Work

- Update release identity/links, metadata, README and availability text. Explicitly
  distinguish manuscript Version 1.0 from GitHub packaging release v1.0.1.
- Compare scientific text/tables with the verified base; rebuild and visually
  inspect PDF. Preserve all frozen evidence and scientific results.
- Rebuild source/reanalysis ZIPs and a standard outer SHA256SUMS.txt containing
  the three payload hashes (the fourth uploaded file is this manifest itself).
- Verify public-only reanalysis and hashes from a fresh extracted directory.
- Commit/push metadata and final artifacts to memory-interference/main. Create
  an annotated v1.0.1 tag at the verified artifact commit; never move v1.0.0.
- Create a draft with all four files, verify upload sizes/hashes, publish as
  latest, then prepend a superseded notice to the old release while retaining
  its original body and tag. No Zenodo API changes.
- Download every published asset without authentication, compare SHA-256,
  confirm tag target/latest endpoint/manuscript-repository agreement. Save local
  handoff verification outside the release archive to avoid changing its target.

Acceptance: no changed scientific findings, original evidence intact, tests/lint,
PDF/source compilation, archive and principal reproduction pass; public downloads
match final local bytes; old tag remains 51a95541e9f9c94ef8c2ca35a743bd3dfd41dc16.
Assumptions: owner approval and DOI reservation remain valid; no arXiv/Zenodo
publication is implied by a GitHub release.
