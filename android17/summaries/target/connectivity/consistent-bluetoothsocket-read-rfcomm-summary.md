# Consistent BluetoothSocket read() behavior for RFCOMM - 1ページ要約（One Page Summary）

## 対象（Target）

Android 17 Behavior Change

From:
- android-16.0.0_r4

To:
- TBD: Android 17 AOSP tag

Previous targetSdkVersion:
- 36

Target targetSdkVersion:
- 37

## 適用条件（Applicability）

- 主分類（Primary classification）: UNKNOWN_NEEDS_MORE_EVIDENCE
- OS アップデート / 全アプリ（OS update / all apps）: Unknown。原文は targetSdkVersion 37 を明示しているが、AOSP gate 未確認。
- targetSdkVersion 37 以上: 公式文書上は該当。AOSP gate 未確認。
- その他の必須条件（Other required conditions）: RFCOMM-based `BluetoothSocket`、`InputStream.read()`、socket closed / connection dropped、read loop 実装。
- Compat Change ID: Unknown
- Compat default state: Unknown

## 早見マトリクス（At-a-Glance Matrix）

| シナリオ（Scenario） | 影響（Impact） |
| --- | --- |
| Android 17 / targetSdkVersion 36 | Unknown。この section は targetSdkVersion 37 向けだが、AOSP gate 未確認。 |
| Android 17 / targetSdkVersion 37 | 公式文書上、RFCOMM `BluetoothSocket` の `read()` が close / disconnect 時に `-1` を返す。 |
| Android 17 / targetSdkVersion 37 + 必須条件 | `IOException` だけに依存する read loop は終了しない可能性があり、`-1` check が必要。 |

## 要約（Summary）

Android 17 / targetSdkVersion 37 では、RFCOMM-based `BluetoothSocket` の `InputStream.read()` が socket close / connection dropped 時に `-1` を返す、と公式文書は説明している。

## 顧客影響（Customer Impact）

- 要確認

## 影響対象（Who Is Affected）

- 対象アプリ: Bluetooth Classic / RFCOMM / SPP 相当の通信を行うアプリ。
- 対象機能: printer、scanner、IoT、embedded device、serial data transfer、Bluetooth peripheral 連携。
- 対象条件: targetSdkVersion 37、RFCOMM `BluetoothSocket`、read loop が `IOException` catch だけで終了する実装。

## 対応要否（Required Action）

- 必須対応: RFCOMM read loop で `read()` の戻り値 `-1` を EOF / disconnect として扱う。
- 推奨対応: remote disconnect、local close、Bluetooth off、range out で loop 終了と再接続をテストする。
- 不要: RFCOMM `BluetoothSocket` を使わないアプリ、または `-1` handling 済みのアプリでは直接影響は限定的。

## テストマトリクス（Test Matrix）

| 端末 OS（Device OS） | targetSdkVersion | 期待挙動（Expected behavior） |
| --- | --- | --- |
| Android 16 | 36 | Android 16 baseline。具体挙動は Android 17 tag 比較待ち。 |
| Android 17 | 36 | Unknown。この section は targetSdkVersion 37 向けだが、AOSP gate 未確認。 |
| Android 17 | 37 | RFCOMM `read()` は socket closed / connection dropped 時に `-1` を返すと公式文書は説明。 |

## 顧客向け説明（Explanation for Customers）

Android 17 / targetSdkVersion 37 では、RFCOMM `BluetoothSocket` の `InputStream.read()` が、socket close や remote disconnect 時に `-1` を返すようになります。これは `InputStream` の標準 EOF 挙動に合わせる変更です。

`IOException` が throw されることだけを前提に read loop を抜けている実装は、切断時に loop が終了しない可能性があります。`bytesRead == -1` を明示的に確認して、EOF / disconnect として処理してください。現時点では local AOSP checkout に Android 17 tag がないため、targetSdkVersion gate、実装 path、compat flag の有無は未確認です。

## 根拠（Evidence）

- Official documentation: https://developer.android.com/about/versions/17/behavior-changes-17
- Original statement: targetSdkVersion 37 のアプリでは、RFCOMM-based `BluetoothSocket` から取得した `InputStream.read()` が socket closed / connection dropped 時に `-1` を返す。`IOException` だけに依存せず `-1` を確認する必要がある。
- AOSP files: 未確認。local `frameworks-base` に `android-17*` tag がない。
- AOSP source context: 未確認。tag 間 diff が実行できない。
- Diff interpretation: 未分類。公式文書上は changed condition / behavior consistency change と読めるが、AOSP diff による確認は Android 17 tag 待ち。
- Gate conclusion: Unknown。公式文書は targetSdkVersion 37 と RFCOMM condition を示すが、AOSP gate evidence は未取得。

## 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- Human decision required

判断（Decision）:
- Further investigation required
