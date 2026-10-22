import Foundation

public struct EnsemblePoint: Codable, Equatable, Sendable {
    public let day: Double
    public let lower: Double
    public let median: Double
    public let upper: Double
}

public struct SensitivityResult: Codable, Equatable, Sendable {
    public let parameter: ModelParameter
    public let derivative: Double
    public let elasticity: Double?
}

public struct SweepPoint: Codable, Equatable, Sendable {
    public let value: Double
    public let finalFibrosis: Double
    public let finalReserve: Double
}

public struct SyntheticObservation: Codable, Equatable, Sendable {
    public let day: Double
    public let fibrosis: Double
    public init(day: Double, fibrosis: Double) { self.day = day; self.fibrosis = fibrosis }
}

public struct CalibrationResult: Codable, Equatable, Sendable {
    public let parameter: ModelParameter
    public let value: Double
    public let meanSquaredError: Double
    public let candidateCount: Int
}

/// SplitMix64: fixed integer algorithm; independent of Swift's randomized hashing.
public struct SeededGenerator: RandomNumberGenerator, Sendable {
    private var state: UInt64
    public init(seed: UInt64) { state = seed }
    public mutating func next() -> UInt64 {
        state &+= 0x9E3779B97F4A7C15
        var z = state
        z = (z ^ (z >> 30)) &* 0xBF58476D1CE4E5B9
        z = (z ^ (z >> 27)) &* 0x94D049BB133111EB
        return z ^ (z >> 31)
    }
    public mutating func unitInterval() -> Double { Double(next() >> 11) * 0x1.0p-53 }
}

public enum ResearchAnalysis {
    public static func sensitivity(_ configuration: SimulationConfiguration, parameter: ModelParameter,
                                   relativeChange: Double = 0.05) throws -> SensitivityResult {
        try configuration.validate()
        guard relativeChange.isFinite, relativeChange > 0, relativeChange <= 0.5 else {
            throw SimulationError.invalidInput("Sensitivitätsänderung muss in (0, 0.5] liegen")
        }
        let value = configuration.parameters[parameter]
        let delta = max(value * relativeChange, 1e-6)
        let low = max(0, value-delta), high = min(1, value+delta)
        let points = try sweep(configuration, parameter: parameter, values: [low, value, high])
        let derivative = (points[2].finalFibrosis-points[0].finalFibrosis)/(high-low)
        let baseline = points[1].finalFibrosis
        return SensitivityResult(parameter: parameter, derivative: derivative,
                                 elasticity: baseline > 0 ? derivative * value / baseline : nil)
    }

    public static func sweep(_ configuration: SimulationConfiguration, parameter: ModelParameter,
                             values: [Double]) throws -> [SweepPoint] {
        try validateBatch(configuration, count: values.count)
        let configurations = try values.map { value in
            var changed = configuration
            changed.parameters[parameter] = value
            try changed.validate()
            return changed
        }
        try checkTotalWork(configurations)
        return try configurations.map { changed in
            let sample = try LiverSimulator.run(changed).samples.last!
            return SweepPoint(value: changed.parameters[parameter], finalFibrosis: sample.state.fibrosis,
                              finalReserve: sample.reserve)
        }
    }

    /// Quantiles describe assumed parameter spread, never a calibrated prediction interval.
    public static func ensemble(_ configuration: SimulationConfiguration, count: Int = 64,
                                relativeSpread: Double = 0.2) throws -> [EnsemblePoint] {
        try validateBatch(configuration, count: count)
        guard count >= 2, relativeSpread.isFinite, (0...1).contains(relativeSpread) else {
            throw SimulationError.invalidInput("Ensemble benötigt mindestens 2 Mitglieder und Streuung in 0...1")
        }
        for parameter in ModelParameter.allCases {
            guard configuration.parameters[parameter] * (1+relativeSpread) <= 1 else {
                throw SimulationError.invalidInput("Parameterstreuung überschreitet 1 / Tag")
            }
        }
        var generator = SeededGenerator(seed: configuration.seed)
        var configurations: [SimulationConfiguration] = []
        for _ in 0..<count {
            var changed = configuration
            for parameter in ModelParameter.allCases {
                changed.parameters[parameter] *= 1 + relativeSpread * (2*generator.unitInterval()-1)
            }
            try changed.validate()
            configurations.append(changed)
        }
        try checkTotalWork(configurations)
        let runs = try configurations.map { try LiverSimulator.run($0) }
        return runs[0].samples.indices.map { index in
            let values = runs.map { $0.samples[index].state.fibrosis }.sorted()
            func quantile(_ p: Double) -> Double {
                let location = p * Double(values.count-1)
                let low = Int(location), high = min(low+1, values.count-1)
                return values[low] + (location-Double(low)) * (values[high]-values[low])
            }
            return EnsemblePoint(day: runs[0].samples[index].day, lower: quantile(0.05),
                                 median: quantile(0.5), upper: quantile(0.95))
        }
    }

    /// Fits only explicitly synthetic matrix observations; no clinical calibration claim.
    public static func calibrateSynthetic(_ configuration: SimulationConfiguration, parameter: ModelParameter,
                                          candidates: [Double], observations: [SyntheticObservation]) throws -> CalibrationResult {
        try validateBatch(configuration, count: candidates.count)
        guard !observations.isEmpty, observations.count <= 20_000,
              Set(observations.map(\.day)).count == observations.count else {
            throw SimulationError.invalidInput("Synthetische Beobachtungen fehlen oder haben doppelte Zeitpunkte")
        }
        for observation in observations {
            guard observation.day.isFinite, observation.day >= 0,
                  observation.day - configuration.durationDays <= 8 * max(observation.day.ulp, configuration.durationDays.ulp),
                  observation.fibrosis.isFinite, (0...1).contains(observation.fibrosis) else {
                throw SimulationError.invalidInput("Synthetische Beobachtung außerhalb des Bereichs")
            }
        }
        let configurations = try candidates.map { candidate in
            var changed = configuration
            changed.parameters[parameter] = candidate
            try changed.validate()
            return changed
        }
        try checkTotalWork(configurations)
        var bestValue = candidates[0]
        var bestLoss = Double.infinity
        var observationIndices: [Int]?
        for changed in configurations {
            let samples = try LiverSimulator.run(changed).samples
            if observationIndices == nil {
                observationIndices = try observations.map { observation in
                    var low = 0, high = samples.count
                    while low < high {
                        let middle = (low+high)/2
                        if samples[middle].day < observation.day { low = middle+1 }
                        else { high = middle }
                    }
                    let upper = min(low, samples.count-1), lower = max(0, low-1)
                    let index = abs(samples[lower].day-observation.day) < abs(samples[upper].day-observation.day) ? lower : upper
                    let tolerance = 8 * max(samples[index].day.ulp, observation.day.ulp)
                    guard abs(samples[index].day-observation.day) <= tolerance else {
                        throw SimulationError.invalidInput("Beobachtungszeit fehlt im Ausgaberaster")
                    }
                    return index
                }
                guard Set(observationIndices!).count == observations.count else {
                    throw SimulationError.invalidInput("Mehrere Beobachtungen entsprechen derselben Ausgabezeit")
                }
            }
            var loss = 0.0
            for (observation, index) in zip(observations, observationIndices!) {
                loss += pow(samples[index].state.fibrosis-observation.fibrosis, 2)
            }
            loss /= Double(observations.count)
            if loss < bestLoss { bestLoss = loss; bestValue = changed.parameters[parameter] }
        }
        return CalibrationResult(parameter: parameter, value: bestValue, meanSquaredError: bestLoss,
                                 candidateCount: candidates.count)
    }

    private static func validateBatch(_ configuration: SimulationConfiguration, count: Int) throws {
        try configuration.validate()
        guard (1...256).contains(count), configuration.estimatedWork * Double(count) <= 2_000_000 else {
            throw SimulationError.resourceLimit
        }
    }

    private static func checkTotalWork(_ configurations: [SimulationConfiguration]) throws {
        guard configurations.reduce(0.0, { $0 + $1.estimatedWork }) <= 2_000_000 else {
            throw SimulationError.resourceLimit
        }
    }
}
