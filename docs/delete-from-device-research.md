# Google Photos "Delete from device": when the action is offered

Research date: 2026-09-19. Static analysis only. No device was touched and nothing was posted.

Binaries: Google Photos iOS **7.92.0**, the same decrypted build as `docs/free-up-space-research.md`. "main" is the app executable and "fw" is `GooglePhotos_GeneratedFramework`. Addresses are static and unslid. String IDs were resolved through `PHSStringLoaderKey`'s table (fw `0x75cb1f0`). Examples: 1458 = `delete_device_originals_1up`, 1457 = `delete_device_originals`, 1459 = `delete_device_originals_subtitle_v2`, 1460 = `delete_device_originals_title`, 1473 = `delete_some_device_originals_plural_v2`.

**Verified** means I read it in the disassembly. **Inferred** means I reasoned it from names or structure without tracing the code.

## Summary

Delete from device has its **own** check. It does not reuse the Free up space candidate filter. It asks one question: is this tile a server item that the grid has **paired with a photo on this device by dedup key**? That is the same dedup-key match as Free up space step 2. None of the other Free up space checks apply: no `hasAdjustments`/edited check, no Live Photo or `hasAssociatedMedia` check, no partial-backup check, no video-playable check, no server flag and no 30-day rule.

The action is not greyed out when it doesn't apply. It is left out of the menu.

- **Single photo** (overflow menu, `delete_device_originals_1up`): offered only when (1) the viewer was **not** opened from an album, shared album or conversation, (2) the current tile is a server item, and (3) that server item's dedup key maps to at least one local asset in the grid's current store result.
- **Multi-select**: offered only in one grid type (behavior 43, which I infer is the main Photos grid). It appears when the selection contains **at least one local asset**, backed up or not. Backup state affects only the warning dialog, whose title is `delete_device_originals_title`.

**Why some backed-up photos have it and others don't.** Edited-vs-unedited and Live-vs-still are never checked directly. The likeliest cause is the edited photos, and only indirectly: the account holds both the pre-fix original and the edited render as separate tiles, and only the render pairs with the device photo. The original's tile looks backed up but has nothing on the device to delete. The other causes are opening the photo from an album or conversation, and a dedup key that is briefly missing. The candidates are ranked in finding 5.

## Findings

### 1. Single-photo viewer (Verified)

`PHSOneUpDeleteFromDeviceBehavior` is registered unconditionally in `-[PHSOneUpPageViewControllerImpl loadDefaultBehaviors]` (main `0x1017bb0f0`, with no branch around it). `locationForMediaItem:` returns 6, the overflow menu (main `0x10188b228`). `-[PHSOneUpBehaviorController actionItemsForLocation:fromActions:]` (main `0x101888b78`) adds the action only if `shouldShowActionForMediaItem:` is YES **and** `actionItem` is a non-nil `PHSUIAction` (`0x101888c78`–`0x101888cac`).

| Check | Where | Evidence |
| --- | --- | --- |
| Not displaying media from an album | `shouldShowActionForMediaItem:` main `0x10188b1b8` | `isDisplayingMediaFromAlbum` = the data source conforms to `PHSAlbumPhotoOneUpDataSource` (main `0x1031ad84c`, `0x1017c3e34`). The conforming classes are `PHSAlbumDataSourceImpl`, `PHSThreadDataSourceImpl` and `PHSConversationMediaGridDataSource`. |
| The tile expands to ≥1 local asset | `0x10188b1d0` | `findLocalAssetsForMediaItem:` (main `0x1031ae0b4`) runs `dataSource expandedMediaItemArray:` and keeps `itemType == 2` (`PHSLocalAsset`). |
| That local asset was not already deleted in this session | `0x10188b1f8` | `-[PHSOneUpBehaviorHelper isLocalAssetDeleted:]` (main `0x101889550`) checks `presenter.deletedKeys`. |
| The current tile is a server item | `actionItem` main `0x10188b2bc`–`0x10188b2d4` | Returns nil unless `currentServerPhoto` is non-nil. `-[PHSOneUpBehaviorContext currentServerPhoto]` (main `0x1031ad9f4`) returns the item if its `itemType` is 1 (`PHSServerPhoto`), or the contained item if the tile is a `PHSExtendedPhoto` (0) wrapping a server photo. Otherwise it returns nil. |

item types: `PHSExtendedPhoto` 0 (fw `0x1241a9c`), `PHSServerPhoto` 1 (`0x124daf8`), `PHSLocalAsset` 2 (`0x124a13c`), `PHSImageUrlPhoto` 3 (`0x1249760`).

When tapped, `performDeleteDeviceCopy:serverPhoto:` (main `0x10188b5cc`) collects the tile's local assets and server photos. If there are more local assets than server photos, it shows the `MDCAlertController` category method `deleteDeviceCopyAlertControllerWithAccountID:confirmBlock:` (prefixed `phs_`) (main `0x102c62984`: title 1460, message 1459 "…isn't backed up to Google Photos and this will permanently delete it", button "Delete"). Otherwise it deletes straight away through a `deleteLocalAssets` command (`0x10188bb30`), and iOS asks for its own confirmation.

A second behavior, `PHSOneUpLockedPhotoDeleteDeviceCopyBehavior` (main `0x101894ca0`, same string 1458), handles only Locked Folder items (`lockedLocalAsset`/`lockedServerPhoto` in `-[PHSOneUpBehaviorContext isMediaItemActionEnabled:]`, main `0x1031adc14`). It does not apply here.

### 2. Multi-select (Verified, except where noted)

`-[PHSActionsGridModel configureDeleteFromDeviceAction:]` (fw `0xf7baa4`) posts `PHSActionsModelConfigureDeleteFromDeviceAction`. The handler is `-[PHSDeviceActionsBehaviorImpl configureDeleteFromDeviceAction:]` (main `0x100fa1f54`):

1. `gridDestination hasBehavior: 43`. If the grid lacks it, the method returns and no action block is set (`0x100fa1fa4`–`0x100fa1fb8`). **Inferred:** 43 marks the main Photos grid. The same flag gates date-scrubber, zoom, archive-animation and 1-up-context code (e.g. `PHSNavigationBehaviorImpl createOneUpContext` `0x10103a594`, `PHSScrubbingBehaviorImpl` `0x100fc8180`). I did not decode the Swift enum.
2. Expand the selection (`+[PHSNearDupesDisambiguationUtils expandMediaItems:accountID:burstCount:groupCount:]`, then `dataSource expandedMediaItemArray:`) and split it into local assets and server photos (`findSelectedLocalAssets:serverPhotos:inMediaItemArray:`, `0x100fa21e8`).
3. If there are **zero local assets**, return (`0x100fa2060`). Otherwise set `affectedMediaItemsCount` and `actionBlock`.

The grid shows only actions whose `actionBlock` is non-nil (`-[PHSGridActionsConfig configuredActions]` fw `0xf7f378`, `phs_filter:` on `actionBlock != nil`). The button is created as `PHSUIAction` type 19 with title 1457 `delete_device_originals` in `-[PHSGridActionsConfig initWithAccountID:]` (fw `0xf7df90`–`0xf7dfdc`).

Server photos are not required. On tap, `deleteDeviceCopiesWithLocalAssets:serverPhotos:` (main `0x100fa2490`) maps both lists to `localDedupKey` (blocks `0x100fa2e28`/`0x100fa2e30`) and subtracts the server keys from the local keys:

- nothing left over: delete with no Google dialog (`0x100fa25b4` → `0x100fa2664`)
- some left over and ≥1 server photo: title 1460, message 1473 "Some of these items aren't backed up to Google Photos…"
- no server photos at all: title 1460 and message 1459 "…aren't backed up…"

### 3. How a tile gets paired with a device photo (Verified)

- **Grid build.** `-[PHSStoreResult dedupServerPhotos:sortedDedupedPhotosWithCollapsedGroups:sortedLocalAssets:doAllBurstAssets:]` (fw `0x112b3fc`) walks the local assets. If a local asset has a `localDedupKey` and a server photo with that key exists, the asset is filed under the key and **not shown as its own tile**, so the server photo is the tile (`0x112b994`–`0x112b9f0`). If no server photo has that key, the local asset gets its own tile (item type 2) and has no `currentServerPhoto`.
- **Keyless local assets.** A local asset with no key yet is matched heuristically. The server photo must have the same capture time (to the second, `clientCreationTimestampMs`/`timestampMs`), the same `dimensions`, not be `isForkedCopy`, and be the **only** such candidate (`0x112b76c`–`0x112bad4`). With zero or several candidates, the asset stays its own local tile.
- **Tap time.** `-[PHSStoreResult expandMediaItems:withOptions:]` (fw `0x1129bf4`, options 3) takes the server photo's **primary** `localDedupKey` and returns `serverPhotosForLocalDedupKey:` + `localAssetsForLocalDedupKey:`. Both are plain dictionary lookups (fw `0x11299a0`, `0x1129b14`). A local tile expands only to itself.
- **Stale keys.** When the local store restores a local asset, it clears the asset's dedup key and queues it for re-fingerprinting if the stored `localDedupKeyTimeMs` differs from `PHAsset.modificationDate` (or `creationDate`): `updateLocalDedupKey:nil localDedupKeyTimeMs:0` in `dbRestoreLocalAssetsWithStmt:…assetsNeedingDedupKey:` (fw `0x87e89c`–`0x87e94c`). `-[PHSLocalAsset localDedupKey]` is just the stored ivar (fw `0x1249e3c`).
- **Server items are merged only when their keys are identical.** `+[PHSServerPhotoStoreResult sortAndDedupServerPhotos:withServerPhotosByLocalDedupKey:]` (fw `0x112d5a4`) lists a server item as a tile if its key is nil or not seen before (`0x112d754`, `0x112d764`–`0x112d77c`). An item whose key is already present is appended under that key and not listed (`0x112d6cc`–`0x112d748`). Two uploads with different SHA-1s therefore become two tiles. Nothing on this path drops edited or forked copies. `isForkedCopy` is read only by the keyless heuristic (`0x112b894`), and `PHSServerPhoto.isEditedCopy` (fw `0x124da08`) only by logging and the editor's save-as-copy.
- **Server-side equivalents.** The server photo store also files an item under each of its `equivalentLocalDedupKeys` when flag bit 39 is set (`-[PHSServerPhotoStoreModel stAddToDedupMap:]` fw `0x8a7de8`–`0x8a7e5c`). See open question 2.

### 4. What it does not check (Verified by absence)

I grepped these ranges for `hasAdjustments`, `hasEdit`, `hasUserEdit`, `hasPendingEdit`, `isPartialBackup`, `hasAssociatedMedia`, `isVideoPlaybackUnavailable`, `hasOriginalBytes`, `fixFusPromise`, `isLivePhoto`, `storagePolicy`, `quotaChargeable` and `creationDate`, and found no matches: main `0x10188b0e4`–`0x10188c238` (1-up behavior), `0x101889550`–`0x1018896f4` (helper), `0x101888b78`–`0x101889134` (menu builder), `0x1031ad84c`–`0x1031ae208` (1-up context), `0x100fa1f54`–`0x100fa2e3c` (multi-select), and fw `0x1129bf4`–`0x112a1f0` and `0x112b3fc`–`0x112bef8` (expansion and dedup). The only `timestampMs` reads are in the keyless-asset heuristic, not an age filter. No selector names a server flag on either path.

So it does **not** share the Free up space function (`+[PHSDeviceManagementUtils …DeletionCandidates…]`, main `0x1019ab768`). Both depend on the same key equality, local `localDedupKey` versus server dedup key. **Inferred:** anything Free up space offers can also be deleted this way from the Photos tab, but not the other way round.

### 5. Why it shows on some backed-up photos and not others

This model makes a checkable prediction. From the Photos tab, Delete from device should be offered on essentially every photo Google counts as backed up (about 8,500). That includes the ~8,100 edited ones that Free up space refuses (it offers 461). If that holds, the rules differ as described here. If edited photos are missing it broadly, this model is wrong.

Ranked by how well each fits. Each gate is Verified. Whether it applies on this phone is Inferred.

1. **The tile is a cloud-only duplicate (high confidence the mechanism exists, medium that it is what was seen on device; edited photos only).** For the ~8,100 edited photos, the account holds two server items: the pre-fix upload of the **original** and the post-fix upload of the **edited render**. They have different SHA-1s, so the grid shows them as two tiles (finding 3). Only the item whose key equals the device photo's key pairs, and per the on-device finding in project notes, that is the edited render. The original upload is a separate server-only tile with the same capture time, so it sits next to its pair. It looks backed up (no cloud-off badge) but expands to no local asset, so it has no Delete from device. Unedited photos have one server item and don't show this split. **Inferred:** if the server stacks the two copies as a near-duplicate group, whichever copy is primary decides whether the stack offers the option.
2. **Where the photo was opened from (Verified gate; applies only when comparing across views).** The same photo shows the option when opened from the Photos tab and loses it when opened from an album, shared album or conversation (`isDisplayingMediaFromAlbum`). Multi-select offers it only in a grid with behavior 43. Search results and other views also depend on whether their data source has a store result with local assets: if the ivar is nil, `expandedMediaItemArray:` returns the tile unchanged (fw `0xccb1c8`, `0x102c8a4`), so no local asset is found.
3. **The device photo's key is missing or stale (low–medium).** Any change that moves `modificationDate` clears the key until the app re-fingerprints the photo. That includes edits and favorites, and possibly iOS's own updates. While the key is missing, pairing falls back to the unique-match heuristic, and that fails when an edited photo has two same-second, same-size server copies. The photo then shows as a local tile with no Delete from device in the single viewer. It shows up again after re-fingerprinting.
4. **Google doesn't count it as backed up (Verified; it covers the 43).** A local-only tile has no `currentServerPhoto`, so the single viewer never offers the action. Multi-select still does, with the "aren't backed up" warning.
5. **Transient (low).** `-[PHSAllPhotosDataSource dataChanged]` (main `0x1031ace0c`) sets the store-result ivar to nil before refetching, and `expandedMediaItemArray:` (main `0x1031acdac`) then returns tiles unexpanded. A menu opened during heavy sync could miss the action once.

Live Photos make no difference to whether the option is offered. A Live Photo with motion attached is still one server item keyed by the still's SHA-1, and neither path reads `hasAssociatedMedia`. Deletion goes through `-[PHSDeletePhotoCommand deleteLocalAssets]` (main `0x1018dec14`), and the block code right after that method tail-calls `deleteAssets:` (`0x1018df5f0`), the `PHAssetChangeRequest` API. The call is Verified. That the block belongs to this method is Inferred from where it sits. **Inferred from PhotoKit semantics:** deleting the asset removes its still and its motion together, and I found no motion-specific warning in either dialog.

## How to tell which one it is

1. For an edited photo that lacks the option in the Photos tab, look at the neighbouring tiles. If an identical-looking tile with the same time sits next to it and **that** one offers Delete from device, it is cause 1. Photos Backup can check this without the phone: an edited asset whose original SHA-1 and rendered SHA-1 both resolve to server items has two tiles.
2. Open a photo that shows Delete from device from the **Photos tab**. Then reach the same photo through an album and compare. If the option disappears, it is cause 2.
3. If neither applies, reopen the photo a few minutes later without editing or favoriting it. If the option appears, it is cause 3 or 5.

## Open questions

1. What exactly is grid behavior 43, and which destinations have it (Photos tab, device folders, search)? It is a Swift enum in `GridDestination.hasBehavior` (fw `0xf9ac48`) and is not decoded.
2. Does the grid's `serverPhotosByLocalDedupKey` include `equivalentLocalDedupKeys`? If it does, a device photo paired only through an equivalent key is hidden as a separate tile. But the lookup at tap time uses the server item's **primary** key, so the action would be missing. What sets flag bit 39, and does it apply to Google's own uploads of edited photos?
3. Does the server group an original and its edited copy into a near-duplicate stack (`serverGroupPhotoMap`), and which one becomes primary?
4. What exactly bumps `PHAsset.modificationDate` on iOS 26 for photos nobody touched? That decides how often cause 3 happens.
