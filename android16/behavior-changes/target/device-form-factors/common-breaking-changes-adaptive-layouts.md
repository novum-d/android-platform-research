# Common breaking changes 調査レポート

## 基本情報（Metadata）

### 調査対象 Android バージョン（Android Versions）

From:
- android-15.0.0_r36

To:
- android-16.0.0_r4

Note:
- `android16/AGENTS.md` の既定 scope は `android-16.0.0_r1` だが、この調査では依頼に従い、公開済み Android 16 tag として `android-16.0.0_r4` を使った。
- `frameworks-base` checkout は clean。指定 tag `android-15.0.0_r36` / `android-16.0.0_r4` はどちらも存在する。
- AOSP evidence は local checkout の作業ツリーではなく、`git show <tag>:<path>` と `git diff android-15.0.0_r36 android-16.0.0_r4 -- <path>` で明示 tag を参照した。

### Behavior Change 文書（Behavior Change Source）

Document:
- https://developer.android.com/about/versions/16/behavior-changes-16#common-breaking

Section:
- Common breaking changes

Parent section:
- Adaptive layouts

Category:
- Device form factors

### 分類スナップショット（Classification Snapshot）

主分類（Primary classification）:
- `TARGET_SDK_36_CONDITIONAL`

早見表（At-a-glance impact）:

| 確認項目 | 回答 | 根拠 |
| --- | --- | --- |
| Android 16 へ OS アップデートしただけで targetSdkVersion 35 以下の全アプリに適用されるか | No | 上位 behavior の `UNIVERSAL_RESIZABLE_BY_DEFAULT` は targetSdkVersion 36 以上で default enabled |
| targetSdkVersion 36 以上が必要か | Yes | AOSP `ActivityInfo.UNIVERSAL_RESIZABLE_BY_DEFAULT` / 357141415 は `@EnabledAfter(VANILLA_ICE_CREAM)` |
| large screen 条件が必要か | Yes | Android 16 `DisplayContent#getIgnoreOrientationRequest()` は `sw >= 600dp` で orientation request を既定で無視する |
| UI 破壊・state loss は platform の直接動作か | Partly / No | platform は制約無視・configuration change・relaunch 経路を提供する。stretched layout、off-screen component、state loss は主にアプリ実装の前提が崩れるリスク |
| Compat framework でテストできるか | Yes | 公式 compat page は `UNIVERSAL_RESIZABLE_BY_DEFAULT` / 357141415 を Android 16 target で enabled と説明 |

### 調査日（Investigation Date）

2026-07-03

### 信頼度（Confidence）

- High

理由:
- 公式文書、公式 compat framework changes、AOSP ChangeId、targetSdkVersion gate、large screen gate、orientation / resizability / aspect ratio 制約無視の実装経路は一致している。
- `Common breaking changes` に書かれた stretched layout、off-screen animations/components、state loss は AOSP の単一 API 変更ではなく、制約無視・rotation・resize・recreation によってアプリ側の固定前提が破綻するリスクとして整理できる。

### 適用条件分類（Applicability Classification）

適用される条件（Applies when）:
- [ ] OS update / all apps on Android 16 regardless of targetSdkVersion
- [ ] targetSdkVersion >= 36 on Android 16+
- [x] targetSdkVersion >= 36, with additional runtime conditions
- [ ] Mainline / Google Play system update dependent
- [ ] API addition only, not a behavior change
- [ ] Unknown / needs more evidence

必要な実行時条件（Required runtime conditions）:
- Android version: Android 16 以上。
- targetSdkVersion: 36 以上。
- Device/form factor: display `smallestScreenWidthDp >= 600`。
- App category: `ApplicationInfo.CATEGORY_GAME` ではない。
- User setting: user aspect ratio setting が app default / 非 resizable と互換な例外状態ではない。
- Opt-out: `android.window.PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY=true` が application / activity に指定されていない。
- App implementation risk: small portrait-only layout、fixed aspect ratio、absolute positioning、off-screen animation、state preservation 不足、configuration / bounds change 未対応がある場合に顕在化しやすい。

Compat framework:
- Change ID: 357141415
- Change name: `UNIVERSAL_RESIZABLE_BY_DEFAULT`
- Default state: 公式 compat page では Android 16 / API level 36 以上を target するアプリで enabled。
- AOSP annotation: `@EnabledAfter(targetSdkVersion = Build.VERSION_CODES.VANILLA_ICE_CREAM)`。
- Force-enable / force-disable: `@Overridable`。公式文書は app compatibility framework で `UNIVERSAL_RESIZABLE_BY_DEFAULT` を enabled にしてテスト可能と説明している。

---

# エグゼクティブサマリー（Executive Summary）

Android 16 では、targetSdkVersion 36 以上のアプリが `sw >= 600dp` の large screen で実行される場合、orientation、resizability、aspect ratio の制約が既定で無視される。この結果、portrait 固定・小画面前提・固定 aspect ratio 前提の UI は、window 全体に stretch されたり、animation / component が想定外の位置に出たりする可能性がある。

この `Common breaking changes` 節は、platform が直接 UI を壊す専用処理を追加したというより、上位の adaptive layout behavior によってアプリの固定前提が崩れるリスクを説明している。state loss についても、platform がアプリ状態を消すというより、device rotation / bounds change / multi-window resize による Activity recreation 増加に対して、アプリが状態保存を実装していない場合に発生する。

顧客向けには「Android 16 へ OS アップデートしただけの影響」と「targetSdkVersion 36 化した時の large screen 影響」を分けて説明する。temporary opt-out は Android 16 では使えるが一時策であり、恒久対応は adaptive layout、state preservation、visual regression testing である。

---

# 公式ドキュメント確認（Original Documentation）

## 原文（Statement）

検証対象 statement:

```text
Ignoring orientation, resizability, and aspect ratio restrictions might impact your app's UI on some devices, especially elements that were designed for small layouts locked in portrait orientation.
```

```text
issues like stretched layouts and off-screen animations and components.
```

```text
Any assumptions about aspect ratio or orientation can cause visual issues with your app.
```

```text
Allowing device rotation results in more activity re-creation, which can result in losing user state if not properly preserved.
```

## 最新本文との差分（Documentation drift）

調査開始時に公式 URL の `#common-breaking` セクションを再確認した。ユーザー提示の Original statements / Applicability details と、確認時点の公式本文に実質差分はなかった。

## 解釈（Interpretation）

この節は `Adaptive layouts` の低レベル実装そのものではなく、`Ignore orientation, resizability, and aspect ratio restrictions` の結果として発生し得る UI / lifecycle risk を説明している。AOSP evidence では「制約が無視される platform gate」と「configuration change / relaunch 経路」を確認し、stretched layout や state loss はアプリ実装リスクとして分離する。

---

# 変更内容（What Changed）

- Android 16 tag では、`DisplayContent#getIgnoreOrientationRequest()` に large screen（`sw >= 600dp`）で orientation request を既定で無視する分岐が追加された。
- `ActivityRecord#isUniversalResizeable()` は large screen、compat change、game exception、temporary opt-out、user aspect ratio setting を評価し、fixed orientation / aspect ratio / resizability をまとめて無視する gate になる。
- `ActivityRecord#getOverrideOrientation()` は restricted fixed orientation を `SCREEN_ORIENTATION_UNSPECIFIED` に置き換える。
- `AppCompatAspectRatioPolicy#getMinAspectRatio()` / `getMaxAspectRatio()` は universal resizable の場合に min/max aspect ratio を 0 として扱う。
- `ActivityRecord#ensureActivityConfiguration()` / `updateReportedConfigurationAndSend()` は configuration / display / bounds 変更を評価し、必要なら `relaunchActivityLocked()` を呼ぶ。device rotation や resize が増えれば、アプリが処理すべき configuration / recreation ケースも増える。
- AOSP は app UI の stretched layout や state loss を直接作るのではなく、制約無視と再構成機会を増やす。UI 崩れと state loss は、固定 layout・固定座標・状態保存不足の app implementation risk として説明する。

---

# 適用条件（Applicability）

## OS アップデート時の挙動（OS Update Behavior）

- Android 16 に OS アップデートしただけで targetSdkVersion 35 以下の全アプリに適用されるか: No。
- Android 16 / targetSdkVersion 35: `UNIVERSAL_RESIZABLE_BY_DEFAULT` は default enabled ではない。従来の orientation、resizability、aspect ratio、compatibility mode / pillarboxing の扱いが残る想定。
- ただし OEM / device config の `ignore_activity_orientation_request` 系設定、ユーザー aspect ratio settings、既存 app compat override は別条件として存在するため、個別端末の挙動は device policy を確認する。

## targetSdkVersion 36 以上での挙動（targetSdkVersion 36 Behavior）

- Android 16 / targetSdkVersion 36 / `sw >= 600dp` / game ではない / opt-out なし / user exception なし: orientation、resizability、aspect ratio constraints は無視される。
- その結果、small portrait layout、fixed aspect ratio layout、off-screen animation、fixed-position component は visual issue を起こす可能性がある。
- device rotation / bounds change / multi-window resize により configuration change や Activity recreation の機会が増える。状態保存が不十分な場合、form input、scroll position、navigation state、media playback state などが失われる可能性がある。

## Android 15 / targetSdkVersion 36

- `android-15.0.0_r36` にも `UNIVERSAL_RESIZABLE_BY_DEFAULT`、opt-out property、`ActivityRecord#isUniversalResizeable()` の準備コードは存在する。
- ただし、`android-16.0.0_r4` では `DisplayContent#getIgnoreOrientationRequest()` に「large screen は既定で orientation request を無視する」分岐が追加されている。Android 15 tag には同等の default large screen 分岐は確認できなかった。
- よって Android 15 / targetSdkVersion 36 は Android 16 の公式 Behavior Change と同一とは結論しない。検証可能な環境があれば Android 16 / targetSdkVersion 36 と比較する。

## Temporary opt-out

- property: `android.window.PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY`
- 指定場所: application または activity の `<property>`。
- 値: `true` で restricted resizability を許可し、従来の compatibility mode 側へ戻す。
- 優先順位: AOSP は application level を先に確認し、true でなければ activity level を確認する。どちらかが true なら opt-out として扱われる。
- 将来 scope: `WindowManager.java` の comment に `TODO(b/357141415): Remove this from sdk 37` がある。Android 16 r4 の実装上は API 37 無効化 gate までは確認していないが、公式文書の将来無効化 statement と AOSP TODO は整合する。

---

# AOSP 調査（AOSP Investigation）

## 関連ファイル（Related Files）

- `core/java/android/content/pm/ActivityInfo.java`
- `core/java/android/view/WindowManager.java`
- `core/java/android/window/flags/windowing_frontend.aconfig`
- `services/core/java/com/android/server/wm/DisplayContent.java`
- `services/core/java/com/android/server/wm/DisplayArea.java`
- `services/core/java/com/android/server/wm/ActivityRecord.java`
- `services/core/java/com/android/server/wm/AppCompatResizeOverrides.java`
- `services/core/java/com/android/server/wm/AppCompatAspectRatioPolicy.java`
- `services/core/java/com/android/server/wm/AppCompatAspectRatioOverrides.java`
- `core/java/android/app/ActivityThread.java`
- `core/api/current.txt`
- `core/api/test-current.txt`

## 確認したソース文脈（Source Context Reviewed）

| ファイル / シンボル | Android 15 baseline | Android 16 target | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| `ActivityInfo.UNIVERSAL_RESIZABLE_BY_DEFAULT` | Change ID 357141415、`@EnabledAfter(VANILLA_ICE_CREAM)` が存在 | 同じ | targetSdkVersion 36 gate と compat override の根拠 |
| `DisplayContent#getIgnoreOrientationRequest()` | large screen default ignore 分岐なし | `mHasSetIgnoreOrientationRequest` が false かつ flag enabled の場合、`isLargeScreen()` なら true | Android 16 で large screen が既定で orientation request を無視する差分 |
| `DisplayContent#isLargeScreen()` / `WindowManager.LARGE_SCREEN_SMALLEST_SCREEN_WIDTH_DP` | threshold は 600 | threshold は 600 | `sw >= 600dp` 判定 |
| `ActivityRecord#isUniversalResizeable()` | 準備コードあり | large screen + ignore orientation + compat + opt-out + user setting を評価 | orientation / aspect ratio / resizability をまとめて無視する central gate |
| `ActivityRecord#canBeUniversalResizeable()` | `CATEGORY_GAME` を false にする | 同じ | game exception |
| `ActivityRecord#isResizeable()` | `isUniversalResizeable()` を含む | 同じ | `resizeableActivity=false` が実質無効になる経路 |
| `ActivityRecord#getOverrideOrientation()` | restricted fixed orientation を unspecified にできる | 同じ。Android 16 default large screen gate で到達しやすくなる | fixed orientation の実効無視 |
| `AppCompatAspectRatioPolicy#getMinAspectRatio()` / `getMaxAspectRatio()` | universal resizable なら 0 | 同じ。Android 16 default large screen gate で到達しやすくなる | `minAspectRatio` / `maxAspectRatio` 無効化 |
| `ActivityRecord#ensureActivityConfiguration()` / `updateReportedConfigurationAndSend()` | configuration 差分で relaunch / configuration callback を判断 | 同じ | rotation / resize / bounds change が activity recreation や config callback に接続される根拠 |
| `ActivityThread#scheduleRelaunchActivityIfPossible()` / `onConfigurationChanged()` | relaunch message と config callback を処理 | 同じ | app lifecycle / state preservation risk の platform context |
| `AppCompatResizeOverrides#allowRestrictedResizability()` | property を application / activity level で読む | 同じ | temporary opt-out |
| `WindowManager.PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY` | property 定義あり | property 定義あり、SDK 37 removal TODO あり | opt-out と future removal evidence |
| `AppCompatAspectRatioOverrides#userPreferenceCompatibleWithNonResizability()` | user aspect ratio code を評価 | 同じ | user aspect ratio setting exception |
| `core/api/current.txt` / `test-current.txt` | `UNIVERSAL_RESIZABLE_BY_DEFAULT` は public current ではなく test-current | 同じ | public API surface 上の新規一般 API ではなく compat/test API |

必須記入項目（Required context）:
- Entry point / caller: activity launch / configuration resolution、`Activity#setRequestedOrientation()` -> `ActivityClientController#setRequestedOrientation()` -> `ActivityRecord#setRequestedOrientation()`、bounds resolution -> `AppCompatAspectRatioPolicy`、configuration update -> `ActivityRecord#ensureActivityConfiguration()` -> relaunch or config callback。
- Relevant class or service responsibility: WindowManager / ActivityTaskManager は activity の orientation、window bounds、resizeability、size compat、aspect ratio policy、configuration dispatch を解決する。
- Baseline behavior: Android 15 tag には compat change と一部準備コードはあるが、large screen で default ignore する `DisplayContent#getIgnoreOrientationRequest()` 差分はない。
- Target behavior: Android 16 tag では large screen display が既定で orientation request を無視し、それが universal resizable 判定に接続される。
- Diff kind: added behavior（large screen default ignore）、changed condition（targetSdkVersion 36 compat gate）、removed behavior（fixed orientation / non-resizable / aspect ratio 制約の実効性）、indirect risk（UI 崩れ・state loss）。
- Excluded code paths: PiP aspect ratio、camera compat、test-only classes、desktop decoration rendering は、本 Behavior Change の主要 gate ではないため主根拠から除外した。

## 差分解釈（Diff Interpretation）

| 確認した差分 | 解釈 | Behavior Change との関係 | 信頼度 |
| --- | --- | --- | --- |
| `DisplayContent#getIgnoreOrientationRequest()` に large screen default 分岐追加 | Added behavior | Android 16 で `sw >= 600dp` が既定で orientation request を無視する根拠 | High |
| `ActivityInfo.UNIVERSAL_RESIZABLE_BY_DEFAULT` は `@EnabledAfter(VANILLA_ICE_CREAM)` | Changed condition / targetSdk gate | targetSdkVersion 36 以上が必要 | High |
| `ActivityRecord#canBeUniversalResizeable()` が `ApplicationInfo.CATEGORY_GAME` を除外 | Exception | game app 例外 | High |
| `ActivityRecord#isUniversalResizeable()` が opt-out property を確認 | Exception / opt-out | temporary opt-out で従来挙動へ戻る | High |
| `AppCompatAspectRatioPolicy` が universal resizable 時に min/max aspect ratio を 0 扱い | Removed behavior | fixed aspect ratio 前提が崩れる根拠 | High |
| `ActivityRecord#getOverrideOrientation()` が restricted fixed orientation を unspecified に変換 | Removed behavior | portrait locked small layout 前提が崩れる根拠 | High |
| `ActivityRecord#ensureActivityConfiguration()` が configuration 差分で relaunch を判断 | Existing lifecycle behavior exposed more often | rotation / resize / bounds change 増加により state preservation risk が増える根拠 | Medium |
| stretched layout / off-screen component / state loss | App implementation risk | AOSP が直接 UI を壊すのではなく、制約無視・recreation にアプリが適応できない場合の結果 | Medium |
| `WindowManager.PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY` に SDK 37 removal TODO | Future scope | opt-out が一時的という公式説明と整合 | Medium |
| public `current.txt` に新規 public API なし、`test-current.txt` に compat ID | API surface | 一般 app API 追加ではなく platform behavior / compat change | High |

---

# 期待挙動マトリクス（Expected Behavior Matrix）

## OS / targetSdkVersion

| Device OS | targetSdkVersion | 期待挙動 |
| --- | --- | --- |
| Android 16 | 35 | `UNIVERSAL_RESIZABLE_BY_DEFAULT` は default enabled ではない。Android 16 へ OS アップデートしただけでは本 Behavior Change の既定適用対象にしない |
| Android 16 | 36 | `sw >= 600dp`、game ではない、opt-out なし、user exception なしなら orientation / resizability / aspect ratio constraints を無視。UI / state preservation risk が増える |
| Android 15 | 36 | Android 15 tag に compat 準備コードはあるが、Android 16 の large screen default ignore 差分はない。公式 Behavior Change と同一扱いにせず、実機で比較確認 |

## Android 16 / targetSdkVersion 36 詳細

| 条件 | 期待挙動 |
| --- | --- |
| `sw >= 600dp` / opt-out なし | fixed orientation、non-resizable、min/max aspect ratio は無視され、window 全体を使用。small portrait layout は stretch risk |
| `sw >= 600dp` / Activity-level opt-out あり | 該当 activity では restricted resizability を許可し、従来の compatibility mode 側へ戻る |
| `sw >= 600dp` / Application-level opt-out あり | package 全体で opt-out。AOSP は application level を先に評価 |
| `sw < 600dp` | large screen gate を満たさないため、本 Behavior Change の適用対象外 |
| game app | `ApplicationInfo.CATEGORY_GAME` により universal resizable 対象外 |
| user aspect ratio setting exception | user preference が非 resizable と互換な場合、universal resizable から外れる |
| multi-window | constraints ignored により resize / bounds change へ対応する必要がある |
| full-screen | pillarboxing 前提ではなく window 全体を使う |
| split screen | window bounds 変化により fixed-size / absolute-position UI の崩れを確認する |
| desktop windowing | free resize / windowing mode resize による relaunch または config callback を確認する |
| device rotation | rotation により configuration change / recreation が増える可能性がある |
| Activity recreation with saved state | state restoration が正しく実装されていれば user state loss は抑制可能 |
| Activity recreation without saved state | navigation state、form input、scroll position、media state などの loss risk |

---

# 影響対象（Affected App Types）

- small layout locked in portrait orientation 前提のアプリ: large screen で横長 / 大画面 bounds に stretch されやすい。
- portrait / landscape 固定に依存するアプリ: fixed orientation が実効制約にならず、想定外 orientation / bounds で表示される。
- fixed aspect ratio 前提の UI を持つアプリ: canvas、media、preview、custom view の scaling / crop / letterbox policy を明示する必要がある。
- `resizeableActivity=false` に依存するアプリ: large screen で non-resizable 前提が崩れ、multi-window / desktop windowing / split screen で再レイアウトが必要になる。
- `minAspectRatio` / `maxAspectRatio` に依存するアプリ: aspect ratio による bounds 制限が効かず、固定アスペクト比 UI が崩れる可能性がある。
- pillarboxing / compatibility mode に依存するアプリ: compatibility mode に置かれる前提の余白、背景、入力領域、animation 範囲が崩れる可能性がある。
- off-screen animation / fixed-position component を持つアプリ: window bounds 全体使用により、開始位置・終了位置・可視範囲が想定とずれる可能性がある。
- Activity recreation 時の state preservation が不十分なアプリ: form input、navigation state、scroll position、media playback state を失う可能性がある。
- configuration change / bounds change を十分に扱っていないアプリ: `onConfigurationChanged`、relaunch、resource reload のテストが必要。
- `setRequestedOrientation()` を runtime に呼ぶアプリ: large screen で orientation lock として効かない。
- `getRequestedOrientation()` の戻り値に依存するアプリ: requested value と実効 orientation / bounds を混同しない。
- large screen / tablet / foldable / desktop windowing 対応が不十分なアプリ: stretch、off-screen component、固定寸法、状態消失が出やすい。
- games: AOSP 上は `ApplicationInfo.CATEGORY_GAME` で例外。`android:appCategory` の設定確認が必要。
- temporary opt-out 済みアプリ: Android 16 target では一時回避可能。ただし API 37 以降を見据えた恒久対応が必要。
- Compose UI アプリと View UI アプリ: window bounds / lifecycle の問題なので UI toolkit に関係なく対象。Compose では `rememberSaveable` なども含めて確認する。

---

# テスト観点（Test Considerations）

- Android 15 端末上の targetSdkVersion 35。
- Android 16 端末上の targetSdkVersion 35。
- Android 16 端末上の targetSdkVersion 36。
- Android 15 端末上の targetSdkVersion 36 が検証可能な場合の比較。
- `sw >= 600dp` と `sw < 600dp` の比較。
- portrait / landscape / reverse / sensor / user orientation 指定。
- `setRequestedOrientation()` 呼び出し後の挙動。
- `getRequestedOrientation()` の戻り値。
- `resizeableActivity=false` 指定あり / なし。
- `minAspectRatio` / `maxAspectRatio` 指定あり / なし。
- full-screen と multi-window。
- split screen と desktop windowing。
- device rotation。
- Activity recreation 回数。
- `onSaveInstanceState` / ViewModel / SavedStateHandle / Compose `rememberSaveable` などの state preservation。
- stretched layout。
- off-screen animation / component。
- fixed-size container / absolute-position UI。
- navigation state / form input / scroll position / media playback state の保持。
- Activity-level opt-out と Application-level opt-out。
- game app category。
- user aspect ratio settings。
- visual regression / screenshot testing。

---

# Facts / Observations / Hypotheses / Conclusions

## Facts

- 公式文書は、orientation / resizability / aspect ratio restrictions が無視されることで small portrait layout、stretched layout、off-screen animation / component、aspect ratio / orientation assumptions による visual issue が起き得ると説明している。
- 公式文書は、device rotation を許容することで Activity recreation が増え、状態保存が不十分な場合に user state を失う可能性があると説明している。
- 公式 compat page は `UNIVERSAL_RESIZABLE_BY_DEFAULT` / 357141415 を、Android 16 / API 36 以上を target するアプリで default enabled と説明している。
- AOSP `ActivityInfo.UNIVERSAL_RESIZABLE_BY_DEFAULT` は `@EnabledAfter(VANILLA_ICE_CREAM)`、`@Overridable`、`@TestApi`。
- AOSP `DisplayContent#getIgnoreOrientationRequest()` は Android 16 tag で large screen default ignore 分岐を持つ。
- AOSP `ActivityRecord#ensureActivityConfiguration()` は configuration 差分を評価し、必要なら `relaunchActivityLocked()` を呼ぶ。
- AOSP `AppCompatResizeOverrides` は `PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY` を application level、次に activity level で確認する。

## Observations

- `Common breaking changes` は低レベル API の追加・削除ではなく、上位の adaptive layout behavior による developer-facing risk の説明である。
- Android 15 tag にも compat change と一部準備コードはあるが、Android 16 tag では large screen default ignore 経路が追加されている。
- stretched layout / off-screen component は AOSP が直接生成するものではなく、アプリの layout が可変 bounds に適応できない場合の結果である。
- state loss は AOSP が直接 user state を削除するというより、relaunch / configuration change に対してアプリが state preservation を実装していない場合の結果である。

## Hypotheses

- 固定座標 animation、画面外からの translation、固定幅 container、portrait-only navigation flow は、large screen で最も visual regression が出やすい。
- Activity recreation の増加は、`configChanges` 指定、UI toolkit、navigation architecture、state holder 実装により影響度が大きく変わる。
- OEM device config や user aspect ratio settings により、同じ Android 16 / targetSdkVersion 36 でも個別端末の表示が変わる可能性がある。

## Conclusions

- 本件は `TARGET_SDK_36_CONDITIONAL`。ただし targetSdkVersion 36 だけでなく、Android 16 以上、large screen `sw >= 600dp`、game ではないこと、temporary opt-out なし、user aspect ratio exception なしという追加条件がある。
- Android 16 へ OS アップデートしただけの targetSdkVersion 35 以下アプリに、本 Behavior Change を既定適用として説明しない。
- visual issue と state loss は、platform の制約無視・rotation / resize / recreation 増加に対して、アプリの固定前提や state preservation 不足が露出するリスクである。
- 顧客対応では、targetSdkVersion 36 化時に large screen / multi-window / desktop windowing / rotation の visual regression と state restoration を重点確認する。

---

# 推奨対応候補（Recommended Action Candidates）

- fixed orientation を前提にせず、window bounds と size class に応じて layout を切り替える。
- fixed aspect ratio の canvas / media / preview 領域は、content aspect ratio と container aspect ratio を分離し、余白や crop policy を明示する。
- absolute position / off-screen animation は window bounds 依存で再計算し、tablet / foldable / desktop windowing の screenshot regression を追加する。
- Activity recreation を前提に、navigation state、form input、scroll position、media playback state を `onSaveInstanceState`、ViewModel、SavedStateHandle、Compose `rememberSaveable` 等で保持する。
- 一時的に移行期間が必要な activity だけ `PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY=true` を検討する。ただし API 37 以降を見据えて恒久対応を並行する。

---

# Human Decision

最終優先度（Final Priority）:
- 未判断

最終 severity（Final Severity）:
- 未判断

Release readiness:
- 未判断

Customer communication priority:
- 未判断

Owner notes:
- 最終優先度、severity、release readiness、顧客 communication priority は repository owner が判断する。
