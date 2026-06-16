# 複雑な IME 物理キーボード入力のアクセシビリティ対応 - 1ページ要約

## 対象（Target）

Android 17 挙動変更

From:
- android-16.0.0_r4

To:
- TBD: Android 17 AOSP タグ

Previous targetSdkVersion:
- 36

Target targetSdkVersion:
- 37

## 適用条件（Applicability）

- 主分類（Primary classification）: UNKNOWN_NEEDS_MORE_EVIDENCE
- OS アップデート / 全アプリ: 未確認。公式ページは targetSdkVersion 37+ 向けだが、API adoption 条件も含む。
- targetSdkVersion 37 以上: 標準 `TextView` の既定有効化は公式文書上 targetSdkVersion 37+。AOSP 適用ゲート未確認。
- その他の必須条件: CJKV IME 変換中テキスト、物理キーボード入力、カスタム `InputConnection`、`TYPE_VIEW_TEXT_CHANGED`、AccessibilityService の処理。
- Compat Change ID: 未確認
- Compat default state: 未確認

## 早見マトリクス

| シナリオ（Scenario） | 影響（Impact） |
| --- | --- |
| Android 17 / targetSdkVersion 36 | 未確認。標準 `TextView` の既定有効化は targetSdkVersion 37+ と読めるが、AOSP 適用ゲート未確認。 |
| Android 17 / targetSdkVersion 37 | 標準 `TextView` が IME データ取得とテキスト変更種別の設定を既定で処理すると公式文書は説明。 |
| Android 17 / targetSdkVersion 37 + 必須条件 | CJKV IME 変換中テキスト / 候補選択 / 確定に対するスクリーンリーダーフィードバックがより正確になる可能性がある。 |

## 要約

Android 17 では、CJKV IME の物理キーボード入力中に、候補選択や変換中テキスト / commit の違いをアクセシビリティサービスへ伝える API と `TextView` 既定処理が追加される、と公式文書は説明している。

## 顧客影響

- 要確認

## 影響対象

- 対象アプリ: IME アプリ、カスタム編集フィールドを持つアプリ、AccessibilityService、targetSdkVersion 37 以上で標準 `TextView` を使うアプリ。
- 対象機能: CJKV 入力、変換中テキスト、conversion candidate selection、`TYPE_VIEW_TEXT_CHANGED`、スクリーンリーダー読み上げ。
- 対象条件: 新 `TextAttribute` / `AccessibilityEvent` API を送受信する、または `TextView` の既定イベント送信に依存する場合。

## 対応要否

- 必須対応: カスタム `InputConnection` と独自 `TYPE_VIEW_TEXT_CHANGED` 送信の有無を棚卸しする。
- 推奨対応: IME、custom edit フィールド、AccessibilityService は新 API の採用と Android 17 読み上げテストを検討する。
- 不要: CJKV IME 変換中テキスト、custom text エディタ、AccessibilityService と関係しないアプリでは互換性対応は限定的。

## テストマトリクス

| 端末 OS | targetSdkVersion | 期待挙動 |
| --- | --- | --- |
| Android 16 | 36 | Android 16 基準挙動。新 API / TextView default handling は Android 17 タグ比較待ち。 |
| Android 17 | 36 | 未確認。公式文書上は targetSdkVersion 37+ の TextView 既定有効化が中心だが、AOSP 適用ゲートは未確認。 |
| Android 17 | 37 | standard `TextView` では text 変更 type 設定が既定で処理されると公式文書は説明。 |

## 顧客向け説明

Android 17 では、CJKV 入力中のスクリーンリーダー読み上げを改善するため、IME、edit フィールド、AccessibilityService の間で変換中テキストや commit の意味を伝える仕組みが追加されます。standard `TextView` を使う targetSdkVersion 37 以上のアプリでは既定で処理されると説明されていますが、custom `InputConnection` や独自アクセシビリティイベント送信を持つアプリは新 API への対応を検討する必要があります。

現時点ではローカル AOSP checkout に Android 17 タグがないため、targetSdkVersion 適用ゲート、API surface diff、compat flag の有無は未確認です。最終的な適用分類は Android 17 AOSP タグ公開後に再確認が必要です。

## 根拠

- Official documentation: https://developer.android.com/about/versions/17/behavior-changes-17
- API reference: https://developer.android.com/reference/android/view/accessibility/AccessibilityEvent
- API reference: https://developer.android.com/reference/android/view/inputmethod/TextAttribute
- 検証対象の原文: CJKV language input の screen reader feedback を改善するため、`AccessibilityEvent` と `TextAttribute` API が導入され、targetSdkVersion 37+ の standard `TextView` では既定で有効になる。
- AOSP ファイル: 未確認。ローカルの `frameworks-base` に `android-17*` タグがない。
- AOSP ソース文脈: 未確認。タグ間差分が実行できない。
- 差分解釈: 未分類。added behavior / changed condition / changed default の判定は Android 17 タグ待ち。
- 適用ゲートの結論: 未確認。公式文書は targetSdkVersion 37+ と API 使用条件を示すが、AOSP 適用ゲート根拠は未取得。

## 人間の判断欄

最終優先度（Final Priority）:
- Human decision required

判断（Decision）:
- 追加調査が必要
