# Touchpads deliver relative events by default during pointer capture

## 基本情報（Metadata）

### 調査対象 Android バージョン（Android Versions）

比較元:
- android-16.0.0_r4

比較先:
- android-17.0.0_r1

以前の targetSdkVersion:
- 36

対象 targetSdkVersion:
- 37

### Behavior Change 文書（Behavior Change Source）

文書:
- https://developer.android.com/about/versions/17/behavior-changes-all

関連文書:
- https://developer.android.com/reference/android/view/View#requestPointerCapture()
- https://developer.android.com/reference/android/view/View#requestPointerCapture(int)
- https://developer.android.com/reference/android/view/View#onCapturedPointerEvent(android.view.MotionEvent)
- https://developer.android.com/reference/android/view/View#POINTER_CAPTURE_MODE_RELATIVE
- https://developer.android.com/reference/android/view/View#POINTER_CAPTURE_MODE_ABSOLUTE
- https://developer.android.com/reference/android/view/MotionEvent
- https://developer.android.com/reference/android/view/InputDevice

セクション:
- Touchpads deliver relative events by default during pointer capture

ページ種別:
- Behavior changes: all apps

### 分類スナップショット（Classification Snapshot）

主分類（Primary classification）:
- OS_UPDATE_ALL_APPS

公式文書からの初期適用条件判断:
- 公式文書は Android 17 の `Behavior changes: all apps` ページにこの項目を掲載している。
- 公式文書は、Android 17 から touchpad が pointer capture 中に absolute coordinate ではなく relative motion event を default で deliver すると説明している。
- 公式文書は、app が以前と同じ absolute coordinate behavior を必要とする場合は、Android 17 で導入された `requestPointerCapture(int)` と `View.POINTER_CAPTURE_MODE_ABSOLUTE` を使って request するよう説明している。
- 原文には targetSdkVersion 条件は記載されていない。
- AOSP では `View.requestPointerCapture()` が `pointerCaptureModes()` と `relativeCaptureModeByDefault()` を確認し、条件を満たす場合に `POINTER_CAPTURE_MODE_RELATIVE` を default として `ViewRootImpl.requestPointerCapture()` へ渡す。`requestPointerCapture(int)` と `POINTER_CAPTURE_MODE_ABSOLUTE` / `RELATIVE` も API surface に追加されている。
- ただし、`relative_capture_mode_by_default` の製品 default state と native inputflinger 側の touchpad event conversion は `frameworks-base` だけでは完全に確認できていないため、信頼度は Medium とする。

早見表（At-a-glance impact）:

| 確認項目 | 回答 | 根拠 |
| --- | --- | --- |
| Android 17 に OS アップデートしただけで適用されるか | Yes / Conditional | all apps ページの項目であり、`View.requestPointerCapture()` の default mode 変更に targetSdkVersion ゲートは見つからない。 |
| targetSdkVersion 37 以上が必要か | No | `View.requestPointerCapture()` は `targetSdkVersion` を参照せず、feature flag により relative / absolute を分岐する。 |
| 追加の実行時条件があるか | ある | app が pointer capture を使い、input device が touchpad で、captured event の座標解釈に依存している場合。 |
| Compat Change ID が関係するか | 根拠なし in frameworks-base | `CompatChanges.isChangeEnabled` / `@ChangeId` は確認されず、aconfig flag による制御が確認された。 |

### 調査日（Investigation Date）

2026-06-15

### 信頼度（Confidence）

- Low

### 適用条件分類（Applicability Classification）

適用される条件（Applies when）:
- [x] targetSdkVersion に関係なく Android 17 の全アプリへ適用
- [ ] Android 17 以上かつ targetSdkVersion 37 以上で適用
- [ ] targetSdkVersion 37 以上かつ追加の実行時条件を満たす場合に適用
- [ ] Mainline / Google Play system update に依存
- [ ] API 追加のみであり、挙動変更ではない
- [ ] 未確認 / 追加 evidence が必要

必要な実行時条件（Required runtime conditions）:
- Android version: Android 17 以上。
- targetSdkVersion: 条件なし。`View.requestPointerCapture()` の default mode 分岐に targetSdkVersion ゲートは確認されていない。
- Device/form factor: touchpad を持つ device、または touchpad input device が接続された device。
- Permission/API/component condition: `View.requestPointerCapture()`、`View.requestPointerCapture(int)`、`View.onCapturedPointerEvent(MotionEvent)`、`MotionEvent`、`InputDevice`、pointer capture、relative pointer events。
- App state/process condition: app が pointer capture 中の touchpad event を処理し、absolute coordinate を前提にしている場合。

Compat framework:
- Change ID: 確認されず
- 変更名: 該当なし
- 既定状態: compat framework ではなく aconfig flags `pointer_capture_modes` / `relative_capture_mode_by_default` に依存
- テスト時に切り替え可能か: aconfig flag のため build / device configuration 依存

分類信頼度（Classification confidence）:
- Medium

分類根拠（Classification evidence）:
- 公式ドキュメントページ: `behavior-changes-all`
- 検証対象の適用条件文: Android 17 から touchpad は pointer capture 中に default で relative motion event を deliver する。
- AOSP targetSdk gate: なし。確認した `View.requestPointerCapture()` path に `targetSdkVersion` / compat gate は見つからない。
- Compat framework entry: なし。`CompatChanges.isChangeEnabled` / `@ChangeId` ではなく aconfig flag による制御。

---

# エグゼクティブサマリー

Android 17 では、touchpad input が pointer capture 中に default で relative motion event として app に届く、と公式文書は説明している。これまで pointer capture 中の touchpad event を absolute coordinate として扱っていた app は、Android 17 で pointer movement の解釈が変わる可能性がある。

影響を受けるのは、pointer capture を使う game、remote desktop、streaming、emulator、virtualization、drawing、CAD、editor などである。これらの app が touchpad の captured event を画面上の absolute position として扱っている場合、cursor movement、camera control、remote pointer mapping、drag 操作などにずれが出る可能性がある。

公式文書は、従来の absolute coordinate behavior が必要な場合は Android 17 で追加された `requestPointerCapture(int)` に `View.POINTER_CAPTURE_MODE_ABSOLUTE` を指定するよう説明している。AOSP でも `View.requestPointerCapture()` の default が、flag 条件を満たす場合に `POINTER_CAPTURE_MODE_RELATIVE` へ変わることを確認した。実際の touchpad conversion は native input stack 側も関係するため、信頼度は Medium とする。

---

# 公式ドキュメント確認

## 原文（Statement）

ページタイトル:
- Behavior changes: all apps

ページ URL:
- https://developer.android.com/about/versions/17/behavior-changes-all

ページ種別:
- all apps

セクションタイトル:
- Touchpads deliver relative events by default during pointer capture

検証対象の原文:
- Android 17 から、touchpad は pointer capture 中に absolute coordinates ではなく relative motion events を default で deliver する。
- 既存の absolute coordinate behavior が必要な app は、Android 17 で導入された `requestPointerCapture(int)` API を使い、`View.POINTER_CAPTURE_MODE_ABSOLUTE` を渡して request する。

## 解釈（Interpretation）

この変更は、pointer capture 中に touchpad input が app へ渡される default mode を変える挙動変更である。touchpad の captured event を relative delta として処理する app には自然な挙動になる一方、absolute coordinate を前提にした app では入力解釈が変わる可能性がある。

顧客向けには「pointer capture 全体が変わる」ではなく、「touchpad device の pointer capture default が relative event になる」と説明する必要がある。mouse、stylus、touchscreen など他 device source への影響範囲は AOSP tag で確認が必要である。

---

# 変更内容（What Changed）

公式文書上の変更点:
- Android 17 から touchpad は pointer capture 中に default で relative motion event を deliver する。
- 以前と同じ absolute coordinate behavior が必要な app は、`requestPointerCapture(int)` と `View.POINTER_CAPTURE_MODE_ABSOLUTE` を使う。
- `View.POINTER_CAPTURE_MODE_ABSOLUTE` は Android 17 で導入された API と説明されている。

AOSP で確認した点 / 未確認の点:
- `View.requestPointerCapture()` は `pointerCaptureModes() && relativeCaptureModeByDefault()` が true の場合に `POINTER_CAPTURE_MODE_RELATIVE`、それ以外では `POINTER_CAPTURE_MODE_ABSOLUTE` を `ViewRootImpl.requestPointerCapture()` へ渡す。
- `requestPointerCapture(int)`、`POINTER_CAPTURE_MODE_UNCAPTURED`、`POINTER_CAPTURE_MODE_ABSOLUTE`、`POINTER_CAPTURE_MODE_RELATIVE` が API surface に追加されている。
- `InputManagerService.requestPointerCapture()` は mode を validate し、native input manager へ渡す。
- `input_framework.aconfig` に `pointer_capture_modes` と `relative_capture_mode_by_default` が追加され、説明文は touchpad gesture を mouse-like event に変換する relative mode default を示す。
- 未確認: `relative_capture_mode_by_default` の製品 default state、native inputflinger 側の exact conversion、touchpad 以外への影響有無。

## 適用条件

この変更がいつ適用されるかを OS 条件と targetSdkVersion 条件に分けて説明する。

### OS アップデート時の挙動（OS Update Behavior）

- Android 17 に OS アップデートしただけで適用されるか: Yes / Conditional。all apps ページに掲載され、`View.requestPointerCapture()` の default mode 分岐に targetSdkVersion ゲートはない。
- targetSdkVersion に依存しない根拠: 原文に targetSdkVersion 条件がなく、AOSP の `View.requestPointerCapture()` は feature flag のみで relative / absolute を分岐する。
- Android 16 以前での挙動: Android 16 の `requestPointerCapture()` は absolute mode 相当の従来挙動。Android 17 では flag 条件により relative mode を default にできる。

### targetSdkVersion 37 以上での挙動（targetSdkVersion 37 Behavior）

- targetSdkVersion 37 以上で適用されるか: 公式文書上、targetSdkVersion 37 は必要条件ではない。
- Android 17 以外で targetSdkVersion 37 にした場合の挙動: Unknown。公式文書は Android 17 platform behavior として説明している。
- opt-out / temporary override の有無: absolute coordinate behavior が必要な場合は `View.requestPointerCapture(View.POINTER_CAPTURE_MODE_ABSOLUTE)` を明示的に呼び出す。

### その他の条件（Other Conditions）

- device/form factor: touchpad input device が存在する device。laptop、tablet + keyboard / trackpad、desktop mode、external touchpad などが候補。
- API usage: app が pointer capture を request し、`onCapturedPointerEvent(MotionEvent)` などで captured event を処理する。
- input device condition: 公式文書の対象は touchpad。mouse / stylus / touchscreen などの扱いは未確認。
- app behavior condition: captured event の `MotionEvent` を absolute coordinate として扱う場合に影響が大きい。
- not affected / lower risk: pointer capture を使わない app、touchpad event を処理しない app、relative delta を前提にした pointer capture 実装。

---

# AOSP 調査（AOSP Investigation）

## チェックアウト状態

確認コマンド:

```bash
git -C frameworks-base status --short
git -C frameworks-base tag --list android-16.0.0_r4
git -C frameworks-base tag --list 'android-17*'
```

結果:
- `frameworks-base` の `status --short` は空で、未コミット変更 は確認されなかった。
- `android-16.0.0_r4` tag は存在する。
- `android-17.0.0_r1` tag は local checkout に存在する。

根拠上の制約:
- ソース根拠 は `android-16.0.0_r4` と `android-17.0.0_r1` の明示的な tag 比較、および `android-17.0.0_r1` 上の symbol 確認に限定した。
- `frameworks-base` working tree は clean のため、ローカル作業ツリーの変更 を platform 根拠 として誤採用するリスクは確認されていない。
- native inputflinger 側の exact conversion と flag default は未確認のため、confidence は Medium に留める。

## 関連ファイル（Related Files）

- `core/java/android/view/View.java`
- `core/java/android/view/MotionEvent.java`
- `core/java/android/view/InputDevice.java`
- `core/java/android/view/ViewRootImpl.java`
- `services/core/java/com/android/server/input/InputManagerService.java`
- `core/java/android/hardware/input/input_framework.aconfig`
- `core/api/current.txt`

注記:
- 実際の input dispatch は `frameworks-base` 以外の inputflinger / native service 側にある可能性がある。Android 17 tag 入手後は該当 project も evidence 対象として確認する必要がある。

## 確認したソース文脈（Source Context Reviewed）

| ファイル / シンボル（File / symbol） | Android 16 の基準挙動（baseline） | Android 17 の挙動 | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| `View.requestPointerCapture()` | `ViewRootImpl.requestPointerCapture(POINTER_CAPTURE_MODE_ABSOLUTE)` を呼ぶ。 | `pointerCaptureModes() && relativeCaptureModeByDefault()` が true なら `POINTER_CAPTURE_MODE_RELATIVE`、それ以外は `POINTER_CAPTURE_MODE_ABSOLUTE` を渡す。 | pointer capture default mode を決める app API entry point。 |
| `View.requestPointerCapture(int)` | API surface なし。 | explicit mode selection API として追加。 | absolute behavior が必要な場合の mitigation API。 |
| `POINTER_CAPTURE_MODE_*` constants | API surface なし。 | `UNCAPTURED` / `ABSOLUTE` / `RELATIVE` が追加。 | touchpad captured event の mode を app が指定するための API。 |
| `InputManagerService.requestPointerCapture()` | mode 引数なし、または absolute 前提。 | mode を validate し native input manager に渡す。 | framework から native input stack へ mode を伝える境界。 |
| `input_framework.aconfig` | pointer capture mode flags なし。 | `pointer_capture_modes` と `relative_capture_mode_by_default` が追加。 | default relative mode が feature flag で制御される根拠。 |

必須記入項目:
- Entry point / caller: app の `requestPointerCapture()` / `requestPointerCapture(int)` -> `ViewRootImpl.requestPointerCapture(mode)` -> `InputManagerService.requestPointerCapture()` -> native input manager -> captured `MotionEvent` delivery -> `onCapturedPointerEvent(MotionEvent)`。
- Relevant class or service responsibility: pointer capture request、input device classification、motion event coordinate mode、captured event dispatch。
- Runtime path from app API / system event to changed code: app が pointer capture を request -> `View.requestPointerCapture()` が default mode を選ぶ -> touchpad event が発生 -> native input stack が選択された capture mode に従って event を deliver -> app が absolute coordinate を必要とする場合は `POINTER_CAPTURE_MODE_ABSOLUTE` を指定する。
- Why unrelated code paths were excluded: `InputDevice` / `MotionEvent` の documentation-only diff は source / tool type 説明の補助 evidence とし、primary gate evidence には `View.requestPointerCapture()` と `InputManagerService.requestPointerCapture()` を採用した。

## 差分解釈（Diff Interpretation）

| 確認した差分（Observed diff） | 解釈（Interpretation） | Behavior Change との関係 | 信頼度（Confidence） |
| --- | --- | --- | --- |
| Android 17 tag 未取得のため source diff 未確認 | 公式文書上は changed default / API addition with behavior mitigation と読める | touchpad pointer capture default が relative event に変わり、static mode を明示 request できると説明されている | Low |

必須分類:
- Added behavior: 未確認。`requestPointerCapture(int)` と pointer capture mode constants が追加された可能性がある。
- Removed behavior: `requestPointerCapture()` が常に absolute mode 相当を request する挙動は、flag 条件下では relative mode default に置き換わる。
- Changed condition: touchpad device かつ pointer capture 中、かつ `pointer_capture_modes` / `relative_capture_mode_by_default` が有効な場合に event mode が変わる。
- Changed default: 該当。`View.requestPointerCapture()` の default mode が flag 条件下で `POINTER_CAPTURE_MODE_RELATIVE` になる。
- No behavior change: 該当しない。少なくとも `View` API boundary と `InputManagerService` boundary では source diff が確認できる。

---

# 影響分析

## 影響を受ける可能性があるアプリ（Potentially Affected Apps）

- pointer capture を使う game。
- remote desktop、VNC、cloud gaming、game streaming、PC streaming app。
- emulator、virtualization、container、remote control app。
- drawing、CAD、editor、3D viewport など pointer movement を細かく扱う productivity app。
- laptop / tablet + touchpad / desktop mode を重視する app。

## 影響を受けにくいアプリ（Less Likely Affected）

- pointer capture を使わない app。
- touchpad input を想定していない app。
- captured pointer event を relative delta として扱っている app。
- touchscreen の通常 touch event のみを扱う app。
- mouse / stylus など touchpad 以外の input device のみを対象にしている app。ただし AOSP tag で device source の扱い確認が必要。

## 顧客向けリスク（Customer-facing Risk）

- cursor movement や camera rotation が想定より速い、遅い、または位置ずれする。
- remote desktop / streaming で touchpad 操作が remote cursor の absolute position と合わない。
- drawing / CAD / editor で drag、pan、selection、viewport 操作が誤動作する。
- automated input tests が captured touchpad event の座標前提で失敗する。

---

# サービス影響例

このセクションは、公式文書と AOSP 根拠から導いた「起こりうる影響例」を記録する。特定サービスで実際に発生確認した事実ではない。

## 例1（Example 1）: Chrome Remote Desktop / Microsoft Remote Desktop のような remote desktop

- 具体サービス例: Chrome Remote Desktop、Microsoft Remote Desktop、Splashtop、Parsec。
- 影響を受ける実装パターン: pointer capture 中の touchpad event を absolute coordinate として remote cursor へ送る実装。
- 発生条件: Android 17 で touchpad pointer capture が relative event を返し、アプリが absolute coordinate 前提のまま処理する場合。
- ユーザーに見える症状: remote cursor が飛ぶ、移動量が過大 / 過小になる、drag selection がずれる可能性。
- 技術的に起きていること: captured touchpad event の default が relative delta になり、従来の座標変換処理と合わなくなる。
- 推奨対応シーン: remote desktop / game streaming / VNC 系の pointer capture path を Android 17 touchpad で検証する。
- 検証観点: touchpad、mouse、touchscreen を分け、absolute mode が必要な画面では `requestPointerCapture(int)` の利用可否を確認する。
- 根拠: 公式文書の touchpad pointer capture default 変更、`View.requestPointerCapture(int)` / `InputManagerService.requestPointerCapture()` の AOSP source context。
- Confidence（信頼度）: Low。レポート自体の AOSP 差分確認が限定的なため。
- 注意: 上記サービスで発生確認した事実ではない。実際の影響は pointer capture の利用有無と入力変換実装に依存する。

## 例2（Example 2）: Minecraft / Roblox / GeForce NOW のような camera / viewport 操作

- 具体サービス例: Minecraft、Roblox、GeForce NOW、Unity / Unreal Engine 製の 3D editor や game。
- 影響を受ける実装パターン: captured pointer movement を camera rotation、viewport pan、aiming に使う実装。
- 発生条件: touchpad event を relative delta として扱うべき場面で absolute coordinate 前提の補正を残している場合。
- ユーザーに見える症状: camera rotation が急に速くなる / 遅くなる、視点移動が不安定になる、精密操作が難しくなる可能性。
- 技術的に起きていること: input source / tool type ごとの movement model が変わり、mouse と touchpad を同一処理している箇所の前提が崩れる。
- 推奨対応シーン: laptop / tablet + touchpad、desktop mode、external display での pointer capture QA。
- 検証観点: touchpad captured event の座標系、delta scaling、API 17 未満との compatibility wrapper。
- 根拠: 公式文書の relative event default と absolute mode 明示 request の説明。
- Confidence（信頼度）: Low。
- 注意: 上記サービスで発生確認した事実ではない。game engine / input library ごとの検証が必要。

---

# 対応候補（Recommended Action Candidates）

## 実装対応（Implementation）

- pointer capture を使う箇所を棚卸しし、touchpad event を absolute coordinate と relative delta のどちらとして扱っているか確認する。
- relative motion event を前提にできる機能では、Android 17 の default behavior に合わせて delta-based processing に整理する。
- absolute coordinate behavior が必要な場合は、Android 17 以上で `requestPointerCapture(int)` に `View.POINTER_CAPTURE_MODE_ABSOLUTE` を指定する。
- source / tool type / input device を確認し、touchpad、mouse、stylus、touchscreen の処理を同一視しない。
- Android 17 未満との互換性を保つため、新 API 呼び出しは API level guard または reflection / compatibility wrapper で分岐する。

## 検証対応（Testing）

- Android 16 / targetSdkVersion 36 で pointer capture 中の touchpad event baseline を確認する。
- Android 17 / targetSdkVersion 36 と Android 17 / targetSdkVersion 37 の両方で、touchpad pointer capture の event coordinates / axes / deltas を確認する。
- `requestPointerCapture()` と `requestPointerCapture(int, STATIC)` 相当の挙動を分けて確認する。
- touchpad、mouse、touchscreen、stylus を別々に確認する。
- remote pointer mapping、camera control、drag、pan、selection、viewport navigation など、座標解釈に依存する user flow を確認する。

## 顧客説明候補（Customer Explanation）

Android 17 では、touchpad を pointer capture 中に使った場合、default で relative motion event が app に届くようになります。pointer capture 中の touchpad event を absolute coordinate として扱っている app では、cursor movement や remote pointer mapping が変わる可能性があります。従来の absolute coordinate behavior が必要な場合は、Android 17 の新 API `requestPointerCapture(int)` で `View.POINTER_CAPTURE_MODE_ABSOLUTE` を指定してください。

---

# 検証マトリクス（Verification Matrix）

| 端末 OS | targetSdkVersion | アプリ条件 | 期待挙動 |
| --- | --- | --- | --- |
| Android 16 | 36 | touchpad + pointer capture | baseline。captured event が absolute / relative のどちらとして届くか確認。 |
| Android 17 | 36 | touchpad + pointer capture + default request | flag 条件を満たす場合、`requestPointerCapture()` は relative mode を default request する。 |
| Android 17 | 37 | touchpad + pointer capture + default request | targetSdkVersion 36 と同様の可能性。公式文書に targetSdkVersion 条件なし。 |
| Android 17 | 36 / 37 | touchpad + `POINTER_CAPTURE_MODE_ABSOLUTE` | absolute coordinate behavior を request できることを確認する。 |
| Android 17 | 36 / 37 | mouse / stylus / touchscreen + pointer capture | touchpad 以外への影響範囲を確認する。 |

---

# 未解決事項（Open Questions）

- `relative_capture_mode_by_default` の製品 default state はどの build / release config で有効になるか。
- native inputflinger 側で relative / absolute mode がどのように touchpad event conversion に反映されるか。
- touchpad 判定は `InputDevice` source、device class、kernel event、InputReader classification のどれに基づくか。
- `MotionEvent` のどの座標 / axis / history が relative event として変化するか。
- mouse、stylus、touchscreen、trackball、external pointing device への影響範囲。

---

# 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- 人間による判断が必要

最終影響度:
- 人間による判断が必要

顧客通知要否（Customer Communication Required）:
- 人間による判断が必要

リリース判断:
- 人間による判断が必要
