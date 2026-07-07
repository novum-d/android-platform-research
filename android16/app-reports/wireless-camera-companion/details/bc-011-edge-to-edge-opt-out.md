# BC-011: Edge-to-edge opt-out going away

## 基本情報

Behavior Change 文書:
- URL: https://developer.android.com/about/versions/16/behavior-changes-16#edge-to-edge
- Section: Edge-to-edge opt-out going away

既存調査:
- [android16/behavior-changes/target/user-experience-and-system-ui/edge-to-edge-opt-out-going-away.md](../../../behavior-changes/target/user-experience-and-system-ui/edge-to-edge-opt-out-going-away.md)
- [android16/summaries/target/user-experience-and-system-ui/edge-to-edge-opt-out-going-away-summary.md](../../../summaries/target/user-experience-and-system-ui/edge-to-edge-opt-out-going-away-summary.md)

## 対象アプリとの関係

関連するアプリ機能:
- live view / full-screen preview。
- image viewer。
- setup / pairing flow。
- transfer progress。
- IME を使う Wi-Fi password / camera setup form。

アプリが該当する可能性:
- Conditional。`windowOptOutEdgeToEdgeEnforcement=true` に依存する場合に該当。

## 適用条件分類

主分類:
- `TARGET_SDK_36_CONDITIONAL`

必要条件:
- Android 16。
- targetSdkVersion 36 以上。
- opt-out 属性に依存している Activity / Window。

Confidence:
- High。

## AOSP / 公式根拠

既存 Android16 調査で確認済み:
- `DISABLE_OPT_OUT_EDGE_TO_EDGE` / 377864165。
- `@EnabledSince(targetSdkVersion = BAKLAVA)`。
- `PhoneWindow.isEdgeToEdgeEnforced()` が opt-out 可否を compat change で判定。

## アプリ影響

想定される影響:
- status bar / navigation bar / cutout / IME と UI が重なる。
- full-screen camera preview の control overlay が system bars と重なる。
- Android 15 で opt-out していた画面が Android 16 / targetSdkVersion 36 で崩れる。

推奨対応:
- opt-out 属性を棚卸しする。
- Compose / Views の insets 対応を実装する。
- live view、image viewer、setup form、transfer progress を縦横で確認する。

## テスト観点

- Android 15 / targetSdkVersion 35 / 36。
- Android 16 / targetSdkVersion 35 / 36。
- gesture navigation / 3-button navigation。
- IME open / close。
- landscape live view。

## Human Decision

- Final priority: TBD by human
- Release readiness impact: TBD by human
