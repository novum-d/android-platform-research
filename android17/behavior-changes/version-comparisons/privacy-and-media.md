# Android 16 → 17 Privacy and Media 挙動比較

## 1. 比較範囲

- [比較一覧](README.md)
- [Android 17対応例](../implementation-examples/privacy-and-media.md)
- Baseline: Android 16 / `android-16.0.0_r4`
- Target: Android 17 / `android-17.0.0_r1`
- Observed: SMS、LAN、TLS、password UI、audioとも未実施

## 2. 先に結論

Android 16でopt-inまたは限定適用だったprivacy protectionの一部が、
Android 17ではtargetSdkVersion 37 appのdefault / mandatory behaviorになる。
特にLocal Network Permission、standard SMS OTP、ECHはtarget 37移行試験が必要である。
Background audioにはall-apps制限とtarget37追加制限の二層がある。

## 3. 項目別比較

### SMS OTP protection

- [All-apps主レポート](../all/privacy/sms-otp-protection.md)
- [All-apps要約](../../summaries/all/privacy/sms-otp-protection-summary.md)
- [Standard SMS主レポート](../target/privacy/otp-protection-standard-sms.md)
- [Standard SMS要約](../../summaries/target/privacy/otp-protection-standard-sms-summary.md)

| Message | Android 16 | Android 17 |
| --- | --- | --- |
| SMS Retriever hash | intended app以外へ3時間delayする既存保護 |保護を継続 |
| WebOTP |同等のdomain-based 3時間保護は対象外 | all appsでdomain verification非一致appへのbroadcast / queryを3時間保留 |
| Standard OTP SMS | SMS permission appが直接抽出し得る | target37の多くのappでは3時間保留 |

対応:

- inbox / provider / `SMS_RECEIVED_ACTION`の直接抽出からSMS RetrieverまたはSMS User Consentへ移行する。
- default SMS / assistant / companionなどの例外roleを一般appへ一般化しない。

### Local network permission

- [主レポート](../target/privacy/local-network-permission.md)
- [要約](../../summaries/target/privacy/local-network-permission-summary.md)
- 適用: `TARGET_SDK_37_CONDITIONAL`

| 観点 | Android 16 | Android 17 / target 37 |
| --- | --- | --- |
| System behavior | `RESTRICT_LOCAL_NETWORK` compat opt-in test。current restoreは`NEARBY_WIFI_DEVICES` | direct LAN accessに`ACCESS_LOCAL_NETWORK` runtime permissionをmandatory enforcement |
| App signal | defaultではLAN socket / NSDが従来動作 | denied / revokedでLAN discovery・socket・HTTP等が失敗。Internetは別 |
| 対応 | opt-inでinventory / error pathを先行検証 | permission宣言・request・rationale・revocation、またはsystem-mediated picker |

system pickerで完結する単一device selectionと、persistent / direct LAN accessを分ける。

### ECH enabled

- [主レポート](../target/privacy/ech-encrypted-client-hello.md)
- [要約](../../summaries/target/privacy/ech-encrypted-client-hello-summary.md)
- 適用: `TARGET_SDK_37_CONDITIONAL`

| 観点 | Android 16 | Android 17 / target 37 |
| --- | --- | --- |
| System behavior | ECHをdefault適用するtarget37 ruleなし | supported library / serverでopportunistic ECH。非成立時はECH GREASE |
| App signal | TLS ClientHelloのSNIがnetwork observerから見える前提 | SNIが暗号化され、enterprise inspection / filtering前提が変化 |
| 対応 | endpoint / library / proxyを棚卸し | `<domainEncryption>`のglobal / per-domain policyと接続fallbackを検証 |

### Hiding passwords from physical devices

- [主レポート](../target/privacy/hiding-passwords-physical-devices.md)
- [要約](../../summaries/target/privacy/hiding-passwords-physical-devices-summary.md)
- 適用: `TARGET_SDK_37_CONDITIONAL`

| 観点 | Android 16 | Android 17 / target 37 |
| --- | --- | --- |
| System behavior | touch / physical入力が共通のshow-password挙動 | physical keyboardは`show_passwords_physical`を使い、defaultですべて非表示 |
| App signal |最後の1文字が一時表示され得る | external keyboard入力では直ちにmask |
| 対応 | custom password field / transformationを検出 | touch / physicalを分離してvisual・accessibility・IME試験 |

### Background audio hardening

- [All-apps主レポート](../all/media/background-audio-hardening.md)
- [All-apps要約](../../summaries/all/media/background-audio-hardening-summary.md)
- [Target37主レポート](../target/media/background-audio-hardening.md)
- [Target37要約](../../summaries/target/media/background-audio-hardening-summary.md)

| 観点 | Android 16 | Android 17 / target36 | Android 17 / target37 |
| --- | --- | --- | --- |
| Playback / volume |既存lifecycle / AppOps policy | background interactionをpartial hardening。playback / volumeはsilent no-opになり得る | stricter block |
| Audio focus | request可能な経路 |不正background requestは`AUDIOFOCUS_REQUEST_FAILED` | foreground service + WIU capability等を要求 |
| Alarm exception |既存policy |条件付き | exact alarm permission + `USAGE_ALARM`で例外になり得る |

対応:

- playback、focus、volume、ringerを別APIとしてlogする。
- user actionから開始し、必要なforeground service / while-in-use capabilityを満たす。
- silent failureを成功扱いしない。

## 4. OS / targetSdk マトリクス

| 項目 | Android 16 / target36 | Android 17 / target36 | Android 17 / target37 |
| --- | --- | --- | --- |
| WebOTP protection | baseline | 3時間保護 |同左 |
| Standard OTP | baseline | legacy | 3時間保護 |
| Local network | opt-inのみ | target36はlegacy | runtime permission必須 |
| ECH | target37 defaultなし | target36はlegacy | supported条件でdefault |
| Physical password |共通setting | target36はlegacy | physical入力をdefault mask |
| Background audio | baseline | partial all-apps restriction | strict追加条件 |

## 5. 比較試験

| Case | Trigger | Expected Android 16 | Expected Android 17 | Observed |
| --- | --- | --- | --- | --- |
| P1 | non-recipient WebOTP read |即時accessし得る |3時間filter | 未実施 |
| P2 | target37 standard OTP |即時accessし得る |3時間filter | 未実施 |
| P3 | LAN permission deny | default通信成功 | target37でLAN失敗 | 未実施 |
| P4 | ECH対応endpoint |通常TLS | target37でECH / GREASE | 未実施 |
| P5 | physical keyboard password |最後の文字表示 | target37で全mask | 未実施 |
| P6 | background focus request |既存結果 | failure code | 未実施 |

## 6. Evidence / Human Decision

実装gate、role exception、networking library、native AudioPolicyの制約とconfidenceは主レポートを正とする。
この資料ではObserved resultとHuman Decisionを確定しない。
