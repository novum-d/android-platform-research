# Improved bond loss handling - 1ページ要約（One Page Summary）

## 対象（Target）

Android 16 Behavior Change

From:
- android-15.0.0_r36

To:
- android-16.0.0_r4

Behavior Change:
- Improved bond loss handling

Official documentation:
- https://developer.android.com/about/versions/16/behavior-changes-all#improved-bond-loss-handling

Category:
- Connectivity

## 適用条件（Applicability）

- 主分類（Primary classification）: `OS_UPDATE_ALL_APPS`
- OS アップデート / 全アプリ（OS update / all apps）: Yes / Conditional。Android 16 上で bonded Bluetooth device の remote bond loss / authentication failure が起きる app に影響し得る。
- targetSdkVersion 36 以上: No。targetSdkVersion 36 は必要条件ではない。
- その他の必須条件（Other required conditions）: previously bonded Bluetooth device が再接続時に remote bond loss / key missing / authentication failure になること。
- Compat Change ID: 見つからない。
- Compat default state: N/A
- Confidence: High。Android 15 の BR/EDR incoming pairing path では automatic remove + pairing continuation を確認し、Android 16 では non-encrypted bonded path が bond loss report / disconnect に変わることを確認した。Settings 側の `ACTION_KEY_MISSING` dialog / notification path も確認済み。

## 早見マトリクス（At-a-Glance Matrix）

| シナリオ（Scenario） | 影響（Impact） |
| --- | --- |
| Android 16 / targetSdkVersion 35 | remote bond loss 時の system-managed handling が適用され得る |
| Android 16 / targetSdkVersion 36 | targetSdkVersion 35 と同様。targetSdkVersion 36 固有ではない |
| Android 15 / targetSdkVersion 36 | Android 16 Bluetooth stack 差分はない。targetSdkVersion 36 だけでは同じ挙動にならない |
| remote bond loss on reconnect | link disconnect、local bond retained、system dialog による re-pair 誘導 |
| normal disconnect | 今回の bond loss path ではない |
| local user forget / unpair | local bond removal なので `BOND_NONE` transition が期待される |
| app expects automatic bond removal | Android 16 で互換性リスク |
| app expects automatic re-pairing | Android 16 で user-directed re-pairing へ変わる可能性 |

## 要約（Summary）

Android 16 では、以前ペアリング済みの Bluetooth device が再接続時に認証できない場合、Bluetooth stack は bond loss として link を切断し、local bond information を保持する。公式文書では、system dialog でユーザーに bond loss を知らせ、re-pair へ誘導すると説明されている。

AOSP では、Android 15 の BR/EDR incoming pairing path が bonded device に対して `bta_dm_process_remove_device()` を呼び、その後 pairing request 処理へ進むことを確認した。Android 16 では `btm_sec_report_bond_loss()`、`ACTION_KEY_MISSING`、`EXTRA_BOND_LOSS_REASON`、key missing count、ACL / GATT disconnect reason の auth failure 変換を確認した。Settings には `BluetoothKeyMissingReceiver` / `BluetoothKeyMissingDialog` があり、初回 key missing 時に dialog / notification から device settings へ誘導する。`BondLossTest` は remote が bond を削除した後も対象 device が bonded devices list に残ることを検証している。

## 顧客影響（Customer Impact）

- 影響あり: bonded Bluetooth device を扱い、remote bond loss 後の `BOND_NONE`、automatic bond removal、automatic re-pairing を前提にしているアプリ。
- 影響あり: authentication failure / GATT disconnect / profile disconnect を独自 retry や re-pair UI に接続しているアプリ。
- 影響軽微: Bluetooth bonded device を扱わないアプリ、または system-managed re-pairing UI と auth failure を graceful に扱えるアプリ。

## 影響対象（Who Is Affected）

- Bluetooth Classic device と接続するアプリ。
- BLE / GATT device と接続するアプリ。
- CompanionDeviceManager と Bluetooth device を併用するアプリ。
- wearable / earbuds / health device / IoT / camera / tracker / automotive accessory を扱うアプリ。
- `ACTION_BOND_STATE_CHANGED` / `BOND_NONE` に依存するアプリ。
- connection failure analytics / customer support logs を持つアプリ。

## 対応要否（Required Action）

- 必須確認: Android 16 で remote device 側 bond を削除 / factory reset した状態から再接続し、bond state、disconnect callback、system dialog、app UI を確認する。
- 推奨対応: `BOND_NONE` だけに依存せず、`ACTION_KEY_MISSING`、auth failure、profile / GATT disconnect、user-driven re-pairing を扱う。
- 注意: targetSdkVersion 36 移行時は別項目として `ACTION_KEY_MISSING` / `ACTION_ENCRYPTION_CHANGE` の target-only behavior も確認する。

## テストマトリクス（Test Matrix）

| 端末 OS（Device OS） | targetSdkVersion | 期待挙動（Expected behavior） |
| --- | --- | --- |
| Android 15 | 35 | baseline。remote bond loss 時の従来挙動を記録 |
| Android 16 | 35 | link disconnect、local bond retained、system-managed bond loss handling |
| Android 16 | 36 | targetSdkVersion 35 と同様。新 intent 受信条件は別途確認 |
| Android 15 | 36 | 技術的に検証可能なら比較。Android 16 OS update impact と混同しない |

追加テスト:
- remote device bond deleted / factory reset / key missing
- reconnect authentication failure
- normal disconnect / reconnect
- local user unpair / forget
- Bluetooth Classic / BLE / GATT
- `ACTION_BOND_STATE_CHANGED` / `BOND_BONDED` / `BOND_NONE`
- `ACTION_KEY_MISSING` / `ACTION_ENCRYPTION_CHANGE`
- `createBond()` / `removeBond()`
- system bond loss dialog and app custom re-pair UI
- logcat / dumpsys / bugreport / btsnoop

## 顧客向け説明（Explanation for Customers）

この変更は targetSdkVersion 36 化だけで発生するものではなく、Android 16 OS 上で bonded Bluetooth device の remote bond loss が発生した場合の Bluetooth stack 挙動です。Android 16 では system が local bond を保持し、ユーザーに re-pair を促すため、アプリ側で immediate `BOND_NONE` や automatic re-pairing を前提にした flow は見直しが必要です。

## 根拠（Evidence）

- Official documentation: Android 16 all apps / Connectivity / Improved bond loss handling
- AOSP files:
  - `system/stack/btm/btm_sec.cc`
  - `system/bta/dm/bta_dm_sec.cc`
  - `android/app/jni/com_android_bluetooth_btservice_AdapterService.cpp`
  - `android/app/src/com/android/bluetooth/btservice/RemoteDevices.java`
  - `android/app/src/com/android/bluetooth/btservice/storage/DatabaseManager.java`
  - `android/app/src/com/android/bluetooth/gatt/GattService.java`
  - `framework/java/android/bluetooth/BluetoothDevice.java`
  - `framework/tests/bumble/src/android/bluetooth/pairing/BondLossTest.java`
  - `Settings/AndroidManifest.xml`
  - `Settings/src/com/android/settings/bluetooth/BluetoothKeyMissingReceiver.java`
  - `Settings/src/com/android/settings/bluetooth/BluetoothKeyMissingDialog.java`
  - `Settings/src/com/android/settings/bluetooth/BluetoothKeyMissingDialogFragment.java`
- Diff interpretation:
  - added behavior: `btm_sec_report_bond_loss()`、bond loss reason、key missing count
  - changed behavior: local host disconnect reason を app-facing auth failure に変換
  - UI behavior: `ACTION_KEY_MISSING` から Settings の dialog / notification / toast と device settings 誘導につながる
  - retained behavior: default path で local bond を保持
  - exception: selected IOP workaround では `removeBond()` が呼ばれ得る
- Gate conclusion:
  - Android 16 OS 上、bonded Bluetooth device の remote bond loss 時に targetSdkVersion と無関係に影響し得る。

## 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- Critical / High / Medium / Low

判断（Decision）:
- Explain / Monitor / Ignore / Further investigation required

顧客説明優先度（Customer communication priority）:
- TBD by human

リリース判定（Release readiness decision）:
- TBD by human

## 再検証記録（2026-08-22）

- Android 16 の公式 Behavior Change 一覧と最新通常AOSPタグを再確認した。
- 対応する[主レポート](../../../behavior-changes/all/connectivity/improved-bond-loss-handling.md)で official section、AOSP project / remote / checkout、解決済み commit、比較 command、dirty risk を再検証した。
- 主レポートの分類、confidence、未確認事項を維持し、実機未実施の項目を Observed 済みへ変更していない。
- 全件の結果は[再検証台帳](../../../analysis/REVALIDATION_2026-08-22.md)を参照する。
