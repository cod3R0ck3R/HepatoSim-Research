import SwiftUI
import Charts
import UniformTypeIdentifiers
import HepatoCore
import HepatoStorage

private enum Workspace: String, CaseIterable, Identifiable {
    case overview = "Übersicht", laboratories = "Laborwerte", parameters = "Parameter", evidence = "ALD-Evidenz", model = "Modellgrenzen", plugins = "Erweiterungen"
    var id: String { rawValue }
    var symbol: String {
        switch self {
        case .overview: "waveform.path.ecg"
        case .laboratories: "chart.xyaxis.line"
        case .parameters: "slider.horizontal.3"
        case .evidence: "books.vertical"
        case .model: "function"
        case .plugins: "puzzlepiece.extension"
        }
    }
}

public struct ResearchDashboard: View {
    @StateObject private var session = ResearchSession()
    @State private var workspace: Workspace = .overview
    @State private var importing = false
    @State private var exporting = false
    @State private var exportDocument = ResearchDocument(data: Data())
    @State private var exportType: UTType = .json
    @State private var exportName = "HepatoSim-Lauf"
    @State private var lab = LabMetric.alt
    @State private var timelineEdits = ParameterEdits()
    @FocusState private var focusedNumber: String?
    @Environment(\.horizontalSizeClass) private var horizontalSizeClass

    public init() {}

    public var body: some View {
        NavigationSplitView {
            sidebar
                .navigationSplitViewColumnWidth(min: 210, ideal: 245, max: 300)
        } detail: {
            ScrollViewReader { proxy in
            ScrollView {
                VStack(alignment: .leading, spacing: 24) {
                    header
                    researchNotice
                    if !session.parameterEdits.invalid.isEmpty {
                        Text("Ungültige Zahlenfelder: " + session.parameterEdits.invalid.sorted().joined(separator: ", "))
                            .font(.callout).foregroundStyle(.red)
                    }
                    switch workspace {
                    case .overview: overview
                    case .laboratories: laboratoryPanel
                    case .parameters: parameterPanel
                    case .evidence: ALDEvidenceView()
                    case .model: evidencePanel
                    case .plugins: pluginPanel
                    }
                }
                .padding(24)
                .frame(maxWidth: 1500)
                .frame(maxWidth: .infinity)
            }
            .background(Color.primary.opacity(0.025))
            .navigationTitle("HepatoSim Research")
            .onChange(of: focusedNumber) { _, field in
                if let field { proxy.scrollTo(field) }
            }
            }
        }
        .tint(.teal)
        .task { await session.open() }
        .fileImporter(isPresented: $importing, allowedContentTypes: [.json]) { result in
            switch result {
            case .success(let url): Task { await session.importRun(url) }
            case .failure(let error): session.error = error.localizedDescription
            }
        }
        .fileExporter(isPresented: $exporting, document: exportDocument,
                      contentType: exportType, defaultFilename: exportName) { result in
            if case .failure(let error) = result { session.error = error.localizedDescription }
        }
        .alert("Vorgang nicht abgeschlossen", isPresented: Binding(
            get: { session.error != nil }, set: { if !$0 { session.error = nil } })) {
                Button("OK") { session.error = nil }
            } message: { Text(session.error ?? "") }
    }

    private var sidebar: some View {
        List {
            Section {
                VStack(alignment: .leading, spacing: 7) {
                    Label("HEPATOSIM", systemImage: "waveform.path.ecg")
                        .font(.headline).tracking(2).foregroundStyle(.teal)
                    Text("Research Workspace").font(.caption).foregroundStyle(.secondary)
                }.padding(.vertical, 14)
                ForEach(Workspace.allCases) { item in
                    Button { workspace = item } label: {
                        Label(item.rawValue, systemImage: item.symbol)
                            .foregroundStyle(workspace == item ? Color.teal : Color.primary)
                            .padding(.vertical, 5)
                    }.buttonStyle(.plain)
                }
            }
            Section("Gespeicherte Läufe · \(session.runs.count)") {
                ForEach(session.runs) { run in
                    Button { session.select(run); workspace = .overview } label: {
                        VStack(alignment: .leading, spacing: 4) {
                            Text(run.configuration.scenario.name).font(.subheadline.weight(.medium))
                            Text(run.createdAt, format: .dateTime.day().month().hour().minute())
                                .font(.caption).foregroundStyle(.secondary)
                        }
                        .foregroundStyle(session.selected?.id == run.id ? Color.teal : Color.primary)
                        .padding(.vertical, 4)
                    }.buttonStyle(.plain).disabled(session.busy)
                }
            }
            Section {
                Label("Simulation: synthetisch", systemImage: "lock.shield")
                    .font(.caption).foregroundStyle(.secondary)
                Text("Modell \(LiverSimulator.modelVersion)")
                    .font(.caption.monospaced()).foregroundStyle(.secondary)
            }
        }.listStyle(.sidebar)
    }

    private var header: some View {
        ViewThatFits(in: .horizontal) {
            HStack(alignment: .top) { title; Spacer(); actions }
            VStack(alignment: .leading, spacing: 16) { title; actions }
        }
    }

    private var title: some View {
        VStack(alignment: .leading, spacing: 5) {
            Text("IN SILICO · FORSCHUNGSPROTOTYP")
                .font(.caption.weight(.semibold)).tracking(1.5).foregroundStyle(.teal)
            Text(workspace.rawValue).font(.largeTitle.weight(.semibold))
            Text("Leberdynamik untersuchen. Annahmen sichtbar machen.")
                .font(.subheadline).foregroundStyle(.secondary)
        }
    }

    private var actions: some View {
        HStack {
            Button { importing = true } label: { Label("Import", systemImage: "square.and.arrow.down") }
                .disabled(session.busy)
            Menu {
                Button("Lauf als JSON") { export(.json) }
                Button("Zeitreihe als CSV") { export(.commaSeparatedText) }
                Button("Forschungsbericht als Markdown") { export(.plainText) }
            } label: { Label("Export", systemImage: "square.and.arrow.up") }
                .disabled(session.selected == nil)
        }.controlSize(.large)
    }

    private var researchNotice: some View {
        Label {
            Text("Simulationen sind nicht medizinisch validiert. Modellierte Verläufe und Interventionseffekte sind hypothetisch. Keine individuelle Prognose.")
                .font(.callout)
        } icon: { Image(systemName: "info.circle.fill").foregroundStyle(.orange) }
            .padding(13).frame(maxWidth: .infinity, alignment: .leading)
            .background(Color.orange.opacity(0.09), in: RoundedRectangle(cornerRadius: 10))
    }

    private var overview: some View {
        VStack(alignment: .leading, spacing: 22) {
            if let sample = session.sample {
                LazyVGrid(columns: Array(repeating: GridItem(.flexible(), spacing: 14), count: horizontalSizeClass == .compact ? 2 : 4), spacing: 14) {
                    MetricCard(title: "Hepatozyten", value: sample.state.hepatocytes, detail: "normierter Zellindex", color: .teal)
                    MetricCard(title: "Fibrose", value: sample.state.fibrosis, detail: "kein klinisches Stadium", color: .purple)
                    MetricCard(title: "Funktionelle Reserve", value: sample.reserve, detail: "Modellindex · 0–1", color: .blue)
                    MetricCard(title: "Portaler Widerstand", value: sample.portalResistance, detail: "relativer Index · kein HVPG", color: .orange)
                }
            }
            ViewThatFits(in: .horizontal) {
                HStack(alignment: .top, spacing: 20) {
                    trajectoryPanel.frame(minWidth: 470)
                    scenarioPanel.frame(width: 300)
                }
                VStack(spacing: 20) { trajectoryPanel; scenarioPanel }
            }
            spreadPanel
            if let run = session.selected {
                ViewThatFits(in: .horizontal) {
                    HStack(spacing: 20) { liverPanel(run).frame(width: 280); timePanel(run) }
                    VStack(spacing: 20) { liverPanel(run); timePanel(run) }
                }
                Text("Lauf \(run.id.uuidString.prefix(8)) · Modell \(run.modelVersion) · RK4 Δt ≤ \(run.configuration.stepDays.formatted()) d · Seed \(run.configuration.seed)")
                    .font(.caption.monospaced()).foregroundStyle(.secondary).textSelection(.enabled)
            }
        }
    }

    private var trajectoryPanel: some View {
        VStack(alignment: .leading, spacing: 18) {
            HStack {
                VStack(alignment: .leading, spacing: 5) {
                    Text("Verlauf & Kontrolle").font(.title3.weight(.semibold))
                    Text("Dimensionslose Modellindizes · keine Erkrankungsstadien")
                        .font(.caption).foregroundStyle(.secondary)
                }
                Spacer()
                if session.busy { ProgressView().controlSize(.small) }
            }
            if let run = session.selected {
                Chart {
                    ForEach(run.samples.indices, id: \.self) { index in
                        let sample = run.samples[index]
                        LineMark(x: .value("Tag", sample.day), y: .value("Index", sample.state.fibrosis))
                            .foregroundStyle(by: .value("Verlauf", "Fibrose · Szenario"))
                        LineMark(x: .value("Tag", sample.day), y: .value("Index", sample.reserve))
                            .foregroundStyle(by: .value("Verlauf", "Reserve · Szenario"))
                        LineMark(x: .value("Tag", sample.day), y: .value("Index", sample.state.inflammation))
                            .foregroundStyle(by: .value("Verlauf", "Entzündung · Szenario"))
                    }
                    if let control = session.control {
                        ForEach(control.samples.indices, id: \.self) { index in
                            let sample = control.samples[index]
                            LineMark(x: .value("Tag", sample.day), y: .value("Index", sample.state.fibrosis))
                                .foregroundStyle(by: .value("Verlauf", "Fibrose · Kontrolle"))
                                .lineStyle(StrokeStyle(lineWidth: 2, dash: [5, 4]))
                        }
                    }
                    RuleMark(x: .value("Inspektion", session.selectedDay))
                        .foregroundStyle(.secondary.opacity(0.5)).lineStyle(StrokeStyle(dash: [2, 3]))
                }
                .chartForegroundStyleScale([
                    "Fibrose · Szenario": Color.purple,
                    "Reserve · Szenario": Color.teal,
                    "Entzündung · Szenario": Color.orange,
                    "Fibrose · Kontrolle": Color.gray
                ])
                .chartYScale(domain: 0...1)
                .chartXAxisLabel("Modellzeit (Tage)")
                .chartLegend(position: .bottom, alignment: .leading, spacing: 12)
                .frame(height: 280)
                .accessibilityLabel("Zeitreihen synthetischer Modellindizes. Numerische Werte über die Zeitleiste zugänglich.")
                if session.control == nil {
                    Text("Gespeicherter Einzellauf. Eine neue Berechnung erzeugt Szenario und Kontrolle gemeinsam.")
                        .font(.caption).foregroundStyle(.secondary)
                }
            } else { ContentUnavailableView("Noch kein Lauf", systemImage: "chart.xyaxis.line", description: Text("Ein synthetisches Szenario berechnen.")) }
        }.researchCard()
    }

    private var scenarioPanel: some View {
        VStack(alignment: .leading, spacing: 14) {
            Label("Szenarioeditor", systemImage: "slider.horizontal.3").font(.title3.weight(.semibold))
            Text("Hypothetische Eingriffe, keine Wirkstoff- oder Dosisangaben.")
                .font(.caption).foregroundStyle(.secondary)
            Button("ALD: Wegfall der Schädigung") { session.applyALDCessation() }
                .buttonStyle(.bordered)
                .help("Modellhypothese zur Beendigung des schädigenden Einflusses; kein aus einer Studie geschätzter Therapieeffekt.")
            Text("ALD-Vorlage: modellierten Schädigungsfaktor auf null setzen. Keine aus Studiendaten geschätzte Rekompensationswirkung.")
                .font(.caption2).foregroundStyle(.secondary)
            TextField("Szenarioname", text: $session.configuration.scenario.name)
                .textFieldStyle(.roundedBorder)
            parameterSlider("Schädigungsfaktor", value: $session.configuration.scenario.injuryMultiplier, range: 0...4)
            parameterSlider("Entzündungsfaktor", value: $session.configuration.scenario.inflammationMultiplier, range: 0...4)
            parameterSlider("Antifibrotischer Effekt", value: $session.configuration.scenario.antifibroticEffect, range: 0...1)
            parameterSlider("Regenerationsfaktor", value: $session.configuration.scenario.regenerationMultiplier, range: 0...4)
            parameterSlider("Interventionsbeginn (Tag)", value: $session.configuration.scenario.startDay, range: 0...3650)
            Button { Task { await session.simulate() } } label: {
                Label(session.busy ? "Berechnung läuft …" : "Berechnen & speichern", systemImage: "play.fill")
                    .frame(maxWidth: .infinity)
            }.buttonStyle(.borderedProminent).controlSize(.large).disabled(session.busy || !session.parameterEdits.invalid.isEmpty)
            Text("Änderungen wirken erst nach der Berechnung. Kontrolle: gleiche Anfangswerte, keine Intervention.")
                .font(.caption2).foregroundStyle(.secondary)
        }.researchCard().disabled(session.busy)
    }

    private func timePanel(_ run: SimulationRun) -> some View {
        VStack(alignment: .leading, spacing: 15) {
            HStack {
                Text("Zeitleiste").font(.title3.weight(.semibold)); Spacer()
                Text("Tag \((session.sample?.day ?? 0).formatted(.number.precision(.fractionLength(0))))")
                    .font(.title2.monospacedDigit()).foregroundStyle(.teal)
            }
            ParameterControl(label: "Modelltag", value: $session.selectedDay,
                range: 0...max(1, run.configuration.durationDays), edits: $timelineEdits,
                focusedField: $focusedNumber, fieldOrder: ["Modelltag"])
                .onChange(of: run.id) { _, _ in timelineEdits = ParameterEdits() }
            HStack { Text("0"); Spacer(); Text("\(run.configuration.durationDays.formatted()) Tage") }
                .font(.caption).foregroundStyle(.secondary)
            if let s = session.sample {
                Text("Entzündung \(s.state.inflammation.formatted(.number.precision(.fractionLength(3)))) · Sternzellaktivierung \(s.state.stellate.formatted(.number.precision(.fractionLength(3))))")
                    .font(.callout.monospacedDigit())
            }
            Text("Inspektion des nächstgelegenen gespeicherten Samples. Die Zeitskala ist eine unkalibrierte Modellannahme.")
                .font(.caption).foregroundStyle(.secondary)
        }.researchCard()
    }

    private func liverPanel(_ run: SimulationRun) -> some View {
        VStack(spacing: 8) {
            LiverGlyph().fill(LinearGradient(colors: [.teal.opacity(0.9), .purple.opacity(0.6)], startPoint: .topLeading, endPoint: .bottomTrailing))
                .overlay { LiverGlyph().stroke(.primary.opacity(0.15), lineWidth: 1) }
                .frame(width: 180, height: 100)
                .accessibilityHidden(true)
            Text("Synthetischer Leberzustand").font(.subheadline.weight(.medium))
            Text("Schematisch · kein anatomisches Modell").font(.caption2).foregroundStyle(.secondary)
        }.frame(maxWidth: .infinity).researchCard()
    }

    private var laboratoryPanel: some View {
        VStack(alignment: .leading, spacing: 18) {
            Text("Unkalibrierte Beobachtungsfunktionen").font(.title2.weight(.semibold))
            Text("Diese Laborwerte werden aus dem Modellzustand abgeleitet. Sie sind weder Messungen noch patientenbezogene Vorhersagen. Referenzbereiche werden deshalb nicht eingeblendet.")
                .foregroundStyle(.secondary)
            Picker("Laborparameter", selection: $lab) {
                ForEach(LabMetric.allCases) { Text($0.rawValue).tag($0) }
            }.pickerStyle(.menu)
            if let run = session.selected {
                Chart(run.samples.indices, id: \.self) { index in
                    let sample = run.samples[index]
                    LineMark(x: .value("Tag", sample.day), y: .value(lab.rawValue, lab.value(sample)))
                        .foregroundStyle(.teal)
                }.frame(height: 330).chartXAxisLabel("Modellzeit (Tage)").chartYAxisLabel(lab.unit)
                Text("Weitere Laborparameter sind im synthetischen Datenmodell verfügbar, werden durch diesen Kern jedoch nicht dynamisch simuliert.")
                    .font(.caption).foregroundStyle(.secondary)
            }
        }.researchCard()
    }

    private var spreadPanel: some View {
        VStack(alignment: .leading, spacing: 14) {
            HStack {
                Text("Parameterunsicherheit untersuchen").font(.title3.weight(.semibold))
                Spacer()
                if session.analyzing { ProgressView().controlSize(.small) }
                Button("64 Varianten berechnen") { Task { await session.analyzeSpread() } }
                    .disabled(session.busy || session.analyzing || session.selected?.modelVersion != LiverSimulator.modelVersion)
            }
            Text("Unabhängige gleichverteilte Ratenvariation ±20 %. 5.–95. Perzentil des Fibroseindex. Gewählte Parameterstreuung, kein klinisches Konfidenz- oder Prognoseintervall.")
                .font(.caption).foregroundStyle(.secondary)
            if !session.ensemble.isEmpty {
                Chart(session.ensemble.indices, id: \.self) { index in
                    let point = session.ensemble[index]
                    AreaMark(x: .value("Tag", point.day), yStart: .value("5. Perzentil", point.lower), yEnd: .value("95. Perzentil", point.upper))
                        .foregroundStyle(.purple.opacity(0.18))
                    LineMark(x: .value("Tag", point.day), y: .value("Median", point.median))
                        .foregroundStyle(.purple)
                }.chartYScale(domain: 0...1).chartXAxisLabel("Modellzeit (Tage)").frame(height: 180)
            }
        }.researchCard()
    }

    private var parameterPanel: some View {
        VStack(alignment: .leading, spacing: 18) {
            Text("Parameterinspektor").font(.title2.weight(.semibold))
            Text("Alle Raten sind frei gewählte Modellparameter (d⁻¹), nicht klinisch geschätzt. Änderungen gelten für den nächsten Lauf.")
                .foregroundStyle(.secondary)
            Button("ALD-Studien und Grenzen der Parameterableitung") { workspace = .evidence }
            Text("Tab wechselt zwischen Zahlenfeldern. Dezimalkomma und Dezimalpunkt sind zulässig; keine Tausendertrennzeichen.")
                .font(.caption).foregroundStyle(.secondary)
            VStack(spacing: 18) {
                parameterSlider("Schädigung", value: $session.configuration.parameters.injuryRate, range: 0...1)
                parameterSlider("Regeneration", value: $session.configuration.parameters.regenerationRate, range: 0...1)
                parameterSlider("Entzündungsaufbau", value: $session.configuration.parameters.inflammationRate, range: 0...1)
                parameterSlider("Entzündungsauflösung", value: $session.configuration.parameters.resolutionRate, range: 0...1)
                parameterSlider("Sternzellaktivierung", value: $session.configuration.parameters.activationRate, range: 0...1)
                parameterSlider("Sternzelldeaktivierung", value: $session.configuration.parameters.deactivationRate, range: 0...1)
                parameterSlider("Kollagenablagerung", value: $session.configuration.parameters.depositionRate, range: 0...1)
                parameterSlider("Matrixrückbildung", value: $session.configuration.parameters.regressionRate, range: 0...1)
                parameterSlider("Initiale Hepatozyten", value: $session.configuration.initial.hepatocytes, range: 0...1)
                parameterSlider("Initiale Fibrose", value: $session.configuration.initial.fibrosis, range: 0...1)
                parameterSlider("Initiale Entzündung", value: $session.configuration.initial.inflammation, range: 0...1)
                parameterSlider("Initiale Sternzellaktivierung", value: $session.configuration.initial.stellate, range: 0...1)
            }
            Button("Mit diesen Parametern berechnen") { Task { await session.simulate() } }
                .buttonStyle(.borderedProminent).disabled(session.busy || !session.parameterEdits.invalid.isEmpty)
            if !session.parameterEdits.invalid.isEmpty {
                Text("Vor der Berechnung korrigieren: " + session.parameterEdits.invalid.sorted().joined(separator: ", "))
                    .font(.caption).foregroundStyle(.red)
            }
        }.researchCard().disabled(session.busy)
    }

    private var evidencePanel: some View {
        VStack(alignment: .leading, spacing: 18) {
            Text("Was das Modell aussagt").font(.title2.weight(.semibold))
            evidenceRow("Biologischer Mechanismus", "Schädigung, Entzündung, Sternzellaktivierung und Matrixumbau motivieren die Modellstruktur. Die Literatur belegt nicht diese konkreten Gleichungen.", "books.vertical", .teal)
            evidenceRow("Experimentelle Annahmen", "Vier normierte Zustände, homogene Leber, vereinfachte Rückkopplungen. Reserve, Widerstand und Laborwerte sind algebraische Beobachtungsfunktionen.", "function", .purple)
            evidenceRow("Frei gewählte Parameter", "Alle Raten, Anfangswerte und Interventionseffekte sind synthetisch. Synthetische Kalibrierung prüft nur den Algorithmus.", "slider.horizontal.3", .orange)
            evidenceRow("Klinische Validierung: keine", "Keine Zuordnung zu Child-Pugh, MELD, kompensierter oder dekompensierter Zirrhose. Keine Prognosen zu Überleben, Ereignissen oder Therapieerfolg.", "exclamationmark.shield", .red)
            Divider()
            Text("Vollständige Gleichungen, Einheiten, Quellen und Grenzen stehen in Docs/02-ScientificModel.md. Tests und Validierungsplan: Docs/05-ValidationStrategy.md.")
                .font(.callout).textSelection(.enabled)
            Link("Friedman · Hepatic stellate cells (Physiological Reviews, 2008)", destination: URL(string: "https://doi.org/10.1152/physrev.00013.2007")!)
            Link("Apple · Swift Charts", destination: URL(string: "https://developer.apple.com/documentation/charts")!)
            Divider()
            Text("KI-Hypothesen sind ein separater Datentyp. Dieser Prototyp enthält keinen verbundenen KI-Provider und sendet keine Daten an KI-Dienste.")
                .font(.caption).foregroundStyle(.secondary)
        }.researchCard()
    }

    private var pluginPanel: some View {
        VStack(alignment: .leading, spacing: 18) {
            Label("Plugin-Architektur · geplant für Phase 5", systemImage: "puzzlepiece.extension")
                .font(.title2.weight(.semibold))
            Text("Der ausführbare Slice verwendet ausschließlich den eingebauten Kern. Installation, Signaturprüfung und isolierte Plugin-Ausführung sind noch nicht implementiert.")
            evidenceRow("Native Erweiterungen", "iOS: ausschließlich mit der App signierter, vorab ausgelieferter Code. macOS: separat zu prüfende XPC-Isolation.", "shippingbox", .teal)
            evidenceRow("Serverseitige Plugins", "Geplante Ausführung mit expliziten Berechtigungen, Datenminimierung, Ressourcenlimits und versionierten Ergebnissen.", "server.rack", .blue)
            evidenceRow("Vertrauensgrenze", "Manifest, Abhängigkeiten, Signaturen, Audit und Update-Rollback sind in Docs/04-PluginSpecification.md spezifiziert.", "lock.shield", .purple)
        }.researchCard()
    }

    private func evidenceRow(_ title: String, _ detail: String, _ icon: String, _ color: Color) -> some View {
        HStack(alignment: .top, spacing: 14) {
            Image(systemName: icon).foregroundStyle(color).font(.title3).frame(width: 26)
            VStack(alignment: .leading, spacing: 5) {
                Text(title).font(.headline)
                Text(detail).foregroundStyle(.secondary).fixedSize(horizontal: false, vertical: true)
            }
        }
    }

    private func parameterSlider(_ label: String, value: Binding<Double>, range: ClosedRange<Double>) -> some View {
        ParameterControl(label: label, value: value, range: range, edits: $session.parameterEdits,
                         focusedField: $focusedNumber, fieldOrder: numberFieldOrder)
    }

    private var numberFieldOrder: [String] {
        workspace == .parameters
            ? ["Schädigung", "Regeneration", "Entzündungsaufbau", "Entzündungsauflösung", "Sternzellaktivierung", "Sternzelldeaktivierung", "Kollagenablagerung", "Matrixrückbildung", "Initiale Hepatozyten", "Initiale Fibrose", "Initiale Entzündung", "Initiale Sternzellaktivierung"]
            : ["Schädigungsfaktor", "Entzündungsfaktor", "Antifibrotischer Effekt", "Regenerationsfaktor", "Interventionsbeginn (Tag)"]
    }

    private func export(_ type: UTType) {
        guard let run = session.selected else { return }
        do {
            if type == .json { exportDocument = ResearchDocument(data: try RunExchange.encodeJSON(run)) }
            else if type == .commaSeparatedText { exportDocument = ResearchDocument(data: try RunExchange.exportCSV(run)) }
            else { exportDocument = ResearchDocument(data: Data(ResearchReport.markdown(run).utf8)) }
            exportType = type
            exportName = "HepatoSim-\(run.id.uuidString.prefix(8))" + (type == .plainText ? ".md" : "")
            exporting = true
        } catch { session.error = error.localizedDescription }
    }
}

private struct MetricCard: View {
    let title: String
    let value: Double
    let detail: String
    let color: Color
    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(title).font(.subheadline).foregroundStyle(.secondary)
            Text(value.formatted(.number.precision(.fractionLength(3))))
                .font(.system(size: 32, weight: .medium, design: .rounded).monospacedDigit()).foregroundStyle(color)
            Text(detail).font(.caption2).foregroundStyle(.secondary)
        }.frame(maxWidth: .infinity, alignment: .leading).researchCard()
            .accessibilityElement(children: .combine)
    }
}

private enum LabMetric: String, CaseIterable, Identifiable {
    case alt = "ALT", bilirubin = "Bilirubin", albumin = "Albumin", inr = "INR"
    var id: String { rawValue }
    var unit: String {
        switch self { case .alt: "U/L"; case .bilirubin: "mg/dL"; case .albumin: "g/dL"; case .inr: "dimensionslos" }
    }
    func value(_ sample: SimulationSample) -> Double {
        switch self { case .alt: sample.alt; case .bilirubin: sample.bilirubin; case .albumin: sample.albumin; case .inr: sample.inr }
    }
}

private struct LiverGlyph: Shape {
    func path(in rect: CGRect) -> Path {
        var p = Path()
        p.move(to: CGPoint(x: 0.06, y: 0.38))
        p.addCurve(to: CGPoint(x: 0.70, y: 0.12), control1: CGPoint(x: 0.16, y: 0.04), control2: CGPoint(x: 0.42, y: 0.10))
        p.addCurve(to: CGPoint(x: 0.96, y: 0.33), control1: CGPoint(x: 0.83, y: 0.10), control2: CGPoint(x: 0.98, y: 0.20))
        p.addCurve(to: CGPoint(x: 0.60, y: 0.66), control1: CGPoint(x: 0.92, y: 0.53), control2: CGPoint(x: 0.73, y: 0.51))
        p.addCurve(to: CGPoint(x: 0.12, y: 0.91), control1: CGPoint(x: 0.39, y: 0.91), control2: CGPoint(x: 0.14, y: 1.04))
        p.addCurve(to: CGPoint(x: 0.06, y: 0.38), control1: CGPoint(x: 0.03, y: 0.76), control2: CGPoint(x: 0.01, y: 0.52))
        p.closeSubpath()
        return p.applying(CGAffineTransform(scaleX: rect.width, y: rect.height))
    }
}

private extension View {
    func researchCard() -> some View {
        padding(20)
            .background(.background, in: RoundedRectangle(cornerRadius: 14))
            .overlay { RoundedRectangle(cornerRadius: 14).stroke(.primary.opacity(0.07), lineWidth: 1) }
    }
}
