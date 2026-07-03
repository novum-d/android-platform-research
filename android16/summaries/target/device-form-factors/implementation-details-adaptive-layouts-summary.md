# Implementation details - 1ページ要約（One Page Summary）

## 対象（Target）

Android 16 Behavior Change

From:
- android-15.0.0_r36

To:
- android-16.0.0_r4

Note:
- `android16/AGENTS.md` の既定 scope は `android-16.0.0_r1` だが、この調査では依頼に従い `android-16.0.0_r4` を使用した。

## 適用条件（Applicability）

- 主分類（Primary classification）: `TARGET_SDK_36_CONDITIONAL`
- OS アップデート / 全アプリ（OS update / all apps）: No。Android 16 へ OS アップデートしただけで targetSdkVersion 35 以下の全アプリに既定適用されるとは判断しない。
- targetSdkVersion 36 以上: Yes。`UNIVERSAL_RESIZABLE_BY_DEFAULT` / 357141415 が targetSdkVersion 36 以上で default enabled。
- その他の必須条件（Other required conditions）: Android 16 以上、display `sw >= 600dp`、game ではない、temporary opt-out なし、user aspect ratio setting exception なし。
- Compat Change ID: `UNIVERSAL_RESIZABLE_BY_DEFAULT` / 357141415
- Compat default state: Android 16 / API level 36 以上を target するアプリで enabled。
- Temporary opt-out: `android.window.PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY=true` を application または activity property として指定。ただし公式文書と AOSP TODO は API 37 以降で使えなくなる予定を示す。

## 早見マトリクス（At-a-Glance Matrix）

| シナリオ | 期待挙動 |
| --- | --- |
| Android 16 / targetSdkVersion 35 | 本 Behavior Change の既定適用対象外 |
| Android 16 / targetSdkVersion 36 / `sw >= 600dp` / opt-out なし | listed attributes / APIs は実効 orientation / resizeability / aspect ratio constraint として無視 |
| Android 16 / targetSdkVersion 36 / `sw < 600dp` | large screen 条件を満たさないため対象外 |
| Android 16 / targetSdkVersion 36 / full-screen | `screenOrientation`、`resizeableActivity=false`、min/max aspect ratio などは実効制約として無視 |
| Android 16 / targetSdkVersion 36 / multi-window | non-resizable / aspect ratio 前提ではなく bounds change に対応 |
| Android 16 / targetSdkVersion 36 / Activity or Application opt-out | Android 16 では従来の compatibility mode 側へ一時的に戻せる |
| Android 16 / targetSdkVersion 36 / game app | `ApplicationInfo.CATEGORY_GAME` により対象外 |
| Android 16 / targetSdkVersion 36 / user aspect ratio setting exception | user preference により universal resizable から外れる |
| Android 15 / targetSdkVersion 36 | Android 16 の large screen default ignore 差分はないため、同一挙動とは結論しない |

## 要約（Summary）

`Implementation details` は、Android 16 の adaptive layout behavior で無視される manifest attributes / runtime APIs を列挙する節である。
対象は `screenOrientation`、`resizeableActivity`、`minAspectRatio`、`maxAspectRatio`、`setRequestedOrientation()`、`getRequestedOrientation()`。
AOSP では値自体は parsing / retention されるが、Android 16 / targetSdkVersion 36 / `sw >= 600dp` 条件下では WindowManager policy により実効制約として尊重されなくなる。

## 顧客影響（Customer Impact）

- 要確認

理由:
- targetSdkVersion 36 化、Android 16、`sw >= 600dp`、非 game、opt-out なし、user exception なしが重なった場合に発生する。
- fixed orientation、non-resizable、min/max aspect ratio、pillarboxing 前提の UI では実効表示が変わる。
- `getRequestedOrientation()` は戻り値と実効 orientation / bounds を分けて確認する必要がある。

## 影響対象（Who Is Affected）

- `android:screenOrientation` に依存するアプリ。
- portrait / landscape / reverse / sensor / user orientation 固定に依存するアプリ。
- `Activity#setRequestedOrientation()` を runtime に呼ぶアプリ。
- `Activity#getRequestedOrientation()` の戻り値に依存するアプリ。
- `resizeableActivity=false` に依存するアプリ。
- `minAspectRatio` / `maxAspectRatio` に依存するアプリ。
- pillarboxing / compatibility mode に依存するアプリ。
- full-screen 前提の固定 orientation UI を持つアプリ。
- multi-window / split screen / desktop windowing 対応が不十分なアプリ。
- Compose UI / View UI のどちらも対象。

## 対応要否（Required Action）

- 必須対応: targetSdkVersion 36 化するアプリで、listed attributes / APIs を large screen 表示制御に使っている場合。
- 推奨対応: actual window metrics / configuration に基づく adaptive layout、split screen、desktop windowing、visual regression の確認。
- 一時対応: Android 16 target では `PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY=true` を activity または application に指定できるが、恒久対応として扱わない。
- 不要に近い: large screen でも既に responsive に動作し、orientation / aspect ratio / non-resizable 制約に依存していないアプリ。

## テストマトリクス（Test Matrix）

| 端末 OS | targetSdkVersion | 条件 | 期待挙動 / 確認点 |
| --- | --- | --- | --- |
| Android 15 | 35 | baseline | 従来挙動 |
| Android 16 | 35 | OS update only | 本 Behavior Change の既定適用対象外 |
| Android 16 | 36 | `sw >= 600dp` / opt-out なし | attributes / APIs は実効制約として無視 |
| Android 16 | 36 | `sw >= 600dp` / Activity opt-out | 該当 activity は一時的に従来挙動 |
| Android 16 | 36 | `sw >= 600dp` / Application opt-out | package 全体で一時的に従来挙動 |
| Android 16 | 36 | `sw < 600dp` | 対象外 |
| Android 16 | 36 | full-screen | fixed orientation / aspect ratio 前提を確認 |
| Android 16 | 36 | multi-window | resize / bounds change を確認 |
| Android 16 | 36 | game category | 対象外 |
| Android 16 | 36 | user aspect ratio setting exception | user preference により universal resizable から外れる |

追加テスト:
- Android 15 / targetSdkVersion 36 が検証可能な場合の比較。
- `screenOrientation=portrait` / `reversePortrait` / `sensorPortrait` / `userPortrait`。
- `screenOrientation=landscape` / `reverseLandscape` / `sensorLandscape` / `userLandscape`。
- `setRequestedOrientation()` 呼び出し後の実効 orientation / configuration / bounds。
- `getRequestedOrientation()` の戻り値と実効 orientation constraint の差。
- `resizeableActivity=false`、`minAspectRatio`、`maxAspectRatio` 指定あり / なし。
- pillarboxing / compatibility mode の有無。
- visual regression / screenshot testing。

## 顧客向け説明（Explanation for Customers）

Android 16 へ OS アップデートしただけで、targetSdkVersion 35 以下のアプリにこの変更が既定適用されるとは説明しません。
targetSdkVersion 36 以上に上げると、Android 16 端末の large screen では `screenOrientation`、`resizeableActivity=false`、`minAspectRatio`、`maxAspectRatio`、`setRequestedOrientation()` が実効制約として効かなくなります。
`getRequestedOrientation()` の戻り値だけで実際の orientation / bounds を判断せず、実際の configuration と window metrics で確認してください。

## 根拠（Evidence）

- Official documentation: https://developer.android.com/about/versions/16/behavior-changes-16#implementation-details
- Compat framework: `UNIVERSAL_RESIZABLE_BY_DEFAULT` / 357141415、Android 16 / API 36 以上 target で enabled。
- AOSP files: `ActivityInfo.java`、`PackageParser.java`、`Activity.java`、`ActivityClientController.java`、`DisplayContent.java`、`ActivityRecord.java`、`AppCompatResizeOverrides.java`、`AppCompatAspectRatioPolicy.java`。
- AOSP source context: manifest/runtime input -> `ActivityInfo` / `ActivityRecord` -> `DisplayContent#getIgnoreOrientationRequest()` -> `ActivityRecord#isUniversalResizeable()` -> orientation / resizeability / aspect ratio policy。
- Diff interpretation: Android 16 tag で large screen default ignore 経路が追加。manifest / API values は保持され得るが実効制約として無視される。
- Gate conclusion: Android 16 以上 + targetSdkVersion 36 以上 + `sw >= 600dp` + non-game + opt-out なし + user exception なし。

## 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- 未判断

判断（Decision）:
- 未判断

Owner notes:
- 最終優先度、severity、release readiness、顧客 communication priority は repository owner が判断する。
