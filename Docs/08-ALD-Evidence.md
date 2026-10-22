# Alkoholassoziierte Lebererkrankung: integrierte Forschungsevidenz

Stand der gezielten Recherche: **22.10.2026**. Fünf überprüfte Primärarbeiten zu alkoholassoziierter Lebererkrankung (ALD). Dies ist ein kuratierter Forschungsdatensatz, keine vollständige systematische Literaturübersicht. Ergebnisse anderer Ätiologien wurden nicht als ALD-Wirksamkeitsdaten übernommen.

## Was die Integration leistet

Die Evidenzebene erfasst Studienpopulation, Exposition, Design, Endpunkt, Nachbeobachtung, veröffentlichte Aggregate, Quelle und Grenzen als eigene Forschungsobjekte. Sie ermöglicht prüfbare deskriptive Kohortenstatistik. Diese beobachteten Daten bleiben getrennt vom hypothetischen Simulationslauf und dessen Parameter-Ensemble.

Die bestehende ODE **`hepatosim.liver-ode@0.1.0` bleibt unverändert und unkalibriert**. Ein neuer Evidenzdatensatz macht die bisherigen acht Raten, Laborabbildungen oder Modelltage nicht nachträglich zu klinisch geschätzten Größen. Aussagen zur Evidenz und zur Vorhersagegüte erhalten deshalb getrennte Kennzeichnungen.

## Quellen und extrahierte Endpunkte

| Quelle | Population, Design und zentraler Befund | Zulässige Verwendung |
|---|---|---|
| Hofer et al., 2023, *Alcohol Abstinence Improves Prognosis Across All Stages of Portal Hypertension in Alcohol-Related Cirrhosis*. [PubMed 36481475](https://pubmed.ncbi.nlm.nih.gov/36481475/), [DOI](https://doi.org/10.1016/j.cgh.2022.11.033) | Beobachtende Einzentrumsstudie; 320 Patienten mit HVPG ≥10 mmHg. Publizierte Dreijahres-Dekompensationswahrscheinlichkeit bei HVPG 10–19: 32,4 % versus 60,0 %; bei HVPG ≥20: 57,5 % versus 82,6 %; jeweils abstinent versus weiterer Konsum. | Klinischer Kontext für Abstinenz und portale Hypertension. Zeitpunktschätzungen; keine binomialen Ereigniszahlen daraus erzeugen. Nicht randomisiert. |
| Hofer et al., 2023, *Hepatic recompensation according to Baveno VII criteria is linked to a significant survival benefit in decompensated alcohol-related cirrhosis*. [PubMed 37469291](https://pubmed.ncbi.nlm.nih.gov/37469291/), [DOI](https://doi.org/10.1111/liv.15676) | Retrospektive Kohorte: **37/204** abstinente, dekompensierte ALD-Patienten erreichten klinische Rekompensation. Median-Follow-up **24,4 Monate**, IQR 10,9–50,4. | Beobachteter Kohortenanteil; keine feste Zweijahreswahrscheinlichkeit. Selektierte HVPG-Population; Abstinenzerfassung begrenzt. |
| Hofer et al., 2026, *Incidence and implications of abstinence-induced recompensation in alcohol-related cirrhosis*. [PubMed 41580090](https://pubmed.ncbi.nlm.nih.gov/41580090/), [DOI](https://doi.org/10.1016/j.jhep.2026.01.007) | Retrospektiv, 17 Zentren: **197/633** Rekompensationen während median **36,3 Monaten**, IQR 19,2–63,2. Der rohe Anteil **31,1 %** unterscheidet sich von der veröffentlichten kumulativen Fünfjahresinzidenz **33,8 %**. | Deskriptiver Anteil und publizierte Zeitpunktschätzung getrennt speichern. Unterschiede in Population, Therapie und Beobachtung berücksichtigen; keine randomisierte Wirkungsschätzung. |
| Gianni et al., 2017, *Prospective Evaluation of Liver Stiffness Using Transient Elastography in Alcoholic Patients Following Abstinence*. [PubMed 27542989](https://pubmed.ncbi.nlm.nih.gov/27542989/), [DOI](https://doi.org/10.1093/alcalc/agw053) | Prospektive Untersuchung von 64 Personen. Bei Abstinenten sank die mittlere Steifigkeit nach vier Wochen von 9,2 auf 6,9 kPa. | Frühe Steifigkeitsänderungen müssen von histologischer Fibroseregression unterschieden werden. Kleine Studie, begrenzte spätere Wiederteilnahme. Keine direkte Kollagen-Zeitreihe. |
| Hofer et al., 2025, *Inflammation remains a dynamic component of portal hypertension in regressive alcohol-related cirrhosis*. [PubMed 39708052](https://pubmed.ncbi.nlm.nih.gov/39708052/), [DOI](https://doi.org/10.1002/ueg2.12643), [Volltext](https://pmc.ncbi.nlm.nih.gov/articles/PMC11999040/) | Humane Beobachtungsanalyse mit 128 abstinenten ALD-Patienten: Entzündung war mit höherem als aus Lebersteifigkeit erwartetem HVPG verbunden. Gesonderter tierexperimenteller Studienteil. | Motiviert die getrennte Betrachtung dynamischer Entzündung und struktureller Veränderungen. Tierexperimentelle Toxinmodelle begründen keine menschlichen ALD-Reaktionszeiten. |

Die klinische Rekompensation ist ein zusammengesetzter Endpunkt. Die Studien verwenden Baveno-VII-bezogene Definitionen: Ursachenbehandlung beziehungsweise anhaltende Abstinenz, Auflösung von Aszites und hepatischer Enzephalopathie ohne jeweilige Therapie, ein Zeitraum ohne Varizenblutung und gebesserte Leberfunktion. Die genaue **studieneigene Operationalisierung bleibt versioniert**; sie darf nicht aus einem einzelnen Laborwert oder einem simulierten Reserveindex rekonstruiert werden.

Patientenüberlappung zwischen den Wiener Arbeiten und der späteren multizentrischen Studie ist nicht ausgeschlossen. Die Datensätze werden daher nicht als unabhängige Stichproben zusammengefasst. Eine gemeinsame Autorenschaft beweist weder Überlappung noch Unabhängigkeit; für eine spätere Metaanalyse wäre eine explizite Kohortenprüfung erforderlich.

## Was die neu berechnete Statistik bedeutet

Für ausdrücklich publizierte Zähler und Nenner wird der rohe Anteil `p = k/n` berechnet. Ein zweiseitiges 95-%-Wilson-Intervall verwendet `z = 1.959963984540054`:

```text
Nenner      = 1 + z²/n
Zentrum     = (p + z²/(2n)) / Nenner
Halbbreite  = z * sqrt(p(1-p)/n + z²/(4n²)) / Nenner
Intervall   = Zentrum ± Halbbreite
```

Dies ist eine **neu berechnete deskriptive Intervallschätzung unter einem Binomialmodell**, kein von den Autoren berichtetes Überlebensintervall. Unterschiedliche Beobachtungszeiten, Zensierung, Tod und Transplantation werden dadurch nicht berücksichtigt. Die Endpunkte der beiden Rekompensationskohorten bezeichnen Beobachtungen während der jeweiligen Nachbeobachtung, keine persönliche Chance bis zu einem gemeinsamen Datum. Ein Wilson-Intervall korrigiert weder Selektionsbias noch Confounding.

Veröffentlichte kumulative Inzidenzen und Hazard Ratios bleiben separate Ergebnisarten. Eine kumulative Inzidenz darf nicht mit `Prozent × Gesamt-N` in vermeintliche Ereigniszahlen umgewandelt werden. Eine Hazard Ratio ist kein Risikoverhältnis und kein Multiplikator für eine ODE-Rate. Ein nicht beobachtetes Ereignis beweist kein Nullrisiko. Ein Mittelwert mit Standardabweichung ist kein Konfidenzintervall; gepaarte Änderungen benötigen geeignete Streuungsinformationen.

## Konsequenzen für das wissenschaftliche Modell

1. **Abstinenz ist eine klinische Exposition.** Der aktuelle Slider „Schädigungsfaktor“ ist ein hypothetischer Multiplikator. Er ist weder Gramm Alkohol pro Tag noch ein validiertes Abstinenzmodell. Die Kohorten liefern keine direkte Schätzung seines Zahlenwertes.
2. **Fibrose, Steifigkeit und Leberfunktion sind unterschiedliche Größen.** Eine schnelle Steifigkeitsabnahme ist kein Beweis einer gleich schnellen Kollagenresorption. Weder kPa noch histologische Stadien lassen sich ohne Messmodell auf `fibrosis ∈ [0,1]` abbilden.
3. **Portale Hypertension benötigt eine hämodynamische Beschreibung.** Der bestehende Widerstandsindex ist kein HVPG. Eine Überführung in mmHg verlangt unter anderem validierte Beziehungen zu Blutfluss, strukturellen und dynamischen Widerstandsanteilen sowie Messbedingungen.
4. **Regeneration ist hier nicht direkt quantifiziert.** Klinische Besserung kann unterschiedliche biologische Prozesse und Therapiewirkungen zusammenfassen. Die ausgewählten Aggregate messen keine individuelle Hepatozytenregenerationsrate und identifizieren keine menschliche Kollagenabbaukonstante.
5. **Rekompensation benötigt Ereignis- und Behandlungsverläufe.** Die vier normierten ODE-Zustände enthalten diese Informationen nicht. Eine willkürliche Schwelle wäre eine zusätzliche, unvalidierte Annahme.

Zwei Rekompensationsanteile können acht biologische Raten und zusätzliche Beobachtungsmodelle nicht eindeutig bestimmen. Selbst ein numerisch perfekter Fit wäre kein Identifizierbarkeitsnachweis. Die unterschiedliche Nachbeobachtung und mögliche Kohortenüberlappung würden einen solchen Fit zusätzlich verzerren.

## Nächster prüfbarer Kalibrierungsplan

| Gate | Konkrete Arbeit | Freigabekriterium |
|---|---|---|
| A: belastbarer Evidenzkatalog | Extraktionen unabhängig gegen Abstract/Volltext prüfen; Nenner, Endpunkt, Zeitbezug und fehlende Angaben erfassen; Quellen- und Evidenzversion getrennt von Modellversion führen. | Keine erfundenen Ereigniszahlen; jede Kennzahl rückverfolgbar; keine stillschweigende Vermischung von Rohanteil und Ereigniszeitanalyse. |
| B: beobachtbare Zielgröße | Zunächst eine eng definierte Forschungsfrage zu wiederholtem HVPG und Labor-/Steifigkeitsverlauf bei abstinenten ALD-Patienten festlegen. Zeitnullpunkt, Exposition, Messfehler und Begleittherapien präregistrieren. | Einheit, Population und Vorhersagehorizont eindeutig; Studienvariablen besitzen eine dokumentierte Messbeziehung. |
| C: geeignete Daten | Rechtskonform zugängliche longitudinale Daten mit Messzeitpunkten, Abstinenz-/Rückfallinformation, Behandlungen und Ereignissen beschaffen. Herkunft und mögliche Mehrfachverwendung von Patienten prüfen. | Ausreichende wiederholte Messungen; dokumentierte Missingness und Zensierung; Datenschutz-/Zweckbindung geklärt. Derzeit liegen solche Individualdaten hier nicht vor. |
| D: sparsame Modellbildung | Ein minimales Beobachtungsmodell für die gewählte Zielgröße formulieren; nur identifizierbare Parameter freigeben. Biologischen Zustandskern und ein späteres klinisches Ereignis-/Mehrzustandsmodell getrennt entwickeln. | Strukturelle und praktische Identifizierbarkeit, Profil-Likelihood beziehungsweise geeignete Posterior-Diagnostik und numerische Verifikation dokumentiert. |
| E: Kalibrierung und Vergleich | Gegen einfache Referenzmodelle vergleichen; Patientengruppen und Zentren vollständig zwischen Training und Test trennen. Zeitabhängige Exposition, Begleittherapie, konkurrierende Ereignisse und Missingness behandeln. | Vorab definierte Gütemaße, keine Patienten-/Zeit-Leckage; Unsicherheit umfasst Parameter-, Beobachtungs- und Modellabweichung. |
| F: externe Prüfung | Zeitlich und räumlich unabhängige Kohorte; je nach Ziel Kalibrierung, Fehler, Intervallabdeckung, zeitabhängige Diskrimination und klinische Plausibilität prüfen. | Vorab festgelegte Akzeptanzgrenzen erreicht und unabhängig hepatologisch/biometrisch geprüft. Erst danach darf eine konkrete validierte Aussage benannt werden. |

Auch ein extern geprüftes Forschungsmodell wäre damit nicht automatisch für individuelle Therapieentscheidungen oder als Medizinprodukt freigegeben. Der vorliegende Schritt integriert reale wissenschaftliche Beobachtungen und prüfbare Statistik; die klinische Validierung des Simulationskerns bleibt offen.
