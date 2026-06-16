# Android 17 1ページ要約（One Page Summaries）

顧客説明・社内共有に使える1ページ要約を配置する。

## 公式カテゴリ別索引（Official Category Index）

1ページ要約は、公式の挙動変更文書のページ種別（全アプリ / Android 17 を対象とするアプリ）とカテゴリに合わせて配置する。

### 全アプリ

| カテゴリ（Category） | 要約（Summaries） |
| --- | --- |
| コア機能 | [アプリのメモリ上限](all/core-functionality/app-memory-limits-summary.md) |
| プライバシー | [SMS OTP 保護](all/privacy/sms-otp-protection-summary.md) |
| セキュリティ | [usesCleartextTraffic 廃止計画](all/security/usescleartexttraffic-deprecation-plan-summary.md), [暗黙的な URI 権限付与の制限](all/security/restrict-implicit-uri-grants-summary.md), [アプリごとの Keystore 上限](all/security/per-app-keystore-limits-summary.md), [プロファイルをまたぐループバック通信のブロック](all/security/block-cross-profile-loopback-traffic-summary.md) |
| ユーザー体験とシステム UI | [回転後の既定 IME 表示復元](all/user-experience-and-system-ui/restoring-default-ime-visibility-after-rotation-summary.md) |
| 人間の入力 | [ポインターキャプチャ中のタッチパッド相対イベント既定化](all/human-input/touchpads-relative-events-pointer-capture-summary.md) |
| メディア | [バックグラウンド音声の制限強化](all/media/background-audio-hardening-summary.md) |
| 接続 | [Bluetooth ペアリング情報消失時の自律的な再ペアリング](all/connectivity/autonomous-repairing-bluetooth-bond-losses-summary.md) |

### Android 17 を対象とするアプリ

| カテゴリ（Category） | 要約（Summaries） |
| --- | --- |
| コア機能 | [MessageQueue の新しいロックフリー実装](target/core-functionality/messagequeue-lock-free-summary.md), [static final フィールドが変更不可に](target/core-functionality/static-final-fields-summary.md) |
| アクセシビリティ | [複雑な IME 物理キーボード入力のアクセシビリティ対応](target/accessibility/accessibility-ime-physical-keyboard-summary.md) |
| プライバシー | [ECH の有効化](target/privacy/ech-encrypted-client-hello-summary.md), [Android 17 を対象とするアプリに必要なローカルネットワーク権限](target/privacy/local-network-permission-summary.md), [物理入力デバイスでのパスワード非表示](target/privacy/hiding-passwords-physical-devices-summary.md), [標準 SMS メッセージの OTP 保護](target/privacy/otp-protection-standard-sms-summary.md) |
| セキュリティ | [Activity セキュリティ](target/security/activity-security-summary.md), [CT のデフォルト有効化](target/security/enable-ct-by-default-summary.md), [より安全なネイティブ DCL-C](target/security/safer-native-dcl-c-summary.md), [CP2 データビューの PII フィールド制限](target/security/restrict-pii-fields-cp2-data-view-summary.md), [CP2 の厳格な SQL 検証](target/security/enforce-strict-sql-checks-cp2-summary.md) |
| メディア | [バックグラウンド音声の制限強化 - targetSdkVersion 37 追加制限](target/media/background-audio-hardening-summary.md) |
| 端末フォームファクター | [大画面で画面向き・リサイズ可否・アスペクト比制約を無視するプラットフォーム API の変更](target/device-form-factors/large-screen-orientation-resizability-aspect-ratio-summary.md) |
| 接続 | [RFCOMM の BluetoothSocket read() 挙動の一貫化](target/connectivity/consistent-bluetoothsocket-read-rfcomm-summary.md) |

## 命名規則（Naming）

```text
target/core-functionality/messagequeue-lock-free-summary.md
all/core-functionality/app-memory-limits-summary.md
all/media/background-audio-hardening-summary.md
```

## テンプレート（Template）

使用テンプレート:

```text
android17/templates/one-page-summary-template.md
```
