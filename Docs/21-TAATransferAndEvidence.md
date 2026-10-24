# TAA transfer and evidence intake / TAA-Übertragung und Datenaufnahme

Date / Stand: 2026-10-24. Maintainer: Johnnie 4 free.

## Question, predefined check and result

Can the previously fitted mouse CCl4 net CPA decline rate describe TAA regression without refitting? Specification `Research/TAATransfer/specification-v1.json` was hashed before calculation. All published aggregate values had already been inspected: this is a retrospective internal same-study transfer check, not blinded or independent biological validation. Neither the original Kappa model nor a drug parameter was changed.

The model is `C(t)=h+(C0-h)exp(-r*t)`. CCl4 days0/7 and its healthy median determine r; only TAA healthy/day0 initialize the primary transfer. Time is days after withdrawal; output is PSR collagen proportionate area (CPA), percent. Hofer2025 Supplementary Table2 provides separate sacrifice cohorts of male C57BL/6JRj mice after 12 weeks of exposure, including n = 8 per TAA group. Rats, human alcohol-related disease and mouse CPA are not pooled.

| Method | Day14 prediction, CPA % | Absolute error, percentage points | Role |
| --- | ---: | ---: | --- |
| Fixed CCl4 rate transferred to TAA | 1.764954 | 1.175046 | Primary check |
| Constant TAA baseline | 3.800000 | 0.860000 | Simple comparator |
| TAA day0/day7 fit | 3.375974 | 0.435974 | Retrospective development comparison |
| Zero-offset CCl4 transfer | 1.335622 | 1.604378 | Alternative assumption |

The primary median transfer fails the predefined descriptive criterion: its day14 error exceeds the constant baseline error. It also overpredicts regression at day7. The CCl4 net coefficient is 0.079544/day; the descriptive early TAA coefficient is 0.010768/day. These are net area-fraction coefficients, not independently measured synthesis or clearance rates. TAA fitting uses day7, so its day7 fit and two-point MAE are not out-of-sample evidence.

Across 243 combinations of source/initialization quartiles, predicted day14 CPA spans 1.279139–3.022698%. This is a sensitivity envelope, not a confidence interval. It includes the observed TAA day14 median: the failed median transfer is not a statistical population-level rejection. Animal-level uncertainty, serial covariance and imaging denominator effects remain unestimated.

## Evidence acquired and priorities

The targeted search checked seven primary-source leads, including 2026 publications, and rejected the adipose-tissue dataset PXD064522 as a liver benchmark. It was not a systematic review. Exact DOI, access status, species and limitations are in `Research/TAATransfer/evidence-catalog.json`.

1. **GSE295293 / Pham2026**: the complete 424,663,040-byte GEO archive was downloaded and hashed. Nine matrix headers were inspected; this is not a completed expression reanalysis. The article identifies macrophage SEMA4D–PlexinB2 and HSC LMCD1–AKT/mTOR as investigable mechanisms. Its VX15/2503 experiment compares vehicle and antibody during TAA progression, n = 5 per group; this does not demonstrate reversal of established human cirrhosis. Next: inspect sample/pooling/batch structure and reproduce author QC, then preregister animal-level pseudobulk contrasts. Cells must not be counted as independent animals. Reference: doi:10.1016/j.jhepr.2026.101783, Figure5J and data availability; GEO GSE295293.
2. **Decaris2015**: full text and supplementary Tables1/2 were downloaded. Eighteen complete chain/subject rows contain = 54 values across relative abundance, fraction newly made during labeling, and fractional synthesis percent/day. Six subjects have hepatic proteomics; the wider pilot evaluated eight. These human data can constrain a future synthesis measurement model but cannot supply a separately observed clearance rate or a mouse TAA treatment effect. Relative abundance is not absolute collagen mass. Reference: doi:10.1371/journal.pone.0123311, TablesS1/S2 and methods.
3. **Königshofer2026**: close8/12-week toxin-regression comparator, but underlying data are request-only. Shared investigators/design with Hofer2025 mean cohort overlap must be resolved before any independence claim. Reference: doi:10.1038/s41598-026-54627-5, methods/data availability.
4. **STAT1-siRNA2026**: recent preclinical lead; full methods were inaccessible through the tested publisher route. Abstract findings are insufficient for quantitative drug mapping or a safety/efficacy conclusion. Reference: doi:10.1021/acs.biomac.6c00375. Gardner2007 isotope work and Takahashi2025 monkey collagen-composition work supply methodological alternatives, not replacement human efficacy data.

## Verification and storage

Two analytic runs produced byte-identical result files. Sixteen distinct tests passed: nine extraction/database tests, five reused collagen tests and two transfer tests. No ODE discretization or RNG applies to this closed-form calculation. Source/data/code hashes and environment are recorded beside the result. Source baseline commit:284444c457cb1ca243ecbfc0d580e3e2f06bd48b.

The existing local `research.sqlite` receives a separate additive `research_evidence_v1` table. Evidence is not serialized as a synthetic SimulationRun. Existing run payloads and schema user_version1 are preserved. Every insert is transactional, backed up, content-hashed and idempotent; conflicting record IDs fail rather than overwrite. Raw papers, table extracts, matrix archive and private paths remain local. The current app does not yet display this evidence table; no UI or schema-version migration was necessary.

Software verification: passed for the bounded checks above. Publication reproduction: this calculation is an original descriptive check, not a new reproduction of Kappa. Calibration: only the explicitly labeled early CCl4/TAA descriptive fits. Independent biological validation: not achieved. Human transfer and clinical use: not established. No drug efficacy, dose or cure probability is inferred.

## Deutsche Fassung

Die unveränderte frühe CCl4-Rate wurde auf TAA übertragen. Alle Tabellenwerte waren zuvor bekannt; es handelt sich um eine rückblickende Prüfung innerhalb derselben Studie. Die Vorhersage nach 14 Tagen verfehlt den TAA-Median um 1,175 Prozentpunkte und ist schlechter als die konstante Vergleichsannahme mit 0,860 Prozentpunkten Fehler. Nachträgliches TAA-Anpassen verbessert die Beschreibung, liefert aber keine unabhängige Bestätigung. Die 243 Quartilkombinationen zeigen eine breite Empfindlichkeitsspanne einschließlich des beobachteten Medians; daraus entsteht weder ein Konfidenzintervall noch eine statistische Widerlegung auf Populationsebene.

Neu aufgenommen wurden der vollständige GEO-Datensatz GSE295293 mit neun Probenmatrizen und publizierte menschliche Kollagensynthese-Daten: 18 Zeilen beziehungsweise 54 Messwerte für drei Kollagenketten bei sechs Personen. Der RNA-Datensatz ist heruntergeladen und auf Matrixkopf-Ebene geprüft, noch nicht biologisch neu ausgewertet. Die menschlichen Synthesedaten messen keinen gesonderten Abbau und sind keine TAA- oder ALD-Therapiestudie.

SEMA4D/PlexinB2 und LMCD1 sind überprüfbare Mechanismuskandidaten aus einer2026er Primärarbeit. Der Antikörpervergleich betrifft fortschreitende Mausfibrose, nicht nachgewiesene Heilung menschlicher Zirrhose. Die neuere Wiener Vergleichsarbeit erfordert Datenanfrage und Prüfung möglicher Wiederverwendung derselben Tiere. Der aktuelle STAT1-Hinweis bleibt wegen unvollständiger Methodenprüfung vorläufig.

Alle 16 unterschiedlichen Tests bestanden; zwei Rechenläufe waren exakt wiederholbar. Die Ergebnisse werden getrennt von den bestehenden Simulationen in der lokalen Datenbank gespeichert. Weder unabhängige biologische noch klinische Validierung ist damit erreicht. Nächster begründeter Schritt: Probenzuordnung und Qualitätskontrolle der neun GEO-Proben prüfen und anschließend einen vorab festgelegten Vergleich auf Tierebene durchführen; Synthese-Daten erst nach Prüfung der Messgleichungen separat verwenden.

## Operational receipt / Betriebsnachweis

Database import inserted 12 records, a second identical import inserted 0; both existing simulation runs remained byte-identical. Both database integrity checks passed. The local Goose/Hermes request remained queued because of CPU/memory pressure and was cancelled before execution; no AI output or savings claim is recorded. Numerical computation, parsing and database loading ran as ordinary local programs through the coordinator.

Datenbank: 12 neue Einträge, Wiederholung ohne weitere Einträge, zwei vorhandene Läufe unverändert; Integritätsprüfungen bestanden. Der lokale Goose-Auftrag startete wegen Last/Speicherdruck nicht und wurde aus der Warteschlange entfernt. Keine Cloud-Ausweichinferenz.
