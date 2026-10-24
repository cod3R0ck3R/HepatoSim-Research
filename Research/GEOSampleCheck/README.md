# Nine-library GEO audit / Prüfung der neun GEO-Bibliotheken

GSE295293: male mouse liver, three control, three 10-week TAA and three 2-week withdrawal libraries. This is an exploratory reanalysis of author development data, not an independent biological validation or a drug trial. Read [the report](../../Docs/22-GEOSampleCheck.md) and [frozen specification](specification-v1.json).

Requirements: Python3 and NumPy; no Seurat/Scanpy, network inference or new model download. The raw archive and upstream code are not redistributed. Download from the GEO link in [provenance](provenance.json), or use the existing bounded downloader below. Use the project coordinator where configured; the default matrix scan now deliberately throttles parsing plus aggregation to 20% of one CPU core, checks peak RSS against 512 MiB, and keeps the 600 s timeout. Register this low-load version as one light worker with 1 GiB. The full local language model remains a heavy job; no resource gate is disabled. See [the pre-execution resource amendment](resource-amendment.json). Metadata-only checks are small and do not replace a full scan.

From the repository root:

```sh
python3 Research/TAATransfer/fetch_geo.py --output geo-new
python3 -m unittest discover -s Research/GEOSampleCheck -p 'test_*.py'
python3 Research/GEOSampleCheck/audit_metadata.py --archive geo-new/GSE295293_RAW.tar --spec Research/GEOSampleCheck/specification-v1.json --output metadata-new.json
python3 Research/GEOSampleCheck/analyze_geo.py --archive geo-new/GSE295293_RAW.tar --spec Research/GEOSampleCheck/specification-v1.json --checkpoints geo-checkpoints --output geo-result.json
python3 Research/GEOSampleCheck/analyze_geo.py --replay --spec Research/GEOSampleCheck/specification-v1.json --checkpoints geo-checkpoints --output geo-replay.json
cmp geo-result.json geo-replay.json
```

Resume the fourth command with the same checkpoint directory and a new result filename if needed. Checkpoints bind each sample to archive, specification and code hashes; corrupted/stale files fail rather than silently restarting or overwriting. A partial checkpoint requires explicit inspection and quarantine before retry. Completed valid samples are skipped. `--replay` recomputes statistics from checked aggregates; it is not a second raw-matrix scan. The parser deliberately rejects unsorted coordinates rather than risking undetected duplicates. CLI execution refuses to overwrite outputs.

Deutsch: Die neun Bibliotheken werden einzeln geprüft. Zellen zählen nicht als unabhängige Tiere. Der Vergleich nutzt acht vorab bestimmte Gene, dieselben Filtergrenzen wie das geprüfte Autorenskript und ungefilterte Kontrollauswertungen. Gesamte Leberbibliotheken vermischen Zellhäufigkeiten und Genexpression innerhalb der Zellen. Aus beobachteten Unterschieden folgt keine Arzneimittelwirkung. Die Befehle oben gelten unverändert. Bei Wiederaufnahme werden nur fehlende Proben verarbeitet; Hashfehler verlangen eine Prüfung. Eine lokale Wiederholung der Aggregatstatistik ersetzt keine unabhängigen biologischen Daten.

The MIT license covers our original code/report. No upstream R implementation, paper PDF, matrix archive, individual cell records or correspondence is included. See [third-party notices](../../THIRD_PARTY_NOTICES.md).
