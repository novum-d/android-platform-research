# Support for 3-button navigation 調査レポート

## 基本情報（Metadata）

### 調査対象 Android バージョン（Android Versions）

From:
- android-15.0.0_r36

To:
- android-16.0.0_r4

Note:

Previous targetSdkVersion:
- 35

Target targetSdkVersion:
- 36

### Behavior Change 文書（Behavior Change Source）

Document:
- https://developer.android.com/about/versions/16/behavior-changes-all#three-button-predictive-back

Page:
- Behavior changes: all apps

Category:
- User experience and system UI

Section:
- Support for 3-button navigation

### 分類スナップショット（Classification Snapshot）

主分類（Primary classification）:
- `OS_UPDATE_ALL_APPS`

補足:
- 公式文書は `behavior-changes-all` に掲載され、Android 16 の 3-button navigation mode で predictive back animation をサポートする OS / SystemUI / WM Shell 側の変更として説明している。
- ただし実際に animation が見えるには、アプリ / Activity が predictive back に移行済みであること、または `android:enableOnBackInvokedCallback` が有効であることが必要になる。
- Android 16 r4 の AOSP では application-level `enableOnBackInvokedCallback` の既定値が `targetSdk > VANILLA_ICE_CREAM`、つまり targetSdkVersion 36 以上で true になる。これは「3-button navigation support」自体の gate ではなく、predictive back 有効化条件の一部として分けて扱う。

早見表（At-a-glance impact）:

| 確認項目（Question） | 回答（Answer） | 根拠（Evidence） |
| --- | --- | --- |
| Android 16 へ OS アップデートしただけで 3-button long-press predictive back の OS 機能は存在するか | Yes | SystemUI / LauncherProxy / WM Shell に `KEYCODE_BACK` long press と `EDGE_NONE` predictive back animation 経路がある。 |
| targetSdkVersion 36 が必須か | No, but important | 3-button support 自体は all-apps OS behavior。ただし target 36 以上では `enableOnBackInvokedCallback` が既定で true になり、predictive back 有効化条件を満たしやすい。 |
| targetSdkVersion 35 app でも影響するか | Conditional Yes | manifest で predictive back を有効化している、または AndroidX などで適切に移行済みの場合、Android 16 の 3-button long-press animation 対象になり得る。 |
| gesture navigation の挙動変更か | No | 本項目は 3-button navigation mode で Back button 長押しに predictive back preview を追加するもの。gesture navigation の predictive back とは入力経路が異なる。 |
| short press Back が変わるか | Mostly No | 公式文書は long-press Back を animation trigger として説明する。short press は通常の Back commit として扱う。 |
| Compat Change ID が関係するか | No evidence found | 該当する compat framework Change ID は確認できない。関連 gate は manifest 属性、target SDK default、SystemProperties、aconfig flag。 |

### 調査日（Investigation Date）

2026-07-05

### 信頼度（Confidence）

- Medium-High

理由:
- 公式文書、predictive back guide、AOSP SystemUI / WM Shell / Activity / package parser / API surface / tests を確認した。
- 3-button long-press Back から predictive back animation へ入る AOSP 経路と、back-to-home / cross-task / cross-activity type の根拠を確認した。
- 一方で Launcher / OEM launcher / SystemUI integration の一部は製品実装差を持ち得るため、Pixel / OEM 実機での UX verification は別途必要。

### 適用条件分類（Applicability Classification）

適用される条件（Applies when）:
- [x] OS update / all apps on Android 16 regardless of targetSdkVersion
- [ ] targetSdkVersion >= 36 on Android 16+
- [ ] targetSdkVersion >= 36, with additional runtime conditions
- [ ] Mainline / Google Play system update dependent
- [ ] API addition only, not a behavior change
- [ ] Unknown / needs more evidence

必要な実行時条件（Required runtime conditions）:
- Android version: Android 16 以上。
- Navigation mode: 3-button navigation。
- User action: Back button long press。
- App state: app / Activity が predictive back に移行済み、または `OnBackInvokedCallback` / AndroidX integration / manifest 設定により predictive back が有効。
- Animation target: system animation がサポートする back-to-home、cross-task、cross-activity などの flow。

targetSdkVersion 条件:
- 3-button navigation support 自体は targetSdkVersion 36 専用ではない。
- Android 16 r4 の package parsing では、application-level `enableOnBackInvokedCallback` の default が `targetSdk > Build.VERSION_CODES.VANILLA_ICE_CREAM` であり、targetSdkVersion 36 以上では predictive back が既定で有効になる。
- targetSdkVersion 35 でも manifest で明示的に有効化していれば対象になり得る。
- targetSdkVersion 36 でも manifest / Activity で `android:enableOnBackInvokedCallback="false"` を指定すれば predictive back は無効化される。

Compat framework:
- Change ID: 確認できない。
- Change name: N/A。
- Default state: N/A。
- Force-enable / force-disable: N/A。

Aconfig / flags:
- `com.android.window.flags.predictive_back_priority_system_navigation_observer`
  - `PRIORITY_SYSTEM_NAVIGATION_OBSERVER` の predictive back API extension。
  - Android 16 r4 では public API surface で `PRIORITY_SYSTEM_NAVIGATION_OBSERVER` が flag annotation なしに見える。
- `com.android.window.flags.predictive_back_stop_keycode_back_forwarding`
  - description: app が `enableOnBackInvokedCallback=true` の場合、`KEYCODE_BACK` forwarding を止める。
  - 3-button / hardware Back の predictive back integration と関連する。

分類信頼度（Classification confidence）:
- Medium-High

分類根拠（Classification evidence）:
- Official documentation page: `behavior-changes-all` の `Support for 3-button navigation`。
- AOSP implementation: SystemUI が Back button long press を `KEYCODE_BACK` + `FLAG_LONG_PRESS` として扱い、LauncherProxy / WM Shell の `BackAnimationController` が `EDGE_NONE` input として predictive back animation を開始できる。
- targetSdk nuance: AOSP package parser に target 36 以上で predictive back default enable となる default 値があるため、OS update impact と targetSdkVersion 36 impact を分離する必要がある。

---

# エグゼクティブサマリー（Executive Summary）

Android 16 では、3-button navigation mode でも Back button の長押しにより predictive back animation が開始される。これにより、ユーザーは gesture navigation と同様に、Back 操作が home、別 task、前 activity などどこへ遷移するかを preview できる。

この変更は `behavior-changes-all` の項目であり、3-button navigation support 自体は targetSdkVersion 36 専用ではない。ただし、predictive back animation が表示されるにはアプリ側が predictive back に移行済みである必要がある。Android 16 r4 の AOSP では targetSdkVersion 36 以上の application で `enableOnBackInvokedCallback` が既定 true になるため、target 36 化により「3-button long-press predictive back の対象になる flow」が増える可能性がある。

顧客向けには、「Android 16 へ OS アップデートしただけの影響」「targetSdkVersion 36 化で predictive back が既定有効になる影響」「3-button navigation の長押し時だけに見える UX」を混ぜずに説明する必要がある。

---

# 公式ドキュメント確認（Original Documentation）

## 原文（Statements）

調査対象の公式文書は、2026-07-05 時点で以下を述べている。

- Android 16 brings predictive back support to the 3-button navigation for apps that have properly migrated to predictive back.
- Long-pressing the back button initiates a predictive back animation, giving you a preview of where the back swipe takes you.
- This behavior applies across all areas of the system that support predictive back animations, including the system animations: back-to-home, cross-task, and cross-activity.
- The predictive back animations in 3-button navigation mode.

## 公式文書との差分（Documentation Drift）

依頼時の Original statements と、調査開始時に確認した公式本文に実質差分は見つからない。

関連する predictive back guide では、Android 15 以降は back-to-home / cross-task / cross-activity の system animation が developer option なしで表示されること、サポートには AndroidX `OnBackPressedCallback` / platform `OnBackInvokedCallback` への移行が必要であること、`android:enableOnBackInvokedCallback="false"` で opt-out できることが説明されている。

---

# AOSP Evidence

## AOSP checkout hygiene

`frameworks-base` evidence 使用前に以下を確認した。

- `git -C frameworks-base status --short`: clean
- `git -C frameworks-base tag --list android-15.0.0_r36`: exists
- `git -C frameworks-base tag --list android-16.0.0_r4`: exists

ローカル working tree の未コミット変更は `frameworks-base` にはなく、本調査の AOSP evidence は明示 tag から取得した。

## Evidence 1: 3-button Back long press is represented as KEYCODE_BACK with long-press flag

Reviewed source:
- `frameworks-base/packages/SystemUI/src/com/android/systemui/navigationbar/views/buttons/KeyButtonView.java`
- `frameworks-base/packages/SystemUI/src/com/android/systemui/navigationbar/views/NavigationBar.java`

Relevant symbols / entry points:
- `KeyButtonView.mCheckLongPress`
- `KeyButtonView.performAccessibilityActionInternal`
- `KeyButtonView.sendEvent(int action, int flags, long when)`
- `NavigationBar.onLongClick(...)`

Android 16 target behavior:
- Back button long press sends `KeyEvent.ACTION_DOWN` with `KeyEvent.FLAG_LONG_PRESS`.
- `sendEvent()` creates a `KeyEvent` with:
  - key code: `KEYCODE_BACK`
  - repeat count: `1` when `FLAG_LONG_PRESS` is set
  - flags: `FLAG_FROM_SYSTEM | FLAG_VIRTUAL_HARD_KEY`
  - display ID set when available
- `NavigationBar` explicitly handles Back long press and calls `keyButtonView.sendEvent(KeyEvent.ACTION_DOWN, KeyEvent.FLAG_LONG_PRESS)`.

Diff interpretation:
- This code path establishes the input-side signal for 3-button long press Back.
- Android 15 baseline already injected long-press `KEYCODE_BACK`; Android 16 changes around LauncherProxy / Shell determine whether that signal can drive predictive back animation.

Why relevant:
- The official behavior says long-pressing the back button initiates predictive back animation. This code is the SystemUI nav bar source of the long-press Back input.

## Evidence 2: Launcher / SystemUI proxy passes KEYCODE_BACK events into BackAnimation with EDGE_NONE

Reviewed source:
- `frameworks-base/packages/SystemUI/shared/src/com/android/systemui/shared/recents/ISystemUiProxy.aidl`
- `frameworks-base/packages/SystemUI/src/com/android/systemui/LauncherProxyService.java`
- `frameworks-base/core/java/android/window/BackEvent.java`

Relevant symbols / entry points:
- `ISystemUiProxy.onBackEvent(in KeyEvent keyEvent, int displayId)`
- `LauncherProxyService.onBackEvent(...)`
- `BackEvent.EDGE_NONE`

Android 16 target behavior:
- `ISystemUiProxy.onBackEvent` documentation states that SystemUI may use non-null `KeyEvent` to show a predictive back animation.
- `LauncherProxyService.onBackEvent()` passes the event into `mBackAnimation.onBackMotion(..., EDGE_NONE, displayId)`.
- `BackEvent.EDGE_NONE` is documented as the case where back was not triggered by an edge swipe, including 3-button navigation and hardware Back.

Android 15 baseline:
- The AIDL method existed as a generic back key event callback, but Android 16 changes its signature / documentation to include `displayId` and explicitly mention predictive back animation use.

Diff interpretation:
- Changed condition / changed integration path: Android 16 makes a non-gesture Back event usable as predictive back input (`EDGE_NONE`), which is the essential 3-button navigation bridge.

Why relevant:
- This directly maps the 3-button long-press Back input to the predictive back animation system without confusing it with gesture navigation edge-swipe input.

## Evidence 3: Shell BackAnimation starts system animation and handles 3-button EDGE_NONE path

Reviewed source:
- `frameworks-base/libs/WindowManager/Shell/src/com/android/wm/shell/back/BackAnimationController.java`
- `frameworks-base/libs/WindowManager/Shell/src/com/android/wm/shell/back/ShellBackAnimationRegistry.java`

Relevant symbols / entry points:
- `BackAnimationController.startBackNavigation(...)`
- `BackAnimationController.onBackNavigationInfoReceived(...)`
- `BackAnimationController.startSystemAnimation()`
- `BackAnimationController.shouldTriggerCloseTransition()`
- `ShellBackAnimationRegistry`

Android 16 target behavior:
- `BackAnimationController` calls `ActivityTaskManager.startBackNavigation(...)` to obtain `BackNavigationInfo`.
- If a system animation is available, it starts the registered `BackAnimationRunner`.
- `shouldTriggerCloseTransition()` returns true for:
  - `TYPE_RETURN_TO_HOME`
  - `TYPE_CROSS_TASK`
  - `TYPE_CROSS_ACTIVITY`
- In `startSystemAnimation()`, Android 16 has an explicit comment that `onBackStarted` is dispatched so `WindowOnBackInvokedDispatcher` can intercept touch events while active, and that this is used for 3-button-nav predictive back cases.
- `ShellBackAnimationRegistry` registers animation runners for `TYPE_CROSS_ACTIVITY`, `TYPE_CROSS_TASK`, `TYPE_DIALOG_CLOSE`, and `TYPE_RETURN_TO_HOME`.

Diff interpretation:
- Added / changed behavior: Android 16 Shell side is prepared to drive predictive back animation even when `BackEvent` edge is `EDGE_NONE`, which covers 3-button navigation and hardware Back.

Why relevant:
- This is the animation-side evidence for the official statement that 3-button navigation supports predictive back animations across system animation areas.

## Evidence 4: WM BackNavigationController chooses back-to-home, cross-task, and cross-activity types

Reviewed source:
- `frameworks-base/services/core/java/com/android/server/wm/BackNavigationController.java`

Relevant symbols / entry points:
- `BackNavigationController.startBackNavigation(...)`
- `BackNavigationInfo.TYPE_RETURN_TO_HOME`
- `BackNavigationInfo.TYPE_CROSS_TASK`
- `BackNavigationInfo.TYPE_CROSS_ACTIVITY`
- `BackNavigationInfo.TYPE_CALLBACK`

Android 16 target behavior:
- `startBackNavigation()` returns null if predictive back is disabled or no valid focused window / callback exists.
- If the focused window has callback info, the controller calculates previous destination and chooses:
  - `TYPE_CROSS_ACTIVITY` when returning to a previous Activity in the current task and conditions are animatable.
  - `TYPE_RETURN_TO_HOME` when the previous task is home.
  - `TYPE_CROSS_TASK` when returning to a previous non-home task and conditions are animatable.
  - `TYPE_CALLBACK` fallback when prediction / animation is not safe.
- It sets `prepareAnimation` only for supported types when the `BackAnimationAdapter` reports the type as animatable.

Android 15 baseline:
- Predictive back existed, but the Android 16 item adds 3-button long-press entry into this animation path.

Diff interpretation:
- The WM path confirms the official list of system animation categories. It also shows that some flows fall back to callback-only behavior and therefore may not show a full system preview.

Why relevant:
- This code determines the actual preview destination and separates system-controlled animation from app callback-only back handling.

## Evidence 5: app / Activity predictive back enablement is controlled by manifest and target default

Reviewed source:
- `frameworks-base/core/res/res/values/attrs_manifest.xml`
- `frameworks-base/core/java/com/android/internal/pm/pkg/parsing/ParsingPackageUtils.java`
- `frameworks-base/core/java/com/android/internal/pm/pkg/component/ParsedActivityUtils.java`
- `frameworks-base/core/java/android/content/pm/ApplicationInfo.java`
- `frameworks-base/core/java/android/content/pm/ActivityInfo.java`
- `frameworks-base/core/java/android/window/WindowOnBackInvokedDispatcher.java`
- `frameworks-base/core/java/android/app/Activity.java`

Relevant symbols / entry points:
- `android:enableOnBackInvokedCallback`
- `ApplicationInfo.PRIVATE_FLAG_EXT_ENABLE_ON_BACK_INVOKED_CALLBACK`
- `ActivityInfo.PRIVATE_FLAG_ENABLE_ON_BACK_INVOKED_CALLBACK`
- `ActivityInfo.PRIVATE_FLAG_DISABLE_ON_BACK_INVOKED_CALLBACK`
- `WindowOnBackInvokedDispatcher.isOnBackInvokedCallbackEnabled(...)`
- `Activity.onCreate()` default back callback registration

Android 16 target behavior:
- `attrs_manifest.xml` defines `enableOnBackInvokedCallback` for application and activity.
- Application parsing uses default:
  - `targetSdk > Build.VERSION_CODES.VANILLA_ICE_CREAM`
  - Therefore targetSdkVersion 36+ defaults to predictive back enabled unless overridden.
- Activity parsing records explicit enable / disable when the activity attribute is set.
- `WindowOnBackInvokedDispatcher.isOnBackInvokedCallbackEnabled(...)` first respects Activity-level explicit value, then Application-level value.
- `Activity.onCreate()` registers a default system callback when `isOnBackInvokedCallbackEnabled(this)` is true.

Android 15 baseline:
- Android 15 r36 also contains code to default-enable predictive back for target SDK 36 behind `Flags.predictiveBackDefaultEnableSdk36()`.
- Android 16 r4 has direct `targetSdk > VANILLA_ICE_CREAM` default in the parser.

Diff interpretation:
- Changed default / condition: targetSdkVersion 36 can change whether the app is considered predictive-back-enabled by default.
- This is not the 3-button support gate itself, but it is a major applicability condition for whether an app is "properly migrated to predictive back" in practice.

Why relevant:
- The official statement includes "apps that have properly migrated to predictive back." This source determines whether platform back handling uses OnBackInvoked / predictive back instead of legacy `KEYCODE_BACK` / `onBackPressed`.

## Evidence 6: API surface supports OnBack and observer path

Reviewed source:
- `frameworks-base/core/api/current.txt`

Relevant API surface:
- `android.R.attr.enableOnBackInvokedCallback`
- `android.window.OnBackInvokedCallback`
- `android.window.OnBackInvokedDispatcher`
- `android.window.OnBackAnimationCallback`
- `OnBackInvokedDispatcher.PRIORITY_SYSTEM_NAVIGATION_OBSERVER`
- `BackEvent.EDGE_NONE`

Android 16 target behavior:
- `PRIORITY_SYSTEM_NAVIGATION_OBSERVER` is public in `current.txt` without flagged annotation.
- `BackEvent` includes the non-edge-swipe case through `EDGE_NONE`, described in source as 3-button / hardware Back.

Diff interpretation:
- API exposure supports the platform mechanism used to observe / route predictive back for non-gesture Back cases.

## Evidence 7: Tests cover BackNavigationInfo types and Shell back tests

Reviewed source:
- `frameworks-base/services/tests/wmtests/src/com/android/server/wm/BackNavigationControllerTests.java`
- `frameworks-base/libs/WindowManager/Shell/src/com/android/wm/shell/back/TEST_MAPPING`
- `frameworks-base/packages/SystemUI/multivalentTests/src/com/android/systemui/navigationbar/views/buttons/KeyButtonViewTest.java`

Relevant tests:
- `backNavInfo_HomeWhenBackToLauncher()`: expects `TYPE_RETURN_TO_HOME` and animation scheduled.
- `backTypeCrossTaskWhenBackToPreviousTask()`: expects `TYPE_CROSS_TASK`.
- `backTypeCrossActivityWhenBackToPreviousActivity()`: expects `TYPE_CROSS_ACTIVITY`.
- `preparesForBackToHome()`: verifies back-to-home preparation and callback fallback under conditions.
- `TEST_MAPPING` includes `WMShellUnitTests_shell_back` and `CtsWindowManagerDeviceBackNavigation_com_android_wm_shell_back`.
- `KeyButtonViewTest` verifies back long-press logging path with `KEYCODE_BACK`, `ACTION_DOWN`, `FLAG_LONG_PRESS`.

Diff interpretation:
- Tests verify the WM target type calculation and Shell back test coverage, but do not fully replace manual UX verification of 3-button long press animation on device.

---

# Facts / Observations / Hypotheses / Conclusions

## Facts

- Official documentation places this item under `Behavior changes: all apps`.
- Official documentation says Android 16 brings predictive back support to 3-button navigation for apps properly migrated to predictive back.
- Official documentation says long-pressing Back initiates predictive back animation.
- AOSP SystemUI injects Back long press as `KEYCODE_BACK` with `FLAG_LONG_PRESS`.
- AOSP `BackEvent.EDGE_NONE` explicitly covers 3-button navigation and hardware Back.
- AOSP LauncherProxy routes `onBackEvent(KeyEvent, displayId)` into `BackAnimation.onBackMotion(..., EDGE_NONE, displayId)`.
- AOSP Shell starts predictive back animation using `BackNavigationInfo`.
- AOSP WM computes `TYPE_RETURN_TO_HOME`, `TYPE_CROSS_TASK`, and `TYPE_CROSS_ACTIVITY`.
- AOSP package parser defaults application `enableOnBackInvokedCallback` to true when `targetSdk > VANILLA_ICE_CREAM`.
- No compat framework Change ID specific to this behavior was found.

## Observations

- The feature is best understood as two layers:
  - OS / SystemUI / Shell support for 3-button long-press predictive animation.
  - App / Activity eligibility for predictive back through manifest, target SDK default, or AndroidX migration.
- targetSdkVersion 36 does not create the 3-button feature, but it can make predictive back enabled by default, which can expose the app to the feature in more flows.
- If an app uses custom back handling that consumes back or disables `enableOnBackInvokedCallback`, the system may fall back to callback / legacy behavior and predictive animation may not be shown.
- Gesture navigation and 3-button navigation use different input edges:
  - gesture navigation: edge swipe (`EDGE_LEFT` / `EDGE_RIGHT`)
  - 3-button / hardware Back: non-edge-swipe (`EDGE_NONE`)

## Hypotheses

- Pixel / AOSP Launcher3 / OEM launchers may differ in visual polish or availability of the 3-button long-press animation, because Launcher / SystemUI integration is productized.
- Apps targeting 36 that did not explicitly opt out may see more predictive back animation exposure than the same app targeting 35, because target 36 default enables `enableOnBackInvokedCallback`.
- Apps that only tested gesture navigation may miss regressions specific to long-press Back timing, cancellation, and preview destination in 3-button mode.

## Conclusions

- Primary classification is `OS_UPDATE_ALL_APPS`, with additional conditions: Android 16, 3-button navigation mode, long-press Back, predictive-back-enabled app/activity, and animatable back destination.
- Customer-facing explanation must not say "targetSdkVersion 36 alone adds 3-button predictive back." The OS feature is Android 16. target 36 mainly affects predictive back default enablement.
- Apps with custom back handling, multiple activities, custom transitions, deep links, and task-affinity behavior should test 3-button long-press Back explicitly.
- Apps not migrated to predictive back, or explicitly opting out with `android:enableOnBackInvokedCallback="false"`, should not be expected to show the Android 16 3-button predictive animation.

---

# Expected Behavior Matrix

## OS / targetSdkVersion matrix

| Scenario | Expected behavior | Notes |
| --- | --- | --- |
| Android 16 / targetSdkVersion 35 | 3-button long-press predictive back can appear if app explicitly enables / migrates to predictive back. | target 35 does not default-enable app-level predictive back in Android 16 parser. |
| Android 16 / targetSdkVersion 36 | 3-button long-press predictive back can appear; application-level predictive back defaults to enabled unless overridden. | target 36 increases exposure but is not the OS feature gate. |
| Android 15 / targetSdkVersion 36 | Predictive back exists, but official 3-button long-press support is Android 16 behavior. | Android 15 r36 has target 36 default-enable code behind a flag; compare on real build if needed. |
| Android 16 / gesture navigation | Existing predictive back gesture path; not the focus of this item. | Edge swipe path uses `EDGE_LEFT` / `EDGE_RIGHT`. |
| Android 16 / 3-button navigation | Long-press Back can enter predictive back path using `EDGE_NONE`. | Official behavior target. |

## Detailed condition matrix

| Scenario | Expected impact |
| --- | --- |
| Android 16 / targetSdkVersion 35 / 3-button navigation | Conditional impact if predictive back enabled. |
| Android 16 / targetSdkVersion 36 / 3-button navigation | Conditional impact; target 36 default enables application predictive back. |
| Android 16 / targetSdkVersion 35 / gesture navigation | Gesture predictive back behavior; not a new 3-button behavior. |
| Android 16 / targetSdkVersion 36 / gesture navigation | Gesture predictive back behavior plus target 36 default enablement. |
| Android 16 / 3-button navigation / short press Back | Normal Back commit path; no long-press preview expectation. |
| Android 16 / 3-button navigation / long press Back | Predictive back preview / animation may start. |
| Android 16 / app properly migrated to predictive back | Eligible for system predictive back animation where destination is animatable. |
| Android 16 / app not migrated to predictive back | May fall back to legacy / callback behavior; animation not guaranteed. |
| Android 16 / `android:enableOnBackInvokedCallback=true` | OnBackInvoked path enabled; eligible for predictive back. |
| Android 16 / `android:enableOnBackInvokedCallback=false` | Predictive back disabled for that scope; 3-button animation should not be expected. |
| Android 16 / OnBackInvokedCallback registered | App callback participates; custom callback may affect animation / commit. |
| Android 16 / no OnBackInvokedCallback | System default callback may apply if predictive back is enabled; otherwise legacy path. |
| Android 16 / AndroidX OnBackPressedDispatcher integration | Relevant but outside AOSP; verify with AndroidX version and official guide. |
| Android 16 / Jetpack Navigation back stack | Relevant through AndroidX; verify with Jetpack Navigation version. |
| Android 16 / Compose BackHandler / Navigation Compose | Relevant through AndroidX Compose; verify with Jetpack docs / runtime. |
| Android 16 / back-to-home predictive animation | Supported when WM returns `TYPE_RETURN_TO_HOME` and Shell has runner. |
| Android 16 / cross-task predictive animation | Supported when WM returns `TYPE_CROSS_TASK` and Shell has runner. |
| Android 16 / cross-activity predictive animation | Supported when WM returns `TYPE_CROSS_ACTIVITY` and Shell has runner. |
| Android 16 / custom back handling | Risk: callback-only path or preview destination mismatch. |
| Android 16 / custom activity transition | System preview phase may be system-controlled; custom transition applies after commit where supported. |
| Android 16 / multiple activities | Higher test priority for cross-activity preview. |
| Android 16 / deep link entry point | Test preview destination from each entry point. |
| Android 15 / targetSdkVersion 36 | Use as baseline; 3-button support should not be assumed identical to Android 16. |
| app tests only gesture navigation | Gap: misses 3-button long-press behavior. |
| app tests both gesture and 3-button navigation | Recommended. |

---

# Developer Impact

## 影響対象（Who Is Affected）

- predictive back に移行済みのアプリ。
- predictive back 未移行だが targetSdkVersion 36 化で default enable になるアプリ。
- `OnBackInvokedCallback` を使うアプリ。
- AndroidX Activity / `OnBackPressedDispatcher` を使うアプリ。
- Jetpack Navigation を使うアプリ。
- Navigation Compose / Compose `BackHandler` を使うアプリ。
- custom back handling を持つアプリ。
- multi-activity app。
- custom activity transition / custom animation を持つアプリ。
- deep link / notification / launcher shortcut から複数 entry point を持つアプリ。
- task / affinity / cross-task navigation に依存するアプリ。
- 3-button navigation ユーザーを QA 対象にしていないアプリ。
- back-to-home / cross-task / cross-activity animation の UX regression を避けたいアプリ。

## 低影響または非影響になりやすいケース

- Android 15 以下で実行されるアプリ。
- gesture navigation のみを対象にしたテストケース。ただし 3-button ユーザー影響は別途残る。
- predictive back を無効化している Activity。
- `android:enableOnBackInvokedCallback="false"` を指定している app / Activity。
- simple single-activity app で system default back behavior に従い、preview destination が明確な flow。
- Back animation が support されない flow で WM が `TYPE_CALLBACK` に fallback するケース。

## 顧客向け説明で混ぜてはいけない点

- Android 16 OS update:
  - 3-button navigation に long-press predictive back support が追加される。
- targetSdkVersion 36 化:
  - `enableOnBackInvokedCallback` が application default で true になり、predictive back 対象になる可能性が上がる。
- 3-button navigation:
  - long-press Back が preview trigger。short press Back と同じではない。
- predictive back migration:
  - `OnBackInvokedCallback` / AndroidX migration / manifest setting が必要。
- system animation:
  - back-to-home / cross-task / cross-activity が対象だが、すべての custom back flow が system animation になるわけではない。

---

# Recommended Action Candidates

- 3-button navigation mode を Android 16 QA matrix に追加する。
- Back button の short press と long press を別テストとして記録する。
- targetSdkVersion 36 化時に `android:enableOnBackInvokedCallback` の effective value を確認する。
- legacy `Activity#onBackPressed()` / `KEYCODE_BACK` interception を棚卸しする。
- AndroidX Activity / AppCompat / Navigation / Compose Navigation の predictive back 対応 version を確認する。
- multi-activity、deep link、notification entry、cross-task return、custom transition の preview destination を確認する。
- system animation が出るべき flow と app callback-only に fallback してよい flow を設計上区別する。
- screen recording / manual UX verification で animation start、cancel、commit、destination を記録する。
- `dumpsys activity`、WM Shell tracing、logcat、Perfetto で unexpected destination / duplicate callback / stale preview を調査できるようにする。

---

# Test Matrix

| 観点 | 確認内容 |
| --- | --- |
| Android 15 / targetSdkVersion 35 | baseline Back behavior。 |
| Android 16 / targetSdkVersion 35 | OS update のみで 3-button long-press animation が出る条件。 |
| Android 16 / targetSdkVersion 36 | target 36 default enable による差分。 |
| Android 15 / targetSdkVersion 36 | Android 16 との差分が OS feature か target default かを分離。 |
| 3-button navigation mode | Back button long press preview。 |
| gesture navigation mode | edge swipe predictive back baseline。 |
| short press Back | 通常 commit と regression。 |
| long press Back | preview start / progress / cancel / commit。 |
| predictive back opt-in / migrated state | manifest / AndroidX / callback 状態。 |
| `android:enableOnBackInvokedCallback=true` | OnBackInvoked path が有効か。 |
| `android:enableOnBackInvokedCallback=false` | predictive animation が抑制されるか。 |
| OnBackInvokedCallback registered / unregistered | callback ordering / duplicate invocation。 |
| AndroidX OnBackPressedDispatcher | AOSP 外 evidence として library version 別に確認。 |
| Jetpack Navigation back stack | expected destination preview。 |
| Compose BackHandler / Navigation Compose | callback と animation の整合。 |
| back-to-home animation | app exit / task to home preview。 |
| cross-task animation | previous task preview。 |
| cross-activity animation | previous activity preview。 |
| custom back handling | callback-only fallback / unexpected destination。 |
| custom activity transition | preview phase と commit transition の差。 |
| multiple activity flow | Activity stack navigation。 |
| deep link entry flow | entry point ごとの Back destination。 |
| accessibility / touch exploration | long-press interaction との相互作用があれば確認。 |
| tracing | logcat / dumpsys / WM Shell tracing / Perfetto。 |

---

# Evidence Gaps / Limits

- AndroidX Activity、Jetpack Navigation、Compose BackHandler の具体挙動は AOSP ではなく Jetpack library 側の evidence が必要。
- Pixel Launcher / OEM launcher の visual behavior は AOSP SystemUI / Shell evidence だけでは完全には保証できない。
- Android 15 実機での targetSdkVersion 36 比較は、build に含まれる predictive back flags の状態に依存する可能性がある。
- 本調査では実機 UI recording は実施していない。

---

# Human Decision Placeholder

最終優先度（Final Priority）:
- Critical / High / Medium / Low

顧客通知要否（Customer Communication Required）:
- Yes / No / Monitor

推奨アクション採用判断（Action Decision）:
- Adopt / Defer / Not applicable / Further investigation required

補足:
- 最終優先度、顧客通知要否、release readiness は repository owner が判断する。
