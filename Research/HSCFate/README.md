# Post-withdrawal HSC fate benchmark

Version HSR-HSC-FATE-001, frozen before new simulation outputs. Research use only.

This is a declared extension of Bouguéon et al. (2024), DOI 10.1371/journal.pcbi.1011858. It is not an independently biologically validated treatment model. Original Kappa rules and 10,000-cell scale are preserved. Derived model files retain their original AGPL-3.0-or-later license; the surrounding HepatoSim Python code follows the repository license. The copied run_benchmark.py is the existing trace/provenance helper, not a replacement solver.

## Reproduce and resume

Run from this directory with Python 3.10+ and the existing KaSim executable matching runtime-lock.json. No new dependencies are needed.

```sh
python3 -m unittest -v test_fate
python3 run.py --run control-101 --kasim /path/to/KaSim
python3 run.py --run fate50-101 --kasim /path/to/KaSim
python3 run.py --run fate50-102 --kasim /path/to/KaSim
python3 run.py --run fate50-103 --kasim /path/to/KaSim
python3 run.py --run replay-101 --kasim /path/to/KaSim
python3 run.py --run grid-101 --kasim /path/to/KaSim
python3 run.py --analyze
```

On a host with a coordinator, run every command through that coordinator and declare one worker. Run each job separately. A successful existing result is hash-checked and reused. An incomplete/failed result is retained and blocks automatic retry. Do not delete it to obtain a favourable run. Never resume a stochastic model from its CSV observations. The six-run budget is 3,600 simulation seconds, 600 per job. Queue time is separate; no detached work.

## What changes

The control adds observables only. The fate50 scenario additionally changes the reactivated-MFB inactivation fraction from 0.05 to 0.50 after model day 60, after the last injury pulse at 56.5. Its complementary removal fraction remains 1 minus that fraction. The total exit hazard is unchanged. This is a chosen sensitivity scenario, not an inferred drug effect. Three archived default trajectories have exact provenance checks and are previously seen controls, not independent data. Day 90 collagen, active cells and fully inactivated HSCs are the primary descriptive outcomes; early inactive cells and TGFbeta pools expose measurement/assumption limitations.

The separate component calculation conditions on a mature unbound reactivated MFB with no incoming cells, proliferation or TGFbeta rebinding. It computes A→E→I and removal exactly, then checks the result against stochastic waiting times and quadrature. It does not calculate collagen or replace the Kappa model. The 135 parameter-grid rows are deliberately selected scenarios, not an empirical uncertainty distribution.

## Interpretation

Identical seed numbers do not guarantee identical reaction paths after perturbation. Technical replay and grid checks must be examined separately. Three seeds cannot establish equivalence, distributional convergence or clinical efficacy. Source papers provide mechanistic support unless specifically qualified as independent test data. No human doses, restored organ-function estimates or cure probabilities are produced.

The proposed laboratory distinction is whether lower activated-cell markers reflect faster removal from the active state, a different fate after exit, or both. Measure retained lineage-labelled cells and extracellular matrix separately; test later reactivation in a separately designed experiment. No drug is assigned an arbitrary efficacy percentage.

## Conditional equations and units

Time is in days; A, E, I and R are probabilities per initially mature unbound reactivated MFB. Rates k=ln(2)/h_exit, mu=ln(2)/h_early and delta=ln(2)/h_inactive have units day^-1. Fate fraction f is dimensionless in [0,1]. The conditional equations are:

- dA/dt = -k A
- dE/dt = f k A - mu E
- dI/dt = mu E - delta I
- R = 1 - A - E - I

A(0)=1, E(0)=I(0)=R(0)=0. For distinct positive rates, A=exp(-kt), E=fk[exp(-kt)-exp(-mu t)]/(mu-k), and I=fkmu times the sum, over r in {k,mu,delta}, of exp(-rt) divided by the product of (s-r) for the other two rates s. Equal-rate limits are deliberately outside the frozen grid and rejected by the implementation.

R means exit from the tracked active/inactive compartments; it includes commitment to apoptosis/senescence. The original model's short terminal clearance phase is collapsed here. R must not be interpreted as an instantaneous count of physically dead cells. No new cell input, cell division or ligand binding is represented in this conditional calculation.

The original exit half-life 3.54 days, early-inactive half-life 0.75 days and inactive half-life 730 days are model estimates/assumptions, not newly measured human constants. Alternative half-lives and fate fractions are an explicitly chosen sensitivity grid, not inferred credible ranges. The 100,000-lineage stochastic check uses seed 20261026 and a 5-binomial-standard-error numerical tolerance; it is unrelated to clinical accuracy.

The additional identifiability diagnostic is separately frozen in identifiability-spec.json. It constructs theoretical endpoint-equivalent parameter sets; it does not estimate biological parameters:

```sh
python3 identifiability.py
```

Public CSV copies omit KaSim comment headers containing machine paths. public-trace-map.json records original/published file hashes and equality of parsed numerical payloads. No rows, seeds or outcomes are removed. Results and explicit revalidation receipts are preserved separately from private runtime logs.

`python3 verify.py` verifies all six runs, the initial time, source hashes and controls, then reruns the analyses and tests in a temporary copy. It compares result bytes and preserves the original results.

## Completed package

Six KaSim runs completed in 1,724.847 seconds. Seven tests, exact seed replay, shared-grid and pre-intervention checks passed; the sanitized export reproduced all analyses byte for byte. The three-seed collagen contrast has mixed signs while the retained inactive-cell pool increases. These are exploratory model results. Read the [English laboratory brief](../../Docs/29-HSCFateLabDecision.md) or [German laboratory brief](../../Docs/29-HSCFateLabDecision.de.md) before interpreting an intervention.

The public snapshot already contains completed runs. The commands above validate and reuse them. For a fresh simulation, create a separate checkout/copy that omits results, retain this archived evidence, then execute the six commands sequentially; do not overwrite a failed or completed run. The verification command itself needs only Python and runs no new KaSim process.

`evidence-bundle.json` is the append-only, versioned research record. Its local database import and idempotent replay are summarized in `database-receipt.json`; the user's database and its backups are not distributed.
