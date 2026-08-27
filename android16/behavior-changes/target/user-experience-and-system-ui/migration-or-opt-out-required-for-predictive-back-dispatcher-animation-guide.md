# Predictive Back - Dispatcher 移行後にアニメーションが消える原因と対処

## 位置づけ（Scope）

このファイルは、AndroidX `OnBackPressedDispatcher` へ移行した後に Predictive Back animation が見えなくなった場合の原因切り分けと対処をまとめる補足資料である。
Behavior Change の根拠、適用条件、分類、confidence、人間の判断は、主レポートと1ページ要約を正とする。

主レポート:
- [migration-or-opt-out-required-for-predictive-back.md](migration-or-opt-out-required-for-predictive-back.md)

1ページ要約:
- [migration-or-opt-out-required-for-predictive-back-summary.md](../../../summaries/target/user-experience-and-system-ui/migration-or-opt-out-required-for-predictive-back-summary.md)

実装例:
- [migration-or-opt-out-required-for-predictive-back-implementation-examples.md](../../implementation-examples/migration-or-opt-out-required-for-predictive-back-implementation-examples.md)

実行挙動の比較:
- [migration-or-opt-out-required-for-predictive-back-runtime-behavior-comparison.md](migration-or-opt-out-required-for-predictive-back-runtime-behavior-comparison.md)

## 結論（Conclusion）

`OnBackPressedDispatcher` 自体が Predictive Back を無効化するわけではない。
主な原因は次の2つである。

| 現象 | 原因 | 対処 |
| --- | --- | --- |
| toolbar / custom button から戻った時だけ animation がない | `onBackPressedDispatcher.onBackPressed()` は programmatic invocation であり、system gesture の start / progress / cancel を生成しない | toolbar Up なら `navigateUp()`、明示的な pop なら `popBackStack()` を使い、通常の navigation transition として扱う |
| 実際の edge swipe でも system animation がない | Activity / root destination で enabled な consuming callback が Back を intercept している | callback を必要な UI state の間だけ enabled にし、それ以外は Navigation library または system に Back を委ねる |

Predictive Back animation は「戻る処理を実行した結果」ではなく、system gesture の lifecycle と戻り先の管理に基づいて描画される。
確定済み Back を programmatic に dispatcher へ投入しても、system gesture animation を再現することはできない。

## 原因 1: Dispatcher の programmatic invocation

次の呼び出しは、現在 enabled な callback を登録順の逆順で選択し、最終的な Back 処理を即時実行する。

```kotlin
onBackPressedDispatcher.onBackPressed()
```

この呼び出しには、実際の gesture が持つ次の入力がない。

```text
touch start
  -> back started
  -> progress 0.0 ... 1.0
  -> cancelled または completed
```

そのため、toolbar click から dispatcher を呼ぶと system back と同じ callback chain / fallback を利用できるが、gesture progress や Predictive Back preview は発生しない。

`OnBackPressedDispatcher.dispatchOnBackStarted()`、`dispatchOnBackProgressed()`、`dispatchOnBackCancelled()` は API reference 上で `VisibleForTesting` とされている。
アプリが toolbar click から疑似的な system gesture を組み立てるためには使用しない。

### 操作の意味に応じた API 選択

| UI 操作 | 推奨 API | Animation の扱い |
| --- | --- | --- |
| system Back gesture | Navigation / AndroidX の supported back integration | system または library が gesture lifecycle を処理 |
| toolbar / app bar の Up | `NavController.navigateUp()` | 通常の Up transition |
| 現在 destination を明示的に pop | `NavController.popBackStack()` | 通常の pop transition |
| custom button から system Back と同じ最終処理順を使う | `onBackPressedDispatcher.onBackPressed()` | callback chain は同じだが Predictive Back gesture animation はない |

## 原因 2: enabled callback による interception

次のような Activity-wide callback を常時 enabled にすると、通常状態でもアプリが Back を消費する。

```kotlin
onBackPressedDispatcher.addCallback(
    this,
    object : OnBackPressedCallback(true) {
        override fun handleOnBackPressed() {
            navController.popBackStack()
        }
    },
)
```

公式ドキュメントでは、root Activity で Back を intercept すると back-to-home animation が無効になり、Activity で intercept すると cross-activity animation が無効になると説明されている。
enabled な consuming callback が存在する場合、アプリ側が Back を処理する責務を持つため、system の既定 animation を期待しない。

### 推奨する enabled 管理

callback は Back を独自に処理する UI state の間だけ有効にする。

```kotlin
val callback = object : OnBackPressedCallback(false) {
    override fun handleOnBackPressed() {
        closeSelectionMode()
    }
}

onBackPressedDispatcher.addCallback(viewLifecycleOwner, callback)

viewLifecycleOwner.lifecycleScope.launch {
    repeatOnLifecycle(Lifecycle.State.STARTED) {
        viewModel.isSelectionMode.collect { isSelectionMode ->
            callback.isEnabled = isSelectionMode
        }
    }
}
```

適切な enabled 条件の例:
- drawer が開いている。
- selection mode 中である。
- 未保存変更があり確認 dialog を表示する必要がある。
- 内部 UI stack が存在し、Navigation stack より先に閉じる必要がある。

callback を無効にすべき状態の例:
- 通常の Navigation back stack を戻るだけである。
- root destination から Home へ戻る。
- Activity stack を戻る。
- analytics / logging / business logic の観測だけが目的である。

Android 16 以上で system Back を消費せずに観測する必要がある場合は、platform `OnBackInvokedCallback` の `PRIORITY_SYSTEM_NAVIGATION_OBSERVER` を候補とする。
Compose destination の破棄を記録するだけなら、destination change や destination-scoped `ViewModel.onCleared()` など、Back interception 以外の lifecycle signal も検討する。

## アプリ内遷移を gesture に追従させる場合

最初に、利用中の navigation library / UI component が持つ built-in Predictive Back support を確認する。
独自 progress animation は、built-in transition では要件を満たせない場合に追加する。

| UI 構成 | 第一候補 | 独自対応が必要な場合 |
| --- | --- | --- |
| Navigation Compose | `navigation-compose` 2.8.0 以上の `NavHost` | `popEnterTransition` / `popExitTransition`、または画面固有の `PredictiveBackHandler` |
| Navigation 3 | `NavDisplay` の built-in predictive pop | `predictivePopTransitionSpec` または Navigation Event API |
| Compose custom screen | `PredictiveBackHandler` | `BackEventCompat.progress` を UI state に反映 |
| Views / Fragment | Navigation / Fragment の対応 transition | `OnBackPressedCallback` の started / progressed / cancelled / pressed callbacks |
| Material component | component の built-in support | component state と callback enabled 条件を確認 |

gesture lifecycle ごとの責務を分ける。

| Lifecycle | 実行する処理 | 実行しない処理 |
| --- | --- | --- |
| started | preview の準備、初期値保存 | destination pop、永続 state 更新 |
| progressed | progress に応じた一時的な描画更新 | navigation commit |
| cancelled | 一時描画を初期状態へ戻す | destination pop |
| completed / pressed | destination pop、確定処理を1回だけ実行 | cancel reset |

具体的な Compose、Views、Navigation Event のコードは、実装例ファイルの「gesture progress に合わせた animation」を参照する。

## 切り分けチェックリスト

1. animation が消える入力を分ける。
   - toolbar / custom button だけか。
   - 実際の edge swipe でも発生するか。
2. Activity、Fragment、Composable の callback を検索する。

```bash
rg -n "OnBackPressedCallback|BackHandler|PredictiveBackHandler|OnBackInvokedCallback" app src
```

3. root Activity / root destination で consuming callback が常時 enabled になっていないか確認する。
4. callback の enabled 条件が Back 発生後の `if` ではなく、事前の observable UI state で管理されているか確認する。
5. Navigation library の built-in callback と Activity-wide callback が競合していないか確認する。
6. `android:enableOnBackInvokedCallback="false"` が application / Activity に残っていないか確認する。
7. AndroidX Activity、Navigation、Compose / Material の利用 version が必要な Predictive Back support を含むか確認する。
8. gesture cancel、root destination、cross-activity、back-to-home を実機または emulator で別々に確認する。

## Expected / Observed

| Scenario | Expected | Observed | Result |
| --- | --- | --- | --- |
| toolbar から dispatcher | callback chain は実行されるが gesture progress はない | 未実施 | 未実施 |
| root で consuming callback が enabled | system back-to-home animation は実行されない | 未実施 | 未実施 |
| root で consuming callback が disabled | system が Back を処理し、対応条件下で system animation が実行される | 未実施 | 未実施 |
| Navigation Compose built-in support | swipe progress に応じた in-app transition が実行される | 未実施 | 未実施 |
| custom progress callback | cancel では state を確定せず、completed 時だけ navigation する | 未実施 | 未実施 |

## Fact / Evidence / Confidence

| Fact | Evidence | Confidence |
| --- | --- | --- |
| `onBackPressedDispatcher.onBackPressed()` は enabled callback を逆順に選択し、gesture progress 自体は生成しない | `OnBackPressedDispatcher` API reference | High |
| root Activity / Activity で Back を intercept すると back-to-home / cross-activity system animation が無効になる | Predictive Back setup guide | High |
| enabled な consuming callback は system animation を実行せず、アプリが Back を処理する必要がある | Predictive Back callback best practices | High |
| Compose custom animation は `PredictiveBackHandler`、Views custom animation は progress callbacks で lifecycle を扱える | Predictive Back animation guides | High |
| 対象アプリで animation が消えた直接原因 | 対象コードおよび実機挙動は未確認 | Low |

## References

### Entry Point

- https://developer.android.com/about/versions/16/behavior-changes-16#predictive-back

### Official Documentation

- https://developer.android.com/develop/ui/compose/system/predictive-back-setup
- https://developer.android.com/guide/navigation/custom-back/predictive-back-gesture
- https://developer.android.com/guide/navigation/custom-back/support-animations
- https://developer.android.com/guide/navigation/custom-back/support-animations-views
- https://developer.android.com/reference/androidx/activity/OnBackPressedDispatcher
- https://developer.android.com/guide/navigation/navigation-event/handle-back

### Validation

- 対象アプリの callback 登録状態と実機 gesture は未確認。
- programmatic invocation と実 gesture は、同じ画面状態で別ケースとして検証する必要がある。
