import Foundation

/// Units are fixed by the exchange contract, never inferred from magnitudes.
public struct LaboratoryValues: Codable, Equatable, Sendable {
    public var alt, ast, ggt, ap, bilirubin, albumin, inr, platelets, creatinine, sodium: Double?

    public init(alt: Double? = nil, ast: Double? = nil, ggt: Double? = nil, ap: Double? = nil,
                bilirubin: Double? = nil, albumin: Double? = nil, inr: Double? = nil,
                platelets: Double? = nil, creatinine: Double? = nil, sodium: Double? = nil) {
        self.alt = alt; self.ast = ast; self.ggt = ggt; self.ap = ap; self.bilirubin = bilirubin
        self.albumin = albumin; self.inr = inr; self.platelets = platelets
        self.creatinine = creatinine; self.sodium = sodium
    }

    var ordered: [Double?] { [alt, ast, ggt, ap, bilirubin, albumin, inr, platelets, creatinine, sodium] }
}

public struct FibrosisFinding: Codable, Equatable, Sendable {
    public var system, stage, note: String
    public init(system: String, stage: String, note: String = "") {
        self.system = system; self.stage = stage; self.note = note
    }
}

public struct ClinicalEvent: Codable, Equatable, Sendable, Identifiable {
    public enum Kind: String, Codable, Sendable { case ascites, varicealBleeding, encephalopathy, infection, other }
    public let id: UUID
    public var occurredAt: Date
    public var kind: Kind
    public var note: String

    public init(id: UUID = UUID(), occurredAt: Date, kind: Kind, note: String = "") {
        self.id = id; self.occurredAt = occurredAt; self.kind = kind; self.note = note
    }
}

public struct SyntheticPatientRecord: Codable, Equatable, Sendable, Identifiable {
    public let id: UUID
    public var synthetic: Bool
    public var observedAt: Date
    public var laboratory: LaboratoryValues
    public var elastographyKPa: Double?
    public var elastographyMethod: String?
    public var fibrosis: FibrosisFinding?
    public var events: [ClinicalEvent]

    public init(id: UUID = UUID(), observedAt: Date, laboratory: LaboratoryValues = .init(),
                elastographyKPa: Double? = nil, elastographyMethod: String? = nil,
                fibrosis: FibrosisFinding? = nil, events: [ClinicalEvent] = []) {
        self.id = id; self.synthetic = true; self.observedAt = observedAt; self.laboratory = laboratory
        self.elastographyKPa = elastographyKPa; self.elastographyMethod = elastographyMethod
        self.fibrosis = fibrosis; self.events = events
    }

    public static let example = SyntheticPatientRecord(
        id: UUID(uuidString: "00000000-0000-0000-0000-000000000001")!,
        observedAt: Date(timeIntervalSince1970: 0),
        laboratory: .init(alt: 75, ast: 90, ggt: 110, ap: 130, bilirubin: 1.6,
                          albumin: 3.5, inr: 1.2, platelets: 125, creatinine: 0.9, sodium: 138),
        elastographyKPa: 14, elastographyMethod: "Synthetic example; no measured subject",
        fibrosis: .init(system: "METAVIR", stage: "F3", note: "Invented example, not inferred from elastography"))
}

public enum MedicalExchange {
    public static let maximumRecords = 10_000
    public static let csvHeader = ["id", "synthetic", "observed_at_reference_seconds", "ALT_U/L", "AST_U/L",
        "GGT_U/L", "AP_U/L", "bilirubin_mg/dL", "albumin_g/dL", "INR_1", "platelets_10^9/L",
        "creatinine_mg/dL", "sodium_mmol/L", "elastography_kPa", "elastography_method_json",
        "fibrosis_json", "events_json"]
    private struct Envelope: Codable {
        let schemaVersion: Int
        let dataKind: String
        let records: [SyntheticPatientRecord]
    }

    public static func encodeJSON(_ records: [SyntheticPatientRecord]) throws -> Data {
        try validate(records)
        return try ResearchJSON.encode(Envelope(schemaVersion: 1, dataKind: "synthetic-medical", records: records))
    }

    public static func decodeJSON(_ data: Data) throws -> [SyntheticPatientRecord] {
        let envelope = try ResearchJSON.decode(Envelope.self, from: data)
        guard envelope.schemaVersion == 1 else { throw StorageError.unsupportedSchema(envelope.schemaVersion) }
        guard envelope.dataKind == "synthetic-medical" else { throw StorageError.invalid("synthetic medical data required") }
        try validate(envelope.records)
        return envelope.records
    }

    public static func encodeCSV(_ records: [SyntheticPatientRecord]) throws -> Data {
        try validate(records)
        var rows = [csvHeader.joined(separator: ",")]
        for record in records {
            var fields = [record.id.uuidString, "true", String(record.observedAt.timeIntervalSinceReferenceDate)]
            fields += record.laboratory.ordered.map { $0.map { String($0) } ?? "" }
            fields.append(record.elastographyKPa.map { String($0) } ?? "")
            // JSON cells preserve free text and keep spreadsheet formulas from becoming executable cells.
            fields.append(try jsonCell(record.elastographyMethod))
            fields.append(try jsonCell(record.fibrosis))
            fields.append(try jsonCell(record.events))
            guard fields.allSatisfy({ $0.utf8.count <= 65_536 }) else { throw StorageError.invalid("CSV field limit") }
            rows.append(fields.map(CSV.quote).joined(separator: ","))
        }
        let data = Data((rows.joined(separator: "\r\n") + "\r\n").utf8)
        guard data.count <= RunExchange.maximumBytes else { throw StorageError.invalid("CSV exceeds size limit") }
        return data
    }

    public static func decodeCSV(_ data: Data) throws -> [SyntheticPatientRecord] {
        let rows = try CSV.parse(data)
        guard rows.first == csvHeader else { throw StorageError.invalid("CSV header or units do not match schema 1") }
        var records: [SyntheticPatientRecord] = []
        for row in rows.dropFirst() {
            guard row.count == csvHeader.count, let id = UUID(uuidString: row[0]), row[1] == "true",
                  let timestamp = Double(row[2]), timestamp.isFinite else {
                throw StorageError.invalid("CSV identity, synthetic flag, date, or column count")
            }
            let values = try row[3...13].map { field -> Double? in
                if field.isEmpty { return nil }
                guard let value = Double(field), value.isFinite, value >= 0 else { throw StorageError.invalid("CSV numeric value") }
                return value
            }
            let laboratory = LaboratoryValues(alt: values[0], ast: values[1], ggt: values[2], ap: values[3],
                bilirubin: values[4], albumin: values[5], inr: values[6], platelets: values[7],
                creatinine: values[8], sodium: values[9])
            let method = try ResearchJSON.decode(String?.self, from: Data(row[14].utf8))
            let fibrosis = try ResearchJSON.decode(FibrosisFinding?.self, from: Data(row[15].utf8))
            let events = try ResearchJSON.decode([ClinicalEvent].self, from: Data(row[16].utf8))
            records.append(.init(id: id, observedAt: Date(timeIntervalSinceReferenceDate: timestamp), laboratory: laboratory,
                                 elastographyKPa: values[10], elastographyMethod: method, fibrosis: fibrosis, events: events))
        }
        try validate(records)
        return records
    }

    private static func jsonCell<T: Encodable>(_ value: T) throws -> String {
        String(decoding: try ResearchJSON.encode(value), as: UTF8.self)
    }

    private static func validate(_ records: [SyntheticPatientRecord]) throws {
        guard records.count <= maximumRecords, Set(records.map(\.id)).count == records.count else {
            throw StorageError.invalid("record count or duplicate IDs")
        }
        for record in records {
            guard record.synthetic, record.observedAt.timeIntervalSince1970.isFinite else {
                throw StorageError.invalid("synthetic data and finite observation time required")
            }
            guard (record.laboratory.ordered + [record.elastographyKPa]).compactMap({ $0 })
                .allSatisfy({ $0.isFinite && $0 >= 0 }) else { throw StorageError.invalid("negative or nonfinite measurement") }
            guard (record.elastographyMethod?.utf8.count ?? 0) <= 512, record.events.count <= 100,
                  Set(record.events.map(\.id)).count == record.events.count else { throw StorageError.invalid("method or events limit") }
            if let fibrosis = record.fibrosis {
                guard !fibrosis.system.isEmpty, !fibrosis.stage.isEmpty, fibrosis.system.utf8.count <= 128,
                      fibrosis.stage.utf8.count <= 64, fibrosis.note.utf8.count <= 4_096 else {
                    throw StorageError.invalid("fibrosis finding")
                }
            }
            guard record.events.allSatisfy({ $0.occurredAt.timeIntervalSince1970.isFinite && $0.note.utf8.count <= 4_096 }) else {
                throw StorageError.invalid("event date or note")
            }
        }
    }
}
