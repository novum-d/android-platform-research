# Predictive Back への移行または opt-out が必要 - 調査レポート

## 基本情報（Metadata）

### 調査対象 Android バージョン（Android Versions）

比較元:
- android-15.0.0_r36

比較先:
- android-16.0.0_r4

注記:

### Behavior Change 文書（Behavior Change Source）

文書:
- https://developer.android.com/about/versions/16/behavior-changes-16#predictive-back

セクション:
- Migration or opt-out required for predictive back

### 分類スナップショット（Classification Snapshot）

主分類（Primary classification）:
- `TARGET_SDK_36_CONDITIONAL`

早見表（At-a-glance impact）:

| 確認項目（Question） | 回答（Answer） | 根拠（Evidence） |
| --- | --- | --- |
| Android 16 に OS アップデートしただけで適用されるか | いいえ | 公式文書には、Android 16 / API level 36 以上を対象とするアプリと明記されている。AOSP でも application manifest の既定値は `targetSdk > VANILLA_ICE_CREAM` で決まる |
| targetSdkVersion 36 以上が必要か | はい | Android 16 の `ParsingPackageUtils` は、targetSdkVersion 36 以上で `enableOnBackInvokedCallback` の既定値を `true` にする |
| 追加の実行時条件があるか | はい | Android 16 以上の端末上で動作し、Back イベントを独自に処理する、または従来の `onBackPressed` / `KEYCODE_BACK` の通知に依存する場合に、実質的な影響が出る |
| Compat Change ID が関係するか | いいえ / 見つからない | 公開されている compat framework changes ページと AOSP の `@ChangeId` 検索では、本件に対応する compat Change ID は確認できなかった。AOSP の aconfig flag `predictive_back_stop_keycode_back_forwarding` は確認した |

### 調査日（Investigation Date）

2026-06-30

### 信頼度（Confidence）

- Medium

理由:
- 公式文書、AOSP の targetSdkVersion 36 default gate、manifest opt-out の parsing、`ViewRootImpl` の `KEYCODE_BACK` interception path は確認できた。
- 一方、公開 compat framework changes ページには該当 Change ID がなく、`KEYCODE_BACK` 転送停止は aconfig flag `predictive_back_stop_keycode_back_forwarding` 経由であり、release build での flag default は公式文書からの整合確認に留まる。

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
- Device/form factor: 特定 form factor 条件は確認していない。
- Permission/API/component condition: back event を intercept している、`Activity.onBackPressed()`、`Dialog.onBackPressed()`、または `KEYCODE_BACK` dispatch に依存している場合に影響が顕在化する。
- App state/process condition: Activity / window が back navigation を受ける状態。

Compat framework:
- Change ID: Not found
- Change name: Not found
- Default state: 公式 compat framework changes ページに該当 entry なし。AOSP では compat Change ID ではなく manifest default と aconfig flag による制御を確認。
- Toggleable for testing: `android:enableOnBackInvokedCallback="false"` による manifest opt-out が公式文書で案内されている。compat override command 用の Change ID は確認できなかった。

分類信頼度（Classification confidence）:
- Medium

分類根拠（Classification evidence）:
- Official documentation page: `behavior-changes-16` の `User experience and system UI` セクション。
- Original applicability statement: apps targeting Android 16 / API level 36 or higher and running on Android 16 or higher device。
- AOSP targetSdk gate: `ParsingPackageUtils` で application-level `enableOnBackInvokedCallback` default が `targetSdk > Build.VERSION_CODES.VANILLA_ICE_CREAM`。
- Compat framework entry: 公開 compat page と AOSP `@ChangeId` 検索では該当なし。

---

# エグゼクティブサマリー（Executive Summary）

Android 16 では、targetSdkVersion 36 以上のアプリで Predictive Back のシステムアニメーションが既定で有効になる。
この状態では、従来の `onBackPressed()` は呼ばれず、`KEYCODE_BACK` も通常はアプリへ通知されない。そのため、Back イベントを独自に処理しているアプリは、`OnBackInvokedCallback` などの対応 API へ移行する必要がある。
一時的な回避策として、`android:enableOnBackInvokedCallback="false"` を application または activity に指定できる。
OS アップデートだけで targetSdkVersion 35 以下のアプリへ同じ挙動が適用される根拠は確認していない。

---

# 公式ドキュメント確認（Original Documentation）

## 原文（Statement）

検証対象 statement:

```text
predictive back system animations ... are enabled by default
onBackPressed is not called
KeyEvent.KEYCODE_BACK is not dispatched anymore
```

適用条件として、公式文書は次も述べている。

```text
For apps targeting Android 16 (API level 36) or higher and running on an Android 16 or higher device
```

## 解釈（Interpretation）

この変更は Android 16 の `behavior-changes-16` に掲載されているため、初期分類は targetSdkVersion 36 以上向けである。
ただし、targetSdkVersion 36 以上であることに加えて、Android 16 以上の端末上で実行され、アプリが従来方式の Back 処理に依存している場合に、実質的な影響が出る。
公式文書は、未移行のアプリに対し、対応する Back navigation API への移行、または一時的な opt-out として `android:enableOnBackInvokedCallback="false"` を設定する方法を案内している。

---

# 変更内容（What Changed）

- Android 16 では、targetSdkVersion 36 以上の application について `enableOnBackInvokedCallback` の default が true になる。
- predictive back enabled の場合、Back key / back gesture は `OnBackInvokedCallback` に置き換えられ、legacy `onBackPressed()` / `KEYCODE_BACK` dispatch に依存した処理は呼ばれない。
- Android 15 では同じ default enable 条件が `predictiveBackDefaultEnableSdk36()` flag に依存していたが、Android 16 ではその flag 条件が外れ、`targetSdk > VANILLA_ICE_CREAM` が直接 default 条件になっている。
- Activity または application の manifest で `android:enableOnBackInvokedCallback="false"` を明示すると、一時的に legacy back behavior を選べる。

## 適用条件（Applicability）

### OS アップデート時の挙動（OS Update Behavior）

- Android 16 にアップデートしただけで適用されるか: 原則 No。
- targetSdkVersion に依存しない根拠: なし。AOSP の application default は `targetSdk > VANILLA_ICE_CREAM`。
- Android 15 以前での挙動: Android 15 tag では target 36 default enable が `predictiveBackDefaultEnableSdk36()` flag に依存しており、Android 16 のように unconditional な target 36 default ではない。

### targetSdkVersion 36 以上での挙動（targetSdkVersion 36 Behavior）

- targetSdkVersion 36 以上で適用されるか: Yes。Android 16 以上の端末上で適用される。
- Android 16 以外で targetSdkVersion 36 にした場合の挙動: 公式文書の適用条件外。Android 15 では default enable が flag 依存であるため、Android 16 と同じとは扱わない。
- opt-out / temporary override の有無: `android:enableOnBackInvokedCallback="false"` を application または activity に指定する temporary opt-out がある。

### その他の条件（Other Conditions）

- device/form factor: 特定条件なし。
- permission: 権限条件なし。
- API usage: `onBackPressed()`, `Dialog.onBackPressed()`, `KEYCODE_BACK`, custom back intercept、または predictive back API の未移行。
- manifest attribute: `android:enableOnBackInvokedCallback`。
- component boundary: application-level default と activity-level override の両方がある。activity-level が設定されていれば activity の指定が優先される。

---

# AOSP 調査（AOSP Investigation）

## 関連ファイル（Related Files）

- `core/java/com/android/internal/pm/pkg/parsing/ParsingPackageUtils.java`
- `core/java/com/android/internal/pm/pkg/component/ParsedActivityUtils.java`
- `core/java/android/content/pm/ApplicationInfo.java`
- `core/java/android/content/pm/ActivityInfo.java`
- `core/java/android/window/WindowOnBackInvokedDispatcher.java`
- `core/java/android/view/ViewRootImpl.java`
- `core/java/android/app/Activity.java`
- `core/java/android/window/flags/windowing_frontend.aconfig`
- `packages/SystemUI/src/com/android/systemui/flags/Flags.kt`
- `services/core/java/com/android/server/wm/BackNavigationController.java`

## 確認したソース文脈（Source Context Reviewed）

| ファイル / シンボル（File / symbol） | Android 15 の基準挙動（baseline） | Android 16 の挙動 | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| `ParsingPackageUtils.setOnBackInvokedCallbackEnabled` | default は `predictiveBackDefaultEnableSdk36() && targetSdk > VANILLA_ICE_CREAM` | default は `targetSdk > VANILLA_ICE_CREAM` | targetSdkVersion 36 以上で predictive back が default enabled になる直接 gate |
| `ParsedActivityUtils` / `enableOnBackInvokedCallback` | Activity manifest 属性を private flag に反映 | 同じく true / false を activity private flag に反映 | temporary opt-out が activity 単位で効く根拠 |
| `ApplicationInfo.isOnBackInvokedCallbackEnabled()` | application private flag から enabled 判定 | 同じ private flag を使用 | application-level default / opt-out の保持場所 |
| `ActivityInfo.isOnBackInvokedCallbackEnabled()` | activity-level attribute がある場合に enabled 判定 | 同じ private flag を使用 | activity-level override の保持場所 |
| `WindowOnBackInvokedDispatcher.isOnBackInvokedCallbackEnabled()` | predictive back feature flag と manifest state を見る | Android 16 でも manifest state を見て enabled 判定。activity が指定されていれば activity 優先、なければ application を見る | window runtime で predictive back / legacy back を選ぶ中心ロジック |
| `ViewRootImpl.doOnBackKeyEvent()` | enabled の場合に `KEYCODE_BACK` を `OnBackInvokedCallback` へ変換 | Android 16 では `predictiveBackStopKeycodeBackForwarding()` が true の場合に handled / not handled とし、後続の key dispatch を止める | 公式文書の `KEYCODE_BACK is not dispatched anymore` に対応する runtime path |
| `Activity.onCreate()` / default callback | enabled の場合に default back callback を登録 | Android 16 でも default callback を登録し、observer callback も flag 条件で登録 | `onBackPressed` ではなく `OnBackInvokedCallback` model に寄せる入口 |
| `Flags.WM_ENABLE_PREDICTIVE_BACK_ANIM` / `BackNavigationController` | predictive back animation は flag / controller に依存 | SystemUI flag default true、controller は back-to-home / cross-task / cross-activity を判定 | 公式文書の predictive back system animations の AOSP 文脈 |

必須記入項目（Required context）:
- Entry point / caller: package parsing -> `ApplicationInfo` / `ActivityInfo` flags -> Activity / Window attach -> `WindowOnBackInvokedDispatcher` -> `ViewRootImpl` input stage -> `BackNavigationController` / Shell animation。
- Relevant class or service responsibility: package parser は manifest default / override を決める。`WindowOnBackInvokedDispatcher` は back callback の enabled 判定と dispatch を管理する。`ViewRootImpl` は `KEYCODE_BACK` input を view tree / callback へ流す。`BackNavigationController` は system back animation target を決める。
- Runtime path from app API / system event to changed code: app targetSdkVersion 36 -> application default `enableOnBackInvokedCallback=true` -> window dispatcher enabled -> back key / gesture が `OnBackInvokedCallback` path に入り、legacy key dispatch / `onBackPressed` 依存処理が呼ばれない。
- Why unrelated code paths were excluded: IME-specific back animation、Wear fallback `windowSwipeToDismiss`、Settings strings、test manifests は本件の targetSdkVersion 36 default gate を決める primary evidence ではないため補助情報に留めた。

## 差分解釈（Diff Interpretation）

| 確認した差分（Observed diff） | 解釈（Interpretation） | Behavior Change との関係 | 信頼度（Confidence） |
| --- | --- | --- | --- |
| `predictiveBackDefaultEnableSdk36()` 条件が Android 16 で削除され、`targetSdk > VANILLA_ICE_CREAM` が直接 default 条件になった | Changed condition / gate | targetSdkVersion 36 以上で predictive back が default enabled になる | High |
| `ViewRootImpl.doOnBackKeyEvent()` が `predictiveBackStopKeycodeBackForwarding()` true 時に handled / not handled を返し、後続 key dispatch を止める | Changed condition / removed legacy dispatch | `KEYCODE_BACK is not dispatched anymore` に対応する | Medium |
| `ParsedActivityUtils` が activity-level `enableOnBackInvokedCallback` true / false を private flag に保存 | Existing / supporting behavior | temporary opt-out の根拠 | High |
| SystemUI predictive back animation flag が default true | Changed/default-supporting behavior | predictive back system animations が default enabled になる補助根拠 | Medium |

必須分類（Required interpretation）:
- Added behavior: Android 16 では targetSdkVersion 36 以上で application default が predictive back enabled になる。
- Removed behavior: enabled 状態では legacy `KEYCODE_BACK` dispatch / `onBackPressed` 依存 path が通常の back handling 入口ではなくなる。
- Changed condition / gate: Android 15 の aconfig flag 依存から、Android 16 の targetSdkVersion 36 以上 default へ変わった。
- Changed default: `enableOnBackInvokedCallback` の default が targetSdkVersion 36 以上で true。
- No behavior change found: `enableOnBackInvokedCallback` 属性や `OnBackInvokedCallback` API 自体は Android 16 で新規追加されたものではない。default / dispatch behavior が変わる。

## 事実（Evidence）

- 公式文書は、Android 16 / targetSdkVersion 36 以上 / Android 16 以上端末で predictive back system animations が default enabled と述べている。
- Android 16 AOSP の `ParsingPackageUtils` は `enableOnBackInvokedCallback` default を `targetSdk > Build.VERSION_CODES.VANILLA_ICE_CREAM` にしている。
- `Build.VERSION_CODES.VANILLA_ICE_CREAM` は API 35 であるため、`targetSdk > VANILLA_ICE_CREAM` は targetSdkVersion 36 以上を意味する。
- Android 15 AOSP では同じ default が `predictiveBackDefaultEnableSdk36()` flag に依存していた。
- `WindowOnBackInvokedDispatcher` は activity-level attribute があれば activity を優先し、なければ application-level flag を見る。
- `ViewRootImpl` は predictive back enabled の場合、`KEYCODE_BACK` を `OnBackInvokedCallback` path に入れる。
- 公開 compat framework changes ページで predictive back / OnBack / KEYCODE_BACK / enableOnBackInvokedCallback を検索したが、本件に対応する compat Change ID は見つからなかった。

## 観察（Observations）

- `android:enableOnBackInvokedCallback="false"` は application または activity に設定でき、activity-level が明示されると activity の設定が優先される。
- `KEYCODE_BACK` 転送停止は compat Change ID ではなく aconfig flag `predictive_back_stop_keycode_back_forwarding` の実装として見える。
- SystemUI の `WM_ENABLE_PREDICTIVE_BACK_ANIM` は `persist.wm.debug.predictive_back_anim` を default true としている。

## 仮説（Hypotheses）

- Android 16 release build では `predictive_back_stop_keycode_back_forwarding` が有効であるため公式文書の `KEYCODE_BACK is not dispatched anymore` と一致すると考えられる。ただし aconfig flag の release default は今回の source grep だけでは完全には追跡していない。

## 結論（Conclusions）

- 主分類は `TARGET_SDK_36_CONDITIONAL`。
- Android 16 / targetSdkVersion 35 では、OS アップデートだけで本変更が適用されるとは判断しない。
- Android 16 / targetSdkVersion 36 では predictive back が default enabled になり、legacy back handling に依存するアプリは API 移行または temporary opt-out が必要になる。

## 適用ゲート根拠（Applicability Gate Evidence）

- targetSdkVersion gate: `targetSdk > Build.VERSION_CODES.VANILLA_ICE_CREAM`。
- CompatChanges.isChangeEnabled / ChangeId: 該当 Change ID は見つからない。
- @EnabledAfter / @EnabledSince / default state: 該当 annotation は見つからない。
- Build.VERSION / SDK_INT gate: Android 16 以上端末が公式文書上の条件。AOSP parsing の target gate は targetSdkVersion 36 以上。
- DeviceConfig / resources config: System properties `persist.wm.debug.predictive_back` default 1、`persist.wm.debug.predictive_back_anim` default true。
- Permission/AppOps gate: 該当なし。
- Manifest/property gate: `android:enableOnBackInvokedCallback`。false で temporary opt-out。
- No gate found: 公開 compat framework changes ページには該当 entry なし。
- Gate conclusion: Android 16 以上端末かつ targetSdkVersion 36 以上で predictive back が default enabled。実質影響は legacy back handling 依存または back event intercept のあるアプリに限定される。
- Reasoning from source context: package parsing で targetSdkVersion 36 以上の default が true になり、runtime dispatcher がその flag に基づいて back event を `OnBackInvokedCallback` path に切り替えるため。

---

# 影響分析（Impact Analysis）

## 影響を受けるアプリ（Affected Apps）

- `Activity.onBackPressed()` / `Dialog.onBackPressed()` を override して back navigation を処理しているアプリ。
- View / Activity / Dialog で `KEYCODE_BACK` dispatch を直接受ける前提の実装を持つアプリ。
- predictive back API に未移行だが back event を intercept しているアプリ。
- `android:enableOnBackInvokedCallback="false"` をまだ指定していない legacy back handling 依存アプリ。

## 影響を受けないアプリ（Non-Affected Apps）

- targetSdkVersion 35 以下のまま Android 16 端末上で動作するアプリ。
- Android 15 端末上で動作する targetSdkVersion 36 アプリ。ただし Android 15 の flag 状態により挙動が変わる可能性はあるため、Android 16 と同一扱いしない。
- すでに `OnBackInvokedCallback` または AndroidX の supported back navigation APIs に移行済みのアプリ。
- temporary opt-out として `android:enableOnBackInvokedCallback="false"` を明示している activity / application。

---

# 顧客影響（Customer Impact）

## 影響度（Impact Level）

- Medium

※ 仮評価。最終判断は人間が行う。

## ビジネス影響（Business Impact）

- ユーザー影響: back 操作時の遷移 animation が変わり、legacy back handler が呼ばれないことで画面遷移、確認 dialog、未保存データ確認が期待通り動かない可能性がある。
- 運用影響: targetSdkVersion 36 対応時に back navigation の回帰テストが必要になる。
- 開発影響: `onBackPressed` / `KEYCODE_BACK` 依存を supported back navigation APIs に移行する必要がある。

---

# 対応候補（Required Actions）

実装例:
- [Predictive back implementation examples](../../case-guides/migration-or-opt-out-required-for-predictive-back-implementation-examples.md)
- [Predictive back - Dispatcher 経由あり・なしの実行挙動比較](migration-or-opt-out-required-for-predictive-back-runtime-behavior-comparison.md)
- [Predictive back - Dispatcher 移行後にアニメーションが消える原因と対処](migration-or-opt-out-required-for-predictive-back-dispatcher-animation-guide.md)

## 必須対応（Must）

- `onBackPressed`, `KEYCODE_BACK`, `dispatchKeyEvent`, `onKeyDown`, `onKeyUp` の back handling 利用箇所を棚卸しする。
- Android 16 / targetSdkVersion 36 で back-to-home、cross-task、cross-activity、dialog、nested navigation の挙動を確認する。
- back event を intercept している箇所は `OnBackInvokedCallback` または AndroidX の supported back navigation APIs に移行する。

代表例:

```kotlin
onBackPressedDispatcher.addCallback(this, object : OnBackPressedCallback(true) {
    override fun handleOnBackPressed() {
        if (viewModel.hasUnsavedChanges) {
            showDiscardConfirmDialog()
            return
        }

        isEnabled = false
        onBackPressedDispatcher.onBackPressed()
    }
})
```

## 推奨対応（Recommended）

- 一時回避が必要な Activity には `android:enableOnBackInvokedCallback="false"` を限定的に設定し、移行計画と削除予定を記録する。
- UI test / manual test に 3-button navigation と gesture navigation の両方を含める。
- 「戻るで確認 dialog を出す」「戻るで内部 stack を pop する」「戻るで task / home に遷移する」ケースを分けて検証する。

一時 opt-out 例:

```xml
<activity
    android:name=".LegacyFlowActivity"
    android:enableOnBackInvokedCallback="false" />
```

## 任意対応（Optional）

- aconfig flag や system property の状態を debuggable build で確認し、`KEYCODE_BACK` 転送停止の挙動を isolated test する。

---

# 検証方法（Verification Method）

## 検証マトリクス（Matrix）

| 端末 OS（Device OS） | targetSdkVersion | Compat flag | 期待挙動（Expected behavior） |
| --- | --- | --- | --- |
| Android 15 | 35 | default | legacy back behavior。predictive back default enable は target 36 条件外 |
| Android 15 | 36 | default | Android 15 tag では default enable が flag 依存。Android 16 と同一扱いしない |
| Android 16 | 35 | default | OS アップデートだけでは target 36 default enabled にならない |
| Android 16 | 36 | default | predictive back enabled。`onBackPressed` は呼ばれず、`KEYCODE_BACK` は通常 dispatch されない |
| Android 16 | 36 | `enableOnBackInvokedCallback=false` | temporary opt-out により legacy back behavior を維持する |

## 手順（Steps）

- targetSdk変更: 同一 app で targetSdkVersion 35 と 36 の build variant を用意する。
- compat framework command: 該当 Change ID は未確認。`adb shell am compat` ではなく manifest opt-out を主な検証手段にする。
- テスト方法: `onBackPressed`, `OnBackInvokedCallback`, `dispatchKeyEvent(KEYCODE_BACK)` の各 hook に logging を入れ、Android 15 / Android 16、target 35 / target 36、manifest opt-out 有無で比較する。
- 再現手順: Activity A -> Activity B、別 task、home 遷移、dialog 表示中、nested navigation の各状態で back gesture / back button を実行する。
- 期待結果: Android 16 / targetSdkVersion 36 / default では supported back callback path が使われ、legacy `onBackPressed` / `KEYCODE_BACK` 依存処理は呼ばれない。

---

# 結論（Conclusion）

この変更は、Android 16 端末上で targetSdkVersion 36 以上にしたアプリに対し、Predictive Back を既定で有効にする。
従来の `onBackPressed` / `KEYCODE_BACK` に依存する Back 処理は呼ばれなくなるため、対応する Back navigation API への移行が必要である。
顧客向けには、OS アップデートだけの影響ではなく、targetSdkVersion 36 化に伴う条件付き影響として説明する。

---

# 参照（References）

## ドキュメント（Documentation）

- https://developer.android.com/about/versions/16/behavior-changes-16#predictive-back
- https://developer.android.com/guide/navigation/custom-back/predictive-back-gesture
- https://developer.android.com/guide/navigation/custom-back/predictive-back-gesture#update-custom
- https://developer.android.com/guide/topics/manifest/activity-element#enableOnBackInvokedCallback
- https://developer.android.com/reference/android/window/OnBackInvokedCallback
- https://developer.android.com/reference/android/view/KeyEvent#KEYCODE_BACK
- https://developer.android.com/about/versions/16/reference/compat-framework-changes

## AOSP

- `core/java/com/android/internal/pm/pkg/parsing/ParsingPackageUtils.java`
- `core/java/com/android/internal/pm/pkg/component/ParsedActivityUtils.java`
- `core/java/android/content/pm/ApplicationInfo.java`
- `core/java/android/content/pm/ActivityInfo.java`
- `core/java/android/window/WindowOnBackInvokedDispatcher.java`
- `core/java/android/view/ViewRootImpl.java`
- `core/java/android/app/Activity.java`
- `core/java/android/window/flags/windowing_frontend.aconfig`
- `packages/SystemUI/src/com/android/systemui/flags/Flags.kt`
- `services/core/java/com/android/server/wm/BackNavigationController.java`

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
