# Measured macrophage expression / Gemessene Makrophagenexpression

HSR-EXPR-001, 24 October 2026. Exploratory analysis; no treatment efficacy claim.

## English

### Question, evidence and frozen test

Do the available expression measurements distinguish the two macrophage sample groups, and how sensitive are descriptive contrasts to individual samples? This is a narrower question than predicting collagen regression. The source is Ramachandran et al. (2012), accession E-MEXP-3177: male mouse liver macrophages after CCl4 injury, three biological array replicates at each of 24 and 72 hours. The paper describes different sorted phenotypes (24 h Ly-6Chi versus 72 h Ly-6Clo). Time and phenotype are confounded; individual-animal pooling/batch relationships are not established by the intake metadata. Six arrays are not six longitudinally followed animals.

The newly available material was obtained from a public repository after a literature suggestion. It is not a privately supplied collagen dataset. The matrix contains **241,576 probe sets and 1,449,456 measured, finite values**. Values are author-normalized RMA log2 microarray intensities, not raw sequencing counts. No renormalization, feature selection, gene annotation or figure digitization was performed. A probe set is not necessarily a distinct gene. The source was already cited by the reference-model authors and inspected during intake; it is exploratory development material, not untouched independent validation data.

Before statistical calculation, [specification 1.0.0](../Research/Expression/specification-v1.json) fixed input hashes, sample assignments, tests, interpretation and resource limits. Its SHA-256 is `506bf80c9dcd1426fbade4aeb62bf11f56d7ab0ef374936fde22725f281a2e10`. Prior inspection had included dimensions, source methods and a few matrix rows; this is not a blinded preregistration.

The primary statistic is an unscaled Euclidean pseudo-F across all probe sets: between-group sum of squares divided by within-group sum of squares / 4 (degrees of freedom 1 and 4). Every one of the 20 labelled 3-versus-3 allocations is enumerated. The upper-tail fraction includes the observed allocation and its complementary labelling. This conditional permutation calculation assumes exchangeability, which the source metadata cannot establish. There are only ten distinct unlabelled partitions: the smallest attainable p is 0.10. No 0.05 success criterion, clinical accuracy threshold or fitted model was introduced.

### Actual result

| Quantity | Result |
|---|---:|
| Global pseudo-F | 1.9259350402 |
| Exact upper-tail allocation fraction | 2/20 = 0.10 |
| Probe sets with mean(72 h) − mean(24 h) ≥ 1 log2 unit | 15,279 |
| Probe sets with difference ≤ −1 log2 unit | 10,000 |
| Total absolute difference ≥ 1 | 25,279 / 241,576 = 10.4642% |
| Direction retained after omitting one sample from each group | 99.38–99.83% of those 25,279 probe sets |
| Absolute difference ≥ 1 retained under the same omissions | 69.13–87.33% |

The observed grouping and its complement have the highest global statistic among these allocations. This does **not** establish a causal time effect, a drug effect, absence of batch effects, or a 90% probability of a biological hypothesis. The exact p does not reject at 0.05, and its coarse resolution does not establish absence of biological differences. No probe-level significance tests or adjusted gene-level p-values were calculated. The original publication used a different gene-level analysis; this is not a reproduction or refutation of its reported differential-expression list.

An absolute log2 difference of one denotes a twofold ratio of geometric mean normalized intensities; it is a descriptive threshold, not a therapeutic endpoint. The nine 2+2 omissions overlap and were selected from the original thresholded set: their ranges are sensitivity diagnostics, **not confidence intervals, independent replicates or a parameter posterior**. Signal magnitude is more sensitive to sample omission than direction. No decomposition of technical measurement noise and biological variability is possible from these six processed arrays alone.

### Execution, review and limitations

Both full executions produced byte-identical JSON and CSV results. The final focused suite passed **10 tests**: five expression tests and five local-worker tests. These include a hand-calculated pseudo-F, permutation symmetry, constant-data behaviour, translation/sample-swap invariance, input rejection and both Ollama native backend names. Input hashes and SDRF assignments were checked. [Results and checksums](../Research/Expression/results-v1/) and [execution receipt](../Research/Expression/verification.json) preserve provenance. Python 3.15.0 ran the calculation; the script uses only the standard library and requires Python 3.11 or later. No new KaSim trajectory, calibration, Swift build or complete application regression suite was run.

A bounded Goose 1.45.0 / Ollama 0.40.10 task used the already installed `hermes3:8b` model, digest `4f6b83f30b62bc3d0cf9be09266db222805ee815c8fd7d8b38f863f655be78b7`. Local offline inference was established by matching the manifest's model-layer digest to the time-matched native `llama-server --offline` log, completed inference timings and generated output. The old detector looked only for `ollama runner`; it is now tested for both backends. Raw historical audits remain unchanged; the separate [review record](../Research/Expression/local-worker-review.json) corrects the conclusion.

The 42.724-second task returned an incorrect proposal to apply log2(raw counts + 1) normalization. It was rejected because the input is already normalized microarray intensity. Nothing from that proposal entered the analysis. Goose reported 1,306 input and 331 output tokens; no token savings were measured. Recorded model/KV buffers are not peak process RAM. A preliminary launch failed before inference because the coordinator service could not open the Documents path; the run used the project's established isolated execution area without changing permissions, downloading a model or switching provider. Private prompts, contacts and native logs are not published.

### Mechanistic implication and next discriminating test

The source paper's macrophage-phenotype hypothesis remains worth testing: matrix-remodelling activity may depend on macrophage state and phagocytosis-related signalling rather than a single constant degradation rate. **This global reanalysis does not identify MMP genes, measure enzyme activity or quantify that mechanism.** The source's Mmp9/Mmp12 and ERK findings are literature evidence, not newly recovered gene-level results. There is no defensible conversion from these intensity contrasts to Kappa collagen-degradation rates or to a named drug's efficacy.

A discriminating study would jointly measure macrophage state/composition, matrix-degrading activity and standardized collagen endpoints after injury withdrawal, with matched controls and a prospectively specified intervention and analysis. Possible counterevidence includes expression changes without increased degradation, a composition/batch explanation, or unchanged collagen despite altered macrophage markers. Obtain sample-to-animal and batch mapping, a verified probe-to-gene annotation, and independent collagen/protease measurements before fitting a mechanistic extension. Rat TAA suggestions require a separate species/exposure protocol; they cannot be substituted into this mouse CCl4 analysis. No doses or individual treatment recommendations follow.

**Status:** software verification passed within the stated tests; historical Kappa publication reproduction remains partial; no new parameter calibration; no independent collagen prediction; no demonstrated human transferability; no clinical validation. No raw matrix, third-party figure, private correspondence or patient data is included in this publication.

## Deutsch

### Frage, Evidenz und vorab festgelegter Test

Unterscheiden sich die vorhandenen Expressionsmessungen zwischen den beiden Makrophagengruppen, und wie empfindlich sind beschreibende Kontraste gegenüber einzelnen Proben? Diese Frage ist enger als eine Vorhersage der Kollagenrückbildung. Quelle ist Ramachandran et al. (2012), E-MEXP-3177: Lebermakrophagen männlicher Mäuse nach CCl4-Schädigung, je drei biologische Arrayreplikate bei 24 und 72 Stunden. Die Publikation beschreibt verschiedene sortierte Phänotypen (24 h Ly-6Chi gegenüber 72 h Ly-6Clo). Zeitpunkt und Phänotyp sind vermischt; Tierpooling und Chargenzuordnung sind durch die Aufnahmemetadaten nicht geklärt. Sechs Arrays entsprechen nicht sechs longitudinal beobachteten Tieren.

Das neu verfügbare Material wurde nach einem Literaturhinweis aus einem öffentlichen Archiv beschafft. Es ist kein privat gelieferter Kollagendatensatz. Die Matrix enthält **241.576 Probe-Sets und 1.449.456 endliche Messwerte**: bereits durch die Autoren RMA-normalisierte log2-Microarrayintensitäten, keine rohen Sequenziercounts. Keine erneute Normalisierung, Merkmalsauswahl, Genannotation oder Abbildungsdigitalisierung. Probe-Sets sind nicht zwangsläufig verschiedene Gene. Die Quelle war bereits bei den Referenzmodellautoren zitiert und bei der Datenaufnahme gesichtet worden: explorative Entwicklungsdaten, keine unberührte unabhängige Prüfung.

Vor der statistischen Berechnung legte die oben verlinkte Spezifikation 1.0.0 Eingangshashes, Probenzuordnung, Tests, Interpretation und Ressourcenlimits fest. Ihr SHA-256 steht im englischen Abschnitt. Zuvor waren Dimensionen, Methoden und einzelne Matrixzeilen bekannt; dies ist keine verblindete Präregistrierung.

Primäre Größe ist ein unskaliertes euklidisches Pseudo-F über alle Probe-Sets: Quadratsumme zwischen Gruppen geteilt durch die Quadratsumme innerhalb der Gruppen / 4 (Freiheitsgrade 1 und 4). Alle 20 benannten 3-gegen-3-Aufteilungen werden berechnet. Der obere Anteil schließt beobachtete Zuordnung und deren komplementäre Beschriftung ein. Vorausgesetzt wird bedingte Austauschbarkeit; diese ist durch die Quellenmetadaten nicht belegt. Es gibt nur zehn unterschiedliche unbenannte Aufteilungen, daher ist p = 0,10 das erreichbare Minimum. Kein Erfolgskriterium von 0,05, keine klinische Genauigkeitsgrenze und kein angepasstes Modell wurden eingeführt.

### Tatsächliches Ergebnis

Die Tabelle oben gilt unverändert: Pseudo-F **1,9259350402**, oberer exakter Anteil **2/20 = 0,10**; 15.279 Probe-Sets mit mittlerem Unterschied ≥ 1 und 10.000 mit ≤ −1 log2-Einheit. Zusammen sind das **25.279 von 241.576 beziehungsweise 10,4642 %**. Beim Weglassen je einer Probe aus beiden Gruppen behalten **99,38–99,83 %** dieser Menge die Richtung und **69,13–87,33 %** den absoluten Abstand ≥ 1.

Beobachtete Zuordnung und Komplement haben den höchsten globalen Wert unter diesen Aufteilungen. Daraus folgen **weder** kausaler Zeiteffekt oder Arzneimittelwirkung **noch** ausgeschlossene Chargeneffekte oder eine 90-prozentige Wahrscheinlichkeit einer biologischen Hypothese. Der Test verwirft nicht bei 0,05; seine grobe Auflösung beweist aber auch nicht das Fehlen biologischer Unterschiede. Es wurden keine Probe-Set-Signifikanztests oder korrigierten Gen-p-Werte berechnet. Die ursprüngliche Publikation verwendet eine andere Analyse auf Genebene; deren Liste wird hier weder reproduziert noch widerlegt.

Eine log2-Einheit entspricht einem zweifachen Verhältnis geometrischer Mittel normalisierter Intensitäten. Das ist eine beschreibende Grenze, kein Therapieendpunkt. Die neun überlappenden 2+2-Teilmengen beziehen sich auf die ursprünglich ausgewählte Menge. Ihre Spannweiten sind Empfindlichkeitsprüfungen, **keine Konfidenzintervalle, unabhängigen Replikate oder Parameterposterioren**. Die Effektgröße hängt stärker von einzelnen Proben ab als die Richtung. Technischer Messfehler und biologische Streuung lassen sich aus diesen sechs verarbeiteten Arrays nicht getrennt bestimmen.

### Ausführung, Prüfung und Grenzen

Beide vollständigen Auswertungen erzeugten bytegleiche JSON-/CSV-Ergebnisse. **Zehn gezielte Tests bestanden**: fünf für Expression, fünf für lokale Worker. Geprüft wurden unter anderem ein handberechnetes Pseudo-F, Permutationssymmetrie, konstante Daten, Verschiebungs-/Gruppentauschinvarianz, fehlerhafte Eingaben und beide nativen Ollama-Prozessnamen. Eingangshashes und SDRF-Zuordnung wurden kontrolliert. Ergebnisse, Prüfsummen und Ausführungsbeleg sind oben verlinkt. Ausführung mit Python 3.15.0; benötigt wird nur die Standardbibliothek ab Python 3.11. Keine neue KaSim-Trajektorie, Kalibrierung, Swift-Kompilierung oder vollständige App-Regressionsprüfung.

Ein begrenzter Goose-/Ollama-Auftrag nutzte das vorhandene `hermes3:8b` mit den oben genannten Versionen und dem bestätigten Digest. Modellmanifest, zugehöriger Modellblob, zeitlich passende Offline-`llama-server`-Protokolle, Inferenzzeiten und tatsächlich erzeugte Antwort belegen lokale Inferenz. Der alte Detektor kannte nur `ollama runner`; beide Varianten sind nun getestet. Alte Rohbelege wurden nicht überschrieben, die Korrektur steht im separaten Prüfbeleg.

Die Antwort nach 42,724 Sekunden empfahl fälschlich log2(Rohcounts + 1). Dieser Vorschlag wurde wegen bereits normalisierter Microarraydaten verworfen und nicht integriert. Goose meldete 1.306 Eingabe- und 331 Ausgabetokens; eine Tokenersparnis wurde nicht gemessen. Modell-/KV-Puffergrößen sind kein Spitzen-RAM-Nachweis. Ein Vorstartversuch scheiterte am Zugriff des Koordinatordienstes auf den Dokumente-Pfad. Die eigentliche Ausführung erfolgte im etablierten isolierten Projektbereich, ohne Berechtigungsänderung, Modelldownload oder Providerwechsel. Private Prompts, Kontakte und native Protokolle bleiben unveröffentlicht.

### Mechanistische Bedeutung und nächster unterscheidender Test

Die Hypothese der Quellpublikation bleibt prüfenswert: Matrixabbau könnte vom Makrophagenzustand und phagozytosebezogenen Signalen abhängen, statt durch eine einzige konstante Abbaurate beschrieben zu werden. **Diese globale Auswertung identifiziert keine MMP-Gene, misst keine Enzymaktivität und quantifiziert diesen Mechanismus nicht.** Mmp9/Mmp12- und ERK-Befunde stammen aus der Literatur, nicht aus einer hier neu gewonnenen Genanalyse. Eine Umrechnung der Intensitätsunterschiede in Kappa-Kollagenabbauraten oder die Wirkung eines bestimmten Arzneimittels ist nicht begründet.

Ein unterscheidendes Experiment würde nach Schädigungsende Makrophagenzustand/-zusammensetzung, Matrixabbauaktivität und standardisierte Kollagenendpunkte gemeinsam erfassen, mit passenden Kontrollen und vorab festgelegter Intervention und Auswertung. Gegenbefunde wären Expressionsänderungen ohne erhöhten Abbau, eine Erklärung durch Zellzusammensetzung/Charge oder unverändertes Kollagen trotz anderer Marker. Vor einer Modellergänzung fehlen Proben-/Tier-/Chargenzuordnung, geprüfte Probe-Set-Genannotation und unabhängige Kollagen-/Proteasemessungen. Hinweise auf Ratten-TAA erfordern ein eigenes Spezies-/Expositionsprotokoll; sie lassen sich nicht in diese Maus-CCl4-Auswertung einsetzen. Keine Dosierungen oder individuellen Empfehlungen.

**Status:** Software-Verifikation im genannten Umfang bestanden; historische Kappa-Publikationsreproduktion weiterhin teilweise; keine neue Parameterkalibrierung; keine unabhängige Kollagenvorhersage; keine belegte Übertragbarkeit auf Menschen; keine klinische Validierung. Keine Rohmatrix, fremde Abbildung, private Korrespondenz oder Patientendaten veröffentlicht.

## Sources / Quellen

- [Ramachandran et al. 2012, original study, DOI 10.1073/pnas.1119964109](https://pmc.ncbi.nlm.nih.gov/articles/PMC3503234/): macrophage microarray methods and Figure 5; mechanistic experiments are separate from this reanalysis.
- [E-MEXP-3177 source archive](https://www.ebi.ac.uk/biostudies/arrayexpress/studies/E-MEXP-3177): IDF, SDRF and processed matrix; exact URLs/hashes in the specification.
- [Author repository copy](https://www.research.ed.ac.uk/en/publications/differential-ly-6c-expression-identifies-the-recruited-macrophage/): locally read full text, methods and phenotypes.
- [Bouguéon et al. 2024](https://doi.org/10.1371/journal.pcbi.1011858): existing reference model; no new model-equation change.
- [Reproduction instructions / Reproduktionsanleitung](../Research/Expression/README.md).
