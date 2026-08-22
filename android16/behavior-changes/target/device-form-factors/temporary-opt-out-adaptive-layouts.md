# Temporary opt-out 調査レポート

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
- https://developer.android.com/about/versions/16/behavior-changes-16#temporary-opt-out

Section:
- Opt out temporarily

Parent section:
- Adaptive layouts

Category:
- Device form factors

### 分類スナップショット（Classification Snapshot）

主分類（Primary classification）:
- `TARGET_SDK_36_CONDITIONAL`

補足:
- この項目は Adaptive layouts の base behavior そのものではなく、base behavior を一時的に抑止する opt-out mechanism を扱う。
- 依頼時の初期仮説は `TARGET_SDK_36_CONDITIONAL_WITH_TEMPORARY_OPT_OUT` だが、`android16/behavior-changes/APPLICABILITY_CLASSIFICATION.md` の既定 label としては `TARGET_SDK_36_CONDITIONAL` を使い、temporary opt-out を追加条件として本文で明示する。

早見表（At-a-glance impact）:

| 確認項目 | 回答 | 根拠 |
| --- | --- | --- |
| Android 16 へ OS アップデートしただけで targetSdkVersion 35 以下の全アプリに適用されるか | No | base behavior は `UNIVERSAL_RESIZABLE_BY_DEFAULT` / targetSdkVersion 36 gate が前提 |
| targetSdkVersion 36 以上が必要か | Yes | AOSP `ActivityInfo.UNIVERSAL_RESIZABLE_BY_DEFAULT` / 357141415 は `@EnabledAfter(VANILLA_ICE_CREAM)` |
| `sw >= 600dp` が必要か | Yes | Android 16 の `DisplayContent#getIgnoreOrientationRequest()` は large screen gate を持つ |
| Application-level opt-out はあるか | Yes | `AppCompatResizeOverrides` が package-level `getPropertyAsUser(..., className=null)` を先に読む |
| Activity-level opt-out はあるか | Yes | package-level が true でない場合に activity component の property を読む |
| Application-level opt-out は全 activity に効くか | Yes | activity ごとの判定前に package-level property が true なら true を返す |
| Activity-level opt-out は該当 activity に限定されるか | Yes | `mActivityComponent` の package / className で property を読む |
| opt-out false / 未指定 | base behavior を抑止しない | property default は false。`NameNotFoundException` 時も false |
| API 37 以降の扱い | Temporary | 公式文書は API 37 target では無効と説明し、AOSP に SDK 37 removal TODO がある |
| Public API surface | Public current では確認できない | `PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY` は `current.txt` / `test-current.txt` などに出ない hidden property |

### 調査日（Investigation Date）

2026-07-03

### 信頼度（Confidence）

- High

理由:
- 公式文書、公式compat framework changes、AOSP ChangeId、targetSdkVersion gate、large screen gate、property定義、application / activity property lookup、あらゆるウィンドウサイズへ変更可能とする判定の抑止経路、API 37 removal TODOが一致している。
- `PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY` は API reference page では検索できず、AOSP でも `@hide` として定義されているため、公開 API 定数として利用するのではなく manifest property name 文字列として扱う必要がある。

### 適用条件分類（Applicability Classification）

適用される条件（Applies when）:
- [ ] OS update / all apps on Android 16 regardless of targetSdkVersion
- [ ] targetSdkVersion >= 36 on Android 16+
- [x] targetSdkVersion >= 36, with additional runtime conditions
- [ ] Mainline / Google Play system update dependent
- [ ] API addition only, not a behavior change
- [ ] Unknown / needs more evidence

Base behavior が適用される条件（Base behavior applies when）:
- Android version: Android 16 以上。
- targetSdkVersion: 36 以上。
- Device/form factor: display `smallestScreenWidthDp >= 600`。
- App category: `ApplicationInfo.CATEGORY_GAME` ではない。
- User setting: user aspect ratio settings で app default behavior を明示選択していない。
- Opt-out: `android.window.PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY=true` が application / activity に指定されていない。

Temporary opt-out が意味を持つ条件:
- base behavior が適用される条件を満たしている。
- application または activity の manifest `<property>` で `android:name="android.window.PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY"` / `android:value="true"` を指定している。

Compat framework:
- Change ID: 357141415
- Change name: `UNIVERSAL_RESIZABLE_BY_DEFAULT`
- Default state: 公式 compat page では Android 16 / API level 36 以上を target するアプリで enabled。
- AOSP annotation: `@EnabledAfter(targetSdkVersion = Build.VERSION_CODES.VANILLA_ICE_CREAM)`。
- Force-enable / force-disable: `@Overridable`。公式文書は app compatibility framework で `UNIVERSAL_RESIZABLE_BY_DEFAULT` を enabled にしてテスト可能と説明している。

---

# エグゼクティブサマリー（Executive Summary）

Android 16 の `Opt out temporarily` 節は、Adaptive layouts の base behavior、つまり large screen で orientation / resizability / aspect ratio restrictions を無視する挙動を、一時的に application level または activity level で抑止する方法を説明している。

AOSP evidenceでは、`PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY`は`WindowManager`にhidden propertyとして定義され、`AppCompatResizeOverrides`が`PackageManager#getPropertyAsUser()`でapplication-level propertyを先に確認し、trueでなければactivity-level propertyを確認する。どちらかがtrueの場合、`ActivityRecord#isUniversalResizeable()`がfalseになり、base behaviorの「あらゆるウィンドウサイズへ変更可能とする処理経路」から外れる。

この opt-out は Android 16 の移行猶予であり、公式文書は API level 37 target では適用されないと説明している。AOSP にも `TODO(b/357141415): Remove this from sdk 37` がある。顧客向けには、OS アップデートだけの影響、targetSdkVersion 36 化による base behavior、temporary opt-out の効果を分けて説明する。

---

# 公式ドキュメント確認（Original Documentation）

## 原文（Statement）

検証対象 statement:

```text
If needed, you can temporarily opt out at either the application level or the activity level.
```

```text
To opt out, set the PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY property to true in your app manifest.
```

```text
Support for this property will be removed in the next Android release.
```

```text
When you add the property at the application level, all activities are opted out.
```

```text
To opt out at the application level, add the property in the <application> tag.
```

```text
To opt out at the activity level, add the property in the <activity> tag.
```

## 最新本文との差分（Documentation drift）

調査開始時に公式 URL の `#temporary-opt-out` 相当箇所を再確認した。確認時点の公式本文では見出しは `Opt out temporarily` で、内容は以下だった。

- specific activity を opt out するには `<activity>` に `PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY` property を宣言する。
- app の多くが Android 16 に未対応の場合は `<application>` に同じ property を適用して opt out completely できる。
- opt-out は temporary であり、future Android release で API level 37 を target すると適用されない。

依頼文の「Support for this property will be removed in the next Android release」は、現行公式本文では「targeting API level 37 in a future Android release」と表現されている。実質的には同じ方向性だが、report では API 37 target 条件として記録する。

## 解釈（Interpretation）

この節は base behavior の説明ではなく、Android 16 / targetSdkVersion 36 / `sw >= 600dp` で base behavior が適用される場合に、それを一時的に抑止する manifest property を説明している。opt-out は「large screen 対応不要」の宣言ではなく、API 37 以降に向けた移行猶予である。

---

# 変更内容（What Changed）

- Android 16のadaptive layouts base behaviorは`UNIVERSAL_RESIZABLE_BY_DEFAULT`により、large screenで固定方向・アスペクト比・サイズ変更可否の制約を無視する。
- `PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY=true`をapplicationまたはactivityに指定すると、AOSPの`ActivityRecord#isUniversalResizeable()`がfalseになり、base behaviorの「あらゆるウィンドウサイズへ変更可能とする処理経路」から外れる。
- application-level property は package-level lookup で先に判定されるため、true なら全 activity に効く。
- activity-level property は specific activity component の property として読まれるため、該当 activity に限定される。
- `android:value="false"` または未指定では opt-out にならない。
- AOSP では property に `@hide` と SDK 37 removal TODO が付いている。公式文書も API 37 target では opt-out が効かないと説明している。

---

# 適用条件（Applicability）

## OS アップデート時の挙動（OS Update Behavior）

- Android 16 に OS アップデートしただけで targetSdkVersion 35 以下の全アプリに base behavior が既定適用されるか: No。
- Android 16 / targetSdkVersion 35: `UNIVERSAL_RESIZABLE_BY_DEFAULT` は default enabled ではないため、targetSdkVersion 36 起因の base behavior は既定適用されない。
- このため targetSdkVersion 35 アプリでは temporary opt-out property を指定しても、抑止対象となる targetSdkVersion 36 base behavior がそもそも既定では発生しない。

## targetSdkVersion 36 以上での挙動（targetSdkVersion 36 Behavior）

- Android 16 / targetSdkVersion 36 / `sw >= 600dp` / non-game / user exception なし / opt-out なしでは、base behavior が適用される。
- application-level opt-out trueでは、packageの全activityが、あらゆるウィンドウサイズへ変更可能とする処理経路から外れる。
- activity-level opt-out trueでは、該当activityのみが、あらゆるウィンドウサイズへ変更可能とする処理経路から外れる。
- application-level true と activity-level true が混在しても、application-level true の時点で true を返すため、全 activity が opt-out される。
- application-level false と activity-level true の場合、application-level は抑止せず、該当 activity の activity-level true が効く。
- activity-level false は opt-out にならない。application-level true がある場合、activity-level false で再度 opt-in する経路は確認できない。

## Android 15 / targetSdkVersion 36

- `android-15.0.0_r36` にも `PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY` と `ActivityRecord#isUniversalResizeable()` の準備コードは存在する。
- ただし`android-16.0.0_r4`では`DisplayContent#getIgnoreOrientationRequest()`に「large screenでは既定で画面の向きの要求を無視する」分岐が追加されている。Android 15 tagには同等のdefault large screen分岐は確認できなかった。
- よって Android 15 / targetSdkVersion 36 で opt-out property を指定しても、Android 16 の公式 Behavior Change と同一の抑止効果とは結論しない。検証可能な環境があれば Android 16 / targetSdkVersion 36 と比較する。

## Game / user aspect ratio setting / `sw < 600dp`

- game、user aspect ratio setting exception、`sw < 600dp` は base behavior 自体から外れる条件である。
- これらの条件ではtemporary opt-out propertyの有無にかかわらず、base behaviorの「あらゆるウィンドウサイズへ変更可能とする処理経路」に入らない可能性が高い。
- ただし端末固有 DeviceConfig や user setting は別条件として確認する。

---

# AOSP 調査（AOSP Investigation）

## 関連ファイル（Related Files）

- `core/java/android/content/pm/ActivityInfo.java`
- `core/java/android/view/WindowManager.java`
- `core/java/android/content/pm/PackageManager.java`
- `core/java/android/content/pm/IPackageManager.aidl`
- `services/core/java/com/android/server/wm/DisplayContent.java`
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
| `DisplayContent#getIgnoreOrientationRequest()` | large screen default ignore分岐なし | `isLargeScreen()`なら画面の向きの要求を既定で無視 | base behaviorのAndroid 16差分 |
| `DisplayContent#isLargeScreen()` / `WindowManager.LARGE_SCREEN_SMALLEST_SCREEN_WIDTH_DP` | threshold は 600 | threshold は 600 | `sw >= 600dp` 判定 |
| `WindowManager.PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY` | hidden property として存在 | hidden property として存在、SDK 37 removal TODO あり | opt-out property 定義 |
| `AppCompatResizeOverrides` constructor | application-level -> activity-level の順で property を読む | 同じ | scope と優先順位 |
| `PackageManager#getPropertyAsUser()` | property 取得 API が存在 | 同じ | manifest property が PackageManager property として参照される根拠 |
| `ActivityRecord#isUniversalResizeable()` | `allowRestrictedResizability()` が true なら false | 同じ | opt-out が base behavior を抑止する根拠 |
| `ActivityRecord#isResizeable()` | `isUniversalResizeable()` を含む | 同じ | opt-out true で `resizeableActivity=false` が従来 policy に戻る根拠 |
| `AppCompatAspectRatioPolicy#getMinAspectRatio()` / `getMaxAspectRatio()` | あらゆるウィンドウサイズへ変更可能と判定された場合は0 | 同じ | opt-out trueでmin/max aspect ratioが従来policyに戻る根拠 |
| `ActivityRecord#getOverrideOrientation()` | あらゆるウィンドウサイズへ変更可能とする処理経路に接続 | 同じ | opt-out trueで固定方向を無視する処理経路から外れる根拠 |
| `core/api/current.txt` / `test-current.txt` | property は public current / test-current に出ない | 同じ | property は公開 API 定数ではなく hidden manifest property |

必須記入項目（Required context）:
- Entry point / caller: manifest `<property>` -> PackageManager property -> `AppCompatResizeOverrides#allowRestrictedResizability()` -> `ActivityRecord#isUniversalResizeable()`。
- Relevant class or service responsibility: WindowManager / ActivityTaskManager は activity の orientation、window bounds、resizeability、size compat、aspect ratio policy、letterbox / compatibility mode を解決する。
- Baseline Android behavior: Android 15 tag では Android 16 の large screen default ignore 分岐は確認できない。
- Target Android behavior: Android 16 tagではtargetSdkVersion 36 compat changeとlarge screen gateにより、あらゆるウィンドウサイズへ変更可能とする処理経路が既定有効になる。temporary opt-out trueはその処理経路を抑止する。
- Diff kind: changed condition / changed default。Android 16 tag の `DisplayContent#getIgnoreOrientationRequest()` が large screen default true を返す条件を追加している。
- Classification support: targetSdkVersion 36 gate と runtime condition / opt-out があるため `TARGET_SDK_36_CONDITIONAL`。
- Unrelated or excluded paths: UI state loss、stretched layout、off-screen animation は `Common breaking changes` の影響説明であり、本 report では opt-out mechanism の直接証跡としては扱わない。

## Base behavior の実装根拠

`ActivityInfo.UNIVERSAL_RESIZABLE_BY_DEFAULT`:

```text
@ChangeId
@Overridable
@TestApi
@EnabledAfter(targetSdkVersion = Build.VERSION_CODES.VANILLA_ICE_CREAM)
public static final long UNIVERSAL_RESIZABLE_BY_DEFAULT = 357141415L;
```

Android 16 の `DisplayContent#getIgnoreOrientationRequest()`:

```text
boolean isLargeScreen() {
    return getConfiguration().smallestScreenWidthDp
            >= WindowManager.LARGE_SCREEN_SMALLEST_SCREEN_WIDTH_DP;
}

boolean getIgnoreOrientationRequest() {
    if (mHasSetIgnoreOrientationRequest
            || !Flags.universalResizableByDefault()) {
        return super.getIgnoreOrientationRequest();
    }
    return isLargeScreen() && !mWmService.isIgnoreOrientationRequestDisabled();
}
```

`WindowManager.LARGE_SCREEN_SMALLEST_SCREEN_WIDTH_DP` は 600。したがって temporary opt-out が実質的に意味を持つのは、base behavior が適用され得る `sw >= 600dp` である。

## opt-out property の定義

`WindowManager.PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY`:

```text
Application or Activity level PackageManager.Property that specifies whether this package or activity
can declare or request fixed orientation, max/min aspect ratio, unresizable on large screen devices
with the ignore orientation request display setting enabled since Android 16 (API level 36) or higher.

The default value is false.
```

property 文字列:

```text
android.window.PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY
```

AOSP comment:

```text
TODO(b/357141415): Remove this from sdk 37
```

解釈:
- property は application または activity level の `PackageManager.Property` として定義される。
- default false なので未指定または false では opt-out にならない。
- `@hide` であり、public API surface には出ていない。manifest には文字列名で指定する。

## Application-level / Activity-level の判定経路

`AppCompatResizeOverrides` は application-level を先に読む。

```text
if (allowRestrictedResizability(packageManager, mActivityRecord.packageName,
        mActivityRecord.mUserId)) {
    return true;
}
```

application-level lookup:

```text
pm.getPropertyAsUser(PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY, packageName,
        null /* className */, userId).getBoolean();
```

activity-level lookup:

```text
packageManager.getPropertyAsUser(
        PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY,
        mActivityRecord.mActivityComponent.getPackageName(),
        mActivityRecord.mActivityComponent.getClassName(),
        mActivityRecord.mUserId).getBoolean();
```

解釈:
- application-level true は `className=null` の package property として読まれ、各 activity の判定で先に true を返すため、全 activity に効く。
- application-level が true でない場合だけ、specific activity component の property を読む。
- activity-level opt-out はその activity component に限定される。
- property が存在しない場合は `NameNotFoundException` を catch して false。

## opt-out true が抑止する挙動

`ActivityRecord#isUniversalResizeable()`:

```text
if (mAppCompatController.getResizeOverrides().allowRestrictedResizability()) {
    return false;
}
```

このためopt-out trueは`isUniversalResizeable()`をfalseにする。結果として、base behaviorで無視されるはずだった制約が「あらゆるウィンドウサイズへ変更可能とする処理経路」から外れる。

| 制約 / API | opt-out なし | opt-out true |
| --- | --- | --- |
| `screenOrientation` / 固定方向 | large screenで最終的な制約として採用されない | あらゆるウィンドウサイズへ変更可能とする処理経路から外れ、従来policyに戻る可能性 |
| `Activity#setRequestedOrientation()` | 要求した画面の向きが最終的な制約として採用されない | 従来policy / device policyに従う可能性 |
| `Activity#getRequestedOrientation()` | 要求値と、システムが実際に採用した画面の向き・アプリに割り当てられたウィンドウ領域が乖離し得る | 要求値と最終的な制約が近くなる可能性。ただし戻り値だけで判断しない |
| `resizeableActivity=false` | `isResizeable()` が `isUniversalResizeable()` を含むため non-resizable 前提が崩れる | `isUniversalResizeable()` が false になり、manifest の resize mode が残る |
| `minAspectRatio` / `maxAspectRatio` | aspect ratio policy が 0 扱いになり制限として効かない | `isUniversalResizeable()` false により manifest ratio が評価される |
| Pillarboxing / compatibility mode | 公式文書上 pillarboxing は使われず full display window を満たす | 公式文書上 previous behavior / compatibility mode に戻る |

`AppCompatAspectRatioPolicy#getMinAspectRatio()` / `getMaxAspectRatio()`:

```text
if (minAspectRatio == 0 || mActivityRecord.isUniversalResizeable()) {
    return 0;
}
```

```text
if (maxAspectRatio == 0 || mActivityRecord.isUniversalResizeable()) {
    return 0;
}
```

opt-out true で `isUniversalResizeable()` が false になると、manifest の min/max aspect ratio が 0 でない場合は再び評価される。

## API 37 / next Android release の扱い

公式文書:
- opt-out は temporary。
- future Android release で API level 37 を target すると適用されない。
- API level 37 target では `sw600dp` 以上の display で orientation / resizability / aspect ratio restrictions が無視される。

AOSP:
- `WindowManager.PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY` に `TODO(b/357141415): Remove this from sdk 37` がある。

解釈:
- Android 16 / API 36 target の移行猶予として使える。
- API 37 以降を見据えると恒久対応ではない。
- Android 16 r4 の code では API 37 無効化 gate そのものより、removal TODO と公式文書が evidence になる。

## API surface

- `PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY` は `core/api/current.txt`、`core/api/test-current.txt`、`core/api/system-current.txt`、`core/api/module-lib-current.txt`、`core/api/system-server-current.txt` に出現しなかった。
- `UNIVERSAL_RESIZABLE_BY_DEFAULT` は `core/api/test-current.txt` に出現する。
- したがって opt-out property は public SDK constant として参照するものではなく、manifest property name 文字列として指定する。

---

# 期待挙動マトリクス（Expected Behavior Matrix）

## OS / targetSdkVersion Matrix

| シナリオ | 期待挙動 | 根拠 / 注意 |
| --- | --- | --- |
| Android 16 / targetSdkVersion 35 | targetSdkVersion 36 起因の base behavior は既定適用対象外 | compat change default は API 36 target 以上 |
| Android 16 / targetSdkVersion 36 | 条件が揃えば base behavior 適用。opt-out true で抑止 | `UNIVERSAL_RESIZABLE_BY_DEFAULT` + runtime gates |
| Android 15 / targetSdkVersion 36 | Android 16 の large screen default ignore と同一とは結論しない | Android 16 tag で `DisplayContent#getIgnoreOrientationRequest()` に差分 |

## Opt-out Matrix

| シナリオ | 期待挙動 / 確認点 |
| --- | --- |
| Android 16 / targetSdkVersion 36 / `sw >= 600dp` / no opt-out | orientation / resizability / aspect ratio restrictions は無視 |
| Android 16 / targetSdkVersion 36 / `sw >= 600dp` / Application-level opt-out | 全activityが、あらゆるウィンドウサイズへ変更可能とする処理経路から外れる |
| Android 16 / targetSdkVersion 36 / `sw >= 600dp` / Activity-level opt-out | 該当activityのみが、あらゆるウィンドウサイズへ変更可能とする処理経路から外れる |
| Android 16 / targetSdkVersion 36 / `sw >= 600dp` / both Application-level and Activity-level opt-out | application-level true により全 activity opt-out |
| Android 16 / targetSdkVersion 36 / `sw >= 600dp` / opt-out false | opt-out なしと同等 |
| Android 16 / targetSdkVersion 36 / `sw < 600dp` | large screen gate を満たさないため base behavior 対象外 |
| Android 16 / targetSdkVersion 36 / game app | `ApplicationInfo.CATEGORY_GAME` により base behavior 対象外 |
| Android 16 / targetSdkVersion 36 / user aspect ratio setting exception | user preference により base behavior から外れる |
| Android 16 / targetSdkVersion 36 / full-screen | opt-out なしなら base behavior、opt-out true なら previous behavior / compatibility mode 側 |
| Android 16 / targetSdkVersion 36 / multi-window | opt-out なしなら base behavior、opt-out true なら previous behavior / compatibility mode 側 |

---

# 影響対象（Affected App Categories）

## temporary opt-out を検討しているアプリ

- Android 16 / targetSdkVersion 36 / large screenで固定方向・サイズ変更不可・アスペクト比を前提とするUIが崩れる場合に、一時的な回避策として検討できる。
- API 37 以降は使えない前提で、恒久対応は adaptive layout 化である。

## Application-level opt-out を指定するアプリ

- package の全 activity が opt-out される。
- large screen 対応済み activity と未対応 activity が混在する場合、全体 opt-out は対応済み activity にも previous behavior を適用するため、activity-level opt-out との使い分けを検討する。

## Activity-level opt-out を指定するアプリ

- 該当 activity に限定して opt-out できる。
- mixed opt-out strategy では、未対応 activity だけを opt-out し、対応済み activity は base behavior に乗せる設計が可能。

## mixed opt-out strategy を使うアプリ

- application-level true があると全 activity に効くため、activity-level false で個別に opt-in する設計は AOSP evidence 上確認できない。
- mixed strategy では application-level を未指定または false にし、必要な activity だけ true にするのが実装経路に合う。

## 固定方向 / aspect ratio / compatibility modeに依存するアプリ

- opt-out true で previous behavior / compatibility mode に戻せる可能性がある。
- ただし temporary であり、API 37 以降に向けて fixed assumption を解消する必要がある。

## games

- game は `ApplicationInfo.CATEGORY_GAME` により base behavior から外れるため、temporary opt-out 以前に exception として扱われる。
- game だが `appCategory` が未設定の app は category 確認が必要。

## Compose UI アプリと View UI アプリ

- Platform windowing policy の変更であり、Compose / View のどちらにも影響し得る。
- opt-out は UI toolkit ではなく activity / application manifest property による platform policy 抑止である。

---

# テスト観点（Test Considerations）

必須比較:
- Android 15 端末上の targetSdkVersion 35。
- Android 16 端末上の targetSdkVersion 35。
- Android 16 端末上の targetSdkVersion 36。
- Android 15 端末上の targetSdkVersion 36 が検証可能な場合の比較。

opt-out 条件:
- `sw >= 600dp` と `sw < 600dp`。
- opt-out property 未指定。
- opt-out property `android:value="true"`。
- opt-out property `android:value="false"`。
- Application-level opt-out。
- Activity-level opt-out。
- Application-level と Activity-level の混在。

制約別:
- `screenOrientation` / `setRequestedOrientation()` / `getRequestedOrientation()` の opt-out 有無による差。
- `resizeableActivity=false` 指定あり / なし。
- `minAspectRatio` / `maxAspectRatio` 指定あり / なし。
- full-screen と multi-window。
- pillarboxing / compatibility mode の有無。
- game app category。
- user aspect ratio settings。
- visual regression / screenshot testing。

確認方法の候補:
- `<application>` に property true を指定し、複数 activity で同じ抑止が起きるか確認する。
- `<activity>` に property true を指定し、指定 activity と未指定 activity で挙動差を確認する。
- property false と未指定を比較し、base behavior が抑止されないことを確認する。
- `adb shell am compat enable UNIVERSAL_RESIZABLE_BY_DEFAULT <package>` / `disable` で compat change を切り替える。
- `dumpsys window` / `dumpsys package`で要求した画面の向き、bounds、letterbox / compatibility mode関連state、manifest propertyを確認する。

---

# Facts / Observations / Hypotheses / Conclusions

## Facts

- 公式 `Opt out temporarily` section は activity-level と application-level の property 指定例を示している。
- 公式文書は API level 37 target では opt-out が適用されないと説明している。
- `UNIVERSAL_RESIZABLE_BY_DEFAULT` / 357141415 は `@EnabledAfter(VANILLA_ICE_CREAM)` の compat change である。
- `PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY` は `WindowManager` に `@hide` property として定義される。
- `AppCompatResizeOverrides` は application-level property を先に読み、true でなければ activity-level property を読む。
- `ActivityRecord#isUniversalResizeable()` は `allowRestrictedResizability()` が true なら false を返す。
- property default は false。未指定の場合は false として扱われる。

## Observations

- 現行公式本文の見出しは `Temporary opt-out` ではなく `Opt out temporarily`。
- 依頼文の「next Android release」は、公式本文では「future Android release で API level 37 target」として表現される。
- `PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY` は Android Developers の `WindowManager` API reference では検索できず、AOSP public API surface にも出ていない。
- opt-out は manifest property name 文字列として使う mechanism であり、SDK constant 参照を前提にしない。

## Hypotheses

- application-level true と activity-level false を混在させても、application-level true が先に true を返すため、activity-level false で個別 opt-in することはできない。
- activity-level true だけを使うことで、未対応 activity だけを temporary opt-out し、対応済み activity は Android 16 base behavior に乗せられる。
- opt-out true で previous behavior / compatibility mode に戻るが、端末固有 DeviceConfig や user aspect ratio settings により見え方は変わり得る。

## Conclusions

- 本項目の主分類は `TARGET_SDK_36_CONDITIONAL`。ただし Android 16 以上、targetSdkVersion 36 以上、`sw >= 600dp`、non-game、user exception なしという base behavior 条件の上で、temporary opt-out が抑止条件として働く。
- application-level opt-out は全 activity、activity-level opt-out は該当 activity に効くという公式 statement は AOSP evidence と整合する。
- opt-out true は `isUniversalResizeable()` を false にし、orientation / resizability / aspect ratio restrictions を無視する base behavior を抑止する。
- API 37 以降の恒久対策ではないため、顧客向けには移行猶予として説明する。

---

# 推奨対応候補（Recommended Action Candidates）

- targetSdkVersion 36 化前に、large screen で崩れる activity を特定し、temporary opt-out の必要範囲を application-level ではなく activity-level から検討する。
- application-level opt-out は全 activity に効くため、対応済み activity まで previous behavior に戻す影響を評価する。
- property false は opt-out にならないため、manifest merge 後の final manifest を確認する。
- API 37 以降を見据え、adaptive layout、window size class、state preservation、multi-window / desktop windowing 対応を進める。
- opt-out 適用時も visual regression / screenshot testing で pillarboxing、compatibility mode、bounds、activity recreation を確認する。

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
