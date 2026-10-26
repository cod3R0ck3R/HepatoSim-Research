# HSC finite-seed and assumption follow-up

HSR-HSC-ROBUST-001. See [English report](../../Docs/30-HSCPreLabVerification.md) / [deutscher Bericht](../../Docs/30-HSCPreLabVerification.de.md).

Python 3 standard library; executed with Python 3.15.1 on macOS. Run from the repository root:

```sh
cd Research/HSCRobustness
python3 -B -m unittest -v test_check
python3 -B verify.py
```

`verify.py` checks hashes, complete output grids and endpoint arithmetic, then recomputes the analysis in a temporary copy and compares exact bytes. It needs no KaSim or external service. It preserves existing verification receipts and fails if they disagree. `executed-check.py` is the original checker used for simulation; `check.py` is the explicitly amended event/export checker. Original failures remain in two run manifests alongside their revalidation receipts.

The verified resume command for the supplied result is:

```sh
python3 -B check.py --run fate50-104 --kasim /absolute/path/to/KaSim
```

Use only the locally available executable matching SHA256 `ecff78d14fc6370ef6086b8c5cbcf1d5efd4d79b0a534c2b4d6e6849eef6d2f8`. The command verifies and reuses a completed result; it does not simulate again. Incomplete results are retained and cannot be automatically retried.

For a fresh bounded run, preserve the original checkout. In a separate copy retain sibling `HSCFate`, all frozen inputs and archives; move the copied `results` and `verification.json` aside. Run `python3 -B check.py --batch --kasim /absolute/path/to/KaSim`, then `python3 -B check.py --analyze`. This executes only the eleven specified jobs, two workers, at most 600 seconds each (6,600 summed seconds). Use the host coordinator when present; declare 4 GiB, respect admission, and do not bypass resource limits. Full runs are separate from the inexpensive replay above. Fresh run manifests and elapsed-time metadata will differ; no cross-platform bitwise reproducibility is promised.

All reported intervals describe stochastic seed variation at fixed parameters. The 30-day persistence corner is chosen, not measured. No empirical calibration, independent biological validation, drug efficacy or human transferability is established. No laboratory forwarding.

Own Python code follows the repository MIT license. Derived Kappa model files retain their original AGPL license in `models/LICENSE`; see [third-party notices](../../THIRD_PARTY_NOTICES.md).
