import Foundation
import SwiftUI

/// One line in the feasibility checklist.
struct ProbeStep: Identifiable, Equatable {
    enum State: Equatable {
        case pending
        case running
        case passed
        case failed
        case skipped

        var symbol: String {
            switch self {
            case .pending: return "circle"
            case .running: return "circle.dotted"
            case .passed: return "checkmark.circle.fill"
            case .failed: return "xmark.octagon.fill"
            case .skipped: return "minus.circle"
            }
        }

        var tint: Color {
            switch self {
            case .pending: return .secondary
            case .running: return .blue
            case .passed: return .green
            case .failed: return .red
            case .skipped: return .orange
            }
        }
    }

    let id: String
    let title: String
    var state: State = .pending
    var detail: String = ""
}

/// Ordered, observable checklist shared by the UI and the orchestrator.
@MainActor
final class ProbeLog: ObservableObject {
    @Published private(set) var steps: [ProbeStep]

    // Step identifiers, in run order.
    static let build = "build"
    static let extensionEnabled = "ext-enabled"
    static let hostPermission = "host-permission"
    static let cookieRead = "cookie-read"
    static let nativeHandoff = "native-handoff"
    static let appIngest = "app-ingest"
    static let masterToken = "master-token"
    static let photosToken = "photos-token"
    static let readAccess = "read-access"

    init() {
        steps = [
            ProbeStep(id: Self.build, title: String(localized: "App build & launch")),
            ProbeStep(id: Self.extensionEnabled, title: String(localized: "Google sign-in completed in-app")),
            ProbeStep(id: Self.hostPermission, title: String(localized: "oauth_token cookie present")),
            ProbeStep(id: Self.cookieRead, title: String(localized: "App reads the oauth_token cookie")),
            ProbeStep(id: Self.nativeHandoff, title: String(localized: "Token captured from the web view")),
            ProbeStep(id: Self.appIngest, title: String(localized: "App ingests the handed-off token (single use)")),
            ProbeStep(id: Self.masterToken, title: String(localized: "Exchange oauth_token → Android master token")),
            ProbeStep(id: Self.photosToken, title: String(localized: "Exchange master token → Photos access token")),
            ProbeStep(id: Self.readAccess, title: String(localized: "Read-only Photos request succeeds")),
        ]
    }

    func set(_ id: String, _ state: ProbeStep.State, _ detail: String = "") {
        guard let i = steps.firstIndex(where: { $0.id == id }) else { return }
        steps[i].state = state
        if !detail.isEmpty { steps[i].detail = detail }
    }

    func detail(_ id: String) -> String {
        steps.first(where: { $0.id == id })?.detail ?? ""
    }

    func reset(from id: String) {
        guard let start = steps.firstIndex(where: { $0.id == id }) else { return }
        for i in start..<steps.count {
            steps[i].state = .pending
            steps[i].detail = ""
        }
    }
}
