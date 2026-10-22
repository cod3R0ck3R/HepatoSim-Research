# Ausführbarer Referenz-Benchmark HSR-BG2024-001

Dieser Forschungsadapter führt das **unveränderte stochastische Kappa-Modell von Bouguéon et al. (2024)** aus. Er ersetzt weder dessen Regeln durch die Swift-ODE noch verwendet er die synthetischen Laborwerte der App als biologische Messdaten. Ziel ist die nachvollziehbare Prüfung von Abbildung 2 B2/B3: HSC-Zustände und Kollagen während wiederholter Stimulation und nach deren Ende.

Das Referenzsystem betrifft Maus-/CCl₄-Fibrose mit modellierten TGFβ1-Pulsen. Die bestehende ALD-Literaturansicht bleibt ein getrenntes Projektmodul. Das Referenzmodell ist **kein Humanmodell der alkoholassoziierten Lebererkrankung**.

**Abgeschlossener Stand vom 22.10.2026:** 14 von 32 geplanten Jobs vollständig, zwei Timeouts, 16 wegen des Gesamtbudgets nicht gestartet. Das Default-Ensemble ist mit zehn Seeds vollständig; die Legendenvariante nur mit vier von zehn. Der [Abschlussbericht](../../Docs/10-ReferenceBenchmark.md) enthält Ergebnisse und Abweichungen. [Maschinenlesbare Auswertung](analysis/benchmark-v1.1.json), [Diagramme](analysis/figures/collagen-trajectories.png) und [74 bestandene Softwaretests](analysis/software-tests.txt) sind enthalten. Vollständiger Seed-Replay, Rasterkontrolle und unabhängige biologische Prüfung bleiben offen.

## Dokumente und unveränderliche Eingaben

- [Audit des bisherigen Demonstrationsmodells](../../Docs/09-DemonstrationModelAudit.md).
- [Referenzauswahl, Quellen und biologische Datenlücken](selection-and-data.md).
- [Originalcode und Pipelineversionen](source-lock.json); unveränderte Modelle und vollständige AGPL-Lizenz unter `vendor/HSC_model_Kappa/`.
- [Runtime-Identität](runtime-lock.json) und [technische Prüfung](runtime-audit.md).
- [Benchmark 1.0](benchmark-v1.0.0.json) und [begründete Ergänzung 1.1](benchmark-v1.1.0.json), jeweils mit SHA256-Datei. Beide wurden vor ihrem jeweiligen Rechenlauf festgelegt.
- [Unterschiede der Modellvarianten](variant-audit.md), [Forschungsprotokoll](research-log.md) und [tatsächlich versuchte lokale Goose-Delegation](local-goose-audit.md).

## Bestehende Ergebnisse auswerten

Alle Befehle hier werden aus dem Projektordner `HepatoSimResearch` ausgeführt. Python 3 ist erforderlich; Runner, Statistik und Tests verwenden ausschließlich dessen Standardbibliothek. Neue Ausgabeordner/-dateien werden verlangt; vorhandene Ergebnisse werden nicht ersetzt.

```sh
python3 -B -m unittest discover -s Research/Reference -p 'test_*.py'
python3 -B Research/Reference/analyze_benchmark.py \
  --results Research/Reference/results/benchmark-v1.1 \
  --previous-results Research/Reference/results/benchmark-v1 \
  --output /tmp/hepatosim-analysis-new.json
```

Die Analyse liest nur abgeschlossene, integritätsgeprüfte Läufe. Bei laufenden oder fehlgeschlagenen Bedingungen enthält sie Einzelresultate und den Fehlstatus; vollständige Ensemblekennzahlen werden zurückgehalten. Ein erneuter Aufruf benötigt einen neuen Ausgabepfad.

## Originalmodell erneut simulieren

Der vorhandene, geprüfte KaSim liegt im lokalen Workspace unter `work/runtime-audit/runtime-v4.1.3.1/KaSim`. Er wird nicht global installiert. `runtime-lock.json` dokumentiert Downloadquelle, Archiv, Eintrag, Commit und ausführbaren Hash. Auf einem anderen Rechner muss genau diese Runtime zugänglich sein; ein anderer Build benötigt eine ausdrücklich neue Benchmarkversion. Ein automatischer Download ist nicht Teil des Runners.

```sh
python3 -B Research/Reference/run_benchmark.py \
  --kasim ../../work/runtime-audit/runtime-v4.1.3.1/KaSim \
  --spec Research/Reference/benchmark-v1.1.0.json \
  --output /tmp/hepatosim-benchmark-new
```

Budget: höchstens 32 Läufe, zwei gleichzeitige KaSim-Prozesse, 900 Sekunden je Lauf und 3.600 Sekunden Gesamt-Rechenfenster. Einzelne technische Abschlussarbeiten und Prozessbeendigung können wenige Sekunden darüber hinaus benötigen. Keine Optimierung, keine Datenanpassung, keine verkleinerte Population als stiller Ersatz. Nach einem fehlgeschlagenen ersten vollständigen Lauf stoppt die Serie. Ein Timeout ist ein technischer Abbruch, kein biologisches Negativergebnis.

Ein Laufordner enthält `run.json` mit Befehlsargumenten, Seed, Status, Laufzeit und Hashes, `trace.csv`, die Originalausgabe sowie KaSim-Eingabeprotokolle. Der Serienordner enthält die eingefrorene Spezifikation, Umgebungsinformationen und `execution.json`. Die Quelle des eigenen Runners wird im Umgebungsmanifest gehasht. Kommentar-UUIDs von KaSim können sich auch bei identischen numerischen Trajektorien unterscheiden.

## Abbildungen

`plot_benchmark.py` benötigt das bereits lokal vorhandene Matplotlib. Die numerische Auswertung hängt davon nicht ab. Im ursprünglichen Workspace ist die Umgebung unter `work/research-venv` vorhanden:

```sh
../../work/research-venv/bin/python Research/Reference/plot_benchmark.py \
  --analysis /tmp/hepatosim-analysis-new.json \
  --results Research/Reference/results/benchmark-v1.1 \
  --output /tmp/hepatosim-figures-new
```

Die Abbildungen enthalten tatsächliche stochastische Einzelverläufe. Bänder beschreiben ausschließlich die Streuung zwischen festgelegten Seeds. Sie enthalten weder Messunsicherheit noch Parameterposterior oder klinische Prognoseunsicherheit. Die beiden markierten Entwicklungsziele sind ungefähre Textzusammenfassungen aus der Veröffentlichung, keine unabhängigen Rohmessungen.

## Interpretation und Grenzen

Die ursprünglichen Autoren verwendeten Kisseleva-2012-Daten bereits zur Modellentwicklung. Sie werden deshalb nicht als unabhängige Testdaten umetikettiert. Keine geeignete unabhängige, protokollkompatible Kollagenzeitreihe mit geklärter Messabbildung wurde für diesen Benchmark qualifiziert. Neuere gepoolte CCl₄-/TAA-Daten benennen eine konkrete Anschlussmöglichkeit, erlauben ohne Stratifizierung jedoch noch keine saubere CCl₄-Vorhersageprüfung.

Die ungefähren 12-/14-fachen Entwicklungsziele erlauben deskriptive Fehlermaße, aber keinen sachlich begründeten Genauigkeits-Grenzwert. Die 43 Tabellenpositionen sind keine 43 unabhängigen Fitparameter; die [Quellenprüfung zur Identifizierbarkeit](parameter-identifiability.md) korrigiert diese zu grobe Einordnung der eingefrorenen Spezifikation. Eine formale Identifizierbarkeitsanalyse wurde nicht durchgeführt. Die vorab definierten Varianten sind Sensitivitätsszenarien, keine geschätzten Parametersätze mit Konfidenzbereichen. Ein Kollagenrückgang bedeutet weder Wiederherstellung aller Leberfunktionen noch Heilung einer Zirrhose.

Die Original-Python-Pipeline ist unvollständig und enthält einen Syntaxfehler; der dünne Adapter ruft stattdessen KaSim direkt auf. Die existierende App besitzt noch keine implementierte Plugin-Laufzeit, an die ein ausführbares Referenzplugin angeschlossen werden könnte. Der Forschungskern bleibt deshalb unabhängig von SwiftUI. Es wird kein herunterladbarer nativer Code auf iOS ausgeführt.

## Lizenzen und Verteilung

Die eingebetteten Originalmodelle und die untersuchte Originalpipeline stehen unter **AGPL-3.0-or-later**; die unveränderte Lizenz ist enthalten. Der Artikel steht unter CC BY 4.0. Die geprüfte KaSim-Runtime besitzt eine eigene LGPL-Lizenz; sie ist nicht als Binärdatei in diesem Forschungsordner eingebettet. Quellen und Lizenzpflichten dürfen bei späterer Weitergabe nicht mit einer medizinischen Freigabe verwechselt werden.

Für den selbst entwickelten HepatoSim-Projektcode wurde in diesem Meilenstein keine neue Open-Source-Lizenz festgelegt. Vor öffentlicher Distribution sind Projektlizenz, Drittanbieterhinweise und die konkrete Integration mit den AGPL-Komponenten zu klären. Dieser Meilenstein veröffentlicht nichts und verarbeitet keine personenbezogenen Gesundheitsdaten.
