# New intents to handle bond loss and encryption changes 調査レポート

## 基本情報

### 調査対象 Android バージョン

From:
- android-15.0.0_r36

To:
- android-16.0.0_r4

Scope note:

### Behavior Change 文書

Document:
- https://developer.android.com/about/versions/16/behavior-changes-16#new-intents-to-handle-bond-loss

Section:
- New intents to handle bond loss and encryption changes

Category:
- Connectivity

Related all-apps behavior:
- https://developer.android.com/about/versions/16/behavior-changes-all#improved-bond-loss-handling

### 分類スナップショット

主分類:
- `OS_UPDATE_ALL_APPS`

補足:
- 公式 target apps 文書は「Apps targeting Android 16 can now receive」と説明しているが、AOSP 実装では `ACTION_KEY_MISSING` / `ACTION_ENCRYPTION_CHANGE` の broadcast 送信に `targetSdkVersion >= 36` gate は見つからなかった。
- Android 16 で API surface から `@FlaggedApi` が外れ、通常アプリが API 36 として定数を参照できるようになった点は targetSdkVersion 36 移行時の採用機会として扱う。
- 実際の受信・影響は、Android 16 以上、Bluetooth bonded device、remote bond loss または link encryption change、receiver / permission / OEM 実装差に依存する。

| 確認項目 | 回答 | 根拠 |
| --- | --- | --- |
| Android 16 に OS アップデートしただけで適用されるか | Conditional | Bluetooth stack は Android 16 で targetSdk gate なしに broadcast を送る。アプリが receiver を持ち、該当 Bluetooth event が発生する場合に観測される。 |
| targetSdkVersion 36 以上が必要か | No / API adoption には Yes | AOSP broadcast path に targetSdk gate は見つからない。一方、API 定数は Android 16 current API で flag なし public API になった。 |
| 追加の実行時条件があるか | Yes | bonded device、remote bond loss、encryption change、`BLUETOOTH_CONNECT`、receiver registration、OEM 実装差。 |
| Compat Change ID が関係するか | No | Android 16 compat framework 公式ページと Bluetooth `ChangeIds.java` に該当 Change ID は見つからない。 |

### 調査日

2026-07-03

### 信頼度

- Medium

理由:
- API surface、broadcast 送信経路、native stack から Java callback までの AOSP evidence は確認できた。
- ただし、公式文書が明示する OEM implementation variation は AOSP だけでは全 OEM 実装を検証できないため、OEM 差分に関する結論は Medium に留める。

## エグゼクティブサマリー

Android 16 では、Bluetooth の remote bond loss と link encryption change をアプリが把握しやすくするため、`BluetoothDevice.ACTION_KEY_MISSING` と `BluetoothDevice.ACTION_ENCRYPTION_CHANGE` が flag なし public API として利用可能になった。AOSP では Android 16 Bluetooth stack が `ACTION_KEY_MISSING` を `BLUETOOTH_CONNECT` の ordered broadcast として送り、`ACTION_ENCRYPTION_CHANGE` も encryption 状態・key size・algorithm を含めて broadcast する。

この項目は「targetSdkVersion 36 にした瞬間に既存処理が壊れる」変更というより、Android 16 上で Bluetooth bond loss / encryption change を扱うアプリが新しい signal を取り込めるようになる変更である。Android 16 へ OS アップデートしただけでも、アプリが action string を直接扱って receiver を持つ場合は受信し得るが、API として正式に扱うには API 36 への移行が前提になる。

顧客向けには、「Android 16 の OS 変更」と「targetSdkVersion 36 化による API 採用」を混ぜずに説明する必要がある。`ACTION_KEY_MISSING` が来る場合と来ない場合の両方を想定し、legacy な `ACTION_BOND_STATE_CHANGED` / disconnect based handling も fallback として残すべきである。

## 公式ドキュメント確認

### 原文で確認した主張

- Android 16 は improved bond loss handling の一部として、bond loss と encryption change の認識性を高める 2 つの intent を導入する。
- Android 16 を target するアプリは、remote bond loss 検出時に `ACTION_KEY_MISSING` を受信できる。
- Android 16 を target するアプリは、link encryption status が変化した時に `ACTION_ENCRYPTION_CHANGE` を受信できる。
- encryption status、encryption algorithm、encryption key size の変化を含む。
- 後続の `ACTION_ENCRYPTION_CHANGE` で link が正常に暗号化された場合、アプリは bond restored とみなす必要がある。
- 新 intent の実装と broadcast は OEM により異なる可能性がある。
- `ACTION_KEY_MISSING` が broadcast される場合、system は ACL link を切断し、bond information は保持する。
- `ACTION_KEY_MISSING` が broadcast されない場合、ACL link は接続されたまま、bond information は Android 15 と同様に削除される。

### 公式本文との差分

- 調査開始時点の公式本文は、ユーザー提示の Original statements と実質的に一致していた。
- サブセクション URL の anchor は公式 HTML 上でも `bond-loss-oem-impletations` という綴りである。
- 公式ページの Last updated は 2026-06-24 UTC。

## 変更内容

### Android 15 baseline

- Bluetooth module の `framework/api/current.txt` には `ACTION_KEY_MISSING` と `ACTION_ENCRYPTION_CHANGE` が存在するが、Android 15 tag では `@FlaggedApi("com.android.bluetooth.flags.key_missing_public")` / `@FlaggedApi("com.android.bluetooth.flags.encryption_change_broadcast")` が付いている。
- Android 15 の `RemoteDevices.keyMissingCallback()` は、`Flags.keyMissingPublic()` が true の場合のみ `BLUETOOTH_CONNECT` の ordered broadcast を送り、それ以外は `BLUETOOTH_CONNECT` と `BLUETOOTH_PRIVILEGED` の複数 permission broadcast を使う。
- Android 15 の `RemoteDevices.encryptionChangeCallback()` は intent を作るが、`Flags.encryptionChangeBroadcast()` が true の場合だけ broadcast する。
- LE key missing path では、status が `HCI_ERR_KEY_MISSING` のとき key flags / key type を消す分岐が確認できるため、公式文書の「ACTION_KEY_MISSING が来ない場合は Android 15 と同様に bond information が削除される」という説明と整合する legacy path がある。

### Android 16 target behavior

- Android 16 の API surface では、`ACTION_KEY_MISSING`、`ACTION_ENCRYPTION_CHANGE`、`EXTRA_ENCRYPTION_STATUS`、`EXTRA_ENCRYPTION_ALGORITHM`、`EXTRA_KEY_SIZE`、`EXTRA_ENCRYPTION_ENABLED` の `@FlaggedApi` が外れ、public API として利用できる。
- Android 16 の `BluetoothDevice.ACTION_KEY_MISSING` Javadoc は、Android 16 より前は `BLUETOOTH_PRIVILEGED` も必要だったが、Android 16 からは `BLUETOOTH_CONNECT` が主な受信 permission になることを示す。
- Android 16 の `RemoteDevices.keyMissingCallback(byte[] address, int reason)` は、bonded device でない場合は return し、bonded device の場合に `ACTION_KEY_MISSING` を作って `BLUETOOTH_CONNECT` の ordered broadcast として送信する。
- Android 16 の native stack では `btm_sec_report_bond_loss()` が bond loss を検出し、`bta_dm_remote_key_missing()` を呼んだ後、ACL link を `HCI_ERR_AUTH_FAILURE` で disconnect する。
- Android 16 の `RemoteDevices.encryptionChangeCallback()` は encryption event ごとに `ACTION_ENCRYPTION_CHANGE` を作り、status、enabled、transport、key size、algorithm を extra として送信する。Android 15 のような `Flags.encryptionChangeBroadcast()` gate はない。
- `ACTION_ENCRYPTION_CHANGE` で encryption が enabled になり、かつ key missing count が残っている場合、Android 16 は `ACTION_KEY_MISSING_TO_ENCRYPTION_CHANGE` transition を記録し、key missing count を reset する。これは公式文書の「link が正常に暗号化されたら bond restored とみなす」と整合する。

## 適用条件

### OS アップデート時の挙動

- Android 16 に OS アップデートしただけで、Bluetooth stack 側の `ACTION_KEY_MISSING` / `ACTION_ENCRYPTION_CHANGE` broadcast 実装は存在する。
- AOSP の broadcast path には `targetSdkVersion >= 36` gate は見つからない。
- targetSdkVersion 35 のアプリでも、action string を直接扱い、`BLUETOOTH_CONNECT` を持ち、receiver が適切に登録され、該当 Bluetooth event が発生すれば、Android 16 上で broadcast を観測できる可能性がある。
- ただし API 定数として正式に参照し、SDK 型安全に実装するには Android 16 / API 36 への compile/target 移行が現実的な前提になる。

### targetSdkVersion 36 以上での挙動

- targetSdkVersion 36 以上に上げること自体で broadcast 送信ロジックが有効化される AOSP gate は確認できなかった。
- targetSdkVersion 36 / compile SDK 36 では、`BluetoothDevice.ACTION_KEY_MISSING` と `ACTION_ENCRYPTION_CHANGE` が flag なし public API として参照可能になる。
- Android 15 端末上で targetSdkVersion 36 にしただけでは、Android 16 Bluetooth stack の new public API / broadcast behavior は保証されない。Android 15 tag の API は flagged で、runtime broadcast も flag dependent である。

### その他の条件

- Bluetooth bonded device を扱う。
- remote bond loss または link encryption change が発生する。
- アプリが `BLUETOOTH_CONNECT` permission を持つ。
- receiver が manifest / runtime のどちらかで適切に登録されている。
- OEM / vendor / Bluetooth controller / stack 実装が該当 callback を AOSP と同様に broadcast する。
- `ACTION_KEY_MISSING` が broadcast されない device では、従来の bond loss handling が必要になる。

## AOSP 調査

### 使用 checkout

- `frameworks-base`: clean。`android-15.0.0_r36` と `android-16.0.0_r4` tag を確認済み。
- `tmp/aosp-checkouts/Bluetooth`: clean。`android-15.0.0_r36` = `2dcb862e7ff2a006ae4fb7bc5af149f0b2befc3b`、`android-16.0.0_r4` = `47bc1e1ce4eade22b0d9dabdf7e70f6ed4eafb40`。

### 関連ファイル

- `packages/modules/Bluetooth/framework/api/current.txt`
- `packages/modules/Bluetooth/framework/java/android/bluetooth/BluetoothDevice.java`
- `packages/modules/Bluetooth/android/app/src/com/android/bluetooth/btservice/RemoteDevices.java`
- `packages/modules/Bluetooth/android/app/src/com/android/bluetooth/btservice/JniCallbacks.java`
- `packages/modules/Bluetooth/android/app/jni/com_android_bluetooth_btservice_AdapterService.cpp`
- `packages/modules/Bluetooth/system/stack/btm/btm_sec.cc`
- `packages/modules/Bluetooth/system/bta/dm/bta_dm_sec.cc`
- `packages/modules/Bluetooth/system/btif/src/btif_dm.cc`
- `packages/modules/Bluetooth/system/btif/src/bluetooth.cc`
- `packages/modules/Bluetooth/android/app/change-ids/com/android/bluetooth/ChangeIds.java`
- `frameworks/base/core/res/AndroidManifest.xml`

### 確認したソース文脈

| ファイル / シンボル | Android 15 の基準挙動 | Android 16 の挙動 | 根拠としての意味 |
| --- | --- | --- | --- |
| `BluetoothDevice.ACTION_KEY_MISSING` | `@FlaggedApi(key_missing_public)` 付き。broadcast receiver には `BLUETOOTH_CONNECT` と条件付き `BLUETOOTH_PRIVILEGED` が関係する。 | flag なし public API。Javadoc は Android 16 より前に `BLUETOOTH_PRIVILEGED` が必要だったことを明記。 | API 36 で通常アプリ向けに露出した根拠。 |
| `BluetoothDevice.ACTION_ENCRYPTION_CHANGE` | `@FlaggedApi(encryption_change_broadcast)` 付き。 | flag なし public API。status / enabled / key size / algorithm extra が public。 | encryption change intent が Android 16 の public API になった根拠。 |
| `RemoteDevices.keyMissingCallback()` | flag により送信 permission / ordered broadcast path が分岐。 | bonded device の場合に `ACTION_KEY_MISSING` を `BLUETOOTH_CONNECT` で ordered broadcast。 | アプリが Android 16 で受信可能になる実行時 path。 |
| `RemoteDevices.encryptionChangeCallback()` | `Flags.encryptionChangeBroadcast()` が true の場合のみ broadcast。 | flag gate なしで `ACTION_ENCRYPTION_CHANGE` を broadcast。 | encryption status / algorithm / key size change 通知の実装根拠。 |
| `btm_sec_report_bond_loss()` | Android 15 では分散した flag dependent path。 | bond loss 検出時に `bta_dm_remote_key_missing()` を呼び、ACL link を disconnect。 | `ACTION_KEY_MISSING` broadcast と ACL disconnect の native stack 根拠。 |
| `DatabaseManager.updateKeyMissingCount()` | Android 16 の key missing count 管理は確認できない。 | key missing 検出時に count increment、successful bond 検出時に reset。 | 後続 encryption success を bond restored と扱う補助根拠。 |
| `frameworks/base/core/res/AndroidManifest.xml` | 該当 protected broadcast の Android 15 状態は未採用。 | `android.bluetooth.device.action.KEY_MISSING` と `android.bluetooth.device.action.ENCRYPTION_CHANGE` が protected broadcast。 | 送信元が system/Bluetooth stack であることの根拠。 |
| `Bluetooth ChangeIds.java` | `ENFORCE_CONNECT` のみ。 | `ENFORCE_CONNECT` のみ。 | この behavior 用の compat Change ID は確認できない。 |

Entry point / caller:
- Native HCI / security event -> `btm_sec_report_bond_loss()` or `bta_dm_on_encryption_change()` -> `BTA_DM_KEY_MISSING_EVT` / `BTA_DM_ENCRYPTION_CHANGE_EVT` -> `btif_dm.cc` -> `invoke_key_missing_cb()` / `invoke_encryption_change_cb()` -> JNI callbacks -> `RemoteDevices.keyMissingCallback()` / `RemoteDevices.encryptionChangeCallback()` -> Android broadcast.

Relevant class or service responsibility:
- `BluetoothDevice`: app-facing action / extra constants.
- `RemoteDevices`: remote device state, bond state, ACL/encryption callback handling and broadcast emission.
- `btm_sec.cc`: Bluetooth security manager; HCI key missing / encryption failure / incoming pairing while bonded を bond loss として検出。

Runtime path from app/system event to changed code:
- Remote device が bond を失った状態で reconnect / authentication / encryption が発生する。
- HCI status `HCI_ERR_KEY_MISSING` または bonded unencrypted incoming pairing が security manager に届く。
- Android 16 は `ACTION_KEY_MISSING` を broadcast し、ACL link を disconnect する。
- 後続の encryption change では `ACTION_ENCRYPTION_CHANGE` を broadcast し、status / enabled / key size / algorithm を extra として付与する。

Excluded code paths:
- A2DP / socket / LE subrate など同じ API diff に含まれる Bluetooth 変更は、この Behavior Change の bond loss / encryption intent とは直接関係しないため除外した。
- DevicePolicyManager の `THROW_EXCEPTION_WHEN_KEY_MISSING` は Android Keystore / DPM 系の別 compat change であり、Bluetooth bond loss intent とは無関係のため除外した。

## 差分解釈

| 確認した差分 | 解釈 | Behavior Change との関係 | 信頼度 |
| --- | --- | --- | --- |
| Android 16 `current.txt` で `ACTION_KEY_MISSING` / `ACTION_ENCRYPTION_CHANGE` / encryption extras の `@FlaggedApi` が外れた | API surface の公開状態変更 | 「Android 16 introduces 2 new intents」を API 公開として支持する | High |
| `RemoteDevices.keyMissingCallback()` が Android 16 で `BLUETOOTH_CONNECT` の ordered broadcast を送る | broadcast 受信可能性の拡大 | 通常アプリが `ACTION_KEY_MISSING` を受信できる根拠 | High |
| `RemoteDevices.encryptionChangeCallback()` が Android 16 で flag gate なしに broadcast | changed condition / gate | `ACTION_ENCRYPTION_CHANGE` が encryption change ごとに通知される根拠 | High |
| `btm_sec_report_bond_loss()` が `bta_dm_remote_key_missing()` 後に disconnect | added/consolidated behavior | `ACTION_KEY_MISSING` broadcast 時に ACL link が disconnect される根拠 | High |
| Android 15 LE key missing path に key removal 分岐がある | baseline behavior | `ACTION_KEY_MISSING` が来ない場合は Android 15 と同様に bond information が removed される説明と整合 | Medium |
| targetSdkVersion 36 gate が見つからない | no target SDK gate found | 公式 target page だが primary classification を `TARGET_SDK_36` にしない根拠 | Medium |
| compat framework Change ID が見つからない | no compat change found | force-enable / force-disable で検証する項目ではない | Medium |

## Facts

- 公式文書は、Android 16 が `ACTION_KEY_MISSING` と `ACTION_ENCRYPTION_CHANGE` を導入し、apps targeting Android 16 が受信できると説明している。
- Android 16 all-apps 文書は、remote bond loss 時に system が link を disconnect し、local bond information を保持し、ユーザーに re-pair を促す system dialog を表示すると説明している。
- Android 16 AOSP Bluetooth API surface では、`ACTION_KEY_MISSING` と `ACTION_ENCRYPTION_CHANGE` が flag なし public API として存在する。
- Android 15 AOSP Bluetooth API surface では、同じ action / extras は `@FlaggedApi` 付きである。
- Android 16 `RemoteDevices.keyMissingCallback()` は、bonded device でない場合は return し、bonded device の場合に `ACTION_KEY_MISSING` を送る。
- Android 16 `RemoteDevices.encryptionChangeCallback()` は、`EXTRA_ENCRYPTION_STATUS`、`EXTRA_ENCRYPTION_ENABLED`、`EXTRA_KEY_SIZE`、`EXTRA_ENCRYPTION_ALGORITHM` を付与する。
- Android 16 `btm_sec_report_bond_loss()` は `bta_dm_remote_key_missing()` を呼んだ後、HCI disconnect を送る。
- Android 16 の Bluetooth `ChangeIds.java` にはこの behavior 専用の Change ID はない。
- Android 16 compat framework 公式ページで、`KEY_MISSING` / `ENCRYPTION_CHANGE` / Bluetooth bond loss に一致する compat entry は確認できなかった。

## Observations

- 公式 target apps ページ上の項目だが、実装は targetSdkVersion 36 gate ではなく、Bluetooth module の API surface / flag removal / broadcast permission change として現れている。
- `ACTION_KEY_MISSING` は app-facing signal であり、remote bond loss の唯一の検出手段ではない。公式文書も OEM により broadcast されない場合があると説明している。
- `ACTION_ENCRYPTION_CHANGE` は bond restored 判定の補助 signal として重要で、key missing count reset の実装と整合する。
- `ACTION_KEY_MISSING` が broadcast される path では Android 側の local bond information は保持される設計だが、一部 app/device IOP workaround では `device.removeBond()` が呼ばれる path がある。これは OEM / device / app 相性差の注意点として扱う。

## Hypotheses

- 公式文書の「Apps targeting Android 16 can now receive」は、実行時 targetSdk gate ではなく、API 36 SDK で public constants として正式利用可能になったことをアプリ開発者向けに表現している可能性が高い。
- targetSdkVersion 35 アプリでも、Android 16 上で action string を明示的に使えば broadcast を受ける可能性がある。ただし公式サポートされる移行パスとしては targetSdkVersion / compile SDK 36 で新 API を使う形が期待される。
- OEM implementation variation は、AOSP の security manager path だけでなく、controller / vendor stack / Bluetooth module flag / device-specific workaround により差が出る可能性がある。

## Conclusions

- 主分類は `OS_UPDATE_ALL_APPS`。ただし実影響は Bluetooth bonded device と該当 event handling を持つアプリに限定される。
- targetSdkVersion 36 は broadcast 送信の実行時 gate ではなく、API 36 public API として新 intent / extras を採用するための開発条件として整理する。
- 顧客には「Android 16 へ OS アップデートしただけで Bluetooth stack の bond loss handling は変わる可能性がある」と「targetSdkVersion 36 化により新 intent を正式 API として利用できる」を分けて説明する。
- Bluetooth bonded device を扱うアプリは、`ACTION_KEY_MISSING` と `ACTION_ENCRYPTION_CHANGE` を追加 signal として利用しつつ、受信できない OEM/device に備えて legacy handling を残す必要がある。

## 期待挙動マトリクス

| シナリオ | 期待挙動 |
| --- | --- |
| Android 16 / targetSdkVersion 35 | AOSP 実装上は target gate なし。receiver / permission / event 条件を満たす場合、action string による受信可能性がある。ただし API 36 constants としての正式利用はできない。 |
| Android 16 / targetSdkVersion 36 | API constants を使って `ACTION_KEY_MISSING` / `ACTION_ENCRYPTION_CHANGE` を実装可能。broadcast 受信は Bluetooth event、permission、OEM 実装に依存。 |
| Android 15 / targetSdkVersion 36 | Android 16 Bluetooth stack の behavior はない。Android 15 tag では該当 API は flagged で、broadcast も flags dependent。 |

### 詳細マトリクス

| 条件 | 期待挙動 |
| --- | --- |
| Android 16 / targetSdkVersion 36 / `ACTION_KEY_MISSING` received | primary bond loss signal として扱う。ACL link は system により disconnect され、local bond information は原則保持される。 |
| Android 16 / targetSdkVersion 36 / `ACTION_KEY_MISSING` not received | Android 15 と同様の fallback handling が必要。公式文書では ACL link は残り、bond information は removed とされる。 |
| Android 16 / targetSdkVersion 36 / `ACTION_ENCRYPTION_CHANGE` received / encrypted | encryption success として扱い、過去に key missing 状態だった場合は bond restored とみなす。 |
| Android 16 / targetSdkVersion 36 / `ACTION_ENCRYPTION_CHANGE` received / not encrypted | encryption disabled / failure として扱い、reconnect や re-pair guidance の条件に使う。 |
| Android 16 / targetSdkVersion 36 / encryption algorithm changed | `EXTRA_ENCRYPTION_ALGORITHM` を確認する。AES / E0 / none を想定する。 |
| Android 16 / targetSdkVersion 36 / encryption key size changed | `EXTRA_KEY_SIZE` を確認する。固定 key size 前提の診断・telemetry は更新が必要。 |
| Android 16 / targetSdkVersion 36 / ACL link disconnected / bond retained | `ACTION_KEY_MISSING` path。ユーザーに remote device 側の bond 状態確認と re-pair を案内する。 |
| Android 16 / targetSdkVersion 36 / ACL link retained / bond removed | no `ACTION_KEY_MISSING` / legacy path。`ACTION_BOND_STATE_CHANGED` や connection failure から検出する。 |
| Android 16 / targetSdkVersion 36 / `ACTION_BOND_STATE_CHANGED` only legacy handling | 新 intent を取りこぼすため、ユーザー説明や reconnect 制御が遅れる可能性がある。 |
| Android 16 / targetSdkVersion 36 / OEM broadcasts `ACTION_KEY_MISSING` | AOSP に近い path。新 signal を primary にできる。 |
| Android 16 / targetSdkVersion 36 / OEM does not broadcast `ACTION_KEY_MISSING` | legacy fallback 必須。受信前提の reconnect block は避ける。 |

## 影響対象

- Bluetooth bonded device を管理するアプリ
- paired peripheral と reconnect するアプリ
- `ACTION_BOND_STATE_CHANGED` のみに依存しているアプリ
- disconnect event で bond loss を推定しているアプリ
- device forgetting / re-pairing flow を持つアプリ
- encryption status / algorithm / key size を確認する必要があるアプリ
- OEM ごとの Bluetooth behavior 差に影響を受けるアプリ
- Companion Device Manager / companion device flow と組み合わせるアプリ

## 推奨対応候補

- Android 16 / API 36 対応時に `ACTION_KEY_MISSING` receiver を追加し、remote bond loss の primary signal として扱う。
- `ACTION_ENCRYPTION_CHANGE` receiver を追加し、`EXTRA_ENCRYPTION_STATUS`、`EXTRA_ENCRYPTION_ENABLED`、`EXTRA_KEY_SIZE`、`EXTRA_ENCRYPTION_ALGORITHM` を記録・判定する。
- `ACTION_KEY_MISSING` を受け取った後の自動 reconnect は慎重に扱い、remote device 側で bond が消えている可能性をユーザーに案内する。
- `ACTION_KEY_MISSING` が来ない場合に備え、`ACTION_BOND_STATE_CHANGED`、ACL disconnect、connection failure、app-specific protocol error による legacy bond loss detection を残す。
- OEM / device / Bluetooth chipset ごとに broadcast sequence を検証し、new intent を受け取れない場合も破綻しない UX にする。

## テスト観点

- Android 15 端末上の targetSdkVersion 35
- Android 16 端末上の targetSdkVersion 35
- Android 16 端末上の targetSdkVersion 36
- Android 15 端末上の targetSdkVersion 36 が検証可能な場合の比較
- `ACTION_KEY_MISSING` broadcast 受信有無
- `ACTION_ENCRYPTION_CHANGE` broadcast 受信有無
- encryption status / algorithm / key size extra の内容
- remote bond loss 発生時の ACL link 状態
- remote bond loss 発生時の local bond information 状態
- `ACTION_BOND_STATE_CHANGED` の発火有無と timing
- `ACTION_KEY_MISSING` 後の reconnect behavior
- `ACTION_ENCRYPTION_CHANGE` による bond restored 判定
- device forget / re-pairing flow
- OEM / device / Bluetooth stack implementation differences
- Classic Bluetooth / BLE / bonded peripheral の違い
- foreground / background receiver behavior
- required Bluetooth permissions and receiver registration mode
- runtime fallback behavior when new intents are not received

## Compat framework

- Change ID: 該当なし
- Change name: 該当なし
- Default state: 該当なし
- Toggleable for testing: 公式 compat framework では該当項目を確認できない

根拠:
- Android 16 compat framework 公式ページで `KEY_MISSING` / `ENCRYPTION_CHANGE` / Bluetooth bond loss に一致する項目なし。
- Bluetooth module の `android/app/change-ids/com/android/bluetooth/ChangeIds.java` は `ENFORCE_CONNECT = 211757425L` のみで、この behavior 専用 Change ID はない。

## AOSP source context reviewed

- API surface: `packages/modules/Bluetooth/framework/api/current.txt`
  - Android 15: `@FlaggedApi` 付き。
  - Android 16: flag なし public API。
  - Diff type: changed API exposure.
- App-facing constants: `packages/modules/Bluetooth/framework/java/android/bluetooth/BluetoothDevice.java`
  - Android 16: `ACTION_KEY_MISSING` / `ACTION_ENCRYPTION_CHANGE` と extras の Javadoc / permission annotations を確認。
  - Diff type: changed documentation and removed `@FlaggedApi`.
- Broadcast path: `packages/modules/Bluetooth/android/app/src/com/android/bluetooth/btservice/RemoteDevices.java`
  - Android 16: key missing / encryption change broadcast を確認。
  - Diff type: changed gate / added public receiver path.
- Native security path: `packages/modules/Bluetooth/system/stack/btm/btm_sec.cc`
  - Android 16: `btm_sec_report_bond_loss()` と key missing detection points を確認。
  - Diff type: consolidated added behavior.
- Protected broadcasts: `frameworks/base/core/res/AndroidManifest.xml`
  - Android 16: protected broadcast declarations を確認。
  - Diff type: platform protected broadcast declaration.

## 顧客向け説明

Android 16 では Bluetooth remote device の bond loss と link encryption change をアプリが把握するための intent が正式に利用できるようになります。`ACTION_KEY_MISSING` を受け取った場合は remote bond loss の primary signal として扱い、再接続や再ペアリングを急がず、ユーザーに remote device 側の状態確認を促すのが安全です。

ただし、この変更は targetSdkVersion 36 に上げたことだけで発生するものではありません。AOSP では targetSdk gate は確認できず、Android 16 の Bluetooth stack と device / OEM 実装に依存します。`ACTION_KEY_MISSING` が来ない端末では Android 15 と同様の bond loss handling が必要なため、新 intent と legacy fallback を併用してください。

## Human Decision

最終優先度:
- 未判断

判断:
- Human decision required

確認事項:
- 自社アプリが bonded Bluetooth device / reconnect / re-pairing flow を持つか
- `ACTION_BOND_STATE_CHANGED` のみに依存しているか
- Android 16 device matrix で `ACTION_KEY_MISSING` が受信できるか
- OEM 差分を吸収する fallback UX を用意するか
