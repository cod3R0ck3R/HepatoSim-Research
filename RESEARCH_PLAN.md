# Forschungsversion: Meilenstein HSR-002

## Current execution gate — 2026-10-23

New research, simulation and calibration are paused by user request. Resume only after explicit authorization and a separately frozen budget and test specification; older computational next steps below are historical and do not authorize execution. Existing data-intake limitations are recorded in [the bilingual checkpoint](Docs/17-DataCollectionStatus.md). No automatic restart.

## Aktuelle Nutzersteuerung – 23.10.2026: Daten sammeln

Für einige Tage Rückmeldungen, Literatur und bereitgestellte Daten sammeln. **Keine neuen Simulationen oder Kalibrierungen starten.** Kein fester Wiederanlauftermin; neue Nutzerfreigabe und dokumentierte Benchmark-/Budgetentscheidung erforderlich. Diese Steuerung hat Vorrang vor älteren Rechenschritten dieses Plans. Die lokale Datenaufnahme liegt unter `../Datenaufnahme-2026-10-23/README.md` und `manifest.json`. Veröffentlichungsrechte und Datenunabhängigkeit bleiben getrennte Prüfungen. Der stündliche Mailmonitor löst keine Berechnung oder Antwortmail aus.

Beginn: 22.10.2026. Fortsetzung von HSR-BG2024-001; dessen Rohdaten und Grenzen bleiben erhalten.

## Forschungsfragen und Abnahme

1. **Technische Wiederholbarkeit:** Lassen sich der vollständige Seed-101-Verlauf und seine gemeinsamen Ausgabepunkte bei 0,25 statt 0,5 Tagen wiederholen? Akzeptanz bleibt numerische Zeilengleichheit beim Replay und absolute Abweichung höchstens 1e-8 an vollständigen gemeinsamen Rastern. Keine ODE-Schrittweiteninterpretation. Gleiche Runtime, Originalmodelle und Parameter.
2. **Mechanismushypothese:** Wie beeinflusst die erneute Inaktivierung aktivierter HSC den Kollagenverlauf nach Reizende? Parameter- und Strukturkontraste separat einfrieren, erst nach technischen Kontrollen ausführen. Vorhandene Kontrollen wiederverwenden. Negative oder instabile Kontraste berichten; keine medikamentenspezifischen Effekte erfinden.
3. **Biologische Evidenz:** Gibt es unbenutzte, protokollkompatible CCl4-Mausdaten mit Kollagenmessung, Zeitachse, Gruppenzuordnung, Stichprobengröße und Messunsicherheit? Fehlende Messabbildung, gepoolte Toxine und Entwicklungsdaten schließen einen unabhängigen Test aus. Keine Ersatzvalidierung durch synthetische Daten.
4. **Kandidatendossiers:** Wenige primärquellenbasierte Ansätze mit Spezies, Stadium, regulatorischem Stand, Sicherheitsdaten, Gegenbefunden, Modellabbildung und unterscheidendem Experiment. Untersuchungsschwerpunkte: PPARγ/HSC-Inaktivierung, HSP47/Kollagensynthese, LOXL2/Matrixstabilisierung. Auswahl ist keine Wirksamkeitsrangliste.
5. **Reproduzierbare Nutzung:** Getestete Wiederaufnahme überspringt nur integritätsgeprüfte vollständige Läufe; Fehler bleiben erhalten. Mindestens eine tatsächlich lokale Goose/Ollama-Aufgabe wird unabhängig geprüft.
6. **Veröffentlichung:** Inhaltlich übereinstimmende englische/deutsche README, Reproduktionsanleitung, Beitragsregeln, Sicherheits- und Lizenzhinweise; bereinigtes öffentliches GitHub-Repository mit geprüftem Remote-Commit oder belegtem externem Veröffentlichungsblocker.

## Budgets und Reihenfolge

Zuerst Bestandsprüfung, Koordination und zwei technische Kontrollläufe. Technisches Paket: ein KaSim-Worker, höchstens zwei neue Läufe, je 900 Sekunden; 1.800 Sekunden neues Rechenbudget, höchstens 100 MB neue Ausgaben. Ein existierender Kontrolllauf wird nach Hash-/Argumentprüfung kopiert, nicht neu gerechnet. Queue-Wartezeit zählt getrennt. Kein automatischer Retry eines fehlgeschlagenen Laufes.

Lokale KI: ein Goose-Worker, eine kurze isolierte Aufgabe, höchstens 300 Sekunden, zunächst kein Retry. Nicht parallel mit KaSim oder schweren Builds. Ressourcen und tatsächlichen Durchsatz messen, bevor Parallelität erwogen wird.

Mechanismuspaket erst mit eigener eingefrorener Spezifikation und Koordinatorfreigabe. Keine stille Erweiterung des früheren erschöpften Budgets. Vor jedem weiteren Paket wichtigsten Informationsgewinn und verbleibende Ressourcen prüfen.

## Iterationsprotokoll

Forschungsfrage → verfügbare Evidenz → vorab festgelegter Test → Ausführung → Ergebnis → Fehleranalyse → nächster Schritt. Status in `RESEARCH_STATE.json`, wissenschaftliche Entscheidungen in `DECISIONS.md`, ausführliche Originalbelege unter `Research/Reference/`.

## Mechanismuspilot1.3 nach Abschluss der technischen Kontrollen

Siehe `Docs/13-TechnicalControls.md` für tatsächlich geschlossene Replay-/Raster-/Resume-Prüfungen. Anschließend vorab eingefrorener Pilot1.3: Default und zwei Originalmodellvarianten, Seeds101–103; fünf geprüfte Archivläufe wiederverwenden, sechs neue Läufe einzeln koordinieren, je900s und insgesamt5400s. Kein neuer Fit. Der Drei-Seed-Pilot ersetzt nicht den früher geplanten Fünf-Seed-Vergleich; vollständige Kontraste erst nach allen vorgesehenen Läufen. Arzneimittelabbildung, Parameterintervalle und unabhängige Biologie bleiben offen.


## 2026-10-22 continuation checkpoint

Inspect the1.3.1 coordinator jobs and result manifests before further execution. Preserve the1.3.0 timeout; never retry automatically. Verify every completed new trajectory before any subset comparison, and keep the full original pilot marked incomplete. In parallel, review the Sato2023 supplemental material and request animal-level data and reuse terms; freeze any future biological benchmark before evaluation. Contact lists and dispatch receipts remain private.

## 2026-10-23: subset stopped at its first timeout

The first1.3.1 contrast reached its900-second limit at model day45; its preserved trace is incomplete. Both unstarted dependent jobs were cancelled, and the ended reservation was resolved only as interrupted after lifecycle checks. See `Research/Reference/mechanism-subset-timeout-2026-10-23.md`. Do not launch another series or retry from CSV. Next computational decision requires a separately specified runtime-feasibility diagnostic and budget; no cause is inferred from timeout alone. Independently inspect the already queued Jerez conversion once it ends. Outreach remains51confirmed/8unconfirmed/141unattempted; this diagnostic authorizes no additional send action.

## 2026-10-23: queued data-conversion closeout

The existing Jerez conversion and a bounded source/output integrity check passed. Figure6E contains three groups with six numerical entries each; units, normalization and biological-replicate mapping remain unqualified. No statistical analysis or new simulation followed. See the dated addendum in `Research/Reference/jerez2026-data-triage.md`. Next scientific work, after the goal budget is restored, must first resolve these measurement definitions and prespecify any separate endpoint benchmark; the current withdrawal benchmark stays unchanged. Raw-data redistribution remains withheld. Do not repeat the completed conversion.


## 2026-10-24: bounded expression reanalysis completed

HSR-EXPR-001 uses available E-MEXP-3177 processed measurements, not a new collagen time series. Frozen specification, two byte-identical full executions, ten focused tests and local worker review are in Research/Expression and Docs/18-ExpressionReanalysis.md. Do not retry the incomplete Kappa pilot or fit degradation rates to expression intensity. Next research step requires sample/animal/batch mapping, verified probe annotation and matched independent collagen/protease measurements. New runs require a separately specified scope/budget; no ongoing research automation was resumed.

## 2026-10-24 — collagen check and prerelease

Bounded collagen check completed: frozen retrospective comparison, 5 tests, exact replay. Next: qualify formation-versus-clearance measurements before treatment parameterization. User additionally requested a macOS prerelease; build and release verification are tracked separately.

MacOS prerelease v0.1.0-alpha.1 published; source commit 9ae34e4f458d8c1542469c6f02bda45cf61f1db9. Anonymous asset download and SHA-256 verification passed. Bounded analysis and release task complete; further numerical research requires new informative data or explicit next scope.

## 2026-10-24 TAA transfer and evidence intake
Completed: frozen same-study transfer test, negative median-transfer baseline comparison,16 tests,12 immutable evidence records in existing database. Downloaded GSE295293 and Decaris supplementary measurements. Next: sample-level QC and prespecified animal-level pseudobulk; independent joint synthesis/clearance cohort remains missing. No further unconstrained sweeps.

## GEO sample audit —24 October2026

Nine-library metadata and seven software checks completed. Full count-entry/QC scan and bounded local methodological review require coordinator capacity. Freeze 8 genes and 2 contrasts before expression results; whole-library analyses are exploratory and composition-confounded. No intervention effect, independent validation or parameter calibration. Next: inspect real scan output, compare published cell totals without retuning, then evaluate direction sensitivity; retain any discrepancy.

Completion: all nine real matrices checked, published QC group sizes matched, seven tests and real resume/replay passed. Prioritize cell-resolved SEMA4D–PLXNB2 follow-up; LMCD1 regression and CTSL sensitivity prevent a simple reversal claim. No new automatic computation without a separately bounded question.

## SEMA external cohort — 24 October 2026
Completed frozen six-gene external-cohort comparison: SEMA4D positive, PLXNB2 not significantly increased; joint rule failed. Next bounded question: donor-aware GSE210077 cell-type/spatial review after overlap audit. No automatic additional analyses.

### 2026-10-24 GSE210077

GSE210077 donor/cell-type milestone completed:14 tests, exact primary and post hoc replays, two local evidence records. Remaining uncertainty: condition-confounded library reference and small heterogeneous donor cohort; next work requires a separately authorized harmonized cohort/perturbation check.

### 2026-10-24 GSE244832

Completed common-pipeline cohort audit:18 donors,128223 nuclei,22 tests, three exact replay checks, two SQLite evidence records. Joint SEMA4D/PLXNB2 increase failed under both source-label assignments. Next: resolve JB321/JB337 clinical-label conflict and original per-cell annotations; separately budget GSE289173 if needed. No automatic follow-up.

## 2026-10-26 completed bounded follow-up

Closed: GEO Description omission; matched18donors; exclusion control and exact replay;18focused tests; local Goose review; shared-log/release audit. Open: original-author per-cell annotation and biological adjudication of cellCSV conflicts. Next executable research step: inspect experimental units, units, groups and timepoints in the48-sheetETS1publisher graph-point workbook; freeze a comparison before numerical extraction or fitting. Transcriptomics overlapGSE244832; mouse/spheroid independence must be checked. No automatic next run.

## ETS1 follow-up —26October2026

Completed: original-source normalization audit, local calculation, tests, independent parser cross-check and replay. Next: resolve Figure2B/C mapping, denominator, animal IDs/aggregation and n6/n7 discrepancy through the research handoff. Acceptance requires source-backed resolution; otherwise retain this data gap. No further calibration until the inputs are coherent.

## ETS1 scaling control — 26 October 2026

Completed: frozen alternative-divisor feasibility test, four software tests, separate-process replay and idempotent evidence import. Three groups remain incompatible with one constant divisor per group within declared rounding. Next: obtain author analysis export and animal/field/denominator mapping before quantitative use. No automatic further run or budget renewal.

## HSR-HSC-FATE-001 — laboratory-discriminating mechanism test

Prespecified post-withdrawal Kappa fate perturbation, three seeds and technical replay/grid controls. Separate conditional identifiability calculation. IL-10 signalling is a qualitative laboratory candidate; cell loss, persistence, restimulation and hepatocyte function must be distinguished. No new biological fit. Next empirical gap: joint longitudinal viable-cell fate and matrix/rechallenge measurements with independent biological IDs. See Docs/29-HSCFateLabDecision.md.
