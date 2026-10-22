# Test-, Verifikations- und Validierungsstrategie

Stand: 22.10.2026. **Keine klinische oder medizinische Validierung liegt vor.** Ein bestandener Build, ein plausibles Diagramm oder die Wiedergewinnung synthetisch erzeugter Parameter ändert diesen Status nicht. Tatsächlich ausgeführte Prüfungen stehen im Testbericht; diese Datei definiert zusätzlich zukünftige Abnahmekriterien.

## Welche Aussage welcher Nachweis erlaubt

| Stufe | Frage | Zulässiger Nachweis | Unzulässige Schlussfolgerung |
|---|---|---|---|
| Softwareverifikation | Implementiert der Code seine Spezifikation? | Unit-, Vertrags-, Integrations- und Importtests | „Damit medizinisch richtig“ |
| Numerische Verifikation | Wird das formulierte mathematische Problem ausreichend genau gelöst? | Analytische Grenzfälle, Schrittverfeinerung, Referenzsolver | „Damit biologische Vorhersage bestätigt“ |
| Mechanistische Plausibilität | Sind Richtung und Struktur mit Literatur vereinbar? | Nachvollziehbare Quellen und fachliches Review | „Rate oder Therapieeffekt quantitativ belegt“ |
| Kalibrierung | Welche Parameter passen zu gewählten Daten? | Vorgegebene Zielfunktion, Fehlerstruktur, Identifizierbarkeit | „Guter Trainingsfit validiert das Modell“ |
| Externe Validierung | Funktioniert das festgelegte Modell für den vorgesehenen Zweck? | Unabhängige Daten, vorab definierte Endpunkte und Fehlergrenzen | Übertragung auf andere Population/Zwecke ohne Prüfung |
| Klinischer Nutzen / regulatorische Eignung | Verbessert die konkrete Nutzung Entscheidungen sicher? | Zweckbezogenes Studien-, Qualitäts- und Risikokonzept | Ableitung allein aus Diskrimination oder publiziertem Mechanismus |

## Testpyramide des ersten Vertical Slice

1. **Eingaben:** Zustände, Parameter, Schrittweite und Horizont sind endlich und innerhalb dokumentierter Grenzen. NaN/Infinity, negative Raten, ungültige Größen, leere Imports und zu große Aufgaben liefern Fehler. Keine stille Korrektur fachlicher Eingaben.
2. **Kern:** Gleiche Eingaben ergeben bei gleicher Laufzeit-/Solverkonfiguration gleiche Werte. Nullschädigung, ausgeschaltete Reaktionen, Randzustände und konstante Gleichgewichte prüfen erwartete Richtung bzw. Erhaltung. Jeder Zustand bleibt im definierten Wertebereich; ein Verstoß wird nicht durch verstecktes Clipping als Erfolg ausgegeben.
3. **Numerik:** Schrittweitenvergleich `h`, `h/2`, `h/4` für repräsentative und extreme zulässige Parameter. Referenzwerte werden aus einer unabhängigen Methode oder analytischen Sonderfällen abgeleitet. Ein eingefrorener Snapshot desselben Codes ist nur Regression, keine unabhängige Referenz.
4. **Szenarien:** Identische Kontroll-/Interventionskonfiguration ergibt identische Kurven. Nullintervention entspricht Kontrolle. Interventionsbeginn und Dauer werden an Schritt-/Samplegrenzen geprüft; Änderungen erzeugen neue Läufe.
5. **Persistenz:** Simulation → SQLite → Prozess/Verbindung schließen → erneut öffnen → identische Parameter, Version, Seed und Samples. Transaktionsabbruch darf keinen halben Lauf hinterlassen. Neue Schema-Versionen müssen kontrolliert migrieren oder ohne Datenverlust abgelehnt werden.
6. **Austausch:** JSON-/CSV-Rundlauf, UTF-8, Anführungszeichen, Dezimalformat, fehlende/zusätzliche Felder, ungültige Einheiten und Versionskonflikte. CSV ist ein definiertes Schema, kein ungetypter Universaldateneingang. Export für Tabellenprogramme benötigt vor späteren freien Textfeldern Schutz gegen Formelausführung.
7. **UI:** Simulation, Vergleich, Speicherung, Wiederladen und Export sind bedienbar; Langläufe blockieren keine Eingabe. Fehler bleiben sichtbar. Forschungsstatus erscheint bei Diagrammen und Export. VoiceOver, Tastatur, Dynamic Type, Kontrast, Dark/Light Mode und kleine Displays werden gesondert manuell geprüft.

Jeder Fehler erhält eine reproduzierbare Eingabe und einen Regressionstest. Tests dürfen Fehlergrenzen nicht nachträglich lockern, um einen unerklärten Fehler zu verdecken. Ein Softwareupdate darf bestehende Ergebnisdateien weder umdeuten noch neu schreiben, nur weil die Modellversion neuer ist.

## Numerische Prüfprotokolle

Der erste Kern verwendet dimensionslose Zustände und eine Zeitbasis in Tagen. Einheiten und Gleichungen stehen in der Modelldokumentation. Eine mathematische Zustandsgrenze muss begründet werden; bei einem Integrationsfehler ist eine kleinere Schrittweite oder ein anderer Solver erforderlich.

Für jede Modellversion werden mindestens ein Ruhefall, ein moderater Ausgangszustand und ein starker Schädigungsfall mit zwei Interventionszeitpunkten geprüft. Je Lauf werden Maximum des absoluten Fehlers je Zustand, Fehler der Endwerte und Aufwand erfasst. Ziel für Standardkonfiguration: Endwertabweichung zwischen den beiden feinsten Stufen höchstens `1e-5` je dimensionslosem Zustand. Das ist ein technisches Präzisionsziel, keine klinisch relevante Fehlerschwelle. Bei nicht glatten Interventionen erfolgt Segmentierung an Ereigniszeiten; eine RK4-Ordnungsbehauptung über eine Sprungstelle wäre unzulässig.

Vor längeren oder steifen Modellen kommen unabhängige Referenzintegration mit strengen Toleranzen, Steifheitsdiagnostik, Positivität und Abbruchgrenzen hinzu. Für Vergleiche verschiedener CPU-/Compilerplattformen gilt eine dokumentierte numerische Toleranz; Bitgleichheit wird nicht pauschal versprochen. Metal wird erst akzeptiert, wenn es identische wissenschaftliche Schlussfolgerungen innerhalb vorher definierter Toleranzen und einen nachweisbaren Zeit-/Energievorteil liefert.

## Sensitivität, Unsicherheit und Kalibrierung

Lokale Sensitivität nutzt kontrollierte Parameterperturbationen und berichtet absolute Ableitungen sowie dimensionslose Elastizität nur bei nicht verschwindendem Nenner. Parameter-Sweeps verändern genau dokumentierte Achsen. Globale Sensitivität folgt erst nach Festlegung plausibler Verteilungen und Abhängigkeiten; unabhängige Uniform-Verteilungen sind keine biologischen Priors.

Ensemblequantile heißen **Szenario-/Parameterband**, solange sie aus frei gewählten Parametern stammen. Weder Konfidenz- noch klinisches Prognoseintervall behaupten. Dokumentiert werden Parameterverteilung, Seed, RNG-Algorithmus, Samplezahl und Quantildefinition. Mehr Stichproben verringern Monte-Carlo-Fehler, beheben aber keine strukturelle Modellunsicherheit.

Die erste Kalibrierung verwendet ausschließlich synthetische Beobachtungen. Zielparameter, Bounds, Startwerte, Gewichtung und Ausgabefehler werden gespeichert. Ein Test stellt Daten mit bekannter Parameterkombination her, prüft Verlustreduktion und Vorhersagefehler auf separaten Zeitpunkten. Er garantiert keine eindeutige Parameteridentifikation. Vor Realdaten sind strukturelle/praktische Identifizierbarkeit, Parameterkorrelationen, Profile-Likelihood oder gleichwertige Unsicherheitsanalyse erforderlich. Nicht identifizierbare Parameter werden fixiert, zusammengefasst oder als nicht bestimmt ausgewiesen.

## Wissenschaftlicher Validierungsplan, Phase 6

Vor Datensichtung werden ein enges Anwendungsziel, Population, Ätiologie, Zeitraum, Endpunkt, Messverfahren, Einheiten und Ausschlussregeln festgelegt. Ein erster realistischer Anspruch wäre die Beschreibung ausgewählter Gruppenverläufe unter bekannten Bedingungen, nicht die individuelle Prognose von Dekompensation oder Überleben.

Forschungsprotokoll:

1. Mechanismen und Parameterbelege in einem Claim-Register erfassen: Quelle, Population/Spezies, Evidenzart, Unsicherheit, Ableitung und verantwortliche Prüfung.
2. Verfügbaren longitudinalen Datensatz auf Messfehler, Missingness, Selektionsbias, Behandlung, Zensierung und zeitliche Auflösung prüfen. Elastographie ist kein direkter Kollagenanteil; mögliche Entzündungs-/Stauungseinflüsse müssen im Messmodell berücksichtigt werden.
3. Trainings-, Abstimmungs- und externe Testdaten auf Personen-/Zentrumsebene trennen. Wiederholte Messungen einer Person nicht über Splits verteilen. Testdaten nicht zur Parameterauswahl verwenden.
4. Einfachen Baselineansatz festlegen. Fehlermaße, vorab definierte Akzeptanzgrenzen und Umgang mit fehlenden Daten protokollieren. Labore getrennt nach Einheit und Messverfahren beurteilen.
5. Diskrimination, Kalibration und Unsicherheitsabdeckung nur für die tatsächlich definierte Zielvariable messen; Subgruppen und Transportierbarkeit untersuchen. Ein ODE-Zustand ohne validiertes Messmodell ist kein klinischer Endpunkt.
6. Externe Auswertung unabhängig reproduzieren. Negative Resultate, Abweichungen und Modelländerungen dokumentieren. Jede Änderung nach Testdateneinsicht erfordert einen neuen unabhängigen Test.

Fachreview mindestens durch Hepatologie und quantitative Modellierung. Evidenz aus Zell-/Tiermodellen darf nicht als nachgewiesener humaner Therapieeffekt ausgegeben werden. Eine hypothetische Intervention wird durch Parameteränderung definiert; ohne pharmakologisches Modell gibt es keine Dosis-, Wirkstoff- oder Behandlungsaussage.

## Klinische Scores: geplante, getrennte Auswertungen

Im ersten Slice werden **keine klinischen Scores implementiert**. Modellierte Laborproxies ersetzen keine gemessenen Werte. Für spätere Scores wird eine eigene Definition-ID samt Quelle, Datum, Eingabeeinheiten, Grenzwerten, Rundung und Anwendungsbereich gespeichert. Fehlt ein Pflichtwert, entsteht kein Score und keine stillschweigende Normalwertannahme.

| Definition | Geplante Trennung | Abnahme vor Freigabe |
|---|---|---|
| MELD, historische Fassung | Das ursprünglich publizierte Modell und spätere Allokationsformeln sind nicht unter einer unspezifischen `MELD`-Funktion zu vermischen | Exakte Publikations-/Policyfassung, Laborgrenzen, Logarithmus, Dialyseregel und Rundung dokumentieren |
| MELD-Na | Eigene Definition mit Natrium und versionsabhängigen Regeln | Offizielle Referenzfälle, sämtliche unteren/oberen Grenzen und Einheitenumrechnung prüfen |
| MELD 3.0 | Eigenes Modell mit zusätzlichen Kovariaten/Interaktionen; nicht bloß ein Labelwechsel | Veröffentlichte Formel und tatsächlich geltende Allokationsfassung gesondert verifizieren; demografische Eingaben explizit, nie inferiert |
| Child-Pugh | Bilirubin, Albumin, Gerinnungsdefinition, Aszites und Enzephalopathie; verwendete klinische Variante ausdrücklich benennen | Stufengrenzen, INR versus Prothrombinzeit, Varianten bei Cholestase und subjektive Einstufungen klinisch abnehmen |

Das historische MELD-Modell wurde in einer definierten klinischen Population untersucht; seine berichtete Leistung validiert keine HepatoSim-Zeitreihe. [Kamath et al., 2001](https://pubmed.ncbi.nlm.nih.gov/11172350/) MELD 3.0 ist eine gesondert publizierte Aktualisierung. [Kim et al., 2021](https://pubmed.ncbi.nlm.nih.gov/34481845/) Der HRSA/OPTN-Rechner dokumentiert einen Formelwechseldatum vom 13.07.2023; Allokationsregeln sind vor Implementierung erneut in der geltenden Policy zu prüfen. [HRSA MELD Calculator](https://www.hrsa.gov/optn/data-calculators/allocation-calculators/meld-calculator) Child-Pugh wird historisch auf Pugh et al. zurückgeführt; das ersetzt nicht die Festlegung einer konkreten heutigen Operationalisierung. [Pugh et al., 1973](https://pubmed.ncbi.nlm.nih.gov/4541913/)

Die Ausgabe bleibt ein versionsgebundenes Forschungsergebnis. Es gibt keine Transplantationspriorisierung, Überlebenswahrscheinlichkeit oder Behandlungsempfehlung aus dem unvalidierten Simulationsmodell.

## Datenschutz und regulatorische Grenzen

Der Slice verarbeitet nur synthetische Daten, ohne externe KI-Aufrufe oder automatische Übertragung. Freitextimporte können dennoch Personenbezug enthalten; ein Feld `synthetic` beweist keine Anonymität. Pseudonymisierung ist keine Anonymisierung. Vor Aufnahme realer Daten ist ein eigenes Projektfreigabeverfahren erforderlich.

DSGVO-Prüfung: Zweck und Verantwortlichkeit, Rechtsgrundlage nach Artikel 6, erforderliche Ausnahme für Gesundheitsdaten nach Artikel 9, Datenminimierung, Aufbewahrung, Betroffenenrechte, Zugriffsschutz und gegebenenfalls Datenschutz-Folgenabschätzung. Forschungszwecke sind keine pauschale Erlaubnis; Artikel 89 verlangt geeignete Garantien. Anbieter, Auftragsverarbeitung und Drittlandtransfers sind vor Server-/KI-Nutzung zu prüfen. [DSGVO, insbesondere Artikel 5, 6, 9, 25, 28, 32, 35 und 89](https://eur-lex.europa.eu/eli/reg/2016/679/)

Dateirechte, SQLite und ein lokaler Speicherort sind keine vollständige Verschlüsselungslösung. Vor Realdaten: Schlüsselbundgestütztes Schlüsselmanagement, verschlüsselte Speicherung/Backups, iOS Data Protection, entsperrungsabhängiger Zugriff, sichere Exporte, Löschkonzept und überprüfte Signatur/Sandbox des ausgelieferten Artefakts. Diese Maßnahmen sind im Slice nicht als vollständig implementiert anzusehen.

Ob Software unter die MDR fällt, hängt von ihrer konkreten Zweckbestimmung und Funktion ab. Ein „Research only“-Hinweis ist keine automatische Ausnahme. Vor individueller diagnostischer/prognostischer/therapeutischer Verwendung sind Qualifikation und Klassifikation, unter anderem Anhang VIII Regel 11, fachlich zu bewerten. [Verordnung (EU) 2017/745](https://eur-lex.europa.eu/eli/reg/2017/745/) Die EU-Kommission veröffentlichte MDCG 2019-11 Rev.1 im Juni 2025 als Orientierung für Softwarequalifikation und -klassifikation. [MDCG 2019-11 Rev.1](https://health.ec.europa.eu/latest-updates/update-mdcg-2019-11-rev1-qualification-and-classification-software-regulation-eu-2017745-and-2025-06-17_en)

Diese Architektur ist keine Rechtsberatung, CE-Konformitätsbewertung oder Zusicherung regulatorischer Eignung. Bei Zweckänderung werden Risiken, Qualitätsmanagement, klinische Evidenz und nötige Zulassungs-/Konformitätsschritte neu geplant.

## KI-Ausgaben und wissenschaftliche Provenienz

Eine Provider-Schnittstelle darf nur Forschungsanfragen und getrennte Hypothesenartefakte liefern. Jede Ausgabe benötigt Provider-/Modellkennung, Zeitpunkt, benannte Einschränkungen und überprüfbare Quellenreferenzen. Das mathematische Ergebnisobjekt bleibt davon getrennt. Ein KI-generierter Literaturhinweis ist bis zur Quellenprüfung unbestätigt; URL und Zitat allein beweisen keine Stützung.

Vor einem produktiven Adapter: Tests für erfundene Zitate, widersprüchliche Quellen, Prompt-Injection in importierter Literatur, medizinische Überbehauptungen und unerlaubte Datenweitergabe. Providertext wird als untrusted content behandelt, nie als ausführbare Anweisung. Externe Provider bleiben standardmäßig ausgeschaltet. Kein API-Schlüssel wird im Repository, in Laufdaten oder Logs gespeichert.
