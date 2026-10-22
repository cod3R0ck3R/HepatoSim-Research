# Mechanism pilot 1.3 — prospective protocol

Frozen on 22 October 2026, after the successful technical controls in report 13 and before any new mechanism-contrast result. This document records a planned experiment, not completed mechanism predictions.

Question: how do the original published reactivated-myofibroblast fate variants affect the collagen trajectory during repeated injury and after withdrawal? The mouse/CCl4-oriented scope, original Kappa source, pinned runtime, stimulus and collagen-token measurement remain as documented in the reference benchmark. This is a whole-course perturbation beginning at model time zero, not a drug first administered at withdrawal.

Three fixed seeds (101–103) compare the repository default, the original model without re-inactivation, and the original with-inactivation model with its weight set to 0.10. These are the first three seeds of the earlier unexecuted five-seed contrasts. This is explicitly a smaller pilot, not completion of that earlier experiment or a post hoc selection of successful trajectories. It was selected before observing any contrast output. Figure 2A/B/C of [Bouguéon 2024](https://doi.org/10.1371/journal.pcbi.1011858) motivates the scenarios. A published scenario is not a measured parameter uncertainty interval.

Primary readout: paired model collagen difference at day 240; secondary day-32/60/90 values and within-run withdrawal changes. The full frozen specification lists normalization, metrics, comparisons and limits. All declared seeds must complete before aggregate condition comparisons are reported. Opposite directions, zero effects and timeouts are retained. Three seeds cannot establish tail convergence, identifiable parameter intervals or robust treatment benefit. No new fitting, independent biological validation or drug-to-parameter mapping occurs.

## Budget and archive reuse

Six new simulations, each at most 900 seconds, 5400 seconds total, one worker and at most 100 MB output. Existing default seeds 101–103 and both completed technical controls are verified and reused; their historical compute cost is not charged as new work and they are not additional independent observations. Each command executes at most one missing run. Schedule each separately through the coordinator, so other projects can run between them. Declare 2 GiB RAM conservatively; this does not authorize an increase of the host's shared capacity limit. Failed, incomplete, changed or corrupt runs block automatic retry.

The v1.2 resume implementation is unchanged. A separate driver reuses its provenance/inspection helpers and the original KaSim runner, preserving the ability to replay v1.2 with its recorded code hashes. The new driver passed nine focused tests, including reuse of five real archived runs, changed-manifest rejection, no silent replacement of missing controls, refusal of partial work, cost/budget boundaries and one-run-per-invocation behavior. The latter uses an explicitly mocked worker in temporary storage; it is not evidence of a new biological simulation. Test process exit 0, 0.180 seconds; no new Swift build or rerun of the full research suite is claimed.

From the project directory, inspect without starting a simulation:

```sh
python3 -B Research/Reference/run_mechanism_pilot.py
```

After obtaining the coordinator's slot, execute one missing run:

```sh
python3 -B Research/Reference/run_mechanism_pilot.py --execute-one --kasim /absolute/path/to/KaSim
```

After the process and all child sessions have ended, inspect `Research/Reference/results/mechanism-v1.3/resume-state.json`. Exit 0 means that invocation completed its one run; remaining jobs may still exist. The ordinary reference analyzer can inspect this directory, with a new output file for each analysis. Do not run the old general batch entry point on this specification: that would recompute archived controls. Do not update a live runner or frozen specification.

## Deutsch

Vorab festgelegter Mechanismuspilot mit drei Seeds und zwei veröffentlichten Alternativen zur Defaultkonfiguration. Sechs neue Läufe, maximal je 900 Sekunden; fünf vorhandene Kontrollen werden geprüft wiederverwendet. Jeder Aufruf führt höchstens einen fehlenden Lauf aus und wird einzeln koordiniert. Neun gezielte Softwaretests bestanden; Mechanismusergebnisse liegen bei Protokollanlage noch nicht vor.

Geprüft wird eine Parameteränderung über den gesamten Verlauf. Das ist keine erst nach Schädigungsende beginnende Behandlung und kein Arzneimittelmodell. Unvollständige Ensembles werden nicht als erfolgreiche Teilstichprobe ausgewertet. Parameterunsicherheit, unabhängige biologische Vorhersage und klinische Übertragbarkeit bleiben getrennte offene Fragen.
