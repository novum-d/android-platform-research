# RFCOMM における BluetoothSocket read() 挙動の一貫化

## 基本情報

### 調査対象 Android バージョン

比較元:
- android-16.0.0_r4

比較先:
- android-17.0.0_r1

以前の targetSdkVersion:
- 36

対象 targetSdkVersion:
- 37

### Behavior Change 文書

文書:
https://developer.android.com/about/versions/17/behavior-changes-17

関連文書:
- https://developer.android.com/reference/java/io/InputStream?#read(byte%5B%5D)
- https://developer.android.com/reference/android/bluetooth/BluetoothSocket
- https://developer.android.com/develop/connectivity/bluetooth/transfer-data#example
- https://developer.android.com/develop/connectivity/bluetooth/transfer-data

セクション:
Consistent BluetoothSocket read() behavior for RFCOMM

ページ種別:
- Apps targeting Android 17 or higher

### 分類スナップショット

主分類（Primary classification）:
- TARGET_SDK_37_CONDITIONAL

公式文書からの初期適用条件判断:
- 公式文書は、targetSdkVersion 37 のアプリでは、RFCOMM-based `BluetoothSocket` から取得した `InputStream` の `read()` が、socket close または connection dropped 時に `-1` を返すと説明している。
- この変更は LE CoC sockets と一貫した挙動にし、標準 `InputStream.read()` documentation の end-of-stream 仕様に合わせるためのものと説明されている。
- `IOException` の catch だけで read loop を抜ける実装は影響を受ける可能性があり、`read()` の戻り値 `-1` を明示的に確認する必要がある。
- 追加 checkout の `platform/packages/modules/Bluetooth` で、`BluetoothSocket.read()`、ChangeId `MAKE_SOCKET_READ_BEHAVIOR_CONSISTENT = 383671392`、`@EnabledSince(CINNAMON_BUN)`、`CompatChanges.isChangeEnabled()` を確認したため、確定分類は `TARGET_SDK_37_CONDITIONAL` とする。

早見表:

| 確認項目 | 回答 | 根拠 |
| --- | --- | --- |
| Android 17 に OS アップデートしただけで適用されるか | 原則 No | `@EnabledSince(targetSdkVersion = CINNAMON_BUN)` の compat ChangeId で制御される。 |
| targetSdkVersion 37 以上が必要か | Yes | `BluetoothSocket.MAKE_SOCKET_READ_BEHAVIOR_CONSISTENT = 383671392` が `@EnabledSince(CINNAMON_BUN)`。 |
| 追加の実行時条件があるか | ある | RFCOMM-based `BluetoothSocket`、`InputStream.read()`、socket close / connection dropped、read loop 実装が関係する。 |
| Compat Change ID が関係するか | Yes | `MAKE_SOCKET_READ_BEHAVIOR_CONSISTENT = 383671392`。 |

### 調査日

2026-06-11

### 信頼度

- High

### 適用条件分類

適用される条件:
- [ ] Android 17 上の全アプリ（targetSdkVersion に依存しない）
- [ ] Android 17 以上で targetSdkVersion >= 37
- [x] targetSdkVersion 37 以上かつ追加の実行時条件を満たす場合に適用
- [ ] Mainline / Google Play system update に依存
- [ ] API addition only, not a behavior change
- [ ] 追加根拠が必要

必要な実行時条件:
- Android version: Android 17 以上。
- targetSdkVersion: 公式文書上は 37。
- Device/form factor: 公式抜粋では条件なし。Bluetooth RFCOMM を利用できる device が前提。
- Permission/API/component condition: RFCOMM-based `BluetoothSocket`、`BluetoothSocket.getInputStream()`、`InputStream.read()`、socket close / remote disconnect。
- App state/process condition: アプリが RFCOMM socket の read loop で data を読み取っている時点。

Compat framework:
- Change ID: `383671392`
- 変更名: `MAKE_SOCKET_READ_BEHAVIOR_CONSISTENT`
- 既定状態: `@EnabledSince(targetSdkVersion = Build.VERSION_CODES.CINNAMON_BUN)`
- テスト時の切り替え可否: compat change と `make_socket_read_behavior_consistent` flag により切り替え可能

分類信頼度:
- High

分類根拠:
- 公式ドキュメントページ: `behavior-changes-17`
- 検証対象の適用条件文: apps targeting Android 17 / API level 37, RFCOMM `BluetoothSocket` input stream `read()` returns `-1` on socket closed / connection dropped.
- AOSP targetSdk gate: `platform/packages/modules/Bluetooth` の `BluetoothSocket` で確認。
- Compat framework entry: `MAKE_SOCKET_READ_BEHAVIOR_CONSISTENT = 383671392`、`@EnabledSince(CINNAMON_BUN)`。

---

# エグゼクティブサマリー

Android 17 / targetSdkVersion 37 のアプリでは、RFCOMM-based `BluetoothSocket` の `InputStream.read()` が、socket close または connection dropped 時に `-1` を返す、と公式文書は説明している。これは LE CoC socket と挙動を揃え、`InputStream.read()` の end-of-stream 仕様に合わせるための変更である。

これまで `IOException` が throw されることだけを期待して read loop を終了していたアプリは、`read()` が `-1` を返した場合に loop が抜けず、無限ループ、空読み、切断検出遅延などを起こす可能性がある。RFCOMM read loop は `-1` を明示的にチェックする必要がある。

Bluetooth module の Android 17 tag で `BluetoothSocket` 実装差分、targetSdkVersion ゲート、Compat Change ID を確認できたため、信頼度は High とする。

---

# 公式ドキュメント確認

## 原文（Statement）

Page title:
- Behavior changes: Apps targeting Android 17 or higher

Page URL:
- https://developer.android.com/about/versions/17/behavior-changes-17

ページ種別:
- apps targeting Android 17

Section title:
- Consistent BluetoothSocket read() behavior for RFCOMM

検証対象の原文:

> For apps targeting Android 17 (API level 37), the read() method of the InputStream obtained from an RFCOMM-based BluetoothSocket now returns -1 when the socket is closed or the connection is dropped.

提供された公式文書の抜粋は、この変更により RFCOMM の挙動が LE CoC sockets および標準 `InputStream.read()` documentation と整合すると説明している。`IOException` の catch だけで read loop を抜けるアプリは、`-1` を明示的に確認する必要がある。

## 解釈

この変更は、RFCOMM `BluetoothSocket` の end-of-stream 表現を Java `InputStream` の標準挙動に合わせる compatibility behavior change である。切断時に例外だけを期待するのではなく、`read()` の戻り値が `-1` の場合も stream end として扱う必要がある。

アプリ開発者にとって重要なのは、targetSdkVersion 37 へ更新すると、remote device disconnect や socket close が `IOException` ではなく `-1` return として観測される可能性がある点である。read loop の終了条件に `bytes == -1` を含める必要がある。

---

# 変更内容

公式文書上の変更点:
- targetSdkVersion 37 のアプリで、RFCOMM-based `BluetoothSocket` から取得した `InputStream.read()` が socket closed / connection dropped 時に `-1` を返す。
- 変更の目的は、RFCOMM socket behavior を LE CoC sockets と一貫させること。
- 変更は、end of stream 到達時に `-1` を返すという標準 `InputStream.read()` documentation と整合する。
- `IOException` catch だけで read loop を抜けるアプリは影響を受ける可能性がある。
- BluetoothSocket read loop は `-1` return を明示的に確認し、remote disconnect / socket close 時に正しく終了する必要がある。

AOSP で確認した点 / 未確認の点:
- `frameworks-base` の `android-16.0.0_r4` -> `android-17.0.0_r1` 比較では、`BluetoothSocket` / RFCOMM read path の直接実装は確認できなかった。
- `frameworks-base` の Android 17 tag には `core/java/android/bluetooth/BluetoothSocket.java` や `packages/modules/Bluetooth` が存在しなかった。
- `tmp/aosp-checkouts/Bluetooth` に `platform/packages/modules/Bluetooth` の Android 16 / Android 17 tag を取得し、`BluetoothSocket.read(byte[], int, int)` の EOF handling を確認した。
- Android 17 で RFCOMM read path が `Flags.makeSocketReadBehaviorConsistent()`、`CompatChanges.isChangeEnabled(MAKE_SOCKET_READ_BEHAVIOR_CONSISTENT)`、`SdkLevel.isAtLeastC()` を満たす場合に `-1` を返す。
- targetSdkVersion 37 gate は ChangeId `383671392` の `@EnabledSince(CINNAMON_BUN)`。
- `BluetoothInputStream` 経由の `read(byte[])` / `read(byte[], int, int)` が対象。single-byte read は Java stream wrapper の委譲範囲として扱う。
- local close と remote disconnect の扱い差。
- LE CoC socket の既存挙動との整合。
- native stack 内部の close reason 詳細。

## 適用条件

公式文書と Bluetooth module evidence から、Android 17 以上、targetSdkVersion 37、RFCOMM-based `BluetoothSocket` の `InputStream.read()` を使うアプリに適用される。確定分類は `TARGET_SDK_37_CONDITIONAL` とする。

### OS アップデート時の挙動

- Android 17 にアップデートしただけで適用されるか: 原則 No。ChangeId は targetSdkVersion 37 以上で enabled。
- targetSdkVersion に依存しない根拠: なし。原文は apps targeting Android 17 / API level 37 と明示している。
- Android 16 以前での挙動: Android 16 Bluetooth tag には `MAKE_SOCKET_READ_BEHAVIOR_CONSISTENT` ChangeId と compat gated `-1` return path がない。

### targetSdkVersion 37 以上での挙動

- targetSdkVersion 37 以上で適用されるか: Yes。`@EnabledSince(CINNAMON_BUN)` の ChangeId で確認。
- Android 17 以外で targetSdkVersion 37 にした場合の挙動: 未確認。公式文書は Android 17 Behavior Changes として説明しているため、Android 17 platform behavior として扱う。
- opt-out / temporary override の有無: compat change `383671392` と feature flag `make_socket_read_behavior_consistent` に依存。

### その他の条件

- device/form factor: 公式抜粋では条件なし。
- permission: `BluetoothSocket` 利用には通常 Bluetooth permission が関係するが、read behavior gate は ChangeId / feature flag / socket type で決まる。
- API usage: `BluetoothSocket`、RFCOMM socket、`BluetoothSocket.getInputStream()`、`InputStream.read()`。
- manifest attribute: Bluetooth permission declaration / runtime grant が関係する可能性。
- component boundary: app read loop、framework `BluetoothSocket` Java API、Bluetooth stack / native socket、remote device connection state にまたがる。

---

# AOSP 調査

## checkout 状態

根拠を採用する前に確認したコマンド:

```bash
git -C frameworks-base status --short
git -C frameworks-base tag --list android-16.0.0_r4
git -C frameworks-base tag --list 'android-17*'
```

結果:
- `frameworks-base` working tree: 調査時点で clean。
- From tag: `android-16.0.0_r4` exists.
- To tag: `android-17.0.0_r1` exists.

根拠上の制約:
- `frameworks-base` では明示的な tag 比較と file / symbol 検索を実施したが、`BluetoothSocket` / RFCOMM read path の直接実装、targetSdkVersion ゲート、Compat Change ID は確認できなかった。
- Bluetooth socket の実装本体は `frameworks-base` ではなく Bluetooth module 側にあり、追加 checkout で確認済み。
- 広域の `frameworks-base` tag diff では rename detection が skipped される警告が出たため、`--no-renames` と対象 path 限定で再確認した。追加で見つかった Bluetooth 関連差分は `core/java/android/net/flags.aconfig` の Bluetooth flags と SettingsLib の pairing diagnosis であり、RFCOMM `BluetoothSocket.read()` 実装ではなかった。
- この制約は解消済み。AOSP-backed conclusion は High confidence とする。

## 関連ファイル

追加 checkout で確認:
- `platform/packages/modules/Bluetooth/framework/java/android/bluetooth/BluetoothSocket.java`
- `platform/packages/modules/Bluetooth/flags/rfcomm.aconfig`
- `platform/packages/modules/Bluetooth/framework/tests/bumble/src/android/bluetooth/sockets/rfcomm/RfcommTest.kt`
- `platform/packages/modules/Bluetooth/tests/navi/navi/tests/functionality/rfcomm_socket_test.py`

## 確認したソース文脈

`frameworks-base` の Android 17 tag では直接実装はない。Bluetooth module 側で実装を確認した。

| ファイル / シンボル | Android 16 基準挙動 | Android 17 挙動 | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| `frameworks-base` / `core/java/android/bluetooth` | `BluetoothSocket` 実装なし | `BluetoothSocket` 実装なし | framework checkout に API boundary / implementation があるかを確認したが、直接 evidence は見つからなかった。 |
| `frameworks-base` / `packages/modules/Bluetooth` | path なし | path なし | Bluetooth module が local `frameworks-base` checkout に含まれるか確認したが、含まれていなかった。 |
| `core/java/android/net/flags.aconfig` / Bluetooth flags | relevant flag なし | `autonomous_repairing_initiation` / `bluetooth_pairing_hardening` が追加 | Bluetooth 周辺 feature flag だが、RFCOMM read / EOF behavior の実装ではないため補助 evidence に留める。 |
| `packages/SettingsLib` / Bluetooth diagnosis | pairing context を診断表示に使わない | `EXTRA_PAIRING_CONTEXT` / `PAIRING_CONTEXT_REPAIRING` を診断表示で参照 | pairing diagnosis UI の差分であり、`BluetoothSocket` read behavior ではないため除外。 |
| `BluetoothSocket.MAKE_SOCKET_READ_BEHAVIOR_CONSISTENT` | なし | ChangeId `383671392`、`@EnabledSince(CINNAMON_BUN)` | targetSdkVersion 37 gate。 |
| `BluetoothSocket.read(byte[], int, int)` | negative read return で `IOException` | flag + compat change + Android C 以上なら EOF として `-1` を返す | 公式文書の `read()` behavior change 本体。 |
| `flags/rfcomm.aconfig` / `make_socket_read_behavior_consistent` | flag なし | RFCOMM & LE CoC sockets の EOF return を一貫させる flag | feature flag gate。 |

必須記入項目:
- Entry point / caller: app の `InputStream.read()`、`BluetoothSocket.getInputStream()`、RFCOMM socket read、remote disconnect / local close handling。
- Relevant class or service responsibility: Bluetooth module の `BluetoothSocket` が app-facing stream read behavior を決める。
- Runtime path from app API / system event to changed code: app read loop -> `BluetoothInputStream` -> `BluetoothSocket.read(byte[], int, int)` -> RFCOMM socket / native Bluetooth stack -> local close or remote disconnect handling。
- 除外した無関係なコードパス: `media/packages/BluetoothMidiService` は BLE MIDI service であり、RFCOMM `BluetoothSocket` read behavior ではないため除外。

## 差分解釈

| 確認した差分 | 解釈 | 挙動変更との関係 | 信頼度 |
| --- | --- | --- | --- |
| `frameworks-base` で `BluetoothSocket` 実装が見つからない | no behavior change found in frameworks-base scope | 実装本体は Bluetooth module 側にあるため、frameworks-base 単体では根拠にならない。 | 高 |
| Bluetooth module `BluetoothSocket.read()` の EOF branch | changed condition | flag + compat change + Android C 以上なら `IOException` ではなく `-1` を返す。 | 高 |
| ChangeId `383671392` | compat gate | targetSdkVersion 37 以上で デフォルト有効。 | 高 |

必須分類:
- Added behavior: RFCOMM EOF 時の `-1` return path。
- Removed behavior: targetSdkVersion 37 以上での RFCOMM EOF 時 `IOException` path。
- Changed condition / gate: `@EnabledSince(CINNAMON_BUN)` の compat ChangeId と feature flag。
- Changed default: targetSdkVersion 37 以上では compat change が デフォルト有効。
- No behavior change found: `frameworks-base` scope では該当。ただし platform 全体の evidence は Bluetooth module で確認済み。

## 事実

事実:
- 公式 Behavior Change 文書は、targetSdkVersion 37 のアプリで RFCOMM-based `BluetoothSocket` の `InputStream.read()` が socket closed / connection dropped 時に `-1` を返すと述べている。
- 公式文書は、この変更が LE CoC sockets と RFCOMM socket の挙動を一貫させると述べている。
- 公式文書は、この変更が end of stream 到達時に `-1` を返す標準 `InputStream.read()` documentation と整合すると述べている。
- 公式文書は、`IOException` catch だけに依存する read loop が影響を受ける可能性があり、`-1` を明示的に確認すべきと述べている。
- ローカル `frameworks-base` には `android-16.0.0_r4` タグがある。
- ローカル `frameworks-base` には `android-17.0.0_r1` タグがある。
- 調査時点で `frameworks-base` working tree は clean。
- `frameworks-base` の Android 17 tag には `BluetoothSocket` 実装と `packages/modules/Bluetooth` が含まれていない。
- `platform/packages/modules/Bluetooth` の Android 16 / Android 17 tag を `tmp/aosp-checkouts/Bluetooth` に取得した。
- Android 17 Bluetooth tag の `BluetoothSocket` には ChangeId `383671392` と EOF 時 `-1` return path がある。

観察:
- 公式ページ種別は targetSdkVersion 37 以上向けである。
- 原文は "For apps targeting Android 17 (API level 37)" と明示しており、targetSdkVersion 37 gate がある可能性が高い。
- この項目は targetSdkVersion 37 条件に加えて、RFCOMM-based `BluetoothSocket` と socket close / connection dropped という API usage / runtime condition を含む。
- 仕様としては Java `InputStream` の標準 EOF handling に近づく変更であり、例外駆動の read loop が互換性リスクになる。
- targetSdkVersion 37 gate は Bluetooth module 側で確認できた。
- feature flag `make_socket_read_behavior_consistent` も gate に含まれる。

仮説:
- Android 17 / targetSdkVersion 37 では、flag と compat change が有効な場合に RFCOMM remote disconnect 時の negative read return が `-1` として返る。
- Android 17 / targetSdkVersion 36 のアプリでは compat change が デフォルト無効 のため旧挙動が維持される。
- `IOException` catch だけを終了条件にした loop は、`-1` を data length として扱って誤動作する、または loop 終了しない可能性がある。

結論:
- `TARGET_SDK_37_CONDITIONAL` と分類する。
- Android 17 / targetSdkVersion 37 の RFCOMM `BluetoothSocket` read loop では `read()` の `-1` return を EOF として扱う必要がある。
- Confidence は High。

## 適用ゲート根拠

- targetSdkVersion 適用ゲート: `@EnabledSince(targetSdkVersion = Build.VERSION_CODES.CINNAMON_BUN)`。
- CompatChanges.isChangeEnabled / ChangeId: `MAKE_SOCKET_READ_BEHAVIOR_CONSISTENT = 383671392`。
- @EnabledAfter / @EnabledSince / default state: `@EnabledSince(CINNAMON_BUN)`。
- Build.VERSION / SDK_INT 適用ゲート: `SdkLevel.isAtLeastC()`。
- DeviceConfig / resources config: 該当なし。feature flag と compat gate で制御。
- Permission/AppOps 適用ゲート: Bluetooth permission は利用条件として関係するが、read behavior gate ではない。
- Manifest/property 適用ゲート: Bluetooth permission declaration は利用条件として関係するが、read behavior gate ではない。
- 適用ゲート未検出: 該当なし。
- 適用ゲートの結論: targetSdkVersion 37 + Android 17 + feature flag + RFCOMM `BluetoothSocket` + close / disconnect condition。
- ソース文脈からの推論: `frameworks-base` には該当 path がなく、Bluetooth module の `BluetoothSocket` が app-facing behavior を実装する。

---

# 影響分析

## 影響を受けるアプリ

影響を受ける可能性があるアプリ:
- RFCOMM `BluetoothSocket` で serial-like data transfer を行うアプリ。
- `BluetoothSocket.getInputStream().read()` の戻り値 `-1` を確認していないアプリ。
- `IOException` catch だけで read loop を終了するアプリ。
- remote device disconnect / socket close 時の EOF handling を検証していない Bluetooth peripheral / embedded device / printer / scanner / IoT 連携アプリ。
- targetSdkVersion 37 への更新を予定している Bluetooth Classic / SPP 相当の通信アプリ。

## 影響を受けにくいアプリ

影響が限定的または対象外と考えられるケース:
- Bluetooth RFCOMM を使わないアプリ。
- LE CoC socket だけを使うアプリ。
- `InputStream.read()` の `-1` return をすでに EOF として扱っているアプリ。
- socket close / disconnect handling を byte count と exception の両方で処理しているアプリ。
- Bluetooth module 側の AOSP 根拠 で対象外 gate や exemption が確認されたケース。

---

# 顧客影響

## 影響度

- 人間による判断が必要

※ 最終 severity / priority は人間が判断する。このレポートでは確定しない。

## ビジネス影響

- ユーザー影響: Bluetooth device 切断時に read loop が終了しない、再接続できない、UI が接続中のままになる、データ転送スレッドが残る可能性がある。
- 運用影響: remote disconnect、local close、通信エラー、再接続のテスト matrix を見直す必要がある可能性がある。
- 開発影響: RFCOMM read loop の終了条件修正、`-1` handling、thread / coroutine cancellation、resource close、再接続処理の更新が必要になる可能性がある。

---

# サービス影響例

このセクションは、公式文書と AOSP 根拠 から導いた「起こりうる影響例」を記録する。特定サービスで実際に発生確認した事実ではない。

## 例1: Square POS / Shopify POS のような Bluetooth レシートプリンター連携

- 具体サービス例: Square Point of Sale、Shopify POS、スマレジなど、店舗端末で Bluetooth プリンターやバーコードスキャナーを使う POS アプリ。
- 影響を受ける実装パターン: RFCOMM `BluetoothSocket` の read loop を `IOException` catch だけで終了する実装。
- 発生条件: Android 17 / targetSdkVersion 37 で socket close / connection dropped 時に `read()` が `-1` を返す場合。
- ユーザーに見える症状: 切断後も接続中表示のままになる、再接続できない、印刷 / 読み取り job が止まる可能性。
- 技術的に起きていること: EOF が exception ではなく `-1` として返り、既存 loop が終了条件として扱わない。
- 開発・運用への影響: read loop、thread cancellation、再接続 flow、device disconnect test の見直しが必要になる可能性。
- 推奨対応候補: `bytesRead == -1` を EOF として扱い、socket close と reconnect 処理へ進む。
- 根拠: 公式 statement と report の expected behavior。
- 信頼度: 高
- 注意: 上記サービスで発生確認した事実ではない。実際の影響は利用プリンター / scanner SDK と read loop 実装に依存する。

## 例2: OBDLink / 専用計測アプリのような Bluetooth SPP 相当通信

- 具体サービス例: OBDLink のような OBD-II adapter 連携アプリ、工場・医療・物流向けの専用計測アプリ。
- 影響を受ける実装パターン: remote disconnect 時に exception が必ず発生すると仮定した parser / protocol loop。
- 発生条件: `read()` が `-1` を返し、アプリがそれを data length として扱う、または無視する場合。
- ユーザーに見える症状: データ更新が止まる、切断検出が遅れる、再接続操作が効かない可能性。
- 技術的に起きていること: serial protocol の受信 loop が EOF と異常終了を区別できず、state machine が connected のまま残る。
- 開発・運用への影響: protocol state machine、EOF handling、device firmware 別 regression test が必要になる可能性。
- 推奨対応候補: `>0` data、`-1` EOF、`IOException` abnormal error を分けて処理する。
- 根拠: 公式 statement と report の action candidates。
- 信頼度: 高
- 注意: 上記サービスで発生確認した事実ではない。実 device / firmware / SDK ごとの差異は実機検証が必要。

---

# 対応候補

## 必須対応（Must）

- RFCOMM `BluetoothSocket` の read loop を棚卸しし、`read()` の戻り値 `-1` を確認しているか確認する。
- `IOException` catch だけで loop を終了している箇所を修正し、`bytesRead == -1` を EOF / disconnect として扱う。
- remote device disconnect、local socket close、Bluetooth off、range out などの切断シナリオで read loop が終了するか確認する。
- Android 17 / targetSdkVersion 37 のテスト環境が利用可能になったら、RFCOMM read loop の戻り値と exception を記録する。
- compat change `383671392` が有効な状態で、targetSdkVersion 36 / 37 の挙動差を確認する。

## 推奨対応（Recommended）

- `InputStream.read()` の標準仕様に沿い、0 より大きい値を data length、`-1` を EOF、`IOException` を abnormal error として分ける。
- read thread / coroutine の cancellation、socket close、stream close、reconnect flow を統一的に整理する。
- Bluetooth transfer-data guide の recommended implementation に read loop を合わせる。
- LE CoC と RFCOMM の切断処理を共通化できる場合は、`-1` EOF handling を共通 path に入れる。

## 任意対応（Optional）

- Bluetooth device vendor / firmware ごとに disconnect behavior が異ならないか、主要 device で regression test を追加する。
- 接続状態 telemetry を追加し、read loop が終了しない状態や再接続失敗を検出する。

---

# 検証方法

## 検証マトリクス

| 端末 OS | targetSdkVersion | Compat flag | 期待される挙動 |
| --- | --- | --- | --- |
| Android 16 | 36 | default | Android 16 baseline。compat gated `-1` return path はない。 |
| Android 17 | 36 | default | compat change デフォルト無効。旧挙動。 |
| Android 17 | 37 | default | RFCOMM `BluetoothSocket` input stream `read()` は socket closed / connection dropped 時に `-1` を返す。 |
| Android 17 | 36 | force-enabled（利用可能な場合） | `-1` return path を強制できる可能性がある。 |
| Android 17 | 37 | force-disabled（利用可能な場合） | 旧 `IOException` path に戻せる可能性がある。 |

## 手順

- targetSdk変更: targetSdkVersion 36 と 37 の test build を用意する。
- Compat framework コマンド: ChangeId `383671392` を対象に force-enabled / force-disabled を確認する。
- テスト方法: RFCOMM `BluetoothSocket` を接続し、remote disconnect、local socket close、Bluetooth adapter off、range out を分けて `InputStream.read()` の return value / exception を記録する。
- 再現手順: Android 17 device で対象アプリを install し、RFCOMM device と接続する。read loop 実行中に remote device 側から切断し、`read()` が `-1` を返すか、`IOException` を throw するか、loop が終了するかを確認する。
- 期待結果: targetSdkVersion 37 のアプリでは、socket closed / connection dropped 時に `read()` が `-1` を返し、app がそれを EOF として扱って loop を終了する。targetSdkVersion 36 では旧挙動が維持される。

---

# 結論

公式文書上、Android 17 / targetSdkVersion 37 のアプリでは RFCOMM `BluetoothSocket` の `InputStream.read()` が socket close / connection dropped 時に `-1` を返す。`IOException` だけに依存する read loop は終了しない可能性があるため、`-1` を EOF として扱う修正が必要である。

Bluetooth module の Android 17 AOSP タグで、実装 gate、RFCOMM read path、targetSdkVersion 36 / 37 の差分、compat ChangeId を確認済みである。確定分類は `TARGET_SDK_37_CONDITIONAL`、信頼度は High とする。

---

# 人間の判断欄

最終優先度（Final Priority）:
- 人間による判断が必要

最終影響度:
- 人間による判断が必要

リリース判断:
- 人間による判断が必要

顧客通知優先度:
- 人間による判断が必要

判断（Decision）:
- 未判断

判断メモ:
- AOSP 根拠 は確認済み。最終 priority / customer communication priority は人間が判断する。

---

# 参照（References）

## ドキュメント

- https://developer.android.com/about/versions/17/behavior-changes-17
- https://developer.android.com/reference/java/io/InputStream?#read(byte%5B%5D)
- https://developer.android.com/reference/android/bluetooth/BluetoothSocket
- https://developer.android.com/develop/connectivity/bluetooth/transfer-data#example
- https://developer.android.com/develop/connectivity/bluetooth/transfer-data

## AOSP

- ローカル `frameworks-base` では Android 17 tag を確認済み。
- From tag checked: `android-16.0.0_r4`
- To tag checked: `android-17.0.0_r1`
