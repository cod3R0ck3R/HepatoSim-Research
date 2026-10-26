# ETS1 Figure2 source-data audit / Prüfung der ETS1-Quelldaten

26 October 2026 · Johnnie 4 free · research only

## English

**The published Figure2C normalization cannot be reproduced from the supplied Figure2B values for three of four Sirius-red groups.** This is a source-data arithmetic finding, not a judgment about the entire study or misconduct. Different input cohorts, undocumented processing or a source-table mismatch remain possible. We stop at descriptive analysis until the mapping is resolved.

Scope: Lee et al.2025, DOI10.1172/jci.insight.195242, Figure2B/C. Male mouse liver, HSC-specific Ets1 deletion versus floxed controls,6weeks of CCl4 injury and2weeks after injury cessation. Sirius-red-positive area is a percentage of tissue area, not collagen mass, organ function or a per-day regression rate. Samples are terminal histological groups, not paired longitudinal animals. The results paragraph says n=6/group; the figure legend says n=7. The workbook contains7 graph points in each selected column. Animal IDs, field/section averaging and batch mapping are not supplied in these tables. Do not silently manufacture a missing animal or assume technical fields are independent mice.

### Prespecified computation and its limits

The protocol was frozen and hashed before numerical program execution. However, a metadata read inadvertently displayed initial numeric rows of Figures2B/C and excerpts2D/E, and the publication conclusion was already known. This is an exploratory audit, not blinded preregistration. Only the first four Sirius-red columns were analyzed; no endpoint was selected by favorable results.

For each genotype, divide every Figure2B value by its own injury-group arithmetic mean. Compare sorted values with Figure2C, allowing row reordering without inventing animal pairing. The frozen strict tolerance is5e-6; a separate loose sensitivity tolerance is0.002. Neither is a biological accuracy criterion. Three groups fail both tolerances. The control injury group agrees within3.9e-9; all21 values in the other three groups fail even0.002 after sorting.

| Group | n | B mean (% area) | Recomputed normalized mean | Supplied C mean | Largest sorted discrepancy |
|---|---:|---:|---:|---:|---:|
| control_injury | 7 | 5.950000 | 1.000000 | 1.000000 | 0.000000 |
| knockout_injury | 7 | 8.074286 | 1.000000 | 1.000000 | 0.072327 |
| control_regression | 7 | 4.200000 | 0.705882 | 0.662665 | 0.067227 |
| knockout_regression | 7 | 6.751429 | 0.836164 | 0.827621 | 0.182978 |

Derived from B, the remaining-area fractions are0.705882 for control and0.836164 for knockout; their ratio is1.184566. The supplied C gives0.662665 and0.827621, ratio1.248928. These are alternative descriptive calculations from inconsistent source tables, not competing treatment estimates. Both retain the reported directional pattern, but cannot establish a reliable quantitative magnitude. We did not compute inferential p-values or confidence intervals, fit the Kappa model, or label this an independent biological validation.

### Executed checks and provenance

Original XLSX literals were checked against the existing MarkItDown conversion. Maximum conversion rounding error is4.7e-7; calculations use the XLSX literals. That rounding does not explain the discrepancies. Six unit tests and five export/privacy tests passed. Separate-process replay is byte-identical. The tested MarkItDown module command recreates the archived conversion hash. One immutable evidence record was added to the local database; replay added zero, and both preexisting simulation records were preserved.

Two implementation failures were retained locally: an empty Markdown-prefix parser bug was fixed; exact equality against rounded Markdown was replaced by an explicitly recorded conversion-only5e-6 tolerance. The frozen scientific normalization criteria were not changed. Public protocol export removes account quota/reset metadata only; a replay verifies identical numerical results, with only the specification hash binding changed. The redaction receipt records both versions.

Local Goose/Ollama translation was queued against the verified installed model but could not start under coordinator resource limits. It was cancelled before execution. No local inference, token savings or generated translation is claimed for this iteration. All numerical work used local Python standard-library programs.

### Treatment hypothesis and next distinguishing evidence

ETS1 maintenance during recovery remains a mechanism hypothesis, not a quantitatively modeled drug effect. A knockout result does not establish that increasing ETS1 is effective or safe. A useful future comparison would test an HSC-specific rescue initiated after injury cessation against matched controls with comparable starting fibrosis, independent animal-level collagen measurements and injury/function endpoints. Failure to improve collagen regression despite verified target engagement would weaken that hypothesis. No dose or experimental protocol is proposed here.

First resolve source B/C mapping, denominators, exclusions/averaging and n6 versus n7. This focused task has been handed to the separate research chat. No author email was sent. Additional raw images and animal identifiers would be needed to independently check the measurement process. Human transcriptomic reuse of GSE244832 does not provide an independent human cohort.

**Status:** stated software checks passed; arithmetic publication reproduction failed for3/4 groups under the declared interpretation; no parameter calibration, independent biological prediction test, demonstrated human treatment effect or clinical validation.

## Deutsch

**Die normierten Werte aus Abbildung2C lassen sich für drei von vier Siriusrot-Gruppen nicht aus den bereitgestellten Werten von2B reproduzieren.** Das ist ein rechnerischer Quellenbefund, kein Urteil über die gesamte Studie oder wissenschaftliches Fehlverhalten. Andere Eingangskohorten, nicht dokumentierte Verarbeitung oder eine Tabellenabweichung sind weiterhin möglich. Bis zur Klärung bleibt die Analyse beschreibend.

Untersucht wurden männliche Mäuse mit HSC-spezifischem Ets1-Knockout und Kontrolltiere nach6Wochen CCl4-Schädigung beziehungsweise2Wochen Erholung. Siriusrot-positive Fläche ist ein Gewebeflächenanteil, keine Kollagenmasse, Organfunktion oder tägliche Rückbildungsrate. Histologische Endpunkte bilden keine gepaarten individuellen Verläufe. Der Ergebnisteil nennt6, die Legende7 Tiere je Gruppe; tatsächlich stehen7 Graphpunkte in jeder ausgewählten Spalte. Tierkennungen sowie die Zuordnung von Bildfeldern, Schnitten und Batches fehlen in diesen Tabellen.

Die Spezifikation wurde vor der Programmausführung festgelegt. Erste Zahlenzeilen waren durch eine Metadatenvorschau bereits sichtbar, ebenso die publizierte Schlussfolgerung. Daher keine verblindete Präregistrierung. Ausgewählt waren ausschließlich die vier Siriusrot-Spalten. Jeder2B-Wert wurde durch den Schädigungsgruppenmittelwert seines Genotyps geteilt und nach Sortierung mit2C verglichen. Die unveränderten Grenzen5e-6 und0,002 prüfen Rundungsvereinbarkeit, keine biologische Genauigkeit. Nur die Kontroll-Schädigungsgruppe besteht; alle21 Werte der übrigen Gruppen verfehlen auch0,002.

Die obige Tabelle gilt für beide Sprachfassungen. Aus2B ergeben sich verbleibende Flächenanteile von0,705882 und0,836164, Verhältnis1,184566. Die gelieferten2C-Werte ergeben0,662665 und0,827621, Verhältnis1,248928. Das sind beschreibende Rechnungen aus widersprüchlichen Tabellen, keine Behandlungseffekte. Beide zeigen dieselbe Richtung, ihre quantitative Größe bleibt ungeklärt. Deshalb keine p-Werte, Konfidenzintervalle oder Modellkalibrierung.

Die Originalwerte wurden gegen die MarkItDown-Konvertierung geprüft; deren maximale Rundungsabweichung4,7e-7 erklärt den Befund nicht. Sechs Analyse- und fünf Exporttests bestanden. Ein separater Prozess reproduziert das Ergebnis bytegleich; auch die dokumentierte Konvertierung wurde ausgeführt. Ein Evidenzeintrag wurde gespeichert, beim Wiederimport keiner hinzugefügt; beide bisherigen Simulationsdatensätze blieben unverändert. Die zwei behobenen Parser-/Rundungsfehler und die Entfernung ausschließlich privater Kontingentdaten aus der öffentlichen Spezifikation sind dokumentiert. Numerische Ergebnisse wurden dabei nicht verändert.

Der lokale KI-Auftrag wurde wegen der Ressourcenbegrenzung vor dem Start abgebrochen. Für diesen Durchlauf werden weder lokale Inferenz noch Tokenersparnis behauptet. Die numerische Rechnung lief lokal mit der Python-Standardbibliothek.

ETS1-Erhaltung während der Erholung bleibt eine Mechanismushypothese. Ein Knockout-Befund beweist keine sichere oder wirksame Behandlung durch ETS1-Verstärkung. Ein unterscheidender künftiger Vergleich wäre eine erst nach Schädigungsende eingeleitete HSC-spezifische Wiederherstellung gegen passende Kontrollen mit vergleichbarer Ausgangsfibrose und unabhängigen Tiermessungen. Bleibt die Kollagenrückbildung trotz bestätigter Zielaktivierung aus, schwächt das die Hypothese. Keine Dosierung und kein Versuchsprotokoll werden hier vorgeschlagen.

Zuerst sind Tabellenzuordnung, Nenner, Ausschlüsse/Mittelungen und Stichprobengröße zu klären. Dafür liegt ein gezielter Auftrag beim Recherche-Chat; keine Autorenmail wurde versandt. Die Wiederverwendung von GSE244832 ist keine unabhängige humane Kohorte.

**Prüfstatus:** genannte Softwareprüfungen bestanden; rechnerische Publikationsreproduktion bei3/4 Gruppen unter der beschriebenen Interpretation gescheitert. Keine Kalibrierung, unabhängige biologische Vorhersageprüfung, nachgewiesene Behandlung beim Menschen oder klinische Validierung.

## Reproduction and sources / Reproduktion und Quellen

- [Executable audit and instructions](../Research/ETS1Regression/README.md)
- [Lee et al., original article](https://insight.jci.org/articles/view/195242): Figure2B/C legend, results, Methods: Sex as a biological variable, IHC, Statistics, Data availability; checked26October2026.
- [Publisher Supporting Data Values](https://insight.jci.org/articles/view/195242/sd/3). Workbook SHA256: `61bc6eef7b1f1a1e757e73097020673b288c1e0374bc99617fc5f794180ce546`.
- Article licensed CC BY4.0. Workbook, original images, correspondence and local logs are not redistributed here. Public artifacts contain original code and derived audit summaries with attribution.

## Clarification / Präzisierung — 26 October 2026

The article supplies a baseline rule without an explicit individual-point algorithm. The result above is conditional on our declared interpretation. The [follow-up](28-ETS1ScalingFollowup.md) broadens the test to any positive constant divisor per group within declared rounding; it does not assess every possible processing pipeline.

Der Artikel liefert keine ausdrückliche Einzelpunktformel. Der obige Befund gilt für unsere deklarierte Interpretation. Die Folgeprüfung umfasst beliebige positive Gruppennenner mit festgelegter Rundung, nicht sämtliche möglichen Verarbeitungsschritte.
