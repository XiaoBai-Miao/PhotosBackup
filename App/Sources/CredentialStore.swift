import Foundation
import Security

/// The credential the app keeps between launches. `authData` is the whole
/// `&`-joined body `GPMCClient` consumes; the master token inside it is the
/// long-lived secret, so this record never leaves the Keychain.
struct StoredCredential: Codable, Equatable, Sendable {
    let androidId: String
    let email: String
    let masterToken: String
    let authData: String
    let connectedAt: Date
}

/// Backing store for one secret blob. A protocol so the state machine above it
/// can be exercised offline without touching the real Keychain.
protocol SecretStore: Sendable {
    func read() throws -> Data?
    func write(_ data: Data) throws
    func delete() throws
}

struct KeychainSecretStore: SecretStore {
    let service: String
    let account: String
    init(service: String = "com.g8row.photosbackup.credential", account: String = "photos") {
        self.service = service; self.account = account
    }
    private var base: [String: Any] {
        [kSecClass as String: kSecClassGenericPassword,
         kSecAttrService as String: service,
         kSecAttrAccount as String: account]
    }
    func read() throws -> Data? {
        var query = base
        query[kSecReturnData as String] = true
        query[kSecMatchLimit as String] = kSecMatchLimitOne
        var item: CFTypeRef?
        let status = SecItemCopyMatching(query as CFDictionary, &item)
        if status == errSecItemNotFound { return nil }
        guard status == errSecSuccess else { throw CredentialStore.Failure.keychain(status) }
        return item as? Data
    }
    func write(_ data: Data) throws {
        var query = base
        // afterFirstUnlock keeps uploads working while the phone is locked;
        // ThisDeviceOnly keeps the master token out of iCloud and backups.
        query[kSecAttrAccessible as String] = kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly
        let status = SecItemAdd(query.merging([kSecValueData as String: data]) { _, new in new } as CFDictionary, nil)
        if status == errSecDuplicateItem {
            let update = SecItemUpdate(base as CFDictionary, [kSecValueData as String: data] as CFDictionary)
            guard update == errSecSuccess else { throw CredentialStore.Failure.keychain(update) }
            return
        }
        guard status == errSecSuccess else { throw CredentialStore.Failure.keychain(status) }
    }
    func delete() throws {
        let status = SecItemDelete(base as CFDictionary)
        guard status == errSecSuccess || status == errSecItemNotFound else { throw CredentialStore.Failure.keychain(status) }
    }
}

/// In-memory stand-in used by the tests and by SwiftUI previews.
final class MemorySecretStore: SecretStore, @unchecked Sendable {
    private let lock = NSLock()
    private var value: Data?
    private(set) var writes = 0
    init(_ initial: Data? = nil) { value = initial }
    func read() throws -> Data? { lock.lock(); defer { lock.unlock() }; return value }
    func write(_ data: Data) throws { lock.lock(); defer { lock.unlock() }; value = data; writes += 1 }
    func delete() throws { lock.lock(); defer { lock.unlock() }; value = nil }
}

/// Owns the persisted credential and the one decision that goes with it:
/// whether the app currently has an account it can upload with.
actor CredentialStore {
    enum Failure: LocalizedError, Equatable {
        case keychain(OSStatus)
        case bound
        case corrupt
        var errorDescription: String? {
            switch self {
            case .keychain(let status):
                // SecCopyErrorMessageString already ends its sentence, so
                // don't add a second full stop.
                let detail = (SecCopyErrorMessageString(status, nil) as String? ?? "OSStatus \(status)")
                    .trimmingCharacters(in: CharacterSet(charactersIn: " ."))
                return String(format: NSLocalizedString("The Keychain refused the credential: %@.", comment: ""), detail)
            case .bound:
                return NSLocalizedString("Google issued a bound (encrypted) token. This build cannot use it; connect an account whose token is unbound.", comment: "")
            case .corrupt:
                return NSLocalizedString("The saved credential could not be read and has been discarded. Connect the account again.", comment: "")
            }
        }
    }

    /// A credential that is good but could not be written down. Carries the
    /// credential so the caller can still connect with it for this session.
    struct Unpersisted: Error {
        let credential: StoredCredential
        let reason: String
    }

    private let secrets: SecretStore
    private var cached: StoredCredential?

    init(secrets: SecretStore = KeychainSecretStore()) { self.secrets = secrets }

    /// Reads the credential once and keeps it. A blob we cannot decode is
    /// deleted rather than left to fail on every launch.
    func load() async throws -> StoredCredential? {
        if let cached { return cached }
        guard let data = try secrets.read() else { return nil }
        guard let credential = try? JSONDecoder.gpmc.decode(StoredCredential.self, from: data) else {
            try? secrets.delete()
            throw Failure.corrupt
        }
        cached = credential
        return credential
    }

    /// Persists a finished exchange. `TokenEncrypted=1` never reaches disk —
    /// `GPMCClient` and `TokenExchange` both refuse it, and so does this.
    @discardableResult
    func save(_ result: TokenExchange.Result) async throws -> StoredCredential {
        guard !result.encrypted else { throw Failure.bound }
        // Whole seconds: the stored form is ISO-8601 without fractions, so
        // rounding here keeps the record identical across a save/load round trip.
        let credential = StoredCredential(androidId: result.androidId, email: result.email,
                                          masterToken: result.masterToken, authData: result.authData,
                                          connectedAt: Date(timeIntervalSince1970: Date().timeIntervalSince1970.rounded(.down)))
        do {
            try secrets.write(try JSONEncoder.gpmc.encode(credential))
        } catch {
            // The Keychain being unavailable says nothing about whether Google
            // will honour the token, so hand the credential back rather than
            // throwing it away. It is usable now; it just will not survive a
            // relaunch. (Unsigned builds have no keychain-access-group.)
            cached = credential
            throw Unpersisted(credential: credential,
                              reason: (error as? LocalizedError)?.errorDescription ?? error.localizedDescription)
        }
        cached = credential
        return credential
    }

    func clear() async {
        cached = nil
        try? secrets.delete()
    }
}

extension JSONEncoder {
    static var gpmc: JSONEncoder { let e = JSONEncoder(); e.dateEncodingStrategy = .iso8601; return e }
}

extension JSONDecoder {
    static var gpmc: JSONDecoder { let d = JSONDecoder(); d.dateDecodingStrategy = .iso8601; return d }
}
