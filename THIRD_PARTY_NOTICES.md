# Third-party notices and license status / Fremdlizenzen und Lizenzstatus

## English

**Original HepatoSim code and original project documentation:** [MIT License](LICENSE), copyright 2026 Johnnie 4 free, selected by the project owner on 24 October 2026. This grant also covers the original HepatoSim application code in release 0.1.0-alpha.1. It does not relicense third-party models, software, publications or datasets. Preserve their separate notices and comply with their terms when combining or redistributing components.

**Original HSC models:** Bouguéon and contributors, `MBougueon/HSC_model_Kappa`, pinned commit `773a84e65b514b969db20c57b6bf0ba97c1d32fb`. The unmodified models are separate files under `Research/Reference/vendor/HSC_model_Kappa`; their original [AGPL license](Research/Reference/vendor/HSC_model_Kappa/LICENSE) and notices must remain. This document does not relicense them or waive obligations for derivatives/integrations. The examined `MBougueon/simulation_pipeline` commit is recorded in the source lock; no claim of a complete working pipeline is made.

**KaSim:** external KappaTools runtime v4.1.3.1, source commit and retrieval/hash information in `Research/Reference/runtime-lock.json`. It is not bundled as a binary in this project. Its own license applies; a different binary requires explicit reproducibility review. The unresolved article runtime designation is documented in the research report.

**Publications and research data:** references and limited factual summaries are included. Full-text local review copies, publisher figures and private logs are not automatically cleared for redistribution. The Bouguéon article is CC BY 4.0; this does not license other cited articles or their datasets. No patient-level data have been imported into these candidate dossiers. Public-release selection must verify each file and preserve attribution. Derived simulation traces are model outputs, not experimental measurements.

## Deutsch

**Eigener HepatoSim-Code und eigene Projektdokumentation:** [MIT-Lizenz](LICENSE), Copyright 2026 Johnnie 4 free, vom Projektinhaber am 24. Oktober 2026 gewählt. Die Freigabe umfasst auch den eigenen Anwendungscode der Version 0.1.0-alpha.1. Fremde Modelle, Software, Publikationen und Datensätze werden nicht neu lizenziert. Deren Hinweise erhalten und ihre Bedingungen bei Kombination oder Weitergabe beachten.

**Originale HSC-Modelle:** Bouguéon und Mitwirkende, `MBougueon/HSC_model_Kappa`, festgelegter Commit `773a84e65b514b969db20c57b6bf0ba97c1d32fb`. Unveränderte Modelle liegen separat unter `Research/Reference/vendor/HSC_model_Kappa`; originale [AGPL-Lizenz](Research/Reference/vendor/HSC_model_Kappa/LICENSE) und Hinweise bleiben erhalten. Keine Neulizenzierung oder Befreiung von Pflichten für Ableitungen/Integrationen. Der geprüfte `MBougueon/simulation_pipeline`-Commit steht im Source-Lock; eine vollständige funktionsfähige Pipeline wird nicht behauptet.

**KaSim:** externe KappaTools-Runtime v4.1.3.1; Quellcommit, Bezug und Hashes stehen in `Research/Reference/runtime-lock.json`. Keine Binärdatei ist in diesem Projekt eingebettet. Die eigene Lizenz gilt; eine andere Binärdatei benötigt ausdrückliche Reproduzierbarkeitsprüfung. Die ungeklärte Runtimebezeichnung des Artikels ist im Forschungsbericht dokumentiert.

**Publikationen und Forschungsdaten:** Enthalten sind Referenzen und begrenzte sachliche Zusammenfassungen. Lokale Volltext-Prüfkopien, Verlagsabbildungen und private Logs sind nicht automatisch zur Weitergabe freigegeben. Der Bouguéon-Artikel ist CC BY 4.0; das lizenziert keine anderen zitierten Artikel oder Datensätze. Keine personenbezogenen Einzelmessungen wurden in diese Dossiers importiert. Die öffentliche Dateiauswahl muss Rechte je Datei prüfen und Attribution erhalten. Erzeugte Simulationsverläufe sind Modellwerte, keine experimentellen Messungen.


## E-MEXP-3177 analysis, 24 October 2026

The new expression analysis cites Ramachandran et al. (2012), DOI10.1073/pnas.1119964109, and the EMBL-EBI E-MEXP-3177 archive. The source matrix, IDF/SDRF files, article and publisher figures are not redistributed. Only newly computed distance/permutation aggregates, input checksums and original analysis code/report are added. Obtain source files from the documented archive under its applicable terms. The project owner has subsequently authorized MIT for original project code; source-data terms remain separate.

## GSE210077 / Watson human liver study

Watson et al., Nature Communications (2025), DOI 10.1038/s41467-024-55325-4; GEO GSE210077; HCA project 64809a52-f703-4aec-b3a5-eca808a971d0. Source matrices, single-nucleus labels, workbook and publications are not included. Their original terms remain applicable; our MIT license does not relicense them. Hash-pinned retrieval metadata and newly computed donor/cell-type aggregates document provenance. See Research/DonorCellCheck/provenance.json.

### GSE244832 and reanalysis mapping

Raw GEO matrices, original workbook, PDFs and supplementary ZIP are retrieved privately; no redistribution here. Source records and derived analyses cite DOI10.1016/j.jhep.2024.10.044 and DOI10.3390/ijms27177920 (the latter CC BY4.0). No third-party code copied; upstream rights unchanged. Own analysis code/results follow the project MIT license.

## Metadata follow-up2026-10-26

GSE244832 provenance tables are limited derived metadata with primary source links and hashes; source workbook/matrix not redistributed. Lee etal., JCI Insight2025, DOI10.1172/jci.insight.195242, is statedCCBY4.0 by the publisher. Its Supporting Data Values workbook is retained locally; this update distributes only its retrieval receipt and sheet headings. No private logs or correspondence are included.

## Lee et al.2025 ETS1 source-data audit

Lee et al., ETS1 suppresses hepatic stellate cell activation and liver fibrosis, JCI Insight2025;10(24):e195242, DOI10.1172/jci.insight.195242. Article declares CC BY4.0. Original workbook retained locally with provenance; not redistributed. This repository publishes original audit code and derived aggregate comparisons only, not publisher figures, raw images or confidential correspondence.

**HSCRobustness:** The two persistence-contrast Kappa models derive from the same pinned original HSC model and retain AGPL under Research/HSCRobustness/models/LICENSE. Own Python analysis remains under the repository MIT license. / Die beiden Kappa-Persistenzkontraste sind Ableitungen desselben festgelegten Originalmodells und behalten AGPL; eigener Python-Auswertungscode bleibt unter MIT.
