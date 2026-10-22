# HepatoSim Research

[Deutsch](README.de.md) · English

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

## Local Goose/Ollama

Use only the existing local Ollama provider. Confirm installed name, digest and loopback endpoint; a local URL alone does not prove local inference. The task driver rejects remote-model metadata and records a matching loaded GGUF model plus an actual local runner. One isolated task, no profile extensions, 300-second maximum, no automatic retry. No installation or persistent provider changes. Replace placeholders with actual installed values and use a fresh output folder. Reserve Ollama separately from KaSim/heavy builds. AI output must be reviewed and is not biological evidence; no token savings are claimed. Follow-up task: prepared and boundary-tested, not executed. The confirmed model blob is 8,988,113,226 bytes before runtime overhead; the shared host permits only 8 GiB per job. The coordinator declined a speculative increase. No local inference success is claimed. [Earlier timed-out attempts](Research/Reference/local-goose-audit.md).

The driver records `local_runner_observed` separately and never automatically sets `inference_verified`: even a zero Goose exit plus a loaded runner is insufficient. Review the model-to-runner match and the actually generated answer before confirming local inference. Four local-worker regression tests cover successful and failed mocked Goose exits; they do not invoke a model.

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

No open-source license has been selected for original HepatoSim code. Public visibility is not an open-source license. Separately included original models retain AGPL-3.0-or-later. No new license is granted over third-party material. Previous README content is preserved in `Docs/README-HSR001.md`; current progress is tracked in the research state file.
