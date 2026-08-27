# Predictive Back - Dispatcher を経由する場合としない場合の実行挙動比較

## 位置づけ（Scope）

このファイルは、システムの Back gesture、toolbar / 独自の Back 操作、navigation の直接実行について、AndroidX `OnBackPressedDispatcher` の callback chain を通る経路と通らない経路を比較する補足資料である。
Behavior Change の根拠、適用条件、分類、confidence、人間の判断は、主レポートと1ページ要約を正とする。

主レポート:
- [migration-or-opt-out-required-for-predictive-back.md](migration-or-opt-out-required-for-predictive-back.md)

1ページ要約:
- [migration-or-opt-out-required-for-predictive-back-summary.md](../../../summaries/target/user-experience-and-system-ui/migration-or-opt-out-required-for-predictive-back-summary.md)

実装例:
- [migration-or-opt-out-required-for-predictive-back-implementation-examples.md](../../implementation-examples/migration-or-opt-out-required-for-predictive-back-implementation-examples.md)

Dispatcher 移行後に animation が消える場合の切り分け:
- [migration-or-opt-out-required-for-predictive-back-dispatcher-animation-guide.md](migration-or-opt-out-required-for-predictive-back-dispatcher-animation-guide.md)

## 対象（Target）

Android 16 Behavior Change:
- 文書: https://developer.android.com/about/versions/16/behavior-changes-16#predictive-back
- セクション: Migration or opt-out required for predictive back

適用条件の要点:
- OS アップデート / 全アプリ: いいえ。
- targetSdkVersion 36 以上: はい。Android 16 以上の端末で Predictive Back のシステムアニメーションが既定で有効になる。
- その他の必須条件: 従来の `onBackPressed()` / `KEYCODE_BACK`、独自の Back 処理、または Back callback chain を持つこと。

## 「Dispatcher 経由なし」の定義

Android 16 のシステム Back gesture は platform の Back 通知機構を通るため、「dispatcher が一切存在しないシステム gesture」という経路ではない。
この資料でいう Dispatcher は AndroidX `OnBackPressedDispatcher` を指す。

Dispatcher を経由しない場合として比較するのは、次の経路である。
- toolbar / 独自ボタンから `NavController.navigateUp()` / `popBackStack()` / `finish()` / 業務処理を直接呼ぶ。
- platform の `OnBackInvokedDispatcher` へ直接 callback を登録し、AndroidX の callback chain を使わない。
- 従来の `Activity#onBackPressed()` override が呼ばれるのを待つ。ただし、Android 16 / targetSdkVersion 36 のシステム gesture では呼ばれない。

## 比較契約（Comparison Contract）

共通画面状態:

| 条件 | 値 |
| --- | --- |
| Activity callback | Activity の fallback / analytics 用 callback を登録済み |
| Fragment callback | 選択モードを閉じる callback を後から登録済み |
| Navigation | Fragment back stack に前画面がある |
| Drawer / dialog | シナリオごとに開閉状態を指定 |
| Android version | Android 16 |
| targetSdkVersion | 36 |
| Manifest | `enableOnBackInvokedCallback` は default / opt-out なし |

期待する基本順序:
1. 画面固有の UI 状態を閉じる。
2. Fragment / Navigation back stack を戻す。
3. 処理できる callback がなければ、Activity の fallback / finish へ進む。

## 比較対象（Comparison Targets）

| ID | 入力 / API | AndroidX Dispatcher | Gesture lifecycle | Callback selection / fallback |
| --- | --- | --- | --- | --- |
| A | system back gesture | 経由する | あり。利用 API に応じて start / progress / cancel / commit | 後から登録された enabled callback から逆順に選択し、なければ fallback |
| B | toolbar から `onBackPressedDispatcher.onBackPressed()` | 経由する | なし。programmatic invocation | A と同じ AndroidX callback selection / fallback |
| C | toolbar から `NavController.navigateUp()` / `popBackStack()` | 経由しない | なし | Navigation operation を直接実行。AndroidX back callbacks は選択されない |
| D | system gesture + legacy `onBackPressed()` override を待つ | AndroidX callback 未移行 | gesture は system 側にあるが legacy method へ届かない | Android 16 / target 36 では `onBackPressed()` は呼ばれない |

補足:
- platform `OnBackInvokedDispatcher` へ直接登録する実装は platform callback が処理するが、AndroidX `OnBackPressedDispatcher` の callback chain / LifecycleOwner 管理は通らない。
- AndroidX を使う Activity / Fragment では、既存 library integration と lifecycle 管理を維持するため `OnBackPressedDispatcher` を基本経路とする。

## 早見比較（At-a-Glance）

| 比較項目 | A: gesture + Dispatcher | B: toolbar + Dispatcher | C: direct navigation | D: legacy override |
| --- | --- | --- | --- | --- |
| system gesture が入口 | Yes | No | No | Yes |
| predictive gesture progress | 対応 API で取得可能 | No | No | No |
| `OnBackPressedCallback` を選択 | Yes | Yes | No | No |
| callback priority | 後登録 enabled callback が先 | A と同じ | 適用なし | 適用なし |
| Navigation callback / dialog callback | chain に登録されていれば処理 | chain に登録されていれば処理 | bypass され得る | 呼ばれない |
| fallback | callback がなければ Activity fallback | A と同じ | 呼び出し側が明示 | legacy method は入口にならない |
| 主な用途 | system back / predictive back | system back と同じ結果にしたい custom UI | toolbar Up / 明示的 graph operation | 移行対象 |

## 共通観測コード（Common Event Recorder）

```kotlin
class BackEventRecorder {
    private val mutableEvents = mutableListOf<String>()
    val events: List<String> get() = mutableEvents.toList()

    fun record(event: String) {
        mutableEvents += event
    }
}
```

Activity / Fragment callback:

```kotlin
val activityCallback = object : OnBackPressedCallback(true) {
    override fun handleOnBackPressed() {
        recorder.record("activity-callback")
    }
}

val selectionCallback = object : OnBackPressedCallback(selectionMode) {
    override fun handleOnBackPressed() {
        recorder.record("selection-callback")
        exitSelectionMode()
        isEnabled = false
    }
}

onBackPressedDispatcher.addCallback(this, activityCallback)
onBackPressedDispatcher.addCallback(this, selectionCallback)
```

## Scenario 1: selection mode 中に戻る

条件:
- `selectionCallback.isEnabled == true`。
- selection callback は Activity callback より後に登録されている。

### A: system gesture + Dispatcher

```text
system gesture
  -> platform back dispatch
  -> ComponentActivity / AndroidX bridge
  -> OnBackPressedDispatcher
  -> selectionCallback
  -> exitSelectionMode()
```

Expected events:

```text
[selection-callback]
```

- 後から登録された enabled callback が最初に選ばれ、navigation / Activity finish には進まない。

### B: toolbar + Dispatcher

```kotlin
toolbar.setNavigationOnClickListener {
    onBackPressedDispatcher.onBackPressed()
}
```

```text
toolbar click
  -> OnBackPressedDispatcher
  -> selectionCallback
  -> exitSelectionMode()
```

Expected events:

```text
[selection-callback]
```

- callback selection と最終 UI state は A と同じ。
- 本物の gesture ではないため gesture progress / cancel / predictive system animation の入力にはならない。

### C: toolbar + direct navigation

```kotlin
toolbar.setNavigationOnClickListener {
    findNavController(R.id.nav_host_fragment).navigateUp()
}
```

```text
toolbar click
  -> NavController.navigateUp()
  -> destination change
```

Expected events:

```text
[]
```

- `selectionCallback` は選択されない。
- selection mode の cleanup より先に destination が変わる可能性がある。
- toolbar が system back ではなく app bar Up を意味するなら、これは意図した差になり得る。

### 比較結果

| 経路 | selection を閉じる | destination を戻す | Gesture progress |
| --- | --- | --- | --- |
| A | Yes | No | 対応 API で可能 |
| B | Yes | No | No |
| C | No | Yes | No |

## Scenario 2: Fragment callback が処理せず次へ委譲する

### 正しい Dispatcher fallback

```kotlin
val fragmentCallback = object : OnBackPressedCallback(true) {
    override fun handleOnBackPressed() {
        recorder.record("fragment-callback")

        isEnabled = false
        try {
            onBackPressedDispatcher.onBackPressed()
        } finally {
            isEnabled = true
        }
    }
}
```

```text
back input
  -> fragmentCallback
  -> fragmentCallback disabled
  -> Dispatcherへ再投入
  -> activityCallback
```

Expected events:

```text
[fragment-callback, activity-callback]
```

### `isEnabled = false` なし

```text
back input
  -> fragmentCallback
  -> Dispatcherへ再投入
  -> 同じfragmentCallback
  -> Dispatcherへ再投入
  -> ... recursion
```

- `onBackPressedDispatcher.onBackPressed()` は `super.onBackPressed()` や「親 callback だけを呼ぶ API」ではない。
- 現在 enabled な callback chain を先頭から再評価するため、自分自身を無効化しないと再選択される。

### Dispatcher を通らず direct navigation

```kotlin
override fun handleOnBackPressed() {
    recorder.record("fragment-callback")
    findNavController().popBackStack()
}
```

Expected events:

```text
[fragment-callback]
```

- navigation は直接実行される。
- Activity callback / 次の AndroidX callback / dispatcher fallback は呼ばれない。
- 「Navigation stack を 1 つ pop する」が明確な責務なら direct operation が適する。

## Scenario 3: callback が 1 つも enabled でない

### A / B: Dispatcher 経由

```text
back input
  -> OnBackPressedDispatcher
  -> enabled callback なし
  -> fallbackOnBackPressed
  -> Activity / system fallback
```

- Dispatcher 作成時または ComponentActivity integration が持つ fallback に進む。

### C: direct navigation

```kotlin
val handled = navController.navigateUp()
if (!handled) {
    onBackPressedDispatcher.onBackPressed()
}
```

- `navigateUp()` が `false` の場合に何をするかは呼び出し側が決める。
- Dispatcher fallback を明示すれば、Navigation Up と system back fallback を組み合わせられる。
- fallback せず戻り値を無視すると、top-level destination で何も起きない可能性がある。

## Scenario 4: system gesture と legacy `onBackPressed()`

Legacy implementation:

```kotlin
@Deprecated("Use OnBackPressedDispatcher")
override fun onBackPressed() {
    recorder.record("legacy-onBackPressed")
    super.onBackPressed()
}
```

Android 16 / targetSdkVersion 36:

```text
system back gesture
  -> predictive back path
  -X-> Activity.onBackPressed()
```

Expected events:

```text
[]
```

- 公式 Behavior Change は `onBackPressed` が呼ばれず、`KEYCODE_BACK` も dispatch されないと説明している。
- legacy override が持つ drawer close、analytics、navigation fallback は実行されないため、supported back API へ移行する。

## Scenario 5: gesture progress / cancel / commit

### A: 実際の system gesture

```text
touch start
  -> back started
  -> progress 0.1, 0.3, 0.7...
  -> cancel または commit
  -> commit時にback処理
```

- Compose `PredictiveBackHandler`、Views の progress callback、Navigation の built-in support など、対応 API で gesture lifecycle を扱う。
- cancel では destination / business state を確定しない。

### B / C: toolbar click

```text
click
  -> 即時callback selection または navigation operation
```

- toolbar click には gesture progress / cancel がない。
- B は最終 callback chain を A と揃えられるが、gesture animation lifecycleまで再現するものではない。

## Scenario 6: LifecycleOwner と callback の残存

| 経路 | Lifecycle 管理 | 主な確認 |
| --- | --- | --- |
| `addCallback(owner, callback)` | owner が started の間だけ有効になり、destroy で除去 | 前画面 callback が次画面に残らない |
| owner なし `addCallback(callback)` | 呼び出し側で `Cancellable` / callback を管理 | Activity / Fragment 終了後に残さない |
| direct `navigateUp()` | callback 登録なし | click listener / View lifecycle が破棄されること |
| platform callback 直接登録 | platform API の register / unregister を管理 | AndroidX callback と二重処理しない |

## Android バージョン / targetSdkVersion 比較

| OS | targetSdkVersion | System back | Legacy `onBackPressed()` | 推奨確認 |
| --- | ---: | --- | --- | --- |
| Android 16 | 35 | legacy / manifest 状態に依存 | 旧経路を確認 | 移行前 baseline |
| Android 16 | 36 | predictive back default enabled | system gesture から呼ばれない | Dispatcher callback / progress / fallback |
| Android 16 | 36 + temporary opt-out | Activity 単位で legacy behavior | 一時的に旧経路 | opt-out 削除条件を記録 |

## Expected / Observed

| Scenario | Expected | Observed | Result | Evidence |
| --- | --- | --- | --- | --- |
| Selection mode | A / B は selection callback、C は direct navigation | 未実施 | 未実施 | AndroidX API semantics |
| Callback fallback | self-disable 後に次 callback。self-disable なしは再帰 | 未実施 | 未実施 | AndroidX API semantics / unit test candidate |
| No enabled callback | Dispatcher fallback。direct navigation は呼び出し側判断 | 未実施 | 未実施 | AndroidX / Navigation API semantics |
| Legacy override | Android 16 / target 36 gesture では呼ばれない | 未実施 | 未実施 | Android 16 Behavior Change |
| Gesture progress | 実 gesture の supported API のみ progress / cancel を持つ | 未実施 | 未実施 | Predictive back guide |

## 実装選択マップ（Implementation Decision Input）

| 要件 | 実装候補 | 理由 | 追加確認 |
| --- | --- | --- | --- |
| system back と toolbar / custom button の最終処理順を揃える | `onBackPressedDispatcher.onBackPressed()` | 同じ enabled callback chain / fallback を使う | toolbar には gesture progress がない |
| toolbar Up として navigation graph の親へ移動 | `NavController.navigateUp()` | system back ではなく Up semantics を明示する | `false` 時の fallback |
| 現在 destination を明示的に 1 つ pop | `NavController.popBackStack()` | navigation operation を直接表現する | callback cleanup を bypass してよいか |
| drawer / selection / dialog を先に閉じる | lifecycle-aware `OnBackPressedCallback` | UI state ごとに enabled を管理できる | callback 登録順と owner |
| gesture progress に合わせて UI を動かす | supported predictive back API / library built-in support | start / progress / cancel / commit を扱う | 実機 animation test |
| 次 callback / fallback へ進む | self-disable + Dispatcher 再投入 | 同じ callback の再選択を避ける | finally で enabled を戻す要否 |

この表は最終採用 API や優先度を決定しない。最終判断は Human Decision とする。

## テスト仕様（Verification Specification）

### Callback order

- Given: Activity callback を先、Fragment callback を後に登録し、両方 enabled。
- When: system back または Dispatcher へ programmatic back を投入する。
- Then: Fragment callback だけが最初に呼ばれる。
- And: Fragment callback を disabled にすると Activity callback が呼ばれる。

### Dispatcher / direct navigation difference

- Given: selection mode callback が enabled、back stack に前画面がある。
- When: toolbar から Dispatcher を呼ぶ。
- Then: selection mode だけが終了し、destination は変わらない。
- When: toolbar から `navigateUp()` を直接呼ぶ。
- Then: selection callback は呼ばれず、destination が変わる。

### Fallback recursion

- Given: callback 内から次 handler へ委譲する。
- When: self-disable して Dispatcher へ再投入する。
- Then: `[fragment-callback, activity-callback]` の順になる。
- And: self-disable なしの実装を production に残さない。

### Gesture lifecycle

- Given: predictive back 対応画面。
- When: gesture を途中で cancel する。
- Then: destination と business state は確定変更されない。
- When: gesture を commit する。
- Then: callback / navigation が 1 回だけ確定する。

必要なテスト層:
- JVM unit test: callback order、enabled、fallback recursion。
- Robolectric / instrumentation: Activity / Fragment lifecycle と Navigation destination。
- Manual / device: predictive animation、progress、cancel、3-button navigation。

## Fact / Evidence / Confidence

| Fact | Evidence | Confidence |
| --- | --- | --- |
| Android 16 / target 36 では predictive back animations が default enabled で `onBackPressed()` / `KEYCODE_BACK` は通常呼ばれない | Android 16 Behavior Change / AOSP report evidence | High |
| `OnBackPressedDispatcher` は最後に追加された enabled callback を優先し、なければ fallback を実行する | AndroidX API reference / existing unit test examples | High |
| `onBackPressedDispatcher.onBackPressed()` は callback chain へ event を投入し、親 method だけを呼ぶ API ではない | AndroidX API semantics | High |
| toolbar から Dispatcher を呼んでも gesture progress / cancel は発生しない | input source と predictive back guide からの解釈 | High |
| 対象アプリ実機で期待する callback 順になる | 未検証 | Low |

## References

### Entry Point

- https://developer.android.com/about/versions/16/behavior-changes-16#predictive-back

### Official Documentation

- https://developer.android.com/guide/navigation/custom-back/predictive-back-gesture
- https://developer.android.com/guide/navigation/custom-back/support-animations
- https://developer.android.com/reference/androidx/activity/OnBackPressedDispatcher
- https://developer.android.com/reference/androidx/activity/OnBackPressedCallback
- https://developer.android.com/reference/android/window/OnBackInvokedDispatcher
- https://developer.android.com/reference/androidx/navigation/NavController

### Source Code

- https://android.googlesource.com/platform/frameworks/base/+/android-16.0.0_r4/core/java/android/window/WindowOnBackInvokedDispatcher.java
- https://android.googlesource.com/platform/frameworks/base/+/android-16.0.0_r4/core/java/android/view/ViewRootImpl.java

### Validation

- 実機 gesture / instrumentation 検証は未実施。
- callback order / fallback の Java unit test は implementation examples file を参照する。
