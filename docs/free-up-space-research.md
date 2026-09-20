# Google Photos "Free up space" and free Pixel uploads

Research date: 2026-09-18. Read-only research. Nothing was posted and no device was touched.

Binary evidence comes from a decrypted Google Photos iOS **7.92.0** IPA. Its main executable (SHA-256 `0395330b…73858d`) and `GooglePhotos_GeneratedFramework` (SHA-256 `be2629c3…6983d6`) hash exactly like the files in gunshot's [`docs/analysis/objc/manifest.json`](https://github.com/tqmane/gunshot/blob/main/docs/analysis/objc/manifest.json), so this is the same build gunshot analysed. They were disassembled with `llvm-objdump`, resolving selector stubs, GOT entries and protobuf descriptors with a small script. Addresses below are static and unslid. "main" means the app executable and "fw" means the generated framework. The phone may be running a newer app version.

## Summary

The iOS app picks Free up space candidates on the phone. For each local photo it looks up the server item by dedup key and applies a fixed set of checks. None of those checks read `storagePolicy`, `quotaChargeable`, the uploading device, or whether backup is turned on. **The Pixel XL profile and the "Storage saver" label are not what blocks our uploads.**

What blocks them:

- **Live Photos.** A local Live Photo is a candidate only if the matched server item has *associated media*, meaning the motion is attached to that same item. Photos Backup uploads the still on its own, so the still matches and the photo counts as backed up. But the item has no associated media, so it is never offered. A Motion Photo, or a still plus a separate MOV, does not match the dedup key at all (fact 2).
- **Edited photos.** These are skipped whenever the server flag `Growth__fix_fus_promise` is on, and that includes photos Google's own backup uploaded.
- **Recent photos.** Photos captured in the last 30 days are held back when the flag or the "Keep items from the last 30 days" switch says so.

A standalone uploader can therefore make plain, unedited stills eligible today. Videos also have to pass a server processing check (`isVideoPlaybackUnavailable`), and I have not verified that for Pixel uploads. An iPhone library is mostly Live Photos, so Live Photos are what matters. Making them eligible means the server item must carry the motion as associated media, which would require reproducing the iOS app's Live Photo upload. Nobody has done that through the Android API, and it is unknown whether the result would stay free. Inferred: this explains why about 8,490 "backed up" photos produce only 0–1 candidates.

ReVanced and similar mods avoid the problem because the official Android app uploads on its own behalf, and Android Motion Photos are single files. gunshot does not address Free up space.

## Findings

### 1. The candidate check in 7.92.0 (Verified: disassembly)

Entry point: `-[PHSDeviceManagementServiceImpl start]` (main `0x1002d5694`) calls `+[PHSDeviceManagementUtils freshStorageTypeAndDeletionCandidatesForAccount:]` (main `0x1019aae14`). The per-asset block is at main `0x1019ab768`, called from `+cachedStorageTypeAndDeletionCandidatesForAccount:` (main `0x1019ab24c`).

| Step | Check | Evidence |
| --- | --- | --- |
| 0 | The library's initial sync is done (`hasInitialSyncCompleted`; if not, error code 0 in domain `com.google.photos.devicemanagement`) and `PHSReachability.state != 1` (otherwise error code 1, which `+isOfflineError:` maps to "You need an internet connection to remove items"). Code 0 goes to `+isSynchronizerNotReadyError:` → `errorAlertControllerForSynchronizerNotReady`. The alert text is presumably "Too soon to free up space" / "Try again in a few minutes once Photos has checked that your photos & videos are backed up", but that last step is Inferred because I didn't read the string lookup. | main `0x1019aae5c`–`0x1019aaed0`, `0x1019ab0fc`, `0x1019ab16c`, `0x1002d5b88`; `PhotosProd.strings` `not_synced_device_management_error_*` |
| 1 | The local asset has a dedup key, either the stored `PHSLocalAsset.localDedupKey` or the result of `GMUAssetFingerprinter fingerprintAsset:networkAccessAllowed:completion:` | `+enumerateSortedLocalAssets:usingBlock:completion:` main `0x1019abba0` |
| 2 | `serverPhotoStore photosForLocalDedupKey:` returns an item. This is where the byte-identity match happens. | `0x1019ab79c` |
| 3 | Server item is not `isPartialBackup` | `0x1019ab7c8` |
| 4 | Server item is not `isVideoPlaybackUnavailable` | `0x1019ab7d4` |
| 5 | `hasOriginalBytes`: Yes/Unknown/No only pick the storage-type wording (`storageTypeFromOriginal:hq:legacy:`). The item is skipped only for **Maybe** when local and server dimensions differ and the local long side is over 2048 px. | `0x1019ab7e0`–`0x1019ab868`, constant 2048.0 |
| 6 | If flag `fixFusPromise` (`Growth__fix_fus_promise`) is on, skip local assets where `hasAdjustments` is true (`PHAsset.hasAdjustments`). If it is off, skip Portrait/depth photos instead. | `0x1019ab880`–`0x1019ab8a8`; fw `0x1249960` |
| 7 | If the local asset `isLivePhoto`, the server item must have `hasAssociatedMedia` | `0x1019ab8b0`–`0x1019ab8c0` |
| 8 | Keep the oldest N, where N is `Gallery__free_up_space_batch_size` or 5000 | `+limitFreeUpSpaceCandidates:accountID:` `0x1019ac2ac`, `0x1019ac624` |
| 9 | Optionally drop items whose `timestampMs` is later than now − 2,592,000 s (30 days) | `+filterOutNewPhotosFromCandidates:` `0x1019ac394` |

Details:

- **Associated media.** `PHSServerPhoto.hasAssociatedMedia` is bit `0x40000`. `initWithMCMediaItem:` sets it when the server media item's `associatedMediaArray_Count` is non-zero (fw `0x124bc38`–`0x124bc50`, getter `0x124da68`). The app's own Live Photo upload builds this pairing through `GMUPairedVideoUploadMediaRequest initWithCredentials:storagePolicy:videoFingerprint:photoFingerprint:…` (fw `0x198e2d0`).
- **The 30-day rule uses the capture date.** `PHSLocalAsset.timestampMs` (fw `0x124a490`) returns the ivar that `initWithPHAsset:source:index:` fills from `PHAsset.creationDate` (fw `0x1249900`–`0x1249924`). Backup date and date added play no part. The filter applies only when `+shouldFilterOutNewPhotosForAccount:` (main `0x1019ac504`) returns YES. That depends on the flag `Sharing__free_up_space_improvement`: Control never filters, and the ExcludeRecentPhotos / IncludeRecentPhotos / IncludeRecentPhotosExcludeforMinors values set the default. It also depends on the user setting `includeNewPhotosForFreeUpSpace` (1 = include, 2 = exclude), shown as "Keep items from the last 30 days".
- **Which list the screen uses.** Both `localAssets` and `localAssetsExcludingNewPhotos` are computed. `-[PHSDeviceManagementServiceImpl confirmAndLaunchWithResult:]` (main `0x1002d5bec`) picks one of them through `-shouldIncludeNewPhotosForFreeUpSpaceWithAccountID:` (main `0x1002d6d4c`), which reads the same flag and user settings as the `+shouldFilterOutNewPhotosForAccount:` mapping above.
- **No backup-on requirement.** I found no check of backup state anywhere in `start` → candidates → `confirmAndLaunchWithResult:`.
- **Out-of-sync state.** The candidate block reads no conflict state. Delete, edit and Locked Folder conflicts are handled separately by `PHSConflictItemController` (e.g. `deleteLocalAssetsForConflicts:obsoleteConflicts:item:`, main `0x1007966a0`) and the "Review out-of-sync changes" screen. I did not determine whether a pending conflict hides an item from Free up space elsewhere.
- **Server eligibility RPC.** The app contains `/$rpc/social.frontend.photos.freeupspacedata.v1.PhotosFreeUpSpaceDataService/PhotosCheckItemsEligibleForFreeUpSpace`, gated by flag `Gallery__free_up_space_rpc`. The request carries `queryArray[].item{dedupKey, itemDimensions{width,height}}`, `loggingBatchId` and `requestType`. The response carries `resultArray[]{item, eligibility}` (protobuf descriptors fw `0x1e96b78`–`0x1e96d70`). The request class is referenced only in `-[PHSPhotosFreeUpSpaceDataServiceImpl photosCheckItemsEligibleForFreeUpSpaceRPC]` (main `0x1008d3d88`). I found no Objective-C caller of `FreeUpSpaceRpcManager checkItemsEligibleWithRequest:isCritical:completionHandler:` and no use of the `freeUpSpaceRpc` flag selector. **Inferred:** in 7.92.0 the server is not consulted on the path above, but a Swift-only caller may exist. The Android app has the same RPC ([decompiled smali](https://github.com/AkrielMrong/my-decompiled-app/blob/HEAD/smali_classes3/bsjx.smali)).
- **UI text** (`Photos.bundle/en.lproj/PhotosProd.strings`): "These items are already safely backed up in your chosen quality" (older `_backedup_message`) and "These items have already been backed up safely to Google Photos" (`_v2`). "Only older photos and videos are removed from your device". "Your device will automatically delete these items in 30 days, or you can delete them now" (the iOS Recently Deleted step). The "chosen quality" wording does not correspond to any storage-policy check in the code.

### 2. Why the phone shows 0–1 candidates (Inferred)

- Most photos from an iPhone camera are Live Photos. Each one Photos Backup uploaded counts as backed up through its still, then fails step 7.
- Edited photos fail step 6 if `fix_fus_promise` is on for the account.
- Photos under 30 days old may fail step 9.
- Plain stills that are unedited and older than 30 days should pass. If there are many such items and they still aren't offered, this model is incomplete, and the server RPC or step 0 is the next suspect.
- Fact 5, the 13 Jun photo Google's app re-uploaded but did not offer: this fits step 3 (the iOS app uploads "a smaller copy until upload completes", string `partial_backup_info_description_v2`, and for Live Photos "a still photo until your motion photo is fully uploaded"), or step 6 if the photo is edited, or the pending delete conflict. I did not work out which.

### 3. The "Storage saver" label (Verified)

- The details label comes from `quotaInfo.storagePolicy`. Pixel XL uploads come back as Standard (1) with `hasOriginalBytes = Yes` (gunshot [`docs/analysis/original-quality-display.md`](https://github.com/tqmane/gunshot/blob/main/docs/analysis/original-quality-display.md) lines 20–35; [PR #51](https://github.com/tqmane/gunshot/pull/51)). `PHSPhotosStorageQuotaDataServiceImpl.photosConvertToStandardStoragePolicyRPC` (fw `0x9aa044`) points to "Standard" being the Storage saver policy. gunshot's fix only changes the label.
- The candidate check never reads `storagePolicy` or `quotaChargeable`, so the label has no effect on Free up space. Because `hasOriginalBytes` is Yes, step 5 never excludes these items. Photos Backup sends field 7 = 3 and field 10 = 1 with model "Pixel XL" (`GPMC/Core/GPMCClient.swift` lines 527–546 at `c3fff29`).

### 4. ReVanced and Android "unlimited" mods (patch source Verified, user reports anecdotal)

- ReVanced "Spoof build info" sets `model = "Pixel XL"`, `device = "marlin"`. "Spoof features" rewrites the feature-name strings in Photos so that `NEXUS_PRELOAD` is on and the later Pixel features are off. The **official app itself** does the upload ([SpoofFeaturesPatch.kt](https://gitlab.com/ReVanced/revanced-patches/-/raw/main/patches/src/main/kotlin/app/revanced/patches/googlephotos/misc/features/SpoofFeaturesPatch.kt); the GitHub repo returns HTTP 451 after a DMCA takedown). GPhotosUnlimited and Pixelify hook `hasSystemFeature` instead ([GPhotosUnlimited](https://github.com/Rev4N1/GPhotosUnlimited)).
- Free up space on Android does work for these uploads. In [ReVanced #5589](https://gitlab.com/ReVanced/revanced-patches/-/work_items/5589) the patched app offered about 7,000 items, then crashed at an Android 2,000-URI limit (user report). An [OzBargain post](https://www.ozbargain.com.au/node/886360) describes a second phone with backup off freeing photos that a real Pixel had uploaded, after a delay of days (anecdotal). The [pixel-backup-gang maintainer](https://github.com/master-hax/pixel-backup-gang/issues/4) says: "The 'free up space' button provides a guarantee that the media has been successfully uploaded before being deleted."
- Label on Android: "This item doesn't take up space in your account storage" ([ReVanced #5752](https://gitlab.com/ReVanced/revanced-patches/-/work_items/5752), user report). Google's own page says the first Pixel gets "unlimited storage in Original quality at no charge" ([answer 6220791](https://support.google.com/photos/answer/6220791)).
- None of this carries over to iOS. Android Motion Photos are single files and don't need an associated-media pairing, and the Android app runs a different candidate implementation.

### 5. gunshot (Verified from docs and code)

- It hooks the native request types (`GMUAssetUploadRequest`, `GMULivePhotoSingleUploadRequest`, `GMUBackgroundAssetUploadRequest`, `GMULivePhotoUploadRequest`). It hands the PhotoKit **original** resources (`photo` / `video` / `pairedVideo`) to its Go uploader (Pixel XL, field 7 = 3), then resumes the native `start`. The app's own fingerprint existence check then succeeds without sending any payload ([`docs/analysis/backup-routing.md`](https://github.com/tqmane/gunshot/blob/main/docs/analysis/backup-routing.md) lines 20–41 and 55–62; PRs [#8](https://github.com/tqmane/gunshot/pull/8), [#30](https://github.com/tqmane/gunshot/pull/30), [#31](https://github.com/tqmane/gunshot/pull/31)).
- Its own analysis notes that uploading originals is not equivalent to the native upload of an edited photo (`docs/analysis/completion-analysis.md` line 17).
- Free up space, 空き容量, 解放 and デバイスから削除 appear nowhere in its docs, code, issues or PRs (English and Japanese search, 2026-09-18). **Inferred:** routing changes what the native request reports, not the server item, so the check above sees the same server model. Live Photos would still need associated media.

### 6. gotohp / gpmc (Verified)

Not found: no issue in [xob0t/gotohp](https://github.com/xob0t/gotohp/issues) or [xob0t/gpmc](https://github.com/xob0t/gpmc/issues) mentions Free up space or iOS backup status. [gpmc #54](https://github.com/xob0t/gpmc/issues/54) says iOS Live Photos are not supported. gpmc commits the file's SHA-1 and looks items up by hash (`gpmc/api.py`).

### 7. Google's documentation and the Help Community (Verified quotes)

- iOS: "Photos and videos older than 30 days can be deleted". Android: items "fewer than 30 days old may be retained" ([answer 6128843, iOS](https://support.google.com/photos/answer/6128843?co=GENIE.Platform%3DiOS)). Neither version mentions backup being on, the uploading device, Live Photos or quality. The iOS backup page says that when backup is off, "Cloud check: Item is backed up" ([answer 6193313](https://support.google.com/photos/answer/6193313?co=GENIE.Platform%3DiOS)).
- Product Experts give contradictory explanations of the 30-day basis, "created" versus "on the device" ([thread 431124381](https://support.google.com/photos/thread/431124381), [thread 460678174](https://support.google.com/photos/thread/460678174)). The 7.92.0 code settles it: capture date, and only when the filter is active.
- A Diamond Product Expert's workaround for "Nothing to free up" on iOS: turn backup off, select items, then "Delete from device" ([thread 387586885](https://support.google.com/photos/thread/387586885)).
- A 2019 Android test found that uploads from another client became eligible only after a new backup from the device ([thread 23611101](https://support.google.com/photos/thread/23611101)). This is old and Android-only, and the iOS code above has no such rule.

## Options for Photos Backup

Ranked by feasibility.

**0. Confirm the model first (no cost, no risk).** Use Photos Backup's PhotoKit access to classify the assets the Google app shows as backed up: Live, edited, captured under 30 days ago, or none of these. Then find one plain photo or screenshot that is **not Live, not edited, captured more than 30 days ago**, already uploaded and counted as backed up. Open Free up space, with "Keep items from the last 30 days" off if the switch is shown. If that photo is offered and Live Photos are not, the check above explains the phone. If it is not offered, something server-side is involved (open question 1).

**1. Photos Backup deletes the device copies itself (standalone; feasible now).** After a per-asset hash lookup confirms the account holds the exact bytes, call `PHAssetChangeRequest.deleteAssets`. iOS asks for confirmation and keeps the items in Recently Deleted for 30 days. Needs: a hash lookup like gpmc's `find_remote_media_by_hash`, plus a policy for Live Photo motion (upload the MOV too, or accept losing it) and for edits (the upload contains the rendered edit, not the original). Risk: deleting a Live Photo removes its motion, and deleting an edited photo removes the unedited original, unless those were uploaded separately. Cheapest test: a 5-item album with one still, one Live Photo and one edited photo.

**2. Google Photos "Delete from device" on selected items (standalone uploader plus the stock app).** Product Experts report this works with backup off. The app warns "These items aren't backed up to Google Photos and this will permanently delete them" for items it doesn't match (`delete_device_originals_subtitle_v2`). Risk: a Live Photo matched by its still counts as backed up, so its motion is deleted without warning. Cheapest test: one non-Live photo and one Live Photo whose MOV was also uploaded; read the dialog text.

**3. Upload Live Photos the way iOS does (research; feasibility unknown).** Reproduce the iOS paired upload (photo + video fingerprints, with the server item holding `associatedMedia`) through photosdata-pa while claiming a Pixel XL. Needs the commit the iOS app sends for `GMULivePhotoSingleUploadRequest` / `GMUPairedVideoUploadMediaRequest`, which could come from gunshot-style hooks or a proxy on a test device. Unknowns: whether the Android API accepts associated media from an Android profile, whether the pairing keeps the item free, and whether the item's dedup key stays the still's SHA-1. Cheapest test: one new Live Photo. Check that (a) the header counts it backed up, (b) Free up space offers it with the 30-day switch off, (c) the web shows motion, (d) account storage does not change.

**4. Let Google's app back up the Live Photos (quota).** Google's own upload creates the pairing, and the app then waits for the full upload to finish (steps 3 and 7). Each item counts against storage, so this is not viable for about 8,500 items within 15 GB. It could work for a small subset.

**5. A tweaked Google Photos app (gunshot-style).** On its own this changes nothing, because eligibility comes from the server item. Hooking steps 6 or 7 to force eligibility would let Google's app delete motion or originals that aren't in the cloud. Rejected.

## Open questions

1. Is `Gallery__free_up_space_rpc` on for this account, and does the installed app version (not 7.92.0) call `PhotosCheckItemsEligibleForFreeUpSpace` on this path? If it does, what `eligibility` does the server return for Pixel XL items?
2. Is `Growth__fix_fus_promise` on for this account? Test: does Free up space offer an **edited** photo that Google's own backup uploaded more than 30 days after capture?
3. Does photosdata-pa accept a commit with associated media (Live Photo pairing) from the Android profile, and does it stay free?
4. What sets `PHSServerPhoto.isPartialBackup`? Not traced. It may explain fact 5.
5. `setTimestampMs:` exists. I only checked the PhotoKit initializer as a source of the timestamp.
6. For Pixel-profile video uploads, what does the server report for `isVideoPlaybackUnavailable`, and do videos count as backed up at all (fact 7 suggests some don't)?
