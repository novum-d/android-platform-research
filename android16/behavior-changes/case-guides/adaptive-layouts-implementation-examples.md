# Adaptive layouts - 実装例（Implementation Examples）

## 位置づけ（Scope）

このファイルは、Android 16 の Adaptive layouts に関する調査レポートの対応候補を、Compose と Jetpack Navigation 3 を使うアプリ向けに具体化する実装例である。
根拠、適用条件、classification、confidence、Human Decision は主レポートと1ページ要約を正とする。

主レポート:
- [adaptive-layouts.md](../target/device-form-factors/adaptive-layouts.md)

1ページ要約:
- [adaptive-layouts-summary.md](../../summaries/target/device-form-factors/adaptive-layouts-summary.md)

Manifest / API の挙動:
- [adaptive-layouts-manifest-api-behavior-guide.md](adaptive-layouts-manifest-api-behavior-guide.md)

## 対象（Target）

Android 16 Behavior Change:
- 文書: https://developer.android.com/about/versions/16/behavior-changes-16#adaptive-layouts
- セクション: Adaptive layouts

適用条件の要点:
- OS アップデート / 全アプリ: いいえ。Android 16 へ OS アップデートしただけの targetSdkVersion 35 以下アプリには既定適用されない。
- targetSdkVersion 36 以上: はい。
- その他の必須条件: Android 16 以上、対象 display の `smallestScreenWidthDp >= 600`、game ではない、temporary opt-out なし、user aspect ratio setting exception なし。
- 主分類: `TARGET_SDK_36_CONDITIONAL`。

重要:
- platform の適用 gate は、対象 display の smallest width を使う。
- アプリの layout は、現在利用できる app window の bounds に応じて切り替える。
- tablet の split screen で app window 幅が 600dp 未満になっても、display が `sw >= 600dp` なら platform gate は成立し得る。UI の breakpoint に display の `smallestScreenWidthDp` を流用しない。

## 前提と使い方（Prerequisites / How to Use）

- 対象画面は Compose で実装し、navigation は Jetpack Navigation 3 を使う。
- View / Fragment または Navigation 2 の画面は、先に Compose / Navigation 3 へ段階的に移行する。移行期間中も fixed orientation や non-resizable 指定を恒久的な防御にしない。
- 掲載コードは、そのまま貼り付けて使う完成品ではない。対象アプリの dependency versions、architecture、state management、navigation、dependency injection、error policy、lifecycle、threading、test strategy に合わせて調整する。
- artifact version は固定値を発明せず、採用中の Compose BOM、version catalog、Navigation 3 と Material 3 Adaptive の互換性を確認する。
- `Grid`、`FlexBox`、`MediaQuery` など Compose 1.11 の experimental API は、採用判断が別途必要なため、この実装例の必須経路にはしない。
- 実アプリ project は今回の入力に含まれていない。以下の Gradle build、instrumented test、screenshot test の結果はすべて未実施である。

## 対応方針（Implementation Strategy）

推奨方針:
- orientation や aspect ratio から layout を推測せず、現在の app window に応じて navigation、pane 数、column 数、content scaling を組み替える。
- top-level navigation は `NavigationSuiteScaffold` で navigation bar / rail を切り替える。
- list-detail は Navigation 3 の `ListDetailSceneStrategy` を使い、compact window では1 pane、広い window では複数 pane とする。
- 繰り返し表示する項目は `LazyVerticalGrid` と `GridCells.Adaptive` で現在の app window 幅へ追従させる。
- 選択 ID、入力値、scroll position など復元に必要な最小状態を保存し、大きな domain object は repository から再取得する。
- camera / media / preview は、container の bounds と content の aspect ratio を分離し、Fit / Crop を画面要件として明示する。

一時対応:
- Android 16 の未移行 Activity に限り、Activity-level の `PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY` を検討できる。記述方法、適用範囲、削除条件は [Manifest / API 挙動ガイド](adaptive-layouts-manifest-api-behavior-guide.md#temporary-opt-out-の記述例) を参照する。
- opt-out は API 37 target では適用されない予定であり、恒久対応として扱わない。

避けるべき方針:
- `screenOrientation`、`setRequestedOrientation()`、`resizeableActivity=false`、`minAspectRatio`、`maxAspectRatio`、pillarbox だけで UI 崩れを防ぐ。
- `Configuration.orientation` または requested orientation だけで phone / tablet、1 pane / 2 pane を決める。
- tablet なら常に expanded とみなし、split screen、freeform window、foldable の外画面を無視する。
- Activity recreation を `configChanges` で広く回避し、state restoration の不足を隠す。

## 依存関係（Dependencies）

次の alias 名は説明用である。実際の version catalog 名と互換 version に合わせて置き換える。

```kotlin
dependencies {
    implementation(libs.androidx.material3.adaptive.navigation.suite)
    implementation(libs.androidx.material3.adaptive.navigation3)
    implementation(libs.androidx.navigation3.runtime)
    implementation(libs.androidx.navigation3.ui)

    screenshotTestImplementation(libs.screenshot.validation.api)
    screenshotTestImplementation(libs.androidx.compose.ui.tooling)
}
```

対応する artifact:
- `androidx.compose.material3:material3-adaptive-navigation-suite`
- `androidx.compose.material3.adaptive:adaptive-navigation3`
- `androidx.navigation3:navigation3-runtime`
- `androidx.navigation3:navigation3-ui`
- `com.android.tools.screenshot:screenshot-validation-api`

導入前に release notes と compatibility を確認し、既存 Compose / Kotlin / AGP の更新が必要なら Adaptive layouts 対応とは別の変更単位に分ける。
Screenshot test には `com.android.compose.screenshot` plugin と `android.experimental.enableScreenshotTest=true` の設定も必要である。現在の要件は公式 setup を確認する。

## 移行対象の見つけ方（Finding Existing Code）

Manifest:

```bash
rg -n 'screenOrientation|resizeableActivity|minAspectRatio|maxAspectRatio|PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY' \
  --glob 'AndroidManifest.xml' --glob '*.xml'
```

Kotlin / Java:

```bash
rg -n 'setRequestedOrientation|getRequestedOrientation|requestedOrientation|Configuration\.ORIENTATION_' \
  --glob '*.kt' --glob '*.java'
```

Compose / navigation / 固定寸法:

```bash
rg -n 'BottomAppBar|NavigationBar|navigation-compose|NavHost|LazyColumn|LazyVerticalGrid|width\([0-9]+\.dp\)|height\([0-9]+\.dp\)|aspectRatio\(' \
  --glob '*.kt'
```

XML / legacy navigation:

```bash
rg -n 'BottomNavigationView|NavHostFragment|navigation/|layout-land|layout-sw[0-9]+dp|android:layout_width="[0-9]+dp"' \
  --glob '*.xml'
```

検索結果は機械的に削除せず、次のように分類する。

| 既存実装（Existing pattern） | 移行先（Migration target） | 優先度 | Notes |
| --- | --- | --- | --- |
| fixed orientation で portrait UI を保護 | current app window に追従する Compose layout | Must | Android 16 / target 36 / large screen では制約に依存できない |
| bottom navigation を常時表示 | `NavigationSuiteScaffold` | Recommended | compact は bar、広い window は rail |
| list から detail へ常に全画面遷移 | Navigation 3 `ListDetailSceneStrategy` | Recommended | window 幅に応じて1 pane / 複数 pane |
| `LazyColumn` に固定幅 card | `LazyVerticalGrid(GridCells.Adaptive(...))` | Recommended | split screen と freeform resize に追従 |
| requested orientation / portrait-landscape branch | SceneStrategy、adaptive component、現在の bounds | Must | 要求値と実際の window を分ける |
| `remember` だけで選択・入力を保持 | `rememberSaveable` / `SavedStateHandle` | Must | recreation と process recreation を考慮 |
| fixed aspect ratio container に UI 全体を押し込む | resizable container + content-level Fit / Crop | Must | 操作 UI まで crop しない |
| application-level temporary opt-out | Activity-level opt-out、最終的には削除 | Conditional | scope と期限を小さくする |

## 移行マップ（Migration Map）

| Before | After | 目的 |
| --- | --- | --- |
| orientation lock による portrait-only UI | current window に適応する navigation / pane / grid | 制約が無視されても操作可能にする |
| phone 用 bottom navigation 固定 | navigation bar / rail の自動切り替え | 大画面で edge から到達しやすくする |
| list と detail の手動幅分岐 | Navigation 3 SceneStrategy metadata | navigation state と adaptive pane 構成を一致させる |
| 全 item を1列表示 | `GridCells.Adaptive(minSize)` | 横長 window の余白と可読性を改善する |
| 画面全体を16:9固定 | content だけ Fit / Crop | arbitrary aspect ratio でも操作 UI を保持する |
| `remember` に transient state を保存 | `rememberSaveable` / `SavedStateHandle` に最小キーを保存 | rotation / resize / recreation 後に復元する |
| opt-out で従来表示を固定 | adaptive layout 完了後に property を削除 | API 37 target に備える |

## 例 1: Top-level navigation を adaptive にする

目的:
- phone portrait で使っていた bottom navigation を、広い app window では navigation rail へ切り替える。
- 回転方向や端末種別ではなく、現在の app window と posture に応じて navigation component を選ぶ。

既存実装で探す箇所:
- `Scaffold(bottomBar = ...)`、`NavigationBar`、`BottomAppBar`。
- destination ごとに別々に管理された selected state。

移行前:

```kotlin
@Composable
fun AppShell(content: @Composable (PaddingValues) -> Unit) {
    Scaffold(
        bottomBar = { PhoneBottomNavigation() },
        content = content,
    )
}
```

移行後:

```kotlin
@Composable
fun AdaptiveAppShell(
    destinations: List<AppDestination>,
    selected: AppDestination,
    onSelect: (AppDestination) -> Unit,
    content: @Composable () -> Unit,
) {
    NavigationSuiteScaffold(
        navigationSuiteItems = {
            destinations.forEach { destination ->
                item(
                    selected = destination == selected,
                    onClick = { onSelect(destination) },
                    icon = {
                        Icon(
                            imageVector = destination.icon,
                            contentDescription = destination.label,
                        )
                    },
                    label = { Text(destination.label) },
                )
            }
        },
        content = content,
    )
}
```

移行手順:
1. top-level destination と selected destination を単一の navigation state へ寄せる。
2. 既存 navigation item を `NavigationSuiteScaffold` の item へ移す。
3. phone portrait、phone landscape、tablet 全画面、split screen、desktop freeform で bar / rail と content inset を確認する。

既存 architecture への調整点:
- selected destination を Composable ローカル state と back stack の二重管理にしない。Navigation 3 の back stack を source of truth とする。
- analytics は component 種別ではなく destination 遷移を記録し、bar から rail へ変わっても重複送信しない。
- destination scope の ViewModel / DI scope が navigation UI の再構成だけで作り直されないことを確認する。

確認観点:
- compact window では content が bottom navigation に隠れない。
- 広い window では rail が表示され、主要 action が画面 edge から到達できる。
- resize 中に selected destination、back stack、scroll state が変わらない。

注意点:
- detail を phone で全画面表示するため navigation area を隠している場合、list-detail の複数 pane 表示時は navigation area を再表示する。
- IME / system bar inset は別途 edge-to-edge 方針と合わせて確認する。

## 例 2: Navigation 3 SceneStrategy で list-detail にする

目的:
- compact window では list または detail を1 paneで表示し、広い window では list と detail を並べる。
- `ListDetailPaneScaffold` を画面側で直接切り替えず、Navigation 3 の SceneStrategy と back stack を一体で扱う。

既存実装で探す箇所:
- list item click で常に detail Activity / destination へ全画面遷移する処理。
- `isTablet`、`orientation == landscape`、固定 dp を使う2 pane branch。
- detail pane の選択 ID と navigation argument の二重管理。

移行前:

```kotlin
NavHost(navController, startDestination = "items") {
    composable("items") {
        ItemList(onSelect = { id -> navController.navigate("items/$id") })
    }
    composable("items/{id}") { entry ->
        ItemDetail(id = entry.arguments?.getString("id"))
    }
}
```

移行後:

```kotlin
@Serializable
data object ItemListKey : NavKey

@Serializable
data class ItemDetailKey(val id: String) : NavKey

@OptIn(ExperimentalMaterial3AdaptiveApi::class)
@Composable
fun AdaptiveItems() {
    val backStack = rememberNavBackStack(ItemListKey)
    val windowAdaptiveInfo = currentWindowAdaptiveInfoV2()
    val directive = remember(windowAdaptiveInfo) {
        calculatePaneScaffoldDirective(windowAdaptiveInfo)
    }
    val listDetailStrategy =
        rememberListDetailSceneStrategy<NavKey>(directive = directive)

    NavDisplay(
        backStack = backStack,
        onBack = { backStack.removeLastOrNull() },
        sceneStrategies = listOf(listDetailStrategy),
        entryProvider = entryProvider {
            entry<ItemListKey>(
                metadata = ListDetailSceneStrategy.listPane(
                    detailPlaceholder = {
                        EmptyDetail(message = "項目を選択してください")
                    },
                ),
            ) {
                ItemList(
                    onSelect = { id ->
                        backStack.add(ItemDetailKey(id))
                    },
                )
            }

            entry<ItemDetailKey>(
                metadata = ListDetailSceneStrategy.detailPane(),
            ) { key ->
                ItemDetail(id = key.id)
            }
        },
    )
}
```

移行手順:
1. list / detail の destination key を `NavKey` として定義し、保存可能な item ID だけを argument にする。
2. `rememberListDetailSceneStrategy` を `NavDisplay.sceneStrategies` へ渡す。
3. list entry に `listPane()`、detail entry に `detailPane()` metadata を付ける。
4. compact / expanded の双方で同じ back stack 操作から正しい pane 構成になることを確認する。
5. detail が複数 pane に入った時は phone 専用 full-screen、navigation 非表示、常時 back arrow を解除する。

既存 architecture への調整点:
- domain object 全体を key に詰めず ID を保存し、detail のデータは repository / ViewModel から再取得する。
- item selection と back stack を別々の mutable state として更新しない。deep link、process recreation、戻る操作で競合しない source of truth を決める。
- data load の cancel / retry / error policy は pane 数に依存させず、同じ detail destination の状態として扱う。
- lifecycle が `RESUMED` の間だけ navigation event を受理する必要がある場合は、採用中の Navigation 3 recipe に合わせて event を guard する。

確認観点:
- compact window: list から detail へ遷移し、Back で list へ戻る。
- expanded window: list と選択済み detail を同時表示し、選択変更で detail だけが更新される。
- resize: detail 選択を維持したまま1 pane / 複数 pane が切り替わる。
- placeholder: 未選択時に空白ではなく次の操作を説明する。
- accessibility: pane 切り替え後の focus と TalkBack の読み上げ順を確認する。

注意点:
- `ListDetailPaneScaffold` / `NavigableListDetailPaneScaffold` へ独自 navigation state を重ねず、この例では `ListDetailSceneStrategy` を使う。
- `currentWindowAdaptiveInfoV2()` などの API 名と opt-in 要否は採用 version の API reference で確認する。

## 例 3: 繰り返し項目を現在の window 幅へ追従させる

目的:
- portrait phone 用の1列 list を、利用可能な幅に応じて複数列へする。
- `sw600dp` や device type を分岐に使わず、container の実幅へ追従する。

既存実装で探す箇所:
- `LazyColumn` に固定幅 card を並べる画面。
- `isTablet` で列数を2へ固定する分岐。
- `Modifier.width(320.dp)` など、狭い split screen でははみ出す寸法。

移行前:

```kotlin
LazyColumn {
    items(items, key = Item::id) { item ->
        ItemCard(
            item = item,
            modifier = Modifier.width(320.dp),
        )
    }
}
```

移行後:

```kotlin
@Composable
fun AdaptiveItemGrid(
    items: List<Item>,
    onSelect: (String) -> Unit,
    state: LazyGridState = rememberLazyGridState(),
) {
    LazyVerticalGrid(
        columns = GridCells.Adaptive(minSize = 280.dp),
        state = state,
        contentPadding = PaddingValues(16.dp),
        horizontalArrangement = Arrangement.spacedBy(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
    ) {
        items(items, key = Item::id) { item ->
            ItemCard(
                item = item,
                onClick = { onSelect(item.id) },
                modifier = Modifier.fillMaxWidth(),
            )
        }
    }
}
```

移行手順:
1. card が情報と操作を欠かさず表示できる最小幅を design / accessibility 観点で決める。
2. `LazyColumn` を `LazyVerticalGrid` へ置き換え、`GridCells.Adaptive` に最小幅を渡す。
3. content padding と column 間隔を含め、最狭 / 最広 bounds で過密・過疎にならないか確認する。

既存 architecture への調整点:
- item key を安定 ID にし、column 数変更で item state を別 item へ誤適用しない。
- paging / incremental loading は visible row 数ではなく item index / load state を source of truth とする。
- card 内の image load、retry、click event は recomposition と column 数変更に対して idempotent にする。

確認観点:
- phone portrait と狭い split screen で1列を維持し、横 overflow がない。
- tablet / desktop window で利用可能な幅に応じて列数が増える。
- resize 中に item selection と scroll position が失われない。
- font scale 200% でも action と本文が card 外へ切れない。

注意点:
- `280.dp` は例であり、対象 card の content と touch target を測って決める。
- item 数が少ない固定 layout へ experimental `Grid` を採用する場合は、Compose 1.11 experimental API の採用判断を別途行う。

## 例 4: Media の aspect ratio と操作 UI を分離する

目的:
- app window 全体を固定 aspect ratio にせず、media content だけに Fit / Crop policy を適用する。
- 横長 tablet、縦長 window、split screen でも controls を画面外へ押し出さない。

既存実装で探す箇所:
- Activity 全体の landscape lock。
- root container の固定 `aspectRatio(16f / 9f)`。
- preview と controls を同じ crop 対象にする実装。

移行前:

```kotlin
requestedOrientation = ActivityInfo.SCREEN_ORIENTATION_LANDSCAPE

Box(modifier = Modifier.aspectRatio(16f / 9f)) {
    CameraPreviewAndControls()
}
```

移行後:

```kotlin
enum class MediaScalePolicy { Fit, Crop }

@Composable
fun AdaptiveMediaScreen(
    painter: Painter,
    scalePolicy: MediaScalePolicy,
    controls: @Composable RowScope.() -> Unit,
) {
    Column(modifier = Modifier.fillMaxSize()) {
        Box(
            modifier = Modifier
                .weight(1f)
                .fillMaxWidth()
                .background(Color.Black),
            contentAlignment = Alignment.Center,
        ) {
            Image(
                painter = painter,
                contentDescription = null,
                contentScale = when (scalePolicy) {
                    MediaScalePolicy.Fit -> ContentScale.Fit
                    MediaScalePolicy.Crop -> ContentScale.Crop
                },
                modifier = Modifier.fillMaxSize(),
            )
        }

        Row(
            modifier = Modifier
                .fillMaxWidth()
                .windowInsetsPadding(WindowInsets.safeDrawing)
                .padding(16.dp),
            horizontalArrangement = Arrangement.spacedBy(12.dp),
            content = controls,
        )
    }
}
```

移行手順:
1. content の natural aspect ratio と app window / controls の layout を別 component に分ける。
2. Fit / Crop を feature requirement として定義し、重要領域が crop される場合の切り替えを用意する。
3. orientation request を UI layout の制御に使っている call site を削除し、全 orientation / window bounds で controls を再配置する。

既存 architecture への調整点:
- CameraX / media player の lifecycle bind / unbind を単なる size change で繰り返さない。
- surface / player / session は screen state holder で維持し、Composable は bounds と scaling を表現する。
- Crop の初期値、ユーザー設定、重要領域 metadata は domain / product 要件に合わせる。

確認観点:
- Fit では content 全体が見え、余白が明示した背景色になる。
- Crop では重要領域が失われず、controls は crop されない。
- rotation / resize 中に playback position、camera session、入力状態を不必要に初期化しない。
- pointer / keyboard / TalkBack でも controls に到達できる。

注意点:
- camera preview の実装では、利用している `PreviewView` / Compose camera component の scale type へ同じ Fit / Crop policy を対応付ける。
- media content の比率を守ることと Activity の aspect ratio を制限することは別である。

## 例 5: Rotation / resize / recreation で状態を復元する

目的:
- fixed orientation が無視されて Activity recreation が増えても、選択項目、入力値、scroll positionを失わない。
- Bundle に大きな domain object を保存せず、復元に必要な最小キーだけを保存する。

既存実装で探す箇所:
- `remember` だけで保持する text / selection / expanded state。
- Activity / Fragment field に保存した選択 item。
- `configChanges` で recreation を避けることだけに依存する画面。

移行前:

```kotlin
@Composable
fun ItemDetail() {
    var draft by remember { mutableStateOf("") }
    var selectedId by remember { mutableStateOf<String?>(null) }
    // rotation / recreation で初期値へ戻る。
}
```

移行後:

```kotlin
private const val SelectedItemKey = "selected_item_id"

class ItemsViewModel(
    private val savedStateHandle: SavedStateHandle,
    private val repository: ItemRepository,
) : ViewModel() {
    val selectedId: StateFlow<String?> =
        savedStateHandle.getStateFlow(SelectedItemKey, null)

    fun select(id: String) {
        savedStateHandle[SelectedItemKey] = id
    }

    fun item(id: String): Flow<Item> = repository.observe(id)
}

@Composable
fun ItemEditor(
    items: List<Item>,
    selectedId: String?,
    onSelect: (String) -> Unit,
) {
    var draft by rememberSaveable(selectedId) { mutableStateOf("") }
    val gridState = rememberLazyGridState()

    AdaptiveItemGrid(
        items = items,
        onSelect = onSelect,
        state = gridState,
    )

    OutlinedTextField(
        value = draft,
        onValueChange = { draft = it },
        label = { Text("メモ") },
    )
}
```

移行手順:
1. state を UI element state、screen/business state、永続 domain data に分類する。
2. text、expanded、scroll など UI element state は `rememberSaveable` または保存可能な state holder へ移す。
3. business logic が使う selected ID は `SavedStateHandle` に保存し、詳細データは repository から再生成する。
4. rotation、resize、background 後の recreation、可能なら system-initiated process death を検証する。

既存 architecture への調整点:
- ViewModel は configuration change 回避のためだけでなく、screen state と business logic の owner として使う。
- `SavedStateHandle` / `rememberSaveable` には ID や入力値など小さな値だけを保存する。画像、item list、large payload は保存しない。
- navigation key に selected ID がある場合、ViewModel の selected ID と二重 source of truth にしない。
- repository の再取得失敗時は loading / retry / offline policy を定義し、空 detail と誤認させない。

確認観点:
- selected ID、入力中 text、scroll position が rotation / resize 後も維持される。
- detail object は復元した ID から再取得され、古い object snapshot を表示しない。
- process recreation 後も deep link / back stack と selected ID が矛盾しない。

注意点:
- `rememberSaveable(selectedId)` は selected item が変わると draft を初期化する例である。編集中 draft を item ごとに保持すべき場合は保存 key と永続化方針を設計する。
- state restoration と ongoing operation の再実行は別問題である。upload / purchase / remote command を recreation ごとに再送しない。

## 例 6: Form factor 別の screenshot test を追加する

目的:
- phone、foldable、tablet、desktop の preview を同じ UI 仕様で比較し、stretched layout、off-screen component、固定幅、状態別 regression を検出する。
- reference image の更新を review なしで自動承認しない。

既存実装で探す箇所:
- phone 1種類だけの `@Preview`。
- UI test はあるが visual regression test がない画面。
- screenshot 差分を生成せず reference image を常に更新する CI script。

移行前:

```kotlin
@Preview
@Composable
fun ItemsPreview() {
    AppTheme { ItemsScreen(FakeItems.sample) }
}
```

移行後:

```kotlin
@Preview(name = "Phone", device = Devices.PHONE, showBackground = true)
@Preview(name = "Foldable", device = Devices.FOLDABLE, showBackground = true)
@Preview(name = "Tablet", device = Devices.TABLET, showBackground = true)
@Preview(name = "Desktop", device = Devices.DESKTOP, showBackground = true)
annotation class FormFactorPreviews

@PreviewTest
@FormFactorPreviews
@Composable
fun ItemsScreenshotTest() {
    AppTheme {
        ItemsScreen(
            state = ItemsUiState(
                items = FakeItems.sample,
                selectedId = FakeItems.sample.first().id,
            ),
        )
    }
}
```

配置先の例:

```text
app/src/screenshotTest/kotlin/com/example/items/ItemsScreenshotTest.kt
```

移行手順:
1. Compose Preview Screenshot Testing を project に設定し、`screenshotTest` source set を追加する。
2. form factor ごとの multi-preview と、empty / loading / error / selected / IME-visible 相当の状態を用意する。
3. 既存 reference image を人間が確認して承認する。
4. 通常検証では `validateDebugScreenshotTest` など対象 variant の validate task を実行し、reference image を更新しない。

既存 architecture への調整点:
- network、clock、random、image loader は preview 用 fake / deterministic dependency に置き換える。
- ViewModel を preview 内で生成せず、immutable UI state と event lambda を渡せる screen API にする。
- animation clock、locale、font scale、dark theme の検証範囲を project の test strategy に合わせる。

確認観点:
- compact で navigation bar、広い window で rail / multi-pane になる。
- text、button、dialog、animation target が bounds 外へ出ない。
- detail placeholder、selected detail、error UI が各 form factor で成立する。
- golden 更新差分を reviewer が確認できる。

注意点:
- Compose Preview Screenshot Testing は experimental である。採用 version の setup と制約を確認する。
- 今回は実アプリ project がないため、reference image の生成・更新・検証は未実施である。

## テスト観点（Verification）

### Behavior Change と実装差分の最小マトリクス

| Case | OS | targetSdkVersion | Compat change | Opt-out | Implementation | Expected | Observed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A | Android 16 | 35 | default | なし | 移行前 | 本 Behavior Change は既定適用されない。従来制約側の baseline を記録 | 未実施 |
| B | Android 16 | 35 | enable | なし | 移行前 | target 更新前に制約無視時の UI regression を再現 | 未実施 |
| C | Android 16 | 36 | default | なし | 移行前 | 条件成立時に制約が最終的な制約として採用されず、崩れを検出し得る | 未実施 |
| D | Android 16 | 36 | default | なし | 対応後 | app window 幅に応じて navigation、pane、grid、media が再構成され、state を維持 | 未実施 |
| E | Android 16 | 36 | disable | なし | 同一 build | 旧挙動側と比較し、Behavior Change 起因の差を分離 | 未実施 |
| F | Android 16 | 36 | default | Activity | 移行前 | 対象 Activity だけ一時的に従来挙動側へ戻る | 未実施 |

前提:
- Case B / E の compat change 操作は debuggable build を使用し、切り替え後は同じ entry point と初期状態から開始する。
- `UNIVERSAL_RESIZABLE_BY_DEFAULT` の adb 操作は [Manifest / API 挙動ガイド](adaptive-layouts-manifest-api-behavior-guide.md#compat-change-による比較) を参照する。
- 各 Case で端末、OS build、display `smallestScreenWidthDp`、app window bounds、orientation、windowing mode、targetSdkVersion、compat state、opt-out scope を記録する。

### UI / lifecycle matrix

| 観点 | Phone / compact | Tablet full-screen | Tablet split screen | Desktop / freeform | Observed |
| --- | --- | --- | --- | --- | --- |
| Navigation | bar | rail | bounds に応じ bar / rail | rail | 未実施 |
| List-detail | 1 pane | list + detail | bounds に応じ1 / 複数 pane | list + detail | 未実施 |
| Grid | 最小列数 | adaptive columns | resize に追従 | resize に追従 | 未実施 |
| Media | Fit / Crop policy | controls を別領域に保持 | controls が off-screen にならない | arbitrary aspect ratio | 未実施 |
| State | rotation 後に復元 | rotation 後に復元 | divider / resize 後に復元 | repeated resize 後に復元 | 未実施 |
| Input | touch / IME | touch / hardware keyboard | touch / IME | mouse / keyboard / focus | 未実施 |

### 実行 command の候補

project 固有 task 名へ調整する。

```bash
./gradlew test
./gradlew connectedCheck
./gradlew :app:validateDebugScreenshotTest
```

reference image の更新 task は visual diff を確認した後だけ実行し、通常の検証 command と分ける。

## 実装完了の判定候補

- orientation / resizability / aspect ratio 制約を無効化した条件でも主要 user flow が完了する。
- app window の resize 中に navigation state、selected item、入力値、scroll position が失われない。
- compact / medium / expanded 相当の bounds で navigation と pane 構成が成立する。
- camera / media content の Fit / Crop policy と controls の配置が分離されている。
- screenshot 差分、accessibility、keyboard / pointer、IME、edge-to-edge inset を確認している。
- temporary opt-out を使う場合、対象 Activity、理由、owner、削除条件、API 37 target 前の期限が人間の判断として別途記録されている。

最終優先度、severity、release readiness、customer communication priority は repository owner が判断する。

## References

Entry point:
- https://developer.android.com/about/versions/16/behavior-changes-16#adaptive-layouts

Official implementation guidance:
- https://developer.android.com/develop/adaptive-apps/guides/get-started-with-adaptive-apps
- https://developer.android.com/develop/adaptive-apps/guides/build-adaptive-navigation
- https://developer.android.com/guide/navigation/navigation-3/recipes/material-listdetail
- https://developer.android.com/develop/ui/compose/state-saving
- https://developer.android.com/studio/preview/compose-screenshot-testing
- https://developer.android.com/training/testing/ui-tests/screenshot

Repository evidence and verification guides:
- [主レポート](../target/device-form-factors/adaptive-layouts.md)
- [1ページ要約](../../summaries/target/device-form-factors/adaptive-layouts-summary.md)
- [Manifest / API 挙動ガイド](adaptive-layouts-manifest-api-behavior-guide.md)
- [Pixel Tablet 回転・window resize 検証プロンプト](../../../.codex/prompts/verify-app-rotation-on-pixel-tablet.md)
