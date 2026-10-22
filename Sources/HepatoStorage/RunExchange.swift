import Foundation
import HepatoCore

public enum StorageError: Error, LocalizedError, Equatable {
    case invalid(String)
    case unsupportedSchema(Int)
    case unsupportedModel(String)
    case duplicateRun
    case database(String)

    public var errorDescription: String? {
        switch self {
        case .invalid(let reason): return "Invalid research data: \(reason)"
        case .unsupportedSchema(let version): return "Unsupported data schema: \(version)"
        case .unsupportedModel(let version): return "Unsupported model version: \(version)"
        case .duplicateRun: return "This run ID already exists. Existing results were not overwritten."
        case .database(let reason): return "Local database error: \(reason)"
        }
    }
}

public enum RunExchange {
    public static let maximumBytes = 16 * 1024 * 1024
    private struct Envelope: Codable {
        let schemaVersion: Int
        let dataKind: String
        let run: SimulationRun
    }

    public static func encodeJSON(_ run: SimulationRun) throws -> Data {
        try validate(run)
        return try ResearchJSON.encode(Envelope(schemaVersion: 1, dataKind: "synthetic-research", run: run))
    }

    public static func decodeJSON(_ data: Data) throws -> SimulationRun {
        let envelope = try ResearchJSON.decode(Envelope.self, from: data)
        guard envelope.schemaVersion == 1 else { throw StorageError.unsupportedSchema(envelope.schemaVersion) }
        guard envelope.dataKind == "synthetic-research" else { throw StorageError.invalid("synthetic research data required") }
        try validate(envelope.run)
        let reproduced = try LiverSimulator.run(envelope.run.configuration)
        guard reproduced.samples.count == envelope.run.samples.count,
              zip(reproduced.samples, envelope.run.samples).allSatisfy({ expected, actual in
                  let lhs = expected.state, rhs = actual.state
                  return abs(expected.day - actual.day) <= 1e-9 &&
                      zip([lhs.hepatocytes, lhs.inflammation, lhs.stellate, lhs.fibrosis],
                          [rhs.hepatocytes, rhs.inflammation, rhs.stellate, rhs.fibrosis])
                          .allSatisfy { abs($0 - $1) <= 1e-10 }
              }) else { throw StorageError.invalid("samples do not reproduce from their recorded configuration") }
        return envelope.run
    }

    public static func exportCSV(_ run: SimulationRun) throws -> Data {
        try validate(run)
        let header = "run_id,model_version,day,hepatocytes_fraction,inflammation_fraction,stellate_fraction,fibrosis_fraction,reserve_fraction,portal_resistance_relative,alt_proxy_U/L,bilirubin_proxy_mg/dL,albumin_proxy_g/dL,inr_proxy\r\n"
        let rows = run.samples.map { sample in
            ([run.id.uuidString, run.modelVersion] + [sample.day, sample.state.hepatocytes,
                sample.state.inflammation, sample.state.stellate, sample.state.fibrosis,
                sample.reserve, sample.portalResistance, sample.alt, sample.bilirubin,
                sample.albumin, sample.inr].map { String($0) }).map(CSV.quote).joined(separator: ",")
        }.joined(separator: "\r\n")
        let data = Data((header + rows + "\r\n").utf8)
        guard data.count <= maximumBytes else { throw StorageError.invalid("CSV exceeds size limit") }
        return data
    }

    static func validate(_ run: SimulationRun) throws {
        guard run.modelVersion == LiverSimulator.modelVersion else { throw StorageError.unsupportedModel(run.modelVersion) }
        guard run.createdAt.timeIntervalSince1970.isFinite else { throw StorageError.invalid("creation time") }
        try run.configuration.validate()
        guard !run.samples.isEmpty, run.samples.count <= 100_001 else { throw StorageError.invalid("sample count") }
        guard run.samples.first?.day == 0, run.samples.first?.state == run.configuration.initial,
              abs((run.samples.last?.day ?? -1) - run.configuration.durationDays) < 1e-8 else {
            throw StorageError.invalid("sample endpoints")
        }
        var previous = -Double.infinity
        for (index, sample) in run.samples.enumerated() {
            guard sample.day.isFinite, sample.day >= 0, sample.day > previous,
                  sample.day <= run.configuration.durationDays + 1e-8,
                  abs(sample.day - min(Double(index) * run.configuration.sampleEveryDays,
                                       run.configuration.durationDays)) <= 1e-9 else {
                throw StorageError.invalid("sample time order")
            }
            let state = sample.state
            guard [state.hepatocytes, state.inflammation, state.stellate, state.fibrosis]
                .allSatisfy({ $0.isFinite && (0...1).contains($0) }) else {
                throw StorageError.invalid("state must be finite and normalized")
            }
            guard [sample.reserve, sample.portalResistance, sample.alt, sample.bilirubin, sample.albumin, sample.inr]
                .allSatisfy({ $0.isFinite && $0 >= 0 }) else { throw StorageError.invalid("derived values") }
            previous = sample.day
        }
    }
}

enum ResearchJSON {
    static func encode<T: Encodable>(_ value: T) throws -> Data {
        let encoder = JSONEncoder()
        encoder.outputFormatting = [.sortedKeys]
        encoder.dateEncodingStrategy = .deferredToDate
        let data = try encoder.encode(value)
        guard data.count <= RunExchange.maximumBytes else { throw StorageError.invalid("JSON exceeds size limit") }
        return data
    }

    static func decode<T: Decodable>(_ type: T.Type, from data: Data) throws -> T {
        guard !data.isEmpty, data.count <= RunExchange.maximumBytes else { throw StorageError.invalid("JSON size") }
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .deferredToDate
        return try decoder.decode(type, from: data)
    }
}

enum CSV {
    static func quote(_ field: String) -> String {
        field.unicodeScalars.contains(where: { $0 == "," || $0 == "\"" || $0 == "\r" || $0 == "\n" })
            ? "\"" + field.replacingOccurrences(of: "\"", with: "\"\"", options: .literal) + "\"" : field
    }

    static func parse(_ data: Data) throws -> [[String]] {
        guard data.count <= RunExchange.maximumBytes, let text = String(data: data, encoding: .utf8), !text.isEmpty else {
            throw StorageError.invalid("CSV size or UTF-8 encoding")
        }
        let characters = Array(text.unicodeScalars)
        var rows: [[String]] = [], row: [String] = [], field = ""
        var quoted = false, closedQuote = false, index = 0
        func finishRow() throws {
            row.append(field); rows.append(row); row = []; field = ""; closedQuote = false
            guard rows.count <= 10_001 else { throw StorageError.invalid("too many CSV records") }
        }
        while index < characters.count {
            let character = characters[index]
            if quoted {
                if character == "\"" {
                    if index + 1 < characters.count, characters[index + 1] == "\"" { field.append("\""); index += 1 }
                    else { quoted = false; closedQuote = true }
                } else { field.unicodeScalars.append(character) }
            } else if character == "," {
                row.append(field); field = ""; closedQuote = false
            } else if character == "\n" || character == "\r" {
                if character == "\r", index + 1 < characters.count, characters[index + 1] == "\n" { index += 1 }
                try finishRow()
            } else if character == "\"", field.isEmpty, !closedQuote {
                quoted = true
            } else {
                guard character != "\"", !closedQuote else { throw StorageError.invalid("CSV quotation") }
                field.unicodeScalars.append(character)
            }
            guard field.utf8.count <= 65_536, row.count <= 32 else { throw StorageError.invalid("CSV field limit") }
            index += 1
        }
        guard !quoted else { throw StorageError.invalid("unterminated CSV quote") }
        if !field.isEmpty || !row.isEmpty || closedQuote { try finishRow() }
        return rows
    }
}
