import Foundation
import SwiftUI

enum DecimalEntry {
    static func parse(_ text: String, in range: ClosedRange<Double>) -> Double? {
        let normalized = text.trimmingCharacters(in: .whitespacesAndNewlines)
            .replacingOccurrences(of: ",", with: ".")
        guard !normalized.isEmpty,
              normalized.unicodeScalars.allSatisfy({ "0123456789+-.eE".unicodeScalars.contains($0) }),
              let number = Double(normalized), number.isFinite, range.contains(number) else { return nil }
        return number
    }

    static func string(_ number: Double) -> String {
        String(number).replacingOccurrences(of: ".", with: Locale.current.decimalSeparator ?? ".")
    }
}

struct ParameterEdits {
    var text: [String: String] = [:]
    var invalid: Set<String> = []

    mutating func update(_ raw: String, for label: String, range: ClosedRange<Double>) -> Double? {
        text[label] = raw
        guard let number = DecimalEntry.parse(raw, in: range) else {
            invalid.insert(label)
            return nil
        }
        invalid.remove(label)
        return number
    }

    mutating func reset(_ label: String) {
        text.removeValue(forKey: label)
        invalid.remove(label)
    }
}

struct ParameterControl: View {
    let label: String
    @Binding var value: Double
    let range: ClosedRange<Double>
    @Binding var edits: ParameterEdits
    @FocusState.Binding var focusedField: String?
    let fieldOrder: [String]

    static func adjacentField(_ field: String, in order: [String], backwards: Bool) -> String? {
        guard let index = order.firstIndex(of: field) else { return nil }
        let next = index + (backwards ? -1 : 1)
        return order.indices.contains(next) ? order[next] : nil
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            HStack(alignment: .firstTextBaseline, spacing: 10) {
                Text(label).font(.caption)
                Spacer(minLength: 0)
                TextField(label, text: Binding(
                    get: { edits.text[label] ?? DecimalEntry.string(value) },
                    set: { raw in
                        if let number = edits.update(raw, for: label, range: range) { value = number }
                    }))
                    .textFieldStyle(.roundedBorder)
                    .focused($focusedField, equals: label)
                    .onKeyPress(phases: .down) { key in
                        let backtab = KeyEquivalent("\u{19}")
                        guard key.key == .tab || key.key == backtab else { return .ignored }
                        guard let next = Self.adjacentField(label, in: fieldOrder, backwards: key.modifiers.contains(.shift) || key.key == backtab) else { return .ignored }
                        focusedField = next
                        return .handled
                    }
                    .multilineTextAlignment(.trailing)
                    .font(.callout.monospacedDigit())
                    .frame(width: 116)
                    .accessibilityLabel("\(label), Zahlenwert")
                    .accessibilityHint("Dezimalkomma oder Dezimalpunkt; Tab zum nächsten Feld")
                    .overlay { RoundedRectangle(cornerRadius: 5).stroke(edits.invalid.contains(label) ? Color.red : .clear) }
            }
            // Continuous sliders avoid thousands of automatic tick labels on recent macOS versions.
            Slider(value: Binding(get: { value }, set: { number in
                edits.reset(label)
                value = number
            }), in: range) { Text(label) }
                .labelsHidden().accessibilityLabel(label)
            if edits.invalid.contains(label) {
                Text("Zahl zwischen \(DecimalEntry.string(range.lowerBound)) und \(DecimalEntry.string(range.upperBound)) eingeben.")
                    .font(.caption2).foregroundStyle(.red)
            }
        }
        .id(label)
    }
}
