import Foundation

public enum EvidenceError: Error, LocalizedError, Equatable {
    case invalid(String)
    case missingResource

    public var errorDescription: String? {
        switch self {
        case .invalid(let reason): return "Ungültige Evidenzdaten: \(reason)"
        case .missingResource: return "Der gebündelte ALD-Evidenzkatalog fehlt. Es werden keine Ersatzdaten erzeugt."
        }
    }
}

/// Describes published aggregate counts, never a simulated outcome or individual prognosis.
public struct ObservedProportion: Equatable, Sendable {
    public let events: Int
    public let total: Int
    public let fraction: Double
    public let lower95: Double
    public let upper95: Double

    private init(events: Int, total: Int, fraction: Double, lower95: Double, upper95: Double) {
        self.events = events; self.total = total; self.fraction = fraction
        self.lower95 = lower95; self.upper95 = upper95
    }

    /// Two-sided Wilson score interval, z = Φ⁻¹(0.975), without continuity correction.
    /// Sampling uncertainty only: no adjustment for censoring, confounding, or selection.
    /// Reference: https://www.itl.nist.gov/div898/handbook/prc/section2/prc241.htm
    public static func wilson(events: Int, total: Int) throws -> ObservedProportion {
        guard total > 0, events >= 0, events <= total else { throw EvidenceError.invalid("Ereigniszähler/Nenner") }
        let n = Double(total), p = Double(events) / Double(total), z = 1.959963984540054
        let correction = z * z / n
        let centre = (p + correction / 2) / (1 + correction)
        let halfWidth = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + correction)
        return .init(events: events, total: total, fraction: p,
                     lower95: max(0, centre - halfWidth), upper95: min(1, centre + halfWidth))
    }
}

public struct EvidenceFinding: Codable, Equatable, Sendable, Identifiable {
    public enum Kind: String, Codable, Sendable {
        case crudeObservedProportion
        case reportedTimeToEventEstimate
        case reportedContinuousOutcome
        case qualitativeFinding
    }

    public let id: String
    public let endpoint: String
    public let kind: Kind
    public let events: Int?
    public let total: Int?
    public let followUp: String
    public let summary: String

    public func observedProportion() throws -> ObservedProportion? {
        guard kind == .crudeObservedProportion else {
            guard events == nil, total == nil else { throw EvidenceError.invalid("Dieser Endpunkttyp ist kein binomialer Zähler") }
            return nil
        }
        guard let events, let total else { throw EvidenceError.invalid("Fehlender publizierter Zähler oder Nenner") }
        return try .wilson(events: events, total: total)
    }
}

public struct EvidenceRecord: Codable, Equatable, Sendable, Identifiable {
    public let id: String
    public let title: String
    /// A bibliographic short author list may end in "et al."; it is not a claim of complete authorship.
    public let authors: [String]
    public let year: Int
    public let doi: String
    public let url: String
    public let studyDesign: String
    public let population: String
    public let exposureOrMechanism: String
    public let findings: [EvidenceFinding]
    public let limitations: [String]
    public let modelRelevance: String
    public let parameterImplication: String
    public let modelIDs: [String]
}

public struct EvidenceCatalog: Codable, Equatable, Sendable {
    public let schemaVersion: Int
    public let retrievedAt: String
    public let evidenceKind: String
    public let calibrationStatus: String
    public let scope: String
    public let records: [EvidenceRecord]

    public static func loadBundled() throws -> EvidenceCatalog {
        guard let url = Bundle.module.url(forResource: "ald-evidence", withExtension: "json") else {
            throw EvidenceError.missingResource
        }
        return try decode(Data(contentsOf: url))
    }

    public static func decode(_ data: Data) throws -> EvidenceCatalog {
        guard !data.isEmpty, data.count <= 1_048_576 else { throw EvidenceError.invalid("Dateigröße") }
        let catalog = try JSONDecoder().decode(EvidenceCatalog.self, from: data)
        try catalog.validate()
        return catalog
    }

    public func validate() throws {
        guard schemaVersion == 1, retrievedAt == "2026-10-22",
              evidenceKind == "published-aggregate-observations", calibrationStatus == "not-calibrated",
              !scope.isEmpty else { throw EvidenceError.invalid("Katalogversion, Abrufdatum oder Herkunft") }
        guard !records.isEmpty, records.count <= 100, Set(records.map(\.id)).count == records.count,
              Set(records.map { $0.doi.lowercased() }).count == records.count else {
            throw EvidenceError.invalid("Studienzahl oder doppelte Studien-ID")
        }
        for record in records {
            guard Self.identifier(record.id), (1900...2026).contains(record.year),
                  record.doi.range(of: #"^10\.[0-9]{4,9}/[^\s]+$"#, options: .regularExpression) != nil,
                  let source = URLComponents(string: record.url), source.scheme == "https",
                  let host = source.host, !host.isEmpty, source.user == nil, source.password == nil,
                  !record.authors.isEmpty, record.authors.allSatisfy({ !$0.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty }),
                  !record.limitations.isEmpty, !record.modelIDs.isEmpty,
                  record.modelIDs.allSatisfy({ $0 == "hepatosim.liver-ode@0.1.0" }) else {
                throw EvidenceError.invalid("Studienprovenienz für \(record.id)")
            }
            let descriptions = [record.title, record.studyDesign, record.population, record.exposureOrMechanism,
                                record.modelRelevance, record.parameterImplication] + record.limitations
            guard descriptions.allSatisfy({ !$0.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty && $0.utf8.count <= 8_192 }),
                  !record.findings.isEmpty, record.findings.count <= 30,
                  Set(record.findings.map(\.id)).count == record.findings.count else {
                throw EvidenceError.invalid("Studienbeschreibung oder Endpunkte für \(record.id)")
            }
            for finding in record.findings {
                guard Self.identifier(finding.id), [finding.endpoint, finding.followUp, finding.summary]
                    .allSatisfy({ !$0.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty && $0.utf8.count <= 8_192 }) else {
                    throw EvidenceError.invalid("Endpunktbeschreibung")
                }
                _ = try finding.observedProportion()
            }
        }
    }

    private static func identifier(_ value: String) -> Bool {
        value.range(of: #"^[a-z][a-z0-9-]{0,79}$"#, options: .regularExpression) != nil
    }
}
