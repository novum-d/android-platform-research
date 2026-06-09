# Accessibility support of complex IME physical keyboard typing - One Page Summary

## Target

Android 17 Behavior Change

From:
- android-16.0.0_r4

To:
- TBD: Android 17 AOSP tag

Previous targetSdkVersion:
- 36

Target targetSdkVersion:
- 37

## Applicability

- Primary classification: UNKNOWN_NEEDS_MORE_EVIDENCE
- OS update / all apps: Unknown。公式ページは targetSdkVersion 37+ 向けだが、API adoption 条件も含む。
- targetSdkVersion 37+: standard `TextView` の既定有効化は公式文書上 targetSdkVersion 37+。AOSP gate 未確認。
- Other required conditions: CJKV IME composition、physical keyboard typing、custom `InputConnection`、`TYPE_VIEW_TEXT_CHANGED`、AccessibilityService の処理。
- Compat Change ID: Unknown
- Compat default state: Unknown

## At-a-Glance Matrix

| Scenario | Impact |
| --- | --- |
| Android 17 / targetSdkVersion 36 | Unknown。standard `TextView` の既定有効化は targetSdkVersion 37+ と読めるが、AOSP gate 未確認。 |
| Android 17 / targetSdkVersion 37 | standard `TextView` が IME data retrieval と text change type 設定を既定で処理すると公式文書は説明。 |
| Android 17 / targetSdkVersion 37 + required conditions | CJKV IME composition / candidate selection / commit に対するスクリーンリーダー feedback がより正確になる可能性がある。 |

## Summary

Android 17 では、CJKV IME の物理キーボード入力中に、候補選択や composition / commit の違いをアクセシビリティサービスへ伝える API と `TextView` 既定処理が追加される、と公式文書は説明している。

## Customer Impact

- 要確認

## Who Is Affected

- 対象アプリ: IME アプリ、custom edit field を持つアプリ、AccessibilityService、targetSdkVersion 37 以上で standard `TextView` を使うアプリ。
- 対象機能: CJKV 入力、text composition、conversion candidate selection、`TYPE_VIEW_TEXT_CHANGED`、スクリーンリーダー読み上げ。
- 対象条件: 新 `TextAttribute` / `AccessibilityEvent` API を送受信する、または `TextView` の既定イベント送信に依存する場合。

## Required Action

- 必須対応: custom `InputConnection` と独自 `TYPE_VIEW_TEXT_CHANGED` dispatch の有無を棚卸しする。
- 推奨対応: IME、custom edit field、AccessibilityService は新 API の採用と Android 17 読み上げテストを検討する。
- 不要: CJKV IME composition、custom text editor、AccessibilityService と関係しないアプリでは互換性対応は限定的。

## Test Matrix

| Device OS | targetSdkVersion | Expected behavior |
| --- | --- | --- |
| Android 16 | 36 | Android 16 baseline。新 API / TextView default handling は Android 17 tag 比較待ち。 |
| Android 17 | 36 | Unknown。公式文書上は targetSdkVersion 37+ の TextView 既定有効化が中心だが、AOSP gate 未確認。 |
| Android 17 | 37 | standard `TextView` では text change type 設定が既定で処理されると公式文書は説明。 |

## Explanation for Customers

Android 17 では、CJKV 入力中のスクリーンリーダー読み上げを改善するため、IME、edit field、AccessibilityService の間で text composition や commit の意味を伝える仕組みが追加されます。standard `TextView` を使う targetSdkVersion 37 以上のアプリでは既定で処理されると説明されていますが、custom `InputConnection` や独自アクセシビリティイベント送信を持つアプリは新 API への対応を検討する必要があります。

現時点では local AOSP checkout に Android 17 tag がないため、targetSdkVersion gate、API surface diff、compat flag の有無は未確認です。最終的な適用分類は Android 17 AOSP tag 公開後に再確認が必要です。

## Evidence

- Official documentation: https://developer.android.com/about/versions/17/behavior-changes-17
- API reference: https://developer.android.com/reference/android/view/accessibility/AccessibilityEvent
- API reference: https://developer.android.com/reference/android/view/inputmethod/TextAttribute
- Original statement: CJKV language input の screen reader feedback を改善するため、`AccessibilityEvent` と `TextAttribute` API が導入され、targetSdkVersion 37+ の standard `TextView` では既定で有効になる。
- AOSP files: 未確認。local `frameworks-base` に `android-17*` tag がない。
- AOSP source context: 未確認。tag 間 diff が実行できない。
- Diff interpretation: 未分類。added behavior / changed condition / changed default の判定は Android 17 tag 待ち。
- Gate conclusion: Unknown。公式文書は targetSdkVersion 37+ と API usage 条件を示すが、AOSP gate evidence は未取得。

## Human Decision

Final Priority:
- Human decision required

Decision:
- Further investigation required
