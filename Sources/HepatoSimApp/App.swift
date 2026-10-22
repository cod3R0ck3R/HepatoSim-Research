import SwiftUI
import HepatoUI
#if os(macOS)
import AppKit
#endif

@main
struct HepatoSimApp: App {
    init() {
        #if os(macOS)
        NSApplication.shared.setActivationPolicy(.regular)
        #endif
    }

    var body: some Scene {
        WindowGroup("HepatoSim Research") {
            ResearchDashboard()
                #if os(macOS)
                .frame(minWidth: 1000, minHeight: 720)
                .onAppear { NSApplication.shared.activate(ignoringOtherApps: true) }
                #endif
        }
        #if os(macOS)
        .defaultSize(width: 1380, height: 900)
        #endif
    }
}
