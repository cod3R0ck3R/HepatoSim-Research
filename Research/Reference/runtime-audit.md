# Laufzeitaudit des originalen stochastischen Kappa-Modells

Stand: 22.10.2026. Dieses Audit untersucht die unveränderten veröffentlichten Kappa-Dateien. Es ersetzt sie nicht durch die Swift-ODE. Alle Downloads und Tests liegen ausschließlich unter `work/runtime-audit`; keine globalen Pakete wurden installiert. Positive Simulationszeit und wissenschaftliche Benchmarkläufe wurden im Rahmen dieses Audits nicht ausgeführt.

## Ergebnis

Die drei Originalmodelle lassen sich auf diesem Apple-Silicon-Rechner mit dem offiziellen macOS-KaSim-Binary aus **KappaTools v4.1.3.1** parsen, kompilieren und bei Zeit null initialisieren. Das Binary ist **x86_64**, wurde auf diesem Rechner erfolgreich ausgeführt und ist keine hier nachgewiesene native ARM64-Version. Der Papierstand „Kappa 4.2.12, OCaml 4.13.1“ konnte keinem offiziellen KaSim-Tag zugeordnet werden. Deshalb ist die geprüfte Laufzeit ein konkret identifizierter Kompatibilitätskandidat, keine behauptete identische Autorenumgebung.

Die veröffentlichte Python-Pipeline ist in ihrem ausgecheckten Zustand nicht unmittelbar ausführbar. Für kontrollierte Reproduktionsläufe ist der direkte Aufruf der unveränderten `.ka`-Datei mit KaSim der kürzeste belastbare Weg.

## Eingefrorene Quellen und Lizenzen

| Bestandteil | Geprüfter Stand | Lizenz im Repository |
|---|---|---|
| [HSC_model_Kappa](https://github.com/MBougueon/HSC_model_Kappa/tree/773a84e65b514b969db20c57b6bf0ba97c1d32fb) | `773a84e65b514b969db20c57b6bf0ba97c1d32fb`, 12.04.2024 | GNU AGPL v3; Quelldateien nennen Version 3 oder neuer |
| [simulation_pipeline](https://github.com/MBougueon/simulation_pipeline/tree/8b10a8dc403190a0b198918f0288b3d962ab7d40) | `8b10a8dc403190a0b198918f0288b3d962ab7d40`, 24.10.2023 | GNU AGPL v3; Quelldateien nennen Version 3 oder neuer |
| [KappaTools v4.1.3.1](https://github.com/Kappa-Dev/KappaTools/tree/bafaeb8873cb4e4afd9b22ae312dc93724cfc2fa) | Commit `bafaeb8873cb4e4afd9b22ae312dc93724cfc2fa` | `LGPL-3.0-only` laut `kappa-binaries.opam` |

Die lokalen Original-Checkouts blieben unverändert. Lizenztexte und Herkunft müssen bei einer späteren Weitergabe mitgeführt werden. Eine eigenständige wissenschaftliche Ausführung im Arbeitsverzeichnis ist nicht mit einer abgeschlossenen Lizenzprüfung für die Integration in eine verteilte App gleichzusetzen.

SHA-256 der Modelle:

| Datei | SHA-256 |
|---|---|
| `reactMFB-with-inactivation.ka` | `dcfeae87699640cf917e038910402140528e93c0a09897664c3a336f7b397f7d` |
| `reactMFB-wo-inactivation.ka` | `fe426011b22b20494bfabd88728700b690c379ecafc19873072cb52ff59328f9` |
| `iHSC-reversion-to-qHSC.ka` | `b1ce4c1460c333aedd2ab64ff737eba4a4f6a8fb3af47d611abd9d6b8a7caacb` |

## Laufzeitbeschaffung und Versionsunsicherheit

Das in den Original-READMEs verlinkte `https://kappalanguage.org/download` lieferte beim Abruf 404. Die offizielle [Release-Seite](https://github.com/Kappa-Dev/KappaTools/releases/tag/v4.1.3.1) bietet hingegen ein macOS-Archiv an. Downloadquelle:

`https://github.com/Kappa-Dev/KappaTools/releases/download/v4.1.3.1/Kappapp_macos10.15.app.zip`

- Archivgröße: 155.038.432 Byte.
- Archiv-SHA-256: `6c94655255e48d280578681bac52555a7cb7ecf2686113dc3986c8e9c60c20c5`.
- Ausschließlich `Kappapp.app/Contents/Resources/bin/KaSim` wurde als ausführbare Datei extrahiert; die Electron-Anwendung wurde weder installiert noch gestartet.
- Lokaler Pfad: `work/runtime-audit/runtime-v4.1.3.1/KaSim`.
- Binary-SHA-256: `ecff78d14fc6370ef6086b8c5cbcf1d5efd4d79b0a534c2b4d6e6849eef6d2f8`.
- Dateityp: Mach-O 64-bit x86_64; dynamische Abhängigkeit laut `otool -L`: Systembibliothek `libSystem.B.dylib`.
- `--help` meldet `KaSim bafaeb8`. Das vollständige Ergebnis liegt in `work/runtime-audit/kasim-help.log`.
- Der Release-Anhang stellte beim API-Abruf keinen eigenen Digest bereit. Die hier erfassten SHA-256-Werte sichern die lokale Artefaktidentität, sind keine unabhängige Herausgebersignatur.

Die öffentlich abgefragte Tagliste enthält keine Version `4.2.12`. Die [Release-Notizen zu v4.1.3](https://github.com/Kappa-Dev/KappaTools/releases/tag/v4.1.3) erwähnen dagegen explizit ein Update der **Electron**-Abhängigkeit von 4.2.12 auf 9.1.0. Eine Verwechslung der UI-Abhängigkeit mit der Simulatorkennung ist daher möglich, aber nicht belegt. Der [Originalartikel](https://doi.org/10.1371/journal.pcbi.1011858) bleibt hinsichtlich seiner genannten Version unverändert zitiert. Für eine bitgenaue Wiederholung wären der Autoren-Binary-Hash oder ein eindeutig zugehöriger Simulator-Commit sowie die ursprünglichen Seeds erforderlich.

Die [offiziellen Nightly-Artefakte](https://tools.kappalanguage.org/nightly-builds/) waren ebenfalls sichtbar. Sie wurden nicht als unversionierter Ersatz verwendet. Context7 lieferte keinen passenden Kappa/KaSim-Eintrag; die Laufzeitprüfung stützt sich auf die offiziellen Quellen und das geprüfte Binary.

## Durchgeführte Prüfungen

Jeder der folgenden Aufrufe erhielt über Python `subprocess.run(..., timeout=60)` eine harte Zeitgrenze. Es wurde kein Shell-String aus Modellparametern ausgeführt. Die Befehle gelten vom ursprünglichen Chat-Arbeitsverzeichnis aus; die gespeicherten `command.json`-Dateien enthalten die tatsächlich verwendeten absoluten Argumente.

```sh
work/runtime-audit/runtime-v4.1.3.1/KaSim --help

work/runtime-audit/runtime-v4.1.3.1/KaSim \
  work/runtime-audit/HSC_model_Kappa/reactMFB-with-inactivation.ka \
  -l 0 -p 1 -seed 42 -mode batch \
  -d work/runtime-audit/zero-time-smoke -o smoke.csv -log inputs

work/runtime-audit/runtime-v4.1.3.1/KaSim \
  work/runtime-audit/HSC_model_Kappa/reactMFB-wo-inactivation.ka \
  -l 0 -p 1 -seed 42 -mode batch \
  -d work/runtime-audit/zero-time-reactMFB-wo-inactivation -o smoke.csv -log inputs

work/runtime-audit/runtime-v4.1.3.1/KaSim \
  work/runtime-audit/HSC_model_Kappa/iHSC-reversion-to-qHSC.ka \
  -l 0 -p 1 -seed 42 -mode batch \
  -d work/runtime-audit/zero-time-iHSC-reversion-to-qHSC -o smoke.csv -log inputs
```

Alle drei Modellaufrufe endeten mit Exitcode 0 nach ungefähr 0,3 Sekunden. Sie bestätigen Parser-, Compiler- und Initialisierungskompatibilität einschließlich der Counter-Syntax `{=0 / +=14}`. Sie bestätigen weder langfristige numerische Eigenschaften noch die Reproduktion einer Abbildung. Das finale Modell erzeugte intern 160.000 Agenten; dies sind nicht 160.000 biologische HSC, sondern die explizite Kappa-Repräsentation einschließlich Counter. Der Ausgangs-CSV enthält 10.000 qHSC und Gesamt-COL1 0,5 bei Zeit null. Die Originaldateien wurden dafür nicht skaliert.

Prüfbelege: je Modellordner `command.json`, `run.log`, `smoke.csv` und KaSim-Eingabeprotokoll. Eine spätere Benchmarkauswertung muss stdout, stderr, Laufzeit, Endzeit, Seed und Dateidigest zusätzlich sichern.

## Warum die veröffentlichte Pipeline nicht unmittelbar läuft

Fundstellen beziehen sich auf Commit `8b10a8d`:

1. `README.md` nennt `utils.py`, und beide Python-Dateien importieren dieses Modul. Es fehlt jedoch im Repository; das erste Importieren von `launch.py` würde daran scheitern.
2. `graph_kaSim.py:422` enthält ein `if`, dessen einziger eingerückter Inhalt ein Kommentar ist. `ast.parse` bricht bei Zeile 424 mit `IndentationError` ab. Das wurde geprüft, ohne die Pipeline auszuführen.
3. `launch.py:115` initialisiert `output_file` nur in einem Zweig. Für einen einzelnen Wiederholungslauf mit höchstens einem Kombinationswert bleibt es bei der späteren Verwendung undefiniert.
4. `launch.py:120` sucht über `?-*.ka`; keiner der drei veröffentlichten Modellnamen passt zu diesem Muster. Die Konfiguration enthält zudem beispielhafte Linux-Home-Platzhalterpfade.
5. `launch.py:116` prüft/erzeugt den übergeordneten Ausgabeordner, nicht den in Zeile 115 berechneten Unterordner. Die Ausgabeorganisation ist deshalb nicht vollständig vorbereitet.
6. Der Zufallswert in `launch.py:100` dient dem Dateinamen. Der KaSim-Aufruf erhält keinen `-seed`; er ist dadurch kein reproduzierbarer Seed-Vertrag. Zeile 121 nutzt außerdem `shell=True` mit zusammengesetzten Parametern.
7. Die Plot-Abhängigkeiten `numpy`, `pandas`, `matplotlib`, `plotly` und `kaleido` sind nicht versioniert. `DataFrame.append` und `pio.kaleido.scope` binden den Code an ältere Schnittstellen. Die README nennt Python 3.8, enthält aber keinen vollständigen Lockfile.
8. `graph_kaSim.py:141–155` setzt den DataFrame innerhalb der Schleife über CSV-Dateien zurück und berechnet den Mittelwert erst danach. Dieser Auswertungspfad darf ohne Prüfung nicht als Mittel über sämtliche Replikate verwendet werden. Andere Plotfunktionen besitzen eigene Pfade; dies ist keine Behauptung, dass jede Plotfunktion denselben Fehler enthält.

Diese Probleme wurden protokolliert und nicht stillschweigend im Original behoben. Ein separater, versionierter Prozess-Launcher kann KaSim direkt aufrufen und die CSV-Dateien unabhängig auswerten, ohne die Modellregeln umzuschreiben.

## Abbildungsziel und kleinster sinnvoller Folgelauf

Abbildung 2 B2/B3 des Artikels verwendet das Modell mit Reaktivierungs-Inaktivierung, 16 Stimuli im Abstand von 84 Stunden und zehn Wiederholungen. B2 zeigt Mittelwerte der Zellzustände; B3 zeigt zehn Kollagenverläufe. Die Bildlegende nennt 10.000 TGFβ1-Moleküle pro Zelle. Im Quellmodell entspricht dies `TGFB1_pool_by_cell = 1`, während der Repository-Default **6** beträgt. Die beiden Bedingungen dürfen deshalb nicht unbemerkt vermischt werden.

Beispiel für genau einen Lauf der **Legenden-Bedingung**, noch kein Nachweis einer erfolgreichen Abbildungsreproduktion:

```sh
work/runtime-audit/runtime-v4.1.3.1/KaSim \
  work/runtime-audit/HSC_model_Kappa/reactMFB-with-inactivation.ka \
  -var nb_iteration 16 -var interval_py 84 \
  -var TGFB1_pool_by_cell 1 -var inactivation_pourcentage_react 0.05 \
  -var second_input 0 -l 243 -p 0.5 -seed 101 -mode batch \
  -d work/runtime-audit/figure2-caption-seed101 -o trajectory.csv -log inputs
```

Der Ausgabeordner muss vorher existieren. `-p 0.5` ist hier eine ausdrücklich gewählte Ausgabefrequenz, kein aus dem Artikel verifizierter Originalwert. Die Quellregel beendet den Lauf bei Überschreiten von 242,5 Tagen; ein externes Limit 243 lässt diese Originalbedingung wirksam werden. Seeds sind zu dokumentieren, aber mangels publizierter Originalseeds nicht als identische Autoren-Seeds auszugeben. `--print-efficiency` kann ergänzend die Ereignisstatistik liefern.

Vor positiven Benchmarkläufen wurde separat `benchmark-v1.0.0.json` mit SHA-256 `16dc215a6ef5e50f502236df7f059d0748ea6af5a81d5ed7333f94fc7d99c9a2` eingefroren. Dieser Vertrag umfasst 32 Läufe einschließlich Repository-/Legendenbedingungen, Varianten und Reproduzierbarkeitsprüfungen. Er ist für die tatsächlichen Benchmarks maßgeblich, nicht das obige Einzelbeispiel.

Budgetempfehlung: zunächst ein Lauf mit höchstens 180 Sekunden und sichtbarem Abbruchstatus; nur bei vollständigem Abschluss fortsetzen. Für den eingefrorenen Satz gelten maximal zwei Prozesse, 180 Sekunden pro Prozess und 3.600 Sekunden Gesamtlaufzeit. Die Initialisierungszeit erlaubt keine belastbare Extrapolation der gesamten stochastischen Ereigniszahl. Keine Optimierung, Parametersuche oder stille Reduktion der Zellzahl bei Zeitüberschreitung.

## Laufzeitnachtrag: `--gluttony` ohne Modelländerung

Nach dem Zeitlimit des ersten positiven v1-Laufs wurde ausschließlich der Quellcode des Laufzeitschalters geprüft; in diesem Audit wurden dafür keine weiteren Simulationen gestartet. Im fixierten KaSim-Commit setzt `core/cli/common_args.ml:41–42` genau einen OCaml-GC-Parameter: `Gc.space_overhead = 500`. Die Zuordnung des Schalters steht in `:81–87`. Der bestehende GC-Steuerdatensatz wird ansonsten übernommen. Der Quellkommentar nennt 80 als Default; der tatsächlich einkompilierte Runtime-Default wurde nicht ausgelesen.

Dies ist keine feste Heapreservierung und erhöht weder `minor_heap_size` noch die biologische Zellzahl. Der Parameter erlaubt mehr Speicheraufwand, damit der Major-GC weniger häufig arbeiten muss. Eine Beschleunigung ist bei hoher GC-Last plausibel, aber aus 160.000 intern repräsentierten Agenten allein nicht ableitbar. Insbesondere werden weder Ereigniszahl noch Reaktionsraten reduziert. Ein tatsächlicher Zeitgewinn und der Spitzenspeicherbedarf sind erst durch Messung nachgewiesen.

Die Quellenprüfung spricht für unveränderte Trajektorien bei identischem Binary, Seed und sonstigen Modell-/Laufargumenten:

- `core/main/KaSim.ml:257–267` erzeugt aus dem expliziten Seed einen eigenen `Random.State` für die Simulation.
- `core/simulation/state_interpreter.ml:593–594` verwendet diesen Zustand für die Ereigniswartezeit; `generic_rule_interpreter.ml:1271–1283` verwendet ihn für Regel- und Instanzauswahl.
- Eine Suche im versionierten OCaml-Quellbaum nach `Gc.`, `Weak.`, `Ephemeron`, `Obj.` und `Hashtbl.randomize` ergab außer dem genannten GC-Setter keine Treffer. Dies ist keine Prüfung sämtlicher Runtime-/Bibliotheksimplementierungen.
- Die geprüften Modelle verwenden Simulationszeit `[T]`, keinen CPU-Zeitgeber für biologische Bedingungen. Der GC-Schalter verändert keine dieser Bedingungen und ruft keinen Zufallszahlengenerator auf.

**Erwartete Gleichheit ist noch kein empirischer Gleichheitsnachweis.** Für eine ausschließlich auf Laufzeit und Budget beschränkte, vor Ausführung eingefrorene v1.1-Ergänzung ist `--gluttony` deshalb technisch begründbar. Die numerischen Datenzeilen im gemeinsamen abgeschlossenen Zeitbereich des ursprünglichen Seed-101-Laufs und des neuen Laufs sollten verglichen werden; ein vollständig abgeschlossener Lauf mit zusätzlichem Wiederholungslauf bleibt der stärkere Reproduzierbarkeitsnachweis. Dateiheader, Befehlszeilen und Auditfelder können abweichen. Insbesondere erzeugt `core/cli/outputs.ml:15` unabhängig vom Simulations-Seed eine zufällige Ausgabe-UUID; ein Ganzdatei-Hash ist daher kein allein geeigneter Trajektorienvergleich.

Die Hardwareabfrage während der Prüfung ergab Apple M3, 8 CPU-Kerne und 17.179.869.184 Byte RAM (16 GiB). `memory_pressure -Q` meldete zu diesem Zeitpunkt 69 Prozent systemweit frei; dies ist eine Momentaufnahme und keine garantierte Speicherverfügbarkeit für parallele Prozesse. Eine Anpassung auf 900 Sekunden pro Lauf bei unverändertem Gesamtbudget von 3.600 Sekunden wurde vom Hauptlauf vorgeschlagen, hier aber weder als ausgeführter Vertrag noch als ausreichende Laufzeit bestätigt. Die ursprüngliche v1-Spezifikation und ihr Timeout-Befund bleiben erhalten.

## Modell- und Implementierungsfragen vor einer Reproduktionsbehauptung

- `reactMFB-with-inactivation.ka:317` und `:320` verwenden in COL1-Raten `12*h*time_unit`, andere entsprechende Raten `12*h/time_unit`. Bei der angegebenen Tageszeitskala ist das eine erhebliche dimensionsbezogene Inkonsistenz. Sie bleibt im Original erhalten; ein korrigierter Modellzweig wäre ein gesondertes Experiment.
- Die TGFB-Modulationen bei `:346` und `:357` teilen sich `clock` und `iteration`. Daraus folgt nicht automatisch eine doppelte Dosis: Im geprüften KaSim-Commit prüft `core/simulation/state_interpreter.ml:230–275` die Bedingungen sequenziell gegen den jeweils aktualisierten Graphen; `:119–126` aktualisiert Variablen unmittelbar. Der erste ausgeführte Block verändert damit die Bedingung des folgenden. Tatsächliche Stimuluszahlen und die Behandlung des zweiten Stimulationszeitraums müssen dennoch anhand des Laufs geprüft werden.
- Das Dokumentationswort „nach dem letzten Stimulus“ und die Formel `nb_iteration*interval + input_time` verwenden möglicherweise unterschiedliche Zeitanker: bei Start 4 und 16 Abständen von 3,5 liegt der erste Zeitpunkt bei 4, der sechzehnte nominell bei 56,5, die Stopformel verwendet aber 60 als Basis. Keine nachträgliche Achsenverschiebung ohne ausdrückliche Kennzeichnung.
- Die feste Abnahme von COL1-Token um `COL1_deg` wird über vom aktuellen Bestand abhängige Raten ausgelöst. Eine Schrankenprüfung für kleine Restbestände ist im Modelltext nicht erkennbar. Ob negative Bestände tatsächlich auftreten, ist mit den positiven Läufen zu prüfen, nicht aus dem Nullzeit-Test abzuleiten.

## Quellbuild als Ausweichweg

Auf diesem Rechner waren weder `opam`, `ocaml`, `dune` noch `KaSim` im PATH. Ein Quellbuild war nach erfolgreichem Binary-Test nicht nötig. Der geprüfte Release deklariert OCaml `>=4.13.0,<5.0.0`, Dune `>=2.9`, Yojson 2.1.0, Lwt 5.7.0, Num 1.5, Re 1.11.0, Fmt 0.9.0, Logs 0.7.0, Result 1.5, Stdlib-shims 0.3.0 und Camlp-streams 5.0.1. `kappa-library` gehört ebenfalls zum CLI-Build.

Für eine spätere native ARM64-Ausführung: offizielles opam-Binary ausschließlich in einem lokalen Werkzeugordner bereitstellen; `OPAMROOT` auf einen Unterordner des Arbeitsverzeichnisses setzen; dort einen lokalen OCaml-4.13.1-Switch und die im Repository deklarierten CLI-Abhängigkeiten installieren; anschließend den fixierten Commit mit `make all` bauen. Dies ist ein noch nicht ausgeführter Ausweichplan. Kein globales Homebrew-/pip-/opam-Setup, kein automatischer Wechsel zu einem anderen mathematischen Modell. Ein vollständiger lokaler Erstbuild benötigt ein eigenes Zeit- und Speicherbudget; für einen ersten Versuch höchstens 15 Minuten, danach klarer Abbruchbericht.
