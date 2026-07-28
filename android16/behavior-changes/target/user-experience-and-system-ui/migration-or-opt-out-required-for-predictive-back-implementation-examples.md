# Predictive Back への移行または opt-out が必要 - 実装例

## 位置づけ（Scope）

このファイルは、Predictive Back が既定で有効になる変更に関する調査レポートの実装例である。
根拠、適用条件、分類、confidence、人間の判断は、主レポートと1ページ要約を正とする。

主レポート:
- [migration-or-opt-out-required-for-predictive-back.md](migration-or-opt-out-required-for-predictive-back.md)

1ページ要約:
- [migration-or-opt-out-required-for-predictive-back-summary.md](../../../summaries/target/user-experience-and-system-ui/migration-or-opt-out-required-for-predictive-back-summary.md)

実行挙動の比較:
- [migration-or-opt-out-required-for-predictive-back-runtime-behavior-comparison.md](migration-or-opt-out-required-for-predictive-back-runtime-behavior-comparison.md)

Dispatcher 移行後に animation が消える場合の切り分け:
- [migration-or-opt-out-required-for-predictive-back-dispatcher-animation-guide.md](migration-or-opt-out-required-for-predictive-back-dispatcher-animation-guide.md)

## 対象（Target）

Android 16 Behavior Change:
- 文書: https://developer.android.com/about/versions/16/behavior-changes-16#predictive-back
- セクション: Migration or opt-out required for predictive back

適用条件の要点:
- OS アップデート / 全アプリ: いいえ。targetSdkVersion 35 以下のアプリに、OS アップデートだけで適用される根拠は確認していない。
- targetSdkVersion 36 以上: はい。Android 16 以上の端末上で Predictive Back が既定で有効になる。
- その他の必須条件: 従来の `onBackPressed()` / `KEYCODE_BACK` / 独自の Back 処理に依存している場合に、実質的な影響が出る。

## 使い方（How to Use）

- 主レポートの「対応候補」には、短い代表例とこのファイルへのリンクだけを置く。
- このファイルのコードは移行方針を具体化するための例であり、アプリの navigation stack、状態管理、dialog の実装に合わせて調整する。
- 各例は、既存コードで何を探し、どの API / pattern へ置き換えるかを `Before` / `After` で示す。
- 一時的な opt-out は、移行まで互換性を維持する目的に限定し、対象 Activity、理由、削除条件を記録する。

## 対応方針（Implementation Strategy）

推奨方針:
- `KEYCODE_BACK` や `Activity.onBackPressed()` override ではなく、AndroidX Activity / Navigation / Compose の supported back navigation APIs へ寄せる。
- 単純に戻る操作を intercept するだけなら `OnBackPressedCallback` / Compose `BackHandler` を使う。
- callback は独自処理が必要な UI state の間だけ enabled にし、通常の navigation、cross-activity、back-to-home は library または system に委ねる。
- predictive back gesture の進捗に合わせて UI を動かす場合は、Compose `PredictiveBackHandler`、Views の `OnBackPressedCallback` progress callbacks、または Navigation Event APIs を検討する。

一時対応:
- 移行が間に合わない Activity に限定して `android:enableOnBackInvokedCallback="false"` を指定する。

避けるべき方針:
- `dispatchKeyEvent()` / `onKeyDown()` / `onKeyUp()` で `KEYCODE_BACK` を恒久的に処理し続ける。
- analytics / logging だけのために Activity-wide callback を常時 enabled にする。
- toolbar から `onBackPressedDispatcher.onBackPressed()` を呼べば system gesture progress も再現できると考える。
- application 全体へ broad opt-out を設定し、移行対象を見えなくする。

API 選択:
- 戻る操作で dialog 表示、drawer close、内部 stack pop だけを行う場合は `OnBackPressedCallback` / `BackHandler` を優先する。
- gesture 進捗に合わせた custom animation が必要な場合だけ `PredictiveBackHandler` や Views progress callbacks を使う。
- Navigation Event API は、Navigation 3 や独自 navigation layer で back gesture lifecycle を扱う場合に検討する。既存 navigation library が predictive back をサポートしている場合は、その built-in support を優先する。
- opt-out は API 移行までの一時対応とし、Activity 単位に限定する。

## 移行時の重要ポイント（Important Migration Notes）

非推奨 API を使わない:
- `Activity.onBackPressed()` override、`super.onBackPressed()`、`onBackPressed()` の直接呼び出しは移行対象として扱う。
- `KEYCODE_BACK` を `dispatchKeyEvent()` / `onKeyDown()` / `onKeyUp()` で恒久的に処理しない。
- 移行後は `OnBackPressedCallback` を登録し、必要に応じて `onBackPressedDispatcher.onBackPressed()` または `NavController.navigateUp()` / `popBackStack()` に委譲する。

挙動を統一する:
- 端末の戻る操作、toolbar back、custom close button を同じ処理経路にしたい場合は `onBackPressedDispatcher.onBackPressed()` を使う。
- ただし toolbar / custom button からの programmatic invocation には gesture start / progress / cancel がないため、Predictive Back animation は発生しない。
- toolbar / app bar の Up 操作として Navigation graph 上の親へ戻したい場合は `NavController.navigateUp()` を優先する。
- Fragment back stack を明示的に 1 つ戻したい場合は `NavController.popBackStack()` を使う。
- `finish()` へ直接置き換えると、Fragment / Navigation Component / registered callback を飛ばす可能性があるため、既存挙動と一致するか確認する。

`setEnabled(false)` が必要な背景:
- `OnBackPressedDispatcher` は enabled な callback を探して呼ぶ。
- callback の中から `onBackPressedDispatcher.onBackPressed()` を呼ぶと、同じ callback がまだ enabled の場合、再び同じ callback が選ばれる。
- そのため「この callback では処理せず次の handler / fallback に渡す」場合は、自分自身を一時的に disabled にしてから dispatcher に委譲する。

```kotlin
isEnabled = false
try {
    onBackPressedDispatcher.onBackPressed()
} finally {
    isEnabled = true
}
```

設定しない場合に起きること:
- 同じ `OnBackPressedCallback` が再度呼ばれ、無限再帰または stack overflow になる可能性がある。
- fallback したつもりでも、次の callback / Activity fallback に到達しない。
- handler の優先順が見えにくくなり、toolbar back と system back の挙動差分を見落としやすい。

`setEnabled(false)` が不要なケース:
- callback 内で処理を完結し、dispatcher に委譲しない場合。
- `NavController.navigateUp()` / `popBackStack()` を直接呼ぶ場合。
- helper / toolbar click など callback 外から `onBackPressedDispatcher.onBackPressed()` を呼ぶ場合。
- UI state に応じて callback の enabled 状態を事前に管理している場合。

dispatcher 移行後の処理順:
- legacy `Activity.onBackPressed()` override では、Activity の override が戻る処理の中心になり、その中から `super.onBackPressed()`、FragmentManager、Navigation Component、`finish()` などへ流していた。
- `OnBackPressedDispatcher` へ移行すると、dispatcher が enabled な `OnBackPressedCallback` を登録順の逆順で探して呼ぶ。つまり、後から登録された enabled callback が先に処理される。
- 親 Activity が先に callback を登録し、子 Activity が後で callback を登録する構造では、通常は子 callback が先に呼ばれる。子 callback が処理しない場合に自分を disabled にして dispatcher に委譲すると、次の候補として親 callback に進める。
- Activity に broad callback を常時 enabled で登録すると、Fragment / Navigation Component / dialog / bottom sheet などの callback より先に back を消費し、従来呼ばれていた処理をブロックする可能性がある。
- root Activity / root destination で broad callback が enabled の場合は、system の back-to-home / cross-activity animation も実行されない。callback が処理すべき UI state を事前に `isEnabled` へ反映する。
- 画面固有の back handling は Fragment の `onViewCreated()` で `viewLifecycleOwner` に紐付け、Activity callback は Activity 全体の責務に限定する。
- callback が処理すべき状態でない場合は、事前に `setEnabled(false)` にしておくか、callback 内で一時的に disabled にして dispatcher に委譲する。

`onBackPressedDispatcher.onBackPressed()` の意味:
- `onBackPressedDispatcher.onBackPressed()` は、子クラスの `onBackPressed()` 相当の method call ではない。
- 現在の Activity の dispatcher に back event を投入し、その時点で enabled な callback chain を先頭から処理させる操作である。
- 子 callback が最後に登録され、かつ enabled の場合は、結果として子 callback が呼ばれるため「子の戻る処理」のように見える。ただし実際には dispatcher の callback selection の結果であり、親 callback、Fragment callback、Navigation callback、Activity fallback に進む可能性もある。
- 子 callback の中からそのまま `onBackPressedDispatcher.onBackPressed()` を呼ぶと、子 callback 自身が再選択され得る。親 callback に進めたい場合は、子 callback を一時的に disabled にしてから dispatcher に委譲する。

処理順のテスト観点:
- Activity callback、Fragment callback、Navigation Component の callback がある画面で、どれが先に呼ばれるかを確認する。
- 親 callback 登録後に子 callback を登録する構成では、子 callback が先に呼ばれ、子が disabled になった時だけ親 callback に進むことを確認する。
- Fragment 遷移後、前画面の callback が残っていないことを確認する。
- drawer / dialog / bottom sheet / selection mode など、先に閉じるべき UI が Fragment navigation や Activity finish より先に処理されることを確認する。
- toolbar back / custom close button / system back が同じ経路を期待する画面では、同じ callback 順で処理されることを確認する。
- callback が常時 enabled になっていて、他の callback や Navigation Component の back handling を塞いでいないことを確認する。

## 移行対象の見つけ方（Finding Existing Code）

探すコード:
- `Activity.onBackPressed()` / `Dialog.onBackPressed()` override。
- `KEYCODE_BACK` を扱う `dispatchKeyEvent()` / `onKeyDown()` / `onKeyUp()`。
- Fragment / Activity / Compose で独自に戻る操作を intercept している箇所。
- `android:enableOnBackInvokedCallback="false"` の broad opt-out。

```bash
rg -n "KEYCODE_BACK|onBackPressed|dispatchKeyEvent|onKeyDown|onKeyUp|OnBackPressedCallback|BackHandler|enableOnBackInvokedCallback" app src
```

分類:

| 既存実装（Existing pattern） | 移行先（Migration target） | 優先度 | Notes |
| --- | --- | --- | --- |
| `Activity.onBackPressed()` override | `OnBackPressedDispatcher` / Navigation Component | Must | targetSdkVersion 36 で呼ばれない前提で移行する |
| `onBackPressed()` 内で `super.onBackPressed()` を fallback として呼ぶ | `OnBackPressedCallback` を一時的に無効化して dispatcher に戻す | Must | legacy override の fallback 経路を dispatcher 経由に置き換える |
| override ではない helper / click handler で `super.onBackPressed()` を呼ぶ | `onBackPressedDispatcher.onBackPressed()` または `NavController.navigateUp()` | Must | system back と同じ経路に戻すのか、navigation graph の up として扱うのかを分ける |
| 親クラスの `super.onBackPressed()` に共通 back logic がある | 親クラスの共通処理を `protected` method または親側 callback に切り出す | Must | dispatcher には親クラスの戻る処理だけを直接呼ぶ API はない |
| `KEYCODE_BACK` を `dispatchKeyEvent()` で処理 | `OnBackPressedCallback` / `BackHandler` | Must | key event ではなく back navigation callback として扱う |
| Compose 画面で Activity 側の back handler に依存 | `BackHandler` | Recommended | 画面状態と back intercept 条件を Composable 側で明示する |
| Compose 画面で back gesture 進捗に合わせた animation が必要 | `PredictiveBackHandler` | Recommended | `BackEventCompat.progress` を使い、完了 / cancel を分ける |
| View 画面で back gesture 進捗に合わせた animation が必要 | `OnBackPressedCallback` progress callbacks | Optional | default animation で足りない場合だけ使う |
| Navigation Event 対応が必要な画面 | `NavigationEventHandler` / `NavigationBackHandler` | Optional | Navigation 3 など built-in support がある場合はそちらを優先する |
| 移行未完了 Activity | Activity-level `android:enableOnBackInvokedCallback="false"` | Temporary | 削除条件と対象 Activity を記録する |

## 移行マップ（Migration Map）

| Before | After | 目的 |
| --- | --- | --- |
| `onBackPressed()` override で確認 dialog を出す | `OnBackPressedCallback` で確認 dialog を出す | legacy callback 依存をなくす |
| `super.onBackPressed()` で通常 back に委譲する | callback を `isEnabled = false` にして `onBackPressedDispatcher.onBackPressed()` へ委譲する | fallback 経路を dispatcher に戻す |
| helper / toolbar click から `super.onBackPressed()` を呼ぶ | `onBackPressedDispatcher.onBackPressed()` または `NavController.navigateUp()` を呼ぶ | 呼び出し元の意図を保ったまま unsupported API 依存をなくす |
| 親クラスの `super.onBackPressed()` だけを呼びたい | `protected performDefaultBack()` などに親の共通処理を切り出して呼ぶ | dispatcher chain と親クラス共通処理を混同しない |
| `dispatchKeyEvent(KEYCODE_BACK)` で内部 stack を pop する | Navigation Component / `OnBackPressedDispatcher` で pop する | key dispatch ではなく navigation stack に責務を寄せる |
| Compose 画面が Activity の back 処理に依存する | Composable 内で `BackHandler(enabled = ...)` を使う | 画面状態に応じた intercept 条件を明示する |
| Compose custom animation を back 完了後だけ実行する | `PredictiveBackHandler` で progress / completed / cancelled を分ける | gesture 中の preview と cancel reset に対応する |
| View custom animation を back 完了後だけ実行する | `handleOnBackStarted` / `handleOnBackProgressed` / `handleOnBackCancelled` / `handleOnBackPressed` に分ける | gesture 進捗に合わせて View を動かす |
| application 全体の opt-out | Activity 単位の一時 opt-out + 移行計画 | predictive back 対応済み画面まで無効化しない |

## 例 1: Views / Fragment で確認 dialog を出す

目的:
- 未保存変更や転送中断確認など、戻る操作を一時的に intercept する画面を `OnBackPressedCallback` に移行する。

既存実装で探す箇所:
- `Activity.onBackPressed()` または `Fragment` から Activity の `onBackPressed()` override に処理を寄せている箇所。
- 未保存変更、転送中断、pairing flow 中断などの確認 dialog を back 操作で出している箇所。

移行前:

```kotlin
@Deprecated("Use OnBackPressedDispatcher")
override fun onBackPressed() {
    if (viewModel.hasUnsavedChanges) {
        showDiscardConfirmDialog()
    } else {
        super.onBackPressed()
    }
}
```

移行後:

```kotlin
class EditFragment : Fragment(R.layout.edit_fragment) {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        val callback = object : OnBackPressedCallback(false) {
            override fun handleOnBackPressed() {
                showDiscardConfirmDialog()
            }
        }

        requireActivity().onBackPressedDispatcher.addCallback(
            viewLifecycleOwner,
            callback,
        )

        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.hasUnsavedChanges.collect { hasUnsavedChanges ->
                    callback.isEnabled = hasUnsavedChanges
                }
            }
        }
    }
}
```

移行手順:
1. `onBackPressed()` override 内の条件分岐を画面単位の callback に移す。
2. callback を `viewLifecycleOwner` に紐付ける。
3. 未保存状態を callback の `isEnabled` へ事前反映し、処理しない状態では通常の戻る処理へ渡す。

確認観点:
- 未保存変更がある状態では確認 dialog が出る。
- 未保存変更がない状態では通常の navigation stack に戻る。
- Fragment view 再生成後に callback が重複登録されない。

注意点:
- callback は `viewLifecycleOwner` に紐付け、Fragment view 破棄後に残らないようにする。
- 常に back を消費する callback にしない。画面側で処理しない状態では、通常の navigation に戻す。
- callback 内で未保存状態を初めて判定して fallback するのではなく、gesture 開始前から `isEnabled` を同期する。

## 例 2: Compose で確認 dialog を出す

目的:
- Compose 画面で `KEYCODE_BACK` を直接扱わず、`BackHandler` で画面状態に応じた戻る処理を行う。

既存実装で探す箇所:
- Compose 画面の戻る操作を Activity / Fragment 側の `onBackPressed()` override でまとめて処理している箇所。
- 転送中、編集中、setup wizard 中など、画面状態に応じて戻る動作を変えている箇所。

移行前:

```kotlin
override fun onBackPressed() {
    if (transferViewModel.isTransferring) {
        transferViewModel.showCancelConfirmation()
    } else {
        super.onBackPressed()
    }
}
```

移行後:

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

移行手順:
1. Activity 側の back 分岐を Composable の UI state に対応させる。
2. `BackHandler(enabled = ...)` に intercept 条件を明示する。
3. dialog の confirm / dismiss で状態更新と navigation の責務を分ける。

確認観点:
- `uiState.isTransferring == true` の間だけ back が確認 dialog を出す。
- 転送中でない状態では親 navigation の戻る処理が動く。
- configuration change 後も dialog 表示状態が壊れない。

注意点:
- `BackHandler` は `enabled` が true の間だけ戻る操作を消費する。
- predictive back animation の見え方まで作り込む場合は、利用中の Compose / Activity / Navigation version の predictive back support を別途確認する。

## 例 3: `super.onBackPressed()` fallback を置き換える

目的:
- 既存の `onBackPressed()` override が「この画面で処理しない場合は `super.onBackPressed()`」としている箇所を、dispatcher 経由の fallback に移行する。

既存実装で探す箇所:
- `super.onBackPressed()` を呼ぶ `Activity.onBackPressed()` override。
- 条件付きで dialog / internal stack / close drawer を処理し、それ以外を `super` に渡している箇所。

移行前:

```kotlin
override fun onBackPressed() {
    if (drawerLayout.isOpen) {
        drawerLayout.close()
    } else {
        super.onBackPressed()
    }
}
```

移行後: drawer の開閉状態を callback の enabled 状態へ事前に反映する

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val callback = object : OnBackPressedCallback(
            drawerLayout.isDrawerOpen(GravityCompat.START),
        ) {
            override fun handleOnBackPressed() {
                drawerLayout.closeDrawer(GravityCompat.START)
            }
        }

        onBackPressedDispatcher.addCallback(this, callback)

        drawerLayout.addDrawerListener(
            object : DrawerLayout.SimpleDrawerListener() {
                override fun onDrawerOpened(drawerView: View) {
                    callback.isEnabled = true
                }

                override fun onDrawerClosed(drawerView: View) {
                    callback.isEnabled = false
                }
            },
        )
    }
}
```

移行手順:
1. `onBackPressed()` override の条件分岐を `OnBackPressedCallback` に移す。
2. drawer の開閉状態を callback の `isEnabled` に事前反映する。
3. drawer が閉じている通常状態では callback を disabled にし、Navigation / system の Back 処理を妨げない。

確認観点:
- drawer が開いている状態では drawer だけが閉じる。
- drawer が閉じている状態では通常の navigation / finish に進む。
- root destination では callback が disabled になり、back-to-home animation を妨げない。

注意点:
- Back gesture が始まってから callback 内の `if` で fallback するより、gesture 開始前から observable UI state に合わせて `isEnabled` を管理する。
- callback 内から dispatcher の次候補へ委譲する必要がある別ケースでは、現在の callback を一時的に disabled にして無限再帰を避ける。

## 例 4: override ではない関数の `super.onBackPressed()` を置き換える

目的:
- `override fun onBackPressed()` ではない helper / click handler / callback から `super.onBackPressed()` を呼んでいる箇所を、意図に応じて dispatcher または Navigation Component に移行する。

既存実装で探す箇所:
- `private fun closeOrBack()`、`onToolbarBackClicked()`、`onCancelClicked()` などから `super.onBackPressed()` を呼んでいる箇所。
- toolbar の戻るボタン、dialog の cancel、custom UI の back affordance が system back と同じ処理を呼びたい箇所。

移行前:

```kotlin
private fun closeOrBack() {
    if (selectionMode) {
        exitSelectionMode()
    } else {
        super.onBackPressed()
    }
}
```

移行後: system back と同じ経路に委譲する場合

```kotlin
private fun closeOrBack() {
    if (selectionMode) {
        exitSelectionMode()
    } else {
        onBackPressedDispatcher.onBackPressed()
    }
}
```

移行後: Navigation graph の up/back として扱う場合

```kotlin
private fun onToolbarBackClicked() {
    val handled = findNavController(R.id.nav_host_fragment).navigateUp()
    if (!handled) {
        onBackPressedDispatcher.onBackPressed()
    }
}
```

移行手順:
1. その関数が「system back と同じ経路」を呼びたいのか、「toolbar up / navigation graph の戻る」を実行したいのかを分類する。
2. system back と同じ経路なら `onBackPressedDispatcher.onBackPressed()` に置き換える。
3. Navigation Component の toolbar / app bar 操作なら `NavController.navigateUp()` または `popBackStack()` を優先し、必要な場合だけ dispatcher に fallback する。

確認観点:
- toolbar back、cancel button、custom close button が従来と同じ destination へ戻る。
- `OnBackPressedCallback` が登録されている画面では、dispatcher 経由で同じ callback が呼ばれる。
- Navigation graph の top-level destination で `navigateUp()` が false になった場合の fallback が期待通りである。

注意点:
- back callback の中から dispatcher に委譲する場合は、例 3 のように現在の callback を一時的に disable して無限再帰を避ける。
- toolbar up は system back と完全に同じ意味ではない場合があるため、常に `onBackPressedDispatcher.onBackPressed()` に置き換えればよいとは限らない。

## 例 5: 親クラスの共通 back 処理を切り出す

目的:
- `super.onBackPressed()` が親クラスの共通戻る処理を実行していた場合に、dispatcher から「親クラスだけ」を直接呼ぼうとせず、共通処理を明示的な method / callback に移す。

既存実装で探す箇所:
- `BaseActivity.onBackPressed()` に全画面共通の close / analytics / navigation fallback がある。
- 子 Activity の `onBackPressed()` override が条件付きで `super.onBackPressed()` を呼んでいる。
- dispatcher 移行後も「親クラスの共通処理だけ」を呼びたい箇所。

移行前:

```java
public abstract class BaseActivity extends AppCompatActivity {
    @Override
    public void onBackPressed() {
        if (closeGlobalOverlayIfNeeded()) {
            return;
        }

        super.onBackPressed();
    }
}

public final class DetailActivity extends BaseActivity {
    @Override
    public void onBackPressed() {
        if (hasUnsavedChanges()) {
            showDiscardConfirmDialog();
        } else {
            super.onBackPressed();
        }
    }
}
```

移行後: 親クラスの共通処理を `protected` method にする

```java
public abstract class BaseActivity extends AppCompatActivity {
    protected boolean performDefaultBack() {
        if (closeGlobalOverlayIfNeeded()) {
            return true;
        }

        return false;
    }
}

public final class DetailActivity extends BaseActivity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        getOnBackPressedDispatcher().addCallback(this, new OnBackPressedCallback(true) {
            @Override
            public void handleOnBackPressed() {
                if (hasUnsavedChanges()) {
                    showDiscardConfirmDialog();
                    return;
                }

                if (performDefaultBack()) {
                    return;
                }

                setEnabled(false);
                try {
                    getOnBackPressedDispatcher().onBackPressed();
                } finally {
                    setEnabled(true);
                }
            }
        });
    }
}
```

移行手順:
1. 親クラスの `onBackPressed()` に入っている共通処理を `protected` method に切り出す。
2. 子クラスの `OnBackPressedCallback` から、その共通処理を明示的に呼ぶ。
3. 親の共通処理で消費しない場合だけ、dispatcher chain に委譲する。

確認観点:
- 親クラスの global overlay / common cleanup が従来通り先に処理される。
- 親クラスの共通処理が消費しない時だけ、Fragment / Navigation / Activity fallback に進む。
- dispatcher へ委譲する時に現在の callback を disabled にして、同じ callback が再帰しない。

注意点:
- `onBackPressedDispatcher.onBackPressed()` は親クラスだけを呼ぶ API ではない。enabled callback chain に back を流す API として扱う。
- 親クラスに共通 callback を登録する設計も可能だが、子クラス callback との登録順と enabled 状態を必ずテストする。
- 親クラス共通処理が Activity finish を直接呼ぶ場合は、Fragment / Navigation Component の back stack を飛ばしてよいか確認する。
- この例の callback を常時 enabled にすると system animation を抑止する。実装時は `hasUnsavedChanges()` または global overlay が存在する間だけ enabled にし、どちらも false の場合は Navigation / system に Back を委ねる。

## 例 6: Navigation Component で内部 stack を pop する

目的:
- Activity や Fragment の `onBackPressed()` override ではなく、Navigation Component の stack 管理へ戻る処理を寄せる。

既存実装で探す箇所:
- `KEYCODE_BACK` や `onBackPressed()` で fragment stack / custom stack を直接 pop している箇所。
- nested navigation や dialog destination をまたぐ back 処理を Activity 側でまとめている箇所。

移行前:

```kotlin
override fun dispatchKeyEvent(event: KeyEvent): Boolean {
    if (event.keyCode == KeyEvent.KEYCODE_BACK && event.action == KeyEvent.ACTION_UP) {
        if (supportFragmentManager.backStackEntryCount > 0) {
            supportFragmentManager.popBackStack()
            return true
        }
    }
    return super.dispatchKeyEvent(event)
}
```

移行後: 標準の Navigation back stack は Navigation Component に委ねる

```kotlin
class MainActivity : AppCompatActivity(R.layout.main_activity) {
    private val navController: NavController
        get() = findNavController(R.id.nav_host_fragment)

    override fun onSupportNavigateUp(): Boolean {
        return navController.navigateUp() || super.onSupportNavigateUp()
    }
}
```

移行手順:
1. `KEYCODE_BACK` で stack を直接 pop する処理を削除する。
2. system Back は Navigation Component / Fragment integration に任せ、Activity-wide callback を追加しない。
3. toolbar Up は `NavController.navigateUp()` で明示し、処理できない場合だけ Activity の Up fallback に渡す。

確認観点:
- nested destination では system gesture が期待通り現在の graph 内を戻る。
- stack が空の場合は Activity の通常 Back / finish に進み、system animation を妨げる callback が残らない。
- dialog destination / bottom sheet がある場合も閉じる順序が崩れない。

注意点:
- nested navigation、dialog destination、bottom sheet などを使う場合は、画面ごとの stack 状態をテストする。
- 独自 UI stack を Navigation stack より先に閉じる必要がある場合だけ、UI state に応じて enabled になる callback を追加する。
- Activity-wide callback から `popBackStack()` を常時呼ぶと、Navigation library の built-in Predictive Back support を bypass または競合させる可能性がある。

## 例 6A: Navigation Compose の built-in Predictive Back を使う

目的:
- 標準の Compose destination 間遷移では独自 callback を追加せず、Navigation Compose の gesture integration と pop transition を使う。

既存実装で探す箇所:
- root の `BackHandler(enabled = true)` から常に `navController.popBackStack()` を呼んでいる箇所。
- `NavHost` の外側で Activity-wide callback を登録し、Compose navigation を手動で戻している箇所。

移行前:

```kotlin
BackHandler(enabled = true) {
    navController.popBackStack()
}
```

移行後:

```kotlin
NavHost(
    navController = navController,
    startDestination = Home,
    popEnterTransition = {
        EnterTransition.None
    },
    popExitTransition = {
        scaleOut(
            targetScale = 0.9f,
            transformOrigin = TransformOrigin(
                pivotFractionX = 0.5f,
                pivotFractionY = 0.5f,
            ),
        )
    },
) {
    composable<Home> {
        HomeScreen()
    }
    composable<Detail> {
        DetailScreen()
    }
}
```

移行手順:
1. `navigation-compose` 2.8.0 以上を利用する。
2. 標準の destination pop を行うだけの root `BackHandler` / Activity callback を削除する。
3. `NavHost` の `popEnterTransition` / `popExitTransition` で戻る遷移を定義する。
4. dialog、drawer、未保存確認など Navigation stack 以外の UI state だけを、状態連動 callback で処理する。

確認観点:
- edge swipe 中に現在 destination と戻り先の transition が gesture progress に追従する。
- gesture cancel では destination が変わらず、描画が初期状態へ戻る。
- toolbar Up は通常の pop transition、system gesture は predictive transition として、それぞれ意図した結果になる。
- root destination では broad callback が Back を消費せず、back-to-home animation が表示される。

注意点:
- `onBackPressedDispatcher.onBackPressed()` を toolbar から呼んでも system gesture progress は生成されない。
- Navigation library の built-in support で要件を満たす場合は、同じ destination pop のための `PredictiveBackHandler` を重ねて登録しない。

## 例 7: Compose で gesture progress に合わせた animation を行う

目的:
- back gesture の完了後だけ UI を切り替えるのではなく、swipe 中の `progress` に合わせて custom in-app animation を行う。

既存実装で探す箇所:
- `BackHandler` で戻る完了時だけ画面を閉じている Compose 画面。
- back gesture 中に scale / offset / alpha などを preview したい detail 画面。

移行前:

```kotlin
BackHandler(enabled = true) {
    onNavigateBack()
}
```

移行後:

```kotlin
@Composable
fun DetailScreen(onNavigateBack: () -> Unit) {
    var progress by remember { mutableFloatStateOf(0f) }

    PredictiveBackHandler(enabled = true) { progressFlow ->
        try {
            progressFlow.collect { backEvent ->
                progress = backEvent.progress
            }
            onNavigateBack()
        } catch (e: CancellationException) {
            progress = 0f
        }
    }

    DetailContent(
        modifier = Modifier
            .scale(1f - progress * 0.08f)
            .alpha(1f - progress * 0.15f),
    )
}
```

移行手順:
1. 完了時だけ実行していた `BackHandler` を `PredictiveBackHandler` に置き換える。
2. `BackEventCompat.progress` を UI state に反映する。
3. gesture completed では navigation を実行し、cancel では一時 UI state を reset する。

確認観点:
- swipe 中に progress に応じて UI が連続的に変化する。
- gesture cancel 時に scale / alpha が初期値へ戻る。
- gesture completed 時だけ navigation が実行される。

注意点:
- 単純な確認 dialog や stack pop だけなら `BackHandler` で足りる。
- `CancellationException` は gesture cancel として扱い、UI state を戻す。
- Navigation Compose の標準 destination 遷移なら、まず例 6A の built-in support を使い、画面固有の property animation が必要な場合だけ `PredictiveBackHandler` を追加する。

## 例 8: Views で gesture progress に合わせた animation を行う

目的:
- View ベースの画面で、default animation では足りない custom transition を back gesture の進捗に合わせて動かす。

既存実装で探す箇所:
- `OnBackPressedCallback.handleOnBackPressed()` で完了時だけ View animation を実行している箇所。
- `TransitionManager.beginDelayedTransition()` を back 完了後だけ呼んでいる箇所。

移行前:

```kotlin
onBackPressedDispatcher.addCallback(this, object : OnBackPressedCallback(true) {
    override fun handleOnBackPressed() {
        detailView.animate()
            .alpha(0f)
            .withEndAction { finish() }
            .start()
    }
})
```

移行後:

```kotlin
onBackPressedDispatcher.addCallback(this, object : OnBackPressedCallback(true) {
    override fun handleOnBackStarted(backEvent: BackEventCompat) {
        detailView.pivotX = 0f
    }

    override fun handleOnBackProgressed(backEvent: BackEventCompat) {
        val progress = backEvent.progress
        detailView.scaleX = 1f - progress * 0.08f
        detailView.scaleY = 1f - progress * 0.08f
        detailView.alpha = 1f - progress * 0.15f
    }

    override fun handleOnBackCancelled() {
        detailView.animate()
            .scaleX(1f)
            .scaleY(1f)
            .alpha(1f)
            .start()
    }

    override fun handleOnBackPressed() {
        finish()
    }
})
```

移行手順:
1. 完了時だけの animation を、started / progressed / cancelled / pressed に分ける。
2. `BackEventCompat.progress` で View property を更新する。
3. cancel 時は View property を初期値へ戻す。
4. pressed 時は本来の navigation / finish を実行する。

確認観点:
- swipe 中に View が progress に追従する。
- cancel 時に中途半端な scale / alpha が残らない。
- completed 時に navigation / finish が一度だけ実行される。

注意点:
- AndroidX Activity の progress callbacks が使える version を確認する。
- default system animation や Material Component animation で十分な画面には custom progress animation を追加しない。
- callback は custom animation が必要な destination / UI state の間だけ enabled にし、root の back-to-home / cross-activity animation を常時 intercept しない。

## 例 9: Navigation Event API で back gesture lifecycle を扱う

目的:
- Navigation Event API を採用する画面で、back gesture の started / progressed / completed / cancelled を明示的に分ける。

既存実装で探す箇所:
- 独自 dispatcher / multi-platform navigation layer で back event lifecycle を持っている箇所。
- Navigation 3 など built-in predictive back support の有無を確認したい箇所。

移行前:

```kotlin
fun onBack() {
    if (canNavigateBack) {
        navigateUp()
    }
}
```

移行後:

```kotlin
val handler = object : NavigationEventHandler<NavigationEventInfo>(
    initialInfo = NavigationEventInfo.None,
    isBackEnabled = true,
) {
    override fun onBackStarted(event: NavigationEvent) {
        prepareBackPreview()
    }

    override fun onBackProgressed(event: NavigationEvent) {
        updateBackPreview(event.progress)
    }

    override fun onBackCompleted() {
        navigateUp()
    }

    override fun onBackCancelled() {
        resetBackPreview()
    }
}

navigationEventDispatcher.addHandler(handler)
```

移行手順:
1. 既存の一括 back handler を gesture lifecycle ごとの method に分割する。
2. `onBackProgressed()` では UI preview だけを更新する。
3. `onBackCompleted()` で実際の navigation を行う。
4. 画面破棄時に handler を remove する。

確認観点:
- completed 時だけ navigation が実行される。
- cancel 時に preview state が残らない。
- 複数 handler がある場合、priority / LIFO 順が期待通りである。

注意点:
- すでに Navigation 3 など built-in predictive back support を使っている場合は、独自実装を追加する前に既存機能で足りるか確認する。
- handler lifecycle を画面 lifecycle と合わせ、不要になった handler は削除する。

## 例 10: 一時 opt-out を Activity に限定する

目的:
- 移行が間に合わない legacy flow だけ一時的に旧 back behavior を維持する。

既存実装で探す箇所:
- application 全体で `android:enableOnBackInvokedCallback="false"` を指定している manifest。
- `KEYCODE_BACK` / `onBackPressed()` 依存が残っており、targetSdkVersion 36 移行までに修正できない Activity。

移行前:

```xml
<application
    android:enableOnBackInvokedCallback="false" />
```

移行後:

```xml
<activity
    android:name=".LegacyPairingActivity"
    android:enableOnBackInvokedCallback="false" />
```

移行手順:
1. application-level opt-out を避け、未移行 Activity を特定する。
2. Activity-level opt-out に限定する。
3. 対象 Activity ごとに移行 issue、削除条件、検証ケースを記録する。

確認観点:
- opt-out 対象 Activity だけ legacy back behavior になる。
- 移行済み Activity では predictive back が有効なままになる。
- targetSdkVersion 36 移行後に opt-out 削除計画が追跡できる。

注意点:
- application 全体ではなく、移行できていない Activity に限定する。
- issue / TODO / migration plan に削除条件を残す。
- Android 16 / targetSdkVersion 36 の検証では、opt-out あり / なしの両方を比較する。

## 例 11: 旧 `KEYCODE_BACK` 処理の置き換え対象を見つける

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
- toolbar / custom button の programmatic Back と実際の system gesture を別ケースとして確認する。
- root destination で consuming callback が disabled になり、back-to-home animation が表示されることを確認する。
- gesture cancel では destination / business state が確定せず、completed 時だけ navigation が1回実行されることを確認する。

## テストコード例（Test Code Examples）

目的:
- `OnBackPressedDispatcher` 移行後の callback 順、enabled 制御、fallback 委譲を unit test で確認する。
- 実機の predictive back animation 自体は instrumentation / manual test で確認し、callback の business logic は JVM / Robolectric test で分離して検証する。

### callback は後から登録した enabled callback が先に呼ばれる

```java
@Test
public void dispatcherCallsLastEnabledCallbackFirst() {
    List<String> events = new ArrayList<>();
    OnBackPressedDispatcher dispatcher =
            new OnBackPressedDispatcher(() -> events.add("fallback"));

    OnBackPressedCallback activityCallback = new OnBackPressedCallback(true) {
        @Override
        public void handleOnBackPressed() {
            events.add("activity");
        }
    };

    OnBackPressedCallback fragmentCallback = new OnBackPressedCallback(true) {
        @Override
        public void handleOnBackPressed() {
            events.add("fragment");
        }
    };

    dispatcher.addCallback(activityCallback);
    dispatcher.addCallback(fragmentCallback);

    dispatcher.onBackPressed();

    assertEquals(Collections.singletonList("fragment"), events);

    fragmentCallback.setEnabled(false);
    dispatcher.onBackPressed();

    assertEquals(Arrays.asList("fragment", "activity"), events);
}
```

確認できること:
- 後から登録された `fragmentCallback` が先に呼ばれる。
- `fragmentCallback.setEnabled(false)` 後は `activityCallback` に処理が進む。

### callback 内で fallback する場合は自分を一時的に disabled にする

```java
@Test
public void callbackCanDelegateToFallbackWithoutRecursion() {
    List<String> events = new ArrayList<>();
    OnBackPressedDispatcher dispatcher =
            new OnBackPressedDispatcher(() -> events.add("fallback"));

    OnBackPressedCallback callback = new OnBackPressedCallback(true) {
        @Override
        public void handleOnBackPressed() {
            events.add("callback");

            setEnabled(false);
            try {
                dispatcher.onBackPressed();
            } finally {
                setEnabled(true);
            }
        }
    };

    dispatcher.addCallback(callback);

    dispatcher.onBackPressed();

    assertEquals(Arrays.asList("callback", "fallback"), events);
    assertTrue(callback.isEnabled());
}
```

確認できること:
- callback が dispatcher に委譲しても、同じ callback が再帰的に呼ばれない。
- fallback 後に callback が enabled に戻る。

### UI state に応じて enabled を事前管理する

```java
@Test
public void selectionModeCallbackOnlyRunsWhenEnabled() {
    List<String> events = new ArrayList<>();
    OnBackPressedDispatcher dispatcher =
            new OnBackPressedDispatcher(() -> events.add("fallback"));

    OnBackPressedCallback selectionCallback = new OnBackPressedCallback(false) {
        @Override
        public void handleOnBackPressed() {
            events.add("exit-selection");
            setEnabled(false);
        }
    };

    dispatcher.addCallback(selectionCallback);

    dispatcher.onBackPressed();
    assertEquals(Collections.singletonList("fallback"), events);

    selectionCallback.setEnabled(true);
    dispatcher.onBackPressed();
    assertEquals(Arrays.asList("fallback", "exit-selection"), events);

    dispatcher.onBackPressed();
    assertEquals(Arrays.asList("fallback", "exit-selection", "fallback"), events);
}
```

確認できること:
- selection mode でない時は callback が呼ばれず fallback に進む。
- selection mode 中だけ callback が戻る操作を消費する。
- callback が処理後に自分を disabled に戻すと、次回 back は fallback に進む。

### UI test / instrumentation で確認すること

- `ActivityScenario` / `FragmentScenario` で対象画面を起動し、`activity.getOnBackPressedDispatcher().onBackPressed()` を呼んで UI state が変わることを確認する。
- Navigation Component を使う画面では、`TestNavHostController` などで current destination が期待通り変わることを確認する。
- predictive back gesture の progress animation、3-button navigation long press、gesture cancel は emulator / device 上の instrumentation または manual test で確認する。
- `android:enableOnBackInvokedCallback="false"` の一時 opt-out は、対象 Activity と移行済み Activity の両方を起動して差分を確認する。

## References

- https://developer.android.com/about/versions/16/behavior-changes-16#predictive-back
- https://developer.android.com/guide/navigation/custom-back/predictive-back-gesture
- https://developer.android.com/guide/navigation/custom-back/support-animations
- https://developer.android.com/guide/navigation/custom-back/support-animations-views
- https://developer.android.com/guide/navigation/navigation-event/handle-back
- https://developer.android.com/reference/android/window/OnBackInvokedCallback
- https://developer.android.com/guide/topics/manifest/activity-element#enableOnBackInvokedCallback
