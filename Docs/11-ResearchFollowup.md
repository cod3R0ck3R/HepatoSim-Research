# HSR-002: checked continuation, 22 October 2026

This is an interim research release, not completion of the full milestone. It preserves HSR-BG2024-001 and its negative/incomplete findings. The immediate research question remains whether the original HSC model reproduces collagen accumulation and regression and can predict a separately qualified experimental dataset.

## What actually ran

The original KaSim data were reanalysed using `Research/Reference/analyze_benchmark.py`; `Research/Reference/analysis/archive-recheck-v2.json` matches the historical analysis in every top-level field except the generation timestamp. No new simulation values were invented. The default ten-seed ensemble is complete; the other prespecified conditions remain incomplete. The comparison is computational reproduction of an analysis, not an independent biological experiment.

The reference suite ran 82 tests successfully. Following the explicit public-manifest support change, all nine resume tests passed. Three local-provider boundary tests and four publication-export tests also passed. These counts overlap: the original reference suite already included eight resume tests. The central coordinator marked the first suite's synchronously waited separate test-process sessions uncertain, then manually resolved its ended process tree; the actual test process exited zero. No failing scientific test was relabelled successful.

No new Swift build is claimed; historical checks remain in report 07. No UI source was changed in this follow-up.

## Technical controls and real resource boundary

`benchmark-v1.2.0.json` is frozen before new simulations. It retains one verified archived default seed101, plans an exact numeric replay and a 0.25-day output-grid control, with one worker and at most 900 seconds per new run / 1,800 seconds total. The existing 0.5-day reference is compared on the complete common grid at absolute tolerance 1e-8. This checks stochastic output scheduling, not ODE solver step size.

The coordinated execution was queued and explicitly cancelled **before start** because host memory pressure remained elevated. No new KaSim execution occurred and no simulation budget was consumed. The next executable step is the resume command below, once the coordinator admits it. Do not weaken the resource gate, use an unregistered shell, or count a queued command as a result.

```sh
python3 -B Research/Reference/resume_reference.py
python3 -B Research/Reference/resume_reference.py --execute --kasim /absolute/path/to/KaSim
```

The first command is read-only. The tested resume logic skips verified completed runs, retains incomplete or corrupt folders, rejects changed runners/specifications, and accounts for prior completed/timeout costs. A real completed-control resume still requires the pending computations. CSV files are not RNG checkpoints.

## Local AI: verified installation, no new inference claim

The installed Ollama 0.40.8 metadata confirmed `michaelneale/deepseek-r1-goose:latest`, digest `425664f4d9986cb323c8df05ad0e4c375c5d57bb157191898ae0bff438d7f20b`, local GGUF Qwen2 14.8B Q4_K_M, with no remote host/model metadata. The loopback service was reachable and no model was loaded. This establishes installation, **not actual inference**.

The planned isolated Goose translation has a 300-second limit, one worker, no retry, explicit local provider and no extension profile. The 8,988,113,226-byte model blob alone exceeds the shared host's 8 GiB job budget before runtime/KV memory. The coordinator declined a speculative increase. No model download, provider change, smaller substituted model or cloud fallback was performed. Runtime/token consumption for this unstarted task is unavailable, not an estimated saving. Earlier timeout attempts remain documented separately. The milestone's successful reviewed local task requirement is still unmet.

## Mechanism and candidate findings

Three dossiers cover PPARγ/HSC inactivation, HSP47/collagen synthesis and LOXL2/matrix crosslinking. Their primary references, species, causes, stages, regulatory scope, safety observations, negative trials and distinguishing experiments are listed in `Research/Candidates`. Important counterevidence includes no fibrosis benefit in FLIRT, the terminated BMS-986263 NASH cirrhosis study, and negative simtuzumab trials.

The original Kappa inactivation weight also changes a complementary apoptosis/senescence branch. Its two collagen pools do not explicitly represent HSP47 or LOXL2 kinetics. No measured intervention-to-parameter mapping is available. Therefore none of these dossiers claims a quantitative drug simulation. A robust ranking across uncertain parameters and alternative model structures has not yet been calculated. A favourable arbitrary parameter perturbation would not repair this evidence gap.

The most discriminating next experiment measures HSC inactivation and death separately, together with new collagen synthesis, total matrix and regression after a controlled injury stop. A later re-stimulation distinguishes a retained primed cell pool from durable removal. These are research proposals, not patient recommendations.

## Independent data and scope

No suitable independent collagen time course has been qualified. Original-author development sources are not held-out tests. The attempted Hofer supplement response was not a PDF, and the checked OA resolver returned 404; pooled CCl4/TAA summaries do not isolate the needed CCl4 trajectory. Liu2020 supplies mechanism-development evidence and cannot now serve as an untouched validation set for that candidate choice. Required next data include species, toxin exposure/withdrawal schedule, collagen method/units, timepoints, group sizes, variability and prior model-development use. See the dated source register and independent-data follow-up.

| Claim category | Supported scope |
|---|---|
| Software verification | Reported tests and unchanged archived-analysis values; fresh control runs pending |
| Publication reproduction | Historical partial reproduction; original stochastic Kappa implementation |
| Parameter calibration | No new biological calibration or identifiable posterior |
| Independent biological test | Not performed; dataset/mapping gap remains |
| Transfer to humans | Not established; mouse/CCl4-oriented model is not human ALD |
| Clinical use | Not established; no clinical decision, dosing or cure claim |

## Publication provenance

The public project repository was created in Safari under the confirmed GitHub account. The repository commit/push receipt is recorded separately from this pre-push report. The public snapshot excludes caches/builds/databases, private worker and runtime logs, generated model snapshots, local full-text review copies and browser screenshots. Vendor model files and their original AGPL notices remain byte-for-byte intact. Own-code licensing is undecided: public visibility is not an open-source license.

The exporter preserves numeric CSV payload bytes and frozen specifications. KaSim CSV comments also contained local command paths; only those comments are redacted, so complete-file trace hashes change and are recorded separately. Original-digest claims in historical analyses refer to the private originals; fresh public analyses refer to the published traces. It replaces local path prefixes and host identifiers in JSON metadata, records original/published file digests, and produces a per-run manifest-redaction receipt. The receipt verifies public bytes and attests to the withheld original digest; it does **not** make private path strings independently reconstructable. The original archive remains local and unchanged. This limitation is explicit in resume provenance. New Git history must be inspected separately before push.

## Deutsch: geprüfter Stand

Die historische Auswertung wurde tatsächlich neu gerechnet; nur ihr Erstellungszeitpunkt änderte sich. Referenzsuite: 82 erfolgreiche Tests; nach der Exportergänzung neun gezielte Resume-Tests, außerdem drei Providergrenzen- und vier Exporttests erfolgreich. Die Testzahlen überschneiden sich. Neue KaSim-Kontrollen wurden wegen Speicherdruck vor Start aus der Queue genommen; eine erfolgreiche echte Wiederaufnahme abgeschlossener neuer Kontrollläufe ist daher noch nicht belegt.

Das vorhandene lokale DeepSeek-Modell samt Digest wurde bestätigt. Der geplante Goose-Auftrag wurde wegen des zentralen RAM-Budgets nicht gestartet; keine erfolgreiche lokale Inferenz wird behauptet. Drei Kandidatendossiers enthalten überprüfte Mechanismusbezüge und negative klinische Befunde. Quantitative Arzneimittelabbildungen und unabhängige biologische Prüfdaten fehlen. Diese Zwischenveröffentlichung schließt den Forschungsmeilenstein nicht ab. Modelliertes Kollagen ist kein Heilungs- oder Leberfunktionsnachweis.

## Publication-snapshot verification addendum

The actual sanitized snapshot passed all 90 research software tests in 5.595 seconds (process Exit0). All 18 CSV numeric payloads matched the original local files. Reanalysis changed only 101 timestamp/path/hash fields; all scientific and numerical fields remained equal. The explicit checks are recorded in `Research/Reference/analysis/publication-verification-v2.json`; the newly calculated public analysis is `public-recheck-v2.json`. Both README language versions have matching shell-command blocks and existing local links. No new clinical or biological validity follows from these checks.
