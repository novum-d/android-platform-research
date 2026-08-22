# 大画面で画面向き・リサイズ可否・アスペクト比制約を無視するプラットフォーム API の変更（sw >= 600dp） - 1ページ要約

## 対象

Android 17 Behavior Change

比較元:
- android-16.0.0_r4

比較先:
- android-17.0.0_r1

以前の targetSdkVersion:
- 36

対象 targetSdkVersion:
- 37

## 適用条件

- 主分類（Primary classification）: TARGET_SDK_37_CONDITIONAL
- OS アップデート / 全アプリ（OS update / all apps）: 主条件ではない。Android 17 target で opt-out が無効化される。
- targetSdkVersion 37 以上: 該当。
- その他の必須条件（Other required conditions）: `sw >= 600dp`、game 以外、orientation / resizability / aspect ratio restriction、Android 16 opt-out 依存。
- Compat Change ID: `357141415L` (`UNIVERSAL_RESIZABLE_BY_DEFAULT`), `447301631L` (`DISABLE_OPT_OUT_UNIVERSAL_RESIZABLE_BY_DEFAULT`)
- Compat default state: Android 16 target で制約無視 enabled、Android 17 target で opt-out disabled。

## 早見マトリクス

| シナリオ | 影響 |
| --- | --- |
| Android 16 / targetSdkVersion 36 | large screen 制約無視は有効だが opt-out property が効く。 |
| Android 17 / targetSdkVersion 36 | Android 16 互換として opt-out が効く想定。 |
| Android 17 / targetSdkVersion 37 | opt-out property が無効。large screen で orientation / resizability / aspect ratio restrictions が無視される。 |

## 要約

Android 17 では、targetSdkVersion 37 以上のアプリで、Android 16 / SDK 36 では可能だった large screen 制約無視への opt-out が利用できなくなる。

AOSP では `UNIVERSAL_RESIZABLE_BY_DEFAULT = 357141415L` が Android 16 target 以上で制約無視を有効化し、`DISABLE_OPT_OUT_UNIVERSAL_RESIZABLE_BY_DEFAULT = 447301631L` が Android 17 target 以上で `PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY` を無効化する。

## 顧客影響

- 固定 portrait、non-resizable、固定 aspect ratio を前提にした UI は、tablet、foldable、desktop windowing、multi-window で想定外に resize / full area 表示される可能性がある。
- Android 17 target では Android 16 opt-out に依存できない。
- large screen adaptive UI、configuration change、fold / unfold、multi-window resize の検証が必要。

## 対応要否

- 必須対応候補: Android 16 opt-out property、`screenOrientation`、`resizeableActivity`、`minAspectRatio` / `maxAspectRatio`、`setRequestedOrientation()` 依存を棚卸しする。
- 推奨対応: `sw >= 600dp` の tablet / foldable / desktop windowing でレイアウトを検証する。
- 例外確認: game category、user aspect ratio setting、`sw < 600dp`。

## 根拠（Evidence）

- 公式ドキュメント: https://developer.android.com/about/versions/17/behavior-changes-17
- AOSP: `core/java/android/content/pm/ActivityInfo.java` の `UNIVERSAL_RESIZABLE_BY_DEFAULT = 357141415L`
- AOSP: `UNIVERSAL_RESIZABLE_BY_DEFAULT` は `@EnabledAfter(targetSdkVersion = Build.VERSION_CODES.VANILLA_ICE_CREAM)`
- AOSP: `services/core/java/com/android/server/wm/AppCompatResizeOverrides.java` の `DISABLE_OPT_OUT_UNIVERSAL_RESIZABLE_BY_DEFAULT = 447301631L`
- AOSP: `DISABLE_OPT_OUT_UNIVERSAL_RESIZABLE_BY_DEFAULT` は `@EnabledAfter(targetSdkVersion = Build.VERSION_CODES.BAKLAVA)` で、Android 17 / API 37 から opt-out property が効かないと comment している。
- AOSP: `DisplayContent.isLargeScreen` は `smallestScreenWidthDp >= 600dp` を大画面条件にする。
- AOSP: `ActivityRecord.canBeUniversalResizeable`はgameを除外し、大画面かつchange enabledの場合に、あらゆるウィンドウサイズへ変更可能とする判定の候補にする。

## 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- 人間による判断が必要

判断（Decision）:
- 未判断

## 再検証記録（2026-08-22）

- Android 17 の公式 Behavior Change 一覧と最新通常AOSPタグを再確認した。
- 対応する[主レポート](../../../behavior-changes/target/device-form-factors/large-screen-orientation-resizability-aspect-ratio.md)で official section、AOSP project / remote / checkout、解決済み commit、比較 command、dirty risk を再検証した。
- 主レポートの分類、confidence、未確認事項を維持し、実機未実施の項目を Observed 済みへ変更していない。
- 全件の結果は[再検証台帳](../../../analysis/REVALIDATION_2026-08-22.md)を参照する。
