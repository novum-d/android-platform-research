# Abandoned empty jobs stop reason 1ページ要約

## 対象（Target）

Android 16 Behavior Change:
- Abandoned empty jobs stop reason

Official documentation:
- https://developer.android.com/about/versions/16/behavior-changes-all#abandoned-job-stop-reason

From:
- android-15.0.0_r36

To:
- android-16.0.0_r4

Note:

## 適用条件（Applicability）

- 主分類（Primary classification）: `OS_UPDATE_ALL_APPS`
- OS アップデート / 全アプリ: Yes。Android 16 上で direct `JobScheduler` / `JobService` を使うアプリに targetSdkVersion と無関係に影響し得る。
- targetSdkVersion 36 以上: No。AOSP の abandoned job 判定・timeout stop reason 設定経路に targetSdkVersion 36 gate は見つからない。
- 必須条件: `onStartJob()` で非同期継続し、`JobParameters` strong reference を失い、`jobFinished()` を呼ばないまま timeout すること。
- Compat Change ID:
  - `OVERRIDE_HANDLE_ABANDONED_JOBS` = `372529068`
- Compat default state:
  - `@Disabled` / `@Overridable`
- Semantics:
  - override enabled の場合は abandoned handling / `STOP_REASON_TIMEOUT_ABANDONED` reporting を抑止する方向に働く。

## 要約（Summary）

Android 16 では、direct `JobScheduler` / custom `JobService` の job が `JobParameters` を失い、`jobFinished()` を呼ばないまま timeout した場合、通常の `STOP_REASON_TIMEOUT` ではなく `STOP_REASON_TIMEOUT_ABANDONED` として報告される可能性がある。

この stop reason は app 側の lifecycle bug を見つけるための signal。さらに `STOP_REASON_TIMEOUT_ABANDONED` が繰り返されると、AOSP では abandoned failure count を増やし、閾値超過後に aggressive backoff を使う経路があるため、job frequency が下がり得る。

## 早見マトリクス（At-a-Glance Matrix）

| シナリオ（Scenario） | 期待挙動（Expected behavior） |
| --- | --- |
| Android 16 / targetSdkVersion 35 / direct JobScheduler | 条件を満たすと `STOP_REASON_TIMEOUT_ABANDONED` が発生し得る。 |
| Android 16 / targetSdkVersion 36 / direct JobScheduler | targetSdkVersion 35 と同じ。 |
| Android 15 / targetSdkVersion 36 | Android 16 all-apps behavior としては扱わない。flag 状態を記録して比較。 |
| JobService keeps strong JobParameters reference | abandoned 判定されにくい。 |
| JobService loses JobParameters reference | cleaner callback により abandoned mark され得る。 |
| jobFinished() called | cleaner disabled、正常完了扱い。 |
| jobFinished() not called | timeout し得る。JobParameters 喪失時は abandoned timeout。 |
| timeout with retained JobParameters | `STOP_REASON_TIMEOUT`。 |
| timeout with abandoned JobParameters | `STOP_REASON_TIMEOUT_ABANDONED`。 |
| single abandoned occurrence | stop reason として観測。 |
| frequent abandoned occurrences | aggressive backoff による frequency mitigation があり得る。 |
| WorkManager task | 公式文書上は非影響。 |
| DownloadManager task | 公式文書上は非影響。 |
| AsyncTask usage | 公式文書上は非影響。ただし direct JobService 内の自前 lifecycle bug は別。 |

## 影響対象（Who Is Affected）

- JobScheduler を直接使うアプリ。
- JobService を独自実装しているアプリ。
- `onStartJob()` から非同期処理を開始するアプリ。
- `JobParameters` を strong reference として保持していないアプリ。
- `jobFinished()` 呼び出し漏れがあり得るアプリ。
- timeout / retry / reschedule を前提にしているアプリ。
- stop reason を `STOP_REASON_TIMEOUT` としてしか扱っていないアプリ。
- `JobParameters#getStopReason()` をログ化していないアプリ。
- repeated timeout / job frequency mitigation に影響を受けるアプリ。

## テスト観点（Test Points）

| 観点 | 確認内容 |
| --- | --- |
| OS / targetSdkVersion | Android 15 target 35、Android 16 target 35、Android 16 target 36、可能なら Android 15 target 36 を比較。 |
| Direct JobScheduler | custom JobService で `onStartJob()` が true を返す非同期 job を検証。 |
| JobParameters retained | strong reference を保持し、`jobFinished()` を呼ぶ場合に abandoned が出ないこと。 |
| JobParameters lost | reference を失い、`jobFinished()` を呼ばない場合に abandoned timeout になること。 |
| Stop reason | `STOP_REASON_TIMEOUT` と `STOP_REASON_TIMEOUT_ABANDONED` を分けてログ化。 |
| Repeated occurrences | abandoned timeout を繰り返し、backoff / frequency mitigation を確認。 |
| Managed APIs | WorkManager / DownloadManager / AsyncTask で公式非影響主張を実機で確認。 |
| Diagnostics | dumpsys jobscheduler、logs、metrics、retry / reschedule / backoff behavior を確認。 |

## 根拠（Evidence）

- Official documentation: https://developer.android.com/about/versions/16/behavior-changes-all#abandoned-job-stop-reason
- AOSP source context:
  - `JobParameters.STOP_REASON_TIMEOUT_ABANDONED`
  - `JobParameters.OVERRIDE_HANDLE_ABANDONED_JOBS`
  - `JobParameters.enableCleaner()` / `disableCleaner()`
  - `JobParameters.JobCleanupCallback#run()`
  - `JobServiceEngine.JobHandler#MSG_EXECUTE_JOB`
  - `JobServiceEngine.JobHandler#MSG_JOB_FINISHED`
  - `JobService#onStartJob()` / `jobFinished()`
  - `JobServiceContext#doHandleAbandonedJob()`
  - `JobServiceContext#handleOpTimeoutLocked()`
  - `JobSchedulerService#getRescheduleJobForFailureLocked()`
  - `JobSchedulerService#shouldUseAggressiveBackoff()`
  - `JobServiceContextTest`
  - `JobSchedulerServiceTest`
- Diff interpretation:
  - `STOP_REASON_TIMEOUT_ABANDONED` は Android 15 tag にも flagged API として存在するため、単純な API 追加ではない。
  - Android 16 では hidden compat override と abandoned handling / mitigation の条件が明確化されている。
  - targetSdkVersion 36 gate は該当経路に見つからない。

## 顧客向け説明（Customer Explanation）

Android 16 では、direct `JobScheduler` / `JobService` の非同期 job が `JobParameters` を失い、`jobFinished()` を呼ばずに timeout すると、`STOP_REASON_TIMEOUT_ABANDONED` が報告される可能性があります。これは targetSdkVersion 36 化の影響ではなく、Android 16 へ OS アップデートした時の all-apps behavior として説明してください。

この stop reason が出た場合、単なる timeout ではなく、アプリが job lifecycle を失っている可能性を優先的に確認します。頻発すると backoff が強くなり、job の再実行頻度が下がる可能性があります。

## Human Decision Placeholder

最終優先度（Final Priority）:
- Critical / High / Medium / Low

判断（Decision）:
- Explain / Monitor / Ignore / Further investigation required

補足:
- 最終優先度、顧客通知要否、release readiness は repository owner が判断する。
