# Technical controls completed — HSR-002, 22 October 2026

This dated addendum supersedes only the pending technical-control status in report 11. Historical failures and the incomplete publication ensemble remain unchanged.

## Question, protocol and execution

Does the pinned original KaSim implementation reproduce the complete archived seed-101 trajectory, and does halving the output period change its observations? The frozen protocol is `Research/Reference/benchmark-v1.2.0.json`, SHA256 `a6e9726af786f37814eb873be75f3f1374b73b78a9a5321f8ed2b5ba734defa8`. No fitting, acceptance amendment or new biological data were involved.

Original model commit: `773a84e65b514b969db20c57b6bf0ba97c1d32fb`. Pipeline reference: `8b10a8dc403190a0b198918f0288b3d962ab7d40`. Runtime: KaSim v4.1.3.1, source `bafaeb8873cb4e4afd9b22ae312dc93724cfc2fa`, executable SHA256 `ecff78d14fc6370ef6086b8c5cbcf1d5efd4d79b0a534c2b4d6e6849eef6d2f8`. The paper's stated runtime identity remains unresolved. The Python runner and resume implementation match the published source at commit `5808b103fb1365c956fd39af8a4fa3fd58c4a7a8`; execution-environment files additionally record their source hashes. This is not a fresh Swift build.

The existing baseline was verified and copied. Two serial new runs finished with exit 0: seed replay in 652.616870 seconds and the quarter-day grid in 734.896099 seconds. Their total, 1387.512969 seconds, remained within the prespecified 1800-second budget and each within 900 seconds. Queue time is separate. Both covered model time 0–242.5 days; the original population, stimulus and end condition were retained. These timings are observations on a shared host, not performance benchmarks.

The coordinator classified the synchronously waited separate KaSim process groups as uncertain despite the command's exit 0. After confirming that the runner, supervisor, anchor and both KaSim PID/group users had ended, the owner manually resolved the reservation. Its administrative state is interrupted, not an invented successful dependency. Subsequent analysis and resume verification were separately registered light jobs and succeeded.

## Results and actual resume

| Prespecified check | Result | Scope |
|---|---|---|
| Exact seed replay | All 502 numeric rows and columns identical | One seed, fixed runtime/model/parameters; comments and UUIDs excluded |
| Output-grid coverage | 486/486 half-day and 971/971 quarter-day scheduled points present | Includes time zero through day 242.5 |
| Shared observations | 502 shared timestamps; maximum absolute difference 0 | Prespecified tolerance 1e-8; no missing scheduled points |
| Actual repeat of resume command | Exit 0; all three completed folders skipped | All six run-manifest/trace byte hashes unchanged; no new simulation cost |

The additional rows beyond scheduled output times originate from model event output. The comparison retains them. This tests output scheduling, not ODE integration step size, parameter uncertainty or convergence of stochastic distribution tails. The replay and grid run are not additional independent ensemble members.

Machine-readable evidence: [technical analysis](../Research/Reference/analysis/technical-v1.2.json), [actual resume verification](../Research/Reference/analysis/resume-verification-v1.2.json), and manifests/traces under `Research/Reference/results/technical-v1.2`. Use the resume commands in both READMEs with the pinned executable. Repeating them on these completed results verifies and skips work; a new independent execution requires a new output directory. The analysis command accepts that results directory and a new output filename. Files are never silently overwritten.

## Scientific limits and next decision

Software verification now includes these two completed technical checks and actual completed-run resume. Publication reproduction remains partial: the previously completed ten-seed default ensemble and incomplete alternative conditions retain their original status. There is no new parameter calibration, independent biological test, evidence of transfer to human ALD, clinical validation or demonstrated treatment effect.

Source inspection confirms that the two competing exits of a fully differentiated, ligand-free reactivated myofibroblast use complementary weights on the same half-life. Changing the inactivation weight changes fate allocation, not that pair's summed instantaneous exit hazard. The later inactivation-stage half-life is a separate transition. This conditional observation does not establish invariance of a whole collagen trajectory, which also depends on ligand dynamics, cell populations and reactivation. The original with/without-inactivation model files differ in these exit rules; they must remain separately identified.

The next mechanism study must freeze its contrasts, onset time, seeds, readouts and budget before execution. A parameter changed throughout injury is not a treatment started after withdrawal. Original-paper inactivation scenarios are sensitivity choices, not estimated uncertainty intervals or measured drug effects. Candidate dossiers remain qualitative and explicitly include negative trials. Local Goose execution remains blocked by the separately documented RAM budget; mock tests are not inference evidence.

## Deutsch

Seed-Replay und Ausgaberasterkontrolle wurden tatsächlich abgeschlossen und ausgewertet. Alle 502 Replay-Zeilen stimmen numerisch exakt überein; beide Raster sind vollständig, an gemeinsamen Zeitpunkten beträgt die größte Abweichung null. Die echte Wiederaufnahme übersprang alle drei geprüften Ergebnisordner ohne neue Simulation; Manifeste und Zeitreihen blieben bytegleich. Das neue Rechenbudget wurde eingehalten.

Damit sind diese technischen Prüfungen geschlossen. Publikationsreproduktion bleibt teilweise, unabhängige biologische Prüfung und klinische Validierung fehlen weiterhin. Ein Inaktivierungsparameter ist kein Arzneimittelmodell. Die nächste Mechanismusprüfung braucht ein eigenes vorab festgelegtes Protokoll; lokale Goose-Inferenz bleibt eine offene, ressourcenbegrenzte Anforderung.
