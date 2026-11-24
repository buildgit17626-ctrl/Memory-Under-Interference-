# Final artifact identity and publication boundaries

The author supplied reserved DOI 10.5281/zenodo.24500468. The DOI is included in
the manuscript, citation metadata, README, release notes and data-availability
documentation, with its reserved status stated. A permanent identifier string
does not demonstrate registration, public accessibility or a published record.

Only publication metadata and pagination change in this milestone. The results
tables and scientific abstract/results/discussion are compared to rc2; the raw
journals and frozen designs retain their original hashes. The bibliography flows
into the remaining main-text page rather than forcing a mostly empty page; the
prompt appendix uses two columns with a deliberate column break for its longer
example. Numeric results and exact prompt files do not change.

The reproducibility archive is tested after extraction in a fresh analysis-only
Windows environment. Guarded execution checks hashes and recalculates saved-data
statistics/energy while blocking original-data/network access. This does not
regenerate inference, independently rescore programs, calibrate sensors or prove
Linux/macOS portability. Multi-channel original sensor mirrors remain excluded;
the numerical CPU power/time samples are supplied.

SHA256SUMS.json covers archive contents; SHA256SUMS.txt covers the final upload
files. Neither hashes itself. The final Git commit cannot be embedded into files
within that same commit without circularity: the build source commit is recorded
internally, and the final artifact/main commit is reported separately as the
release target.

The main push is explicitly authorized. Publishing the GitHub release or Zenodo
record is not. Repository inspection found an existing remote v1.0.0 tag pointing
at the older audit commit; it must not be silently overwritten. Report that
remaining tag action with the exact final main hash. Prior history is preserved;
new sanitized release derivatives have their own provenance and checksums.

Owner questions:
1. Why is a reserved DOI different from a published, resolvable record?
2. What do the inner and outer hash manifests each verify?
3. Why are the build source commit and final release-target commit different?
4. Which reproducibility claims were actually demonstrated?
5. Why must the existing v1.0.0 tag be reviewed before release publication?

Assumptions: the owner-supplied DOI and previously confirmed author/licence
details are accurate. No scientific findings, experiment definitions, model
inference or MemoryGraph features change.
