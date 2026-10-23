# Jerez et al. 2026: acquired source data, benchmark eligibility unresolved

Checked 2026-10-22. Primary source: [Jerez et al., JCI Insight, DOI 10.1172/jci.insight.193172](https://insight.jci.org/articles/view/193172), published 23 March 2026. This is a data-access and experimental-design audit, not a new efficacy result.

The study tests MARCO-positive versus MARCO-negative macrophage transfer and saline controls in CCl4-injured C57BL/6 mice. Injury continues for six weeks; transfer occurs during injury. Figure 6E measures picrosirius-red staining. The caption reports at least six animals per group. This is not a post-withdrawal collagen time course. Human tissue observations in the same article do not establish treatment efficacy in humans.

The article links supporting numerical data and identifies transcriptomic deposits GSE291711 and GSE291710. The published methods contain an apparent injury-dose unit inconsistency. Do not silently correct that unit or turn it into an experimental instruction; clarification is required.

The supporting XLSX was actually downloaded from the publisher-linked [data file](https://df6sxcketz7bb.cloudfront.net/manuscripts/193000/193172/jci.insight.193172.sdval.xlsx): 3,521,570 bytes, SHA-256 `8de1ee65395d892d584909abbb586c0d91a55f33bd7d111e26f06c0c21b1faa1`. Article HTML, download provenance and source file are retained locally. The first `/sd/4` request returned an HTML landing page, not an XLSX; the format check correctly rejected it. Its download link supplied the spreadsheet.

The required MarkItDown conversion exceeded a 45-second budget. No workbook measurements have yet been interpreted or used to fit a model. One explicitly bounded 180-second conversion is queued with one worker and 2 GiB declared memory. No further automatic retries are authorized.

## Decision before quantitative use

Keep this source outside the current frozen benchmark. Its endpoint intervention design cannot fill the missing injury-and-withdrawal trajectory. Publication after the 2024 reference model supports temporal separation, but dataset-level overlap still needs checking. Inspect Figure 6E and supplementary measurement tables for units, individual animals, technical fields, exclusions and grouping before choosing a statistical unit. Do not treat gene expression as collagen mass.

Any quantitative macrophage intervention model would require a separately justified mapping to model rules; a change to the stellate-cell reinactivation parameter alone does not supply that mapping. A later endpoint benchmark needs its own prespecified observation model, baselines and error criteria. Source availability is progress, not biological validation.

The article states CC BY 4.0. The spreadsheet remains outside the public repository until its contents, licence coverage and identifiers have been checked. This original note and source links are suitable for review. Software verification, publication reproduction, independent biological prediction, human transferability and clinical validation remain separate claims.

## 2026-10-23 addendum: existing conversion completed and inspected

The previously queued 180-second conversion completed with exit 0 in 19.044859332963824 seconds and empty stderr. No second conversion was performed for this inspection. Coordinator job: `hepatosim-jerez-xlsx-read-bounded-20261022`. The original XLSX still matches the source checksum and byte count above. The retained MarkItDown output is valid UTF-8, 4,645,237 characters / 4,645,240 bytes, SHA-256 `6d09f1667bb951e0cf3c56286812169a3f7e8a63e859bc14a2517ab014e981e0`.

The converted `6E` section starts at Markdown line 30938. It contains three labelled rows (Saline, MARCO-Negative, MARCO-Positive), six columns labelled n1–n6 and 18 finite numerical cells. It contains no explicit measurement unit, animal identifier, normalization definition or field-to-animal aggregation rule. These six entries per group are not independently established as six identifiable biological replicates merely because the caption reports at least six animals per group. Original-cell fidelity and retained numerical precision were not separately audited against workbook internals.

The locally retained article's Figure 6 caption confirms picrosirius/fast-green staining and reports at least six animals per group. It describes the authors' ANOVA and multiple-comparison procedure; these analyses were not rerun here. The ImageJ passage found in the main methods concerns the phagocytosis assay, so its image-count rule must not be assigned to Figure 6E collagen quantification. Neither a collagen mass unit nor a conversion from staining to model collagen is established by this inspection.

Lightweight coordinator job `hepatosim-jerez-conversion-integrity-20261023-a` passed source-checksum, conversion-receipt, UTF-8 and table-structure assertions. The private receipt is `work/research-v2/evidence/Jerez2026-supporting-data.integrity-20261023.json`, relative to the task workspace. No effect size, p-value, parameter fit, predictive score or new simulation was computed. Numeric source tables remain private; this note does not redistribute the workbook.

Decision unchanged: exclude this endpoint intervention dataset from the frozen injury-and-withdrawal benchmark. Required before any separately prespecified endpoint analysis: clarify measurement units and normalization, establish animal/field grouping and exclusions, check source-data overlap and licence coverage, and justify an observation model plus a macrophage-mechanism mapping. No new independent biological or clinical validation follows from successful conversion. The research goal remains usage-limited; this addendum closes an already executed job, rather than starting a new analysis series.
