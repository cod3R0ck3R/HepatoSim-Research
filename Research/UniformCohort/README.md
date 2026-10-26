# Uniform cohort audit: GSE244832

18 human liver donors (5 NORMAL, 4 MASL, 9 MASH), one reported Cell Ranger3.0.2/hg38 pipeline, 128,223 retained nuclei. Existing author preprocessing is reused; FASTQ alignment and batch correction were not rerun. Disease association is not a treatment effect.

Original GEO metadata supplies numeric clusters. An outcome-blind addendum uses published **reanalysis** assignments from Tables S19/S20 (DOI10.3390/ijms27177920): cluster5 myeloid, clusters3+11 HSC. Myeloid is not synonymous with pure macrophages; marker coherence cannot establish purity. The original 36-slot exploratory cluster analysis is retained unchanged. `source-register.json` documents selection, failed access routes and source discrepancies.

## Reproduce

Tested: Python3.15.0, NumPy2.5.4, macOS arm64. No new packages, models or cloud providers were installed. Run from the repository root, through your coordinator if configured. Store source files outside a public checkout. The downloader verifies pinned hashes, does not overwrite input files and refuses changed upstream bytes. Source matrices and supplementary files are not redistributed.

```sh
python3 Research/UniformCohort/fetch_data.py --output /path/to/private/uniform-data
python3 -m unittest discover -s Research/UniformCohort -p 'test_*.py' -v
python3 -m unittest discover -s Research/GEOSampleCheck -p 'test_*.py' -v
python3 -m unittest discover -s Research/DonorCellCheck -p 'test_*.py' -v
python3 Research/UniformCohort/analyze.py --spec Research/UniformCohort/analysis-spec-v2.json --data-dir /path/to/private/uniform-data --checkpoint /path/to/private/counts-checkpoint.json --output /path/to/private/cluster-result.json
python3 Research/UniformCohort/compartments.py --spec Research/UniformCohort/compartment-spec-v2.json --result /path/to/private/cluster-result.json --output /path/to/private/compartment-result.json
```

The compressed archive is approximately727MB. Its3.2GB MatrixMarket member has a misleading `.gz` suffix: it is plain text inside the outer gzip tar. It is streamed, never loaded densely. The matrix audit caps observed RSS at512MiB, averages20% of one CPU core, and stops after900seconds. A complete aggregate checkpoint is written only after the entire matrix, count totals and feature counts pass. Interrupted scans restart; no invented partial numerical checkpoint. Existing output files are never overwritten.

```sh
python3 Research/UniformCohort/analyze.py --spec Research/UniformCohort/analysis-spec-v2.json --checkpoint /path/to/private/counts-checkpoint.json --output /path/to/private/replay-result.json --replay
cmp /path/to/private/cluster-result.json /path/to/private/replay-result.json
```

Replay verifies code/spec/source-hash bindings and the checkpoint payload. Use `fetch_data.py --output /path/to/private/uniform-data --verify-only` to separately verify currently available inputs; cached replay alone does not reopen source bytes. Both were run. Replay is exact software verification, not an independent biological replicate.

The shared parser now accepts an explicitly requested larger nnz ceiling (maximum300million); its default100million limit remains unchanged. Historical checkpoint code hashes intentionally fail under changed code: replay old milestones at their recorded commit, including GSE210077 at `f5d5e47b0a2c6ddd78a6e7bc8282ac6342389a65`.

See [the research report](../../Docs/25-UniformCohort.md), frozen specifications, verification receipt and derived JSON. No drug effect, clinical validation, cellular binding or collagen regression is inferred.

## Source-label sensitivity

The cell CSV and donor workbook conflict for JB321/JB337. Preserve the primary result and run the separate post hoc branch:

```sh
python3 Research/UniformCohort/label_sensitivity.py --result /path/to/private/cluster-result.json --compartment-spec Research/UniformCohort/compartment-spec-v2.json --spec Research/UniformCohort/label-sensitivity-spec-v1.json --output /path/to/private/workbook-sensitivity.json
```

Version1 plans are retained as provenance; use version2 for execution. The historical invalid summary and pre-correction aggregate are retained privately. Source label conflicts remain unresolved.

## 26 October2026 follow-up reproduction

Run from the repository root with Python and the installed NumPy version recorded in the result. These commands reuse the published, hash-checked donor aggregate; no raw matrix download is needed. Outputs must be new paths.

```sh
python3 -m unittest discover -s Research/UniformCohort -p 'test_*.py'
python3 -m unittest discover -s Scripts -p 'test_export_public.py'
python3 Research/UniformCohort/exclude_conflicts.py --result Research/UniformCohort/result-v2.json --spec Research/UniformCohort/exclusion-spec-v1.json --compartment-spec Research/UniformCohort/compartment-spec-v2.json --output /tmp/hepatosim-exclusion-new.json
```

Compare to `exclusion-result-v1.json`; numerical replay was byte-identical on the recorded Python/NumPy environment. Environment metadata may differ elsewhere. The primary and workbook-label analyses are not replaced.

To repeat the label audit, download the MINiML and workbook URLs in `followup-verification.json`, verify their hashes, and obtain `hLIVER_metadata.csv` via the existing documented fetch step. Convert the workbook to Markdown with MarkItDown, keeping its five-column table.

```sh
python3 Research/UniformCohort/audit_donor_labels.py --miniml DATA/GSE244832_family.xml.tgz --workbook DATA/GSE244832_240605_18liver_metadata.xlsx --workbook-markdown DATA/metadata.md --cell-metadata DATA/hLIVER_metadata.csv --output /tmp/hepatosim-label-audit-new.json
```

Paths under `DATA` are user-supplied local downloads. The test requires18donors and128223cells and explicitly reads GEO Description. The separateETS1workbook receipt gives its public download URL, byte hash and48worksheet headings; it is not an input to this exclusion calculation. Measurement values were not evaluated.
