# Reproduction and database intake

Read `../../Docs/21-TAATransferAndEvidence.md` and the hashed specification first. These are retrospective internal checks, not clinical predictions. Input source materials are not redistributed.

From the repository root, with the locally downloaded Hofer PDF and its exact MarkItDown transcription:

```sh
python3 Research/Data/extract_hofer_cpa.py --toxin CCl4 --markdown Hofer.md --source-pdf Hofer.pdf --output CCl4.csv
python3 Research/Data/extract_hofer_cpa.py --toxin TAA --markdown Hofer.md --source-pdf Hofer.pdf --output TAA.csv
python3 Research/TAATransfer/analyze_transfer.py --ccl4 CCl4.csv --taa TAA.csv --spec Research/TAATransfer/specification-v1.json --output transfer-new.json
python3 -m unittest discover -s Research/Data -p 'test_*.py'
python3 -m unittest discover -s Research/CollagenCheck -p 'test_*.py'
python3 -m unittest discover -s Research/TAATransfer -p 'test_*.py'
python3 Research/TAATransfer/fetch_geo.py --output geo-new
python3 Research/Data/extract_decaris_collagen.py --abundance Decaris-S1.md --synthesis Decaris-S2.md --output collagen-new.json
```

Use the project's coordinator when configured. GEO download budget:450MiB and180s; partial files are not complete datasets. Archive headers only are checked. Hofer import checks exact source/transcription hashes; results refuse overwrite. Decaris importer requires the printed six-subject order and complete rows, preserving the two different synthesis units. Its input hashes must be checked against locally saved source receipts before scientific use.

For a reviewed private bundle, an existing app schema1 database and a new backup path:

```sh
python3 Research/Data/import_evidence.py --database research.sqlite --bundle evidence-bundle.json --backup research-before.sqlite
```

Bundle schema1 contains records with unique `id`, `kind` (source/dataset/analysis/search), `validation_scope`, `provenance`, and `payload`. Same content is skipped; altered content requires a new ID. Never pass correspondence or credentials. The evidence table is additive and is not yet shown by the app.

Read-only inspection:

```sh
sqlite3 research.sqlite 'SELECT id,kind,validation_scope FROM research_evidence_v1 ORDER BY id;'
```

Resume: verify the recorded result SHA256 and database receipt; rerun only missing acquisitions or checks into new outputs. Do not restart completed simulation work. Raw matrix analysis needs a separately frozen protocol after sample-level QC.
