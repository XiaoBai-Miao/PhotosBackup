import BackgroundTasks
import Foundation

/// The decisions behind a continued backup, kept apart from `BGTaskScheduler`
/// so they can be tested.
enum ContinuedBackupPolicy {
    /// The Info.plist wildcard a continued-backup identifier is built from.
    static let identifierMarker = ".continued-backup.*"

    /// Uploads that run at once while the app is in the background. Each one
    /// stages and hashes a full copy, and iOS ends a background process whose
    /// memory or CPU it needs back, whatever the user chose for the open app.
    static let backgroundConcurrencyLimit = 2

    /// How long a submitted request may go without iOS starting it before the
    /// app stops counting on it.
    static let launchTimeout: TimeInterval = 15

    /// Whether the queue can move on its own. A rate-limit wait ends by itself,
    /// so it keeps the task; a pause that needs the user, a connection, the
    /// account or a new iOS window does not.
    static func shouldContinue(hasWorkableItems: Bool, userPaused: Bool, halted: Bool,
                               networkPaused: Bool, systemPaused: Bool) -> Bool {
        hasWorkableItems && !userPaused && !halted && !networkPaused && !systemPaused
    }

    /// The identifier prefix to submit under, from the Info.plist entries. iOS
    /// wants the bundle ID at the front, so an entry that starts with the
    /// running bundle ID wins; a sideloading tool that renames the bundle but
    /// not the plist leaves only the build-time one, which is still worth a try.
    static func identifierPrefix(bundleIdentifier: String?, permitted: [String]) -> String? {
        let prefixes = permitted.filter { $0.hasSuffix(identifierMarker) }.map { String($0.dropLast()) }
        if let bundleIdentifier, let own = prefixes.first(where: { $0.hasPrefix(bundleIdentifier + ".") }) {
            return own
        }
        return prefixes.first
    }
}

/// What the Live Activity of a continued backup shows.
struct ContinuedBackupProgress: Equatable {
    let completed: Int64
    let total: Int64

    init(settledSinceStart: Int, unfinished: Int) {
        completed = Int64(max(0, settledSinceStart))
        total = completed + Int64(max(0, unfinished))
    }

    func subtitle(waitingFor reason: String?) -> String {
        reason ?? "\(completed.formatted()) of \(total.formatted()) done"
    }
}

/// Keeps the upload queue running after the app leaves the foreground, through
/// an iOS 26 continued-processing task. iOS shows its progress in a Live
/// Activity, where it can also be cancelled. Without one, iOS suspends the app
/// seconds after it leaves the foreground, and only uploads already handed to
/// its background transfer service carry on.
///
/// iOS accepts the request only while the app is in the foreground, so the
/// coordinator starts one whenever the app is open with work queued.
@available(iOS 26.0, *)
@MainActor
final class ContinuedBackupSession {
    static let title = "Backing up to Google Photos"

    /// iOS ended the task early: cancelled in the Live Activity, or the system
    /// needed the resources. Runs before iOS is told the task is over, which
    /// may suspend the app at once.
    var onExpired: (() -> Void)?
    /// iOS started the task. Usually at once, while the app is still open.
    var onStarted: (() -> Void)?

    /// Submitted, or running.
    var isActive: Bool { identifier != nil }
    /// iOS has started the task, so the app keeps running when backgrounded.
    var isRunning: Bool { task != nil }
    /// Submitted, but iOS has not started it for longer than it should take.
    var isOverdue: Bool {
        guard isActive, !isRunning, let submittedAt else { return false }
        return Date().timeIntervalSince(submittedAt) > ContinuedBackupPolicy.launchTimeout
    }
    private var identifier: String?
    private var submittedAt: Date?
    private var task: BGContinuedProcessingTask?
    private var lastSubtitle: String?
    private(set) var settledAtStart = 0

    func start(prefix: String, settledNow: Int, subtitle: String) throws {
        let identifier = prefix + UUID().uuidString
        // Registration of a continued-processing identifier is allowed after
        // launch; each task gets its own, since registering one twice is fatal.
        let registered = BGTaskScheduler.shared.register(forTaskWithIdentifier: identifier, using: nil) { [weak self] task in
            guard let task = task as? BGContinuedProcessingTask else {
                task.setTaskCompleted(success: false)
                return
            }
            // Same gap as the processing window: install a handler before the
            // hop to the main actor, and replay an expiry that lands inside it.
            let window = BackgroundWindow()
            task.expirationHandler = { window.expire() }
            Task { @MainActor [weak self] in
                guard let self, self.identifier == identifier else {
                    task.setTaskCompleted(success: false)
                    return
                }
                self.adopt(task, window: window)
            }
        }
        guard registered else { throw BGTaskScheduler.Error(.notPermitted) }
        let request = BGContinuedProcessingTaskRequest(identifier: identifier, title: Self.title, subtitle: subtitle)
        // Run now or not at all: a queued request would start whenever iOS
        // chose, perhaps after the app is no longer holding any work.
        request.strategy = .fail
        self.identifier = identifier
        submittedAt = Date()
        settledAtStart = settledNow
        lastSubtitle = subtitle
        do {
            try BGTaskScheduler.shared.submit(request)
        } catch {
            self.identifier = nil
            throw error
        }
    }

    func update(_ progress: ContinuedBackupProgress, subtitle: String) {
        guard let task else { return }
        task.progress.totalUnitCount = max(1, progress.total)
        task.progress.completedUnitCount = min(progress.completed, max(1, progress.total))
        if subtitle != lastSubtitle {
            lastSubtitle = subtitle
            task.updateTitle(Self.title, subtitle: subtitle)
        }
    }

    func finish(success: Bool) {
        let task = self.task
        self.task = nil
        identifier = nil
        task?.expirationHandler = nil
        task?.setTaskCompleted(success: success)
    }

    private func adopt(_ task: BGContinuedProcessingTask, window: BackgroundWindow) {
        self.task = task
        let expire: @Sendable () -> Void = { [weak self] in
            Task { @MainActor [weak self] in self?.expired() }
        }
        task.expirationHandler = expire
        window.adopt(expire)
        onStarted?()
    }

    private func expired() {
        guard task != nil else { return }
        onExpired?()
        finish(success: false)
    }
}
