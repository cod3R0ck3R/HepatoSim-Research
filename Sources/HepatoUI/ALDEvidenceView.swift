import SwiftUI
import UniformTypeIdentifiers
import HepatoCore

struct ALDEvidenceView: View {
    @State private var catalog: EvidenceCatalog?
    @State private var error: String?
    @State private var exporting = false
    @State private var document = ResearchDocument(data: Data())

    var body: some View {
        VStack(alignment: .leading, spacing: 20) {
            HStack {
                VStack(alignment: .leading, spacing: 6) {
                    Text("Alkoholassoziierte Lebererkrankung").font(.title2.weight(.semibold))
                    Text("Publizierte Studienbefunde · eigenständige Evidenzebene")
                        .font(.subheadline).foregroundStyle(.blue)
                }
                Spacer()
                Button("Evidenz exportieren", systemImage: "square.and.arrow.up") { export() }
                    .disabled(catalog == nil)
            }
            Text("Hier stehen beobachtete Studienergebnisse mit Quelle und Nenner. Sie sind von den synthetischen ODE-Verläufen getrennt. Klinische Rekompensation ist kein direkter Messwert des modellierten Fibroseindex.")
            if let catalog {
                Text("\(catalog.records.count) Quellen · Stand \(catalog.retrievedAt) · ODE-Raten bisher nicht klinisch kalibriert")
                    .font(.caption.monospaced()).foregroundStyle(.secondary)
                ForEach(catalog.records) { record in
                    study(record)
                }
                VStack(alignment: .leading, spacing: 9) {
                    Text("Was fehlt für quantitative Modellvorhersagen?").font(.headline)
                    Text("Messbare Beobachtungsgrößen, longitudinale Daten mit Zeitpunkten und Unsicherheiten, eine definierte Zuordnung zu den Modellzuständen sowie getrennte Kalibrierungs- und Validierungskohorten. Ein Rekompensationsanteil allein bestimmt keine Kollagen-Abbaurate.")
                    Text("Es werden keine sich möglicherweise überschneidenden Kohorten zusammengefasst. Wilson-Intervalle beschreiben nur Zählerunsicherheit; Zensierung, Confounding und Selektion sind darin nicht berücksichtigt.")
                        .foregroundStyle(.secondary)
                }.padding(20).background(.blue.opacity(0.06), in: RoundedRectangle(cornerRadius: 12))
            } else if let error {
                ContentUnavailableView("Evidenz nicht verfügbar", systemImage: "exclamationmark.triangle", description: Text(error))
            } else { ProgressView("Quellenkatalog laden") }
        }
        .task {
            do { catalog = try EvidenceCatalog.loadBundled() }
            catch { self.error = error.localizedDescription }
        }
        .fileExporter(isPresented: $exporting, document: document, contentType: .json,
                      defaultFilename: "HepatoSim-ALD-Evidenz") { result in
            if case .failure(let failure) = result { error = failure.localizedDescription }
        }
        .alert("Export nicht abgeschlossen", isPresented: Binding(get: { error != nil && catalog != nil },
            set: { if !$0 { error = nil } })) { Button("OK") { error = nil } } message: { Text(error ?? "") }
    }

    private func study(_ record: EvidenceRecord) -> some View {
        VStack(alignment: .leading, spacing: 14) {
            Text("\(record.authors.first ?? "") · \(String(record.year))").font(.caption.weight(.semibold)).foregroundStyle(.blue)
            Text(record.title).font(.headline).textSelection(.enabled)
            Text(record.studyDesign).font(.subheadline.weight(.medium))
            Text(record.population).font(.callout).foregroundStyle(.secondary)
            ForEach(record.findings) { finding in
                VStack(alignment: .leading, spacing: 8) {
                    Text(finding.endpoint).font(.subheadline.weight(.semibold))
                    if let proportion = try? finding.observedProportion() {
                        HStack(alignment: .firstTextBaseline, spacing: 14) {
                            Text(proportion.fraction, format: .percent.precision(.fractionLength(1)))
                                .font(.system(size: 32, weight: .semibold, design: .rounded)).foregroundStyle(.blue)
                            Text("\(proportion.events) / \(proportion.total) beobachtet")
                                .font(.callout.monospacedDigit())
                        }
                        Text("Deskriptives 95%-Wilson-Intervall: \(proportion.lower95.formatted(.percent.precision(.fractionLength(1))))–\(proportion.upper95.formatted(.percent.precision(.fractionLength(1)))). Keine feste Zeitprognose; nicht für Zensierung adjustiert.")
                            .font(.caption).foregroundStyle(.secondary)
                    }
                    Text(finding.summary).font(.callout)
                    Text(finding.followUp).font(.caption).foregroundStyle(.secondary)
                }
                .padding(14).frame(maxWidth: .infinity, alignment: .leading)
                .background(.blue.opacity(0.055), in: RoundedRectangle(cornerRadius: 10))
            }
            DisclosureGroup("Modellbezug und Grenzen") {
                VStack(alignment: .leading, spacing: 10) {
                    Text(record.exposureOrMechanism)
                    Text(record.modelRelevance)
                    Text(record.parameterImplication).fontWeight(.medium)
                    ForEach(record.limitations, id: \.self) { Text("• " + $0).foregroundStyle(.secondary) }
                }.font(.callout).padding(.top, 8)
            }
            if let url = URL(string: record.url) {
                Link("Originalquelle · DOI \(record.doi)", destination: url)
                    .font(.callout).accessibilityLabel("Originalquelle zu \(record.title)")
            }
        }
        .padding(20)
        .background(.background, in: RoundedRectangle(cornerRadius: 14))
        .overlay { RoundedRectangle(cornerRadius: 14).stroke(.blue.opacity(0.16)) }
    }

    private func export() {
        guard let catalog else { return }
        do {
            let encoder = JSONEncoder()
            encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
            document = ResearchDocument(data: try encoder.encode(catalog))
            exporting = true
        } catch { self.error = error.localizedDescription }
    }
}
