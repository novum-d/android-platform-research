# Migration or opt-out required for predictive back - 実装例（Implementation Examples）

## 位置づけ（Scope）

このファイルは、Predictive back default enabled の調査レポートに対する実装例である。
根拠、適用条件、classification、confidence、Human Decision は primary report / one-page summary を正とする。

Primary report:
- [migration-or-opt-out-required-for-predictive-back.md](migration-or-opt-out-required-for-predictive-back.md)

One-page summary:
- [migration-or-opt-out-required-for-predictive-back-summary.md](../../../summaries/target/user-experience-and-system-ui/migration-or-opt-out-required-for-predictive-back-summary.md)

## 対象（Target）

Android 16 Behavior Change:
- Document: https://developer.android.com/about/versions/16/behavior-changes-16#predictive-back
- Section: Migration or opt-out required for predictive back

適用条件の要点:
- OS アップデート / 全アプリ: No。targetSdkVersion 35 以下のアプリに OS アップデートだけで適用される根拠は確認していない。
- targetSdkVersion 36 以上: Yes。Android 16 以上端末上で predictive back が default enabled になる。
- その他の必須条件: legacy `onBackPressed()` / `KEYCODE_BACK` / custom back intercept に依存している場合に実質影響が出る。

## 使い方（How to Use）

- primary report の「対応候補」には、短い代表例とこのファイルへのリンクだけを置く。
- このファイルのコードは移行方針を具体化するための例であり、アプリの navigation stack、状態管理、dialog 実装に合わせて調整する。
- 一時 opt-out は移行までの互換性維持に限定し、対象 Activity、理由、削除条件を記録する。

## 対応方針（Implementation Strategy）

推奨方針:
- `KEYCODE_BACK` や `Activity.onBackPressed()` override ではなく、AndroidX Activity / Navigation / Compose の supported back navigation APIs へ寄せる。

一時対応:
- 移行が間に合わない Activity に限定して `android:enableOnBackInvokedCallback="false"` を指定する。

避けるべき方針:
- `dispatchKeyEvent()` / `onKeyDown()` / `onKeyUp()` で `KEYCODE_BACK` を恒久的に処理し続ける。
- application 全体へ broad opt-out を設定し、移行対象を見えなくする。

## 例 1: Views / Fragment で確認 dialog を出す

目的:
- 未保存変更や転送中断確認など、戻る操作を一時的に intercept する画面を `OnBackPressedCallback` に移行する。

```kotlin
class EditFragment : Fragment(R.layout.edit_fragment) {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        val callback = object : OnBackPressedCallback(true) {
            override fun handleOnBackPressed() {
                if (viewModel.hasUnsavedChanges) {
                    showDiscardConfirmDialog()
                    return
                }

                isEnabled = false
                requireActivity().onBackPressedDispatcher.onBackPressed()
            }
        }

        requireActivity().onBackPressedDispatcher.addCallback(
            viewLifecycleOwner,
            callback,
        )
    }
}
```

注意点:
- callback は `viewLifecycleOwner` に紐付け、Fragment view 破棄後に残らないようにする。
- 常に back を消費する callback にしない。画面側で処理しない状態では、通常の navigation に戻す。

## 例 2: Compose で確認 dialog を出す

目的:
- Compose 画面で `KEYCODE_BACK` を直接扱わず、`BackHandler` で画面状態に応じた戻る処理を行う。

```kotlin
@Composable
fun TransferScreen(
    uiState: TransferUiState,
    onCancelTransfer: () -> Unit,
    onNavigateBack: () -> Unit,
) {
    var showConfirmDialog by rememberSaveable { mutableStateOf(false) }

    BackHandler(enabled = uiState.isTransferring) {
        showConfirmDialog = true
    }

    if (showConfirmDialog) {
        AlertDialog(
            onDismissRequest = { showConfirmDialog = false },
            confirmButton = {
                TextButton(onClick = onCancelTransfer) {
                    Text("Cancel transfer")
                }
            },
            dismissButton = {
                TextButton(onClick = { showConfirmDialog = false }) {
                    Text("Continue")
                }
            },
            title = { Text("Cancel transfer?") },
            text = { Text("The current transfer will stop.") },
        )
    }

    TransferContent(
        uiState = uiState,
        onNavigateBack = onNavigateBack,
    )
}
```

注意点:
- `BackHandler` は `enabled` が true の間だけ戻る操作を消費する。
- predictive back animation の見え方まで作り込む場合は、利用中の Compose / Activity / Navigation version の predictive back support を別途確認する。

## 例 3: Navigation Component で内部 stack を pop する

目的:
- Activity や Fragment の `onBackPressed()` override ではなく、Navigation Component の stack 管理へ戻る処理を寄せる。

```kotlin
val navController = findNavController(R.id.nav_host_fragment)

onBackPressedDispatcher.addCallback(this, object : OnBackPressedCallback(true) {
    override fun handleOnBackPressed() {
        val handled = navController.popBackStack()
        if (!handled) {
            isEnabled = false
            onBackPressedDispatcher.onBackPressed()
        }
    }
})
```

注意点:
- nested navigation、dialog destination、bottom sheet などを使う場合は、画面ごとの stack 状態をテストする。
- Fragment 側で個別 callback を追加する場合は、Activity 側の broad callback と競合しないように責務を分ける。

## 例 4: 一時 opt-out を Activity に限定する

目的:
- 移行が間に合わない legacy flow だけ一時的に旧 back behavior を維持する。

```xml
<activity
    android:name=".LegacyPairingActivity"
    android:enableOnBackInvokedCallback="false" />
```

注意点:
- application 全体ではなく、移行できていない Activity に限定する。
- issue / TODO / migration plan に削除条件を残す。
- Android 16 / targetSdkVersion 36 の検証では、opt-out あり / なしの両方を比較する。

## 例 5: 旧 `KEYCODE_BACK` 処理の置き換え対象を見つける

目的:
- 移行前の棚卸しで、Android 16 / targetSdkVersion 36 で呼ばれなくなる可能性がある back handling を特定する。

```bash
rg -n "KEYCODE_BACK|onBackPressed|dispatchKeyEvent|onKeyDown|onKeyUp|OnBackPressedCallback|BackHandler" app src
```

注意点:
- `KEYCODE_BACK` の検出結果は、入力補助、テストコード、古い workaround も含み得るため、画面遷移に関係するものだけを移行対象として分類する。
- 棚卸し結果は、Android 16 / targetSdkVersion 36 の manual test matrix と対応させる。

## テスト観点（Verification）

- Android 16 / targetSdkVersion 35: OS アップデートだけで legacy flow が変わらないことを確認する。
- Android 16 / targetSdkVersion 36: supported back callback path が使われることを確認する。
- Android 16 / targetSdkVersion 36 + migration: `onBackPressed` / `KEYCODE_BACK` 依存なしで確認 dialog、internal stack pop、task exit が期待通り動くことを確認する。
- Android 16 / targetSdkVersion 36 + temporary opt-out: opt-out 対象 Activity だけ legacy behavior になることを確認する。
- gesture navigation と 3-button navigation の両方で戻る操作を確認する。

## References

- https://developer.android.com/about/versions/16/behavior-changes-16#predictive-back
- https://developer.android.com/guide/navigation/custom-back/predictive-back-gesture
- https://developer.android.com/reference/android/window/OnBackInvokedCallback
- https://developer.android.com/guide/topics/manifest/activity-element#enableOnBackInvokedCallback
