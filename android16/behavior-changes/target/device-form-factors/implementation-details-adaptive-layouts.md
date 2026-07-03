# Implementation details 調査レポート

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
- https://developer.android.com/about/versions/16/behavior-changes-16#implementation-details

Section:
- Implementation details

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
| Android 16 へ OS アップデートしただけで targetSdkVersion 35 以下の全アプリに適用されるか | No | `UNIVERSAL_RESIZABLE_BY_DEFAULT` は Android 16 / API 36 以上 target で default enabled |
| targetSdkVersion 36 以上が必要か | Yes | AOSP `ActivityInfo.UNIVERSAL_RESIZABLE_BY_DEFAULT` / 357141415 は `@EnabledAfter(VANILLA_ICE_CREAM)` |
| `screenOrientation` / `setRequestedOrientation()` が効かなくなる根拠 | Yes | `ActivityRecord#getOverrideOrientation()` が restricted fixed orientation を `SCREEN_ORIENTATION_UNSPECIFIED` に置換 |
| `resizeableActivity=false` が効かなくなる根拠 | Yes | `ActivityRecord#isResizeable()` が `isUniversalResizeable()` を含む |
| `minAspectRatio` / `maxAspectRatio` が効かなくなる根拠 | Yes | `AppCompatAspectRatioPolicy#getMinAspectRatio()` / `getMaxAspectRatio()` が universal resizable で 0 を返す |
| Temporary opt-out | Yes | `PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY` を application / activity property として PackageManager 経由で読む |

### 調査日（Investigation Date）

2026-07-03

### 信頼度（Confidence）

- High

理由:
- 公式文書、公式 compat framework changes、AOSP ChangeId、targetSdkVersion gate、large screen gate、manifest parsing、runtime API path、orientation / resizeability / aspect ratio policy が一致している。
- `getRequestedOrientation()` は公式文書で ignored と列挙されるが、AOSP では requested value を返す経路が残るため、report では「戻り値そのもの」ではなく「実効 orientation constraint として無視される」と分けて記述する。

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
- Windowing mode: 公式文書上は large screen の full-screen / multi-window 両方。AOSP では universal resizable 判定が window policy と aspect ratio policy に接続される。
- App category: `ApplicationInfo.CATEGORY_GAME` ではない。
- User setting: user aspect ratio setting が app default / 非 resizable と互換な例外状態ではない。
- Opt-out: `android.window.PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY=true` が application / activity に指定されていない。

Compat framework:
- Change ID: 357141415
- Change name: `UNIVERSAL_RESIZABLE_BY_DEFAULT`
- Default state: 公式 compat page では Android 16 / API level 36 以上を target するアプリで enabled。
- AOSP annotation: `@EnabledAfter(targetSdkVersion = Build.VERSION_CODES.VANILLA_ICE_CREAM)`。
- Force-enable / force-disable: `@Overridable`。公式文書は app compatibility framework で `UNIVERSAL_RESIZABLE_BY_DEFAULT` を enabled にしてテスト可能と説明している。

---

# エグゼクティブサマリー（Executive Summary）

Android 16 の `Implementation details` 節は、large screen で adaptive layout behavior が有効になったときに、どの manifest attribute / runtime API が実効制約として無視されるかを列挙している。対象は `screenOrientation`、`resizeableActivity`、`minAspectRatio`、`maxAspectRatio`、`setRequestedOrientation()`、`getRequestedOrientation()` である。

AOSP evidence では、これらの値は manifest parsing や runtime API call で `ActivityInfo` / `ActivityRecord` に保持されるが、Android 16 / targetSdkVersion 36 / `sw >= 600dp` / non-game / opt-out なし / user exception なしの条件では、WindowManager 側の universal resizable policy により実効 orientation / resizeability / aspect ratio constraint として尊重されなくなる。

Android 16 へ OS アップデートしただけの targetSdkVersion 35 以下アプリとは分けて説明する。temporary opt-out は Android 16 では可能だが一時策であり、API 37 以降を見据えた adaptive layout 対応が必要である。

---

# 公式ドキュメント確認（Original Documentation）

## 原文（Statement）

検証対象 statement:

```text
The following manifest attributes and runtime APIs are ignored across large screen devices in full-screen and multi-window modes: screenOrientation, resizableActivity, minAspectRatio, maxAspectRatio, setRequestedOrientation(), getRequestedOrientation().
```

```text
The following values for screenOrientation, setRequestedOrientation(), and getRequestedOrientation() are ignored: portrait, reversePortrait, sensorPortrait, userPortrait, landscape, reverseLandscape, sensorLandscape, userLandscape.
```

```text
Regarding display resizability, android:resizeableActivity="false", android:minAspectRatio, and android:maxAspectRatio have no effect.
```

```text
For apps targeting Android 16 (API level 36), app orientation, resizability, and aspect ratio constraints are ignored on large screens by default.
```

```text
Every app that isn't fully ready can temporarily override this behavior by opting out, which results in the previous behavior of being placed in compatibility mode.
```

## 最新本文との差分（Documentation drift）

調査開始時に公式 URL の `#implementation-details` セクションを再確認した。ユーザー提示の Original statements / Applicability details と、確認時点の公式本文に実質差分はなかった。

## 解釈（Interpretation）

この節は Adaptive layouts の具体的な実装詳細として、どの attribute / API / orientation value が large screen 上で実効制約として無視されるかを説明している。AOSP evidence では、値の parsing / retention と、WindowManager policy による実効無視を分けて読む必要がある。

---

# 変更内容（What Changed）

- Android 16 tag では、`DisplayContent#getIgnoreOrientationRequest()` に large screen（`sw >= 600dp`）で orientation request を既定で無視する分岐が追加された。
- `ActivityRecord#isUniversalResizeable()` は large screen、compat change、game exception、temporary opt-out、user aspect ratio setting を評価し、fixed orientation / aspect ratio / resizability をまとめて無視する gate になる。
- `ActivityRecord#getOverrideOrientation()` は restricted fixed orientation を `SCREEN_ORIENTATION_UNSPECIFIED` に置き換える。
- `ActivityInfo.isFixedOrientationPortrait()` / `isFixedOrientationLandscape()` は公式文書に列挙された `portrait`、`reversePortrait`、`sensorPortrait`、`userPortrait`、`landscape`、`reverseLandscape`、`sensorLandscape`、`userLandscape` を fixed orientation として判定する。
- `ActivityRecord#setRequestedOrientation()` は requested orientation を受け取るが、resolved orientation が request と異なり restricted fixed orientation の場合、target sdk 36 として fixed orientation request を無視するログ経路がある。
- `ActivityRecord#isResizeable()` は `isUniversalResizeable()` を含むため、`resizeableActivity=false` の `RESIZE_MODE_UNRESIZEABLE` 前提が崩れる。
- `AppCompatAspectRatioPolicy#getMinAspectRatio()` / `getMaxAspectRatio()` は、universal resizable の場合に manifest 由来の min/max aspect ratio を 0 として扱う。

---

# 適用条件（Applicability）

## OS アップデート時の挙動（OS Update Behavior）

- Android 16 に OS アップデートしただけで targetSdkVersion 35 以下の全アプリに適用されるか: No。
- Android 16 / targetSdkVersion 35: `UNIVERSAL_RESIZABLE_BY_DEFAULT` は default enabled ではない。従来の orientation、resizability、aspect ratio、compatibility mode / pillarboxing の扱いが残る想定。
- ただし OEM / device config の `ignore_activity_orientation_request` 系設定、ユーザー aspect ratio settings、既存 app compat override は別条件として存在するため、個別端末の挙動は device policy を確認する。

## targetSdkVersion 36 以上での挙動（targetSdkVersion 36 Behavior）

- Android 16 / targetSdkVersion 36 / `sw >= 600dp` / game ではない / opt-out なし / user exception なし: 公式文書に列挙された attributes / APIs は実効 orientation / resizeability / aspect ratio constraint として無視される。
- `screenOrientation` と `setRequestedOrientation()` は value が保持されても、large screen policy 上は fixed orientation lock として尊重されない。
- `getRequestedOrientation()` は requested value を返す経路が残るため、戻り値と実効 orientation / bounds を混同しない。
- `resizeableActivity=false`、`minAspectRatio`、`maxAspectRatio` は parsing されても、universal resizable 条件下では window bounds 制限として効かない。

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
- `core/java/android/content/pm/PackageParser.java`
- `core/java/android/app/Activity.java`
- `core/java/android/view/WindowManager.java`
- `core/java/android/window/flags/windowing_frontend.aconfig`
- `services/core/java/com/android/server/wm/ActivityClientController.java`
- `services/core/java/com/android/server/wm/DisplayContent.java`
- `services/core/java/com/android/server/wm/DisplayArea.java`
- `services/core/java/com/android/server/wm/ActivityRecord.java`
- `services/core/java/com/android/server/wm/AppCompatResizeOverrides.java`
- `services/core/java/com/android/server/wm/AppCompatAspectRatioPolicy.java`
- `services/core/java/com/android/server/wm/AppCompatAspectRatioOverrides.java`
- `core/api/current.txt`
- `core/api/test-current.txt`

## 確認したソース文脈（Source Context Reviewed）

| ファイル / シンボル | Android 15 baseline | Android 16 target | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| `ActivityInfo.UNIVERSAL_RESIZABLE_BY_DEFAULT` | Change ID 357141415、`@EnabledAfter(VANILLA_ICE_CREAM)` が存在 | 同じ | targetSdkVersion 36 gate と compat override の根拠 |
| `DisplayContent#getIgnoreOrientationRequest()` | large screen default ignore 分岐なし | `mHasSetIgnoreOrientationRequest` が false かつ flag enabled の場合、`isLargeScreen()` なら true | Android 16 で large screen が既定で orientation request を無視する差分 |
| `DisplayContent#isLargeScreen()` / `WindowManager.LARGE_SCREEN_SMALLEST_SCREEN_WIDTH_DP` | threshold は 600 | threshold は 600 | `sw >= 600dp` 判定 |
| `PackageParser` / `screenOrientation` | manifest value を `ActivityInfo.screenOrientation` に入れる | 同じ | parsing されるが実効 constraint で無視されることを分ける根拠 |
| `PackageParser` / `resizeableActivity` | manifest value から `resizeMode` を設定 | 同じ | `resizeableActivity=false` の入力経路 |
| `PackageParser` / `minAspectRatio` / `maxAspectRatio` | activity / application value を `ActivityInfo` に設定 | 同じ | min/max aspect ratio の入力経路 |
| `ActivityInfo.isFixedOrientationPortrait/Landscape()` | 公式列挙値を fixed portrait / landscape として判定 | 同じ | ignored orientation values の AOSP 対応 |
| `Activity#setRequestedOrientation()` -> `ActivityClientController#setRequestedOrientation()` | runtime API call を server に送る | 同じ | runtime API 入力経路 |
| `ActivityRecord#setRequestedOrientation()` | `setOrientation()` 後、restricted fixed orientation が解決値と異なる場合に target sdk 36 として無視ログ | 同じ | `setRequestedOrientation()` の実効無視 |
| `ActivityRecord#getOverrideOrientation()` | restricted fixed orientation を unspecified にできる | 同じ。Android 16 default large screen gate で到達しやすくなる | `screenOrientation` / requested orientation の実効無視 |
| `ActivityRecord#getRequestedOrientation()` | requested value を返す | 同じ | `getRequestedOrientation()` は戻り値と実効制約を分けて解釈する根拠 |
| `ActivityRecord#isResizeable()` | `isUniversalResizeable()` を含む | 同じ | `resizeableActivity=false` が実効無効になる経路 |
| `AppCompatAspectRatioPolicy#getMinAspectRatio()` / `getMaxAspectRatio()` | universal resizable なら 0 | 同じ | `minAspectRatio` / `maxAspectRatio` 無効化 |
| `AppCompatResizeOverrides#allowRestrictedResizability()` | property を application / activity level で読む | 同じ | temporary opt-out |
| `WindowManager.PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY` | property 定義あり | property 定義あり、SDK 37 removal TODO あり | opt-out と future removal evidence |
| `AppCompatAspectRatioOverrides#userPreferenceCompatibleWithNonResizability()` | user aspect ratio code を評価 | 同じ | user aspect ratio setting exception |
| `core/api/current.txt` / `test-current.txt` | `UNIVERSAL_RESIZABLE_BY_DEFAULT` は public current ではなく test-current | 同じ | public API surface 上の新規一般 API ではなく compat/test API |

必須記入項目（Required context）:
- Entry point / caller: manifest parsing -> `PackageParser` -> `ActivityInfo`、runtime API -> `Activity#setRequestedOrientation()` -> `ActivityClientController` -> `ActivityRecord#setRequestedOrientation()`、bounds / aspect ratio resolution -> `AppCompatAspectRatioPolicy`。
- Relevant class or service responsibility: WindowManager / ActivityTaskManager は activity の orientation、window bounds、resizeability、size compat、aspect ratio policy、letterbox / compatibility mode を解決する。
- Baseline behavior: Android 15 tag には compat change と一部準備コードはあるが、large screen で default ignore する `DisplayContent#getIgnoreOrientationRequest()` 差分はない。
- Target behavior: Android 16 tag では large screen display が既定で orientation request を無視し、それが universal resizable 判定に接続される。
- Diff kind: added behavior（large screen default ignore）、changed condition（targetSdkVersion 36 compat gate）、removed behavior（列挙された manifest attributes / runtime APIs の実効制約）。
- Excluded code paths: PiP aspect ratio、camera compat、test-only classes、desktop decoration rendering は、本 Behavior Change の主要 gate ではないため主根拠から除外した。

## 差分解釈（Diff Interpretation）

| 確認した差分 | 解釈 | Behavior Change との関係 | 信頼度 |
| --- | --- | --- | --- |
| `DisplayContent#getIgnoreOrientationRequest()` に large screen default 分岐追加 | Added behavior | Android 16 で `sw >= 600dp` が既定で orientation request を無視する根拠 | High |
| `ActivityInfo.UNIVERSAL_RESIZABLE_BY_DEFAULT` は `@EnabledAfter(VANILLA_ICE_CREAM)` | Changed condition / targetSdk gate | targetSdkVersion 36 以上が必要 | High |
| `PackageParser` は `screenOrientation` / `resizeableActivity` / `minAspectRatio` / `maxAspectRatio` を従来通り読む | No parsing removal | ignored は parsing されないという意味ではなく、実効制約として尊重されないという意味 | High |
| `ActivityInfo.isFixedOrientationPortrait/Landscape()` が公式列挙値を fixed orientation と判定 | Existing value mapping | 公式の ignored values と AOSP fixed orientation 判定が対応 | High |
| `ActivityRecord#getOverrideOrientation()` が restricted fixed orientation を unspecified に変換 | Removed behavior | `screenOrientation` / `setRequestedOrientation()` の実効無視 | High |
| `ActivityRecord#isResizeable()` が `isUniversalResizeable()` を含む | Removed behavior | `resizeableActivity=false` の実効無視 | High |
| `AppCompatAspectRatioPolicy` が universal resizable 時に min/max aspect ratio を 0 扱い | Removed behavior | `minAspectRatio` / `maxAspectRatio` の実効無視 | High |
| `ActivityRecord#getRequestedOrientation()` は requested value を返す | Nuance | 公式の ignored は戻り値そのものではなく、実効 orientation constraint としての無視を意味すると解釈 | Medium |
| `WindowManager.PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY` に SDK 37 removal TODO | Future scope | opt-out が一時的という公式説明と整合 | Medium |

---

# 期待挙動マトリクス（Expected Behavior Matrix）

## OS / targetSdkVersion

| Device OS | targetSdkVersion | 期待挙動 |
| --- | --- | --- |
| Android 16 | 35 | `UNIVERSAL_RESIZABLE_BY_DEFAULT` は default enabled ではない。Android 16 へ OS アップデートしただけでは本 Behavior Change の既定適用対象にしない |
| Android 16 | 36 | `sw >= 600dp`、game ではない、opt-out なし、user exception なしなら列挙された attributes / APIs は実効制約として無視 |
| Android 15 | 36 | Android 15 tag に compat 準備コードはあるが、Android 16 の large screen default ignore 差分はない。公式 Behavior Change と同一扱いにせず、実機で比較確認 |

## Android 16 / targetSdkVersion 36 詳細

| 条件 | 期待挙動 |
| --- | --- |
| `sw >= 600dp` / opt-out なし | `screenOrientation`、`resizeableActivity=false`、min/max aspect ratio、runtime orientation request は実効制約として無視 |
| `sw >= 600dp` / Activity-level opt-out あり | 該当 activity では restricted resizability を許可し、従来の compatibility mode 側へ戻る |
| `sw >= 600dp` / Application-level opt-out あり | package 全体で opt-out。AOSP は application level を先に評価 |
| `sw < 600dp` | large screen gate を満たさないため、本 Behavior Change の適用対象外 |
| full-screen | 公式文書上、列挙 attributes / APIs は ignored。pillarboxing 前提ではなく window 全体を使う |
| multi-window | 公式文書上、列挙 attributes / APIs は ignored。resize / bounds change へ対応する必要がある |
| `screenOrientation=portrait` | fixed portrait value として判定されるが、universal resizable 条件下では実効 orientation lock にならない |
| `screenOrientation=landscape` | fixed landscape value として判定されるが、universal resizable 条件下では実効 orientation lock にならない |
| `screenOrientation=sensorPortrait` / `sensorLandscape` | fixed portrait / landscape family として判定され、実効制約として無視される |
| `setRequestedOrientation()` 呼び出しあり | requested value は渡るが、restricted fixed orientation は実効 constraint として無視される |
| `resizeableActivity=false` | `isUniversalResizeable()` により resizable 扱いになり得る |
| `minAspectRatio` / `maxAspectRatio` 指定あり | universal resizable では aspect ratio policy が 0 扱いにする |
| game app | `ApplicationInfo.CATEGORY_GAME` により universal resizable 対象外 |
| user aspect ratio setting exception | user preference が非 resizable と互換な場合、universal resizable から外れる |

---

# 影響対象（Affected App Types）

- `android:screenOrientation` に依存するアプリ。
- portrait / landscape / reverse / sensor / user orientation 固定に依存するアプリ。
- `Activity#setRequestedOrientation()` を runtime に呼ぶアプリ。
- `Activity#getRequestedOrientation()` の戻り値に依存するアプリ。戻り値と実効 orientation / bounds を分けて確認する必要がある。
- `resizeableActivity=false` に依存するアプリ。
- `minAspectRatio` / `maxAspectRatio` に依存するアプリ。
- pillarboxing / compatibility mode に依存するアプリ。
- full-screen 前提の固定 orientation UI を持つアプリ。
- multi-window / split screen / desktop windowing 対応が不十分なアプリ。
- games。AOSP 上は `ApplicationInfo.CATEGORY_GAME` で例外。
- temporary opt-out 済みアプリ。Android 16 target では一時回避可能だが、API 37 以降を見据える必要がある。
- Compose UI アプリと View UI アプリ。window bounds / activity policy の問題なので UI toolkit に関係なく対象。

---

# テスト観点（Test Considerations）

- Android 15 端末上の targetSdkVersion 35。
- Android 16 端末上の targetSdkVersion 35。
- Android 16 端末上の targetSdkVersion 36。
- Android 15 端末上の targetSdkVersion 36 が検証可能な場合の比較。
- `sw >= 600dp` と `sw < 600dp` の比較。
- full-screen と multi-window。
- split screen と desktop windowing。
- `screenOrientation=portrait` / `reversePortrait` / `sensorPortrait` / `userPortrait`。
- `screenOrientation=landscape` / `reverseLandscape` / `sensorLandscape` / `userLandscape`。
- `setRequestedOrientation()` 呼び出し後の実効 orientation / configuration / bounds。
- `getRequestedOrientation()` の戻り値と実効 orientation constraint の差。
- `resizeableActivity=false` 指定あり / なし。
- `minAspectRatio` / `maxAspectRatio` 指定あり / なし。
- Activity-level opt-out と Application-level opt-out。
- game app category。
- user aspect ratio settings。
- pillarboxing / compatibility mode の有無。
- Activity recreation と UI state preservation。
- visual regression / screenshot testing。

---

# Facts / Observations / Hypotheses / Conclusions

## Facts

- 公式文書は、large screen devices の full-screen / multi-window modes で `screenOrientation`、`resizeableActivity`、`minAspectRatio`、`maxAspectRatio`、`setRequestedOrientation()`、`getRequestedOrientation()` が ignored と説明している。
- 公式文書は、portrait / reversePortrait / sensorPortrait / userPortrait / landscape / reverseLandscape / sensorLandscape / userLandscape が ignored values と説明している。
- 公式 compat page は `UNIVERSAL_RESIZABLE_BY_DEFAULT` / 357141415 を、Android 16 / API 36 以上を target するアプリで default enabled と説明している。
- AOSP `ActivityInfo.UNIVERSAL_RESIZABLE_BY_DEFAULT` は `@EnabledAfter(VANILLA_ICE_CREAM)`、`@Overridable`、`@TestApi`。
- AOSP `PackageParser` は対象 manifest attributes を `ActivityInfo` に読み込む。
- AOSP `DisplayContent#getIgnoreOrientationRequest()` は Android 16 tag で large screen default ignore 分岐を持つ。
- AOSP `AppCompatResizeOverrides` は `PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY` を application level、次に activity level で確認する。

## Observations

- ignored は「manifest / API value が一切記録されない」という意味ではなく、「large screen policy 上の実効 constraint として尊重されない」という意味で読むべきである。
- `getRequestedOrientation()` は requested value を返す経路が残るため、戻り値と実効 orientation / bounds の差をテストで確認する必要がある。
- Android 15 tag にも compat change と一部準備コードはあるが、Android 16 tag では large screen default ignore 経路が追加されている。
- `PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY` は hidden property であり、public `current.txt` の新規一般 API ではない。

## Hypotheses

- 公式文書の `getRequestedOrientation()` ignored は、アプリが期待する orientation lock の効果が無視されるという互換性説明であり、戻り値 API が常に別値を返すという意味ではない可能性が高い。
- full-screen / multi-window の差は、アプリの bounds / relaunch / configuration handling によって顕在化の仕方が変わる。
- OEM device config や user aspect ratio settings により、同じ Android 16 / targetSdkVersion 36 でも個別端末の表示が変わる可能性がある。

## Conclusions

- 本件は `TARGET_SDK_36_CONDITIONAL`。ただし targetSdkVersion 36 だけでなく、Android 16 以上、large screen `sw >= 600dp`、game ではないこと、temporary opt-out なし、user aspect ratio exception なしという追加条件がある。
- Android 16 へ OS アップデートしただけの targetSdkVersion 35 以下アプリに、本 Behavior Change を既定適用として説明しない。
- 公式文書に列挙された manifest attributes / runtime APIs は、Android 16 / targetSdkVersion 36 / large screen 条件下で実効 orientation / resizeability / aspect ratio constraint として無視される。
- 顧客対応では、API value の保持有無ではなく、実効 window bounds / orientation / pillarboxing / compatibility mode の差分を検証する。

---

# 推奨対応候補（Recommended Action Candidates）

- `screenOrientation` / `setRequestedOrientation()` による UI 制御を前提にせず、window bounds と size class に応じて layout を切り替える。
- `resizeableActivity=false` と aspect ratio manifest 指定に依存した互換表示をやめ、multi-window / split screen / desktop windowing を通常の表示状態として扱う。
- `getRequestedOrientation()` の戻り値で実効 orientation や bounds を推定しない。実際の configuration / window metrics を確認する。
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
