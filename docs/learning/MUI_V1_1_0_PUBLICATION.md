# Version 1.1 GitHub publication

The publication handoff changes repository-facing metadata, not approved
research artifacts. The four files from 43ab2a71ab1436ce397d44f528645254943e6a9e
are compared byte-for-byte; regenerating the manifest preserves its original
line endings and therefore its exact approved bytes.

The publication commit includes updated README/CITATION and a read-only
verification script. GitHub's draft receives four files before becoming public.
The release tag targets the publication commit; earlier tags/releases/assets
are snapshotted and compared afterward. A later local verification receipt
records the exact target commit without a self-referential commit hash.

Data flow: approved files → GitHub draft upload → public release → unauthenticated
downloads → SHA-256/ZIP/inner-manifest verification. No new model generation,
analysis, compilation, manuscript revision or Zenodo publication is involved.
Preparation documents inside the frozen archives remain historical snapshots.

Questions to defend:
1. How is the publication commit different from the approved artifact commit?
2. Why does the outer manifest hash three payloads rather than itself?
3. Why must the public download be checked without an authorization header?
4. How are old tag identities and release assets checked for preservation?
5. Why does GitHub publication not confirm registration of the reserved DOI?

Assumptions: manuscript Version 1.1 maps to GitHub package v1.1.0; the DOI is
reserved until the owner completes Zenodo. Only the Memory-Under-Interference
remote is a publication destination. Unrelated untracked work stays untouched.
No old release body/tag/asset is edited. Verification receipts describe observed
public state and are kept separately from the immutable approved archives.
