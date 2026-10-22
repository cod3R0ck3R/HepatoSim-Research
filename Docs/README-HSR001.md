> Historical HSR-001 README. Relative paths below refer to the project root; current instructions are in ../README.md and ../README.de.md.

# HepatoSim Research

Native Forschungsplattform für experimentelle Lebermodelle mit einem ersten Evidenzschwerpunkt auf **alkoholassoziierter Lebererkrankung (ALD)**. Der Vertical Slice simuliert einen synthetischen Zustand, vergleicht eine Kontrolle, speichert lokal und visualisiert in SwiftUI. Eine getrennte Evidenzansicht erschließt publizierte Aggregate aus fünf überprüften Primärstudien. Die langfristig geplante Plattform ist damit noch nicht vollständig implementiert.

**Keine medizinische Validierung oder klinische Kalibrierung des Simulationskerns.** Gleichungen, Zeitskalen, Parameter und Laborabbildungen bleiben heuristisch. Simulationsergebnisse sind weder individuelle Prognosen noch Therapieempfehlungen. Eigene Patientendatensätze und Simulationsinputs dürfen ausschließlich synthetisch sein. Die separat gekennzeichneten Literaturbefunde stammen dagegen aus veröffentlichten klinischen Beobachtungen; es sind keine Individualdaten importiert worden.

## Implementierter Umfang

- Versionierter Swift-Kern mit vier normierten Zuständen: Hepatozyten, Entzündung, aktivierte Sternzellen und fibrotische Matrix. RK4 teilt Schritte an Ausgabe- und Interventionszeitpunkten; Eingabe- und Ressourcenlimits verhindern ungültige Läufe.
- Hypothetische Interventionen und Kontrolllauf mit gleichen Anfangsbedingungen. Lokale Sensitivität, Parameter-Sweeps, deterministische Ensembles und eindimensionale synthetische Gitterkalibrierung sind als Core-API verfügbar. Die Oberfläche zeigt zusätzlich ein Ensemble aus 64 Varianten.
- SwiftUI-Dashboard mit Verlaufs- und Labordiagrammen, Zeitleiste, Szenarioeditor, Parameterinspektor und Modellhinweisen. Numerische Parameter besitzen direkte Zahlenfelder mit Dezimalkomma/-punkt und kontinuierliche Slider. Ungültige Entwürfe ersetzen keinen gültigen Wert und blockieren die Berechnung. Das Leberbild ist eine schematische Grafik, keine anatomische oder räumliche Simulation.
- Eigenständige ALD-Evidenzansicht mit Quellen, Populationen, Zeitbezug, Grenzen und JSON-Export. Der gebündelte Katalog unterscheidet beobachtete Zähler/Nenner, publizierte Ereigniszeitschätzungen und kontinuierliche Messwerte. Deskriptive Wilson-Intervalle entstehen ausschließlich für Rohanteile; möglicherweise überlappende Kohorten werden nicht gepoolt.
- SQLite-Persistenz vollständiger, unveränderlicher Läufe einschließlich Modellversion, Konfiguration und Seed. JSON-Import/-Export für Läufe, CSV-Ergebnisausgabe und Markdown-Forschungsbericht in der Oberfläche.
- Datenstrukturen und JSON-/CSV-Austausch für synthetische Laborwerte, Fibrosebefunde und Ereignisse als Storage-API. Diese Datensatzimporte sind noch kein eigener UI-Arbeitsablauf. Ein CSV-Ergebnisexport rekonstruiert keinen Simulationslauf; dafür dient JSON.
- Gemeinsame Packages für macOS und iOS, macOS-App, iPhone-/iPad-App-Target und CLI für reproduzierbare Integrationsprüfungen.

Das 5.–95.-Perzentil im Ensemble beschreibt die **frei angenommene Parameterstreuung**. Es ist kein klinisches Konfidenz- oder Prognoseintervall. Ein fester Seed reproduziert die Samples; Lauf-UUID und Erstellungszeit bleiben neue Metadaten.

Auch das separat berechnete 95-%-Wilson-Intervall einer Studienhäufigkeit ist kein persönliches Prognoseintervall. Es berücksichtigt keine variable Nachbeobachtung, Zensierung oder konkurrierenden Ereignisse. Ein publizierter Rekompensationsanteil kalibriert keine ODE-Rate. Die vollständige Einordnung steht in [ALD-Evidenz und Kalibrierungsplan](Docs/08-ALD-Evidence.md).

## Voraussetzungen

Swift 6 und vollständiges Xcode mit macOS- und iOS-SDK; Deployment-Ziele: macOS 14 und iOS 17. Der aktuelle Stand einschließlich ALD-/Zahlenfeld-Erweiterung wurde lokal mit **Xcode 27 und Swift 6.4** erfolgreich für macOS und den iOS-Simulator gebaut. Einzelheiten stehen im [Prüfbericht](Docs/07-VerificationReport.md). Die ältesten unterstützten Betriebssystemversionen wurden nicht auf echten Geräten geprüft.

Keine externen Swift-Package-Abhängigkeiten. SQLite, SwiftUI und Swift Charts stammen aus dem Apple-SDK. Python, Rust, C++ und Metal sind für diesen Kern nicht erforderlich; eine Beschleunigung ist nicht durch Benchmarks begründet.

Alle folgenden Befehle im Projektverzeichnis ausführen.

## Prüfen und macOS-App starten

```sh
./Scripts/verify.sh
./Scripts/build-macos.sh
```

Das Build-Skript erstellt standardmäßig eine native Debug-App für Apple Silicon und gibt den `.app`-Pfad aus. Diesen Pfad im Finder öffnen oder an `open` übergeben. Der lokale Build ersetzt keine Vertriebsignatur, Notarisierung oder App-Store-Freigabe.

Die Skripte verwenden temporäre Build-Verzeichnisse unter `/tmp`. Bei diesem Projektstand haben macOS-Dateianbieter im Documents-Verzeichnis Finder-Metadaten an erzeugte Test-Bundles angehängt; dadurch scheiterte `codesign` mit „resource fork, Finder information, or similar detritus not allowed“. Ein Build außerhalb dieses synchronisierten Verzeichnisses vermeidet den beobachteten Fehler.

Alternativ das gemeinsame Xcode-Projekt öffnen:

```sh
open Apps/HepatoSim.xcodeproj
```

Scheme **HepatoSim-macOS** auswählen und starten. Für ein eigenes Derived-Data-Verzeichnis ebenfalls einen lokalen Pfad außerhalb synchronisierter Documents-Ordner verwenden.

## iOS

Scheme **HepatoSim-iOS** verwendet dieselben Core-, Storage- und UI-Packages. Ein Simulator-Build ist möglich:

```sh
xcodebuild -project Apps/HepatoSim.xcodeproj \
  -scheme HepatoSim-iOS \
  -sdk iphonesimulator \
  -destination 'generic/platform=iOS Simulator' \
  -derivedDataPath /tmp/hepatosim-xcode-iOS \
  CODE_SIGNING_ALLOWED=NO build
```

Der iOS-Simulator-Build der aktuellen Erweiterung ist erfolgreich; die App wurde installiert und gestartet. Ein visueller iPhone-Durchlauf und Tests auf einem echten Gerät stehen aus. Für Geräteinstallation in Xcode ein eigenes Signing-Team konfigurieren. Build und Prozessstart allein belegen keine vollständige Prüfung von Bedienung, VoiceOver, Speicherverhalten oder Hintergrundwechseln.

## Bedienung und lokale Daten

Beim ersten Start wird ein synthetisches Beispiel samt Kontrolle berechnet und gespeichert. Im Szenarioeditor Faktoren direkt als Zahl eingeben oder per Slider ändern und **Berechnen & speichern** wählen. **Tab** wechselt zum nächsten Zahlenfeld, **Shift-Tab** zum vorherigen; im Parameterinspektor wird das fokussierte Feld automatisch sichtbar gescrollt. Diese Wege wurden in der nativen Mac-App geprüft. Änderungen an Parametern beeinflussen erst den nächsten Lauf. Die Zeitleiste zeigt den nächstgelegenen gespeicherten Zeitpunkt. Gespeicherte Läufe lassen sich über die Seitenleiste wieder öffnen; eine gespeicherte Kontrolle wird bei übereinstimmender Konfiguration und Modellversion zugeordnet.

**ALD: Wegfall der Schädigung** setzt den modellierten Schädigungsfaktor ab dem angezeigten Interventionsbeginn auf null. Das ist eine explizite Modellhypothese, kein aus den Studien geschätzter Abstinenzeffekt. Regeneration und Matrixabbau erhalten dadurch keine klinisch belegten Raten. Die Studienbefunde stehen unter **ALD-Evidenz**, getrennt von den Simulationsdiagrammen.

Die App ermittelt das Benutzerverzeichnis mit `FileManager.applicationSupportDirectory` und speichert darunter `HepatoSimResearch/research.sqlite`. Bei der sandboxierten App liegt dieses Verzeichnis im jeweiligen App-Container; beim ungekapselten Swift-Package-Executable kann der Pfad abweichen. Die CLI verwendet ihr ausdrücklich übergebenes Ausgabeverzeichnis. Bestehende Lauf-UUIDs werden nicht überschrieben.

macOS und iOS teilen **Schema und Code, keine automatisch synchronisierte Datenbank**. Läufe können als JSON exportiert und auf dem anderen Gerät importiert werden. Import akzeptiert nur unterstützte Schema-/Modellversionen und prüft die numerische Konsistenz. Dies bestätigt keine authentifizierte Herkunft oder medizinische Richtigkeit.

SQLite ist nicht durch eine eigene Datenbankverschlüsselung geschützt. Dateirechte, macOS-App-Sandbox und iOS-Dateischutz begrenzen den Zugriff; sie erlauben keinen Realdatenbetrieb. Keine Telemetrie und keine verbundenen externen KI-Dienste im Slice.

## Dokumentation und Architekturauftrag

Der neue [Referenz-Benchmark zu Bouguéon 2024](Research/Reference/README.md) führt das veröffentlichte stochastische Kappa-Modell außerhalb der App aus. Der [wissenschaftliche Audit](Docs/09-DemonstrationModelAudit.md) und der [Forschungsbericht](Docs/10-ReferenceBenchmark.md) trennen Software-Verifikation, Publikationsreproduktion und eine noch ausstehende unabhängige biologische Prüfung. Das Referenzsystem betrifft Maus-/CCl₄-Fibrose und ist kein kalibriertes Modell menschlicher ALD. Die Swift-Demonstration bleibt erhalten und wird nicht als Kollagen-Messmodell gewertet.

| Angefordertes Ergebnis | Dokument |
|---|---|
| 1. Architekturübersicht | [Architektur](Docs/01-Architecture.md#umfang-und-abhängigkeiten) |
| 2. Projekt- und Verzeichnisstruktur | [Projektstruktur](Docs/01-Architecture.md#projektstruktur) |
| 3. Technologiebewertung | [Technologiebewertung](Docs/01-Architecture.md#technologiebewertung) |
| 4. Wissenschaftliches Modellkonzept | [Gleichungen, Einheiten, Quellen und Grenzen](Docs/02-ScientificModel.md) |
| 5. Datenbankschema | [Datenarchitektur und Austauschformate](Docs/03-DataSchema.md) |
| 6. Plugin-Spezifikation | [Plugin- und Sicherheitskonzept](Docs/04-PluginSpecification.md) |
| 7. Test- und Validierungsstrategie | [Verifikation, Forschungsvalidierung und regulatorische Grenzen](Docs/05-ValidationStrategy.md) |
| 8. Implementierungsplan mit Meilensteinen | [Phasen und Abnahmekriterien](Docs/06-Milestones.md) |

`Sources/HepatoCore` enthält Modell, Analysen und den typisierten Evidenzkatalog; `Sources/HepatoStorage` Persistenz und Austausch, `Sources/HepatoUI` die gemeinsame Oberfläche. `Tests` prüft unter anderem analytische Grenzfälle, RK4-Schrittverfeinerung, numerische Regression, Interventionsgrenzen, Reproduzierbarkeit, synthetische Kalibrierung, Daten-Roundtrips, Wilson-Grenzfälle, Evidenztypen und Zahleneingaben. Diese Prüfungen belegen Softwareverhalten, keine biologische Vorhersagegüte.

## Bewusste Grenzen dieses Meilensteins

Plugin-Manifest, Signierung, Isolation, Berechtigungen, Audit und Updates sind **spezifiziert, nicht als vollständiger Plugin-Manager implementiert**. iOS lädt keinen beliebigen nativen Plugin-Code nach. Die Erweiterungsansicht erklärt den geplanten Ausbau.

Child-Pugh/MELD, FHIR, externe KI-Provider, Forschungsserver, Cloud-Synchronisierung, Verarbeitung individueller realer Patientendaten und klinische Validierung sind nicht implementiert. Die KI-Schnittstelle trennt Hypothesen strukturell von Simulationsergebnissen; sie erzeugt selbst keine Antworten. Das Modell sagt keine Dekompensation, Komplikationen, Transplantationspriorität oder Überlebenswahrscheinlichkeit voraus. Weitere Phasen benötigen die in den Dokumenten genannten fachlichen und technischen Nachweise.
## Lokales App-Paket und Prüfbericht

Neben diesem Projektordner liegen `Start-HepatoSim.command` und `HepatoSimResearch-macOS.zip`. Beide Dateien zusammen belassen. Ein Doppelklick auf das Startskript im Finder öffnet das vorgebaute lokale Mac-App-Paket ohne erneuten Build. Die App wird nach temporärer Extraktion auf ihre Ad-hoc-Signatur geprüft. Dies ist ein lokaler Entwicklungsbuild, kein notarisiertes Distributionsprodukt.

Der [technische Prüfbericht](Docs/07-VerificationReport.md) dokumentiert **52 erfolgreiche Tests ohne Fehler**, erfolgreiche aktuelle macOS-/iOS-Simulator-Builds sowie die native Prüfung von Zahleneingaben, Tab/Shift-Tab, automatischem Scrollen und Berechnungssperre bei ungültigen Werten. Kontinuierliche Regler vermeiden die aufwendige Erzeugung vieler Schrittmarkierungen, die den untersuchten UI-Stillstand auslöste. Das finale Mac-ZIP wurde neu gepackt, über das Startskript geöffnet und erfolgreich auf seine Ad-hoc-Signatur geprüft; gespeicherte Läufe und alle fünf Evidenzquellen waren nach dem Neustart verfügbar. [Synthetische Beispieldateien](Examples/README.md) liegen in `Examples/`.
