# Migration or opt-out required for predictive back - 1ページ要約（One Page Summary）

## 対象（Target）

Android 16 Behavior Change

From:
- android-15.0.0_r36

To:
- android-16.0.0_r4

Note:
- `android16/AGENTS.md` の既定 scope は `android-16.0.0_r1`。この要約は依頼に従い `android-16.0.0_r4` を確認対象にした。

## 適用条件（Applicability）

- 主分類（Primary classification）: `TARGET_SDK_36_CONDITIONAL`
- OS アップデート / 全アプリ（OS update / all apps）: No。targetSdkVersion 35 以下のアプリに OS アップデートだけで適用される根拠は確認していない。
- targetSdkVersion 36 以上: Yes。Android 16 の `ParsingPackageUtils` は `targetSdk > VANILLA_ICE_CREAM` で `enableOnBackInvokedCallback` を default true にする。
- その他の必須条件（Other required conditions）: Android 16 以上の端末上で動作し、legacy `onBackPressed` / `KEYCODE_BACK` dispatch または back event intercept に依存している場合に実質影響が出る。
- Compat Change ID: Not found
- Compat default state: 公開 compat framework changes ページに該当 entry なし。manifest opt-out と aconfig flag を確認。

## 早見マトリクス（At-a-Glance Matrix）

| シナリオ（Scenario） | 影響（Impact） |
| --- | --- |
| Android 16 / targetSdkVersion 35 | 本変更による predictive back default enable は適用されない |
| Android 16 / targetSdkVersion 36 | predictive back が default enabled。`onBackPressed` / `KEYCODE_BACK` 依存処理は呼ばれない |
| Android 16 / targetSdkVersion 36 + 必須条件 | back intercept / legacy back handling 依存画面で挙動差分が顕在化する |

## 要約（Summary）

Android 16 では、targetSdkVersion 36 以上のアプリで predictive back system animations が default enabled になる。
この状態では legacy `onBackPressed()` と `KEYCODE_BACK` dispatch に依存せず、supported back navigation APIs へ移行する必要がある。

## 顧客影響（Customer Impact）

- 影響あり

## 影響対象（Who Is Affected）

- `Activity.onBackPressed()` / `Dialog.onBackPressed()` に依存するアプリ。
- `KEYCODE_BACK` を直接処理しているアプリ。
- custom back handling を持つが `OnBackInvokedCallback` / AndroidX supported APIs に未移行のアプリ。
- `android:enableOnBackInvokedCallback="false"` を使っていない legacy back handling 依存 Activity。

## 対応要否（Required Action）

- 必須対応: back handling の利用箇所を棚卸しし、Android 16 / targetSdkVersion 36 で back navigation を検証する。
- 推奨対応: `OnBackInvokedCallback` または AndroidX supported back navigation APIs へ移行する。
- 一時対応: 必要な Activity / application に限定して `android:enableOnBackInvokedCallback="false"` を指定する。
- 実装例: [Predictive back implementation examples](../../../behavior-changes/target/user-experience-and-system-ui/migration-or-opt-out-required-for-predictive-back-implementation-examples.md)
- 実行挙動比較: [Dispatcher 経由あり・なし](../../../behavior-changes/target/user-experience-and-system-ui/migration-or-opt-out-required-for-predictive-back-runtime-behavior-comparison.md)

## テストマトリクス（Test Matrix）

| 端末 OS（Device OS） | targetSdkVersion | 期待挙動（Expected behavior） |
| --- | --- | --- |
| Android 15 | 35 | legacy back behavior |
| Android 15 | 36 | Android 15 tag では default enable が flag 依存。Android 16 と同一扱いしない |
| Android 16 | 35 | target 36 default enabled にはならない |
| Android 16 | 36 | predictive back enabled。legacy `onBackPressed` / `KEYCODE_BACK` dispatch は呼ばれない |
| Android 16 | 36 + manifest opt-out | temporary opt-out により legacy back behavior を維持する |

## 顧客向け説明（Explanation for Customers）

Android 16 で targetSdkVersion を 36 以上にすると、predictive back が標準で有効になります。
そのため、従来の `onBackPressed()` や `KEYCODE_BACK` を前提にした戻る処理は呼ばれなくなり、`OnBackInvokedCallback` や AndroidX の supported back navigation APIs への移行が必要です。
移行が間に合わない画面では、暫定的に `android:enableOnBackInvokedCallback="false"` を指定できます。

## 根拠（Evidence）

- Official documentation: https://developer.android.com/about/versions/16/behavior-changes-16#predictive-back
- AOSP files: `ParsingPackageUtils.java`, `ParsedActivityUtils.java`, `ApplicationInfo.java`, `ActivityInfo.java`, `WindowOnBackInvokedDispatcher.java`, `ViewRootImpl.java`, `Activity.java`, `windowing_frontend.aconfig`
- AOSP source context: package parsing で targetSdkVersion 36 以上の default が true になり、window dispatcher / input stage が back event を `OnBackInvokedCallback` path に切り替える。
- Diff interpretation: changed condition / changed default / removed legacy dispatch。Android 15 の flag 依存 default から Android 16 の targetSdkVersion 36 default enable へ変わる。
- Gate conclusion: Android 16 以上かつ targetSdkVersion 36 以上で適用。実質影響は legacy back handling に依存するアプリに限定される。

## 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- Critical / High / Medium / Low

判断（Decision）:
- Explain / Monitor / Ignore / Further investigation required
