import Foundation

public enum SimulationError: Error, LocalizedError, Equatable, Sendable {
    case invalidInput(String)
    case resourceLimit
    case unstableState

    public var errorDescription: String? {
        switch self {
        case .invalidInput(let field): "Ungültige Simulationseingabe: \(field)"
        case .resourceLimit: "Ressourcengrenze überschritten; Dauer, Auflösung oder Anzahl reduzieren."
        case .unstableState: "Numerische Instabilität: Zustand außerhalb des zulässigen Bereichs."
        }
    }
}

public struct LiverState: Codable, Equatable, Sendable {
    public var hepatocytes: Double
    public var inflammation: Double
    public var stellate: Double
    public var fibrosis: Double

    public init(hepatocytes: Double, inflammation: Double, stellate: Double, fibrosis: Double) {
        self.hepatocytes = hepatocytes
        self.inflammation = inflammation
        self.stellate = stellate
        self.fibrosis = fibrosis
    }

    public static let synthetic = LiverState(hepatocytes: 0.78, inflammation: 0.38, stellate: 0.32, fibrosis: 0.35)

    public func validate() throws {
        for value in [hepatocytes, inflammation, stellate, fibrosis] {
            guard value.isFinite, (0...1).contains(value) else {
                throw SimulationError.invalidInput("Zustand muss endlich und zwischen 0 und 1 sein")
            }
        }
    }
}

public enum ModelParameter: String, CaseIterable, Codable, Sendable {
    case injuryRate, regenerationRate, inflammationRate, resolutionRate
    case activationRate, deactivationRate, depositionRate, regressionRate
}

public struct ModelParameters: Codable, Equatable, Sendable {
    // Heuristic rates in day^-1; no human-data calibration. See Docs/02-ScientificModel.md.
    public var injuryRate = 0.012
    public var regenerationRate = 0.035
    public var inflammationRate = 0.040
    public var resolutionRate = 0.025
    public var activationRate = 0.025
    public var deactivationRate = 0.012
    public var depositionRate = 0.008
    public var regressionRate = 0.003

    public init() {}

    public subscript(parameter: ModelParameter) -> Double {
        get {
            switch parameter {
            case .injuryRate: injuryRate
            case .regenerationRate: regenerationRate
            case .inflammationRate: inflammationRate
            case .resolutionRate: resolutionRate
            case .activationRate: activationRate
            case .deactivationRate: deactivationRate
            case .depositionRate: depositionRate
            case .regressionRate: regressionRate
            }
        }
        set {
            switch parameter {
            case .injuryRate: injuryRate = newValue
            case .regenerationRate: regenerationRate = newValue
            case .inflammationRate: inflammationRate = newValue
            case .resolutionRate: resolutionRate = newValue
            case .activationRate: activationRate = newValue
            case .deactivationRate: deactivationRate = newValue
            case .depositionRate: depositionRate = newValue
            case .regressionRate: regressionRate = newValue
            }
        }
    }
}

public struct Scenario: Codable, Equatable, Sendable {
    public var name: String
    public var injuryMultiplier: Double
    public var inflammationMultiplier: Double
    public var antifibroticEffect: Double
    public var regenerationMultiplier: Double
    public var startDay: Double

    public init(name: String = "Kontrolle", injuryMultiplier: Double = 1,
                inflammationMultiplier: Double = 1, antifibroticEffect: Double = 0,
                regenerationMultiplier: Double = 1, startDay: Double = 0) {
        self.name = name
        self.injuryMultiplier = injuryMultiplier
        self.inflammationMultiplier = inflammationMultiplier
        self.antifibroticEffect = antifibroticEffect
        self.regenerationMultiplier = regenerationMultiplier
        self.startDay = startDay
    }

    public static let control = Scenario()
}

public struct SimulationConfiguration: Codable, Equatable, Sendable {
    public var initial: LiverState
    public var parameters: ModelParameters
    public var scenario: Scenario
    public var durationDays: Double
    public var stepDays: Double
    public var sampleEveryDays: Double
    public var seed: UInt64

    public init(initial: LiverState = .synthetic, parameters: ModelParameters = .init(),
                scenario: Scenario = .control, durationDays: Double = 365,
                stepDays: Double = 0.25, sampleEveryDays: Double = 5, seed: UInt64 = 42) {
        self.initial = initial
        self.parameters = parameters
        self.scenario = scenario
        self.durationDays = durationDays
        self.stepDays = stepDays
        self.sampleEveryDays = sampleEveryDays
        self.seed = seed
    }

    public func validate() throws {
        try initial.validate()
        for parameter in ModelParameter.allCases {
            let value = parameters[parameter]
            guard value.isFinite, (0...1).contains(value) else {
                throw SimulationError.invalidInput(parameter.rawValue + " muss in 0...1 / Tag liegen")
            }
        }
        guard !scenario.name.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty,
              scenario.name.utf8.count <= 200 else { throw SimulationError.invalidInput("Szenarioname") }
        for value in [scenario.injuryMultiplier, scenario.inflammationMultiplier, scenario.regenerationMultiplier] {
            guard value.isFinite, (0...4).contains(value) else {
                throw SimulationError.invalidInput("Interventionsmultiplikator muss in 0...4 liegen")
            }
        }
        guard scenario.antifibroticEffect.isFinite, (0...1).contains(scenario.antifibroticEffect),
              scenario.startDay.isFinite, (0...3650).contains(scenario.startDay) else {
            throw SimulationError.invalidInput("Interventionsbeginn oder antifibrotischer Effekt")
        }
        guard durationDays.isFinite, (0...3650).contains(durationDays),
              stepDays.isFinite, stepDays > 0, stepDays <= 1,
              sampleEveryDays.isFinite, sampleEveryDays > 0 else {
            throw SimulationError.invalidInput("Dauer, Schrittweite oder Ausgabeintervall")
        }
        guard estimatedWork <= 200_000, ceil(durationDays / sampleEveryDays) + 1 <= 20_000 else {
            throw SimulationError.resourceLimit
        }
    }

    var integrationStep: Double {
        let p = parameters
        let u = max(1, scenario.injuryMultiplier)
        let v = max(1, scenario.inflammationMultiplier)
        let g = max(1, scenario.regenerationMultiplier)
        let rate = max(1, p.injuryRate * u + p.regenerationRate * g,
                       p.inflammationRate * v * u + p.resolutionRate,
                       p.activationRate + p.deactivationRate, p.depositionRate + p.regressionRate)
        return min(stepDays, 0.1 / rate)
    }

    var estimatedWork: Double {
        ceil(durationDays / integrationStep) + ceil(durationDays / sampleEveryDays) + 2
    }
}

public struct SimulationSample: Codable, Equatable, Sendable {
    public var day: Double
    public var state: LiverState

    public init(day: Double, state: LiverState) { self.day = day; self.state = state }

    public var reserve: Double { state.hepatocytes * (1 - 0.6 * state.fibrosis) }
    public var portalResistance: Double { 1 + 4 * state.fibrosis + 1.5 * state.stellate }
    public var alt: Double { 20 + 300 * state.inflammation * state.hepatocytes }
    public var bilirubin: Double { 0.6 + 4 * pow(1 - reserve, 2) }
    public var albumin: Double { 4.5 - 2 * (1 - reserve) }
    public var inr: Double { 1 + 1.5 * pow(1 - reserve, 2) }
}

public struct SimulationRun: Codable, Equatable, Sendable, Identifiable {
    public var id: UUID
    public var createdAt: Date
    public var modelVersion: String
    public var configuration: SimulationConfiguration
    public var samples: [SimulationSample]

    public init(id: UUID = UUID(), createdAt: Date = Date(), modelVersion: String = LiverSimulator.modelVersion,
                configuration: SimulationConfiguration, samples: [SimulationSample]) {
        self.id = id
        self.createdAt = createdAt
        self.modelVersion = modelVersion
        self.configuration = configuration
        self.samples = samples
    }
}
