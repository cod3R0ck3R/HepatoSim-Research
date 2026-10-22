# Synthetische Beispiele

Erzeugt mit Modell 0.1.0, Seed 42, 365 Modelltagen und maximaler RK4-Schrittweite 0.25 d.

- `scenario.json`: vollständig reproduzierbarer Lauf mit hypothetischer Intervention ab Tag 60.
- `control.json`: gleiche Anfangsbedingungen und Raten ohne Intervention.
- `scenario.csv`: Ergebnistabelle mit expliziten Einheiten und Proxy-Bezeichnungen; keine verlustfreie Laufdatei.
- `ensemble.json`: 5./50./95. Perzentil des Fibroseindex aus 32 Parametersätzen mit ±20 % gleichverteilter Ratenvariation.
- `sweep.json`: Variation der Kollagenablagerungsrate über 0.001, 0.003 und 0.006 d⁻¹.

JSON-Läufe lassen sich über den Importdialog der App einlesen. Ein erneuter Import derselben UUID wird zurückgewiesen. Alle Daten sind synthetisch. Kein klinisches Unsicherheitsintervall, keine Patientendaten und keine validierte Prognose.
