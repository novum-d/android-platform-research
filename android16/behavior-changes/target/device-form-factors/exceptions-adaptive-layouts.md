# Exceptions 調査レポート

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
- https://developer.android.com/about/versions/16/behavior-changes-16#exceptions

Section:
- Exceptions

Parent section:
- Adaptive layouts

Category:
- Device form factors

### 分類スナップショット（Classification Snapshot）

主分類（Primary classification）:
- `TARGET_SDK_36_CONDITIONAL`

補足:
- この項目は base behavior そのものではなく、Android 16 adaptive layouts の base behavior が適用されない例外条件を扱う。
- 依頼時の初期仮説は `TARGET_SDK_36_CONDITIONAL_WITH_EXCEPTIONS` だが、`android16/behavior-changes/APPLICABILITY_CLASSIFICATION.md` の既定 label としては `TARGET_SDK_36_CONDITIONAL` を使い、例外条件を本文で明示する。

早見表（At-a-glance impact）:

| 確認項目 | 回答 | 根拠 |
| --- | --- | --- |
| Android 16 へ OS アップデートしただけで targetSdkVersion 35 以下の全アプリに適用されるか | No | `UNIVERSAL_RESIZABLE_BY_DEFAULT` は Android 16 / API 36 以上 target で default enabled |
| targetSdkVersion 36 以上が必要か | Yes | AOSP `ActivityInfo.UNIVERSAL_RESIZABLE_BY_DEFAULT` / 357141415 は `@EnabledAfter(VANILLA_ICE_CREAM)` |
| `sw < 600dp` は例外か | Yes | `DisplayContent#isLargeScreen()` は `smallestScreenWidthDp >= 600` を要求 |
| game は例外か | Yes | `ActivityRecord#canBeUniversalResizeable()` は `ApplicationInfo.CATEGORY_GAME` なら false |
| user aspect ratio setting は例外になり得るか | Yes | `AppCompatAspectRatioOverrides` の user preference 判定が `isUniversalResizeable()` の gate |
| OEM / device config override は存在するか | Yes | `WindowManagerConstants` の DeviceConfig key と package opt-out list |
| 公式 `#exceptions` に OEM override 文言があるか | No | 再確認時点の公式 section は game / user aspect ratio setting / `sw600dp` 未満の 3 例外を列挙 |
| Temporary opt-out は別条件として存在するか | Yes | `PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY` を application / activity property として読む |

### 調査日（Investigation Date）

2026-07-03

### 信頼度（Confidence）

- High

理由:
- 公式文書、公式 compat framework changes、AOSP ChangeId、targetSdkVersion gate、large screen gate、game exception、user aspect ratio setting gate、DeviceConfig override、temporary opt-out property が一致している。
- OEM override については AOSP evidence は確認できるが、再確認時点の公式 `#exceptions` section には依頼文の OEM statement が掲載されていなかったため、公式文書 statement と AOSP/device configuration evidence を分けて扱う。

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
- OEM / device config: device 側の package opt-out / config override により base behavior から外されていない。

例外条件（Exceptions）:
- Games: `android:appCategory` 由来の `ApplicationInfo.CATEGORY_GAME`。
- User aspect ratio setting: device の aspect ratio settings で user が app default behavior を明示選択する場合。
- Small screens: `sw < 600dp`。
- OEM / device config: `WindowManagerConstants` / DeviceConfigの画面の向きの要求を無視する設定やpackage opt-out list。
- Temporary opt-out: `PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY=true`。公式文書では `Exceptions` ではなく隣接する `Opt out temporarily` 節で説明される。

Compat framework:
- Change ID: 357141415
- Change name: `UNIVERSAL_RESIZABLE_BY_DEFAULT`
- Default state: 公式 compat page では Android 16 / API level 36 以上を target するアプリで enabled。
- AOSP annotation: `@EnabledAfter(targetSdkVersion = Build.VERSION_CODES.VANILLA_ICE_CREAM)`。
- Force-enable / force-disable: `@Overridable`。公式文書は app compatibility framework で `UNIVERSAL_RESIZABLE_BY_DEFAULT` を enabled にしてテスト可能と説明している。

---

# エグゼクティブサマリー（Executive Summary）

Android 16 の `Exceptions` 節は、Adaptive layouts の base behavior、つまり large screen で orientation / resizability / aspect ratio restrictions を無視する挙動が適用されない条件を列挙している。

公式文書で確認できる例外は、game、userがdeviceのaspect ratio settingsでapp default behaviorを明示選択する場合、`sw600dp`未満のscreenの3つである。AOSP evidenceでも、gameは`ApplicationInfo.CATEGORY_GAME`、small screenは`DisplayContent#isLargeScreen()`、user settingは`AppCompatAspectRatioOverrides`を通じて、あらゆるウィンドウサイズへ変更可能とする判定に接続される。

OEM / device configuration override は再確認時点の公式 `#exceptions` section には掲載されていなかったが、AOSP には `WindowManagerConstants` の DeviceConfig key と package opt-out list が存在する。そのため顧客向け説明では、公式の 3 例外と、端末実装・DeviceConfig による追加的な分岐を混ぜずに説明する。

---

# 公式ドキュメント確認（Original Documentation）

## 原文（Statement）

検証対象 statement:

```text
The Android 16 orientation, resizability, and aspect ratio restrictions don't apply in the following situations:
```

```text
Games (based on the android:appCategory flag)
```

```text
Users explicitly opting in to the app's default behavior in aspect ratio settings of the device
```

```text
Screens that are smaller than sw600dp
```

依頼文に含まれる追加 statement:

```text
OEMs can provide overrides to the Android 16 behavior through device configurations.
```

## 最新本文との差分（Documentation drift）

調査開始時に公式 URL の `#exceptions` セクションを再確認した。確認時点の公式本文では、`Exceptions` section は以下の 3 つを列挙していた。

- Games。
- Users explicitly opting in to the app's default behavior in aspect ratio settings。
- Screens that are smaller than `sw600dp`。

依頼文の `OEMs can provide overrides to the Android 16 behavior through device configurations.` は、再確認時点の公式 `#exceptions` section では見つからなかった。AOSP には DeviceConfig override の実装証跡があるため、report では「公式 section の original statement」と「AOSP / device configuration evidence」を分けて記録する。

## 解釈（Interpretation）

この節はbase behaviorの説明ではなく、base behaviorが適用されない条件を説明する節である。base behaviorが有効な場合、Android 16 / targetSdkVersion 36 / `sw >= 600dp`で`screenOrientation`、`resizeableActivity=false`、`minAspectRatio`、`maxAspectRatio`、`setRequestedOrientation()`などが最終的な制約として採用されない。`Exceptions`は、あらゆるウィンドウサイズへ変更可能とする処理経路から外れる条件として読む。

---

# 変更内容（What Changed）

- Android 16 tagでは、`DisplayContent#getIgnoreOrientationRequest()`にlarge screen（`sw >= 600dp`）で画面の向きの要求を既定で無視する分岐が追加されている。
- `ActivityInfo.UNIVERSAL_RESIZABLE_BY_DEFAULT` / 357141415 は `@EnabledAfter(VANILLA_ICE_CREAM)` の compat change として定義され、Android 16 / targetSdkVersion 36 以上で default enabled になる。
- `ActivityRecord#canBeUniversalResizeable()` は、game、large screen、compat change、DeviceConfig、package opt-out、temporary opt-out を評価する。
- `ActivityRecord#isUniversalResizeable()` は、activity-level opt-out と user aspect ratio preference も評価する。
- 例外に該当する場合、固定方向・アスペクト比・サイズ変更可否の制約を無視して、あらゆるウィンドウサイズへ変更可能とする処理経路に入らない。その結果、従来の画面の向きの要求、サイズ変更可否、アスペクト比、pillarboxing / compatibility modeの扱いが残る、またはdevice / user policyに従う。

---

# 適用条件（Applicability）

## OS アップデート時の挙動（OS Update Behavior）

- Android 16 に OS アップデートしただけで targetSdkVersion 35 以下の全アプリに適用されるか: No。
- Android 16 / targetSdkVersion 35: `UNIVERSAL_RESIZABLE_BY_DEFAULT` は default enabled ではないため、targetSdkVersion 36 起因の base behavior は既定適用されない。
- ただしOEM / DeviceConfigによる画面の向きの要求の無視、既存のuser aspect ratio settings、端末固有のapp compat policyは別経路で存在する。これはtargetSdkVersion 36のBehavior Changeと分けて検証する必要がある。

## targetSdkVersion 36 以上での挙動（targetSdkVersion 36 Behavior）

- Android 16 / targetSdkVersion 36 / `sw >= 600dp` / non-game / user exception なし / opt-out なし / OEM package opt-out なしでは、base behavior が適用される。
- Android 16 / targetSdkVersion 36 でも、game、`sw < 600dp`、user aspect ratio setting exception、temporary opt-out、OEM / device config override に該当する場合は、base behavior が抑止される。
- base behavior が抑止される場合、`screenOrientation` / `setRequestedOrientation()`、`resizeableActivity=false`、`minAspectRatio` / `maxAspectRatio` は従来の policy に近い扱いに戻る可能性がある。ただし user setting や OEM config は端末固有のため、単純に全端末で同じ compatibility mode に戻るとは説明しない。

## Android 15 / targetSdkVersion 36

- `android-15.0.0_r36` にも `UNIVERSAL_RESIZABLE_BY_DEFAULT`、opt-out property、`ActivityRecord#isUniversalResizeable()` の準備コードは存在する。
- ただし`android-16.0.0_r4`では`DisplayContent#getIgnoreOrientationRequest()`に「large screenでは既定で画面の向きの要求を無視する」分岐が追加されている。Android 15 tagには同等のdefault large screen分岐は確認できなかった。
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
- `core/java/android/content/pm/ApplicationInfo.java`
- `core/java/android/content/pm/PackageParser.java`
- `core/java/android/view/WindowManager.java`
- `services/core/java/com/android/server/wm/DisplayContent.java`
- `services/core/java/com/android/server/wm/ActivityRecord.java`
- `services/core/java/com/android/server/wm/AppCompatAspectRatioOverrides.java`
- `services/core/java/com/android/server/wm/AppCompatResizeOverrides.java`
- `services/core/java/com/android/server/wm/WindowManagerConstants.java`
- `services/core/java/com/android/server/wm/AppCompatAspectRatioPolicy.java`
- `core/api/current.txt`
- `core/api/test-current.txt`

## 確認したソース文脈（Source Context Reviewed）

| ファイル / シンボル | Android 15 baseline | Android 16 target | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| `ActivityInfo.UNIVERSAL_RESIZABLE_BY_DEFAULT` | Change ID 357141415、`@EnabledAfter(VANILLA_ICE_CREAM)` が存在 | 同じ | targetSdkVersion 36 gate と compat override の根拠 |
| `DisplayContent#getIgnoreOrientationRequest()` | large screen default ignore分岐なし | `isLargeScreen()`なら画面の向きの要求を既定で無視 | base behaviorと`sw < 600dp`例外の根拠 |
| `DisplayContent#isLargeScreen()` / `WindowManager.LARGE_SCREEN_SMALLEST_SCREEN_WIDTH_DP` | threshold は 600 | threshold は 600 | `sw600dp` 判定 |
| `ApplicationInfo.category` / `CATEGORY_GAME` | `android:appCategory` 由来の category 定義あり | 同じ | game exception の入力値 |
| `PackageParser` / `AndroidManifestApplication_appCategory` | manifest の `appCategory` を `ApplicationInfo.category` に設定 | 同じ | `android:appCategory` から game exception へ接続する根拠 |
| `ActivityRecord#canBeUniversalResizeable()` | game、compat、DeviceConfig、package opt-outを評価 | 同じ | あらゆるウィンドウサイズへ変更可能とする処理経路から外れる条件 |
| `ActivityRecord#isUniversalResizeable()` | activity opt-out、user preference を評価 | 同じ | temporary opt-out と user setting exception |
| `AppCompatAspectRatioOverrides#userPreferenceCompatibleWithNonResizability()` | user aspect ratio setting を評価 | 同じ | user が app default behavior を選んだ場合の例外解釈 |
| `WindowManagerConstants` | DeviceConfig key と package opt-out list が存在 | 同じ | OEM / device configuration override evidence |
| `AppCompatResizeOverrides#allowRestrictedResizability()` | application / activity property を読む | 同じ | temporary opt-out evidence |
| `AppCompatAspectRatioPolicy#getMinAspectRatio()` / `getMaxAspectRatio()` | あらゆるウィンドウサイズへ変更可能と判定された場合は0 | 同じ | base behavior時にmin/max aspect ratioが無視される根拠 |
| `ActivityRecord#getOverrideOrientation()` / `isResizeable()` | あらゆるウィンドウサイズへ変更可能とする処理経路に接続 | 同じ | exception時にこの処理経路から外れることの意味 |
| `core/api/current.txt` / `test-current.txt` | `UNIVERSAL_RESIZABLE_BY_DEFAULT` は public current ではなく test-current | 同じ | public API surface 上の新規一般 API ではなく compat/test API |

必須記入項目（Required context）:
- Entry point / caller: manifest parsing -> `PackageParser` -> `ApplicationInfo.category` / `ActivityInfo`、display policy -> `DisplayContent#getIgnoreOrientationRequest()`、resize policy -> `ActivityRecord#isUniversalResizeable()` / `canBeUniversalResizeable()`。
- Relevant class or service responsibility: WindowManager / ActivityTaskManager は activity の orientation、window bounds、resizeability、size compat、aspect ratio policy、letterbox / compatibility mode を解決する。
- Baseline Android behavior: Android 15 tagではAndroid 16のlarge screen default ignore分岐は確認できない。固定方向・サイズ変更不可・アスペクト比の制約は従来のpolicyに従う。
- Target Android behavior: Android 16 tagではtargetSdkVersion 36 compat changeとlarge screen gateにより、あらゆるウィンドウサイズへ変更可能とする処理経路が既定有効になる。ただし本reportの例外条件ではその処理経路から外れる。
- Diff kind: changed condition / changed default。Android 16 tag の `DisplayContent#getIgnoreOrientationRequest()` が large screen default true を返す条件を追加している。
- Classification support: targetSdkVersion 36 gate と runtime condition / exception があるため `TARGET_SDK_36_CONDITIONAL`。
- Unrelated or excluded paths: UI state loss、stretched layout、off-screen animation は `Common breaking changes` の影響説明であり、本 report では例外 gate の証跡としては扱わない。

## Base behavior の実装根拠

`ActivityInfo.UNIVERSAL_RESIZABLE_BY_DEFAULT`:

```text
@ChangeId
@Overridable
@TestApi
@EnabledAfter(targetSdkVersion = Build.VERSION_CODES.VANILLA_ICE_CREAM)
public static final long UNIVERSAL_RESIZABLE_BY_DEFAULT = 357141415L;
```

このchange idは固定方向、アスペクト比、サイズ変更可否の制限を無視し、appがavailable areaを満たすようにするものとして定義されている。

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

`WindowManager.LARGE_SCREEN_SMALLEST_SCREEN_WIDTH_DP` は 600。したがって `sw < 600dp` は base behavior の large screen gate を満たさない。

## Game exception

`ApplicationInfo.category` は `android:appCategory` から設定される。`ApplicationInfo.CATEGORY_GAME` は game app を表す。

```text
Set from the android.R.attr#appCategory attribute in the manifest.
public @Category int category = CATEGORY_UNDEFINED;
public static final int CATEGORY_GAME = 0;
```

`PackageParser` は `AndroidManifestApplication_appCategory` を読み、`ApplicationInfo.category` に設定する。

```text
ai.category = sa.getInt(
        R.styleable.AndroidManifestApplication_appCategory,
        ApplicationInfo.CATEGORY_UNDEFINED);
```

`ActivityRecord#canBeUniversalResizeable()` は game なら即 false を返す。

```text
if (appInfo.category == ApplicationInfo.CATEGORY_GAME) {
    return false;
}
```

解釈:
- `android:appCategory="game"`が`ApplicationInfo.CATEGORY_GAME`になるappは、あらゆるウィンドウサイズへ変更可能とする処理経路に入らない。
- game だが `android:appCategory` を指定していない app は、この AOSP gate だけでは game exception として扱われない可能性がある。installer category hint など別入力もあり得るため、実機では `ApplicationInfo.category` を確認する。

## User aspect ratio setting exception

`ActivityRecord#isUniversalResizeable()` は、base gate と opt-out を通ったあと、user preference を評価する。

```text
return mAppCompatController.getAspectRatioOverrides()
        .userPreferenceCompatibleWithNonResizability();
```

`AppCompatAspectRatioOverrides` では user aspect ratio code を参照する。

```text
boolean userPreferenceCompatibleWithNonResizability() {
    final int aspectRatio = getUserMinAspectRatioOverrideCode();
    return aspectRatio == USER_MIN_ASPECT_RATIO_UNSET
            || aspectRatio == USER_MIN_ASPECT_RATIO_FULLSCREEN;
}
```

また、user min aspect ratio overrideは`USER_MIN_ASPECT_RATIO_APP_DEFAULT`やcustom ratioと区別される。公式文書の「Users explicitly opting in to the app's default behavior」は、userがapp default側を選んだ場合に、あらゆるウィンドウサイズへ変更可能とする処理経路から外れる例外として解釈できる。

解釈:
- user settingが未設定またはfullscreenの場合は、AOSPの`userPreferenceCompatibleWithNonResizability()`はtrueを返し、あらゆるウィンドウサイズへ変更可能とする処理経路を許容する。
- user が app default behavior を明示選択した場合は、この path から外れる可能性がある。実機テストでは device の aspect ratio settings の選択肢と `dumpsys` / windowing behavior を併せて確認する。

## Small screen exception

`DisplayContent#isLargeScreen()` は `smallestScreenWidthDp >= 600` を large screen とする。Android 16 の default ignore は `isLargeScreen()` が true の場合だけ有効になる。

解釈:
- `sw < 600dp` の phone / small screen では base behavior の large screen gate を満たさない。
- `screenOrientation`、`resizeableActivity=false`、`minAspectRatio` / `maxAspectRatio` の扱いは従来 policy に近い。
- ただし DeviceConfig が `all` を指定する場合など、OEM / device policy が別途影響する可能性はあるため、公式 Behavior Change の targetSdkVersion 36 gate と端末固有 policy を分離して確認する。

## OEM / device configuration override

再確認時点の公式 `#exceptions` section に OEM override 文言はなかったが、AOSP には DeviceConfig による override がある。

`WindowManagerConstants`:

```text
KEY_IGNORE_ACTIVITY_ORIENTATION_REQUEST =
        "ignore_activity_orientation_request";
KEY_IGNORE_ACTIVITY_ORIENTATION_REQUEST_SCREENS =
        "ignore_activity_orientation_request_screens";
KEY_OPT_OUT_IGNORE_ACTIVITY_ORIENTATION_REQUEST_LIST =
        "opt_out_ignore_activity_orientation_request_list";
```

```text
allScreens |= ("all".equalsIgnoreCase(whichScreens));
boolean largeScreens = allScreens || ("large".equalsIgnoreCase(whichScreens));
mIgnoreActivityOrientationRequestSmallScreen = allScreens;
mIgnoreActivityOrientationRequestLargeScreen = largeScreens;
```

```text
boolean isPackageOptOutIgnoreActivityOrientationRequest(String packageName) {
    return mOptOutIgnoreActivityOrientationRequestPackages != null
            && mOptOutIgnoreActivityOrientationRequestPackages.contains(packageName);
}
```

`ActivityRecord#canBeUniversalResizeable()` は compat change だけでなく config も評価する。

```text
final boolean configEnabled = (isLargeScreen
        ? wms.mConstants.mIgnoreActivityOrientationRequestLargeScreen
        : wms.mConstants.mIgnoreActivityOrientationRequestSmallScreen)
        && !wms.mConstants.isPackageOptOutIgnoreActivityOrientationRequest(
                appInfo.packageName);
```

解釈:
- OEM / device configuration は base behavior を強制または抑止し得る追加経路である。
- 公式 Behavior Change の「targetSdkVersion 36 で default enabled」とは別に、端末の DeviceConfig / package opt-out list により挙動が変わり得る。
- 顧客向け説明では「Android 16 / targetSdkVersion 36 の標準挙動」と「OEM / device configuration による端末差」を分ける。

## Temporary opt-out との関係

`ActivityRecord#isUniversalResizeable()` は `AppCompatResizeOverrides#allowRestrictedResizability()` が true なら false を返す。

```text
if (mAppCompatController.getResizeOverrides().allowRestrictedResizability()) {
    return false;
}
```

`AppCompatResizeOverrides` は application level property を先に確認し、true でなければ activity level property を確認する。

解釈:
- temporary opt-out は公式 `Exceptions` 節ではなく `Opt out temporarily` 節の条件である。
- ただし実装上は、あらゆるウィンドウサイズへ変更可能とする処理経路を抑止するため、例外条件と同じくbase behaviorを避ける効果を持つ。
- API 37 以降は公式文書上この opt-out は使えなくなる予定であり、恒久対策ではない。

## Base behavior で無視される制約と、例外時の扱い

| 制約 / API | Base behavior 適用時 | 例外時の扱い |
| --- | --- | --- |
| `android:screenOrientation` | 固定方向の制約として採用されない | 従来policy / device policyに従う |
| `Activity#setRequestedOrientation()` | 要求した画面の向きが最終的な制約として採用されない | 従来policy / device policyに従う |
| `Activity#getRequestedOrientation()` | 要求値と、システムが実際に採用した画面の向き・アプリに割り当てられたウィンドウ領域が乖離し得る | 従来policyでは要求値と最終的な制約が近くなる可能性 |
| `android:resizeableActivity="false"` | `isUniversalResizeable()` により non-resizable 前提が崩れる | non-resizable / compatibility mode が残る可能性 |
| `android:minAspectRatio` / `android:maxAspectRatio` | aspect ratio policy が 0 扱いになり制限として効かない | manifest / user / device policy により制限される可能性 |
| Pillarboxing / compatibility mode | 公式文書上 pillarboxing は使われず full display window を満たす | compatibility mode / pillarboxing が戻る可能性 |

---

# 期待挙動マトリクス（Expected Behavior Matrix）

## OS / targetSdkVersion Matrix

| シナリオ | 期待挙動 | 根拠 / 注意 |
| --- | --- | --- |
| Android 16 / targetSdkVersion 35 | targetSdkVersion 36 起因の base behavior は既定適用対象外 | compat change default は API 36 target 以上 |
| Android 16 / targetSdkVersion 36 | 条件が揃えば base behavior 適用。例外条件では抑止 | `UNIVERSAL_RESIZABLE_BY_DEFAULT` + runtime gates |
| Android 15 / targetSdkVersion 36 | Android 16 の large screen default ignore と同一とは結論しない | Android 16 tag で `DisplayContent#getIgnoreOrientationRequest()` に差分 |

## Exception Matrix

| シナリオ | Base behavior | 期待挙動 / 確認点 |
| --- | --- | --- |
| Android 16 / targetSdkVersion 36 / `sw >= 600dp` / non-game / no user exception / no opt-out | 適用 | orientation / resizability / aspect ratio restrictions は無視 |
| Android 16 / targetSdkVersion 36 / `sw < 600dp` | 非適用 | large screen gate を満たさない |
| Android 16 / targetSdkVersion 36 / game app | 非適用 | `ApplicationInfo.CATEGORY_GAME` で `canBeUniversalResizeable()` が false |
| Android 16 / targetSdkVersion 36 / user aspect ratio setting exception | 非適用になり得る | user が app default behavior を明示選択した状態を確認 |
| Android 16 / targetSdkVersion 36 / OEM override enabled | 端末config次第 | DeviceConfigがcompat changeとは別に画面の向きの要求を無視する設定を有効化可能 |
| Android 16 / targetSdkVersion 36 / OEM override disabled / package opt-out | 非適用または抑止 | package opt-out list に入る場合は config path から外れる |
| Android 16 / targetSdkVersion 36 / Activity-level temporary opt-out | 非適用 | 該当 activity は restricted resizability を許可 |
| Android 16 / targetSdkVersion 36 / Application-level temporary opt-out | 非適用 | package 全体で restricted resizability を許可 |
| Android 16 / targetSdkVersion 36 / full-screen | 条件次第 | large screen + no exception なら base behavior |
| Android 16 / targetSdkVersion 36 / multi-window | 条件次第 | large screen + no exception なら base behavior |

---

# 影響対象（Affected App Categories）

## games / `android:appCategory="game"` を指定しているアプリ

- `ApplicationInfo.CATEGORY_GAME`なら、あらゆるウィンドウサイズへ変更可能とする処理経路から外れる。
- Android 16 / targetSdkVersion 36 でも、Adaptive layouts の base behavior は標準では適用されない想定。
- ただし game UI の large screen 対応が不要という意味ではない。端末固有の windowing mode や user settings は別途検証する。

## game だが `appCategory` を指定していないアプリ

- AOSP gate は `ApplicationInfo.category == CATEGORY_GAME` を見ている。
- manifest や installer category hint により category が game になっていない場合、game exception に入らない可能性がある。
- 実機では `ApplicationInfo.category` または package manager 表示を確認する。

## user aspect ratio settings に依存するアプリ

- user が device の aspect ratio settings で app default behavior を選ぶと、base behavior から外れる可能性がある。
- 顧客サポートでは user setting による表示差を再現条件として明示する必要がある。

## OEM device configuration の影響を受ける可能性があるアプリ

- `ignore_activity_orientation_request_screens` や package opt-out list により、端末ごとに挙動が変わり得る。
- Pixel / OEM device / emulator で結果が異なる場合は、DeviceConfig / dumpsys window の確認が必要。

## `sw < 600dp` の phone / small screen 前提のアプリ

- 公式 Behavior Change の large screen base behavior は適用されない。
- ただし small screen でも fold / external display / desktop mode への遷移で `sw` が変わる可能性がある。

## temporary opt-out 済みアプリ

- Android 16 target では一時的に base behavior を避けられる。
- API 37 以降は使えなくなる予定のため、adaptive layout 対応を並行して進める必要がある。

## 固定方向 / aspect ratio / compatibility modeに依存するアプリ

- 例外条件に入らない場合は base behavior により制約が無視される。
- 例外条件に入る場合も、端末設定や user setting の変更で base behavior に戻る可能性があるため、固定前提の UI は長期的にリスクが残る。

## Compose UI アプリと View UI アプリ

- Platform windowing policy の変更であり、Compose / View のどちらにも影響し得る。
- Compose のみでも、実際の window metrics / configuration / size class に基づく layout が必要。

---

# テスト観点（Test Considerations）

必須比較:
- Android 15 端末上の targetSdkVersion 35。
- Android 16 端末上の targetSdkVersion 35。
- Android 16 端末上の targetSdkVersion 36。
- Android 15 端末上の targetSdkVersion 36 が検証可能な場合の比較。

例外条件:
- `sw >= 600dp` と `sw < 600dp`。
- game app category あり / なし。
- `android:appCategory="game"` 指定あり / なし。
- user aspect ratio settings の app default / fullscreen / custom aspect ratio 選択。
- OEM / device config override enabled / disabled。
- Activity-level opt-out と Application-level opt-out。

制約別:
- `screenOrientation` / `setRequestedOrientation()` / `getRequestedOrientation()` の exception 有無による差。
- `resizeableActivity=false` 指定あり / なし。
- `minAspectRatio` / `maxAspectRatio` 指定あり / なし。
- full-screen と multi-window。
- pillarboxing / compatibility mode の有無。
- visual regression / screenshot testing。

確認方法の候補:
- `adb shell am compat enable UNIVERSAL_RESIZABLE_BY_DEFAULT <package>` / `disable` で compat change を切り替える。
- game app は `android:appCategory="game"` の有無で比較する。
- aspect ratio settings は device UI で app default / fullscreen / custom ratio を切り替える。
- `dumpsys window` / `dumpsys package`でpackage category、要求した画面の向き、bounds、letterbox / compat mode関連stateを確認する。
- emulator / Pixel / OEM large screen device で DeviceConfig 差分を確認する。

---

# Facts / Observations / Hypotheses / Conclusions

## Facts

- 公式 `#exceptions` section は game、user aspect ratio setting、`sw600dp` 未満を例外として列挙している。
- 公式 page は apps targeting Android 16 or higher 向け Behavior Changes であり、Android 16 / API 36 以上 target が前提である。
- `UNIVERSAL_RESIZABLE_BY_DEFAULT` / 357141415 は `@EnabledAfter(VANILLA_ICE_CREAM)` の compat change である。
- `DisplayContent#isLargeScreen()` は `smallestScreenWidthDp >= 600` を large screen とする。
- `ActivityRecord#canBeUniversalResizeable()` は `ApplicationInfo.CATEGORY_GAME` なら false を返す。
- `WindowManagerConstants` には DeviceConfig key と package opt-out list がある。
- `PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY` は temporary opt-out として application / activity property から読まれる。

## Observations

- 公式 `#exceptions` section の OEM override statement は再確認時点では見つからなかった。
- OEM / DeviceConfig override の AOSP evidence は存在するため、端末差の説明としては重要である。
- user aspect ratio settingの実装は`AppCompatAspectRatioOverrides`にあり、user preferenceが、あらゆるウィンドウサイズへ変更可能とする判定の一部になる。
- Android 15 tag にも準備コードはあるが、Android 16 tag の `DisplayContent#getIgnoreOrientationRequest()` が large screen default behavior の重要な差分である。

## Hypotheses

- userがaspect ratio settingsでapp default behaviorを選ぶと、`USER_MIN_ASPECT_RATIO_APP_DEFAULT`系のuser preferenceにより、あらゆるウィンドウサイズへ変更可能とする処理経路から外れ、従来のcompatibility mode / aspect ratio policyに近い表示になる。
- OEM / DeviceConfig の `ignore_activity_orientation_request_screens=all` は small screen にも影響し得るが、これは公式 targetSdkVersion 36 の標準 base behavior とは別の端末 policy として扱うべきである。
- game だが category が未設定の app は、公式が意図する game exception に入らない可能性がある。

## Conclusions

- 本項目の主分類は `TARGET_SDK_36_CONDITIONAL`。ただし適用には Android 16 以上、`sw >= 600dp`、non-game、user exception なし、temporary opt-out なし、OEM / device config による抑止なしという条件がある。
- 公式 `Exceptions` の 3 例外は AOSP evidence と整合する。
- OEM override は公式 `#exceptions` section の current text にはないが、AOSP DeviceConfig evidence として確認できる。report では公式文書差分として記録し、顧客説明では端末差の可能性として扱う。
- 顧客向けには「Android 16 へ OS アップデートしただけの影響」と「targetSdkVersion 36 化した時の影響」と「例外条件 / 端末固有設定」を混ぜない。

---

# 推奨対応候補（Recommended Action Candidates）

- `targetSdkVersion 36`化前に、large screen / foldable / tablet / desktop windowingで固定方向 / 固定aspect ratio / サイズ変更不可を前提とするUIを洗い出す。
- game は `android:appCategory="game"` または `ApplicationInfo.category` が期待通り game になっているか確認する。
- user aspect ratio settings を変えたときの display mode、pillarboxing、bounds、activity recreation を確認する。
- temporary opt-out は Android 16 向けの移行猶予としてのみ使い、API 37 以降に向けて adaptive layout 対応を進める。
- OEM device では DeviceConfig / package opt-out list / user setting の影響を含めて再現条件を記録する。

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
