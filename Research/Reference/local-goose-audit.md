# Lokaler Goose-Versuch: Ausführung und Evidenzgrenzen

Datum: 22.10.2026. Nachträgliche Dokumentation der vorhandenen Aufrufrecords und Antwortlogs; für diese Dokumentationsprüfung wurde kein weiterer Goose-, Modell-, Agenten- oder Cloud-Aufruf gestartet.

## Ergebnis

Zwei eng begrenzte Hilfsaufgaben an Goose mit dem Ollama-Modell **`michaelneale/deepseek-r1-goose:latest`** endeten nach ihren Zeitlimits. Beide Antwortlogs enthalten ausschließlich den Sitzungsstart und die Bereitschaftsmeldung. **Keine verwendbare fachliche Antwort, keine übernommene Aussage und keine übernommene Codeänderung.** Die Quellenbefunde im [Referenzaudit](selection-and-data.md) beruhen auf der eigenständigen Primärquellenprüfung und werden nicht Goose zugerechnet. Es entstand kein wissenschaftlicher Validierungsbeleg durch diese Versuche.

## Belegte Aufrufe

| Merkmal | Erster Versuch | Zweiter Versuch |
|---|---|---|
| Provider / Modell | Ollama / `michaelneale/deepseek-r1-goose:latest` | gleiches Modell und gleicher Provider |
| Aufgabe | Nur gelieferte Quellauszüge prüfen: TGFβ1-Input, react_MFB-Verdopplungszeit und Zeitfaktoren der Kollagenregeln; Beobachtung von Schlussfolgerung trennen, maximal 200 Wörter | Auf reine Zeilenextraktion zum TGFβ1-Input eingegrenzt; Dateiverweise und eine offene Frage, maximal 40 Wörter; keine Berechnung oder Korrekturempfehlung |
| Begrenzungen im Prompt | Nur lesen; keine Tools, Änderungen, Unteragenten, Websuche oder medizinischen Gültigkeitsaussagen | Nur lesen; keine Tools, Änderungen oder Agenten |
| Aufrufoptionen | `--no-profile`, `--no-session`, ein Turn, höchstens eine Toolwiederholung, JSON-Ausgabe angefordert | dieselben Begrenzungen |
| Zeitlimit | 180 Sekunden | 120 Sekunden |
| Gemessene Laufzeit laut Record | 180,13207454100484 Sekunden | 120,04190416703932 Sekunden |
| Status / Rückgabecode | `timeout` / −15 | `timeout` / −15 |
| Fachliche Ausgabe | keine im vorhandenen Log | keine im vorhandenen Log |

Die Promptverbote und Aufrufoptionen dokumentieren den beauftragten Umfang. Die Logs zeigen keine Toolaktivität; sie sind jedoch kein vollständiges Sandbox- oder Netzwerk-Audit. Der Startbanner allein beweist keine erfolgreiche Modellantwort. Der zweite Record nennt die Verengung nach dem ersten Timeout ausdrücklich als Grund für den Wiederholungsversuch.

## Abbruch und Konfiguration

Nach beiden Timeouts wurde der Versuch nicht fortgesetzt. **Arbeitsprotokollangabe der ausführenden Instanz:** Das Modell wurde anschließend mit `ollama stop michaelneale/deepseek-r1-goose:latest` gestoppt, um RAM freizugeben. Für diesen Stop-Aufruf wurde kein separater Output-Logpfad erhalten. Die Freigabe einer bestimmten Speichermenge wurde nicht gemessen; es wird kein nachträglicher Lognachweis behauptet.

Provider und Modell wurden durch die in den Records gespeicherten Goose-CLI-Argumente gesetzt. **Im Arbeitsablauf wurde keine Konfigurationsänderung vorgenommen; ein Vorher-/Nachher-Dateivergleich ist nicht dokumentiert.** Der erste Record vermerkt zusätzlich `source_changes: false`. Es wurden keine Goose-Ergebnisse in Modell, Tests oder wissenschaftliche Schlussfolgerungen übernommen.

## Prüfkörper

Die vorhandenen Dateien liegen relativ zur Workspace-Wurzel an folgenden Stellen:

| Pfad | Aussagekraft |
|---|---|
| `work/goose-audit/instructions.txt` | Vollständiger erster Auftrag und übergebene Quellauszüge |
| `work/goose-audit/invocation.json` | Modell/Provider, Argumente, Timeout, Laufzeit, Rückgabecode und Änderungsvermerk |
| `work/goose-audit/response.log` | Tatsächlich gespeicherte Ausgabe des ersten Versuchs |
| `work/goose-audit/retry/instructions.txt` | Eingeschränkter zweiter Auftrag |
| `work/goose-audit/retry/invocation.json` | Zweiter Aufruf mit 120-Sekunden-Limit und Wiederholungsgrund |
| `work/goose-audit/retry/response.log` | Tatsächlich gespeicherte Ausgabe des zweiten Versuchs |

Offen bleiben die Ursache der ausbleibenden Antworten, ein unveränderlicher Modell-Digest zum veränderlichen `latest`-Tag, vollständige Laufzeitdiagnostik sowie ein gesonderter Beleg des anschließenden Modellstopps. Keiner dieser Punkte wird durch einen erfolgreichen wissenschaftlichen oder technischen Review ersetzt: Ein solcher Goose-Review liegt nicht vor.
