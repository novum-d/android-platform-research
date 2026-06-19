# Implicit URI grants の制限 - 1ページ要約

## 対象（Target）

Android 17 Behavior Change

比較元:
- android-16.0.0_r4

比較先:
- android-17.0.0_r1

以前の targetSdkVersion:
- 36

対象 targetSdkVersion:
- 37

## 適用条件（Applicability）

- 主分類（Primary classification）: TARGET_SDK_37_CONDITIONAL
- OS アップデート / 全アプリ（OS update / all apps）: Android 17 では自動 grant 停止ではなく、StrictMode / logcat による検出と移行支援が中心。
- targetSdkVersion 37 以上: StrictMode `detectAll()` による自動検出は `@EnabledAfter(targetSdkVersion = BAKLAVA)` の compat change に依存する。
- その他の必須条件（Other required conditions）: URI を含む `ACTION_SEND`、`ACTION_SEND_MULTIPLE`、`ACTION_IMAGE_CAPTURE` intent を使い、明示 grant flags が欠けていること。
- Compat Change ID: `DETECT_IMPLICIT_URI_PERMISSION_GRANT`
- Compat default state: `@EnabledAfter(targetSdkVersion = Build.VERSION_CODES.BAKLAVA)`
- Confidence: Medium

## 早見マトリクス（At-a-Glance Matrix）

| シナリオ（Scenario） | 影響（Impact） |
| --- | --- |
| Android 17 / targetSdkVersion 36 | 自動 grant 停止は未適用。StrictMode を明示しない限り検出は限定的。 |
| Android 17 / targetSdkVersion 37 | StrictMode `detectAll()` で implicit URI grant を VM violation として検出する想定。 |
| Android 18 以降 | 公式文書上、system の implicit URI grant 自動付与が停止予定。 |

## 要約（Summary）

Android 17 の all apps ページは、URI 付き `ACTION_SEND`、`ACTION_SEND_MULTIPLE`、`ACTION_IMAGE_CAPTURE` に対する implicit URI permission grants の将来制限を案内している。自動 grant 停止は Android 18 starting と説明されており、Android 17 では StrictMode / logcat で検出し、explicit grant flag へ移行する準備項目として扱う。

AOSP では `StrictMode.VmPolicy.Builder.detectImplicitUriPermissionGrant()` が追加され、`Intent` の対象 action path が missing grant flag を検出して warning / StrictMode violation / stats を出す。

## 顧客影響（Customer Impact）

- Android 17 では主にテスト時の StrictMode violation や logcat warning として見える。
- Android 18 以降では、明示 grant がない share / capture flow で target app が URI を読めない、または書き込めない可能性がある。

## 影響対象（Who Is Affected）

- 対象アプリ: content URI を他アプリへ共有するアプリ、camera app に output URI を渡すアプリ。
- 対象機能: share sheet、画像 / document 共有、camera capture、添付ファイル送信。
- 対象条件: URI 付き intent に `FLAG_GRANT_READ_URI_PERMISSION` / `FLAG_GRANT_WRITE_URI_PERMISSION` を明示していない場合。

## 対応要否（Required Action）

- 必須対応: URI 付き `ACTION_SEND`、`ACTION_SEND_MULTIPLE`、`ACTION_IMAGE_CAPTURE` の call site を棚卸しする。
- 推奨対応: `ACTION_SEND` / `ACTION_SEND_MULTIPLE` には read grant、`ACTION_IMAGE_CAPTURE` には read / write grant を明示する。
- 不要: URI を他アプリへ渡さないアプリ、または grant flags をすでに明示している flow では直接影響は限定的。

## テストマトリクス（Test Matrix）

| 端末 OS（Device OS） | targetSdkVersion | 期待挙動（Expected behavior） |
| --- | --- | --- |
| Android 16 | 36 | baseline。implicit grant により target app が URI を読めるか確認。 |
| Android 17 | 36 | 自動 grant 停止は未適用。logcat warning が出る可能性。 |
| Android 17 | 37 | StrictMode `detectAll()` で violation を検出する想定。 |

## 顧客向け説明（Explanation for Customers）

Android 17 の文書では、URI を含む `ACTION_SEND`、`ACTION_SEND_MULTIPLE`、`ACTION_IMAGE_CAPTURE` intent に対して system が暗黙に read / write URI permissions を付与する挙動が、Android 18 から廃止される予定だと説明されています。Android 17 のうちに StrictMode や logcat で依存箇所を検出し、明示的な grant flag を追加することが推奨されます。

`ACTION_SEND` と `ACTION_SEND_MULTIPLE` では `FLAG_GRANT_READ_URI_PERMISSION` を付けます。`ACTION_IMAGE_CAPTURE` では `FLAG_GRANT_READ_URI_PERMISSION` と `FLAG_GRANT_WRITE_URI_PERMISSION` の両方を付けます。

## 根拠（Evidence）

- 公式ドキュメント: https://developer.android.com/about/versions/17/behavior-changes-all
- 検証対象の原文: Android 18 starting で system は URI 付き `ACTION_SEND` / `ACTION_SEND_MULTIPLE` / `ACTION_IMAGE_CAPTURE` に対する read / write URI permissions を自動 grant しなくなる。
- AOSP ファイル: `core/java/android/os/StrictMode.java`, `core/java/android/os/strictmode/ImplicitUriPermissionGrantViolation.java`, `core/java/android/content/Intent.java`, `core/java/android/security/responsible_apis_flags.aconfig`, `core/api/current.txt`
- AOSP ソース文脈: StrictMode detection API、targetSdk gate、Intent 側 missing grant flag warning / violation / guarded restriction path。
- 差分解釈: added detection behavior / added API surface / guarded future restriction path。
- Gate conclusion: Android 17 の検出は feature flag + compat change + StrictMode VM policy 条件。自動 grant 停止の release default は Android 18 側で追加確認が必要。

## 人間の判断欄

最終優先度（Final Priority）:
- 人間による判断が必要

判断（Decision）:
- 未判断
