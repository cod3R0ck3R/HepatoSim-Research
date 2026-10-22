import Foundation
import XCTest
@testable import HepatoCore

final class HepatoCoreTests: XCTestCase {
    func testHealthyEquilibriumWithoutInsult() throws {
        let initial = LiverState(hepatocytes: 1, inflammation: 0, stellate: 0, fibrosis: 0)
        let config = SimulationConfiguration(initial: initial, scenario: Scenario(injuryMultiplier: 0))
        let run = try LiverSimulator.run(config)
        XCTAssertTrue(run.samples.allSatisfy { $0.state == initial })
        XCTAssertEqual(run.samples.last?.reserve, 1)
        XCTAssertEqual(run.samples.last?.portalResistance, 1)
    }

    func testZeroRatesFreezeStateAndZeroDurationHasOneSample() throws {
        var config = SimulationConfiguration()
        for parameter in ModelParameter.allCases { config.parameters[parameter] = 0 }
        XCTAssertTrue(try LiverSimulator.run(config).samples.allSatisfy { $0.state == config.initial })
        config.durationDays = 0
        XCTAssertEqual(try LiverSimulator.run(config).samples, [SimulationSample(day: 0, state: .synthetic)])
    }

    func testResolutionMatchesAnalyticExponential() throws {
        let config = SimulationConfiguration(scenario: Scenario(injuryMultiplier: 0), durationDays: 30)
        let run = try LiverSimulator.run(config)
        for sample in run.samples {
            XCTAssertEqual(sample.state.inflammation,
                           config.initial.inflammation * exp(-config.parameters.resolutionRate * sample.day), accuracy: 1e-11)
        }
    }

    func testFibrosisRegressionMatchesAnalyticExponentialWithoutStellateActivation() throws {
        var config = SimulationConfiguration(initial: LiverState(hepatocytes: 1, inflammation: 0, stellate: 0, fibrosis: 0.6))
        config.parameters.activationRate = 0
        config.parameters.depositionRate = 0
        for sample in try LiverSimulator.run(config).samples {
            XCTAssertEqual(sample.state.fibrosis, 0.6 * exp(-0.003 * sample.day), accuracy: 1e-11)
        }
    }

    func testNumericalRegressionAgainstIndependentFineStepReference() throws {
        // Independent Python RK4, dt=0.001 day, 365000 steps; scientific validity is not implied.
        let state = try XCTUnwrap(LiverSimulator.run(.init()).samples.last?.state)
        XCTAssertEqual(state.hepatocytes, 0.746565655326392, accuracy: 1e-9)
        XCTAssertEqual(state.inflammation, 0.2855210398757961, accuracy: 1e-9)
        XCTAssertEqual(state.stellate, 0.3684590007801131, accuracy: 1e-9)
        XCTAssertEqual(state.fibrosis, 0.5583501551753726, accuracy: 1e-9)
    }

    func testRK4StepConvergence() throws {
        var config = SimulationConfiguration(durationDays: 4, sampleEveryDays: 4)
        for parameter in ModelParameter.allCases { config.parameters[parameter] = 0 }
        config.parameters.resolutionRate = 0.8
        let exact = config.initial.inflammation * exp(-0.8 * config.durationDays)
        var errors: [Double] = []
        for step in [0.08, 0.04, 0.02] {
            config.stepDays = step
            let result = try XCTUnwrap(LiverSimulator.run(config).samples.last)
            errors.append(abs(result.state.inflammation-exact))
        }
        XCTAssertGreaterThan(errors[0], errors[1] * 8)
        XCTAssertGreaterThan(errors[1], errors[2] * 8)
        XCTAssertLessThan(errors[2], 1e-9)
    }

    func testInterventionDiscontinuityUsesExactBoundary() throws {
        let scenario = Scenario(name: "Reizentzug", injuryMultiplier: 0, startDay: 0.37)
        let combined = try LiverSimulator.run(SimulationConfiguration(scenario: scenario, durationDays: 0.5, stepDays: 0.1, sampleEveryDays: 0.37))
        let before = try LiverSimulator.run(SimulationConfiguration(durationDays: 0.37, stepDays: 0.1, sampleEveryDays: 0.37))
        XCTAssertEqual(combined.samples[1], before.samples[1])
        var active = scenario
        active.startDay = 0
        let after = try LiverSimulator.run(SimulationConfiguration(initial: before.samples[1].state, scenario: active,
                                                                  durationDays: 0.13, stepDays: 0.1, sampleEveryDays: 0.13))
        XCTAssertEqual(combined.samples[2].state.fibrosis, after.samples[1].state.fibrosis, accuracy: 1e-14)
        XCTAssertEqual(combined.samples[2].state.hepatocytes, after.samples[1].state.hepatocytes, accuracy: 1e-14)
    }

    func testOutputGridIncludesFinalDayWithoutDuplicate() throws {
        let run = try LiverSimulator.run(SimulationConfiguration(durationDays: 2.5, sampleEveryDays: 0.7))
        XCTAssertEqual(run.samples.map(\.day), [0, 0.7, 1.4, 0.7*3, 2.5])
        XCTAssertEqual(Set(run.samples.map(\.day)).count, run.samples.count)
    }

    func testAllBoundaryStatesAndHighRatesStayFiniteAndBounded() throws {
        var parameters = ModelParameters()
        for parameter in ModelParameter.allCases { parameters[parameter] = 1 }
        for bits in 0..<16 {
            let initial = LiverState(hepatocytes: Double(bits & 1), inflammation: Double((bits >> 1) & 1),
                                     stellate: Double((bits >> 2) & 1), fibrosis: Double((bits >> 3) & 1))
            let scenario = Scenario(injuryMultiplier: 4, inflammationMultiplier: 4, regenerationMultiplier: 4)
            let run = try LiverSimulator.run(SimulationConfiguration(initial: initial, parameters: parameters,
                                                                     scenario: scenario, durationDays: 3, stepDays: 1, sampleEveryDays: 0.25))
            for sample in run.samples { XCTAssertNoThrow(try sample.state.validate()) }
        }
    }

    func testInvalidInputsAndResourceLimitsAreRejected() throws {
        var invalid: [SimulationConfiguration] = []
        var c = SimulationConfiguration(); c.initial.fibrosis = .nan; invalid.append(c)
        c = .init(); c.parameters.injuryRate = -.infinity; invalid.append(c)
        c = .init(); c.parameters.regenerationRate = 1.01; invalid.append(c)
        c = .init(); c.scenario.startDay = -1; invalid.append(c)
        c = .init(); c.scenario.antifibroticEffect = 1.01; invalid.append(c)
        c = .init(); c.scenario.injuryMultiplier = 5; invalid.append(c)
        c = .init(); c.scenario.name = " "; invalid.append(c)
        c = .init(); c.durationDays = .infinity; invalid.append(c)
        c = .init(); c.durationDays = -1; invalid.append(c)
        c = .init(); c.stepDays = 0; invalid.append(c)
        c = .init(); c.sampleEveryDays = 0; invalid.append(c)
        c = .init(); c.sampleEveryDays = 0.0001; invalid.append(c)
        c = .init(); c.stepDays = Double.leastNonzeroMagnitude; invalid.append(c)
        for input in invalid { XCTAssertThrowsError(try LiverSimulator.run(input)) }
    }

    func testDeterministicSamplesAndCodableRoundTrip() throws {
        let run = try LiverSimulator.run(.init())
        XCTAssertEqual(run.samples, try LiverSimulator.run(run.configuration).samples)
        XCTAssertEqual(run, try JSONDecoder().decode(SimulationRun.self, from: JSONEncoder().encode(run)))
    }

    func testInsultWithdrawalImprovesReserveInThisSyntheticModel() throws {
        let baseline = try XCTUnwrap(LiverSimulator.run(.init()).samples.last)
        let treated = try XCTUnwrap(LiverSimulator.run(.init(scenario: Scenario(injuryMultiplier: 0))).samples.last)
        XCTAssertGreaterThan(treated.reserve, baseline.reserve)
        XCTAssertLessThan(treated.state.fibrosis, baseline.state.fibrosis)
    }

    func testSeededGeneratorKnownVector() {
        var generator = SeededGenerator(seed: 0)
        XCTAssertEqual(generator.next(), 0xE220A8397B1DCDAF)
        XCTAssertEqual(generator.next(), 0x6E789E6AA1B965F4)
        for _ in 0..<100 { XCTAssertTrue((0..<1).contains(generator.unitInterval())) }
    }

    func testEnsembleReproducibilityAndOrderedQuantiles() throws {
        var config = SimulationConfiguration(durationDays: 40)
        let first = try ResearchAnalysis.ensemble(config, count: 12)
        XCTAssertEqual(first, try ResearchAnalysis.ensemble(config, count: 12))
        config.seed = 43
        XCTAssertNotEqual(first, try ResearchAnalysis.ensemble(config, count: 12))
        for point in first {
            XCTAssertLessThanOrEqual(point.lower, point.median)
            XCTAssertLessThanOrEqual(point.median, point.upper)
        }
        XCTAssertEqual(first.map(\.day), try LiverSimulator.run(config).samples.map(\.day))
    }

    func testZeroSpreadEnsembleCollapsesToSingleTrajectory() throws {
        let config = SimulationConfiguration(durationDays: 10)
        let band = try ResearchAnalysis.ensemble(config, count: 4, relativeSpread: 0)
        let run = try LiverSimulator.run(config)
        for (point, sample) in zip(band, run.samples) {
            XCTAssertEqual(point.lower, sample.state.fibrosis)
            XCTAssertEqual(point.upper, sample.state.fibrosis)
        }
    }

    func testSensitivityAndSweep() throws {
        let config = SimulationConfiguration(durationDays: 60)
        let result = try ResearchAnalysis.sensitivity(config, parameter: .depositionRate)
        XCTAssertGreaterThan(result.derivative, 0)
        XCTAssertGreaterThan(try XCTUnwrap(result.elasticity), 0)
        let sweep = try ResearchAnalysis.sweep(config, parameter: .depositionRate, values: [0, 0.008, 0.016])
        XCTAssertLessThan(sweep[0].finalFibrosis, sweep[1].finalFibrosis)
        XCTAssertLessThan(sweep[1].finalFibrosis, sweep[2].finalFibrosis)
        var zero = config
        zero.parameters.depositionRate = 0
        XCTAssertTrue(try ResearchAnalysis.sensitivity(zero, parameter: .depositionRate).derivative.isFinite)
        zero.initial = LiverState(hepatocytes: 1, inflammation: 0, stellate: 0, fibrosis: 0)
        zero.parameters.injuryRate = 0
        XCTAssertNil(try ResearchAnalysis.sensitivity(zero, parameter: .depositionRate).elasticity)
    }

    func testSyntheticGridCalibrationRecoversKnownParameter() throws {
        var truth = SimulationConfiguration(durationDays: 100, sampleEveryDays: 10)
        truth.parameters.depositionRate = 0.012
        let observations = try LiverSimulator.run(truth).samples.map { SyntheticObservation(day: $0.day, fibrosis: $0.state.fibrosis) }
        let result = try ResearchAnalysis.calibrateSynthetic(.init(durationDays: 100, sampleEveryDays: 10),
                                                              parameter: .depositionRate, candidates: [0.004, 0.008, 0.012, 0.016],
                                                              observations: observations)
        XCTAssertEqual(result.value, 0.012)
        XCTAssertEqual(result.meanSquaredError, 0)
        XCTAssertNoThrow(try ResearchAnalysis.calibrateSynthetic(
            .init(durationDays: 0.3, sampleEveryDays: 0.1), parameter: .depositionRate,
            candidates: [0.008], observations: [.init(day: 3*0.1, fibrosis: 0.35)]))
        XCTAssertEqual(result.candidateCount, 4)
    }

    func testAnalysisRejectsInvalidDomainsAndOversizedBatches() throws {
        let config = SimulationConfiguration(durationDays: 10)
        XCTAssertThrowsError(try ResearchAnalysis.ensemble(config, count: 1))
        XCTAssertThrowsError(try ResearchAnalysis.ensemble(config, count: 257))
        XCTAssertThrowsError(try ResearchAnalysis.ensemble(config, relativeSpread: .nan))
        XCTAssertThrowsError(try ResearchAnalysis.sensitivity(config, parameter: .injuryRate, relativeChange: 0))
        XCTAssertThrowsError(try ResearchAnalysis.sweep(config, parameter: .injuryRate, values: []))
        XCTAssertThrowsError(try ResearchAnalysis.sweep(config, parameter: .injuryRate, values: [-1]))
        XCTAssertThrowsError(try ResearchAnalysis.ensemble(.init(durationDays: 3650), count: 256))
        var high = config; high.parameters.injuryRate = 0.9
        XCTAssertThrowsError(try ResearchAnalysis.ensemble(high, relativeSpread: 0.2))
        let observation = SyntheticObservation(day: 0, fibrosis: 0.35)
        XCTAssertThrowsError(try ResearchAnalysis.calibrateSynthetic(config, parameter: .injuryRate, candidates: [0.01], observations: []))
        XCTAssertThrowsError(try ResearchAnalysis.calibrateSynthetic(config, parameter: .injuryRate, candidates: [0.01], observations: [observation, observation]))
        XCTAssertThrowsError(try ResearchAnalysis.calibrateSynthetic(config, parameter: .injuryRate, candidates: [0.01], observations: [.init(day: 1, fibrosis: 0.4)]))
    }

    func testSyntheticObservationGridAcceptsRoundingOnly() throws {
        let config = SimulationConfiguration(durationDays: 0.5, sampleEveryDays: 0.1)
        let sample = try LiverSimulator.run(config).samples[3]
        XCTAssertNotEqual(sample.day, 0.3)
        let result = try ResearchAnalysis.calibrateSynthetic(config, parameter: .depositionRate,
            candidates: [config.parameters.depositionRate], observations: [.init(day: 0.3, fibrosis: sample.state.fibrosis)])
        XCTAssertEqual(result.meanSquaredError, 0)
        XCTAssertThrowsError(try ResearchAnalysis.calibrateSynthetic(config, parameter: .depositionRate,
            candidates: [0.008], observations: [.init(day: 0.300001, fibrosis: sample.state.fibrosis)]))
        XCTAssertThrowsError(try ResearchAnalysis.calibrateSynthetic(config, parameter: .depositionRate,
            candidates: [0.008], observations: [.init(day: 0.3, fibrosis: 0.35), .init(day: sample.day, fibrosis: 0.35)]))
        let tiny = SimulationConfiguration(durationDays: 1e-12, sampleEveryDays: 1e-13)
        XCTAssertThrowsError(try ResearchAnalysis.calibrateSynthetic(tiny, parameter: .depositionRate,
            candidates: [0.008], observations: [.init(day: 1.1e-13, fibrosis: 0.35)]))
    }
}
