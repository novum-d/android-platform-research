# Android 17 Behavior Changes 調査一覧

Behavior Changes の各セクションごとに、顧客説明向け調査レポートを作成する。

## 現在の状態（Current Status）

Android 17 official Behavior Change documentation is available.

Local AOSP status:
- `frameworks-base` currently has no `android-17*` tag.
- AOSP-backed High confidence conclusions must wait until the target Android 17 AOSP tag is available.

## 早見表（Quick View）

最初にここを見る。各 Behavior Change は必ず 1 つの primary classification に入れる。

| 分類（Classification） | 適用条件（When it applies） | 顧客向けの意味 | 一覧 |
| --- | --- | --- | --- |
| [`OS_UPDATE_ALL_APPS`](APPLICABILITY_CLASSIFICATION.md#os_update_all_apps) | Android 17 上の全アプリ。targetSdkVersion に依存しない | OS アップデートだけで影響する可能性がある | [All apps](#all-apps) |
| [`TARGET_SDK_37`](APPLICABILITY_CLASSIFICATION.md#target_sdk_37) | Android 17+ で targetSdkVersion >= 37 | targetSdkVersion 37 化で有効になる | [Apps targeting Android 17](#target-apps) |
| [`TARGET_SDK_37_CONDITIONAL`](APPLICABILITY_CLASSIFICATION.md#target_sdk_37_conditional) | targetSdkVersion >= 37 に加えて追加条件あり | targetSdkVersion 37 化だけでは不十分。端末条件、API 利用、権限なども必要 | [Apps targeting Android 17](#target-apps) |
| [`MAINLINE_OR_PLAY_SYSTEM_UPDATE`](APPLICABILITY_CLASSIFICATION.md#mainline_or_play_system_update) | Mainline / Google Play system update に依存 | Android 17 platform image だけで決まらない | [公式カテゴリ別索引](#official-category-index) |
| [`API_ADDITION_ONLY`](APPLICABILITY_CLASSIFICATION.md#api_addition_only) | 既存挙動変更ではなく API 追加 | 互換性リスクではなく採用機会 | [公式カテゴリ別索引](#official-category-index) |
| [`UNKNOWN_NEEDS_MORE_EVIDENCE`](APPLICABILITY_CLASSIFICATION.md#unknown_needs_more_evidence) | 根拠不足 | 顧客向け結論に使わない | [公式カテゴリ別索引](#official-category-index) |

使い方:
- レポート作成時は、最初に公式文書のページ種別と原文から仮分類を置く。
- AOSP gate / compat framework / targetSdkVersion 別の期待挙動を確認できるまで、High confidence にしない。
- 分類に迷う場合は `UNKNOWN_NEEDS_MORE_EVIDENCE` に入れ、不足根拠を明記する。

## 公式ドキュメント（Official Documentation）

Use:

```text
https://developer.android.com/about/versions/17/behavior-changes-all
https://developer.android.com/about/versions/17/behavior-changes-17
```

## テンプレート（Template）

Use:

```text
android17/templates/customer-report-template.md
```

<a id="official-category-index"></a>

## 公式カテゴリ別索引（Official Category Index）

公式 Behavior Change 文書のページ種別（All apps / Apps targeting Android 17）とカテゴリに合わせて配置する。

```text
behavior-changes/
  all/<official-category>/
  target/<official-category>/
```

<a id="all-apps"></a>

## All apps

Android 17 上で実行される全アプリに関係する可能性がある項目。

### Core functionality

| レポート（Report） | 要約（Summary） | 1ページ要約 | 状態（Status） |
| --- | --- | --- | --- |
| [App memory limits](all/core-functionality/app-memory-limits.md) | Android 17 で device total RAM に基づく app memory limits が導入される。 | [summary](../summaries/all/core-functionality/app-memory-limits-summary.md) | AOSP tag 待ち / Low confidence |

### Privacy

| レポート（Report） | 要約（Summary） | 1ページ要約 | 状態（Status） |
| --- | --- | --- | --- |
| [SMS OTP protection](all/privacy/sms-otp-protection.md) | Android 17 で WebOTP format messages にも SMS OTP protection が適用される。 | [summary](../summaries/all/privacy/sms-otp-protection-summary.md) | AOSP tag 待ち / Low confidence |

### Security

| レポート（Report） | 要約（Summary） | 1ページ要約 | 状態（Status） |
| --- | --- | --- | --- |
| [usesClearTraffic deprecation plan](all/security/usescleartexttraffic-deprecation-plan.md) | 将来の `usesCleartextTraffic` deprecation plan と Network Security Configuration への移行 guidance。 | [summary](../summaries/all/security/usescleartexttraffic-deprecation-plan-summary.md) | AOSP tag 待ち / Low confidence |
| [Restrict implicit URI grants](all/security/restrict-implicit-uri-grants.md) | Android 18 に向けて implicit URI permission grant 依存を明示 grant へ移行する guidance。 | [summary](../summaries/all/security/restrict-implicit-uri-grants-summary.md) | AOSP tag 待ち / Low confidence |
| [Per-app keystore limits](all/security/per-app-keystore-limits.md) | Android 17 で Android Keystore の per-app key ownership limit が導入される。 | [summary](../summaries/all/security/per-app-keystore-limits-summary.md) | AOSP tag 待ち / Low confidence |
| [Block cross profile loopback traffic](all/security/block-cross-profile-loopback-traffic.md) | Android 17 で cross-profile loopback traffic が default block される。 | [summary](../summaries/all/security/block-cross-profile-loopback-traffic-summary.md) | AOSP tag 待ち / Low confidence |

### User experience and system UI

| レポート（Report） | 要約（Summary） | 1ページ要約 | 状態（Status） |
| --- | --- | --- | --- |
| [Restoring default IME visibility after rotation](all/user-experience-and-system-ui/restoring-default-ime-visibility-after-rotation.md) | Android 17 で unhandled configuration change 後に previous IME visibility が自動復元されない。 | [summary](../summaries/all/user-experience-and-system-ui/restoring-default-ime-visibility-after-rotation-summary.md) | AOSP tag 待ち / Low confidence |

### Human input

| レポート（Report） | 要約（Summary） | 1ページ要約 | 状態（Status） |
| --- | --- | --- | --- |
| [Touchpads deliver relative events by default during pointer capture](all/human-input/touchpads-relative-events-pointer-capture.md) | Android 17 で touchpad は pointer capture 中に default で relative motion events を deliver する。 | [summary](../summaries/all/human-input/touchpads-relative-events-pointer-capture-summary.md) | AOSP tag 待ち / Low confidence |

### Media

| レポート（Report） | 要約（Summary） | 1ページ要約 | 状態（Status） |
| --- | --- | --- | --- |
| [Background audio hardening](all/media/background-audio-hardening.md) | Android 17 で background audio interaction に共通制限が導入され、targetSdkVersion 37 以上では WIU 条件が追加される。 | [summary](../summaries/all/media/background-audio-hardening-summary.md) | AOSP tag 待ち / Low confidence |

### Connectivity

| レポート（Report） | 要約（Summary） | 1ページ要約 | 状態（Status） |
| --- | --- | --- | --- |
| [Autonomous re-pairing for Bluetooth bond losses](all/connectivity/autonomous-repairing-bluetooth-bond-losses.md) | Android 17 で Bluetooth bond loss 後に system が autonomous re-pairing を試行できる。 | [summary](../summaries/all/connectivity/autonomous-repairing-bluetooth-bond-losses-summary.md) | AOSP tag 待ち / Low confidence |

<a id="target-apps"></a>

## Apps targeting Android 17

Android 17 以上を targetSdkVersion にしたアプリに関係する項目。

### Core functionality

| レポート（Report） | 要約（Summary） | 1ページ要約 | 状態（Status） |
| --- | --- | --- | --- |
| [New lock-free implementation of MessageQueue](target/core-functionality/messagequeue-lock-free.md) | targetSdkVersion 37 以上で `MessageQueue` が lock-free implementation になる。 | [summary](../summaries/target/core-functionality/messagequeue-lock-free-summary.md) | AOSP tag 待ち / Low confidence |
| [Static final fields are now unmodifiable](target/core-functionality/static-final-fields.md) | targetSdkVersion 37 以上では reflection / JNI による `static final` field 変更が制限される。 | [summary](../summaries/target/core-functionality/static-final-fields-summary.md) | AOSP tag 待ち / Low confidence |

### Accessibility

| レポート（Report） | 要約（Summary） | 1ページ要約 | 状態（Status） |
| --- | --- | --- | --- |
| [Accessibility support of complex IME physical keyboard typing](target/accessibility/accessibility-ime-physical-keyboard.md) | CJKV IME composition に関する accessibility feedback が改善される。 | [summary](../summaries/target/accessibility/accessibility-ime-physical-keyboard-summary.md) | AOSP tag 待ち / Low confidence |

### Privacy

| レポート（Report） | 要約（Summary） | 1ページ要約 | 状態（Status） |
| --- | --- | --- | --- |
| [ECH enabled](target/privacy/ech-encrypted-client-hello.md) | targetSdkVersion 37 以上で ECH が TLS connection に使われる。 | [summary](../summaries/target/privacy/ech-encrypted-client-hello-summary.md) | AOSP tag 待ち / Low confidence |
| [Local network permission required for apps targeting Android 17](target/privacy/local-network-permission.md) | targetSdkVersion 37 以上で local network access に `ACCESS_LOCAL_NETWORK` runtime permission が必要になる。 | [summary](../summaries/target/privacy/local-network-permission-summary.md) | AOSP tag 待ち / Low confidence |
| [Hiding passwords from physical devices](target/privacy/hiding-passwords-physical-devices.md) | targetSdkVersion 37 以上で physical input device 利用時の password 表示設定が変わる。 | [summary](../summaries/target/privacy/hiding-passwords-physical-devices-summary.md) | AOSP tag 待ち / Low confidence |
| [OTP protection for standard SMS messages](target/privacy/otp-protection-standard-sms.md) | targetSdkVersion 37 以上で standard SMS OTP messages にも 3 時間 delay が適用される。 | [summary](../summaries/target/privacy/otp-protection-standard-sms-summary.md) | AOSP tag 待ち / Low confidence |

### Security

| レポート（Report） | 要約（Summary） | 1ページ要約 | 状態（Status） |
| --- | --- | --- | --- |
| [Activity Security](target/security/activity-security.md) | Background Activity Launch hardening など secure-by-default 移行に関する変更。 | [summary](../summaries/target/security/activity-security-summary.md) | AOSP tag 待ち / Low confidence |
| [Enable CT by default](target/security/enable-ct-by-default.md) | targetSdkVersion 37 以上で certificate transparency が default enabled になる。 | [summary](../summaries/target/security/enable-ct-by-default-summary.md) | AOSP tag 待ち / Low confidence |
| [Safer Native DCL-C](target/security/safer-native-dcl-c.md) | targetSdkVersion 37 以上で native dynamic code loading の read-only requirement が適用される。 | [summary](../summaries/target/security/safer-native-dcl-c-summary.md) | AOSP tag 待ち / Low confidence |
| [Restrict PII fields in CP2 data view](target/security/restrict-pii-fields-cp2-data-view.md) | Contacts Provider 2 の data view から一部 PII columns が除外される。 | [summary](../summaries/target/security/restrict-pii-fields-cp2-data-view-summary.md) | AOSP tag 待ち / Low confidence |
| [Enforce strict SQL checks in CP2](target/security/enforce-strict-sql-checks-cp2.md) | `READ_CONTACTS` なしで CP2 data table を query する場合に strict SQL validation が適用される。 | [summary](../summaries/target/security/enforce-strict-sql-checks-cp2-summary.md) | AOSP tag 待ち / Low confidence |

### Media

| レポート（Report） | 要約（Summary） | 1ページ要約 | 状態（Status） |
| --- | --- | --- | --- |
| [Background audio hardening - targetSdkVersion 37 additional restrictions](target/media/background-audio-hardening.md) | targetSdkVersion 37 以上で foreground service の WIU capability / exact alarm + `USAGE_ALARM` 条件が追加される。 | [summary](../summaries/target/media/background-audio-hardening-summary.md) | AOSP tag 待ち / Low confidence |

### Device form factors

| レポート（Report） | 要約（Summary） | 1ページ要約 | 状態（Status） |
| --- | --- | --- | --- |
| [Platform API changes to ignore orientation, resizability and aspect ratio constraints on large screens](target/device-form-factors/large-screen-orientation-resizability-aspect-ratio.md) | targetSdkVersion 37 以上では large screen 上で orientation / resizability / aspect ratio restrictions が ignored になる。 | [summary](../summaries/target/device-form-factors/large-screen-orientation-resizability-aspect-ratio-summary.md) | AOSP tag 待ち / Low confidence |

### Connectivity

| レポート（Report） | 要約（Summary） | 1ページ要約 | 状態（Status） |
| --- | --- | --- | --- |
| [Consistent BluetoothSocket read() behavior for RFCOMM](target/connectivity/consistent-bluetoothsocket-read-rfcomm.md) | targetSdkVersion 37 で RFCOMM `BluetoothSocket` の `read()` が close / disconnect 時に `-1` を返す。 | [summary](../summaries/target/connectivity/consistent-bluetoothsocket-read-rfcomm-summary.md) | AOSP tag 待ち / Low confidence |
