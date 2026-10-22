import Foundation

/// Only explicitly selected research context belongs in a provider request.
public struct AIResearchRequest: Sendable {
    public let question: String
    public let context: String
    public let relatedRunIDs: [UUID]

    public init(question: String, context: String, relatedRunIDs: [UUID] = []) {
        self.question = question
        self.context = context
        self.relatedRunIDs = relatedRunIDs
    }
}

/// Provider text is unreviewed content, separate from mathematical simulation results.
public struct AIResearchHypotheses: Sendable {
    public let providerID: String
    public let modelID: String
    public let generatedAt: Date
    public let hypotheses: [String]
    public let sourceURLs: [URL]
    public let limitations: [String]
    public let isMedicallyValidated = false

    public init(
        providerID: String,
        modelID: String,
        generatedAt: Date,
        hypotheses: [String],
        sourceURLs: [URL],
        limitations: [String]
    ) {
        self.providerID = providerID
        self.modelID = modelID
        self.generatedAt = generatedAt
        self.hypotheses = hypotheses
        self.sourceURLs = sourceURLs
        self.limitations = limitations
    }
}

/// Adapters must obtain explicit context-export authorization before network use.
/// No external provider or automatic network call is included in the prototype.
public protocol ResearchAIProvider: Sendable {
    var identifier: String { get }
    func analyze(_ request: AIResearchRequest) async throws -> AIResearchHypotheses
}
