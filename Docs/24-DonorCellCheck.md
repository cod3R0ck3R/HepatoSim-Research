# GSE210077: donor and cell-type analysis / Spender- und Zelltypanalyse

24 October 2026. Maintainer: Johnnie 4 free. Source code based on commit `ee8bbb4e2895b79ab9436a6897147710af0b9496`; exact tested file hashes and environment are in [verification](../Research/DonorCellCheck/verification.json).

## English

**The prespecified joint compartment hypothesis was not supported.** SEMA4D RNA in macrophages did not show a stable disease-associated increase. PLXNB2 RNA in hepatic stellate cells was higher with positive leave-one-donor-out contrasts, but this small cohort and its technical confounding do not establish an effect. The post hoc common-feature normalization did not rescue the joint hypothesis. Neither analysis tests a drug or reversal of fibrosis.

### Sources and experimental unit

Watson et al., *Spatial transcriptomics of healthy and fibrotic human liver at single-cell resolution*, Nature Communications, published 2 January 2025, [DOI 10.1038/s41467-024-55325-4](https://doi.org/10.1038/s41467-024-55325-4). [GEO GSE210077](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE210077) now lists 40 samples. We selected the six libraries explicitly linked to the published-study donor annotations in [HCA project 64809a52](https://explore.data.humancellatlas.org/projects/64809a52-f703-4aec-b3a5-eca808a971d0). The other GEO samples were excluded before expression analysis. Dryad metadata were accessible, but its file downloads returned 403; the official HCA mirror supplied all 21 checksum-verified input files. [Provenance and exact file hashes](../Research/DonorCellCheck/provenance.json).

All 27,692 author-retained nuclei mapped uniquely to their raw library barcodes. There are six independent donors: three normal and three diseased. Nuclei are not extra biological replicates. Author broad cell-type labels were reused without new clustering, relabeling or outcome-dependent filtering. All 36 donor/cell-type strata exceed the prespecified 20-nucleus minimum.

| Donor | Group | Hepatocytes | HSC | Endothelial | Macrophages | Cholangiocytes | Other immune |
|---|---|---:|---:|---:|---:|---:|---:|
| AM042 | Normal | 2589 | 382 | 438 | 244 | 198 | 139 |
| AM048 | Normal | 3866 | 311 | 384 | 425 | 125 | 163 |
| AM061 | Normal | 3564 | 471 | 519 | 255 | 92 | 49 |
| AM031 | Disease | 3090 | 248 | 332 | 131 | 92 | 122 |
| AM062 | Disease | 2948 | 581 | 507 | 396 | 181 | 158 |
| AM072 | Disease | 3065 | 425 | 440 | 239 | 299 | 224 |


Diseased samples are heterogeneous: AM031 F4/cirrhosis; AM062 perivenular sinusoidal fibrosis, Brunt 2/4; AM072 bridging fibrosis, F3. This is not an alcohol-specific, longitudinal, uniformly cirrhotic or decompensated cohort. Age conflicts remain unresolved: AM031 61–70 in annotation versus 51–60 in workbook; AM072 51–60 versus 61–70. No age adjustment was applied. The original article already discussed SEMA4D–PLXNB2, so this is a targeted reanalysis rather than blinded pathway validation. Cross-study subject overlap cannot be exhaustively excluded from available identifiers.

### Frozen comparison and actual execution

[Primary specification](../Research/DonorCellCheck/specification-v1.json) was written before target-count analysis. For each donor/cell type, raw target UMIs are divided by all gene UMIs, multiplied by 1e6 and transformed as log2(CPM+1). Disease-minus-normal differences use three donors per group. Two-sided exact permutation enumerates 20 allocations, so the minimum possible p is 0.1. BH adjustment covers the two primary contrasts. The nine LOO contrasts omit one donor per group; their range is a sensitivity range, not a confidence interval. Other gene/cell-type values in [the aggregate CSV](../Research/DonorCellCheck/donor-cell-genes.csv) are descriptive, not additional confirmatory tests.

| Branch | Gene / compartment | Δ mean log2(CPM+1) | Exact p | BH q | LOO range |
|---|---|---:|---:|---:|---|
| Primary | SEMA4D / Macrophages | +0.012072 | 1.00 | 1.00 | -0.200315 to +0.255500 |
| Primary | PLXNB2 / Hepatic_stellate_cells | +0.241711 | 0.40 | 0.80 | +0.073151 to +0.474990 |
| Post hoc common IDs | SEMA4D / Macrophages | +0.046765 | 0.80 | 0.80 | -0.164906 to +0.290958 |
| Post hoc common IDs | PLXNB2 / Hepatic_stellate_cells | +0.272671 | 0.30 | 0.60 | +0.105962 to +0.502511 |


The first pass exposed 36,601 versus 62,696 feature rows, perfectly aligned with condition. An initial strict common-ID check stopped before counting because normal IDs omit numeric Ensembl versions and disease IDs include them. The failure is retained in [the audit](../Research/DonorCellCheck/strict-id-failure.json). A separately frozen [post hoc v2 protocol](../Research/DonorCellCheck/sensitivity-spec-v2.json) removes only terminal numeric versions, rejects duplicate base IDs and confirms identical unique target base IDs. It found **36,383 shared gene IDs**, rescanned each raw matrix and recomputed only the denominator. Target UMIs, retained nuclei and detection counts were unchanged. This checks denominator sensitivity; it does **not** harmonize upstream alignment, chemistry, intronic counting, annotation or disease/batch effects. Consequently, even the cell-specific directional result cannot be assigned a disease cause.

The primary scan took 230.31s wall time and 38.22s CPU, observed peak RSS 106.9MiB. One worker, sparse chunk processing and 20% CPU throttling during matrix processing were used. Seven new tests plus seven shared-parser regression tests passed. Both real outputs replayed byte-for-byte from unchanged hash-bound donor checkpoints. Two evidence records were added to the local database; repeat import added zero, and two existing simulation runs were preserved. Local Goose/Ollama Hermes3:8b ran for 29.758s with 1,049 input / 178 output tokens. Its translation inverted a negation and was rejected; final wording was independently reviewed. No token-saving percentage is claimed.

### Interpretation and next discriminating step

The earlier bulk NAFLD SEMA4D increase was not reproduced as a robust macrophage-specific increase here. Cell composition, disease cause, stage and technical differences remain possible explanations, not established explanations. PLXNB2 presence and a modest HSC-associated difference justify further measurement, not prioritizing a particular drug. Useful next evidence would be a larger donor cohort processed with a common reference and documented disease causes/stages, plus cell-resolved protein or perturbation measurements capable of distinguishing SEMA4D–PLXNB2 from other receptor/ligand routes. An RNA count alone demonstrates neither binding nor signaling. No pharmacological parameter, dose, clinical response or collagen-regression probability was estimated.

**Status:** software verification passed within the tested paths; no new Kappa publication reproduction; no calibration or treatment efficacy validation; exploratory human donor data analyzed with unresolved confounding; no clinical validity. No significance, equivalence or absence-of-effect claim follows from the nonsignificant tests. Negative findings and the reference mismatch are part of the result.

## Deutsch

**Die vorab festgelegte gemeinsame Kompartiment-Hypothese wird nicht gestützt.** SEMA4D zeigt in Makrophagen keinen stabilen Anstieg bei Erkrankung. PLXNB2 liegt in hepatischen Sternzellen höher; die Richtung bleibt beim Weglassen einzelner Spender positiv. Drei Spender je Gruppe und technische Unterschiede erlauben daraus keine gesicherte Krankheits- oder Arzneimittelwirkung. Auch die nachträgliche Normalisierung auf gemeinsame Gen-IDs stützt die gemeinsame Hypothese nicht.

Von aktuell 40 GEO-Proben wurden nur die sechs zum publizierten Datensatz und zur Autorenannotation zugeordneten Bibliotheken verwendet. Alle 27.692 annotierten Zellkerne konnten eindeutig zugeordnet werden. Die Tabelle oben zeigt sechs breite Zelltypen getrennt nach Spender. Die unabhängigen biologischen Einheiten sind die sechs Spender. Die erkrankte Gruppe mischt F4/Zirrhose, Brunt 2/4 und F3. Zwei Altersangaben widersprechen sich zwischen Quelldateien; sie wurden nicht korrigiert oder als Kovariate eingesetzt. Es handelt sich weder um einen spezifischen Alkohol-Datensatz noch um einen Behandlungs- oder Rückbildungsverlauf. Der publizierte Artikel behandelt den Signalweg bereits; keine verblindete externe Mechanismusvalidierung.

Die erste Tabelle der Effekte enthält die unveränderte Hauptauswertung und die ausdrücklich nachträgliche Sensitivität. Einheit: Differenz der mittleren log2(CPM+1), Erkrankte minus Kontrollen. 20 exakte Permutationen liefern mindestens p = 0,1; BH berücksichtigt zwei Hauptvergleiche. Die LOO-Spanne beschreibt neun Varianten mit jeweils einem ausgelassenen Spender pro Gruppe und ist kein Konfidenzintervall. Weitere Gene und Zelltypen in der CSV sind rein beschreibend.

36.601 gegenüber62.696 Referenzzeilen fallen vollständig mit dem Gruppenunterschied zusammen. Der erste Identitätsvergleich brach vor der Berechnung ab. Nach dokumentierter Entfernung numerischer Ensembl-Versionssuffixe und Ausschluss doppelter Basis-IDs wurden 36,383 gemeinsame Gene verwendet. Dabei änderte sich nur der Nenner; Zielgenzählungen und Zellkerne blieben erhalten. Diese Prüfung vereinheitlicht weder die ursprüngliche Ausrichtung der Sequenzen noch weitere Labor- und Zählschritte. Die technische Konfundierung bleibt bestehen.

14 Softwaretests bestanden; beide echten Ergebnisse waren aus unveränderten Checkpoints bytegleich wiederholbar. Zwei Datenbankeinträge ergänzt, wiederholter Import ohne Duplikate, zwei vorhandene Simulationen erhalten. Die lokale KI führte eine begrenzte Übersetzung aus; eine umgekehrte Verneinung und die ungenaue Übersetzung von RNA wurden erkannt und verworfen. Simulation und Statistik stammen aus ausgeführten Programmen.

Nächster sinnvoller Schritt: mehr sauber dokumentierte Spender mit einheitlicher Referenzverarbeitung sowie Protein- oder gezielte Perturbationsdaten, die alternative Liganden/Rezeptoren unterscheiden. Kein Beleg für Bindung, Heilung, Fibroserückbildung, Dosierung oder klinische Einsatzfähigkeit. Nichtsignifikante Tests beweisen auch keine Gleichwertigkeit oder fehlende Wirkung. Negative Ergebnisse werden erhalten. [Ausführen und fortsetzen](../Research/DonorCellCheck/README.md).
