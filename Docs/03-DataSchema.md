# Datenarchitektur und Austauschformate

Stand: 22.10.2026. Status: implementierter Forschungsprototyp, ausschließlich synthetische Daten.

## Persistenzschema 1

`RunStore` kapselt SQLite als Swift Actor. Jede Änderung erfolgt in einer Transaktion; ein Fehler verwirft die gesamte Änderung. Die Dateidatenbank besitzt eine Tabelle:

```sql
CREATE TABLE runs (
  id TEXT PRIMARY KEY NOT NULL,
  created_at REAL NOT NULL,
  model_version TEXT NOT NULL,
  payload BLOB NOT NULL
);
```

`payload` ist ein validiertes JSON-Austauschobjekt mit `schemaVersion = 1`, `dataKind = "synthetic-research"` und vollständigem `SimulationRun`. Der Lauf erhält UUID, UTC-Erstellungszeit, Modellversion, Ausgangszustand, Parameter, Intervention, Seed, Integrations- und Abtastschritt sowie alle Simulationspunkte. Die JSON-Datumsdarstellung nutzt Foundations Referenzzeit (Sekunden seit 01.01.2001 00:00:00 UTC), um `Date` ohne zusätzliche Rundung zu erhalten; `Double` bleibt in voller JSON-Genauigkeit erhalten. Die separaten Indexspalten werden beim Lesen mit dem Payload verglichen. Ein Lauf ist unveränderlich: bestehende UUIDs werden zurückgewiesen, niemals überschrieben. Löschen erfolgt nur über eine explizite UUID.

`PRAGMA user_version = 1` identifiziert das SQLite-Schema, unabhängig von Modell- und JSON-Version. Neue leere Datenbanken erhalten Schema 1 atomar. Fremde nichtleere Datenbanken mit Version 0 und unbekannte zukünftige Versionen werden abgelehnt. Weitere Migrationen benötigen expliziten Code und Tests; derzeit gibt es keine automatische Konvertierung fremder Daten.

Ein neu erstelltes privates Verzeichnis erhält Modus `0700`, die Datenbank `0600`. Ein vorhandenes Verzeichnis mit Gruppen- oder Fremdzugriff wird ohne Änderung seiner Rechte abgelehnt. Der Aufrufer muss ein dediziertes Anwendungsverzeichnis verwenden. Symlinks für Verzeichnis oder Datenbank werden abgelehnt, einschließlich ins Leere zeigender Dateisymlinks. Systempfad-Aliase wie macOS `/var` werden vor dem SQLite-Aufruf mit POSIX `realpath` aufgelöst. SQLite nutzt DELETE-Journaling und volle Synchronisierung; auf iOS erhält die Datenbank vollständigen Dateischutz. Dateirechte schützen nicht gegen den angemeldeten Benutzer oder kompromittierte Geräte. SQLite selbst ist hier nicht verschlüsselt. FileVault beziehungsweise iOS Data Protection gehören zur Betriebsumgebung; echte Patientendaten sind ausdrücklich nicht freigegeben. Kein Cloud-Sync, keine Netzwerkübertragung, keine Telemetrie.

## Austauschverträge

`RunExchange` exportiert und importiert vollständige Läufe als begrenzte JSON-Dokumente (maximal 16 MiB). Schema und Modellversion, endliche Zahlen, normierte Zustände, Ausgangszustand, Abtastgitter und Konfiguration werden geprüft. Beim JSON-Import und Datenbanklesen wird der Lauf aus seiner Konfiguration erneut berechnet: Abweichungen über `1e-9` Tage oder `1e-10` pro normierter Zustandskomponente führen zur Ablehnung. Diese absoluten technischen Toleranzen erlauben minimale Gleitkommaunterschiede; sie sind keine wissenschaftlichen Unsicherheitsintervalle. Der erneute Rechenaufwand bleibt durch die Konfigurationsgrenzen des Kerns begrenzt und gehört außerhalb des UI-Hauptthreads. Die Prüfung belegt Konsistenz mit dem implementierten Modell, keine authentifizierte Urheberschaft und keine medizinische Richtigkeit. Eine fremde Modellversion wird zurückgewiesen, statt stillschweigend mit dem aktuellen Kern interpretiert zu werden. JSON ist das verlustfreie Simulationsformat. Der CSV-Export ist eine lesbare Ergebnistabelle mit Lauf-ID, Modellversion, Tag, Zuständen und abgeleiteten Forschungswerten; er ist kein Format zur Rekonstruktion eines Laufs. Alle abgeleiteten Laborwerte sind unvalidierte Modell-Proxys, keine Messungen.

`MedicalExchange` importiert/exportiert synthetische Datensätze als JSON und CSV. Jeder Datensatz trägt `synthetic = true`. Diese Markierung ist eine Herkunftsdeklaration, kein technischer Nachweis, dass ein Benutzer keine echten Daten eingegeben hat. Es gibt keine Felder für Namen, Geburtsdatum, Adresse oder Identifikatoren externer Patienten. CSV verwendet UTF-8, Komma, Dezimalpunkt, RFC-4180-artige Anführungszeichen und eine feste Kopfzeile. Eingebettete Kommas, Anführungszeichen und Zeilenumbrüche werden korrekt verarbeitet; unbekannte Spalten, falsche Einheiten, ungültige Zahlen, negative Messwerte und `synthetic = false` führen zum Abbruch. Leere optionale Messwerte bedeuten fehlend, niemals null. Der CSV-Zeitstempel nutzt dieselbe Referenzzeit von 2001 wie JSON. Freitext, Fibrosebefunde und Ereignisse stehen in JSON-Zellen; dadurch bleiben Struktur und Quoting erhalten und Freitext beginnt nicht als Tabellenkalkulationsformel. Importgrenzen: 16 MiB, höchstens 10.000 Datensätze; Texte sind längenbegrenzt. Es werden keine Einheiten stillschweigend umgerechnet.

## Medizinischer Datensatz

`SyntheticPatientRecord`: UUID, synthetisches Kennzeichen, Beobachtungszeitpunkt, optionale Laborwerte, optionale Elastographie/Fibrose und klinische Ereignisse. Alle Laborwerte sind optionale `Double`-Werte; Einheiten sind fest und im CSV-Kopf explizit.

| Feld | Einheit / Kodierung |
|---|---|
| ALT, AST, GGT, AP | U/L |
| Bilirubin | mg/dL |
| Albumin | g/dL |
| INR | dimensionslos |
| Thrombozyten | 10^9/L |
| Kreatinin | mg/dL |
| Natrium | mmol/L |
| Elastographie | kPa, mit optionaler Methodenangabe |
| Fibrosebefund | System, Stadium, synthetischer Befundtext; keine automatische Umrechnung aus kPa |
| Klinische Ereignisse | UUID, Zeitpunkt, Typ und synthetischer Text |

Ereignistypen: Aszites, Varizenblutung, Enzephalopathie, Infektion, sonstiges. Die Speicherung solcher Ereignisse behauptet keine Vorhersagefähigkeit des Simulationsmodells. Fibrose, portaler Widerstand und modellierte Reserve allein stellen keine Diagnose einer dekompensierten Zirrhose dar.

## Child-Pugh und MELD: explizit ausstehend

Dieser Meilenstein berechnet keine klinischen Scores. Eine spätere Child-Pugh-Implementierung benötigt zusätzlich explizite, dokumentierte Kategorien für Aszites und Enzephalopathie sowie eine ausgewählte Definition der Grenzwerte, einschließlich cholestatischer Varianten. Die Ereignisliste ist kein zulässiger Ersatz dieser Kategorien. Für MELD muss die konkrete Formel (Original-MELD, MELD-Na oder MELD 3.0), ihr Geltungsbereich, Einheiten, Kappungen, Dialysestatus, Rundung und zeitliche Gültigkeit versioniert werden. MELD 3.0 benötigt zusätzliche Eingaben; aus den vorhandenen Feldern wird kein Ersatzscore erzeugt. Vor Freigabe: Primärquellenabgleich, unabhängige Referenzfälle, Grenzwerttests und hepatologische Prüfung. Scores dürfen weder aus unvalidierten Simulations-Proxys als reale Prognose noch als Transplantationspriorität dargestellt werden.

## FHIR-Plan

FHIR ist noch nicht implementiert. Vorgesehen: ein fest versioniertes Implementation Guide, `Observation` für Labor und Elastographie, `DiagnosticReport` für zusammengehörige Befunde, geeignete Ereignisressourcen und `Provenance` für Herkunft, Transformation und Modellversion. UCUM-Einheiten und LOINC-Codes werden erst nach fachlicher Prüfung eingebunden. Die Auswahl R4/R5 richtet sich nach dem Zielsystem. Keine Behauptung bestehender FHIR-Konformität.

## Nachweise und Tests

Tests decken SQLite-Wiederöffnung, Duplikat-Rollback, Löschen, zukünftige/fremde Schemata, Dateirechte, ungültiges JSON, Versionierung und CSV-Roundtrips einschließlich Quoting, fehlender Werte, Einheiten und ungültiger Zahlen ab. Die Tests prüfen Softwareverhalten, keine klinische Validität.

Primärquellen, abgerufen 22.10.2026:

- [SQLite Transaction](https://www.sqlite.org/lang_transaction.html): Transaktionen und Fehlerverhalten.
- [SQLite PRAGMA](https://www.sqlite.org/pragma.html#pragma_user_version): anwendungseigene Schemaversion.
- [HL7 FHIR R5 Observation](https://www.hl7.org/fhir/observation.html): Beobachtungen und Abgrenzung zu anderen Ressourcen; Grundlage des späteren Interoperabilitätsplans.
