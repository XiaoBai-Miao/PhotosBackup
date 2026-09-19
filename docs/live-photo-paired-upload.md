# How Google Photos iOS uploads a Live Photo with its motion attached

Research date: 2026-09-18. Static analysis only: no network traffic, no device, nothing posted.

Binaries: Google Photos iOS **7.92.0**, the same decrypted build as `docs/free-up-space-research.md`. "fw" is `GooglePhotos_GeneratedFramework`; all upload code lives there. Addresses are static and unslid. Protobuf schemas come from the GPB descriptors that each message's `+descriptor` passes to `allocDescriptorForClass:…fields:fieldCount:`. They were decoded with a small script, and the enums with `allocDescriptorForName:…valueNames:values:count:`.

**Verified** means read directly from a descriptor or from disassembly. **Inferred** means reasoned from names or structure without tracing it.

## Summary

The iOS app attaches Live Photo motion through the **same RPC Photos Backup already calls**. `16538846908252377752` is `social.frontend.photos.data.v1.PhotosFeService.PhotosCreateMediaItems` (fw `0x989c70`: `FCDCreateUnaryRPC(SFPDPhotosCreateMediaItemsRequest, …Response, "/6439526531001121323/16538846908252377752")`). The Android commit body is this same `PhotosCreateMediaItemsRequest` message; iOS just fills in more fields.

iOS pairs the two files in one of two ways:

- **A. New Live Photo (the normal case).** The still and the MOV are uploaded as two separate blobs to `…/uploadmedia/interactive`. One commit follows, whose blueprint carries the still's token and hash plus field **24 `livePhotoInfo`** `{1: videoUploadToken, 2: videoSourceSha1, 3: videoCrc32C}`. The resulting item keeps the still's SHA-1 as its dedup key.
- **B. The still is already on the server without motion.** This is the "repair" path. Only the MOV is uploaded. It is committed as its own blueprint (video token, video SHA-1, video filename) with field **9 `reconcileInfo`** `{2: reconcileType = Phodeo(1), 3: sourceSha1 = the still's SHA-1, 4: photoUploadBlueprint (optional)}`. The app takes this path when its own records say the still is already uploaded (`shouldUploadFingerprint:` returns NO) and no server item for the still's dedup key has associated media. That is exactly the state of the ~8,490 Live Photos Photos Backup has already uploaded.

Both variants can be expressed with the existing `Proto` helpers and the Pixel XL profile; the bodies are given below. **Confidence:** high (Verified) for the message layout, the endpoints and the order of calls. **Unknown:** whether photosdata-pa accepts `livePhotoInfo` or `reconcileInfo` from an Android-profile commit, and whether the motion part stays free. Nothing in the binary addresses either question, and the fact that the schema is shared proves nothing about server policy. One on-device test answers both.

## Request sequence (variant A, `GMULivePhotoSingleUploadRequest`)

For any asset with `mediaSubtypes & PHAssetMediaSubtypePhotoLive`, `-[GMUAutoBackupController uploadNextAsset]` chooses `GMULivePhotoSingleUploadRequest` (fw `0x19791d4`–`0x19791e8`). On the background-upload path it chooses `GMUBackgroundAssetUploadRequest` instead (`0x19790d4`–`0x19790f8`), which ends with the same `livePhotoInfo` commit (`addUploadTokenToBlueprint:` `0x1987fac`–`0x1988028`).

1. **Fingerprint the still.** `startPhotoFingerprint` (fw `0x197d568`) → `GMUAssetFingerprinterImpl fingerprintAsset:` → `GMUFingerprinter` computes CC_SHA1 and CRC32C over the whole file (`internalFingerprintForStream:` `0x1a7e41c`, `fingerprintForData:` `0x1a7e1d8`–`0x1a7e210`). The resource is `+preferredImageResourceFromResources:forAsset:` (`0x19f137c`): FullSizePhoto (5) if `hasAdjustments`, otherwise the best original, which is type 1, or type 4 when type 1 is RAW. Verified.
2. **Branch on the still.** If the delegate's `uploadRequest:shouldUploadFingerprint:` returns NO and `uploadRequest:shouldUploadPairedVideoForPhotoFingerprint:` returns YES, the request sets `useLegacyFlow`, cancels both uploads and runs variant B (`0x197ddb8`–`0x197de34`). The second method is `!phodeoExistsForPhotoFingerprint:` (`0x197b3b0`), and "phodeo exists" means `isDedupKeyRecentlyUploadedAsLivePhoto:` or any `photosForLocalDedupKey:` item with `hasAssociatedMedia` (`-[PHSAutoBackupController autoBackupController:phodeoExistsForPhotoFingerprint:]` `0x272904`). Otherwise the app runs an existence check: `PhotosReadItemsByContentHash`, `/6439526531001121323/5084965799730810217`, built by `+[GMUExistenceRequest rpcForFingerprints:]` `0x1a24928`. **If the still exists, the request finishes without pairing** (`0x197da48`–`0x197daac`). Verified. What `shouldUploadFingerprint:` checks was not traced.
3. **Upload the still.** `startPhotoUpload:` (`0x197e084`) creates a `GMUUploadBlobRequest`. It carries the still's bytes and mimeType, and its album is `@"instant"`. It sets `shouldSkipFingerprintingData`, so the SHA-1 from step 1 is reused. `-[GMUUploadBlobRequest createRpcRequest]` (`0x199681c`) POSTs to `https://photos.googleapis.com/data/upload/uploadmedia/interactive` (or `…/background` when purpose ≠ interactive) with `X-Goog-Hash: sha1=<base64>` (`addScottyHeaderWithSHA1Base64Digest:` `0x1a22d9c`), using GTMSessionUploadFetcher's resumable protocol (`-[GMUUploadRequest createFetcher]` `0x1a4ccd0`). **No metadata body is set on this path.** When the upload finishes, the **raw response body** becomes `photoBlobRef` (`uploadFetcherDidCompleteWithData:error:` `0x1996708`–`0x199676c`). Verified.
4. **Fingerprint the MOV** (started from `startPhotoUpload:` at `0x197e1dc`, so it runs in parallel). `startVideoFingerprint` (`0x197e574`) uses `fingerprintForAssetPairedVideoComponent:`. That fetch picks FullSizePairedVideo (10) if `hasAdjustments`, otherwise PairedVideo (9) (`fetchCurrentBytesForPairedVideoComponent:` `0x19ed940`–`0x19ed99c`). If the asset carries `uneditedLivePhoto`, the fetch uses its PairedVideo instead (`0x197e700`–`0x197e758`). Hashing is the same SHA-1 plus CRC32C. Verified.
5. **Existence check for the MOV.** The query sets `sha1MediaType = PhodeoMovie (2)` because the fingerprint `isForPairedVideoComponent` (`0x1a24a30`–`0x1a24a40`). If the MOV already exists as a phodeo movie, the request completes without committing (`0x197e9e4`–`0x197ea44`). Verified.
6. **Upload the MOV.** `startVideoUpload:` (`0x197ed64`) runs the same `GMUUploadBlobRequest` path to the same URL; the response body becomes `videoBlobRef`. Verified.
7. **Commit.** Once both blob refs exist, `uploadRequest:didCompleteWithBlobRef:` (`0x197fb94`) calls `createLivePhotoMediaItem` (`0x197f1e4`) and then `configureRequestProtoWithFingerprint:…` (`0x197f3e0`):
   - `+[GMUUploadMediaUtils configureBlueprint:…]` (`0x1a7b8c0`) sets `uploadQuality = OriginalBytes (1)` unconditionally. It sets `storagePolicy` to the input when that is 1–4; for input 5 it sets `Full (2)` plus `storagePolicyConfidence = StoragePolicyUnset (1)`. It also sets `fileName` (the still's original filename), `sourceSha1` (the still's SHA-1), `crc32C` when known, `filesystemCreateTime`/`filesystemModTime` from PHAsset creation/modification dates, `localScreenCaptureStatus = 2` for screenshots, and `editList`.
   - `uploadToken = photoBlobRef` (`0x197f554`).
   - `livePhotoInfo.videoUploadToken = videoBlobRef` (`0x197f5b0`), `livePhotoInfo.videoSourceSha1 = videoFingerprint.sha1Digest` (`0x197f5fc`), and `livePhotoInfo.videoCrc32C` when present (`0x197f64c`).
   - The blueprint joins the per-account `GMUBlueprintQueue` (`0x197f848`). `+[GMUCreateMediaRequest requestWithBlueprints:accountID:]` (`0x1a23ab0`) wraps it; `-[PHSGMUOnePlatformRPCManager createMediaItems:isCritical:]` (`0x96bc8c`) sends it with a QoS side channel (`PHSRPCContextWithQOSSideChannel`).
   - Verified.

That makes **two byte uploads and one `PhotosCreateMediaItems`**, plus two `ReadItemsByContentHash` lookups first.

### Variant B (`GMULivePhotoUploadRequest` → `GMUPairedVideoUploadMediaRequest`)

1. `-[GMULivePhotoUploadRequest start]` (`0x1980bf0`) runs a normal photo upload request. When the still already exists this is only the existence check. `photoUploadDidComplete:` (`0x1981e64`) then re-asks `shouldUploadPairedVideoForPhotoFingerprint:` and calls `startVideoFingerprint` (`0x198131c`). Verified.
2. MOV fingerprint and a PhodeoMovie existence check, as in steps 4–5 above. Verified.
3. `startVideoUpload:` (`0x1981b70`) creates `GMUPairedVideoUploadMediaRequest initWithCredentials:storagePolicy:videoFingerprint:photoFingerprint:photoBlueprint:delegate:`, where `photoBlueprint` is `photoUpload.blueprint` and may be nil. Its URL request comes from `GMUCreateUploadMediaURLRequest` (`0x1996194`): a POST to the same `uploadmedia` URL whose **HTTP body is the serialized `SFPDUploadMediaMetadata`**, from `metadataWithStoragePolicy:mediaType:2 (Video)…` (`0x198e980`). Verified.
4. `configureRequestProtoWithFingerprint:` (`0x198e6b8`) builds a blueprint with `blueprintWithStoragePolicy:…fingerprint:<MOV>` and sets `fileName` to the paired-video resource's `originalFilename`. It then sets `reconcileInfo.sourceSha1 = _photoFingerprint.sha1Digest` (ivar `0x7dbfe28`), `reconcileInfo.reconcileType = 1` and `reconcileInfo.photoUploadBlueprint = photoBlueprint.proto`, the last only when non-nil (`0x198e834`–`0x198e918`). Verified.
5. After the upload, `-[GMUUploadRequest commonUploadFetcherDidCompleteWithData:error:]` (`0x1995e4c`) sets `blueprint.uploadToken = <response body>` (`0x199603c`) and queues it for `PhotosCreateMediaItems`. Verified.

That makes **one byte upload (MOV only) and one `PhotosCreateMediaItems`**.

## Message schemas (all Verified from descriptors unless marked)

`SFPDPhotosCreateMediaItemsRequest` (fw `0x1e8686c`), the Android commit body:

| # | Name | Type | Android / Photos Backup today |
|---|---|---|---|
| 1 | blueprintArray | repeated MediaItemBlueprint | field 1 |
| 2 | uploadDeviceInfo | PhotosMCUploadDeviceInfo `{1 serial: string, 3 model: string, 4 manufacturer: string, 5 sdkVersion: int32}` | `{3:"Pixel XL", 4:"Google", 5:28}`. iOS sends `{4:"Apple", 3: UIDevice.model}` (`0x1a23b8c`–`0x1a23bb8`) |
| 3 | clientCapabilityArray | repeated enum ClientCapability `{0 Unknown, 1 OqGuardrailsBackupOnly, 3 PcBarebone}` | bytes `[1,3]` = packed `[1,3]`. iOS sends one value, 1 or 3 (`0x1a23bf0`–`0x1a23c30`) |
| 5 | resultItemMask | PhotosMCMediaItemMask | not sent. iOS sends a full or provider mask |

`…Request_MediaItemBlueprint` (`0x1e86960`, 32 fields; only the relevant ones are listed):

| # | Name | Type | Notes |
|---|---|---|---|
| 1 | uploadToken | bytes | the upload's response body (Photos Backup: `receipt`) |
| 2 | fileName | string | |
| 3 | sourceSha1 | bytes | 20-byte SHA-1 of the uploaded file. This is the dedup key |
| 4 | estimatedCaptureTime | SFPDProto2Timestamp `{1 seconds: int64, 2 nanos: int32}` | Photos Backup sets this; iOS `configureBlueprint` does not |
| 5 / 6 | filesystemCreateTime / filesystemModTime | Proto2Timestamp | iOS sets these from PHAsset dates |
| 7 | storagePolicy | enum `{0 Unknown, 1 Standard, 2 Full, 3 UseManualUploadServerSetting, 4 Basic}` | Photos Backup sends **3**. iOS auto-backup sends 1 or 2 (`-[GMUAutoBackupController storagePolicy]` `0x1975ec0`) |
| 9 | reconcileInfo | ReconcileInfo `{2 reconcileType: enum {0 Unknown, 1 Phodeo, 2 VideoOriginal}, 3 sourceSha1: bytes, 4 photoUploadBlueprint: MediaItemBlueprint}` | variant B |
| 10 | uploadQuality | enum `{1 OriginalBytes, 2 CompressedOriginal, 3 Thumbnail}` | always 1 on iOS and in Photos Backup |
| 13 | itemStateArray | repeated enum `{…, 4 MotionOff, 5 MotionLooping}` | not set on the Live Photo path |
| 14 | editList | PEFEditList | |
| 18 | storagePolicyConfidence | enum `{1 StoragePolicyUnset}` | |
| 24 | **livePhotoInfo** | LivePhotoInfo `{1 videoUploadToken: bytes, 2 videoSourceSha1: bytes, 3 videoCrc32C: fixed32}` | variant A |
| 33 | backupMethod | enum `{1 AutoBackup, 2 InteractiveBackup}` | not set on this path |
| 34 | crc32C | fixed32 | optional |

Response `SFPDPhotosCreateMediaItemsResponse{1 blueprintResultArray: [{1 uploadToken, 2 code: GERRCode, 3 mediaItem: PhotosMCMediaItem, 4 invalidArgumentErrorReason, 5 abortedErrorReason}]}`. Photos Backup's `[1,3,1]` read is `mediaItem.id_p`. `invalidArgumentErrorReason` is one of `{UnrecognizedFormat, UnsupportedFormat, FileSizeTooBig, ResolutionTooBig, FileSizeOrResolutionTooBig, FileNotFound, CndeEditedBytesMissing, InvalidEditList}`; `abortedErrorReason` is `{Crc32CHashMismatch}`; the failure detail `PhotosCreateMediaItemsFailure.errorCode` is `{AccountOutOfStorage, UploadRateLimitExceeded}`.

Where Free up space reads the result: `PhotosMCMediaItem.itemType (5)` → `PhotosMCItemType{1 mediaType, 2 photo, 3 video, 5 associatedMediaArray: [PhotosMCAssociatedMedia], 6 phodeoMomentsMetadata}`. `PhotosMCAssociatedMedia` is `{1 associatedMediaType: {1 Phodeo}, 2 video, 3 downloadURLWithAssociatedMedia, 4 stillImageTimestampMs, 7 motionState, 8 status: {1 Inconsistent, 2 FullyConsistent}}`. Quota is `mediaItem.metadata (2).quotaInfo (35)` → `{1 quotaChargeable: {1 Chargeable, 2 NotChargeable}, 2 quotaChargedBytes, 3 storagePolicy, 4 provisionalChargedBytes, 6 serverStoragePolicy}`.

The existence check is `SFPDPhotosReadItemsByContentHashRequest{1 request: {1 queryArray: [{1 sha1Hash, 2 width, 3 height, 4 matchFullOriginal, 5 sha1MediaType: {1 StandaloneMedia (default), 2 PhodeoMovie}, 6 itemStoragePolicy}], 2 itemMask, 3 resumeToken, 4 viewType (iOS: 1 PhotosNext), 5 freeUpSpaceRequest: bool}}`. Photos Backup's `[1,2,2,1]` read is `response.resultArray.item.id_p`. The mask messages are `MediaItemMask{1 metadata: ItemMetadataMask{…36 quotaInfo…}, 5 itemType: ItemTypeMask{5 associatedMedia}}`.

`SFPDUploadMediaMetadata` (`0x1eab7d0`), the upload-session body: `{1 uploadPurpose: {1 Autobackup, 2 Interactive}, 2 fileGenre: {1 Photo, 2 Video}, 4 storagePolicy (same enum as blueprint 7), 5 width, 6 height, 7 sizeBytes, 9 localFolderName, 11 uploadTokenOutput: {1 Body, 2 Header}}`. Photos Backup's init body `{1:2, 2:2, 3:1, 4:3, 7:size}` decodes as Interactive, **fileGenre = Video (even for stills)**, an unknown field 3, UseManualUploadServerSetting, and the size. Field 3 is not in the 7.92.0 descriptor, and I can't explain it; it comes from gpmc.

Headers (Verified): the extension numbers are GPB message-set extensions (fw `__data` `0x8000878`, `0x80009e8`). `x-goog-ext-173412678-bin` = `FCDClientInfoExtension{1 socialClient: SCSocialClient{1 device, 2 application, 3 platform, 4 trafficType}}`, and Photos Backup's `CgcIAhClARgC` decodes to `{device: AndroidPhone (2), application: Photos (165), platform: Native (2)}`; iOS would send `IosPhone (4)`. `x-goog-ext-174067345-bin` = `FCDQosExtension{1 requestQos: {1 criticality: {0 Sheddable … 2 Critical}}}`, and `CgIIAg==` decodes to `Critical`. Leave both unchanged.

## Proposal for Photos Backup

Keep the Pixel XL profile, the ext headers, `storagePolicy 3` (so that a later edit to 2 doesn't look like a fix) and `uploadQuality 1`. Only unedited Live Photos are in scope at first: edited ones fail Free up space step 6 anyway, and the edited-resource choice (FullSize* vs `uneditedLivePhoto`) adds variables.

**Video bytes.** Export `PHAssetResourceType.pairedVideo` (9) byte-for-byte. Hash it with the same SHA-1 loop as the still, then run the existing upload init and PUT. Send the init body **unchanged**: it is proven for stills, and it matches neither iOS shape (`GMUUploadBlobRequest` sends no body, only `X-Goog-Hash`; `GMUUploadMediaRequest`/`GMUPairedVideoUploadMediaRequest` send `SFPDUploadMediaMetadata`), so its field mapping is unresolved (open question 6). Keep the PUT response as `videoReceipt`. **Do not commit it on its own**: a standalone MOV item would be a separate video in the library and would trip step 5.

**Checks.** The still is checked with today's lookup. For the MOV, use the phodeo variant:

```swift
let movieCheck = Proto.bytes(1, Proto.bytes(1, Proto.bytes(1, videoHash) + Proto.int(5, 2)) + Proto.bytes(2, Data()))
```

`sha1MediaType` has a declared default of 1 (StandaloneMedia), which is why today's lookup for stills, which leaves field 5 out, needs no change.

**A. The still is not on the server.** Commit once with `livePhotoInfo`, as in `commit()`:

```swift
let live = Proto.bytes(1, videoReceipt) + Proto.bytes(2, videoHash)          // 24.3 videoCrc32C optional (fixed32; Proto has no helper)
let metadata = Proto.bytes(1, receipt) + Proto.string(2, prepared.filename) + Proto.bytes(3, prepared.hash)
    + Proto.bytes(4, Proto.int(1, stamp) + Proto.int(2, 46_000_000)) + Proto.int(7, profile.quality) + Proto.int(10, 1)
    + Proto.bytes(24, live)
let body = Proto.bytes(1, metadata) + Proto.bytes(2, device) + Proto.bytes(3, Data([1, 3]))   // same device, same ext headers
```

**B. The still is already backed up (`prepareUpload` returned `.alreadyBackedUp`).** Upload only the MOV, then commit a video blueprint that points at the still:

```swift
let reconcile = Proto.int(2, 1) + Proto.bytes(3, stillHash)                   // 9.4 photoUploadBlueprint omitted (Inferred OK)
let metadata = Proto.bytes(1, videoReceipt) + Proto.string(2, movFilename)    // e.g. "IMG_1234.MOV"
    + Proto.bytes(3, videoHash) + Proto.bytes(4, Proto.int(1, stamp) + Proto.int(2, 46_000_000))
    + Proto.int(7, profile.quality) + Proto.int(10, 1) + Proto.bytes(9, reconcile)
let body = Proto.bytes(1, metadata) + Proto.bytes(2, device) + Proto.bytes(3, Data([1, 3]))   // keep device + capabilities, or the Pixel XL profile is lost
```

In both cases the existing `[1,3,1]` read still returns a media key. **Inferred:** in B it should be the still's key. If it is a new key, the pairing may have failed and the server created a standalone video.

Verification without Free up space: run `ReadItemsByContentHash` on the **still's** SHA-1 with `itemMask = Proto.bytes(1, Proto.bytes(36, Data())) + Proto.bytes(5, Proto.bytes(5, Data()))`, which asks for quotaInfo and associatedMedia. Then read associated media at `[1, 2, 2, 5, 5]` (non-empty means paired) and quota at `[1, 2, 2, 2, 35]` (`1 quotaChargeable`, `2 quotaChargedBytes`). The mask uses field 36 and the data uses field 35 for quotaInfo. The difference is real, not a typo: both numbers come from the descriptors. Inferred: an empty sub-message in a mask means "include this".

**Cheapest on-device test.** Take one fresh, unedited Live Photo that Google's app has never seen. Upload it with variant A and check:
- (a) the Google Photos app counts it as backed up;
- (b) Free up space offers it, with "Keep items from the last 30 days" off;
- (c) the motion plays on photos.google.com;
- (d) account storage is unchanged, and `quotaChargeable` / `quotaChargedBytes` from the lookup above show it is free.

If all four pass, test variant B on a single still Photos Backup has already uploaded before touching the backlog.

## Open questions and risks

1. **Server acceptance and quota: not found.** Nothing in the binary says whether an Android-profile commit may carry `livePhotoInfo` or `reconcileInfo`, or how the paired video is charged. Android's own Motion Photos are single files and never use either field. The Pixel XL exemption may cover the MOV, or the MOV may be charged against quota.
2. **Early exits in the iOS flow.** If the still exists (step 2) or the MOV exists as a phodeo movie (step 5), iOS finishes without pairing. What makes iOS's `shouldUploadFingerprint:` return NO, and so trigger variant B, was not traced.
3. **Google's app might repair these items on its own (Inferred).** With backup on, Google Photos could run variant B for Photos Backup stills that lack motion, uploading the MOV as an **iOS** client under the account's own storage policy. That upload would likely count against quota. It has not been observed.
4. **`photoUploadBlueprint` (9.4).** iOS sets it only when the still was uploaded in the same request. Omitting it is Inferred to be fine.
5. **Timestamps.** Photos Backup uses field 4 and iOS uses fields 5/6. This works today for stills. Whether the server prefers the MOV's own date for the motion is unknown.
6. **Upload init body.** Read as `SFPDUploadMediaMetadata`, it would say `fileGenre = Video` for stills and it carries a field 3 that message does not have. So either it is a different message (gpmc's) or the server does not enforce field 2. It works today; leave it alone.
7. **CRC32C.** It is optional on iOS (set only when `hasCRC32CDigest`). If it is sent and wrong, the commit fails with `Crc32CHashMismatch`. Leave it out unless a `fixed32` helper is added and tested.
8. **Scope.** Not analysed: the `scottySrlService` Swift upload path (`UploadAsset`, `X-Goog-Photos-Upload-Metadata` header), edited Live Photos, and Locked Folder (`PHSLockedPhotoLivePhotoSingleUploadRequest`).
