# Deprecating disruptive accessibility announcements 調査レポート

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
- https://developer.android.com/about/versions/16/behavior-changes-all#disruptive-a11y

Page:
- Behavior changes: all apps

Category:
- User experience and system UI

Section:
- Deprecating disruptive accessibility announcements

### 分類スナップショット（Classification Snapshot）

主分類（Primary classification）:
- `OS_UPDATE_ALL_APPS`

補足:
- 公式 all apps ページに掲載されているため `OS_UPDATE_ALL_APPS` と分類する。ただし AOSP evidence では `announceForAccessibility()` / `TYPE_ANNOUNCEMENT` の runtime dispatch を Android 16 で抑制・変換する実装差分は確認できない。本件の実質は API deprecation / SDK documentation guidance / accessibility practice migration である。

早見表（At-a-glance impact）:

| 確認項目（Question） | 回答（Answer） | 根拠（Evidence） |
| --- | --- | --- |
| Android 16 に OS アップデートしただけで runtime 挙動が変わるか | No evidence found | `View#announceForAccessibility()` は Android 16 でも `TYPE_ANNOUNCEMENT` event を生成して親へ dispatch する。`AccessibilitySecurityPolicy` も `TYPE_ANNOUNCEMENT` を常時 dispatch 可能な event として扱う。 |
| Android 16 all apps behavior として開発者対応が必要か | Conditional Yes | 公式 all apps ページは disruptive announcement pattern の deprecation と代替 API への移行を全アプリ向けに案内している。 |
| targetSdkVersion 36 以上が必要か | No | 該当 API / dispatch path に targetSdkVersion 36 gate は見つからない。 |
| compileSdk 36 で影響が見えるか | Yes | `View#announceForAccessibility()` と `AccessibilityEvent.TYPE_ANNOUNCEMENT` は API surface 上 `@Deprecated` として見えるため、compile / lint / IDE warning の対象になる。 |
| Compat Change ID が関係するか | No | 公式 compat framework changes と AOSP code path で本件の toggleable Change ID は確認できない。Aconfig flag `android.view.accessibility.deprecate_accessibility_announcement_apis` は API deprecation 表示を制御する。 |

### 調査日（Investigation Date）

2026-07-05

### 信頼度（Confidence）

- Medium

理由:
- 公式文書、API reference、AOSP public API / implementation / dispatch path を確認した。
- targetSdkVersion 36 gate と runtime blocking は見つからない。
- 一方で、`android-15.0.0_r36` の `current.txt` と source にも `@Deprecated` / `@FlaggedApi` が存在するため、Android 16 tag 差分だけで「Android 16 で初めて API annotation が追加された」とは断定しない。公式 Android 16 all apps 文書で developer-facing behavior change として明文化された項目として扱う。

### 適用条件分類（Applicability Classification）

適用される条件（Applies when）:
- [x] OS update / all apps on Android 16 regardless of targetSdkVersion
- [ ] targetSdkVersion >= 36 on Android 16+
- [ ] targetSdkVersion >= 36, with additional runtime conditions
- [ ] Mainline / Google Play system update dependent
- [ ] API addition only, not a behavior change
- [ ] Unknown / needs more evidence

必要な実行時条件（Required runtime conditions）:
- Android version: Android 16 以上の all apps guidance。
- targetSdkVersion: 条件なし。35 と 36 の期待 runtime 挙動差は確認できない。
- API usage: `View#announceForAccessibility(CharSequence)` を呼ぶ、または `AccessibilityEvent.TYPE_ANNOUNCEMENT` を直接 dispatch するアプリ。
- Practical impact: compileSdk 36 / API 36 docs / lint / IDE warning、accessibility QA、TalkBack / screen reader UX regression risk。
- Runtime enforcement: Android 16 r4 AOSP では announcement event の dispatch 抑制・変換は確認できない。

Compat framework:
- Change ID: 確認できない。
- Change name: N/A。
- Default state: N/A。
- Force-enable / force-disable: N/A。

Aconfig:
- `android.view.accessibility.deprecate_accessibility_announcement_apis`
  - namespace: `accessibility`
  - description: disruptive accessibility announcements に関係する platform API の deprecation を制御する。
  - exported: true

分類信頼度（Classification confidence）:
- Medium

分類根拠（Classification evidence）:
- Official documentation page: `behavior-changes-all` の `Deprecating disruptive accessibility announcements`。
- AOSP targetSdk gate: `View#announceForAccessibility()`、`AccessibilityEvent.TYPE_ANNOUNCEMENT`、framework dispatch path に targetSdkVersion 36 gate は見つからない。
- Runtime behavior: Android 16 で announcement event を抑制・変換・warning log 化する platform runtime behavior は確認できない。
- Baseline nuance: Android 15 r36 tag にも flagged deprecation annotation と代替 API documentation が存在する。

---

# エグゼクティブサマリー（Executive Summary）

Android 16 の all apps behavior change として、`View#announceForAccessibility()` と `AccessibilityEvent.TYPE_ANNOUNCEMENT` による disruptive accessibility announcements は deprecated pattern として明示された。これは targetSdkVersion 36 化による runtime gate ではなく、Android 16 SDK / documentation / accessibility best practice の変更として扱うのが妥当である。

AOSP `android-16.0.0_r4` では `announceForAccessibility()` は引き続き `TYPE_ANNOUNCEMENT` を生成して親 ViewParent へ送信する。`AccessibilitySecurityPolicy` でも `TYPE_ANNOUNCEMENT` は dispatch 可能な event として扱われており、Android 16 で platform がこの event を強制的に block する実装は確認できない。

顧客向けには、OS アップデートだけで即座に機能が壊れる変更ではなく、compileSdk 36 / API 36 で deprecated warning が見え、accessibility UX の観点で代替 semantics へ移行すべき項目として説明する。

---

# 公式ドキュメント確認（Original Documentation）

## 原文（Statement）

公式文書は以下を述べている。

- Android 16 は `announceForAccessibility` の利用や `TYPE_ANNOUNCEMENT` event の dispatch に代表される accessibility announcements を deprecated にする。
- これらは TalkBack と Android screen reader のユーザーに一貫しない体験を生む可能性がある。
- 代替手段は複数の Android assistive technologies にまたがる幅広いユーザー needs に適している。
- window changes など significant UI changes には `Activity.setTitle(CharSequence)` と `View#setAccessibilityPaneTitle(CharSequence)` を使う。
- Compose では `Modifier.semantics { paneTitle = "paneTitle" }` を使う。
- critical UI の変更通知には `View#setAccessibilityLiveRegion(int)` を使う。
- Compose では `Modifier.semantics { liveRegion = LiveRegionMode.[Polite|Assertive] }` を使う。
- live region は View 更新ごとに announcements を生成し得るため sparingly に使う。
- errors には `AccessibilityEvent.CONTENT_CHANGE_TYPE_ERROR`、`AccessibilityNodeInfo#setError(CharSequence)`、または `TextView#setError(CharSequence)` を使う。
- deprecated `announceForAccessibility` API reference に代替 API の詳細がある。

## 公式本文との差分確認

調査開始時点で公式本文を再確認した。依頼に含まれる Original statements と公式本文は実質的に一致している。

## 解釈（Interpretation）

この項目は「screen reader に読ませたい文字列を app が直接投げる」実装から、「画面・pane・live region・error state などの意味を UI semantics として提供する」実装へ移行するための guidance である。

ただし AOSP evidence では Android 16 で `TYPE_ANNOUNCEMENT` が platform によって runtime block される挙動は確認できない。したがって、customer-facing impact は「compile / lint warning と accessibility QA / UX 改善のための移行」であり、「Android 16 へ OS アップデートしただけで announcement が必ず読まれなくなる」とは説明しない。

---

# 変更内容（What Changed）

## 変更点

- `View#announceForAccessibility(CharSequence)` は public API surface 上 `@Deprecated` / `@FlaggedApi("android.view.accessibility.deprecate_accessibility_announcement_apis")` として表示される。
- `AccessibilityEvent.TYPE_ANNOUNCEMENT` も `@Deprecated` / `@FlaggedApi("android.view.accessibility.deprecate_accessibility_announcement_apis")` として表示される。
- `View#announceForAccessibility()` の documentation は、announcement event が semantic meaning を持たず accessibility services が ignore し得ること、代替 API を使うことを説明する。
- `AccessibilityEvent.TYPE_ANNOUNCEMENT` の documentation も、`View#announceForAccessibility()` の代替 API を参照する。
- 代替 API として、pane title、activity title、live region、state description、error semantics が documentation 上で整理されている。

## 適用条件（Applicability）

### OS アップデート時の挙動（OS Update Behavior）

- Android 16 に OS アップデートしただけで runtime event dispatch が block される evidence はない。
- Android 16 all apps page に掲載されているため、Android 16 で実行される全アプリ向けの compatibility / UX guidance として扱う。
- 影響を受けるのは、manual announcement pattern を使うアプリ、または SDK / UI framework / hybrid framework が内部で同 pattern を使うアプリである。

### targetSdkVersion 36 以上での挙動（targetSdkVersion 36 Behavior）

- targetSdkVersion 36 gate は見つからない。
- Android 16 / targetSdkVersion 35 と Android 16 / targetSdkVersion 36 で、`announceForAccessibility()` の runtime dispatch path は同じ見込み。
- targetSdkVersion を 36 に上げただけで announcement dispatch が platform block されるとは判断しない。

### API deprecation / compileSdk 36 の影響

- compileSdk 36 / API 36 docs では `announceForAccessibility()` と `TYPE_ANNOUNCEMENT` が deprecated として見える。
- Java/Kotlin compile warning、IDE inspection、lint / static analysis で usage が検出される可能性がある。
- Android 15 r36 tag にも flagged deprecation が存在するため、tag 差分だけで Android 16 で初めて annotation が追加されたとは扱わない。

### Runtime behavior change

- `View#announceForAccessibility()` は Android 16 r4 でも `AccessibilityEvent.TYPE_ANNOUNCEMENT` を生成し、text を event に追加し、`mParent.requestSendAccessibilityEvent(this, event)` を呼ぶ。
- `AccessibilitySecurityPolicy.canDispatchAccessibilityEventLocked()` は `TYPE_ANNOUNCEMENT` を常時 dispatch 可能な event group に含める。
- Android 16 r4 AOSP では、`TYPE_ANNOUNCEMENT` を抑制・変換・warning log 化する runtime path は確認できない。

---

# AOSP 調査（AOSP Investigation）

## 関連ファイル（Related Files）

- `frameworks-base/core/java/android/view/View.java`
- `frameworks-base/core/java/android/view/accessibility/AccessibilityEvent.java`
- `frameworks-base/core/java/android/view/accessibility/AccessibilityNodeInfo.java`
- `frameworks-base/core/java/android/widget/TextView.java`
- `frameworks-base/core/java/android/app/Activity.java`
- `frameworks-base/core/java/android/view/accessibility/flags/accessibility_flags.aconfig`
- `frameworks-base/core/api/current.txt`
- `frameworks-base/core/res/res/values/attrs.xml`
- `frameworks-base/services/accessibility/java/com/android/server/accessibility/AccessibilitySecurityPolicy.java`
- `frameworks-base/services/tests/servicestests/src/com/android/server/accessibility/AccessibilitySecurityPolicyTest.java`

Checkout hygiene:
- `git -C frameworks-base status --short`: clean。
- `git -C frameworks-base tag --list android-15.0.0_r36`: tag exists。
- `git -C frameworks-base tag --list android-16.0.0_r4`: tag exists。
- evidence は explicit tag (`git show android-16.0.0_r4:<path>` / `git diff android-15.0.0_r36 android-16.0.0_r4 -- <path>`) で確認した。

## 確認したソース文脈（Source Context Reviewed）

| ファイル / シンボル（File / symbol） | Android 15 の基準挙動（baseline） | Android 16 の挙動 | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| `View#announceForAccessibility(CharSequence)` | `@Deprecated` / `@FlaggedApi` が存在し、`TYPE_ANNOUNCEMENT` event を生成して dispatch する。 | 同じく deprecated。runtime implementation は event を生成して parent へ送る。 | deprecating announcement API の中心 API。runtime block の有無を確認する entry point。 |
| `AccessibilityEvent.TYPE_ANNOUNCEMENT` | `@Deprecated` / `@FlaggedApi` が存在する。 | 同じく deprecated。値は `1 << 14` / `16384`。 | direct event dispatch の中心 constant。 |
| `accessibility_flags.aconfig` / `deprecate_accessibility_announcement_apis` | flag は存在し exported。 | flag は存在し exported。description は disruptive announcements の platform API deprecation を制御する。 | deprecation annotation の feature flag 根拠。 |
| `current.txt` | `announceForAccessibility()` と `TYPE_ANNOUNCEMENT` は `@Deprecated @FlaggedApi` として現れる。 | 同じく `@Deprecated @FlaggedApi` として現れる。 | API surface 上の deprecation visibility の根拠。 |
| `View#setAccessibilityPaneTitle(CharSequence)` | pane title 変更時に `CONTENT_CHANGE_TYPE_PANE_*` を通知する。 | 同じ。pane title を持つ View は window-like semantics として `TYPE_WINDOW_STATE_CHANGED` を発生させる。 | significant UI / pane changes の推奨代替。 |
| `View#setAccessibilityLiveRegion(int)` | live region mode を設定し、変更時に accessibility state change を通知する。 | 同じ。live region の View では `TYPE_WINDOW_CONTENT_CHANGED` event を即時送信する。 | critical UI updates の推奨代替。 |
| `AccessibilityEvent.CONTENT_CHANGE_TYPE_ERROR` | error content change type として定義される。 | 同じ。`TYPE_WINDOW_CONTENT_CHANGED` と組み合わせる error semantics。 | validation / form error の推奨代替。 |
| `AccessibilityNodeInfo#setError(CharSequence)` | node error text を保持する。 | 同じ。AccessibilityService からは sealed node に対して変更不可。 | error semantics を node に提供する根拠。 |
| `TextView#setError(CharSequence)` | editor error を設定し、`CONTENT_CHANGE_TYPE_ERROR | CONTENT_CHANGE_TYPE_CONTENT_INVALID` を通知する。 | 同じ。`onInitializeAccessibilityNodeInfo()` で `info.setError()` と `setContentInvalid(true)` を反映する。 | standard widget による error semantics の根拠。 |
| `Activity#setTitle(CharSequence)` | activity/window title を変更し、window title と ActionBar title に反映する。 | 同じ。`onTitleChanged()` 経由で `Window#setTitle()` を呼ぶ。 | screen / window title changes の代替。 |
| `AccessibilitySecurityPolicy#canDispatchAccessibilityEventLocked()` | `TYPE_ANNOUNCEMENT` を dispatch 可能 event として扱う。 | 同じく global window state などと同じ group で true を返す。 | platform dispatch path で announcement が block されていない根拠。 |

必須記入項目（Required context）:
- Entry point / caller: app code / library -> `View#announceForAccessibility()` -> `AccessibilityEvent.TYPE_ANNOUNCEMENT` -> `ViewParent#requestSendAccessibilityEvent()` -> accessibility framework dispatch。
- Relevant class or service responsibility: `View` は app UI から accessibility event を生成し、`AccessibilityEvent` は event type と content change type を定義し、AccessibilityManager / service 側が event を解釈する。
- Runtime path from app API / system event to changed code: app が API を呼ぶ場合、Android 16 でも event は生成される。deprecation は compile / doc / API annotation の問題であり、runtime enforcement ではない。
- Why unrelated code paths were excluded: accessibility service permission / virtual display / non-SDK hidden API / unrelated a11y selection API / sort direction API は本件の disruptive announcement deprecation とは別機能のため除外した。

## 差分解釈（Diff Interpretation）

| 確認した差分（Observed diff） | 解釈（Interpretation） | Behavior Change との関係 | 信頼度（Confidence） |
| --- | --- | --- | --- |
| Android 16 公式 all apps page が disruptive accessibility announcements の deprecation を明記。 | Developer-facing guidance の明文化。 | 公式 Behavior Change の主根拠。 | High |
| `View#announceForAccessibility()` / `TYPE_ANNOUNCEMENT` は Android 16 API surface で deprecated。 | API deprecation。 | compileSdk 36 / API docs / IDE warning に影響する。 | High |
| Android 15 r36 tag にも同じ flagged deprecation が存在。 | Baseline nuance。 | Android 16 tag 差分だけでは新規 runtime change と言えない。 | High |
| `announceForAccessibility()` implementation は Android 16 でも `TYPE_ANNOUNCEMENT` を生成して送信。 | No runtime behavior change found。 | OS update で必ず block される変更ではない。 | High |
| `AccessibilitySecurityPolicy` は `TYPE_ANNOUNCEMENT` を dispatch 可能 event として扱う。 | No framework suppression found。 | accessibility service 側が ignore し得るという doc guidance と、framework dispatch の責務を分離する根拠。 | High |
| `setAccessibilityPaneTitle()` / live region / error semantics は既存 API として実装済み。 | Alternative APIs available。 | 推奨移行先の AOSP 実装根拠。 | High |

必須分類（Required interpretation）:
- Added behavior: Android 16 r4 AOSP 差分として announcement dispatch の追加 block は確認できない。
- Removed behavior: `TYPE_ANNOUNCEMENT` dispatch path の削除は確認できない。
- Changed condition: targetSdkVersion 36 gate は確認できない。
- Changed default: runtime default 変更は確認できない。
- Documentation/API annotation behavior: deprecated API / constant として扱われ、代替 API へ移行する guidance が中心。

---

# Facts / Observations / Hypotheses / Conclusions

## Facts

- 公式 all apps ページは Android 16 の全アプリ向け項目として `Deprecating disruptive accessibility announcements` を掲載している。
- 公式文書は `announceForAccessibility` と `TYPE_ANNOUNCEMENT` を disruptive announcement pattern として deprecated と説明する。
- Android API reference では `AccessibilityEvent.TYPE_ANNOUNCEMENT` が API level 36 で deprecated と表示され、accessibility services may choose to ignore と説明される。
- AOSP `android-16.0.0_r4` では `View#announceForAccessibility()` が `@Deprecated` / `@FlaggedApi(FLAG_DEPRECATE_ACCESSIBILITY_ANNOUNCEMENT_APIS)` 付きで定義される。
- AOSP `android-16.0.0_r4` では `AccessibilityEvent.TYPE_ANNOUNCEMENT` が `@Deprecated` / `@FlaggedApi(Flags.FLAG_DEPRECATE_ACCESSIBILITY_ANNOUNCEMENT_APIS)` 付きで定義される。
- `View#announceForAccessibility()` は Android 16 でも `AccessibilityEvent.TYPE_ANNOUNCEMENT` を生成し、text を追加し、`mParent.requestSendAccessibilityEvent()` で dispatch する。
- `AccessibilitySecurityPolicy.canDispatchAccessibilityEventLocked()` は Android 16 でも `TYPE_ANNOUNCEMENT` を dispatch 可能 event として扱う。
- targetSdkVersion 36 gate と compat framework Change ID は確認できない。

## Observations

- Android 15 r36 tag にも `announceForAccessibility()` / `TYPE_ANNOUNCEMENT` の deprecated annotation と documentation が存在する。これは Android 16 公式文書の掲載より前に AOSP tag へ staging / flag guarded deprecation が入っていた可能性を示す。
- Android 16 の実質的な app impact は runtime breakage より、compileSdk 36 adoption、static analysis、accessibility UX review、manual announcement pattern の置換にある。
- TalkBack / screen reader が event をどう扱うかは Android framework dispatch とは別の層である。AOSP framework は event を送信し得るが、accessibility service は ignore し得る。
- Compose `paneTitle` / `liveRegion` は Jetpack Compose semantics であり、本調査では official documentation evidence として扱い、AOSP platform implementation evidence とは分ける。

## Hypotheses

- Android 16 / API 36 SDK で deprecated warning がより一般の app developer に見えることで、実務上の migration pressure が高まる。
- TalkBack や OEM / third-party screen reader は `TYPE_ANNOUNCEMENT` の扱いを独自に変える可能性があるが、本調査の AOSP evidence だけでは service-specific behavior は確定できない。
- 将来 Android release では `TYPE_ANNOUNCEMENT` をより強く抑制する可能性があるが、Android 16 r4 AOSP ではその enforcement は確認できない。

## Conclusions

- 主分類は `OS_UPDATE_ALL_APPS`。ただし実態は runtime enforcement ではなく、全アプリ向け API deprecation / accessibility guidance として扱う。
- targetSdkVersion 36 化だけで `announceForAccessibility()` / `TYPE_ANNOUNCEMENT` の runtime behavior が変わる evidence はない。
- Android 16 / targetSdkVersion 35 と Android 16 / targetSdkVersion 36 の runtime dispatch 期待挙動は同じ。
- 顧客向けには、manual announcements を用途別 semantics へ移行する必要があると説明する。screen / pane changes には title / pane title、critical updates には live region、errors には node error / TextView error を使う。

---

# 期待挙動マトリクス（Expected Behavior Matrix）

## OS / targetSdkVersion 別

| シナリオ | 期待挙動 |
| --- | --- |
| Android 16 / targetSdkVersion 35 | `announceForAccessibility()` / `TYPE_ANNOUNCEMENT` は deprecated pattern。runtime block は確認できない。 |
| Android 16 / targetSdkVersion 36 | targetSdkVersion 35 と同じ runtime 期待挙動。targetSdkVersion 36 gate はない。 |
| Android 15 / targetSdkVersion 36 | Android 15 r36 tag にも flagged deprecation が存在する。Android 16 公式 all apps guidance とは分けて扱う。 |

## 詳細シナリオ別

| シナリオ | 期待挙動 |
| --- | --- |
| Android 16 / targetSdkVersion 35 / `View#announceForAccessibility` | deprecated API。event は従来通り生成・dispatch され得る。 |
| Android 16 / targetSdkVersion 36 / `View#announceForAccessibility` | targetSdkVersion 35 と同じ。compile warning / lint 対象になり得る。 |
| Android 16 / targetSdkVersion 35 / `TYPE_ANNOUNCEMENT` dispatch | deprecated constant。framework dispatch block は確認できない。 |
| Android 16 / targetSdkVersion 36 / `TYPE_ANNOUNCEMENT` dispatch | targetSdkVersion 35 と同じ。 |
| Android 16 / `Activity#setTitle` for significant UI change | window / Activity title semantics を提供する推奨代替。 |
| Android 16 / `View#setAccessibilityPaneTitle` | pane title の追加 / 削除 / 変更で pane content change を通知する。 |
| Android 16 / Compose paneTitle semantics | Jetpack Compose semantics として推奨。AOSP platform evidence とは分ける。 |
| Android 16 / `View#setAccessibilityLiveRegion` polite | critical UI update を screen reader へ通知する代替。頻繁な更新には注意。 |
| Android 16 / `View#setAccessibilityLiveRegion` assertive | より緊急度の高い update 用。割り込みリスクがあるため sparingly に使う。 |
| Android 16 / Compose liveRegion polite / assertive | Jetpack Compose semantics として推奨。 |
| Android 16 / live region used for frequently-updating view | 過剰通知になり得る。必要なら throttling / min duration 等を検討。 |
| Android 16 / `AccessibilityEvent.CONTENT_CHANGE_TYPE_ERROR` | error state の content change type として利用。 |
| Android 16 / `AccessibilityNodeInfo#setError` | node に error text を提供する。 |
| Android 16 / `TextView#setError` | error state と accessibility event dispatch を framework widget が管理する。 |
| Android 16 / app depends on announcement ordering or interruption | accessibility service-specific behavior に依存するため移行リスクが高い。 |
| Android 16 / app uses standard widgets only | framework semantics が既にある場合は低リスク。 |
| Android 16 / app uses custom View manual announcements | 代替 semantics への移行対象。 |
| Android 16 / app uses SDK / library that calls `announceForAccessibility` | transitive usage の棚卸しが必要。 |
| Android 15 / targetSdkVersion 36 / same app behavior if technically comparable | Android 15 r36 tag にも deprecation は見える。実機 / SDK 差分を確認する。 |
| compileSdk 36 / deprecated API warning | deprecated API / constant warning が出る可能性がある。 |
| targetSdkVersion changed to 36 without code change | runtime dispatch の変化は確認できないが、compileSdk 変更時の warning と QA 対応は必要。 |

---

# 開発者影響（Developer Impact）

## 影響対象

- `View#announceForAccessibility` を使うアプリ。
- `AccessibilityEvent.TYPE_ANNOUNCEMENT` を直接 dispatch するアプリ。
- custom View / custom accessibility behavior を持つアプリ。
- Jetpack Compose UI と手動 announcement を併用しているアプリ。
- screen / pane / dialog / bottom sheet / navigation changes を announcement で通知しているアプリ。
- validation error / form error を announcement で通知しているアプリ。
- loading / progress / snackbar / toast / banner / transient status を announcement で通知しているアプリ。
- accessibility announcement の順序 / 割り込み / TalkBack speech timing に依存するアプリ。
- SDK / library / cross-platform framework が announcement を内部利用するアプリ。
- accessibility QA / inclusive design 要件があるアプリ。
- platform standard widgets と semantics に移行すべきアプリ。

## 顧客向け説明で混ぜてはいけない点

- Android 16 OS update impact: all apps guidance として disruptive announcement pattern が deprecated と明示される。
- targetSdkVersion 36 impact: runtime gate ではない。
- compileSdk 36 impact: deprecated API / constant warning が見える可能性がある。
- runtime behavior change: Android 16 r4 AOSP では announcement event dispatch の抑制・変換は確認できない。
- TalkBack behavior: Android framework dispatch と TalkBack / screen reader interpretation は別レイヤーである。

## 用途別の移行候補

| 用途 | 避ける pattern | 推奨候補 |
| --- | --- | --- |
| screen / window change | announcement text を直接読む | `Activity#setTitle(CharSequence)`、Activity label |
| pane / dialog / bottom sheet / major section change | `announceForAccessibility()` | `View#setAccessibilityPaneTitle(CharSequence)`、Compose `paneTitle` |
| critical UI update | `TYPE_ANNOUNCEMENT` | `View#setAccessibilityLiveRegion(int)`、Compose `liveRegion` |
| frequently-updating progress / loading | live region / announcement の乱用 | 更新頻度を下げる、必要なら throttle、semantic state を提供 |
| validation / form error | announcement text の直接 dispatch | `AccessibilityNodeInfo#setError(CharSequence)`、`TextView#setError(CharSequence)`、`CONTENT_CHANGE_TYPE_ERROR` |
| custom View | manual announcement | node info / state / error / pane / live region semantics を実装 |

## 推奨対応候補

- app / SDK / hybrid framework 内の `announceForAccessibility` と `TYPE_ANNOUNCEMENT` usage を grep / static analysis で棚卸しする。
- compileSdk 36 で deprecated warning を確認し、warning suppression ではなく用途別 semantics へ置換する。
- TalkBack だけでなく複数 assistive technologies で UX を確認する。
- custom View では `AccessibilityNodeInfo`、pane title、live region、error semantics を正しく提供する。
- standard widgets が提供する semantics を優先し、manual event dispatch を最小化する。

---

# テスト観点（Testing Guidance）

| 観点 | 確認内容 |
| --- | --- |
| Android 15 端末上の targetSdkVersion 35 | baseline として announcement / TalkBack behavior を記録。 |
| Android 16 端末上の targetSdkVersion 35 | OS update 後に runtime block がないか、UX 差分がないか確認。 |
| Android 16 端末上の targetSdkVersion 36 | targetSdkVersion 35 と差がないか確認。 |
| Android 15 端末上の targetSdkVersion 36 | targetSdkVersion 36 だけで runtime behavior が変わらないことを比較。 |
| compileSdk 36 | deprecated API warning / lint / IDE inspection を確認。 |
| `View#announceForAccessibility` 呼び出し | event dispatch、TalkBack 読み上げ、重複読み上げを確認。 |
| `TYPE_ANNOUNCEMENT` AccessibilityEvent dispatch | custom event が service に届くか、service が ignore するか確認。 |
| TalkBack 有効時 | ordering / interruption / duplication を確認。 |
| TalkBack 以外の assistive technology | announcement 依存が機能しない場合の UX を確認。 |
| `Activity#setTitle` | screen / window title change が適切に伝わるか確認。 |
| `View#setAccessibilityPaneTitle` | pane / dialog / bottom sheet の表示・消滅・title change を確認。 |
| Compose paneTitle semantics | Compose UI で同等 semantics を確認。 |
| `setAccessibilityLiveRegion` polite / assertive | critical update の通知と過剰通知を確認。 |
| frequently updating live region | progress / timer / loading で過剰通知が起きないか確認。 |
| `AccessibilityNodeInfo#setError` | custom View error state が node info に出るか確認。 |
| `TextView#setError` | error text / content invalid / event sequence を確認。 |
| `CONTENT_CHANGE_TYPE_ERROR` | error content change event が適切に発生するか確認。 |
| custom View accessibility event sequence | announcement から semantic event への置換後の event sequence を確認。 |
| SDK / library 経由 usage | dependency 内 usage を static analysis / runtime event capture で確認。 |
| UI automation / AccessibilityService test | 受信 event type / content change type / node info を検証。 |

---

# Evidence Gaps / 注意点

- TalkBack は AOSP framework とは別レイヤーであり、本調査では TalkBack の内部実装や proprietary distribution behavior までは確認していない。
- Jetpack Compose `paneTitle` / `liveRegion` は Android Developers の official documentation evidence として扱った。AOSP platform source evidence ではない。
- Android 15 r36 tag にも flagged deprecation が存在するため、Android 16 r4 tag diff だけでは deprecation annotation の初出は断定しない。
- runtime enforcement は確認できないため、customer-facing 説明では「Android 16 で必ず読み上げられなくなる」と書かない。

---

# 最終結論（Conclusion）

`Deprecating disruptive accessibility announcements` は Android 16 all apps ページの項目として `OS_UPDATE_ALL_APPS` に分類する。ただし、AOSP `android-16.0.0_r4` で確認できる範囲では runtime enforcement ではなく、`announceForAccessibility()` / `TYPE_ANNOUNCEMENT` の deprecated API guidance として扱うべきである。

開発者は targetSdkVersion 36 化の有無ではなく、manual announcement pattern の有無を基準に影響を判断する。screen / pane changes、critical updates、errors をそれぞれ semantic API へ置き換え、TalkBack 固有の読み上げ timing 依存から脱却することが推奨される。

## Human Decision placeholder

最終優先度（Final Priority）:
- Critical / High / Medium / Low

判断（Decision）:
- Explain / Monitor / Ignore / Further investigation required

補足:
- 最終優先度、顧客通知要否、release readiness は repository owner が判断する。

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
