# GSE295293: nine-library audit / Prüfung der neun Bibliotheken

24 October 2026 · Maintainer: Johnnie 4 free

## English

**Question.** Can the available libraries support a bounded investigation of fibrosis-associated mechanisms? They cannot directly estimate treatment efficacy: the nine groups are control, TAA injury and withdrawal, with no drug arm.

**Evidence and design.** [GEO GSE295293](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE295293) provides nine male mouse liver libraries: three untreated, three after 10 weeks TAA, three after 2 weeks withdrawal. Pham et al., [JHEP Reports 2026, DOI 10.1016/j.jhepr.2026.101783](https://doi.org/10.1016/j.jhepr.2026.101783), describe three biological replicates per group. Distinct BioSample/library identifiers agree with that statement, but animal-to-library mapping, pooling, processing batches and randomization have not been independently established. GEO's shared “8 weeks old” field does not resolve starting versus collection age. These are separate endpoint groups, not longitudinal measurements of the same animals.

**Actual small preflight.** All nine feature/barcode files passed uniqueness and matrix-dimension checks: 19,059 gene features per library, 48,993 input barcodes and 116,958,320 declared nonzero entries. All eight prespecified genes have one feature each; 13 mitochondrial features are represented. Header totals alone do not verify count entries. The paper reports 38,136 cells after processing; this is a comparator, not a number to force by tuning filters. [Per-library table](../Research/GEOSampleCheck/sample-table.md) · [machine-readable preflight](../Research/GEOSampleCheck/metadata-result.json).

**Frozen method.** [Specification](../Research/GEOSampleCheck/specification-v1.json): Sema4d,Plxnb2,Lmcd1,Col1a1,Acta2,Timp1,Mmp14,Ctsl; whole-library count sums, before and after published-code QC; log2(CPM+1); fibrosis–control and withdrawal–fibrosis contrasts; leave-one-library-per-group-out ranges. The source thresholds are gene detection in≥3 cells,>200 and <4000 detected genes/cell, <20,000 counts/cell and <20% mitochondrial counts. Author script commit 8b90c0177df6892952c137e247460212d5b07d08 integrates exactly these nine libraries; additional CYGB setup is outside that integration list. Our implementation does not reproduce Seurat integration, cell typing, doublet handling or all downstream author decisions.

With three libraries per group there are 20 label allocations, giving a minimum two-sided exact permutation p = 0.1. BH correction covers 16 tests per QC branch. These are conditional descriptive checks: exchangeability remains unconfirmed; absence of significance is not evidence of no effect. Cells are never treated as independent animals. Direction sensitivity is not a confidence interval or a drug-response estimate. All data and the first three targets were used by the original authors, so this is development-data reanalysis.

**Treatment questions that fit the material.**

| Approach | What these libraries can examine | Additional evidence needed |
|---|---|---|
| SEMA4D–PLXNB2 blockade | Whether ligand/receptor expression accompanies injury and withdrawal; source reports a separate VX15/2503 intervention experiment | Cell-resolved animal-level validation; delayed intervention after established fibrosis, matched withdrawal controls, collagen and safety outcomes. That separate experiment is absent from these nine libraries. |
| LMCD1-associated HSC activation | Whether Lmcd1 tracks matrix/activation genes; source proposes an HSC mechanism | Verify HSC-specific expression and perturbation independently, including viability/off-target controls. No quantitative drug-to-parameter mapping is available. |
| Matrix turnover / cause removal | Whether Col1a1,Acta2,Timp1,Mmp14,Ctsl change during withdrawal | Joint collagen synthesis and degradation measurements plus an independent time course. RNA abundance is neither enzyme activity nor net collagen clearance. |

These are experimental questions, not ranked efficacious drugs. Whole-liver mixtures confound cell abundance and per-cell expression. No claim about human alcohol-associated disease, decompensated cirrhosis, clinical safety or current drug authorization follows from this dataset. Current regulatory status was not investigated in this bounded task.

## Deutsch

**Fragestellung.** Die neun Mausleber-Bibliotheken erlauben eine begrenzte Untersuchung fibrosebezogener Mechanismen. Eine Arzneimittelwirkung ist damit nicht direkt bestimmbar: Es gibt Kontrolle, TAA-Schädigung und Rückbildung nach Absetzen, aber keinen Medikamentenarm.

**Design.** Je drei Bibliotheken repräsentieren unbehandelte Lebern, 10 Wochen TAA und 2 Wochen nach Absetzen. Die Publikation bezeichnet sie als biologische Replikate. Unterschiedliche BioSample- und Bibliothekskennungen passen dazu; Tierzuordnung, Pooling, Chargen und Randomisierung sind nicht unabhängig bestätigt. Das gemeinsame GEO-Altersfeld „8 Wochen“ klärt Start- gegenüber Entnahmealter nicht. Es handelt sich um getrennte Endpunktgruppen, nicht wiederholte Messungen derselben Tiere.

**Tatsächlich geprüft.** Alle neun Gen-/Barcodeverzeichnisse sind intern eindeutig und stimmen mit den Matrixdimensionen überein: 19.059 Genmerkmale je Bibliothek, 48.993 Barcodes, 116.958.320 deklarierte Einträge. Alle acht Zielgene sind eindeutig vorhanden, außerdem 13 mitochondriale Merkmale. Das bestätigt noch nicht sämtliche Zähleinträge. Die publizierten 38.136 Zellen nach Verarbeitung dienen nur zum Vergleich; Filter werden nicht auf diese Zahl angepasst.

**Vorab festgelegt.** Acht Gene, zwei Gruppenvergleiche, ganze Bibliotheken als Auswertungseinheiten, ungefilterte und nach Autorengrenzen gefilterte Summen sowie Weglassen jeweils einer Bibliothek pro Gruppe. Die konkreten Filter und Transformationen stehen im verlinkten Protokoll. Keine Zelltypzuordnung oder vollständige Seurat-Reproduktion. Drei gegen drei Bibliotheken erlauben nur 20 Labelbelegungen; der kleinste zweiseitige exakte p-Wert ist 0,1. 16 Tests werden pro Filterzweig gemeinsam korrigiert. Austauschbarkeit bleibt ungeklärt. Keine Signifikanz bedeutet nicht Wirkungslosigkeit; Sensitivitätsspannen sind keine Konfidenzintervalle. Die Daten und die ersten drei Zielgene stammen bereits aus der Modellentwicklung der Autoren.

**Sinnvolle Forschungsansätze.** SEMA4D–PLXNB2: Ligand/Rezeptor im Schädigungs- und Rückbildungsverlauf prüfen; der separate VX15/2503-Versuch der Publikation ist kein Teil dieser neun Bibliotheken. Als nächster unterscheidender Test wäre eine verzögerte Intervention bei bereits bestehender Fibrose mit passenden Absetzkontrollen, Kollagen- und Sicherheitsmessungen nötig. LMCD1: Zusammenhang mit Sternzellaktivierung prüfen; Zelltypzuordnung und unabhängige Perturbation mit Viabilitäts-/Nebeneffektkontrollen fehlen. Matrixumbau: Col1a1/Acta2/Timp1/Mmp14/Ctsl liefern Expressionsfragen; zusätzlich braucht es gemeinsame Synthese-/Abbaumessungen und eine unabhängige Zeitreihe. RNA ist weder Enzymaktivität noch Kollagenabbau.

Die Ansätze sind experimentell; keine Rangliste wirksamer Medikamente. Zellmischung und Expression innerhalb von Zellen sind vermengt. Keine Übertragung auf menschliche alkoholassoziierte Erkrankung, dekompensierte Zirrhose, klinische Sicherheit oder aktuelle Zulassung. Ein regulatorischer Statusabgleich war nicht Teil dieser begrenzten Aufgabe.

## Executed results / Tatsächlich ausgeführte Ergebnisse

**The full scan completed:** all 116,958,320 positive integer coordinate entries are unique and dimensionally valid. The frozen filters retained **38,136 of 48,993 barcodes**, with group totals **13,948 / 14,986 / 9,202**, exactly matching the published control / fibrosis / regression sizes. This reproduces those aggregate QC counts; the identity of individual retained cells was not compared with an author reference list. Cell annotation and the full publication pipeline were not reproduced.

The local run took **524.981 s wall time**, **77.188 s CPU time**, and **90,112,000 bytes observed peak RSS**. The amended parser deliberately throttled streaming and aggregation; no coordinator limit or AI memory gate was disabled. Seven software tests passed. Real checkpoint resume and aggregate replay were byte-identical to the first result. Replay did not rescan every raw coordinate. [Execution](../Research/GEOSampleCheck/execution-summary.json), [comparison](../Research/GEOSampleCheck/publication-comparison.json), [verification](../Research/GEOSampleCheck/verification.json), [full result](../Research/GEOSampleCheck/result-v1.json).

The following differences are **mean log2(CPM+1)** differences between libraries, not drug effects or collagen quantities. Leave-out ranges are sensitivity ranges, not confidence intervals. “Stable” uses the frozen sign criterion across both raw/QC analyses and all nine two-versus-two leave-out comparisons.

| Gene | Fibrosis − control, QC Δ | Withdrawal − fibrosis, QC Δ | Withdrawal leave-out range | Stable both contrasts across QC + leave-out |
|---|---:|---:|---:|---|
| Sema4d | +3.235 | -1.181 | [-1.477, -0.886] | yes / ja |
| Plxnb2 | +0.846 | -0.290 | [-0.377, -0.199] | yes / ja |
| Lmcd1 | +1.580 | +0.063 | [-0.096, +0.245] | no / nein |
| Col1a1 | +4.652 | -2.452 | [-2.915, -1.885] | yes / ja |
| Acta2 | +3.586 | -1.284 | [-2.113, -0.465] | yes / ja |
| Timp1 | +0.882 | -0.930 | [-1.196, -0.571] | no / nein |
| Mmp14 | +1.320 | -0.214 | [-0.301, -0.152] | yes / ja |
| Ctsl | -0.187 | +0.401 | [+0.313, +0.462] | no / nein |

**Interpretation.** SEMA4D–PLXNB2 is the clearest first target pair for a cell-resolved follow-up in these data: both rise with fibrosis and fall after withdrawal across the specified sensitivity checks. This descriptive coherence and the separate intervention evidence in the same paper motivate a hypothesis; neither supplies an independent efficacy estimate. The minimum QC-branch BH q-value is **0.1333**; no gene reaches a 0.05 threshold, and that threshold is not used as a success criterion.

LMCD1 rises with injury but its withdrawal contrast is **+0.063 after QC versus −0.294 before QC**, with a leave-out range crossing zero. The simple claim that its liver-wide RNA expression reliably falls during regression is not supported here. Its proposed cell-specific mechanism remains testable. CTSL reverses direction with QC in both contrasts and should not be prioritized from this whole-liver comparison. TIMP1's injury contrast is also unstable under sample removal. COL1A1/ACTA2 patterns support an expression-level injury/withdrawal contrast, but cannot establish collagen clearance or restored organ function. MMP14 expression falls after withdrawal; this does not imply that matrix degradation itself falls.

**Next discriminating step.** Obtain animal-level, cell-type annotated counts and processing metadata to separate cell proportions from expression within HSCs/macrophages. Check SEMA4D/PLXNB2 and LMCD1 protein/activity alongside collagen synthesis and clearance in an independent cohort. A later established-fibrosis intervention comparison needs matched cause-removal controls and safety outcomes. No quantitative mapping from these RNA changes to Kappa parameters or medicine effects has been justified; no new drug simulation or calibration was performed.

**Deutsch.** Der Vollscan prüfte alle 116.958.320 positiven ganzzahligen Einträge auf Eindeutigkeit und gültige Dimensionen. Die unveränderten Filter liefern 38.136 von 48.993 Barcodes; alle drei Gruppensummen stimmen exakt mit der Publikation überein. Das reproduziert aggregierte QC-Zellzahlen, nicht die Identität einzelner Zellen, Zelltypzuordnungen oder die gesamte Publikationspipeline. Laufzeit 524,981 s, CPU-Zeit 77,188 s, beobachteter Spitzen-RSS 90.112.000 Bytes. Sieben Tests bestanden; echte Wiederaufnahme und Aggregatwiederholung sind bytegleich. Keine erneute vollständige Rohmatrixprüfung beim Replay.

Die Tabelle zeigt Differenzen mittlerer log2(CPM+1)-Werte. Weglassbereiche sind Sensitivitätsbereiche, keine Konfidenzintervalle. SEMA4D–PLXNB2 ist hier das am klarsten begründete erste Paar für eine zelltypspezifische Folgeprüfung: beide Richtungen bleiben unter den festgelegten Kontrollen erhalten. Das ist eine Hypothesenpriorisierung ohne unabhängigen Wirksamkeitsnachweis. Der kleinste korrigierte q-Wert beträgt 0,1333; kein Gen unterschreitet 0,05, was ausdrücklich kein erzwungenes Erfolgskriterium ist.

LMCD1 steigt bei Schädigung, fällt bei Rückbildung aber nicht stabil: nach QC +0,063, vorher −0,294; der Weglassbereich schließt null ein. Die einfache Behauptung einer verlässlichen leberweiten Abnahme ist damit nicht gestützt. Ein zelltypspezifischer Mechanismus ist dadurch nicht widerlegt. CTSL wechselt unter QC in beiden Vergleichen das Vorzeichen; daraus wird kein bevorzugter Therapieansatz abgeleitet. Auch TIMP1 bei Schädigung ist weglassensitiv. COL1A1/ACTA2 sind Expressionsbefunde, keine Kollagenabbau- oder Funktionsmessungen. Sinkende MMP14-RNA beweist keinen verminderten Matrixabbau.

Nächster unterscheidender Schritt: tierbezogene Zelltypdaten und Verarbeitungsmetadaten beschaffen, danach Protein/Aktivität und Kollagenbildung/-abbau unabhängig prüfen. Ein späterer Interventionsversuch bei bestehender Fibrose braucht passende Absetzkontrollen und Sicherheitsmessungen. Keine belastbare RNA-zu-Kappa- oder RNA-zu-Arzneimittel-Parameterzuordnung; keine neue Arzneimittelsimulation oder Kalibrierung.

Two reviewed records (metadata, analysis) were added locally; idempotent replays added zero duplicates and both existing simulations were preserved. Goose/Ollama was queued with the confirmed installed hermes3:8b digest, but remained resource-blocked and was cancelled before inference. No local model answer or token-saving claim was integrated. All numerical calculations ran locally in Python. / Zwei geprüfte Einträge wurden lokal ergänzt; Wiederholungen ohne Duplikate, beide Simulationen erhalten. Goose/Ollama blieb ressourcenbedingt blockiert und wurde vor Inferenz abgebrochen. Keine übernommenen KI-Antworten oder behauptete Tokenersparnis; sämtliche Zahlen lokal mit Python berechnet.

**Scope:** software verification passed within the stated tests; reported QC group sizes reproduced; broader publication reproduction incomplete; no calibration, independent biological validation, demonstrated human transferability or clinical usability.

**Geltungsbereich:** Softwareprüfungen bestanden; publizierte QC-Gruppengrößen reproduziert; umfassende Publikationsreproduktion unvollständig. Keine Kalibrierung, unabhängige biologische Validierung, nachgewiesene Übertragbarkeit auf Menschen oder klinische Einsatzfähigkeit.

## Provenance, rights and reproduction / Herkunft, Rechte und Wiederholung

[Provenance and source hashes](../Research/GEOSampleCheck/provenance.json) · [Commands and resume](../Research/GEOSampleCheck/README.md). The original archive remains private; code and derived analytical metrics only are published. No license was found in the pinned author repository tree; its R source is not redistributed. The article is CC BY-NC-ND4.0; its files are not relicensed by this project's MIT license. The attempted supplementary PDF returned HTML, so the supplement was not read. No individual-cell records, correspondence, clinical data or native worker logs are published.

Originalarchiv und Autorencode bleiben lokal. Veröffentlicht werden eigener Code und abgeleitete Prüfkennzahlen. Die MIT-Lizenz des Projekts ändert keine Fremdrechte. Das Zusatz-PDF war über den geprüften Zugang nicht abrufbar; keine behauptete Auswertung. Keine Veröffentlichung von Einzelzelllisten, Korrespondenz oder privaten Protokollen.
