# Plugin-Spezifikation — Entwurf 0.1

Stand: 22.10.2026. Diese Spezifikation beschreibt Phase 5. Der erste Vertical Slice besitzt **keinen installierbaren Plugin-Manager**, keinen Signaturprüfer und keine isolierte Plugin-Laufzeit. Eine angezeigte Komponentenliste wäre kein Nachweis dieser Funktionen. Alle folgenden Anforderungen sind erst nach ihren Abnahmetests als implementiert zu kennzeichnen.

## Vertriebs- und Ausführungsmodell

| Ziel | Zugelassener Weg | Sicherheitsgrenze |
|---|---|---|
| iOS/iPadOS | Mit der App kompilierte, registrierte native Implementierung; Update über neue App-Version | Läuft innerhalb der App-Sandbox; kein eigener Prozessschutz zwischen eingebauten Modulen |
| macOS, Mac App Store | Mit der App ausgelieferte Implementierung; für isolierte Algorithmen vorab eingebetteter und signierter XPC-Dienst | Eigener Sandbox-Prozess und enges IPC-Protokoll; Code-Updates mit App-Update |
| macOS, spätere direkte Distribution | Gesondert geprüftes Developer-ID-signiertes und notarisiertes Host-/Dienstpaket | Kein `dlopen` fremder Bibliotheken in der UI; Vertriebsweg und Installation separat freizugeben |
| Server auf allen Plattformen | Explizit freigegebene, versionierte Operation über HTTPS | Fremder Code ausschließlich serverseitig in isolierten Jobs; Datenexport braucht separate Berechtigung |
| Daten-/Visualisierungspaket | Validierte Parameter, Literaturmetadaten, begrenzte deklarative Diagrammbeschreibung | Kein JavaScript, Python, Shader, Ausdrucksevaluator, Shellkommando oder andere ausführbare Nutzlast |

Apple beschränkt nachgeladene ausführbare Funktionen in Richtlinie 2.5.2. Richtlinie 4.7 regelt bestimmte zusätzliche Softwareangebote, ist aber keine allgemeine Erlaubnis für heruntergeladenen nativen iOS-Code. HepatoSim setzt diese Ausnahme nicht voraus. Auch Mac-App-Store-Updates unterliegen dem vorgesehenen Vertriebsweg. Eine Signatur allein garantiert keine App-Store-Zulässigkeit. Vor jeder Veröffentlichung sind die dann geltenden Regeln erneut zu prüfen. [Apple App Review Guidelines, 2.4.5, 2.5.2, 4.7](https://developer.apple.com/app-store/review/guidelines/)

XPC ist die geplante macOS-Prozessgrenze. Apple beschreibt XPC-Dienste als Hilfsprozesse; ihre Sandbox und Entitlements sind explizit zu konfigurieren. Ein Swift-Protokoll oder ein Swift-`actor` isoliert keinen bösartigen Code. [Apple XPC](https://developer.apple.com/documentation/xpc), [Apple: Creating XPC Services](https://developer.apple.com/library/archive/documentation/MacOSX/Conceptual/BPSystemStartup/Chapters/CreatingXPCServices.html)

## SDK und Erweiterungspunkte

Das geplante Package `HepatoPluginSDK` enthält ausschließlich serialisierbare Verträge, Fähigkeitsbeschreibungen und Fehlercodes. Kernmodell, Host-API und Plugin erhalten getrennte Versionskennungen. Keine Abhängigkeit des biologischen Kerns vom Plugin-Manager.

| Typ | Eingabe | Ausgabe | Unverzichtbare Bedingung |
|---|---|---|---|
| `simulationModel` | Zustand, Parameter, Szenario, Solverkonfiguration, Seed | Zeitreihe, Diagnostik, Modellversion, Quellen | Eigene Gleichungen und Einheiten; niemals alte Läufe still überschreiben |
| `researchAlgorithm` | Ausgewählte unveränderliche Läufe | Sensitivität, Kalibrierung oder Ensemble | Methode, Stichprobe, Seed und Grenzen im Ergebnis |
| `dataIO` | Explizit ausgewählte Bytes bzw. Datensätze | Validierte Datensätze bzw. Exportbytes | Größen-, Schema-, Einheiten- und Provenienzprüfung |
| `medicalAdapter` | Freigegebene externe Datenrepräsentation | Fachliche Beobachtungen mit Originaleinheit | Kein automatisches Zusammenführen von Identitäten |
| `visualization` | Nur angeforderte Ergebnisfelder | Deklarative Diagrammbeschreibung | Host rendert; Achsen, Einheit und Unsicherheitsart verpflichtend |
| `researchReport` | Ausgewählte Läufe und Quellen | Bericht mit Modell- und Softwareversion | Warnstatus und hypothetische Therapieeffekte bleiben enthalten |
| `aiAnalysis` | Freigegebene Forschungsfrage und expliziter Kontext | Separates Hypothesen-/Literaturartefakt | Kein Schreibzugriff auf mathematische Simulationsergebnisse |

Jeder Aufruf enthält `requestID`, `contractVersion`, `pluginID`, `pluginVersion`, Deadline, Ressourcenlimit und einen Snapshot erlaubter Eingaben. Antworten tragen dieselbe Request-ID, Datenformatversion, Provenienz und begrenzte Diagnostik. Unbekannte Felder werden nur zugelassen, wenn das jeweilige Schema sie ausdrücklich erlaubt. Unbekannte Berechtigungen, Typen und API-Hauptversionen werden abgelehnt.

Native Swift-APIs sind keine dauerhaft stabile Binärschnittstelle für fremde Module. Eingebaute Module werden gemeinsam gebaut; XPC und Server verwenden versionierte, längenbegrenzte Nachrichten. Laufende Jobs sind abbrechbar und besitzen einen definierten Fehler bei Dienstabbruch. Ein fehlendes Plugin verhindert das Anzeigen gespeicherter Ergebnisse nicht.

## Manifest

Beispiel für ein **zukünftiges**, eingebautes Modell. Null-Hash und fehlende Signatur machen dieses Dokument ausdrücklich nicht installierbar. `entryPoint` verweist auf einen im Host vorhandenen Registry-Eintrag, niemals auf einen Dateipfad oder frei wählbaren Klassennamen.

```json
{
  "manifestVersion": 1,
  "id": "org.hepatosim.model.example",
  "name": "Synthetisches Lebermodell",
  "version": "1.0.0",
  "type": "simulationModel",
  "execution": "bundled",
  "entryPoint": "registered.synthetic-liver-v1",
  "hostAPI": {"minimum": "1.0.0", "maximumExclusive": "2.0.0"},
  "platforms": [{"os": "macOS", "minimum": "14.0"}, {"os": "iOS", "minimum": "17.0"}],
  "dependencies": [],
  "permissions": ["simulation.readSelected", "simulation.compute"],
  "model": {"id": "synthetic-liver", "version": "1.0.0", "validation": "unvalidated"},
  "artifacts": [{"path": "model-description.json", "sha256": "0000000000000000000000000000000000000000000000000000000000000000"}],
  "publisherKeyID": "hepatosim-research-release-1",
  "license": "TO-BE-SELECTED",
  "sourceURLs": ["https://example.org/research-model"]
}
```

Schema: UTF-8, höchstens 64 KiB, keine doppelten JSON-Schlüssel, keine NaN/Infinity-Werte, begrenzte Listen und Textlängen. Plugin-IDs bleiben publishergebunden. `manifestVersion` ist eine Schema-, keine Pluginversion. Vor Phase 5 wird eine maschinenlesbare JSON-Schema-Datei mit negativen Testvektoren Bestandteil des SDK.

Versionsordnung folgt [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html). Abhängigkeiten enthalten `id`, `minimum` und `maximumExclusive`; keine frei interpretierbaren npm-Ausdrücke. Vorabversionen benötigen explizite Freigabe. Build-Metadaten beeinflussen die Reihenfolge nicht. Für `0.x` werden kompatible Minor-Versionen ausdrücklich begrenzt. Der Resolver erzeugt einen azyklischen, vollständig gepinnten Lockgraph mit Hash je Paket; er lehnt Konflikte und Zyklen vor Änderungen ab.

## Signatur und Herkunft

1. Ein signierter Katalog enthält Paket-ID, Version, SHA-256 des vollständigen Archivs, Publisher-Schlüsselkennung, monoton steigende Sequenz und Ablaufzeit. HTTPS schützt den Transport; es ersetzt die Signatur nicht.
2. Die Archivsignatur liegt außerhalb des Archivs. Ed25519 signiert eine feste Protokollkennung plus Archivhash. Vertrauensanker stammen aus der App oder einem separat bestätigten Administrationsvorgang, niemals allein aus dem zu prüfenden Paket. [Apple CryptoKit: Curve25519.Signing](https://developer.apple.com/documentation/cryptokit/curve25519/signing)
3. Vor dem Entpacken gelten Größen-/Dateizahllimits. Nach der Hash- und Signaturprüfung erfolgt das Entpacken in ein privates Staging-Verzeichnis. Absolute Pfade, `..`, Symlinks, Hardlinks, Dateinamenkollisionen und übermäßige Expansion werden abgelehnt. Manifestdateien müssen exakt den signierten Inhaltshashes entsprechen.
4. Native macOS-Artefakte benötigen zusätzlich Apples Codesign-Prüfung, erwartete Team-/Bundle-Identität und die für den Vertriebsweg erforderliche Notarisierung. Eine gültige Paketsignatur umgeht keine Betriebssystemkontrolle. [Apple Platform Security: App code signing in macOS](https://support.apple.com/guide/security/app-code-signing-process-sec3ad8e6e53/web)
5. Schlüsselrotation benötigt eine separat vertrauenswürdige Freigabe; widerrufene Schlüssel sperren neue Jobs. Offlinebetrieb erlaubt nur bereits vertrauenswürdig verifizierte Versionen. Katalogalter und fehlende Widerrufsaktualität sind sichtbar. Herabstufungen brauchen einen expliziten, protokollierten Wiederherstellungsvorgang.

Hash- und Signaturprüfung beziehen sich auf die Bytes, die anschließend unveränderlich installiert und ausgeführt werden. Staging-Dateien dürfen zwischen Prüfung und Aktivierung nicht austauschbar sein. Wissenschaftliche Richtigkeit lässt sich nicht aus einer gültigen Signatur ableiten.

## Lebenszyklus und Updates

Zustände: `absent → staged → verified → installedDisabled → enabled`; zusätzliche Zustände `quarantined`, `updateStaged`, `failed`. Für gebündelte Erweiterungen bedeutet Installation das Registrieren vorhandener Komponenten, nicht den Download von Code.

Installation prüft in dieser Reihenfolge Herkunft, Manifest, Plattform/API, Abhängigkeitsgraph, Ressourcenbedarf und Berechtigungen. Erst danach erfolgen atomare Registry-Transaktion und Aktivierung. Fehler lassen die vorherige Version vollständig nutzbar. Aktivierung startet keine Berechnung und exportiert keine Daten.

Deaktivierung verhindert neue Jobs, widerruft Sitzungstokens und beendet oder kontrolliert beendet laufende Jobs; unvollständige Resultate erhalten keinen Erfolgsstatus. Abhängige Plugins werden sichtbar gesperrt. Deinstallation prüft Rückwärtsabhängigkeiten, entfernt Laufzeit und privaten Cache, erhält aber unveränderliche Laufprovenienz und bereits gespeicherte Ergebnisse. Fachliche Daten werden nur in einem getrennten, bestätigten Löschvorgang entfernt.

Updates werden signiert im Staging geprüft, einschließlich Migrations- und Regressionstests. Erweiterte Berechtigungen bedürfen neuer Zustimmung. Läufe bleiben an die bisherige Modell-/Pluginversion gebunden. Alte Ergebnisse werden nie automatisch neu berechnet. Nach fehlgeschlagenem Update erfolgt atomarer Rückwechsel; irreversible Datenmigrationen sind in Pluginupdates unzulässig. App-Store-Codeupdates erfolgen ausschließlich über App-Versionen.

## Berechtigungen und tatsächliche Durchsetzung

Standard ist verweigert. Grants sind an Plugin-ID, geprüften Paketdigest, Datenumfang und Sitzung/Zweck gebunden. Eine Manifestdeklaration ist ein Antrag, keine Erlaubnis. Daten werden als Kopie bzw. kurzlebige Fähigkeit übergeben; Plugins erhalten keinen SQLite-Pfad, Datenbankschlüssel oder globalen Dateizugriff.

| Berechtigung | Begrenzung |
|---|---|
| `simulation.readSelected` | Nur explizit ausgewählte Lauf-IDs und Felder |
| `simulation.compute` | CPU-Zeit, Speicher, maximale Samples, Deadline |
| `syntheticData.readSelected` | Ausschließlich gewählte synthetische Datensätze |
| `files.readSelected` / `files.writeSelected` | Benutzergewählte Datei; begrenztes Format; kein Verzeichnisvollzugriff |
| `network.callApprovedService` | Konkrete HTTPS-Origin und Operation; keine Redirects zu fremden Origins |
| `researchData.exportSelected` | Separater, sichtbarer Exportzweck; im Slice nicht verfügbar |

Gebündelte In-Process-Module werden als vertrauenswürdiger Hostcode behandelt: granulare API-Grants bieten dort keine harte Grenze gegen absichtlich bösartigen Code. Fremde native Implementierungen gehören in den XPC-/Serverweg. XPC prüft gegenseitig die erwartete Signaturidentität, validiert jedes Nachrichtenfeld und erhält minimale Entitlements. Sandbox-Deny-Tests müssen Zugriff auf Netzwerk, Schlüsselbund und fremde Dateien tatsächlich scheitern lassen.

Serverjobs laufen mit nicht privilegierter Identität, schreibgeschütztem Image, CPU-/RAM-/Laufzeitlimits, temporärem Dateisystem und standardmäßig gesperrtem ausgehenden Netzwerk. Container allein werden nicht als ausreichende Grenze für beliebigen feindlichen Code betrachtet; für nicht vertrauenswürdige Drittanbieterjobs ist eine stärkere VM-Grenze vorgesehen. Authentifizierung, Mandantentrennung, Datenlöschung und Protokollierung benötigen eigene Integrationstests. Endpunkt- und DNS-Prüfung verhindert SSRF auf lokale/private Netze.

## Audit und Bedrohungsmodell

Auditereignisse enthalten UTC-Zeit, monotone lokale Sequenz, Akteur, Aktion, Plugin-ID/-Version/-Digest, Grantänderung, Job-ID und Ergebniscode. Keine Patientennamen, Rohdaten, Prompts oder Geheimnisse. Eine Hashkette macht nachträgliche Manipulationen erkennbar, verhindert aber keine Änderung durch einen Administrator mit vollständigem Hostzugriff. Stärkere Beweiskraft benötigt externen, zugriffsgeschützten Anker und Aufbewahrungskonzept.

| Angriff / Fehler | Entwurfsmaßnahme | Verbleibende Grenze |
|---|---|---|
| Manipuliertes Archiv, Registry-Kompromittierung | Gepinnter Vertrauensanker, Digest, Signatur, Widerruf | Kompromittierter legitimer Schlüssel benötigt Incident Response |
| Pfadtraversal, Zip-Bomb, TOCTOU | Private Stagingdateien, Limits, atomare unveränderliche Installation | Plattformintegration muss getestet werden |
| Datenabfluss | Kein Default-Netzwerk, Auswahlscopes, Hostbroker | Vertrauenswürdiger In-Process-Code besitzt Hostrechte |
| Dienstabsturz, Endlosschleife | Prozessgrenze, Timeout, Abbruch, Joblimits | Eine Sandbox ist kein Beweis vollständiger Fehlerfreiheit |
| Unbemerkte Modelländerung | Pinned Version/Digest, neue Lauf-ID, Regression | Ein stabil falsches Modell bleibt falsch |
| Falsche wissenschaftliche Aussagen | Unvalidiert-Status, Quellen, Fachreview | Signaturen und Tests sind keine medizinische Validierung |

## Verbindliche Abnahme für Phase 5

- Manipuliertes Byte, unbekannter/widerrufener Schlüssel, abgelaufener Katalog, falsches Team und Downgrade werden abgelehnt; kein Code startet.
- Fehlende Abhängigkeit, Zyklus, inkompatible Host-API, unzulässige Plattform und unbekannte Berechtigung ändern keine installierte Version.
- `../../`-Eintrag, absolute Pfade, Symlink und Zip-Bomb verlassen das Stagingverzeichnis nicht und erzeugen einen protokollierten Fehler.
- Ein Testplugin scheitert nachweislich an nicht gewährten Datei-/Netzwerkzugriffen; der Host bleibt nach Absturz und Timeout bedienbar.
- Installations-/Updateabbruch an jedem Transaktionsschritt bewahrt vorherigen Zustand; Deinstallation erhält Forschungsresultate.
- Grantwiderruf wirkt auf laufende Sitzungen; Rechteausweitung bei Update aktiviert sich nicht automatisch.
- iOS-Artefaktprüfung findet keinen dynamischen Downloader/Loader für nativen Fremdcode; alle Entry-Points stammen aus der Build-Registry.
- Serverjobs zeigen Mandantentrennung, Datenlöschung, Größen-/Laufzeitgrenzen und überprüfbare Auditereignisse.
- Ein Modell- und ein Visualisierungsplugin durchlaufen SDK-Vertragstests samt reproduzierbarer Ergebnisse. Die dokumentierte Bedrohungsanalyse erhält unabhängiges Review.
