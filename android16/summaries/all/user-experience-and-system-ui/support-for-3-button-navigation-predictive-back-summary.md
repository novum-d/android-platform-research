# Support for 3-button navigation - 1ページ要約（One Page Summary）

## 対象（Target）

Android 16 Behavior Change:
- Support for 3-button navigation

From:
- android-15.0.0_r36

To:
- android-16.0.0_r4

Note:

## 適用条件（Applicability）

- 主分類（Primary classification）: `OS_UPDATE_ALL_APPS`
- Android 16 OS update: 3-button navigation の Back 長押しで predictive back preview / animation が利用可能になる。
- targetSdkVersion 36: 3-button support 自体の必須条件ではない。ただし Android 16 r4 では app-level `enableOnBackInvokedCallback` が target 36 以上で既定 true になる。
- 実行時条件: Android 16、3-button navigation mode、Back button long press、predictive back 移行済み / 有効化済みの app/activity、animatable destination。
- Compat Change ID: 確認できない。

## 早見マトリクス（At-a-Glance Matrix）

| シナリオ（Scenario） | 影響（Impact） |
| --- | --- |
| Android 16 / targetSdkVersion 35 / 3-button | manifest 等で predictive back enabled なら対象。 |
| Android 16 / targetSdkVersion 36 / 3-button | target 36 default enable により対象になりやすい。 |
| Android 16 / gesture navigation | 既存の edge swipe predictive back path。 |
| Android 16 / 3-button / short press Back | 通常 Back。preview trigger は long press。 |
| Android 16 / 3-button / long press Back | predictive back animation が開始され得る。 |
| `android:enableOnBackInvokedCallback=false` | predictive back は無効化され、animation は期待しない。 |
| app not migrated | callback / legacy fallback の可能性。 |
| back-to-home / cross-task / cross-activity | WM / Shell が system animation type として扱う。 |

## 要約（Summary）

Android 16 では 3-button navigation mode でも Back button 長押しにより predictive back animation が開始され、Back の遷移先を preview できる。対象は「Android 16 に OS アップデートした端末」だが、実際に表示されるにはアプリが predictive back に対応している必要がある。

targetSdkVersion 36 化そのものが 3-button support を作るわけではない。ただし Android 16 r4 の AOSP では target 36 以上で `enableOnBackInvokedCallback` が既定 true になるため、target 36 化により predictive back animation の露出が増える可能性がある。

## 顧客影響（Customer Impact）

- 3-button navigation ユーザーにも predictive back preview が見えるようになる。
- gesture navigation だけを QA している場合、3-button long-press 固有の UX regression を見落とす。
- custom back handling、multi-activity、deep link、task affinity、custom transition は preview destination / callback timing の確認が必要。
- target 36 化時は manifest の `enableOnBackInvokedCallback` effective value を確認する必要がある。

## 影響対象（Who Is Affected）

- predictive back に移行済みのアプリ。
- targetSdkVersion 36 化で predictive back が既定有効になるアプリ。
- `OnBackInvokedCallback` / AndroidX `OnBackPressedDispatcher` を使うアプリ。
- Jetpack Navigation / Navigation Compose / Compose `BackHandler` を使うアプリ。
- custom back handling、multi-activity、custom activity transition、deep link / notification entry を持つアプリ。
- 3-button navigation を QA 対象にしていないアプリ。

## 推奨対応（Recommended Actions）

- Android 16 の QA に 3-button navigation mode を追加する。
- short press Back と long press Back を分けて検証する。
- targetSdkVersion 36 化時に `android:enableOnBackInvokedCallback` の default / override を確認する。
- legacy `onBackPressed()` / `KEYCODE_BACK` interception を棚卸しする。
- AndroidX Activity / Navigation / Compose の predictive back 対応 version を確認する。
- back-to-home、cross-task、cross-activity、deep link entry の preview destination を screen recording で確認する。

## テスト観点（Test Matrix）

| 観点 | 確認内容 |
| --- | --- |
| Android 15 / targetSdkVersion 35 | baseline。 |
| Android 16 / targetSdkVersion 35 | OS update + explicit predictive back enable。 |
| Android 16 / targetSdkVersion 36 | target 36 default enable。 |
| Android 15 / targetSdkVersion 36 | Android 16 との差分分離。 |
| 3-button navigation | long-press Back preview。 |
| gesture navigation | edge swipe predictive back baseline。 |
| `enableOnBackInvokedCallback=true/false` | animation eligibility。 |
| OnBackInvokedCallback | callback order / duplicate / cancel。 |
| AndroidX / Jetpack / Compose | library integration。 |
| back-to-home / cross-task / cross-activity | preview destination と commit。 |
| custom transition / multi-activity / deep link | unexpected destination / stale preview。 |
| tracing | logcat / dumpsys / WM Shell trace / Perfetto。 |

## 根拠（Evidence）

- Official documentation: https://developer.android.com/about/versions/16/behavior-changes-all#three-button-predictive-back
- Predictive back guide: https://developer.android.com/guide/navigation/custom-back/predictive-back-gesture
- AOSP files:
  - `frameworks-base/packages/SystemUI/src/com/android/systemui/navigationbar/views/buttons/KeyButtonView.java`
  - `frameworks-base/packages/SystemUI/src/com/android/systemui/navigationbar/views/NavigationBar.java`
  - `frameworks-base/packages/SystemUI/shared/src/com/android/systemui/shared/recents/ISystemUiProxy.aidl`
  - `frameworks-base/packages/SystemUI/src/com/android/systemui/LauncherProxyService.java`
  - `frameworks-base/libs/WindowManager/Shell/src/com/android/wm/shell/back/BackAnimationController.java`
  - `frameworks-base/libs/WindowManager/Shell/src/com/android/wm/shell/back/ShellBackAnimationRegistry.java`
  - `frameworks-base/services/core/java/com/android/server/wm/BackNavigationController.java`
  - `frameworks-base/core/java/android/window/BackEvent.java`
  - `frameworks-base/core/java/android/window/WindowOnBackInvokedDispatcher.java`
  - `frameworks-base/core/java/com/android/internal/pm/pkg/parsing/ParsingPackageUtils.java`
  - `frameworks-base/core/api/current.txt`
- Diff interpretation:
  - Android 16 の OS / Shell / SystemUI で 3-button / hardware Back を `EDGE_NONE` として predictive back animation path に接続する。
  - target 36 は `enableOnBackInvokedCallback` default enable の条件であり、3-button support 自体の唯一 gate ではない。

## 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- Critical / High / Medium / Low

判断（Decision）:
- Explain / Monitor / Ignore / Further investigation required

補足:
- 最終優先度、顧客通知要否、release readiness は repository owner が判断する。
