# ETS1 source-data audit / Quelldatenprüfung

Recomputes the Figure2B-to-2C Sirius-red normalization in Lee et al.2025, DOI10.1172/jci.insight.195242. This is an exploratory arithmetic check, not a drug or clinical model. See [bilingual report](../../Docs/27-ETS1SourceAudit.md).

Prerequisites tested: analysis Python3.15.1 (standard library only); conversion Python3.12 with MarkItDown0.1.7, pandas3.0.3, openpyxl3.1.5. No packages were installed for this iteration. Different converter output hashes intentionally fail rather than silently replacing inputs. Exact byte replay also records the Python version.

From the repository root, keep downloaded source data outside the checkout:

```sh
ets1_tmp=$(mktemp -d)
curl --fail --location 'https://df6sxcketz7bb.cloudfront.net/manuscripts/195000/195242/jci.insight.195242.sdval.xlsx' -o "$ets1_tmp/source.xlsx"
python3.12 -m markitdown "$ets1_tmp/source.xlsx" > "$ets1_tmp/source.md"
python3.15 -m unittest discover -s Research/ETS1Regression -p test_analyze.py -v
python3.15 Research/ETS1Regression/analyze.py --workbook "$ets1_tmp/source.xlsx" --markdown "$ets1_tmp/source.md" --spec Research/ETS1Regression/spec-v1.json --output "$ets1_tmp/result.json"
```

The input hashes are checked before extraction. The output file must not already exist. Tests use explicitly artificial fixtures, not synthetic replacements for biological evidence. `result-v1.json` contains observed derived results; `verification.json` records actual tests, separate-process replay and database integrity checks. `publication-redaction.json` explains removal of private quota metadata and proves unchanged numerical outputs. The frozen scientific criteria are retained.

Deutsch: Rechnet ausschließlich die angegebene Normalisierung nach. Originaldatei wird außerhalb des Repositorys gespeichert und anhand ihres Hashs geprüft. Testdaten sind künstliche Softwareprüffälle. Die Rechnung liefert keine Wirksamkeits- oder Heilungsaussage. Die publizierten Zahlen stimmen nach Entfernung privater Budgetmetadaten mit dem ursprünglichen Lauf überein. Die lokale KI wurde vor Ausführung wegen Ressourcenbelegung abgebrochen; siehe `local-worker.json`.

## Alternative-divisor control / Kontrolle anderer Nenner

See [bilingual follow-up](../../Docs/28-ETS1ScalingFollowup.md). Reuse the original source.xlsx retrieved outside the checkout above. The new frozen specification allows independent constant divisors per group and explicit rounding. Four additional tests and exact replay were executed. No source data are repaired.

```sh
python3.15 -m unittest discover -s Research/ETS1Regression -p test_scaling.py -v
python3.15 Research/ETS1Regression/check_scaling.py --workbook "$ets1_tmp/source.xlsx" --spec Research/ETS1Regression/scaling-spec-v1.json --output "$ets1_tmp/scaling-result.json"
```

Deutsch: Nutzt dieselbe zuvor extern gespeicherte Originaldatei. Prüft einen alternativen konstanten Nenner je Gruppe mit festgelegter Rundung, ohne Quelldatenänderung. Details, Grenzen und tatsächlich ausgeführte Prüfungen stehen im verlinkten Bericht.
