# Android 17 Behavior Changes 調査一覧

Behavior Changes の各セクションごとに、顧客説明向け調査レポートを作成する。

## 現在の状態

Android 17 の公式 Behavior Change ドキュメントは公開済み。

AOSP scope:
- 2026-08-22 に公式 refs で確認した `android-16.0.0_r4` から `android-17.0.0_r1` を標準の比較 pair とする。
- 新規・更新調査では [`research-scope.json`](../research-scope.json) と公式 refs を再確認し、AOSP 根拠は明示的な tag 比較から取得する。

Android 16 と Android 17 の挙動差を項目別に確認する場合:

- [Android 16 → 17 挙動比較一覧](version-comparisons/README.md)

Android 17向けの実装・設定・テスト例を確認する場合:

- [Android 17対応例一覧](implementation-examples/README.md)

## 早見表

最初にここを見る。各 Behavior Change は必ず 1 つの主分類に入れる。

| 分類 | 適用条件 | 顧客向けの意味 | 一覧 |
| --- | --- | --- | --- |
| [`OS_UPDATE_ALL_APPS`](APPLICABILITY_CLASSIFICATION.md#os_update_all_apps) | Android 17 上の全アプリ。targetSdkVersion に依存しない | OS アップデートだけで影響する可能性がある | [全アプリ向け変更](#all-apps) |
| [`TARGET_SDK_37`](APPLICABILITY_CLASSIFICATION.md#target_sdk_37) | Android 17+ で targetSdkVersion >= 37 | targetSdkVersion 37 化で有効になる | [Android 17 を対象にするアプリ向け変更](#target-apps) |
| [`TARGET_SDK_37_CONDITIONAL`](APPLICABILITY_CLASSIFICATION.md#target_sdk_37_conditional) | targetSdkVersion >= 37 に加えて追加条件あり | targetSdkVersion 37 化だけでは不十分。端末条件、API 利用、権限なども必要 | [Android 17 を対象にするアプリ向け変更](#target-apps) |
| [`MAINLINE_OR_PLAY_SYSTEM_UPDATE`](APPLICABILITY_CLASSIFICATION.md#mainline_or_play_system_update) | Mainline / Google Play system update に依存 | Android 17 platform image だけで決まらない | [公式カテゴリ別索引](#official-category-index) |
| [`API_ADDITION_ONLY`](APPLICABILITY_CLASSIFICATION.md#api_addition_only) | 既存挙動変更ではなく API 追加 | 互換性リスクではなく採用機会 | [公式カテゴリ別索引](#official-category-index) |
| [`UNKNOWN_NEEDS_MORE_EVIDENCE`](APPLICABILITY_CLASSIFICATION.md#unknown_needs_more_evidence) | 根拠不足 | 顧客向け結論に使わない | [公式カテゴリ別索引](#official-category-index) |

使い方:
- レポート作成時は、最初に公式文書のページ種別と原文から仮分類を置く。
- AOSP の適用ゲート / compat framework / targetSdkVersion 別の期待挙動を確認できるまで、High confidence にしない。
- 分類に迷う場合は `UNKNOWN_NEEDS_MORE_EVIDENCE` に入れ、不足根拠を明記する。

## 公式ドキュメント

参照:

```text
https://developer.android.com/about/versions/17/behavior-changes-all
https://developer.android.com/about/versions/17/behavior-changes-17
```

## テンプレート

使用するテンプレート:

```text
android17/templates/customer-report-template.md
android17/templates/implementation-examples-template.md
docs/templates/android-os-version-behavior-comparison-template.md
```

<a id="official-category-index"></a>

## 公式カテゴリ別索引

公式 Behavior Change 文書のページ種別（全アプリ向け / Android 17 を対象にするアプリ向け）とカテゴリに合わせて配置する。

```text
behavior-changes/
  all/<official-category>/
  target/<official-category>/
```

<a id="all-apps"></a>

## 全アプリ向け変更

Android 17 上で実行される全アプリに関係する可能性がある項目。

### コア機能

| レポート | 要約 | 1ページ要約 | 状態 |
| --- | --- | --- | --- |
| [App memory limits](all/core-functionality/app-memory-limits.md) | Android 17 で端末の合計 RAM に基づくアプリごとのメモリ制限が導入される。 | [要約](../summaries/all/core-functionality/app-memory-limits-summary.md) | AOSP 根拠更新済み / High confidence |

### プライバシー

| レポート | 要約 | 1ページ要約 | 状態 |
| --- | --- | --- | --- |
| [SMS OTP protection](all/privacy/sms-otp-protection.md) | Android 17 で WebOTP 形式のメッセージにも SMS OTP protection が適用される。 | [要約](../summaries/all/privacy/sms-otp-protection-summary.md) | AOSP API 根拠更新済み。Telephony provider による適用は未確認 / Medium confidence |

### セキュリティ

| レポート | 要約 | 1ページ要約 | 状態 |
| --- | --- | --- | --- |
| [usesClearTraffic deprecation plan](all/security/usescleartexttraffic-deprecation-plan.md) | 将来の `usesCleartextTraffic` 廃止計画と Network Security Configuration への移行 guidance。 | [要約](../summaries/all/security/usescleartexttraffic-deprecation-plan-summary.md) | AOSP 根拠更新済み。compat default は未確認 / Medium confidence |
| [Restrict implicit URI grants](all/security/restrict-implicit-uri-grants.md) | Android 18 に向けて implicit URI permission grant 依存を明示 grant へ移行する guidance。 | [要約](../summaries/all/security/restrict-implicit-uri-grants-summary.md) | AOSP StrictMode 根拠更新済み。Android 18 での適用は未確認 / Medium confidence |
| [Per-app keystore limits](all/security/per-app-keystore-limits.md) | Android 17 で Android Keystore のアプリごとの key ownership limit が導入される。 | [要約](../summaries/all/security/per-app-keystore-limits-summary.md) | AOSP API 根拠更新済み。keystore2 による適用は未確認 / Medium confidence |
| [Block cross profile loopback traffic](all/security/block-cross-profile-loopback-traffic.md) | Android 17 で cross-profile loopback traffic がデフォルトでブロックされる。 | [要約](../summaries/all/security/block-cross-profile-loopback-traffic-summary.md) | AOSP permission 根拠更新済み。netd/BPF による適用は未確認 / Medium confidence |

### ユーザー エクスペリエンスとシステム UI

| レポート | 要約 | 1ページ要約 | 状態 |
| --- | --- | --- | --- |
| [Restoring default IME visibility after rotation](all/user-experience-and-system-ui/restoring-default-ime-visibility-after-rotation.md) | Android 17 で未処理の configuration change 後に以前の IME 表示状態が自動復元されない。 | [要約](../summaries/all/user-experience-and-system-ui/restoring-default-ime-visibility-after-rotation-summary.md) | AOSP 根拠更新済み。release flag/config 根拠は未確認 / Medium confidence |

### 入力

| レポート | 要約 | 1ページ要約 | 状態 |
| --- | --- | --- | --- |
| [Touchpads deliver relative events by default during pointer capture](all/human-input/touchpads-relative-events-pointer-capture.md) | Android 17 で touchpad は pointer capture 中にデフォルトで relative motion events を送出する。 | [要約](../summaries/all/human-input/touchpads-relative-events-pointer-capture-summary.md) | AOSP 根拠更新済み。flag/native default は未確認 / Medium confidence |

### メディア

| レポート | 要約 | 1ページ要約 | 状態 |
| --- | --- | --- | --- |
| [Background audio hardening](all/media/background-audio-hardening.md) | Android 17 でバックグラウンド音声操作に共通制限が導入され、targetSdkVersion 37 以上では WIU 条件が追加される。 | [要約](../summaries/all/media/background-audio-hardening-summary.md) | AOSP 根拠更新済み。native AudioPolicy details は未確認 / Medium confidence |

### 接続

| レポート | 要約 | 1ページ要約 | 状態 |
| --- | --- | --- | --- |
| [Autonomous re-pairing for Bluetooth bond losses](all/connectivity/autonomous-repairing-bluetooth-bond-losses.md) | Android 17 で Bluetooth bond loss 後に system が自律的な再ペアリングを試行できる。 | [要約](../summaries/all/connectivity/autonomous-repairing-bluetooth-bond-losses-summary.md) | Bluetooth module 根拠更新済み / High confidence |

<a id="target-apps"></a>

## Android 17 を対象にするアプリ向け変更

Android 17 以上を targetSdkVersion にしたアプリに関係する項目。

### コア機能

| レポート | 要約 | 1ページ要約 | 状態 |
| --- | --- | --- | --- |
| [New lock-free implementation of MessageQueue](target/core-functionality/messagequeue-lock-free.md) | targetSdkVersion 37 以上で `MessageQueue` が lock-free implementation になる。 | [要約](../summaries/target/core-functionality/messagequeue-lock-free-summary.md) | AOSP 根拠更新済み / High confidence |
| [Static final fields are now unmodifiable](target/core-functionality/static-final-fields.md) | targetSdkVersion 37 以上では reflection / JNI による `static final` field 変更が制限される。 | [要約](../summaries/target/core-functionality/static-final-fields-summary.md) | ART/libcore 根拠更新済み / High confidence |

### ユーザー補助

| レポート | 要約 | 1ページ要約 | 状態 |
| --- | --- | --- | --- |
| [Accessibility support of complex IME physical keyboard typing](target/accessibility/accessibility-ime-physical-keyboard.md) | CJKV IME composition に関するアクセシビリティ フィードバックが改善される。 | [要約](../summaries/target/accessibility/accessibility-ime-physical-keyboard-summary.md) | AOSP API/TextView 根拠更新済み。target gate は未解決 / Medium confidence |

### プライバシー

| レポート | 要約 | 1ページ要約 | 状態 |
| --- | --- | --- | --- |
| [ECH enabled](target/privacy/ech-encrypted-client-hello.md) | targetSdkVersion 37 以上で ECH が TLS 接続に使われる。 | [要約](../summaries/target/privacy/ech-encrypted-client-hello-summary.md) | AOSP 根拠更新済み / High confidence |
| [Local network permission required for apps targeting Android 17](target/privacy/local-network-permission.md) | targetSdkVersion 37 以上で local network access に `ACCESS_LOCAL_NETWORK` runtime permission が必要になる。 | [要約](../summaries/target/privacy/local-network-permission-summary.md) | AOSP permission/AppOps 根拠更新済み。Connectivity による適用は未確認 / Medium confidence |
| [Hiding passwords from physical devices](target/privacy/hiding-passwords-physical-devices.md) | targetSdkVersion 37 以上で物理入力デバイス利用時の password 表示設定が変わる。 | [要約](../summaries/target/privacy/hiding-passwords-physical-devices-summary.md) | AOSP 根拠更新済み / High confidence |
| [OTP protection for standard SMS messages](target/privacy/otp-protection-standard-sms.md) | targetSdkVersion 37 以上で standard SMS OTP messages にも 3 時間 delay が適用される。 | [要約](../summaries/target/privacy/otp-protection-standard-sms-summary.md) | AOSP 根拠更新済み / High confidence |

### セキュリティ

| レポート | 要約 | 1ページ要約 | 状態 |
| --- | --- | --- | --- |
| [Activity Security](target/security/activity-security.md) | Background Activity Launch hardening など secure-by-default 移行に関する変更。 | [要約](../summaries/target/security/activity-security-summary.md) | AOSP 根拠更新済み / High confidence |
| [Enable CT by default](target/security/enable-ct-by-default.md) | targetSdkVersion 37 以上で certificate transparency がデフォルト有効になる。 | [要約](../summaries/target/security/enable-ct-by-default-summary.md) | AOSP 根拠更新済み / High confidence |
| [Safer Native DCL-C](target/security/safer-native-dcl-c.md) | targetSdkVersion 37 以上で native dynamic code loading の read-only requirement が適用される。 | [要約](../summaries/target/security/safer-native-dcl-c-summary.md) | libcore/VMRuntime 根拠更新済み / High confidence |
| [Restrict PII fields in CP2 data view](target/security/restrict-pii-fields-cp2-data-view.md) | Contacts Provider 2 の data view から一部 PII columns が除外される。 | [要約](../summaries/target/security/restrict-pii-fields-cp2-data-view-summary.md) | ContactsProvider 根拠更新済み / High confidence |
| [Enforce strict SQL checks in CP2](target/security/enforce-strict-sql-checks-cp2.md) | `READ_CONTACTS` なしで CP2 data table を query する場合に strict SQL validation が適用される。 | [要約](../summaries/target/security/enforce-strict-sql-checks-cp2-summary.md) | ContactsProvider 根拠更新済み / High confidence |

### メディア

| レポート | 要約 | 1ページ要約 | 状態 |
| --- | --- | --- | --- |
| [Background audio hardening - targetSdkVersion 37 additional restrictions](target/media/background-audio-hardening.md) | targetSdkVersion 37 以上で foreground service の WIU capability / exact alarm + `USAGE_ALARM` 条件が追加される。 | [要約](../summaries/target/media/background-audio-hardening-summary.md) | AOSP target gate 根拠更新済み。native AudioPolicy details は未確認 / Medium confidence |

### デバイス フォーム ファクタ

| レポート | 要約 | 1ページ要約 | 状態 |
| --- | --- | --- | --- |
| [Platform API changes to ignore orientation, resizability and aspect ratio constraints on large screens](target/device-form-factors/large-screen-orientation-resizability-aspect-ratio.md) | targetSdkVersion 37 以上では large screen 上で orientation / resizability / aspect ratio restrictions が無視される。 | [要約](../summaries/target/device-form-factors/large-screen-orientation-resizability-aspect-ratio-summary.md) | AOSP 根拠更新済み / High confidence |

### 接続

| レポート | 要約 | 1ページ要約 | 状態 |
| --- | --- | --- | --- |
| [Consistent BluetoothSocket read() behavior for RFCOMM](target/connectivity/consistent-bluetoothsocket-read-rfcomm.md) | targetSdkVersion 37 で RFCOMM `BluetoothSocket` の `read()` が close / disconnect 時に `-1` を返す。 | [要約](../summaries/target/connectivity/consistent-bluetoothsocket-read-rfcomm-summary.md) | Bluetooth module 根拠更新済み / High confidence |
