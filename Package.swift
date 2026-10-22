// swift-tools-version: 6.0
import PackageDescription

let package = Package(
    name: "HepatoSimResearch",
    platforms: [.macOS(.v14), .iOS(.v17)],
    products: [
        .library(name: "HepatoCore", targets: ["HepatoCore"]),
        .library(name: "HepatoStorage", targets: ["HepatoStorage"]),
        .library(name: "HepatoUI", targets: ["HepatoUI"]),
        .executable(name: "HepatoSimResearch", targets: ["HepatoSimApp"]),
        .executable(name: "hepatosim", targets: ["HepatoCLI"])
    ],
    targets: [
        .systemLibrary(name: "CSQLite", pkgConfig: "sqlite3"),
        .target(name: "HepatoCore", resources: [.process("Resources")]),
        .target(name: "HepatoStorage", dependencies: ["HepatoCore", "CSQLite"]),
        .target(name: "HepatoUI", dependencies: ["HepatoCore", "HepatoStorage"]),
        .executableTarget(name: "HepatoSimApp", dependencies: ["HepatoUI"]),
        .executableTarget(name: "HepatoCLI", dependencies: ["HepatoCore", "HepatoStorage"]),
        .testTarget(name: "HepatoCoreTests", dependencies: ["HepatoCore"]),
        .testTarget(name: "HepatoStorageTests", dependencies: ["HepatoStorage"]),
        .testTarget(name: "HepatoUITests", dependencies: ["HepatoUI"])
    ]
)
