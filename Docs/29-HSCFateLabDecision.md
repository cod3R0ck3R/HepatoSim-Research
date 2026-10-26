# HSC fate and a discriminating laboratory question

26 October 2026 · [Deutsch](29-HSCFateLabDecision.de.md)

**Decision:** prioritize a mechanistic test of whether HSC reversion preserves a reactivation-prone population, rather than treating a fall in activation markers as proof of scar removal. IL-10 signalling is a candidate to investigate, not a quantitatively simulated medicine. This package does not establish efficacy against human cirrhosis.

## Computational question

The frozen HSR-HSC-FATE-001 experiment extends the original Bouguéon model [1]. It preserves the original stochastic Kappa rules, 10,000-cell scale and injury history. After nominal withdrawal at model day 60, one scenario changes the inactivation fraction of reactivated myofibroblasts from 0.05 to 0.50. Their complementary removal fraction changes from 0.95 to 0.50; the total exit hazard remains unchanged. This chosen sensitivity contrast is not a measured drug effect. Collagen, active cells and retained inactive cells must therefore be examined separately.

Three archived default seeds are previously inspected controls. New contrast seeds 101–103 and technical replay/grid controls are prespecified. The extra-observable control is compared to the original archive. The underlying context is mouse CCl4-associated fibrosis represented by TGFβ1 pulses. It is not an alcohol-associated human liver model. Collagen is in model units, not a clinical fibrosis percentage. The historical runtime discrepancy with the paper remains unresolved.

The separate exact calculation follows a mature, unbound, reactivated MFB through active→early inactive→inactive or removal. It assumes no new cell influx, proliferation or TGFβ1 rebinding. Across 135 chosen scenarios, fate fraction, exit half-life and inactive-cell persistence are varied separately. This calculation does not produce collagen and does not replace Kappa. Its tests include 100,000 stochastic waiting-time histories and independent quadrature; these are numerical checks, not biological replicates.

## Executed results and verification

All six prespecified KaSim jobs finished, using 1,724.847 seconds of local simulation wall time (28.75 minutes; the cap was 3,600 seconds). No parameter optimization was performed. This iteration used local executable calculations; no new Goose/Ollama inference is claimed.

Day 90 descriptive results are below. COL1 uses the original model's units; iHSC is a model-cell count. These three stochastic seeds are not animals or human donors.

| Seed | COL1 control | COL1 fate50 | Difference | iHSC control | iHSC fate50 | Difference |
|---|---:|---:|---:|---:|---:|---:|
| 101 | 3.251017 | 3.282935 | +0.031917 | 3201 | 17839 | +14638 |
| 102 | 3.161025 | 3.134947 | -0.026078 | 3167 | 16966 | +13799 |
| 103 | 3.169879 | 3.051145 | -0.118734 | 3109 | 16723 | +13614 |

The retained inactive population is larger in all three contrasts, by 13,614–14,638 model cells. The COL1 differences have mixed signs (−0.118734 to +0.031917); these runs do not establish a reliably lower collagen endpoint. No confidence interval or statistical equivalence is claimed from three seeds. Rechallenge was not run in this package: the larger reactivatable population motivates that experiment rather than proving an increased relapse outcome.

The instrumented control agrees exactly with the archived control at 197 shared times. Exact numeric seed replay passes. Output periods 0.5 and 0.25 days agree at 198 shared times; this checks observation sampling, not an ODE step-size approximation. The three histories before intervention each agree with their archived controls at 136 shared times. Seven tests pass. A fresh-process analysis on the sanitized export reproduces the analysis, 135-row conditional grid and identifiability result byte for byte. Completed-run resume reused the existing fate50-101 result without a new simulation. See [verification](../Research/HSCFate/verification.json), [all numerical results](../Research/HSCFate/results/analysis.json) and [resume receipt](../Research/HSCFate/resume-verification.json).

One preflight failed before KaSim started because a runtime file was an unavailable cloud placeholder; the already-local executable with the same required hash was used. The first completed control was initially classified as invalid because KaSim printed constant observable values instead of aliases. Only the parser was corrected. The failed manifest and explicit revalidation remain in the archive; model settings and acceptance limits were not changed. The actual runtime is KaSim 4.1.3.1, while the paper names 4.2.12. Its unresolved provenance difference limits the reproduction claim.

| Evidence level | Status for this package |
|---|---|
| Software/numerical verification | Specified tests, history, replay, grid and export checks passed |
| Publication reproduction | Original implementation extended; archive concordance shown; not a new full reproduction of every published figure |
| Parameter calibration | Not performed; fate50 is chosen, not fitted |
| Independent biological prediction | Not performed; no matched joint fate/matrix data available in this package |
| Human transferability | Not established; model, cell-study and disease contexts differ |
| Clinical validation | Not performed; no medicine efficacy, dose or treatment recommendation |

Parameter uncertainty is not estimated. The selected conditional grid explores assumptions, not a measured probability distribution; no empirical noise model is available. Matching random seeds does not preserve identical reaction paths after intervention. The original model's feedback, cell loss, matrix production and matrix breakdown should be tested jointly before attributing a real intervention to this parameter.

## Identifiability result

An independently frozen conditional diagnostic constructs three parameter combinations with exactly the same active and inactive fractions at day 30. Inactive-cell half-lives of 30, 365 and 730 days pair with fate fractions 0.843521, 0.511467 and 0.500000, respectively. Their predicted inactive fractions at day 90 differ: 0.122612, 0.436231 and 0.461758. These are theoretical counterexamples, not fitted patient or animal measurements, and not a parameter posterior. One endpoint cannot distinguish these combinations; earlier/later observations can. See [reproducible result](../Research/HSCFate/identifiability-result.json).

## Candidate and counterevidence dossiers

**IL-10 signalling / restoration of an inactive HSC phenotype.** Wang et al. [2], Fig. 7, report effects of IL-10 pathway perturbations on vitamin-A-related readouts in human hiPSC-derived multicellular liver cultures. Primary human HSC responses varied by donor. Activation-marker transcripts decreased while apoptotic markers also increased. Fig. 6 shows stronger restimulation responses after reversion; its reported n = 4 cannot safely be re-labelled as four donors. This supports testing cell fate and subsequent response together. It does not isolate the model's fate fraction or identify a rate constant. IL-10 was not simulated as a medicine; there is no evidence that it implements the chosen 0.05→0.50 parameter change. Context: HCV-associated and metabolic-stress cell systems, not a clinical cirrhosis intervention. Status on 26 October 2026: research mechanism; no specific medicinal product, formulation or approved indication is asserted. No new medicine-authorisation assessment or human dosing is provided.

**Indole-3-propionic acid (IPA).** Ilha et al. [3] combine an observational cohort with LX-2 experiments. Apoptosis and activation-marker changes coexist; figures 2/5 report three independent experiments, not three donors. This makes IPA useful for investigating whether an apparent inactivation signal is explained by cell loss. It is not a calibrated treatment arm here. The publisher's 5 May 2025 supplementary-file correction is acknowledged. The paper does not demonstrate reversal of established human cirrhosis.

**Preserved HSC function is a necessary countercheck.** Sugimoto et al. [4] show that broad HSC depletion and HSC-derived RSPO3 affect liver homeostasis and regeneration; Fig. 1b includes seven mice per group. Broad depletion is not the same intervention as selective removal of activated cells after withdrawal. The result nevertheless prevents an unqualified claim that removing more HSCs is better. Regeneration and injury/metabolism must be measured alongside matrix.

All three works postdate the 2024 model and provide independent mechanistic evidence. None is a matched independent quantitative test of this new fate-only perturbation. Kisseleva/Troeger 2012 were model antecedents and remain excluded from independent validation. Source text was checked through publisher/Europe PMC originals, with Scite used for discovery/metadata. Absence of a Scite notice is not proof that no editorial notice exists; the model's same-DOI 8 August 2024 version signal remains unexplained.

## Laboratory decision sheet — proposed, not executed

1. **Hypothesis:** increasing survival into an inactive state can lower basal activation markers while leaving a larger population capable of later reactivation. It need not accelerate loss of active cells or degradation of existing matrix.
2. **System and controls:** use an appropriately reviewed noninfectious HSC regression system with tracked previously activated cells, withdrawal-only and vehicle controls, and a time-matched initially quiescent comparator. Analyse distinct biological preparations/donors as the replicate unit; wells, fields and individual cells are nested observations. Do not import a mouse model day as a human culture time or choose sample size from simulation seeds.
3. **Primary measurements:** absolute viable lineage-tracked cell counts; active/inactive transitions over time; cell death and proliferation; newly produced collagen and pre-existing matrix separately. Report per-system and per-live-cell quantities. A transcript alone does not measure matrix clearance.
4. **Discriminating second phase:** compare response latency and activated fraction after a standardized noninfectious re-stimulation, controlling starting live-cell number and exposure. A persistent response difference supports cellular memory; disappearance after those controls weakens it.
5. **Function and counterfindings:** assess compatible hepatocyte function/regeneration readouts. Marker loss caused only by cell death rejects pure inactivation. In the isolated fixed-cohort subsystem, changing only fate leaves the active-state exit distribution unchanged. In the full model or a culture, aggregate active-cell counts can also change through proliferation, reactivation, ligand exposure or stochastic variation; faster net decline alone does not identify a changed exit rate. Lower collagen accompanied by impaired function is not a favourable treatment result.
6. **Next data needed:** jointly observed longitudinal cell fate, viability, proliferation, matrix production/clearance and rechallenge response, with biological IDs and exposure metadata. Estimate variance in a pilot before specifying power, meaningful effect sizes or equivalence bounds. GSE304675, GSE256398 and GSE256377 are source leads, not downloaded/calibrated treatment datasets in this package.

No laboratory work was performed. The proposal is an experiment-design brief, not an animal protocol, infection procedure, human treatment plan or claim of a new therapeutic discovery.

## References

1. Bouguéon, M., et al. (2024). *A rule-based multiscale model of hepatic stellate cell plasticity: Critical role of the inactivation loop in fibrosis progression*. PLOS Computational Biology 20(7), e1011858. DOI: 10.1371/journal.pcbi.1011858.
2. Wang, X., et al. (2026; online 2025). *Single-cell analysis of heterogeneity in reverted hiPSC-derived human hepatic stellate cells*. JHEP Reports 8(2), 101669. DOI: 10.1016/j.jhepr.2025.101669; PMC12803900, Figs. 6–7.
3. Ilha, M., et al. (2025). *Indole-3-propionic acid promotes hepatic stellate cells inactivation*. Journal of Translational Medicine 23, 253. DOI: 10.1186/s12967-025-06266-z.
4. Sugimoto, A., et al. (2025). *Hepatic stellate cells control liver zonation, size and functions via R-spondin 3*. Nature 640, 752–761. DOI: 10.1038/s41586-025-08677-w; PMC12003176.
