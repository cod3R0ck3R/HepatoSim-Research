# Prüfung der Referenzvarianten und des GC-Laufzeitnachtrags

Stand: 2026-10-22. Begrenzte Read-only-Prüfung der vendorten Originalmodelle und bereits vorhandener Läufe. Es wurden keine neuen Simulationen gestartet, keine Parameter angepasst und keine Quellen oder Laufdaten verändert. Die numerischen Ergebnisse dieses Berichts stammen aus einer Python-Standardbibliotheksprüfung (`csv`, `difflib`, `hashlib`, `json`, `math`); alle unten genannten Gleichheitsbedingungen wurden als Assertions geprüft.

## 1. Vollständiger Quelldiff

Bezug: `vendor/HSC_model_Kappa/`, Originalcommit `773a84e65b514b969db20c57b6bf0ba97c1d32fb`.

| Datei | SHA-256 |
|---|---|
| `reactMFB-with-inactivation.ka` | `dcfeae87699640cf917e038910402140528e93c0a09897664c3a336f7b397f7d` |
| `reactMFB-wo-inactivation.ka` | `fe426011b22b20494bfabd88728700b690c379ecafc19873072cb52ff59328f9` |

Der Vergleich aller Zeilen ergibt genau **einen** zusammenhängenden Änderungsblock: `reactMFB-with-inactivation.ka:296–300` wird durch `reactMFB-wo-inactivation.ka:296` ersetzt. Der restliche Dateiinhalt ist zeilenidentisch; die nachfolgenden Zeilennummern verschieben sich um die entfernten Zeilen. Beide Dateien enthalten jeweils 80 `%var`-, 10 `%obs`-, 4 `%init`- und 7-Direktivzeilen. Die jeweiligen Direktivzeilen sind einschließlich ihrer Reihenfolge exakt gleich. Dies sind syntaktische Deklarationszahlen, keine Anzahl unabhängiger biologischer Parameter.

Der Block verändert zwei gekoppelte Reaktionswege:

- `with:300`: Der Übergang reaktivierter Myofibroblasten in den inaktivierten Zustand entfällt vollständig in `without`.
- `with:296` gegenüber `without:296`: Die Apoptose-/Seneszenzrate verliert den Faktor `apop_sene_react_MFB_pourcentage`. Damit übernimmt sie die gesamte zuvor auf beide Wege aufgeteilte Abgangsrate.

Andere Regeln, Parameterwerte, Eingangspulse, Startzustände und Observable-Definitionen ändern sich nicht. Insbesondere sind die Kollagenregeln gleich. Der Vergleich isoliert die Verzweigung des Abgangs aus dem reaktivierten MFB-Zustand; er ist kein bloßes Löschen einer Regel bei ansonsten unveränderter konkurrierender Rate.

## 2. Konsequenzen für die eingefrorenen Bedingungen

Maßgeblich ist `benchmark-v1.1.0.json`, SHA-256 `ba8292920faf7765e29c1619e5b5b8efaab0a9bcc63b0a9904135a4cb3b39288`. `without_reinactivation` verwendet die Originaldatei ohne CLI-Override; `reinactivation_10pct` verwendet die Originaldatei mit Reinaktivierung und ausschließlich den Override `inactivation_pourcentage_react = 0.1`.

In beiden Originaldateien definieren Zeilen 98–99 den Reinaktivierungsanteil und seinen komplementären Apoptose-/Seneszenzanteil. Zeilen 90 und 112 legen die gemeinsame Halbwertszeit fest. Mit **k = ln(2) / 3,54 Tage** teilen die beiden Regeln im Modell mit Reinaktivierung die Rate in p·k und (1−p)·k auf. Die berechneten Raten gelten pro passender Zelle mit `reactivated_myofibroblast`, `intermediate_step = 14` und freier TGFB1-Bindungsstelle.

| Bedingung | effektives p | Reinaktivierung [Tag⁻¹] | Apoptose/Seneszenz [Tag⁻¹] | Summe [Tag⁻¹] |
|---|---:|---:|---:|---:|
| repository_default | 0.05 | 0.00979021441469 | 0.186014073879 | 0.195804288294 |
| without_reinactivation | 0 | 0 | 0.195804288294 | 0.195804288294 |
| reinactivation_10pct | 0.1 | 0.0195804288294 | 0.176223859464 | 0.195804288294 |

**`without_reinactivation`:** Der effektive Reinaktivierungszweig ist null, obwohl die unveränderte, nun für diese Reaktionswege unbenutzte Variablendefinition in Zeile 98 weiterhin den Originalwert enthält. Die Apoptose-/Seneszenzrate erhöht sich gegenüber dem Default komplementär; die Summe der beiden betrachteten Abgangsraten bleibt gleich. Dies entspricht auf Ratenebene dem Grenzfall p = 0, ist aber kein Nachweis identischer Seed-Trajektorien gegenüber einem separat kompilierten Modell mit einer beibehaltenen Nullratenregel.

**`reinactivation_10pct`:** Der Override erhöht den Reinaktivierungszweig und verringert über die Definition in Zeile 99 zugleich den Apoptose-/Seneszenzzweig. Er verändert daher zwei komplementäre Raten, nicht die Summe dieser Raten. Die primäre MFB-Inaktivierung bleibt in beiden Bedingungen bestehen: Zeilen 96–97 und 245/250 verwenden einen eigenen Anteil von 0,45. „Ohne Reinaktivierung“ darf deshalb nicht als „ohne jegliche Inaktivierung“ bezeichnet werden.

Die Prozentwerte sind Verzweigungsgewichte der genannten Regeln, keine vorgegebenen Anteile einer Gesamtpopulation, keine Kollagen-Änderungsprozente und keine Wirksamkeiten einer Therapie. Andere Ereignisse können mit diesen Regeln konkurrieren. Zudem führt `with:300` zunächst in den inaktivierten Zwischenzustand; die in beiden Dateien gleiche Regel in Zeile 251 überführt diesen erst in den in `with:339` beziehungsweise `without:335` gezählten iHSC-Zustand. Das iHSC-Observable muss daher nicht unmittelbar dem Reinaktivierungsereignis entsprechen.

Die vorab festgelegten Seeds bleiben Vergleichspaare für die Auswertung. Gleiche Seednummern bei verändertem Regelkatalog garantieren jedoch weder dieselbe Ereignisfolge noch identische Zufallszahlennutzung entlang biologisch entsprechender Ereignisse. Aussagen zu Kollagenunterschieden benötigen die tatsächlich abgeschlossenen Variantenläufe und deren Streuung; aus dem Quelldiff allein folgt keine Richtung oder Größe des Endpunkteffekts.

## 3. Empirischer Vergleich des Seed-101-Präfixes

Geprüft wurden ausschließlich:

- `results/benchmark-v1/repository_default-101/trace.csv` und `run.json`.
- `results/benchmark-v1.1/repository_default-101/trace.csv` und `run.json`.

Die gespeicherten Befehlsargumente stimmen nach Entfernung des jeweiligen Ausgabeordners und des zusätzlichen `--gluttony` exakt überein. Modellhash, Seed, Beobachtungsperiode und angefordertes Zeitlimit sind gleich. Beide Befehle referenzieren denselben Interpreterpfad; dessen bei dieser Prüfung berechneter SHA-256 lautet `ecff78d14fc6370ef6086b8c5cbcf1d5efd4d79b0a534c2b4d6e6849eef6d2f8`. Der v1-Lauf endet laut Manifest als `timeout` mit Returncode -15, der v1.1-Lauf als `completed` mit Returncode 0.

| Eigenschaft | v1 | v1.1 |
|---|---:|---:|
| gespeicherte Datenzeilen | 53 | 502 |
| erste Modellzeit [Tage] | 0 | 0 |
| letzte Modellzeit [Tage] | 23 | 242.5 |
| Spalten einschließlich Zeit | 11 | 11 |

Prüfmethode: Kommentarzeilen und Leerzeilen auslassen, CSV-Header und sämtliche übrigen CSV-Zellen einlesen, numerische Felder als Python-Float prüfen; keine Interpolation, keine Rasterreduktion und keine Rundung vor dem Vergleich. Beide vollständigen gespeicherten Dateien haben ausschließlich endliche Werte und streng steigende Zeitstempel.

**Alle 53 gespeicherten v1-Datenzeilen sind das exakte Präfix der v1.1-Datenzeilen.** Dies gilt für 583 numerische Felder einschließlich Zeit über den Bereich 0 bis 23 Tage. Die maximale absolute Abweichung beträgt 0; kein Feld weicht ab. Zusätzlich sind die eingelesenen CSV-Zellen vor der Float-Konvertierung zeichengetreu gleich, und die Header stimmen überein. Unterschiedliche Kommentarheader und Ausgabe-UUIDs wurden nicht als biologische Werte verglichen.

| Beleg | SHA-256 |
|---|---|
| v1 `trace.csv` | `e15fc9beed4ddf9e7b3eedc2c06a32424ab46d5325bb1cf79c16f87737178984` |
| v1.1 `trace.csv` | `c0060b14872d448aff877591f3adc1c11b24cad7615663ec2d68eade936b841c` |
| v1 `run.json` | `db3d0df991bd5f6d525e41ccc1f10274c327d1cf41d09ad119c2b39d4ebca4af` |
| v1.1 `run.json` | `7cf57432eaad87d1ac5bd45cb3f5b23fda63b254fc83320e9789906ba4eba783` |

Damit ist für diesen Seed und den gemeinsam gespeicherten Beobachtungsbereich keine Auswirkung des GC-Schalters auf die ausgegebenen Werte feststellbar. Das ist ein empirischer Präfixnachweis, kein Nachweis identischer interner Ereignisse, späterer Modellzeiten oder anderer Seeds. Die Behauptung einer kausal durch `--gluttony` erreichten Beschleunigung ist aus diesem Vergleich nicht ableitbar: Ein abgebrochener Lauf und ein vollständiger Lauf mit geändertem Laufzeitbudget bilden keinen isolierten Geschwindigkeitsvergleich. Es wurde weder ein Speedup berechnet noch eine Ursache für unterschiedliche Laufzeiten behauptet.

## 4. Prüfgrenzen

Diese Prüfung untersucht Implementierungsunterschiede und reproduzierbare Ausgabewerte. Sie belegt weder die biologische Richtigkeit der Verzweigungsannahmen noch eine Publikationsreproduktion oder klinische Validierung. Varianten-Endpunkte und ein vollständiger Seed-Replay wurden hier nicht neu ausgeführt. Die ursprünglichen Quell- und Laufdateien wurden nach Erstellung dieses Dokuments erneut gehasht; ihre Digests blieben unverändert.
