# Common breaking changes - 1ページ要約（One Page Summary）

## 対象（Target）

Android 16 Behavior Change

From:
- android-15.0.0_r36

To:
- android-16.0.0_r4

Note:

## 適用条件（Applicability）

- 主分類（Primary classification）: `TARGET_SDK_36_CONDITIONAL`
- OS アップデート / 全アプリ（OS update / all apps）: No。Android 16 へ OS アップデートしただけで targetSdkVersion 35 以下の全アプリに既定適用されるとは判断しない。
- targetSdkVersion 36 以上: Yes。上位 behavior の `UNIVERSAL_RESIZABLE_BY_DEFAULT` / 357141415 が targetSdkVersion 36 以上で default enabled。
- その他の必須条件（Other required conditions）: Android 16 以上、display `sw >= 600dp`、game ではない、temporary opt-out なし、user aspect ratio setting exception なし。
- Compat Change ID: `UNIVERSAL_RESIZABLE_BY_DEFAULT` / 357141415
- Compat default state: Android 16 / API level 36 以上を target するアプリで enabled。
- Temporary opt-out: `android.window.PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY=true` を application または activity property として指定。ただし公式文書と AOSP TODO は API 37 以降で使えなくなる予定を示す。

## 早見マトリクス（At-a-Glance Matrix）

| シナリオ | 期待挙動 / リスク |
| --- | --- |
| Android 16 / targetSdkVersion 35 | 本 Behavior Change の既定適用対象外 |
| Android 16 / targetSdkVersion 36 / `sw >= 600dp` / opt-out なし | 制約無視。stretched layout、off-screen component、state preservation risk |
| Android 16 / targetSdkVersion 36 / `sw < 600dp` | large screen 条件を満たさないため対象外 |
| Android 16 / targetSdkVersion 36 / game app | `ApplicationInfo.CATEGORY_GAME` により対象外 |
| Android 16 / targetSdkVersion 36 / user aspect ratio setting exception | user preferenceにより、あらゆるウィンドウサイズへ変更可能とする判定から外れる |
| Android 16 / targetSdkVersion 36 / Activity or Application opt-out | Android 16 では従来の compatibility mode 側へ一時的に戻せる |
| Android 15 / targetSdkVersion 36 | Android 16 の large screen default ignore 差分はないため、同一挙動とは結論しない |

## 要約（Summary）

`Common breaking changes` は、Android 16 の adaptive layout behavior により、固定 orientation / fixed aspect ratio / non-resizable 前提の UI が large screen で崩れる可能性を説明する節である。
platform が直接 UI を壊すのではなく、orientation・resizability・aspect ratio constraints が無視されることで、アプリ側の小画面 portrait 前提、固定座標 animation、状態保存不足が露出する。

## 顧客影響（Customer Impact）

- 要確認

理由:
- targetSdkVersion 36 化、Android 16、`sw >= 600dp`、非 game、opt-out なし、user exception なしが重なった場合に発生する。
- fixed layout / fixed aspect ratio / off-screen animation / state preservation 不足の有無で影響度が変わる。
- opt-out は一時的で、API 37 以降を見据えた adaptive layout 対応が必要。

## 影響対象（Who Is Affected）

- small layout locked in portrait orientation 前提のアプリ。
- portrait / landscape 固定に依存するアプリ。
- fixed aspect ratio 前提の UI を持つアプリ。
- `resizeableActivity=false`、`minAspectRatio`、`maxAspectRatio`、pillarboxing に依存するアプリ。
- off-screen animation / fixed-position component を持つアプリ。
- Activity recreation 時の state preservation が不十分なアプリ。
- configuration change / bounds change を十分に扱っていないアプリ。
- `setRequestedOrientation()` / `getRequestedOrientation()` に依存するアプリ。
- large screen / tablet / foldable / desktop windowing 対応が不十分なアプリ。
- Compose UI / View UI のどちらも対象。window bounds と lifecycle の問題なので UI toolkit だけでは回避できない。

## 対応要否（Required Action）

- 必須対応: targetSdkVersion 36化するアプリで、large screen上の固定方向 / 固定aspect ratio / state preservation不足がある場合。
- 推奨対応: adaptive layout、state preservation、split screen、desktop windowing、foldable posture、rotation、visual regression の確認。
- 一時対応: Android 16 target では `PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY=true` を activity または application に指定できるが、恒久対応として扱わない。
- 不要に近い: large screen でも既に responsive に動作し、rotation / resize / recreation で状態を保持できるアプリ。

## テストマトリクス（Test Matrix）

| 端末 OS | targetSdkVersion | 条件 | 期待挙動 / 確認点 |
| --- | --- | --- | --- |
| Android 15 | 35 | baseline | 従来挙動 |
| Android 16 | 35 | OS update only | 本 Behavior Change の既定適用対象外 |
| Android 16 | 36 | `sw >= 600dp` / opt-out なし | 制約無視、UI stretch / state loss risk |
| Android 16 | 36 | `sw >= 600dp` / Activity opt-out | 該当 activity は一時的に従来挙動 |
| Android 16 | 36 | `sw >= 600dp` / Application opt-out | package 全体で一時的に従来挙動 |
| Android 16 | 36 | `sw < 600dp` | 対象外 |
| Android 16 | 36 | game category | 対象外 |
| Android 16 | 36 | user aspect ratio setting exception | user preferenceにより、あらゆるウィンドウサイズへ変更可能とする判定から外れる |
| Android 16 | 36 | device rotation | Activity recreation / saved state を確認 |
| Android 16 | 36 | split screen / desktop windowing | bounds change、animation、fixed-position UI を確認 |

追加テスト:
- Android 15 / targetSdkVersion 36 が検証可能な場合の比較。
- portrait / landscape / reverse / sensor / user orientation 指定。
- `setRequestedOrientation()` 呼び出し後の挙動。
- `getRequestedOrientation()` の戻り値。
- `resizeableActivity=false`、`minAspectRatio`、`maxAspectRatio` 指定あり / なし。
- `onSaveInstanceState` / ViewModel / SavedStateHandle / Compose `rememberSaveable`。
- navigation state / form input / scroll position / media playback state。
- stretched layout、off-screen animation / component、fixed-size container、absolute-position UI。
- visual regression / screenshot testing。

## 顧客向け説明（Explanation for Customers）

Android 16 へ OS アップデートしただけで、targetSdkVersion 35 以下のアプリにこの変更が既定適用されるとは説明しません。
targetSdkVersion 36 以上に上げると、Android 16 端末の large screen では固定 orientation、非 resizable、min/max aspect ratio、pillarboxing の前提が効かなくなり、UI が伸びる、部品や animation が画面外に出る、Activity recreation で状態を失う、といった問題が起きる可能性があります。
対象アプリは adaptive layout と state preservation を確認してください。

## 根拠（Evidence）

- Official documentation: https://developer.android.com/about/versions/16/behavior-changes-16#common-breaking
- Compat framework: `UNIVERSAL_RESIZABLE_BY_DEFAULT` / 357141415、Android 16 / API 36 以上 target で enabled。
- AOSP files: `ActivityInfo.java`、`WindowManager.java`、`DisplayContent.java`、`ActivityRecord.java`、`AppCompatResizeOverrides.java`、`AppCompatAspectRatioPolicy.java`、`ActivityThread.java`。
- AOSP source context: `DisplayContent#getIgnoreOrientationRequest()` -> `ActivityRecord#isUniversalResizeable()` -> orientation / resizability / aspect ratio policy -> configuration update / relaunch path。
- Diff interpretation: Android 16 tag で large screen default ignore 経路が追加。UI 崩れと state loss は、その結果として app assumptions が崩れるリスク。
- Gate conclusion: Android 16 以上 + targetSdkVersion 36 以上 + `sw >= 600dp` + non-game + opt-out なし + user exception なし。

## 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- 未判断

判断（Decision）:
- 未判断

Owner notes:
- 最終優先度、severity、release readiness、顧客 communication priority は repository owner が判断する。

## 再検証記録（2026-08-22）

- Android 16 の公式 Behavior Change 一覧と最新通常AOSPタグを再確認した。
- 対応する[主レポート](../../../behavior-changes/target/device-form-factors/common-breaking-changes-adaptive-layouts.md)で official section、AOSP project / remote / checkout、解決済み commit、比較 command、dirty risk を再検証した。
- 主レポートの分類、confidence、未確認事項を維持し、実機未実施の項目を Observed 済みへ変更していない。
- 全件の結果は[再検証台帳](../../../analysis/REVALIDATION_2026-08-22.md)を参照する。
