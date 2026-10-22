import Foundation

public enum LiverSimulator {
    public static let modelVersion = "0.1.0"

    public static func run(_ configuration: SimulationConfiguration) throws -> SimulationRun {
        try configuration.validate()
        var state = configuration.initial
        var day = 0.0
        var sampleIndex = 1
        var samples = [SimulationSample(day: 0, state: state)]
        while day < configuration.durationDays {
            try Task.checkCancellation()
            let nextSample = min(Double(sampleIndex) * configuration.sampleEveryDays, configuration.durationDays)
            while day < nextSample {
                let active = day >= configuration.scenario.startDay
                let boundary = active ? nextSample : min(nextSample, configuration.scenario.startDay)
                let endpoint = min(day + configuration.integrationStep, boundary)
                let dt = endpoint - day
                guard dt > 0 else { throw SimulationError.unstableState }
                state = try advance(state, dt: dt, parameters: configuration.parameters,
                                    scenario: active ? configuration.scenario : .control)
                day = endpoint
            }
            samples.append(SimulationSample(day: nextSample, state: state))
            sampleIndex += 1
        }
        return SimulationRun(configuration: configuration, samples: samples)
    }

    private static func derivative(_ x: LiverState, _ p: ModelParameters, _ s: Scenario) -> LiverState {
        let h = x.hepatocytes, i = x.inflammation, a = x.stellate, f = x.fibrosis
        return LiverState(
            hepatocytes: p.regenerationRate * s.regenerationMultiplier * h * (1-h) * (1-0.7*f)
                - p.injuryRate * s.injuryMultiplier * h * (0.25+0.75*i),
            inflammation: p.inflammationRate * s.inflammationMultiplier * s.injuryMultiplier * (1-h) * (1-i)
                - p.resolutionRate * i,
            stellate: p.activationRate * i * (1-a) - p.deactivationRate * a,
            fibrosis: p.depositionRate * (1-s.antifibroticEffect) * a * (1-f)
                - p.regressionRate * (1-a) * f)
    }

    private static func add(_ x: LiverState, _ d: LiverState, scale: Double) -> LiverState {
        LiverState(hepatocytes: x.hepatocytes + scale*d.hepatocytes,
                   inflammation: x.inflammation + scale*d.inflammation,
                   stellate: x.stellate + scale*d.stellate,
                   fibrosis: x.fibrosis + scale*d.fibrosis)
    }

    private static func advance(_ x: LiverState, dt: Double, parameters p: ModelParameters,
                                scenario s: Scenario) throws -> LiverState {
        let k1 = derivative(x, p, s)
        let k2 = derivative(add(x, k1, scale: dt/2), p, s)
        let k3 = derivative(add(x, k2, scale: dt/2), p, s)
        let k4 = derivative(add(x, k3, scale: dt), p, s)
        var result = add(add(add(add(x, k1, scale: dt/6), k2, scale: dt/3), k3, scale: dt/3), k4, scale: dt/6)
        func checked(_ value: Double) throws -> Double {
            guard value.isFinite, value >= -1e-10, value <= 1+1e-10 else { throw SimulationError.unstableState }
            return min(1, max(0, value))
        }
        result.hepatocytes = try checked(result.hepatocytes)
        result.inflammation = try checked(result.inflammation)
        result.stellate = try checked(result.stellate)
        result.fibrosis = try checked(result.fibrosis)
        return result
    }
}
