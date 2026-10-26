# HSC pre-laboratory verification: closed numerical checks and remaining gaps

26 October 2026 · [Deutsch](30-HSCPreLabVerification.de.md)

**Decision: no laboratory forwarding.** The new computational checks are complete. They support a larger retained inactive-cell pool under the chosen fate perturbation, but do not establish a reliable collagen reduction. A quantitatively calibrated treatment hypothesis is still unavailable.

## Frozen experiment and actual execution

HSR-HSC-ROBUST-001 v1.0.0, [specification](../Research/HSCRobustness/spec.json), SHA256 `d78f8f8bd71b82dc78e22da559e74078d79f420c34018c90a9cc846941c61a46`, extends [the previous milestone](29-HSCFateLabDecision.md). The original model commit is `773a84e65b514b969db20c57b6bf0ba97c1d32fb`. It represents mouse/CCl4-associated HSC plasticity through model TGFβ1 inputs, not human alcohol-associated disease or decompensated cirrhosis. Injury history is unchanged; the chosen reactivated-MFB inactivation fraction changes from 0.05 to 0.50 after model day 60, preserving its total exit hazard. Day 90 is the endpoint; output interval is 0.5 model days. COL1 is in original model units; iHSC and aSMA-cells are model-cell counts, not measured laboratory values.

Seven new fate contrasts (seeds 104–110) extend the earlier three to ten paired seeds. Ten previously inspected default-control simulations are reused; they are development simulations, not independent biological controls. Four additional runs compare control/fate contrasts at seeds 101–102 under an inactive-cell half-life of 30 rather than 730 model days after day 60. This is a deliberately chosen stress assumption, not an empirically estimated plausible range. No dose, medicine response or parameter posterior was fitted.

All 11 new KaSim processes returned exit 0 and reached day 90. Their summed wall times are 4153.706 seconds, within the frozen 6,600-second cap; two workers were used. Summed process wall time is not elapsed session time or CPU time. No simulations were retried. Calculations ran locally; no new Goose/Ollama inference is claimed.

## Results: ten paired seeds

Differences are scenario minus control. The bootstrap uses 20,000 resamples and seed 2026102603. These are exploratory finite-seed intervals under fixed parameters; they do not include measurement error, biological variation or parameter uncertainty. Small seed sets and prior inspection limit inferential scope. Shared seeds do not keep reaction paths identical after intervention.

| Observable | Mean difference | SD | Monte Carlo SE | 95% bootstrap interval | Positive / total |
|---|---:|---:|---:|---|---:|
| COL1 tot | -0.021666 | 0.052342 | 0.016552 | [-0.053339, 0.008783] | 4/10 |
| iHSC | 14018.900000 | 557.162942 | 176.190393 | [13717.595000, 14362.605000] | 10/10 |
| aSMA-cells | -38.800000 | 112.389996 | 35.540837 | [-106.902500, 25.200000] | 3/10 |

COL1 increases in four and decreases in six seeds. Its mean interval crosses zero; this is neither evidence of a reliable reduction nor proof of equivalence. The inactive-cell difference is positive in all ten seeds. The exact binomial 95% interval for a positive iHSC difference is [0.691503, 1.000000]; for COL1 it is [0.121552, 0.737622]. These refer to pseudorandom-seed outcomes, not response probabilities in patients. aSMA-cell changes also have mixed signs.

The seven newly executed fate contrasts are reported separately from the inspected pilot:

| Observable | Mean difference | SD | Monte Carlo SE | 95% bootstrap interval | Positive / total |
|---|---:|---:|---:|---|---:|
| COL1 tot | -0.014823 | 0.044753 | 0.016915 | [-0.044134, 0.016573] | 3/7 |
| iHSC | 14019.714286 | 605.294065 | 228.779652 | [13653.803571, 14472.571429] | 7/7 |
| aSMA-cells | -10.428571 | 97.450598 | 36.832864 | [-74.142857, 59.285714] | 3/7 |

## Alternative persistence assumption

| Seed | Observable | Difference, 730-day assumption | Difference, 30-day assumption |
|---|---|---:|---:|
| 101 | COL1 tot | 0.031917 | 0.053891 |
| 101 | iHSC | 14638.000000 | 10023.000000 |
| 101 | aSMA-cells | -26.000000 | 88.000000 |
| 102 | COL1 tot | -0.026078 | 0.094704 |
| 102 | iHSC | 13799.000000 | 9604.000000 |
| 102 | aSMA-cells | -25.000000 | 173.000000 |

The retained inactive pool is larger in both tested alternative pairs. COL1 is higher in both; seed 102 reverses direction relative to the original persistence assumption. aSMA-cell directions reverse in both. With only two pairs, stochastic variation cannot be separated reliably from the assumption's effect on signs. This is a warning against a robust treatment claim, not a global sensitivity result or a measured biological effect. Rechallenge and organ-function outcomes were not simulated.

## Verification and corrected failure

Nine focused tests pass. Complete half-day output grids, exact day-90 endpoints, pre-intervention agreement and imported pilot/control correspondence pass. Analysis of the private raw traces and of sanitized public traces is byte-identical in separate processes. The export removes only comment lines; parsed numerical rows match exactly. Completed-result resume was executed with subprocess creation forbidden and left every original result file unchanged. See [verification](../Research/HSCRobustness/verification.json), [resume](../Research/HSCRobustness/resume-verification.json), [results](../Research/HSCRobustness/results/analysis.json) and [reproduction commands](../Research/HSCRobustness/README.md).

The original checker rejected two completed alternative runs. Two `$PLOTENTRY` operations at the same event time expose the first parameter update before the second. The amended checker accepts exactly that intermediate row only at the first post-60 event, immediately followed at the identical time by the complete update and unchanged biological state. Original failed manifests and the executed checker remain intact, with separate revalidation receipts. No model, seed, effect threshold or endpoint changed. The original checker did not produce the final analysis; the corrected checker did. The [post-run amendment](../Research/HSCRobustness/export-amendment.json) makes this explicit. Regression tests reject a changed biological state, differing event time or missing completed update.

The coordinator lost a process-identity observation and marked the batch uncertain while its foreground descendants continued. After all children ended, their absence and all 11 manifests were checked, and the coordinator job was manually resolved as interrupted. The dependent analysis job was cancelled and a separately identified verification/export job ran successfully. This administrative status was not relabelled as a successful original coordinator run.

## What remains unresolved

| Evidence layer | Current status / requirement |
|---|---|
| Software and numerical checks | The stated controls and nine tests pass; eleven finished runs, two output-format revalidations preserved |
| Publication reproduction | Original rules and our runtime are pinned; exact author-environment identity remains unresolved |
| Calibration / parameter uncertainty | No empirical fit; the earlier conditional identifiability counterexample is not a global proof for full Kappa |
| Independent biological prediction | No matched independent joint cell-fate/matrix time series tested |
| Intervention mapping | No quantitative link from IL-10 or another intervention to the chosen fate/persistence parameters |
| Human transfer and clinical validation | Not established; no treatment efficacy or organ recovery claim |

The runtime audit confirms that our KaSim 4.1.3.1 release was published on 16 October 2024, after the paper dated 29 July 2024. The paper still states Kappa 4.2.12; the queried official tags did not contain that tag. A release note's Electron-version reference is only a clue and does not identify the authors' simulator. Required evidence is the author binary hash or simulator commit plus compiler/package lock and seeds. No replacement runtime was guessed or installed. [Source URLs, access failures and hashes](../Research/HSCRobustness/runtime-review.json).

The supplementary-data review was interrupted by an automatic service safety gate citing potential biological dual use. It was not completed or rerouted. Partial files were preserved privately and excluded from calibration and publication. No claim is made that they supply the missing joint measurements.

The next useful input is verified, jointly observed longitudinal cell fate, viable-cell counts, proliferation, matrix production/clearance and response after re-stimulation, with biological IDs and exposure metadata. A qualified review must resolve whether a candidate's effects map to these model parameters and whether function is preserved. The present computational tests cannot manufacture those observations. No laboratory was contacted, no laboratory work performed, and no forwarding authorized by this package.
