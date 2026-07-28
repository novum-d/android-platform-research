# Android 17 UI, Input and Device Form Factors 対応例

## 位置づけ

このファイルは、Android 17のUI、input、accessibility、large-screen変更を
アプリ実装と試験へ落とすcompanionである。
適用条件、AOSP evidence、confidenceは各主レポートを正とする。

- [Android 16→17挙動比較](../version-comparisons/ui-input-and-device-form-factors.md)
- [対応例テンプレート](../../templates/implementation-examples-template.md)

## 対象と適用条件

| 項目 | Android 17での主な適用条件 | 主レポート |
| --- | --- | --- |
| Rotation後のIME visibility | OS update、Activity recreation、focused editor | [Report](../all/user-experience-and-system-ui/restoring-default-ime-visibility-after-rotation.md) |
| Touchpad relative event | OS update、pointer capture、touchpad、feature flag | [Report](../all/human-input/touchpads-relative-events-pointer-capture.md) |
| CJKV physical keyboard accessibility | API 37、feature flag。targetSdk gateは未解決 | [Report](../target/accessibility/accessibility-ime-physical-keyboard.md) |
| Large-screen constraints | Android 17 + targetSdkVersion 37 + smallest width 600dp以上 | [Report](../target/device-form-factors/large-screen-orientation-resizability-aspect-ratio.md) |

## 既存実装の検出

```bash
rg -n "windowSoftInputMode|showSoftInput|WindowInsetsController|Type\\.ime|requestFocus" app src
rg -n "requestPointerCapture|onCapturedPointerEvent|MotionEvent|touchpad|mouse" app src
rg -n "InputConnection|TextAttribute|AccessibilityEvent|TYPE_VIEW_TEXT_CHANGED" app src
rg -n "screenOrientation|resizeableActivity|minAspectRatio|maxAspectRatio|setRequestedOrientation" app src
rg -n "PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY" app src
```

## 例1: Rotation後もIMEが必要なscreenだけ明示表示する

常にIMEを表示する専用ActivityならManifestで意図を明示できる。

```xml
<activity
    android:name=".search.SearchActivity"
    android:windowSoftInputMode="stateAlwaysVisible" />
```

画面状態により表示要否が変わる場合は、recreation後にfocusとwindow attachmentを待って
IME表示を要求する。

```kotlin
import android.view.View
import androidx.core.view.ViewCompat
import androidx.core.view.WindowInsetsCompat

fun restoreEditorFocus(
    editor: View,
    shouldContinueEditing: Boolean,
) {
    if (!shouldContinueEditing) return

    editor.requestFocus()
    editor.post {
        ViewCompat.getWindowInsetsController(editor)
            ?.show(WindowInsetsCompat.Type.ime())
    }
}
```

`shouldContinueEditing`はsaved stateやscreen stateから決める。
すべての画面で無条件に`show()`すると、戻る操作で閉じたIMEやhardware keyboard利用時の
user intentを上書きするため避ける。

検証:

- IME表示中 / 非表示中のrotation。
- portrait / landscape、Activity recreationあり / `onConfigurationChanged()`処理あり。
- gesture navigationのbackでIMEを閉じた直後。
- hardware keyboard接続時、multi-window、fold / unfold。

## 例2: Pointer captureの目的に応じてmodeを選ぶ

camera control、remote desktop、gameのようにdeltaで処理できる機能は、
Android 17のrelative defaultを受け入れる。

```kotlin
fun beginRelativePointerControl(target: View) {
    target.requestFocus()
    target.requestPointerCapture()
}

override fun onCapturedPointerEvent(event: MotionEvent): Boolean {
    return relativePointerController.onMotionEvent(event)
}
```

描画surface上のfinger locationなどabsolute座標が不可欠な画面だけ、
API 37のmode指定を使う。

```kotlin
fun beginAbsoluteTouchpadControl(target: View) {
    target.requestFocus()
    if (Build.VERSION.SDK_INT >= 37) {
        target.requestPointerCapture(View.POINTER_CAPTURE_MODE_ABSOLUTE)
    } else {
        // Android 16以前のrequestPointerCapture()は従来のabsolute挙動。
        target.requestPointerCapture()
    }
}
```

relative / absoluteをeventの値から推測して切り替えず、機能要件からmodeを選ぶ。
mouse、touchpad、touchscreen、stylusを別々に試験し、scroll、button、
capture loss、window focus lossも確認する。

## 例3: CJKV accessibilityは標準editorを優先する

通常の入力欄は標準`EditText` / `TextView`と標準`EditableInputConnection`を使い、
Android 17 frameworkによるcomposition / commit / candidate metadataの伝播を利用する。

```xml
<EditText
    android:id="@+id/message"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:inputType="textMultiLine"
    android:importantForAccessibility="yes" />
```

独自IMEがcandidate selectionを通知する場合のAPI 37検証用例:

```kotlin
// API 37 / feature flag条件を確認する検証用。targetSdk gateは主レポートで未解決。
val attributes = TextAttribute.Builder()
    .setTextSuggestionSelected(true)
    .build()

inputConnection.setComposingText(
    selectedCandidate,
    1,
    attributes,
)
```

独自editorがaccessibility eventを生成する場合の検証用例:

```kotlin
// Framework標準editorで自動生成されるeventを二重送信しない。
if (Build.VERSION.SDK_INT >= 37 && usesCustomInputConnection) {
    val event = AccessibilityEvent.obtain(
        AccessibilityEvent.TYPE_VIEW_TEXT_CHANGED,
    ).apply {
        textChangeTypes =
            AccessibilityEvent.TEXT_CHANGE_TYPE_CONVERSION_SUGGESTION_SELECTED_BY_IME
    }
    customEditor.sendAccessibilityEventUnchecked(event)
}
```

この項目は主レポート上`UNKNOWN_NEEDS_MORE_EVIDENCE`である。
上記をtarget 37必須のproduction workaroundとして一律導入せず、
API 37 emulator / device、flag state、標準editorとの差分を記録する。
TalkBack等で、日本語、中国語、韓国語、ベトナム語のcomposition、candidate移動、
commit、取消を確認する。

## 例4: Android 16のlarge-screen temporary opt-outを削除する

削除対象の例:

```xml
<!-- Android 17 / target 37では大画面opt-outとして機能しない。 -->
<property
    android:name="android.window.PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY"
    android:value="true" />
```

固定orientation、`resizeableActivity="false"`、`minAspectRatio` / `maxAspectRatio`を
layout correctnessの前提にしない。
これらがphoneなど別条件で必要な場合でも、大画面ではavailable boundsが変化する前提で設計する。

Composeでwindow幅に応じて1-pane / 2-paneを切り替える最小例:

```kotlin
@Composable
fun AdaptiveCatalog(
    selectedId: String?,
    onSelect: (String) -> Unit,
) {
    BoxWithConstraints(Modifier.fillMaxSize()) {
        if (maxWidth >= 600.dp) {
            Row(Modifier.fillMaxSize()) {
                CatalogList(
                    selectedId = selectedId,
                    onSelect = onSelect,
                    modifier = Modifier.weight(1f),
                )
                CatalogDetail(
                    selectedId = selectedId,
                    modifier = Modifier.weight(1f),
                )
            }
        } else {
            if (selectedId == null) {
                CatalogList(
                    selectedId = null,
                    onSelect = onSelect,
                    modifier = Modifier.fillMaxSize(),
                )
            } else {
                CatalogDetail(
                    selectedId = selectedId,
                    modifier = Modifier.fillMaxSize(),
                )
            }
        }
    }
}
```

`selectedId`はActivity / composable local stateだけに閉じず、
`ViewModel`と`SavedStateHandle`など、configuration changeとprocess recreationを越えられる
state ownerへhoistする。

幅600dpはこの例のscreen固有breakpointであり、端末種別判定ではない。
実際にはcontentに必要な最小幅、navigation pattern、window size classを基に決める。

## Large-screen試験セット

| Case | 確認内容 |
| --- | --- |
| Portrait / landscape | `screenOrientation`に依存せず操作できる |
| Split screen | 狭幅と広幅を跨いでもstate / scroll / selectionを保持 |
| Fold / unfold | hinge / posture変更でpaneとfocusが破損しない |
| Desktop resize |連続resizeでoverflow、重なり、blank areaがない |
| Camera / media preview | aspect fit / crop方針が明示される |
| Dialog / keyboard | large screenでdialog width、IME、focusが一貫する |
| Back navigation | 2-paneと1-paneで同じlogical back stackを保つ |

## 検証マトリクス

| Case | Android 16 / target 36 | Android 17 / target 36 | Android 17 / target 37 |
| --- | --- | --- | --- |
| IME表示中rotation |復元し得る | default visibilityへ | target 36と同じOS条件 |
| Pointer capture default | absolute | flag条件でrelative | target 36と同じOS条件 |
| Explicit absolute capture |新APIなし /従来default | API 37でabsolute指定 | API 37でabsolute指定 |
| Standard editor + CJKV |旧event |新API、gate記録 |公式説明とflagを検証 |
| Custom editor + CJKV | custom behavior |新metadata対応を比較 | target gateは断定しない |
| sw600dp + opt-out | Android 16の条件で有効 | target 36なら有効条件あり | opt-out無効 |
| Resize / rotate state | baseline | adaptive behavior | adaptive behavior必須 |

## 完了条件

- IMEを暗黙復元せず、必要なscreen stateから表示要否を決めた。
- Pointer captureをrelative / absoluteの機能要件で分類した。
- CJKV accessibilityは標準editorを優先し、custom editorだけ追加検証した。
- CJKV項目の未解決target gateを確定事項として記載していない。
- large-screen opt-outを削除し、resize / rotate / fold / multi-windowを試験した。
- configuration changeとprocess recreationの両方でstateを復元した。
- Android 17 / target 36とtarget 37を分けて結果を記録した。

## References

- [UI, Input and Device Form Factors挙動比較](../version-comparisons/ui-input-and-device-form-factors.md)
- [Android 17 Behavior Changes一覧](../README.md)

## Human Decision

この対応例では最終priority、severity、release readinessを決定しない。
