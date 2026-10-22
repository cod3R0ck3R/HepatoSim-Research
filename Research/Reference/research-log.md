# Forschungsprotokoll HSR-BG2024-001

## Iteration 1 — Quellen und vorab definierter Test

2026-10-22T11:14:52.805652+00:00 UTC. Vor wissenschaftlichen Simulationen eingefroren. Originalquellen und Code gelesen; keine simulierten Kollagenergebnisse für die Auswahl verwendet. Ein Parser-/Laufzeit-Smoke-Test ohne biologischen Zeithorizont ist getrennte technische Vorbereitung.

Frage: Reproduktion von Fig. 2 B, danach Prüfung der Verfügbarkeit unabhängiger Kollagenzeitreihen. Wichtigste Unsicherheiten: Original-Laufzeitversion, Stimulusamplitude (Legende gegenüber Code), Messdatenprovenienz. Budget und Abbruchregeln stehen in der JSON-Spezifikation. Keine Anpassung von Parametern an spätere Ergebnisse.

Die Original-Pipeline importiert eine nicht veröffentlichte utils.py; der eigene Adapter ruft deshalb dieselbe KaSim-CLI direkt mit explizitem Seed auf. Kein Ersatz des stochastischen Modells durch RK4. Das bestehende Projekt hat noch keine implementierte Plugin-Laufzeit; der Adapter bleibt ein unabhängiges Forschungs-CLI.

## Iteration 2 — dokumentierte Budgetanpassung

2026-10-22T11:25:56.607486+00:00 UTC. V1 nach 180 s abgebrochen; Teilverlauf bis Tag 23. Kein biologisches Urteil. V1.1 vor erneutem Lauf eingefroren: 900 s pro Lauf, weiterhin 3.600 s insgesamt und maximal zwei Prozesse. Originale Regeln, Parameter und Auswertung unverändert. Die offizielle --gluttony-Option ändert die Speicherverwaltung; keine Solver-/Modelländerung. Ein verursachter Geschwindigkeitsgewinn ist nicht isoliert gemessen. Der Vergleich identischer Seed-Präfixe wird als technische Kontrolle berichtet. Zwei lokale Goose-Aufträge endeten nach 180/120 s ohne verwertbare Antwort; keine Inhalte integriert, Modell danach laut Arbeitsprotokoll zur RAM-Freigabe entladen.

## Iteration 3 — Auswertung und unabhängiger Software-Review

22.10.2026, während der unveränderten v1.1-Rechenserie. Frage: Können fehlerhafte Laufzuordnung, unvollständige Ensembles oder lückenhafte Ausgaberaster als erfolgreiche Auswertung erscheinen? Vorgehen: künstliche Parser-/Manifestfixtures, Quellen-/Tracehashprüfung, getrennte technische Kontrollläufe und Figurenprüfung.

Ein unabhängiger Code-Review reproduzierte zwei echte Auswertungsfehler: passende Metadaten konnten abweichende KaSim-Argumente verdecken; fünf Endpunkte konnten als vollständiger Rastervergleich durchgehen. Die Analyse wurde vor dem Abschlussbericht korrigiert und um Regressionstests erweitert. Das ändert keine biologischen Regeln, Parameter, Seeds, Ziele oder Akzeptanzgrenzen. Die Laufserie und ihre Rohdaten wurden nicht verändert. Eine Figurenlegende wurde auf alle Panels erweitert, damit ein vollständiges Alternativensemble auch bei unvollständiger Kontrolle korrekt bezeichnet bleibt.

Fünf vollständig berechnete Default-Läufe waren zu diesem Zeitpunkt vorhanden. Keine Überlebenden-Teilstichprobe wurde als volles Zehnerensemble ausgewertet. Die verbleibenden Läufe dürfen das bereits festgelegte Gesamtbudget nicht überschreiten. Eine Verschiebung des Rechenbudgets oder Reihenfolge nach Betrachtung der Kollagenergebnisse erfolgt nicht.

Das gewünschte Download-Log wurde in-place umformatiert, zuvor unverändert gesichert und mit benutzerspezifischen grc-Farbregeln geprüft. Die wissenschaftliche Rechenserie wurde dafür nicht angehalten.

## Iteration 4 — Parameterprovenienz statt pauschaler Dimensionzählung

22.10.2026. Quellenprüfung anhand vorhandener S2 Table und Originalcode, ohne neue Simulation. Die Spezifikation bezeichnet 43 Originalparameter zu pauschal: 43 Tabellenpositionen sind keine 43 freien Fitparameter. 22 sind als empirisch geschätzt markiert; acht davon sind algebraisch gekoppelt. Weitere Literatur-, abgeleitete und Inputgrößen sind zu trennen. Der Originalartikel verwendete zudem mehr Beobachtungen als die zwei hier extrahierten Kollagenziele. Ergebnis und Fundstellen stehen in parameter-identifiability.md.

Die eingefrorenen Dateien wurden nicht umgeschrieben. README und Abschlussbericht korrigieren ihre interpretative Aussage ausdrücklich. Kein neuer Fit, keine Behauptung eines Identifizierbarkeitsranges, keine veränderten Parameter oder Auswahlkriterien. Nächster Schritt bleibt ein klar definierter Daten-/Messfehlervertrag vor jeder Identifizierbarkeits- oder Parameterschätzungsanalyse.

## Iteration 5 — Abschluss am festen Budgetende

22.10.2026, gegen 14:26 Uhr CEST. Der Runner endete mit Exit 1, weil das gesamte geplante Programm innerhalb von 3.600 Sekunden nicht abgeschlossen wurde. 32 finale Jobmanifeste: 14 vollständig, zwei Timeouts und 16 wegen erschöpften Budgets nicht gestartet. Default: alle zehn Seeds; Legendenvariante: vier von zehn. Kein alternatives Restensemble wurde als vollständig ausgegeben. Mechanismusvarianten, voller Replay und Rasterkontrolle wurden nicht ausgeführt.

Die abschließende Analyse steht in analysis/benchmark-v1.1.json, die Abbildungen mit Provenienz in analysis/figures/, die 74 bestandenen Softwaretests in analysis/software-tests.txt. Docs/10-ReferenceBenchmark.md berichtet Zahlen, Quellenkonflikte und Datenlücken. Keine Parameteranpassung, kein neuer Datensplit, keine nachträgliche Akzeptanzschwelle. Die späte Platzierung der technischen Kontrollen war unter diesem Budget ungünstig; deren Priorisierung ist der nächste kleine technische Schritt, kein Grund zur stillen Verlängerung dieses Laufs.

Eine eigene Prozessprüfung bestätigte anschließend null KaSim-Prozesse. Der Rechenslot wurde an die angefragte übergeordnete Ressourcenkoordination zurückgemeldet. Keine weitere schwere Rechenserie gestartet. Das Originalmodell bleibt Maus-/CCl4-bezogen; unabhängige biologische Prüfung, menschliche Übertragbarkeit und klinische Einsatzfähigkeit sind nicht nachgewiesen.
