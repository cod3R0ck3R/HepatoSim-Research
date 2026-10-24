# GSE210077: donor and cell-type check

Human cross-sectional snRNA-seq, six donors, six broad author-annotated cell types. See [frozen specification](specification-v1.json), [source audit](provenance.json), and [bilingual findings](../../Docs/24-DonorCellCheck.md). The current GEO series contains 40 samples; only the six published-study libraries joined to the author annotation are included. Additional libraries are not silently treated as additional donors.

Requires Python 3, NumPy and approximately 1 GB of free disk space. No new AI provider or package is needed in the tested local environment. Run from the repository root; use the configured coordinator wrapper on coordinated hosts. The checked public HCA mirror supplies the exact files named in the manifest. Raw inputs and private logs are not redistributed.

```sh
cd Research/DonorCellCheck
python3 -B fetch_data.py input-manifest.json
python3 -B -m unittest -v test_analyze
python3 -B analyze.py --spec specification-v1.json --manifest input-manifest.json --source sources --checkpoints checkpoints --output result-local.json
python3 -B analyze.py --spec specification-v1.json --manifest input-manifest.json --source sources --checkpoints checkpoints --output replay-local.json --replay
cmp result-local.json replay-local.json
```

The calculation never overwrites a result. Resume the calculation with the same command and a new output name; validated donor checkpoints are reused, missing donors are computed. Cache-only `--replay` requires all six checkpoints and the matching annotation. Specification, manifest, analysis and shared-parser hashes must match. The ordinary command rechecks every input file's size and hash. Completed donor checkpoints are durable; an interrupted donor is rescanned. A leftover download `.partial` is preserved for inspection and must be moved aside before a deliberate retry. No endless retries.

The shared sparse parser keeps its previous 100,000-column default. This caller explicitly permits the measured raw-droplet column count (maximum ten million) while storing only author-retained nuclei. Its seven existing tests are rerun alongside seven new tests. Historical checkpoints remain tied to their original code version; use the historical commit for historical replay.

Statistics use three diseased versus three normal donors, not individual nuclei as biological replicates. Two-sided exact permutation tests have only 20 allocations (minimum p=0.1); leave-one-donor-out ranges are sensitivity ranges, not confidence intervals. No treatment, receptor-binding or fibrosis-regression effect is identified.

## Deutsch

Sechs menschliche Spender werden anhand der publizierten Autorenannotation nach sechs breiten Zelltypen getrennt. Der aktuelle GEO-Eintrag umfasst 40 Proben; ausgewertet werden nur die sechs eindeutig zugeordneten Bibliotheken. Die Befehle oben laden prüfsummengebundene Dateien, führen Tests aus und prüfen eine identische Cache-Wiederholung.

Vorhandene Ergebnisdateien werden nicht überschrieben. Wiederaufnahme nutzt passende Spender-Checkpoints; geänderte Eingaben oder Programmversionen werden abgewiesen. Für historische Ergebnisse die damalige Codeversion verwenden. Die Alterskonflikte zweier Spender bleiben offen. Drei unterschiedlich stark erkrankte Spender erlauben weder eine Arzneimittelwirkung noch einen Beleg für die Rückbildung einer Zirrhose.

## Post hoc reference sensitivity

The first strict-ID attempt stopped before counting because Ensembl version suffixes differed by condition. Its failure and both protocol versions are retained. V2 removes terminal numeric versions, rejects ambiguous base IDs, and rescans denominators over the intersection. It uses the pinned primary aggregate counts and verifies unchanged target identities; it does not harmonize upstream alignment.

From `Research/DonorCellCheck`, after obtaining the source files:

```sh
python3 -B reference_sensitivity.py . common-local.json
python3 -B reference_sensitivity.py . common-replay-local.json --replay
cmp common-local.json common-replay-local.json
```

Deutsch: Die nachträgliche Referenzprüfung entfernt ausschließlich numerische Versionssuffixe und prüft Mehrdeutigkeiten. Sie erhält die Hauptauswertung und ersetzt keine einheitliche Rohdatenverarbeitung. Beide Protokollversionen und der erste kontrollierte Abbruch bleiben dokumentiert. Sieben neue Tests und sieben bestehende Parsertests prüfen die verwendeten Rechenwege.
