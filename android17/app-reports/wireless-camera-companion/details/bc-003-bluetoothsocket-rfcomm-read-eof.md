# BC-003: Consistent BluetoothSocket read() behavior for RFCOMM

## 基本情報（Basic Information）

Behavior Change 文書:
- URL: https://developer.android.com/about/versions/17/behavior-changes-17
- Section: Consistent BluetoothSocket read() behavior for RFCOMM

Original statement:
> targetSdkVersion 37 のアプリでは、RFCOMM-based `BluetoothSocket` の `InputStream.read()` が socket closed / connection dropped 時に `-1` を返す、という趣旨の公式説明。

調査対象 Android バージョン:
- From: android-16.0.0_r4
- To: android-17.0.0_r1

## 対象アプリとの関係（Relevance to Target App）

関連するアプリ機能:
- Bluetooth Classic / RFCOMM / SPP 相当の通信。
- カメラとの制御チャネル、ステータス取得、接続維持。

関連する API / permission / component:
- `BluetoothSocket`
- `InputStream.read()`
- RFCOMM socket

アプリが該当する可能性:
- Unknown / Conditional。Bluetooth Low Energy のみなら直接影響は限定的。Bluetooth Classic / RFCOMM を使う場合は該当。

判断理由:
- カメラ連携アプリが Classic Bluetooth RFCOMM を利用するか未確認。利用している場合、切断処理の read loop に直接影響する。

## 適用条件分類（Applicability Classification）

主分類（Primary classification）:
- TARGET_SDK_37_CONDITIONAL

早見表（At-a-glance impact）:

| 確認項目（Question） | 回答（Answer） | 根拠（Evidence） |
| --- | --- | --- |
| Android 17 に OS アップデートしただけで適用されるか | No | Android 17 / targetSdkVersion 36 では旧挙動。 |
| targetSdkVersion 37 以上が必要か | Yes | Change ID `383671392` が targetSdkVersion 37 で enabled。 |
| 追加の実行時条件があるか | Yes | RFCOMM `BluetoothSocket`、read loop、socket close / disconnect。 |
| Compat Change ID が関係するか | Yes | `MAKE_SOCKET_READ_BEHAVIOR_CONSISTENT`。 |

必要な実行時条件（Required runtime conditions）:
- Android version: Android 17。
- targetSdkVersion: 37 以上。
- Device/form factor: 条件なし。
- Permission/API/component condition: RFCOMM-based `BluetoothSocket`。
- App state/process condition: read 中の local close / remote disconnect / connection drop。

Compat framework:
- Change ID: `383671392`
- Change name: `MAKE_SOCKET_READ_BEHAVIOR_CONSISTENT`
- Default state: `@EnabledSince(targetSdkVersion = Build.VERSION_CODES.CINNAMON_BUN)`
- Toggleable for testing: compat change として確認候補。

## AOSP 調査（AOSP Investigation）

関連ファイル:
- `tmp/aosp-checkouts/Bluetooth/framework/java/android/bluetooth/BluetoothSocket.java`

確認したソース文脈（Source Context Reviewed）:

| ファイル / シンボル（File / symbol） | Android 16 の基準挙動（baseline） | Android 17 の挙動 | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| `BluetoothSocket.java` / read EOF path | EOF 時に `IOException` path | targetSdkVersion 37 以上では `-1` を返す | アプリの read loop が直接呼ぶ API の挙動差分。 |

必須記入項目:
- Entry point / caller: app read loop -> `BluetoothSocket` input stream -> RFCOMM socket。
- Relevant class or service responsibility: Bluetooth socket read / EOF handling。
- Runtime path from app API / system event to changed code: remote disconnect / local close -> `read()` return path。
- Why unrelated code paths were excluded: BLE GATT は RFCOMM `BluetoothSocket` ではないため除外。

差分解釈（Diff Interpretation）:
- Changed condition / gate: targetSdkVersion 37 以上で EOF が `-1`。
- Removed behavior: targetSdkVersion 37 以上では EOF を `IOException` だけで扱う旧挙動から変わる。

適用ゲート根拠（Applicability Gate Evidence）:
- targetSdkVersion gate: targetSdkVersion 37。
- CompatChanges.isChangeEnabled / ChangeId: `383671392`。
- @EnabledAfter / @EnabledSince / default state: targetSdkVersion 37 以上で enabled。
- Gate conclusion: Android 17 / targetSdkVersion 37 / RFCOMM `BluetoothSocket` read loop に適用。

## 事実・観察・仮説・結論（Facts / Observations / Hypotheses / Conclusion）

事実（Facts）:
- Android 17 / targetSdkVersion 37 では RFCOMM read EOF が `-1` を返す。

観察（Observations）:
- `IOException` catch だけで切断処理をしている実装は影響を受ける。

仮説（Hypotheses）:
- 対象アプリが RFCOMM を使う場合、切断時の loop 終了、UI 更新、再接続 trigger が変わる可能性がある。

結論（Conclusion）:
- RFCOMM 利用有無と read loop 実装を確認する。該当する場合は対応必須候補。

## アプリ影響（App Impact）

想定される影響:
- 切断時に read loop が終了しない、または disconnect UI に遷移しない可能性。

ユーザー影響:
- カメラ切断後も接続中表示が残る、再接続できない、転送中 UI が止まる可能性。

開発者影響:
- `bytesRead == -1` を EOF / disconnect として処理する修正が必要。

既存実装で確認すべき点:
- `BluetoothSocket.getInputStream().read()` の戻り値 check。
- `IOException` catch だけで終了していないか。

推奨対応候補:
- `-1` handling を追加する。
- remote disconnect、local close、Bluetooth off、range out をテストする。

## Confidence

Confidence:
- High

Confidence の根拠:
- Bluetooth module の Change ID、targetSdkVersion gate、EOF handling を確認済み。

不足している根拠:
- 対象アプリが RFCOMM を使うか未確認。

---
