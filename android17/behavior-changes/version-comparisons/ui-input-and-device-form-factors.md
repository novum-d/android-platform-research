# Android 16 → 17 UI, Input and Device Form Factors 挙動比較

## 1. 比較範囲

- [比較一覧](README.md)
- [Android 17対応例](../implementation-examples/ui-input-and-device-form-factors.md)
- Baseline: Android 16 / `android-16.0.0_r4`
- Target: Android 17 / `android-17.0.0_r1`
- Observed: rotation、keyboard、touchpad、screen reader、large screenとも未実施

## 2. 先に結論

Android 17では、configuration change後のIME、pointer capture中のtouchpad、
CJKV compositionのaccessibility event、大画面opt-outの4箇所でappの既存前提が変わる。
特にlarge screenはAndroid 16で許されたtemporary opt-outがtarget 37で使えなくなる。

## 3. 項目別比較

### Restoring default IME visibility after rotation

- [主レポート](../all/user-experience-and-system-ui/restoring-default-ime-visibility-after-rotation.md)
- [要約](../../summaries/all/user-experience-and-system-ui/restoring-default-ime-visibility-after-rotation-summary.md)
- 適用: `OS_UPDATE_ALL_APPS`

| 観点 | Android 16 | Android 17 |
| --- | --- | --- |
| System behavior | Activity recreation後に以前のIME shown stateを復元し得る | default visibility modeへ戻し、以前shownだけでは復元しない |
| App signal | rotation後もkeyboard表示が継続し得る | keyboardが閉じる |
| 対応 |暗黙復元に依存するscreenを検出 | `stateAlwaysVisible`またはlifecycleに合わせた明示request |

appがconfiguration changeを自分で処理する場合は別経路として比較する。

### Touchpad relative events during pointer capture

- [主レポート](../all/human-input/touchpads-relative-events-pointer-capture.md)
- [要約](../../summaries/all/human-input/touchpads-relative-events-pointer-capture-summary.md)
- 適用: `OS_UPDATE_ALL_APPS` + pointer capture + touchpad

| 観点 | Android 16 | Android 17 |
| --- | --- | --- |
| System behavior | captured touchpadからraw absolute finger location | defaultでcaptured mouse相当のrelative motion / scroll |
| App signal | screen coordinate的な`MotionEvent` | delta movement / wheel-like scroll |
| 対応 | touchpad専用absolute mappingを検出 | mouseと共通relative handlerへ。absolute必須なら`POINTER_CAPTURE_MODE_ABSOLUTE` |

### Accessibility support for complex IME physical keyboard typing

- [主レポート](../target/accessibility/accessibility-ime-physical-keyboard.md)
- [要約](../../summaries/target/accessibility/accessibility-ime-physical-keyboard-summary.md)
- 分類: `UNKNOWN_NEEDS_MORE_EVIDENCE`

| 観点 | Android 16 | Android 17 documentation / AOSP |
| --- | --- | --- |
| System behavior | composition / commit / candidate selectionを専用text-change typeで伝えない | `AccessibilityEvent` / `TextAttribute`に新typeとcandidate flag |
| Standard TextView | generic `TYPE_VIEW_TEXT_CHANGED` | target37では新情報をdefault処理すると公式説明 |
| Custom editor / IME |独自情報伝達なし | IMEがcandidate選択を設定し、custom `InputConnection`がevent typeへ反映 |

AOSPで直接のtargetSdkVersion 37 gateを閉じられていないため、OS / target matrixは
主レポートどおり未解決として扱う。

### Large-screen orientation / resizability / aspect ratio

- [主レポート](../target/device-form-factors/large-screen-orientation-resizability-aspect-ratio.md)
- [要約](../../summaries/target/device-form-factors/large-screen-orientation-resizability-aspect-ratio-summary.md)
- 適用: `TARGET_SDK_37_CONDITIONAL` + `sw >= 600dp`

| 観点 | Android 16 / target36 | Android 17 / target37 |
| --- | --- | --- |
| System behavior | orientation / aspect / resizability制約を無視するがtemporary opt-out可能 |制約を無視し、`PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY` opt-outも無効 |
| App signal | opt-out Activityはpillarbox / 固定方向を維持可能 | available areaにresize / rotate |
| 対応 | opt-out対象と削除条件を記録 | adaptive layout、state保存、multi-window / fold / desktop testを完了 |

状態差:

```text
Android 16 target36: large screen -> constraints ignored
                              \-> temporary opt-out -> restricted layout
Android 17 target37: large screen -> constraints ignored（opt-out不可）
```

## 4. OS / targetSdk マトリクス

| 項目 | Android 16 / target36 | Android 17 / target36 | Android 17 / target37 |
| --- | --- | --- | --- |
| IME rotation | previous visibilityを復元し得る | default visibility | target36と同じ |
| Touchpad capture | absolute | relative default | target36と同じ |
| CJKV accessibility |旧event |新API。gate未解決 | standard TextView defaultと公式説明 |
| Large screen | opt-out可能 | target36はopt-out可能 | opt-out不可 |

## 5. 比較試験

| Case | Trigger | Expected Android 16 | Expected Android 17 | Observed |
| --- | --- | --- | --- | --- |
| U1 | focused field表示中にrotate | IME復元し得る | defaultでは閉じる | 未実施 |
| U2 | touchpad + pointer capture | absolute coordinates | relative delta | 未実施 |
| U3 | CJKV candidate select / commit | generic change | typed change metadata | 未実施 |
| U4 | large screen + temporary opt-out | restricted layout | target37でfull bounds | 未実施 |

## 6. Evidence / Human Decision

flag default、native input conversion、accessibility target gate、large-screen exceptionとconfidenceは主レポートを正とする。
この資料ではObserved resultとHuman Decisionを確定しない。
