# Forschungsversion: Meilenstein HSR-002

## Current execution gate — 2026-10-23

New research, simulation and calibration are paused by user request. Resume only after explicit authorization and a separately frozen budget and test specification; older computational next steps below are historical and do not authorize execution. Existing data-intake limitations are recorded in [the bilingual checkpoint](Docs/17-DataCollectionStatus.md). No automatic restart.

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


## 2026-10-23: bounded execution and source-data update

Pilot1.3.0 and subset1.3.1 remain incomplete after two900-second timeouts; partial traces are retained and the two unstarted follow-ups cancelled. Do not retry from CSV or infer a biological effect. See Research/Reference/mechanism-subset-timeout-2026-10-23.md. Jerez source-table conversion succeeded, but units, normalization and animal/field mapping remain unresolved; Sato animal-level measurements remain unavailable. No new fitting, independent prediction or clinical validation. New scientific execution requires a separately specified runtime-feasibility diagnostic and budget.


## 2026-10-24: bounded expression reanalysis completed

HSR-EXPR-001 uses available E-MEXP-3177 processed measurements, not a new collagen time series. Frozen specification, two byte-identical full executions, ten focused tests and local worker review are in Research/Expression and Docs/18-ExpressionReanalysis.md. Do not retry the incomplete Kappa pilot or fit degradation rates to expression intensity. Next research step requires sample/animal/batch mapping, verified probe annotation and matched independent collagen/protease measurements. New runs require a separately specified scope/budget; no ongoing research automation was resumed.

## 2026-10-24 — collagen check and prerelease

Bounded collagen check completed: frozen retrospective comparison, 5 tests, exact replay. Next: qualify formation-versus-clearance measurements before treatment parameterization. User additionally requested a macOS prerelease; build and release verification are tracked separately.

## 2026-10-24 TAA transfer and evidence intake
Completed: frozen same-study transfer test, negative median-transfer baseline comparison,16 tests,12 immutable evidence records in existing database. Downloaded GSE295293 and Decaris supplementary measurements. Next: sample-level QC and prespecified animal-level pseudobulk; independent joint synthesis/clearance cohort remains missing. No further unconstrained sweeps.
