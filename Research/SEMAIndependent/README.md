# Reproduce the external SEMA4D–PLXNB2 association check

English / Deutsch: [report and interpretation / Bericht und Einordnung](../../Docs/23-SEMAIndependent.md).
Python 3 with NumPy; tested on macOS with Python 3.15.0 and NumPy 2.5.4. No new package was installed for this run. Resource reporting was verified on macOS; other platforms were not checked. Approximately 46 MB compressed source downloads; originals remain outside Git.

From repository root, through your coordinator wrapper where configured:

```sh
python3 -B -m unittest discover -s Research/SEMAIndependent -p 'test_*.py' -v
python3 Research/SEMAIndependent/fetch_data.py /tmp/hepatosim-sema-data
python3 -B Research/SEMAIndependent/analyze.py --sources /tmp/hepatosim-sema-data --spec Research/SEMAIndependent/specification-v1.json --cache /tmp/hepatosim-sema-cache.json --out /tmp/hepatosim-sema-result.json
python3 -B Research/SEMAIndependent/analyze.py --sources /tmp/hepatosim-sema-data --spec Research/SEMAIndependent/specification-v1.json --cache /tmp/hepatosim-sema-cache.json --out /tmp/hepatosim-sema-replay.json
cmp /tmp/hepatosim-sema-result.json /tmp/hepatosim-sema-replay.json
```

Use unused output/cache paths on the first run. Existing valid input files are verified, not redownloaded. A completed hash-bound count cache resumes the statistical analysis; incomplete raw scans restart without inventing partial results. Output files are never overwritten. A damaged cache or changed code/input/specification fails instead of silently reusing results. The raw scan streams one compressed file at a time, with one worker and CPU throttling; no full expression matrix is needed.

Für den Erstlauf neue Ausgabe- und Cachepfade verwenden. Vorhandene Eingaben werden per SHA-256 geprüft. Ein vollständiger Cache erlaubt die Wiederholung der Statistik; eine unterbrochene Rohdatenprüfung wird neu begonnen. Keine stillen Überschreibungen. Die Statistik vergleicht menschliche NAFLD-Fibrosestadien, keine Therapien. Die gemeinsame SEMA4D/PLXNB2-Bedingung wurde nicht erfüllt.

[Specification](specification-v1.json), [source decisions](source-search.json), [download hashes](provenance.json), [tests](tests.txt), [verification](verification.json), [actual result](result-v1.json), [local AI review](local-worker-review.json).
