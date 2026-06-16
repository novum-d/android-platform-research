# Android 17 1ページ要約（One Page Summaries）

顧客説明・社内共有に使える1ページ要約を配置する。

## 公式カテゴリ別索引（Official Category Index）

1ページ要約は、公式 Behavior Change 文書のページ種別（All apps / Apps targeting Android 17）とカテゴリに合わせて配置する。

### All apps

| カテゴリ（Category） | 要約（Summaries） |
| --- | --- |
| Core functionality | [App memory limits](all/core-functionality/app-memory-limits-summary.md) |
| Privacy | [SMS OTP protection](all/privacy/sms-otp-protection-summary.md) |
| Security | [usesClearTraffic deprecation plan](all/security/usescleartexttraffic-deprecation-plan-summary.md), [Restrict implicit URI grants](all/security/restrict-implicit-uri-grants-summary.md), [Per-app keystore limits](all/security/per-app-keystore-limits-summary.md), [Block cross profile loopback traffic](all/security/block-cross-profile-loopback-traffic-summary.md) |
| User experience and system UI | [Restoring default IME visibility after rotation](all/user-experience-and-system-ui/restoring-default-ime-visibility-after-rotation-summary.md) |
| Human input | [Touchpads deliver relative events by default during pointer capture](all/human-input/touchpads-relative-events-pointer-capture-summary.md) |
| Media | [Background audio hardening](all/media/background-audio-hardening-summary.md) |
| Connectivity | [Autonomous re-pairing for Bluetooth bond losses](all/connectivity/autonomous-repairing-bluetooth-bond-losses-summary.md) |

### Apps targeting Android 17

| カテゴリ（Category） | 要約（Summaries） |
| --- | --- |
| Core functionality | [New lock-free implementation of MessageQueue](target/core-functionality/messagequeue-lock-free-summary.md), [Static final fields are now unmodifiable](target/core-functionality/static-final-fields-summary.md) |
| Accessibility | [Accessibility support of complex IME physical keyboard typing](target/accessibility/accessibility-ime-physical-keyboard-summary.md) |
| Privacy | [ECH enabled](target/privacy/ech-encrypted-client-hello-summary.md), [Local network permission required for apps targeting Android 17](target/privacy/local-network-permission-summary.md), [Hiding passwords from physical devices](target/privacy/hiding-passwords-physical-devices-summary.md), [OTP protection for standard SMS messages](target/privacy/otp-protection-standard-sms-summary.md) |
| Security | [Activity Security](target/security/activity-security-summary.md), [Enable CT by default](target/security/enable-ct-by-default-summary.md), [Safer Native DCL-C](target/security/safer-native-dcl-c-summary.md), [Restrict PII fields in CP2 data view](target/security/restrict-pii-fields-cp2-data-view-summary.md), [Enforce strict SQL checks in CP2](target/security/enforce-strict-sql-checks-cp2-summary.md) |
| Media | [Background audio hardening - targetSdkVersion 37 additional restrictions](target/media/background-audio-hardening-summary.md) |
| Device form factors | [Platform API changes to ignore orientation, resizability and aspect ratio constraints on large screens](target/device-form-factors/large-screen-orientation-resizability-aspect-ratio-summary.md) |
| Connectivity | [Consistent BluetoothSocket read() behavior for RFCOMM](target/connectivity/consistent-bluetoothsocket-read-rfcomm-summary.md) |

## 命名規則（Naming）

```text
target/core-functionality/messagequeue-lock-free-summary.md
all/core-functionality/app-memory-limits-summary.md
all/media/background-audio-hardening-summary.md
```

## テンプレート（Template）

Use:

```text
android17/templates/one-page-summary-template.md
```
