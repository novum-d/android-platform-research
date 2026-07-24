# Predictive Back への移行または opt-out が必要 - 1ページ要約

## 対象（Target）

Android 16 Behavior Change

比較元:
- android-15.0.0_r36

比較先:
- android-16.0.0_r4

注記:
- `android16/AGENTS.md` の既定の比較先は `android-16.0.0_r1` である。この要約では、依頼に従い `android-16.0.0_r4` を確認対象とした。

## 適用条件（Applicability）

- 主分類（Primary classification）: `TARGET_SDK_36_CONDITIONAL`
- OS アップデート / 全アプリ: いいえ。targetSdkVersion 35 以下のアプリに、OS アップデートだけで適用される根拠は確認していない。
- targetSdkVersion 36 以上: はい。Android 16 の `ParsingPackageUtils` は、`targetSdk > VANILLA_ICE_CREAM` の場合に `enableOnBackInvokedCallback` を既定で `true` にする。
- その他の必須条件: Android 16 以上の端末上で動作し、従来の `onBackPressed` / `KEYCODE_BACK` の通知、または Back イベントの独自処理に依存している場合に、実質的な影響が出る。
- Compat Change ID: 見つからない
- Compat の既定状態: 公開されている compat framework changes ページに該当項目はない。manifest による opt-out と aconfig flag を確認した。

## 早見マトリクス（At-a-Glance Matrix）

| シナリオ（Scenario） | 影響（Impact） |
| --- | --- |
| Android 16 / targetSdkVersion 35 | この変更によって Predictive Back が既定で有効になることはない |
| Android 16 / targetSdkVersion 36 | Predictive Back が既定で有効になる。`onBackPressed` / `KEYCODE_BACK` に依存する処理は呼ばれない |
| Android 16 / targetSdkVersion 36 + 必須条件 | Back イベントの独自処理や従来方式の Back 処理に依存する画面で、挙動の違いが表面化する |

## 要約（Summary）

Android 16 では、targetSdkVersion 36 以上のアプリで Predictive Back のシステムアニメーションが既定で有効になる。
この状態では、従来の `onBackPressed()` と `KEYCODE_BACK` の通知に依存せず、正式に対応している Back navigation API へ移行する必要がある。

## 顧客影響（Customer Impact）

- 影響あり

## 影響対象（Who Is Affected）

- `Activity.onBackPressed()` / `Dialog.onBackPressed()` に依存しているアプリ。
- `KEYCODE_BACK` を直接処理しているアプリ。
- 独自の Back 処理があり、`OnBackInvokedCallback` または対応する AndroidX API へ移行していないアプリ。
- `android:enableOnBackInvokedCallback="false"` を使わず、従来方式の Back 処理に依存している Activity。

## 対応要否（Required Action）

- 必須対応: Back 処理の実装箇所を棚卸しし、Android 16 / targetSdkVersion 36 で Back navigation を検証する。
- 推奨対応: `OnBackInvokedCallback` または対応する AndroidX の Back navigation API へ移行する。
- 一時対応: 必要な Activity / application に限定して `android:enableOnBackInvokedCallback="false"` を指定する。
- 実装例: [Predictive Back の実装例](../../../behavior-changes/target/user-experience-and-system-ui/migration-or-opt-out-required-for-predictive-back-implementation-examples.md)
- 実行挙動比較: [Dispatcher 経由あり・なし](../../../behavior-changes/target/user-experience-and-system-ui/migration-or-opt-out-required-for-predictive-back-runtime-behavior-comparison.md)

## テストマトリクス（Test Matrix）

| 端末 OS（Device OS） | targetSdkVersion | 期待挙動（Expected behavior） |
| --- | --- | --- |
| Android 15 | 35 | 従来方式の Back 処理 |
| Android 15 | 36 | Android 15 タグでは、既定で有効にするかどうかが flag に依存する。Android 16 と同一に扱わない |
| Android 16 | 35 | targetSdkVersion 36 向けの既定有効化は適用されない |
| Android 16 | 36 | Predictive Back が有効になる。従来の `onBackPressed` / `KEYCODE_BACK` の通知は呼ばれない |
| Android 16 | 36 + manifest opt-out | 一時的な opt-out により、従来方式の Back 処理を維持する |

## 顧客向け説明（Explanation for Customers）

Android 16 で targetSdkVersion を 36 以上にすると、Predictive Back が標準で有効になります。
そのため、従来の `onBackPressed()` や `KEYCODE_BACK` を前提にした戻る処理は呼ばれなくなり、`OnBackInvokedCallback` や対応する AndroidX の Back navigation API への移行が必要です。
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
