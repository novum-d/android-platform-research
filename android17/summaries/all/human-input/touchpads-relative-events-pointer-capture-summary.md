# Pointer capture 中の touchpad relative event 既定化 - 1ページ要約

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

- 主分類（Primary classification）: OS_UPDATE_ALL_APPS
- OS アップデート / 全アプリ（OS update / all apps）: Yes / Conditional。Android 17 の all apps ページに掲載され、AOSP の `View.requestPointerCapture()` に targetSdkVersion ゲートは見つからない。
- targetSdkVersion 37 以上: 不要。default mode は aconfig flag により分岐し、targetSdkVersion は参照されない。
- その他の必須条件（Other required conditions）: app が pointer capture を使い、input device が touchpad で、captured event の座標解釈に依存していること。
- Compat Change ID: 確認されず
- Compat default state: compat framework ではなく aconfig flags `pointer_capture_modes` / `relative_capture_mode_by_default` に依存

## 早見マトリクス

| シナリオ | 影響 |
| --- | --- |
| Android 17 / targetSdkVersion 36 | flag 条件を満たす場合、touchpad + pointer capture で default relative motion event が届く可能性。 |
| Android 17 / targetSdkVersion 37 | targetSdkVersion 36 と同様の可能性。公式文書に targetSdkVersion 条件なし。 |
| Android 17 / targetSdkVersion 37 + 必須条件 | absolute coordinate 前提の pointer capture 実装で cursor movement / remote pointer mapping が変わる可能性。 |

## 要約

Android 17 では、touchpad が pointer capture 中に default で relative motion event を deliver する。AOSP では `View.requestPointerCapture()` が `pointerCaptureModes()` と `relativeCaptureModeByDefault()` を確認し、条件を満たす場合に `POINTER_CAPTURE_MODE_RELATIVE` を request する。

absolute mode がタッチパッド上の指の位置を通知するのに対し、relative mode は前回からの移動量を通知する。指が端に到達した後に持ち上げて中央へ置き直しても、カーソルやカメラを飛ばさずに同じ方向へ操作を続けられる。そのため、リモートデスクトップ、ゲーム内カメラ、viewport navigation に適している。正確な指の位置や独自のジェスチャーが必要な機能では、absolute mode を明示する。

## 顧客影響

- pointer capture 中の touchpad event を absolute coordinate として扱うアプリでは、cursor movement、remote pointer mapping、drag / pan / selection の解釈が変わる可能性がある。

## 影響対象（Who Is Affected）

- 対象アプリ: pointer capture を使う game、remote desktop、streaming、emulator、virtualization、drawing、CAD、editor。
- 対象機能: camera control、remote cursor mapping、drag、pan、selection、viewport navigation。
- 対象条件: touchpad input を captured event として受け取り、absolute coordinate 前提で処理している場合。

## 対応要否

- 必須対応: pointer capture 利用箇所で touchpad event の座標解釈を確認する。
- 推奨対応: relative motion event 前提に処理するか、absolute coordinate behavior が必要な場合は Android 17 以上で `requestPointerCapture(int)` と `View.POINTER_CAPTURE_MODE_ABSOLUTE` を使う。
- 不要: pointer capture を使わない app、touchpad input を扱わない app、relative delta 前提の実装では直接影響は限定的。

## テストマトリクス

| 端末 OS | targetSdkVersion | 期待挙動 |
| --- | --- | --- |
| Android 16 | 36 | baseline。touchpad + pointer capture の event coordinate behavior を確認。 |
| Android 17 | 36 | touchpad captured event は default relative motion event として届くと公式文書は説明。 |
| Android 17 | 37 | targetSdkVersion 36 と同じ期待。targetSdkVersion 条件は公式文書に記載なし。 |

イベント単位のテストでは、1 本指での移動が `ACTION_MOVE` と相対値の `getX()` / `getY()`、2 本指でのスクロールが `ACTION_SCROLL` と `AXIS_VSCROLL` / `AXIS_HSCROLL` になること、およびイベントソースが `SOURCE_MOUSE_RELATIVE` になることを確認する。ユーザー操作単位のテストでは、タッチパッドの端から指を置き直したときに、カーソル、カメラ、ドラッグ、パン、選択位置が飛ばずに操作を続けられることを確認する。

## 顧客向け説明

Android 17 では、touchpad を pointer capture 中に使った場合、default で relative motion event が app に届くようになります。absolute coordinate 前提の実装では cursor movement や remote pointer mapping が変わる可能性があります。

従来の absolute coordinate behavior が必要な場合は、Android 17 の `requestPointerCapture(int)` で `View.POINTER_CAPTURE_MODE_ABSOLUTE` を指定してください。

## 根拠（Evidence）

- 公式ドキュメント: https://developer.android.com/about/versions/17/behavior-changes-all
- 検証対象の原文: Android 17 から、touchpad は pointer capture 中に absolute coordinates ではなく relative motion events を default で deliver する。
- AOSP ファイル: `View.java`, `ViewRootImpl.java`, `InputManagerService.java`, `input_framework.aconfig`, `core/api/current.txt`
- AOSP ソース文脈: app `requestPointerCapture()` -> `ViewRootImpl.requestPointerCapture(mode)` -> `InputManagerService.requestPointerCapture()` -> native input manager。
- 差分解釈: changed default / API addition。`requestPointerCapture()` default が flag 条件下で relative mode になり、`requestPointerCapture(int)` と `POINTER_CAPTURE_MODE_*` が追加された。
- ゲート結論: Android 17 で pointer capture を使い、touchpad event を扱う場合に影響し得る。targetSdkVersion ゲート / compat Change ID は確認されず、aconfig flag と device input condition に依存する。

## 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- 人間による判断が必要

判断（Decision）:
- 人間による判断が必要
