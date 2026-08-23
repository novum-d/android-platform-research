# Android 16 Adaptive layouts - Manifest / API 挙動ガイド

## 位置づけ

このファイルは、Android 16 の Adaptive layouts で挙動が変わる manifest 属性、runtime API、例外、temporary opt-out を横断して確認するための companion guide である。

適用条件、AOSP evidence、classification、confidence、Human Decision は次の primary report を正とする。

- [Adaptive layouts](../target/device-form-factors/adaptive-layouts.md)
- [Ignore orientation, resizability, and aspect ratio restrictions](../target/device-form-factors/ignore-orientation-resizability-and-aspect-ratio-restrictions.md)
- [Implementation details](../target/device-form-factors/implementation-details-adaptive-layouts.md)
- [Exceptions](../target/device-form-factors/exceptions-adaptive-layouts.md)
- [Temporary opt-out](../target/device-form-factors/temporary-opt-out-adaptive-layouts.md)

本ガイドは新しい Behavior Change や独立した結論を追加しない。既存の調査結果を、実装の棚卸しと実機確認に使える形へ並べ替えたものである。

## 対象

- Android OS: Android 16
- targetSdkVersion: 36 以上
- large screen: display の `smallestScreenWidthDp >= 600`
- 主分類: `TARGET_SDK_36_CONDITIONAL`
- Compat change: `UNIVERSAL_RESIZABLE_BY_DEFAULT`（Change ID `357141415`）

既定適用の基本条件は次のとおり。

| 条件 | 必要な状態 |
| --- | --- |
| Device OS | Android 16 以上 |
| targetSdkVersion | 36 以上 |
| Display size | `smallestScreenWidthDp >= 600` |
| App category | game ではない |
| User setting | app の従来挙動を使う aspect ratio 例外が選択されていない |
| Temporary opt-out | application / activity のどちらにも opt-out がない |

Android 16 へ OS アップデートしただけで、targetSdkVersion 35 以下のアプリへ本変更が既定適用されるわけではない。

## 読み方: 指定値・保持値・システムが実際に採用する挙動を分ける

「ignored」は、manifest parser や API call がなくなるという意味ではない。次の 3 段階を分けて確認する。

| 段階 | 意味 | 例 |
| --- | --- | --- |
| 指定・要求 | manifest または runtime API からアプリが渡す値 | `screenOrientation="portrait"`、`setRequestedOrientation(...)` |
| 保持・取得 | framework 内部や getter で確認できる要求値 | `ActivityInfo.screenOrientation`、`getRequestedOrientation()` |
| システムが実際に採用する挙動 | WindowManager policy が最終的に採用する画面の向き、ウィンドウ領域、サイズ変更可否 | 横向きの大画面全体へ再レイアウトされる |

指定値やgetterの戻り値が残っていても、システムが実際に採用する画面の向きや、アプリに割り当てるウィンドウ領域の制約として採用されない場合がある。

本文では、人向けの説明に次の日本語表現を使う。AOSPのメソッド名、compat change名、ログ、引用原文などの識別子は翻訳しない。

- 制限対象となる固定方向
- 画面の向きの要求 / 要求値
- あらゆるウィンドウサイズへ変更可能とする状態・判定

## 「無視」はデフォルト値へ書き換えるという意味ではない

結論として、manifest 属性や runtime API の値が一律にデフォルト値へ変更されるわけではない。「無視」は、指定・要求された値を最終的な orientation、resizability、aspect ratio、window bounds を決める制約として採用しない、という意味である。

```text
Manifest / runtime API で値を指定
-> 値を parse、保持、または system server へ送信
-> Adaptive layouts の適用条件を評価
-> 対象なら固定方向・サイズ変更不可・アスペクト比の制約から除外
-> display またはmulti-window containerの条件で、実際に適用するConfigurationとウィンドウ領域を決定
```

属性・APIごとの違いは次のとおり。

| 属性・API | 指定値そのもの | policy 内部での扱い | システムが実際に採用する結果 | デフォルト値化と呼べるか |
| --- | --- | --- | --- | --- |
| `android:screenOrientation` | `ActivityInfo.screenOrientation` に保持され得る | 制限対象となる固定方向は、最終的な画面の向きを決める際に`SCREEN_ORIENTATION_UNSPECIFIED`相当として扱われる | アプリの固定方向ではなくdisplay / window policyに従う | No。manifest値を書き換えるのではなく、解決時に制約から外す |
| `setRequestedOrientation()` | 画面の向きの要求はsystem serverへ送られ、要求値が残る場合がある | 制限対象となる固定方向の要求を、最終的な画面の向きの制約にしない | 要求した向きと実際の画面の向きが一致しない場合がある | No。methodの引数をデフォルト値へ変更するわけではない |
| `getRequestedOrientation()` | 要求値を返す経路が残る | getterの戻り値は、システムが実際に採用した画面の向きを示す正本にならない | portraitを返しても横長のウィンドウ領域で表示され得る | No。常に`UNSPECIFIED`やデフォルト値を返すわけではない |
| `android:resizeableActivity="false"` | manifest value と `resizeMode` の入力経路は残る | `isUniversalResizeable()` により最終的な resizable 判定が true になり得る | 全画面以外に分割画面や可変boundsでも表示される | No。属性を `true` へ書き換えるのではなく、判定結果を上書きする |
| `android:minAspectRatio` / `android:maxAspectRatio` | manifest指定値は保持され得る | あらゆるウィンドウサイズへ変更可能と判定された場合、aspect ratio policyは判定に使うmin / maxを`0`として扱う | 指定比率でウィンドウ領域を制限せず、利用可能な領域を使う | No。`0`はこのpolicyで「制約なし」を表す値であり、manifest値の書き換えではない |

`SCREEN_ORIENTATION_UNSPECIFIED` 相当や aspect ratio `0` が内部処理に現れても、すべての属性・APIがそれぞれの宣言上のデフォルト値へ戻された、と一般化しない。共通する意味は「アプリ指定の制約を最終レイアウト決定に使わない」である。

### 全画面モードとマルチウィンドウモード

制約を無視する基本的な意味は両モードで同じだが、制約を除外した後にアプリへ割り当てるウィンドウ領域を決める外部条件が異なる。

| Mode | 制約を除外した後の主な決定条件 | 期待される見え方 | 確認すべき情報 |
| --- | --- | --- | --- |
| Full-screen | displayの回転、利用可能領域、system bar / display feature | appは固定方向やpillarboxに依存せず、原則として利用可能な画面全体へ配置される | 要求値、`Configuration.orientation`、WindowMetrics、実画面 |
| Multi-window | split-screen dividerやdesktop windowingが与えるwindow container bounds | 物理displayの向きにかかわらず、縦長・横長・狭幅などのwindowへ再レイアウトされる | 要求値、window bounds変更、configuration change、UI state |

したがって、実装側は「無視された後にどのデフォルト値になるか」ではなく、「現在与えられたwindow boundsとconfigurationに対してUIをどう適応させるか」を基準にする。window変更でActivityが再生成されるか、configuration callbackになるかもmanifest属性のデフォルト値からは判断せず、実機で状態保持を含めて確認する。

## Manifest 属性・runtime API 一覧

| 種別 | 属性・API | 従来依存していた挙動 | Android 16 / target 36 / large screenでシステムが実際に採用する挙動 | 値・呼び出しの扱い | 主な確認方法 |
| --- | --- | --- | --- | --- | --- |
| Manifest | `android:screenOrientation` | Activityを指定した画面の向きに固定する | 下表の列挙値は固定方向の制約として採用されない | manifest値はparseされ`ActivityInfo`に保持され得る | 端末回転後の`Configuration.orientation`、アプリに割り当てられたウィンドウ領域、画面表示を確認 |
| Manifest | `android:resizeableActivity="false"` | Activityをサイズ変更不可とし、compatibility modeを期待する | あらゆるウィンドウサイズへ変更可能とする条件ではサイズ変更可能として扱われ、falseによる制約は効かない | manifest値の入力経路は残る | 全画面、分割画面、window resizeで領域の追従を確認 |
| Manifest | `android:minAspectRatio` | 最小アスペクト比でウィンドウ領域を制限する | あらゆるウィンドウサイズへ変更可能とする条件ではaspect ratio policyが0扱いにし、制約として効かない | manifest値の入力経路は残る | 縦長・横長・分割画面でアプリに割り当てられたウィンドウ領域とcontent scalingを確認 |
| Manifest | `android:maxAspectRatio` | 最大アスペクト比でウィンドウ領域を制限する | あらゆるウィンドウサイズへ変更可能とする条件ではaspect ratio policyが0扱いにし、制約として効かない | manifest値の入力経路は残る | pillarboxの有無、アプリに割り当てられたウィンドウ領域、content scalingを確認 |
| Runtime API | `Activity#setRequestedOrientation(int)` | 実行中にActivityの画面の向きの変更を要求する | 制限対象となる固定方向の要求は、最終的に適用する制約として採用されない | 要求はsystem serverへ渡り、要求値が残る場合がある | 呼び出し前後のgetter、Configuration、recreation、ウィンドウ領域を別々に記録 |
| Runtime API | `Activity#getRequestedOrientation()` | 現在の画面の向きの要求値を取得する | getterの値だけでは、システムが実際に採用した画面の向きやアプリに割り当てられたウィンドウ領域を判定できない | 要求値を返す経路は残る | getterと`Configuration.orientation`、WindowMetrics、画面キャプチャを比較 |

公式文書では `resizableActivity` と表記される箇所があるが、Android manifest の属性名は `android:resizeableActivity` である。コード検索では後者を使う。

## 無視される orientation 値

公式文書が `screenOrientation`、`setRequestedOrientation()`、`getRequestedOrientation()` について明示している値を示す。列挙されていない orientation 値を同じ挙動と推定しない。

| Family | Manifest value | Runtime constant | 条件成立時の扱い |
| --- | --- | --- | --- |
| Portrait | `portrait` | `ActivityInfo.SCREEN_ORIENTATION_PORTRAIT` | portraitへの固定制約として採用されない |
| Portrait | `reversePortrait` | `ActivityInfo.SCREEN_ORIENTATION_REVERSE_PORTRAIT` | portraitへの固定制約として採用されない |
| Portrait | `sensorPortrait` | `ActivityInfo.SCREEN_ORIENTATION_SENSOR_PORTRAIT` | portraitへの固定制約として採用されない |
| Portrait | `userPortrait` | `ActivityInfo.SCREEN_ORIENTATION_USER_PORTRAIT` | portraitへの固定制約として採用されない |
| Landscape | `landscape` | `ActivityInfo.SCREEN_ORIENTATION_LANDSCAPE` | landscapeへの固定制約として採用されない |
| Landscape | `reverseLandscape` | `ActivityInfo.SCREEN_ORIENTATION_REVERSE_LANDSCAPE` | landscapeへの固定制約として採用されない |
| Landscape | `sensorLandscape` | `ActivityInfo.SCREEN_ORIENTATION_SENSOR_LANDSCAPE` | landscapeへの固定制約として採用されない |
| Landscape | `userLandscape` | `ActivityInfo.SCREEN_ORIENTATION_USER_LANDSCAPE` | landscapeへの固定制約として採用されない |

## 制約ごとの処理経路

| 入力 | 主なframework経路 | 最終的な制約として採用されなくなる処理 | 開発者が誤解しやすい点 |
| --- | --- | --- | --- |
| `screenOrientation` | manifest parsing -> `ActivityInfo.screenOrientation` -> `ActivityRecord#getOverrideOrientation()` | 制限対象となる固定方向を`SCREEN_ORIENTATION_UNSPECIFIED`相当に解決 | manifestが読まれないのではなく、最終policyで制約として採用されない |
| `setRequestedOrientation()` | `Activity` -> `ActivityClientController` -> `ActivityRecord#setRequestedOrientation()` | 要求値と、解決後の画面の向きが分離する | method callがno-opになると決めつけない。configuration changeの有無も別に観測する |
| `getRequestedOrientation()` | `Activity` / `ActivityRecord#getRequestedOrientation()` | 要求値を返す経路が残る | getterがportraitでも、表示中のwindowが横長の領域になる可能性がある |
| `resizeableActivity=false` | manifest parsing -> `ActivityInfo.resizeMode` -> `ActivityRecord#isResizeable()` | `isUniversalResizeable()` が resizable 判定に含まれる | false を指定しても split screen や resize を避けられるとは限らない |
| `minAspectRatio` / `maxAspectRatio` | manifest parsing -> `ActivityInfo` -> `AppCompatAspectRatioPolicy` | あらゆるウィンドウサイズへ変更可能と判定された場合にmin / maxを0として扱う | 指定値が存在してもpillarboxや固定比率を保証しない |

詳細な AOSP file、symbol、baseline / target diff、confidence は primary report の「AOSP 調査」を参照する。

## 適用を変える属性・設定

| 種別 | 属性・設定 | `true` / 選択時の効果 | Scope | 注意点 |
| --- | --- | --- | --- | --- |
| Manifest | `android:appCategory="game"` | game exceptionの判定対象となり、あらゆるウィンドウサイズへ変更可能とする処理経路から外れる | Application | gameであることを回避策として偽装しない。実際のcategoryと一致させる |
| Manifest property | `android.window.PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY=true` | サイズ変更を制限する指定を一時的に許可し、従来のcompatibility mode側へ戻す | ApplicationまたはActivity | temporary opt-out。API level 37 targetでは適用されないと公式文書が説明している |
| User setting | deviceのapp aspect ratio settingでapp default behaviorを明示選択 | user aspect ratio exceptionとして、あらゆるウィンドウサイズへ変更可能とする処理経路から外れる | User / app | 端末・OEM依存。アプリ側の恒久対応として扱わない |
| Compat framework | `UNIVERSAL_RESIZABLE_BY_DEFAULT` / `357141415` | enable で新挙動、disable で旧挙動を比較できる | Package | debuggable build での検証用。製品仕様の opt-out として扱わない |
| Device configuration | OEM / device config override | 画面の向きの要求やresize policyが既定と異なる可能性がある | Device | 公式Exceptionsの3項目とは分け、対象端末でObservedを記録する |

## Temporary opt-out の記述例

Application 全体を一時的に opt out する場合:

```xml
<application>
    <property
        android:name="android.window.PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY"
        android:value="true" />
</application>
```

特定 Activity だけを一時的に opt out する場合:

```xml
<application>
    <activity android:name=".LegacyActivity">
        <property
            android:name="android.window.PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY"
            android:value="true" />
    </activity>
</application>
```

Application-level property が true なら全 Activity が opt out される。移行中は影響を限定できる Activity-level を優先候補とし、理由、対象 Activity、削除条件、API 37 対応期限を判断ログへ残す。

## 600dp の読み違いを防ぐ

Behavior Change の platform gate は、対象 display の `smallestScreenWidthDp >= 600` を基準にする。現在のアプリ window の横幅だけを見て「600dp未満だから対象外」と判断しない。

一方、アプリの adaptive UI は、現在利用できる app window bounds を基準に組み替える。全画面の tablet でも分割画面では app window が狭くなるため、platform gate と UI breakpoint は別々に扱う。

`sw` は `smallest width` の略で、表示先ディスプレイの短い側に相当する幅を dp で表す。同じディスプレイを通常の portrait / landscape 回転にした場合、長辺と短辺が入れ替わるだけなので `sw` は基本的に変わらない。

Pixel Tablet を単純化した概念例（システム UI などにより実際の値とは差があり得る）:

```text
portrait:                 800dp x 1280dp
landscape:               1280dp x 800dp
display smallest width:           800dp（sw800dp）
split screen app window width:    500dp
```

この場合、画面回転後も display は `sw800dp` であり、本 Behavior Change の `sw600dp` gate を満たす。split screen で app window 幅が 500dp になっても platform gate は満たしたままだが、UI は現在の 500dp 幅に合わせて組み替える。foldable の外側 / 内側 display 切り替えや外部 display への移動など、表示先 display 自体が変わる場合は `sw` を再評価する。

| 判定 | 用途 | 基準 |
| --- | --- | --- |
| Platform behavior gate | orientation / resizability / aspect ratio 制約を無視するか | display の smallest width |
| App layout adaptation | nav bar / rail、pane数、content幅をどう変えるか | 現在の app window bounds |

## コードベースの棚卸し

Manifest:

```bash
rg -n 'screenOrientation|resizeableActivity|minAspectRatio|maxAspectRatio|PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY|appCategory' \
  --glob 'AndroidManifest.xml' --glob '*.xml'
```

Kotlin / Java:

```bash
rg -n 'setRequestedOrientation|getRequestedOrientation|requestedOrientation' \
  --glob '*.kt' --glob '*.java'
```

検索結果は次のように分類する。

| 分類 | 例 | 対応候補 |
| --- | --- | --- |
| UI制御 | camera、media、editor画面で orientation を固定 | window bounds に応じた layout と content scaling を定義 |
| Compatibility依存 | `resizeableActivity=false`、aspect ratio、pillarbox 前提 | 全画面・分割画面・desktop windowing を通常状態として検証 |
| Getter依存 | `getRequestedOrientation()`で分岐 | 実際に適用されたConfigurationと、アプリに割り当てられたウィンドウ領域を使う設計へ見直す |
| 一時回避 | opt-out property | Activity単位へ限定し、削除条件を記録 |
| 正当な例外 | game category | category と実際のアプリ用途が一致することを確認 |

## Compat change による比較

```bash
adb shell am compat enable UNIVERSAL_RESIZABLE_BY_DEFAULT <package>
adb shell am compat disable UNIVERSAL_RESIZABLE_BY_DEFAULT <package>
adb shell am compat reset UNIVERSAL_RESIZABLE_BY_DEFAULT <package>
```

切り替え時にアプリプロセスが停止するため、各ケースは同じ entry point と初期状態から開始する。public user build では制約があるため、原則として debuggable build を使う。

## 最小検証マトリクス

Pixel Tablet実機でAndroidアプリ画面の証跡を収集する場合は、[汎用実行プロンプト](../../../.codex/prompts/verify-app-rotation-on-pixel-tablet.md)を使用する。

| Case | OS | targetSdkVersion | Compat change | Opt-out | Expected |
| --- | --- | --- | --- | --- | --- |
| Baseline target | Android 16 | 35 | default | なし | 新挙動は既定適用されない |
| Forced new behavior | Android 16 | 35 | enable | なし | 移行前に新挙動を先行確認 |
| Default new behavior | Android 16 | 36 | default | なし | 条件成立時に指定された制約を最終的な制約として採用しない |
| Forced old behavior | Android 16 | 36 | disable | なし | 同一buildで旧挙動と比較 |
| Temporary opt-out | Android 16 | 36 | default | Activity または Application | opt-out scope だけ従来挙動側へ戻る |

各ケースで全画面の portrait / landscape、分割画面の幅変更、background / foreground、Activity再生成、入力状態とUI state preservationを確認する。

## Expected / Observed 記録表

| Case | 指定・要求値 | Getter / 保持値 | システムが実際に採用した画面の向き | アプリに割り当てられたウィンドウ領域 | UI状態 | Expected | Observed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `<case>` | `<manifest/API value>` | `<getter result>` | `<portrait/landscape>` | `<width x height dp>` | `<preserved/lost>` | `<primary reportから導出>` | 未実施 |

Observed を未確認のまま Expected と混ぜない。端末モデル、build、OS、targetSdkVersion、compat state、display mode、window modeも合わせて記録する。

## よくある誤解

| 誤解 | 正しい読み方 |
| --- | --- |
| `setRequestedOrientation()`は呼び出されなくなる | call pathは残る。固定方向の要求が最終的な制約として採用されない |
| `getRequestedOrientation()`がportraitなら画面もportrait | getterは要求値を返し得る。システムが実際に採用した画面の向きと、アプリに割り当てられたウィンドウ領域は別に確認する |
| `resizeableActivity=false`なら分割画面に入らない | あらゆるウィンドウサイズへ変更可能とする条件では、falseによる制約へ依存できない |
| aspect ratio属性が残っていればpillarboxされる | あらゆるウィンドウサイズへ変更可能とする条件では、min / max aspect ratioが最終的な制約として効かない |
| split screen の窓幅が600dp未満なら変更対象外 | platform gate の600dpは display 基準。UI adaptation は現在の窓幅基準 |
| opt-out を入れれば対応完了 | 一時的な移行猶予であり、API 37 target では適用されない |

## References

Entry point:

- https://developer.android.com/about/versions/16/behavior-changes-16#adaptive-layouts

Official references:

- https://developer.android.com/about/versions/16/behavior-changes-16#ignore-orientation
- https://developer.android.com/about/versions/16/behavior-changes-16#implementation-details
- https://developer.android.com/about/versions/16/reference/compat-framework-changes
- https://developer.android.com/guide/app-compatibility/test-debug

AOSP evidence と tag pair:

- `android-15.0.0_r36` -> `android-16.0.0_r4`
- 各 primary report の「AOSP 調査」を参照する。
