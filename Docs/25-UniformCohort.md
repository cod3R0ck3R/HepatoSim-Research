# GSE244832: larger common-pipeline cohort audit

24 October 2026 · Johnnie 4 free · research only

## Result / Ergebnis

**EN:**18 human liver donors and128,223 nuclei were audited. Myeloid SEMA4D is directionally higher, while HSC PLXNB2 is directionally lower in the disease group. Neither comparison survives the prespecified two-test adjustment; both bootstrap intervals include zero. The joint increase hypothesis fails under both source-label assignments. This is an exploratory association check, not proof against every biological role of the pathway or a treatment result.

**DE:**18 menschliche Leberspender und128.223 Zellkerne wurden geprüft. Myeloides SEMA4D liegt im Erkrankungsvergleich tendenziell höher, Sternzell-PLXNB2 niedriger. Keiner der beiden Vergleiche besteht die vorab festgelegte Korrektur für zwei Tests; beide Bootstrapintervalle enthalten null. Die Hypothese eines gemeinsamen Anstiegs besteht unter keiner der beiden Quellenzuordnungen. Daraus folgt weder eine generelle Widerlegung des Signalwegs noch eine Aussage zur Wirksamkeit einer Behandlung.

## Source and design

The primary [GEO cohort](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE244832) and [Kim et al.](https://doi.org/10.1016/j.jhep.2024.10.044) describe5 NORMAL,4 MASL and9 MASH donors. All18 RNA libraries report NextSeq500 and the same Cell Ranger3.0.2/hg38 processing including introns/exons. A common27,200-gene matrix reduces the specific gene-reference discrepancy found in GSE210077, but does not establish absent batch effects. No FASTQ reprocessing was performed. Metabolic disease is not alcohol-associated disease or decompensated cirrhosis.

GEO metadata has numeric clusters only. Explicit assignments were found in [a published reanalysis](https://doi.org/10.3390/ijms27177920), supplementary TableS19 (HSC3+11) and TableS20 (myeloid5). The aggregate sizes reproduce13,940 HSC and5,743 myeloid nuclei; matching sizes alone were **not** used to assign labels. These are reanalysis labels, not independently verified original-author per-cell annotations. Myeloid is broader than macrophages. CD163 is enriched in the mapped myeloid compartment, NGFR in the mapped HSC compartment; these descriptive marker checks do not prove purity.

The source has two unresolved donor-label conflicts: **JB321** is NASH in cell metadata but MASL in the donor workbook; **JB337** is NAFL in cell metadata but MASH in the workbook. The corresponding GEO sample pages list tissue without resolving disease. The aggregate group sizes stay5/4/9. Historical NASH/NAFL terms are kept as source labels; the article uses MASH/MASL. No preferred label truth is asserted.

A further source discrepancy is retained: the PMC author manuscript's data-availability section says GSE224688, whereas GSE244832 cites the correct PMID39522884 and the workbook supplies the18 RNA libraries. Original primary supplementary DOCX retrieval returned HTML / an access-availability error. The reanalysis XML and supplementary ZIP were actually downloaded through EuropePMC; no original figures or supplementary tables are republished.

## Frozen tests and amendments

The selection specification preceded count inspection. The initial plan retained36cluster-gene slots (18clusters ×2genes). During an outcome-blind count scan, explicitly published compartment labels became available; a separate two-test exploratory addendum was frozen before effects were read. It pools raw counts across HSC clusters before normalizing, and compares donors rather than treating nuclei as replicates. At least20 nuclei per compartment and at least3 donors per group are required; both compartment tests retained9disease/5control donors. The4NAFL/MASL donors remain descriptive.

Version1 incorrectly used MASH as a source label and produced zero tested disease comparisons. A regression now rejects absent contrast labels. Version2 fixes the source spelling to NASH, preserving the validated aggregate and the original version/checksums. It was not a response to biological effects. The workbook conflict was discovered **after** primary effects; the separate label-sensitivity specification is explicitly post hoc and leaves the primary output intact.

Effect = difference in donor mean log2(1+CPM), disease minus NORMAL; it is **not** a log fold change. Every test enumerates2,002 label permutations, assuming donor-label exchangeability. BH uses a separate family of2 compartment tests; the all-cluster family retains36 slots, with untestable slots assigned p=1. There are28 testable cluster-gene slots and none at q<0.05. Bootstrap intervals use5,000 within-group donor resamples, PCG64 seed20261024, and are descriptive rather than simultaneous confidence intervals. All45 leave-one-donor-from-each-group comparisons are reported.

| Assignment | Compartment / gene | Difference | Bootstrap95% | Exact p | BH q (2) | Leave-one-each range |
|---|---|---:|---|---:|---:|---|
| Matrix CSV | myeloid / SEMA4D | +0.755 | [-0.022, +1.496] | 0.0734 | 0.1469 | [+0.386, +1.155] |
| Matrix CSV | HSC / PLXNB2 | -0.316 | [-0.723, +0.105] | 0.1913 | 0.1913 | [-0.554, -0.100] |
| Workbook sensitivity | myeloid / SEMA4D | +0.694 | [-0.095, +1.464] | 0.1119 | 0.2183 | [+0.318, +1.088] |
| Workbook sensitivity | HSC / PLXNB2 | -0.297 | [-0.708, +0.121] | 0.2183 | 0.2183 | [-0.533, -0.079] |

The positive SEMA4D direction and negative PLXNB2 direction persist in all leave-one-each comparisons and after the workbook reassignment. That robustness of direction does not override nonsignificant tests or source uncertainty. Age, sex, fibrosis stage and other covariates were not adjusted. Nuclear RNA abundance does not establish surface protein, receptor engagement, collagen regression or causal efficacy.

## Executed verification and local work

All236,313,523 nonzero coordinates passed positivity, bounds, order, uniqueness and completeness checks. Every nucleus exactly reproduced the author nCount_RNA **and** nFeature_RNA metadata; total483,738,655 UMIs. The one local scan took283.444 s wall /39.486 s CPU and137,756,672bytes peak RSS. The file suffix is misleading: the matrix is plain MatrixMarket inside the outer gzip tar. Downloaded archive727,189,398bytes; source hashes pinned, not claimed to be upstream-signed hashes.

22 tests passed (8new/current,7shared parser,7previous donor checks). Primary, compartment and workbook-sensitivity cached replays were byte-identical. Input checksums were separately verified. The source-label repair reused an unchanged checked count payload; the old code was reconstructed and its original hash verified. Two initial coordinator launches failed on Documents access before execution; the unchanged execution mirror resolved that issue. No repeated simulation or therapeutic optimization was started.

One existing local Goose1.45.0/Ollama0.40.10 Hermes3:8b worker reviewed wording in23.363 s. Model digest, native GGUF runner and actual generated response were checked; no cloud fallback, install or download. Goose reported1,105 input/111 output tokens,4 cache-read tokens. These are worker-reported usage, not measured savings. Its cautions were reviewed; AI supplied no numerical evidence.

Two versioned evidence records were added to the existing SQLite research store; replay added zero. Both existing simulation records remained unchanged. Full private logs, database backups, raw inputs and source correspondence are excluded from GitHub.

## Scope-specific status

| Layer | Status |
|---|---|
| Software verification |22 tests, exact count oracles, three deterministic replay checks passed |
| Publication reproduction | Common source counts and explicitly sourced reanalysis compartment membership audited; no complete reproduction of either paper |
| Parameter calibration | Not performed |
| Independent biological evidence | A separate observational cohort was analyzed; anonymous donor overlap not independently excluded; unresolved clinical-label provenance; no causal validation |
| Human treatment / clinical use | Not established; no drug effects or doses estimated |

**Next step:** resolve the two donor assignments and obtain author per-cell annotations before strengthening cell-type claims. A separately budgeted GSE289173 audit could increase donor numbers; its approximately1.9 GB count archive exceeded this task's1.5 GB download ceiling, and its alternative Zenodo object was not evaluated. Do not select a better-looking cohort or tune success criteria to force an increase in both genes. The18-donor result weakens the simple joint-transcript-upregulation rationale; intervention-level and protein-level evidence remain required.

**Nächster Schritt:** die widersprüchlichen Spenderzuordnungen und Original-Zellannotation klären. Dieser Lauf begründet keinen Wirkstoffversuch und ersetzt keine unabhängige funktionelle Prüfung.

[Reproduce / Wiederholen](../Research/UniformCohort/README.md) · [sources](../Research/UniformCohort/source-register.json) · [verification](../Research/UniformCohort/verification.json) · [primary](../Research/UniformCohort/compartment-result-v2.json) · [label sensitivity](../Research/UniformCohort/label-sensitivity-result-v1.json)

The reusable downloader was tested against the existing source cache. Its fresh-network path was not repeated; actual source downloads used the recorded retrieval scripts/receipts. No new app build was needed for this research-only change.

## 26 October 2026 correction / Korrektur

The earlier assertion that GEO sample records provide only tissue is incorrect: the `Description` field labels all18 RNA donors and agrees with the author workbook. The final publisher paragraph namesGSE244832; the other accession is in the PMC manuscript. Historical results above remain intact. See [the correction and frozen exclusion control](26-DonorProvenanceFollowup.md).

Die frühere Aussage zu fehlenden GEO-Erkrankungsgruppen ist korrigiert: `Description` enthält sie für alle18 RNA-Spender und stimmt mit der Autoren-Tabelle überein. Die Verlagsfassung nenntGSE244832; die abweichende Kennung steht im PMC-Manuskript. Die bisherigen Ergebnisse bleiben erhalten.
