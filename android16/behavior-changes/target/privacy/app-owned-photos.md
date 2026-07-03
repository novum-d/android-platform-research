# App-owned photos

## 調査メタデータ

- Android version: Android 16
- Version directory: `android16`
- From tag: `android-15.0.0_r36`
- To tag: `android-16.0.0_r4`
- Previous targetSdkVersion: 35
- Target targetSdkVersion: 36
- Behavior Change section: App-owned photos
- Official documentation URL: https://developer.android.com/about/versions/16/behavior-changes-16#owned-photos
- Official documentation category: Privacy
- Report output file: `android16/behavior-changes/target/privacy/app-owned-photos.md`
- Summary output file: `android16/summaries/target/privacy/app-owned-photos-summary.md`
- Applicability classification: `TARGET_SDK_36_CONDITIONAL`
- Confidence: High

Scope note: `android16/AGENTS.md` は To tag を `android-16.0.0_r1` としているが、本調査では依頼どおり公開済み Android 16 tag として `android-16.0.0_r4` を使用した。

Classification note: この変更は Android 16 / API level 36 以上を target する app に対して、selected media permission flow で limited access を選んだ場合に発生する。targetSdkVersion 36 は必要条件だが、Android 16 OS、photo/video permission prompt、limited selected media access、app-owned image/video の存在、ユーザーの保持または deselection が追加条件になるため `TARGET_SDK_36_CONDITIONAL` と分類する。

## Official Documentation Review

2026-07-03 に公式ドキュメントの `#owned-photos` セクションを再確認した。対象ページは `Last updated 2026-07-01 UTC` と表示されていた。

確認した公式記述:

- Android 16 以上の端末上で、SDK 36 以上を target する app が photo / video permission を求めたとき、ユーザーが selected media への limited access を選ぶと、app が所有する写真が photo picker で pre-selected される。
- ユーザーは pre-selected item を deselect でき、その場合 app の当該写真・動画への access が revoke される。

依頼文の Original statements / Applicability details と公式本文に実質差分はない。なお、公式文書は「photos」と書いているが、AOSP の compat change comment と revoke 実装は photos and videos / image or video を対象としている。

## AOSP Evidence Scope

Primary evidence:

- `platform/packages/providers/MediaProvider`
  - `android-15.0.0_r36`
  - `android-16.0.0_r4`
- `platform/frameworks/base`
  - `android-16.0.0_r4`

Checkout hygiene:

- `frameworks-base` checkout は clean。
- `tmp/aosp-checkouts/MediaProvider` checkout は clean。
- 両 checkout で `android-15.0.0_r36` / `android-16.0.0_r4` tag が存在することを確認済み。
- Android 15 baseline では `ENABLE_OWNED_PHOTOS`、`revoke_access_owned_photos`、`FilesOwnershipUtils`、`removeOwnerPackageNameForUris`、`isOwnedPhotosEnabled` は見つからなかった。

Compat official page:

- 公式 Android 16 compatibility framework changes ページでは `ENABLE_OWNED_PHOTOS` / `310703690` / `OWNED_PHOTOS` の掲載を確認できなかった。
- AOSP `MediaProvider.java` の `@ChangeId` / `@EnabledAfter` を compat framework evidence の primary source として扱う。

## Original Statements Verification

| Original statement | Verification |
|---|---|
| SDK 36 以上を target する app が Android 16 以上で photo/video permission prompt を出し、limited selected media access を選ぶと、app-owned photos が photo picker で pre-selected される | Confirmed. `MediaProvider.ENABLE_OWNED_PHOTOS` は Change ID `310703690` で `@EnabledAfter(targetSdkVersion = VANILLA_ICE_CREAM)`。Android 16 / Baklava OS gate と flag gate もある。PhotoPicker query は `ACTION_USER_SELECT_IMAGES_FOR_APP` のとき、既存 media grants に加えて `media.owner_package_name IN calling packages` を `is_pre_granted` に含める。 |
| ユーザーが pre-selected item を deselect すると、その写真・動画への app access が revoke される | Confirmed. Picker / MediaProvider の revoke path は grant を削除し、owned photos feature が enabled の場合は `FilesOwnershipUtils.removeOwnerPackageNameForUris()` により `files.owner_package_name` を `NULL` に更新する。MediaProvider の constrained access は `OWNER_PACKAGE_NAME` と calling package の一致に依存するため、deselect 後は app-owned access が失われ得る。 |

## Facts

### Compat gate は Android 16 OS + targetSdkVersion 36 以上

Reviewed source:

- `packages/providers/MediaProvider/src/com/android/providers/media/MediaProvider.java`
- `packages/providers/MediaProvider/mediaprovider_flags.aconfig`

Android 16 r4 の `MediaProvider` には次の compat change がある。

- `ENABLE_OWNED_PHOTOS = 310703690L`
- `@ChangeId`
- `@EnabledAfter(targetSdkVersion = Build.VERSION_CODES.VANILLA_ICE_CREAM)`
- comment: app target sdk が `BAKLAVA` 以上なら、app が作成した photos/videos への access を失う可能性がある

`Build.VERSION_CODES.VANILLA_ICE_CREAM` は API 35 なので、`@EnabledAfter(35)` は targetSdkVersion 36 以上で default enabled になることを意味する。

`isOwnedPhotosEnabled(uid)` は次をすべて要求する。

- OS が Baklava / Android 16 以上であること
- `CompatChanges.isChangeEnabled(ENABLE_OWNED_PHOTOS, uid)` が true
- `Flags.revokeAccessOwnedPhotos()` が true

`mediaprovider_flags.aconfig` では `revoke_access_owned_photos` が `is_fixed_read_only: true` として定義され、description は app-created photos への access revoke を可能にする flag と説明している。

Source context:

- Entry point / caller: PhotoPicker query、MediaProvider revoke media grants、MediaStore query / access filtering。
- Relevant responsibility: app-owned media を picker 上で pre-granted / pre-selected として扱い、ユーザー deselection を access control に反映する。
- Baseline Android behavior: Android 15 r36 では該当 compat change / feature flag / ownership removal utility を確認できない。
- Target Android behavior: Android 16 r4 では targetSdkVersion 36 以上の app UID で feature が enabled になる。
- Diff kind: added behavior / changed targetSdk gate / added owner revocation path。
- Applicability support: Android 16 / targetSdkVersion 35 と Android 16 / targetSdkVersion 36 で expected behavior が分かれる。

### PhotoPicker は app-owned media を pre-granted として扱う

Reviewed source:

- `packages/providers/MediaProvider/src/com/android/providers/media/photopicker/v2/sqlite/MediaProjection.java`
- `packages/providers/MediaProvider/src/com/android/providers/media/photopicker/v2/PickerDataLayerV2.java`
- `packages/providers/MediaProvider/src/com/android/providers/media/photopicker/v2/model/PreviewMediaQuery.java`
- `packages/providers/MediaProvider/src/com/android/providers/media/photopicker/v2/sqlite/PickerMediaDatabaseUtil.java`

`MediaProjection.getIsPreGranted(intentAction)` は `MediaStore.ACTION_USER_SELECT_IMAGES_FOR_APP` の場合にだけ special handling を行う。`isOwnedPhotosEnabled(mCallingPackageUid)` が true で calling package names がある場合、`current_media_grants.file_id IS NOT NULL` または `media.owner_package_name IN calling packages AND media._user_id = userId` を満たす行を `is_pre_granted = 1` にする。

`PickerDataLayerV2.fetchCountForPreGrantedItems()` も、owned photos enabled の場合は `media.owner_package_name` と `media_grants.owner_package_name` の両方を pre-granted count に含める。コメントは「media either owned by the app or user has granted access」と説明している。

`PreviewMediaQuery` は owned photos enabled の場合、`current_media_grants.file_id IS NOT NULL` または `media.owner_package_name IN calling packages` を対象にしつつ、`current_de_selections.file_id IS NULL` を要求する。つまり、session 中にユーザーが deselect した item は preview / selected state から除外される。

`PickerMediaDatabaseUtil.getMediaPageQuery()` は owned photos enabled のとき calling UID から package names を取得し、`MediaProjection` に渡す。

Interpretation:

- UI そのものの描画 code ではなく、PhotoPicker UI が利用する query / projection 層で app-owned media が pre-granted として渡される。
- `ACTION_USER_SELECT_IMAGES_FOR_APP` は permission prompt photo picker flow の action であり、通常の `ACTION_PICK_IMAGES` とは異なる。
- `MediaStore.EXTRA_PICKER_PRE_SELECTION_URIS` は通常 picker の pre-selection extra であり、API doc は「de-selection does not revoke grant」と説明している。この app-owned photos behavior とは別物である。

### Deselect 後は media grants と owner package name が更新される

Reviewed source:

- `packages/providers/MediaProvider/src/com/android/providers/media/MediaProvider.java`
- `packages/providers/MediaProvider/src/com/android/providers/media/FilesOwnershipUtils.java`

MediaProvider の revoke media grants path では、caller が self / PhotoPicker / shell として認可された後、package UID から package names と userId を取得する。

`uris != null` の場合:

- `mMediaGrants.removeMediaGrantsForPackage(packageNames, uris, userId)` を呼ぶ。
- `isOwnedPhotosEnabled(packageUid)` が true なら `mFilesOwnershipUtils.removeOwnerPackageNameForUris(packageNames, uris, userId)` を呼ぶ。
- revoke count を `OWNED_PHOTOS_REVOKED_FROM_APP_REPORTED` として stats log に記録する。

`FilesOwnershipUtils.removeOwnerPackageNameForUris()` は対象 URI の `_ID` を temp table に入れ、`files` table を次の条件で update する。

- `_ID` が対象 URI の id に含まれる
- `owner_package_name IN (calling packages)`
- `_user_id = packageUserId`

更新内容は次の通り。

- `generation_modified` を更新
- `owner_package_name` を `NULL` にする

Class / method comment も、app が作成した画像が preselected され、ユーザーが deselect したら `owner_package_name` を null にして access を revoke する、と説明している。

Interpretation:

- Deselect は単なる picker UI の selection 解除ではなく、MediaProvider database の ownership field を更新する。
- `owner_package_name` が null になるため、以後の app-owned media access は従来の owner package match では成立しない。
- ただし full photo/video permission、URI grant、または別の正当な access path があれば、当該 media への access が別途成立する可能性はある。

### MediaProvider access control は owner package name と selected media grants を組み合わせる

Reviewed source:

- `packages/providers/MediaProvider/src/com/android/providers/media/MediaProvider.java`
- `packages/providers/MediaProvider/src/com/android/providers/media/AccessChecker.java`
- `packages/providers/MediaProvider/src/com/android/providers/media/LocalCallingIdentity.java`

`MediaProvider.appendAccessCheckQuery()` は、global / full collection access がある場合は特別な filtering を行わない。`READ_MEDIA_VISUAL_USER_SELECTED` による selected access がある場合は、`media_grants` による user selected access と、constrained access を OR で追加する。

`AccessChecker.getWhereForConstrainedAccess()` は images / videos について `getWhereForOwnerPackageMatch(callingIdentity)` を返す。`getWhereForOwnerPackageMatch()` は `OWNER_PACKAGE_NAME IN calling package names` を生成する。

`LocalCallingIdentity.checkCallingPermissionUserSelected()` は user select mode を `READ_MEDIA_VISUAL_USER_SELECTED == true && READ_MEDIA_IMAGES == false && READ_MEDIA_VIDEO == false` として判定する。

Interpretation:

- Limited selected media access では、user selected grants と owner package match が access filtering に関与する。
- App-owned item を deselect して `owner_package_name` が null になると、owner package match での access は成立しなくなる。
- Full access (`READ_MEDIA_IMAGES` / `READ_MEDIA_VIDEO`) では full collection access 側が先に成立し、この selected access / owner constrained path とは異なる挙動になる。

### App uninstall / reinstall は owner package semantics に影響する

Reviewed source:

- `packages/providers/MediaProvider/src/com/android/providers/media/MediaProvider.java`
- `apex/framework/java/android/provider/MediaStore.java`

`MediaProvider.orphanEntries()` は package が orphaned になったとき、`owner_package_name = packageName AND _user_id = userId` に一致する files row の `owner_package_name` を null にする。

`MediaStore.MediaColumns.OWNER_PACKAGE_NAME` API doc は、この値は media を contributed した package name であり、ownership を reliable に決定できない場合は `NULL` になり得ると説明している。

Interpretation:

- App update with same package では通常 owner package identity は維持される可能性が高い。
- App uninstall / reinstall、package name change、ownership が不明な media では `OWNER_PACKAGE_NAME` が null になり、app-owned pre-selection の対象にならない可能性がある。

### Permission definitions は Android 16 API surface に存在する

Reviewed source:

- `frameworks/base/core/res/AndroidManifest.xml`
- `frameworks/base/core/api/current.txt`

Android 16 r4 API surface には以下が public permission として存在する。

- `android.permission.READ_MEDIA_IMAGES`
- `android.permission.READ_MEDIA_VIDEO`
- `android.permission.READ_MEDIA_VISUAL_USER_SELECTED`

`READ_MEDIA_VISUAL_USER_SELECTED` の manifest comment は、permission prompt photo picker でユーザーが選んだ image/video files への read access を許可する permission と説明している。`READ_MEDIA_IMAGES` / `READ_MEDIA_VIDEO` を request した app には自動的に manifest へ追加される、とも説明されている。

## Observations

- この Behavior Change は `MediaStore.ACTION_USER_SELECT_IMAGES_FOR_APP` を使う permission prompt photo picker flow に強く結びついている。
- App-owned 判定は MediaStore row の `OWNER_PACKAGE_NAME` / calling UID に紐づく package names / `_user_id` に依存する。
- App-owned media が pre-selected されることと、ユーザーが deselect したあとアクセスが revoke されることは別の code path で実装されている。
- Deselect 後の revoke は `media_grants` の削除だけでなく、`files.owner_package_name = NULL` によって app-owned access の根拠を消す。
- `EXTRA_PICKER_PRE_SELECTION_URIS` の pre-selection は、この Behavior Change の pre-selection と異なり、API doc 上は deselect しても grant revoke にならない。
- PermissionController 側の permission dialog 起動 path は今回の source pass では詳細追跡していない。ただし PhotoPicker / MediaProvider module 内で preselection query と revoke enforcement は確認できている。

## Hypotheses

- 既存 app-owned media は、Android 16 へ OS upgrade しただけでは targetSdkVersion 35 app に対してこの revoke behavior が default 有効にならない。
- Android 16 / targetSdkVersion 36 の app では、過去に app が作成した media でも `OWNER_PACKAGE_NAME` が維持されていれば permission prompt picker で pre-selected される可能性が高い。
- App reinstall 後の既存 media は owner package が orphaned / null になっていれば pre-selected されず、app-owned access の前提にもならない可能性がある。
- Cloud media / cross-profile media など PhotoPicker provider 境界をまたぐ item は、local MediaProvider の `owner_package_name` evidence だけでは扱いを断定できない。

## Conclusions

- 公式文書の主張は AOSP evidence と一致する。
- Android 16 / targetSdkVersion 36 以上では、selected media permission flow で app-owned image/video が pre-granted / pre-selected として扱われる。
- ユーザーが pre-selected app-owned item を deselect すると、MediaProvider は selected media grant を削除し、owned photos feature が enabled の場合は `OWNER_PACKAGE_NAME` を null にする。これにより、app-owned media だから常に access できる、という前提は成立しなくなる。
- Android 16 へ OS update しただけの targetSdkVersion 35 app には、AOSP compat gate 上、この変更は default では適用されない。
- Android 15 OS 上の targetSdkVersion 36 app では、Android 15 r36 に該当 feature 実装がないため、この Android 16 behavior は発生しないと考える。

## Expected Behavior Matrix: OS / targetSdkVersion

| Scenario | Expected behavior |
|---|---|
| Android 16 / targetSdkVersion 35 | `ENABLE_OWNED_PHOTOS` は default disabled。app-owned photos/videos の pre-selection / deselection revoke は原則発生しない。 |
| Android 16 / targetSdkVersion 36 | `ENABLE_OWNED_PHOTOS` が default enabled。limited selected media flow で app-owned media が pre-selected され、deselect で access revoke され得る。 |
| Android 15 / targetSdkVersion 36 | Android 15 r36 に該当 feature / utility / flag がないため、Android 16 の app-owned photos behavior は発生しない。 |

## Expected Behavior Matrix: Detailed Conditions

| Scenario | Expected behavior |
|---|---|
| Android 16 / targetSdkVersion 35 / limited selected media access | Android 16 r4 の compat gate 上、app-owned pre-selection / revoke behavior は default では適用されない。 |
| Android 16 / targetSdkVersion 36 / limited selected media access | App-owned images/videos が pre-granted / pre-selected として picker に渡される。 |
| Android 16 / targetSdkVersion 36 / full photo/video access | Full collection access が成立するため、selected media allowlist / owner constrained access とは別 path。limited selection の pre-selection / deselection revoke flow は主経路ではない。 |
| Android 16 / targetSdkVersion 36 / permission denied | Limited selected media flow の grants は作られない。既存の owner package access は、過去に deselect revoke されていなければ別途成立し得る。 |
| Android 16 / targetSdkVersion 36 / app-owned photo pre-selected | `owner_package_name IN calling packages` かつ userId match なら `is_pre_granted = 1` になり得る。 |
| Android 16 / targetSdkVersion 36 / app-owned video pre-selected | AOSP comment / query / revoke path は image or video / photos and videos を対象にしている。video も対象と解釈できる。 |
| Android 16 / targetSdkVersion 36 / app-owned media deselected by user | media grant が削除され、owned feature enabled なら `owner_package_name` が null に更新される。以後 owner match access は失われ得る。 |
| Android 16 / targetSdkVersion 36 / app-owned media retained by user | Pre-granted / selected item として残り、selected media grant または owner package access により access が継続する。 |
| Android 16 / targetSdkVersion 36 / media owned by another app | Requesting app の `owner_package_name` と一致しないため、app-owned pre-selection にはならない。ユーザーが選択した場合のみ selected media grant の対象。 |
| Android 16 / targetSdkVersion 36 / media created before permission prompt | `OWNER_PACKAGE_NAME` が requesting app と一致していれば pre-selected 対象になり得る。 |
| Android 16 / targetSdkVersion 36 / media created after permission grant | その session の pre-selection には通常含まれない。将来の permission prompt / picker query では ownership があれば対象になり得る。 |
| Android 16 / targetSdkVersion 36 / app update with same package | Package identity が維持され、`OWNER_PACKAGE_NAME` が残っていれば app-owned と扱われ得る。 |
| Android 16 / targetSdkVersion 36 / app reinstall | Uninstall / orphan 処理で `owner_package_name` が null になる場合、再インストール後に pre-selection 対象外になり得る。 |
| Android 16 / targetSdkVersion 36 / work profile / secondary user | `_user_id` 条件が query / update に含まれるため user boundary ごとに扱われる。実機で profile 別検証が必要。 |
| MediaStore query after deselection | `owner_package_name` が null になった item は owner package constrained access に一致しない。full permission / URI grant がなければ見えなくなり得る。 |
| MediaStore openFile after deselection | Query と同様、owner package access だけを前提にした open は失敗し得る。full permission / URI grant は別途評価される。 |
| Photo Picker UI pre-selection | Query projection の `is_pre_granted` により UI 側で selected として扱われる根拠がある。 |
| PermissionController selected media allowlist update | MediaProvider revoke path は PhotoPicker caller を許可し、grant removal と owner removal を行う。PermissionController の詳細 UI caller path は追加確認対象。 |

## Impact by App Type

| App type | Impact |
|---|---|
| 写真・動画を作成 / 保存するアプリ | App-created media が limited access prompt で pre-selected され、ユーザー deselect により access を失う可能性がある。 |
| カメラアプリ | 自アプリで撮影保存した media への継続 access を前提にしている場合、deselection 後の query / open failure に備える必要がある。 |
| ギャラリー / メディア管理アプリ | App-owned と user-selected の違い、full access と limited access の違いを UI / cache に反映する必要がある。 |
| 写真編集 / 動画編集アプリ | 編集結果を MediaStore に保存する場合、保存物が app-owned として pre-selected され得るが、ユーザー deselect 後は owner access を失い得る。 |
| SNS / messaging / posting app | 投稿用に保存・生成した media への再アクセスで limited access state を考慮する必要がある。 |
| バックアップ / 同期アプリ | App-owned media が always accessible とは限らない。MediaStore query result の欠落を permission / deselection として扱う必要がある。 |
| `READ_MEDIA_IMAGES` / `READ_MEDIA_VIDEO` を要求するアプリ | Full grant では影響が限定的だが、ユーザーが limited access を選ぶ flow では影響を受ける。 |
| `READ_MEDIA_VISUAL_USER_SELECTED` を扱うアプリ | Selected media grants と owner package access の両方を分けて扱う必要がある。 |
| Permission denial / revocation に備える必要があるアプリ | Deselect は user-driven revocation として扱い、再リクエスト、説明、fallback を用意する必要がある。 |

## Developer Action Candidates

- App-owned media へのアクセスを「常に可能」と仮定しない。
- Limited selected media access の permission flow で、app-owned item がユーザーに deselect され得る前提で query / open / thumbnail / metadata access を実装する。
- `READ_MEDIA_IMAGES` / `READ_MEDIA_VIDEO` の full grant、`READ_MEDIA_VISUAL_USER_SELECTED` の limited grant、URI grant を分けて扱う。
- MediaStore query result から app-created media が消えるケースを permission state / user deselection として扱う。
- App-owned media の cache index は MediaStore `_ID` だけでなく、実アクセス可能性を再確認する。
- App update / reinstall / package rename 後に `OWNER_PACKAGE_NAME` が期待どおり残るかを検証する。
- User-facing explanation と re-request flow を用意する。ただし deselection は明示的なユーザー選択なので、無限再要求は避ける。

## Test Focus

- Android 15 端末上の targetSdkVersion 35
- Android 16 端末上の targetSdkVersion 35
- Android 16 端末上の targetSdkVersion 36
- Android 15 端末上の targetSdkVersion 36 が検証可能な場合の比較
- `READ_MEDIA_IMAGES` request
- `READ_MEDIA_VIDEO` request
- `READ_MEDIA_VISUAL_USER_SELECTED` behavior
- Full access / limited access / deny
- App-owned photo pre-selected
- App-owned video pre-selected
- User deselects app-owned media
- User keeps app-owned media selected
- Media owned by another app
- MediaStore query result before / after deselection
- MediaStore openFile / thumbnail / metadata access before / after deselection
- App-created media before OS upgrade
- App-created media before permission prompt
- App-created media after limited permission grant
- App update / reinstall / package name change
- Work profile / secondary user
- PhotoPicker UI / PermissionController UI screenshot verification
- Permission grant / revoke / settings change flow
- Graceful fallback / user-facing explanation / re-request flow

## Missing Evidence / Residual Risk

- PermissionController 側の permission dialog から `ACTION_USER_SELECT_IMAGES_FOR_APP` を起動する full caller path は今回詳細追跡していない。
- Cloud media provider / remote media で `owner_package_name` と pre-selection がどう扱われるかは、local MediaProvider evidence だけでは断定できない。
- Work profile / cloned app / secondary user は `_user_id` evidence があるが、実機 UI での verification が望ましい。
- Official compatibility framework page に Change ID `310703690` は掲載されていなかったため、compat page 上の force-enable / force-disable documentation は確認できない。ただし AOSP `@ChangeId` と `@EnabledAfter` は確認済み。

## Facts / Observations / Hypotheses / Conclusions

### Facts

- 公式 App-owned photos セクションは SDK 36 以上 + Android 16 以上 + limited selected media access flow を条件としている。
- AOSP Android 16 r4 には `ENABLE_OWNED_PHOTOS = 310703690L` があり、`@EnabledAfter(targetSdkVersion = VANILLA_ICE_CREAM)` で gate されている。
- `isOwnedPhotosEnabled(uid)` は Android 16 OS gate、compat gate、`revoke_access_owned_photos` flag gate を持つ。
- PhotoPicker query は app-owned media を `is_pre_granted` に含める。
- Deselect revoke path は `media_grants` を削除し、`owner_package_name` を null にする。
- Android 15 r36 には同名 feature / utility / flag は確認できない。

### Observations

- Pre-selection は PhotoPicker query / projection 層で実装されている。
- Access revocation は MediaProvider database update と access filtering によって実効化される。
- Full access、limited access、denied は同じ影響ではない。
- App-owned media と user-selected media は同じ picker selection UI に現れるが、access の根拠は異なる。

### Hypotheses

- Existing app-owned media は `OWNER_PACKAGE_NAME` が維持されていれば Android 16 / targetSdkVersion 36 の prompt で pre-selected される。
- Reinstall / orphaned media は owner package が null になり、pre-selection 対象から外れる可能性がある。
- Cloud media は local provider と同じ ownership semantics ではない可能性がある。

### Conclusions

- Primary classification は `TARGET_SDK_36_CONDITIONAL`。
- Android 16 へ OS update しただけの targetSdkVersion 35 app と、targetSdkVersion 36 化した app の影響は分けて説明すべき。
- App-owned photos/videos は limited access prompt でユーザーに pre-selected として提示されるが、ユーザーが deselect すると access が revoke され得る。
- 顧客向けには「app が作成した media だから常に読める」という前提を見直す必要がある、と説明するのが適切。
