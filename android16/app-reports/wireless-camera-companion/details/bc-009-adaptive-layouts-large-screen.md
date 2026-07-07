# BC-009: Adaptive layouts

## 基本情報

Behavior Change 文書:
- URL: https://developer.android.com/about/versions/16/behavior-changes-16#adaptive-layouts
- Section: Adaptive layouts

既存調査:
- [android16/behavior-changes/target/device-form-factors/adaptive-layouts.md](../../../behavior-changes/target/device-form-factors/adaptive-layouts.md)
- [android16/summaries/target/device-form-factors/adaptive-layouts-summary.md](../../../summaries/target/device-form-factors/adaptive-layouts-summary.md)

## 対象アプリとの関係

関連するアプリ機能:
- カメラ live view。
- リモート操作。
- 画像一覧 / full-screen viewer。
- setup / pairing flow。
- portrait 固定 UI。

アプリが該当する可能性:
- Conditional。large screen 上で fixed orientation / non-resizable / aspect ratio 制限に依存する場合に該当。

## 適用条件分類

主分類:
- `TARGET_SDK_36_CONDITIONAL`

必要条件:
- Android 16 以上。
- targetSdkVersion 36 以上。
- `sw >= 600dp`。
- non-game。
- temporary opt-out なし。
- user aspect ratio setting exception なし。

Confidence:
- High。

## AOSP / 公式根拠

既存 Android16 調査で確認済み:
- `UNIVERSAL_RESIZABLE_BY_DEFAULT` / 357141415。
- `@EnabledAfter(VANILLA_ICE_CREAM)`。
- orientation / resizability / aspect ratio restrictions を large screen で無視。
- temporary opt-out property。

## アプリ影響

想定される影響:
- fixed orientation の live view が landscape / large window に伸びる。
- `resizeableActivity=false` や min/max aspect ratio による保護が効かない。
- camera preview の aspect ratio、button position、touch target、state restoration が崩れる。

推奨対応:
- WindowMetrics / adaptive layout へ移行する。
- preview surface と操作 UI を分け、window bounds に応じて配置する。
- temporary opt-out は Android 16 の一時対応として限定する。

## テスト観点

- Android 16 / targetSdkVersion 35 / large screen。
- Android 16 / targetSdkVersion 36 / `sw >= 600dp`。
- tablet / foldable / split screen / desktop windowing。
- portrait-only live view。
- `resizeableActivity=false` / minAspectRatio / maxAspectRatio。

## Human Decision

- Final priority: TBD by human
- Release readiness impact: TBD by human
