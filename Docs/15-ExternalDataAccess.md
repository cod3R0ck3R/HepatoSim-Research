# External collagen data: access and eligibility audit

22 October 2026. This report corrects the earlier access gap; it does not report an independent prediction test. The earlier failed downloads remain part of the audit trail.

## Executed work

Public NCBI Article Datasets metadata and two supplements were retrieved over HTTPS. Both PDFs matched the MD5 supplied in the respective metadata, had PDF signatures and were converted with the installed Headroom MarkItDown command (exit 0). The Xie supplement contains source immunoblots; it did not provide a numerical collagen time series. Hofer Supplementary Table 2 contains separate CCl4 and TAA summaries, unlike the pooled main table. A local importer extracted four CCl4 groups. The integrated importer passed six tests through the central coordinator (0.002 seconds, exit 0), including changed-transcription rejection and preservation of existing evidence. The import itself completed successfully. No individual animal observations were reconstructed, no figures were digitized and no model was fitted.

Source: Hofer et al., *Inflammation remains a dynamic component of portal hypertension in regressive alcohol-related cirrhosis*, [DOI 10.1002/ueg2.12643](https://doi.org/10.1002/ueg2.12643), [PMC11999040](https://pmc.ncbi.nlm.nih.gov/articles/PMC11999040/), Supplementary Table 2, page 13. The inspected main-text methods specify male C57BL/6JRj mice, twelve weeks of CCl4 induction, three administrations per week, and sacrifice groups at withdrawal and one/two weeks later. The human alcohol-related cirrhosis cohort in the same paper is a different dataset and is not used in this importer.

The four group sizes are 5 healthy controls, 6 at peak disease, 7 after one week and 7 after two weeks. The endpoint is Picro-Sirius-red collagen proportionate area (CPA, percent). Table parentheses denote quartiles, not standard deviations or confidence limits. These are separate sacrifice groups, not longitudinal observations from the same animals. Healthy controls have no invented withdrawal time. No pooling with TAA, denominator normalization or animal-level imputation is performed.

## Why the biological benchmark is still open

The current reference uses sixteen surrogate TGF-beta pulses separated by 84 hours, with the last pulse at model day 56.5. Hofer uses a different exposure schedule and a longer induction period. Shifting the horizontal axis would not resolve this mismatch. COL1 tokens, including their two remodeling pools, have no externally established quantitative mapping to total PSR-positive area in this protocol. A visually similar recovery curve would therefore not be a validated biological prediction.

Hofer values have now been inspected for eligibility. They are a candidate external dataset, not a blinded holdout. A future protocol must distinguish publication date from confirmation that the dataset was not used in model development. It must prospectively specify exposure adaptation, observation mapping, data roles, a simple comparator, errors and uncertainty. If these observations are used to choose or fit that mapping, they become development data; a separate study/protocol is then needed for an independent prediction claim. No random split of these four aggregate groups is planned.

The remaining data gap is now specific: compatible exposure/measurement mapping, individual values or justified aggregate uncertainty, and a qualified untouched evaluation cohort. Lack of downloadable collagen aggregates is no longer a correct blanket description.

## Reproduce the local import

Download the metadata and supplement from the public NCBI dataset:

- [Versioned metadata](https://pmc-oa-opendata.s3.amazonaws.com/PMC11999040.1/PMC11999040.1.json)
- [Original supplement](https://pmc-oa-opendata.s3.amazonaws.com/PMC11999040.1/UEG2-13-317-s004.pdf)
- PDF SHA-256: `b26583fb964fa2ec4629725a35458014ddfa34e7387e679306aab181dcfeea2a`
- Reviewed Markdown SHA-256: `2dfd2736ef980e5b3c02bd71778412ab2aa52ed22b569109d8d05884301c3743`

Convert the PDF with the installed MarkItDown tool, saving its Markdown output locally. Then, from the project directory:

```sh
python3 -B Research/Data/extract_hofer_cpa.py --markdown /absolute/path/UEG2-13-317-s004.md --source-pdf /absolute/path/UEG2-13-317-s004.pdf --output /absolute/path/Hofer-CCl4-CPA.csv
python3 -B -m unittest discover -s Research/Data -p 'test_*.py'
```

Use the coordinator wrapper on a shared host. Inputs must match the reviewed PDF and transcription; a converter producing different Markdown requires a new source review, not silent acceptance. Output/provenance files must be new. The provenance records input/output/importer hashes. The source license is CC BY-NC-ND 4.0; original PDFs and extracted data remain local rather than being included in the public software export. This project distributes only the importer, synthetic parser fixtures, source links and this audit. It makes no new licensing claim over the source data.

## Deutsch

Der über NCBI tatsächlich heruntergeladene Hofer-Anhang enthält getrennte CCl4-Kollagenaggregate mit Gruppengrößen und Quartilen. PDF-Prüfsummen, Konvertierung, sechs Importertests und der lokale Import wurden geprüft. Frühere erfolglose Zugänge werden dadurch präzisiert, nicht gelöscht. Die Daten betreffen männliche C57BL/6JRj-Mäuse mit zwölf Wochen Schädigung und getrennten Opferungsgruppen. Die menschliche ALD-Kohorte derselben Publikation wird nicht importiert.

Eine unabhängige Vorhersageprüfung wurde nicht durchgeführt. Expositionsfolge und Messabbildung passen noch nicht zum Referenzlauf. Bereits gesichtete Werte sind keine verblindete Prüfmenge; eine spätere Anpassung an diese Werte macht sie zu Entwicklungsdaten. Quartile sind keine Standardabweichungen oder Konfidenzintervalle. Keine erfundenen Tierdaten, keine TAA-Poolung, keine klinische Übertragung. Originaldateien und abgeleitete Daten bleiben lokal; öffentliche Quellen, Hashes und der getestete Importer ermöglichen die nachvollziehbare Prüfung.
