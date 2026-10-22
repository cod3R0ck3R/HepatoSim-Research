# Parameterzahl und Identifizierbarkeit: Quellenprüfung

Stand: 22.10.2026. Geprüft wurden ausschließlich die bereits lokal vorhandenen Originalquellen: Bouguéon 2024, S2 Table und `reactMFB-with-inactivation.ka`. Keine neue Simulation, Parameterschätzung oder formale Identifizierbarkeitsanalyse.

**Die Aussage „43 freie Parameter sind anhand zweier 12-/14-fach-Ziele nicht bestimmbar“ ist in dieser Form nicht belegt.** Die 43 Tabellenpositionen sind weder 43 unabhängig freie Fitparameter noch wurde das Originalmodell ausschließlich an diesen beiden Kollagenangaben kalibriert. Eine eindeutige Identifizierung der einzelnen Parameter ist durch die vorliegende Dokumentation allerdings ebenfalls nicht nachgewiesen.

## Was die 43 Tabellenpositionen tatsächlich ausweisen

Die folgende vollständige Zählung übernimmt die Beschriftung der Spalte `Reference` von S2 Table, Blatt `model_parameters`. Nummern sind die im Feld `Parameter` gedruckten Nummern, nicht Excel-Zeilennummern.

| Tabellenkennzeichnung | Anzahl | Parameternummern |
|---|---:|---|
| `Estimated from biological observations` | **22** | 14–17, 19, 22–25, 31–43 |
| `Calculated from` / `Calculated` | **9** | 4–7, 20, 26–29 |
| PMID-Verweis ohne eines dieser beiden Kennwörter | **10** | 1–3, 8–12, 18, 30 |
| Keine Referenz angegeben; MarkItDown gibt `NaN` aus | **2** | 13, 21 |
| Gesamt | **43** | 1–43 |

Die zehn bloß zitierten Positionen sind **nicht automatisch zehn direkt gemessene, unabhängig feststehende Konstanten**: Beispielsweise wird Nr. 8 im Code aus Nr. 7 durch Division durch 3,5 gebildet. Die Rezeptorparameter Nr. 1–3 werden durch Halbzeit-/Ratenumrechnung übernommen. Literaturbezug bedeutet weder Fehlerfreiheit noch bekannte Unsicherheitsgrenzen.

Der Haupttext, Abschnitt *Calibration and parameters estimation* (`sec026`), nennt dagegen **13 direkt aus Literatur, neun berechnete und 22 empirisch geschätzte Parameter**. Diese Zahlen summieren sich zu **44**, nicht 43. Die Differenz zur Tabelle ist mit den geprüften Quellen nicht eindeutig aufgelöst; insbesondere dürfen die zwei fehlenden Tabellenreferenzen nicht stillschweigend zu Literaturwerten erklärt werden. Die Tabellenzählung und die Textbehauptung bleiben getrennt.

## Empirisch geschätzt ist nicht gleich unabhängig frei

Im unveränderten Quellcode sind **acht der 22 empirisch bezeichneten Tabellenpositionen algebraisch an andere Parameter gekoppelt**:

| Tabellenpositionen | Kopplung im Default | Fundstelle in `.ka` |
|---|---|---|
| 17 | react_MFB-Halbwertszeit gleich MFB-Halbwertszeit Nr. 16 | Zeile 112 |
| 23–25 | Drei Verdopplungszeiten aus aHSC-Verdopplungszeit Nr. 22; Faktoren 1/3,5 beziehungsweise 2 | Zeilen 89, 109–110 |
| 35–38 | Vier TGFβ1-abhängige Kollagenproduktionswerte aus den jeweiligen Grundproduktionen Nr. 31–34; Faktoren 10 beziehungsweise 2 | Zeilen 159–162 |

Unter Beibehaltung dieser Kopplungen verbleiben innerhalb der empirisch markierten Gruppe **14 separat gesetzte Grundgrößen**: fünf für Zelldynamik (Nr. 14, 15, 16, 19, 22) und neun für Kollagen (Nr. 31–34, 39–43). Die vier Kollagensynthese-Eingaben stehen separat als `_py`-Werte in Zeilen 143–147; Abbauquantum und vier Umbauzeiten in Zeilen 150 und 166–169. Trotz numerischer Verhältnisse der Defaults sind die vier `_py`-Eingaben im Code nicht alle an einen einzigen Syntheseparameter gebunden.

**14 ist eine bedingte Code-Abhängigkeitszählung, kein statistischer Identifizierbarkeitsrang und keine nachgewiesene Zahl ursprünglich gleichzeitig gefitteter Parameter.** Werden abgeleitete Größen separat übersteuert, bisher feste Faktoren freigegeben oder Bindungen geändert, ändert sich die Parametrisierung. Auch innerhalb der übrigen Tabellenkategorien gibt es Kopplungen; die Zählung 14 beschreibt deshalb nicht die gesamten Freiheitsgrade des Modells.

Fünf Tabellenpositionen sind im gewählten Reproduktionsprotokoll als Input-/Anfangsgrößen festzuhalten: Stimulationsamplitude, Pulsanzahl und Abstand (Nr. 10–12), initiale Zellzahl (Nr. 13) und initialer Kollagenwert (Nr. 30). Diese Einordnung **überlappt** mit den Quellenkategorien oben und ist keine zusätzliche Summengruppe. Nr. 21, die apoptotische/seneszente Halbzeit, hat keine Tabellenreferenz; der Source-Kommentar in Zeile 91 beschreibt eine Ableitung aus einer angenommenen 24-Stunden-Dauer. Deren belastbare empirische Herkunft bleibt offen. Bei einer reinen Reproduktion aller fixierten Defaults werden überhaupt keine Parameter neu geschätzt.

Die bekannten Abweichungen zwischen Tabelle und Source bei Nr. 25, bei Kollagen-Skalierungen und Zeitfaktoren bleiben bestehen; siehe [Quellenaudit](selection-and-data.md). Ohne Entscheidung, welche genaue Modellversion geprüft wird, ist schon der Gegenstand einer späteren Identifizierbarkeitsanalyse nicht eindeutig.

## Welche Daten wurden laut Artikel verwendet?

`sec026` beschreibt eine sequenzielle, blockweise Kalibrierung anhand vieler Simulationen und abschließender visueller Kontrolle: zunächst kollagenproduzierende Zellen, dann react_MFB-Inaktivierung, qHSC/iHSC-Dynamik und schließlich Kollagen. Parameterabhängigkeiten werden ausdrücklich als Schwierigkeit benannt.

Die ungefähr 12- und 14-fachen COL1-Werte nach einem beziehungsweise zwei Monaten sind nur ein Teil davon (`sec031`). Derselbe Abschnitt nennt Produktionsverhältnisse sowie schnellen Rückgang im ersten und Annäherung an den Ausgangswert um sechs Monate nach Reizentzug. Weitere Abschnitte verwenden Aktivierungszeiten und Proliferationsverhältnisse (`sec027`), Zellakkumulation und Verschwinden nach Reizentzug (`sec030`), Inaktivierung (`sec032`) sowie qHSC/iHSC-Verhältnis und Zellzahl nach einem beziehungsweise sechs Monaten (`sec033`). Ein Teil dieser Informationen ist qualitativ oder eine Modellannahme; daraus folgt kein vollständiger, gewichteter Beobachtungsdatensatz.

Die Stimulations-Sensitivitätsanalyse in Fig. 3 / `sec005` variiert Inputhöhe, Zahl und Abstand. Sie zeigt Modellantworten, aber keine eindeutige Schätzbarkeit sämtlicher innerer Raten. In den geprüften Kalibrierabschnitten und S2 Table sind kein vollständiger Schätzverlust mit Messfehlern, keine parameterweisen Konfidenzintervalle und keine formale strukturelle oder praktische Identifizierbarkeitsanalyse dokumentiert.

## Zulässige Schlussfolgerung

Eine quellengerechte Aussage lautet:

> S2 Table enthält 43 Positionen, davon 22 ausdrücklich empirisch geschätzte. Mehrere sind im Code gekoppelt. Die beiden ungefähren COL1-Fold-Changes allein belegen keine eindeutige gemeinsame Schätzung der separat veränderlichen Synthese-, Abbau- und Umbaueingaben. Welche Einzelparameter oder Parameterkombinationen mit einem definierten Datensatz identifizierbar wären, wurde hier nicht untersucht. Das Original verwendet zusätzliche Zell- und Regressionsbeobachtungen sowie Modellannahmen.

Weder „alle 43 sind frei“ noch „alle 22 sind unabhängig“ noch „jeder einzelne Parameter ist nachweislich nicht identifizierbar“ ist aus dieser Prüfung ableitbar. Auch neun separat gesetzte Kollagengrundgrößen gegenüber zwei skalaren Zielen sind **keine durchgeführte formale Analyse**. Für einen späteren Fit müssen Modellversion, tatsächlich freigegebene Parameter und Bindungen, Messgröße, konkrete Beobachtungen und Fehlermodell vorab feststehen. Biologisch plausible Grenzen oder statistische Unsicherheitsintervalle werden hier nicht erfunden.

## Fundstellen

- [Bouguéon et al. 2024, DOI 10.1371/journal.pcbi.1011858](https://doi.org/10.1371/journal.pcbi.1011858): lokal `work/reference-repos/bougueon2024.xml`, Abschnitte `sec005`, `sec026`–`sec033`.
- S2 Table: lokal `work/reference-audit/S2Table.xlsx`, mit Headroom MarkItDown gelesen; vollständige Spaltenklassifikation oben.
- [Original-Repository](https://github.com/MBougueon/HSC_model_Kappa), Commit `773a84e65b514b969db20c57b6bf0ba97c1d32fb`, lokal `work/reference-repos/HSC_model_Kappa/reactMFB-with-inactivation.ka`; relevante Zeilen 72–125, 143–182. Keine Änderung des Originals.
