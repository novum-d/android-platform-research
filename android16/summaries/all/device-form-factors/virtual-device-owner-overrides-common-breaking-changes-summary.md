# Common breaking changes One Page Summary

## 対象

- Android version: Android 16
- From / To: `android-15.0.0_r36` -> `android-16.0.0_r4`
- Previous / Target targetSdkVersion: 35 -> 36
- Official documentation: https://developer.android.com/about/versions/16/behavior-changes-all#common-breaking
- Category: Device form factors
- Parent section: Virtual device owner overrides
- Section: Common breaking changes

## 結論

Primary classification:
- `OS_UPDATE_ALL_APPS`

ただし無条件の all apps impact ではない。Android 16 上で、trusted / privileged virtual device owner が管理する selected virtual device / trusted virtual display へ app が投影され、orientation / aspect ratio / resizability restrictions が無視される場合に影響し得る。

targetSdkVersion 36 化は本件の必要条件ではない。Android 16 / targetSdkVersion 35 と Android 16 / targetSdkVersion 36 のどちらも、virtual device owner projection 条件を満たす場合は同様に large screen UI impact を受け得る。

## 何が起きるか

Android 16 では、virtual device owner projection 環境で app settings override が可能になる。親項目の `Per-app overrides` により、external display へ投影するときに orientation、aspect ratio、resizability restrictions が無視され得る。

`Common breaking changes` は、その結果として car displays、Chromebooks、PC displays、VR displays などの large screen form factors 上で、small portrait phone display 向け layout が崩れる可能性を示す subsection である。

## 影響が出る条件

| 条件 | 判定 |
| --- | --- |
| Android 16 OS update | Conditional impact。projection 条件が必要。 |
| targetSdkVersion 36 | 必須ではない。 |
| local physical phone display | 原則として本件の影響外。 |
| virtual device owner projection | 主な影響条件。 |
| trusted / privileged owner | 必要。ordinary app は任意に同じ override を使えない。 |
| selected virtual display override enabled | 必要。 |
| large screen / external display | breakage が顕在化しやすい。 |
| small portrait phone UI assumption | high risk。 |
| adaptive layout 対応済み | lower risk。 |

## AOSP evidence

- `VirtualDisplayConfig.Builder#setIgnoreActivitySizeRestrictions(boolean)` は、fixed orientation、aspect ratio、resizability を無視する virtual display property を設定する SystemApi。
- `DisplayManagerService` は trusted virtual display でない場合、この request を無視する。trusted display の場合だけ WindowManager に display-level override を設定する。
- `DisplayWindowSettings` / `DisplayContent` は display uniqueId / `Display.TYPE_VIRTUAL` に紐付く ignore state を保持する。
- `AppCompatOrientationPolicy` は eligible virtual display で orientation request を `SCREEN_ORIENTATION_USER` 相当に扱う。
- `AppCompatAspectRatioOverrides` は display ignore state を fullscreen / aspect ratio override 条件に含める。
- `VirtualDeviceManager` / `AndroidManifest.xml` evidence では、`CREATE_VIRTUAL_DEVICE` は `internal|role`、`ADD_TRUSTED_DISPLAY` は `signature|role` で、ordinary app 向け runtime permission ではない。
- `DisplayContent` / `TaskFragment` / `ConfigurationContainer` / `WindowMetrics` は display / task bounds / density から app-facing configuration / metrics を計算するため、projection 先の large bounds が layout に反映され得る。

## 期待挙動マトリクス

| Scenario | Expected behavior |
| --- | --- |
| Android 16 / targetSdkVersion 35 / local physical display | 本件の selected virtual display override は原則適用されない。 |
| Android 16 / targetSdkVersion 36 / local physical display | 同上。targetSdkVersion 36 large screen compat changes は別項目。 |
| Android 16 / targetSdkVersion 35 / projected by virtual device owner | override enabled なら UI impact が出得る。 |
| Android 16 / targetSdkVersion 36 / projected by virtual device owner | targetSdkVersion 35 と同様。 |
| Android 15 / targetSdkVersion 36 | 関連 API / flag は存在するが、Android 16 behavior change とは分けて実機確認が必要。 |
| car display / Chromebook / PC / VR projection | large / landscape / desktop-class bounds で phone portrait UI が崩れ得る。 |
| orientation / aspect ratio / resizability ignored | `screenOrientation`、min/max aspect ratio、`resizeableActivity=false` 前提は保護にならない可能性。 |
| adaptive layout | lower risk。WindowMetrics / resource qualifier / input modality QA は必要。 |

## 影響対象

- companion app streaming / virtual device projection で利用されるアプリ。
- phone portrait 専用 UI のアプリ。
- fixed orientation / fixed aspect ratio / `resizeableActivity=false` に依存するアプリ。
- car display / Chromebook / PC / VR display で利用され得るアプリ。
- camera、media、map、game、productivity、form、document editing など window size / orientation / input modality に敏感なアプリ。
- custom `DisplayMetrics` / `WindowMetrics` assumptions を持つアプリ。

## テスト観点

- Android 16 / targetSdkVersion 35 と 36 の比較。
- local physical display と virtual device owner projection の比較。
- selected virtual device override enabled / disabled。
- portrait-only activity を large landscape display へ投影。
- `screenOrientation`、`resizeableActivity`、minAspectRatio / maxAspectRatio combinations。
- WindowMetrics / Configuration / DisplayInfo / resources qualifier changes。
- keyboard / mouse / touch / controller input。
- screenshot / screen recording による clipping、stretching、letterboxing / pillarboxing、touch target regression 確認。

## Recommended action candidates

- orientation / aspect / resizability restrictions を UI correctness の主要な防御策として扱わない。
- adaptive layouts、WindowMetrics、responsive resources、large screen QA を整備する。
- projection 環境を再現できない場合でも、large landscape / freeform / external display 相当の bounds で先に検証する。
- customer communication では OS update impact、targetSdkVersion impact、projection-only impact、local display non-impact を分離する。

## Evidence gaps

- `android-15.0.0_r36` にも関連 API / aconfig flag が存在するため、AOSP diff だけで導入時点は断定しない。
- Android 15 product build での feature enablement は device / product config / 実機確認が必要。
- car / Chromebook / PC / VR の具体挙動は OEM / product implementation と framework evidence を分ける必要がある。

## Human Decision Placeholder

- Final priority:
- Final severity:
- Customer communication priority:
- Release readiness:
- Required app-side migration:
- Required QA scope:
