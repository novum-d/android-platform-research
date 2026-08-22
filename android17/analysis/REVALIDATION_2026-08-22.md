# Android 17 全項目再検証台帳（2026-08-22）

## 目的

Android 17 の既存 Behavior Change 調査へ、最新のレビュー済みルールが反映されているかを全件確認した記録である。個別レポートの分類、confidence、AOSP source context、Human Decision を置き換えない。

## 公式文書とタグ

- all-apps: https://developer.android.com/about/versions/17/behavior-changes-all
- target: https://developer.android.com/about/versions/17/behavior-changes-17
- 比較: `android-16.0.0_r4` -> `android-17.0.0_r1`
- 公式refs確認日: 2026-08-22
- 結果: baseline / target とも、各利用AOSP projectで上記が最新通常リリースタグ。
- Android 17 の公式ページ最終更新: all-apps / target 2026-08-14 UTC。compat framework URL は 2026-08-22 時点で HTTP 404。

## AOSP workspace と再実行結果

`git status --short` または展開中の index lock、official remote、タグ存在、解決済みcommitを確認し、working tree に依存しない次の比較を各projectで再実行した。

```bash
git -C <checkout> diff --no-renames --name-only android-16.0.0_r4 android-17.0.0_r1
```

| AOSP project | Official remote URL | Checkout path | From commit | To commit | Changed paths | Inventory SHA-256 | Working tree |
| --- | --- | --- | --- | --- | ---: | --- | --- |
| `platform/frameworks/base` | `https://android.googlesource.com/platform/frameworks/base` | `frameworks-base/` | `45034f0663f960d9ee5fb0a101a4732b71f6e2f4` | `94b4c163b7dfe5ce3607f7bb8456f9573f7de57d` | 18434 | `6768dd7bc470438c3111d2e4944db0706387bb9e1a341f3be5b4aea95cd6e5d0` | Clean |
| `platform/packages/modules/Bluetooth` | `https://android.googlesource.com/platform/packages/modules/Bluetooth` | `tmp/aosp-checkouts/Bluetooth/` | `5323f31677c7dfa04de2e6e9fce1012ef4edaff2` | `c77db469de80f86660bc053bec4dee0c5d4b947c` | 4103 | `977fb7a22fb6df08f3489863101568fae14cccf64da43875c7b4165e221c839e` | 展開中 |
| `platform/art` | `https://android.googlesource.com/platform/art` | `tmp/aosp-checkouts/art/` | `1690c6912a7972c9e62c39b48c706de9b8b18b4a` | `b753cf97923c3695338d21466fa14c57b480a59a` | 2066 | `c7003190d3bee2fe0cce8e34429cc74a1e6c6685127f6b1bb0bf96153ea37916` | 展開中 |
| `platform/libcore` | `https://android.googlesource.com/platform/libcore` | `tmp/aosp-checkouts/libcore/` | `1c599b67bcd3de5c50c79d0622e40b6de99b4cb4` | `4ebfb391ee0109d16abe6e2bc965724b940928c5` | 412 | `f14e3aab100872da0cc86af2d9ca7bcc786646c17d0d4b24040ea1aa07072ea3` | 展開中 |
| `platform/packages/providers/ContactsProvider` | `https://android.googlesource.com/platform/packages/providers/ContactsProvider` | `tmp/aosp-checkouts/ContactsProvider/` | `5821e66694f1075d15e48f9a7d073bddd7b34aa8` | `3788ede92ad2ab5f69d7d5da740c1e449980949c` | 42 | `2390a3512fd2b8f2fb17ac8648547bb8dbda1ecff7da42bfabbb4217b030f9d5` | Clean |

## 項目別結果

全レポートで、公式 section、OS / targetSdkVersion の分離、AOSP project provenance、source context、diff interpretation、Facts / Observations / Hypotheses / Conclusions、Human Decision の参照を確認した。タグが同一だったため、既存の結論や confidence は機械的に引き上げず、未確認事項を維持した。

| レポート | 1ページ要約 | 主分類 | AOSP project | 結果 |
| --- | --- | --- | --- | --- |
| [Autonomous re-pairing for Bluetooth bond losses](../behavior-changes/all/connectivity/autonomous-repairing-bluetooth-bond-losses.md) | [要約](../summaries/all/connectivity/autonomous-repairing-bluetooth-bond-losses-summary.md) | `OS_UPDATE_ALL_APPS` | `platform/frameworks/base`<br>`platform/packages/modules/Bluetooth` | 再検証済み |
| [App memory limits](../behavior-changes/all/core-functionality/app-memory-limits.md) | [要約](../summaries/all/core-functionality/app-memory-limits-summary.md) | `OS_UPDATE_ALL_APPS` | `platform/frameworks/base` | 再検証済み |
| [Touchpads deliver relative events by default during pointer capture](../behavior-changes/all/human-input/touchpads-relative-events-pointer-capture.md) | [要約](../summaries/all/human-input/touchpads-relative-events-pointer-capture-summary.md) | `OS_UPDATE_ALL_APPS` | `platform/frameworks/base` | 再検証済み |
| [Background audio hardening](../behavior-changes/all/media/background-audio-hardening.md) | [要約](../summaries/all/media/background-audio-hardening-summary.md) | `OS_UPDATE_ALL_APPS` | `platform/frameworks/base` | 再検証済み |
| [SMS OTP protection](../behavior-changes/all/privacy/sms-otp-protection.md) | [要約](../summaries/all/privacy/sms-otp-protection-summary.md) | `OS_UPDATE_ALL_APPS` | `platform/frameworks/base` | 再検証済み |
| [Block cross profile loopback traffic](../behavior-changes/all/security/block-cross-profile-loopback-traffic.md) | [要約](../summaries/all/security/block-cross-profile-loopback-traffic-summary.md) | `OS_UPDATE_ALL_APPS` | `platform/frameworks/base` | 再検証済み |
| [Per-app keystore limits](../behavior-changes/all/security/per-app-keystore-limits.md) | [要約](../summaries/all/security/per-app-keystore-limits-summary.md) | `OS_UPDATE_ALL_APPS` | `platform/frameworks/base` | 再検証済み |
| [Implicit URI grants の制限](../behavior-changes/all/security/restrict-implicit-uri-grants.md) | [要約](../summaries/all/security/restrict-implicit-uri-grants-summary.md) | `TARGET_SDK_37_CONDITIONAL` | `platform/frameworks/base` | 再検証済み |
| [usesCleartextTraffic の deprecation plan](../behavior-changes/all/security/usescleartexttraffic-deprecation-plan.md) | [要約](../summaries/all/security/usescleartexttraffic-deprecation-plan-summary.md) | `TARGET_SDK_37_CONDITIONAL` | `platform/frameworks/base` | 再検証済み |
| [Rotation 後の default IME visibility 復元](../behavior-changes/all/user-experience-and-system-ui/restoring-default-ime-visibility-after-rotation.md) | [要約](../summaries/all/user-experience-and-system-ui/restoring-default-ime-visibility-after-rotation-summary.md) | `OS_UPDATE_ALL_APPS` | `platform/frameworks/base` | 再検証済み |
| [複雑な IME 物理キーボード入力のアクセシビリティ対応](../behavior-changes/target/accessibility/accessibility-ime-physical-keyboard.md) | [要約](../summaries/target/accessibility/accessibility-ime-physical-keyboard-summary.md) | `UNKNOWN_NEEDS_MORE_EVIDENCE` | `platform/frameworks/base` | 再検証済み |
| [RFCOMM における BluetoothSocket read() 挙動の一貫化](../behavior-changes/target/connectivity/consistent-bluetoothsocket-read-rfcomm.md) | [要約](../summaries/target/connectivity/consistent-bluetoothsocket-read-rfcomm-summary.md) | `TARGET_SDK_37_CONDITIONAL` | `platform/frameworks/base`<br>`platform/packages/modules/Bluetooth` | 再検証済み |
| [MessageQueue の新しい lock-free 実装](../behavior-changes/target/core-functionality/messagequeue-lock-free.md) | [要約](../summaries/target/core-functionality/messagequeue-lock-free-summary.md) | `TARGET_SDK_37` | `platform/frameworks/base` | 再検証済み |
| [static final field が変更不可に](../behavior-changes/target/core-functionality/static-final-fields.md) | [要約](../summaries/target/core-functionality/static-final-fields-summary.md) | `TARGET_SDK_37_CONDITIONAL` | `platform/frameworks/base`<br>`platform/art`<br>`platform/libcore` | 再検証済み |
| [大画面で画面向き・リサイズ可否・アスペクト比制約を無視するプラットフォーム API の変更（sw >= 600dp）](../behavior-changes/target/device-form-factors/large-screen-orientation-resizability-aspect-ratio.md) | [要約](../summaries/target/device-form-factors/large-screen-orientation-resizability-aspect-ratio-summary.md) | `TARGET_SDK_37_CONDITIONAL` | `platform/frameworks/base` | 再検証済み |
| [バックグラウンド音声の制限強化](../behavior-changes/target/media/background-audio-hardening.md) | [要約](../summaries/target/media/background-audio-hardening-summary.md) | `TARGET_SDK_37_CONDITIONAL` | `platform/frameworks/base` | 再検証済み |
| [ECH (Encrypted Client Hello) の有効化](../behavior-changes/target/privacy/ech-encrypted-client-hello.md) | [要約](../summaries/target/privacy/ech-encrypted-client-hello-summary.md) | `TARGET_SDK_37_CONDITIONAL` | `platform/frameworks/base` | 再検証済み |
| [物理デバイス入力時のパスワード非表示](../behavior-changes/target/privacy/hiding-passwords-physical-devices.md) | [要約](../summaries/target/privacy/hiding-passwords-physical-devices-summary.md) | `TARGET_SDK_37_CONDITIONAL` | `platform/frameworks/base` | 再検証済み |
| [Android 17 をターゲットにするアプリで必要になるローカルネットワーク権限](../behavior-changes/target/privacy/local-network-permission.md) | [要約](../summaries/target/privacy/local-network-permission-summary.md) | `TARGET_SDK_37_CONDITIONAL` | `platform/frameworks/base` | 再検証済み |
| [標準 SMS メッセージに対する OTP 保護](../behavior-changes/target/privacy/otp-protection-standard-sms.md) | [要約](../summaries/target/privacy/otp-protection-standard-sms-summary.md) | `TARGET_SDK_37_CONDITIONAL` | `platform/frameworks/base` | 再検証済み |
| [Activity 起動のセキュリティ強化](../behavior-changes/target/security/activity-security.md) | [要約](../summaries/target/security/activity-security-summary.md) | `TARGET_SDK_37_CONDITIONAL` | `platform/frameworks/base` | 再検証済み |
| [CT のデフォルト有効化](../behavior-changes/target/security/enable-ct-by-default.md) | [要約](../summaries/target/security/enable-ct-by-default-summary.md) | `TARGET_SDK_37_CONDITIONAL` | `platform/frameworks/base` | 再検証済み |
| [CP2 での strict SQL checks の強制](../behavior-changes/target/security/enforce-strict-sql-checks-cp2.md) | [要約](../summaries/target/security/enforce-strict-sql-checks-cp2-summary.md) | `TARGET_SDK_37_CONDITIONAL` | `platform/frameworks/base`<br>`platform/packages/providers/ContactsProvider` | 再検証済み |
| [CP2 data view における PII fields の制限](../behavior-changes/target/security/restrict-pii-fields-cp2-data-view.md) | [要約](../summaries/target/security/restrict-pii-fields-cp2-data-view-summary.md) | `TARGET_SDK_37_CONDITIONAL` | `platform/frameworks/base`<br>`platform/packages/providers/ContactsProvider` | 再検証済み |
| [Safer Native DCL-C](../behavior-changes/target/security/safer-native-dcl-c.md) | [要約](../summaries/target/security/safer-native-dcl-c-summary.md) | `TARGET_SDK_37_CONDITIONAL` | `platform/frameworks/base`<br>`platform/libcore` | 再検証済み |

## 変更点と制約

- Behavior Change section inventory は既存25件と一致し、未収録の section はなかった。
- Android 17 summary page にだけ掲載される追加調査待ち項目は、[`latest-documentation-gaps.md`](../behavior-changes/version-comparisons/latest-documentation-gaps.md) に引き続き分離する。
- 実機試験は今回実施していない。Expected と Observed を混同せず、未実施状態を維持した。
- 最終判断は [`DECISION_LOG.md`](../decisions/DECISION_LOG.md) のみが正本である。
