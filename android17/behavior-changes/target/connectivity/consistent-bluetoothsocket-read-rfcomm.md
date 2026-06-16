# RFCOMM の BluetoothSocket read() 挙動の一貫化

## 基本情報（Metadata）

### 調査対象 Android バージョン

From:
- android-16.0.0_r4

To:
- TBD: Android 17 AOSP タグ

Previous targetSdkVersion:
- 36

Target targetSdkVersion:
- 37

### Behavior Change 文書

Document:
https://developer.android.com/about/versions/17/behavior-changes-17

Related documents:
- https://developer.android.com/reference/java/io/InputStream?#read(byte%5B%5D)
- https://developer.android.com/reference/android/bluetooth/BluetoothSocket
- https://developer.android.com/develop/connectivity/bluetooth/transfer-data#example
- https://developer.android.com/develop/connectivity/bluetooth/transfer-data

Section:
RFCOMM の BluetoothSocket read() 挙動の一貫化

Page type:
- Apps targeting Android 17 or higher

### 分類スナップショット

主分類（Primary classification）:
- UNKNOWN_NEEDS_MORE_EVIDENCE

公式文書からの初期適用条件判断:
- 公式文書は、targetSdkVersion 37 のアプリでは、RFCOMM-based `BluetoothSocket` から取得した `InputStream` の `read()` が、socket close または接続 dropped 時に `-1` を返すと説明している。
- この変更は LE CoC sockets と一貫した挙動にし、標準 `InputStream.read()` documentation の end-of-stream 仕様に合わせるためのものと説明されている。
- `IOException` の catch だけで read loop を抜ける実装は影響を受ける可能性があり、`read()` の戻り値 `-1` を明示的に確認する必要がある。
- ただし、ローカルの `frameworks-base` に Android 17 AOSP タグがないため、RFCOMM read パス、targetSdkVersion 適用ゲート、socket close / remote disconnect 時の戻り値、LE CoC との差分、Compat Change ID、default state は未検証である。確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

早見表:

| 確認項目 | 回答 | 根拠 |
| --- | --- | --- |
| Android 17 に OS アップデートしただけで適用されるか | 未確認 | 公式文書は Android 17 を対象とするアプリ / API level 37 と述べるが、AOSP 適用ゲートは未確認。 |
| targetSdkVersion 37 以上が必要か | その可能性が高いが未検証 | 原文は targetSdkVersion 37 を明示している。 |
| 追加の実行時条件があるか | あり | RFCOMM-based `BluetoothSocket`、`InputStream.read()`、socket close / 接続 dropped、read loop 実装が関係する。 |
| Compat Change ID が関係するか | 未確認 | Android 17 タグと Compat framework の根拠が未確認。 |

### 調査日（Investigation Date）

2026-06-11

### 信頼度

- 低

### 適用条件分類（Applicability Classification）

適用される条件（Applies when）:
- [ ] Android 17 上の全アプリ（targetSdkVersion に依存しない）
- [ ] Android 17 以上で targetSdkVersion >= 37
- [ ] targetSdkVersion >= 37, with additional runtime conditions
- [ ] Mainline / Google Play system update dependent
- [ ] API addition only, not a behavior change
- [x] 未確認 / 追加根拠が必要

必要な実行時条件:
- Android バージョン: Android 17 以上が前提と考えられるが、AOSP タグは未取得。
- targetSdkVersion: 公式文書上は 37。
- 端末/フォームファクター: 公式抜粋では条件なし。Bluetooth RFCOMM を利用できる端末が前提。
- Permission/API/コンポーネント条件: RFCOMM-based `BluetoothSocket`、`BluetoothSocket.getInputStream()`、`InputStream.read()`、socket close / remote disconnect。
- アプリ状態/プロセス条件: アプリが RFCOMM socket の read loop で data を読み取っている時点。

Compat framework:
- Change ID: 未確認
- 変更名: 未確認
- default state: 未確認
- テスト時の切り替え可否: 未確認

分類信頼度:
- 低

分類根拠:
- Official documentation page: `behavior-changes-17`
- 検証対象の適用条件文: Android 17 を対象とするアプリ / API level 37, RFCOMM `BluetoothSocket` input stream `read()` returns `-1` on socket closed / connection dropped.
- AOSP targetSdk 適用ゲート: 未確認。ローカルの `frameworks-base` に `android-17*` タグがない。
- Compat framework エントリ: 未確認。Android 17 Compat framework の根拠が未取得。

---

# エグゼクティブサマリー

Android 17 / targetSdkVersion 37 のアプリでは、RFCOMM-based `BluetoothSocket` の `InputStream.read()` が、socket close または接続 dropped 時に `-1` を返す、と公式文書は説明している。これは LE CoC socket と挙動を揃え、`InputStream.read()` の end-of-stream 仕様に合わせるための変更である。

これまで `IOException` が throw されることだけを期待して read loop を終了していたアプリは、`read()` が `-1` を返した場合に loop が抜けず、無限ループ、空読み、切断検出遅延などを起こす可能性がある。RFCOMM read loop は `-1` を明示的にチェックする必要がある。

ただし、現時点のローカルの `frameworks-base` には Android 17 AOSP タグがないため、実装差分、targetSdkVersion 適用ゲート、ネイティブ / Bluetooth stack の read パス、Compat Change ID は未確認である。

---

# 公式ドキュメント確認

## 原文（Statement）

Page title:
- Behavior changes: Apps targeting Android 17 or higher

Page URL:
- https://developer.android.com/about/versions/17/behavior-changes-17

Page type:
- Android 17 を対象とするアプリ

Section title:
- RFCOMM の BluetoothSocket read() 挙動の一貫化

検証対象の原文:

> Android 17 (API level 37) を対象とするアプリでは、RFCOMM ベースの `BluetoothSocket` から取得した `InputStream` の `read()` メソッドが、ソケットが閉じられた場合または接続が切断された場合に `-1` を返す。

提供された公式文書の抜粋は、この変更により RFCOMM の挙動が LE CoC ソケットおよび標準の `InputStream.read()` ドキュメントに揃うと説明している。読み取りループを抜けるために `IOException` の捕捉だけに依存しているアプリは、`-1` を明示的に確認する必要がある。

## 解釈（解釈）

この変更は、RFCOMM `BluetoothSocket` のストリーム終端表現を Java `InputStream` の標準挙動に合わせる互換性挙動変更である。切断時に例外だけを期待するのではなく、`read()` の戻り値が `-1` の場合もストリーム終端として扱う必要がある。

アプリ開発者にとって重要なのは、targetSdkVersion 37 へ更新すると、remote 端末 disconnect や socket close が `IOException` ではなく `-1` return として観測される可能性がある点である。read loop の終了条件に `bytes == -1` を含める必要がある。

---

# 変更内容

公式文書上の変更点:
- targetSdkVersion 37 のアプリで、RFCOMM-based `BluetoothSocket` から取得した `InputStream.read()` が socket closed / 接続 dropped 時に `-1` を返す。
- 変更の目的は、RFCOMM socket の挙動を LE CoC sockets と一貫させること。
- 変更は、end of stream 到達時に `-1` を返すという標準 `InputStream.read()` documentation と整合する。
- `IOException` catch だけで read loop を抜けるアプリは影響を受ける可能性がある。
- BluetoothSocket read loop は `-1` return を明示的に確認し、remote disconnect / socket close 時に正しく終了する必要がある。

AOSP で未確認の点:
- Android 16 基準挙動で RFCOMM socket close / disconnect 時に `read()` が `IOException` を throw していたか、または別の値を返していたか。
- Android 17 で RFCOMM read パスが `-1` return に変更された実装箇所。
- targetSdkVersion 37 適用ゲートの実装箇所。
- `read(byte[])`、`read(byte[], int, int)`、single-byte `read()` の対象範囲。
- ローカル close と remote disconnect の扱い差。
- LE CoC socket の既存挙動との整合。
- Bluetooth module / ネイティブ stack と `frameworks-base` API 境界。
- Compat Change ID と default state。

## 適用条件（Applicability）

公式文書の一次判断では、Android 17 以上、targetSdkVersion 37、RFCOMM-based `BluetoothSocket` の `InputStream.read()` を使うアプリに適用される。AOSP タグが未取得のため、確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

### OS アップデート時の挙動

- Android 17 にアップデートしただけで適用されるか: 未確認
- targetSdkVersion に依存しない根拠: なし。原文は Android 17 を対象とするアプリ / API level 37 と明示している。
- Android 16 以前での挙動: 未確認。Android 17 タグとの明示的な比較ができないため、Android 16 source だけから platform 根拠として断定しない。

### targetSdkVersion 37 以上での挙動

- targetSdkVersion 37 以上で適用されるか: 公式文書上は Yes と読めるが、AOSP 適用ゲートは未確認。
- Android 17 以外で targetSdkVersion 37 にした場合の挙動: 未確認。公式文書は Android 17 挙動変更として説明しているため、Android 17 platform の挙動として扱う。
- opt-out / temporary override の有無: 未確認。公式抜粋には opt-out は示されていない。Compat framework による force enable / disable は未確認。

### その他の条件

- 端末/フォームファクター: 公式抜粋では条件なし。
- 権限: Bluetooth 接続権限が関係する可能性はあるが、今回の read 挙動適用ゲートとしては AOSP 未確認。
- API 使用: `BluetoothSocket`、RFCOMM socket、`BluetoothSocket.getInputStream()`、`InputStream.read()`。
- manifest attribute: Bluetooth 権限 declaration / 実行時権限付与が関係する可能性。
- コンポーネント境界: アプリ read loop、framework `BluetoothSocket` Java API、Bluetooth stack / ネイティブ socket、remote 端末接続状態にまたがる。

---

# AOSP 調査

## checkout 状態

根拠利用前に確認したコマンド:

```bash
git -C frameworks-base status --short
git -C frameworks-base tag --list android-16.0.0_r4
git -C frameworks-base tag --list 'android-17*'
```

結果:
- `frameworks-base` 作業ツリー: 調査時点で clean。
- From タグ: `android-16.0.0_r4` は存在する。
- To タグ: ローカルに `android-17*` タグは存在しない。

根拠上の制約:
- Android 17 AOSP タグがローカルの `frameworks-base` に存在しないため、`git -C frameworks-base diff android-16.0.0_r4 <android-17-tag> -- ...` による明示的なタグ比較を実行できない。
- Repository rule に従い、Android 17 作業ツリーや推測によるソース根拠は採用しない。
- Bluetooth socket の実装本体は `frameworks-base` ではなく Bluetooth module / packages / ネイティブ stack 側にある可能性がある。Android 17 タグ入手後は `frameworks-base` API 境界と Bluetooth module implementation の両方を確認する必要がある。
- この制約により、AOSP に基づく結論は高信頼度にできない。

## 関連ファイル

未確認。Android 17 AOSP タグ取得後に、少なくとも以下の候補をタグ比較で確認する必要がある。

- `core/java/android/bluetooth/BluetoothSocket.java`
- `core/java/android/bluetooth/BluetoothDevice.java`
- `core/java/android/bluetooth/BluetoothAdapter.java`
- Compat framework 定義ファイル内の BluetoothSocket / RFCOMM / targetSdkVersion 37 関連 Change ID
- Bluetooth module / packages 側の RFCOMM socket read implementation
- ネイティブ Bluetooth stack / socket bridge の close / disconnect handling

## 確認したソース文脈

Android 17 AOSP タグがないため、ソース文脈は未レビュー。

| ファイル / シンボル | Android 16 基準挙動 | Android 17 挙動 | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| 未レビュー | 未レビュー | 未レビュー | Android 17 タグがないため、公式文書の記述を AOSP 差分で検証できない。 |

必須記入項目:
- 入口 / 呼び出し元: 未確認。想定される入口は、アプリの `InputStream.read()`、`BluetoothSocket.getInputStream()`、RFCOMM socket read、remote disconnect / ローカル close handling だが、AOSP 根拠としては未採用。
- Relevant class or service responsibility: 未確認。
- アプリ API またはシステムイベントから変更箇所までの実行時パス: 未確認。
- 除外した無関係なコードパス: Android 17 タグ不在のため、ソースパスの採否判断自体を保留。

## 差分解釈

| 確認した差分 | 解釈 | 挙動変更との関係 | 信頼度 |
| --- | --- | --- | --- |
| Android 17 タグ間差分は利用不可 | ソース差分の種別はまだ分類できない | 公式文書の `read()` return `-1` 挙動、targetSdkVersion 37 適用ゲート、RFCOMM / LE CoC consistency をソース差分で裏取りできていない | 低 |

必須分類:
- Added behavior: 未確認。
- Removed behavior: 未確認。
- Changed condition / gate: 未確認。targetSdkVersion 37 適用ゲートがある可能性は高いが、AOSP では未確認。
- Changed default: 未確認。
- No behavior change found: 未確認。タグ不在のため「no behavior change」とは判断しない。

## 事実

事実:
- 公式 Behavior Change 文書は、targetSdkVersion 37 のアプリで RFCOMM-based `BluetoothSocket` の `InputStream.read()` が socket closed / 接続 dropped 時に `-1` を返すと述べている。
- 公式文書は、この変更が LE CoC sockets と RFCOMM socket の挙動を一貫させると述べている。
- 公式文書は、この変更が end of stream 到達時に `-1` を返す標準 `InputStream.read()` documentation と整合すると述べている。
- 公式文書は、`IOException` catch だけに依存する read loop が影響を受ける可能性があり、`-1` を明示的に確認すべきと述べている。
- ローカルの `frameworks-base` には `android-16.0.0_r4` タグがある。
- ローカルの `frameworks-base` には `android-17*` タグがない。
- 調査時点で `frameworks-base` 作業ツリーは clean。

観察:
- 公式ページ種別は targetSdkVersion 37 以上向けである。
- 原文は "For Android 17 を対象とするアプリ (API level 37)" と明示しており、targetSdkVersion 37 適用ゲートがある可能性が高い。
- この項目は targetSdkVersion 37 条件に加えて、RFCOMM-based `BluetoothSocket` と socket close / 接続 dropped という API 使用 / 実行時条件を含む。
- 仕様としては Java `InputStream` の標準 EOF handling に近づく変更であり、例外駆動の read loop が互換性リスクになる。
- AOSP タグがないため、実装が本当に targetSdkVersion 37 適用ゲートで制御されているかは未確認。
- Compat framework エントリの有無も未確認。

仮説:
- Android 17 / targetSdkVersion 37 では、RFCOMM remote disconnect 時に `read(byte[])` が `IOException` ではなく `-1` を返す可能性が高い。
- Android 17 / targetSdkVersion 36 のアプリでは旧挙動が維持される可能性があるが、AOSP 適用ゲートが未確認のため断定しない。
- `IOException` catch だけを終了条件にした loop は、`-1` を data length として扱って誤動作する、または loop 終了しない可能性がある。

結論:
- 現時点で顧客向けに確定できるのは、「公式文書上は Android 17 / targetSdkVersion 37 の RFCOMM `BluetoothSocket` read loop では `read()` の `-1` return を EOF として扱う必要がある」という範囲まで。
- AOSP 適用ゲート、RFCOMM read implementation、失敗 / EOF 挙動、Compat framework default state が未確認のため、主分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

## 適用ゲート根拠

- targetSdkVersion 適用ゲート: 未確認。公式文書は targetSdkVersion 37 を示すが、AOSP 適用ゲート根拠はない。
- CompatChanges.isChangeEnabled / ChangeId: 未確認。Android 17 タグがないため検索未実施。
- @EnabledAfter / @EnabledSince / default state: 未確認。Android 17 タグがないため検索未実施。
- Build.VERSION / SDK_INT 適用ゲート: 未確認。
- DeviceConfig / resources 設定: 未確認。
- 権限/AppOps 適用ゲート: 未確認。Bluetooth 権限は利用条件として関係する可能性があるが、read 挙動適用ゲートとしては未確認。
- Manifest/property 適用ゲート: 未確認。
- 適用ゲート未検出: 未確認。Android 17 タグがないため「適用ゲートがない」とは判断しない。
- 適用ゲートの結論: 未確認。公式文書の wording から targetSdkVersion 37 + RFCOMM `BluetoothSocket` + close / disconnect 条件と推定されるが、AOSP で検証できていない。
- ソース文脈からの推論: ソース文脈未レビューのため未確定。

---

# 影響分析

## 影響を受けるアプリ

影響を受ける可能性があるアプリ:
- RFCOMM `BluetoothSocket` で serial-like data transfer を行うアプリ。
- `BluetoothSocket.getInputStream().read()` の戻り値 `-1` を確認していないアプリ。
- `IOException` catch だけで read loop を終了するアプリ。
- remote 端末 disconnect / socket close 時の EOF handling を検証していない Bluetooth peripheral / embedded 端末 / printer / scanner / IoT 連携アプリ。
- targetSdkVersion 37 への更新を予定している Bluetooth Classic / SPP 相当の通信アプリ。

## 影響を受けにくいアプリ

影響が限定的または対象外と考えられるケース:
- Bluetooth RFCOMM を使わないアプリ。
- LE CoC socket だけを使うアプリ。
- `InputStream.read()` の `-1` return をすでに EOF として扱っているアプリ。
- socket close / disconnect handling を byte count と exception の両方で処理しているアプリ。
- Android 17 AOSP タグ取得後に対象外適用ゲートや exemption が確認されたケース。

---

# 顧客影響

顧客説明用。

## 影響度

- Human decision required

※ 仮評価。最終判断は人間が行う。

## ビジネス影響

- ユーザー影響: Bluetooth 端末切断時に read loop が終了しない、再接続できない、UI が接続中のままになる、データ転送スレッドが残る可能性がある。
- 運用影響: remote disconnect、ローカル close、通信エラー、再接続のテスト matrix を見直す必要がある可能性がある。
- 開発影響: RFCOMM read loop の終了条件修正、`-1` handling、thread / coroutine cancellation、resource close、再接続処理の更新が必要になる可能性がある。

---

# サービス影響例

このセクションは、公式文書と AOSP 根拠 から導いた「起こりうる影響例」を記録する。特定サービスで実際に発生確認した事実ではない。

## 例1（Example 1）: Bluetooth プリンター / スキャナー連携

- 対象サービス例: モバイル POS、配送ラベル印刷、バーコードスキャナー、店舗端末連携。
- 影響を受ける実装パターン: RFCOMM `BluetoothSocket` の read loop を `IOException` catch だけで終了する実装。
- 発生条件: Android 17 / targetSdkVersion 37 で socket close / 接続 dropped 時に `read()` が `-1` を返す場合。
- ユーザーに見える症状: 切断後も接続中表示のままになる、再接続できない、印刷 / 読み取り job が止まる可能性。
- 開発・運用への影響: read loop、thread cancellation、再接続フロー、端末 disconnect テストの見直しが必要になる可能性。
- 推奨対応候補: `bytesRead == -1` を EOF として扱い、socket close と reconnect 処理へ進む。
- 根拠: 公式文書の記述とレポートの 期待される挙動。
- 信頼度: 低
- 注意: targetSdkVersion 適用ゲートと exact read パスは AOSP タグ待ち。

## 例2（Example 2）: IoT / embedded 端末 の serial data transfer

- 対象サービス例: 計測器、医療周辺機器、車載 / 工場デバイス、Bluetooth SPP 相当通信。
- 影響を受ける実装パターン: remote disconnect 時に exception が必ず発生すると仮定した parser / protocol loop。
- 発生条件: `read()` が `-1` を返し、アプリがそれを data length として扱う、または無視する場合。
- ユーザーに見える症状: データ更新が止まる、切断検出が遅れる、再接続操作が効かない可能性。
- 開発・運用への影響: protocol state machine、EOF handling、端末 firmware 別 regression test が必要になる可能性。
- 推奨対応候補: `>0` data、`-1` EOF、`IOException` abnormal error を分けて処理する。
- 根拠: 公式文書の記述とレポートの 対応候補。
- 信頼度: 低
- 注意: 実端末ごとの差異は実機検証が必要。

---

# 対応候補

## 必須対応（Must）

- RFCOMM `BluetoothSocket` の read loop を棚卸しし、`read()` の戻り値 `-1` を確認しているか確認する。
- `IOException` catch だけで loop を終了している箇所を修正し、`bytesRead == -1` を EOF / disconnect として扱う。
- remote 端末 disconnect、ローカル socket close、Bluetooth off、range out などの切断シナリオで read loop が終了するか確認する。
- Android 17 / targetSdkVersion 37 のテスト環境が利用可能になったら、RFCOMM read loop の戻り値と exception を記録する。
- Android 17 AOSP タグ入手後に、targetSdkVersion 適用ゲート、RFCOMM read パス、Compat Change ID を再確認する。

## 推奨対応（Recommended）

- `InputStream.read()` の標準仕様に沿い、0 より大きい値を data length、`-1` を EOF、`IOException` を abnormal error として分ける。
- read thread / coroutine の cancellation、socket close、stream close、reconnect フローを統一的に整理する。
- Bluetooth transfer-data guide の recommended implementation に read loop を合わせる。
- LE CoC と RFCOMM の切断処理を共通化できる場合は、`-1` EOF handling を共通パスに入れる。

## 任意対応（Optional）

- Bluetooth 端末 vendor / firmware ごとに disconnect 挙動が異ならないか、主要端末で regression test を追加する。
- 接続状態テレメトリを追加し、read loop が終了しない状態や再接続失敗を検出する。

---

# 検証方法

## 検証マトリクス

| 端末 OS | targetSdkVersion | Compat flag | 期待される挙動 |
| --- | --- | --- | --- |
| Android 16 | 36 | デフォルト | Android 16 基準挙動。RFCOMM disconnect 時の `read()` 挙動は Android 17 タグ比較待ち。 |
| Android 17 | 36 | デフォルト | 未確認。この section は targetSdkVersion 37 向けだが、AOSP 適用ゲートは未確認。 |
| Android 17 | 37 | デフォルト | 公式文書上、RFCOMM `BluetoothSocket` input stream `read()` は socket closed / 接続 dropped 時に `-1` を返す。 |
| Android 17 | 36 | force-有効 if 利用可能 | 未確認。Compat Change ID は未確認。 |
| Android 17 | 37 | force-無効 if 利用可能 | 未確認。Compat Change ID は未確認。 |

## 手順

- targetSdk 変更: targetSdkVersion 36 と 37 のテスト build を用意する。
- Compat framework コマンド: 未確認。Android 17 Compat framework エントリ / Change ID が判明後に記録する。
- テスト方法: RFCOMM `BluetoothSocket` を接続し、remote disconnect、ローカル socket close、Bluetooth adapter off、range out を分けて `InputStream.read()` の return value / exception を記録する。
- 再現手順: Android 17 端末で対象アプリを install し、RFCOMM 端末と接続する。read loop 実行中に remote 端末側から切断し、`read()` が `-1` を返すか、`IOException` を throw するか、loop が終了するかを確認する。
- 期待結果: targetSdkVersion 37 のアプリでは、socket closed / 接続 dropped 時に `read()` が `-1` を返し、アプリがそれを EOF として扱って loop を終了する。具体的な targetSdkVersion 36 との差分は AOSP タグと実機検証待ち。

---

# 結論

公式文書上、Android 17 / targetSdkVersion 37 のアプリでは RFCOMM `BluetoothSocket` の `InputStream.read()` が socket close / 接続 dropped 時に `-1` を返す。`IOException` だけに依存する read loop は終了しない可能性があるため、`-1` を EOF として扱う修正が必要である。

ただし、Android 17 AOSP タグがローカル checkout にないため、実装上の適用ゲート、RFCOMM read パス、targetSdkVersion 36 との差分、Compat framework の確認は未完了である。最終的な適用分類と顧客向け確定説明は、Android 17 AOSP タグ入手後に再調査が必要である。

---

# 人間の判断欄

最終優先度（Final Priority）:
- Human decision required

最終影響度（Final Severity）:
- Human decision required

リリース判断（Release Readiness）:
- Human decision required

顧客通知優先度（Customer Communication Priority）:
- Human decision required

判断（Decision）:
- 追加調査が必要

判断メモ:
- Android 17 AOSP タグ入手後に、AOSP 根拠と Compat framework 根拠を確認してから最終判断する。

---

# 参照（References）

## ドキュメント

- https://developer.android.com/about/versions/17/behavior-changes-17
- https://developer.android.com/reference/java/io/InputStream?#read(byte%5B%5D)
- https://developer.android.com/reference/android/bluetooth/BluetoothSocket
- https://developer.android.com/develop/connectivity/bluetooth/transfer-data#example
- https://developer.android.com/develop/connectivity/bluetooth/transfer-data

## AOSP

- ローカルの `frameworks-base` では Android 17 は利用不可。
- From タグ checked: `android-16.0.0_r4`
- To タグ checked: ローカルに `android-17*` タグなし。
