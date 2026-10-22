# Bouguéon 2024: Referenzauswahl und Datenprüfung

Stand: 22.10.2026. Quellenprüfung vor Ausführung einer wissenschaftlichen Referenzsimulation. Dieses Dokument enthält keine erzeugten Simulationsresultate, keine digitalisierten Kurven und keine medizinische Validierung.

## Entscheidungsvorschlag

Als ersten technischen Reproduktionsfall **Bouguéon et al., Abbildung 2 B2/B3, Modellfamilie `reactMFB-with-inactivation`, 5 % Inaktivierung reaktivierter Myofibroblasten** wählen. Das Modell und seine Parameter sind öffentlich verfügbar; die Abbildung zeigt HSC-Zustände und Kollagen nach wiederholter Stimulation und deren Ende. Sie ist für eine nachvollziehbare Referenzimplementierung geeigneter als ein eigenes Humanmodell.

**Der unveränderte Repository-Default und die aus der Abbildungslegende abgeleitete Variante sind nicht identisch.** Beide müssen getrennte Protokollkennungen erhalten. Eine genaue Reproduktion der veröffentlichten Kurven ist ohne Originalkonfiguration, Seeds und numerische Kurvendaten derzeit nicht nachgewiesen. Das Reproduktionsziel ist zunächst die Ausführung und dokumentierte Prüfung des veröffentlichten Modells. Ein Erfolg wäre keine unabhängige biologische Validierung.

Primärquelle: M. Bouguéon et al., *A rule-based multiscale model of hepatic stellate cell plasticity: Critical role of the inactivation loop in fibrosis progression*, PLoS Computational Biology 20(7), e1011858, 29.07.2024. [DOI](https://doi.org/10.1371/journal.pcbi.1011858), [Artikel](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1011858), [maschinenlesbarer Volltext](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11309422/fullTextXML).

## Geltungsbereich des Modells

Das regelbasierte, stochastische Kappa-Modell beschreibt die Plastizität hepatischer Sternzellen. Es enthält qHSC, aHSC, MFB, iHSC, react_HSC, react_MFB und apoptotische/seneszente MFB sowie freie/gebundene TGFβ1-Pools und Kollagen mit hoher/niedriger Umbaudynamik. Aktivierungszähler bilden Zwischenstufen ab. KaSim führt stochastische Reaktionsereignisse aus.

Die maßgebliche Kalibrierung betrifft **CCl4-induzierte Fibrose in Mäusen**; Einzelparameter stammen auch aus Zellkultur-/Rezeptorliteratur, unter anderem aus Rattenexperimenten. Der Artikel ergänzt einen Vergleich mit menschlichen NAFLD/NASH-Transkriptomen. Er ist **kein parametrisiertes Modell der menschlichen alkoholbedingten Zirrhose**, kein umfassendes Leberfunktionsmodell und kein Modell für individuelle Prognosen, Laborverläufe, Dekompensation oder Überleben.

Die Abbildung von Toxinexposition auf TGFβ1-Pulse, der 5-%-Inaktivierungsanteil und die Kollagen-Umbauraten sind Modellannahmen beziehungsweise empirische Parameter. Ein experimentell beobachteter Mechanismus validiert weder deren Zahlenwerte noch sämtliche daraus entstehenden Vorhersagen.

## Reproduktionsprotokoll und Messgrößen

Die folgenden Werte dienen der vorläufigen Spezifikation. Die ausführende Instanz muss ihren endgültigen Benchmark mit konkreten Seeds, Beobachtungszeiten und erlaubten Änderungen separat einfrieren.

| Element | Beleg / Vorgabe | Konsequenz |
|---|---|---|
| Modell | `reactMFB-with-inactivation.ka` | Unveränderte Originaldatei archivieren; Adapter getrennt halten. |
| Ausgangszustand | 10 000 quieszente HSC; freies/gebundenes TGFβ1 zunächst 0; COL1 hoch 0,5, niedrig 0 | Modellzellzahl, keine Patientenzellzahl. |
| Inaktivierung | MFB 0,45; react_MFB 0,05 | Source-Zeilen 96–99; die 5-%-Variante entspricht Fig. 2 B. |
| Zeit | Tage; erste Stimulationsschwelle Tag 4; Abstand 84 Stunden = 3,5 Tage; 16 Pulse | Nominale Schwellen `4 + 3,5·k`, k = 0…15; letzte Schwelle Tag 56,5. Source verwendet strikt `T > clock`; tatsächliche Auslösezeiten protokollieren. |
| Unveränderter Default | `TGFB1_pool_by_cell = 6`, 10 000 Rezeptoreinheiten; Input = Zellzahl × Pool × Rezeptoreinheiten | **60 000 TGFβ1-Einheiten je initialer HSC je Puls**; S2 Table Zeile 10 stimmt damit überein. |
| Captionvariante | Fig. 2 nennt 10 000 Moleküle je Zelle | Entspräche explizit `TGFB1_pool_by_cell = 1`. Nicht heimlich zum Default erklären; Original-Run-Konfiguration unbestätigt. |
| Zweite Stimulationsserie | `second_input = 0` | Im Default ausgeschaltet. |
| Simulationsende | Source-Stop nach `4 + 16·3,5 + 182,5 = 242,5` Tagen | Zeitkonvention beginnt bei Tag 60, also einen Abstand nach letzter nomineller Pulsschwelle. |
| Recovery-Snapshots | Source-Schwellen Tag 90 und Tag 239 | Source berechnet `input_time + iteration·interval + 30/179`; nicht mit exakt 30/179 Tagen nach letzter nomineller Pulszeit gleichsetzen. |
| Wiederholungen | Fig. 2: 10 Läufe; Zellverläufe als Mittel, alle 10 COL1-Kurven einzeln | Neue Seeds erlauben Verteilungs-/Merkmalsvergleich, keine behauptete punktweise Wiederholung unbekannter Originalseeds. |
| αSMA | aHSC + MFB + react_HSC + react_MFB | Zellanzahl im Modell; keine direkte Umrechnung in histologische αSMA-positive Fläche ohne Messmodell. |
| COL1 | `COL1 remodeling high + COL1 remodeling low` | **A.U.**, nach Artikel an prozentualer Kollagenablagerungsfläche orientiert; keine Molekülmasse, kein Hydroxyprolin und keine universell kalibrierte CPA-Messung. |

Bei Quotienten Baseline explizit definieren: initialer Tokenwert 0,5 ist nicht automatisch identisch mit dem stochastischen Wert unmittelbar vor dem ersten Puls. Zeitpunkte für Plateau und Regression müssen vor Ausführung feststehen; keine Auswahl günstiger Zeiten nach Betrachtung der Resultate.

## Widersprüche, die eine unveränderte Reproduktion begrenzen

Alle Zeilenangaben beziehen sich auf den unten eingefrorenen Commit des HSC-Repositories.

| Befund | Quellen | Behandlung |
|---|---|---|
| Stimulationsamplitude 10 000 gegenüber 60 000 | Fig. 2-Legende gegenüber S2 Table Zeile 10 und `.ka` 119–121, 349 | Default und Captionvariante getrennt. Ein im Artikel beschriebenes Sättigungsverhalten beweist keine numerische Identität. |
| react_MFB-Verdopplungszeit | S2 Table Zeile 25: 8,86 Tage; `.ka` 85, 110: 15,5/3,5 ≈ 4,43 Tage | Originalcode erhalten; nicht als geklärten Tippfehler korrigieren. |
| Uneinheitliche Zeitumrechnung zweier Kollagenregeln | `.ka` 317 und 320 multiplizieren im Nenner mit `time_unit`; parallele Regeln 318–324 dividieren durch `time_unit` | Potenziell erheblicher Unterschied; Original und jede wissenschaftlich begründete Korrektur wären verschiedene Modellversionen. |
| Zusätzliches ×10 in MFB-Kollagenproduktion | `.ka` 143–147, 154–157: Eingabewerte bereits zehnfach, danach bei MFB/react_MFB nochmals ×10 | Bei maximalen Aktivierungszählern rechnerisch 100:1 statt der im Artikel beschriebenen 10:1-Grundproduktion. Die Zeitumrechnungsabweichung ist davon unabhängig. |
| Halbwertszeiten als inverse Zeiten beschriftet | S2 Table etwa „75 days-1“, „3 min-1“; Supplementlegende bezeichnet Dauern als Halbzeiten, Source bildet `ln(2)/Dauer` | Tabellenetiketten nicht wörtlich als Raten importieren; Source-Ausdruck und physikalische Interpretation getrennt dokumentieren. |
| Zellvergleich 1,43-fach | Fig. 2-Legende nennt αSMA-Zellen; Kalibriertext nennt HSC-Anteil 10,6 ± 0,8 % → 14,3 ± 1,5 % | Quotient der genannten Mittel ist ≈1,35. Unterschied zwischen Zellzählung, Zellanteil und positiver Fläche nicht übergehen. |
| Mehrere Zeit-/Protokollangaben bei Fig. 4 | Siehe unten | Für den ersten Benchmark zurückstellen. |

Es wird hier keine der Abweichungen behoben. Eine Abweichung zwischen einem unveränderten Originalrun und der Publikationsbeschreibung ist ein Ergebnis der Reproduzierbarkeitsprüfung, kein Anlass für unprotokolliertes Nachjustieren.

## Kalibrierungsbelege und verfügbare Zahlen

Der Artikel, Abschnitt *Parameters for collagen 1 dynamic rules* (`sec031`), nennt aus Kisseleva 2012 übernommene Ziele: ungefähr **12-faches COL1 nach einem Monat** und **14-faches COL1 nach zwei Monaten** Stimulation. Die Regression wurde für schnellen Rückgang im ersten Monat und eine anschließende Annäherung an den Ausgangswert um sechs Monate kalibriert. Fig. 2 markiert den 14-fachen Vergleich ausdrücklich als ungefähren biologischen Bezugspunkt.

**Keine exakten numerischen COL1-Zielwerte nach zwei oder 30 Tagen Regression wurden im geprüften Haupttext oder in S2 Table gefunden.** S2 Table enthält Parameter, keine tierindividuelle Messreihe. Ein kurzer 2-/30-Tage-Test kann technische Kennzahlen liefern, aber ohne belegte Beobachtungswerte keine quantitative biologische Übereinstimmung belegen. Die Werte dürfen nicht aus Diagrammen geschätzt oder erfunden werden.

| Quelle | Rolle und Messung | Stichprobe / Zeit / Datenzugang |
|---|---|---|
| [Kisseleva 2012](https://doi.org/10.1073/pnas.1201840109), PNAS 109:9448–9453 | Hauptkalibrierung und Mechanismus HSC-Inaktivierung; Fig. 1 enthält Sirius-Red-Fläche, Hydroxyprolin, αSMA, Reporter und mRNA als unterschiedliche Endpunkte | Maus, CCl4 intragastrisch 16 Gaben über 2 Monate; Fig. 1: unbehandelt, Fibrose, 1/4 Monate Erholung. n der Kollagenreihe aus zugänglicher Legende nicht sicher bestimmt. Fig. 2A-Zellhistologie n=4/8/10; diese n nicht auf Kollagen übertragen. Kein maschinenlesbarer Kollagenrohdatensatz identifiziert. SI-PDF verlinkt, Download durch Zugriffsantwort blockiert. |
| [Troeger 2012](https://doi.org/10.1053/j.gastro.2012.06.036), Gastroenterology 143:1073–1083 | Ergänzende Kalibrierung/Mechanismus; HSC-Deaktivierung, Reporter, fibrogene Genexpression | Fig. 1: Balb/c, 4 CCl4-Injektionen 0,5 μl/g; unbehandelt n=4, 2 Tage n=6, 15 Tage n=5, 30 Tage n=8 für Ganzleber-qPCR/Histologie. Keine isolierte neue Validierung, da bereits in Modellparameter eingeflossen. Reporterfläche und Col1a1-mRNA sind nicht COL1-Tokenmasse. |
| [El Taghdouini 2015](https://doi.org/10.1186/s13069-015-0031-z) | Menschliche primäre HSC in vitro, Reversion/Reaktivierung; Parameterbezug des Modells | Mechanistische Ergänzung, kein longitudinaler menschlicher Kollagen- oder ALD-Datensatz. |
| [Govaere 2020](https://doi.org/10.1126/scitranslmed.aba4448); [GEO GSE135251](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE135251) | Menschliche NAFLD-RNA-Sequenzierung; Bouguéon vergleicht Inaktivierungssignaturen zwischen F0–F1 und F3–F4 | Bouguéon-Methoden: n=34 niedrige und n=68 hohe Fibrose; 21 595 Gene, nach Filter 16 021. GEO-Accession über GEO-Suchtreffer und zugeordnete Veröffentlichungen bestätigt. Kein Kollagenzeitverlauf; bereits im Originalvergleich verwendet. Kein Patientendatensatz in HepatoSim importiert. |

Die n-Werte bezeichnen die konkret benannte Messung; unterschiedliche Messverfahren derselben Studie können andere Teilstichproben verwenden. Publizierte Mittelwerte, Mediane, SEM, SD und IQR dürfen nicht ineinander umgedeutet werden.

## Weitere Abbildungen und Originalvergleichsdaten

**Bouguéon Fig. 4:** Eigene weibliche C57Bl/6-Mäuse, sieben Wochen alt; Methoden nennen n=5 je Gruppe und Opferungszeit. CCl4 oral in Olivenöl, 2,4 g/kg Priming drei Tage vor wöchentlichen 1,6 g/kg, insgesamt zehn Wochen; Proben 24 Stunden nach letzter Gabe. Kollagen wird auf 20-μm-Gefrierschnitten durch SHG und ImageJ als Signalfläche/Gesamtfläche in Prozent erfasst, Mittel ± SD. Für den Regressionsarm nennen die Methoden vier Wochen Exposition und acht/15 Tage Erholung. Die Abbildungslegende beschreibt drei Modellpulse in Woche eins, dann wöchentlich; der Ergebnisteil enthält wiederum abweichende Zeitbezüge, darunter acht Wochen nach Entfernung. Keine numerische Tabelle der fünf Tiere pro Zeit/Gruppe identifiziert. Vor Nutzung Originaldaten und genaue Gruppenzuordnung klären. Die Behauptung der Autoren, ihr Modell zu validieren, ersetzt diese Prüfung nicht.

| Quelle / Abbildung | Protokoll und Messgröße | Einordnung / Lücke |
|---|---|---|
| Bouguéon S1 Fig | Alternative iHSC→qHSC-Reversion; gleiche Stimulationsidee | Legende nennt 10 Zell-Replikate, aber 5 COL1-Replikate. Andere Zielabbildung, nicht unbemerkt mit Fig. 2 vermischen. |
| [Sato 2021](https://doi.org/10.1111/jgh.15587), übernommen in S2 Fig A | DMN-Rattenmodell; Bouguéon simuliert 3 Pulse/Woche für 6 Wochen. Primärverlags-Suchtreffer nennt n=6–8 je experimenteller Gruppe | Volltextzugriff hier blockiert; n und Einheiten des konkret in S2 Fig A verwendeten Kollagenarms nicht sicher zugeordnet. Nicht für einen numerischen Test freigegeben. Im Original bereits verglichen. |
| [Abramovitch 2011](https://doi.org/10.1136/gut.2010.234666), S2 Fig B | TAA-Ratten; Bouguéon: 2 Pulse/Woche für 10 Wochen | Frei zugängliches Abstract identifiziert, aber genaue n/Fehlerbalken/Einheiten des übernommenen Arms nicht verifiziert. Keine erfundenen Vergleichszahlen. Im Original bereits verglichen. |
| [Farooq 2022](https://doi.org/10.3390/nu14020386), S2 Fig C | Männliche C57BL/6J, 10–12 Wochen alt, n=7/Gruppe; 5 oder 12 Wochen HFHCD, danach 4 oder 12 Wochen Standarddiät. Sirius-Red-Flächenanteil und SHG; Mittel ± SEM | Volltext zugänglich, Daten laut Erklärung im Artikel/Supplement. Bouguéon nennt ausdrücklich an die Ergebnisse angepasste Pulse: 6 alle 14 Tage für 84 Tage. Deshalb kein unbenutzter unabhängiger Validierungsdatensatz. Keine grafischen Werte digitalisiert. |

S1 Table enthält Signaturgene; S2 Table Modellparameter. Die zwei Supplementabbildungen enthalten Kurven/Bilddaten. In den beiden geprüften Git-Repositories liegen weder ein numerischer Fig.-2-Referenzexport noch die tierindividuellen Fig.-4-Messwerte. Die Data-Availability-Erklärung verlinkt Modellcode und Pipeline, nicht einen Rohdatenkatalog.

## Unabhängiger Kandidat für spätere Prüfung

**Hofer et al. 2025, [Inflammation remains a dynamic component of portal hypertension in regressive alcohol-related cirrhosis](https://doi.org/10.1002/ueg2.12643), [Volltext](https://pmc.ncbi.nlm.nih.gov/articles/PMC11999040/).** Nach Bouguéon veröffentlicht; keine Verwendung im 2024er Modell festgestellt. Dies ist ein Kandidat, kein bereits durchgeführter Validierungstest.

Tierarm: männliche C57BL/6JRj-Mäuse; CCl4 oral oder TAA intraperitoneal dreimal wöchentlich für zwölf Wochen; danach sieben oder 14 Tage ohne Toxin. 44 exponierte Tiere (20 CCl4, 24 TAA) und 13 Kontrollen. Fibrose: Picro-Sirius-Red, Kollagenflächenanteil CPA in %. Portalvenendruck durch direkte Kanülierung in mmHg. **Tabelle 1 liefert tatsächlich gedruckte Zahlen; keine Digitalisierung erforderlich:**

| Gruppe | n | CPA %, Median (IQR) | Portalvenendruck mmHg, Median (IQR) |
|---|---:|---:|---:|
| Gesund | 13 | 0,77 (0,73–0,97) | 5,4 (5,2–5,7) |
| Nach zwölf Wochen Exposition | 14 | 4,35 (3,79–16,20) | 8,3 (7,7–9,9) |
| Sieben Tage Regression | 15 | 4,33 (3,58–9,74) | 7,7 (7,2–8,2) |
| 14 Tage Regression | 15 | 3,29 (2,94–5,09) | 6,4 (6,0–8,1) |

**Grenzen:** Die Tabelle poolt CCl4 und TAA; für einen sauberen CCl4-Test sind toxin-, zeit- und messmethodenspezifische Daten nötig. Querschnittliche Opferungsgruppen sind keine individuellen Längsverläufe. IQR ist kein Konfidenzintervall des Medians. CPA ist nicht ohne Kalibrierung gleich dem COL1-Token. Der Humanarm mit 128 abstinenten ALD-Patienten und gleichzeitigen HVPG/LSM-Messungen ist ein anderer Teil der Studie und liefert keine direkte Validierung des HSC-Kollagenzeitverlaufs.

Die Datenverfügbarkeit lautet **auf begründete Anfrage beim korrespondierenden Autor**. Keine frei herunterladbaren individuellen Messwerte gefunden. Sinnvolle nächste Anfrage: Tier-ID, Toxin, Dosis/Datum letzter Gabe, Opferungszeit, CPA-Rohwert und Bildquantifizierung, fehlende Werte, Kontrollen und Zuordnung zu Tabelle 1. Es wurde keine Nachricht versandt.

Vor einem späteren externen Test: Intervention-zu-TGFβ1-Mapping und CPA-Messmodell ohne Kenntnis der Testresultate festlegen; Parameter einfrieren; nur klar bezeichnete Kalibrierungsdaten nutzen; Unsicherheit der Transformation mitführen. Wenn Hofer-Daten zur Parameteranpassung genutzt werden, sind sie für diese Modellversion keine unabhängigen Testdaten mehr.

## Provenienz und Lizenzen

| Artefakt | Fixierter Stand / Lizenzbeleg |
|---|---|
| [HSC_model_Kappa](https://github.com/MBougueon/HSC_model_Kappa) | Commit `773a84e65b514b969db20c57b6bf0ba97c1d32fb`; LICENSE: GNU AGPL Version 3. Quelldateiheader: Copyright 2022 Inserm, AGPL Version 3 **oder später**. |
| `reactMFB-with-inactivation.ka` | SHA-256 `dcfeae87699640cf917e038910402140528e93c0a09897664c3a336f7b397f7d` |
| [simulation_pipeline](https://github.com/MBougueon/simulation_pipeline) | Commit `8b10a8dc403190a0b198918f0288b3d962ab7d40`; LICENSE: GNU AGPL v3; Pythonheader ausdrücklich v3 oder später, Copyright 2022 Inserm. |
| `launch.py` | SHA-256 `16f04084d0c63082d57de240f83f2178c4cca0c8e42bbf6c54db8a64ec587733` |
| Bouguéon-Artikel/Supplement | Primär-XML nennt ausdrücklich [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), Copyright Autoren 2024. S1/S2 Table als Supplement dieser Publikation. |
| Farooq-Artikel | Primär-XML nennt ausdrücklich CC BY 4.0. |
| Hofer-Artikel | Primär-XML nennt ausdrücklich [CC BY-NC-ND 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0/). Keine pauschale Weitergabe bearbeiteter Abbildungen oder Rohdaten unter einer liberaleren Projektlizenz. |
| Kisseleva/Troeger und weitere Verlagsmaterialien | Kein frei übertragbares CC-BY-Nutzungsrecht für sämtliche Materialien in dieser Prüfung bestätigt. Zitation/Faktenextraktion bedeutet keine Lizenzübernahme. |

**Artikel- und Codelizenz sind verschieden.** CC BY der Publikation gilt nicht automatisch für die AGPL-Software. Originalcode und abgeleitete Kappa-Dateien samt Hinweisen erhalten; eine Weiterverteilung oder Integration muss AGPL-Bedingungen einschließlich eventueller Netzwerkbereitstellung beachten. Der Simulator selbst benötigt eine gesonderte Versions-/Lizenzprüfung durch die Laufzeitprüfung.

Das Original nennt **Kappa/KaSim 4.2.12 und OCaml 4.13.1**. Reproduktionsmetadaten müssen tatsächliche Binary-Version, Betriebssystem, Architektur, Modellhash, Parameterübersteuerungen, Seeds, Zeitkonventionen, Ausgabeintervall und Abbruchstatus erfassen.

Die veröffentlichte Python-Pipeline ist nicht ohne Prüfung als reproduzierbarer Runner zu übernehmen: `launch.py:24,175` importiert `utils`, die Datei fehlt im geprüften Commit; Zeile 100 erzeugt lediglich einen zufälligen Dateinamenszusatz, während der KaSim-Aufruf in Zeile 120 keinen expliziten Seed setzt. Außerdem verwendet er ein spezielles Eingabedatei-Glob. Eine alternative Aufrufhülle muss als eigene technische Ergänzung kenntlich bleiben.

## Abnahmekriterien vor Aussagen über Reproduktion

1. Originaldatei und Commit unverändert archiviert; alle Adapteränderungen separat dokumentiert.
2. Definiert, ob Default oder Captionvariante ausgeführt wird; alle verbleibenden Quellenkonflikte sichtbar.
3. Originalruntime oder begründete kompatible Runtime, konkrete Seeds, Zeitachse und Beobachtungsdefinitionen fixiert.
4. Numerische Referenzgrößen nur aus überprüfbarem Text/Tabellen oder gelieferten Originaldaten; fehlende 2-/30-Tage-Ziele bleiben fehlend.
5. Technischer Lauf, Verhaltensvergleich, Kalibrierung und unabhängige biologische Validierung als getrennte Evidenzstufen berichtet.
6. Keine Umdeutung in menschliche ALD-Verläufe, medizinisch zuverlässige Prognosen oder Behandlungsempfehlungen.

## Verwendete Zugänge und verbleibende Lücken

Bouguéon-Haupttext und beide XLSX-Supplemente wurden gelesen; XLSX über Headroom MarkItDown. Hofer und Farooq wurden als Europe-PMC-Volltext-XML geprüft. Troeger wurde über den NCBI-BioC-Volltext einschließlich Bildlegenden geprüft. Kisseleva-PNAS-Text und PubMed-Bildlegenden waren lesbar, das Appendix-PDF nicht. Sato/Abramovitch konnten für den spezifischen übernommenen Kollagenarm nicht bis zu n, Einheiten und Rohdaten verifiziert werden. Zugriffsbeschränkungen sind keine Aussage, dass diese Daten nicht existieren.

Lokale Prüfkörper liegen unter `work/reference-audit/`, die Original-Repositories unter `work/reference-repos/`; sie sind Arbeitsmaterial, kein neu erhobener Forschungsdatensatz. Dieses Dokument ist die Daten- und Quellenbewertung. Laufzeitbelege und Benchmarkentscheidungen anderer Arbeitspakete sind damit nicht vorweggenommen.
