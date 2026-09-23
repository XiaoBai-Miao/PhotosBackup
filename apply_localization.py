# -*- coding: utf-8 -*-
"""Apply all localization replacements to PhotosBackup Swift sources (Linux LF clone)."""
import io, os, sys

ROOT = r"/home/user/Doubao/chats/38443843430476034/PhotosBackup"

# (relative_path, old, new, expected_count)
R = []

def add(path, old, new, count=1):
    R.append((path, old, new, count))

# ============ OnboardingView.swift ============
P = "App/Sources/OnboardingView.swift"
add(P,
    '            eyebrow: "PHOTOS BACKUP",\n            title: "Your memories, safely backed up",\n            message: "Choose the albums that matter. Photos Backup keeps them protected in your Google Photos library.",\n            primaryTitle: "Get Started",\n            primaryAction: next,\n            credit: "Built with GPMC by xob0t"',
    '            eyebrow: String(localized: "PHOTOS BACKUP"),\n            title: String(localized: "Your memories, safely backed up"),\n            message: String(localized: "Choose the albums that matter. Photos Backup keeps them protected in your Google Photos library."),\n            primaryTitle: String(localized: "Get Started"),\n            primaryAction: next,\n            credit: String(localized: "Built with GPMC by xob0t")')
add(P,
    '            eyebrow: "YOUR LIBRARY",\n            title: "Choose what to protect",\n            message: "Allow photo access so you can pick albums and back up individual photos. Your library stays private on this device.",\n            primaryTitle: permissionButtonTitle,\n            primaryAction: {\n                Task {\n                    if albums.authorization == .notDetermined {\n                        await albums.requestAccess()\n                        if albums.canRead { next() }\n                    } else if albums.canRead {\n                        next()\n                    } else {\n                        openAppSettings()\n                    }\n                }\n            },\n            secondaryTitle: albums.authorization == .denied || albums.authorization == .restricted ? "Continue without access" : nil,',
    '            eyebrow: String(localized: "YOUR LIBRARY"),\n            title: String(localized: "Choose what to protect"),\n            message: String(localized: "Allow photo access so you can pick albums and back up individual photos. Your library stays private on this device."),\n            primaryTitle: permissionButtonTitle,\n            primaryAction: {\n                Task {\n                    if albums.authorization == .notDetermined {\n                        await albums.requestAccess()\n                        if albums.canRead { next() }\n                    } else if albums.canRead {\n                        next()\n                    } else {\n                        openAppSettings()\n                    }\n                }\n            },\n            secondaryTitle: albums.authorization == .denied || albums.authorization == .restricted ? String(localized: "Continue without access") : nil,')
add(P,
    '            eyebrow: "CONNECT YOUR ACCOUNT",\n            title: "Sign in with Google",\n            message: "Connect your Google account to back up to Google Photos. Sign-in opens in a secure in-app window — sign in, then tap I agree.",\n            primaryTitle: "Connect Google Account",',
    '            eyebrow: String(localized: "CONNECT YOUR ACCOUNT"),\n            title: String(localized: "Sign in with Google"),\n            message: String(localized: "Connect your Google account to back up to Google Photos. Sign-in opens in a secure in-app window — sign in, then tap I agree."),\n            primaryTitle: String(localized: "Connect Google Account"),')
add(P,
    'Button(probe.running ? "Verifying…" : (connectionFailed ? "Try Again" : "Check Again")) {\n                            if connectionFailed { showingConnect = true } else { verifyConnection() }\n                        }\n                        .buttonStyle(PrimaryButtonStyle()).disabled(probe.running)\n                        if !probe.running {\n                            Button("Connect a Different Account") { showingConnect = true }',
    'Button(probe.running ? String(localized: "Verifying…") : (connectionFailed ? String(localized: "Try Again") : String(localized: "Check Again"))) {\n                            if connectionFailed { showingConnect = true } else { verifyConnection() }\n                        }\n                        .buttonStyle(PrimaryButtonStyle()).disabled(probe.running)\n                        if !probe.running {\n                            Button(String(localized: "Connect a Different Account")) { showingConnect = true }')
add(P,
    'Text("CHOOSE ALBUMS").font(.caption.weight(.bold)).tracking(1.2).foregroundStyle(BackupTheme.blue)\n                Text("What should we back up?").font(.largeTitle.bold()).multilineTextAlignment(.center)\n                Text("You can change this anytime in Albums.")\n                    .font(.body).foregroundStyle(.secondary)',
    'Text(String(localized: "CHOOSE ALBUMS")).font(.caption.weight(.bold)).tracking(1.2).foregroundStyle(BackupTheme.blue)\n                Text(String(localized: "What should we back up?")).font(.largeTitle.bold()).multilineTextAlignment(.center)\n                Text(String(localized: "You can change this anytime in Albums."))\n                    .font(.body).foregroundStyle(.secondary)')
add(P,
    'EmptyState(symbol: "photo.badge.exclamationmark", title: "Photo access is off", message: "You can choose albums later after allowing photo access in Settings.")',
    'EmptyState(symbol: "photo.badge.exclamationmark", title: String(localized: "Photo access is off"), message: String(localized: "You can choose albums later after allowing photo access in Settings."))')
add(P,
    'Button(preferences.selectedAlbumIDs.isEmpty ? "Choose Later" : "Continue") { next() }',
    'Button(preferences.selectedAlbumIDs.isEmpty ? String(localized: "Choose Later") : String(localized: "Continue")) { next() }')
add(P,
    'Text("When should we back up?")\n                        .font(.largeTitle.bold()).multilineTextAlignment(.center).padding(.top, 24)\n                    Text("Choose how Photos Backup uses your connection.")\n                        .font(.body).foregroundStyle(.secondary).multilineTextAlignment(.center).padding(.top, 10)',
    'Text(String(localized: "When should we back up?"))\n                        .font(.largeTitle.bold()).multilineTextAlignment(.center).padding(.top, 24)\n                    Text(String(localized: "Choose how Photos Backup uses your connection."))\n                        .font(.body).foregroundStyle(.secondary).multilineTextAlignment(.center).padding(.top, 10)')
add(P,
    'Toggle("Back up selected albums automatically", isOn: $preferences.automaticBackup)\n                        .font(.subheadline.weight(.medium))\n                        .padding(.top, 22)\n                    Spacer(minLength: 28)\n                    Button("Continue") { next() }.buttonStyle(PrimaryButtonStyle())',
    'Toggle(String(localized: "Back up selected albums automatically"), isOn: $preferences.automaticBackup)\n                        .font(.subheadline.weight(.medium))\n                        .padding(.top, 22)\n                    Spacer(minLength: 28)\n                    Button(String(localized: "Continue")) { next() }.buttonStyle(PrimaryButtonStyle())')
add(P,
    'eyebrow: "ALL SET",\n            title: "Your backup is ready",\n            message: completionMessage,\n            primaryTitle: "Go to Photos Backup",',
    'eyebrow: String(localized: "ALL SET"),\n            title: String(localized: "Your backup is ready"),\n            message: completionMessage,\n            primaryTitle: String(localized: "Go to Photos Backup"),')
add(P,
    '''    private var permissionButtonTitle: String {
        switch albums.authorization {
        case .authorized, .limited: return "Continue"
        case .denied, .restricted: return "Open Settings"
        default: return "Allow Photo Access"
        }
    }

    private var completionMessage: String {
        let count = preferences.selectedAlbumIDs.count
        return count == 0
            ? "Your account is connected. You can choose albums from the Albums tab."
            : "Your account is connected, and we’ll keep \(count) selected \(count == 1 ? "album" : "albums") protected."
    }''',
    '''    private var permissionButtonTitle: String {
        switch albums.authorization {
        case .authorized, .limited: return String(localized: "Continue")
        case .denied, .restricted: return String(localized: "Open Settings")
        default: return String(localized: "Allow Photo Access")
        }
    }

    private var completionMessage: String {
        let count = preferences.selectedAlbumIDs.count
        return count == 0
            ? String(localized: "Your account is connected. You can choose albums from the Albums tab.")
            : String(localized: "Your account is connected, and we’ll keep \(count) selected \(count == 1 ? "album" : "albums") protected.")
    }''')
add(P,
    '''    private var connectionEyebrow: String {
        if connectionVerified { return "CONNECTION VERIFIED" }
        if connectionFailed { return "COULDN’T CONNECT" }
        return probe.running ? "VERIFYING ACCOUNT" : "WAITING TO CONNECT"
    }

    private var connectionTitle: String {
        if connectionVerified { return "You’re connected" }
        if connectionFailed { return "Let’s try that again" }
        return probe.running ? "Checking your account…" : "Finish connecting"
    }

    private var connectionMessage: String {
        if connectionVerified { return "Photos Backup verified your Google Photos account. You’re ready to continue." }
        if connectionFailed {
            return "We received the sign-in, but couldn’t verify it. Tap Try Again, sign in, and tap I agree."
        }
        return probe.running
            ? "We securely captured your sign-in and are verifying your Google Photos access."
            : "Sign in and tap I agree in the connect window. We’ll verify everything before continuing."
    }''',
    '''    private var connectionEyebrow: String {
        if connectionVerified { return String(localized: "CONNECTION VERIFIED") }
        if connectionFailed { return String(localized: "COULDN’T CONNECT") }
        return probe.running ? String(localized: "VERIFYING ACCOUNT") : String(localized: "WAITING TO CONNECT")
    }

    private var connectionTitle: String {
        if connectionVerified { return String(localized: "You’re connected") }
        if connectionFailed { return String(localized: "Let’s try that again") }
        return probe.running ? String(localized: "Checking your account…") : String(localized: "Finish connecting")
    }

    private var connectionMessage: String {
        if connectionVerified { return String(localized: "Photos Backup verified your Google Photos account. You’re ready to continue.") }
        if connectionFailed {
            return String(localized: "We received the sign-in, but couldn’t verify it. Tap Try Again, sign in, and tap I agree.")
        }
        return probe.running
            ? String(localized: "We securely captured your sign-in and are verifying your Google Photos access.")
            : String(localized: "Sign in and tap I agree in the connect window. We’ll verify everything before continuing.")
    }''')
add(P,
    '''    private var detail: String {
        guard let backedUpCount else { return "\(album.count.formatted()) items" }
        if backedUpCount >= album.count, album.count > 0 { return "All \(album.count.formatted()) backed up" }
        return "\(backedUpCount.formatted()) of \(album.count.formatted()) backed up"
    }''',
    '''    private var detail: String {
        guard let backedUpCount else { return String(localized: "\(album.count.formatted()) items") }
        if backedUpCount >= album.count, album.count > 0 { return String(localized: "All \(album.count.formatted()) backed up") }
        return String(localized: "\(backedUpCount.formatted()) of \(album.count.formatted()) backed up")
    }''')

# ============ SettingsView.swift ============
P = "App/Sources/SettingsView.swift"
add(P,
    'Text(account.verifying ? "Checking Connection…" : "Check Connection")',
    'Text(account.verifying ? String(localized: "Checking Connection…") : String(localized: "Check Connection"))')
add(P,
    'Text(warning + " The account works for this session but may need to be connected again after relaunch.")',
    'Text(warning + " " + String(localized: "The account works for this session but may need to be connected again after relaunch."))')
add(P,
    'Text(isVerifying ? "Re-checking…" : "Re-check Backups")',
    'Text(isVerifying ? String(localized: "Re-checking…") : String(localized: "Re-check Backups"))')
add(P,
    'LabeledRow("App", value: "Photos Backup")\n            LabeledRow("Version", value: appVersion)\n            LabeledRow("iOS", value: UIDevice.current.systemVersion)\n            LabeledRow("Core technology") {',
    'LabeledRow(String(localized: "App"), value: String(localized: "Photos Backup"))\n            LabeledRow(String(localized: "Version"), value: appVersion)\n            LabeledRow(String(localized: "iOS"), value: UIDevice.current.systemVersion)\n            LabeledRow(String(localized: "Core technology")) {')
add(P,
    '''    private var accountTitle: String {
        switch account.status {
        case .loading: return "Checking account…"
        case .disconnected: return "Not connected"
        case .connected(let email, _): return email
        case .rejected(let email, _): return email.isEmpty ? "Sign in again" : email
        }
    }

    private var accountSubtitle: String {
        switch account.status {
        case .loading: return "Looking for a saved credential"
        case .disconnected: return "Connect to start backing up"
        case .connected(_, let since): return "Connected · \(since.formatted(date: .abbreviated, time: .omitted))"
        case .rejected(_, let reason): return reason
        }
    }''',
    '''    private var accountTitle: String {
        switch account.status {
        case .loading: return String(localized: "Checking account…")
        case .disconnected: return String(localized: "Not connected")
        case .connected(let email, _): return email
        case .rejected(let email, _): return email.isEmpty ? String(localized: "Sign in again") : email
        }
    }

    private var accountSubtitle: String {
        switch account.status {
        case .loading: return String(localized: "Looking for a saved credential")
        case .disconnected: return String(localized: "Connect to start backing up")
        case .connected(_, let since): return String(localized: "Connected · \(since.formatted(date: .abbreviated, time: .omitted))")
        case .rejected(_, let reason): return reason
        }
    }''')
add(P,
    '.accessibilityLabel(account.status.isUsable ? "Connected" : "Action needed")',
    '.accessibilityLabel(account.status.isUsable ? String(localized: "Connected") : String(localized: "Action needed"))')

# ============ DashboardView.swift ============
P = "App/Sources/DashboardView.swift"
add(P,
    '''        case .loading:
            banner(color: .blue, symbol: "hourglass", title: "Checking your account", message: "Just a moment…")
        case .disconnected:
            Button(action: onConnect) {
                banner(color: .orange, symbol: "person.crop.circle.badge.exclamationmark", title: "Connect Google Photos", message: "Sign in to start protecting your library", showsChevron: true)
            }
            .buttonStyle(.plain)
        case .connected:
            if let warning = account.persistenceWarning {
                banner(color: .orange, symbol: "key.slash", title: "Not saved to Keychain", message: warning, showsChevron: false)
            } else if let reason = queue.pauseReason {
                banner(color: .orange, symbol: "pause.circle.fill", title: "Backup paused", message: reason, showsChevron: false)
            }
        case .rejected(_, let reason):
            Button(action: onConnect) {
                banner(color: .red, symbol: "exclamationmark.arrow.circlepath", title: "Sign in again", message: reason, showsChevron: true)
            }
            .buttonStyle(.plain)''',
    '''        case .loading:
            banner(color: .blue, symbol: "hourglass", title: String(localized: "Checking your account"), message: String(localized: "Just a moment…"))
        case .disconnected:
            Button(action: onConnect) {
                banner(color: .orange, symbol: "person.crop.circle.badge.exclamationmark", title: String(localized: "Connect Google Photos"), message: String(localized: "Sign in to start protecting your library"), showsChevron: true)
            }
            .buttonStyle(.plain)
        case .connected:
            if let warning = account.persistenceWarning {
                banner(color: .orange, symbol: "key.slash", title: String(localized: "Not saved to Keychain"), message: warning, showsChevron: false)
            } else if let reason = queue.pauseReason {
                banner(color: .orange, symbol: "pause.circle.fill", title: String(localized: "Backup paused"), message: reason, showsChevron: false)
            }
        case .rejected(_, let reason):
            Button(action: onConnect) {
                banner(color: .red, symbol: "exclamationmark.arrow.circlepath", title: String(localized: "Sign in again"), message: reason, showsChevron: true)
            }
            .buttonStyle(.plain)''')
add(P,
    '''                metric(value: queue.completedSourceCount.formatted(), label: "Backed up")
                Divider().frame(height: 38)
                metric(value: selectedAlbums.count.formatted(), label: "Albums")
                Divider().frame(height: 38)
                metric(value: queue.activeCount.formatted(), label: "In queue")''',
    '''                metric(value: queue.completedSourceCount.formatted(), label: String(localized: "Backed up"))
                Divider().frame(height: 38)
                metric(value: selectedAlbums.count.formatted(), label: String(localized: "Albums"))
                Divider().frame(height: 38)
                metric(value: queue.activeCount.formatted(), label: String(localized: "In queue"))''')
add(P,
    '''        return Button(action: backUpSelectedAlbums) {
            quickActionLabel(symbol: "arrow.up.circle.fill",
                             title: isStartingManualRun ? "Checking…" : "Back Up Now",
                             detail: backUpActionDetail,
                             isEnabled: enabled)
        }
        .disabled(!enabled)
    }

    private var backUpActionDetail: String {
        if selectedAlbums.isEmpty { return "Choose albums first" }
        if queue.isUserPaused { return "Backup is paused" }
        let backedUp = selectedBackedUpCount
        guard selectedItemCount > 0 else { return "\(selectedItemCount.formatted()) items" }
        return "\(backedUp.formatted()) of \(selectedItemCount.formatted()) backed up"
    }''',
    '''        return Button(action: backUpSelectedAlbums) {
            quickActionLabel(symbol: "arrow.up.circle.fill",
                             title: isStartingManualRun ? String(localized: "Checking…") : String(localized: "Back Up Now"),
                             detail: backUpActionDetail,
                             isEnabled: enabled)
        }
        .disabled(!enabled)
    }

    private var backUpActionDetail: String {
        if selectedAlbums.isEmpty { return String(localized: "Choose albums first") }
        if queue.isUserPaused { return String(localized: "Backup is paused") }
        let backedUp = selectedBackedUpCount
        guard selectedItemCount > 0 else { return String(localized: "\(selectedItemCount.formatted()) items") }
        return String(localized: "\(backedUp.formatted()) of \(selectedItemCount.formatted()) backed up")
    }''')
add(P,
    'quickActionLabel(symbol: "photo.badge.plus", title: "Pick Photos", detail: "Manual backup", isEnabled: enabled)',
    'quickActionLabel(symbol: "photo.badge.plus", title: String(localized: "Pick Photos"), detail: String(localized: "Manual backup"), isEnabled: enabled)')
add(P,
    'StatusPill(text: "Automatic", symbol: "arrow.triangle.2.circlepath", color: .green)',
    'StatusPill(text: String(localized: "Automatic"), symbol: "arrow.triangle.2.circlepath", color: .green)')
add(P,
    '''    private var heroTitle: String {
        if !account.status.isUsable { return "Connect to back up" }
        if queue.pauseReason != nil { return "Backup paused" }
        if !queue.isIdle { return "Backing up…" }
        if queue.failedCount > 0 { return "Backup needs attention" }
        if queue.completedSourceCount == 0 { return "Ready to back up" }
        return "Backup complete"
    }

    private var heroSubtitle: String {
        if !account.status.isUsable { return "Connect an account to get started" }
        if let reason = queue.pauseReason { return reason }
        if !queue.isIdle { return "\(queue.activeCount) items remaining" }
        if queue.failedCount > 0 { return "\(queue.failedCount) items failed — open Activity to retry" }
        if selectedAlbums.isEmpty { return "Choose albums to protect" }
        return "Your selected albums are up to date"
    }''',
    '''    private var heroTitle: String {
        if !account.status.isUsable { return String(localized: "Connect to back up") }
        if queue.pauseReason != nil { return String(localized: "Backup paused") }
        if !queue.isIdle { return String(localized: "Backing up…") }
        if queue.failedCount > 0 { return String(localized: "Backup needs attention") }
        if queue.completedSourceCount == 0 { return String(localized: "Ready to back up") }
        return String(localized: "Backup complete")
    }

    private var heroSubtitle: String {
        if !account.status.isUsable { return String(localized: "Connect an account to get started") }
        if let reason = queue.pauseReason { return reason }
        if !queue.isIdle { return String(localized: "\(queue.activeCount) items remaining") }
        if queue.failedCount > 0 { return String(localized: "\(queue.failedCount) items failed — open Activity to retry") }
        if selectedAlbums.isEmpty { return String(localized: "Choose albums to protect") }
        return String(localized: "Your selected albums are up to date")
    }''')
add(P,
    '''    private func progressLabel(for album: PhotoAlbum) -> String {
        guard let backedUp = albums.backedUpCounts[album.id] else {
            return "\(album.count.formatted()) items"
        }
        return "\(backedUp.formatted()) of \(album.count.formatted()) backed up"
    }''',
    '''    private func progressLabel(for album: PhotoAlbum) -> String {
        guard let backedUp = albums.backedUpCounts[album.id] else {
            return String(localized: "\(album.count.formatted()) items")
        }
        return String(localized: "\(backedUp.formatted()) of \(album.count.formatted()) backed up")
    }''')
add(P,
    '''    static func message(for outcome: AutomaticBackupCoordinator.ManualRunOutcome) -> String {
        switch outcome {
        case .noLibraryAccess: return "Allow photo access in Settings to back up your albums."
        case .noAlbumsSelected: return "Choose albums in the Albums tab first."
        case .nothingToDo: return "Everything in your selected albums is already backed up."
        case .started(let count): return "Backing up \(count.formatted()) items. Watch progress in Activity."
        case .rechecking(let count): return "Re-checking \(count.formatted()) items against Google Photos."
        }
    }

    private var stopBackupMessage: String {
        if preferences.automaticBackup {
            return "Uploads in progress will be cancelled, the queue will be cleared, and Automatic Backup will be turned off. Photos already backed up are not affected."
        }
        return "Uploads in progress will be cancelled and the queue will be cleared. Photos already backed up are not affected."
    }''',
    '''    static func message(for outcome: AutomaticBackupCoordinator.ManualRunOutcome) -> String {
        switch outcome {
        case .noLibraryAccess: return String(localized: "Allow photo access in Settings to back up your albums.")
        case .noAlbumsSelected: return String(localized: "Choose albums in the Albums tab first.")
        case .nothingToDo: return String(localized: "Everything in your selected albums is already backed up.")
        case .started(let count): return String(localized: "Backing up \(count.formatted()) items. Watch progress in Activity.")
        case .rechecking(let count): return String(localized: "Re-checking \(count.formatted()) items against Google Photos.")
        }
    }

    private var stopBackupMessage: String {
        if preferences.automaticBackup {
            return String(localized: "Uploads in progress will be cancelled, the queue will be cleared, and Automatic Backup will be turned off. Photos already backed up are not affected.")
        }
        return String(localized: "Uploads in progress will be cancelled and the queue will be cleared. Photos already backed up are not affected.")
    }''')
add(P,
    '.accessibilityLabel(account.status.isUsable ? "Account connected" : "Account not connected")',
    '.accessibilityLabel(account.status.isUsable ? String(localized: "Account connected") : String(localized: "Account not connected"))')

# ============ UploadsView.swift ============
P = "App/Sources/UploadsView.swift"
add(P,
    'EmptyState(symbol: "tray", title: "No backup activity", message: "Photos you back up manually or from selected albums will appear here.")',
    'EmptyState(symbol: "tray", title: String(localized: "No backup activity"), message: String(localized: "Photos you back up manually or from selected albums will appear here."))')
add(P,
    '''    private var stopBackupMessage: String {
        if preferences.automaticBackup {
            return "Uploads in progress will be cancelled, the queue will be cleared, and Automatic Backup will be turned off. Photos already backed up are not affected."
        }
        return "Uploads in progress will be cancelled and the queue will be cleared. Photos already backed up are not affected."
    }''',
    '''    private var stopBackupMessage: String {
        if preferences.automaticBackup {
            return String(localized: "Uploads in progress will be cancelled, the queue will be cleared, and Automatic Backup will be turned off. Photos already backed up are not affected.")
        }
        return String(localized: "Uploads in progress will be cancelled and the queue will be cleared. Photos already backed up are not affected.")
    }''')

# ============ FolderSelectionView.swift ============
P = "App/Sources/FolderSelectionView.swift"
add(P,
    'EmptyState(symbol: "rectangle.stack", title: "No albums found", message: "Albums from your Photos library will appear here.")',
    'EmptyState(symbol: "rectangle.stack", title: String(localized: "No albums found"), message: String(localized: "Albums from your Photos library will appear here."))')
add(P,
    'Text(preferences.automaticBackup ? "Selected albums back up automatically" : "Automatic backup is paused")',
    'Text(preferences.automaticBackup ? String(localized: "Selected albums back up automatically") : String(localized: "Automatic backup is paused"))')
add(P,
    'EmptyState(symbol: "photo.on.rectangle.angled", title: "See your albums", message: "Allow photo access to choose which albums Photos Backup should protect.")',
    'EmptyState(symbol: "photo.on.rectangle.angled", title: String(localized: "See your albums"), message: String(localized: "Allow photo access to choose which albums Photos Backup should protect."))')
add(P,
    'EmptyState(symbol: "photo.badge.exclamationmark", title: "Photo access is off", message: "Allow access in Settings to choose albums and back up photos.")',
    'EmptyState(symbol: "photo.badge.exclamationmark", title: String(localized: "Photo access is off"), message: String(localized: "Allow access in Settings to choose albums and back up photos."))')

# ============ StorageUsageView.swift ============
P = "App/Sources/StorageUsageView.swift"
add(P,
    '''                storageRow("Pending upload copies", bytes: snapshot?.stagedUploads)
                storageRow("Backup history and queue", bytes: snapshot?.backupRecords)
                storageRow("Completed transfer receipts", bytes: snapshot?.transferResults)''',
    '''                storageRow(String(localized: "Pending upload copies"), bytes: snapshot?.stagedUploads)
                storageRow(String(localized: "Backup history and queue"), bytes: snapshot?.backupRecords)
                storageRow(String(localized: "Completed transfer receipts"), bytes: snapshot?.transferResults)''')
add(P,
    'storageRow("Network and web caches", bytes: snapshot?.caches)',
    'storageRow(String(localized: "Network and web caches"), bytes: snapshot?.caches)')

# ============ DiagnosticsView.swift ============
P = "App/Sources/DiagnosticsView.swift"
add(P,
    'LabeledRow("iOS", value: UIDevice.current.systemVersion)',
    'LabeledRow(String(localized: "iOS"), value: UIDevice.current.systemVersion)')
add(P,
    '''                    Text(queue.failureCount > queue.recentFailures.count
                         ? "\(queue.failureCount) failures this session; showing the \(queue.recentFailures.count) most recent."
                         : "\(queue.failureCount) failures this session.")''',
    '''                    Text(queue.failureCount > queue.recentFailures.count
                         ? String(localized: "\(queue.failureCount) failures this session; showing the \(queue.recentFailures.count) most recent.")
                         : String(localized: "\(queue.failureCount) failures this session."))''')

# ============ DiagnosticEventsView.swift ============
P = "App/Sources/DiagnosticEventsView.swift"
add(P,
    'Text(filter == .all ? "No events recorded yet." : "No warnings or errors.")',
    'Text(filter == .all ? String(localized: "No events recorded yet.") : String(localized: "No warnings or errors."))')
add(P,
    '''                    Text("Repeated \(event.occurrences) times"
                         + (event.firstDate.map { " since \($0.formatted(date: .omitted, time: .shortened))" } ?? ""))''',
    '''                    Text(String(localized: "Repeated \(event.occurrences) times")
                         + (event.firstDate.map { String(localized: " since \($0.formatted(date: .omitted, time: .shortened))") } ?? ""))''')
add(P,
    'Text(run.source.rawValue).font(.subheadline.weight(.medium))',
    'Text(NSLocalizedString(run.source.rawValue, comment: "Backup run source")).font(.subheadline.weight(.medium))')
add(P,
    'ForEach(Filter.allCases) { Text($0.rawValue).tag($0) }',
    'ForEach(Filter.allCases) { Text(NSLocalizedString($0.rawValue, comment: "Event filter")).tag($0) }')

# ============ DiagnosticReportView.swift ============
P = "App/Sources/DiagnosticReportView.swift"
add(P,
    'Label(report == nil ? "Generate Report" : "Refresh Report", systemImage: "doc.text.magnifyingglass")',
    'Label(report == nil ? String(localized: "Generate Report") : String(localized: "Refresh Report"), systemImage: "doc.text.magnifyingglass")')
add(P,
    'Label(copied ? "Copied" : "Copy Report Text", systemImage: copied ? "checkmark" : "doc.on.doc")',
    'Label(copied ? String(localized: "Copied") : String(localized: "Copy Report Text"), systemImage: copied ? "checkmark" : "doc.on.doc")')
add(P,
    'errorMessage = "Could not create the report: \(error.localizedDescription)"',
    'errorMessage = String(localized: "Could not create the report: \(error.localizedDescription)")')

# ============ DesignComponents.swift ============
P = "App/Sources/DesignComponents.swift"
add(P,
    'Text(scene == .enableExtension ? "Safari Extensions" : "accounts.google.com")',
    'Text(scene == .enableExtension ? String(localized: "Safari Extensions") : "accounts.google.com")')
add(P,
    '''    private let steps: [(String, String, String)] = [
        ("1", "Sign in and tap I agree", "Complete Google’s sign-in page."),
        ("2", "Open Safari’s extension menu", "Tap the puzzle-piece or page menu icon."),
        ("3", "Choose Photos Backup Connect", "Open our extension from the list."),
        ("4", "Tap Connect to App", "Wait for the green confirmation, then return.")
    ]''',
    '''    private let steps: [(String, String, String)] = [
        ("1", String(localized: "Sign in and tap I agree"), String(localized: "Complete Google’s sign-in page.")),
        ("2", String(localized: "Open Safari’s extension menu"), String(localized: "Tap the puzzle-piece or page menu icon.")),
        ("3", String(localized: "Choose Photos Backup Connect"), String(localized: "Open our extension from the list.")),
        ("4", String(localized: "Tap Connect to App"), String(localized: "Wait for the green confirmation, then return."))
    ]''')

# ============ BackupPreferences.swift ============
P = "App/Sources/BackupPreferences.swift"
add(P,
    '''    var title: String {
        switch self {
        case .wifiOnly: return "Wi-Fi Only"
        case .wifiAndCellular: return "Wi-Fi & Cellular"
        }
    }

    var detail: String {
        switch self {
        case .wifiOnly: return "Wait for Wi-Fi before uploading"
        case .wifiAndCellular: return "Back up wherever you are"
        }
    }''',
    '''    var title: String {
        switch self {
        case .wifiOnly: return String(localized: "Wi-Fi Only")
        case .wifiAndCellular: return String(localized: "Wi-Fi & Cellular")
        }
    }

    var detail: String {
        switch self {
        case .wifiOnly: return String(localized: "Wait for Wi-Fi before uploading")
        case .wifiAndCellular: return String(localized: "Back up wherever you are")
        }
    }''')
add(P,
    'title: collection.localizedTitle ?? "Untitled Album",',
    'title: collection.localizedTitle ?? String(localized: "Untitled Album"),')
add(P,
    'title: "All Photos",',
    'title: String(localized: "All Photos"),')

# ============ NetworkPolicy.swift ============
P = "App/Sources/NetworkPolicy.swift"
add(P,
    '''        case .checking:
            return NetworkPolicyDecision(allowsUploads: false, pauseReason: "Checking the network connection…")
        case .unavailable:
            return NetworkPolicyDecision(allowsUploads: false, pauseReason: "Waiting for a network connection")
        case .wifi, .wired:
            return .allowed
        case .cellular, .other:
            if self == .wifiAndCellular { return .allowed }
            return NetworkPolicyDecision(allowsUploads: false, pauseReason: "Waiting for Wi-Fi")''',
    '''        case .checking:
            return NetworkPolicyDecision(allowsUploads: false, pauseReason: String(localized: "Checking the network connection…"))
        case .unavailable:
            return NetworkPolicyDecision(allowsUploads: false, pauseReason: String(localized: "Waiting for a network connection"))
        case .wifi, .wired:
            return .allowed
        case .cellular, .other:
            if self == .wifiAndCellular { return .allowed }
            return NetworkPolicyDecision(allowsUploads: false, pauseReason: String(localized: "Waiting for Wi-Fi"))''')

# ============ PhotosAccount.swift ============
P = "App/Sources/PhotosAccount.swift"
add(P,
    'guard let client else { return .failed("Connect an account before checking it.") }\n        guard !verifying else { return .failed("A connection check is already running.") }',
    'guard let client else { return .failed(String(localized: "Connect an account before checking it.")) }\n        guard !verifying else { return .failed(String(localized: "A connection check is already running.")) }')

# ============ CredentialStore.swift ============
P = "App/Sources/CredentialStore.swift"
add(P,
    '''                return "The Keychain refused the credential: \(detail)."
            case .bound:
                return "Google issued a bound (encrypted) token. This build cannot use it; connect an account whose token is unbound."
            case .corrupt:
                return "The saved credential could not be read and has been discarded. Connect the account again."''',
    '''                return String(localized: "The Keychain refused the credential: \(detail).")
            case .bound:
                return String(localized: "Google issued a bound (encrypted) token. This build cannot use it; connect an account whose token is unbound.")
            case .corrupt:
                return String(localized: "The saved credential could not be read and has been discarded. Connect the account again.")''')

# ============ ProbeLog.swift ============
P = "App/Sources/ProbeLog.swift"
add(P,
    '''            ProbeStep(id: Self.build, title: "App build & launch"),
            ProbeStep(id: Self.extensionEnabled, title: "Google sign-in completed in-app"),
            ProbeStep(id: Self.hostPermission, title: "oauth_token cookie present"),
            ProbeStep(id: Self.cookieRead, title: "App reads the oauth_token cookie"),
            ProbeStep(id: Self.nativeHandoff, title: "Token captured from the web view"),
            ProbeStep(id: Self.appIngest, title: "App ingests the handed-off token (single use)"),
            ProbeStep(id: Self.masterToken, title: "Exchange oauth_token → Android master token"),
            ProbeStep(id: Self.photosToken, title: "Exchange master token → Photos access token"),
            ProbeStep(id: Self.readAccess, title: "Read-only Photos request succeeds"),''',
    '''            ProbeStep(id: Self.build, title: String(localized: "App build & launch")),
            ProbeStep(id: Self.extensionEnabled, title: String(localized: "Google sign-in completed in-app")),
            ProbeStep(id: Self.hostPermission, title: String(localized: "oauth_token cookie present")),
            ProbeStep(id: Self.cookieRead, title: String(localized: "App reads the oauth_token cookie")),
            ProbeStep(id: Self.nativeHandoff, title: String(localized: "Token captured from the web view")),
            ProbeStep(id: Self.appIngest, title: String(localized: "App ingests the handed-off token (single use)")),
            ProbeStep(id: Self.masterToken, title: String(localized: "Exchange oauth_token → Android master token")),
            ProbeStep(id: Self.photosToken, title: String(localized: "Exchange master token → Photos access token")),
            ProbeStep(id: Self.readAccess, title: String(localized: "Read-only Photos request succeeds")),''')

# ============ BackupShortcuts.swift ============
P = "App/Sources/BackupShortcuts.swift"
add(P,
    'return "Open Photos Backup once, then run this shortcut again."',
    'return String(localized: "Open Photos Backup once, then run this shortcut again.")')
add(P,
    '''    static let title: LocalizedStringResource = "Back Up Photos"
    static let description = IntentDescription(
        "Finds new photos and videos in the albums chosen in Photos Backup and starts uploading them to Google Photos. Uploads continue in the background after the action ends."
    )''',
    '''    static let title: LocalizedStringResource = "Back Up Photos"
    static let description = IntentDescription(
        String(localized: "Finds new photos and videos in the albums chosen in Photos Backup and starts uploading them to Google Photos. Uploads continue in the background after the action ends.")
    )''')

# ============ ContinuedBackup.swift ============
P = "App/Sources/ContinuedBackup.swift"
add(P,
    'reason ?? "\(completed.formatted()) of \(total.formatted()) done"',
    'reason ?? String(localized: "\(completed.formatted()) of \(total.formatted()) done")')
add(P,
    'static let title = "Backing up to Google Photos"',
    'static let title = String(localized: "Backing up to Google Photos")')

# ============ UploadQueue.swift ============
P = "App/Sources/UploadQueue.swift"
add(P, 'case .queued: return "Waiting"', 'case .queued: return String(localized: "Waiting")')
add(P, 'case .waitingToRetry(let attempt): return "Retrying (attempt \(attempt + 1))"',
    'case .waitingToRetry(let attempt): return String(localized: "Retrying (attempt \(attempt + 1))")')
add(P, 'case .waitingForICloud: return "Will download from iCloud when you open the app"',
    'case .waitingForICloud: return String(localized: "Will download from iCloud when you open the app")')
add(P, 'case .exporting: return "Preparing"', 'case .exporting: return String(localized: "Preparing")')
add(P, 'case .hashing: return "Checking"', 'case .hashing: return String(localized: "Checking")')
add(P, 'case .checkingDuplicate: return "Looking for a copy"', 'case .checkingDuplicate: return String(localized: "Looking for a copy")')
add(P, 'case .uploading: return "Uploading"', 'case .uploading: return String(localized: "Uploading")')
add(P, 'case .finalizing: return "Finishing"', 'case .finalizing: return String(localized: "Finishing")')
add(P, 'case .alreadyBackedUp: return "Already backed up"', 'case .alreadyBackedUp: return String(localized: "Already backed up")')
add(P, 'case .done: return "Backed up"', 'case .done: return String(localized: "Backed up")')
add(P, 'case .cancelled: return "Stopped by you"', 'case .cancelled: return String(localized: "Stopped by you")')
add(P, 'name: String = "Preparing…"', 'name: String = String(localized: "Preparing…")')
add(P, '?? (isUserPaused ? "You paused backup. Tap Resume to continue." : nil)',
    '?? (isUserPaused ? String(localized: "You paused backup. Tap Resume to continue.") : nil)')
add(P, 'persistenceWarning = "Upload completion could not be saved: \(error.localizedDescription)"',
    'persistenceWarning = String(localized: "Upload completion could not be saved: \(error.localizedDescription)")', 2)
add(P, 'persistenceWarning = "The saved upload queue could not be restored: \(error.localizedDescription)"',
    'persistenceWarning = String(localized: "The saved upload queue could not be restored: \(error.localizedDescription)")')
add(P, 'persistenceWarning = "Upload progress could not be saved: \(error.localizedDescription)"',
    'persistenceWarning = String(localized: "Upload progress could not be saved: \(error.localizedDescription)")')
add(P, 'let nextReason = allowed ? nil : (pauseReason ?? "Waiting for an allowed connection")',
    'let nextReason = allowed ? nil : (pauseReason ?? String(localized: "Waiting for an allowed connection"))')
add(P, 'systemPauseReason = "Paused until iOS gives the app more time"',
    'systemPauseReason = String(localized: "Paused until iOS gives the app more time")')
add(P, 'let interrupted = "Backing this item up kept being interrupted before it finished."',
    'let interrupted = String(localized: "Backing this item up kept being interrupted before it finished.")')
add(P, 'rateLimitPauseReason = "Google asked the app to slow down. Backup continues in "\n            + (minutes <= 1 ? "a minute." : "\(minutes) minutes.")',
    'rateLimitPauseReason = String(localized: "Google asked the app to slow down. Backup continues in ")\n            + (minutes <= 1 ? String(localized: "a minute.") : String(localized: "\(minutes) minutes."))')
add(P, 'recordFailure(name: "Backup stopped", reason: error.message, status: error.status)',
    'recordFailure(name: String(localized: "Backup stopped"), reason: error.message, status: error.status)')
add(P, 'case .exporting: return "exporting it from Photos"', 'case .exporting: return String(localized: "exporting it from Photos")')
add(P, 'case .hashing: return "reading the file"', 'case .hashing: return String(localized: "reading the file")')
add(P, 'case .checkingDuplicate: return "asking Google for an existing copy"',
    'case .checkingDuplicate: return String(localized: "asking Google for an existing copy")')
add(P, 'case .uploading: return "uploading"', 'case .uploading: return String(localized: "uploading")')
add(P, 'case .finalizing: return "finishing it in Google Photos"', 'case .finalizing: return String(localized: "finishing it in Google Photos")')
add(P, 'default: return "starting"', 'default: return String(localized: "starting")')
add(P, 'let reason = "Photos Backup closed unexpectedly more than once while preparing this item, so it was skipped to let the rest of the backup continue. Retry it from here, and please send a diagnostic report."',
    'let reason = String(localized: "Photos Backup closed unexpectedly more than once while preparing this item, so it was skipped to let the rest of the backup continue. Retry it from here, and please send a diagnostic report.")')

# ============ AutomaticBackupCoordinator.swift ============
P = "App/Sources/AutomaticBackupCoordinator.swift"
add(P, 'return "background tasks are unavailable — Background App Refresh is off for this app or the whole device, or this is the Simulator"',
    'return String(localized: "background tasks are unavailable — Background App Refresh is off for this app or the whole device, or this is the Simulator")')
add(P, 'return "iOS already holds too many pending requests from this app"',
    'return String(localized: "iOS already holds too many pending requests from this app")')
add(P, 'return "this build does not declare the task identifier in its Info.plist, or background activity is turned off for this app"',
    'return String(localized: "this build does not declare the task identifier in its Info.plist, or background activity is turned off for this app")')
add(P, 'return "iOS is too busy to start it right now"',
    'return String(localized: "iOS is too busy to start it right now")')
add(P, 'if !preferences.completedOnboarding { return "Onboarding is not finished" }',
    'if !preferences.completedOnboarding { return String(localized: "Onboarding is not finished") }')
add(P, 'if requiringAutomaticBackup, !preferences.automaticBackup { return "Automatic Backup is turned off" }',
    'if requiringAutomaticBackup, !preferences.automaticBackup { return String(localized: "Automatic Backup is turned off") }')
add(P, 'if preferences.selectedAlbumIDs.isEmpty { return "No albums are selected" }',
    'if preferences.selectedAlbumIDs.isEmpty { return String(localized: "No albums are selected") }')
add(P, 'return UIApplication.shared.isProtectedDataAvailable\n                ? "No Google account is connected"\n                : "No Google account is available — if the iPhone has not been unlocked since it restarted, the saved account cannot be read yet"',
    'return UIApplication.shared.isProtectedDataAvailable\n                ? String(localized: "No Google account is connected")\n                : String(localized: "No Google account is available — if the iPhone has not been unlocked since it restarted, the saved account cannot be read yet")')
add(P, 'summary = "interrupted when the app left the foreground or the selection changed"',
    'summary = String(localized: "interrupted when the app left the foreground or the selection changed")')
add(P, 'summary = "no photo library access (\(DiagnosticReportBuilder.photoAuthorization()))"',
    'summary = String(localized: "no photo library access (\(DiagnosticReportBuilder.photoAuthorization()))")')
add(P, 'summary = "backed up \(completed); \(queue.failedCount) failed; \(queue.activeCount) unfinished"\n                + (queue.pauseReason.map { "; paused: \($0)" } ?? "")',
    'summary = String(localized: "backed up \(completed); \(queue.failedCount) failed; \(queue.activeCount) unfinished")\n                + (queue.pauseReason.map { String(localized: "; paused: \($0)") } ?? "")')
add(P, 'if total < 90 { return "\(total) s" }', 'if total < 90 { return String(localized: "\(total) s") }')
add(P, 'if minutes < 90 { return "\(minutes) min" }', 'if minutes < 90 { return String(localized: "\(minutes) min") }')
add(P, 'if hours < 48 { return "\(hours) h \(minutes % 60) min" }',
    'if hours < 48 { return String(localized: "\(hours) h \(minutes % 60) min") }')
add(P, 'return "\(hours / 24) days"', 'return String(localized: "\(hours / 24) days")')
add(P, 'let waiting = queue.rateLimitPauseReason == nil ? nil : "Waiting: Google asked the app to slow down"',
    'let waiting = queue.rateLimitPauseReason == nil ? nil : String(localized: "Waiting: Google asked the app to slow down")')
add(P, 'let reason = idle ? "nothing is left to back up" : (queue.pauseReason ?? "nothing can move on its own")',
    'let reason = idle ? String(localized: "nothing is left to back up") : (queue.pauseReason ?? String(localized: "nothing can move on its own"))')
add(P, '        let settled = max(0, queue.settledRowCount - run.settledBefore)\n',
    '        let settled = max(0, queue.settledRowCount - run.settledBefore)\n        let settledText = settled == 1 ? String(localized: "1 item") : String(localized: "\(settled) items")\n')
add(P, 'summary: "finished \(settled) item\(settled == 1 ? "" : "s"); \(queue.failedCount) failed; \(queue.activeCount) unfinished; ended because \(ending)"',
    'summary: String(localized: "finished \(settledText); \(queue.failedCount) failed; \(queue.activeCount) unfinished; ended because \(ending)")')

# ============ Apply ============
failures = []
applied = 0
for path, old, new, expected in R:
    full = os.path.join(ROOT, path)
    with io.open(full, "r", encoding="utf-8", newline="") as f:
        text = f.read()
    count = text.count(old)
    if count != expected:
        failures.append("%s expected %d got %d: %r" % (path, expected, count, old[:70]))
        continue
    text = text.replace(old, new)
    with io.open(full, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    applied += 1

if failures:
    for f in failures:
        print("FAIL:", f)
    print("applied %d / %d" % (applied, len(R)))
    sys.exit(1)
print("OK: applied %d replacements across %d files" % (applied, len(set(p for p, _, _, _ in R))))
