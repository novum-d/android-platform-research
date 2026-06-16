# ポインターキャプチャ中のタッチパッド相対イベント既定化

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
- https://developer.android.com/about/versions/17/behavior-changes-all

Related documents:
- https://developer.android.com/reference/android/view/View#requestPointerCapture()
- https://developer.android.com/reference/android/view/View#requestPointerCapture(int)
- https://developer.android.com/reference/android/view/View#onCapturedPointerEvent(android.view.MotionEvent)
- https://developer.android.com/reference/android/view/View#POINTER_CAPTURE_MODE_RELATIVE
- https://developer.android.com/reference/android/view/View#POINTER_CAPTURE_MODE_ABSOLUTE
- https://developer.android.com/reference/android/view/MotionEvent
- https://developer.android.com/reference/android/view/InputDevice

Section:
- ポインターキャプチャ中のタッチパッド相対イベント既定化

Page type:
- Behavior changes: 全アプリ

### 分類スナップショット

主分類（Primary classification）:
- UNKNOWN_NEEDS_MORE_EVIDENCE

公式文書からの初期適用条件判断:
- 公式文書は Android 17 の `Behavior changes: all apps` ページにこの項目を掲載している。
- 公式文書は、Android 17 からタッチパッドがポインターキャプチャ中に、絶対座標ではなく相対移動イベントをデフォルトで送ると説明している。
- 公式文書は、アプリが従来と同じ絶対座標の挙動を必要とする場合は、Android 17 で導入された `requestPointerCapture(int)` と `View.POINTER_CAPTURE_MODE_ABSOLUTE` を使って要求するよう説明している。
- 原文には targetSdkVersion 条件は記載されていない。
- ただし、ローカルの `frameworks-base` に Android 17 AOSP タグがないため、input dispatch、ポインターキャプチャ、タッチパッド source 判定、Compat framework エントリは未確認である。確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

早見表:

| 確認項目 | 回答 | 根拠 |
| --- | --- | --- |
| Android 17 に OS アップデートしただけで適用されるか | その可能性が高いが、追加条件の有無は未確認 | 公式文書は全アプリ向けページに掲載し、targetSdkVersion 条件を示していない。AOSP 適用ゲートは未確認。 |
| targetSdkVersion 37 以上が必要か | 公式文書上は不要と読めるが、AOSP では未確認 | 原文に targetSdkVersion 条件はない。AOSP の targetSdkVersion 適用ゲートは未確認。 |
| 追加の実行時条件があるか | あり | アプリがポインターキャプチャを使い、入力デバイスがタッチパッドで、captured event の座標解釈に依存している場合。 |
| Compat Change ID が関係するか | 未確認 | Android 17 タグと Compat framework の根拠が未確認。 |

### 調査日（Investigation Date）

2026-06-15

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
- Android バージョン: Android 17 以上。AOSP タグ未取得のため、実装上の OS 適用ゲートは未確認。
- targetSdkVersion: 公式文書上は条件なし。AOSP の targetSdkVersion 適用ゲートは未確認。
- 端末/フォームファクター: タッチパッドを持つ端末、またはタッチパッド入力デバイスが接続された端末。
- Permission/API/コンポーネント条件: `View.requestPointerCapture()`、`View.requestPointerCapture(int)`、`View.onCapturedPointerEvent(MotionEvent)`、`MotionEvent`、`InputDevice`、pointer capture、relative pointer events。
- アプリ状態/プロセス条件: アプリがポインターキャプチャ中のタッチパッド event を処理し、絶対座標を前提にしている場合。

Compat framework:
- Change ID: 未確認
- 変更名: 未確認
- default state: 未確認
- テスト時の切り替え可否: 未確認

分類信頼度:
- 低

分類根拠:
- Official documentation page: `behavior-changes-all`
- 検証対象の適用条件文: Android 17 から、タッチパッドはポインターキャプチャ中にデフォルトで相対移動イベントを送る。
- AOSP targetSdk 適用ゲート: 未確認。ローカルの `frameworks-base` に `android-17*` タグがない。
- Compat framework エントリ: 未確認。Android 17 Compat framework の根拠が未取得。

---

# エグゼクティブサマリー

Android 17 では、タッチパッド入力がポインターキャプチャ中に、デフォルトで相対移動イベントとしてアプリに届く、と公式文書は説明している。これまでポインターキャプチャ中のタッチパッド event を絶対座標として扱っていたアプリは、Android 17 で pointer movement の解釈が変わる可能性がある。

影響を受けるのは、ポインターキャプチャを使う game、remote desktop、streaming、emulator、virtualization、drawing、CAD、エディタなどである。これらのアプリがタッチパッドの captured event を画面上の絶対位置として扱っている場合、cursor movement、camera 制御、remote pointer mapping、drag 操作などにずれが出る可能性がある。

公式文書は、従来の絶対座標の挙動が必要な場合は、Android 17 で追加された `requestPointerCapture(int)` に `View.POINTER_CAPTURE_MODE_ABSOLUTE` を指定するよう説明している。現時点ではローカルの `frameworks-base` に Android 17 AOSP タグがなく、実装上の適用ゲート、Compat Change ID、targetSdkVersion 分岐の有無を確認できない。確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE`、信頼度は低とする。

---

# 公式ドキュメント確認

## 原文（Statement）

Page title:
- Behavior changes: 全アプリ

Page URL:
- https://developer.android.com/about/versions/17/behavior-changes-all

Page type:
- 全アプリ

Section title:
- ポインターキャプチャ中のタッチパッド相対イベント既定化

検証対象の原文:
- Android 17 から、タッチパッドはポインターキャプチャ中に absolute coordinates ではなく、相対移動イベントをデフォルトで送る。
- 既存の絶対座標の挙動が必要なアプリは、Android 17 で導入された `requestPointerCapture(int)` API を使い、`View.POINTER_CAPTURE_MODE_ABSOLUTE` を渡して要求する。

## 解釈

この変更は、ポインターキャプチャ中にタッチパッド入力がアプリへ渡される default mode を変える挙動変更である。タッチパッドの captured event を relative delta として処理するアプリには自然な挙動になる一方、絶対座標を前提にしたアプリでは入力解釈が変わる可能性がある。

顧客向けには「ポインターキャプチャ全体が変わる」ではなく、「タッチパッド端末のポインターキャプチャ default が relative event になる」と説明する必要がある。mouse、stylus、touchscreen など他の device source への影響範囲は AOSP タグで確認が必要である。

---

# 変更内容

公式文書上の変更点:
- Android 17 から、タッチパッドはポインターキャプチャ中にデフォルトで相対移動イベントを送る。
- 以前と同じ絶対座標の挙動が必要なアプリは、`requestPointerCapture(int)` と `View.POINTER_CAPTURE_MODE_ABSOLUTE` を使う。
- `View.POINTER_CAPTURE_MODE_ABSOLUTE` は Android 17 で導入された API と説明されている。

AOSP で未確認の点:
- タッチパッド source 判定がどの input source / 端末 property で行われるか。
- ポインターキャプチャ mode の default がどの layer で決まるか。
- `requestPointerCapture()` と `requestPointerCapture(int)` の default mode 差分。
- `POINTER_CAPTURE_MODE_RELATIVE` / `POINTER_CAPTURE_MODE_ABSOLUTE` の API surface と input dispatch への反映。
- targetSdkVersion 適用ゲートの有無。
- Compat framework Change ID と default state。
- mouse、stylus、touchscreen、trackball、rotary など、タッチパッド以外の入力デバイスへの影響有無。

## 適用条件（Applicability）

この変更がいつ適用されるかを OS 条件と targetSdkVersion 条件に分けて説明する。

### OS アップデート時の挙動

- Android 17 に OS アップデートしただけで適用されるか: 公式文書上は Yes / Conditional。全アプリ向けページに掲載され、targetSdkVersion 条件は示されていない。ただし AOSP 適用ゲートは未確認。
- targetSdkVersion に依存しない根拠: 原文に targetSdkVersion 条件がない。
- Android 16 以前での挙動: 公式文書は、Android 17 からタッチパッドがデフォルトで relative event を送ると説明している。Android 16 の基準挙動におけるポインターキャプチャ mode は AOSP 差分では未確認。

### targetSdkVersion 37 以上での挙動

- targetSdkVersion 37 以上で適用されるか: 公式文書上、targetSdkVersion 37 は必要条件ではない。
- Android 17 以外で targetSdkVersion 37 にした場合の挙動: 未確認。公式文書は Android 17 platform の挙動として説明している。
- opt-out / temporary override の有無: 絶対座標の従来挙動が必要な場合の明示的な要求として `View.POINTER_CAPTURE_MODE_ABSOLUTE` が示されている。compat opt-out の有無は未確認。

### その他の条件

- 端末/フォームファクター: タッチパッド入力デバイスが存在する端末。laptop、tablet + キーボード / trackpad、desktop mode、external タッチパッドなどが候補。
- API 使用: アプリがポインターキャプチャを要求し、`onCapturedPointerEvent(MotionEvent)` などで captured event を処理する。
- 入力デバイス条件: 公式文書の対象はタッチパッド。mouse / stylus / touchscreen などの扱いは未確認。
- アプリ挙動条件: captured event の `MotionEvent` を絶対座標として扱う場合に影響が大きい。
- 影響を受けにくいケース: ポインターキャプチャを使わないアプリ、タッチパッド event を処理しないアプリ、relative delta を前提にしたポインターキャプチャ実装。

---

# AOSP 調査

## checkout 状態

確認コマンド:

```bash
git -C frameworks-base status --short
git -C frameworks-base tag --list android-16.0.0_r4
git -C frameworks-base tag --list 'android-17*'
```

結果:
- `frameworks-base` の `status --short` は空で、dirty な作業ツリーは確認されなかった。
- `android-16.0.0_r4` タグは存在する。
- `android-17*` タグはローカル checkout に存在しない。

根拠上の制約:
- Android 17 AOSP タグがローカルの `frameworks-base` にないため、`android-16.0.0_r4` と Android 17 タグの明示的なソース差分は実行できない。
- そのため、ローカル作業ツリーや未確定 branch を platform 根拠として扱わない。
- 本レポートの AOSP に基づく結論は低信頼度に留める。

## 関連ファイル

Android 17 AOSP タグ未取得のため、タグ間差分に基づく関連ファイルは未確定。

Android 17 タグ 公開後に確認すべき候補:
- `core/java/android/view/View.java`
- `core/java/android/view/MotionEvent.java`
- `core/java/android/view/InputDevice.java`
- `core/java/android/view/ViewRootImpl.java`
- `services/core/java/com/android/server/input/` 以下の input dispatch / ポインターキャプチャパス
- `native/services/inputflinger/` または input dispatcher / reader に関係する AOSP project
- API surface file の `requestPointerCapture(int)`、`POINTER_CAPTURE_MODE_RELATIVE`、`POINTER_CAPTURE_MODE_ABSOLUTE`
- Compat framework 定義ファイル内のポインターキャプチャ / タッチパッド relative event 関連 Change ID

Note:
- 実際の input dispatch は `frameworks-base` 以外の inputflinger / ネイティブ service 側にある可能性がある。Android 17 タグ入手後は該当 project も根拠対象として確認する必要がある。

## 確認したソース文脈

AOSP タグ間差分は未実行。以下は公式文書から見た確認予定のソース文脈であり、AOSP 根拠ではない。

| ファイル / シンボル | Android 16 の基準挙動 | Android 17 の挙動 | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| `View.requestPointerCapture()` | 未確認 | default mode がタッチパッドで relative になると公式文書が説明 | アプリがポインターキャプチャを開始する主要 API であり default mode の入口になるため |
| `View.requestPointerCapture(int)` | API なしまたは未確認 | absolute 挙動が必要な場合に `POINTER_CAPTURE_MODE_ABSOLUTE` を指定すると公式文書が説明 | 新しい明示的な mode selection API の確認が必要なため |
| `View.onCapturedPointerEvent(MotionEvent)` | 未確認 | 相対移動イベントが配送される可能性 | アプリが captured event を受け取る callback であるため |
| input dispatch / ポインターキャプチャパス | 未確認 | タッチパッド event の coordinate mode が default relative に変わる可能性 | 実際に event coordinate / axis を変換する適用 point の候補であるため |
| 入力デバイス classification パス | 未確認 | タッチパッドのみが対象と公式文書が説明 | mouse / stylus / touchscreen との切り分けに必要なため |
| Compat framework エントリ | 未確認 | targetSdkVersion 適用ゲートの有無は不明 | 全アプリ型か targetSdkVersion 適用ゲート型かの確定に必要なため |

必須記入項目:
- 入口 / 呼び出し元: 未確認。想定される入口は、アプリの `requestPointerCapture()` / `requestPointerCapture(int)` -> ViewRoot / Window / input dispatcher -> captured `MotionEvent` の配送 -> `onCapturedPointerEvent(MotionEvent)`。
- Relevant class or service responsibility: pointer capture request、入力デバイス classification、motion event coordinate mode、captured event dispatch。
- アプリ API またはシステムイベントから変更箇所までの実行時パス: アプリがポインターキャプチャを要求 -> タッチパッド event が発生 -> Android 17 は default relative mode で captured motion event を配送 -> アプリが絶対座標を必要とする場合は `POINTER_CAPTURE_MODE_ABSOLUTE` を指定、というパスが想定される。AOSP 根拠としては未確認。
- 除外した無関係なコードパス: タグ間差分未実行のため、除外判断は未完了。

## 差分解釈

| 確認した差分 | 解釈 | 挙動変更との関係 | 信頼度 |
| --- | --- | --- | --- |
| Android 17 タグ未取得のためソース差分は未確認 | 公式文書上は、変更された default / API addition による挙動 mitigation と読める | タッチパッドのポインターキャプチャ default が relative event に変わり、absolute mode を明示要求できると説明されている | 低 |

必須分類:
- Added behavior: 未確認。`requestPointerCapture(int)` とポインターキャプチャ mode constants が追加された可能性がある。
- Removed behavior: 未確認。タッチパッドのポインターキャプチャにおける implicit absolute default が削除または限定された可能性がある。
- Changed condition / gate: 未確認。タッチパッド端末かつポインターキャプチャ中という条件で event mode が変わる可能性がある。
- Changed default: 公式文書上は該当候補。タッチパッドのポインターキャプチャ default が相対移動イベントになると読める。
- No behavior change found: 現時点では公式文書上の説明と矛盾するため候補ではないが、AOSP タグ間差分で確認が必要。

---

# 影響分析

## 影響を受ける可能性があるアプリ

- ポインターキャプチャを使う game。
- remote desktop、VNC、cloud gaming、game streaming、PC streaming app。
- emulator、virtualization、container、remote 制御アプリ。
- drawing、CAD、エディタ、3D viewport など pointer movement を細かく扱う productivity アプリ。
- laptop / tablet + タッチパッド / desktop mode を重視するアプリ。

## 影響を受けにくいアプリ

- ポインターキャプチャを使わないアプリ。
- タッチパッド input を想定していないアプリ。
- captured pointer event を relative delta として扱っているアプリ。
- touchscreen の通常 touch event のみを扱うアプリ。
- mouse / stylus など、タッチパッド以外の入力デバイスのみを対象にしているアプリ。ただし AOSP タグで device source の扱い確認が必要。

## 顧客向けリスク

- cursor movement や camera 画面回転が想定より速い、遅い、または位置ずれする。
- remote desktop / streaming で、タッチパッド操作が remote cursor の絶対位置と合わない。
- drawing / CAD / エディタで drag、pan、selection、viewport 操作が誤動作する。
- automated input tests が captured タッチパッド event の座標前提で失敗する。

---

# 対応候補

## 実装対応（Implementation）

- ポインターキャプチャを使う箇所を棚卸しし、タッチパッド event を絶対座標と relative delta のどちらとして扱っているか確認する。
- 相対移動イベントを前提にできる機能では、Android 17 の default 挙動に合わせて delta-based processing に整理する。
- 絶対座標の従来挙動が必要な場合は、Android 17 以上で `requestPointerCapture(int)` に `View.POINTER_CAPTURE_MODE_ABSOLUTE` を指定する。
- source / tool type / 入力デバイスを確認し、タッチパッド、mouse、stylus、touchscreen の処理を同一視しない。
- Android 17 未満との互換性を保つため、新 API 呼び出しは API level guard または reflection / compatibility wrapper で分岐する。

## 検証対応（Testing）

- Android 16 / targetSdkVersion 36 で、ポインターキャプチャ中のタッチパッド event の基準挙動を確認する。
- Android 17 / targetSdkVersion 36 と Android 17 / targetSdkVersion 37 の両方で、タッチパッドのポインターキャプチャにおける event coordinates / axes / deltas を確認する。
- `requestPointerCapture()` と `requestPointerCapture(int, ABSOLUTE)` 相当の挙動を分けて確認する。
- タッチパッド、mouse、touchscreen、stylus を別々に確認する。
- remote pointer mapping、camera 制御、drag、pan、selection、viewport navigation など、座標解釈に依存するユーザーフローを確認する。

## 顧客説明候補（Customer Explanation）

Android 17 では、タッチパッドをポインターキャプチャ中に使った場合、デフォルトで相対移動イベントがアプリに届くようになります。ポインターキャプチャ中のタッチパッド event を絶対座標として扱っているアプリでは、cursor movement や remote pointer mapping が変わる可能性があります。従来の絶対座標の挙動が必要な場合は、Android 17 の新 API `requestPointerCapture(int)` で `View.POINTER_CAPTURE_MODE_ABSOLUTE` を指定してください。

---

# 検証マトリクス

| 端末 OS | targetSdkVersion | アプリ条件 | 期待される挙動 |
| --- | --- | --- | --- |
| Android 16 | 36 | タッチパッド + ポインターキャプチャ | 基準挙動。captured event が absolute / relative のどちらとして届くか確認。 |
| Android 17 | 36 | タッチパッド + ポインターキャプチャ + default 要求 | タッチパッド event は default で相対移動イベントとして届く可能性。公式文書上の変更対象。AOSP 適用ゲートは未確認。 |
| Android 17 | 37 | タッチパッド + ポインターキャプチャ + デフォルト 要求 | targetSdkVersion 36 と同様の可能性。公式文書に targetSdkVersion 条件なし。 |
| Android 17 | 36 / 37 | タッチパッド + `POINTER_CAPTURE_MODE_ABSOLUTE` | 絶対座標の従来挙動を要求できることを確認する。 |
| Android 17 | 36 / 37 | mouse / stylus / touchscreen + ポインターキャプチャ | タッチパッド以外への影響範囲を確認する。 |

---

# 未解決事項

- Android 17 AOSP タグ上で、タッチパッドのポインターキャプチャ default mode はどの code パスで変わっているか。
- targetSdkVersion 適用ゲートまたは Compat Change ID が存在するか。
- `requestPointerCapture()` の default mode と `requestPointerCapture(int)` の mode selection はどのように dispatch layer へ渡るか。
- タッチパッド判定は `InputDevice` source、端末 class、kernel event、InputReader classification のどれに基づくか。
- `MotionEvent` のどの座標 / axis / history が relative event として変化するか。
- mouse、stylus、touchscreen、trackball、external pointing 端末への影響範囲。

---

# 人間の判断欄

最終優先度（Final Priority）:
- Human decision required

最終影響度（Final Severity）:
- Human decision required

顧客通知要否（Customer Communication Required）:
- Human decision required

リリース判断（Release Readiness）:
- Human decision required
