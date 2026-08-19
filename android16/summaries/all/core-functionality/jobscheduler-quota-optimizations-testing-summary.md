# JobScheduler quota optimizations - Testing 1ページ要約

## 対象（Target）

Android 16 Behavior Change:
- JobScheduler quota optimizations

Section:
- Testing

Official documentation:
- https://developer.android.com/about/versions/16/behavior-changes-all#job-quota-opt-testing

From:
- android-15.0.0_r36

To:
- android-16.0.0_r4

Note:

## 適用条件（Applicability）

- 主分類（Primary classification）: `OS_UPDATE_ALL_APPS`
- OS アップデート / 全アプリ: Yes。Android 16 上で JobScheduler quota 管理対象 work を使うアプリに targetSdkVersion と無関係に影響し得る。
- targetSdkVersion 36 以上: No。AOSP `QuotaController` に targetSdkVersion 36 gate は見つからない。
- Testing override: あり。`am compat enable` で package 単位の override を設定できる。
- Compat Change ID:
  - `OVERRIDE_QUOTA_ENFORCEMENT_TO_TOP_STARTED_JOBS` = `374323858`
  - `OVERRIDE_QUOTA_ENFORCEMENT_TO_FGS_JOBS` = `341201311`
- Compat default state: どちらも `@Disabled` / `@Overridable`。
- 重要: `am compat enable` はこの 2 項目では enforcement を有効化するのではなく、Android 16 default enforcement を無効化して比較するために使う。

## 要約（Summary）

Android 16 では、top state 中に開始して invisible 後も続く job と、foreground service と同時実行される job が default で runtime quota に従う。Testing セクションは、この default Android 16 挙動を testing override で無効化し、旧挙動に近い状態と比較するための手順を説明している。

`adb shell am set-standby-bucket` / `adb shell am get-standby-bucket` は standby bucket による quota 差を作って確認するための diagnostic / setup command。stop reason と pending reason history と組み合わせて、job が停止したのか、開始待ちなのかを切り分ける。

## 早見マトリクス（At-a-Glance Matrix）

| シナリオ（Scenario） | 期待挙動（Expected behavior） |
| --- | --- |
| Android 16 / targetSdkVersion 35 / default | quota optimization が適用される。 |
| Android 16 / targetSdkVersion 36 / default | targetSdkVersion 35 と同じ。 |
| Android 15 / targetSdkVersion 36 | Android 16 default policy は発生しない。比較時は Android 15 feature flag 状態を記録。 |
| Top-started job / default | invisible 後も続く場合は quota 対象。 |
| Top-started job / `OVERRIDE_QUOTA_ENFORCEMENT_TO_TOP_STARTED_JOBS` enabled | enforcement が無効化され、top-started job は旧来の quota-free に近い扱い。 |
| FGS-concurrent job / default | quota 対象。 |
| FGS-concurrent job / `OVERRIDE_QUOTA_ENFORCEMENT_TO_FGS_JOBS` enabled | enforcement が無効化され、FGS process state が quota-free threshold 側に戻る。 |
| `am set-standby-bucket active` | active bucket quota をテスト。generous だが有限。 |
| `am set-standby-bucket working_set|frequent|rare|restricted` | bucket ごとの quota 差をテスト。 |
| `am get-standby-bucket` | 現在 bucket の diagnostic。 |

## 影響対象（Who Is Affected）

- JobScheduler を直接使うアプリ。
- WorkManager を使うアプリ。
- DownloadManager を使うアプリ。
- expedited jobs を使うアプリ。
- foreground service と job を併用するアプリ。
- app visible 中に job を開始し、invisible 後も継続するアプリ。
- active standby bucket なら quota 制限を受けない前提のアプリ。
- long-running upload / download / sync を ordinary job で実装しているアプリ。
- user-visible data transfer を user-initiated data transfer job へ移行すべきアプリ。
- stop reason / pending reason をログ化していないアプリ。
- Android 16 quota behavior を compat override で比較検証する必要があるアプリ。

## テスト観点（Test Points）

| 観点 | 確認内容 |
| --- | --- |
| OS / targetSdkVersion | Android 15 target 35、Android 16 target 35、Android 16 target 36、可能なら Android 15 target 36 を比較。 |
| Default enforcement | regular / expedited job、top-started job、FGS-concurrent job が quota 対象になるか確認。 |
| Top override | `OVERRIDE_QUOTA_ENFORCEMENT_TO_TOP_STARTED_JOBS` enabled / disabled の差を確認。 |
| FGS override | `OVERRIDE_QUOTA_ENFORCEMENT_TO_FGS_JOBS` enabled / disabled の差を確認。 |
| Standby bucket | `am set-standby-bucket` で active / working_set / frequent / rare / restricted を切り替える。 |
| Bucket diagnostic | `am get-standby-bucket` で現在 bucket を記録。 |
| Stop reason | `JobParameters#getStopReason()` または WorkManager `WorkInfo#getStopReason()` をログ化。 |
| Pending reason | `JobScheduler#getPendingJobReasonsHistory()` で開始しない理由を確認。 |
| Ordinary vs UIJ | ordinary upload/download job と user-initiated data transfer job を比較。 |

## 根拠（Evidence）

- Official documentation: https://developer.android.com/about/versions/16/behavior-changes-all#job-quota-opt-testing
- AOSP source context:
  - `QuotaController.OVERRIDE_QUOTA_ENFORCEMENT_TO_TOP_STARTED_JOBS`
  - `QuotaController.OVERRIDE_QUOTA_ENFORCEMENT_TO_FGS_JOBS`
  - `QuotaController.prepareForExecutionLocked()`
  - `QuotaController.isTopStartedJobLocked()`
  - `QuotaController.getProcessStateQuotaFreeThreshold()`
  - `ActivityManagerShellCommand.runCompat()`
  - `PlatformCompat.setOverrides()`
  - `ActivityManagerShellCommand.runSetStandbyBucket()`
  - `ActivityManagerShellCommand.runGetStandbyBucket()`
  - `AppStandbyController.setAppStandbyBucket()` / `getAppStandbyBucket()`
  - `JobStatus.constraintToStopReason()`
  - `JobSchedulerService#getPendingJobReasonsHistory()`
- Diff interpretation:
  - Android 16 default では top-started / FGS-concurrent job が quota enforcement の通常経路に入る。
  - compat override enabled は enforcement を無効化する testing path。
  - standby bucket command は UsageStats/AppStandbyController 経由で JobScheduler quota testing に使える。
- Gate conclusion:
  - targetSdkVersion gate なし。Android 16 OS / JobScheduler 実装上の all apps 変更。

## 顧客向け説明（Customer Explanation）

Android 16 の JobScheduler quota testing では、default 挙動と override 挙動を分けて確認してください。`am compat enable OVERRIDE_QUOTA_ENFORCEMENT_TO_TOP_STARTED_JOBS` と `am compat enable OVERRIDE_QUOTA_ENFORCEMENT_TO_FGS_JOBS` は、新しい制限を有効化するためのコマンドではなく、Android 16 の default enforcement を無効化して比較するためのコマンドです。

この項目は targetSdkVersion 36 化の影響ではありません。Android 16 へ OS アップデートした時の JobScheduler quota policy として説明し、targetSdkVersion 35 / 36 の比較、compat override enabled / disabled の比較、standby bucket の比較を別々に記録してください。

## Human Decision Placeholder

最終優先度（Final Priority）:
- Critical / High / Medium / Low

判断（Decision）:
- Explain / Monitor / Ignore / Further investigation required

補足:
- 最終優先度、顧客通知要否、release readiness は repository owner が判断する。
