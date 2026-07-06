# Improved bond loss handling 調査レポート

## 基本情報（Metadata）

### 調査対象 Android バージョン（Android Versions）

From:
- android-15.0.0_r36

To:
- android-16.0.0_r4

Note:
- `android16/AGENTS.md` は To tag を `android-16.0.0_r1` としているが、本調査では依頼スコープに従い公開済み Android 16 tag として `android-16.0.0_r4` を使用した。
- AOSP checkout `frameworks-base`、`tmp/aosp-checkouts/Bluetooth`、`tmp/aosp-checkouts/Settings` は clean で、`android-15.0.0_r36` / `android-16.0.0_r4` tag の存在を確認した。

Previous targetSdkVersion:
- 35

Target targetSdkVersion:
- 36

### Behavior Change 文書（Behavior Change Source）

Document:
- https://developer.android.com/about/versions/16/behavior-changes-all#improved-bond-loss-handling

Page:
- Behavior changes: all apps

Category:
- Connectivity

Section:
- Improved bond loss handling

### 分類スナップショット（Classification Snapshot）

主分類（Primary classification）:
- `OS_UPDATE_ALL_APPS`

早見表（At-a-glance impact）:

| 確認項目（Question） | 回答（Answer） | 根拠（Evidence） |
| --- | --- | --- |
| Android 16 に OS アップデートしただけで適用されるか | Yes / Conditional | 公式 all apps ページ掲載。AOSP Bluetooth stack の remote bond loss / key missing path で Android 16 runtime behavior を確認した。影響は bonded Bluetooth device の remote bond loss / authentication failure 時に限られる。 |
| targetSdkVersion 36 以上が必要か | No | Bluetooth stack / Java service / JNI / native stack の確認範囲で targetSdkVersion 36 gate は見つからない。 |
| 追加の実行時条件があるか | Yes | previously bonded Bluetooth device が reconnection 時に remote bond loss / key missing / authentication failure になること。 |
| Compat Change ID が関係するか | No / Not found | Android 16 compat framework changes page で bond loss / key missing / Bluetooth 関連の該当 compat change は見つからない。AOSP confirmed path でも compat gate は見つからない。 |

### 調査日（Investigation Date）

2026-07-06

### 信頼度（Confidence）

- High

理由:
- 公式文書は Android 16 all apps / Connectivity section として、targetSdkVersion に関係なく Android 16 上の Bluetooth stack の挙動変更を説明している。
- AOSP Bluetooth module では、Android 16 で `btm_sec_report_bond_loss()` による remote bond loss の統一処理、link disconnect、`ACTION_KEY_MISSING` 送出、key missing count 記録、GATT / ACL disconnect reason の `HCI_ERR_AUTH_FAILURE` 変換、bonded device list に残ることを検証する `BondLossTest` を確認した。
- AOSP Settings では、`ACTION_KEY_MISSING` を受ける `BluetoothKeyMissingReceiver`、`BluetoothKeyMissingDialog`、`BluetoothKeyMissingDialogFragment` を確認した。Android 16 r4 では初回 key missing 時に dialog / notification を出し、device details へ誘導する path がある。
- targetSdkVersion gate / compat framework gate は確認できない。
- Android 15 baseline の bonded incoming pairing path では、`btm_io_capabilities_req()` が bonded device を検出して `bta_dm_process_remove_device()` を呼び、その後 `btm_find_or_alloc_dev()` から pairing request 処理へ進む経路を確認した。Android 16 r4 では同じ非 encrypted bonded device path が `btm_sec_report_bond_loss(... BREDR_INCOMING_PAIRING)` に変わり、pairing request を reject して bond loss として通知・切断する。
- Android 15 Settings dialog では positive button が `removeBond()` を直接呼ぶ一方、Android 16 r4 Settings dialog は device settings へ誘導する。native stack と Settings UI の両方で、Android 16 が automatic removal ではなく user-guided handling に寄っていることを確認した。

### 適用条件分類（Applicability Classification）

適用される条件（Applies when）:
- [x] OS update / all apps on Android 16 regardless of targetSdkVersion
- [ ] targetSdkVersion >= 36 on Android 16+
- [ ] targetSdkVersion >= 36, with additional runtime conditions
- [ ] Mainline / Google Play system update dependent
- [ ] API addition only, not a behavior change
- [ ] Unknown / needs more evidence

必要な実行時条件（Required runtime conditions）:
- Android version: Android 16
- targetSdkVersion: 条件なし。targetSdkVersion 35 / 36 の両方が影響対象になり得る。
- Device/API condition: previously bonded Bluetooth device を扱うこと。
- Runtime condition: remote device 側の bond reset / key loss / factory reset 等により、reconnection 時に Android 側が認証できないこと。
- Transport/profile condition: AOSP evidence では BR/EDR と LE encryption failure の両方に key missing path がある。アプリ観点では Bluetooth Classic、BLE / GATT、profile 接続、CompanionDeviceManager 併用 device が確認対象。

Compat framework:
- Change ID: 見つからない。
- Change name: N/A
- Default state: N/A
- Toggleable for testing: N/A

分類信頼度（Classification confidence）:
- High

分類根拠（Classification evidence）:
- Official documentation page: `behavior-changes-all` の Connectivity section。
- Original applicability statement: Android 16 の Bluetooth stack 変更として説明されている。
- AOSP targetSdk gate: 見つからない。
- Compat framework entry: 見つからない。

---

# エグゼクティブサマリー（Executive Summary）

Android 16 では、以前ペアリング済みの Bluetooth device が再接続時に認証できない場合、Bluetooth stack は remote bond loss として扱い、link を切断し、local bond information を保持する。アプリが従来のように「remote bond loss 直後に `BOND_NONE` へ落ちる」「system が自動で再ペアリングを開始する」と仮定している場合、retry、re-pairing UI、analytics、support log の挙動がずれる可能性がある。

Android 16 AOSP では、native stack に `btm_sec_report_bond_loss()` が追加され、BR/EDR authentication failure、BR/EDR incoming pairing、LE encryption failure、LE incoming pairing の key missing reason を Java 層へ渡す。Java 層では `ACTION_KEY_MISSING` を送出し、key missing count を bonded device metadata に記録する。Bumble test では remote が bond を削除した後、Android が `ACTION_KEY_MISSING` と ACL disconnect を受け、対象 device が bonded devices に残ることを検証している。

この変更は targetSdkVersion 36 化だけの影響ではない。Android 16 OS 上で bonded Bluetooth device の remote bond loss が起きる場合に、targetSdkVersion 35 / 36 の両方で影響し得る。

---

# 公式ドキュメント確認（Original Documentation）

## 原文（Statement）

公式文書は以下を説明している。

- Starting in Android 16, Bluetooth stack は remote bond loss 検出時の security と user experience を改善する。
- 以前は system が bond を自動削除し、新しい pairing process を開始することがあり、unintentional re-pairing につながり得た。
- 多くのケースで app が bond loss event を一貫して扱っていなかった。
- Android 16 は bond loss handling を system 側に改善・統一する。
- previously bonded Bluetooth device が再接続時に認証できない場合、system は link を切断し、local bond information を保持し、bond loss を通知して re-pair を促す system dialog を表示する。

## 公式文書との差分確認

- requested anchor `#improved-bond-loss-handling` は現在の公式 HTML 上で確認できた。
- 公式文書の該当 section は 2026-06-24 UTC 更新の Android 16 all apps ページに存在する。
- 依頼の Original statements は現在の公式本文と一致する。

## 解釈（Interpretation）

この Behavior Change は、remote device 側で bond が失われたときに Android が自動で local bond を削除して再ペアリングへ進むのではなく、system が bond loss を検出・通知し、user-driven な再ペアリングへ誘導する変更である。

API surface 上は Android 16 target-only ページに「New intents to handle bond loss and encryption changes」があり、`ACTION_KEY_MISSING` / `ACTION_ENCRYPTION_CHANGE` の受信は targetSdkVersion 36 の関連項目として扱われている。ただし、本 report の対象は all-apps ページの runtime behavior であり、target-only の新 intent 受信要件とは分けて扱う。

---

# 変更内容（What Changed）

## 変更点

- Android 15 baseline:
  - BR/EDR / LE の key missing path で `bta_dm_remote_key_missing(...)` と link disconnect が行われる箇所は存在する。
  - `ACTION_KEY_MISSING` は flag 条件や permission 条件つきで扱われ、reason extra や key missing count はない。
  - `btm_io_capabilities_req()` は bonded device の incoming pairing request を受けると `bta_dm_process_remove_device(...)` を呼び、その後 `btm_find_or_alloc_dev()` 以降の pairing request 処理へ進む。これは公式文書の「previously, the system would automatically remove the bond and initiate a new pairing process」に対応する baseline evidence。
  - Settings `BluetoothKeyMissingDialogFragment` は positive button で `BluetoothDevice#removeBond()` を直接呼ぶ。
- Android 16 target:
  - native stack に `btm_sec_report_bond_loss(...)` が追加され、remote bond loss detection を理由コードつきで集約する。
  - `btm_sec_report_bond_loss(...)` は `bta_dm_remote_key_missing(...)` を呼び、link が残っていれば `HCI_ERR_AUTH_FAILURE` で disconnect する。
  - Java 層 `RemoteDevices#keyMissingCallback(...)` は bonded device のみを対象に `ACTION_KEY_MISSING` を ordered broadcast し、`EXTRA_BOND_LOSS_REASON` を追加できる。
  - `DatabaseManager` は bonded device metadata に `key_missing_count` を保持し、bond loss 検出で increment、successful encrypted connection で reset する。
  - ACL / GATT disconnect callback は key missing count がある場合、native の local host disconnect reason を app には auth failure として見せる。
  - Settings は `ACTION_KEY_MISSING` を受け、foreground / interactive 条件と key missing count に応じて system dialog、notification、toast を出す。Android 16 r4 の dialog は positive button で device settings へ誘導し、device details 側で re-pair / forget を判断する flow に寄せている。
  - default path では local bond を保持する。例外として、AOSP には特定 package / device name 向けの temporary IOP workaround があり、その場合だけ `removeBond()` が呼ばれ得る。
  - `BondLossTest` は BR/EDR remote bond loss 後に `ACTION_KEY_MISSING`、ACL disconnect、bonded devices list に device が残ることを検証している。

## 適用条件（Applicability）

### OS アップデート時の挙動（OS Update Behavior）

- Android 16 に OS アップデートしただけで適用されるか: Yes / Conditional。
- targetSdkVersion に依存しない根拠: AOSP confirmed path に targetSdkVersion 36 gate は見つからない。公式文書も all apps ページ。
- Android 15 以前での挙動: Android 15 baseline では key missing path はあるが、Android 16 の `btm_sec_report_bond_loss()`、bond loss reason、key missing count、default retained-bond test は確認できない。

### targetSdkVersion 36 以上での挙動（targetSdkVersion 36 Behavior）

- targetSdkVersion 36 以上で適用されるか: targetSdkVersion 36 は必要条件ではない。
- Android 16 / targetSdkVersion 35: remote bond loss 時の system-managed handling の対象になり得る。
- Android 16 / targetSdkVersion 36: targetSdkVersion 35 と同様に対象になり得る。
- Android 15 / targetSdkVersion 36: Android 16 の Bluetooth stack 差分は OS 側にないため、この all-apps behavior と同じ挙動になる根拠はない。

### その他の条件（Other Conditions）

- Bluetooth Classic: BR/EDR auth failure / incoming pairing path に `btm_sec_report_bond_loss()` がある。
- BLE / GATT: LE encryption failure path に `btm_sec_report_bond_loss()` があり、GATT app callback は auth failure に変換され得る。
- Local unpair / forget device: user または app / privileged path が local bond を削除する場合は別挙動であり、remote bond loss ではない。
- Normal disconnect: authentication failure / key missing がない通常 disconnect は今回の retained bond / bond loss dialog path とは別。
- App-facing broadcast: Android 16 target-only documentation によると `ACTION_KEY_MISSING` / `ACTION_ENCRYPTION_CHANGE` の受信は targetSdkVersion 36 関連項目として扱われる。all-apps behavior の存在と、app が新 intent を受けられる条件は分けて検証する必要がある。

---

# AOSP 調査（AOSP Investigation）

## 関連ファイル（Related Files）

- `tmp/aosp-checkouts/Bluetooth/system/stack/btm/btm_sec.cc`
- `tmp/aosp-checkouts/Bluetooth/system/bta/dm/bta_dm_sec.cc`
- `tmp/aosp-checkouts/Bluetooth/system/btif/src/bluetooth.cc`
- `tmp/aosp-checkouts/Bluetooth/android/app/jni/com_android_bluetooth_btservice_AdapterService.cpp`
- `tmp/aosp-checkouts/Bluetooth/android/app/src/com/android/bluetooth/btservice/RemoteDevices.java`
- `tmp/aosp-checkouts/Bluetooth/android/app/src/com/android/bluetooth/btservice/AdapterService.java`
- `tmp/aosp-checkouts/Bluetooth/android/app/src/com/android/bluetooth/btservice/storage/DatabaseManager.java`
- `tmp/aosp-checkouts/Bluetooth/android/app/src/com/android/bluetooth/gatt/GattService.java`
- `tmp/aosp-checkouts/Bluetooth/framework/java/android/bluetooth/BluetoothDevice.java`
- `tmp/aosp-checkouts/Bluetooth/framework/api/current.txt`
- `tmp/aosp-checkouts/Bluetooth/framework/tests/bumble/src/android/bluetooth/pairing/BondLossTest.java`
- `tmp/aosp-checkouts/Settings/AndroidManifest.xml`
- `tmp/aosp-checkouts/Settings/src/com/android/settings/bluetooth/BluetoothKeyMissingReceiver.java`
- `tmp/aosp-checkouts/Settings/src/com/android/settings/bluetooth/BluetoothKeyMissingDialog.java`
- `tmp/aosp-checkouts/Settings/src/com/android/settings/bluetooth/BluetoothKeyMissingDialogFragment.java`
- `tmp/aosp-checkouts/Settings/res/layout/bluetooth_key_missing.xml`
- `tmp/aosp-checkouts/Settings/res/values/strings.xml`

## 確認したソース文脈（Source Context Reviewed）

| ファイル / シンボル（File / symbol） | Android 15 の基準挙動（baseline） | Android 16 の挙動 | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| `btm_sec.cc` / BR/EDR incoming pairing | bonded device の incoming pairing request で `bta_dm_process_remove_device()` を呼び、その後 pairing request 処理へ進む path がある。bonded かつ非 encrypted の場合は flag 条件で key missing 通知 / disconnect path がある。 | bonded かつ非 encrypted なら pairing request を reject し、`btm_sec_report_bond_loss(... BREDR_INCOMING_PAIRING)` に集約し、key missing event と disconnect を行う。 | remote bond loss / incoming pairing 検出、および以前の automatic remove + pairing continuation から Android 16 の bond loss handling への差分根拠。 |
| `btm_sec.cc` / auth complete `HCI_ERR_KEY_MISSING` | flag 条件つきで `bta_dm_remote_key_missing(...)` と disconnect。 | `btm_sec_report_bond_loss(... BREDR_AUTH_FAILURE)` に集約。 | previously bonded device が reconnection auth failure になる中心 path。 |
| `btm_sec.cc` / LE encryption failure | `HCI_ERR_KEY_MISSING` で key missing 通知し、flag 条件で disconnect。 | `btm_sec_report_bond_loss(... LE_ENCRYPT_FAILURE)` に集約し、disconnect。 | BLE / GATT device への影響根拠。 |
| `bta_dm_sec.cc#bta_dm_remote_key_missing` | `bd_addr` のみを event に載せる。 | `bd_addr` と `reason` を event に載せる。 | native から Java callback へ bond loss reason を伝える根拠。 |
| `AdapterService.cpp#key_missing_callback` | address のみを Java callback に渡す。 | address と reason を Java callback に渡す。 | JNI 境界の差分根拠。 |
| `RemoteDevices#keyMissingCallback` | `ACTION_KEY_MISSING` を送る。reason extra / count / retained bond tracking はない。 | bonded device のみを対象に `ACTION_KEY_MISSING` を ordered broadcast し、`EXTRA_BOND_LOSS_REASON` と key missing count を扱う。 | app-facing signal と local bond retained state tracking の Java layer 根拠。 |
| `RemoteDevices#keyMissingCallback` IOP workaround | 該当なし。 | 特定 package / device name で `device.removeBond()` する temporary workaround がある。 | Android 16 でも例外的に local bond が削除され得る条件。 |
| `DatabaseManager#updateKeyMissingCount` | 該当なし。 | bonded device metadata に key missing count を保存し、成功時に reset。 | local bond information を保持したまま bond loss state を追跡する根拠。 |
| `RemoteDevices#aclStateChangeCallback` | local host disconnect reason を auth failure に変換する key missing count 条件はない。 | key missing count がある場合、app callback へ `HCI_ERR_AUTH_FAILURE` 相当を通知。 | app-managed reconnect / retry behavior への影響根拠。 |
| `GattService#onDisconnected` | key missing count による disconnect status 変換はない。 | key missing count がある場合、GATT callback へ auth failure status を返す。 | BLE / GATT app への影響根拠。 |
| `BluetoothDevice.java` / API surface | `ACTION_KEY_MISSING` は Android 15 に存在するが flagged / permission 条件が異なる。 | `EXTRA_BOND_LOSS_REASON` と `BOND_LOSS_REASON_*`、`getKeyMissingCount()` が追加される。 | API surface 追加と runtime behavior の関係整理。 |
| `BondLossTest` | 該当 test は Android 15 baseline にない。 | remote が bond を削除した後、Android が `ACTION_KEY_MISSING` と disconnect を受け、bonded device list に残ることを検証。 | retained local bond behavior の最も直接的な test evidence。 |
| Settings `BluetoothKeyMissingReceiver` / `BluetoothKeyMissingDialog` | `ACTION_KEY_MISSING` receiver / dialog は存在し、dialog の positive button は `removeBond()` を直接呼ぶ。 | `ACTION_KEY_MISSING` 受信後、first key-missing なら foreground dialog または notification を出す。dialog は device details へ誘導し、2 回目以降は toast へ変える。 | 公式文書の system dialog / re-pair guidance の UI path 根拠。 |
| Settings strings / layout | title は device not connected、message は forget then pair again。 | title は can not connect、message は device settings への誘導。device details 用の key missing guidance string も追加。 | Android 16 で user-guided handling へ寄せた UI 差分の根拠。 |

必須記入項目（Required context）:
- Entry point / caller: Bluetooth controller / remote device reconnect -> native security manager `btm_sec.cc` -> BTA / BTIF callback -> JNI `AdapterService.cpp` -> Java `RemoteDevices#keyMissingCallback` -> app-facing broadcast / callbacks。
- Relevant class or service responsibility: native stack は key missing / authentication failure / encryption failure を検出し、Java Bluetooth service は broadcast、metadata、disconnect callback reason を app-facing signal に変換する。
- Runtime path from app API / system event to changed code: app が bonded device へ connect / GATT connect / profile connect する、または remote が再接続する。remote 側で bond が失われていると authentication / encryption が失敗し、Android 16 stack が bond loss として disconnect し、local bond を保持する。
- Why unrelated code paths were excluded: local user unpair、normal disconnect、initial pairing、temporary pairing、PBAP specific re-pair notification、CompanionDeviceManager association creation は remote bond loss handling の中心挙動ではないため、補助情報としてのみ扱った。

## 差分解釈（Diff Interpretation）

| 確認した差分（Observed diff） | 解釈（Interpretation） | Behavior Change との関係 | 信頼度（Confidence） |
| --- | --- | --- | --- |
| `btm_sec_report_bond_loss()` 追加 | BR/EDR / LE の remote bond loss handling を native stack に集約。 | 公式文書の「improved the bond loss handling to the system」に対応。 | High |
| `bta_dm_remote_key_missing` / JNI callback が reason を受け渡す | bond loss reason を Java 層へ伝える added behavior。 | Android 16 で system / app-facing signal が具体化された根拠。 | High |
| `RemoteDevices#keyMissingCallback` が `EXTRA_BOND_LOSS_REASON` と key missing count を扱う | local bond を削除せず、bond loss state を bonded metadata として追跡する。 | 公式文書の「retain local bond information」に対応。 | High |
| `BondLossTest` が bonded devices list に残ることを assert | remote bond loss 後も local bond が保持されることを test で確認。 | retained local bond behavior の直接根拠。 | High |
| `RemoteDevices` / `GattService` が disconnect reason を auth failure に変換 | app callback では authentication failure として見える可能性が高い。 | app retry / analytics / failure handling への影響根拠。 | High |
| `device.removeBond()` が IOP workaround に限定される | Android 16 でも特定 app / device 例外はあるが general path ではない。 | 「常に retained」と断定しないための例外条件。 | High |
| Settings に `BluetoothKeyMissingReceiver` / `BluetoothKeyMissingDialog` が存在 | Bluetooth module の `ACTION_KEY_MISSING` を Settings が受け、dialog / notification / toast を出す。Android 16 r4 では device details へ誘導する。 | 公式文書の system dialog / user-directed re-pair guidance に対応。 | High |
| targetSdkVersion / compat gate が見つからない | OS update all-apps behavior として解釈。 | classification を `OS_UPDATE_ALL_APPS` とする根拠。 | High |

---

# Facts / Observations / Hypotheses / Conclusions

## Facts

- 公式文書は Android 16 all apps page の Connectivity section にこの項目を掲載している。
- 公式文書は remote bond loss 検出時に link disconnect、local bond information retention、system dialog による re-pair 誘導を説明している。
- Android 16 AOSP Bluetooth stack には `btm_sec_report_bond_loss()` が存在し、BR/EDR auth failure、BR/EDR incoming pairing、LE encryption failure、LE incoming pairing を key missing reason として扱う。
- Android 16 `RemoteDevices#keyMissingCallback()` は bonded device に対して `ACTION_KEY_MISSING` を ordered broadcast し、key missing count を increment する。
- Android 16 Settings `BluetoothKeyMissingReceiver` は `ACTION_KEY_MISSING` を受け、`enableBluetoothKeyMissingDialog` flag が有効な場合に key missing dialog / notification / toast を出す。
- Android 16 `BondLossTest` は remote が bond を削除した後、Android が `ACTION_KEY_MISSING` と ACL disconnect を受け、対象 device が bonded devices list に残ることを検証している。
- targetSdkVersion 36 gate と compat framework Change ID は確認できない。

## Observations

- Android 15 にも key missing notification / disconnect path はあるが、Android 16 は reason、count、test coverage、app-facing auth failure conversion を追加し、system-managed handling として整理している。
- Android 15 の BR/EDR incoming pairing path には bonded device の自動 remove と pairing continuation がある。一方 Android 16 の非 encrypted bonded path は pairing request を reject して bond loss として扱う。
- Android 16 でも temporary IOP workaround として特定 package / device name に対して `removeBond()` が呼ばれる可能性がある。
- target-only ページには `ACTION_KEY_MISSING` / `ACTION_ENCRYPTION_CHANGE` の新 intent 受信に関する説明があるため、all-apps runtime behavior と app が新 intent を受ける条件は混同しない。
- Android 15 Settings の key-missing dialog は positive button で `removeBond()` を直接呼ぶが、Android 16 r4 の dialog は device details へ誘導する。これにより、Android 16 の「local bond を保持してユーザーに状況を説明する」方向と整合する。

## Hypotheses

- OEM 実装差により、`ACTION_KEY_MISSING` の broadcast 有無や user-facing dialog 表示にはばらつきがあり得る。公式 target-only ページも OEM 実装差に注意を促している。
- `ACTION_BOND_STATE_CHANGED` / `BOND_NONE` に依存する legacy app は、Android 16 default path では remote bond loss を即座に検出できない可能性がある。

## Conclusions

- この Behavior Change の primary classification は `OS_UPDATE_ALL_APPS`。
- targetSdkVersion 36 化そのものではなく、Android 16 OS 上の Bluetooth stack behavior が主因である。
- bonded Bluetooth device を扱う app は、remote bond loss 時に automatic bond removal / automatic re-pairing / immediate `BOND_NONE` を前提にしない設計へ見直す必要がある。
- app の re-pair flow は、system-managed dialog と競合しないよう、authentication failure、`ACTION_KEY_MISSING`、disconnect callback、manual `removeBond()` / `createBond()` の順序を Android 16 実機で確認する必要がある。

---

# 期待挙動マトリクス（Required Behavior Matrix）

| OS / targetSdkVersion | 期待挙動（Expected behavior） |
| --- | --- |
| Android 16 / targetSdkVersion 35 | remote bond loss 時、Android 16 Bluetooth stack の system-managed handling が適用され得る。targetSdkVersion 36 は不要。 |
| Android 16 / targetSdkVersion 36 | targetSdkVersion 35 と同様。追加で target-only の `ACTION_KEY_MISSING` / `ACTION_ENCRYPTION_CHANGE` 受信条件は別途確認対象。 |
| Android 15 / targetSdkVersion 36 | Android 16 の `btm_sec_report_bond_loss()` / retained-bond test path はない。targetSdkVersion 36 だけで同じ behavior になる根拠はない。 |

## 詳細マトリクス

| シナリオ（Scenario） | 期待影響（Expected impact） |
| --- | --- |
| Android 16 / targetSdkVersion 35 / previously bonded Bluetooth device | remote bond loss が起きると system-managed handling の対象になり得る。 |
| Android 16 / targetSdkVersion 36 / previously bonded Bluetooth device | targetSdkVersion 35 と同様。 |
| Android 16 / targetSdkVersion 35 / remote bond loss on reconnect | link disconnect、local bond retained、system dialog 表示が期待される。 |
| Android 16 / targetSdkVersion 36 / remote bond loss on reconnect | targetSdkVersion 35 と同様。 |
| Android 16 / authentication failure on reconnection | key missing count がある場合、ACL / GATT callback で auth failure として見える。 |
| Android 16 / normal disconnect without bond loss | 今回の bond loss retained-bond path ではない。 |
| Android 16 / local user forgets / unpairs device | local bond removal なので `BOND_NONE` transition が期待される。remote bond loss とは別。 |
| Android 16 / system disconnects link | `btm_sec_report_bond_loss()` は link が有効なら `HCI_ERR_AUTH_FAILURE` で disconnect する。 |
| Android 16 / local bond information retained | default path では bonded device list に残る。`BondLossTest` が検証している。 |
| Android 16 / system dialog displayed | Settings `BluetoothKeyMissingReceiver` / `BluetoothKeyMissingDialog` が `ACTION_KEY_MISSING` から dialog / notification / toast を出す。 |
| Android 16 / user follows dialog to re-pair | app 独自 flow と重複しないか確認が必要。 |
| Android 16 / app expects automatic bond removal | `BOND_NONE` を即時前提にすると誤判定の可能性。 |
| Android 16 / app expects automatic pairing process | system-managed user-directed re-pairing へ変わるため確認が必要。 |
| Android 16 / app listens to ACTION_BOND_STATE_CHANGED | remote bond loss 直後に `BOND_NONE` が来ない可能性がある。 |
| Android 16 / app receives BOND_NONE | local unpair、manual `removeBond()`、IOP workaround など限定条件で発生し得る。 |
| Android 16 / app does not receive BOND_NONE because local bond is retained | default retained-bond path ではこの想定が妥当。 |
| Android 16 / app calls createBond() after dialog | user-driven re-pairing flow として確認対象。 |
| Android 16 / app calls removeBond() manually | local unpair path として `BOND_NONE` transition を確認。 |
| Android 16 / Bluetooth Classic device | BR/EDR auth failure / incoming pairing path で対象。 |
| Android 16 / BLE / GATT device | LE encryption failure path と GATT disconnect auth failure conversion が対象。 |
| Android 16 / HID / audio profile device | profile-specific retry / reconnect と system-managed bond loss dialog の相互作用を確認。 |
| Android 16 / CompanionDeviceManager-managed Bluetooth device | CDM association と Bluetooth bond state の両方を確認。 |
| Android 15 / targetSdkVersion 35 / remote bond loss behavior | Android 15 baseline として比較。Android 16 retained-bond path と混同しない。 |
| Android 15 / targetSdkVersion 36 / same app behavior if technically comparable | targetSdkVersion 36 だけでは Android 16 stack behavior は入らない。 |
| app updates retry / re-pair flow for system-managed bond loss dialog | 推奨。system UI と競合しない retry / re-pair 導線へ調整。 |
| app continues relying on automatic bond removal / automatic re-pairing | Android 16 で互換性リスク。 |

---

# 影響対象（Affected Apps）

- bonded Bluetooth device を扱うアプリ。
- Bluetooth Classic device と接続するアプリ。
- BLE / GATT device と接続するアプリ。
- CompanionDeviceManager と Bluetooth device を併用するアプリ。
- wearable / earbuds / health device / IoT / camera / tracker / automotive accessory を扱うアプリ。
- remote device 側の bond reset / factory reset / key loss が発生し得るアプリ。
- `ACTION_BOND_STATE_CHANGED` / `BOND_NONE` に依存するアプリ。
- authentication failure を独自 UI / retry / re-pair flow で扱うアプリ。
- automatic bond removal / automatic re-pairing を前提にしているアプリ。
- connection failure analytics / customer support logs を持つアプリ。
- Bluetooth permission / nearby devices permission / location privacy の影響に敏感なアプリ。

## 影響が低いケース（Lower-impact / non-impact cases）

- Bluetooth bonded device を使わないアプリ。
- scan only / unbonded connection のみを使うアプリ。
- remote bond loss 時に system-managed re-pairing UI を許容できるアプリ。
- automatic bond removal を前提にしないアプリ。
- authentication failure と user-driven re-pairing を graceful に扱えるアプリ。
- Android 15 以前のみで動くアプリ。ただし Android 16 へ OS update される可能性がある device は確認対象。

---

# 推奨対応候補（Recommended Action Candidates）

- remote bond loss を `BOND_NONE` だけで検出しない。`ACTION_KEY_MISSING`、authentication failure、GATT disconnect status、profile disconnect、connection retry failure を組み合わせて扱う。
- Android 16 では system dialog が表示され得るため、app 独自 re-pair UI を即時表示して二重 dialog にしない。
- retry loop は aggressive にしない。key missing / auth failure 後は backoff し、ユーザーに remote device の状態確認と re-pair を促す。
- analytics / support log は `BOND_NONE`、auth failure、key missing、manual removeBond、system dialog dismissal を分けて記録する。
- targetSdkVersion 36 へ移行する場合は、target-only の `ACTION_KEY_MISSING` / `ACTION_ENCRYPTION_CHANGE` 項目も別途確認する。
- Bluetooth Classic と BLE / GATT の両方を扱うアプリは transport ごとに再接続・再ペアリング動線を検証する。

---

# テスト観点（Test Plan）

必須比較:
- Android 15 端末上の targetSdkVersion 35。
- Android 16 端末上の targetSdkVersion 35。
- Android 16 端末上の targetSdkVersion 36。
- Android 15 端末上の targetSdkVersion 36 が検証可能な場合の比較。

機能テスト:
- previously bonded device。
- remote device bond deleted / factory reset / key missing。
- reconnect authentication failure。
- normal disconnect / reconnect。
- local user unpair / forget。
- Bluetooth Classic pairing。
- BLE / GATT bonding。
- CompanionDeviceManager-managed pairing, if applicable。
- `ACTION_BOND_STATE_CHANGED` broadcast。
- `BOND_BONDED` / `BOND_NONE` state transitions。
- `ACTION_KEY_MISSING` / `ACTION_ENCRYPTION_CHANGE` 受信可否。
- `createBond()` / `removeBond()`。
- system bond loss dialog display。
- user re-pair flow from dialog。
- app custom re-pair UI interaction with system dialog。
- automatic retry / backoff behavior。
- connection failure / pairing failure analytics。
- logcat / `dumpsys bluetooth_manager` / `dumpsys bluetooth_manager --proto` / bugreport。
- Bluetooth module logs / btsnoop if available。
- user-visible failure / silent failure / duplicate dialogs。
- regression testing for pairing success, bond loss, re-pairing, and normal reconnect。

観察すべき結果:
- Android 16 default path で local bond が retained されるか。
- `BOND_NONE` が remote bond loss 直後に出ないか。
- GATT / profile callback が auth failure として見えるか。
- system dialog と app UI が競合しないか。
- OEM device で `ACTION_KEY_MISSING` broadcast / dialog 表示に差がないか。

---

# Evidence Gaps / Limitations

- Android 15 baseline の automatic remove + pairing continuation は BR/EDR incoming pairing path で確認した。LE / GATT では key missing notification / disconnect path は確認したが、同じ automatic remove + pairing continuation としては扱わない。
- OEM Bluetooth UI / Settings / Pixel-specific implementation は AOSP Bluetooth module / AOSP Settings と異なる可能性がある。

---

# 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- Critical / High / Medium / Low

判断（Decision）:
- Explain / Monitor / Ignore / Further investigation required

顧客説明優先度（Customer communication priority）:
- TBD by human

リリース判定（Release readiness decision）:
- TBD by human
