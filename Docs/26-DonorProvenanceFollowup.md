# Donor provenance correction and exclusion sensitivity

26 October 2026 · Johnnie 4 free · research only

## English

**The previous source audit missed GEO's `Description` field.** The archived MINiML file already contained disease groups for all 18 RNA libraries. A fresh download gives identical donor labels; the author workbook is byte-identical to the earlier download. GEO and the workbook agree for all 18 donors. JB321/GSM7830569 is MASL (normalized NAFL), and JB337/GSM7830572 is MASH (normalized NASH). Both disagree with the per-cell CSV. The statement in Report25 that GEO provides only tissue and cannot resolve the group is therefore incorrect. Source agreement supports using the workbook/GEO assignment for further development, but is not independent biological proof. Existing primary and alternative-label results remain unchanged.

The final publisher's indexed data-availability paragraph names GSE244832. The incorrect GSE224688 identifier belongs to the PMC author manuscript. Direct publisher retrieval returned403; no inaccessible supplement was claimed as obtained. Original-author per-cell annotation remains unverified: HSC clusters3+11 and myeloid cluster5 still rely on the previously cited reanalysis. Myeloid does not mean pure macrophages.

### Executed control

Before calculating this control, `exclusion-spec-v1.json` froze removal of **all** rows from both conflicting donors, retaining all other counts, labels, compartment definitions and statistics. This is explicitly post hoc to previously known full-cohort outcomes. It leaves16 donors:5 NORMAL,3 NAFL,8 NASH. The inferential comparison uses8 NASH versus5 NORMAL donors; the3 NAFL donors are descriptive. Neither donor was selected by expression level. The GEO Description correction was discovered after specification freeze but before evaluation; the frozen exclusion rule was not changed.

Effect is the difference in donor means of log2(1+CPM), NASH minus NORMAL, **not a log fold change**. Each contrast uses1,287 exhaustive permutations,5,000 PCG64 bootstrap resamples with seed20261024 and40 leave-one-donor-from-each-group comparisons. BH correction covers the same two contrasts. This assumes donor exchangeability and does not adjust age, sex, fibrosis stage or batch.

| Contrast | Difference | Permutation p | BH q | Percentile bootstrap95% | Leave-one-each range |
|---|---:|---:|---:|---:|---:|
| Myeloid SEMA4D | +0.791560 | 0.079254 | 0.158508 | [0.010169,1.540778] | [0.409095,1.211933] |
| HSC PLXNB2 | −0.301918 | 0.241647 | 0.241647 | [−0.737421,0.120320] | [−0.550634,−0.070818] |

The directions survive these donor exclusions, but neither adjusted test meets q<0.05. The SEMA4D percentile interval narrowly excludes zero while its permutation test does not reject: these are different finite-sample procedures, not interchangeable significance decisions. We retain both and do not select the favorable one. The original joint positive-direction rule remains false. This does not disprove all pathway activity, establish receptor signaling, or estimate drug benefit.

### Verification and next evidence

Eighteen tests passed:3 exclusion,2 GEO-description,8 existing cohort and5 publication-export tests. The exclusion replay is byte-identical (`617e7a709d77ab867db32543a6025b4a4815be27d51bc62967f0364b72744013`). Historical and fresh metadata audits produce identical results. No new count scan, FASTQ alignment or KaSim simulation was necessary. The existing aggregate and its code hashes were checked before reuse. Python3.15.1 and NumPy version are recorded in the result binding; historical results are preserved.

One local Goose/Ollama task used the verified installed `hermes3:8b` model. Native local inference was observed; its wording was rejected for unsupported interpretations. No scientific conclusion or number was adopted from it. Full logs remain private; the review receipt records actual usage without claiming savings. Three immutable evidence records were added to the local database; replay added zero and preserved both simulation records.

A separate new evidence lead is Lee et al., *ETS1 suppresses hepatic stellate cell activation and liver fibrosis* (2025), DOI10.1172/jci.insight.195242. The article reports mouse injury/cessation experiments and human liver spheroids. Loss of ETS1 impairing regression is not proof that increasing ETS1 is a safe or effective treatment. Its human transcriptomics reuse GSE244832 and are not an independent cohort. The publisher Supporting Data Values workbook was actually downloaded (84,832 bytes;48 worksheets), hashed and converted locally; receipt and worksheet inventory are in `ets1-data-receipt.json`. No measurement values from that workbook were analyzed here. Next: audit experimental units, timing, collagen measurement and overlap, then freeze a separate reference test before numerical extraction. Do not map ETS1 knockdown to an arbitrary Kappa parameter.

**Status:** software verification passed for the stated checks; no new publication reproduction or parameter calibration; no independent biological prediction test; no demonstrated human treatment effect or clinical validation.

## Deutsch

**Die frühere Quellenprüfung hatte das GEO-Feld `Description` übersehen.** Bereits die archivierte MINiML-Datei enthält die Erkrankungsgruppen aller18 RNA-Bibliotheken. Ein neuer Download bestätigt dieselben Zuordnungen; die Autoren-Tabelle ist bytegleich zur bisherigen Datei. GEO und Tabelle stimmen für alle18 Spender überein. JB321/GSM7830569 ist MASL (vereinheitlicht NAFL), JB337/GSM7830572 MASH (vereinheitlicht NASH). Beide widersprechen der Zell-CSV. Die Aussage in Bericht25, GEO enthalte nur Gewebeangaben, ist damit korrigiert. Die Übereinstimmung stützt diese Zuordnung für weitere Entwicklungsarbeiten, beweist aber nicht unabhängig die biologische Richtigkeit. Bisherige Ergebnisse werden erhalten.

Die indexierte Verlagsfassung nennt korrekt GSE244832; GSE224688 steht im PMC-Autorenmanuskript. Der direkte Verlagsabruf endete mit403. Nicht zugängliche Ergänzungen wurden nicht als heruntergeladen ausgegeben. Die Original-Zellannotation bleibt ungeprüft: HSC3+11 und myeloid5 beruhen weiterhin auf der zitierten Reanalyse. Myeloide Zellen sind keine reine Makrophagenpopulation.

Die vor dieser Rechnung eingefrorene Ausschlussprüfung entfernt beide widersprüchlich zugeordneten Spender vollständig. Alle übrigen Werte und Verfahren bleiben gleich. Diese Prüfung ist nachträglich zu den bekannten Vollkohortenergebnissen; sie ist keine unabhängige Bestätigung. Es verbleiben16 Spender, davon8 NASH und5 NORMAL im statistischen Vergleich;3 NAFL bleiben beschreibend. Die GEO-Korrektur wurde nach Festlegung des Tests entdeckt; die Ausschlussregel blieb unverändert.

Die Tabelle oben gilt für beide Sprachfassungen. Einheit: Differenz der mittleren Spenderwerte log2(1+CPM), kein Log-Fold-Change. Verwendet wurden1.287 exakte Permutationen,5.000 Bootstrap-Wiederholungen mit Seed20261024 und40 Weglassvergleiche. Die Richtung bleibt für SEMA4D positiv und für PLXNB2 negativ. Kein BH-korrigierter Test erreicht q<0,05. Das SEMA4D-Perzentilintervall schließt null knapp aus, der Permutationstest verwirft die Nullhypothese jedoch nicht. Die Verfahren sind nicht austauschbar; beide Ergebnisse werden berichtet. Die gemeinsame positive Richtung bleibt unbestätigt. Alter, Geschlecht, Stadium und Batch sind nicht adjustiert.

18 Tests bestanden; die wiederholte Auswertung ist bytegleich. Keine neue Matrixdurchrechnung, FASTQ-Verarbeitung oder KaSim-Simulation. Der lokale Goose/Ollama-Lauf wurde nachgewiesen, seine fehlerhafte Formulierung verworfen. Private Protokolle bleiben lokal.

Die ETS1-Studie von Lee et al. ist ein neuer Datenhinweis für Verletzung und anschließende Fibroserückbildung. Ihre humanen Transkriptomdaten verwenden dieselbe GEO-Kohorte. Ein Knockout-Befund beweist keine wirksame oder sichere Behandlung durch Verstärkung des Mechanismus. Die publizierte Messwertdatei wurde tatsächlich heruntergeladen (84.832 Bytes;48 Tabellenblätter), gehasht und lokal konvertiert. Hier wurden daraus keine Messwerte ausgewertet. Als Nächstes sind Versuchseinheiten, Zeitpunkte, Kollagenmessung und Datenüberschneidungen zu prüfen und ein eigener Referenztest festzulegen. Keine willkürliche Übersetzung in einen Kappa-Parameter.

**Prüfstatus:** genannte Softwareprüfungen bestanden; keine neue Publikationsreproduktion oder Kalibrierung; keine unabhängige biologische Vorhersageprüfung, keine nachgewiesene Behandlung beim Menschen und keine klinische Validierung.

## Sources / Quellen

- [GEO GSE244832](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE244832), explicit sample `Description` in archived and freshly downloaded MINiML; exact hashes in the audit receipt.
- [JB321 / GSM7830569](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSM7830569) and [JB337 / GSM7830572](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSM7830572).
- [Kim et al., final publisher version](https://www.journal-of-hepatology.eu/article/S0168-8278%2824%2902667-9/fulltext), [PMC manuscript](https://pmc.ncbi.nlm.nih.gov/articles/PMC12306656/).
- [Published compartment reanalysis](https://doi.org/10.3390/ijms27177920), TablesS19–S20; source and limits retained from Report25.
- [Lee et al., JCI Insight](https://insight.jci.org/articles/view/195242), [Supporting Data Values](https://insight.jci.org/articles/view/195242/sd/3).
