import XCTest
@testable import PhotosBackup

final class ContinuedBackupTests: XCTestCase {

    func testTheTaskContinuesOnlyWhileTheQueueCanMoveOnItsOwn() {
        func decide(workable: Bool = true, user: Bool = false, halted: Bool = false,
                    network: Bool = false, system: Bool = false) -> Bool {
            ContinuedBackupPolicy.shouldContinue(hasWorkableItems: workable, userPaused: user, halted: halted,
                                                 networkPaused: network, systemPaused: system)
        }
        XCTAssertTrue(decide())
        XCTAssertFalse(decide(workable: false), "nothing left, or only rows waiting for iCloud")
        XCTAssertFalse(decide(user: true))
        XCTAssertFalse(decide(halted: true), "the account needs the user")
        XCTAssertFalse(decide(network: true), "no allowed connection")
        XCTAssertFalse(decide(system: true))
    }

    func testTheIdentifierUsesThePlistEntryThatStartsWithTheRunningBundleID() {
        let permitted = [
            "com.g8row.photosbackup.background-backup",
            "com.g8row.photosbackup.continued-backup.*",
            "com.g8row.photosbackup.TEAM.continued-backup.*",
        ]
        XCTAssertEqual(ContinuedBackupPolicy.identifierPrefix(bundleIdentifier: "com.g8row.photosbackup.TEAM",
                                                              permitted: permitted),
                       "com.g8row.photosbackup.TEAM.continued-backup.")
        XCTAssertEqual(ContinuedBackupPolicy.identifierPrefix(bundleIdentifier: "com.g8row.photosbackup",
                                                              permitted: permitted),
                       "com.g8row.photosbackup.continued-backup.")
    }

    func testARenamedBundleStillTriesTheBuildTimeEntry() {
        // A sideloading tool can rename the bundle without touching the plist.
        XCTAssertEqual(ContinuedBackupPolicy.identifierPrefix(bundleIdentifier: "com.g8row.photosbackup.TEAM",
                                                              permitted: ["com.g8row.photosbackup.continued-backup.*"]),
                       "com.g8row.photosbackup.continued-backup.")
        XCTAssertNil(ContinuedBackupPolicy.identifierPrefix(bundleIdentifier: "com.g8row.photosbackup",
                                                            permitted: ["com.g8row.photosbackup.background-backup"]))
    }

    func testTheShippedPlistPermitsAContinuedBackupIdentifier() throws {
        let bundle = Bundle(for: UploadQueue.self)
        let permitted = try XCTUnwrap(bundle.object(forInfoDictionaryKey: "BGTaskSchedulerPermittedIdentifiers") as? [String])
        let prefix = try XCTUnwrap(ContinuedBackupPolicy.identifierPrefix(bundleIdentifier: bundle.bundleIdentifier,
                                                                          permitted: permitted))
        XCTAssertTrue(prefix.hasPrefix(try XCTUnwrap(bundle.bundleIdentifier) + "."),
                      "iOS wants the bundle ID at the front of a continued-processing identifier")
    }

    func testTheHeartbeatMovesProgressInsideTheItemInFlightOnly() {
        let units = ContinuedBackupProgress.unitsPerItem
        let twoOfTen = ContinuedBackupProgress(settledSinceStart: 2, unfinished: 8)
        // Real progress jumps to the finished items; a heartbeat adds one unit.
        XCTAssertEqual(twoOfTen.nextReported(after: 0, heartbeat: false), 2 * units)
        XCTAssertEqual(twoOfTen.nextReported(after: 2 * units, heartbeat: true), 2 * units + 1)
        // Never reaches the next finished item, however long the item takes.
        XCTAssertEqual(twoOfTen.nextReported(after: 3 * units - 1, heartbeat: true), 3 * units - 1)
        // Never goes backwards when real progress catches up.
        XCTAssertEqual(ContinuedBackupProgress(settledSinceStart: 3, unfinished: 7)
                        .nextReported(after: 3 * units - 1, heartbeat: false), 3 * units)
        // All done: exactly the total, heartbeat or not.
        let done = ContinuedBackupProgress(settledSinceStart: 10, unfinished: 0)
        XCTAssertEqual(done.nextReported(after: 9 * units + 500, heartbeat: true), 10 * units)
    }

    func testProgressCountsWhatFinishedAgainstWhatFinishedPlusWhatIsLeft() {
        let progress = ContinuedBackupProgress(settledSinceStart: 12, unfinished: 1308)
        XCTAssertEqual(progress.completed, 12)
        XCTAssertEqual(progress.total, 1320)
        XCTAssertEqual(progress.subtitle(waitingFor: nil), "\(12.formatted()) of \(1320.formatted()) done")
        XCTAssertEqual(progress.subtitle(waitingFor: "Waiting"), "Waiting")
        XCTAssertEqual(ContinuedBackupProgress(settledSinceStart: -3, unfinished: 5).completed, 0)
    }
}
