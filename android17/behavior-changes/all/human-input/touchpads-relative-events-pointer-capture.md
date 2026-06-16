# Touchpads deliver relative events by default during pointer capture

## 基本情報（Metadata）

### 調査対象 Android バージョン（Android Versions）

From:
- android-16.0.0_r4

To:
- TBD: Android 17 AOSP tag

Previous targetSdkVersion:
- 36

Target targetSdkVersion:
- 37

### Behavior Change 文書（Behavior Change Source）

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
- Touchpads deliver relative events by default during pointer capture

Page type:
- Behavior changes: all apps

### 分類スナップショット（Classification Snapshot）

主分類（Primary classification）:
- UNKNOWN_NEEDS_MORE_EVIDENCE

公式文書からの初期適用条件判断:
- 公式文書は Android 17 の `Behavior changes: all apps` ページにこの項目を掲載している。
- 公式文書は、Android 17 から touchpad が pointer capture 中に absolute coordinate ではなく relative motion event を default で deliver すると説明している。
- 公式文書は、app が以前と同じ absolute coordinate behavior を必要とする場合は、Android 17 で導入された `requestPointerCapture(int)` と `View.POINTER_CAPTURE_MODE_ABSOLUTE` を使って request するよう説明している。
- 原文には targetSdkVersion 条件は記載されていない。
- ただし、local `frameworks-base` に Android 17 AOSP tag がないため、input dispatch / pointer capture / touchpad source 判定 / compat framework entry は未確認である。確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

早見表（At-a-glance impact）:

| 確認項目（Question） | 回答（Answer） | 根拠（Evidence） |
| --- | --- | --- |
| Android 17 に OS アップデートしただけで適用されるか | Likely Yes / Conditional, but unverified | 公式文書は all apps ページに掲載し、targetSdkVersion 条件を示していない。AOSP gate 未確認。 |
| targetSdkVersion 37 以上が必要か | Likely No, but unverified | 原文に targetSdkVersion 条件はない。AOSP targetSdkVersion gate 未確認。 |
| 追加の実行時条件があるか | Yes | app が pointer capture を使い、input device が touchpad で、captured event の座標解釈に依存している場合。 |
| Compat Change ID が関係するか | Unknown | Android 17 tag と compat framework evidence が未確認。 |

### 調査日（Investigation Date）

2026-06-15

### 信頼度（Confidence）

- Low

### 適用条件分類（Applicability Classification）

適用される条件（Applies when）:
- [ ] OS update / all apps on Android 17 regardless of targetSdkVersion
- [ ] targetSdkVersion >= 37 on Android 17+
- [ ] targetSdkVersion >= 37, with additional runtime conditions
- [ ] Mainline / Google Play system update dependent
- [ ] API addition only, not a behavior change
- [x] Unknown / needs more evidence

必要な実行時条件（Required runtime conditions）:
- Android version: Android 17 以上。AOSP tag 未取得のため実装上の OS gate は未確認。
- targetSdkVersion: 公式文書上は条件なし。AOSP targetSdkVersion gate 未確認。
- Device/form factor: touchpad を持つ device、または touchpad input device が接続された device。
- Permission/API/component condition: `View.requestPointerCapture()`、`View.requestPointerCapture(int)`、`View.onCapturedPointerEvent(MotionEvent)`、`MotionEvent`、`InputDevice`、pointer capture、relative pointer events。
- App state/process condition: app が pointer capture 中の touchpad event を処理し、absolute coordinate を前提にしている場合。

Compat framework:
- Change ID: Unknown
- Change name: Unknown
- Default state: Unknown
- Toggleable for testing: Unknown

分類信頼度（Classification confidence）:
- Low

分類根拠（Classification evidence）:
- Official documentation page: `behavior-changes-all`
- Original applicability statement: Android 17 から touchpad は pointer capture 中に default で relative motion event を deliver する。
- AOSP targetSdk gate: 未確認。local `frameworks-base` に `android-17*` tag がない。
- Compat framework entry: 未確認。Android 17 compat framework evidence が未取得。

---

# エグゼクティブサマリー（Executive Summary）

Android 17 では、touchpad input が pointer capture 中に default で relative motion event として app に届く、と公式文書は説明している。これまで pointer capture 中の touchpad event を absolute coordinate として扱っていた app は、Android 17 で pointer movement の解釈が変わる可能性がある。

影響を受けるのは、pointer capture を使う game、remote desktop、streaming、emulator、virtualization、drawing、CAD、editor などである。これらの app が touchpad の captured event を画面上の absolute position として扱っている場合、cursor movement、camera control、remote pointer mapping、drag 操作などにずれが出る可能性がある。

公式文書は、従来の absolute coordinate behavior が必要な場合は Android 17 で追加された `requestPointerCapture(int)` に `View.POINTER_CAPTURE_MODE_ABSOLUTE` を指定するよう説明している。現時点では local `frameworks-base` に Android 17 AOSP tag がなく、実装上の gate、compat Change ID、targetSdkVersion 分岐の有無を確認できない。確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE`、信頼度は Low とする。

---

# 公式ドキュメント確認（Original Documentation）

## 原文（Statement）

Page title:
- Behavior changes: all apps

Page URL:
- https://developer.android.com/about/versions/17/behavior-changes-all

Page type:
- all apps

Section title:
- Touchpads deliver relative events by default during pointer capture

Original statement being verified:
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

AOSP で未確認の点:
- touchpad source 判定がどの input source / device property で行われるか。
- pointer capture mode の default がどの layer で決まるか。
- `requestPointerCapture()` と `requestPointerCapture(int)` の default mode 差分。
- `POINTER_CAPTURE_MODE_RELATIVE` / `POINTER_CAPTURE_MODE_ABSOLUTE` の API surface と input dispatch への反映。
- targetSdkVersion gate の有無。
- compat framework Change ID と default state。
- mouse、stylus、touchscreen、trackball、rotary など touchpad 以外の input device への影響有無。

## 適用条件（Applicability）

この変更がいつ適用されるかを OS 条件と targetSdkVersion 条件に分けて説明する。

### OS アップデート時の挙動（OS Update Behavior）

- Android 17 に OS アップデートしただけで適用されるか: 公式文書上は Yes / Conditional。all apps ページに掲載され、targetSdkVersion 条件は示されていない。ただし AOSP gate 未確認。
- targetSdkVersion に依存しない根拠: 原文に targetSdkVersion 条件がない。
- Android 16 以前での挙動: 公式文書は Android 17 から touchpad が default で relative event を deliver すると説明している。Android 16 baseline の pointer capture mode は AOSP diff 未確認。

### targetSdkVersion 37 以上での挙動（targetSdkVersion 37 Behavior）

- targetSdkVersion 37 以上で適用されるか: 公式文書上、targetSdkVersion 37 は必要条件ではない。
- Android 17 以外で targetSdkVersion 37 にした場合の挙動: Unknown。公式文書は Android 17 platform behavior として説明している。
- opt-out / temporary override の有無: absolute coordinate behavior が必要な場合の explicit request として `View.POINTER_CAPTURE_MODE_ABSOLUTE` が示されている。compat opt-out の有無は未確認。

### その他の条件（Other Conditions）

- device/form factor: touchpad input device が存在する device。laptop、tablet + keyboard / trackpad、desktop mode、external touchpad などが候補。
- API usage: app が pointer capture を request し、`onCapturedPointerEvent(MotionEvent)` などで captured event を処理する。
- input device condition: 公式文書の対象は touchpad。mouse / stylus / touchscreen などの扱いは未確認。
- app behavior condition: captured event の `MotionEvent` を absolute coordinate として扱う場合に影響が大きい。
- not affected / lower risk: pointer capture を使わない app、touchpad event を処理しない app、relative delta を前提にした pointer capture 実装。

---

# AOSP 調査（AOSP Investigation）

## checkout 状態（Checkout Status）

確認コマンド:

```bash
git -C frameworks-base status --short
git -C frameworks-base tag --list android-16.0.0_r4
git -C frameworks-base tag --list 'android-17*'
```

結果:
- `frameworks-base` の `status --short` は空で、dirty working tree は確認されなかった。
- `android-16.0.0_r4` tag は存在する。
- `android-17*` tag は local checkout に存在しない。

Evidence limitation:
- Android 17 AOSP tag が local `frameworks-base` にないため、`android-16.0.0_r4` と Android 17 tag の明示的な source diff は実行できない。
- そのため、local working tree や未確定 branch を platform evidence として扱わない。
- 本レポートの AOSP-backed conclusion は Low confidence に留める。

## 関連ファイル（Related Files）

Android 17 AOSP tag 未取得のため、tag diff に基づく related files は未確定。

Android 17 tag 公開後に確認すべき候補:
- `core/java/android/view/View.java`
- `core/java/android/view/MotionEvent.java`
- `core/java/android/view/InputDevice.java`
- `core/java/android/view/ViewRootImpl.java`
- `services/core/java/com/android/server/input/` 以下の input dispatch / pointer capture path
- `native/services/inputflinger/` または input dispatcher / reader に関係する AOSP project
- API surface file の `requestPointerCapture(int)`、`POINTER_CAPTURE_MODE_RELATIVE`、`POINTER_CAPTURE_MODE_ABSOLUTE`
- compat framework 定義ファイル内の pointer capture / touchpad relative event 関連 Change ID

Note:
- 実際の input dispatch は `frameworks-base` 以外の inputflinger / native service 側にある可能性がある。Android 17 tag 入手後は該当 project も evidence 対象として確認する必要がある。

## 確認したソース文脈（Source Context Reviewed）

AOSP tag diff は未実行。以下は公式文書から見た確認予定の source context であり、AOSP evidence ではない。

| ファイル / シンボル（File / symbol） | Android 16 の基準挙動（baseline） | Android 17 の挙動 | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| `View.requestPointerCapture()` | 未確認 | default mode が touchpad で relative になると公式文書が説明 | app が pointer capture を開始する主要 API であり default mode の入口になるため |
| `View.requestPointerCapture(int)` | API なしまたは未確認 | absolute behavior が必要な場合に `POINTER_CAPTURE_MODE_ABSOLUTE` を指定すると公式文書が説明 | 新しい explicit mode selection API の確認が必要なため |
| `View.onCapturedPointerEvent(MotionEvent)` | 未確認 | relative motion event が deliver される可能性 | app が captured event を受け取る callback であるため |
| input dispatch / pointer capture path | 未確認 | touchpad event の coordinate mode が default relative に変わる可能性 | 実際に event coordinate / axis を変換する enforcement point の候補であるため |
| input device classification path | 未確認 | touchpad のみが対象と公式文書が説明 | mouse / stylus / touchscreen との切り分けに必要なため |
| compat framework entry | 未確認 | targetSdkVersion gate の有無は不明 | all apps 型か targetSdkVersion gate 型かの確定に必要なため |

必須記入項目（Required context）:
- Entry point / caller: 未確認。想定される entry point は app の `requestPointerCapture()` / `requestPointerCapture(int)` -> ViewRoot / Window / input dispatcher -> captured `MotionEvent` delivery -> `onCapturedPointerEvent(MotionEvent)`。
- Relevant class or service responsibility: pointer capture request、input device classification、motion event coordinate mode、captured event dispatch。
- Runtime path from app API / system event to changed code: app が pointer capture を request -> touchpad event が発生 -> Android 17 は default relative mode で captured motion event を deliver -> app が absolute coordinate を必要とする場合は `POINTER_CAPTURE_MODE_ABSOLUTE` を指定、という path が想定される。AOSP evidence としては未確認。
- Why unrelated code paths were excluded: tag diff 未実行のため、除外判断は未完了。

## 差分解釈（Diff Interpretation）

| 確認した差分（Observed diff） | 解釈（Interpretation） | Behavior Change との関係 | 信頼度（Confidence） |
| --- | --- | --- | --- |
| Android 17 tag 未取得のため source diff 未確認 | 公式文書上は changed default / API addition with behavior mitigation と読める | touchpad pointer capture default が relative event に変わり、static mode を明示 request できると説明されている | Low |

必須分類（Required interpretation）:
- Added behavior: 未確認。`requestPointerCapture(int)` と pointer capture mode constants が追加された可能性がある。
- Removed behavior: 未確認。touchpad pointer capture の implicit absolute default が削除または限定された可能性がある。
- Changed condition: 未確認。touchpad device かつ pointer capture 中という条件で event mode が変わる可能性がある。
- Changed default: 公式文書上は該当候補。touchpad pointer capture default が relative motion event になると読める。
- No behavior change: 現時点では公式文書上の説明と矛盾するため候補ではないが、AOSP tag diff で確認が必要。

---

# 影響分析（Impact Analysis）

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

| Device OS | targetSdkVersion | App condition | Expected behavior |
| --- | --- | --- | --- |
| Android 16 | 36 | touchpad + pointer capture | baseline。captured event が absolute / relative のどちらとして届くか確認。 |
| Android 17 | 36 | touchpad + pointer capture + default request | touchpad event は default relative motion event として届く可能性。公式文書上の変更対象。AOSP gate 未確認。 |
| Android 17 | 37 | touchpad + pointer capture + default request | targetSdkVersion 36 と同様の可能性。公式文書に targetSdkVersion 条件なし。 |
| Android 17 | 36 / 37 | touchpad + `POINTER_CAPTURE_MODE_ABSOLUTE` | absolute coordinate behavior を request できることを確認する。 |
| Android 17 | 36 / 37 | mouse / stylus / touchscreen + pointer capture | touchpad 以外への影響範囲を確認する。 |

---

# 未解決事項（Open Questions）

- Android 17 AOSP tag 上で、touchpad pointer capture default mode はどの code path で変わっているか。
- targetSdkVersion gate または compat Change ID が存在するか。
- `requestPointerCapture()` の default mode と `requestPointerCapture(int)` の mode selection はどのように dispatch layer へ渡るか。
- touchpad 判定は `InputDevice` source、device class、kernel event、InputReader classification のどれに基づくか。
- `MotionEvent` のどの座標 / axis / history が relative event として変化するか。
- mouse、stylus、touchscreen、trackball、external pointing device への影響範囲。

---

# 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- Human decision required

最終影響度（Final Severity）:
- Human decision required

顧客通知要否（Customer Communication Required）:
- Human decision required

リリース判断（Release Readiness）:
- Human decision required
