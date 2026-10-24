# macOS 0.1.0-alpha.1 release verification

24 October 2026. Maintainer: **Johnnie 4 free**.

The existing native macOS app compiled in Release configuration (Xcode build exit 0, 79.07 seconds). A CoreSimulator version warning was emitted, but the native macOS build completed; iPhone distribution was not tested. App/package sources match the recorded source commit. No application behavior was changed for this release.

The final executable contains arm64 and x86_64 slices. Its debug/local symbols were removed to avoid publishing local build paths, then it was ad-hoc signed again. Strict recursive signature verification passed. The final ten-file bundle passed checks for local home paths, former personal attribution and known credential patterns; these checks are not a proof of absence of every possible secret. Source files, compiled resources and the publication allowlist were also reviewed. No user database, research input table or correspondence is bundled.

The final packaged app was launched on the Apple Silicon Mac and its actual executable path verified. Its dashboard, research limitations and editable parameter fields were observed. No new simulation was started, and no full GUI, Intel-runtime, downloaded-quarantine or iPhone test is claimed. The archive checksum is in the release asset and [machine-readable verification](../Research/Release/package-verification.json).

**Distribution limits:** macOS 14 or later; universal executable, only Apple Silicon launch checked. Ad-hoc signed, **not Apple-notarized**. Gatekeeper may warn or block a downloaded copy; build from reviewed source if the packaged preview is unsuitable. This is an experimental research prototype, with hypothetical simulations and no medical validation or treatment recommendations. Existing code licensing remains unchanged.

The initial packaging architecture-check command failed because the installed tool rejected its verification syntax. The final check instead reads the actual architecture list and asserts both slices; previous failed attempts were preserved locally. Earlier debug-path-containing packages were not uploaded.

## Deutsch

Der vorhandene native macOS-Code wurde als Release erfolgreich gebaut (Exit 0, 79,07 Sekunden). Eine CoreSimulator-Versionswarnung verhinderte den macOS-Build nicht; die iPhone-Verteilung wurde nicht geprüft. Die App-Quellen entsprechen dem dokumentierten Commit. Das App-Verhalten wurde nicht verändert.

Die endgültige Datei enthält arm64 und x86_64. Debug- und lokale Symbole mit Rechnerpfaden wurden entfernt, anschließend wurde die App erneut ad-hoc signiert. Die strenge Signaturprüfung bestand. Das Paket mit zehn Dateien wurde auf lokale Benutzerpfade, frühere persönliche Namensangaben und bekannte Zugangsdatenmuster geprüft; diese Suche garantiert nicht die Abwesenheit jedes denkbaren Geheimnisses. Quellcode, eingebundene Ressourcen und Veröffentlichungsauswahl wurden zusätzlich geprüft. Keine Nutzerdatenbank, Eingangsmesstabelle oder Korrespondenz enthalten.

Die endgültige App wurde auf Apple Silicon gestartet; der tatsächliche Programmpfad wurde bestätigt. Dashboard, Forschungshinweise und Parametertextfelder waren sichtbar. Keine neue Simulation, kein vollständiger GUI-Test und kein Test auf Intel, mit heruntergeladener Quarantänemarkierung oder auf dem iPhone. Prüfsummen und maschinenlesbare Verifikation sind verlinkt.

**Grenzen:** macOS ab Version 14; universelle ausführbare Datei, Start nur auf Apple Silicon geprüft. Ad-hoc signiert, **nicht von Apple notarisiert**. Gatekeeper kann bei einem Download warnen oder blockieren; alternativ aus geprüftem Quellcode bauen. Experimenteller Forschungsprototyp ohne medizinische Validierung und ohne individuelle Behandlungsempfehlungen. Der Lizenzstatus bleibt unverändert. Fehlgeschlagene Verpackungsversuche sind lokal erhalten; frühere Pakete mit Rechnerpfaden wurden nicht hochgeladen. Die endgültige Architekturprüfung liest und prüft beide vorhandenen Architekturen.
