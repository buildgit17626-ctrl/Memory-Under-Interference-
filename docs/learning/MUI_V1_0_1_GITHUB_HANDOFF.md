# GitHub packaging v1.0.1, research Version 1.0

The author approved scientific content at verified commit
723cf5d139144f914023d0fa65b74d340cbcc943 and authorized publishing a new GitHub
release. Only release links/status, packaging and citation metadata change.
Manuscript Version 1.0, all numerical tables, original evidence, model outputs
and statistical findings remain unchanged. DOI 10.5281/zenodo.24500468 stays
reserved; Zenodo publication is manual and no Zenodo API changes are made.

The v1.0.1 tag points to the verified final artifact commit. The v1.0.0 tag is
never moved. Its original release body is retained after a superseded notice,
and the new release is marked latest. Four assets are attached: PDF, source ZIP,
reproducibility ZIP and SHA256SUMS.txt. The manifest contains hashes of the three
payloads rather than a recursive hash of itself or absent optional files.

Verification connects the layers: compare science to the approved commit;
rebuild and inspect PDF; verify ZIP hashes and saved-data reanalysis; check
uploaded draft bytes; publish; download all four public assets without auth;
compare hashes and check latest/tag targets. Post-publication verification is
saved separately so it cannot change the release commit it verifies. A source
build commit and final artifact/tag commit therefore have different roles.

Five owner questions:
1. Why can the GitHub release be v1.0.1 while the manuscript stays Version 1.0?
2. How do checks prove science and results did not change?
3. Why is the old tag preserved rather than moved?
4. What does a SHA-256 match of a public asset prove and not prove?
5. Which actions remain manual on Zenodo?

Assumptions: explicit publication approval, reserved DOI and confirmed author/
licence details remain valid. No scientific improvements or new data are implied
by this packaging release; all previously disclosed limits still apply.
