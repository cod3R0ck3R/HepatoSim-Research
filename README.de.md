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

Für eigenen HepatoSim-Code wurde keine Open-Source-Lizenz gewählt. Öffentliche Sichtbarkeit ist keine Open-Source-Lizenz. Separat eingebettete Originalmodelle behalten AGPL-3.0-or-later. Keine neue Lizenz für Fremdmaterial. Der frühere README-Inhalt bleibt in `Docs/README-HSR001.md`; aktueller Fortschritt steht in der Forschungszustandsdatei.

## Kollagenprüfung und Vorbereitung der macOS-Vorabversion

Maintainer: **Johnnie 4 free**. [Der neue interne Kollagenvergleich](Docs/19-CollagenInternalCheck.md) bestand fünf Softwaretests und die exakte Wiederholung. Er identifiziert keine Behandlungswirkung und liefert keine unabhängige biologische Validierung. [Prüfung ausführen](Research/CollagenCheck/README.md). Das macOS-Packaging erzeugt eine Apple-Silicon-Forschungsvorabversion mit Ad-hoc-Signatur; sie ist nicht notarisiert. Die Version ist experimentell, benötigt macOS 14 oder neuer und ist kein Medizinprodukt. Kein iPhone-Binärpaket enthalten. Der bestehende Lizenzstatus bleibt unverändert.
