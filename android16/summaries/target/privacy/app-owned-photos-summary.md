# App-owned photos summary

## One Page Summary

### 対象

- Android version: Android 16
- From tag: `android-15.0.0_r36`
- To tag: `android-16.0.0_r4`
- Previous targetSdkVersion: 35
- Target targetSdkVersion: 36
- Official documentation URL: https://developer.android.com/about/versions/16/behavior-changes-16#owned-photos
- Category: Privacy
- Section: App-owned photos
- Report: `android16/behavior-changes/target/privacy/app-owned-photos.md`

### 結論

Android 16 / targetSdkVersion 36 以上では、photo/video permission prompt でユーザーが limited selected media access を選ぶ場合、app が所有する photos/videos が photo picker で pre-selected として扱われる。ユーザーがそれらを deselect すると、MediaProvider は grant を削除し、該当 media の `owner_package_name` を `NULL` にするため、app-owned media への owner package access は失われ得る。

Android 16 へ OS アップデートしただけの targetSdkVersion 35 app には、AOSP compat gate 上この変更は default では適用されない。Android 15 OS 上では該当 Android 16 実装を確認できない。

### Applicability Classification

- Primary classification: `TARGET_SDK_36_CONDITIONAL`
- Confidence: High

理由:

- 公式文書は Android 16 以上 + SDK 36 以上 + limited selected media access を条件としている。
- AOSP Android 16 r4 には `ENABLE_OWNED_PHOTOS = 310703690L` があり、`@EnabledAfter(targetSdkVersion = VANILLA_ICE_CREAM)`、つまり targetSdkVersion 36 以上で default enabled。
- `isOwnedPhotosEnabled()` は Android 16 OS gate、compat gate、`revoke_access_owned_photos` flag gate を持つ。
- Android 15 r36 には同名 feature / utility / flag を確認できない。

### Facts

- PhotoPicker query は `ACTION_USER_SELECT_IMAGES_FOR_APP` で `media.owner_package_name IN calling packages` を `is_pre_granted` に含める。
- `PickerDataLayerV2` は app-owned media と user-granted media の count を pre-granted media として扱う。
- User deselection は current session の de-selections table に反映される。
- MediaProvider revoke path は `media_grants` を削除し、owned photos enabled 時は `FilesOwnershipUtils.removeOwnerPackageNameForUris()` を呼ぶ。
- `FilesOwnershipUtils` は対象 URI の `owner_package_name` を `NULL` に更新する。
- MediaProvider の constrained access は images/videos で `OWNER_PACKAGE_NAME` と calling package の一致に依存する。

### Observations

- Pre-selection UI と access revocation は別 code path だが、どちらも MediaProvider / PhotoPicker module 内で確認できる。
- App-owned media だから常にアクセスできる、という前提は Android 16 / targetSdkVersion 36 / limited access flow では成立しない。
- Full photo/video access と limited selected media access は分けて扱う必要がある。
- `EXTRA_PICKER_PRE_SELECTION_URIS` の pre-selection は deselection しても grant revoke にならない別機能であり、本件とは混同しない。

### Hypotheses

- `OWNER_PACKAGE_NAME` が維持されている既存 app-created media は pre-selected 対象になる可能性が高い。
- Uninstall / reinstall 後に owner package が orphaned / null になった media は pre-selected 対象外になり得る。
- Cloud media / cross-profile media は追加検証が必要。

### 期待挙動

| Scenario | Expected behavior |
|---|---|
| Android 16 / targetSdkVersion 35 | default では app-owned pre-selection / deselection revoke は適用されない |
| Android 16 / targetSdkVersion 36 / limited access | app-owned photos/videos が pre-selected される |
| Android 16 / targetSdkVersion 36 / app-owned media deselected | media grant 削除 + `owner_package_name = NULL` により access が revoke され得る |
| Android 16 / targetSdkVersion 36 / app-owned media retained | selected / owner access が継続する |
| Android 16 / targetSdkVersion 36 / full access | full collection access path。limited picker deselection の影響とは分ける |
| Android 16 / targetSdkVersion 36 / permission denied | limited selected grant は作られない。既存 owner access は過去の revoke 状態次第 |
| Android 15 / targetSdkVersion 36 | Android 16 の該当 feature は確認できない |
| Media owned by another app | requesting app の app-owned pre-selection 対象外 |
| App reinstall | owner package が null になっていれば pre-selection 対象外になり得る |

### Developer Action Candidates

- App-created media へのアクセスを常に保証されたものとして扱わない。
- Limited access flow で app-owned photos/videos が deselect されるケースを query / openFile / thumbnail / metadata access でテストする。
- Full grant、limited selected grant、URI grant、owner package access を分けて実装・ログ化する。
- Deselect 後の missing media を permission revocation として扱い、説明・再選択・fallback を用意する。
- App update / reinstall / package name change 後の `OWNER_PACKAGE_NAME` 維持を確認する。

### Test Focus

- Android 16 / targetSdkVersion 35 vs 36
- Android 15 / targetSdkVersion 36 比較
- `READ_MEDIA_IMAGES` / `READ_MEDIA_VIDEO` / `READ_MEDIA_VISUAL_USER_SELECTED`
- Full access / limited access / deny
- App-owned photo / video pre-selected
- User deselects / keeps app-owned media
- Media owned by another app
- MediaStore query / openFile before and after deselection
- App-created media before OS upgrade / before prompt / after grant
- App update / reinstall / package name change
- Work profile / secondary user
- PhotoPicker / PermissionController UI screenshot

### Human Decision Placeholder

- Human decision: 未判断
- Priority: 未判断
- Severity: 未判断
- Release readiness: 未判断
- Customer communication priority: 未判断

## 再検証記録（2026-08-22）

- Android 16 の公式 Behavior Change 一覧と最新通常AOSPタグを再確認した。
- 対応する[主レポート](../../../behavior-changes/target/privacy/app-owned-photos.md)で official section、AOSP project / remote / checkout、解決済み commit、比較 command、dirty risk を再検証した。
- 主レポートの分類、confidence、未確認事項を維持し、実機未実施の項目を Observed 済みへ変更していない。
- 全件の結果は[再検証台帳](../../../analysis/REVALIDATION_2026-08-22.md)を参照する。
