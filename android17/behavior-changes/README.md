# Android 17 挙動変更調査一覧

挙動変更の各セクションごとに、顧客説明向け調査レポートを作成する。

## 現在の状態

Android 17 の公式挙動変更ドキュメントは利用可能。

ローカル AOSP 状態:
- `frameworks-base` には現在 `android-17*` タグがない。
- AOSP に基づく高信頼度の結論は、対象 Android 17 AOSP タグが利用可能になるまで保留する。

## 早見表（Quick View）

最初にここを見る。各挙動変更は必ず 1 つの主分類に入れる。

| 分類（Classification） | 適用条件（When it applies） | 顧客向けの意味 | 一覧 |
| --- | --- | --- | --- |
| [`OS_UPDATE_ALL_APPS`](APPLICABILITY_CLASSIFICATION.md#os_update_all_apps) | Android 17 上の全アプリ。targetSdkVersion に依存しない | OS アップデートだけで影響する可能性がある | [全アプリ](#all-apps) |
| [`TARGET_SDK_37`](APPLICABILITY_CLASSIFICATION.md#target_sdk_37) | Android 17+ で targetSdkVersion >= 37 | targetSdkVersion 37 化で有効になる | [Android 17 を対象とするアプリ](#target-apps) |
| [`TARGET_SDK_37_CONDITIONAL`](APPLICABILITY_CLASSIFICATION.md#target_sdk_37_conditional) | targetSdkVersion >= 37 に加えて追加条件あり | targetSdkVersion 37 化だけでは不十分。端末条件、API 利用、権限なども必要 | [Android 17 を対象とするアプリ](#target-apps) |
| [`MAINLINE_OR_PLAY_SYSTEM_UPDATE`](APPLICABILITY_CLASSIFICATION.md#mainline_or_play_system_update) | Mainline / Google Play システムアップデートに依存 | Android 17 プラットフォームイメージだけでは決まらない | [公式カテゴリ別索引](#official-category-index) |
| [`API_ADDITION_ONLY`](APPLICABILITY_CLASSIFICATION.md#api_addition_only) | 既存挙動変更ではなく API 追加 | 互換性リスクではなく採用機会 | [公式カテゴリ別索引](#official-category-index) |
| [`UNKNOWN_NEEDS_MORE_EVIDENCE`](APPLICABILITY_CLASSIFICATION.md#unknown_needs_more_evidence) | 根拠不足 | 顧客向け結論に使わない | [公式カテゴリ別索引](#official-category-index) |

使い方:
- レポート作成時は、最初に公式文書のページ種別と原文から仮分類を置く。
- AOSP 適用ゲート / Compat framework / targetSdkVersion 別の期待挙動を確認できるまで、高信頼度にしない。
- 分類に迷う場合は `UNKNOWN_NEEDS_MORE_EVIDENCE` に入れ、不足根拠を明記する。

## 公式ドキュメント（Official Documentation）

参照先:

```text
https://developer.android.com/about/versions/17/behavior-changes-all
https://developer.android.com/about/versions/17/behavior-changes-17
```

## テンプレート（Template）

使用テンプレート:

```text
android17/templates/customer-report-template.md
```

<a id="公式-category-index"></a>

## 公式カテゴリ別索引（Official Category Index）

公式の挙動変更文書のページ種別（全アプリ / Android 17 を対象とするアプリ）とカテゴリに合わせて配置する。

```text
behavior-changes/
  all/<official-category>/
  target/<official-category>/
```

<a id="all-apps"></a>

## 全アプリ

Android 17 上で実行される全アプリに関係する可能性がある項目。

### コア機能

| レポート | 要約 | 1ページ要約 | 状態 |
| --- | --- | --- | --- |
| [アプリのメモリ上限](all/core-functionality/app-memory-limits.md) | Android 17 で、端末の総 RAM 容量に基づくアプリのメモリ上限が導入される。 | [要約](../summaries/all/core-functionality/app-memory-limits-summary.md) | AOSP タグ待ち / 低信頼度 |

### プライバシー

| レポート | 要約 | 1ページ要約 | 状態 |
| --- | --- | --- | --- |
| [SMS OTP 保護](all/privacy/sms-otp-protection.md) | Android 17 で WebOTP 形式のメッセージにも SMS OTP 保護が適用される。 | [要約](../summaries/all/privacy/sms-otp-protection-summary.md) | AOSP タグ待ち / 低信頼度 |

### セキュリティ

| レポート | 要約 | 1ページ要約 | 状態 |
| --- | --- | --- | --- |
| [usesCleartextTraffic 廃止計画](all/security/usescleartexttraffic-deprecation-plan.md) | 将来の `usesCleartextTraffic` 廃止計画とネットワークセキュリティ設定への移行ガイダンス。 | [要約](../summaries/all/security/usescleartexttraffic-deprecation-plan-summary.md) | AOSP タグ待ち / 低信頼度 |
| [暗黙的な URI 権限付与の制限](all/security/restrict-implicit-uri-grants.md) | Android 18 に向けて、暗黙的な URI 権限付与への依存を明示的な権限付与へ移行するためのガイダンス。 | [要約](../summaries/all/security/restrict-implicit-uri-grants-summary.md) | AOSP タグ待ち / 低信頼度 |
| [アプリごとの Keystore 上限](all/security/per-app-keystore-limits.md) | Android 17 で、Android Keystore にアプリごとの鍵数上限が導入される。 | [要約](../summaries/all/security/per-app-keystore-limits-summary.md) | AOSP タグ待ち / 低信頼度 |
| [プロファイルをまたぐループバック通信のブロック](all/security/block-cross-profile-loopback-traffic.md) | Android 17 で、プロファイルをまたぐループバック通信がデフォルトでブロックされる。 | [要約](../summaries/all/security/block-cross-profile-loopback-traffic-summary.md) | AOSP タグ待ち / 低信頼度 |

### ユーザー体験とシステム UI

| レポート | 要約 | 1ページ要約 | 状態 |
| --- | --- | --- | --- |
| [回転後の既定 IME 表示復元](all/user-experience-and-system-ui/restoring-default-ime-visibility-after-rotation.md) | Android 17 では、アプリが処理しない構成変更の後に以前の IME 表示状態が自動復元されない。 | [要約](../summaries/all/user-experience-and-system-ui/restoring-default-ime-visibility-after-rotation-summary.md) | AOSP タグ待ち / 低信頼度 |

### 人間の入力

| レポート | 要約 | 1ページ要約 | 状態 |
| --- | --- | --- | --- |
| [ポインターキャプチャ中のタッチパッド相対イベント既定化](all/human-input/touchpads-relative-events-pointer-capture.md) | Android 17 で、タッチパッドはポインターキャプチャ中にデフォルトで相対移動イベントを送る。 | [要約](../summaries/all/human-input/touchpads-relative-events-pointer-capture-summary.md) | AOSP タグ待ち / 低信頼度 |

### メディア

| レポート | 要約 | 1ページ要約 | 状態 |
| --- | --- | --- | --- |
| [バックグラウンド音声の制限強化](all/media/background-audio-hardening.md) | Android 17 でバックグラウンドでの音声操作に共通制限が導入され、targetSdkVersion 37 以上では WIU 条件が追加される。 | [要約](../summaries/all/media/background-audio-hardening-summary.md) | AOSP タグ待ち / 低信頼度 |

### 接続

| レポート | 要約 | 1ページ要約 | 状態 |
| --- | --- | --- | --- |
| [Bluetooth ペアリング情報消失時の自律的な再ペアリング](all/connectivity/autonomous-repairing-bluetooth-bond-losses.md) | Android 17 で、Bluetooth のペアリング情報が失われた後にシステムが自律的な再ペアリングを試行できる。 | [要約](../summaries/all/connectivity/autonomous-repairing-bluetooth-bond-losses-summary.md) | AOSP タグ待ち / 低信頼度 |

<a id="target-apps"></a>

## Android 17 を対象とするアプリ

Android 17 以上を targetSdkVersion にしたアプリに関係する項目。

### コア機能

| レポート | 要約 | 1ページ要約 | 状態 |
| --- | --- | --- | --- |
| [MessageQueue の新しいロックフリー実装](target/core-functionality/messagequeue-lock-free.md) | targetSdkVersion 37 以上で `MessageQueue` がロックフリー実装になる。 | [要約](../summaries/target/core-functionality/messagequeue-lock-free-summary.md) | AOSP タグ待ち / 低信頼度 |
| [static final フィールドが変更不可に](target/core-functionality/static-final-fields.md) | targetSdkVersion 37 以上では reflection / JNI による `static final` フィールド変更が制限される。 | [要約](../summaries/target/core-functionality/static-final-fields-summary.md) | AOSP タグ待ち / 低信頼度 |

### アクセシビリティ

| レポート | 要約 | 1ページ要約 | 状態 |
| --- | --- | --- | --- |
| [複雑な IME 物理キーボード入力のアクセシビリティ対応](target/accessibility/accessibility-ime-physical-keyboard.md) | CJKV IME 変換中テキストに関するアクセシビリティフィードバックが改善される。 | [要約](../summaries/target/accessibility/accessibility-ime-physical-keyboard-summary.md) | AOSP タグ待ち / 低信頼度 |

### プライバシー

| レポート | 要約 | 1ページ要約 | 状態 |
| --- | --- | --- | --- |
| [ECH の有効化](target/privacy/ech-encrypted-client-hello.md) | targetSdkVersion 37 以上で ECH が TLS 接続に使われる。 | [要約](../summaries/target/privacy/ech-encrypted-client-hello-summary.md) | AOSP タグ待ち / 低信頼度 |
| [Android 17 を対象とするアプリに必要なローカルネットワーク権限](target/privacy/local-network-permission.md) | targetSdkVersion 37 以上で、ローカルネットワークアクセスに `ACCESS_LOCAL_NETWORK` 実行時権限が必要になる。 | [要約](../summaries/target/privacy/local-network-permission-summary.md) | AOSP タグ待ち / 低信頼度 |
| [物理入力デバイスでのパスワード非表示](target/privacy/hiding-passwords-physical-devices.md) | targetSdkVersion 37 以上で、物理入力デバイス利用時のパスワード表示設定が変わる。 | [要約](../summaries/target/privacy/hiding-passwords-physical-devices-summary.md) | AOSP タグ待ち / 低信頼度 |
| [標準 SMS メッセージの OTP 保護](target/privacy/otp-protection-standard-sms.md) | targetSdkVersion 37 以上で、標準 SMS OTP メッセージにも 3 時間の遅延が適用される。 | [要約](../summaries/target/privacy/otp-protection-standard-sms-summary.md) | AOSP タグ待ち / 低信頼度 |

### セキュリティ

| レポート | 要約 | 1ページ要約 | 状態 |
| --- | --- | --- | --- |
| [Activity セキュリティ](target/security/activity-security.md) | バックグラウンド Activity Launch の制限強化など、安全な既定値へ移行するための変更。 | [要約](../summaries/target/security/activity-security-summary.md) | AOSP タグ待ち / 低信頼度 |
| [CT のデフォルト有効化](target/security/enable-ct-by-default.md) | targetSdkVersion 37 以上で証明書透明性がデフォルトで有効になる。 | [要約](../summaries/target/security/enable-ct-by-default-summary.md) | AOSP タグ待ち / 低信頼度 |
| [より安全なネイティブ DCL-C](target/security/safer-native-dcl-c.md) | targetSdkVersion 37 以上で、ネイティブ動的コード読み込みの読み取り専用要件が適用される。 | [要約](../summaries/target/security/safer-native-dcl-c-summary.md) | AOSP タグ待ち / 低信頼度 |
| [CP2 データビューの PII フィールド制限](target/security/restrict-pii-fields-cp2-data-view.md) | Contacts Provider 2 のデータビューから一部の PII 列が除外される。 | [要約](../summaries/target/security/restrict-pii-fields-cp2-data-view-summary.md) | AOSP タグ待ち / 低信頼度 |
| [CP2 の厳格な SQL 検証](target/security/enforce-strict-sql-checks-cp2.md) | `READ_CONTACTS` なしで CP2 データテーブルを問い合わせる場合に、厳格な SQL 検証が適用される。 | [要約](../summaries/target/security/enforce-strict-sql-checks-cp2-summary.md) | AOSP タグ待ち / 低信頼度 |

### メディア

| レポート | 要約 | 1ページ要約 | 状態 |
| --- | --- | --- | --- |
| [バックグラウンド音声の制限強化 - targetSdkVersion 37 追加制限](target/media/background-audio-hardening.md) | targetSdkVersion 37 以上で、フォアグラウンドサービスの WIU 能力 / 正確なアラーム + `USAGE_ALARM` 条件が追加される。 | [要約](../summaries/target/media/background-audio-hardening-summary.md) | AOSP タグ待ち / 低信頼度 |

### 端末フォームファクター

| レポート | 要約 | 1ページ要約 | 状態 |
| --- | --- | --- | --- |
| [大画面で画面向き・リサイズ可否・アスペクト比制約を無視するプラットフォーム API の変更](target/device-form-factors/large-screen-orientation-resizability-aspect-ratio.md) | targetSdkVersion 37 以上では、大画面上で画面向き / リサイズ可否 / アスペクト比の制限が無視される。 | [要約](../summaries/target/device-form-factors/large-screen-orientation-resizability-aspect-ratio-summary.md) | AOSP タグ待ち / 低信頼度 |

### 接続

| レポート | 要約 | 1ページ要約 | 状態 |
| --- | --- | --- | --- |
| [RFCOMM の BluetoothSocket read() 挙動の一貫化](target/connectivity/consistent-bluetoothsocket-read-rfcomm.md) | targetSdkVersion 37 で、RFCOMM `BluetoothSocket` の `read()` が close / disconnect 時に `-1` を返す。 | [要約](../summaries/target/connectivity/consistent-bluetoothsocket-read-rfcomm-summary.md) | AOSP タグ待ち / 低信頼度 |
