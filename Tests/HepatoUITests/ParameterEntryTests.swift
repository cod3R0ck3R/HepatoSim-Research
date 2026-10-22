import XCTest
import HepatoCore
@testable import HepatoUI

final class ParameterEntryTests: XCTestCase {
    @MainActor
    func testTabTraversalSkipsSlidersAndDoesNotTrapAtFormBoundaries() {
        let fields = ["Schädigung", "Regeneration", "Fibrose"]
        XCTAssertEqual(ParameterControl.adjacentField("Schädigung", in: fields, backwards: false), "Regeneration")
        XCTAssertEqual(ParameterControl.adjacentField("Fibrose", in: fields, backwards: true), "Regeneration")
        XCTAssertNil(ParameterControl.adjacentField("Schädigung", in: fields, backwards: true))
        XCTAssertNil(ParameterControl.adjacentField("Fibrose", in: fields, backwards: false))
    }
    func testDecimalInputAcceptsCommaPointExponentAndBoundaries() {
        for text in ["0,012", "0.012", "1.2e-2", " 0,012 "] {
            XCTAssertEqual(DecimalEntry.parse(text, in: 0...1), 0.012)
        }
        XCTAssertEqual(DecimalEntry.parse("0,", in: 0...1), 0)
        XCTAssertEqual(DecimalEntry.parse(".5", in: 0...1), 0.5)
        XCTAssertEqual(DecimalEntry.parse("1", in: 0...1), 1)
        for value in [0.0, 0.000000001, 0.00005, 0.123456789012, 1.0] {
            XCTAssertEqual(DecimalEntry.parse(DecimalEntry.string(value), in: 0...1), value)
        }
    }

    func testInvalidNumbersCannotReplaceCommittedValue() {
        for text in ["", "-", ",", ".", "1,2.3", "1 000", "1'000", "NaN", "Inf", "-0.1", "1.01", "1e999", "0x1"] {
            XCTAssertNil(DecimalEntry.parse(text, in: 0...1), text)
        }
        var edits = ParameterEdits()
        XCTAssertNil(edits.update("oops", for: "Rate", range: 0...1))
        XCTAssertTrue(edits.invalid.contains("Rate"))
        XCTAssertEqual(edits.update("0,", for: "Rate", range: 0...1), 0)
        XCTAssertEqual(edits.text["Rate"], "0,")
        XCTAssertTrue(edits.invalid.isEmpty)
        edits.reset("Rate")
        XCTAssertNil(edits.text["Rate"])
    }

    @MainActor
    func testInvalidDraftBlocksSimulationAndSelectionClearsIt() async throws {
        let session = ResearchSession()
        _ = session.parameterEdits.update("bad", for: "Rate", range: 0...1)
        await session.simulate()
        XCTAssertNotNil(session.error)
        let run = try LiverSimulator.run(SimulationConfiguration(durationDays: 0))
        session.select(run)
        XCTAssertTrue(session.parameterEdits.invalid.isEmpty)
        XCTAssertTrue(session.parameterEdits.text.isEmpty)
    }

    @MainActor
    func testALDCessationIsExplicitHypothesisAndResetsDrafts() {
        let session = ResearchSession()
        let originalRates = session.configuration.parameters
        _ = session.parameterEdits.update("bad", for: "Rate", range: 0...1)
        session.applyALDCessation()
        XCTAssertEqual(session.configuration.parameters, originalRates)
        XCTAssertEqual(session.configuration.scenario.injuryMultiplier, 0)
        XCTAssertEqual(session.configuration.scenario.inflammationMultiplier, 1)
        XCTAssertEqual(session.configuration.scenario.regenerationMultiplier, 1)
        XCTAssertEqual(session.configuration.scenario.antifibroticEffect, 0)
        XCTAssertTrue(session.parameterEdits.invalid.isEmpty)
    }
}
