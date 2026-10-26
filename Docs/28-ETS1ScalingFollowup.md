# ETS1 normalization follow-up / Ergänzende Normierungsprüfung

26 October 2026 · Johnnie 4 free · research only

## English

**One different positive divisor per group cannot reconcile three of the four Figure2B/C Sirius-red groups, even after allowing the specified rounding.** This narrows the explanation of our [previous source audit](27-ETS1SourceAudit.md). It does not establish which source table or processing step is responsible, nor invalidate the whole study.

We retained the same original workbook, endpoints and groups from Lee et al.2025, DOI10.1172/jci.insight.195242. The previous discrepancy was known: this is an exploratory follow-up, not blinded preregistration. A new protocol was frozen before computation. Unlike the previous genotype-baseline calculation, this check allows any positive divisor independently for each group. The rounding sensitivity bounds are ±0.005 percentage points in B and ±0.000005 dimensionless units in C. These are calculation assumptions, not estimates of biological or measurement error.

For each sorted pair b,c, a possible divisor must fall in [(b−rB)/(c+rC), (b+rB)/(c−rC)]. We intersect these intervals across all seven points. Positive scaling preserves order; sorting makes row permutations irrelevant without assigning animal identities. Exact rational arithmetic decides whether the interval is empty. No best-fitting divisor is chosen.

| Group | Required lower bound | Required upper bound | Compatible |
|---|---:|---:|---|
| control_injury | 5.945324 | 5.954676 | yes |
| knockout_injury | 8.498959 | 7.414397 | no |
| control_regression | 6.523184 | 6.118901 | no |
| knockout_regression | 8.497471 | 6.118112 | no |

A lower bound exceeding its upper bound denotes an empty intersection, not a confidence interval. Thus changing a shared divisor, including replacing a group mean with another group constant, does not resolve these three groups within the bounds. Batch-specific denominators, nonlinear transformations, different samples or aggregation before normalization remain possible. This test does not identify the actual explanation.

Four new software tests passed, covering a known scale, row permutation, incompatible distributions, rounding feasibility and invalid inputs. A separate process reproduced the result byte-for-byte. The existing importer added one evidence record; repeat import added none, preserved both simulation records and passed SQLite quick_check. Computation used local Python3.15.1 and its standard library; no language-model-generated numbers or local inference are claimed.

Quantitative ETS1 treatment-effect calibration remains withheld. Neither this consistency test nor expression/knockout evidence establishes safe or effective human ETS1 enhancement. No new biological prediction test, human treatment result or clinical validation was performed. The next useful evidence is the original analysis export with animal-to-field mapping, denominators, exclusions and clarification of six versus seven animals. No author email was sent.

### Primary-source review of the research handoff

We checked the researcher’s material against the original article and supplement. The article describes a baseline rule without an explicit individual-point algorithm; the original audit therefore tests a declared interpretation. Supplemental Figure S2C (PDF page5) describes QuPath over3–5 random fields per sample, with7 mice/group in the B–E legend. This does not establish the individual values or processing used in Figure2B/C. Raw data are available on request according to the article. The visible publisher history contains4November and22December2025; it does not settle possible corrections elsewhere.

The researcher’s three search queries returned empty tool output, so the broader correction/repository search is inconclusive, not a negative finding. Two original fulltexts were inspected. The response was reviewed, but its private files and correspondence draft are excluded from publication. No new independent cohort was identified in that checked material.

## Deutsch

**Ein anderer positiver Nenner je Gruppe erklärt die Abweichungen zwischen2B und2C bei drei von vier Siriusrot-Gruppen auch mit den festgelegten Rundungsgrenzen nicht.** Damit wird eine mögliche Erklärung des vorherigen Befunds ausgeschlossen. Welche Tabelle oder Verarbeitung verantwortlich ist, bleibt offen; die gesamte Studie wird dadurch nicht widerlegt.

Dieselben Quelldaten und Endpunkte wurden beibehalten. Der frühere Befund war bekannt; es handelt sich um eine explorative Folgeprüfung. Das neue Protokoll wurde vor der Rechnung festgelegt. Es erlaubt je Gruppe einen beliebigen positiven Nenner und Rundungsabweichungen von ±0,005 Prozentpunkten für B sowie ±0,000005 für C. Diese Grenzen sind Rechenannahmen, keine Mess- oder biologische Unsicherheit.

Für jedes sortierte Wertepaar wird der zulässige Nennerbereich nach der obigen Formel berechnet. Die Schnittmenge aller sieben Bereiche entscheidet über Vereinbarkeit; exakte Bruchrechnung vermeidet numerische Grenzfallfehler. Sortierung erlaubt umgestellte Zeilen, ohne Tieridentitäten zu erfinden. Ein unterer Grenzwert über dem oberen bedeutet eine leere Schnittmenge, kein Konfidenzintervall. Die Tabelle gilt für beide Sprachfassungen.

Nur die Kontroll-Schädigungsgruppe ist vereinbar. Ein anderer gemeinsamer Gruppenmittelwert oder sonstiger konstanter Nenner löst die übrigen Abweichungen nicht innerhalb der Grenzen. Batchabhängige Verarbeitung, nichtlineare Transformationen, andere Proben oder vorgelagerte Mittelungen bleiben mögliche Erklärungen. Keine davon wurde nachgewiesen.

Vier neue Softwaretests bestanden; ein separater Prozess reproduzierte das Ergebnis bytegleich. Ein Evidenzeintrag wurde gespeichert, beim Wiederimport keiner; beide bisherigen Simulationsdatensätze blieben erhalten, SQLite quick_check war erfolgreich. Die Rechnung erfolgte lokal mit Python3.15.1 und der Standardbibliothek. Keine KI-Schätzwerte und keine lokale Inferenz werden behauptet.

Eine quantitative Behandlungskalibrierung bleibt ausgesetzt. Weder Quellenprüfung noch Expressions-/Knockoutbefund belegen eine sichere oder wirksame ETS1-Verstärkung beim Menschen. Keine neue unabhängige biologische Vorhersageprüfung oder klinische Validierung. Benötigt werden der ursprüngliche Analyseexport, Tier-/Bildfeldzuordnung, Nenner und Ausschlüsse sowie die Klärung von sechs versus sieben Tieren. Keine Autorenmail wurde versandt.

### Prüfung der Rechercheübergabe an Originalquellen

Artikel und Supplement wurden selbst nachgeprüft. Der Artikel nennt eine Baseline-Regel, aber keinen ausdrücklichen Algorithmus für Einzelpunkte; die ursprüngliche Rechnung prüft daher eine deklarierte Interpretation. S2C nennt auf PDF-Seite5 drei bis fünf zufällige QuPath-Bildfelder je Probe und für B–E sieben Mäuse je Gruppe. Das klärt die Einzelwerte und Verarbeitung von2B/C nicht. Rohdaten sind laut Artikel auf Anfrage erhältlich. Die sichtbare Verlagschronik nennt4.November und22.Dezember2025; Korrekturen andernorts sind damit nicht ausgeschlossen.

Drei Suchanfragen des Recherche-Chats lieferten leere Werkzeugausgaben. Die übergreifende Korrektur-/Repositorysuche ist deshalb unentschieden, kein negativer Nachweis. Zwei Originalvolltexte wurden geprüft. Die private Übergabe samt Anfrageentwurf wird nicht veröffentlicht. Im geprüften Material wurde keine neue unabhängige Kohorte identifiziert.

## Artifacts and primary source / Artefakte und Primärquelle

- [Executable instructions](../Research/ETS1Regression/README.md), [frozen protocol](../Research/ETS1Regression/scaling-spec-v1.json), [result](../Research/ETS1Regression/scaling-result-v1.json), [verification](../Research/ETS1Regression/scaling-verification.json).
- [Original article](https://insight.jci.org/articles/view/195242), Results: development/regression; Figure2 legend, checked26October2026. Article CC BY4.0. Scope and source restrictions remain as in report27.
- Source SHA256: `61bc6eef7b1f1a1e757e73097020673b288c1e0374bc99617fc5f794180ce546`. Workbook and private research handoffs are not redistributed.

- [Original supplement](https://insight.jci.org/articles/view/195242/sd/pdf/render/1), Figure S2 legend, PDF page5. SHA256 `61abb0ea032fe70d0bb73227c1f6262ae490a91c6173d2f2351d567703700ae7`.
