# RFCOMM の BluetoothSocket read() 挙動の一貫化 - 1ページ要約

## 対象（Target）

Android 17 挙動変更

From:
- android-16.0.0_r4

To:
- TBD: Android 17 AOSP タグ

Previous targetSdkVersion:
- 36

Target targetSdkVersion:
- 37

## 適用条件（Applicability）

- 主分類（Primary classification）: UNKNOWN_NEEDS_MORE_EVIDENCE
- OS アップデート / 全アプリ: 未確認。原文は targetSdkVersion 37 を明示しているが、AOSP 適用ゲートは未確認。
- targetSdkVersion 37 以上: 公式文書上は該当。AOSP 適用ゲートは未確認。
- その他の必須条件: RFCOMM-based `BluetoothSocket`、`InputStream.read()`、socket closed / 接続 dropped、read loop 実装。
- Compat Change ID: 未確認
- Compat default state: 未確認

## 早見マトリクス

| シナリオ（Scenario） | 影響（Impact） |
| --- | --- |
| Android 17 / targetSdkVersion 36 | 未確認。この section は targetSdkVersion 37 向けだが、AOSP 適用ゲートは未確認。 |
| Android 17 / targetSdkVersion 37 | 公式文書上、RFCOMM `BluetoothSocket` の `read()` が close / disconnect 時に `-1` を返す。 |
| Android 17 / targetSdkVersion 37 + 必須条件 | `IOException` だけに依存する read loop は終了しない可能性があり、`-1` の確認が必要。 |

## 要約

Android 17 / targetSdkVersion 37 では、RFCOMM-based `BluetoothSocket` の `InputStream.read()` が socket close / 接続 dropped 時に `-1` を返す、と公式文書は説明している。

## 顧客影響

- 要確認

## 影響対象

- 対象アプリ: Bluetooth Classic / RFCOMM / SPP 相当の通信を行うアプリ。
- 対象機能: printer、scanner、IoT、embedded 端末、serial data transfer、Bluetooth peripheral 連携。
- 対象条件: targetSdkVersion 37、RFCOMM `BluetoothSocket`、read loop が `IOException` catch だけで終了する実装。

## 対応要否

- 必須対応: RFCOMM read loop で `read()` の戻り値 `-1` を EOF / disconnect として扱う。
- 推奨対応: remote disconnect、ローカル close、Bluetooth off、range out で loop 終了と再接続をテストする。
- 不要: RFCOMM `BluetoothSocket` を使わないアプリ、または `-1` handling 済みのアプリでは直接影響は限定的。

## テストマトリクス

| 端末 OS | targetSdkVersion | 期待挙動 |
| --- | --- | --- |
| Android 16 | 36 | Android 16 基準挙動。具体挙動は Android 17 タグ比較待ち。 |
| Android 17 | 36 | 未確認。この section は targetSdkVersion 37 向けだが、AOSP 適用ゲートは未確認。 |
| Android 17 | 37 | RFCOMM `read()` は socket closed / 接続 dropped 時に `-1` を返すと公式文書は説明。 |

## 顧客向け説明

Android 17 / targetSdkVersion 37 では、RFCOMM `BluetoothSocket` の `InputStream.read()` が、socket close や remote disconnect 時に `-1` を返すようになります。これは `InputStream` の標準 EOF 挙動に合わせる変更です。

`IOException` が throw されることだけを前提に read loop を抜けている実装は、切断時に loop が終了しない可能性があります。`bytesRead == -1` を明示的に確認して、EOF / disconnect として処理してください。現時点ではローカル AOSP checkout に Android 17 タグがないため、targetSdkVersion 適用ゲート、実装パス、compat flag の有無は未確認です。

## 根拠

- Official documentation: https://developer.android.com/about/versions/17/behavior-changes-17
- 検証対象の原文: targetSdkVersion 37 のアプリでは、RFCOMM-based `BluetoothSocket` から取得した `InputStream.read()` が socket closed / 接続 dropped 時に `-1` を返す。`IOException` だけに依存せず `-1` を確認する必要がある。
- AOSP ファイル: 未確認。ローカルの `frameworks-base` に `android-17*` タグがない。
- AOSP ソース文脈: 未確認。タグ間差分が実行できない。
- 差分解釈: 未分類。公式文書上は changed condition / behavior consistency change と読めるが、AOSP 差分による確認は Android 17 タグ待ち。
- 適用ゲートの結論: 未確認。公式文書は targetSdkVersion 37 と RFCOMM 条件を示すが、AOSP 適用ゲート根拠は未取得。

## 人間の判断欄

最終優先度（Final Priority）:
- Human decision required

判断（Decision）:
- 追加調査が必要
