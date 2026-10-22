import XCTest
@testable import HepatoCore

final class EvidenceTests: XCTestCase {
    private func alteredCatalog(_ edit: (inout [String: Any]) -> Void) throws -> Data {
        let data = try JSONEncoder().encode(EvidenceCatalog.loadBundled())
        var object = try XCTUnwrap(JSONSerialization.jsonObject(with: data) as? [String: Any])
        edit(&object)
        return try JSONSerialization.data(withJSONObject: object)
    }

    func testBundledCatalogPreservesPublishedObservationsAndProvenance() throws {
        let catalog = try EvidenceCatalog.loadBundled()
        XCTAssertEqual(catalog.retrievedAt, "2026-10-22")
        XCTAssertEqual(catalog.calibrationStatus, "not-calibrated")
        XCTAssertEqual(catalog.evidenceKind, "published-aggregate-observations")
        XCTAssertEqual(catalog.records.count, 5)
        let elastography = try XCTUnwrap(catalog.records.first { $0.id == "gianni-2017-elastography" })
        XCTAssertEqual(elastography.findings.first?.kind, .reportedContinuousOutcome)
        XCTAssertNil(try elastography.findings.first?.observedProportion())
        let first = try XCTUnwrap(catalog.records.first { $0.id == "hofer-2023-recompensation" })
        let second = try XCTUnwrap(catalog.records.first { $0.id == "hofer-2026-recompensation" })
        XCTAssertEqual(first.doi, "10.1111/liv.15676")
        XCTAssertEqual(second.doi, "10.1016/j.jhep.2026.01.007")
        let firstCount = try XCTUnwrap(first.findings.first?.observedProportion())
        let secondCount = try XCTUnwrap(second.findings.first?.observedProportion())
        XCTAssertEqual(firstCount.events, 37); XCTAssertEqual(firstCount.total, 204)
        XCTAssertEqual(secondCount.events, 197); XCTAssertEqual(secondCount.total, 633)
        XCTAssertEqual(firstCount.fraction, 37.0 / 204.0)
        XCTAssertEqual(secondCount.fraction, 197.0 / 633.0)
        XCTAssertEqual(try EvidenceCatalog.decode(JSONEncoder().encode(catalog)), catalog)
    }

    func testWilsonRejectsInvalidDenominatorsAndEvents() {
        for (events, total) in [(0, 0), (0, -1), (-1, 10), (11, 10)] {
            XCTAssertThrowsError(try ObservedProportion.wilson(events: events, total: total))
        }
    }

    func testWilsonZeroAndAllEventsHaveBoundedIntervals() throws {
        let zero = try ObservedProportion.wilson(events: 0, total: 10)
        XCTAssertEqual(zero.fraction, 0)
        XCTAssertEqual(zero.lower95, 0, accuracy: 1e-15)
        XCTAssertEqual(zero.upper95, 0.2775327998628892, accuracy: 1e-14)
        let all = try ObservedProportion.wilson(events: 10, total: 10)
        XCTAssertEqual(all.fraction, 1)
        XCTAssertEqual(all.lower95, 0.7224672001371107, accuracy: 1e-14)
        XCTAssertEqual(all.upper95, 1, accuracy: 1e-15)
    }

    func testWilsonOneEventAndBalancedReferenceCases() throws {
        let one = try ObservedProportion.wilson(events: 1, total: 10)
        XCTAssertEqual(one.lower95, 0.017876213095072896, accuracy: 1e-14)
        XCTAssertEqual(one.upper95, 0.4041500267952385, accuracy: 1e-14)
        let balanced = try ObservedProportion.wilson(events: 50, total: 100)
        XCTAssertEqual(balanced.fraction, 0.5)
        XCTAssertEqual(balanced.lower95, 0.4038315303659957, accuracy: 1e-14)
        XCTAssertEqual(balanced.upper95, 0.5961684696340044, accuracy: 1e-14)
        let single = try ObservedProportion.wilson(events: 1, total: 1)
        XCTAssertEqual(single.lower95, 0.20654931437723745, accuracy: 1e-14)
        XCTAssertEqual(single.upper95, 1, accuracy: 1e-15)
    }

    func testWilsonLargeCountsRemainFiniteAndBounded() throws {
        let interval = try ObservedProportion.wilson(events: Int.max / 2, total: Int.max)
        XCTAssertTrue(interval.lower95.isFinite && interval.upper95.isFinite)
        XCTAssertTrue(interval.lower95 >= 0 && interval.upper95 <= 1)
        XCTAssertLessThanOrEqual(interval.lower95, interval.fraction)
        XCTAssertGreaterThanOrEqual(interval.upper95, interval.fraction)
    }

    func testTimeToEventEstimateDoesNotAcquireBinomialInterval() throws {
        let catalog = try EvidenceCatalog.loadBundled()
        let finding = try XCTUnwrap(catalog.records.flatMap(\.findings).first { $0.kind == .reportedTimeToEventEstimate })
        XCTAssertNil(try finding.observedProportion())
        XCTAssertNil(finding.events); XCTAssertNil(finding.total)
        let invalid = EvidenceFinding(id: "wrong-denominator", endpoint: "Time-to-event", kind: .reportedTimeToEventEstimate,
                                      events: 10, total: 100, followUp: "Variable", summary: "Not a binomial endpoint")
        XCTAssertThrowsError(try invalid.observedProportion())
    }

    func testCatalogRejectsInvalidURLDOIModelAndDuplicateStudy() throws {
        for (key, value) in [("url", "javascript:alert(1)"), ("url", "https://user:password@example.org/"),
                             ("doi", "not-a-doi"), ("id", "../untrusted")] {
            let data = try alteredCatalog {
                var records = $0["records"] as! [[String: Any]]
                records[0][key] = value
                $0["records"] = records
            }
            XCTAssertThrowsError(try EvidenceCatalog.decode(data))
        }
        let unknownModel = try alteredCatalog {
            var records = $0["records"] as! [[String: Any]]
            records[0]["modelIDs"] = ["unvalidated-model"]
            $0["records"] = records
        }
        XCTAssertThrowsError(try EvidenceCatalog.decode(unknownModel))
        let duplicate = try alteredCatalog {
            var records = $0["records"] as! [[String: Any]]
            records.append(records[0])
            $0["records"] = records
        }
        XCTAssertThrowsError(try EvidenceCatalog.decode(duplicate))
    }

    func testCatalogRejectsInvalidCountAndMissingDenominator() throws {
        for invalidTotal in [0, 1] {
            let data = try alteredCatalog {
                var records = $0["records"] as! [[String: Any]]
                var findings = records[0]["findings"] as! [[String: Any]]
                findings[0]["total"] = invalidTotal
                records[0]["findings"] = findings
                $0["records"] = records
            }
            XCTAssertThrowsError(try EvidenceCatalog.decode(data))
        }
        let incomplete = EvidenceFinding(id: "missing", endpoint: "Count", kind: .crudeObservedProportion,
                                         events: 1, total: nil, followUp: "Variable", summary: "Missing denominator")
        XCTAssertThrowsError(try incomplete.observedProportion())
    }

    func testCatalogRejectsFutureSchemaWrongFreezeDateAndCalibrationClaim() throws {
        for (key, value) in [("retrievedAt", "2027-01-01"), ("calibrationStatus", "clinically-validated"),
                             ("evidenceKind", "synthetic-research")] {
            XCTAssertThrowsError(try EvidenceCatalog.decode(alteredCatalog { $0[key] = value }))
        }
        XCTAssertThrowsError(try EvidenceCatalog.decode(alteredCatalog { $0["schemaVersion"] = 2 }))
        XCTAssertThrowsError(try EvidenceCatalog.decode(Data("{}".utf8)))
        XCTAssertThrowsError(try EvidenceCatalog.decode(Data()))
    }
}
