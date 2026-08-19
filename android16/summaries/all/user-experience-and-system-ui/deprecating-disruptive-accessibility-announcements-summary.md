# Deprecating disruptive accessibility announcements - 1ページ要約（One Page Summary）

## 対象（Target）

Android 16 Behavior Change:
- Deprecating disruptive accessibility announcements

From:
- android-15.0.0_r36

To:
- android-16.0.0_r4

Note:

## 適用条件（Applicability）

- 主分類（Primary classification）: `OS_UPDATE_ALL_APPS`
- Android 16 OS update: all apps guidance として影響。ただし runtime block evidence はなし。
- targetSdkVersion 36 以上: No。targetSdkVersion gate は見つからない。
- compileSdk 36: deprecated API / constant warning が見える可能性あり。
- 実質条件: `View#announceForAccessibility()` または `AccessibilityEvent.TYPE_ANNOUNCEMENT` を使うこと。
- Compat Change ID: 確認できない。
- Runtime enforcement: Android 16 r4 AOSP では announcement event の抑制・変換は確認できない。

## 早見マトリクス（At-a-Glance Matrix）

| シナリオ（Scenario） | 影響（Impact） |
| --- | --- |
| Android 16 / targetSdkVersion 35 / `announceForAccessibility` | deprecated pattern。runtime dispatch は継続する見込み。 |
| Android 16 / targetSdkVersion 36 / `announceForAccessibility` | targetSdkVersion 35 と同じ。 |
| Android 16 / `TYPE_ANNOUNCEMENT` dispatch | deprecated constant。framework block は確認できない。 |
| Android 15 / targetSdkVersion 36 | Android 15 r36 tag にも flagged deprecation が見えるため、Android 16 guidance と分けて扱う。 |
| compileSdk 36 | deprecated warning / lint 対象になり得る。 |
| standard widgets only | 低リスク。framework semantics を優先。 |
| custom View manual announcements | 移行対象。semantic event / node info へ置換。 |

## 要約（Summary）

Android 16 は `announceForAccessibility()` と `TYPE_ANNOUNCEMENT` による disruptive accessibility announcements を deprecated pattern として明示する。AOSP 上は runtime blocking ではなく、API deprecation / documentation guidance が中心である。

## 顧客影響（Customer Impact）

- OS アップデートだけで announcement が必ず無効化されるとは言えない。
- targetSdkVersion 36 化だけで runtime behavior が変わる evidence はない。
- compileSdk 36 では deprecated warning が出る可能性がある。
- TalkBack の読み上げ順序・割り込み・timing に依存する UX は移行リスクが高い。
- accessibility QA では announcement text ではなく UI semantics が正しいかを確認する必要がある。

## 影響対象（Who Is Affected）

- `View#announceForAccessibility` を使うアプリ。
- `AccessibilityEvent.TYPE_ANNOUNCEMENT` を直接 dispatch するアプリ。
- custom View / custom accessibility behavior を持つアプリ。
- Compose UI と manual announcement を併用しているアプリ。
- screen / pane / dialog / bottom sheet / navigation changes を announcement で通知しているアプリ。
- validation error / form error を announcement で通知しているアプリ。
- SDK / library / cross-platform framework が announcement を内部利用するアプリ。

## 推奨対応（Recommended Actions）

- `announceForAccessibility` / `TYPE_ANNOUNCEMENT` usage を棚卸しする。
- screen / window change は `Activity#setTitle` を使う。
- pane / dialog / bottom sheet / major section change は `View#setAccessibilityPaneTitle` または Compose `paneTitle` を使う。
- critical UI update は `View#setAccessibilityLiveRegion` または Compose `liveRegion` を sparingly に使う。
- error は `AccessibilityNodeInfo#setError`、`TextView#setError`、`CONTENT_CHANGE_TYPE_ERROR` を使う。
- TalkBack だけでなく他の assistive technology でも regression test する。

## テスト観点（Test Matrix）

| 観点 | 確認内容 |
| --- | --- |
| Android 15 / targetSdkVersion 35 | baseline announcement behavior。 |
| Android 16 / targetSdkVersion 35 | OS update 後の runtime / UX 差分。 |
| Android 16 / targetSdkVersion 36 | targetSdkVersion 35 と差がないか。 |
| Android 15 / targetSdkVersion 36 | targetSdkVersion 36 だけで runtime change がないか。 |
| compileSdk 36 | deprecated warning / lint / IDE inspection。 |
| `announceForAccessibility` | event dispatch、TalkBack 読み上げ、重複。 |
| `TYPE_ANNOUNCEMENT` | custom event が service に届くか。 |
| pane title | pane appear / disappear / title change event。 |
| live region | polite / assertive と過剰通知。 |
| errors | `setError` / `CONTENT_CHANGE_TYPE_ERROR` event。 |
| SDK / library | transitive usage の検出。 |

## 顧客向け説明（Explanation for Customers）

この変更は targetSdkVersion 36 に上げた時だけの runtime change ではありません。Android 16 では、アプリが画面読み上げのために任意の文字列を直接 announcement として投げる pattern が deprecated と明示されます。

既存の announcement が Android 16 で直ちに block される evidence はありませんが、今後の互換性と accessibility UX のため、画面変更、pane 変更、critical update、error をそれぞれ意味のある semantics として提供する実装へ移行してください。

## 根拠（Evidence）

- Official documentation: https://developer.android.com/about/versions/16/behavior-changes-all#disruptive-a11y
- API reference: https://developer.android.com/reference/android/view/accessibility/AccessibilityEvent#TYPE_ANNOUNCEMENT
- Compose semantics docs: https://developer.android.com/develop/ui/compose/accessibility/semantics
- AOSP files:
  - `frameworks-base/core/java/android/view/View.java`
  - `frameworks-base/core/java/android/view/accessibility/AccessibilityEvent.java`
  - `frameworks-base/core/java/android/view/accessibility/AccessibilityNodeInfo.java`
  - `frameworks-base/core/java/android/widget/TextView.java`
  - `frameworks-base/core/java/android/app/Activity.java`
  - `frameworks-base/core/java/android/view/accessibility/flags/accessibility_flags.aconfig`
  - `frameworks-base/core/api/current.txt`
  - `frameworks-base/services/accessibility/java/com/android/server/accessibility/AccessibilitySecurityPolicy.java`
- Diff interpretation:
  - runtime dispatch block は確認できない。
  - targetSdkVersion 36 gate は確認できない。
  - API deprecation / guidance が中心。

## 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- Critical / High / Medium / Low

判断（Decision）:
- Explain / Monitor / Ignore / Further investigation required

補足:
- 最終優先度、顧客通知要否、release readiness は repository owner が判断する。
