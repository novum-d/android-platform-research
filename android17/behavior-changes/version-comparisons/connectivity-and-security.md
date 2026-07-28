# Android 16 → 17 Connectivity and Security 挙動比較

## 1. 比較範囲

- [比較一覧](README.md)
- [Android 17対応例](../implementation-examples/connectivity-and-security.md)
- Baseline: Android 16 / `android-16.0.0_r4`
- Target: Android 17 / `android-17.0.0_r1`
- Observed: peripheral、profile、TLS endpoint、work profile、Contacts Providerとも未実施

## 2. 先に結論

Android 16のBluetooth bond lossは「local bondを保持してuser-driven recovery」だったが、
Android 17ではsystemがautonomous re-pairingを先に試す。Securityでは、target 37で
CT、native DCL、Activity起動、Contacts queryなどのdefaultが厳格化される。
一方、cleartext trafficとimplicit URI grantは将来変更に向けたguidanceであり、
Android 17で直ちに削除されるruntime behaviorとして扱わない。

## 3. 項目別比較

### Autonomous re-pairing for Bluetooth bond losses

- [主レポート](../all/connectivity/autonomous-repairing-bluetooth-bond-losses.md)
- [要約](../../summaries/all/connectivity/autonomous-repairing-bluetooth-bond-losses-summary.md)
- 適用: `OS_UPDATE_ALL_APPS`

| 観点 | Android 16 | Android 17 |
| --- | --- | --- |
| System behavior | key missingを通知し、local bondを保持してuser-driven re-pairへ | systemがbackgroundでautonomous re-pairを試行 |
| Pairing signal |通常pairing request | `ACTION_PAIRING_REQUEST`に`EXTRA_PAIRING_CONTEXT`を付加 |
| Key missing timing | bond loss検出時のprimary signal | autonomous repairが失敗した場合にbroadcast |
| Recovery | userがSettingsでunpair / re-pair | security levelを維持できる場合のみkey更新。system UIで確認 |

状態差:

```text
Android 16: bond loss -> ACTION_KEY_MISSING -> disconnect -> user re-pair
Android 17: bond loss -> autonomous re-pair -> success
                                      \-> failure -> ACTION_KEY_MISSING -> user recovery
```

app独自の即時`removeBond()` / pairing UIがsystem recoveryと競合しないようにする。

### Consistent RFCOMM `BluetoothSocket.read()`

- [主レポート](../target/connectivity/consistent-bluetoothsocket-read-rfcomm.md)
- [要約](../../summaries/target/connectivity/consistent-bluetoothsocket-read-rfcomm-summary.md)
- 適用: `TARGET_SDK_37_CONDITIONAL`

| 観点 | Android 16 / target36 | Android 17 / target37 |
| --- | --- | --- |
| System behavior | RFCOMM close / dropをread exceptionとして扱うlegacy path | Java `InputStream` semanticsに合わせEOF `-1` |
| App signal | `IOException`中心 | `read() == -1` |
| 対応 | exceptionだけでloop終了する実装を検出 | `-1`を明示的にdisconnectとして処理 |

### `usesCleartextTraffic` deprecation plan

- [主レポート](../all/security/usescleartexttraffic-deprecation-plan.md)
- [要約](../../summaries/all/security/usescleartexttraffic-deprecation-plan-summary.md)

| 観点 | Android 16 | Android 17 |
| --- | --- | --- |
| Runtime | `usesCleartextTraffic`が機能 |属性は引き続き機能。将来deprecation planを告知 |
| Developer action | manifest attributeだけに依存し得る | API 24+ではNetwork Security Configへdomain単位policyを移行 |

Android 17でHTTPが一律blockされる変更ではない。minSdk < 24では互換manifest属性も必要。

### Restrict implicit URI grants

- [主レポート](../all/security/restrict-implicit-uri-grants.md)
- [要約](../../summaries/all/security/restrict-implicit-uri-grants-summary.md)

| 観点 | Android 16 | Android 17 |
| --- | --- | --- |
| Runtime | `ACTION_SEND` / `SEND_MULTIPLE` / `IMAGE_CAPTURE`でsystem implicit grantに依存可能 | automatic grantは現時点で残るが、Android 18 removalに向けStrictMode / logで検出 |
| 対応 | grant flagがなくても動く場合がある | read / write URI grant flagをactionに応じて明示 |

### Per-app Keystore limits

- [主レポート](../all/security/per-app-keystore-limits.md)
- [要約](../../summaries/all/security/per-app-keystore-limits-summary.md)
- 適用: Android 17 all apps。limit値とerror codeはtarget依存

| 観点 | Android 16 | Android 17 |
| --- | --- | --- |
| System behavior | Android 17のper-app ownership hard limitなし | non-system target37は50,000 keys、その他は200,000 |
| App signal | excessive creationのfailureはresource / implementation依存 | `KeyStoreException`。target37は`ERROR_TOO_MANY_KEYS`、他は`ERROR_INCORRECT_USAGE` |
| 対応 | key lifecycleを計測 | alias reuse、rotation時delete、orphan cleanup、limit error handling |

### Block cross-profile loopback traffic

- [主レポート](../all/security/block-cross-profile-loopback-traffic.md)
- [要約](../../summaries/all/security/block-cross-profile-loopback-traffic-summary.md)
- 適用: `OS_UPDATE_ALL_APPS`

| 観点 | Android 16 | Android 17 |
| --- | --- | --- |
| System behavior | personal / work profile間でloopback serviceへ到達し得る | cross-profile loopbackをdefault block |
| App signal | `127.0.0.1` / `::1`接続がprofile境界を越えて成立し得る | connect failure / timeout |
| 対応 | profile境界を越えるlocalhost IPCを検出 | supported cross-profile API、binder、explicit network endpointへ |

同一profile内loopbackは対象外。

### Activity Security

- [主レポート](../target/security/activity-security.md)
- [要約](../../summaries/target/security/activity-security-summary.md)
- 適用: `TARGET_SDK_37_CONDITIONAL`

| 観点 | Android 16 | Android 17 / target37 |
| --- | --- | --- |
| System behavior | broad `MODE_BACKGROUND_ACTIVITY_START_ALLOWED` opt-inが利用可能 | `IntentSender`を含むBAL hardening。visible条件などgranular modeを要求 |
| App signal | background / trampoline launchが成功し得る | launch block、StrictMode / lint signal |
| 対応 | PendingIntent / IntentSender producer・senderを棚卸し |通常は`ALLOW_IF_VISIBLE`。`ALLOW_ALWAYS`は限定用途だけ |

### Certificate Transparency default enabled

- [主レポート](../target/security/enable-ct-by-default.md)
- [要約](../../summaries/target/security/enable-ct-by-default-summary.md)
- 適用: `TARGET_SDK_37_CONDITIONAL`

| 観点 | Android 16 | Android 17 / target37 |
| --- | --- | --- |
| System behavior | CTはNetwork Security Config等でopt-in | platform TLSでCT default enabled |
| App signal | opt-inしない接続はCT要件外 | CT非対応certificate chainでTLS failureになり得る |
| 対応 | production / staging / private PKIをinventory | certificate chain、pinning、NSC、CT log inclusionを検証 |

### Safer Native DCL-C

- [主レポート](../target/security/safer-native-dcl-c.md)
- [要約](../../summaries/target/security/safer-native-dcl-c-summary.md)
- 適用: `TARGET_SDK_37_CONDITIONAL`

| 観点 | Android 16 | Android 17 / target37 |
| --- | --- | --- |
| System behavior | DEX / JAR向けDCL protectionはあるがnative `System.load()`のtarget37 readonly強制なし | writable native fileの`System.load()`を拒否 |
| App signal | downloaded / extracted `.so`をloadできる場合がある | `UnsatisfiedLinkError` |
| 対応 | native download / generate / update pathを検出 | load前にread-only化し、その後書換不能を保証。可能ならDCL廃止 |

### Restrict PII fields in CP2 data view

- [主レポート](../target/security/restrict-pii-fields-cp2-data-view.md)
- [要約](../../summaries/target/security/restrict-pii-fields-cp2-data-view-summary.md)
- 適用: `TARGET_SDK_37_CONDITIONAL`

| 観点 | Android 16 | Android 17 / target37 |
| --- | --- | --- |
| System behavior | `ContactsContract.Data` projectionでaccount PII columnsを取得可能 | `ACCOUNT_NAME`、`ACCOUNT_TYPE`、`ACCOUNT_TYPE_AND_DATA_SET`をdata viewから制限 |
| App signal | cursorにcolumnsあり | missing / restricted projection |
| 対応 | Data query projectionを検索 | `RAW_CONTACT_ID`で`RawContacts`から必要情報を取得 |

### Enforce strict SQL checks in CP2

- [主レポート](../target/security/enforce-strict-sql-checks-cp2.md)
- [要約](../../summaries/target/security/enforce-strict-sql-checks-cp2-summary.md)
- 適用: `TARGET_SDK_37_CONDITIONAL` + `READ_CONTACTS`なし

| 観点 | Android 16 | Android 17 / target37 |
| --- | --- | --- |
| System behavior | permissionなしData queryにlegacy SQL validation | `StrictColumns` / `StrictGrammar`を強制 |
| App signal |非標準projection / selectionが通る場合がある | incompatible queryでexception |
| 対応 | raw SQL fragment、alias、projectionを検出 | documented columns / grammarに限定し、permissionなしcaseを試験 |

## 4. OS / targetSdk マトリクス

| 項目 | Android 16 / target36 | Android 17 / target36 | Android 17 / target37 |
| --- | --- | --- | --- |
| Bluetooth re-pair | user-driven | autonomous repair | target36と同じ |
| RFCOMM EOF | exception path | legacy | `-1` |
| Cleartext / URI grant | legacy | guidance / detection | target36と同じ |
| Keystore limit |新limitなし | 200k | non-system 50k |
| Cross-profile loopback |到達し得る | default block | target36と同じ |
| Activity Security | legacy BAL | compatibility | granular hardening |
| CT | opt-in | opt-in | default enabled |
| Native DCL | writable load可能性 | compatibility | readonly必須 |
| CP2 PII / SQL | legacy | compatibility | restriction / strict validation |

## 5. 比較試験

| Case | Trigger | Expected Android 16 | Expected Android 17 | Observed |
| --- | --- | --- | --- | --- |
| S1 | peripheral remote bond loss | key-missing後user recovery | autonomous repairを先行 | 未実施 |
| S2 | RFCOMM peer close | exception中心 | target37で`-1` | 未実施 |
| S3 | URI intent without grant flags | implicit grant | log / future warning、現状grant | 未実施 |
| S4 | profile跨ぎloopback |接続し得る | block | 未実施 |
| S5 | background PendingIntent launch | broad opt-in可能 | target37でvisible条件 | 未実施 |
| S6 | CT不適合TLS chain | opt-in時のみfailure | target37 defaultでfailure | 未実施 |
| S7 | writable `.so` load | loadし得る | `UnsatisfiedLinkError` | 未実施 |
| S8 | CP2 legacy query | data / queryが通る | target37で制限 / exception | 未実施 |

## 6. Evidence / Human Decision

Facts、AOSP gate、compat Change ID、role / permission / device exception、confidenceは各主レポートを正とする。
この資料ではObserved resultとHuman Decisionを確定しない。
