# Ignore orientation, resizability, and aspect ratio restrictions 調査レポート

Companion guide: [Adaptive layouts Manifest / API 挙動ガイド](../../case-guides/adaptive-layouts-manifest-api-behavior-guide.md)

## 基本情報（Metadata）

### 調査対象 Android バージョン（Android Versions）

From:
- android-15.0.0_r36

To:
- android-16.0.0_r4

Note:
- `frameworks-base` checkout は clean。指定 tag `android-15.0.0_r36` / `android-16.0.0_r4` はどちらも存在する。
- AOSP evidence は local checkout の作業ツリーではなく、`git show <tag>:<path>` と `git diff android-15.0.0_r36 android-16.0.0_r4 -- <path>` で明示 tag を参照した。

### Behavior Change 文書（Behavior Change Source）

Document:
- https://developer.android.com/about/versions/16/behavior-changes-16#ignore-orientation

Section:
- Ignore orientation, resizability, and aspect ratio restrictions

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
| Android 16 へ OS アップデートしただけで targetSdkVersion 35 以下の全アプリに適用されるか | No | `UNIVERSAL_RESIZABLE_BY_DEFAULT` は targetSdkVersion 36 以上で default enabled |
| targetSdkVersion 36 以上が必要か | Yes | AOSP `ActivityInfo.UNIVERSAL_RESIZABLE_BY_DEFAULT` / 357141415 は `@EnabledAfter(VANILLA_ICE_CREAM)` |
| large screen 条件が必要か | Yes | Android 16 `DisplayContent#isLargeScreen()` は `smallestScreenWidthDp >= 600` を判定し、`getIgnoreOrientationRequest()` の default true 条件に使う |
| 例外があるか | Yes | game app、user aspect ratio setting exception、temporary opt-out、`sw < 600dp` |
| Compat framework でテストできるか | Yes | 公式 compat page は `UNIVERSAL_RESIZABLE_BY_DEFAULT` / 357141415 を Android 16 target で enabled とし、公式文書も compat flag enabled によるテストを説明 |

### 調査日（Investigation Date）

2026-08-23

### 信頼度（Confidence）

- High

理由:
- 公式文書、公式 compat framework changes、AOSP ChangeId、targetSdkVersion gate、large screen gate、game exception、user setting exception、temporary opt-out、orientation / resizability / aspect ratio policy 経路が一致している。
- Android 15 tag にも準備コードは存在するが、Android 16 tag で `DisplayContent#getIgnoreOrientationRequest()` に large screen default ignore 経路が追加されているため、Android 15 / targetSdkVersion 36 と Android 16 / targetSdkVersion 36 は分離して扱える。

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
- Windowing mode: full-screen または multi-window。ここで multi-window は上位概念であり、split screen と desktop windowing を含む。
- App category: `ApplicationInfo.CATEGORY_GAME` ではない。
- User setting: user aspect ratio setting が app default / 非 resizable と互換な例外状態ではない。
- Opt-out: `android.window.PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY=true` が application / activity に指定されていない。
- App behavior: 固定方向、サイズ変更不可、min/max aspect ratio、pillarboxing、優先する画面の向き、固定aspect ratioの前提に依存している場合に顕在化しやすい。

条件式としてまとめると次のとおり。

```text
Android 16 以上
AND targetSdkVersion 36 以上
AND 表示先ディスプレイの smallestScreenWidthDp >= 600
AND（full-screen OR multi-window）
AND game 例外ではない
AND temporary opt-out なし
AND user aspect ratio setting 例外なし
```

`full-screen` と `multi-window` は同時に満たす条件ではなく、どちらの表示状態でも制約無視が適用されるという意味である。desktop windowing は multi-window の一形態なので対象に含まれる。`smallestScreenWidthDp >= 600` は現在のアプリウィンドウ幅ではなく表示先ディスプレイの判定であり、split screen や desktop windowing によって現在のウィンドウ幅が 600dp 未満になっても、それだけで本 Behavior Change の対象外にはならない。

Compat framework:
- Change ID: 357141415
- Change name: `UNIVERSAL_RESIZABLE_BY_DEFAULT`
- Default state: 公式 compat page では Android 16 / API level 36 以上を target するアプリで enabled。
- AOSP annotation: `@EnabledAfter(targetSdkVersion = Build.VERSION_CODES.VANILLA_ICE_CREAM)`。Android 15 は API 35 なので、実質 targetSdkVersion 36 以上で default enabled と読む。
- Force-enable / force-disable: `@Overridable`。公式文書は app compatibility framework で `UNIVERSAL_RESIZABLE_BY_DEFAULT` を enabled にしてテスト可能と説明している。

---

# エグゼクティブサマリー（Executive Summary）

Android 16では、targetSdkVersion 36以上のアプリが`sw >= 600dp`のdisplayで実行される場合、固定方向、サイズ変更不可、min/max aspect ratioなどの制約が既定で無視される。アプリはaspect ratioや優先する画面の向きに関係なくdisplay window全体を使い、従来のpillarboxing / compatibility modeを前提にできない。

これは「Android 16 へ OS アップデートしただけ」の影響ではなく、Android 16 端末上で targetSdkVersion 36 化した場合の large screen behavior change として説明する必要がある。実質影響は、large screen、非 game、opt-out なし、user aspect ratio exception なし、かつ固定 orientation / resizability / aspect ratio 制約に依存する UI で発生する。

一時 opt-out は `android.window.PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY=true` で可能だが、公式文書と AOSP comment は API level 37 以降では使えなくなる予定を示している。恒久対応は adaptive layout 化、状態保存、large screen / multi-window / desktop windowing の検証である。

---

# 公式ドキュメント確認（Original Documentation）

## 原文（Statement）

検証対象 statement:

```text
For apps targeting Android 16 (API level 36), orientation, resizability, and aspect ratio restrictions no longer apply on displays with smallest width >= 600dp.
```

```text
Apps fill the entire display window, regardless of aspect ratio or a user's preferred orientation, and pillarboxing isn't used.
```

```text
This change introduces a new standard platform behavior.
```

```text
Restrictions like fixed orientation or limited resizability hinder app adaptability.
```

```text
You can also test this behavior by using the app compatibility framework and enabling the UNIVERSAL_RESIZABLE_BY_DEFAULT compat flag.
```

## 最新本文との差分（Documentation drift）

調査開始時に公式 URL の `#ignore-orientation` セクションを再確認した。ユーザー提示の Original statements / Applicability details と、確認時点の公式本文に実質差分はなかった。

## 解釈（Interpretation）

公式文書は、Android 16 / targetSdkVersion 36 以上の large screen 向け Behavior Change として説明している。したがって、targetSdkVersion 35 以下の既存アプリが Android 16 へ OS アップデートしただけで同じ既定挙動になる、とは説明しない。

補足の公式 [Support multi-window mode](https://developer.android.com/develop/adaptive-apps/guides/support-multi-window-mode) は、multi-window mode の表示形態として split-screen、picture-in-picture、desktop windowing を挙げている。本レポートで desktop windowing を multi-window の一形態として扱う根拠はこの定義である。

---

# 変更内容（What Changed）

- Android 16 tag では、明示 override がなく `universal_resizable_by_default` flag が有効な場合、`DisplayContent#getIgnoreOrientationRequest()` が large screen（`sw >= 600dp`）で true を返す経路が追加された。
- `ActivityRecord#isUniversalResizeable()`はlarge screenかつdisplayが画面の向きの要求を無視する場合に、`UNIVERSAL_RESIZABLE_BY_DEFAULT` compat change、game exception、temporary opt-out、user aspect ratio settingを評価する。
- あらゆるウィンドウサイズへ変更可能と判定されたactivityは`isResizeable()`がtrueになり、`resizeableActivity=false`相当のサイズ変更不可という制約が実質的に効かない。
- `ActivityRecord#getOverrideOrientation()`は制限対象となる固定方向を`SCREEN_ORIENTATION_UNSPECIFIED`に置き換えるため、manifest / runtimeの固定方向は最終的な制約として採用されない。
- `AppCompatAspectRatioPolicy#getMinAspectRatio()` / `getMaxAspectRatio()`は、activityがあらゆるウィンドウサイズへ変更可能と判定された場合にmin/max aspect ratioを0として扱う。
- 結果として、アプリは preferred orientation や manifest aspect ratio による bounds 制限ではなく、与えられた display window 全体に適応する必要がある。

---

# 適用条件（Applicability）

## OS アップデート時の挙動（OS Update Behavior）

- Android 16 に OS アップデートしただけで targetSdkVersion 35 以下の全アプリに適用されるか: No。
- Android 16 / targetSdkVersion 35: `UNIVERSAL_RESIZABLE_BY_DEFAULT` は default enabled ではない。従来の orientation、resizability、aspect ratio、compatibility mode / pillarboxing の扱いが残る想定。
- ただし OEM / device config の `ignore_activity_orientation_request` 系設定、ユーザー aspect ratio settings、既存 app compat override は別条件として存在するため、個別端末の挙動は device policy を確認する。

## targetSdkVersion 36 以上での挙動（targetSdkVersion 36 Behavior）

- Android 16 / targetSdkVersion 36 / `sw >= 600dp` / game ではない / opt-out なし / user exception なし: orientation、resizability、aspect ratio constraints は無視される。
- 公式文書の「full-screen and multi-window modes」は、制約無視が両方の表示状態をカバーするという意味である。`full-screen AND multi-window` を同時に満たす必要はない。
- desktop windowing は multi-window mode の一形態である。split screen を desktop window 内でさらに開始できるかどうかとは無関係に、desktop windowing 自体が対象となる。
- `sw >= 600dp` は表示先ディスプレイの `smallestScreenWidthDp` で判定する。現在のアプリウィンドウ幅や端末の portrait / landscape の向きだけで適用対象から外れない。
- `setRequestedOrientation()`を呼んでも固定方向の指定として効かず、large screen上ではwindow全体を使う方向へ解決される。
- `getRequestedOrientation()`の戻り値と、システムが実際に採用した画面の向き・アプリに割り当てられたウィンドウ領域は分けて考える。AOSPでは要求した画面の向きを返す経路が残るが、最終的なlayoutの制約としては採用されない。

## Android 15 / targetSdkVersion 36

- `android-15.0.0_r36` にも `UNIVERSAL_RESIZABLE_BY_DEFAULT`、opt-out property、`ActivityRecord#isUniversalResizeable()` の準備コードは存在する。
- ただし、`android-16.0.0_r4`では`DisplayContent#getIgnoreOrientationRequest()`に「large screenでは既定で画面の向きの要求を無視する」分岐が追加されている。Android 15 tagには同等のdefault large screen分岐は確認できなかった。
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
- `core/api/current.txt`
- `core/api/test-current.txt`

## 確認したソース文脈（Source Context Reviewed）

| ファイル / シンボル | Android 15 baseline | Android 16 target | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| `ActivityInfo.UNIVERSAL_RESIZABLE_BY_DEFAULT` | Change ID 357141415、`@EnabledAfter(VANILLA_ICE_CREAM)` が存在 | 同じ | targetSdkVersion 36 gate と compat override の根拠 |
| `DisplayContent#getIgnoreOrientationRequest()` | large screen default ignore分岐なし | `mHasSetIgnoreOrientationRequest`がfalseかつflag enabledの場合、`isLargeScreen()`ならtrue | Android 16でlarge screenが既定で画面の向きの要求を無視する差分 |
| `DisplayContent#isLargeScreen()` | 未確認 | `smallestScreenWidthDp >= WindowManager.LARGE_SCREEN_SMALLEST_SCREEN_WIDTH_DP` | `sw >= 600dp` 判定 |
| `WindowManager.LARGE_SCREEN_SMALLEST_SCREEN_WIDTH_DP` | 600 | 600 | large screen threshold |
| `ActivityRecord#isUniversalResizeable()` | 準備コードあり | large screen + ignore orientation + compat + opt-out + user setting を評価 | orientation / aspect ratio / resizability をまとめて無視する central gate |
| `ActivityRecord#canBeUniversalResizeable()` | `CATEGORY_GAME` を false にする | 同じ | game exception |
| `ActivityRecord#isResizeable()` | `isUniversalResizeable()` を含む | 同じ | `resizeableActivity=false` が実質無効になる経路 |
| `ActivityRecord#getOverrideOrientation()` | 制限対象となる固定方向をunspecifiedにできる | 同じ。Android 16 default large screen gateで到達しやすくなる | 固定方向が最終的な制約として採用されないこと |
| `AppCompatAspectRatioPolicy#getMinAspectRatio()` / `getMaxAspectRatio()` | あらゆるウィンドウサイズへ変更可能と判定された場合は0 | 同じ。Android 16 default large screen gateで到達しやすくなる | `minAspectRatio` / `maxAspectRatio`無効化 |
| `AppCompatResizeOverrides#allowRestrictedResizability()` | property を application / activity level で読む | 同じ | temporary opt-out |
| `WindowManager.PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY` | property 定義あり | property 定義あり、SDK 37 removal TODO あり | opt-out と future removal evidence |
| `AppCompatAspectRatioOverrides#userPreferenceCompatibleWithNonResizability()` | user aspect ratio code を評価 | 同じ | user aspect ratio setting exception |
| `core/api/current.txt` / `test-current.txt` | `UNIVERSAL_RESIZABLE_BY_DEFAULT` は public current ではなく test-current | 同じ | public API surface 上の新規一般 API ではなく compat/test API |

必須記入項目（Required context）:
- Entry point / caller: activity launch / configuration resolution、`Activity#setRequestedOrientation()` -> `ActivityClientController#setRequestedOrientation()` -> `ActivityRecord#setRequestedOrientation()`、bounds resolution -> `AppCompatAspectRatioPolicy`。
- Relevant class or service responsibility: WindowManager / ActivityTaskManager は activity の orientation、window bounds、resizeability、size compat、aspect ratio policy を解決する。
- Baseline behavior: Android 15 tag には compat change と一部準備コードはあるが、large screen で default ignore する `DisplayContent#getIgnoreOrientationRequest()` 差分はない。
- Target behavior: Android 16 tagではlarge screen displayが既定で画面の向きの要求を無視し、それがあらゆるウィンドウサイズへ変更可能とする判定に接続される。
- Diff kind: added behavior（large screen default ignore）、changed condition（targetSdkVersion 36 compat gate）、removed behavior（固定方向・サイズ変更不可・アスペクト比の制約が最終的に適用される挙動）。
- Excluded code paths: PiP aspect ratio、camera compat、test-only classes、desktop decoration rendering は、本 Behavior Change の主要 gate ではないため主根拠から除外した。

## 差分解釈（Diff Interpretation）

| 確認した差分 | 解釈 | Behavior Change との関係 | 信頼度 |
| --- | --- | --- | --- |
| `DisplayContent#getIgnoreOrientationRequest()`にlarge screen default分岐追加 | Added behavior | Android 16で`sw >= 600dp`が既定で画面の向きの要求を無視する根拠 | High |
| `ActivityInfo.UNIVERSAL_RESIZABLE_BY_DEFAULT` は `@EnabledAfter(VANILLA_ICE_CREAM)` | Changed condition / targetSdk gate | targetSdkVersion 36 以上が必要 | High |
| `ActivityRecord#canBeUniversalResizeable()` が `ApplicationInfo.CATEGORY_GAME` を除外 | Exception | game app 例外 | High |
| `ActivityRecord#isUniversalResizeable()` が opt-out property を確認 | Exception / opt-out | temporary opt-out で従来挙動へ戻る | High |
| `AppCompatAspectRatioPolicy`があらゆるウィンドウサイズへ変更可能と判定された場合にmin/max aspect ratioを0扱い | Removed behavior | `minAspectRatio` / `maxAspectRatio`が最終的な制約として採用されないこと | High |
| `ActivityRecord#getOverrideOrientation()`が制限対象となる固定方向をunspecifiedに変換 | Removed behavior | manifest / runtimeの固定方向が最終的な制約として採用されないこと | High |
| `WindowManager.PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY` に SDK 37 removal TODO | Future scope | opt-out が一時的という公式説明と整合 | Medium |
| public `current.txt` に新規 public API なし、`test-current.txt` に compat ID | API surface | 一般 app API 追加ではなく platform behavior / compat change | High |

---

# 期待挙動マトリクス（Expected Behavior Matrix）

## OS / targetSdkVersion

| Device OS | targetSdkVersion | 期待挙動 |
| --- | --- | --- |
| Android 16 | 35 | `UNIVERSAL_RESIZABLE_BY_DEFAULT` は default enabled ではない。Android 16 へ OS アップデートしただけでは本 Behavior Change の既定適用対象にしない |
| Android 16 | 36 | `sw >= 600dp`、game ではない、opt-out なし、user exception なしなら orientation / resizability / aspect ratio constraints を無視 |
| Android 15 | 36 | Android 15 tag に compat 準備コードはあるが、Android 16 の large screen default ignore 差分はない。公式 Behavior Change と同一扱いにせず、実機で比較確認 |

## Android 16 / targetSdkVersion 36 詳細

| 条件 | 期待挙動 |
| --- | --- |
| `sw >= 600dp` / opt-outなし | 固定方向、サイズ変更不可、min/max aspect ratioの制約は無視され、window全体を使用 |
| `sw >= 600dp` / Activity-level opt-out あり | 該当 activity では restricted resizability を許可し、従来の compatibility mode 側へ戻る |
| `sw >= 600dp` / Application-level opt-out あり | package 全体で opt-out。AOSP は application level を先に評価 |
| `sw < 600dp` | large screen gate を満たさないため、本 Behavior Change の適用対象外 |
| game app | `ApplicationInfo.CATEGORY_GAME`により、あらゆるウィンドウサイズへ変更可能とする判定の対象外 |
| user aspect ratio setting exception | user preferenceがサイズ変更不可と互換な場合、あらゆるウィンドウサイズへ変更可能とする判定から外れる |
| full-screen | 公式文書上は full-screen でも constraints ignored。pillarboxing 前提ではなく window 全体を使う |
| multi-window | 公式文書上は large screen devices の multi-window でも constraints ignored。split screen と desktop windowing を含む |
| desktop windowing で現在の window 幅が 600dp 未満 | `sw` は表示先 display の判定なので、window 幅が狭くなったことだけでは対象外にならない |

---

# 影響対象（Affected App Types）

- portrait / landscape固定に依存するアプリ: large screenでは指定した画面の向きが最終的な制約にならず、横長/縦長windowにstretchされる。
- `resizeableActivity=false` に依存するアプリ: large screen で non-resizable 前提が崩れ、multi-window / desktop windowing / split screen で再レイアウトが必要になる。
- `minAspectRatio` / `maxAspectRatio` に依存するアプリ: aspect ratio による bounds 制限が効かず、固定アスペクト比 UI が崩れる可能性がある。
- pillarboxing / compatibility mode に依存するアプリ: compatibility mode に置かれる前提で余白、背景、入力領域、animation 範囲を設計している場合に差分が出る。
- `setRequestedOrientation()` を runtime に呼ぶアプリ: large screen で orientation lock として効かない。Activity recreation / state preservation の想定を見直す。
- `getRequestedOrientation()`の戻り値に依存するアプリ: 要求値と、システムが実際に採用した画面の向き・アプリに割り当てられたウィンドウ領域を混同しない。
- preferred orientation / user orientation 前提の UI を持つアプリ: user preferred orientation と window 全体使用の差分を確認する。
- fixed aspect ratio 前提の UI を持つアプリ: canvas、media、preview、custom view の scaling / crop / letterbox policy を明示する必要がある。
- large screen / tablet / foldable / desktop windowing 対応が不十分なアプリ: stretch、off-screen component、固定寸法、状態消失が出やすい。
- games: AOSP 上は `ApplicationInfo.CATEGORY_GAME` で例外。`android:appCategory` の設定確認が必要。
- temporary opt-out 済みアプリ: Android 16 target では一時回避可能。ただし API 37 以降を見据えた恒久対応が必要。
- Compose UI アプリと View UI アプリ: window bounds の behavior なので UI toolkit に関係なく対象。Compose でも adaptive layout と state preservation を確認する。

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
- Activity-level opt-out と Application-level opt-out。
- game app category。
- user aspect ratio settings。
- Activity recreation と UI state preservation。
- stretched layout、off-screen animation / component、固定アスペクト比前提 UI の visual regression。

---

# Facts / Observations / Hypotheses / Conclusions

## Facts

- 公式文書は Android 16 / API 36 target アプリの Behavior Change として、`sw >= 600dp` display で orientation、resizability、aspect ratio restrictions が適用されないと説明している。
- 公式 compat page は `UNIVERSAL_RESIZABLE_BY_DEFAULT` / 357141415 を、Android 16 / API 36 以上を target するアプリで default enabled と説明している。
- AOSP `ActivityInfo.UNIVERSAL_RESIZABLE_BY_DEFAULT` は `@EnabledAfter(VANILLA_ICE_CREAM)`、`@Overridable`、`@TestApi`。
- AOSP `DisplayContent#getIgnoreOrientationRequest()` は Android 16 tag で large screen default ignore 分岐を持つ。
- AOSP `ActivityRecord#canBeUniversalResizeable()` は game app を除外する。
- AOSP `AppCompatResizeOverrides` は `PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY` を application level、次に activity level で確認する。
- AOSP `WindowManager.PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY` には SDK 37 で削除する TODO がある。

## Observations

- Android 15 tag にも compat change と一部準備コードはあるが、Android 16 tag では large screen default ignore 経路が追加されている。
- `screenOrientation` / `setRequestedOrientation()`はAPI call自体が消えるのではなく、large screenであらゆるウィンドウサイズへ変更可能とする条件下では、最終的な画面の向きの制約として採用されなくなる。
- `getRequestedOrientation()`はAOSP上では要求値を返す経路が残るため、公式文書の「ignored」は戻り値の単純no-opではなく、large screen layout policy上の制約無視として解釈するのが妥当。
- `PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY` は hidden property であり、public `current.txt` の新規一般 API ではない。

## Hypotheses

- OEM device config や user aspect ratio settings により、同じ Android 16 / targetSdkVersion 36 でも個別端末の表示が変わる可能性がある。
- Android 15 / targetSdkVersion 36 は、compat change 準備コードの存在だけでは Android 16 large screen behavior と同一とは言えない。実機で target 36 アプリを install / run できる環境があれば追加確認が必要。
- API 37 で opt-out が無効化される実装 gate は Android 16 r4 scope では確認対象外で、Android 17 以降の tag で別途確認する必要がある。

## Conclusions

- 本件は `TARGET_SDK_36_CONDITIONAL`。ただし targetSdkVersion 36 だけでなく、Android 16 以上、large screen `sw >= 600dp`、game ではないこと、temporary opt-out なし、user aspect ratio exception なしという追加条件がある。
- Android 16 へ OS アップデートしただけの targetSdkVersion 35 以下アプリに、本 Behavior Change を既定適用として説明しない。
- 顧客対応では、targetSdkVersion 36 化時の large screen regression risk として、orientation lock、non-resizable、aspect ratio、pillarboxing 前提を棚卸しする。
- temporary opt-out は移行期間の回避策であり、最終対応は adaptive layout 化と large screen / multi-window / desktop windowing テストである。

---

# 推奨対応候補（Recommended Action Candidates）

- 固定方向を前提にせず、window boundsとsize classに応じてlayoutを切り替える。
- fixed aspect ratio の canvas / media / preview 領域は、content aspect ratio と container aspect ratio を分離し、余白や crop policy を明示する。
- `resizeableActivity=false` と aspect ratio manifest 指定に依存した互換表示をやめ、multi-window / split screen / desktop windowing を通常の表示状態として扱う。
- `setRequestedOrientation()` による UI 制御を見直し、必要なら component 単位の layout adaptation と state restoration に置き換える。
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

---

## 再検証記録（2026-08-22）

### 調査日（Investigation Date）

- 2026-08-22

### 公式ドキュメント再確認（Original Documentation Recheck）

- Android 16 の all-apps / target Behavior Change ページを再取得し、このレポートが参照する公式 section の掲載と適用範囲を再確認した。
- 公式ページの最終更新表示: all-apps: 2026-08-14 UTC / target: 2026-08-17 UTC。
- Android 16 compat framework 一覧も 2026-08-22 に再取得した。
- 既存の引用は短い要約として扱い、適用条件は公式ページ種別と AOSP gate の両方で再評価した。

### AOSP 証拠ワークスペース（AOSP Evidence Workspaces）

| AOSP project | Official remote URL | Checkout path | Working tree | From tag / resolved commit | To tag / resolved commit | Comparison command | Dirty risk / limitations |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `platform/frameworks/base` | `https://android.googlesource.com/platform/frameworks/base` | `frameworks-base/` | Clean | `android-15.0.0_r36` / `396d32905ded85c082232bc510b525c9e372e585` | `android-16.0.0_r4` / `45034f0663f960d9ee5fb0a101a4732b71f6e2f4` | `git -C frameworks-base diff --no-renames --name-only android-15.0.0_r36 android-16.0.0_r4` | なし。明示タグ比較のため working tree の内容は根拠に含めない。 |

### ソース文脈・差分解釈の再確認（Source Context Reviewed / Diff Interpretation）

- 各 official remote で Android 15 / 16 の最新通常リリースタグが `android-15.0.0_r36` / `android-16.0.0_r4` のままであることを確認した。
- 上表の project-level `--name-only` 比較を再実行し、既存本文の path / symbol 別 source context、gate、追加・削除・条件変更・既定値変更・差分なしの解釈を再確認した。
- タグと解決済み commit が既存調査の比較対象から変わっていないため、本文の evidence record を別タグへ機械的に置換していない。
- 実機 Observed は新規実施していない。既存の「未実施」「未確認」および不足根拠はそのまま維持した。

### 事実（Facts）

- `android-15.0.0_r36` と `android-16.0.0_r4` は 2026-08-22 時点の最新通常リリースタグである。
- 上表に再検証時の working tree 状態を記録し、official remote、両タグ、解決済み commit を確認した。展開中または dirty の working tree は根拠に使用していない。
- 公式 section と AOSP evidence の比較 pair は一致している。

### 観察（Observations）

- 最新タグが変わっていないため、今回の再検証で既存の source diff 解釈を変更する新しい AOSP tag evidence は生じなかった。
- report 内に残る Medium / Low confidence、OEM / Mainline / QPR 条件、未確認の module enforcement は解消したものとして扱わない。

### 仮説（Hypotheses）

- 新しい仮説は追加しない。既存本文で仮説または可能性として記載した事項は、実機・製品 build・未確認 module の evidence が得られるまで事実へ昇格しない。

### 結論（Conclusions）

- 既存本文の主分類、confidence、対応候補を維持する。既存の不足根拠がある場合はその制約も維持する。
- 全件再検証の横断記録は [`android16/analysis/REVALIDATION_2026-08-22.md`](../../../analysis/REVALIDATION_2026-08-22.md) を参照する。

### Human Decision

- この再検証では最終 priority、severity、release readiness、顧客説明優先度を変更していない。
- 人間の判断は [Android 16 Decision Log](../../../decisions/DECISION_LOG.md) を正とする。

## 追補確認（2026-08-23）

- Android 16 Behavior Change と Support multi-window mode の公式文書を再確認し、desktop windowing が multi-window の一形態であることを適用条件へ明記した。
- `sw >= 600dp` は現在のアプリウィンドウ幅ではなく表示先ディスプレイの `smallestScreenWidthDp` 判定であることを明記した。
- latest standard AOSP tag pair は `android-15.0.0_r36` / `android-16.0.0_r4` のままで、主分類、confidence、AOSP差分解釈、Human Decision は変更していない。
