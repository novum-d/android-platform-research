# Fully deprecating JobInfo#setImportantWhileForeground 1ページ要約

## 対象（Target）

Android 16 Behavior Change:
- Fully deprecating JobInfo#setImportantWhileForeground

Official documentation:
- https://developer.android.com/about/versions/16/behavior-changes-all#jobinfo-setimportantwhileforeground

From:
- android-15.0.0_r36

To:
- android-16.0.0_r4

Note:

## 適用条件（Applicability）

- 主分類（Primary classification）: `OS_UPDATE_ALL_APPS`
- OS アップデート / 全アプリ: Yes。Android 16 上で `JobInfo.Builder#setImportantWhileForeground()` / `JobInfo#isImportantWhileForeground()` を使うアプリに targetSdkVersion と無関係に影響し得る。
- targetSdkVersion 36 以上: No。AOSP の該当実装に targetSdkVersion 36 gate は見つからない。
- 必須条件: deprecated API を使い、important-while-foreground による priority / quota / doze relaxation / thermal restriction 例外を期待していること。
- Public compat Change ID: 見つからない。
- AOSP aconfig flag:
  - `android.app.job.ignore_important_while_foreground`
  - bug: `374175032`
  - Android 15 では条件分岐に使われていたが、Android 16 の public API 実装は unconditional no-op / false。

## 要約（Summary）

Android 16 では、`JobInfo.Builder#setImportantWhileForeground(true)` を呼んでも job は important-while-foreground として扱われない。builder は warning log を出して `return this` するだけで、`FLAG_IMPORTANT_WHILE_FOREGROUND` や priority を変更しない。

`JobInfo#isImportantWhileForeground()` も Android 16 では常に `false` を返す。

これはtargetSdkVersion 36化の影響ではなく、Android 16 all appsのOS behavior change。Android 12からのdeprecationと、Android 16で呼び出しても動作が変わらなくなるruntime behavior changeを分けて説明する。

## 早見マトリクス（At-a-Glance Matrix）

| シナリオ（Scenario） | 期待挙動（Expected behavior） |
| --- | --- |
| Android 16 / targetSdkVersion 35 / `setImportantWhileForeground(true)` | ignored。flag / priority は変更されない。 |
| Android 16 / targetSdkVersion 36 / `setImportantWhileForeground(true)` | target 35 と同じ。 |
| Android 16 / `setImportantWhileForeground(false)` | ignored。 |
| Android 16 / `JobInfo#isImportantWhileForeground()` | 常に false。 |
| Android 16 / direct JobScheduler job | important-while-foreground の特別扱いは得られない。 |
| Android 16 / WorkManager task | Jetpack 実装次第。deprecated API に依存していなければ低影響。 |
| Android 16 / app foreground when scheduling | この API による特別扱いはない。 |
| Android 16 / app background when scheduling | この API による特別扱いはない。 |
| Android 16 / temporary background restriction exemption | この API では doze relaxation を期待できない。 |
| Android 16 / priority or quota relying on important-while-foreground | 成立しない。 |
| Android 16 / expedited job alternative | 用途が合えば `setExpedited(true)` を検討。 |
| Android 16 / user-initiated data transfer job alternative | user-visible data transfer なら `setUserInitiated(true)` と permission を検討。 |
| Android 16 / foreground service alternative | ユーザー可視の継続処理なら FGS policy と合わせて検討。 |
| Android 15 / targetSdkVersion 36 / same app | baseline。flag 状態により従来挙動が残る可能性あり。 |

## 影響対象（Who Is Affected）

- `JobScheduler` を直接使うアプリ。
- `JobInfo.Builder#setImportantWhileForeground(true)` を呼ぶアプリ。
- `JobInfo#isImportantWhileForeground()` の戻り値に依存するアプリ。
- foreground 中の job を重要扱いにする前提のアプリ。
- temporary background restriction exemption 中の job behavior に依存するアプリ。
- priority / quota / timing を important-while-foreground に依存しているアプリ。
- legacy JobScheduler code を持つアプリ。
- SDK / library が `setImportantWhileForeground(true)` を内部で呼ぶアプリ。
- expedited jobs / user-initiated data transfer jobs / foreground services へ移行すべきアプリ。

## テスト観点（Test Points）

| 観点 | 確認内容 |
| --- | --- |
| OS / targetSdkVersion | Android 15 target 35、Android 16 target 35、Android 16 target 36、可能なら Android 15 target 36 を比較。 |
| setter true | `setImportantWhileForeground(true)` 後に `isImportantWhileForeground()` が false になること。 |
| setter false | `setImportantWhileForeground(false)`が実際の動作を変えないこと。 |
| dumpsys / persistence | scheduled job の flags / priority / dumpsys jobscheduler 表示。 |
| foreground scheduling | app foreground state でもこの API の特別扱いがないこと。 |
| background scheduling | app background state でも同様に no-op であること。 |
| temporary allowlist | temporary background restriction exemption 中に doze relaxation を期待できないこと。 |
| alternatives | expedited job、user-initiated data transfer job、foreground service との比較。 |
| library usage | WorkManager / SDK 経由で deprecated API が使われていないか。 |
| diagnostics | warning log、job stop reason、execution timing、quota、retry behavior。 |

## 根拠（Evidence）

- Official documentation: https://developer.android.com/about/versions/16/behavior-changes-all#jobinfo-setimportantwhileforeground
- AOSP source context:
  - `apex/jobscheduler/framework/java/android/app/job/JobInfo.java`
    - `JobInfo#isImportantWhileForeground()`
    - `JobInfo.Builder#setImportantWhileForeground(boolean)`
    - `FLAG_IMPORTANT_WHILE_FOREGROUND`
    - `flags` parcel / builder path
  - `apex/jobscheduler/framework/aconfig/job.aconfig`
    - `ignore_important_while_foreground`
  - `apex/jobscheduler/service/java/com/android/server/job/controllers/DeviceIdleJobsController.java`
  - `apex/jobscheduler/service/java/com/android/server/job/controllers/QuotaController.java`
  - `apex/jobscheduler/service/java/com/android/server/job/restrictions/ThermalStatusRestriction.java`
  - `core/api/current.txt`
- Diff interpretation:
  - Android 15: flag 状態により `setImportantWhileForeground(true)` が flag と priority を設定し得る。
  - Android 16: setter は常に ignored、getter は常に false。
  - Android 16: controller 側から important-while-foreground の特別扱いが削除。
  - targetSdkVersion 36 gate は見つからない。

## 顧客向け説明（Customer Explanation）

Android 16 では、`JobInfo.Builder#setImportantWhileForeground(true)` を呼んでも job は重要扱いされません。`JobInfo#isImportantWhileForeground()` も常に `false` を返します。

これはtargetSdkVersion 36に上げた時の影響ではなく、Android 16にOSアップデートした端末上で発生するall-apps behaviorです。Android 12からdeprecatedだったAPIが、Android 16では呼び出しても実際の動作を変えないno-opになったと説明してください。

該当 API に priority / quota / doze relaxation を依存させている場合は、用途に応じて expedited job、user-initiated data transfer job、foreground service、または通常 job へ整理し直す必要があります。

## Human Decision Placeholder

最終優先度（Final Priority）:
- Critical / High / Medium / Low

判断（Decision）:
- Explain / Monitor / Ignore / Further investigation required

補足:
- 最終優先度、顧客通知要否、release readiness は repository owner が判断する。

## 再検証記録（2026-08-22）

- Android 16 の公式 Behavior Change 一覧と最新通常AOSPタグを再確認した。
- 対応する[主レポート](../../../behavior-changes/all/core-functionality/fully-deprecating-jobinfo-setimportantwhileforeground.md)で official section、AOSP project / remote / checkout、解決済み commit、比較 command、dirty risk を再検証した。
- 主レポートの分類、confidence、未確認事項を維持し、実機未実施の項目を Observed 済みへ変更していない。
- 全件の結果は[再検証台帳](../../../analysis/REVALIDATION_2026-08-22.md)を参照する。
