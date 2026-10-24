# HSR-EXPR-001 — expression reanalysis / Expressionsauswertung

[Bilingual result report / Zweisprachiger Ergebnisbericht](../../Docs/18-ExpressionReanalysis.md).

Python ≥ 3.11, standard library only. Run from the repository root. On a coordinated host use its wrapper and reserve a separate output directory. The source matrix stays outside the repository; download rights are not a redistribution licence. SHA-256 checks reject changed inputs. No model download, fitting or random-number generator is involved: every allocation is enumerated.

Python ≥ 3.11, nur Standardbibliothek. Befehle ab Repositorywurzel ausführen. Auf koordinierten Rechnern Wrapper und separates Ausgabeverzeichnis verwenden. Quelldaten bleiben außerhalb des Repositorys. Bezugsmöglichkeit bedeutet keine Weitergabelizenz. Geänderte Eingaben werden anhand ihrer Prüfsummen abgewiesen. Kein Modelldownload, Fit oder Zufallszahlengenerator: alle Zuordnungen werden vollständig berechnet.

```sh
mkdir -p /tmp/hsr-expr-inputs
curl --fail --location --max-time 60 https://www.ebi.ac.uk/biostudies/files/E-MEXP-3177/genePS_prakash.txt.magetab -o /tmp/hsr-expr-inputs/genePS_prakash.txt.magetab
curl --fail --location --max-time 60 https://www.ebi.ac.uk/biostudies/files/E-MEXP-3177/E-MEXP-3177.idf.txt -o /tmp/hsr-expr-inputs/E-MEXP-3177.idf.txt
curl --fail --location --max-time 60 https://www.ebi.ac.uk/biostudies/files/E-MEXP-3177/E-MEXP-3177.sdrf.txt -o /tmp/hsr-expr-inputs/E-MEXP-3177.sdrf.txt
python3 -B -m unittest discover -s Research/Expression -p 'test_*.py'
python3 -B Research/Expression/analyze_expression.py --inputs /tmp/hsr-expr-inputs --spec Research/Expression/specification-v1.json --output /tmp/hsr-expr-results
```

The output directory must be new. A 120-second wall limit applies. Expected result: 241,576 probe sets, pseudo-F approximately 1.9259350402, exact allocation fraction 0.10. Last-bit floating-point differences on other runtimes are possible; exact replay was checked on the recorded Python version. There is no equivalence claim for other preprocessing or gene annotation.

Das Ausgabeverzeichnis muss neu sein. Zeitlimit: 120 Sekunden. Erwartet: 241.576 Probe-Sets, Pseudo-F ungefähr 1,9259350402, exakter Zuordnungsanteil 0,10. Andere Laufzeitversionen können letzte Gleitkommastellen verändern; bytegleiche Wiederholung wurde für die protokollierte Python-Version geprüft. Keine Gleichwertigkeitsaussage für andere Vorverarbeitung oder Genannotation.

## Resume without recalculation / Wiederaufnahme ohne Neuberechnung

Check the published completed artifacts before starting another calculation. This exact check was executed successfully. It validates the archived files, not the biological conclusions. If it fails, investigate; do not overwrite the evidence or automatically rerun. For a new calculation choose a new output path and a new explicit budget.

Abgeschlossene Artefakte vor einem neuen Lauf prüfen. Genau dieser Aufruf wurde erfolgreich ausgeführt. Er prüft die archivierten Dateien, keine biologischen Schlussfolgerungen. Bei Fehler Ursache klären; Belege weder überschreiben noch automatisch neu berechnen. Ein neuer Lauf erhält einen neuen Ausgabepfad und ein ausdrücklich festgelegtes Budget.

```sh
cd Research/Expression/results-v1
shasum -a 256 -c SHA256SUMS
```

Original data and metadata are sourced from E-MEXP-3177, not reissued here. Published CSV files contain only six-sample distance aggregates and 20 permutation statistics, not input intensities. Published results contain no private correspondence. This analysis does not establish independent collagen prediction, drug efficacy or clinical validity.

Originaldaten/-metadaten werden aus E-MEXP-3177 bezogen und hier nicht weitergegeben. Veröffentlichte CSVs enthalten nur Distanzaggregate über sechs Proben und 20 Permutationsstatistiken, keine Eingangsintensitäten. Keine private Korrespondenz. Keine unabhängige Kollagenvorhersage, Arzneimittelwirksamkeit oder klinische Validität belegt.
