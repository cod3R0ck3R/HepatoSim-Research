import Foundation
import HepatoCore
import CSQLite
import Darwin

/// Owns one connection. All post-initialization access is confined to RunStore's actor.
private final class SQLiteConnection {
    let handle: OpaquePointer

    init(path: String) throws {
        var opened: OpaquePointer?
        let result = sqlite3_open_v2(path, &opened, SQLITE_OPEN_CREATE | SQLITE_OPEN_READWRITE | SQLITE_OPEN_FULLMUTEX | SQLITE_OPEN_NOFOLLOW, nil)
        guard result == SQLITE_OK, let opened else {
            let message = opened.map { "\(String(cString: sqlite3_errmsg($0))) (SQLite \(sqlite3_extended_errcode($0)), system \(sqlite3_system_errno($0)))" } ?? "Could not open database"
            if let opened { sqlite3_close(opened) }
            throw StorageError.database(message)
        }
        handle = opened
        sqlite3_busy_timeout(handle, 5_000)
    }

    deinit { sqlite3_close(handle) }

    func execute(_ sql: String) throws {
        guard sqlite3_exec(handle, sql, nil, nil, nil) == SQLITE_OK else { throw error() }
    }

    func prepare(_ sql: String) throws -> OpaquePointer {
        var statement: OpaquePointer?
        guard sqlite3_prepare_v2(handle, sql, -1, &statement, nil) == SQLITE_OK, let statement else { throw error() }
        return statement
    }

    func integer(_ sql: String) throws -> Int {
        let statement = try prepare(sql)
        defer { sqlite3_finalize(statement) }
        guard sqlite3_step(statement) == SQLITE_ROW else { throw error() }
        return Int(sqlite3_column_int(statement, 0))
    }

    func error() -> StorageError { .database(String(cString: sqlite3_errmsg(handle))) }

    func bind(_ value: String, to index: Int32, in statement: OpaquePointer) throws {
        let result = value.withCString { sqlite3_bind_text(statement, index, $0, -1, unsafeBitCast(-1, to: sqlite3_destructor_type.self)) }
        guard result == SQLITE_OK else { throw error() }
    }
}

public actor RunStore {
    private let connection: SQLiteConnection

    public init(url: URL) throws {
        guard url.isFileURL else { throw StorageError.invalid("local database URL required") }
        let fileManager = FileManager.default
        let directory = url.deletingLastPathComponent()
        if fileManager.fileExists(atPath: directory.path) {
            let directoryAttributes = try fileManager.attributesOfItem(atPath: directory.path)
            guard directoryAttributes[.type] as? FileAttributeType == .typeDirectory else {
                throw StorageError.invalid("database directory must not be a symlink")
            }
            guard let mode = directoryAttributes[.posixPermissions] as? NSNumber, mode.intValue & 0o077 == 0 else {
                throw StorageError.invalid("existing database directory must be private (0700)")
            }
        } else {
            try fileManager.createDirectory(at: directory, withIntermediateDirectories: true, attributes: [.posixPermissions: 0o700])
        }
        // O_NOFOLLOW also rejects dangling symlinks before any file creation or permission change.
        let descriptor = Darwin.open(url.path, O_CREAT | O_RDWR | O_NOFOLLOW | O_CLOEXEC, 0o600)
        guard descriptor >= 0 else { throw StorageError.database(String(cString: strerror(errno))) }
        defer { Darwin.close(descriptor) }
        var attributes = stat()
        guard fstat(descriptor, &attributes) == 0, (attributes.st_mode & S_IFMT) == S_IFREG,
              fchmod(descriptor, 0o600) == 0 else { throw StorageError.invalid("database must be a private regular file") }
        #if os(iOS)
        try fileManager.setAttributes([.protectionKey: FileProtectionType.complete], ofItemAtPath: url.path)
        #endif
        // SQLite rejects symlinks anywhere in the path; macOS /var itself aliases /private/var.
        guard let physicalDirectory = realpath(directory.path, nil) else { throw StorageError.invalid("database directory path") }
        defer { free(physicalDirectory) }
        let database = try SQLiteConnection(path: String(cString: physicalDirectory) + "/" + url.lastPathComponent)
        let version = try database.integer("PRAGMA user_version")
        guard version == 0 || version == 1 else { throw StorageError.unsupportedSchema(version) }
        if version == 0 {
            guard try database.integer("SELECT count(*) FROM sqlite_master WHERE name NOT LIKE 'sqlite_%'") == 0 else {
                throw StorageError.invalid("unrecognized nonempty database")
            }
            try database.execute("BEGIN IMMEDIATE")
            do {
                try database.execute("CREATE TABLE runs (id TEXT PRIMARY KEY NOT NULL, created_at REAL NOT NULL, model_version TEXT NOT NULL, payload BLOB NOT NULL)")
                try database.execute("PRAGMA user_version = 1")
                try database.execute("COMMIT")
            } catch {
                try? database.execute("ROLLBACK")
                throw error
            }
        }
        let probe = try database.prepare("SELECT id, created_at, model_version, payload FROM runs LIMIT 0")
        sqlite3_finalize(probe)
        try database.execute("PRAGMA journal_mode = DELETE")
        try database.execute("PRAGMA synchronous = FULL")
        try database.execute("PRAGMA trusted_schema = OFF")
        connection = database
    }

    public func save(_ run: SimulationRun) throws {
        let payload = try RunExchange.encodeJSON(run)
        try connection.execute("BEGIN IMMEDIATE")
        do {
            let statement = try connection.prepare("INSERT INTO runs(id, created_at, model_version, payload) VALUES (?, ?, ?, ?)")
            defer { sqlite3_finalize(statement) }
            try connection.bind(run.id.uuidString, to: 1, in: statement)
            guard sqlite3_bind_double(statement, 2, run.createdAt.timeIntervalSince1970) == SQLITE_OK else { throw connection.error() }
            try connection.bind(run.modelVersion, to: 3, in: statement)
            let bound = payload.withUnsafeBytes {
                sqlite3_bind_blob(statement, 4, $0.baseAddress, Int32($0.count), unsafeBitCast(-1, to: sqlite3_destructor_type.self))
            }
            guard bound == SQLITE_OK else { throw connection.error() }
            let result = sqlite3_step(statement)
            if result == SQLITE_CONSTRAINT { throw StorageError.duplicateRun }
            guard result == SQLITE_DONE else { throw connection.error() }
            try connection.execute("COMMIT")
        } catch {
            try? connection.execute("ROLLBACK")
            throw error
        }
    }

    public func runs() throws -> [SimulationRun] {
        let statement = try connection.prepare("SELECT id, created_at, model_version, payload FROM runs ORDER BY created_at DESC, id ASC")
        defer { sqlite3_finalize(statement) }
        var result: [SimulationRun] = []
        while true {
            let step = sqlite3_step(statement)
            if step == SQLITE_DONE { return result }
            guard step == SQLITE_ROW else { throw connection.error() }
            let size = Int(sqlite3_column_bytes(statement, 3))
            guard size > 0, size <= RunExchange.maximumBytes, let bytes = sqlite3_column_blob(statement, 3),
                  let id = sqlite3_column_text(statement, 0), let version = sqlite3_column_text(statement, 2) else {
                throw StorageError.invalid("stored payload")
            }
            let run = try RunExchange.decodeJSON(Data(bytes: bytes, count: size))
            guard run.id.uuidString == String(cString: id), run.modelVersion == String(cString: version),
                  run.createdAt.timeIntervalSince1970 == sqlite3_column_double(statement, 1) else {
                throw StorageError.invalid("stored provenance mismatch")
            }
            result.append(run)
        }
    }

    public func delete(id: UUID) throws {
        try connection.execute("BEGIN IMMEDIATE")
        do {
            let statement = try connection.prepare("DELETE FROM runs WHERE id = ?")
            defer { sqlite3_finalize(statement) }
            try connection.bind(id.uuidString, to: 1, in: statement)
            guard sqlite3_step(statement) == SQLITE_DONE else { throw connection.error() }
            try connection.execute("COMMIT")
        } catch {
            try? connection.execute("ROLLBACK")
            throw error
        }
    }
}
