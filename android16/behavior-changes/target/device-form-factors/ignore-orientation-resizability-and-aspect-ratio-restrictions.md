# Ignore orientation, resizability, and aspect ratio restrictions 調査レポート

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

2026-07-03

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
- App category: `ApplicationInfo.CATEGORY_GAME` ではない。
- User setting: user aspect ratio setting が app default / 非 resizable と互換な例外状態ではない。
- Opt-out: `android.window.PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY=true` が application / activity に指定されていない。
- App behavior: fixed orientation、non-resizable、min/max aspect ratio、pillarboxing、preferred orientation、固定 aspect ratio 前提に依存している場合に顕在化しやすい。

Compat framework:
- Change ID: 357141415
- Change name: `UNIVERSAL_RESIZABLE_BY_DEFAULT`
- Default state: 公式 compat page では Android 16 / API level 36 以上を target するアプリで enabled。
- AOSP annotation: `@EnabledAfter(targetSdkVersion = Build.VERSION_CODES.VANILLA_ICE_CREAM)`。Android 15 は API 35 なので、実質 targetSdkVersion 36 以上で default enabled と読む。
- Force-enable / force-disable: `@Overridable`。公式文書は app compatibility framework で `UNIVERSAL_RESIZABLE_BY_DEFAULT` を enabled にしてテスト可能と説明している。

---

# エグゼクティブサマリー（Executive Summary）

Android 16 では、targetSdkVersion 36 以上のアプリが `sw >= 600dp` の display で実行される場合、fixed orientation、non-resizable、min/max aspect ratio などの制約が既定で無視される。アプリは aspect ratio や preferred orientation に関係なく display window 全体を使い、従来の pillarboxing / compatibility mode を前提にできない。

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

---

# 変更内容（What Changed）

- Android 16 tag では、明示 override がなく `universal_resizable_by_default` flag が有効な場合、`DisplayContent#getIgnoreOrientationRequest()` が large screen（`sw >= 600dp`）で true を返す経路が追加された。
- `ActivityRecord#isUniversalResizeable()` は large screen かつ display が orientation request を無視する場合に、`UNIVERSAL_RESIZABLE_BY_DEFAULT` compat change、game exception、temporary opt-out、user aspect ratio setting を評価する。
- universal resizable と判定された activity は `isResizeable()` が true になり、`resizeableActivity=false` 相当の非 resizable 制約が実質的に効かない。
- `ActivityRecord#getOverrideOrientation()` は restricted fixed orientation を `SCREEN_ORIENTATION_UNSPECIFIED` に置き換えるため、manifest / runtime fixed orientation は実効 constraint として尊重されない。
- `AppCompatAspectRatioPolicy#getMinAspectRatio()` / `getMaxAspectRatio()` は、universal resizable の場合に min/max aspect ratio を 0 として扱う。
- 結果として、アプリは preferred orientation や manifest aspect ratio による bounds 制限ではなく、与えられた display window 全体に適応する必要がある。

---

# 適用条件（Applicability）

## OS アップデート時の挙動（OS Update Behavior）

- Android 16 に OS アップデートしただけで targetSdkVersion 35 以下の全アプリに適用されるか: No。
- Android 16 / targetSdkVersion 35: `UNIVERSAL_RESIZABLE_BY_DEFAULT` は default enabled ではない。従来の orientation、resizability、aspect ratio、compatibility mode / pillarboxing の扱いが残る想定。
- ただし OEM / device config の `ignore_activity_orientation_request` 系設定、ユーザー aspect ratio settings、既存 app compat override は別条件として存在するため、個別端末の挙動は device policy を確認する。

## targetSdkVersion 36 以上での挙動（targetSdkVersion 36 Behavior）

- Android 16 / targetSdkVersion 36 / `sw >= 600dp` / game ではない / opt-out なし / user exception なし: orientation、resizability、aspect ratio constraints は無視される。
- `setRequestedOrientation()` を呼んでも fixed orientation lock として効かず、large screen 上では window 全体を使う方向へ解決される。
- `getRequestedOrientation()` の戻り値と実効 orientation / window bounds は分けて考える。AOSP では requested orientation を返す経路が残るが、実効 layout constraint としては無視される。

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
- `core/api/current.txt`
- `core/api/test-current.txt`

## 確認したソース文脈（Source Context Reviewed）

| ファイル / シンボル | Android 15 baseline | Android 16 target | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| `ActivityInfo.UNIVERSAL_RESIZABLE_BY_DEFAULT` | Change ID 357141415、`@EnabledAfter(VANILLA_ICE_CREAM)` が存在 | 同じ | targetSdkVersion 36 gate と compat override の根拠 |
| `DisplayContent#getIgnoreOrientationRequest()` | large screen default ignore 分岐なし | `mHasSetIgnoreOrientationRequest` が false かつ flag enabled の場合、`isLargeScreen()` なら true | Android 16 で large screen が既定で orientation request を無視する差分 |
| `DisplayContent#isLargeScreen()` | 未確認 | `smallestScreenWidthDp >= WindowManager.LARGE_SCREEN_SMALLEST_SCREEN_WIDTH_DP` | `sw >= 600dp` 判定 |
| `WindowManager.LARGE_SCREEN_SMALLEST_SCREEN_WIDTH_DP` | 600 | 600 | large screen threshold |
| `ActivityRecord#isUniversalResizeable()` | 準備コードあり | large screen + ignore orientation + compat + opt-out + user setting を評価 | orientation / aspect ratio / resizability をまとめて無視する central gate |
| `ActivityRecord#canBeUniversalResizeable()` | `CATEGORY_GAME` を false にする | 同じ | game exception |
| `ActivityRecord#isResizeable()` | `isUniversalResizeable()` を含む | 同じ | `resizeableActivity=false` が実質無効になる経路 |
| `ActivityRecord#getOverrideOrientation()` | restricted fixed orientation を unspecified にできる | 同じ。Android 16 default large screen gate で到達しやすくなる | fixed orientation の実効無視 |
| `AppCompatAspectRatioPolicy#getMinAspectRatio()` / `getMaxAspectRatio()` | universal resizable なら 0 | 同じ。Android 16 default large screen gate で到達しやすくなる | `minAspectRatio` / `maxAspectRatio` 無効化 |
| `AppCompatResizeOverrides#allowRestrictedResizability()` | property を application / activity level で読む | 同じ | temporary opt-out |
| `WindowManager.PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY` | property 定義あり | property 定義あり、SDK 37 removal TODO あり | opt-out と future removal evidence |
| `AppCompatAspectRatioOverrides#userPreferenceCompatibleWithNonResizability()` | user aspect ratio code を評価 | 同じ | user aspect ratio setting exception |
| `core/api/current.txt` / `test-current.txt` | `UNIVERSAL_RESIZABLE_BY_DEFAULT` は public current ではなく test-current | 同じ | public API surface 上の新規一般 API ではなく compat/test API |

必須記入項目（Required context）:
- Entry point / caller: activity launch / configuration resolution、`Activity#setRequestedOrientation()` -> `ActivityClientController#setRequestedOrientation()` -> `ActivityRecord#setRequestedOrientation()`、bounds resolution -> `AppCompatAspectRatioPolicy`。
- Relevant class or service responsibility: WindowManager / ActivityTaskManager は activity の orientation、window bounds、resizeability、size compat、aspect ratio policy を解決する。
- Baseline behavior: Android 15 tag には compat change と一部準備コードはあるが、large screen で default ignore する `DisplayContent#getIgnoreOrientationRequest()` 差分はない。
- Target behavior: Android 16 tag では large screen display が既定で orientation request を無視し、それが universal resizable 判定に接続される。
- Diff kind: added behavior（large screen default ignore）、changed condition（targetSdkVersion 36 compat gate）、removed behavior（fixed orientation / non-resizable / aspect ratio 制約の実効性）。
- Excluded code paths: PiP aspect ratio、camera compat、test-only classes、desktop decoration rendering は、本 Behavior Change の主要 gate ではないため主根拠から除外した。

## 差分解釈（Diff Interpretation）

| 確認した差分 | 解釈 | Behavior Change との関係 | 信頼度 |
| --- | --- | --- | --- |
| `DisplayContent#getIgnoreOrientationRequest()` に large screen default 分岐追加 | Added behavior | Android 16 で `sw >= 600dp` が既定で orientation request を無視する根拠 | High |
| `ActivityInfo.UNIVERSAL_RESIZABLE_BY_DEFAULT` は `@EnabledAfter(VANILLA_ICE_CREAM)` | Changed condition / targetSdk gate | targetSdkVersion 36 以上が必要 | High |
| `ActivityRecord#canBeUniversalResizeable()` が `ApplicationInfo.CATEGORY_GAME` を除外 | Exception | game app 例外 | High |
| `ActivityRecord#isUniversalResizeable()` が opt-out property を確認 | Exception / opt-out | temporary opt-out で従来挙動へ戻る | High |
| `AppCompatAspectRatioPolicy` が universal resizable 時に min/max aspect ratio を 0 扱い | Removed behavior | `minAspectRatio` / `maxAspectRatio` の実効無視 | High |
| `ActivityRecord#getOverrideOrientation()` が restricted fixed orientation を unspecified に変換 | Removed behavior | manifest / runtime fixed orientation の実効無視 | High |
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
| `sw >= 600dp` / opt-out なし | fixed orientation、non-resizable、min/max aspect ratio は無視され、window 全体を使用 |
| `sw >= 600dp` / Activity-level opt-out あり | 該当 activity では restricted resizability を許可し、従来の compatibility mode 側へ戻る |
| `sw >= 600dp` / Application-level opt-out あり | package 全体で opt-out。AOSP は application level を先に評価 |
| `sw < 600dp` | large screen gate を満たさないため、本 Behavior Change の適用対象外 |
| game app | `ApplicationInfo.CATEGORY_GAME` により universal resizable 対象外 |
| user aspect ratio setting exception | user preference が非 resizable と互換な場合、universal resizable から外れる |
| multi-window | 公式文書上は large screen devices の multi-window でも constraints ignored。AOSP の resizable 判定により non-resizable 制約を避ける |
| full-screen | 公式文書上は full-screen でも constraints ignored。pillarboxing 前提ではなく window 全体を使う |

---

# 影響対象（Affected App Types）

- portrait / landscape 固定に依存するアプリ: large screen で指定 orientation が実効制約にならず、横長/縦長 window に stretch される。
- `resizeableActivity=false` に依存するアプリ: large screen で non-resizable 前提が崩れ、multi-window / desktop windowing / split screen で再レイアウトが必要になる。
- `minAspectRatio` / `maxAspectRatio` に依存するアプリ: aspect ratio による bounds 制限が効かず、固定アスペクト比 UI が崩れる可能性がある。
- pillarboxing / compatibility mode に依存するアプリ: compatibility mode に置かれる前提で余白、背景、入力領域、animation 範囲を設計している場合に差分が出る。
- `setRequestedOrientation()` を runtime に呼ぶアプリ: large screen で orientation lock として効かない。Activity recreation / state preservation の想定を見直す。
- `getRequestedOrientation()` の戻り値に依存するアプリ: requested value と実効 orientation / bounds を混同しない。
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
- `screenOrientation` / `setRequestedOrientation()` は API call 自体が消えるのではなく、large screen universal resizable 条件下で実効 orientation constraint として尊重されなくなる。
- `getRequestedOrientation()` は AOSP 上では requested value を返す経路が残るため、公式文書の「ignored」は戻り値の単純 no-op ではなく、large screen layout policy 上の制約無視として解釈するのが妥当。
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

- fixed orientation を前提にせず、window bounds と size class に応じて layout を切り替える。
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
