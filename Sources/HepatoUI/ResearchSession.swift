import Foundation
import SwiftUI
import UniformTypeIdentifiers
import HepatoCore
import HepatoStorage

@MainActor
final class ResearchSession: ObservableObject {
    @Published var configuration = SimulationConfiguration(
        scenario: Scenario(name: "Experiment A", injuryMultiplier: 0.35,
                           inflammationMultiplier: 0.7, antifibroticEffect: 0.35,
                           regenerationMultiplier: 1.2, startDay: 60))
    @Published var runs: [SimulationRun] = []
    @Published var selected: SimulationRun?
    @Published var control: SimulationRun?
    @Published var ensemble: [EnsemblePoint] = []
    @Published var analyzing = false
    @Published var parameterEdits = ParameterEdits()
    @Published var busy = false
    @Published var error: String?
    @Published var selectedDay = 365.0
    private var store: RunStore?
    private var initialized = false

    var sample: SimulationSample? {
        selected?.samples.min { abs($0.day - selectedDay) < abs($1.day - selectedDay) }
    }

    func open() async {
        guard !initialized else { return }
        initialized = true
        do {
            let directory = try FileManager.default.url(for: .applicationSupportDirectory,
                in: .userDomainMask, appropriateFor: nil, create: true)
                .appendingPathComponent("HepatoSimResearch", isDirectory: true)
            store = try RunStore(url: directory.appendingPathComponent("research.sqlite"))
            try await refresh()
            if let latest = runs.first { select(latest) }
            else { await simulate() }
        } catch { self.error = error.localizedDescription }
    }

    func simulate() async {
        guard parameterEdits.invalid.isEmpty else {
            error = "Ungültige Zahlenfelder korrigieren: " + parameterEdits.invalid.sorted().joined(separator: ", ")
            return
        }
        guard !busy, let store else { return }
        busy = true
        defer { busy = false }
        let input = configuration
        do {
            let pair = try await Task.detached(priority: .userInitiated) {
                var reference = input
                reference.scenario = .control
                let baseline = try LiverSimulator.run(reference)
                return (try LiverSimulator.run(input), baseline)
            }.value
            try await store.save(pair.1)
            try await store.save(pair.0)
            selected = pair.0
            control = pair.1
            ensemble = []
            selectedDay = input.durationDays
            try await refresh()
        } catch { self.error = error.localizedDescription }
    }

    func select(_ run: SimulationRun) {
        parameterEdits = ParameterEdits()
        selected = run
        var reference = run.configuration
        reference.scenario = .control
        control = run.configuration.scenario == .control ? nil : runs.first {
            $0.id != run.id && $0.modelVersion == run.modelVersion && $0.configuration == reference
        }
        ensemble = []
        selectedDay = run.configuration.durationDays
        // A saved run is displayed as recorded; editing starts an explicit new run.
        if run.modelVersion == LiverSimulator.modelVersion { configuration = run.configuration }
    }

    func applyALDCessation() {
        parameterEdits = ParameterEdits()
        configuration.scenario = Scenario(name: "ALD: Wegfall modellierter Schädigung",
            injuryMultiplier: 0, inflammationMultiplier: 1, antifibroticEffect: 0,
            regenerationMultiplier: 1, startDay: 60)
    }

    func analyzeSpread() async {
        guard let run = selected, !busy, !analyzing, run.modelVersion == LiverSimulator.modelVersion else { return }
        analyzing = true
        defer { analyzing = false }
        do {
            let result = try await Task.detached(priority: .userInitiated) {
                try ResearchAnalysis.ensemble(run.configuration, count: 64, relativeSpread: 0.2)
            }.value
            if selected?.id == run.id { ensemble = result }
        } catch { self.error = error.localizedDescription }
    }

    func importRun(_ url: URL) async {
        guard let store, !busy else { return }
        busy = true
        defer { busy = false }
        let access = url.startAccessingSecurityScopedResource()
        defer { if access { url.stopAccessingSecurityScopedResource() } }
        do {
            let run = try await Task.detached(priority: .userInitiated) {
                let file = try FileHandle(forReadingFrom: url)
                defer { try? file.close() }
                let bytes = try file.read(upToCount: RunExchange.maximumBytes + 1) ?? Data()
                guard bytes.count <= RunExchange.maximumBytes else { throw CocoaError(.fileReadTooLarge) }
                return try RunExchange.decodeJSON(bytes)
            }.value
            try await store.save(run)
            try await refresh()
            select(run)
        } catch { self.error = error.localizedDescription }
    }

    private func refresh() async throws {
        guard let store else { return }
        runs = try await store.runs().sorted { $0.createdAt > $1.createdAt }
    }
}

struct ResearchDocument: FileDocument {
    static var readableContentTypes: [UTType] { [.json, .commaSeparatedText, .plainText] }
    var data: Data
    init(data: Data) { self.data = data }
    init(configuration: ReadConfiguration) throws {
        guard let bytes = configuration.file.regularFileContents else { throw CocoaError(.fileReadCorruptFile) }
        data = bytes
    }
    func fileWrapper(configuration: WriteConfiguration) throws -> FileWrapper {
        FileWrapper(regularFileWithContents: data)
    }
}

enum ResearchReport {
    static func markdown(_ run: SimulationRun) -> String {
        let config = run.configuration
        let last = run.samples.last
        return """
        # HepatoSim Research — synthetischer Forschungsbericht

        **Nicht medizinisch validiert. Keine individuelle Prognose oder Therapieempfehlung.**

        - Lauf: \(run.id.uuidString)
        - Erstellt: \(run.createdAt.ISO8601Format())
        - Modell: \(run.modelVersion)
        - Szenario: \(config.scenario.name)
        - Horizont: \(config.durationDays) Modelltage
        - Maximale Integrationsschrittweite: \(config.stepDays) Tage; Ausgabeintervall: \(config.sampleEveryDays) Tage
        - Seed: \(config.seed) (ODE deterministisch; Seed für Parameter-Ensembles)
        - Fibroseindex am Ende: \(last?.state.fibrosis.formatted(.number.precision(.fractionLength(4))) ?? "–")
        - Reserveindex am Ende: \(last?.reserve.formatted(.number.precision(.fractionLength(4))) ?? "–")

        Alle Zustandsgrößen sind dimensionslose Modellindizes. Der Fibroseindex ist kein
        METAVIR-Stadium. Der Widerstandsindex ist kein HVPG. Laborausgaben sind unkalibrierte
        Beobachtungsfunktionen. Interventionen beschreiben hypothetische Parameteränderungen.
        Es werden keine Dekompensationsereignisse oder Überlebenswahrscheinlichkeiten geschätzt.

        ## Reproduzierbarkeit

        Der JSON-Export enthält Anfangszustand, sämtliche Parameter, Szenario, Zeitraster,
        Modellversion und Samples. Diesen Bericht zusammen mit dem JSON-Lauf archivieren.
        Modellgleichungen und Quellen: Docs/02-ScientificModel.md im Quellprojekt.

        ## Validierungsstand

        Software- und Numeriktests prüfen die Implementierung. Sie belegen keine biologische
        oder klinische Vorhersagegüte. Es wurden keine echten Patientendaten zur Kalibrierung verwendet.

        \(evidenceContext())
        """
    }

    private static func evidenceContext() -> String {
        do {
            let catalog = try EvidenceCatalog.loadBundled()
            return "## Publizierter ALD-Evidenzkontext\n\nStand: \(catalog.retrievedAt). "
                + "Diese Quellen sind keine quantitative Kalibrierung des obigen ODE-Laufs. "
                + "Rekompensation und Fibroseindex sind verschiedene Endpunkte. Kohorten werden nicht gepoolt.\n\n"
                + catalog.records.map { record in
                    "### \(record.title) (\(record.year))\n\n[Originalquelle](\(record.url)), DOI \(record.doi).\n\n"
                    + record.findings.map { "- \($0.endpoint): \($0.summary) \($0.followUp)" }.joined(separator: "\n")
                    + "\n\nModellbezug: \(record.parameterImplication)\n\n"
                }.joined()
        } catch {
            return "## ALD-Evidenzkontext\n\nNicht verfügbar: \(error.localizedDescription)"
        }
    }
}
