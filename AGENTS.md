# HepatoSim Research: Arbeitsregeln

Bestehende Ergebnisse, Originalmodelle, eingefrorene Spezifikationen und Lizenzen erhalten. Historische Berichte werden durch datierte Nachträge ergänzt, nicht nachträglich zu Erfolgserklärungen umgeschrieben.

## Koordination und Zuständigkeit

Auf einem Rechner mit zentralem Koordinator vor konfliktträchtigen Aktionen dessen `~/.local/share/build-coordinator/COORDINATION.md` lesen. Sitzung und gesamten Workspace registrieren. Schreibzuständigkeit über `source:` plus **absoluten Workspace-Pfad** reservieren; eine Projekt-ID ist hier kein Pfadalias. Vor einem Build oder Rechenlauf die manuelle Sperre dokumentiert freigeben und den freigegebenen Wrapper verwenden. Fremde Prozesse nicht beenden. Ohne erreichbaren Koordinator betroffene Aktionen zurückstellen. Diese Regeln gelten auch für lokale Worker. Projektspezifische Overrides zusätzlich beachten.

## Wissenschaftliche Prüfpflichten

- Original-Kappa-Code nicht still durch eine ODE oder geänderte Regeln ersetzen.
- Vor jeder neuen Auswertung Messgrößen, Kontrollgruppen, Seeds, Akzeptanzkriterien, Budget und Datenrollen festlegen und hashen.
- Software-Verifikation, Publikationsreproduktion, Kalibrierung, unabhängige biologische Prüfung und klinische Validierung getrennt berichten.
- Keine erfundenen Daten, Quellen, Testergebnisse oder klinischen Umrechnungen. Stochastische Streuung ist kein Parameterposterior.
- Studien nach Spezies, Ursache, Stadium und experimentellem Zusammenhang trennen. Bereits verwendete Entwicklungsdaten sind nicht unabhängig.
- Ein Parameterkontrast ist ohne belegte quantitative Verknüpfung kein Arzneimittelmodell. Keine Dosierungs- oder individuellen Therapieempfehlungen.

## Werkzeuge, Budget und Wiederaufnahme

Vorhandene Swift-/Python-Werkzeuge und Original-KaSim wiederverwenden. Kein neuer Provider, Modell-Download oder kostenpflichtiger Dienst. Delegierte KI-Aufgaben ausschließlich über bestätigtes lokales Goose/Ollama, anfangs ein Worker, isolierter Kontext und Arbeitsordner. Modellname, Digest, lokale Inferenz, Laufzeit und Ergebnis belegen; KI-Ausgaben vor Übernahme prüfen.

`RESEARCH_STATE.json` nach Arbeitspaketen aktualisieren; Entscheidungen in `DECISIONS.md` festhalten. Erfolgreiche Läufe vor Wiederverwendung auf Integrität prüfen. Keine automatischen unbegrenzten Wiederholungen. Abgebrochene stochastische Läufe nicht aus einer CSV als vollständigen Zustand fortsetzen. Vollständige Läufe sind die Wiederaufnahmeeinheit, solange RNG-/Modellzustand nicht nachweislich checkpointfähig ist.

Neue nichttriviale Logik gezielt testen. Keine parallelen Änderungen derselben Dateien. Keine Veröffentlichungen anderer Projekte. Vor öffentlicher Veröffentlichung Dateien und Git-Historie auf Geheimnisse, personenbezogene Informationen und Weitergaberechte prüfen. Für eigenen Code keine Lizenz ohne Nutzerentscheidung vergeben.
