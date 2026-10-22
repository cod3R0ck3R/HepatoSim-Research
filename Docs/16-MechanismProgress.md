# Mechanism pilot: execution checkpoint

22 October 2026. This is an incomplete execution checkpoint, not a completed treatment experiment. The prospective protocol remains [report 14](14-MechanismPilot.md), specification 1.3.0, with three fixed seeds per condition.

Two original-model runs without re-inactivation completed (seeds 101 and 102). Each returned exit 0 with a verified trace hash and eligible observations through the declared horizon. Runtime was 330.305465 and 705.433327 seconds respectively. Both stayed within the unchanged 900-second per-run limit. Four new contrast runs remain; five verified historical runs are reused, not counted as new independent replicates.

The new analysis file `Research/Reference/analysis/mechanism-progress-2.json` records individual runs and missing jobs. Both between-condition summaries are deliberately withheld. The legacy analyzer previously required five paired seeds even for this three-seed protocol. Its small correction takes the explicitly declared seed set for the mechanism pilot, retaining the legacy five-seed default. Three new arithmetic/boundary tests and 47 existing analysis tests passed. The actual partial-result analysis also ran successfully and confirmed the expected withholding. Frozen model, input, runtime and execution-driver bytes remain unchanged; no threshold or outcome selection was introduced.

The coordinator initially retained each job because KaSim intentionally starts a separate process session. Administrative completion was resolved only after checking the recorded process identities, their groups and descendants, the synchronous `wait` contract, exit status and resulting files. A completed numerical run and an administrative `interrupted` status after manual resolution are different records, both preserved. No simulation was repeated to obtain a more convenient coordinator status.

## Scientific interpretation

No aggregate mechanism benefit is claimed from two surviving runs. The eventual complete comparison concerns whole-course allocation of reactivated-myofibroblast fates, including the injury phase. It is not an intervention started after withdrawal. Neither stochastic seed spread nor the published 0/0.05/0.10 scenarios establish calibrated parameter uncertainty. PPARγ, HSP47 and LOXL2 dossiers retain their mechanistic and clinical limitations; no drug-to-parameter mapping has been inferred.

Software verification: focused tests and executed integrity/analysis checks. Publication reproduction: still partial, with known source/runtime ambiguities. New parameter calibration: none. Independent biological prediction: not performed; [new data access evidence](15-ExternalDataAccess.md) narrows the remaining gap. Human transferability and clinical use: not established.

## Deutsch

Zwei der sechs neuen Kontrastläufe sind vollständig und auf Integrität geprüft. Vier fehlen. Der Zwischenbericht enthält deshalb keine aggregierte Behauptung über eine Behandlung. Beide Kontrastzusammenfassungen werden zurückgehalten. Die kleine, getestete Analysekorrektur verwendet die vorab festgelegten drei Pilot-Seeds; ältere Auswertungen behalten ihren Fünf-Seed-Standard. Modelle, Eingänge, Runtime, Runner und Grenzwerte wurden nicht geändert.

Die manuelle Freigabe der Koordinatorressourcen erfolgte erst nach nachgewiesenem Prozessende. Numerischer Abschluss und Verwaltungsstatus bleiben getrennt dokumentiert. Keine neue Parameterschätzung, keine unabhängige biologische Vorhersageprüfung und keine klinische Validierung. Weiterarbeit erfolgt mit dem bestehenden Einzellauf-/Resume-Befehl und dem verbleibenden ursprünglichen Rechenbudget.
