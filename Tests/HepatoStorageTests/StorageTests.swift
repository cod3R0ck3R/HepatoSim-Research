import XCTest
import Foundation
import CSQLite
import HepatoCore
@testable import HepatoStorage

@MainActor
final class StorageTests: XCTestCase {
    private func temporaryURL() -> URL {
        FileManager.default.temporaryDirectory.appendingPathComponent("HepatoSimTests-\(UUID())", isDirectory: true)
            .appendingPathComponent("runs.sqlite")
    }

    private func makeRun() throws -> SimulationRun {
        try LiverSimulator.run(.init(durationDays: 10, stepDays: 0.25, sampleEveryDays: 2))
    }

    private func mutateJSON(_ data: Data, _ change: (inout [String: Any]) -> Void) throws -> Data {
        var object = try XCTUnwrap(JSONSerialization.jsonObject(with: data) as? [String: Any])
        change(&object)
        return try JSONSerialization.data(withJSONObject: object)
    }

    private func rawSQL(_ sql: String, at url: URL) throws {
        var database: OpaquePointer?
        XCTAssertEqual(sqlite3_open(url.path, &database), SQLITE_OK)
        defer { sqlite3_close(database) }
        guard sqlite3_exec(database, sql, nil, nil, nil) == SQLITE_OK else {
            throw StorageError.database(String(cString: sqlite3_errmsg(database)))
        }
    }

    func testPersistenceReopensAndPreservesAllProvenance() async throws {
        let url = temporaryURL()
        defer { try? FileManager.default.removeItem(at: url.deletingLastPathComponent()) }
        let expected = try makeRun()
        do {
            let store = try RunStore(url: url)
            try await store.save(expected)
        }
        let reopened = try RunStore(url: url)
        let actual = try await reopened.runs()
        XCTAssertEqual(actual, [expected])
        let file = try FileManager.default.attributesOfItem(atPath: url.path)
        let directory = try FileManager.default.attributesOfItem(atPath: url.deletingLastPathComponent().path)
        XCTAssertEqual((file[.posixPermissions] as? NSNumber)?.intValue, 0o600)
        XCTAssertEqual((directory[.posixPermissions] as? NSNumber)?.intValue, 0o700)
    }

    func testDuplicateRollsBackThenNextWriteAndDeleteWork() async throws {
        let url = temporaryURL()
        defer { try? FileManager.default.removeItem(at: url.deletingLastPathComponent()) }
        let store = try RunStore(url: url)
        let first = try makeRun()
        try await store.save(first)
        do {
            try await store.save(first)
            XCTFail("Duplicate must not replace saved data")
        } catch { XCTAssertEqual(error as? StorageError, .duplicateRun) }
        let second = try makeRun()
        try await store.save(second)
        let before = try await store.runs()
        XCTAssertEqual(Set(before.map(\.id)), Set([first.id, second.id]))
        XCTAssertEqual(before.first(where: { $0.id == first.id }), first)
        try await store.delete(id: first.id)
        let after = try await store.runs()
        XCTAssertEqual(after, [second])
    }

    func testFutureDatabaseAndUnversionedForeignDatabaseFailClosed() async throws {
        let url = temporaryURL()
        defer { try? FileManager.default.removeItem(at: url.deletingLastPathComponent()) }
        _ = try RunStore(url: url)
        try rawSQL("PRAGMA user_version = 2", at: url)
        XCTAssertThrowsError(try RunStore(url: url)) { XCTAssertEqual($0 as? StorageError, .unsupportedSchema(2)) }
        try rawSQL("PRAGMA user_version = 0", at: url)
        XCTAssertThrowsError(try RunStore(url: url))
    }

    func testCorruptStoredProvenanceIsNotSilentlyLoaded() async throws {
        let url = temporaryURL()
        defer { try? FileManager.default.removeItem(at: url.deletingLastPathComponent()) }
        let store = try RunStore(url: url)
        try await store.save(makeRun())
        try rawSQL("UPDATE runs SET model_version = 'tampered'", at: url)
        do { _ = try await store.runs(); XCTFail("Tampered provenance must fail") }
        catch { XCTAssertTrue(error is StorageError) }
    }

    func testDatabaseSymlinkRejected() throws {
        let url = temporaryURL()
        let directory = url.deletingLastPathComponent()
        defer { try? FileManager.default.removeItem(at: directory) }
        try FileManager.default.createDirectory(at: directory, withIntermediateDirectories: true, attributes: [.posixPermissions: 0o700])
        let target = directory.appendingPathComponent("target")
        try Data().write(to: target)
        try FileManager.default.createSymbolicLink(at: url, withDestinationURL: target)
        XCTAssertThrowsError(try RunStore(url: url))
        try FileManager.default.removeItem(at: target)
        XCTAssertThrowsError(try RunStore(url: url))
        XCTAssertFalse(FileManager.default.fileExists(atPath: target.path), "Dangling symlink must not create its target")
    }

    func testRunJSONRoundTripAndCSVIncludesResearchUnits() throws {
        let expected = try makeRun()
        XCTAssertEqual(try RunExchange.decodeJSON(RunExchange.encodeJSON(expected)), expected)
        let csv = String(decoding: try RunExchange.exportCSV(expected), as: UTF8.self)
        XCTAssertTrue(csv.contains("alt_proxy_U/L"))
        XCTAssertTrue(csv.contains(expected.id.uuidString))
        XCTAssertEqual(csv.components(separatedBy: "\r\n").count, expected.samples.count + 2)
    }

    func testExistingSharedDirectoryIsRejectedWithoutChangingPermissions() throws {
        let url = temporaryURL()
        let directory = url.deletingLastPathComponent()
        defer { try? FileManager.default.removeItem(at: directory) }
        try FileManager.default.createDirectory(at: directory, withIntermediateDirectories: true, attributes: [.posixPermissions: 0o755])
        XCTAssertThrowsError(try RunStore(url: url))
        let attributes = try FileManager.default.attributesOfItem(atPath: directory.path)
        XCTAssertEqual((attributes[.posixPermissions] as? NSNumber)?.intValue, 0o755)
        XCTAssertFalse(FileManager.default.fileExists(atPath: url.path))
    }

    func testJSONRejectsMalformedFutureAndNonSyntheticInput() throws {
        XCTAssertThrowsError(try RunExchange.decodeJSON(Data("{broken}".utf8)))
        let data = try RunExchange.encodeJSON(makeRun())
        let future = try mutateJSON(data) { $0["schemaVersion"] = 2 }
        XCTAssertThrowsError(try RunExchange.decodeJSON(future)) { XCTAssertEqual($0 as? StorageError, .unsupportedSchema(2)) }
        let real = try mutateJSON(data) { $0["dataKind"] = "clinical" }
        XCTAssertThrowsError(try RunExchange.decodeJSON(real))
        let futureModel = try mutateJSON(data) {
            var run = $0["run"] as! [String: Any]
            run["modelVersion"] = "99.0.0"
            $0["run"] = run
        }
        XCTAssertThrowsError(try RunExchange.decodeJSON(futureModel)) {
            XCTAssertEqual($0 as? StorageError, .unsupportedModel("99.0.0"))
        }
    }

    func testInvalidRunSamplesAreRejected() throws {
        let expected = try makeRun()
        let badTime = SimulationRun(configuration: expected.configuration,
                                    samples: [.init(day: 0, state: .synthetic), .init(day: 0, state: .synthetic)])
        XCTAssertThrowsError(try RunExchange.encodeJSON(badTime))
        var invalidState = LiverState.synthetic
        invalidState.fibrosis = -.infinity
        let badState = SimulationRun(configuration: expected.configuration,
                                    samples: [.init(day: 0, state: invalidState), .init(day: 10, state: .synthetic)])
        XCTAssertThrowsError(try RunExchange.encodeJSON(badState))
    }

    func testImportRejectsFabricatedInteriorAndFinalStatesAndTimes() throws {
        let data = try RunExchange.encodeJSON(makeRun())
        for position in [1, 5] {
            let fabricated = try mutateJSON(data) {
                var run = $0["run"] as! [String: Any]
                var samples = run["samples"] as! [[String: Any]]
                var state = samples[position]["state"] as! [String: Any]
                state["fibrosis"] = 0.99
                samples[position]["state"] = state
                run["samples"] = samples
                $0["run"] = run
            }
            XCTAssertThrowsError(try RunExchange.decodeJSON(fabricated))
        }
        let shifted = try mutateJSON(data) {
            var run = $0["run"] as! [String: Any]
            var samples = run["samples"] as! [[String: Any]]
            samples[1]["day"] = 1.5
            run["samples"] = samples
            $0["run"] = run
        }
        XCTAssertThrowsError(try RunExchange.decodeJSON(shifted))
    }

    func testZeroDurationRunRoundTrip() throws {
        let expected = try LiverSimulator.run(.init(durationDays: 0))
        XCTAssertEqual(try RunExchange.decodeJSON(RunExchange.encodeJSON(expected)), expected)
    }

    func testMedicalJSONAndCSVPreserveValuesMissingnessAndQuotedText() throws {
        var record = SyntheticPatientRecord.example
        record.observedAt = Date()
        record.laboratory.ast = nil
        record.elastographyMethod = "Example, \"quoted\"\r\nsecond line"
        record.fibrosis = .init(system: "Example", stage: "F3", note: "comma, quote\" and\nnewline")
        record.events = [.init(occurredAt: Date(), kind: .other, note: "Synthetic, \"event\"\nnext")]
        XCTAssertEqual(try MedicalExchange.decodeJSON(MedicalExchange.encodeJSON([record])), [record])
        XCTAssertEqual(try MedicalExchange.decodeCSV(MedicalExchange.encodeCSV([record])), [record])
        XCTAssertEqual(try MedicalExchange.decodeCSV(MedicalExchange.encodeCSV([])), [])
    }

    func testCSVRejectsWrongUnitsNegativeNonfiniteAndMalformedQuotes() throws {
        let data = try MedicalExchange.encodeCSV([.example])
        let csv = String(decoding: data, as: UTF8.self)
        XCTAssertThrowsError(try MedicalExchange.decodeCSV(Data(csv.replacingOccurrences(of: "bilirubin_mg/dL", with: "bilirubin_umol/L").utf8)))
        var rows = try CSV.parse(data)
        for invalid in ["-1", "nan", "inf", "1e999", "bad"] {
            rows[1][3] = invalid
            let invalidCSV = rows.map { $0.map(CSV.quote).joined(separator: ",") }.joined(separator: "\r\n")
            XCTAssertThrowsError(try MedicalExchange.decodeCSV(Data(invalidCSV.utf8)))
        }
        XCTAssertThrowsError(try CSV.parse(Data("a,\"unterminated".utf8)))
        XCTAssertThrowsError(try CSV.parse(Data("a,\"closed\"junk".utf8)))
        XCTAssertThrowsError(try CSV.parse(Data("a,b\"c".utf8)))
    }

    func testCSVParserQuotedNewlinesAndEscapedQuotes() throws {
        let data = Data("first,second\r\n\"a,b\",\"quote\"\"\r\nnext\"\r\n".utf8)
        XCTAssertEqual(try CSV.parse(data), [["first", "second"], ["a,b", "quote\"\r\nnext"]])
        for field in ["a\r\nb", "a,\u{0301}b", "🙂\"\u{0301}b"] {
            XCTAssertEqual(try CSV.parse(Data(CSV.quote(field).utf8)), [[field]])
        }
    }

    func testMedicalImportRejectsRealFlagAndDuplicateIDs() throws {
        var real = SyntheticPatientRecord.example
        real.synthetic = false
        XCTAssertThrowsError(try MedicalExchange.encodeJSON([real]))
        XCTAssertThrowsError(try MedicalExchange.encodeCSV([real]))
        XCTAssertThrowsError(try MedicalExchange.encodeJSON([.example, .example]))
        let synthetic = try MedicalExchange.encodeJSON([.example])
        let tampered = try mutateJSON(synthetic) {
            var records = $0["records"] as! [[String: Any]]
            records[0]["synthetic"] = false
            $0["records"] = records
        }
        XCTAssertThrowsError(try MedicalExchange.decodeJSON(tampered))
    }

    func testMedicalJSONRejectsNegativeAndNonfiniteNumbers() throws {
        var record = SyntheticPatientRecord.example
        record.laboratory.sodium = -1
        XCTAssertThrowsError(try MedicalExchange.encodeJSON([record]))
        record.laboratory.sodium = .nan
        XCTAssertThrowsError(try MedicalExchange.encodeJSON([record]))
        let valid = try MedicalExchange.encodeJSON([.example])
        let invalid = try mutateJSON(valid) {
            var records = $0["records"] as! [[String: Any]]
            var labs = records[0]["laboratory"] as! [String: Any]
            labs["alt"] = -1
            records[0]["laboratory"] = labs
            $0["records"] = records
        }
        XCTAssertThrowsError(try MedicalExchange.decodeJSON(invalid))
    }

    func testCSVFreeTextCannotBecomeSpreadsheetFormula() throws {
        var record = SyntheticPatientRecord.example
        record.elastographyMethod = "=HYPERLINK(\"https://invalid.example\")"
        let data = try MedicalExchange.encodeCSV([record])
        let rows = try CSV.parse(data)
        XCTAssertTrue(rows[1][14].hasPrefix("\""))
        XCTAssertEqual(try MedicalExchange.decodeCSV(data), [record])
    }
}
