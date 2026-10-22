import XCTest
import HepatoCore
@testable import HepatoUI

final class ResearchSessionTests: XCTestCase {
    @MainActor
    func testStoredComparisonRequiresMatchingConfigurationAndVersion() throws {
        let config = SimulationConfiguration(scenario: Scenario(name: "Experiment", injuryMultiplier: 0.3), durationDays: 10)
        let run = try LiverSimulator.run(config)
        var reference = config
        reference.scenario = .control
        let baseline = try LiverSimulator.run(reference)
        var wrongVersion = baseline
        wrongVersion.id = UUID()
        wrongVersion.modelVersion = "99.0.0"
        var wrongConfiguration = reference
        wrongConfiguration.seed = 99
        let wrongControl = try LiverSimulator.run(wrongConfiguration)
        let session = ResearchSession()
        session.runs = [wrongVersion, wrongControl, baseline, run]
        session.select(run)
        XCTAssertEqual(session.control, baseline)
        XCTAssertEqual(session.selected, run)
        XCTAssertEqual(session.configuration, config)
        session.select(baseline)
        XCTAssertNil(session.control)
    }

    @MainActor
    func testUnmatchedSavedRunIsNotSilentlyRecomputed() throws {
        let run = try LiverSimulator.run(SimulationConfiguration(scenario: Scenario(name: "Experiment"), durationDays: 10))
        let session = ResearchSession()
        session.select(run)
        XCTAssertNil(session.control)
        XCTAssertEqual(session.selected, run)
        XCTAssertEqual(session.selectedDay, 10)
    }
}
