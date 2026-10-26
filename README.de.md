# HepatoSim Research

Deutsch · [English](README.md)

## Aktueller Stand — 24. Oktober 2026

Die begrenzte Auswertung realer Makrophagen-Expressionsdaten ist abgeschlossen: sechs Proben, 241.576 Probe-Sets, exakter globaler Permutationswert p = 0,10. Zwei Ausführungen waren bytegleich; zehn gezielte Tests bestanden. Lokale Goose-Inferenz ist belegt, ihr falscher Normalisierungsvorschlag wurde verworfen. Keine neue Kollagenvorhersage, Arzneimittelwirksamkeit oder klinische Validierung belegt. [Zweisprachige Ergebnisse](Docs/18-ExpressionReanalysis.md) · [Ergebnisse reproduzieren oder prüfen](Research/Expression/README.md). Keine automatische neue Berechnung geplant.

## Ziel

Forschungsprototyp für Leberfibrosemechanismen, reproduzierbare Simulationen und Lehre für Forschende, Entwickler und Lehrende. Langfristiger klinischer Schwerpunkt ist die alkoholassoziierte Lebererkrankung (ALD). **Kein validiertes Medizinprodukt, individuelles Prognosewerkzeug oder System für Therapieempfehlungen.**

## Wissenschaftliche Komponenten

Die native Swift-Anwendung enthält ein synthetisches Demonstrationsmodell mit vier Zuständen, RK4, hypothetischen Eingriffen, Kontrollen, Sensitivitätsanalyse, Parameter-Sweeps und synthetischer Kalibrierung. Labor-/Funktionsproxies besitzen keine etablierte klinische Messabbildung. Ein separater ALD-Katalog enthält veröffentlichte Aggregate; diese Beobachtungen kalibrieren die Gleichungen nicht.

Der unabhängige Python-Adapter führt das originale stochastische Kappa-Modell von Bouguéon et al. (2024) aus: HSC-Populationen und Kollagen-Token überwiegend im Maus-/CCl4-Kontext. Kein menschliches ALD- oder Gesamtlebermodell und keine Übertragung auf RK4. [Modellaudit](Docs/09-DemonstrationModelAudit.md) · [Referenzbericht](Docs/10-ReferenceBenchmark.md).

## Tatsächlicher Umfang

Implementiert: macOS- und iPhone-/iPad-Targets, SwiftUI-Diagramme/Zeitleiste, Szenarioeditor, Parameterinspektor, Zahlenfelder mit Tab/Shift-Tab zusätzlich zu Reglern, SQLite, Lauf-JSON-Import/-Export, CSV-Ergebnisexport, Markdown-Berichte und getrennte Evidenzansicht. CSV-Ergebnisse rekonstruieren keinen vollständigen Lauf. Austausch synthetischer medizinischer Datensätze ist eine Storage-API, kein vollständiger UI-Importablauf.

Experimentell: Publikationsreproduktion, Mechanismushypothesen und Kandidatendossiers. Forschungsadapter und App bleiben getrennt. Geplant: vollständige sichere Plugin-Laufzeit, FHIR, Forschungsserver und klinische Kalibrierung. Signierung/Isolation sind spezifiziert, kein fertiger Manager. iOS führt keinen beliebigen heruntergeladenen nativen Code aus. Kein Benchmark begründet Metal-Beschleunigung.

## Architektur und Voraussetzungen

`Sources/HepatoCore`: Modelle/Evidenz; `HepatoStorage`: SQLite/Austausch; `HepatoUI`: gemeinsame SwiftUI. App- und CLI-Einstieg sind getrennt. `Research/Reference`: eingefrorene Spezifikationen, lizenzierte Originalmodelle, Runner, Analyse und Ergebnisse. `Research/Candidates`: Dossiers. Zustand und Entscheidungen bleiben in `RESEARCH_STATE.json`, `RESEARCH_PLAN.md` und `DECISIONS.md`.

Apps benötigen Swift 6 und vollständiges Xcode mit macOS-/iOS-SDK; minimale Deployment-Ziele sind macOS 14 und iOS 17. Keine externen Swift-Package-Abhängigkeiten. Forschungsrunner/-tests benötigen Python 3 mit Standardbibliothek. Matplotlib ist optional für Abbildungen. KaSim ist eine getrennte festgelegte Runtime; siehe [runtime-lock.json](Research/Reference/runtime-lock.json). Der dokumentierte x86_64-Build lief auf Apple Silicon. Andere Builds benötigen einen ausdrücklichen Vergleich. Historische Xcode-27-/Swift-6.4-Prüfungen sind dokumentiert; minimale OS-Versionen und echte iPhones wurden nicht getestet.

## Apps installieren und starten

Einen sauberen Checkout verwenden und Befehle im Projektordner ausführen. Auf koordinierten Rechnern die lokalen Regeln beachten und Builds/Tests über den Wrapper führen; Reservierungen oder Budgets nicht umgehen. Das macOS-Skript gibt den erzeugten `.app`-Pfad aus: diesen öffnen. Alternativ in Xcode `HepatoSim-macOS` wählen und starten. Temporäre Buildverzeichnisse vermeiden beobachtete Finder-Metadaten-/Signaturprobleme synchronisierter Documents-Ordner. Keine Vertriebssignatur, Notarisierung oder App-Store-Freigabe.

Für iPhone/iPad in Xcode `HepatoSim-iOS` und einen verfügbaren Simulator/ein Gerät wählen und starten. Echte Geräte benötigen ein eigenes Signing-Team. Für einen Simulator-Build dient der folgende Befehl.

```sh
./Scripts/verify.sh
./Scripts/build-macos.sh
open Apps/HepatoSim.xcodeproj
xcodebuild -project Apps/HepatoSim.xcodeproj -scheme HepatoSim-iOS -sdk iphonesimulator -destination 'generic/platform=iOS Simulator' -derivedDataPath /tmp/hepatosim-xcode-iOS -jobs 2 CODE_SIGNING_ALLOWED=NO build
```

## Bedienung und synthetisches Beispiel

Die App erzeugt beim ersten Start ein synthetisches Beispiel. Parameter direkt oder per Regler eingeben, dann berechnen und speichern. Änderungen betreffen den nächsten Lauf; ungültige Eingaben blockieren die Berechnung. macOS/iOS teilen Code und Schema, keine automatisch synchronisierte Datenbank. Läufe als JSON übertragen. Daten liegen im Application-Support-/Containerverzeichnis der App; bestehende Lauf-UUIDs werden nicht überschrieben.

Für das folgende Beispiel ein neues Ausgabeverzeichnis verwenden. Die CLI prüft deterministische Sample-Wiederholung und SQLite-/JSON-Roundtrips und schreibt Szenario-/Kontroll-JSON, CSV, Ensemble und Sweep. Seed 42 und die feste Konfiguration reproduzieren numerische Samples; UUIDs/Zeitstempel ändern sich. [Gebündelte Beispiele](Examples/README.md) sind synthetisch, keine Patientendaten. Parameterstreuungsbänder sind keine klinischen Prognoseintervalle. Das Abdrucken des Befehls behauptet keinen neuen erfolgreichen Lauf.

```sh
swift run --jobs 2 --scratch-path /tmp/hepatosim-example-build hepatosim /tmp/hepatosim-example-session
```

## Referenz-Benchmark und Wiederaufnahme

Der Prüfbefehl liest ausschließlich. Die Ausführung benötigt die festgelegte KaSim-Datei und einen Koordinatorslot. Spezifikation 1.2 verwendet eine geprüfte historische Kontrolle und führt nur fehlende technische Kontrollen aus. Gültige vollständige Läufe werden übersprungen; unvollständige/beschädigte Läufe sperren automatische Wiederholungen. Budget: ein Worker, zwei neue Läufe, höchstens je 900 Sekunden und insgesamt 1.800 Simulationssekunden. Vollständige Läufe sind die Checkpointeinheit; CSV bewahrt keinen RNG-Zustand. Änderungen an laufender Spezifikation/Runner werden zurückgewiesen. [Früherer Benchmark und Analyseanleitung](Research/Reference/README.md). **Neun Resume-Unit-Tests bestanden. Beide echten technischen Kontrollen und die tatsächliche Wiederaufnahme abgeschlossener Läufe sind jetzt bestanden; siehe [Kontrollergebnisse](Docs/13-TechnicalControls.md).** Im öffentlichen Export wird das bereinigte Kontrollmanifest gegen einen ausdrücklichen Exportbeleg geprüft; ursprüngliche private Pfadbytes sind nur durch den Exporteur attestiert. Numerische CSV-Inhalte und eingefrorene Kriterien bleiben unverändert. CSV-Kommentare werden bereinigt; ursprüngliche und veröffentlichte Trace-Hashes getrennt dokumentiert.

```sh
python3 -B -m unittest discover -s Research/Reference -p 'test_*.py'
python3 -B Research/Reference/resume_reference.py
python3 -B Research/Reference/resume_reference.py --execute --kasim /absolute/path/to/KaSim
```

Der separat eingefrorene [Mechanismuspilot](Docs/14-MechanismPilot.md) verwendet geprüfte Kontrollen wieder und führt je Aufruf höchstens einen fehlenden Kontrast aus. Sein Runner bestand neun gezielte Softwaretests; das Protokoll behauptet noch kein Mechanismusergebnis.

Eine spätere [Prüfung des externen Datenzugangs](Docs/15-ExternalDataAccess.md) erschloss getrennte Hofer-CCl4-Kollagenaggregate. Der geprüfte Importer bestand sechs Tests und wurde auf die Quelltabelle angewendet. Expositionsprotokoll und Messabbildung müssen noch qualifiziert werden; keine unabhängige Vorhersageprüfung wird behauptet.

Zwei der sechs neuen Kontrastläufe sind vollständig; aggregierte Vergleiche bleiben zurückgehalten. [Ausführungsstand und Analyseprüfungen](Docs/16-MechanismProgress.md).

**Stand 23. Oktober:** Zwei spätere Kontrastversuche erreichten ihre Grenze von 900 Sekunden; die übrigen zwei wurden vor dem Start storniert. Originalpilot und Teilserie 1.3.1 bleiben unvollständig. Teilkurven bleiben erhalten, ohne aggregierte Behandlungsaussage. [Timeoutbericht](Research/Reference/mechanism-subset-timeout-2026-10-23.md). Die [Sato-Quellenprüfung](Research/Reference/sato2023-data-triage.md) benennt eine Datenanfrage zu einer Entzugsstudie; die [Jerez-Quellenprüfung](Research/Reference/jerez2026-data-triage.md) dokumentiert eine erfolgreich gelesene Endpunkttabelle unter fortgesetzter Schädigung, deren Einheiten, Normalisierung und Tier-/Feldzuordnung noch zu klären sind. Beides ist kein unabhängiges Validierungsergebnis.

Die erhaltene Teilserie ohne neue Simulation prüfen. Dieser Befehl endet absichtlich mit Exit 1, weil ein Lauf unvollständig ist; eine korrekte Zurückweisung durch die Software ist kein erfolgreicher Benchmark:

```sh
python3 -B Research/Reference/run_mechanism_pilot.py --spec Research/Reference/benchmark-v1.3.1.json --output Research/Reference/results/mechanism-v1.3.1
```

## Lokales Goose/Ollama

Nur den vorhandenen lokalen Ollama-Provider verwenden. Installierten Namen, Digest und Loopback-Endpunkt bestätigen; eine lokale URL allein beweist keine lokale Inferenz. Der Aufgabentreiber verwirft Remote-Modellmetadaten und erfasst ein passend geladenes GGUF-Modell samt tatsächlichem lokalen Runner. Eine isolierte Aufgabe, keine Profil-Erweiterungen, höchstens 300 Sekunden, kein automatischer Retry. Keine Installation oder dauerhaften Provideränderungen. Platzhalter durch tatsächlich installierte Werte ersetzen und einen neuen Ausgabeordner verwenden. Ollama getrennt von KaSim/schweren Builds reservieren. KI-Ausgaben prüfen; sie sind keine biologische Evidenz. Keine behauptete Tokenersparnis. Folgeaufgabe: vorbereitet und an den Providergrenzen getestet, nicht ausgeführt. Der bestätigte Modellblob umfasst bereits 8.988.113.226 Bytes vor Runtimebedarf; der gemeinsame Rechner erlaubt nur 8 GiB je Job. Der Koordinator lehnte eine spekulative Erhöhung ab. Keine erfolgreiche lokale Inferenz behauptet. [Frühere Timeoutversuche](Research/Reference/local-goose-audit.md).

Der Treiber erfasst `local_runner_observed` getrennt und setzt `inference_verified` niemals automatisch: Auch Goose-Exit0 mit geladenem Runner reicht nicht. Modell-Runner-Zuordnung und tatsächlich erzeugte Antwort prüfen, bevor lokale Inferenz bestätigt wird. Vier lokale Worker-Regressionstests decken erfolgreiche und fehlgeschlagene gemockte Goose-Abschlüsse ab; sie rufen kein Modell auf.

Späterer Ausführungsstand: Eine separat erlaubte einmalige Aufgabe mit dem vorhandenen `hermes3:8b` lieferte nach 112,647 Sekunden Goose-Exit 0. Ihr Audit belegte weder einen passend zugeordneten lokalen Runner noch verifizierte Inferenz. Das ersetzt die frühere Angabe „nicht ausgeführt“ nur für diese konkrete Aufgabe; daraus folgt weder ein Inferenzerfolgs- noch ein Tokenersparnisnachweis.

```sh
python3 -B -m unittest discover -s Research/LocalAI -p 'test_*.py'
python3 -B Research/LocalAI/run_local_task.py --model INSTALLED_MODEL --digest CONFIRMED_DIGEST --task Research/LocalAI/translation-task.txt --output /absolute/path/to/new-local-task
```

## Prüfstatus, Quellen und Grenzen

Der historische Meilenstein schloss 14/32 geplante Jobs ab, darunter zehn Default-Seeds; zwei endeten mit Timeout, sechzehn wurden nicht gestartet. Die qualitative Kollagenrichtung wurde teilweise reproduziert, mit quantitativen sowie Quellen-/Runtimegrenzen. Historische Belege dokumentieren 52 Swift- und 74 Forschungstests. Die Folge-Referenzsuite bestand 82 Tests; nach der Exportergänzung bestanden neun Resume-, drei Providergrenzen- und vier Exporttests. Diese Zahlen überschneiden sich. Die Archivauswertung wurde tatsächlich neu berechnet und stimmt bis auf den Erstellungszeitpunkt überein. [Aktueller Forschungsbericht](Docs/11-ResearchFollowup.md). Seed-Replay stimmt in allen 502 Zeilen numerisch exakt überein; beide Ausgaberaster sind vollständig und an gemeinsamen Zeiten ohne Abweichung. Das sind technische Prüfungen eines Seeds, keine zusätzlichen unabhängigen Ensemblemitglieder. Keine unabhängige biologische Validierung, Übertragbarkeit auf Menschen oder klinische Validität belegt.

Stochastische Streuung, Parameterunsicherheit, Messfehler und numerische Zuverlässigkeit sind getrennte Größen. Weniger modelliertes Kollagen belegt keine Heilung oder wiederhergestellte Leberfunktion. Entwicklungsdaten dürfen nicht als unabhängig umbenannt werden. [Bouguéon 2024](https://doi.org/10.1371/journal.pcbi.1011858) · [festgelegte Quellen](Research/Reference/source-lock.json) · [Kandidaten und negative Studien](Research/Candidates/README.md) · [Datenlücke](Research/Candidates/independent-data-followup.md) · [ALD-Evidenz](Docs/08-ALD-Evidence.md).

Der tatsächliche bereinigte Veröffentlichungssnapshot bestand **90 Forschungssoftwaretests**. Die Neuauswertung bewahrte alle wissenschaftlichen/numerischen Felder; sämtliche 18 numerischen CSV-Inhalte stimmten mit den lokalen Originalen überein. Nur Zeitstempel-/Pfad-/Hashmetadaten änderten sich. [Publikationsprüfung](Research/Reference/analysis/publication-verification-v2.json) · [Testnachweis](Research/Reference/analysis/software-tests-v2.txt).

## Sicherheit, Lizenzen und Mitarbeit

Nur synthetische Eingaben und passend lizenzierte öffentliche Aggregate verwenden. SQLite besitzt keine zusätzliche Datenbankverschlüsselung; Plattformschutz erlaubt keinen Patientendatenbetrieb. Keine Geheimnisse oder identifizierbaren Gesundheitsdaten einsenden. [Sicherheit](SECURITY.md) · [Mitarbeit](CONTRIBUTING.md) · [Fremdkomponenten](THIRD_PARTY_NOTICES.md).

Eigener HepatoSim-Code und eigene Projektdokumentation stehen unter der [MIT-Lizenz](LICENSE), Copyright 2026 Johnnie 4 free. Nutzung, Änderung und Weitergabe sind auch kommerziell erlaubt; Lizenz- und Copyright-Hinweise müssen erhalten bleiben. Separat eingebettete Originalmodelle behalten AGPL-3.0-or-later. Keine neue Lizenz für Fremdmaterial. Der frühere README-Inhalt bleibt in `Docs/README-HSR001.md`; aktueller Fortschritt steht in der Forschungszustandsdatei.

## Kollagenprüfung und Vorbereitung der macOS-Vorabversion

Maintainer: **Johnnie 4 free**. [Der neue interne Kollagenvergleich](Docs/19-CollagenInternalCheck.md) bestand fünf Softwaretests und die exakte Wiederholung. Er identifiziert keine Behandlungswirkung und liefert keine unabhängige biologische Validierung. [Prüfung ausführen](Research/CollagenCheck/README.md). Das macOS-Packaging erzeugt eine universelle macOS-Forschungsvorabversion (Start auf Apple Silicon geprüft) mit Ad-hoc-Signatur; sie ist nicht notarisiert. Die Version ist experimentell, benötigt macOS 14 oder neuer und ist kein Medizinprodukt. Kein iPhone-Binärpaket enthalten. Eigener HepatoSim-Code und diese App-Version sind jetzt MIT-lizenziert; Fremdlizenzen gelten weiterhin.

[macOS release verification / Prüfung](Docs/20-MacOSReleaseVerification.md).

## TAA-Übertragung und Datenaufnahme (24.Oktober2026)

Die unveränderte CCl4-Rate verfehlte bei TAA das vorab definierte Vergleichskriterium.16 Tests bestanden;12 geprüfte Forschungseinträge wurden lokal ergänzt, bestehende Simulationsläufe unverändert erhalten. Ein TAA-Einzelzellarchiv von 2026 und menschliche Kollagensynthese-Tabellen wurden aufgenommen. Dies ist keine klinische Validierung. Siehe [Bericht](Docs/21-TAATransferAndEvidence.md) und [Reproduktion/Datenaufnahme](Research/TAATransfer/README.md).

## Prüfung der neun GEO-Bibliotheken (24. Oktober 2026)

Neun echte Matrizen wurden lokal geprüft: 38.136 gefilterte Zellen und alle drei Gruppensummen stimmen mit der Publikation überein. Sieben Tests und exakte echte Wiederaufnahme/Wiederholung bestanden. SEMA4D–PLXNB2 begründet eine Zelltyp-Folgeprüfung; LMCD1 bei Rückbildung und CTSL zeigen wichtige Sensitivitätsgrenzen. Explorative Auswertung der Autorendaten, kein Arzneimittelwirksamkeitsnachweis. Die lokale KI-Prüfung blieb blockiert und wurde nicht verwendet. [Prüfung und Mechanismusfragen](Docs/22-GEOSampleCheck.md) · [Wiederholen/fortsetzen](Research/GEOSampleCheck/README.md).

## Externe SEMA4D–PLXNB2-Prüfung (24. Oktober 2026)

Eine getrennte menschliche NAFLD-Kohorte stützt erhöhte SEMA4D-RNA, jedoch nicht den vorab geforderten gemeinsamen Anstieg von SEMA4D und PLXNB2. Alle 216 Zähldateien wurden geprüft; 206 erkrankte Biopsien gingen in die Analyse ein. Fünf Tests und eine identische Cache-Wiederholung bestanden. Lokale Goose-Inferenz fand statt; unbelegte Vorschläge wurden verworfen. [Ergebnisse und Grenzen](Docs/23-SEMAIndependent.md) · [Wiederholen](Research/SEMAIndependent/README.md).

## GSE210077: donor/cell-type check (24 October 2026)

Sechs menschliche Spender und 27.692 annotierte Zellkerne wurden nach Zelltyp ausgewertet. Das gemeinsame Richtungskriterium für Makrophagen-SEMA4D und Sternzell-PLXNB2 wurde nicht erfüllt. Die nachträgliche Prüfung gemeinsamer Gen-IDs ändert das nicht; Referenz und Erkrankungsgruppe bleiben konfundiert.14 Tests und beide identischen Cache-Wiederholungen bestanden. [Report / Bericht](Docs/24-DonorCellCheck.md) · [Reproduce / Wiederholen](Research/DonorCellCheck/README.md).

## Größere Kohorte mit gemeinsamer Verarbeitung (24. Oktober 2026)

GSE244832:18 menschliche Spender,128.223 Zellkerne. Myeloides SEMA4D tendenziell höher, Sternzell-PLXNB2 niedriger; keiner besteht die Korrektur für zwei Tests. Zwei widersprüchliche Spendergruppen wurden separat geprüft; die Hypothese eines gemeinsamen Anstiegs besteht unter beiden Zuordnungen nicht.22 Tests und drei identische Cache-Wiederholungen bestanden. [Bericht](Docs/25-UniformCohort.md) · [Wiederholen](Research/UniformCohort/README.md). Keine Aussage zur Behandlungswirkung.

### 26. Oktober2026: Spenderzuordnung nachgeprüft

GEO-Description und Autoren-Tabelle stimmen für alle18 Spender überein; das Feld war zuvor übersehen worden. Ohne beide Spender mit widersprüchlichen Zellmetadaten verbleiben8 Erkrankte und5 Kontrollen in den zwei Tests: SEMA4D-Differenz+0,791560 (q0,158508), PLXNB2−0,301918 (q0,241647); keine Unterstützung einer gemeinsamen positiven Richtung.18 gezielte Tests und eine bytegleiche Wiederholung bestanden. Eine neueETS1-Messwertdatei wurde für einen späteren Benchmark heruntergeladen; ihre Messwerte wurden nicht ausgewertet. [Bericht und Grenzen](Docs/26-DonorProvenanceFollowup.md), [Wiederholung](Research/UniformCohort/README.md).

## ETS1-Quellenprüfung —26.Oktober2026

[Die Prüfung der Abbildung2](Docs/27-ETS1SourceAudit.md) kann die gelieferte Normalisierung für3/4 Siriusrot-Gruppen nicht reproduzieren. Elf Softwaretests bestanden; Wiederholung in einem separaten Prozess bytegleich. Eine quantitative Behandlungsinterpretation bleibt bis zur Quellenklärung zurückgestellt. [Reproduktion](Research/ETS1Regression/README.md). Private Übergaben und Logs bleiben unveröffentlicht.

## ETS1-Normierungskontrolle — 26. Oktober 2026

[Die Folgeprüfung](Docs/28-ETS1ScalingFollowup.md) schließt einen anderen gemeinsamen Nenner je Gruppe innerhalb der festgelegten Rundungsgrenzen als Erklärung für drei der vier widersprüchlichen Quellgruppen aus. Vier neue Tests und bytegleiche Wiederholung bestanden. Quellenzuordnung bleibt offen; keine Behandlungskalibrierung.

## HSC-Zellschicksal als Laborfrage (26. Oktober 2026)

Das [Labor-Entscheidungsblatt](Docs/29-HSCFateLabDecision.de.md) trennt HSC-Inaktivierung, Entfernung und spätere Reaktivierung. Eine vorab festgelegte Erweiterung des ursprünglichen Kappa-Modells prüft eine Zellschicksalsänderung nach Schädigungsende. Unabhängige Originalquellen begründen die Untersuchung des IL-10-Signalwegs und funktioneller Gegenbefunde; eine Arzneimittelwirkung wird nicht angepasst. Die bedingte Identifizierbarkeitsrechnung zeigt, warum ein Endpunkt Zellschicksal und Persistenz nicht getrennt bestimmt. Dies sind Forschungsergebnisse, keine klinische Validierung.

Die kleinen Prüfungen lassen sich vom Repository-Hauptverzeichnis aus wiederholen. Vollständige KaSim-Läufe und geprüfte Wiederaufnahme sind in [Research/HSCFate](Research/HSCFate/README.md) dokumentiert:

```sh
cd Research/HSCFate
python3 -m unittest -v test_fate
python3 identifiability.py
python3 run.py --analyze
python3 verify.py
```

## HSC-Folgeprüfungen (26. Oktober 2026)

Elf weitere lokale Läufe erweitern den Zellschicksalskontrast auf zehn gepaarte Seeds und prüfen eine Persistenzannahme. Das Kollagen-Mittelwertintervall überschreitet null; der inaktive Zellpool steigt in allen zehn Paaren. Neun Tests, bytegleiche Roh-/Exportauswertung und geprüfte Wiederaufnahme bestanden. Zwei Fehler der Ereignisausgabeprüfung bleiben erhalten und sind ausdrücklich korrigiert. Autorenruntime und biologische/Arzneimittel-Zuordnung bleiben offen; keine Laborweiterleitung. [Bericht](Docs/30-HSCPreLabVerification.de.md).

```sh
cd Research/HSCRobustness
python3 -B verify.py
```
