# HSC-Prüfung vor einer Laborweitergabe: abgeschlossene Numerik und offene Lücken

26. Oktober 2026 · [English](30-HSCPreLabVerification.md)

**Entscheidung: keine Weiterleitung an ein Labor.** Die neuen rechnerischen Prüfungen sind abgeschlossen. Sie stützen einen größeren zurückbleibenden inaktiven Zellpool unter dem gewählten Zellschicksalskontrast, belegen aber keine verlässliche Kollagensenkung. Eine quantitativ kalibrierte Behandlungshypothese liegt weiterhin nicht vor.

## Festgelegter Versuch und tatsächliche Ausführung

HSR-HSC-ROBUST-001 v1.0.0, [Spezifikation](../Research/HSCRobustness/spec.json), SHA256 `d78f8f8bd71b82dc78e22da559e74078d79f420c34018c90a9cc846941c61a46`, ergänzt [den vorherigen Meilenstein](29-HSCFateLabDecision.de.md). Originalmodell-Commit: `773a84e65b514b969db20c57b6bf0ba97c1d32fb`. Abgebildet wird HSC-Plastizität im Maus-/CCl4-Kontext durch modellierte TGFβ1-Eingänge; kein Modell menschlicher alkoholassoziierter Erkrankung oder dekompensierter Zirrhose. Der Schädigungsverlauf bleibt gleich. Nach Modelltag 60 steigt der gewählte Inaktivierungsanteil reaktivierter MFB von 0,05 auf 0,50, bei unveränderter gesamter Austrittsrate. Endpunkt: Tag 90; Ausgabeintervall: 0,5 Modelltage. COL1 trägt ursprüngliche Modelleinheiten; iHSC und aSMA-cells sind Modellzellzahlen, keine gemessenen Laborwerte.

Sieben neue Zellschicksalskontraste (Seeds 104–110) ergänzen die bisherigen drei auf zehn gepaarte Startwerte. Zehn bereits betrachtete Default-Kontrollsimulationen werden wiederverwendet; sie sind Entwicklungssimulationen, keine unabhängigen biologischen Kontrollen. Vier weitere Läufe vergleichen Kontrolle und Kontrast bei Seeds 101–102 mit einer inaktiven Zellhalbwertszeit von 30 statt 730 Modelltagen nach Tag 60. Das ist eine frei gewählte Belastungsannahme, kein empirisch geschätzter plausibler Bereich. Keine Dosis, Arzneimittelantwort oder Parameterverteilung wurde angepasst.

Alle elf neuen KaSim-Prozesse endeten mit Exit 0 und erreichten Tag 90. Ihre summierten Laufzeiten betragen 4153.706 Sekunden und liegen unter der festgelegten Grenze von 6.600 Sekunden; verwendet wurden zwei Worker. Summierte Prozesslaufzeit ist weder verstrichene Sitzungszeit noch CPU-Zeit. Keine Simulation wurde wiederholt. Die Rechnungen liefen lokal; neue Goose-/Ollama-Inferenz wird nicht behauptet.

## Ergebnisse: zehn gepaarte Startwerte

Differenzen bedeuten Szenario minus Kontrolle. Der Bootstrap verwendet 20.000 Wiederholungen und Seed 2026102603. Die Intervalle beschreiben explorativ die Streuung über endlich viele Seeds bei festen Parametern; Messfehler, biologische Variation und Parameterunsicherheit fehlen. Kleine Seed-Zahlen und vorherige Einsicht begrenzen die Aussage. Gleiche Seeds erhalten nach dem Eingriff keine identischen Reaktionspfade. Die Tabellen verwenden Dezimalpunkte.

| Messgröße | Mittlere Differenz | Standardabweichung | Monte-Carlo-Standardfehler | 95%-Bootstrap-Intervall | Positiv / gesamt |
|---|---:|---:|---:|---|---:|
| COL1 tot | -0.021666 | 0.052342 | 0.016552 | [-0.053339, 0.008783] | 4/10 |
| iHSC | 14018.900000 | 557.162942 | 176.190393 | [13717.595000, 14362.605000] | 10/10 |
| aSMA-cells | -38.800000 | 112.389996 | 35.540837 | [-106.902500, 25.200000] | 3/10 |

COL1 steigt in vier und fällt in sechs Seeds. Das Intervall des Mittelwerts überschreitet null; dies belegt weder eine verlässliche Senkung noch Gleichwertigkeit. Der inaktive Zellpool wächst in allen zehn Seeds. Das exakte binomiale 95%-Intervall für eine positive iHSC-Differenz beträgt [0,691503; 1,000000], für COL1 [0,121552; 0,737622]. Gemeint sind Ergebnisse pseudorandomisierter Seeds, keine Ansprechwahrscheinlichkeiten bei Patienten. Auch die Änderungen der aSMA-Zellzahl haben unterschiedliche Vorzeichen.

Die sieben neu ausgeführten Kontraste werden getrennt vom bereits betrachteten Pilotversuch ausgewiesen:

| Messgröße | Mittlere Differenz | Standardabweichung | Monte-Carlo-Standardfehler | 95%-Bootstrap-Intervall | Positiv / gesamt |
|---|---:|---:|---:|---|---:|
| COL1 tot | -0.014823 | 0.044753 | 0.016915 | [-0.044134, 0.016573] | 3/7 |
| iHSC | 14019.714286 | 605.294065 | 228.779652 | [13653.803571, 14472.571429] | 7/7 |
| aSMA-cells | -10.428571 | 97.450598 | 36.832864 | [-74.142857, 59.285714] | 3/7 |

## Alternative Persistenzannahme

| Seed | Messgröße | Differenz bei 730-Tage-Annahme | Differenz bei 30-Tage-Annahme |
|---|---|---:|---:|
| 101 | COL1 tot | 0.031917 | 0.053891 |
| 101 | iHSC | 14638.000000 | 10023.000000 |
| 101 | aSMA-cells | -26.000000 | 88.000000 |
| 102 | COL1 tot | -0.026078 | 0.094704 |
| 102 | iHSC | 13799.000000 | 9604.000000 |
| 102 | aSMA-cells | -25.000000 | 173.000000 |

Der zurückbleibende inaktive Zellpool ist auch in beiden alternativ geprüften Paaren größer. COL1 ist in beiden höher; Seed 102 wechselt gegenüber der ursprünglichen Persistenzannahme die Richtung. Die aSMA-Zellzahl wechselt in beiden die Richtung. Bei nur zwei Paaren lässt sich Zufallsstreuung nicht zuverlässig vom Einfluss der Annahme auf die Vorzeichen trennen. Das warnt vor einer robusten Behandlungsaussage; es ist weder eine globale Sensitivitätsanalyse noch ein gemessener biologischer Effekt. Erneute Stimulation und Organfunktion wurden nicht simuliert.

## Verifikation und behobener Fehler

Neun gezielte Tests bestanden. Vollständige Halbtag-Ausgaberaster, exakte Tag-90-Endpunkte, Übereinstimmung vor dem Eingriff und die Übernahme der bisherigen Pilot-/Kontrolldaten wurden geprüft. Die Auswertung privater Rohspuren und bereinigter öffentlicher Spuren ist in getrennten Prozessen bytegleich. Der Export entfernt ausschließlich Kommentarzeilen; die eingelesenen Zahlenzeilen sind exakt gleich. Die Wiederaufnahme eines fertigen Ergebnisses wurde bei technisch gesperrtem Unterprozessstart ausgeführt und ließ sämtliche ursprünglichen Ergebnisdateien unverändert. Belege: [Verifikation](../Research/HSCRobustness/verification.json), [Wiederaufnahme](../Research/HSCRobustness/resume-verification.json), [Ergebnisse](../Research/HSCRobustness/results/analysis.json), [Wiederholungsbefehle](../Research/HSCRobustness/README.md).

Der ursprüngliche Prüfer wies zwei vollständige Alternativläufe zurück. Zwei `$PLOTENTRY`-Operationen zum selben Ereigniszeitpunkt zeigen die erste Parameteränderung vor der zweiten. Der korrigierte Prüfer akzeptiert genau diese Zwischenzeile ausschließlich beim ersten Ereignis nach Tag 60, unmittelbar gefolgt von der vollständigen Änderung zum identischen Zeitpunkt und bei unverändertem biologischem Zustand. Ursprüngliche Fehlermanifeste und ausgeführter Prüfer bleiben erhalten; separate Belege dokumentieren die erneute Prüfung. Modell, Seeds, Effektschwelle und Endpunkt wurden nicht geändert. Die endgültige Analyse stammt vom korrigierten Prüfer, nicht vom ursprünglichen. Das legt der [nachträgliche Prüfnachtrag](../Research/HSCRobustness/export-amendment.json) offen. Regressionstests verwerfen geänderte biologische Zustände, abweichende Ereigniszeiten und fehlende vollständige Änderungen.

Der Koordinator verlor eine Prozessidentitätsbeobachtung und markierte den Lauf als unklar, während seine Vordergrund-Kindprozesse weiterliefen. Nach Ende sämtlicher Kinder wurden deren Abwesenheit und alle elf Manifeste geprüft; der Koordinatorjob wurde manuell als unterbrochen aufgelöst. Die abhängige Analyse wurde storniert; ein separat gekennzeichneter Prüf-/Exportjob bestand. Der ursprüngliche Koordinatorstatus wurde nicht nachträglich als erfolgreich ausgegeben.

## Verbleibende Grenzen

| Evidenzebene | Stand / erforderlicher Nachweis |
|---|---|
| Software und Numerik | Genannte Kontrollen und neun Tests bestanden; elf vollständige Läufe, zwei erhaltene Ausgabeformat-Nachprüfungen |
| Publikationsreproduktion | Originalregeln und eigene Runtime festgelegt; genaue Autorenumgebung weiterhin ungeklärt |
| Kalibrierung / Parameterunsicherheit | Keine empirische Anpassung; das frühere bedingte Identifizierbarkeitsgegenbeispiel ist kein globaler Beweis für das vollständige Kappa-Modell |
| Unabhängige biologische Vorhersage | Keine passenden unabhängigen gemeinsamen Zellschicksals-/Matrixzeitreihen geprüft |
| Zuordnung eines Eingriffs | Keine quantitative Verknüpfung von IL-10 oder anderen Eingriffen mit den gewählten Zellschicksals-/Persistenzparametern |
| Übertragung auf Menschen / klinische Validierung | Nicht belegt; keine Aussage über Behandlungswirksamkeit oder Organerholung |

Das Runtime-Audit bestätigt: Die verwendete KaSim-Version 4.1.3.1 erschien am 16. Oktober 2024, nach der Publikation vom 29. Juli 2024. Die Publikation nennt weiterhin Kappa 4.2.12; unter den abgefragten offiziellen Tags war dieser Tag nicht vorhanden. Ein Electron-Versionshinweis in Release-Notizen ist nur ein Anhaltspunkt und identifiziert den Autorensimulator nicht. Benötigt werden der Hash der Autoren-Binärdatei oder Simulator-Commit mit Compiler-/Paket-Lock und Seeds. Keine Ersatzruntime wurde geraten oder installiert. [Quelladressen, Zugriffsfehler und Hashes](../Research/HSCRobustness/runtime-review.json).

Die Prüfung ergänzender Quelldaten wurde durch eine automatische Sicherheitsprüfung des Dienstes mit Verweis auf mögliche biologische Doppelnutzung unterbrochen. Sie wurde weder abgeschlossen noch auf anderem Weg wiederholt. Teildateien bleiben privat und wurden weder zur Kalibrierung noch zur Veröffentlichung verwendet. Es wird nicht behauptet, dass sie die fehlenden gemeinsamen Messungen liefern.

Der nächste hilfreiche Eingang sind geprüfte gemeinsame Zeitreihen zu Zellschicksal, lebensfähigen Zellzahlen, Proliferation, Matrixproduktion/-abbau und Reaktion nach erneuter Stimulation, mit biologischen IDs und Expositionsmetadaten. Eine fachkundige Prüfung muss klären, ob Kandidatenwirkungen diesen Modellparametern zugeordnet werden können und ob Funktion erhalten bleibt. Die rechnerischen Prüfungen können diese Beobachtungen nicht ersetzen. Kein Labor wurde kontaktiert, keine Laborarbeit durchgeführt und keine Weitergabe durch dieses Paket freigegeben.
