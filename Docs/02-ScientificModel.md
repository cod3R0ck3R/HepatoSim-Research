# Wissenschaftliches Modell v0.1.0

## Status und Forschungsfrage

**Experimentelles, unkalibriertes Demonstrationsmodell. Keine klinisch validierte Vorhersage.** Vier normierte Zustände bilden qualitative Rückkopplungen zwischen Schädigung, Regeneration, Entzündung, Sternzellaktivierung und Kollagen ab. Das Modell untersucht, ob definierte hypothetische Parameteränderungen qualitativ plausible Verläufe erzeugen. Es prognostiziert weder individuelle Krankheitsverläufe noch Überleben, Dekompensation oder Therapieerfolg.

Die Zeitachse verwendet Tage als Modellkonvention. **Alle Zahlenwerte, Zeitskalen, Kopplungen und Laborabbildungen sind frei gewählte heuristische Parameter**, nicht aus den Quellen geschätzt. Insbesondere bedeutet `fibrosis = 0.5` weder F2 noch 50 % histologischen Kollagenanteil. Gesunde, kompensierte und dekompensierte Zirrhose sind keine identifizierten Modellklassen.

## Evidenz und Übertragungsgrenzen

Online überprüft am 22.10.2026; DOI/PMID identifizieren die zugrunde liegenden Arbeiten. Die Quellen begründen nur biologische Mechanismen, **keine konkrete Gleichung und keinen Koeffizienten dieses Modells**.

1. Iredale JP et al. *Mechanisms of spontaneous resolution of rat liver fibrosis. Hepatic stellate cell apoptosis and reduced hepatic expression of metalloproteinase inhibitors.* J Clin Invest. 1998;102:538–549. [DOI:10.1172/JCI1018](https://doi.org/10.1172/JCI1018), [PMID:9691091](https://pubmed.ncbi.nlm.nih.gov/9691091/). Primäre Tierexperimentstudie: Fibroserückbildung und Abnahme aktivierter Sternzellen nach Ende des Schädigungsreizes. Keine quantitative Übertragbarkeit auf menschliche Zirrhose.
2. Kisseleva T et al. *Myofibroblasts revert to an inactive phenotype during regression of liver fibrosis.* PNAS. 2012;109:9448–9453. [DOI:10.1073/pnas.1201840109](https://doi.org/10.1073/pnas.1201840109), [PMID:22566629](https://pubmed.ncbi.nlm.nih.gov/22566629/). Primäre Mausstudie: Inaktivierung von Myofibroblasten. Der Zustand `s` unterscheidet Inaktivierung und Apoptose nicht.
3. Duffield JS et al. *Selective depletion of macrophages reveals distinct, opposing roles during liver injury and repair.* J Clin Invest. 2005;115:56–65. [DOI:10.1172/JCI22675](https://doi.org/10.1172/JCI22675), [PMID:15630444](https://pubmed.ncbi.nlm.nih.gov/15630444/). Primäre Tierexperimentstudie: phasenabhängige Funktionen von Makrophagen. Ein einziger Entzündungszustand kann diese gegensätzlichen Funktionen nicht auflösen; dies ist ein zentraler Strukturfehler des Prototyps.
4. Michalopoulos GK. *Liver regeneration.* J Cell Physiol. 2007;213:286–300. [DOI:10.1002/jcp.21172](https://doi.org/10.1002/jcp.21172), [PMID:17559071](https://pubmed.ncbi.nlm.nih.gov/17559071/). Übersichtsarbeit, keine primäre Kalibrierungsstudie. Biologischer Hintergrund zur Regeneration; logistischer Ansatz nur Modellannahme.
5. Hernández-Guerra M, García-Pagán JC, Bosch J. *Increased hepatic resistance: a new target in the pharmacologic therapy of portal hypertension.* J Clin Gastroenterol. 2005;39 Suppl 2:S131–137. [PMID:15758648](https://pubmed.ncbi.nlm.nih.gov/15758648/). Übersichtsarbeit über strukturelle und dynamische Widerstandsanteile. Das Modell berechnet weder Blutfluss noch HVPG; sein Widerstandsindex ist kein Druckwert.

## Zustände, Gleichungen und Einheiten

Zustand `x = (h, i, s, f)`, jeweils dimensionslos in [0, 1]:

| Symbol / Swift-Feld | Bedeutung |
|---|---|
| h / hepatocytes | Normierter funktionsfähiger Hepatozytenanteil |
| i / inflammation | Zusammengefasste Entzündungsaktivität |
| s / stellate | Zusammengefasster aktivierter Sternzellanteil |
| f / fibrosis | Normierte fibrotische Matrixlast |

Für t in Tagen gilt:

```text
dh/dt = r*g*h*(1-h)*(1-0.7*f) - k*u*h*(0.25+0.75*i)
di/dt = a*v*u*(1-h)*(1-i) - b*i
ds/dt = c*i*(1-s) - d*s
df/dt = e*(1-A)*s*(1-f) - q*(1-s)*f
```

| Symbol / Parameter | Default | Einheit | Zulässiger Bereich |
|---|---:|---|---|
| k / injuryRate | 0.012 | Tag⁻¹ | 0…1 |
| r / regenerationRate | 0.035 | Tag⁻¹ | 0…1 |
| a / inflammationRate | 0.040 | Tag⁻¹ | 0…1 |
| b / resolutionRate | 0.025 | Tag⁻¹ | 0…1 |
| c / activationRate | 0.025 | Tag⁻¹ | 0…1 |
| d / deactivationRate | 0.012 | Tag⁻¹ | 0…1 |
| e / depositionRate | 0.008 | Tag⁻¹ | 0…1 |
| q / regressionRate | 0.003 | Tag⁻¹ | 0…1 |

Die Konstanten 0.7, 0.25 und 0.75 sind ebenfalls dimensionslose freie Annahmen. Die Startwerte `(0.78, 0.38, 0.32, 0.35)` sind synthetisch. Es existiert keine Patientenzuordnung.

Vor `startDay` gelten `u=v=g=1, A=0`. Ab diesem Zeitpunkt sind `u=injuryMultiplier`, `v=inflammationMultiplier`, `g=regenerationMultiplier` (jeweils 0…4) und `A=antifibroticEffect` (0…1). Die Größen sind **keine Dosierungen oder geschätzten Wirksamkeiten**. `startDay` darf nach dem Simulationsende liegen. Die antifibrotische Intervention reduziert nur die Ablagerung; sie erhöht keine Regression. Der Term `h*(1-h)` verhindert Regeneration bei h=0; alternative Vorläuferzellmechanismen fehlen.

Das kontinuierliche Vektorfeld zeigt an allen Rändern des Einheitswürfels nach innen oder tangential. Hieraus folgt Bereichsinvarianz für das ODE-Modell; das ersetzt keine Prüfung des diskreten Integrators.

## Abgeleitete Ausgaben

```text
reserve = h*(1-0.6*f)                    dimensionslos
portalResistance = 1 + 4*f + 1.5*s      relativer Index, NICHT mmHg
ALT = 20 + 300*i*h                      synthetische U/L
Bilirubin = 0.6 + 4*(1-reserve)^2       synthetische mg/dL
Albumin = 4.5 - 2*(1-reserve)           synthetische g/dL
INR = 1 + 1.5*(1-reserve)^2             synthetischer dimensionsloser Wert
```

Alle Abbildungen und Konstanten sind erfunden und nur für Softwaretests und Lehre vorgesehen. Kein validiertes Messmodell, keine Referenzbereiche, keine Vorhersage von Laborwerten. AST, GGT, AP, Thrombozyten, Kreatinin, Natrium und Elastographie erhalten Datenfelder im Datenmodell, aber keine vorgetäuschten ODE-Vorhersagen. Child-Pugh, MELD, Aszites, Enzephalopathie, Blutung, Infektion, Nierenfunktion und Mortalität sind nicht Teil dieses Kerns. Eine Reserve-Schwelle darf keine Dekompensation diagnostizieren.

## Numerik und Reproduzierbarkeit

Klassisches explizites RK4 in Double-Präzision. `stepDays` ist eine maximale Integrationsschrittweite. Zusätzlich begrenzt `0.1 / max(1, k*u+r*g, a*v*u+b, c+d, e+q)` den Schritt konservativ. An jedem Ausgabezeitpunkt, am Interventionsbeginn und am Simulationsende wird der Schritt exakt geteilt. Ein Schritt bis zum Interventionsbeginn verwendet vollständig die vorherige Intervention; der folgende Schritt verwendet die neue. Kein Mittelwert über eine unstetige Intervention.

Zustände werden auf Endlichkeit und [0,1] geprüft. Nur Rundungsabweichungen bis 1e−10 werden auf die Randwerte gesetzt; größere Ausbrüche lösen einen Fehler aus. Keine stille Projektion instabiler Ergebnisse. Zulässig sind Dauer 0…3650 Tage, Schritt (0,1] Tage und positives Ausgabeintervall. Maximal 200.000 geschätzte Integrations-/Ausgabeschritte pro Lauf und 20.000 Ausgaben begrenzen Ressourcen; extreme gültige Raten können daher kleinere Dauer verlangen. Null-Dauer ergibt genau die Ausgangsprobe.

Die deterministische ODE verwendet keine Zufallszahl. `seed` wird zur Provenienz gespeichert. Ensembles nutzen explizit SplitMix64 mit 53-Bit-Konvertierung auf [0,1); gleiche Eingaben und Seed ergeben gleiche Zustandsproben. UUID und Erstellungszeit unterscheiden sich absichtlich. Bitidentität zwischen unterschiedlichen Swift-/Hardwareversionen wird nicht behauptet.

## Forschungsalgorithmen und Unsicherheit

- **Lokale Sensitivität:** zentrale Differenz der finalen Matrixlast nach einer relativen Parameteränderung (Default ±5 %; minimale absolute Änderung 1e−6/Tag); an Parametergrenzen einseitig. Ergebnis `d(f_final)/d(parameter)` und dimensionslose Elastizität `derivative * parameter / f_final`; bei `f_final=0` ist die Elastizität undefiniert und wird als `nil` ausgegeben. Kein kausaler Therapieeffekt.
- **Sweep:** explizite Werte eines einzelnen Parameters, jeweils gleiche Ausgangslage. Für kombinierte Interventionen können vollständige Szenariokonfigurationen separat verglichen werden.
- **Ensemble:** unabhängige uniforme Multiplikatoren aller acht Raten in `[1-spread, 1+spread]`, Default ±20 %, für eine festgelegte Mitgliederzahl. Parameter oberhalb 1/Tag werden nicht still beschnitten: unzulässige Verteilungen werden abgewiesen. An jedem Ausgabezeitpunkt lineare empirische Quantile 5 %, 50 %, 95 % der Matrixlast. **Parameterstreuungsband, kein Konfidenzintervall, kein klinisches Prognoseintervall.** Es fehlen strukturbedingte Unsicherheit, Parameterkorrelationen, Beobachtungsrauschen und externe Populationsverteilungen.
- **Synthetische Kalibrierung:** eindimensionale Gittersuche mit quadratischem Fehler über f-Beobachtungen an bestehenden Ausgabezeiten. Ein Abstand von maximal acht Double-ULPs akzeptiert Darstellungsrundung (z. B. 0.3 gegenüber 3×0.1), aber keine zeitliche Interpolation. Mehrere Beobachtungen, die demselben Rasterpunkt entsprechen, werden abgewiesen. Nur explizit als synthetisch deklarierte Beobachtungen; keine echte Patientenkalibrierung, kein Nachweis globaler Identifizierbarkeit. Fehlende oder doppelte Zeitpunkte sowie ungültige Werte werden abgewiesen. Ein wiedergefundenes synthetisches Gitterminimum validiert nur Algorithmus und Implementierung.

Analysen akzeptieren höchstens 256 Konfigurationen und zusammen höchstens 2.000.000 geschätzte Integrations-/Ausgabeschritte. Ensemble benötigt mindestens zwei Mitglieder. Diese Grenzen schützen Ressourcen und stellen keine statistische Mindeststichprobe dar.

## Validierungsstatus und nächste wissenschaftliche Gates

Softwaretests prüfen: gesunde Gleichgewichtslösung bei fehlender Schädigung; analytischer exponentieller Entzündungsabbau; keine Fibroseneubildung ohne Ablagerung; definierter Zeitpunkt einer Intervention; Bereichsgrenzen; Eingabefehler; Schrittverfeinerung; feste numerische Regression; deterministischer RNG/Ensemble; synthetische Parameterwiederfindung. Dies ist numerische und technische Verifikation, **keine klinische Validierung**.

Vor Aussagen über menschliche Progression: Forschungsfrage und Zielpopulation festlegen, Einheiten/Beobachtungsmodell identifizieren, Ethik und Datengrundlage klären, strukturelle/praktische Identifizierbarkeit prüfen, informative Parameterverteilungen begründen, longitudinale Daten getrennt für Training und externe Validierung verwenden, Zeit-/Patientenleckage verhindern, Sensitivität und Modellabweichung quantifizieren, Kalibrierungs- und Abdeckungsmetriken präregistrieren, unabhängige hepatologische und biometrische Prüfung durchführen. Diese Arbeiten sind offen.
