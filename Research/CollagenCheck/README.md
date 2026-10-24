# Collagen regression: bounded internal check

Run from the repository root with Python 3 (standard library only). Obtain the locally reviewed input via [the existing source/import procedure](../../Docs/15-ExternalDataAccess.md). Original data and PDFs are not redistributed. Input and specification hashes are checked before calculation. No paid services or Rosalind access are needed.

```sh
python3 -B -m unittest discover -s Research/CollagenCheck -p 'test_*.py'
python3 -B Research/CollagenCheck/analyze_collagen.py --input /absolute/path/Hofer-CCl4-CPA.csv --spec Research/CollagenCheck/specification-v1.json --output /absolute/path/new-collagen-run
```

On the shared development Mac use the registered coordinator wrapper. Use a new output directory. For resume, inspect `verification.json` and verify `results-v1/SHA256SUMS` before deciding whether a run is missing; completed results should not be overwritten. An intentional repeat should match the published `result.json` byte for byte when code, input and specification match. Environment metadata can differ between machines. Five synthetic unit tests and two real-data analytic executions passed on the recorded environment. This is a closed-form calculation, not an RK4 or Kappa replacement; no random seed or step size is involved.

See [the bilingual report and mechanism dossier](../../Docs/19-CollagenInternalCheck.md). All later data were already seen: this is an internal retrospective check. IQR sensitivity ranges are not confidence intervals. Parameter changes are mathematical illustrations, not medicine effects. The public project is maintained under **Johnnie 4 free**; existing licensing status is unchanged.

## Deutsch

Python 3 und die Standardbibliothek genügen; die obigen Befehle gelten unverändert. Den lokal geprüften Eingang über die verlinkte Quellen-/Importanleitung beziehen. Originaldaten und PDFs werden nicht mitveröffentlicht. Eingangs- und Spezifikationsprüfsummen werden vor der Rechnung geprüft. Kein kostenpflichtiger Dienst und kein Rosalind-Zugang nötig. Auf dem gemeinsam genutzten Mac den Koordinator verwenden und ein neues Ausgabeziel wählen.

Zur Wiederaufnahme zuerst `verification.json` und `results-v1/SHA256SUMS` prüfen; vorhandene gültige Ergebnisse nicht neu berechnen oder überschreiben. Ein bewusster Wiederholungslauf muss bei gleichem Code, Eingang und gleicher Spezifikation dieselbe `result.json` erzeugen; Umgebungsmetadaten können auf anderen Rechnern abweichen. Fünf synthetische Tests und zwei analytische Ausführungen mit den Messaggregaten bestanden. Kein RK4-/Kappa-Ersatz, kein Zufallsstartwert und keine Integrationsschrittweite. Die spätere Messung war vorher bekannt: interne rückblickende Prüfung, keine unabhängige Bestätigung. Quartilbereiche sind keine Konfidenzintervalle; Parameteränderungen sind keine Arzneimittelwirkungen. Öffentlicher Projektname des Maintainers: **Johnnie 4 free**. Der Lizenzstatus bleibt unverändert.
