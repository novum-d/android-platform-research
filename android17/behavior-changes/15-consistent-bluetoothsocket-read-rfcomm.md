# Consistent BluetoothSocket read() behavior for RFCOMM

## Metadata

### Android Versions

From:
- android-16.0.0_r4

To:
- TBD: Android 17 AOSP tag

Previous targetSdkVersion:
- 36

Target targetSdkVersion:
- 37

### Behavior Change Source

Document:
https://developer.android.com/about/versions/17/behavior-changes-17

Related documents:
- https://developer.android.com/reference/java/io/InputStream?#read(byte%5B%5D)
- https://developer.android.com/reference/android/bluetooth/BluetoothSocket
- https://developer.android.com/develop/connectivity/bluetooth/transfer-data#example
- https://developer.android.com/develop/connectivity/bluetooth/transfer-data

Section:
Consistent BluetoothSocket read() behavior for RFCOMM

Page type:
- Apps targeting Android 17 or higher

### Classification Snapshot

Primary classification:
- UNKNOWN_NEEDS_MORE_EVIDENCE

Initial applicability assumption from official documentation:
- 公式文書は、targetSdkVersion 37 のアプリでは、RFCOMM-based `BluetoothSocket` から取得した `InputStream` の `read()` が、socket close または connection dropped 時に `-1` を返すと説明している。
- この変更は LE CoC sockets と一貫した挙動にし、標準 `InputStream.read()` documentation の end-of-stream 仕様に合わせるためのものと説明されている。
- `IOException` の catch だけで read loop を抜ける実装は影響を受ける可能性があり、`read()` の戻り値 `-1` を明示的に確認する必要がある。
- ただし、local `frameworks-base` に Android 17 AOSP tag がないため、RFCOMM read path、targetSdkVersion gate、socket close / remote disconnect 時の戻り値、LE CoC との差分、Compat Change ID、default state は未検証である。確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

At-a-glance impact:

| Question | Answer | Evidence |
| --- | --- | --- |
| Android 17 OS update only? | Unknown | 公式文書は apps targeting Android 17 / API level 37 と述べるが、AOSP gate 未確認。 |
| targetSdkVersion 37 required? | Likely, but unverified | 原文は targetSdkVersion 37 を明示している。 |
| Additional runtime conditions? | Yes | RFCOMM-based `BluetoothSocket`、`InputStream.read()`、socket close / connection dropped、read loop 実装が関係する。 |
| Compat Change ID involved? | Unknown | Android 17 tag と compat framework evidence が未確認。 |

### Investigation Date

2026-06-11

### Confidence

- Low

### Applicability Classification

Applies when:
- [ ] OS update / all apps on Android 17 regardless of targetSdkVersion
- [ ] targetSdkVersion >= 37 on Android 17+
- [ ] targetSdkVersion >= 37, with additional runtime conditions
- [ ] Mainline / Google Play system update dependent
- [ ] API addition only, not a behavior change
- [x] Unknown / needs more evidence

Required runtime conditions:
- Android version: Android 17 以上が前提と考えられるが、AOSP tag 未取得。
- targetSdkVersion: 公式文書上は 37。
- Device/form factor: 公式抜粋では条件なし。Bluetooth RFCOMM を利用できる device が前提。
- Permission/API/component condition: RFCOMM-based `BluetoothSocket`、`BluetoothSocket.getInputStream()`、`InputStream.read()`、socket close / remote disconnect。
- App state/process condition: アプリが RFCOMM socket の read loop で data を読み取っている時点。

Compat framework:
- Change ID: Unknown
- Change name: Unknown
- Default state: Unknown
- Toggleable for testing: Unknown

Classification confidence:
- Low

Classification evidence:
- Official documentation page: `behavior-changes-17`
- Original applicability statement: apps targeting Android 17 / API level 37, RFCOMM `BluetoothSocket` input stream `read()` returns `-1` on socket closed / connection dropped.
- AOSP targetSdk gate: 未確認。local `frameworks-base` に `android-17*` tag がない。
- Compat framework entry: 未確認。Android 17 compat framework evidence が未取得。

---

# Executive Summary

Android 17 / targetSdkVersion 37 のアプリでは、RFCOMM-based `BluetoothSocket` の `InputStream.read()` が、socket close または connection dropped 時に `-1` を返す、と公式文書は説明している。これは LE CoC socket と挙動を揃え、`InputStream.read()` の end-of-stream 仕様に合わせるための変更である。

これまで `IOException` が throw されることだけを期待して read loop を終了していたアプリは、`read()` が `-1` を返した場合に loop が抜けず、無限ループ、空読み、切断検出遅延などを起こす可能性がある。RFCOMM read loop は `-1` を明示的にチェックする必要がある。

ただし、現時点の local `frameworks-base` には Android 17 AOSP tag がないため、実装差分、targetSdkVersion gate、native / Bluetooth stack の read path、Compat Change ID は未確認である。

---

# Original Documentation

## Statement

Page title:
- Behavior changes: Apps targeting Android 17 or higher

Page URL:
- https://developer.android.com/about/versions/17/behavior-changes-17

Page type:
- apps targeting Android 17

Section title:
- Consistent BluetoothSocket read() behavior for RFCOMM

Original statement being verified:

> For apps targeting Android 17 (API level 37), the read() method of the InputStream obtained from an RFCOMM-based BluetoothSocket now returns -1 when the socket is closed or the connection is dropped.

The supplied official text also states that this aligns RFCOMM behavior with LE CoC sockets and standard `InputStream.read()` documentation. Apps that rely only on catching `IOException` to break out of a read loop should explicitly check for `-1`.

## Interpretation

この変更は、RFCOMM `BluetoothSocket` の end-of-stream 表現を Java `InputStream` の標準挙動に合わせる compatibility behavior change である。切断時に例外だけを期待するのではなく、`read()` の戻り値が `-1` の場合も stream end として扱う必要がある。

アプリ開発者にとって重要なのは、targetSdkVersion 37 へ更新すると、remote device disconnect や socket close が `IOException` ではなく `-1` return として観測される可能性がある点である。read loop の終了条件に `bytes == -1` を含める必要がある。

---

# What Changed

公式文書上の変更点:
- targetSdkVersion 37 のアプリで、RFCOMM-based `BluetoothSocket` から取得した `InputStream.read()` が socket closed / connection dropped 時に `-1` を返す。
- 変更の目的は、RFCOMM socket behavior を LE CoC sockets と一貫させること。
- 変更は、end of stream 到達時に `-1` を返すという標準 `InputStream.read()` documentation と整合する。
- `IOException` catch だけで read loop を抜けるアプリは影響を受ける可能性がある。
- BluetoothSocket read loop は `-1` return を明示的に確認し、remote disconnect / socket close 時に正しく終了する必要がある。

AOSP で未確認の点:
- Android 16 baseline で RFCOMM socket close / disconnect 時に `read()` が `IOException` を throw していたか、または別の値を返していたか。
- Android 17 で RFCOMM read path が `-1` return に変更された実装箇所。
- targetSdkVersion 37 gate の実装箇所。
- `read(byte[])`、`read(byte[], int, int)`、single-byte `read()` の対象範囲。
- local close と remote disconnect の扱い差。
- LE CoC socket の既存挙動との整合。
- Bluetooth module / native stack と `frameworks-base` API boundary。
- Compat Change ID と default state。

## Applicability

公式文書の一次判断では、Android 17 以上、targetSdkVersion 37、RFCOMM-based `BluetoothSocket` の `InputStream.read()` を使うアプリに適用される。AOSP tag が未取得のため、確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

### OS Update Behavior

- Android 17 にアップデートしただけで適用されるか: Unknown
- targetSdkVersion に依存しない根拠: なし。原文は apps targeting Android 17 / API level 37 と明示している。
- Android 16 以前での挙動: 未確認。Android 17 tag との明示的な比較ができないため、Android 16 source だけから platform evidence として断定しない。

### targetSdkVersion 37 Behavior

- targetSdkVersion 37 以上で適用されるか: 公式文書上は Yes と読めるが、AOSP gate 未確認。
- Android 17 以外で targetSdkVersion 37 にした場合の挙動: Unknown。公式文書は Android 17 Behavior Changes として説明しているため、Android 17 platform behavior として扱う。
- opt-out / temporary override の有無: Unknown。公式抜粋には opt-out は示されていない。compat framework による force enable / disable は未確認。

### Other Conditions

- device/form factor: 公式抜粋では条件なし。
- permission: Bluetooth connection permission が関係する可能性はあるが、今回の read behavior gate としては AOSP 未確認。
- API usage: `BluetoothSocket`、RFCOMM socket、`BluetoothSocket.getInputStream()`、`InputStream.read()`。
- manifest attribute: Bluetooth permission declaration / runtime grant が関係する可能性。
- component boundary: app read loop、framework `BluetoothSocket` Java API、Bluetooth stack / native socket、remote device connection state にまたがる。

---

# AOSP Investigation

## Checkout Status

Commands checked before evidence use:

```bash
git -C frameworks-base status --short
git -C frameworks-base tag --list android-16.0.0_r4
git -C frameworks-base tag --list 'android-17*'
```

Result:
- `frameworks-base` working tree: clean at the time of investigation.
- From tag: `android-16.0.0_r4` exists.
- To tag: no local `android-17*` tag found.

Evidence limitation:
- Android 17 AOSP tag が local `frameworks-base` に存在しないため、`git -C frameworks-base diff android-16.0.0_r4 <android-17-tag> -- ...` による明示的な tag 比較を実行できない。
- Repository rule に従い、Android 17 working tree や推測による source evidence は採用しない。
- Bluetooth socket の実装本体は `frameworks-base` ではなく Bluetooth module / packages / native stack 側にある可能性がある。Android 17 tag 入手後は `frameworks-base` API boundary と Bluetooth module implementation の両方を確認する必要がある。
- この制約により、AOSP-backed conclusion は High confidence にできない。

## Related Files

未確認。Android 17 AOSP tag 取得後に、少なくとも以下の候補を tag 比較で確認する必要がある。

- `core/java/android/bluetooth/BluetoothSocket.java`
- `core/java/android/bluetooth/BluetoothDevice.java`
- `core/java/android/bluetooth/BluetoothAdapter.java`
- compat framework 定義ファイル内の BluetoothSocket / RFCOMM / targetSdkVersion 37 関連 Change ID
- Bluetooth module / packages 側の RFCOMM socket read implementation
- native Bluetooth stack / socket bridge の close / disconnect handling

## Source Context Reviewed

Android 17 AOSP tag がないため、source context は未レビュー。

| File / symbol | Android 16 baseline | Android 17 behavior | Why this code path matters |
| --- | --- | --- | --- |
| Not reviewed | Not reviewed | Not reviewed | Android 17 tag がないため、公式文書の記述を AOSP diff で検証できない。 |

Required context:
- Entry point / caller: 未確認。想定される entry point は app の `InputStream.read()`、`BluetoothSocket.getInputStream()`、RFCOMM socket read、remote disconnect / local close handling だが、AOSP evidence としては未採用。
- Relevant class or service responsibility: 未確認。
- Runtime path from app API / system event to changed code: 未確認。
- Why unrelated code paths were excluded: Android 17 tag 不在のため、source path の採否判断自体を保留。

## Diff Interpretation

| Observed diff | Interpretation | Behavior Change relevance | Confidence |
| --- | --- | --- | --- |
| No Android 17 tag diff available | Source diff type cannot be classified yet | 公式文書の `read()` return `-1` behavior、targetSdkVersion 37 gate、RFCOMM / LE CoC consistency を source diff で裏取りできていない | Low |

Required interpretation:
- Added behavior: 未確認。
- Removed behavior: 未確認。
- Changed condition / gate: 未確認。targetSdkVersion 37 gate がある可能性は高いが、AOSP 未確認。
- Changed default: 未確認。
- No behavior change found: 未確認。tag 不在のため「no behavior change」とは判断しない。

## Evidence

Facts:
- 公式 Behavior Change 文書は、targetSdkVersion 37 のアプリで RFCOMM-based `BluetoothSocket` の `InputStream.read()` が socket closed / connection dropped 時に `-1` を返すと述べている。
- 公式文書は、この変更が LE CoC sockets と RFCOMM socket の挙動を一貫させると述べている。
- 公式文書は、この変更が end of stream 到達時に `-1` を返す標準 `InputStream.read()` documentation と整合すると述べている。
- 公式文書は、`IOException` catch だけに依存する read loop が影響を受ける可能性があり、`-1` を明示的に確認すべきと述べている。
- local `frameworks-base` には `android-16.0.0_r4` tag がある。
- local `frameworks-base` には `android-17*` tag がない。
- 調査時点で `frameworks-base` working tree は clean。

Observations:
- 公式ページ種別は targetSdkVersion 37 以上向けである。
- 原文は "For apps targeting Android 17 (API level 37)" と明示しており、targetSdkVersion 37 gate がある可能性が高い。
- この項目は targetSdkVersion 37 条件に加えて、RFCOMM-based `BluetoothSocket` と socket close / connection dropped という API usage / runtime condition を含む。
- 仕様としては Java `InputStream` の標準 EOF handling に近づく変更であり、例外駆動の read loop が互換性リスクになる。
- AOSP tag がないため、実装が本当に targetSdkVersion 37 gate で制御されているかは未確認。
- Compat framework entry の有無も未確認。

Hypotheses:
- Android 17 / targetSdkVersion 37 では、RFCOMM remote disconnect 時に `read(byte[])` が `IOException` ではなく `-1` を返す可能性が高い。
- Android 17 / targetSdkVersion 36 のアプリでは旧挙動が維持される可能性があるが、AOSP gate 未確認のため断定しない。
- `IOException` catch だけを終了条件にした loop は、`-1` を data length として扱って誤動作する、または loop 終了しない可能性がある。

Conclusions:
- 現時点で顧客向けに確定できるのは、「公式文書上は Android 17 / targetSdkVersion 37 の RFCOMM `BluetoothSocket` read loop では `read()` の `-1` return を EOF として扱う必要がある」という範囲まで。
- AOSP gate、RFCOMM read implementation、failure / EOF behavior、compat framework default state が未確認のため、primary classification は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

## Applicability Gate Evidence

- targetSdkVersion gate: 未確認。公式文書は targetSdkVersion 37 を示すが、AOSP gate evidence はない。
- CompatChanges.isChangeEnabled / ChangeId: 未確認。Android 17 tag がないため検索未実施。
- @EnabledAfter / @EnabledSince / default state: 未確認。Android 17 tag がないため検索未実施。
- Build.VERSION / SDK_INT gate: 未確認。
- DeviceConfig / resources config: 未確認。
- Permission/AppOps gate: 未確認。Bluetooth permission は利用条件として関係する可能性があるが、read behavior gate としては未確認。
- Manifest/property gate: 未確認。
- No gate found: 未確認。Android 17 tag がないため「gate がない」とは判断しない。
- Gate conclusion: Unknown。公式文書の wording から targetSdkVersion 37 + RFCOMM `BluetoothSocket` + close / disconnect condition と推定されるが、AOSP で検証できていない。
- Reasoning from source context: source context 未レビューのため未確定。

---

# Impact Analysis

## Affected Apps

影響を受ける可能性があるアプリ:
- RFCOMM `BluetoothSocket` で serial-like data transfer を行うアプリ。
- `BluetoothSocket.getInputStream().read()` の戻り値 `-1` を確認していないアプリ。
- `IOException` catch だけで read loop を終了するアプリ。
- remote device disconnect / socket close 時の EOF handling を検証していない Bluetooth peripheral / embedded device / printer / scanner / IoT 連携アプリ。
- targetSdkVersion 37 への更新を予定している Bluetooth Classic / SPP 相当の通信アプリ。

## Non-Affected Apps

影響が限定的または対象外と考えられるケース:
- Bluetooth RFCOMM を使わないアプリ。
- LE CoC socket だけを使うアプリ。
- `InputStream.read()` の `-1` return をすでに EOF として扱っているアプリ。
- socket close / disconnect handling を byte count と exception の両方で処理しているアプリ。
- Android 17 AOSP tag 取得後に対象外 gate や exemption が確認されたケース。

---

# Customer Impact

顧客説明用。

## Impact Level

- Human decision required

※ 仮評価。最終判断は人間が行う。

## Business Impact

- ユーザー影響: Bluetooth device 切断時に read loop が終了しない、再接続できない、UI が接続中のままになる、データ転送スレッドが残る可能性がある。
- 運用影響: remote disconnect、local close、通信エラー、再接続のテスト matrix を見直す必要がある可能性がある。
- 開発影響: RFCOMM read loop の終了条件修正、`-1` handling、thread / coroutine cancellation、resource close、再接続処理の更新が必要になる可能性がある。

---

# Service Impact Examples（サービス影響例）

このセクションは、公式文書と AOSP evidence から導いた「起こりうる影響例」を記録する。特定サービスで実際に発生確認した事実ではない。

## Example 1（例1）: Bluetooth プリンター / スキャナー連携

- 対象サービス例: モバイル POS、配送ラベル印刷、バーコードスキャナー、店舗端末連携。
- 影響を受ける実装パターン: RFCOMM `BluetoothSocket` の read loop を `IOException` catch だけで終了する実装。
- 発生条件: Android 17 / targetSdkVersion 37 で socket close / connection dropped 時に `read()` が `-1` を返す場合。
- ユーザーに見える症状: 切断後も接続中表示のままになる、再接続できない、印刷 / 読み取り job が止まる可能性。
- 開発・運用への影響: read loop、thread cancellation、再接続 flow、device disconnect test の見直しが必要になる可能性。
- 推奨対応候補: `bytesRead == -1` を EOF として扱い、socket close と reconnect 処理へ進む。
- 根拠: 公式 statement と report の expected behavior。
- Confidence（信頼度）: Low
- 注意: targetSdkVersion gate と exact read path は AOSP tag 待ち。

## Example 2（例2）: IoT / embedded device の serial data transfer

- 対象サービス例: 計測器、医療周辺機器、車載 / 工場デバイス、Bluetooth SPP 相当通信。
- 影響を受ける実装パターン: remote disconnect 時に exception が必ず発生すると仮定した parser / protocol loop。
- 発生条件: `read()` が `-1` を返し、アプリがそれを data length として扱う、または無視する場合。
- ユーザーに見える症状: データ更新が止まる、切断検出が遅れる、再接続操作が効かない可能性。
- 開発・運用への影響: protocol state machine、EOF handling、device firmware 別 regression test が必要になる可能性。
- 推奨対応候補: `>0` data、`-1` EOF、`IOException` abnormal error を分けて処理する。
- 根拠: 公式 statement と report の action candidates。
- Confidence（信頼度）: Low
- 注意: 実 device ごとの差異は実機検証が必要。

---

# Required Actions

## Must

- RFCOMM `BluetoothSocket` の read loop を棚卸しし、`read()` の戻り値 `-1` を確認しているか確認する。
- `IOException` catch だけで loop を終了している箇所を修正し、`bytesRead == -1` を EOF / disconnect として扱う。
- remote device disconnect、local socket close、Bluetooth off、range out などの切断シナリオで read loop が終了するか確認する。
- Android 17 / targetSdkVersion 37 のテスト環境が利用可能になったら、RFCOMM read loop の戻り値と exception を記録する。
- Android 17 AOSP tag 入手後に、targetSdkVersion gate、RFCOMM read path、compat Change ID を再確認する。

## Recommended

- `InputStream.read()` の標準仕様に沿い、0 より大きい値を data length、`-1` を EOF、`IOException` を abnormal error として分ける。
- read thread / coroutine の cancellation、socket close、stream close、reconnect flow を統一的に整理する。
- Bluetooth transfer-data guide の recommended implementation に read loop を合わせる。
- LE CoC と RFCOMM の切断処理を共通化できる場合は、`-1` EOF handling を共通 path に入れる。

## Optional

- Bluetooth device vendor / firmware ごとに disconnect behavior が異ならないか、主要 device で regression test を追加する。
- 接続状態 telemetry を追加し、read loop が終了しない状態や再接続失敗を検出する。

---

# Verification Method

## Matrix

| Device OS | targetSdkVersion | Compat flag | Expected behavior |
| --- | --- | --- | --- |
| Android 16 | 36 | default | Android 16 baseline。RFCOMM disconnect 時の `read()` behavior は Android 17 tag 比較待ち。 |
| Android 17 | 36 | default | Unknown。この section は targetSdkVersion 37 向けだが、AOSP gate 未確認。 |
| Android 17 | 37 | default | 公式文書上、RFCOMM `BluetoothSocket` input stream `read()` は socket closed / connection dropped 時に `-1` を返す。 |
| Android 17 | 36 | force-enabled if available | Unknown。Compat Change ID 未確認。 |
| Android 17 | 37 | force-disabled if available | Unknown。Compat Change ID 未確認。 |

## Steps

- targetSdk変更: targetSdkVersion 36 と 37 の test build を用意する。
- compat framework command: 未確認。Android 17 compat framework entry / Change ID が判明後に記録する。
- テスト方法: RFCOMM `BluetoothSocket` を接続し、remote disconnect、local socket close、Bluetooth adapter off、range out を分けて `InputStream.read()` の return value / exception を記録する。
- 再現手順: Android 17 device で対象アプリを install し、RFCOMM device と接続する。read loop 実行中に remote device 側から切断し、`read()` が `-1` を返すか、`IOException` を throw するか、loop が終了するかを確認する。
- 期待結果: targetSdkVersion 37 のアプリでは、socket closed / connection dropped 時に `read()` が `-1` を返し、app がそれを EOF として扱って loop を終了する。具体的な targetSdkVersion 36 との差分は AOSP tag と実機検証待ち。

---

# Conclusion

公式文書上、Android 17 / targetSdkVersion 37 のアプリでは RFCOMM `BluetoothSocket` の `InputStream.read()` が socket close / connection dropped 時に `-1` を返す。`IOException` だけに依存する read loop は終了しない可能性があるため、`-1` を EOF として扱う修正が必要である。

ただし、Android 17 AOSP tag が local checkout にないため、実装 gate、RFCOMM read path、targetSdkVersion 36 との差分、compat framework の確認は未完了である。最終的な適用分類と顧客向け確定説明は、Android 17 AOSP tag 入手後に再調査が必要である。

---

# Human Decision Placeholder

Final Priority:
- Human decision required

Final Severity:
- Human decision required

Release Readiness:
- Human decision required

Customer Communication Priority:
- Human decision required

Decision:
- Further investigation required

Decision notes:
- Android 17 AOSP tag 入手後に、AOSP evidence と compat framework evidence を確認してから最終判断する。

---

# References

## Documentation

- https://developer.android.com/about/versions/17/behavior-changes-17
- https://developer.android.com/reference/java/io/InputStream?#read(byte%5B%5D)
- https://developer.android.com/reference/android/bluetooth/BluetoothSocket
- https://developer.android.com/develop/connectivity/bluetooth/transfer-data#example
- https://developer.android.com/develop/connectivity/bluetooth/transfer-data

## AOSP

- Not available for Android 17 in local `frameworks-base`.
- From tag checked: `android-16.0.0_r4`
- To tag checked: no local `android-17*` tag found.
