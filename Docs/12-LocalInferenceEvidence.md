# Local inference evidence correction, 22 October 2026

The prepared driver previously changed `inference_verified` to true when a model appeared loaded alongside a local runner with a model blob. This could occur even if Goose subsequently failed. A process/loading observation does not by itself demonstrate that the selected model generated the requested answer.

A new regression case exercised both zero and nonzero mocked Goose exit codes. Before the fix both cases failed the requirement that inference must remain unverified. After the fix all four local-worker tests passed (0.029 seconds). APIs, process creation, executable-version reads and time were mocked: no local inference, download, provider change or cloud request occurred.

The driver now records the observation separately and leaves `inference_verified` false. A successful exit is explicitly pending review. Verification requires inspecting the selected model's native runner relationship and the actual generated output; a reviewed result belongs in a separate review record, preserving the raw audit. This change fixes the evidence label; it does not satisfy the still-pending requirement to execute and review a real local task.

The full 90-test public-snapshot result remains a historical claim about commit29e16e8a3dc92c2b3d985913dd0fa276ef2f5195. This correction has four focused local-worker tests; no new full suite, KaSim simulation or Swift build is claimed. The publication manifest is explicitly scoped to its original export commit so later source changes do not masquerade as matching that old snapshot's hashes.

## Deutsch

Der vorbereitete Treiber konnte einen geladenen Runner bereits als bestätigte Inferenz markieren, auch bei anschließend fehlgeschlagenem Goose-Prozess. Zwei negative Regressionsteilfälle machten den Fehler sichtbar. Nach der Korrektur bestanden alle vier lokalen Worker-Tests. Diese Tests verwenden ausschließlich Mocks und belegen keine reale Inferenz.

Runnerbeobachtung und Inferenznachweis sind jetzt getrennt. Der Rohbericht bleibt unbestätigt, bis Modell-Runner-Zuordnung und tatsächlich erzeugte Antwort geprüft wurden. Die Ressourcenblockade für den echten lokalen Auftrag bleibt bestehen. Keine neuen medizinischen oder biologischen Aussagen entstehen daraus.
