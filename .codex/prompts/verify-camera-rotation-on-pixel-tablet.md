# Pixel Tablet 実機でカメラ画面の回転影響と証跡を収集する

対象カメラアプリについて、Android 16 の Adaptive layouts による画面回転・window resize 影響を Pixel Tablet 実機で確認し、再確認可能な証跡一式を作成してください。

## Inputs

- Camera project: `<camera-project-path>`
- Package name: `<package-name>`
- targetSdkVersion 35 build command or APK: `<target35-build-command-or-apk>`
- targetSdkVersion 36 build command or APK: `<target36-build-command-or-apk>`
- Known affected screens and entry steps: `<screen-list-and-entry-steps>`
- Evidence output root: `<evidence-output-root>`
- Split-screen companion app: `<companion-package-or-system-app>`

`<...>` が未入力でも project、Gradle設定、manifest、既存test、接続端末から安全に補完できる項目は補完してください。package、build variant、画面到達手順、出力先が一意に決まらない場合だけ確認してください。

## Fixed test conditions

- Device: 物理実機の Google Pixel Tablet。emulatorで代替しない。
- Device OS: Android 16 / API level 36。
- App builds: targetSdkVersion 35 と targetSdkVersion 36。
- target 35 / 36 buildは、可能な限り同じsource commit・同じfeature設定から作成し、targetSdkVersion以外の差を記録する。
- Primary window modes: full-screen、split-screen multi-window。
- Primary orientation states: Pixel Tabletで観測したportrait相当、landscape相当。rotation番号だけで方向を決めつけない。
- Primary lenses: back / front。アプリが片方だけを提供する場合は理由を記録する。
- Primary hardware state: undocked、screen unlocked。dock状態を記録し、docked / Hub Modeを別ケースに含める場合は明示する。

## Scope and authority

- 対象projectのsource、manifest、build設定、既存test、既存logを読み取ってよい。
- build、install、app起動、ADBによる端末状態の読取・一時設定、screenshot、UI hierarchy、logcat、dumpsysの取得を実施してよい。
- 既存証跡だけでは画面到達または分岐実行を確認できない場合、debug / test build限定の最小ログを追加してよい。production / release behavior、analytics、永続設定は変更しない。
- debug / testログ追加前後のdiffを記録し、機密情報、camera frame、ユーザー入力、位置情報、識別子をログへ出さない。
- app dataの消去、端末初期化、production署名、release配布、commit、pushは行わない。
- unrelatedな既存変更を修正しない。dirty worktreeの場合は変更を保護し、競合する場合だけ停止する。
- logcat全体のclearは他の調査ログを失うため既定では行わない。run ID、取得開始時刻、tag、PIDを使って対象区間を分離する。

## Required reading

最初に以下を読んで、Expectedを確定してください。

- `android16/behavior-changes/case-guides/adaptive-layouts-manifest-api-behavior-guide.md`
- `android16/behavior-changes/target/device-form-factors/adaptive-layouts.md`
- `android16/behavior-changes/target/device-form-factors/implementation-details-adaptive-layouts.md`
- https://developer.android.com/develop/adaptive-apps/guides/app-orientation-aspect-ratio-resizability
- https://developer.android.com/guide/app-compatibility/test-debug
- https://developer.android.com/develop/ui/views/layout/support-multi-window-mode
- https://developer.android.com/tools/adb

ExpectedとObservedを分離し、実行していないケースをPassにしないでください。

## Phase 1: Preflight

すべてのADBコマンドで明示的に`-s <serial>`を指定してください。複数端末が接続されている場合に暗黙選択しないでください。

1. `adb devices -l`で接続を確認する。
2. model、product、Android release、SDK、build fingerprint、security patchを取得する。
3. model / productがPixel Tabletを示し、SDKが36であることを確認する。満たさない場合は実機検証を開始しない。
4. `adb shell wm help`を保存し、このbuildで利用可能なrotation / window commandを確認する。command名を推測しない。
5. physical size、override size、density、display情報、`smallestScreenWidthDp`、navigation mode、font scale、locale、dark mode、dock状態、現在のuser rotation設定を保存する。
6. target 35 / 36 APKについて、source commit、variant、versionName、versionCode、targetSdkVersion、APK SHA-256を保存する。
7. feature flags、login / test account、camera permission、端末側のapp aspect-ratio設定、app data、選択中のcamera modeなど、両buildで揃えるinitial stateを保存する。変更やdata消去が必要なら先に確認する。
8. split-screen companion appがcamera / microphoneを要求せず、camera resourceや対象appのforeground動作と競合しないことを確認する。
9. テスト用camera scene、screen lock、通知表示、個人情報を含まない撮影環境を確認する。
10. evidence rootにrun IDを持つdirectoryを作成し、開始時刻と全command transcriptを記録する。

Pixel Tabletのmodel / SDK、APKのtargetSdkVersion、対象packageを証明できない場合は、Observedを作らずblockerとして報告してください。

## Phase 2: Affected screen and code inventory

既知画面だけに限定せず、次の利用箇所から回転・resize影響を受ける画面を棚卸ししてください。

各画面について通常のユーザー導線、必要なpermission / login / feature flag、direct intent / deep linkの有無を記録してください。direct intentやdeep linkで到達できても、通常導線の到達確認を代替したとは扱わず、どちらを実行したか明示してください。

Manifest / configuration:

- `screenOrientation`
- `resizeableActivity`
- `minAspectRatio` / `maxAspectRatio`
- `configChanges`
- `PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY`
- `appCategory`

Runtime / window:

- `setRequestedOrientation()` / `requestedOrientation`
- `getRequestedOrientation()`
- `Configuration.orientation`
- `screenWidthDp` / `screenHeightDp` / `smallestScreenWidthDp`
- `Display.getRotation()` / `display.rotation`
- `WindowMetrics` / window bounds / measured width and height
- `isInMultiWindowMode()` / `onMultiWindowModeChanged()`
- `onConfigurationChanged()`、Activity recreation、saved state

Camera:

- camera sensor orientation
- display rotation / target rotation
- CameraX `PreviewView`、`UseCase.targetRotation`、`SurfaceRequest.TransformationInfo`相当
- Camera1 / Camera2のpreview transform、`setDisplayOrientation()`相当
- front camera mirror
- preview resolution、crop rect、scale type、aspect ratio
- captured image / videoのrotation metadata、JPEG EXIF orientation

### Attribute-driven branch impact

取得または設定した属性に応じて処理を変える箇所は、単なる検索結果ではなく下流処理まで追跡してください。

| File / symbol | 取得・設定する属性 | 値のsource | Branch condition | 選択される処理 | 影響画面 | target 35 expected | target 36 expected | Runtime marker |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `<path:symbol>` | `<attribute>` | `<manifest/API/camera/window>` | `<if/when>` | `<layout/transform/recreate/navigation>` | `<screen>` | `<expected>` | `<expected>` | `<tag/event>` |

次を必ず確認してください。

- 値を取得するだけで分岐に使っていない箇所と、実際に処理を変える箇所を分ける。
- helper、ViewModel、Flow / LiveData / State、callbackを経由する場合もconsumerまで追跡する。
- requested orientationと実効orientation / window boundsを混同していないか確認する。
- displayの600dp gateと現在のapp window幅によるUI breakpointを混同していないか確認する。
- target 35 / 36、full-screen / multi-windowでbranchの入力値または選択結果が変わるか確認する。
- branchがcamera preview transform、crop、mirror、capture metadata、Activity recreation、state restorationへ与える影響を記録する。

## Phase 3: Evidence markers

画面到達は遷移元のclickやnavigation呼出しではなく、遷移先が表示可能な状態になったことを確認してください。

既存ログが不足する場合、debug / test限定で次のmarkerを追加してください。

```text
CameraEvidence RUN_ID=<id> EVENT=SCREEN_RESUMED SCREEN=<stable-screen-id>
CameraEvidence RUN_ID=<id> EVENT=PREVIEW_STREAMING SCREEN=<id> LENS=<front|back>
CameraEvidence RUN_ID=<id> EVENT=ATTRIBUTE_READ NAME=<name> VALUE=<value>
CameraEvidence RUN_ID=<id> EVENT=BRANCH_SELECTED BRANCH=<stable-branch-id> RESULT=<result>
CameraEvidence RUN_ID=<id> EVENT=WINDOW_STATE ROTATION=<value> ORIENTATION=<value> SMALLEST_WIDTH_DP=<value> BOUNDS=<value> MULTI_WINDOW=<true|false>
CameraEvidence RUN_ID=<id> EVENT=CAMERA_TRANSFORM SENSOR_ORIENTATION=<value> TARGET_ROTATION=<value> RESOLUTION=<value> CROP=<value> MIRROR=<value>
```

同じtagとrun IDを全証跡で使用してください。process restart後はPIDが変わるため、PIDだけでrunを識別しないでください。

## Phase 4: Test matrix

Build / compat条件:

| ID | Build | Compat state | Purpose |
| --- | --- | --- | --- |
| B1 | target 35 | default | Android 16上の従来target baseline |
| B2 | target 35 | `UNIVERSAL_RESIZABLE_BY_DEFAULT` enable | target更新前に新挙動を分離 |
| B3 | target 36 | default | Android 16 Adaptive layouts既定挙動 |
| B4 | target 36 | `UNIVERSAL_RESIZABLE_BY_DEFAULT` disable | 同じtarget 36 buildで旧挙動と比較 |
| B5 | target 36 | manifest opt-out | projectがopt-outを利用する場合だけscopeを確認 |

Window / rotation条件:

| ID | Window mode | Operation |
| --- | --- | --- |
| W1 | Full-screen | portrait相当で安定後に取得 |
| W2 | Full-screen | landscape相当で安定後に取得 |
| W3 | Full-screen | W1 -> W2の回転後、Activity / camera / state復帰を取得 |
| W4 | Split-screen | dividerを幅広側にして取得 |
| W5 | Split-screen | dividerを狭幅側にして取得 |
| W6 | Split-screen | split状態のまま回転またはbounds変更し、復帰を取得 |
| W7 | Full-screen | splitから戻した後の状態復帰を取得 |

各影響画面についてB1とB3をW1〜W7で実行してください。B2とB4は最も重要なcamera preview画面でW1〜W6を実行し、Behavior Change単体の影響を分離してください。B5はmanifest opt-outが存在する場合だけ実行してください。

back / front camera、photo / videoなど複数モードがある場合は、screen inventoryのリスクに基づき組み合わせを選び、除外理由を記録してください。最低限、主要preview画面はback / frontの両方を確認してください。

## Phase 5: Device operations

### Rotation

- 実行前に元のuser rotation mode / valueを保存する。
- `adb shell wm help`が示すsyntaxだけを使う。
- commandが成功しても、rotation番号からportrait / landscapeを決めず、実効display情報、window bounds、screenshotで確認する。
- ADBによるlogical rotationと、Pixel Tabletを物理的に回す操作を区別して記録する。
- camera sensor / HAL /端末姿勢の影響を確認するケースでは、必要な時点でユーザーへ物理回転を依頼し、そのケースを自動ADB回転で代替しない。

### Multi-window

- display size overrideは真のmulti-windowの代替にしない。
- 端末buildに依存する非公開・旧式のtask resize commandを推測して使わない。
- 安定したUI test / system UI操作があれば使用する。なければユーザーへsplit-screen開始、divider移動、終了を依頼して継続する。
- `isInMultiWindowMode()` marker、Activity / Window dumps、boundsの3つでmulti-window状態を確認する。
- companion app、divider位置、左右または上下の配置を各ケースで固定・記録する。
- camera / microphoneを使用するappをcompanionに選ばず、camera resource競合をレイアウト不具合と誤認しない。

### Compat change

- `am compat enable|disable|reset UNIVERSAL_RESIZABLE_BY_DEFAULT <package>`を使う前に、debuggable buildと対象端末でtoggle可能か確認する。
- toggleはapp processを停止するため、毎回同じinitial stateとentry pointから画面へ到達し直す。
- case開始前に実効compat stateを保存する。
- 最後にpackage overrideをresetする。

## Phase 6: Evidence collection

各caseで、同じcase IDとrun IDを使って次を保存してください。

```text
<evidence-output-root>/<run-id>/<case-id>/
├── metadata.txt
├── commands.txt
├── logcat.txt
├── activity.txt
├── window.txt
├── display.txt
├── layout.json
├── screenshot.png
├── visual-review.md
└── capture-metadata.txt       # 撮影結果を検証した場合
```

必須証跡:

1. `CameraEvidence`の`SCREEN_RESUMED`と、camera画面なら`PREVIEW_STREAMING`。
2. 属性取得値と`BRANCH_SELECTED`。影響branchがない場合はsource inspection結果を記録する。
3. `dumpsys activity activities`によるtop / resumed Activity。
4. `dumpsys window windows`によるfocus、windowing mode、bounds。
5. display rotation、configuration、size、density。
6. `android layout --device=<serial> --pretty`によるUI hierarchy。失敗時は失敗理由を保存する。
7. `adb -s <serial> exec-out screencap -p`によるdisplay screenshot。
8. screenshotをCodexの画像表示機能で実際に開いたvisual review。
9. command、開始・終了時刻、exit status。
10. targetSdkVersion、APK SHA-256、compat state。

screen到達済みと判定するには、原則として次の4点を一致させてください。

- destination側の`SCREEN_RESUMED`
- top / resumed Activityまたはsingle-Activity appのdestination固有UI marker
- destination固有のUI hierarchy element
- 視認済みscreenshot

single-Activity / Compose navigationではActivity名だけを到達証拠にしないでください。camera previewが`SurfaceView`、protected buffer、`FLAG_SECURE`等によりscreenshotで黒くなる場合は成功扱いにせず、制約を記録し、許可された非secure debug buildまたは端末外観撮影を代替候補として提示してください。secure表示を回避する操作は行わないでください。

撮影画像まで対象とする場合は、preview screenshotとは別に、生成fileのpixel dimensions、rotation metadata / EXIF、front camera mirror方針、表示結果を記録してください。

## Phase 7: Analysis

caseごとに次を比較してください。

- target 35 default vs target 36 default
- target 35 default vs target 35 compat enable
- target 36 default vs target 36 compat disable
- full-screen vs split-screen wide vs split-screen narrow
- requested orientation vs effective orientation / bounds
- app codeで取得した属性値 vs 選択されたbranch vs visual result
- back camera vs front camera
- rotation / resize前後のpreview transform、crop、mirror、controls位置、state preservation

画面のstretch、clip、off-screen control、previewの反転・回転・歪み、system bar / dividerとの重なり、dialog / overlay位置、camera再接続、入力状態消失を確認してください。回転途中だけの黒画面や一時崩れが疑われる場合は、screenshotだけで結論を出さず、許可範囲で短いscreen recordingまたは追加ログを候補として記録してください。

## Output

evidence root直下へ次を作成してください。

- `INDEX.md`: environment、build、case一覧、各artifactへのリンク、Expected / Observed、Pass / Fail / Blocked / Not tested。
- `code-impact.md`: 影響画面、属性取得・設定箇所、branch、下流処理、target 35 / 36差、runtime marker、根拠file / symbol。
- `visual-comparison.md`: target 35 / 36、full-screen / multi-window、before / afterのscreenshot比較と視認結果。
- `SHA256SUMS`: APK、screenshot、主要log / dumpのhash。
- `cleanup.md`: 復元したrotation、compat override、window state、残った変更・blocker。

対象projectまたは調査repositoryへ結果を反映するのは、別途明示された場合だけにしてください。実機結果を反映する場合はUC-09のルールに従い、Expected、Observed、Facts、Conclusionsを分けてください。

## Cleanup

- user rotation mode / valueを開始前の状態へ戻す。
- compat overrideをresetする。
- split-screenを終了し、開始前のwindow状態へ戻す。
- debug / test markerのsource変更は勝手に破棄せず、diffと残置理由を報告する。
- background logcat processがあれば停止する。
- app data、camera media、既存ログを削除していないことを確認する。

## Completion criteria

- Pixel Tablet実機、Android 16 / API 36を証明した。
- target 35 / 36 buildの出所とtargetSdkVersionを証明した。
- 影響画面と属性依存branchをsourceから棚卸しした。
- 必須matrixを実行し、未実行はNot testedとして理由を記録した。
- 各caseの画面到達をlog、system state、UI hierarchy、視認済みscreenshotで確認した。
- camera固有のsensor / target rotation、transform、crop、mirrorを必要範囲で確認した。
- ExpectedとObservedを分け、推測をObservedにしていない。
- 端末設定とcompat overrideを復元した。
- evidence index、code impact、visual comparison、hash、cleanup記録を作成した。
