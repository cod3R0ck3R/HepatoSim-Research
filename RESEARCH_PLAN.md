# Forschungsversion: Meilenstein HSR-002

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
