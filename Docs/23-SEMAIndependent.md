# SEMA4D–PLXNB2: external human cohort check / externe Kohortenprüfung

24 October 2026. Specification: [sema-external-association-v1](../Research/SEMAIndependent/specification-v1.json), frozen before target count inspection. [Results](../Research/SEMAIndependent/result-v1.json) · [Reproduction](../Research/SEMAIndependent/README.md) · [Source decisions](../Research/SEMAIndependent/source-search.json).

## English

**The prespecified two-gene association rule was not met.** SEMA4D was higher in advanced fibrosis; PLXNB2 was not significantly increased and its point estimate was negative. This is a useful limit on transfer from the TAA mouse whole-library pattern, not proof that the receptor has no role in a particular human cell type.

We downloaded and validated all 216 GSE135251 count files: 206 NAFLD biopsies and 10 controls. The primary contrast used 68 F3/F4 versus 85 F0/F1 samples; 53 F2 samples entered only the descriptive stage trend. NAFLD stages: F0 38, F1 47, F2 53, F3 54, F4 14. GEO IDs, patient titles and BioSample references were unique. This supports one annotated biopsy per unit, not independent verification of recruitment records. Controls were excluded by the disease field, not assumed to have identical stage labels.

All libraries contained 64,253 gene features; gene-count totals ranged from 14,692,247 to 37,815,440. Six targets were present with nonzero counts in every library. HTSeq summary rows were excluded from the CPM denominator. Current Ensembl stable identifiers were recorded and matched exactly to original GRCh38/release-78 count IDs; no substitute genes or imputation were used.

| Gene | Advanced − minimal Δlog2(CPM+1) | 95% bootstrap interval | BH q (6 genes) | F3-only effect |
|---|---:|---:|---:|---:|
| SEMA4D | +0.309 | [+0.154, +0.476] | 0.0003 | +0.276 |
| PLXNB2 | -0.134 | [-0.297, +0.028] | 0.1530 | -0.171 |
| PLXNB1 | +0.123 | [-0.051, +0.301] | 0.2125 | +0.068 |
| CD72 | +0.148 | [-0.021, +0.322] | 0.1530 | +0.138 |
| SEMA4C | +0.051 | [-0.077, +0.178] | 0.4256 | +0.024 |
| COL1A1 | +1.084 | [+0.715, +1.441] | 0.0003 | +0.982 |

Values are differences of mean log-transformed CPM, not measured protein fold changes. Two-sided Monte Carlo permutation tests used 9,999 allocations with a plus-one correction; the smallest possible reported p is 0.0001. BH correction covers all six genes. Intervals use 2,000 within-group bootstrap samples, are unadjusted and descriptive. Seed: 20261024. F3-only contrasts and leave-one-patient-out effects retained positive SEMA4D and negative PLXNB2 directions. Descriptive stage Spearman correlations were +0.265 and −0.101, respectively. Neither sign proves a receptor-specific effect. Unmeasured age, sex, metabolic state, centre/batch, cell composition and CPM composition bias remain possible confounders; there was no treatment arm or time course.

GSE135251 was collected in a different published human cohort from the nine mouse libraries. No reuse of this accession or its primary paper was identified in the inspected Pham main text. However, not every supplement or donor-level recruitment link was audited. Treat this as a retrospective external-cohort association test, not a perfectly sealed holdout or validation of a mechanistic treatment model. It does not test alcohol-associated disease, decompensation, collagen clearance or clinical response.

## Mechanism audit and next discriminating test

Pham et al. (2026) report ligand/receptor inference, recombinant-ligand experiments and anti-SEMA4D benefit during TAA injury. Their antibody intervention is separate from the nine RNA libraries and is not a trial of reversal after established cirrhosis. Wang et al. (2023) independently report Sema4D knockout effects involving AOX1/retinoid and T-cell pathways, but the publisher states that their data are confidential. This is supportive prior knowledge cited by Pham, not newly available independent raw evidence.

Receptor selectivity remains unresolved. Masuda et al. (2004) observed SEMA4D binding to both plexin-B1 and plexin-B2 in transfected cells. Friedel et al. (2007) found weaker SEMA4D–B2 binding than B1 and stronger SEMA4C–B2 binding. Maier et al. (2011) reported robust heterologous binding to both B1/B2, while tissue binding persisted in B2-deficient cerebellum. A 2023 corrigendum (DOI 10.1016/j.mcn.2023.103837) removed Maier Figure 6 and its migration results after overlapping image panels and incomplete archived data were identified. We do not use that removed assay; the authors state that the binding figure and other results stand, which is not an independent revalidation. These neuronal assays do not settle liver receptor use and show why binding context matters. Kumanogoh et al. (2000) identified CD72 as another SEMA4D receptor. Ligand neutralization or whole-organ RNA therefore cannot identify PLXNB2 as the sole therapeutic mediator.

Prioritize a donor-aware cell-type analysis of GSE210077 / Dryad 10.5061/dryad.37pvmcvsg, auditing overlap first. The study includes three healthy and three fibrotic donors and already discusses the ligand/receptor pair in healthy zonal signaling. Its cells must not be counted as independent patients. A causal follow-up would compare selective PLXNB2 loss and rescue with PLXNB1 and ligand-neutralization controls in an appropriate human HSC/macrophage system, measuring collagen protein/new matrix alongside viability and receptor abundance. If a ligand effect persists without PLXNB2, the exclusive B2 mechanism is weakened. This is an experimental question, not a laboratory protocol or recommendation for human treatment.

## Verification, uncertainty and provenance

Five unit tests passed; a complete real-data run and seeded statistics replay from a hash-bound count cache were byte-identical. The replay did not independently repeat the full raw scan. Initial run: 46.45 seconds wall time, 7.71 CPU seconds, 57,606,144 bytes peak RSS on macOS; Python 3.15.0, NumPy 2.5.4. CPU throttled to 20% of one core during parsing/statistics, one worker. Two reviewed evidence records were added to the existing database; replay added zero duplicates and both simulation runs were preserved. No Kappa run or model recalibration. The cache is tied to input archive, metadata, specification, analyzer and payload hashes.

A local Goose 1.45.0/Ollama hermes3:8b review genuinely ran for 34.802 seconds with a matched local native runner and GGUF digest; reported 1,051 input and 285 output tokens. Its unsupported receptor/pediatric-study suggestions were rejected, not integrated. No token savings were estimated. Details: [review receipt](../Research/SEMAIndependent/local-worker-review.json).

An initial full-SOFT metadata response hit the read cap before sample records and was discarded from analysis. Complete MINiML replaced it. Two older binding-paper XML downloads were unavailable; their primary web texts were inspected instead. No sources or downloads are claimed beyond the receipts. Scientific criteria stayed unchanged after results. Raw public counts, article files, contact metadata and private correspondence are not redistributed or relicensed.

| Evidence layer | Result and boundary |
|---|---|
| Software verification | Five tests and deterministic real-data cache replay passed. |
| Publication reproduction | Earlier nine-mouse-library QC reproduced; this milestone is a new external analysis. |
| Parameter calibration | None; no drug-to-Kappa parameter mapping. |
| External biological data | Human RNA association tested; two-gene rule failed; receptor-specific causality untested. |
| Human transfer | Limited to this NAFLD biopsy cohort and measurement; no alcohol/decompensation inference. |
| Clinical validation | None. No treatment benefit, dose or safety conclusion. |

## Deutsch

**Die vorab festgelegte gemeinsame Assoziationsbedingung wurde nicht erfüllt.** SEMA4D ist bei fortgeschrittener Fibrose erhöht; PLXNB2 zeigt keinen statistisch gesicherten Anstieg und einen negativen Punktschätzer. Das begrenzt die Übertragung des TAA-Mausbefunds. Es widerlegt keine mögliche Wirkung in einzelnen Zelltypen.

Alle 216 Zähldateien wurden geprüft. Von 206 NAFLD-Biopsien wurden 68 mit F3/F4 und 85 mit F0/F1 verglichen; 53 mit F2 gingen nur in den deskriptiven Stufentrend ein. Zehn Kontrollen wurden anhand des Krankheitsfeldes ausgeschlossen. Eindeutige GEO-, Titel- und BioSample-Einträge ersetzen keine Prüfung der Rekrutierungsakten. Alle Bibliotheken enthielten 64.253 Genmerkmale und alle sechs Zielgene. Die Tabelle oben zeigt Unterschiede des mittleren log2(CPM+1), keine Protein-Fold-Changes. 9.999 Permutationen, BH-Korrektur über sechs Gene und 2.000 Bootstrap-Stichproben waren vorab festgelegt. Die Intervalle sind unadjustiert. Auch ohne F4 und bei Weglassen einzelner Patienten blieb SEMA4D positiv und PLXNB2 negativ. Alter, Geschlecht, Zentrum/Batch, Stoffwechsellage, Zellmischung und Normalisierung bleiben mögliche Verzerrungen.

Die menschliche Kohorte stammt aus einer getrennten Publikation. Im geprüften Pham-Haupttext wurde keine Wiederverwendung gefunden; nicht alle Supplemente und Rekrutierungsverknüpfungen wurden geprüft. Deshalb externe retrospektive Assoziationsprüfung, kein vollständig abgeschotteter Bestätigungsdatensatz. Es gibt weder Behandlungsarm noch zeitliche Rückbildungsmessungen. Alkoholassoziierte oder dekompensierte Zirrhose wurde nicht untersucht.

Die Mausbefunde zur SEMA4D-Blockade bleiben ein präklinischer Forschungsansatz. Sie beweisen keine ausschließliche Vermittlung über PLXNB2. Primärstudien zeigen kontextabhängige Bindung an Plexin-B1/B2 sowie CD72 als weiteren Rezeptor. Eine Korrektur von 2023 entfernte bei Maier die Migrationsabbildung 6 wegen überlappender Bilder und unvollständiger Archivdaten. Diese Ergebnisse werden hier nicht verwendet; die übrigen Angaben sind dadurch nicht unabhängig neu validiert. Die unabhängige Wang-Knockoutarbeit nennt AOX1/Retinoid- und T-Zellmechanismen; ihre Daten sind laut Verlag vertraulich. Als nächster Schritt eignet sich eine donorbasierte Zelltypprüfung der drei gesunden und drei fibrotischen Spender in GSE210077, mit vorheriger Überlappungsprüfung. Ein kausaler Versuch müsste PLXNB2 gezielt gegen PLXNB1 und Ligandenblockade abgrenzen, einschließlich Wiederherstellung des Rezeptors, Kollagen-/Matrixmessung und Viabilitätskontrolle. Das ist eine Forschungsfrage, keine Behandlungsanleitung.

Fünf Softwaretests und eine identische Cache-Wiederholung bestanden. Die echte lokale Berechnung dauerte 46,45 Sekunden bei 57,6 MB Spitzen-RSS. Der lokale Goose-Lauf fand statt; seine unbelegten Rezeptorvorschläge wurden verworfen. Keine Kappa-Kalibrierung, kein Arzneimittelwirksamkeitsnachweis, keine klinische Validierung. Rohdaten, private Korrespondenz und Kontaktmetadaten werden nicht veröffentlicht. Die oben getrennten Evidenzstufen gelten unverändert für diese deutsche Fassung.

## Primary sources / Primärquellen

- Govaere et al. (2020), DOI: [10.1126/scitranslmed.aba4448](https://doi.org/10.1126/scitranslmed.aba4448); [GSE135251](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE135251). GEO metadata/counts read; article abstract/index verified, full text not retrieved.
- Pham et al. (2026), DOI: [10.1016/j.jhepr.2026.101783](https://doi.org/10.1016/j.jhepr.2026.101783). Main-text XML and prior pinned HSC script inspected; no complete supplement audit.
- Wang et al. (2023), DOI: [10.1016/j.phrs.2023.106886](https://doi.org/10.1016/j.phrs.2023.106886). Publisher abstract/data-availability statement.
- Masuda et al. (2004), DOI: [10.1111/j.1365-2443.2004.00766.x](https://doi.org/10.1111/j.1365-2443.2004.00766.x).
- Friedel et al. (2007), [PMID 17554007](https://pubmed.ncbi.nlm.nih.gov/17554007/), [primary full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC6672150/).
- Maier et al. (2011), [primary full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC3030677/).
- Maier et al. (2023), [corrigendum](https://pmc.ncbi.nlm.nih.gov/articles/PMC10247391/), DOI 10.1016/j.mcn.2023.103837; removed Figure 6 excluded.
- Kumanogoh et al. (2000), DOI: [10.1016/S1074-7613(00)00062-5](https://doi.org/10.1016/S1074-7613(00)00062-5).
- Watson et al. (2025), DOI: [10.1038/s41467-024-55325-4](https://doi.org/10.1038/s41467-024-55325-4); [GSE210077](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE210077); [Dryad](https://doi.org/10.5061/dryad.37pvmcvsg).
