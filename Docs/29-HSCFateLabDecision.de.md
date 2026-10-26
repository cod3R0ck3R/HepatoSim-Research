# HSC-Zellschicksal und eine unterscheidbare Laborfrage

26. Oktober 2026 · [English](29-HSCFateLabDecision.md)

**Entscheidung:** Eine mechanistische Prüfung soll klären, ob HSC-Rückbildung einen erneut aktivierbaren Zellbestand erhält. Sinkende Aktivierungsmarker belegen keine Narbenbeseitigung. Der IL-10-Signalweg ist ein Untersuchungskandidat, kein quantitativ simuliertes Medikament. Dieses Paket belegt keine Wirksamkeit gegen menschliche Zirrhose.

## Rechenfrage

Der eingefrorene Versuch HSR-HSC-FATE-001 erweitert das Originalmodell von Bouguéon [1]. Stochastische Kappa-Regeln, 10.000-Zell-Skala und Schädigungsverlauf bleiben erhalten. Erst nach dem nominalen Schädigungsende an Modelltag 60 wird der Inaktivierungsanteil reaktivierter Myofibroblasten von 0,05 auf 0,50 geändert. Der komplementäre Entfernungsanteil sinkt von 0,95 auf 0,50; die gesamte Austrittsrate bleibt gleich. Dieser gewählte Sensitivitätskontrast ist kein gemessener Arzneimitteleffekt. Kollagen, aktive Zellen und verbleibende inaktive Zellen sind getrennt auszuwerten.

Die drei archivierten Standard-Seeds sind bereits eingesehene Kontrollen. Neue Kontrastläufe mit Seeds 101–103 sowie Wiederholungs- und Rasterkontrollen sind vorab festgelegt. Die Kontrolle mit zusätzlichen Messgrößen wird mit dem Originalarchiv verglichen. Biologischer Kontext ist murine CCl4-Fibrose, dargestellt durch TGFβ1-Pulse. Dies ist kein menschliches Modell alkoholassoziierter Lebererkrankung. Kollagen wird in Modelleinheiten, nicht klinischen Fibroseprozenten ausgegeben. Der historische Unterschied zwischen eingesetzter Laufzeitversion und Publikationsangabe bleibt ungeklärt.

Eine getrennte exakte Rechnung verfolgt einen reifen, ungebundenen, reaktivierten Myofibroblasten über aktiv→früh inaktiv→inaktiv beziehungsweise Entfernung. Vorausgesetzt werden fehlender Zellnachschub, fehlende Proliferation und keine erneute TGFβ1-Bindung. 135 gewählte Szenarien variieren Zellschicksalsanteil, Austrittshalbwert und Persistenz inaktiver Zellen getrennt. Diese Rechnung berechnet kein Kollagen und ersetzt Kappa nicht. 100.000 stochastische Wartezeitverläufe und eine unabhängige Quadratur prüfen die Rechnung; es handelt sich nicht um biologische Wiederholungen.

## Ausgeführte Ergebnisse und Verifikation

Alle sechs vorab festgelegten KaSim-Läufe wurden abgeschlossen: 1.724,847 Sekunden lokale Simulationslaufzeit (28,75 Minuten; Obergrenze 3.600 Sekunden). Es gab keine Parameteroptimierung. Diese Iteration verwendete lokal ausgeführte Rechenprogramme; eine neue Goose-/Ollama-Inferenz wird nicht behauptet.

Deskriptive Ergebnisse an Tag 90: COL1 bleibt in Original-Modelleinheiten, iHSC ist eine Modellzellzahl. Die drei stochastischen Seeds sind keine Tiere oder menschlichen Spender.

| Seed | COL1 Kontrolle | COL1 fate50 | Differenz | iHSC Kontrolle | iHSC fate50 | Differenz |
|---|---:|---:|---:|---:|---:|---:|
| 101 | 3.251017 | 3.282935 | +0.031917 | 3201 | 17839 | +14638 |
| 102 | 3.161025 | 3.134947 | -0.026078 | 3167 | 16966 | +13799 |
| 103 | 3.169879 | 3.051145 | -0.118734 | 3109 | 16723 | +13614 |

Der verbleibende inaktive Zellbestand ist in allen drei Vergleichen größer, um 13.614–14.638 Modellzellen. Die COL1-Differenzen haben unterschiedliche Vorzeichen (−0,118734 bis +0,031917); diese Läufe belegen keinen verlässlich niedrigeren Kollagenendpunkt. Aus drei Seeds werden weder Konfidenzintervalle noch statistische Äquivalenz abgeleitet. Ein erneuter Schädigungsreiz wurde in diesem Paket nicht simuliert. Der größere reaktivierbare Bestand begründet diesen Versuch, beweist aber keine erhöhte Rückfallrate.

Die Kontrolle mit zusätzlichen Messgrößen stimmt an 197 gemeinsamen Zeitpunkten exakt mit dem Archiv überein. Die numerische Seed-Wiederholung ist exakt. Ausgaberaster von 0,5 und 0,25 Tagen stimmen an 198 gemeinsamen Zeitpunkten überein; dies prüft die Beobachtungsabtastung, keine ODE-Schrittweitenapproximation. Jeder der drei Verläufe vor der Intervention stimmt an 136 gemeinsamen Zeitpunkten mit seiner Archivkontrolle überein. Sieben Tests bestehen. Eine separate Prozessausführung reproduziert Analyse, bedingtes 135-Zeilen-Raster und Identifizierbarkeitsergebnis aus dem bereinigten Export bytegleich. Die Wiederaufnahme verwendete fate50-101 ohne neue Simulation wieder. Siehe [Verifikation](../Research/HSCFate/verification.json), [sämtliche Rechenergebnisse](../Research/HSCFate/results/analysis.json) und [Wiederaufnahmebeleg](../Research/HSCFate/resume-verification.json).

Eine Vorprüfung scheiterte vor KaSim-Start an einer nicht verfügbaren Cloud-Platzhalterdatei. Danach wurde die bereits lokal vorhandene ausführbare Datei mit identischem erforderlichem Hash verwendet. Die erste abgeschlossene Kontrolle wurde zunächst als ungültig eingestuft, weil KaSim konstante Messgrößen mit ihrem Wert statt Alias beschriftete. Nur der Parser wurde korrigiert. Fehlerhaft eingestuftes Manifest und ausdrückliche Nachprüfung bleiben erhalten; Modelleinstellungen und Akzeptanzgrenzen blieben gleich. Tatsächlich verwendet wurde KaSim 4.1.3.1; die Publikation nennt 4.2.12. Der ungeklärte Provenienzunterschied begrenzt die Reproduktionsaussage.

| Evidenzebene | Status dieses Pakets |
|---|---|
| Software-/Numerikprüfung | Festgelegte Tests sowie Verlaufs-, Wiederholungs-, Raster- und Exportprüfungen bestanden |
| Publikationsreproduktion | Originalimplementierung erweitert; Archivübereinstimmung gezeigt; keine erneute vollständige Reproduktion aller Abbildungen |
| Parameterkalibrierung | Nicht durchgeführt; fate50 ist gewählt, nicht angepasst |
| Unabhängige biologische Vorhersage | Nicht geprüft; passende gemeinsame Zellschicksals-/Matrixdaten fehlen in diesem Paket |
| Übertragbarkeit auf Menschen | Nicht belegt; Modell-, Zellstudien- und Erkrankungskontexte unterscheiden sich |
| Klinische Validierung | Nicht durchgeführt; keine Wirkstoffwirksamkeit, Dosierung oder Therapieempfehlung |

Parameterunsicherheit wurde nicht geschätzt. Das bedingte Raster untersucht gewählte Annahmen, keine gemessene Wahrscheinlichkeitsverteilung; ein empirisches Messfehlermodell fehlt. Gleiche Seeds sichern nach einer Intervention keine identischen Reaktionspfade. Rückkopplung, Zellverlust, Matrixproduktion und Matrixabbau sind gemeinsam zu prüfen, bevor eine reale Intervention diesem Parameter zugeordnet wird.

## Ergebnis zur Identifizierbarkeit

Eine separat vorab festgelegte bedingte Rechnung konstruiert drei Parametersätze mit exakt denselben aktiven und inaktiven Anteilen an Tag 30. Halbwertszeiten inaktiver Zellen von 30, 365 und 730 Tagen entsprechen dabei Zellschicksalsanteilen von 0,843521, 0,511467 und 0,500000. Die vorhergesagten inaktiven Anteile an Tag 90 unterscheiden sich: 0,122612, 0,436231 und 0,461758. Dies sind theoretische Gegenbeispiele, keine Anpassungen an Patienten- oder Tiermessungen und kein Parameterposterior. Ein Endpunkt kann diese Kombinationen nicht unterscheiden; frühere/spätere Messungen können es. Siehe [reproduzierbares Ergebnis](../Research/HSCFate/identifiability-result.json).

## Kandidaten und Gegenbefunde

**IL-10-Signalweg / Wiederherstellung eines inaktiven HSC-Phänotyps.** Wang et al. [2], Abb. 7, untersuchen IL-10-Signaländerungen und Vitamin-A-bezogene Messgrößen in menschlichen hiPSC-Leberzellkulturen. Primäre menschliche HSCs zeigten Unterschiede zwischen Spendern. Aktivierungsmarker-Transkripte nahmen ab, apoptotische Marker zugleich zu. Abb. 6 zeigt stärkere Wiederantworten nach Rückbildung; das angegebene n = 4 darf nicht als vier Spender ausgelegt werden. Dies begründet eine gemeinsame Prüfung von Zellschicksal und späterer Antwort. Weder der Modellanteil noch eine Geschwindigkeitskonstante werden dadurch identifiziert. IL-10 wurde nicht als Wirkstoff simuliert; eine Umsetzung der gewählten Parameteränderung 0,05→0,50 durch IL-10 ist nicht belegt. Kontext: HCV-bezogene und metabolisch belastete Zellmodelle, keine klinische Zirrhosetherapie. Status am 26.10.2026: Forschungsmechanismus; kein bestimmtes Arzneimittel, keine Formulierung und keine zugelassene Indikation werden behauptet. Keine neue Zulassungsbewertung oder menschliche Dosierung.

**Indol-3-propionsäure (IPA).** Ilha et al. [3] verbinden eine Beobachtungskohorte mit LX-2-Versuchen. Apoptose und veränderte Aktivierungsmarker treten zusammen auf; Abb. 2/5 berichten drei unabhängige Experimente, nicht drei Spender. Damit lässt sich untersuchen, ob ein vermeintliches Inaktivierungssignal durch Zellverlust erklärbar ist. IPA ist hier kein kalibrierter Behandlungsarm. Die Ergänzung fehlender Supplementdateien vom 5.5.2025 ist berücksichtigt. Eine Rückbildung etablierter menschlicher Zirrhose ist nicht belegt.

**Erhaltene HSC-Funktion ist eine notwendige Gegenprüfung.** Sugimoto et al. [4] zeigen Auswirkungen breiter HSC-Entfernung und HSC-stämmigen RSPO3 auf Homöostase und Regeneration; Abb. 1b umfasst sieben Mäuse je Gruppe. Breite Entfernung entspricht nicht selektiver Entfernung aktivierter Zellen nach Schädigungsende. Trotzdem verbietet dieser Befund die pauschale Schlussfolgerung, mehr HSC-Entfernung sei besser. Regeneration sowie Schädigung und Stoffwechsel gehören neben Matrixmessungen in die Bewertung.

Alle drei Arbeiten erschienen nach dem Modell von 2024 und liefern unabhängige mechanistische Evidenz. Keine ist ein passender unabhängiger quantitativer Test dieser neuen reinen Zellschicksalsänderung. Kisseleva/Troeger 2012 bleiben als Modellvorarbeiten von unabhängiger Validierung ausgeschlossen. Originaltexte wurden beim Verlag beziehungsweise Europe PMC geprüft; Scite unterstützte Suche und Metadatenprüfung. Ein fehlender Scite-Hinweis beweist nicht das Fehlen redaktioneller Hinweise. Das Versionssignal zum Modell mit unveränderter DOI vom 8.8.2024 bleibt ungeklärt.

## Labor-Entscheidungsblatt — vorgeschlagen, nicht ausgeführt

1. **Hypothese:** Mehr Überleben im inaktiven Zustand kann niedrige basale Aktivierungsmarker mit einem größeren später reaktivierbaren Zellbestand verbinden. Aktive Zellen und vorhandene Matrix müssen deshalb nicht schneller verschwinden.
2. **System und Kontrollen:** Geeignetes fachlich geprüftes, nichtinfektiöses HSC-Rückbildungssystem mit Verfolgung zuvor aktivierter Zellen, Schädigungsentzug allein, Vehikelkontrolle und zeitlich passender ursprünglich ruhender Vergleichsgruppe. Unabhängige biologische Präparationen/Spender sind die Wiederholungseinheit; Wells, Bildfelder und Zellen sind darin verschachtelte Beobachtungen. Modelltage nicht auf menschliche Kulturen übertragen; Stichprobengröße nicht aus Simulations-Seeds ableiten.
3. **Primäre Messungen:** Absolute Zahl lebender, verfolgter Zellen; Übergänge zwischen Zuständen im Verlauf; Zelltod und Proliferation; neu produziertes Kollagen und vorhandene Matrix getrennt. Pro Gesamtsystem und pro lebender Zelle berichten. Ein Transkript misst keinen Matrixabbau.
4. **Unterscheidende zweite Phase:** Reaktionslatenz und aktivierte Fraktion nach standardisiertem nichtinfektiösem Wiederreiz vergleichen, mit kontrollierter Ausgangszellzahl und Exposition. Ein verbleibender Unterschied stützt Zellgedächtnis; sein Verschwinden schwächt diese Erklärung.
5. **Funktion und Gegenbefunde:** Passende Hepatozytenfunktions-/Regenerationsgrößen mitführen. Markerabnahme allein durch Zellverlust widerlegt reine Inaktivierung. Im isolierten Teilsystem mit fester Ausgangskohorte verändert ein anderer Zellschicksalsanteil die Austrittsverteilung aus dem aktiven Zustand nicht. Im Gesamtmodell oder in einer Kultur beeinflussen auch Proliferation, Reaktivierung, Ligandenexposition und Zufall die aktive Zellzahl; ihr schnellerer Nettoabfall identifiziert daher allein keine geänderte Austrittsrate. Weniger Kollagen bei Funktionsverlust ist kein positives Behandlungsergebnis.
6. **Benötigte Daten:** Gemeinsame Zeitverläufe von Zellschicksal, Überleben, Proliferation, Matrixproduktion/-abbau und Wiederantwort mit biologischen IDs und Expositionsangaben. Erst Pilotvarianz bestimmen, danach Power, relevante Effektgrößen oder Äquivalenzgrenzen festlegen. GSE304675, GSE256398 und GSE256377 sind Quellenhinweise, keine in diesem Paket heruntergeladenen oder kalibrierten Behandlungsdatensätze.

Es wurden keine Laborversuche durchgeführt. Dies ist eine Planungshilfe, kein Tierversuchsprotokoll, Infektionsverfahren, menschlicher Behandlungsplan oder Nachweis einer neuen Therapie.

## Literatur

1. Bouguéon, M., et al. (2024). *A rule-based multiscale model of hepatic stellate cell plasticity: Critical role of the inactivation loop in fibrosis progression*. PLOS Computational Biology 20(7), e1011858. DOI: 10.1371/journal.pcbi.1011858.
2. Wang, X., et al. (2026; online 2025). *Single-cell analysis of heterogeneity in reverted hiPSC-derived human hepatic stellate cells*. JHEP Reports 8(2), 101669. DOI: 10.1016/j.jhepr.2025.101669; PMC12803900, Abb. 6–7.
3. Ilha, M., et al. (2025). *Indole-3-propionic acid promotes hepatic stellate cells inactivation*. Journal of Translational Medicine 23, 253. DOI: 10.1186/s12967-025-06266-z.
4. Sugimoto, A., et al. (2025). *Hepatic stellate cells control liver zonation, size and functions via R-spondin 3*. Nature 640, 752–761. DOI: 10.1038/s41586-025-08677-w; PMC12003176.
