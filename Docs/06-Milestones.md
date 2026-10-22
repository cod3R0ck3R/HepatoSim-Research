# Implementierungsplan und überprüfbare Meilensteine

Stand: 22.10.2026. Der Auftrag wird in ausführbare Schritte mit dokumentierter Abnahme geteilt. Der aktuelle Lieferumfang ist Architektur plus erster Vertical Slice. Die folgenden Phasen sind kein Versprechen, dass sämtliche Funktionen bereits vorhanden oder medizinisch validiert sind. Der tatsächliche Stand wird im README/Testbericht festgehalten.

## Phase 1 — Wissenschaftliche Machbarkeit und Architektur

**Ergebnis:** Architektur/Verzeichnisstruktur, Technologiebewertung, Gleichungen mit Parametern/Einheiten, Datenbankschema, Pluginentwurf, Teststrategie und dieser Plan.

**Abnahme:** Jeder Modellterm ist als etablierter Mechanismus, experimentelle Annahme oder freie Parametrisierung eingeordnet. Quellen sind auffindbar. Kein frei gewählter Zahlenwert erhält durch Literaturverweis einen behaupteten Validierungsstatus. Native Distribution, Datenschutz- und Modellgrenzen sind dokumentiert. Ein enger Rechen-/Datenfluss ist als nächster Schritt implementierbar.

**Offene Forschung:** Modellidentifizierbarkeit und reale Zeitkonstanten; Übertragbarkeit zwischen Ätiologien; Zusammenhang von Fibroseproxy, Gefäßstruktur, portalem Widerstand und gemessenen Laborwerten. Das erste Modell umfasst keine vollständige Leberphysiologie.

## Phase 2 — Reproduzierbarer Simulationskern und Daten

**Erster Slice:** Synthetischer Anfangszustand, versionierter Swift-Kern, zeitliche Integration, Kontroll-/Interventionsvergleich, SQLite-Laufarchiv, JSON-/CSV-Austausch und ausführbare CLI. Ein einfacher lokaler Sensitivitäts-/Sweep-/Kalibrierpfad darf nur als Implementierung gelten, wenn er tatsächlich vorhanden und getestet ist.

**Abnahme:** Clean Build und Tests laufen. Die CLI berechnet, speichert und lädt denselben vollständigen Lauf wieder. Gleichungen, Eingaben, Solverkonfiguration, Seed und Versionen sind rekonstruierbar. Ungültige Eingaben scheitern kontrolliert. Schrittverfeinerung und analytische Sonderfälle bestehen. Numerische Grenzen stehen im Testbericht.

**Vervollständigung:** Persistente Ensembles mit explizitem Unsicherheitsmodell, robuste Kalibrierung mit Identifizierbarkeitsdiagnostik, vollständige medizinische Datentypen und definierte Scorevarianten. Erst danach sind Aussagen über umfassende Phase-2-Abdeckung zulässig.

## Phase 3 — Native macOS-Forschungsoberfläche

**Erster Slice:** Dashboard, Parameter-/Szenarioeditor, Kontrolle und Intervention in Zeitreihendiagrammen, lokale Speicherung/Wiederladen, synthetische Laborproxies und ständig sichtbarer Forschungsstatus. Eine vereinfachte Leberdarstellung illustriert Zustände; sie ist keine patientenspezifische Anatomie.

**Abnahme:** Gepackte App startet auf einer unterstützten macOS-Version. Ein vollständiger Ablauf von Parameterwahl bis Wiederladen funktioniert ohne CLI. Fehler werden angezeigt. Hauptthread bleibt bedienbar. Diagramme besitzen Einheiten, Legende und zugängliche Textalternative; Farbwahrnehmung ist nicht der einzige Unterschied zwischen Szenarien.

**Vervollständigung:** Vergleich gespeicherter Läufe, Unsicherheitsband mit Methodenerklärung, interaktive Zeitselektion, Modell-/Quellenansicht, exportierbarer Forschungsbericht und UI-Tests. Signatur, Sandbox und Notarisierung werden am verteilbaren Artefakt geprüft. Ein lokaler Debug-Build erfüllt diese Vertriebsabnahme nicht automatisch.

## Phase 4 — Native iPhone-App

**Ergebnis:** iOS-App-Target mit denselben Core-/Storage-Packages und angepasster Navigation. Gemeinsame Datenbasis bedeutet zunächst identisches Schema und expliziten Dateiaustausch. Automatische Synchronisation über Geräte ist ein eigener, noch nicht implementierter Daten-/Konfliktpfad.

**Abnahme:** iOS-Simulatorbuild und echtes Geräteprofil. Derselbe Eingabevektor ergibt innerhalb festgelegter Toleranz dieselben Kernresultate auf macOS/iOS. Import/Export zwischen Geräten erhält Provenienz und Einheiten. Speicher-/Laufzeitlimits, Background-Unterbrechung, Dateischutz, Dynamic Type, VoiceOver und schmale Displays werden geprüft. Keine UI darf beliebigen nativen Code herunterladen oder ausführen.

**Abhängigkeiten:** Vollständiges Xcode mit iOS-SDK, Simulator bzw. Testgerät und bei Geräteverteilung passende Signierung. Ein Swift-Package-Build für macOS beweist keine iOS-Ausführbarkeit.

## Phase 5 — SDK und sicherer Plugin-Manager

**5a — Verträge:** Versioniertes `HepatoPluginSDK`, maschinenlesbares Manifest, SemVer-/Abhängigkeitsresolver, explizite Grants, Registry, Lifecycle und Contract-Tests. Zuerst ausschließlich gebündelte Implementierungen.

**5b — Installation und Updates:** Signierter Katalog und Pakete, Trust Store, Staging, atomare Installation/Deinstallation, Updateprüfung, Rollback, Audit und unabhängige Sicherheitsprüfung. Alle Negativfälle aus `04-PluginSpecification.md` müssen bestehen.

**5c — Prozessgrenzen:** Gebündelter macOS-XPC-Dienst mit minimalen Entitlements und tatsächlich geprüfter Sandbox; separat autorisierte Serveradapter mit begrenzten Jobs, Mandantentrennung und Exportkontrolle. iOS nutzt eingebaute Module oder Server. Kein allgemeiner Runtime-Loader.

**Abnahme:** Ein Modell-, ein Visualisierungs- und ein Datenadapter-Referenzplugin durchlaufen Installation/Registrierung, Aktivierung, kontrolliertes Scheitern, Update und Entfernung. Fremde Prozesse erhalten keinen impliziten Hostzugriff. Quarantäne, Rechtewiderruf und Herkunftsprüfung sind nicht nur UI-Elemente. Ergebnisprovenienz bleibt nach Entfernung eines Plugins lesbar.

## Phase 6 — Erweiterung und wissenschaftliche Validierungsplanung

**6a — Mechanismen:** Neue Modelle für Gefäßwiderstand, Synthesefunktion, Stoffwechsel und Ereignisse nur nach Definition beobachtbarer Größen. Kompensierte/dekompensierte Zustände dürfen nicht allein aus einem willkürlichen Fibroseschwellwert entstehen. Dekompensationsereignisse benötigen eigene, belegte Definitionen und Daten.

**6b — Daten und Evidenz:** Genehmigter Datenzugang, Qualitätsprüfung, Messmodell, externe Vergleichsdaten, präregistrierte Ziele, Baselines und unabhängige Auswertung. Ergebnisse können unzureichende Modellgüte zeigen; das ist ein zulässiges Forschungsergebnis.

**6c — Interoperabilität:** FHIR-Profile für Patient-/ResearchSubject-Kontext, Observation, DiagnosticReport, Provenance und erforderliche klinische Ereignisse. FHIR-Version, Profil, Terminologie, Einheiten (UCUM), Identitätsabgleich, Authentifizierung und Testserver vor Umsetzung festlegen. Eine JSON-Datei ist kein FHIR-Nachweis.

**6d — KI:** Ein konkret ausgewählter Provider implementiert die austauschbare Schnittstelle. Zunächst nur synthetische/öffentlich verfügbare, ausdrücklich freigegebene Inhalte. Quellenprüfung, Kennzeichnung von Hypothesen und separate Speicher-/UI-Pfade sind Abnahmevoraussetzungen; keine Modellwerte werden durch KI-Text überschrieben.

**6e — Leistungsoptimierung:** Benchmark vor Python-/Rust-/C++-Brücke oder Metal. Messen: Samplezahl, Ensemblegröße, wall-clock-Zeit, Speicher, Energie und numerische Abweichung. Kleine Vier-Zustandsmodelle bleiben auf der CPU, solange kein gemessener Vorteil besteht.

## Liefer- und Änderungsregeln

Jeder Meilenstein liefert ausführbaren Code, reproduzierbaren Testaufruf, bekannte Grenzen und eine kurze Änderungsnotiz. Wissenschaftliche Modelländerungen bekommen eine neue Modellversion; Ergebnisdateien speichern ihre ursprüngliche Version. Datenbankmigrationen besitzen Rücksicherung und Fehlerpfad. Fremdabhängigkeiten benötigen dokumentierten Zweck, Lizenzprüfung und Versionsbindung.

Kein Meilenstein wird wegen Zeitdruck als bestanden markiert. Fehlendes SDK, fehlende Signierung, nicht ausgeführte Geräte-/Accessibilitytests und nicht vorhandene Validierungsdaten werden ausdrücklich benannt. Ein abgeschlossener Softwaremeilenstein ist kein Nachweis medizinischer Wirksamkeit oder regulatorischer Konformität.
