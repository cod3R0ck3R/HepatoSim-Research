# Mechanism subset 1.3.1: bounded execution stopped after timeout

Checked 23 October 2026. This follows the explicitly post-timeout amendment in `mechanism-continuation-2026-10-22.md`. It is a computational feasibility result, not an independent biological test.

## Prespecified question and execution

Subset 1.3.1 asks for a complete default-versus-10-percent reinactivation comparison using seeds 101–103 and unchanged original Kappa rules. The whole-course parameter contrast is not a drug intervention. Specification SHA-256: `27db7236e8b8e0749597c87d8404accfad67290aec2d866468b84de736b2a08d`. The existing runner, resume helper, original model and pinned executable were retained. Runtime: KaSim bafaeb8 / release v4.1.3.1, executable SHA-256 `ecff78d14fc6370ef6086b8c5cbcf1d5efd4d79b0a534c2b4d6e6849eef6d2f8`; its exact equivalence to the publication’s stated runtime remains unresolved.

The coordinator executed only `reinactivation_10pct-101`. Its manifest records start `2026-10-22T21:43:33.401970+00:00`, seed 101, reinactivation override 0.1, 0.5-day output period and duration limit 243 model days. The frozen per-run wall-time limit was 900 seconds, one worker and 2 GiB declared RAM.

## Actual result

The run reached the limit and ended after 900.0925867500482 seconds. The runner sent SIGTERM to its KaSim process group and synchronously waited; the saved return code is -15 and status is `timeout`. The retained trace has 103 data rows and ends at model day 45, before the required complete endpoint. Trace SHA-256: `51757cf6f081eb922ab73a8f3797a9f5d38291a6874a26196c0cd8e6b3c9272e`.

The original read-only inspector was actually rerun through coordinator job `hepatosim-subset131-readonly-audit-20261023`. Exit 1 is the expected rejection of an incomplete result: the three reused default runs and two technical controls are eligible; seed 101 in the 10-percent condition is `not_completed`; seeds 102 and 103 are missing. No simulation was launched by this check. Input, executable, runner and trace hashes were checked against the frozen environment; none was changed.

Both never-started dependent queue entries were cancelled before administrative resolution. No seed was replaced, no timeout enlarged, and no partial trajectory was used as an RNG checkpoint. The three-condition pilot 1.3.0 and the two-condition subset 1.3.1 both remain incomplete. Aggregate mechanism comparisons are withheld.

## Process-end verification

The coordinator flagged the KaSim session because its process group differed from the anchor group. The inspected runner deliberately uses a new session, then performs `wait`; the inspected supervisor retains its conservative group-escape flag even after its tracked live-process set is empty. This explains the administrative `uncertain` state separately from the scientific timeout.

The end audit checked the current boot identifier against the saved job, the saved supervisor/anchor start identities, current PID presence, group membership and descendants, other KaSim users, executable-path matches, and open files under the run directory and executable. No remaining user was found. A second process check agreed. The original microsecond start tuple for the detached KaSim PID was held only in supervisor memory and was not persisted; no retrospective value is fabricated. The retained group-escape event, synchronous wait return code and normal supervisor completion provide the additional lifecycle evidence.

The existing reservation was manually resolved to **interrupted**, preserving its execution exit code 1. This is not successful simulation completion. The full private lifecycle proof remains at `work/research-v2/diagnostics/subset131-101-end-proof-20261023.json` in the workspace; no raw process inventory or coordinator token is published.

## Interpretation and next step

The current runtime and budget did not yield this complete trajectory. Host contention or model/runtime cost may contribute, but this audit does not identify the cause. No extrapolation of the partial curve or runtime to the full horizon is justified.

Before another simulation series, define a separate bounded runtime-feasibility diagnostic and budget. Preserve the original model, seed and observation requirements; inspect event cost and host load before deciding whether a different runtime or budget is justified. A runtime replacement needs its own equivalence checks. Do not automatically retry this run. Independent work can inspect the already queued Jerez source-data conversion and assess measurement mapping.

Software verification: hash and incomplete-run rejection checks performed. Publication reproduction: still partial. Parameter calibration: not performed here. Independent biological prediction: not performed. Human transferability and clinical validity: not established. This timeout supplies no evidence for or against a treatment mechanism.
