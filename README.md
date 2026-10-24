# HepatoSim Research

[Deutsch](README.de.md) · English

## Current checkpoint — 24 October 2026

The bounded reanalysis of real macrophage expression data is complete: six samples, 241,576 probe sets, exact global permutation p = 0.10. Two executions matched byte for byte; 10 focused tests passed. Local Goose inference was verified, but its incorrect normalization suggestion was rejected. No new collagen prediction, drug efficacy or clinical validation is established. [Bilingual results](Docs/18-ExpressionReanalysis.md) · [Reproduce or verify completed results](Research/Expression/README.md). No automatic new computation is scheduled.

## Purpose

Research prototype for liver fibrosis mechanisms, reproducible simulations and teaching, aimed at researchers, developers and educators. The long-term clinical context is alcohol-associated liver disease (ALD). **Not a validated medical device, personal prognosis tool or treatment recommendation system.**

## Scientific components

The native Swift application contains a synthetic four-state demonstration model with RK4, hypothetical interventions, controls, sensitivity analysis, parameter sweeps and synthetic calibration. Laboratory/function proxies have no established clinical measurement mapping. A separate ALD catalogue contains published aggregate evidence; these observations do not calibrate the equations.

The independent Python adapter executes the original stochastic Kappa model of Bouguéon et al. (2024), concerning HSC populations and collagen tokens in a predominantly mouse/CCl4 context. It is not a human ALD or whole-liver model and has not been translated into RK4. [Model audit](Docs/09-DemonstrationModelAudit.md) · [Reference report](Docs/10-ReferenceBenchmark.md).

## Actual scope

Implemented: macOS and iPhone/iPad targets, SwiftUI charts/timeline, scenario editor, parameter inspector, numeric text fields with Tab/Shift-Tab alongside sliders, SQLite persistence, run JSON import/export, CSV result export, Markdown reports and a separate evidence view. CSV results cannot reconstruct a complete run. Synthetic medical-dataset exchange is a storage API, not a complete UI import workflow.

Experimental: publication reproduction, mechanism hypotheses and candidate dossiers. The research adapter remains separate from the app. Planned: complete secure plugin runtime, FHIR, research servers and clinical calibration. Plugin signing/isolation are specifications, not a finished manager. iOS does not execute arbitrary downloaded native code. No benchmark justifies Metal acceleration.

## Architecture and requirements

`Sources/HepatoCore`: models/evidence; `HepatoStorage`: SQLite/exchange; `HepatoUI`: shared SwiftUI. App and CLI entry points are separate. `Research/Reference`: frozen specifications, licensed original models, runners, analysis and results. `Research/Candidates`: dossiers. State and decisions persist in `RESEARCH_STATE.json`, `RESEARCH_PLAN.md` and `DECISIONS.md`.

Apps require Swift 6 and full Xcode with macOS/iOS SDKs; minimum deployment targets are macOS 14 and iOS 17. No third-party Swift package dependencies. Python 3 is required for research runners/tests, using the standard library. Matplotlib is optional for figures. KaSim is a separate pinned runtime; see [runtime-lock.json](Research/Reference/runtime-lock.json). The recorded x86_64 build ran on Apple Silicon. Other builds require explicit comparison. Historical Xcode 27/Swift 6.4 checks are documented; minimum OS versions and physical iPhones were not tested.

## Install and start the apps

Use a clean checkout and run commands from the project root. On coordinated hosts, follow the local coordinator instructions and wrap all builds/tests; do not bypass reservations or budgets. The macOS script prints the generated `.app` path: open that path. Alternatively select `HepatoSim-macOS` in Xcode and Run. Temporary build directories avoid observed Finder metadata/signing problems in synchronized Documents folders. Builds do not provide distribution signing, notarization or App Store approval.

For iPhone/iPad select `HepatoSim-iOS` and an available simulator/device in Xcode, then Run. A physical device requires your own signing team. To build for a simulator, use the command below.

```sh
./Scripts/verify.sh
./Scripts/build-macos.sh
open Apps/HepatoSim.xcodeproj
xcodebuild -project Apps/HepatoSim.xcodeproj -scheme HepatoSim-iOS -sdk iphonesimulator -destination 'generic/platform=iOS Simulator' -derivedDataPath /tmp/hepatosim-xcode-iOS -jobs 2 CODE_SIGNING_ALLOWED=NO build
```

## Usage and synthetic example

The app creates a synthetic example at first launch. Enter parameters directly or use sliders, then calculate and save. Changes affect the next run; invalid entries block calculation. macOS/iOS share code and schema, not an automatically synchronized database. Transfer runs as JSON. Data resides in the application's Application Support/container directory; existing run UUIDs are not overwritten.

Use a fresh output directory for the example below. The CLI checks deterministic sample replay and SQLite/JSON round-trips and writes scenario/control JSON, CSV, ensemble and sweep outputs. Seed 42 and the fixed configuration reproduce numeric samples; UUIDs/timestamps change. [Bundled examples](Examples/README.md) are synthetic, not patient data. Parameter-spread bands are not clinical prediction intervals. Printing this command does not claim a new successful run.

```sh
swift run --jobs 2 --scratch-path /tmp/hepatosim-example-build hepatosim /tmp/hepatosim-example-session
```

## Reference benchmark and resumption

The check command is read-only. Execution requires the pinned KaSim executable and a coordinator slot. Specification 1.2 reuses a verified historical baseline and runs only missing technical controls. Valid completed runs are skipped; partial/corrupt runs block automatic retries. Budget: one worker, two new runs, at most 900 seconds each and 1,800 simulation seconds total. Complete runs are the checkpoint unit; CSV does not preserve RNG state. Changes to an executing specification/runner are rejected. [Earlier benchmark and analysis instructions](Research/Reference/README.md). **Nine resume unit tests passed. Both real technical controls and an actual completed-run resume now pass; see [technical-control results](Docs/13-TechnicalControls.md).** A public export verifies its redacted baseline manifest against an explicit receipt; original private-path bytes are exporter-attested, not independently available. Numeric CSV payloads and frozen criteria remain unchanged. CSV comments are redacted; original and published trace hashes are recorded separately.

```sh
python3 -B -m unittest discover -s Research/Reference -p 'test_*.py'
python3 -B Research/Reference/resume_reference.py
python3 -B Research/Reference/resume_reference.py --execute --kasim /absolute/path/to/KaSim
```

The separately frozen [mechanism pilot](Docs/14-MechanismPilot.md) reuses verified controls and runs at most one missing contrast per invocation. Its driver passed nine focused software tests; no mechanism outcome is claimed by the protocol itself.

A later [external-data access audit](Docs/15-ExternalDataAccess.md) recovered separate Hofer CCl4 collagen aggregates. The reviewed importer passed six tests and ran on the source table. The exposure protocol and observation mapping still require qualification; no independent prediction test is claimed.

Two of six new contrast runs are complete; aggregate comparisons remain withheld. [Execution checkpoint and analysis checks](Docs/16-MechanismProgress.md).

**23 October update:** two later contrast attempts reached their 900-second limits; the remaining two were cancelled before starting. Both the original pilot and subset 1.3.1 remain incomplete. Partial traces are retained, with no aggregate treatment inference. [Timeout report](Research/Reference/mechanism-subset-timeout-2026-10-23.md). [Sato source triage](Research/Reference/sato2023-data-triage.md) identifies a withdrawal-study data request; [Jerez source triage](Research/Reference/jerez2026-data-triage.md) documents a successfully read ongoing-injury endpoint table whose units, normalization and animal/field mapping still need qualification. Neither is an independent validation result.

Inspect the preserved subset without starting a simulation. This command deliberately exits 1 because one run is incomplete; successful software rejection is not a successful benchmark:

```sh
python3 -B Research/Reference/run_mechanism_pilot.py --spec Research/Reference/benchmark-v1.3.1.json --output Research/Reference/results/mechanism-v1.3.1
```

## Local Goose/Ollama

Use only the existing local Ollama provider. Confirm installed name, digest and loopback endpoint; a local URL alone does not prove local inference. The task driver rejects remote-model metadata and records a matching loaded GGUF model plus an actual local runner. One isolated task, no profile extensions, 300-second maximum, no automatic retry. No installation or persistent provider changes. Replace placeholders with actual installed values and use a fresh output folder. Reserve Ollama separately from KaSim/heavy builds. AI output must be reviewed and is not biological evidence; no token savings are claimed. Follow-up task: prepared and boundary-tested, not executed. The confirmed model blob is 8,988,113,226 bytes before runtime overhead; the shared host permits only 8 GiB per job. The coordinator declined a speculative increase. No local inference success is claimed. [Earlier timed-out attempts](Research/Reference/local-goose-audit.md).

The driver records `local_runner_observed` separately and never automatically sets `inference_verified`: even a zero Goose exit plus a loaded runner is insufficient. Review the model-to-runner match and the actually generated answer before confirming local inference. Four local-worker regression tests cover successful and failed mocked Goose exits; they do not invoke a model.

Later execution update: a separately authorized one-off task using the installed `hermes3:8b` returned Goose exit 0 after 112.647 seconds. Its audit did not establish a matching local runner or verified inference. This supersedes the earlier “not executed” description for that specific task only; no inference-success or token-saving claim follows.

```sh
python3 -B -m unittest discover -s Research/LocalAI -p 'test_*.py'
python3 -B Research/LocalAI/run_local_task.py --model INSTALLED_MODEL --digest CONFIRMED_DIGEST --task Research/LocalAI/translation-task.txt --output /absolute/path/to/new-local-task
```

## Scientific status, sources and limits

The historical milestone completed 14/32 planned jobs, including ten default seeds; two timed out, sixteen were not started. It partially reproduced the qualitative collagen direction, with quantitative/source/runtime limitations. Historical records document 52 Swift and 74 research tests. The follow-up reference suite passed 82 tests; after export support, nine resume, three local-provider and four export tests passed. These counts overlap. The archived analysis was re-executed and matches except for its generation timestamp. [Current research report](Docs/11-ResearchFollowup.md). Seed replay is numerically exact for all 502 rows; both output grids are complete with zero difference at shared times. These are technical checks of one seed, not extra independent ensemble members. No independent biological validation, human transferability or clinical validity is established.

Stochastic variability, parameter uncertainty, measurement error and numerical reliability are distinct. Lower model collagen does not establish cure or restored liver function. Development data cannot be relabeled as independent. [Bouguéon 2024](https://doi.org/10.1371/journal.pcbi.1011858) · [pinned sources](Research/Reference/source-lock.json) · [candidates and negative studies](Research/Candidates/README.md) · [data gap](Research/Candidates/independent-data-followup.md) · [ALD evidence](Docs/08-ALD-Evidence.md).

The actual sanitized publication snapshot passed **90 research software tests**. Reanalysis preserved all scientific/numeric fields; all 18 CSV numerical payloads matched the local originals. Only timestamp/path/digest metadata changed. [Publication verification](Research/Reference/analysis/publication-verification-v2.json) · [test record](Research/Reference/analysis/software-tests-v2.txt).

## Safety, licensing and contributions

Use synthetic inputs and appropriately licensed public aggregates only. SQLite has no additional database encryption; platform protections do not authorize patient-data use. Do not submit secrets or identifiable health data. [Security](SECURITY.md) · [Contributing](CONTRIBUTING.md) · [Third-party notices](THIRD_PARTY_NOTICES.md).

Original HepatoSim code and original project documentation are licensed under the [MIT License](LICENSE), copyright 2026 Johnnie 4 free. Use, modification and redistribution, including commercial use, are permitted subject to retaining the license and copyright notice. Separately included original models retain AGPL-3.0-or-later. No new license is granted over third-party material. Previous README content is preserved in `Docs/README-HSR001.md`; current progress is tracked in the research state file.

## Collagen check and macOS prerelease preparation

Maintained by **Johnnie 4 free**. [The new internal collagen comparison](Docs/19-CollagenInternalCheck.md) passed five software tests and exact replay. It does not identify a treatment effect or provide independent biological validation. [Run the check](Research/CollagenCheck/README.md). The macOS packaging script produces a universal macOS research prerelease (launch tested on Apple Silicon) with ad-hoc signing; it is not notarized. The release is experimental, requires macOS 14 or later, and is not a medical product. No iPhone binary is included. Original HepatoSim code and this app release are now MIT-licensed; third-party terms remain applicable.

[macOS release verification / Prüfung](Docs/20-MacOSReleaseVerification.md).

## TAA transfer and evidence intake (24 October2026)

The fixed CCl4-to-TAA median transfer missed the predefined baseline criterion. Sixteen tests passed, and twelve reviewed evidence records were added locally without changing existing simulation runs. A2026 TAA single-cell archive and human collagen-synthesis tables were acquired. These are not clinical validation. See [report](Docs/21-TAATransferAndEvidence.md) and [reproduction/data intake](Research/TAATransfer/README.md).

## Nine-library GEO check (24 October 2026)

Nine real matrices were checked locally: 38,136 retained cells and all three group totals match the paper. Seven software tests and exact real resume/replay passed. SEMA4D–PLXNB2 warrants a cell-resolved follow-up; LMCD1 regression and CTSL patterns have important sensitivity limits. This is exploratory author-data reanalysis, not a drug-efficacy result. The local AI review remained resource-blocked and was not used. [Audit and mechanism questions](Docs/22-GEOSampleCheck.md) · [Reproduce/resume](Research/GEOSampleCheck/README.md).

## External SEMA4D–PLXNB2 check (24 October 2026)

A separate human NAFLD cohort supports increased SEMA4D RNA, but not the prespecified joint increase of SEMA4D and PLXNB2. All 216 count files were checked; 206 diseased biopsies informed the analysis. Five tests and exact cached replay passed. Local Goose inference ran; unsupported suggestions were rejected. [Results and limits](Docs/23-SEMAIndependent.md) · [Reproduce](Research/SEMAIndependent/README.md).

## GSE210077: donor/cell-type check (24 October 2026)

Six human donors and 27,692 annotated nuclei were analyzed by cell type. The joint macrophage-SEMA4D/HSC-PLXNB2 direction criterion failed. A post hoc shared-gene denominator check preserved that result; reference/condition confounding remains unresolved. Fourteen tests and both exact cache replays passed. [Report / Bericht](Docs/24-DonorCellCheck.md) · [Reproduce / Wiederholen](Research/DonorCellCheck/README.md).
