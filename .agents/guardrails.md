# Guardrails — what NOT to do

1. **Don't hand-edit `PhotosBackup.xcodeproj`.** Edit `project.yml`, run `xcodegen generate`.
2. **Don't change bundle IDs / App Group / URL scheme / BG task ID** without updating entitlements, `Info.plist`s, extension manifest, `HandoffStore`, and README's App identity table together.
3. **Don't log or persist tokens.** No `print(token)`, no fixtures with real credentials, no committing `oauth_token`/master tokens.
4. **Don't reuse tokens or queues across accounts.** Token = single-use; durable queue snapshot is version-checked and account-scoped (`activateAccount`), never shared.
5. **Don't bypass network policy.** Wi-Fi-only / cellular enforcement lives at queue (`setNetworkAccess`) AND request level — keep both.
6. **Don't assume background work completes.** Batches are bounded (25 bg / 250 fg); handle expiration via `suspendForBackgroundExpiration` → requeue. No infinite retry.
7. **Don't break free-team sideload.** No hard dependency on App Group/Keychain existing; degrade to URL handoff + session-only with a warning. Nothing may assume stable signing identity.
8. **Don't expand scope silently:** Live Photo motion is attached through its own `livePhotoMotion` queue rows; token binding unsupported; Google may kill private endpoints anytime — surface as errors, don't paper over.
9. **Tests:** default to offline `xcodebuild test`. Live tests only when user explicitly provides a fresh token.
