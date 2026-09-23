import SwiftUI

struct StorageUsageView: View {
    @EnvironmentObject private var queue: UploadQueue
    @State private var snapshot: AppStorageSnapshot?
    @State private var isCleaning = false

    var body: some View {
        List {
            Section("Used by Photos Backup") {
                storageRow(NSLocalizedString("Pending upload copies", comment: ""), bytes: snapshot?.stagedUploads)
                storageRow(NSLocalizedString("Backup history and queue", comment: ""), bytes: snapshot?.backupRecords)
                storageRow(NSLocalizedString("Completed transfer receipts", comment: ""), bytes: snapshot?.transferResults)
            }

            Section("System-managed") {
                storageRow(NSLocalizedString("Network and web caches", comment: ""), bytes: snapshot?.caches)
            }

            Section {
                Button {
                    cleanUp()
                } label: {
                    HStack {
                        Label("Clean Up Unused Data", systemImage: "sparkles")
                        Spacer()
                        if isCleaning { ProgressView() }
                    }
                }
                .disabled(isCleaning)
            } footer: {
                Text("Cleanup removes caches, old orphaned transfer receipts, and upload copies that are not owned by the current queue. It keeps pending uploads, your Google account, and the small history used to prevent duplicate backups.")
            }

            Section("What is retained") {
                Text("Pending uploads keep a full-size local copy until Google confirms the backup. Large videos are therefore the main source of temporary storage use.")
                Text("Backup history stores account-scoped PhotoKit identifiers. It is much smaller than the media and prevents every scan from uploading the same photos again.")
            }
        }
        .navigationTitle("Storage")
        .navigationBarTitleDisplayMode(.inline)
        .task { await refresh() }
        .refreshable { await refresh() }
    }

    @ViewBuilder
    private func storageRow(_ title: String, bytes: Int64?) -> some View {
        HStack {
            Text(title)
            Spacer()
            if let bytes {
                Text(bytes.formatted(.byteCount(style: .file)))
                    .foregroundStyle(.secondary)
            } else {
                ProgressView()
            }
        }
    }

    private func cleanUp() {
        guard !isCleaning else { return }
        isCleaning = true
        let files = queue.retainedStagingURLs
        let transferIDs = queue.retainedTransferIDs
        let before = snapshot?.total
        Task {
            await AppStorageUsage.cleanUp(retaining: files, transferIDs: transferIDs)
            await refresh()
            if let before, let after = snapshot?.total {
                DiagnosticEventLog.shared.record(
                    "storage",
                    "Cleaned up unused data; freed \(DiagnosticProcessInfo.bytes(max(0, before - after)))"
                )
            }
            isCleaning = false
        }
    }

    private func refresh() async {
        snapshot = await AppStorageUsage.measure()
    }
}
