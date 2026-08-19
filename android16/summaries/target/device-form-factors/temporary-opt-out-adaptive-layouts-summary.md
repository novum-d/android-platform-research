# Temporary opt-out - 1ページ要約（One Page Summary）

## 対象（Target）

Android 16 Behavior Change

From:
- android-15.0.0_r36

To:
- android-16.0.0_r4

Note:

## 適用条件（Applicability）

- 主分類（Primary classification）: `TARGET_SDK_36_CONDITIONAL`
- OS アップデート / 全アプリ（OS update / all apps）: No。Android 16 へ OS アップデートしただけで targetSdkVersion 35 以下の全アプリに既定適用されるとは判断しない。
- targetSdkVersion 36 以上: Yes。`UNIVERSAL_RESIZABLE_BY_DEFAULT` / 357141415 が targetSdkVersion 36 以上で default enabled。
- その他の必須条件（Other required conditions）: Android 16 以上、display `sw >= 600dp`、game ではない、user aspect ratio setting exception なし。
- Temporary opt-out: `android.window.PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY=true` を application または activity property として指定。
- Compat Change ID: `UNIVERSAL_RESIZABLE_BY_DEFAULT` / 357141415
- Compat default state: Android 16 / API level 36 以上を target するアプリで enabled。
- Future scope: 公式文書は API level 37 target では opt-out が適用されないと説明。AOSP に SDK 37 removal TODO がある。

## 公式文書との差分（Documentation Drift）

確認時点の公式見出しは `Opt out temporarily`。

依頼文の「Support for this property will be removed in the next Android release」は、現在の公式本文では「future Android release で API level 37 を target すると適用されない」と表現されている。実質的には同じ方向性だが、summary では API 37 target 条件として扱う。

## 早見マトリクス（At-a-Glance Matrix）

| シナリオ | 期待挙動 |
| --- | --- |
| Android 16 / targetSdkVersion 35 | targetSdkVersion 36 起因の base behavior は既定適用対象外 |
| Android 16 / targetSdkVersion 36 / `sw >= 600dp` / no opt-out | orientation / resizability / aspect ratio restrictions は無視 |
| Android 16 / targetSdkVersion 36 / `sw >= 600dp` / Application-level opt-out | 全 activity が universal resizable path から外れる |
| Android 16 / targetSdkVersion 36 / `sw >= 600dp` / Activity-level opt-out | 該当 activity のみ universal resizable path から外れる |
| Android 16 / targetSdkVersion 36 / both Application-level and Activity-level opt-out | application-level true により全 activity opt-out |
| Android 16 / targetSdkVersion 36 / opt-out false | opt-out なしと同等 |
| Android 16 / targetSdkVersion 36 / `sw < 600dp` | large screen gate を満たさないため base behavior 対象外 |
| Android 16 / targetSdkVersion 36 / game app | game exception により base behavior 対象外 |
| Android 16 / targetSdkVersion 36 / user aspect ratio setting exception | user preference により base behavior から外れる |
| Android 15 / targetSdkVersion 36 | Android 16 の large screen default ignore 差分はないため、同一挙動とは結論しない |

## 要約（Summary）

`Temporary opt-out` は、Android 16 adaptive layouts の base behavior を一時的に抑止する manifest property mechanism である。
`PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY=true` を `<application>` に置くと全 activity、`<activity>` に置くと該当 activity が opt-out される。
AOSP では `AppCompatResizeOverrides` が application-level property を先に読み、true でなければ activity-level property を読む。true の場合、`ActivityRecord#isUniversalResizeable()` が false になり、base behavior から外れる。

## 顧客影響（Customer Impact）

- 要確認

理由:
- opt-out は Android 16 / targetSdkVersion 36 / large screen で base behavior が問題になる場合の一時策。
- application-level opt-out は全 activity に効くため、対応済み activity まで previous behavior に戻す可能性がある。
- API 37 以降は使えない前提で、adaptive layout 対応が必要。

## 影響対象（Who Is Affected）

- temporary opt-out を検討しているアプリ。
- Application-level opt-out を指定するアプリ。
- Activity-level opt-out を指定するアプリ。
- mixed opt-out strategy を使うアプリ。
- portrait / landscape 固定に依存するアプリ。
- `resizeableActivity=false` に依存するアプリ。
- `minAspectRatio` / `maxAspectRatio` に依存するアプリ。
- pillarboxing / compatibility mode に依存するアプリ。
- large screen / tablet / foldable / desktop windowing 対応が未完了のアプリ。
- games。
- Compose UI / View UI のどちらも対象。

## 対応要否（Required Action）

- 必須対応: targetSdkVersion 36 化する large screen 対応対象アプリで、base behavior により UI が崩れる場合。
- 推奨: application-level opt-out より先に activity-level opt-out で最小範囲に限定できるか検討する。
- 要確認: property false / 未指定では opt-out されない。
- 要確認: manifest merge 後の final manifest に property が期待通り入っているか確認する。
- 恒久対応: API 37 以降に向け、adaptive layout、window metrics、multi-window / desktop windowing、state preservation に対応する。

## テストマトリクス（Test Matrix）

| 端末 OS | targetSdkVersion | 条件 | 期待挙動 / 確認点 |
| --- | --- | --- | --- |
| Android 15 | 35 | baseline | 従来挙動 |
| Android 16 | 35 | OS update only | targetSdkVersion 36 起因の base behavior は既定適用対象外 |
| Android 16 | 36 | `sw >= 600dp` / no opt-out | restrictions は無視 |
| Android 16 | 36 | Application-level opt-out true | 全 activity が previous behavior / compatibility mode 側 |
| Android 16 | 36 | Activity-level opt-out true | 指定 activity のみ previous behavior / compatibility mode 側 |
| Android 16 | 36 | Application-level true + Activity-level true | 全 activity が opt-out |
| Android 16 | 36 | opt-out false | opt-out なしと同等 |
| Android 16 | 36 | `sw < 600dp` | base behavior 対象外 |
| Android 16 | 36 | game / user setting exception | base behavior 対象外または抑止 |

追加テスト:
- Android 15 / targetSdkVersion 36 が検証可能な場合の比較。
- `screenOrientation` / `setRequestedOrientation()` / `getRequestedOrientation()` の opt-out 有無による差。
- `resizeableActivity=false`、`minAspectRatio`、`maxAspectRatio` 指定あり / なし。
- full-screen と multi-window。
- pillarboxing / compatibility mode の有無。
- visual regression / screenshot testing。

## 顧客向け説明（Explanation for Customers）

Android 16 へ OS アップデートしただけで、targetSdkVersion 35 以下のアプリにこの変更が既定適用されるとは説明しません。
targetSdkVersion 36 以上に上げると、Android 16 端末の large screen では orientation / resizability / aspect ratio restrictions が無視されます。
Android 16 では `PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY=true` により一時的に previous behavior / compatibility mode 側へ戻せますが、API 37 以降の恒久策ではありません。

## 根拠（Evidence）

- Official documentation: https://developer.android.com/about/versions/16/behavior-changes-16#temporary-opt-out
- Compat framework: `UNIVERSAL_RESIZABLE_BY_DEFAULT` / 357141415、Android 16 / API 36 以上 target で enabled。
- AOSP files: `ActivityInfo.java`、`WindowManager.java`、`PackageManager.java`、`DisplayContent.java`、`ActivityRecord.java`、`AppCompatResizeOverrides.java`、`AppCompatAspectRatioPolicy.java`。
- AOSP source context: manifest property -> `PackageManager#getPropertyAsUser()` -> `AppCompatResizeOverrides#allowRestrictedResizability()` -> `ActivityRecord#isUniversalResizeable()`。
- Diff interpretation: Android 16 tag で large screen default ignore 経路が追加。opt-out true は universal resizable path を抑止する。
- API surface: property は public current / test-current には出ない hidden property。manifest property name 文字列として指定する。

## 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- 未判断

判断（Decision）:
- 未判断

Owner notes:
- 最終優先度、severity、release readiness、顧客 communication priority は repository owner が判断する。
