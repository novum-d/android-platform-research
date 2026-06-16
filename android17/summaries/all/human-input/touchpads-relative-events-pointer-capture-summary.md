# ポインターキャプチャ中のタッチパッド相対イベント既定化 - 1ページ要約

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
- OS アップデート / 全アプリ: 公式文書上は該当候補。Android 17 の全アプリ向けページに掲載され、targetSdkVersion 条件は示されていない。
- targetSdkVersion 37 以上: 公式文書上は不要。AOSP 適用ゲートは未確認。
- その他の必須条件: アプリがポインターキャプチャを使い、入力デバイスがタッチパッドで、captured event の座標解釈に依存していること。
- Compat Change ID: 未確認
- Compat default state: 未確認

## 早見マトリクス

| シナリオ（Scenario） | 影響（Impact） |
| --- | --- |
| Android 17 / targetSdkVersion 36 | タッチパッド + ポインターキャプチャで、default の相対移動イベントが届く可能性。AOSP 適用ゲートは未確認。 |
| Android 17 / targetSdkVersion 37 | targetSdkVersion 36 と同様の可能性。公式文書に targetSdkVersion 条件なし。 |
| Android 17 / targetSdkVersion 37 + 必須条件 | 絶対座標前提のポインターキャプチャ実装で、cursor movement / remote pointer mapping が変わる可能性。 |

## 要約

Android 17 では、タッチパッドがポインターキャプチャ中にデフォルトで相対移動イベントを送る。ポインターキャプチャ中のタッチパッド event を絶対座標として扱っているアプリは、入力解釈を見直す必要がある。

## 顧客影響

- 要確認

## 影響対象

- 対象アプリ: ポインターキャプチャを使う game、remote desktop、streaming、emulator、virtualization、drawing、CAD、エディタ。
- 対象機能: camera 制御、remote cursor mapping、drag、pan、selection、viewport navigation。
- 対象条件: タッチパッド input を captured event として受け取り、絶対座標前提で処理している場合。

## 対応要否

- 必須対応: ポインターキャプチャ利用箇所で、タッチパッド event の座標解釈を確認する。
- 推奨対応: 相対移動イベント前提に処理するか、絶対座標の従来挙動が必要な場合は Android 17 以上で `requestPointerCapture(int)` と `View.POINTER_CAPTURE_MODE_ABSOLUTE` を使う。
- 不要: ポインターキャプチャを使わないアプリ、タッチパッド input を扱わないアプリ、relative delta 前提の実装では直接影響は限定的。

## テストマトリクス

| 端末 OS | targetSdkVersion | 期待挙動 |
| --- | --- | --- |
| Android 16 | 36 | 基準挙動。タッチパッド + ポインターキャプチャの event coordinate 挙動を確認。 |
| Android 17 | 36 | タッチパッド captured event は、default の相対移動イベントとして届くと公式文書は説明。 |
| Android 17 | 37 | targetSdkVersion 36 と同じ期待。targetSdkVersion 条件は公式文書に記載なし。 |

## 顧客向け説明

Android 17 では、タッチパッドをポインターキャプチャ中に使った場合、デフォルトで相対移動イベントがアプリに届くようになります。絶対座標前提の実装では cursor movement や remote pointer mapping が変わる可能性があります。

従来の絶対座標の挙動が必要な場合は、Android 17 の `requestPointerCapture(int)` で `View.POINTER_CAPTURE_MODE_ABSOLUTE` を指定してください。

## 根拠

- Official documentation: https://developer.android.com/about/versions/17/behavior-changes-all
- 検証対象の原文: Android 17 から、タッチパッドはポインターキャプチャ中に absolute coordinates ではなく、相対移動イベントをデフォルトで送る。
- AOSP ファイル: 未確認。ローカルの `frameworks-base` に `android-17*` タグがない。
- AOSP ソース文脈: 未確認。タグ間差分が実行できない。
- 差分解釈: 未分類。公式文書上は、変更された default / API addition による挙動 mitigation と読めるが、AOSP 差分による確認は Android 17 タグ待ち。
- 適用ゲートの結論: 未確認。公式文書上は Android 17 全アプリ + タッチパッド + ポインターキャプチャ条件。targetSdkVersion 適用ゲート / Compat framework の根拠は未取得。

## 人間の判断欄

最終優先度（Final Priority）:
- Human decision required

判断（Decision）:
- Android 17 AOSP タグが利用可能になった後に追加調査が必要
