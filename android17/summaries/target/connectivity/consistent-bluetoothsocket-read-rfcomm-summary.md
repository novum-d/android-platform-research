# RFCOMM における BluetoothSocket read() 挙動の一貫化 - 1ページ要約

## 対象

Android 17 Behavior Change

比較元:
- android-16.0.0_r4

比較先:
- android-17.0.0_r1

以前の targetSdkVersion:
- 36

対象 targetSdkVersion:
- 37

## 適用条件

- 主分類（Primary classification）: TARGET_SDK_37_CONDITIONAL
- OS アップデート / 全アプリ: 非該当。AOSP gate は targetSdkVersion 37 以上で有効。
- targetSdkVersion 37 以上: 該当。`BluetoothSocket.read()` の EOF 戻り値が `-1` になる。
- その他の必須条件: RFCOMM-based `BluetoothSocket`、`InputStream.read()`、socket closed / connection dropped、read loop 実装。
- Compat Change ID: `383671392` (`MAKE_SOCKET_READ_BEHAVIOR_CONSISTENT`)
- Compat default state: `@EnabledSince(targetSdkVersion = Build.VERSION_CODES.CINNAMON_BUN)`
- Confidence: High

## 早見マトリクス

| シナリオ | 影響 |
| --- | --- |
| Android 17 / targetSdkVersion 36 | 旧挙動。RFCOMM `read()` の EOF で `IOException` path が維持される。 |
| Android 17 / targetSdkVersion 37 | RFCOMM `BluetoothSocket` の `read()` が close / disconnect 時に `-1` を返す。 |
| Android 17 / targetSdkVersion 37 + 必須条件 | `IOException` だけに依存する read loop は終了しない可能性があり、`-1` check が必要。 |

## 要約

Android 17 / targetSdkVersion 37 では、RFCOMM-based `BluetoothSocket` の `InputStream.read()` が socket close / connection dropped 時に `-1` を返す。Bluetooth module の `BluetoothSocket.java` で ChangeId `383671392`、targetSdkVersion 37 gate、RFCOMM EOF handling を確認した。

## 顧客影響

- `IOException` だけに依存する RFCOMM read loop は、切断時に終了しない可能性がある。
- printer、scanner、IoT、serial data transfer など Bluetooth Classic / RFCOMM 連携で read loop の終了条件確認が必要。

## 影響対象

- 対象アプリ: Bluetooth Classic / RFCOMM / SPP 相当の通信を行うアプリ。
- 対象機能: printer、scanner、IoT、embedded device、serial data transfer、Bluetooth peripheral 連携。
- 対象条件: targetSdkVersion 37、RFCOMM `BluetoothSocket`、read loop が `IOException` catch だけで終了する実装。

## 対応要否

- 必須対応: RFCOMM read loop で `read()` の戻り値 `-1` を EOF / disconnect として扱う。
- 推奨対応: remote disconnect、local close、Bluetooth off、range out で loop 終了と再接続をテストする。
- 不要: RFCOMM `BluetoothSocket` を使わないアプリ、または `-1` handling 済みのアプリでは直接影響は限定的。

## テストマトリクス

| 端末 OS | targetSdkVersion | 期待挙動 |
| --- | --- | --- |
| Android 16 | 36 | Android 16 baseline。具体挙動は Bluetooth module 比較待ち。 |
| Android 17 | 36 | 旧挙動。EOF で `IOException` path。 |
| Android 17 | 37 | RFCOMM `read()` は socket closed / connection dropped 時に `-1` を返す。 |

## 顧客向け説明

Android 17 / targetSdkVersion 37 では、RFCOMM `BluetoothSocket` の `InputStream.read()` が、socket close や remote disconnect 時に `-1` を返すようになります。これは `InputStream` の標準 EOF 挙動に合わせる変更です。

`IOException` が throw されることだけを前提に read loop を抜けている実装は、切断時に loop が終了しない可能性があります。`bytesRead == -1` を明示的に確認して、EOF / disconnect として処理してください。

## 根拠

- 公式ドキュメント: https://developer.android.com/about/versions/17/behavior-changes-17
- 検証対象の原文: targetSdkVersion 37 のアプリでは、RFCOMM-based `BluetoothSocket` から取得した `InputStream.read()` が socket closed / connection dropped 時に `-1` を返す。`IOException` だけに依存せず `-1` を確認する必要がある。
- AOSP ファイル: `tmp/aosp-checkouts/Bluetooth/framework/java/android/bluetooth/BluetoothSocket.java`
- AOSP ソース文脈: app read loop -> `BluetoothSocket` input stream -> RFCOMM socket -> local close or remote disconnect handling。
- AOSP gate: `Flags.makeSocketReadBehaviorConsistent()`、`CompatChanges.isChangeEnabled(MAKE_SOCKET_READ_BEHAVIOR_CONSISTENT)`、`SdkLevel.isAtLeastC()`。
- 差分解釈: `ret < 0` の EOF path で、targetSdkVersion 37 以上では `-1` を返し、それ以外では従来どおり `IOException` を throw する changed condition。
- 適用ゲートの結論: targetSdkVersion 37 条件付き。

## 人間の判断欄

最終優先度（Final Priority）:
- 人間による判断が必要

判断（Decision）:
- 未判断

## 再検証記録（2026-08-22）

- Android 17 の公式 Behavior Change 一覧と最新通常AOSPタグを再確認した。
- 対応する[主レポート](../../../behavior-changes/target/connectivity/consistent-bluetoothsocket-read-rfcomm.md)で official section、AOSP project / remote / checkout、解決済み commit、比較 command、dirty risk を再検証した。
- 主レポートの分類、confidence、未確認事項を維持し、実機未実施の項目を Observed 済みへ変更していない。
- 全件の結果は[再検証台帳](../../../analysis/REVALIDATION_2026-08-22.md)を参照する。
