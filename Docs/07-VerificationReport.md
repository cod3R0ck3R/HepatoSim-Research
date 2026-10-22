# Technischer Prüfbericht — 22.10.2026

## Nachträgliche Präzisierung — 22.10.2026

Das [Audit des Demonstrationsmodells 0.1.0](09-DemonstrationModelAudit.md#8-konkrete-befunde-zum-prüfbericht-und-wissenschaftliche-anschlussarbeit) begrenzt zwei Aussagen des unten unverändert erhaltenen historischen Berichts: Der dort genannte „unabhängige Referenzalgorithmus im Kern-Testcode“ ist **nicht als ausführbarer Referenzgenerator vorhanden**. `HepatoCoreTests.swift:41` vergleicht vier gespeicherte Referenzwerte mit einem Kommentar zu einer feineren Python-RK4-Rechnung. Das ist ein numerischer Regressionstest; ein unabhängig reproduzierbarer Golden-Reference-Nachweis ist damit nicht belegt.

„Konvergenz bestanden“ bezieht sich auf den isolierten exponentiellen Entzündungsabbau bei ansonsten null gesetzten Raten (`HepatoCoreTests.swift:50`). Daraus folgt weder ein Konvergenznachweis des vollständig gekoppelten Systems über den gesamten Eingaberaum noch allgemeine numerische Stabilität. Der ergänzende Eckentest deckt 16 Anfangszustände über drei Modelltage ab. Diese Dokumentationskorrektur verändert keine früheren Testzahlen und führt keine Prüfungen erneut aus. Sämtliche Nachweise bleiben **Software-Verifikation, keine biologische oder medizinische Validierung**; experimentelle Kalibrierung und ein Kollagen-Messmodell fehlen weiterhin.

## Ergebnis und Geltungsbereich

Der erste Vertical Slice ist ausführbar: synthetischer Zustand → RK4-Simulation → SQLite → native SwiftUI-Diagramme. Szenario und Kontrolllauf werden gespeichert; ein gespeicherter Vergleich wird anhand identischer Konfiguration und Modellversion wiederhergestellt. Die aktuelle Erweiterung ergänzt eine getrennte ALD-Evidenzansicht und direkte Zahlenfelder neben kontinuierlichen Slidern. Dies ist Software-Verifikation, keine medizinische oder biologische Validierung.

Die Evidenz stammt aus fünf veröffentlichten Primärstudien und enthält tatsächliche klinische Aggregate. Die ODE, ihre Raten und Laborproxies bleiben synthetisch beziehungsweise heuristisch; es erfolgte keine klinische Kalibrierung. Der Quellenkatalog ist kein Individualdatensatz und kein unabhängiger Validierungsdatensatz für das Modell.

## Aktuelle Erweiterung: Prüfstatus

| Prüfung | Dokumentierter Stand |
|---|---|
| Abschließender Swift-Testlauf | **52 Tests, 0 Fehler: 28 Core, 17 Storage, 7 UI-Zustands-/Eingabelogik**. `swift test` endete erfolgreich; Ergebnisprotokoll `/tmp/hepatosim-final-tests.log`. |
| Unabhängige Quellenprüfung | Fünf Primärabstracts gegen Katalog und `Docs/08-ALD-Evidence.md` geprüft: Hofer 2023 (zwei Arbeiten), Hofer 2026, Gianni 2017, Hofer 2025. Publizierte Zähler, Nenner, Zeitbezüge und Messwerte stimmen mit den extrahierten Befunden überein. |
| Wissenschaftliche Trennung | Quellreview bestätigt: Rohanteile erhalten Wilson-Intervalle; Ereigniszeitschätzungen und kontinuierliche Befunde nicht. Keine gepoolten Kohorten und keine numerische ODE-Kalibrierung aus den Aggregaten. |
| Numerische Eingabe | Automatisierte Parser-/Zustandstests bestanden. Zusätzlich nativ geprüft: Dezimalkomma `0,123`, Punkt `0.42` und Änderung auf `0,2`; Zahlenfelder und Slider bleiben synchron. |
| Native Tastaturbedienung | Tab wechselt vorwärts, Shift-Tab zurück. Im Parameterinspektor erreicht Tab auch das letzte Feld; `ScrollViewReader` scrollt das fokussierte Feld sichtbar. An der laufenden Mac-App geprüft. |
| Ungültiger Entwurf und Zustandswechsel | Initiale Fibrose `99` sperrt die Berechnung. Fehlerhinweis und Sperre bleiben beim Bereichswechsel erhalten; das ALD-Preset verwirft ungültige Entwürfe. Nativ geprüft. |
| ALD-Szenario und Persistenz | Nach Auswahl des Presets erfolgreich berechnet und gespeichert: neues ALD-/Kontrollpaar, insgesamt vier gespeicherte Läufe im geprüften App-Zustand. |
| Finaler macOS-Build | **Erfolgreich**, Exit 0 nach Korrekturen für Shift-Tab und automatisches Scrollen; native App anschließend bedient. |
| Finaler iOS-Build | **Erfolgreich**, Exit 0 und `BUILD SUCCEEDED` in `/tmp/hepatosim-final-ios.log`; generisches iOS-Simulatorziel. |
| Finaler iOS-Start und Persistenz | Aktuelle Simulator-App installiert und gestartet; Prozess nach 41 Sekunden weiterhin aktiv, beobachtete CPU-Anzeige `0.0 %`. Eine schreibgeschützte SQLite-Abfrage bestätigte zwei bestehende synthetische Läufe nach Installation/Update. Start-/Persistenz-Smoke-Test ohne GUI-Prüfung; kein Lastbenchmark. |
| Leerlaufbeobachtung | Der geprüfte Mac-Prozess meldete nach etwa drei Minuten `0.0 %` CPU in `ps`. Einzelbeobachtung, kein vollständiger Performance-, Energie- oder Lastbenchmark. |
| Finales App-Paket | **Bestanden**: finales App-Bundle mit `ditto --norsrc --noextattr` neu als ZIP gepackt, über das vorhandene Startskript extrahiert und gestartet. `codesign --verify --deep --strict --verbose=2` endete mit Exit 0. Lokale Ad-hoc-Signatur, keine Notarisierung. |
| Ressourcen und Persistenz nach Neustart | In der aus dem finalen ZIP gestarteten Mac-App waren alle fünf Evidenzquellen geladen und sichtbar. Vier gespeicherte Läufe einschließlich ALD-/Kontrollpaar blieben nach Neustart vorhanden. |

Die Quellenprüfung ist ein Extraktionsreview, keine systematische Vollständigkeitsprüfung der gesamten ALD-Literatur. Bei der multizentrischen Rekompensationsstudie bleibt der rohe beobachtete Anteil getrennt vom publizierten Fünfjahresschätzer. Frühere Steifigkeitsänderungen werden nicht als histologisch belegte Kollagenregression ausgewiesen. Menschliche und tierexperimentelle Beobachtungen bleiben getrennt.

## Bereits ausgeführte Prüfungen des Basisstands

Diese Ergebnisse wurden vor Abschluss der ALD-/Zahlenfeld-Erweiterung bestätigt. Sie werden als bisherige Nachweise erhalten; für den neuen Stand gilt die Statusmatrix oben.

| Prüfung | Ergebnis |
|---|---|
| Gemeinsamer Swift-Testlauf des Basisstands | **38 Tests, 0 Fehler**: 19 Kern, 17 Speicherung/Austausch, 2 UI-Zustandslogik |
| RK4, Referenztrajektorie, Konvergenz | Bestanden; Details und unabhängiger Referenzalgorithmus im Kern-Testcode |
| Zustandsgrenzen, NaN, Eingaberessourcen, Interventionszeitpunkt | Bestanden |
| Seed-RNG, Ensemble, Sensitivität, Sweep, synthetische Kalibrierung | Bestanden; keinerlei Kalibrierung an Patientendaten |
| SQLite-Wiederöffnung, Duplikat-Rollback, Schemaablehnung, Symlinks und Rechte | Bestanden |
| JSON-Replay, manipulierte Zustände, falsches Zeitgitter | Bestanden; Import wird gegen Modell 0.1.0 nachgerechnet |
| Medizinischer CSV-/JSON-Austausch | Bestanden: fehlende Werte, Einheiten, Quotes, Newlines, Unicode, synthetische Kennzeichnung |
| CLI-Integration | Deterministische Wiederholung, SQLite- und JSON-Roundtrip; 74 Samples, Seed 42; Ensemble und Sweep exportiert |
| macOS-Xcode-Build | Erfolgreich, Debug, arm64; gemeinsame Swift Packages eingebunden |
| Mac-App-Paket | Ad-hoc-Signatur nach ZIP-Extraktion in `/tmp` erfolgreich geprüft; Startskript ausgeführt |
| macOS-Oberfläche | Natives Fenster geöffnet; Dashboard, Diagramme, Laboransicht und 64er-Variantenband über UI geprüft; finale Layoutkorrekturen visuell geprüft |
| iOS-Xcode-Build | Erfolgreich für generischen iOS-Simulator |
| iOS-Lauf | Auf iPhone-17-Pro-Simulator mit iOS 26.5 installiert und gestartet; zwei gespeicherte Modellläufe 0.1.0 in der App-Datenbank nachgewiesen |

Umgebung: Apple Silicon arm64, Xcode 27.0 (27A266a), Swift 6.4. Mindestziele im Projekt: macOS 14 und iOS 17. Diese Mindestversionen wurden nicht auf eigenen Geräten geprüft.

Der abschließende 52er-Lauf verwendete `swift test --scratch-path /tmp/hepatosim-verify.QJAxB7/package` und endete am 22.10.2026 um 12:58 Uhr ohne Fehler. Die drei XCTest-Bundles melden getrennte Summen; zusammen sind es 28 + 17 + 7 Tests. Zusätzliche Meldungen einer Swift-Testing-Laufzeit mit null Tests ändern diese XCTest-Summe nicht. Der wiederholbare Einstieg ist `Scripts/verify.sh`; das Skript verwendet jeweils ein neues temporäres Verzeichnis. macOS-Paketierung: `Scripts/build-macos.sh`. Das abschließend geprüfte ZIP wurde nach `/tmp/hepatosim-launch.dgaFDR/HepatoSimResearch.app` extrahiert. iOS-Aufruf steht im README. Die temporären Protokoll-/Extraktionspfade dienen als lokale Nachweise und sind kein dauerhaftes Testarchiv.

## Gefundene und behobene Fehler

1. Dateianbieter/Finder ergänzen im Dokumente-Ordner Metadaten an Build-Bundles. Dadurch schlug Codesigning mit „resource fork, Finder information, or similar detritus not allowed“ fehl. Builds und App-Extraktion laufen deshalb unter `/tmp`; das auslieferbare Artefakt ist ein ZIP plus geprüftem Startskript.
2. Der macOS-App-Target baute im Debug-Modus zusätzlich x86_64, während das Package nur für die aktive arm64-Architektur gebaut wurde. `ONLY_ACTIVE_ARCH=YES` im Debug-Projekt beseitigt den inkompatiblen Modulimport. Ein universeller Intel-/ARM-Distributionsbuild wurde nicht geprüft.
3. Kalibrierungsbeobachtungen mit Dezimalzeitpunkten konnten durch binäre Rundung abgelehnt werden. Die Zuordnung akzeptiert nun maximal acht ULPs und weist echte Off-Grid-Zeitpunkte sowie doppelte Zuordnungen zurück.
4. Große JSON-Dateien wurden vor Größenprüfung komplett auf dem UI-Thread geladen. Ein begrenztes Lesen mit maximal 16 MiB plus Prüfbyte und Decoding außerhalb des UI-Threads ersetzt dies.
5. Vorhandene fremde Speicherordner erhielten ungefragt neue Dateirechte. Der Store verändert solche Ordner nicht mehr und weist ungeeignete Rechte zurück.
6. Importierte Samples wurden zunächst nur strukturell geprüft. Unterstützte Modellläufe werden nun reproduziert und mit dokumentierter numerischer Toleranz verglichen.
7. CSV-Parsing wurde für Anführungszeichen neben kombinierenden Unicode-Zeichen auf Unicode-Skalare umgestellt.
8. Sliderbeschriftungen erschienen im macOS-Layout doppelt. Sichtbare Beschriftungen wurden vereinheitlicht; zugängliche Labels bleiben erhalten. Slidergrenzen decken gültige Importwerte ab.
9. Die Untersuchung des gemeldeten UI-Stillstands identifizierte aufwendige Erzeugung von Schrittmarkierungen/-beschriftungen durch fein abgestufte native Slider. `ParameterControl` verwendet jetzt kontinuierliche Slider ohne `step` und separate Zahlenfelder für präzise Eingaben. Die auslösende Konfiguration ist entfernt; Zahleneingabe, Vorwärts-/Rückwärtsfokus und Scrollen wurden anschließend nativ geprüft. Die dokumentierte Leerlaufbeobachtung zeigte keine anhaltende CPU-Last. Es wird keine umfassende Performance- oder Lasttestabdeckung behauptet.
10. Die erste Kurzbeschreibung des Rekompensationsendpunkts war zu weit gefasst. Der ALD-Katalog benennt nun die studieneigenen Anforderungen, insbesondere Rückbildung von Aszites und Enzephalopathie ohne jeweilige Therapie. Medikamentös kontrollierte persistierende Dekompensation wird nicht als dieser Rekompensationsendpunkt dargestellt.
11. Rückwärtsnavigation und Fokus auf unterhalb des sichtbaren Bereichs liegende Zahlenfelder waren zunächst unvollständig. Der Fokuspfad berücksichtigt Shift-Tab und das native Backtab-Zeichen; der Parameterinspektor scrollt zum fokussierten Feld. Beide Wege wurden nach dem finalen macOS-Build praktisch geprüft.

## Nicht geprüft oder noch nicht vorhanden

- Kein echtes iPhone/iPad, kein visueller Simulator-Durchlauf: die Simulator-GUI war in der lokalen Xcode-Installation nicht am üblichen Pfad verfügbar. Der Simulatorprozess und die Persistenz wurden über `simctl` geprüft.
- Keine vollständige VoiceOver-, Kontrast-, Dynamic-Type-, Light-Mode- oder Geräte-Matrixprüfung. Native Semantik und adaptive Ansichten sind vorhanden; Barrierefreiheit ist damit nicht zertifiziert.
- Kein notarisiertes Distributionspaket, kein App-Store-Release, kein gehärteter Produktionssignatur-Nachweis. Die lokale Debug-App hat App-Sandbox und nutzergewählten Dateizugriff, aber auch Debugger-Entitlement; keine Netzwerkberechtigung. Nicht für Realdaten einsetzen.
- Keine verschlüsselte Datenbank, keine Cloud-Synchronisierung, kein realer KI-Provider, keine ausführbare Plugin-Laufzeit, keine Child-Pugh-/MELD-Berechnung und kein FHIR-Adapter. Diese Punkte stehen im Meilensteinplan.
- Keine simulierten klinischen Endpunkte, keine Vorhersage von Dekompensation oder Überleben, keine externe biologische Validierung des Kerns. Die separat dargestellten publizierten klinischen Endpunkte ändern diesen Status nicht. Parameterstreuung ist keine klinische Prognoseunsicherheit.

## Übergabe

`Examples/` enthält synthetische Beispielverläufe und Analysen. `../Start-HepatoSim.command` und `../HepatoSimResearch-macOS.zip` müssen nebeneinander bleiben. Das Startskript entpackt in ein neues temporäres Verzeichnis, prüft die Signatur und öffnet die native App. Gespeicherte Daten bleiben im App-Container, nicht im temporären Programmverzeichnis.
