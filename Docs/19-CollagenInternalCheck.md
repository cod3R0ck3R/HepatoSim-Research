# Collagen regression: internal comparison and mechanism limit

24 October 2026. Maintainer: **Johnnie 4 free**. AI-assisted computational research draft; no independent qualified human scientific review is claimed. [Frozen specification](../Research/CollagenCheck/specification-v1.json), [computed results](../Research/CollagenCheck/results-v1/result.json), [verification](../Research/CollagenCheck/verification.json), [reproduction](../Research/CollagenCheck/README.md).

## Question and evidence

Can early collagen regression describe a later group measurement, and can that identify a treatment mechanism? Hofer et al., [10.1002/ueg2.12643](https://doi.org/10.1002/ueg2.12643), Supplementary Table 2, supplies CCl4-specific CPA medians and quartiles after withdrawal. These are male C57BL/6JRj mice after twelve weeks of exposure, separate sacrifice groups at withdrawal and days 7/14, with a healthy control group. Group sizes are 6/7/7 and 5 controls. CPA is Picro-Sirius-red collagen-positive area as a percentage, not absolute collagen mass. The human alcohol-related cirrhosis cohort and the TAA groups from that paper are not analyzed here.

The existing source PDF and its numerical table were checked again. The reviewed input hash and source provenance are documented in [the access audit](15-ExternalDataAccess.md). No individual observations were reconstructed. The source PDF and extracted table remain local; this release adds original analysis code and derived analytical results, without relicensing source materials.

## Frozen test and executed result

The specification was saved and hashed before this new calculation. All table values had already been inspected in earlier work. Day 14 is excluded from fitting, but is **not an independent or blinded holdout**. Days 0 and 7 are development data; this is a retrospective internal temporal comparison. No criteria were changed after calculation.

Primary comparator: `C(t) = h + (C0-h) exp(-r t)`, with `h` fixed to the healthy median and `r = ln((C0-h)/(C7-h))/7`. Time is days after withdrawal; C and h are CPA percent; r is per day. The constant asymptote and exponential net decline are experimental assumptions. The fitted apparent net rate is 0.0795444/day. Its excess-CPA half-time is 8.714 days; this is not a healing time, a direct collagen turnover measurement or a clinical estimate.

| Prespecified comparator | Day-14 prediction, CPA % | Absolute error, percentage points | Relative absolute error |
| --- | ---: | ---: | ---: |
| Healthy-offset exponential (primary) | 6.04045 | 0.47045 | 8.446% |
| Zero-offset exponential | 5.90486 | 0.33486 | 6.012% |
| Constant day-0 level | 16.80000 | 11.23000 | 201.616% |
| Linear extrapolation | 3.12000 | 2.45000 | 43.986% |

The primary comparator beats the constant baseline by the frozen descriptive criterion. The simpler zero-offset alternative has a smaller error at this one point; it was not silently promoted to a validated model. There is no clinical success threshold or significance claim. There is only one later aggregate for comparison, so predictive performance across studies cannot be estimated.

All 27 combinations of lower quartile, median and upper quartile for healthy, day 0 and day 7 were evaluated. They give net rates 0.029803–0.122006/day and day-14 predictions 4.23145–10.53189% CPA. This is a sensitivity envelope over selected summary values, **not a confidence interval, a distribution of group medians or a posterior**. Measurement/sampling uncertainty cannot be reconstructed from these summaries alone. The healthy-offset assumption is separately challenged by the zero-offset alternative.

## Mechanism dossier: macrophage-associated matrix removal

**Evidence and scope.** Ramachandran et al., [10.1073/pnas.1119964109](https://doi.org/10.1073/pnas.1119964109), describes restorative macrophage states, matrix-degrading activity and phagocytosis-associated signaling in mouse injury-resolution experiments. The source supports investigating the mechanism, not assigning a numerical clearance effect to a human medicine. The previously analyzed E-MEXP-3177 expression groups differ in both time and phenotype; they do not supply a causal expression-to-CPA-rate calibration.

**Model representation and negative finding.** Even if excess CPA `X=C-h` were accepted as a collagen proxy, `production=qX` and `clearance=(r+q)X` produce the same `dX/dt=-rX` for every q≥0. Production and clearance are structurally non-identifiable from this trajectory. Moreover, area fractions can change with tissue geometry/denominator, so this balance is a simplifying proxy assumption, not a measured mass balance.

**Actual counterexample calculation.** Three arbitrary ratios q/r of 0, 1 and 4 reproduce the identical baseline curve. Increasing their clearance coefficients by the same hypothetical 25%, while holding production fixed, predicts day-14 CPA values of 4.76211%, 3.79441% and 2.08760%. These ratios are not biologically established plausible parameter bounds; 25% is not an estimated medicine effect. The calculation demonstrates why baseline fit alone cannot quantify a treatment benefit. It is not an intervention efficacy simulation.

**Testable hypothesis.** A restorative macrophage intervention might increase matrix removal after injury withdrawal. A discriminating research study would jointly measure collagen production, degradation/turnover and tissue-normalized collagen quantity, alongside macrophage phenotype and the appropriate untreated-withdrawal control. Prespecify a separate evaluation cohort and assess toxicity and ongoing injury separately. No animal dosing or clinical protocol is proposed here.

**Potential counterevidence.** Apparent regression may reflect reduced production or tissue geometry; macrophage expression changes may follow resolution rather than cause it; an intervention could affect inflammation and injury adversely. The proposed mechanism is not robustly quantified by the available aggregate CPA data. No named drug is assigned an efficacy percentage. No licensed indication, off-label use, human dose or patient-specific recommendation is asserted.

## Verification and next step

Five unit tests passed. Two analytic executions produced byte-identical result JSON; input, specification, code and output hashes plus environment are archived. This checks implementation/replay, not biological reliability. No ODE step-size error or Monte Carlo error is introduced; source rounding, aggregate sampling and model assumptions remain. No new Kappa publication-reproduction claim, independent biological validation, human transferability or clinical readiness is earned by this calculation.

The next informative input is a qualified dataset that distinguishes collagen formation from removal, preferably paired with absolute collagen/tissue-volume measurements and an independent cohort. Another unconstrained parameter sweep cannot replace it. Original reference-model observations still require a justified measurement mapping before comparison to CPA. This bounded package stops here rather than manufacturing a drug-effect estimate.

## Deutsch

**Frage und Quelle.** Können frühe Kollagenaggregate den späteren Gruppenwert beschreiben, und identifiziert dies einen Behandlungsmechanismus? Verwendet wird ausschließlich die CCl4-Mausreihe aus Hofer, Ergänzungstabelle 2: männliche C57BL/6JRj-Mäuse, zwölf Wochen Schädigung, getrennte Gruppen am Ende sowie 7/14 Tage danach (6/7/7 Tiere), fünf gesunde Kontrollen. CPA bezeichnet den Picro-Sirius-rot-positiven Flächenanteil, keine absolute Kollagenmasse. Menschliche ALD- und TAA-Daten werden nicht vermischt. Originalquelle und Tabelle wurden erneut abgeglichen; Originaldateien und extrahierte Tabelle bleiben lokal. Veröffentlicht werden eigener Analysecode und berechnete Auswertungen, ohne neue Lizenzbehauptung über Fremdmaterial.

**Prüfung.** Die neue Spezifikation wurde vor der Rechnung eingefroren. Sämtliche Messwerte waren jedoch bereits bekannt. Tag 0/7 dienen der Anpassung; Tag 14 bleibt davon ausgeschlossen, ist aber keine unabhängige oder verblindete Prüfung. Die obige Tabelle gilt unverändert für beide Sprachfassungen. Das primäre Exponentialmodell mit gesundem Sockelwert verfehlt Tag 14 um 0,47045 CPA-Prozentpunkte (relativ 8,446%) und ist besser als der konstante Vergleich. Das Modell ohne Sockelwert hat an diesem einzelnen Punkt sogar den kleineren Fehler. Keine nachträgliche Kriterienänderung, kein klinischer Erfolgsgrenzwert und keine Signifikanzbehauptung.

**Parameter und Unsicherheit.** Die experimentell angenommene Exponentialform ergibt eine scheinbare Nettoabnahme von 0,0795444 pro Tag und eine Halbwertszeit des überschüssigen CPA-Anteils von 8,714 Tagen. Das ist weder Heilungsdauer noch direkt gemessener Kollagenumsatz. Die 27 Quartilkombinationen liefern 0,029803–0,122006 pro Tag und Tag-14-Vorhersagen von 4,23145–10,53189% CPA. Diese Bereiche sind weder Konfidenzintervalle noch Wahrscheinlichkeitsverteilungen der Gruppenmediane. Mess- und Stichprobenunsicherheit bleiben ohne Einzelwerte unbestimmt. Das Modell ohne Sockelwert prüft eine alternative Strukturannahme.

**Mechanismus und Gegenbefund.** Die zitierte Ramachandran-Arbeit begründet die Untersuchung reparativer Makrophagen und ihres Matrixabbaus in Mausmodellen. Die bereits ausgewerteten Expressionsgruppen unterscheiden sich zugleich in Zeitpunkt und Phänotyp; eine kausale Umrechnung in Kollagenabbauraten fehlt. Selbst unter der vereinfachenden Annahme eines Kollagenproxies erzeugen Produktion qX und Abbau (r+q)X für jedes q≥0 dieselbe Nettokurve. Beide Anteile sind strukturell nicht getrennt bestimmbar. Änderungen der Gewebefläche können den CPA-Anteil außerdem beeinflussen.

**Berechnete Illustration.** Die frei gewählten Verhältnisse q/r=0, 1 und 4 passen dieselbe Ausgangskurve. Dieselbe hypothetische Steigerung des Abbaukoeffizienten um 25% ergibt dennoch 4,76211%, 3,79441% und 2,08760% CPA am Tag 14. Das sind mathematische Gegenbeispiele, keine biologisch belegten Parametergrenzen oder Arzneimittelwirkungen. Ein guter Ausgangsfit reicht deshalb nicht für eine quantitative Behandlungsvorhersage.

**Hypothese und nächster unterscheidender Test.** Reparative Makrophagen könnten nach Ende der Schädigung den Matrixabbau fördern. Aussagekräftig wäre eine gemeinsame Messung von Kollagenneubildung, Abbau/Umsatz, gewebebezogener Kollagenmenge und Makrophagenzustand mit passender unbehandelter Rückbildungsgruppe und vorher festgelegter unabhängiger Prüfkohorte. Toxizität und fortbestehende Schädigung separat erfassen. Gegenbefunde wären eine alleinige Produktionssenkung, Geometrieeffekte, nur nachfolgende statt ursächliche Expressionsänderungen oder unerwünschte Entzündung. Kein benannter Wirkstoff wird quantitativ abgebildet; keine Zulassungs-, Off-label-, Dosierungs- oder individuelle Behandlungsempfehlung.

**Prüfstatus.** Fünf Softwaretests bestanden; zwei analytische Ausführungen erzeugten byteidentische Ergebnisdateien. Prüfsummen und Umgebung sind dokumentiert. Kein RK4-/Kappa-Ersatz, kein neuer Publikationsreproduktionsnachweis, keine unabhängige biologische oder klinische Validierung. Ohne neue Daten zu Bildung und Abbau sowie eine begründete Zuordnung der Referenzmodellzustände zur CPA-Messgröße wird kein zusätzlicher Arzneimitteleffekt berechnet. Dieser KI-unterstützte Forschungsentwurf beansprucht keine unabhängige qualifizierte menschliche Fachbegutachtung. Maintainer: **Johnnie 4 free**.
