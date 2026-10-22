import Foundation
import HepatoCore
import HepatoStorage

@main
struct HepatoCLI {
    static func main() async throws {
        let arguments = CommandLine.arguments
        guard arguments.count == 2 else {
            print("Usage: hepatosim <output-directory>\nCreates synthetic runs, SQLite, JSON, CSV and a reproducibility check.")
            return
        }
        let directory = URL(fileURLWithPath: arguments[1], isDirectory: true)
        try FileManager.default.createDirectory(at: directory, withIntermediateDirectories: true,
                                               attributes: [.posixPermissions: 0o700])
        let configuration = SimulationConfiguration(scenario: Scenario(
            name: "Hypothetischer Entzug", injuryMultiplier: 0.35, inflammationMultiplier: 0.7,
            antifibroticEffect: 0.35, regenerationMultiplier: 1.2, startDay: 60))
        let run = try LiverSimulator.run(configuration)
        var reference = configuration
        reference.scenario = .control
        let control = try LiverSimulator.run(reference)
        let repeatRun = try LiverSimulator.run(configuration)
        guard run.samples == repeatRun.samples else { throw CheckFailure.failed("Deterministic replay failed") }
        let store = try RunStore(url: directory.appendingPathComponent("research.sqlite"))
        try await store.save(run)
        try await store.save(control)
        let loaded = try await store.runs()
        guard loaded.contains(run), loaded.contains(control) else { throw CheckFailure.failed("SQLite roundtrip failed") }
        let json = try RunExchange.encodeJSON(run)
        guard try RunExchange.decodeJSON(json) == run else { throw CheckFailure.failed("JSON roundtrip failed") }
        try json.write(to: directory.appendingPathComponent("scenario.json"), options: .atomic)
        try RunExchange.encodeJSON(control).write(to: directory.appendingPathComponent("control.json"), options: .atomic)
        try RunExchange.exportCSV(run).write(to: directory.appendingPathComponent("scenario.csv"), options: .atomic)
        let ensemble = try ResearchAnalysis.ensemble(configuration, count: 32)
        let sensitivity = try ResearchAnalysis.sensitivity(configuration, parameter: .depositionRate)
        let sweep = try ResearchAnalysis.sweep(configuration, parameter: .depositionRate, values: [0.001, 0.003, 0.006])
        let encoder = JSONEncoder()
        encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
        try encoder.encode(ensemble).write(to: directory.appendingPathComponent("ensemble.json"), options: .atomic)
        try encoder.encode(sweep).write(to: directory.appendingPathComponent("sweep.json"), options: .atomic)
        print("PASS: deterministic replay, SQLite roundtrip, JSON roundtrip")
        print("Model: \(run.modelVersion); samples: \(run.samples.count); seed: \(configuration.seed)")
        print("Synthetic sensitivity (depositionRate): \(sensitivity.derivative)")
        print("Parameter spread: \(ensemble.count) time points, 32 members; no clinical confidence interval")
        print("Outputs: \(directory.path)")
    }

    enum CheckFailure: Error { case failed(String) }
}
