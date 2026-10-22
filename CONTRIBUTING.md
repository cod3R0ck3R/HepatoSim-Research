# Contributing / Mitarbeit

## English

Read `AGENTS.md`, `RESEARCH_PLAN.md`, `RESEARCH_STATE.json` and `DECISIONS.md` first. On coordinated hosts, register the session and reserve the full source path. Keep edits isolated and use the coordinator for tests, builds and simulations. Preserve old evidence and update progress after each package.

For scientific changes, specify the question, sources, data roles, observables, units, seeds, comparisons, acceptance criteria and compute budget before execution. New model assumptions or thresholds require a new specification; never overwrite frozen versions. Include negative results, failures and missing data. Retain original licenses and attributable sources.

Run relevant tests and report actual commands/results. Pure standard-library research checks: `python3 -B -m unittest discover -s Research/Reference -p 'test_*.py'` and the equivalent discovery under `Research/LocalAI`. Swift checks use `Scripts/verify.sh`. These commands must use the host wrapper when coordination is configured. Do not claim new checks from historical logs.

Submit small, reviewable changes with reproducible evidence and explicit limits. Do not contribute private health data or unlicensed datasets. AI-generated proposals require human/maintainer review. No contributor license agreement or open-source license for original HepatoSim code has been established; clarify rights before submitting material whose redistribution is restricted.

Citation: refer to the actual repository URL and commit once publication is verified, and separately cite Bouguéon et al. (2024), DOI 10.1371/journal.pcbi.1011858, for the original model. No project DOI, release tag or unconfirmed authorship is asserted.

## Deutsch

Zuerst `AGENTS.md`, `RESEARCH_PLAN.md`, `RESEARCH_STATE.json` und `DECISIONS.md` lesen. Auf koordinierten Rechnern Sitzung registrieren und vollständigen Source-Pfad reservieren. Änderungen isolieren und Tests, Builds sowie Simulationen durch den Koordinator führen. Alte Belege erhalten und Fortschritt nach jedem Paket speichern.

Für wissenschaftliche Änderungen Frage, Quellen, Datenrollen, Messgrößen, Einheiten, Seeds, Vergleiche, Akzeptanzkriterien und Rechenbudget vor Ausführung festlegen. Neue Modellannahmen oder Grenzwerte benötigen eine neue Spezifikation; eingefrorene Versionen nicht ersetzen. Negative Ergebnisse, Fehler und Datenlücken berichten. Originale Lizenzen und nachvollziehbare Quellen erhalten.

Passende Tests ausführen und tatsächliche Befehle/Ergebnisse berichten. Forschungsprüfungen mit Standardbibliothek: `python3 -B -m unittest discover -s Research/Reference -p 'test_*.py'` sowie entsprechende Discovery unter `Research/LocalAI`. Swift-Prüfungen verwenden `Scripts/verify.sh`. Bei vorhandener Koordination müssen diese Befehle durch den Host-Wrapper laufen. Historische Logs sind keine neuen Prüfungen.

Kleine, überprüfbare Änderungen mit reproduzierbaren Belegen und ausdrücklichen Grenzen einreichen. Keine privaten Gesundheitsdaten oder unlizenzierten Datensätze beitragen. KI-Vorschläge benötigen menschliche/Maintainer-Prüfung. Weder Contributor License Agreement noch Open-Source-Lizenz für eigenen HepatoSim-Code sind festgelegt; Rechte vor Einreichen eingeschränkt weitergebbarer Materialien klären.

Zitation: nach bestätigter Veröffentlichung tatsächliche Repository-URL und Commit nennen; das Originalmodell getrennt als Bouguéon et al. (2024), DOI 10.1371/journal.pcbi.1011858, zitieren. Kein Projekt-DOI, Release-Tag oder unbestätigte Urheberschaft wird behauptet.
