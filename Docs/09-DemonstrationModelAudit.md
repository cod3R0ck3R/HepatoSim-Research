# Audit des Demonstrationsmodells 0.1.0

Datum: 22.10.2026. Gegenstand: tatsächlich implementierter Stand von `Model.swift`, `LiverSimulator.swift`, `ResearchAnalysis.swift`, sämtlichen vorhandenen Tests sowie [Modellbeschreibung](02-ScientificModel.md) und [Prüfbericht](07-VerificationReport.md). Der bestehende Kern wurde für dieses Audit **nicht geändert**. Das neue Forschungsziel ist experimentelle Kollagendynamik während Schädigung und nach Reizentzug; klinische Prognosen sind kein Audit- oder Kalibrierungsziel.

**Ergebnis:** Der Kern ist ein technisch überprüftes Demonstrationsmodell. Kein biologischer Parameter und keine Beobachtungsfunktion wurde an experimentellen oder klinischen Daten geschätzt. Literatur begründet einzelne Mechanismen, nicht die konkrete Gleichungsstruktur oder deren Zahlenwerte. Die biologisch plausiblen Parameterintervalle sind **unbekannt**. Zulässige Softwarewerte dürfen nicht als physiologische Referenzbereiche bezeichnet werden.

## 1. Prüfstand und Nachweisgrenze

Die Quellstände und Prüfergebnisse sind zusätzlich in [audit-manifest.json](../Research/Audit/audit-manifest.json) festgehalten. `LiverSimulator.modelVersion` ist `0.1.0`; der Evidenzkatalog verwendet die längere Zuordnung `hepatosim.liver-ode@0.1.0`. Diese Zuordnung ist keine Registrierung eines austauschbaren Modell-Plugins.

Ein eigener vollständiger Lauf mit `swift test --scratch-path /tmp/hepatosim-audit-20261022-core` endete erfolgreich: **52 vorhandene Tests, keine Fehler** — 19 ODE-/Analyse-, neun Evidenz-, 17 Storage- und sieben UI-Zustands-/Eingabetests. Die Tests wurden gelesen, nicht nur gezählt. Der temporäre Build liegt außerhalb des Documents-Dateianbieters, um den bereits bekannten Codesign-Metadatenfehler zu vermeiden.

Das bestätigt den gelesenen Softwarestand. Native Fensterbedienung, Codesigning des ausgelieferten ZIPs, iOS-Geräteverhalten und frühere manuelle Prüfungen aus Dokument 07 wurden in diesem Audit nicht erneut ausgeführt. Ihre dortigen Protokollangaben werden nicht als neue Auditmessungen ausgegeben.

## 2. Klassifikation

| Kennzeichen | Bedeutung |
|---|---|
| M | Qualitativer Mechanismus durch die benannte Quelle gestützt; Übertragung auf den konkreten Kontext begrenzt. |
| D | Aus identifizierten Daten geschätzter Modellparameter oder identifiziertes Beobachtungsmodell. **Für diesen ODE-Kern keine Einträge.** |
| A | Experimentelle mathematische Annahme, beispielsweise logistischer Term, Sättigung oder lineare Kopplung. |
| F | Frei gewählter Demonstrationswert, numerischer Schwellenwert oder Ressourcenlimit. |

Ein Ausdruck kann M+A enthalten: Der Mechanismus ist belegt, die mathematische Abbildung bleibt eine Annahme. Ein numerischer Default erhält dadurch keinen Datenbezug.

## 3. Vollständiges Zustands- und Parameterinventar

### Zustände und Anfangswerte

Quelle im Code: `Sources/HepatoCore/Model.swift:17` und `:30`.

| Variable | Interpretation im Code | Default | Einheit und erlaubte Softwaregrenze | Einordnung / nicht identifiziert |
|---|---|---:|---|---|
| `h`, `hepatocytes` | Funktionsfähiger Hepatozytenindex | 0,78 | dimensionslos, endlich, [0,1] | M+A; Default F. Kein gemessener Zellanteil, keine definierte Referenzzellzahl. |
| `i`, `inflammation` | Zusammengefasste Entzündungsaktivität | 0,38 | dimensionslos, endlich, [0,1] | M+A; Default F. Kein Cytokin-, CRP- oder Histologiescore. |
| `s`, `stellate` | Aktivierter Sternzellindex | 0,32 | dimensionslos, endlich, [0,1] | M+A; Default F. Keine Zuordnung zu α-SMA-Fläche oder Zellzählung. |
| `f`, `fibrosis` | Normierte Matrixlast | 0,35 | dimensionslos, endlich, [0,1] | M+A; Default F. Keine Zuordnung zu Hydroxyprolin, Kollagenfläche, Fibrosestadium oder kPa. |

Die Normalisierung selbst ist A. „1“ ist eine mathematische Sättigungsgrenze und kein aus einem Experiment bestimmter maximaler Kollagengehalt. Alle vier Anfangswerte sind synthetisch; Unsicherheit oder Messfehler werden nicht mitgespeichert.

### Acht veränderliche Raten

Quelle: `Model.swift:46`. Alle acht Raten sind endlich, numerisch auf **0…1 pro Modelltag** beschränkt. Diese gemeinsame Grenze ist ein Softwarevertrag F, kein wissenschaftlich bestimmtes Intervall. Jede Rate und jeder Default ist **nicht daten-geschätzt**; biologische Plausibilität, Tierartabhängigkeit und Übertragbarkeit der Zeitkonstante sind unbekannt.

| Symbol / Feld | Default [Modelltag⁻¹] | Aufgabe | Mechanistische Stütze / mathematische Grenze |
|---|---:|---|---|
| `k`, `injuryRate` | 0,012 | Verlust von h unter Reiz und Entzündung | Schädigung M; konkrete Verlustkinetik A, Wert F. |
| `r`, `regenerationRate` | 0,035 | Logistischer Wiederaufbau von h | Regeneration M (R4); logistischer Ansatz A, Wert F. |
| `a`, `inflammationRate` | 0,040 | Aufbau von i aus Reiz und Hepatozytendefizit | Entzündungsbeteiligung M (R3); Zusammenfassung und Kopplung A, Wert F. |
| `b`, `resolutionRate` | 0,025 | Linearer Abbau von i | Auflösung/Umstellung von Entzündung M (R3); eine Abbaukonstante A, Wert F. |
| `c`, `activationRate` | 0,025 | Aktivierung von s durch i | Sternzellaktivierung M (R1/R2); direkte lineare Anregung A, Wert F. |
| `d`, `deactivationRate` | 0,012 | Linearer Verlust von s | Inaktivierung beziehungsweise Apoptose M (R1/R2); nicht getrennte Mechanismen A, Wert F. |
| `e`, `depositionRate` | 0,008 | Matrixaufbau durch s | Matrixproduktion durch aktivierte Zellen M (R1/R2); Sättigung A, Wert F. |
| `q`, `regressionRate` | 0,003 | Matrixverlust, moduliert durch 1−s | Matrixremodellierung M (R1); konkrete Gegenspielerfunktion A, Wert F. |

### Szenario und zeitliche Vorgaben

Quelle: `Model.swift:87` und `:109`.

| Feld | Default | Numerisch erlaubt | Bedeutung und Einordnung |
|---|---:|---|---|
| `injuryMultiplier`, u | 1 | endlich, [0,4] | Dimensionsloser Reizfaktor A/F; keine Alkoholmenge oder Toxindosis. |
| `inflammationMultiplier`, v | 1 | endlich, [0,4] | Dimensionsloser Faktor nur des Entzündungsaufbaus A/F. |
| `antifibroticEffect`, A | 0 | endlich, [0,1] | Dimensionsloser Anteil zur Reduktion der Ablagerung A/F; kein gemessener Therapieeffekt. |
| `regenerationMultiplier`, g | 1 | endlich, [0,4] | Dimensionsloser Faktor des h-Aufbaus A/F. |
| `startDay` | 0 | endlich, [0,3650] | Modelltag des abrupten Umschaltens A/F; darf nach Laufende liegen. |
| `durationDays` | 365 | endlich, [0,3650] | Modellhorizont F; keine validierte natürliche Verlaufsdauer. |
| `stepDays` | 0,25 | endlich, (0,1] | Gewünschte maximale numerische Schrittweite F; tatsächlicher Schritt meist kleiner. |
| `sampleEveryDays` | 5 | endlich und >0, zusätzlich Ausgabelimit | Ausgabeintervall F; keine Messplanung aus Experimenten. |
| `seed` | 42 | UInt64, 0…2⁶⁴−1 | Reproduzierbarkeit des Parameter-Ensembles F; keine Zufälligkeit der Einzel-ODE. |
| `name` | „Kontrolle“ | nicht leer nach Trimmen; ≤200 UTF-8-Bytes | Beschreibende Metadaten, keine biologische Variable. |

Vor Beginn gilt das Kontrollszenario u=v=g=1, A=0; danach die konfigurierte Konstante. Es gibt weder Ausschleichen noch wiederholte Expositionen, Rückfallereignisse oder zeitveränderliche Dosierungsdaten. Die gesamte stückweise konstante Intervention ist A; alle Bereichsgrenzen sind F.

## 4. Audit jeder Zustandsdifferentialgleichung

Die vier kanonischen Gleichungen stehen in [Dokument 02, Zustände und Gleichungen](02-ScientificModel.md#zustände-gleichungen-und-einheiten); tatsächliche Implementierung: `LiverSimulator.swift:31`. Rechtsseitige Einheiten sind jeweils normierter Zustand pro Modelltag.

| Gleichung | Jeder implementierte Term und seine Einordnung | Konsequenz für Interpretation |
|---|---|---|
| dh/dt | Aufbau `r*g*h*(1−h)*(1−0.7*f)` und Verlust `k*u*h*(0.25+0.75*i)`. M für Regeneration/Schädigung; sämtliche Produktkopplungen und Logistik A. Die Zahlen 0,7, 0,25, 0,75 sind dimensionslose F. | h=0 ist absorbierend: keine Erholung ohne verbleibendes h. Fibrose reduziert nur den Aufbau; selbst f=1 lässt 30 % dieses Faktors übrig. Der Verlust enthält eine frei gewählte entzündungsunabhängige Komponente. |
| di/dt | Aufbau `a*v*u*(1−h)*(1−i)` und Verlust `b*i`. Mechanistische Entzündungsbeteiligung M; Defizitkopplung, Sättigung und linearer Abbau A. | Quelle hängt vom vorhandenen h-Defizit ab, nicht vom tatsächlichen Verlustfluss k. Auch bei k=0 kann i aufgebaut werden, wenn u>0 und h<1. Bei u=0 fällt i unabhängig von v exponentiell ab. |
| ds/dt | Aktivierung `c*i*(1−s)` und Verlust `d*s`. Zellaktivierung/-inaktivierung M; ein homogener Pool, direkte i-Kopplung und lineare Entfernung A. | Kein separates inaktiviertes Zellkompartiment, keine Zellzahlbilanz, kein Gedächtnis reaktivierbarer HSC. Apoptose und Inaktivierung werden nicht unterschieden. |
| df/dt | Ablagerung `e*(1−A)*s*(1−f)` und Rückbildung `q*(1−s)*f`. Produktion/Remodellierung M; beide Sättigungen, ihre gegenseitige Kopplung und ein homogener Matrixpool A. | Ein antifibrotischer Faktor verändert nur die Ablagerung. Bei s=1 ist Rückbildung null; bei f=1 stoppt neue Ablagerung. Kollagenalter, Vernetzung, Abbauprodukte, MMP/TIMP und räumliche Septen fehlen. |

Die Konstanten 0 und 1 in den Sättigungsfaktoren definieren die angenommenen normierten Kapazitäten. Sie sind keine zusätzlich geschätzten biologischen Konstanten. Der Code verwendet für den Sternzellzustand lokal den Namen `a`; im wissenschaftlichen Dokument steht `s`, während `a` dort die Entzündungsaufbaurate bezeichnet. Die Implementierung ist konsistent, die unterschiedliche Kurznotation darf bei Übertragungen nicht verwechselt werden.

### Reizentzug ist nicht sofortige Matrixregression

Die konkrete Anfangsableitung bei synthetischem Zustand, Default-Raten und Reizentzug u=0, A=0 beträgt für die Matrix **+0,00095 pro Modelltag**; der Sternzellindex wächst zunächst ebenfalls. Reizentzug entfernt die Schädigung und die Entzündungsquelle, aber nicht bereits aktivierte s. Ein initialer Nachlauf der Ablagerung ist daher im Modell möglich. Dieser rechnerische Befund ist weder experimentell bestätigt noch automatisch ein Modellfehler.

Der vorhandene Interventionstest vergleicht den Endzustand des Reizentzugs nach 365 Modelltagen mit dem Kontrolllauf. Er prüft **keine monotone Matrixabnahme**, keinen Zeitpunkt der maximalen Ablagerung und keine Übereinstimmung mit einer gemessenen Regressionszeitreihe.

## 5. Audit sämtlicher Beobachtungsabbildungen

Quelle: `Model.swift:181`. Keine der sechs algebraischen Abbildungen ist D. Sämtliche Formeln sind A, sämtliche Skalierungen und Exponenten F. Unsicherheit wird dafür nicht geschätzt; keine Referenzbereiche oder Messfehlerverteilungen sind identifiziert.

| Ausgabe | Vollständige Koeffizienten/Struktur | Aus Zustandsgrenzen mathematisch folgende Spanne | Einheit / Evidenzgrenze |
|---|---|---|---|
| `reserve` | h multipliziert mit 1−0,6f | [0,1] | dimensionslos; weder gemessene Syntheseleistung noch validierte Leberreserve. |
| `portalResistance` | Offset 1; linear 4f und 1,5s | [1;6,5] | relativer dimensionsloser Index; **kein mmHg**, keine physikalisch kalibrierte Widerstandseinheit. R5 stützt nur strukturelle/dynamische Widerstandsanteile. |
| `alt` | Offset 20; Skalierung 300 des Produkts i·h | [20,320] | synthetische U/L; Offset und Skalierung tragen U/L. Keine Enzymfreisetzungs-/Clearancekinetik. |
| `bilirubin` | Offset 0,6; Faktor 4 auf (1−reserve)² | [0,6;4,6] | synthetische mg/dL; Offset/Faktor tragen mg/dL. Exponent 2 dimensionslos, frei gewählt. |
| `albumin` | Offset 4,5; Abzug 2·(1−reserve) | [2,5;4,5] | synthetische g/dL; Offset/Faktor tragen g/dL. Keine Synthese-, Verteilungs- oder Halbwertszeitdynamik. |
| `inr` | Offset 1; Faktor 1,5 auf (1−reserve)² | [1;2,5] | dimensionslos; keine Gerinnungsfaktor-Kinetik oder Antikoagulationsabbildung. |

Die Spannen entstehen allein aus den Formeln, nicht aus Patientendaten. Sie schließen zahlreiche reale Messwerte per Konstruktion aus. Sie dürfen deshalb nicht als biologische Gültigkeitsbereiche oder zur Bewertung experimenteller Kollagenmessungen verwendet werden. AST, GGT, AP, Thrombozyten, Kreatinin, Natrium und Elastographie werden in diesem Kern nicht dynamisch berechnet.

## 6. Numerik, Analysen und modellierte Unsicherheit

### Integrator und Grenzen

`LiverSimulator.swift:50` implementiert klassisches explizites RK4 mit Gewichten 1/6, 1/3, 1/3, 1/6. Das sind numerische Verfahrenskonstanten, keine Biologie. Es gibt keine adaptive Fehlerkontrolle oder geschätzte lokale Integrationstoleranz.

`Model.swift:159` begrenzt die maximale Schrittweite zusätzlich konservativ. Für die Schranke verwendet der Code **max(1,u), max(1,v), max(1,g)**, somit auch die Kontrollphase vor einer Reduktion. Die Darstellung in Dokument 02 nennt zwar die Raten-Schranke, diese drei Maxima aber nicht ausdrücklich. Bei Default-Raten beträgt der tatsächliche maximale Schritt **0,1 Modelltag**, obwohl `stepDays` 0,25 lautet. Ausgabe-, Start- und Endpunkte können ihn weiter verkürzen.

RK4 schaltet innerhalb eines Teilstücks nicht zwischen Interventionen um: Die alte Konfiguration gilt bis zur Grenze, die neue ab dem nächsten Schritt. Nur abgeschlossene Integrationszustände werden auf Endlichkeit und Bereich geprüft. Grenzverletzungen bis 1e−10 werden abgeschnitten; größere Verletzungen lösen einen Fehler aus. Die Schranke 1e−10 ist numerisch frei gewählt. Zwischenstufen erhalten keine eigene Bereichsprüfung. Die Schrittregel ist konservativ, aber kein bewiesener universeller RK4-Stabilitätssatz.

Das kontinuierliche Vektorfeld ist für erlaubte Parameter auf dem Einheitswürfel nach innen gerichtet beziehungsweise tangential: h′=0 bei h=0, h′≤0 bei h=1; i′≥0 bei i=0 und i′=−b bei i=1; s′≥0 bei s=0 und s′=−d bei s=1; f′≥0 bei f=0 und f′=−q(1−s) bei f=1. Diese Bereichsinvarianz beweist keine biologische Plausibilität und ersetzt keine diskrete Fehlerkontrolle.

Ressourcenlimits F: höchstens 200.000 geschätzte Integrations-/Ausgabeschritte und 20.000 Ausgaben pro Lauf; maximal 256 Konfigurationen und 2.000.000 geschätzte Schritte pro Analyse. Sie beziehen sich auf geschätzte Arbeit, nicht auf einen gemessenen Zeit- oder Speicherbenchmark. Null-Dauer ergibt genau eine Ausgangsprobe. UUID und Erstellungszeit sind neue Metadaten; deterministisch reproduziert werden Zustandsproben.

### Vollständiges Analyseinventar

| Funktion / Code | Tatsächliche Berechnung | Unsicherheit und Grenzen |
|---|---|---|
| `sensitivity`, `ResearchAnalysis.swift:50` | Differenzquotient der finalen f-Werte an durch [0,1] begrenzten Parameterstützstellen; relative Änderung Default 5 %, minimale absolute Änderung 1e−6/Modelltag. Elastizität = Quotient × Parameter/finales f, bei f=0 `nil`. | Quotient hat Einheit Modelltag; Elastizität dimensionslos. Nur bei symmetrischen Stützstellen zentral, am Rand einseitig, randnah ggf. asymmetrische Sekante. Keine globale Sensitivität oder Parameterschätzunsicherheit. |
| `sweep`, `:66` | Einzelparameterwerte explizit durchlaufen, finales f und Reserve ausgeben. | Kein statistischer Unsicherheitsanspruch; alle übrigen Werte fest. |
| `ensemble`, `:84` | Default 64 Läufe; jede Rate unabhängig mit uniformem Faktor in [0,8;1,2] multipliziert. Allgemeine relative Streuung [0,1], bei Überschreitung 1/Tag Abbruch. Lineare empirische 5/50/95-%-Quantile von f pro Ausgabezeit. | Verteilung F, nicht aus Messdaten. Anfangswerte, Formeln, Messfehler und Parametereffekte außerhalb dieses Schemas bleiben fest. Nullraten bleiben null. Keine Parameterkorrelation, keine klinische Prognoseverteilung und kein simultanes Trajektorienband. |
| `SeededGenerator`, `:36` | SplitMix64 mit festen UInt64-Konstanten; 53 höchstwertige Bits liefern uniforme Zahlen in [0,1). | Software-Reproduzierbarkeit; kein biologischer stochastischer Prozess. |
| `calibrateSynthetic`, `:120` | Eindimensionale Kandidatensuche, mittlerer ungewichteter quadratischer Fehler zwischen f-Ausgaben und `SyntheticObservation.fibrosis`. Zeitzuordnung höchstens acht Double-ULPs, ohne Interpolation; doppelte Rasterzuordnung abgelehnt. Bei gleichem Minimum gewinnt der erste Kandidat. | Verlust dimensionslos². Nur synthetische Wiederfindung; keine Likelihood, Messfehlergewichte, Parameterintervalle, Identifizierbarkeit oder externe Prüfung. Eine beliebige Zahlenliste wird durch den Typnamen nicht nachweislich synthetisch. |

Die deskriptiven Wilson-Intervalle des getrennten Evidenzmoduls sind keine Unsicherheit dieser ODE und fließen nicht in die Parameterschätzung ein. Klinische ALD-Ereignisanteile können die hier nicht existierenden klinischen Endpunkte nicht validieren.

## 7. Quellenprüfung und zulässige mechanistische Stütze

DOI/PMID und grundlegender Studieninhalt wurden am Auditdatum online anhand PubMed beziehungsweise der Originalverlagsseite überprüft. Keine der Quellen wurde als numerischer Parameterschätzer verwendet.

| ID | Verifizierte Quelle | Quellentyp und Verwendung im Audit |
|---|---|---|
| R1 | Iredale et al. J Clin Invest. 1998;102:538–549. [DOI 10.1172/JCI1018](https://doi.org/10.1172/JCI1018), [PMID 9691091](https://pubmed.ncbi.nlm.nih.gov/9691091/) | Primäre Rattenstudie: Matrixremodellierung nach toxischem Reizentzug, Abnahme aktivierter Sternzellen und TIMP-Bezug. Begrenzte qualitative Stütze für s/f-Kopplung; kein Nachweis der verwendeten Raten oder menschlichen Reaktionszeiten. |
| R2 | Kisseleva et al. PNAS. 2012;109:9448–9453. [DOI 10.1073/pnas.1201840109](https://doi.org/10.1073/pnas.1201840109), [PMID 22566629](https://pubmed.ncbi.nlm.nih.gov/22566629/) | Primäre Mausstudie: inaktivierter Myofibroblastenphänotyp während Regression. Stützt einen Mechanismus, den das Ein-Kompartiment-s nur grob zusammenfasst. |
| R3 | Duffield et al. J Clin Invest. 2005;115:56–65. [DOI 10.1172/JCI22675](https://doi.org/10.1172/JCI22675), [PMID 15630444](https://pubmed.ncbi.nlm.nih.gov/15630444/) | Primäre Tierexperimentstudie: unterschiedliche Makrophagenfunktionen während Schädigung und Reparatur. Zeigt gerade die Begrenzung eines einzelnen i-Zustands mit nur profibrotischer Wirkung. |
| R4 | Michalopoulos. J Cell Physiol. 2007;213:286–300. [DOI 10.1002/jcp.21172](https://doi.org/10.1002/jcp.21172), [PMID 17559071](https://pubmed.ncbi.nlm.nih.gov/17559071/) | Übersichtsarbeit zur Leberregeneration, keine Primärschätzung der logistischen Rate r. |
| R5 | Hernández-Guerra et al. J Clin Gastroenterol. 2005;39 Suppl 2:S131–137. [PMID 15758648](https://pubmed.ncbi.nlm.nih.gov/15758648/) | Übersichtsarbeit zu hepatischem Widerstand; keine Kalibrierung des dimensionslosen Portalindex. |

Diese Quellen bilden keine lückenlose mechanistische oder systematische Literaturvalidierung. Insbesondere sind die Laborproxies, die Reserveabbildung, die logistischen Kapazitäten und alle konkreten Interventionsmultiplikatoren durch keine dieser Arbeiten quantitativ validiert.

## 8. Konkrete Befunde zum Prüfbericht und wissenschaftliche Anschlussarbeit

| Befund | Bewertung / erforderliche Präzisierung |
|---|---|
| Keine experimentelle Kalibrierung vorhanden | Kritisch für den neuen Forschungszweck. Das vorhandene Modell bleibt Demonstration; es darf nicht nachträglich als an experimentelle Kollagendaten angepasst bezeichnet werden. |
| Kein Messmodell für experimentelles Kollagen | Vor jedem Fit Hydroxyprolin, Kollagenflächenanteil oder andere Messgröße festlegen, Einheit/Normalisierung und Messfehler dokumentieren. Ein Index ist keine gemessene Konzentration. |
| Referenzgenerator nicht im Repository | `HepatoCoreTests.swift:41` enthält vier Referenzzahlen und einen Python-RK4-Kommentar, aber keinen ausführbaren Referenzgenerator. Dokument 07 bezeichnet einen „unabhängigen Referenzalgorithmus im Kern-Testcode“; diese Formulierung ist zu weit. Es handelt sich um einen Vergleich mit gespeicherten Referenzwerten einer angegebenen feineren RK4-Implementierung. |
| Konvergenznachweis enger als allgemeine Stabilität | `HepatoCoreTests.swift:50` prüft exponentiellen i-Abbau mit allen übrigen Raten null. Der Test belegt nicht die Konvergenz des vollständig gekoppelten Systems über den gesamten Eingaberaum. Der Eckentest behandelt 16 Startzustände bei hohen Raten über drei Modelltage, keine vollständige Bereichsabdeckung. |
| Numerische Schrittregel in Dokument 02 verkürzt | Die konservativen max(1,Multiplikator)-Werte und der tatsächliche Default-Schritt von 0,1 sind dort nicht ausdrücklich erklärt. Dies ist eine Dokumentationspräzisierung, keine Änderung biologischer Raten. |
| Synthetische Kalibrierung kann uninformative Minima liefern | Ein einzelner Beobachtungspunkt bei t=0 oder flache Parameterwirkung kann alle Kandidaten gleich gut machen. Der erste Kandidat gewinnt, ohne Identifizierbarkeitswarnung. Das Resultat ist eine Algorithmusausgabe, kein Schätzbeleg. |
| Keine vollständige austauschbare Modell-/Plugin-API | Der statische `LiverSimulator` und fest kodierte Zustandstypen bilden keinen registrierten Plugin-Laufzeitvertrag. Ein Providerprotokoll für KI existiert separat. Aus dem Versionsstring oder dem Evidenz-`modelIDs`-Feld folgt keine sichere Plugin-Ausführung. |

Für den nächsten experimentellen Meilenstein ist ein **separates, versioniertes Modell** angezeigt: definierte Spezies und Schädigungsmethode, klarer Entzugszeitpunkt, echte Kollagenmessungen mit Einheiten, ein ausdrücklich gewähltes Beobachtungsmodell und möglichst wenige zu schätzende Parameter. Erst Datenverfügbarkeit und Identifizierbarkeit entscheiden, ob ein reines Kollagen-Abbaumodell, zusätzliche Aktivierungsdynamik oder komplexere Struktur nötig ist. Der bestehende Demonstrationslauf bleibt als unveränderter Vergleich verfügbar.

Ein experimenteller Fit benötigt einen dokumentierten Datensatz und eine unabhängige Prüfung, nicht bloß klinische ALD-Kohortenanteile. Zu prüfen sind insbesondere Nachlauf der Ablagerung, Rückkehr zum Kontrollniveau, Unsicherheit der Messungen und Endzeitpunkt-/Tiergruppen-Trennung. Tierexperimentelle Güte darf später nicht als Validierung menschlicher Zirrhose ausgegeben werden.
