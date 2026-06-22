# 複雑な IME 物理キーボード入力のアクセシビリティ対応 - 1ページ要約

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

- 主分類（Primary classification）: UNKNOWN_NEEDS_MORE_EVIDENCE
- OS アップデート / 全アプリ: 未確定。AOSP の該当 `TextView` path は feature flag 条件で、targetSdk gate は未検出。
- targetSdkVersion 37 以上: 公式文書上は対象。ただし AOSP gate は未確認。
- その他の必須条件: CJKV IME composition、candidate selection、commit、標準 `TextView` / custom `InputConnection`、`TYPE_VIEW_TEXT_CHANGED`、AccessibilityService。
- Compat Change ID: 確認できず
- Compat default state: `android.view.accessibility.a11y_text_change_types_api` flag に依存
- 信頼度: Medium

## 早見マトリクス

| シナリオ | 影響 |
| --- | --- |
| Android 16 / targetSdkVersion 36 | 新しい text change type API / TextView default handling は存在しない。 |
| Android 17 / targetSdkVersion 36 | AOSP 実装上は flag enabled 時に TextView が text change type を設定する可能性。target gate は未確認。 |
| Android 17 / targetSdkVersion 37 | 公式文書上の対象。標準 `TextView` が IME data retrieval と text change type 設定を処理する。 |

## 要約

Android 17 では、CJKV IME の物理キーボード入力中に、候補選択や composition / commit の違いを AccessibilityService へ伝える API と `TextView` 処理が追加される。AOSP 根拠 は確認できたが、targetSdkVersion 37 gate は未検出のため分類は保留する。

## 顧客影響

- CJKV 入力中のスクリーンリーダー読み上げがより正確になる可能性がある。
- 独自 `InputConnection` や独自 `TYPE_VIEW_TEXT_CHANGED` dispatch を持つアプリは、新 API と整合しない可能性がある。
- AccessibilityService は `AccessibilityEvent.getTextChangeTypes()` を読むことで入力状態に応じたフィードバックを実装できる。

## 影響対象

- 対象アプリ: IME アプリ、custom edit field を持つアプリ、AccessibilityService、標準 `TextView` を使うアプリ。
- 対象機能: CJKV 入力、text composition、conversion candidate selection、commit、`TYPE_VIEW_TEXT_CHANGED`。
- 対象条件: `a11y_text_change_types_api` flag enabled、または新 API を明示的に送受信する場合。

## 対応要否

- 必須対応: custom `InputConnection` と独自 `TYPE_VIEW_TEXT_CHANGED` dispatch の有無を棚卸しする。
- 推奨対応: IME、custom edit field、AccessibilityService は新 API の採用と Android 17 読み上げテストを検討する。
- 保留事項: frameworks-base 内の該当 Java path では targetSdkVersion 37 gate が確認できない。残件は未取得 checkout ではなく、公式 target 37 記述と AOSP feature flag gate の対応確認。

## テストマトリクス

| 端末 OS | targetSdkVersion | 期待挙動 |
| --- | --- | --- |
| Android 16 | 36 | baseline。text change type API はない。 |
| Android 17 | 36 | flag enabled 時に TextView event が変わるか確認。 |
| Android 17 | 37 | 公式文書上の期待どおり text change type が設定されるか確認。 |

## 顧客向け説明

Android 17 では、CJKV 入力中のスクリーンリーダー読み上げを改善するため、IME、edit field、AccessibilityService の間で text composition、commit、候補選択の意味を伝える仕組みが追加されます。標準 `TextView` では framework 側の処理が追加されていますが、独自 editor や AccessibilityService は新 API への対応を確認してください。

## 根拠

- 公式ドキュメント: https://developer.android.com/about/versions/17/behavior-changes-17
- AOSP ファイル:
  - `core/java/android/view/accessibility/AccessibilityEvent.java`
  - `core/java/android/view/inputmethod/TextAttribute.java`
  - `core/java/android/view/inputmethod/EditorInfo.java`
  - `core/java/android/widget/TextView.java`
  - `core/java/com/android/internal/inputmethod/EditableInputConnection.java`
  - `core/java/android/view/accessibility/flags/accessibility_flags.aconfig`
- 差分解釈: API 追加と `TextView` の event 設定処理追加は確認。targetSdkVersion 37 gate は未検出。
- 適用ゲートの結論: `a11y_text_change_types_api` feature flag は確認。`TextView` / `TextAttribute` / `AccessibilityEvent` / `EditableInputConnection` では targetSdkVersion 37 gate は未検出。

## 人間の判断欄

最終優先度（Final Priority）:
- 人間による判断が必要

判断（Decision）:
- 未判断
