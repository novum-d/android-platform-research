# Abandoned empty jobs stop reason 調査レポート

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
- https://developer.android.com/about/versions/16/behavior-changes-all#abandoned-job-stop-reason

Page:
- Behavior changes: all apps

Category:
- Core functionality

Section:
- Abandoned empty jobs stop reason

### 分類スナップショット（Classification Snapshot）

主分類（Primary classification）:
- `OS_UPDATE_ALL_APPS`

早見表（At-a-glance impact）:

| 確認項目（Question） | 回答（Answer） | 根拠（Evidence） |
| --- | --- | --- |
| Android 16 に OS アップデートしただけで適用されるか | Yes | 公式 all apps ページに掲載。AOSP の abandoned job 判定・stop reason 設定経路に targetSdkVersion 36 gate は見つからない。 |
| targetSdkVersion 36 以上が必要か | No | `JobServiceContext` / `JobParameters` / `JobSchedulerService` の abandoned job 経路は `Flags.handleAbandonedJobs()` と compat override を見るが、targetSdkVersion 36 を参照しない。 |
| 追加の実行時条件があるか | Yes | 直接 `JobScheduler` / `JobService` を使い、`onStartJob()` で非同期継続を示した後、`JobParameters` への strong reference を失い、`jobFinished()` を呼ばないまま timeout する場合。 |
| 新しい stop reason があるか | Yes | `JobParameters.STOP_REASON_TIMEOUT_ABANDONED = 16`。API surface 上は Android 15 tag にも flagged API として存在するが、Android 16 all apps 変更として公式文書が案内している。 |
| mitigation があるか | Yes | abandoned timeout 回数を `mNumAbandonedFailures` として数え、閾値超過後に aggressive backoff を使う経路がある。 |
| Compat Change ID が関係するか | Yes | Hidden compat change `OVERRIDE_HANDLE_ABANDONED_JOBS = 372529068`。`@Disabled` / `@Overridable`。enabled の場合は abandoned handling / report を抑止する方向に働く。 |

### 調査日（Investigation Date）

2026-07-04

### 信頼度（Confidence）

- High

理由:
- 公式文書の all apps セクションを再確認し、依頼された Original statements と一致することを確認した。
- AOSP `JobParameters`、`JobServiceEngine`、`JobServiceContext`、`JobSchedulerService`、`JobStatus`、unit test で abandoned 判定、timeout stop reason、backoff mitigation の経路を確認した。
- targetSdkVersion 36 gate は該当経路には見つからない。
- WorkManager / DownloadManager / AsyncTask の非影響は公式文書上の主張として扱い、AOSP で確認できる direct JobScheduler lifecycle の範囲と分けて記録した。

### 適用条件分類（Applicability Classification）

適用される条件（Applies when）:
- [x] OS update / all apps on Android 16 regardless of targetSdkVersion
- [ ] targetSdkVersion >= 36 on Android 16+
- [ ] targetSdkVersion >= 36, with additional runtime conditions
- [ ] Mainline / Google Play system update dependent
- [ ] API addition only, not a behavior change
- [ ] Unknown / needs more evidence

必要な実行時条件（Required runtime conditions）:
- Android version: Android 16
- targetSdkVersion: 条件なし。35 と 36 の両方で同じ platform behavior が期待される。
- API condition: direct `JobScheduler` / `JobService` usage。
- Lifecycle condition: `onStartJob()` が true を返す、または job が active のまま非同期継続する。
- Bug condition: `JobParameters` strong reference を失い、`JobService#jobFinished(JobParameters, boolean)` を呼べない状態になる。
- Timeout condition: job が最大実行時間まで到達し、timeout stop が発生する。
- Mitigation condition: `STOP_REASON_TIMEOUT_ABANDONED` が繰り返し発生し、abandoned failure count が閾値を超える。

Compat framework:
- Change ID: `372529068`
- Change name: `OVERRIDE_HANDLE_ABANDONED_JOBS`
- Default state: `@Disabled`
- Toggleable for testing: Yes。`@Overridable`
- Semantics: enabled のとき abandoned job handling と `STOP_REASON_TIMEOUT_ABANDONED` reporting を抑止する方向に働く。
- Official compat framework page: 2026-07-04 時点の検索では該当名 / ID は見つからなかった。AOSP hidden compat change として確認した。

分類信頼度（Classification confidence）:
- High

分類根拠（Classification evidence）:
- Official documentation page: `behavior-changes-all` の `Abandoned empty jobs stop reason`。
- AOSP targetSdk gate: abandoned job 判定・stop reason 設定経路には見つからない。
- Compat framework entry: AOSP `JobParameters.OVERRIDE_HANDLE_ABANDONED_JOBS`。
- Expected behavior: Android 16 / targetSdkVersion 35 と Android 16 / targetSdkVersion 36 で同じ。

---

# エグゼクティブサマリー（Executive Summary）

Android 16 では、`JobService#onStartJob()` から非同期処理を開始した direct `JobScheduler` 利用アプリが、`JobParameters` への strong reference を失い、`jobFinished()` を呼ばないまま timeout した場合、従来の一般的な `STOP_REASON_TIMEOUT` ではなく、`STOP_REASON_TIMEOUT_ABANDONED` として報告される。

これは targetSdkVersion 36 化だけで発生する変更ではなく、Android 16 all apps の OS behavior change として扱う。targetSdkVersion 35 のままでも、該当する direct JobScheduler / JobService lifecycle bug がある場合は影響し得る。

この stop reason は単なるログ値ではなく、app 側が `JobParameters` lifecycle bug を検出するための signal である。さらに、同じ job で abandoned timeout が繰り返されると、AOSP では abandoned failure count を使って aggressive backoff に切り替える経路があるため、job frequency が下がる可能性がある。

---

# 公式ドキュメント確認（Original Documentation）

## 原文（Statements）

公式文書では次を説明している。

- abandoned job は、job に関連付く `JobParameters` object が garbage collected された一方で、完了通知として `JobService#jobFinished(JobParameters, boolean)` が呼ばれていない場合に発生する。
- これは、アプリが認識しないまま job が実行・再スケジュールされている可能性を示す。
- `JobScheduler` に依存し、`JobParameters` の strong reference を維持せず、timeout するアプリには、従来の `STOP_REASON_TIMEOUT` ではなく新しい `STOP_REASON_TIMEOUT_ABANDONED` が付与される。
- 新しい abandoned stop reason が頻発する場合、system は job frequency を減らす mitigation を行う。
- アプリは新しい stop reason を使い、abandoned job を検出・削減すべき。
- WorkManager、AsyncTask、DownloadManager を使う場合は、それらの API が job lifecycle を管理するため影響を受けない。

## ドキュメント差分確認（Documentation Delta）

- 依頼された Original statements と、2026-07-04 時点で確認した公式本文に実質的な差分はない。
- 公式ページは `behavior-changes-all` であり、targetSdkVersion 36 専用ページではない。

---

# 変更内容（What Changed）

## 新しい stop reason

- `JobParameters.STOP_REASON_TIMEOUT_ABANDONED = 16` は、job が timeout し、かつ system が `JobParameters` strong reference 喪失により `jobFinished()` が呼べない可能性を検出した場合に使われる。
- `JobParameters#getStopReason()` はアプリが `onStopJob(JobParameters)` で stop reason を参照する API。
- API surface 上は Android 15 tag にも flagged API として存在する。したがって、本件は「定数が r15 から r16 で単純追加された」差分ではなく、Android 16 の all apps behavior として abandoned job を検出・報告・mitigation する項目として扱う。

## abandoned job 判定

- `JobServiceEngine` は `MSG_EXECUTE_JOB` で `params.enableCleaner()` を呼び、`onStartJob(params)` を実行する。
- `onStartJob()` が false を返した場合は `params.disableCleaner()` する。
- `jobFinished(params, wantsReschedule)` が呼ばれる場合も `params.disableCleaner()` してから system callback へ完了通知する。
- `JobParameters.JobCleanupCallback` は cleaner が有効な状態で `JobParameters` が GC された場合、`IJobCallback.handleAbandonedJob(jobId)` を呼ぶ。
- `JobServiceContext.doHandleAbandonedJob()` は実行中の jobId と一致する場合だけ `JobStatus#setAbandoned(true)` を設定する。

## timeout 時の分岐

- `JobServiceContext.handleOpTimeoutLocked()` は job が最大実行時間に到達した場合、通常は `STOP_REASON_TIMEOUT` / `INTERNAL_STOP_REASON_TIMEOUT` を設定する。
- `Flags.handleAbandonedJobs()` が有効で、hidden compat override が enabled ではなく、running job が `isAbandoned()` の場合、`STOP_REASON_TIMEOUT_ABANDONED` / `INTERNAL_STOP_REASON_TIMEOUT_ABANDONED` に切り替える。

## repeated abandoned occurrences mitigation

- `JobSchedulerService#getRescheduleJobForFailureLocked()` は `INTERNAL_STOP_REASON_TIMEOUT_ABANDONED` の場合、`numAbandonedFailures` と `numFailures` を増やす。
- `shouldUseAggressiveBackoff()` は abandoned failure count が `ABANDONED_JOB_TIMEOUTS_BEFORE_AGGRESSIVE_BACKOFF` を超える場合、aggressive backoff を使う。
- default threshold は 3。つまり、実装上は count が 3 を超えた後に aggressive backoff 判定が true になる。

---

# AOSP 調査（AOSP Investigation）

## 関連ファイル（Related Files）

- `frameworks-base/apex/jobscheduler/framework/java/android/app/job/JobParameters.java`
- `frameworks-base/apex/jobscheduler/framework/java/android/app/job/JobService.java`
- `frameworks-base/apex/jobscheduler/framework/java/android/app/job/JobServiceEngine.java`
- `frameworks-base/apex/jobscheduler/framework/aconfig/job.aconfig`
- `frameworks-base/apex/jobscheduler/service/java/com/android/server/job/JobServiceContext.java`
- `frameworks-base/apex/jobscheduler/service/java/com/android/server/job/JobSchedulerService.java`
- `frameworks-base/apex/jobscheduler/service/java/com/android/server/job/controllers/JobStatus.java`
- `frameworks-base/apex/jobscheduler/service/java/com/android/server/job/JobStore.java`
- `frameworks-base/core/api/current.txt`
- `frameworks-base/services/tests/mockingservicestests/src/com/android/server/job/JobServiceContextTest.java`
- `frameworks-base/services/tests/mockingservicestests/src/com/android/server/job/JobSchedulerServiceTest.java`

## Checkout hygiene

- `frameworks-base` は status 確認時点で clean。
- `android-15.0.0_r36` と `android-16.0.0_r4` tag が存在することを確認した。
- local working tree の未追跡ファイルや別作業ファイルは AOSP evidence として扱っていない。

## 確認したソース文脈（Source Context Reviewed）

| ファイル / シンボル（File / symbol） | Android 15 baseline | Android 16 behavior | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| `JobParameters.STOP_REASON_TIMEOUT_ABANDONED` | `@FlaggedApi(Flags.FLAG_HANDLE_ABANDONED_JOBS)` として定義済み。 | 同じ値 `16` として public API surface に存在。 | アプリが `getStopReason()` で観測する stop reason の public API 根拠。 |
| `JobParameters.OVERRIDE_HANDLE_ABANDONED_JOBS` | r15 には見つからない。 | `@ChangeId` / `@Disabled` / `@Overridable`、ID `372529068` として追加。 | Android 16 で abandoned handling を compat override できる根拠。 |
| `JobParameters.enableCleaner()` / `disableCleaner()` | cleaner を有効化 / 無効化するが、hidden compat override gate はない。 | `Flags.handleAbandonedJobs()` と `OVERRIDE_HANDLE_ABANDONED_JOBS` を見て cleaner 処理を有効化 / 抑止する。 | `JobParameters` GC による abandoned detection の入口。 |
| `JobParameters.JobCleanupCallback.run()` | cleaner が有効なら `mCallback.handleAbandonedJob(mJobId)` を呼ぶ。 | 同左。 | `JobParameters` GC から system callback へ到達する根拠。 |
| `JobServiceEngine.JobHandler#MSG_EXECUTE_JOB` | `onStartJob(params)` の前に `params.enableCleaner()` を呼び、work ongoing でなければ disable。 | 同左。 | `onStartJob()` で非同期継続する job だけ abandoned risk が残る根拠。 |
| `JobServiceEngine.JobHandler#MSG_JOB_FINISHED` | `jobFinished()` 時に `params.disableCleaner()` してから `callback.jobFinished()` を呼ぶ。 | 同左。 | 正常完了時に abandoned と判定されない根拠。 |
| `JobService#onStartJob()` / `jobFinished()` | `onStartJob()` が true の場合、`jobFinished()` まで active と説明。 | 同左。 | app developer が守るべき lifecycle contract の根拠。 |
| `JobServiceContext.doHandleAbandonedJob()` | running jobId と一致すれば `JobStatus#setAbandoned(true)`。 | running state check がより明確化され、実行中 job だけ abandoned mark する。 | GC callback から job status へ abandoned state を反映する根拠。 |
| `JobStatus#mIsAbandoned` | `jobFinished()` なしで `JobParameters` strong reference が失われた可能性を保持。 | 同左。 | timeout 時の分岐条件 `isAbandoned()` の根拠。 |
| `JobServiceContext.handleOpTimeoutLocked()` | flag enabled かつ `isAbandoned()` の場合は `STOP_REASON_TIMEOUT_ABANDONED` に切り替える準備コードあり。 | flag enabled、override disabled、`isAbandoned()` の場合に `STOP_REASON_TIMEOUT_ABANDONED` に切り替える。 | `STOP_REASON_TIMEOUT` から `STOP_REASON_TIMEOUT_ABANDONED` へ変わる直接根拠。 |
| `JobSchedulerService#getRescheduleJobForFailureLocked()` | abandoned internal reason の場合 `numAbandonedFailures` と `numFailures` を増やす準備コードあり。 | flag enabled、override disabled の場合に abandoned failure として数え、backoff policy に反映する。 | frequent occurrences の mitigation 根拠。 |
| `JobSchedulerService#shouldUseAggressiveBackoff()` | abandoned failure count が threshold を超えると true。 | uid ごとの compat override を見たうえで true / false を返す。 | job frequency mitigation の具体的実装根拠。 |
| `JobServiceContextTest` | abandoned / non-abandoned timeout の stop reason を検証。 | flag enabled + override disabled で abandoned timeout が `STOP_REASON_TIMEOUT_ABANDONED`、override enabled / flag disabled / non-abandoned では `STOP_REASON_TIMEOUT` になることを検証。 | 分岐条件の test evidence。 |
| `JobSchedulerServiceTest` | abandoned timeout count と aggressive backoff を検証。 | threshold 超過で aggressive backoff が true、override enabled では false になることを検証。 | mitigation の test evidence。 |

必須記入項目（Required context）:
- Entry point / caller: direct `JobScheduler` job が `JobService#onStartJob(JobParameters)` を受ける。アプリが true を返して非同期 work を続ける場合、`JobParameters` は後続の `jobFinished()` に必要な job handle になる。
- Runtime path: `JobSchedulerService` -> `JobServiceContext` -> app `JobServiceEngine` -> `onStartJob(params)` -> cleaner enabled -> `JobParameters` GC -> `IJobCallback.handleAbandonedJob()` -> `JobStatus#setAbandoned(true)` -> timeout -> `STOP_REASON_TIMEOUT_ABANDONED`。
- Why relevant: 公式文書が述べる `JobParameters` GC、`jobFinished()` 未呼び出し、timeout、new stop reason、frequency mitigation を直接実装している経路。
- Excluded code paths: `ANR_PRE_UDC_APIS_ON_SLOW_RESPONSES`、network permission job changes、unsupported bias usage など JobScheduler 内の targetSdk gated compat changes は今回の abandoned stop reason とは別経路のため除外した。

## 差分解釈（Diff Interpretation）

| 確認した差分（Observed diff） | 解釈（Interpretation） | Behavior Change との関係 | 信頼度（Confidence） |
| --- | --- | --- | --- |
| Android 16 `JobParameters` に `OVERRIDE_HANDLE_ABANDONED_JOBS = 372529068` が追加され、`enableCleaner()` / `disableCleaner()` が flag と override を見る。 | Changed condition / added compat override。abandoned detection を package / uid 単位で抑止できる hidden testing path が追加。 | default behavior は abandoned handling。override enabled は例外。 | High |
| `JobServiceContext.handleOpTimeoutLocked()` が `OVERRIDE_HANDLE_ABANDONED_JOBS` を見たうえで `STOP_REASON_TIMEOUT_ABANDONED` に切り替える。 | Changed condition。timeout reason と abandoned timeout reason を明確に分岐。 | 公式の「STOP_REASON_TIMEOUT ではなく STOP_REASON_TIMEOUT_ABANDONED」を支持。 | High |
| `JobSchedulerService#getRescheduleJobForFailureLocked()` / `shouldUseAggressiveBackoff()` が abandoned count と compat override を見る。 | Changed condition / mitigation behavior。頻発時に aggressive backoff を適用。 | 公式の「frequent occurrences で job frequency を下げる mitigation」を支持。 | High |
| API surface では Android 15 tag にも `STOP_REASON_TIMEOUT_ABANDONED` が flagged API として存在。 | No simple API-addition diff。Android 16 behavior change は public constant の単純追加ではない。 | API addition only ではなく all-apps behavior change として扱う。 | Medium |
| abandoned job 判定経路に targetSdkVersion 36 gate は見つからない。 | No targetSdk gate found。 | `OS_UPDATE_ALL_APPS` 分類を支持。 | High |

---

# Facts / Observations / Hypotheses / Conclusions

## Facts

- 公式文書は Android 16 all apps ページで `Abandoned empty jobs stop reason` を説明している。
- `JobParameters.STOP_REASON_TIMEOUT_ABANDONED` は `@FlaggedApi(Flags.FLAG_HANDLE_ABANDONED_JOBS)` の public constant として存在する。
- `JobServiceEngine` は `onStartJob()` 前に cleaner を有効化し、`onStartJob()` が false を返す場合と `jobFinished()` 呼び出し時に cleaner を無効化する。
- `JobParameters` cleaner は有効状態で GC されると `handleAbandonedJob(jobId)` を呼ぶ。
- `JobServiceContext` は実行中 job と callback / jobId が一致する場合だけ `JobStatus#setAbandoned(true)` を設定する。
- timeout 時に abandoned と判定されていれば `STOP_REASON_TIMEOUT_ABANDONED` が設定される。
- repeated abandoned timeout は abandoned failure count として reschedule backoff に反映される。

## Observations

- `STOP_REASON_TIMEOUT_ABANDONED` は Android 15 tag の API surface にも flagged API として存在するため、r15 -> r16 の単純な API 追加とは言い切れない。
- Android 16 では hidden compat override `OVERRIDE_HANDLE_ABANDONED_JOBS` が追加され、検証や互換性対応で abandoned handling を抑止できる構造になっている。
- `STOP_REASON_TIMEOUT_ABANDONED` は「確実に app が abandoned した」という断定ではなく、「system が jobFinished() を呼べない状態を検出した probable abandoned signal」として扱うべき。
- `JobParameters` の API comment は、active job を `cancel()` した場合でも strong reference を失っていると system が真の abandoned と区別できない可能性に触れている。

## Hypotheses

- WorkManager / DownloadManager の非影響は、各 API が `JobParameters` lifecycle と `jobFinished()` 相当の完了通知を管理するためという公式説明に基づく。Jetpack WorkManager の詳細実装は AOSP `frameworks-base` 外の evidence が必要。
- Android 15 tag には flagged API と準備コードが存在するが、Android 15 製品上で同じ behavior が常に有効だったとは判断しない。公式には Android 16 all apps 変更として扱われている。

## Conclusions

- Primary classification は `OS_UPDATE_ALL_APPS`。
- Android 16 / targetSdkVersion 35 と Android 16 / targetSdkVersion 36 の期待挙動は同じ。targetSdkVersion 36 化だけでこの挙動が発生する evidence はない。
- 影響の中心は direct `JobScheduler` / custom `JobService` の lifecycle bug。`JobParameters` を保持し、必ず `jobFinished()` を呼ぶ実装では影響しにくい。
- `STOP_REASON_TIMEOUT_ABANDONED` を logging / telemetry に追加し、頻発時は app 側の lifecycle 修正を優先する。
- `STOP_REASON_TIMEOUT_ABANDONED` が頻発すると aggressive backoff により job frequency が低下し得る。

---

# 期待挙動マトリクス（Required OS / targetSdkVersion Matrix）

| OS | targetSdkVersion | 期待挙動（Expected behavior） | 顧客向け説明での扱い |
| --- | --- | --- | --- |
| Android 15 | 35 | Android 16 の all-apps behavior としては扱わない。flagged API / 準備コードは存在し得るため、実機 build の flag 状態を記録する。 | baseline。 |
| Android 16 | 35 | 条件を満たす direct JobScheduler job では `STOP_REASON_TIMEOUT_ABANDONED` と mitigation が発生し得る。 | OS update impact。 |
| Android 16 | 36 | targetSdkVersion 35 と同じ期待挙動。targetSdkVersion 36 gate は見つからない。 | OS update impact。targetSdkVersion 36 化と混ぜない。 |
| Android 15 | 36 | targetSdkVersion 36 の値だけでは Android 16 all-apps behavior は発生しない。比較する場合は platform / flag 状態を明記する。 | targetSdkVersion 36 単独影響ではないことの比較対象。 |

---

# 詳細マトリクス（Required Scenario Matrix）

| シナリオ（Scenario） | 期待挙動（Expected behavior） | 根拠 / 備考 |
| --- | --- | --- |
| Android 16 / targetSdkVersion 35 / direct JobScheduler | 条件を満たすと影響あり。 | targetSdkVersion gate なし。 |
| Android 16 / targetSdkVersion 36 / direct JobScheduler | targetSdkVersion 35 と同じ。 | targetSdkVersion gate なし。 |
| Android 16 / JobService keeps strong JobParameters reference | abandoned 判定されにくい。timeout しても通常 timeout 側。 | cleaner が GC されない。 |
| Android 16 / JobService loses JobParameters reference | cleaner callback により abandoned mark され得る。 | `JobCleanupCallback#run()`。 |
| Android 16 / jobFinished() called | cleaner が disabled になり正常完了扱い。 | `MSG_JOB_FINISHED`。 |
| Android 16 / jobFinished() not called | active job が timeout し得る。JobParameters 喪失時は abandoned timeout。 | `handleOpTimeoutLocked()`。 |
| Android 16 / timeout with retained JobParameters | `STOP_REASON_TIMEOUT`。 | `isAbandoned()` false。 |
| Android 16 / timeout with abandoned JobParameters | `STOP_REASON_TIMEOUT_ABANDONED`。 | flag enabled + override disabled + `isAbandoned()`。 |
| Android 16 / STOP_REASON_TIMEOUT | 通常 timeout。 | non-abandoned / flag disabled / override enabled。 |
| Android 16 / STOP_REASON_TIMEOUT_ABANDONED | probable abandoned timeout。 | `STOP_REASON_TIMEOUT_ABANDONED = 16`。 |
| Android 16 / single abandoned occurrence | stop reason として観測。frequency mitigation は閾値次第。 | count increment。 |
| Android 16 / frequent abandoned occurrences | aggressive backoff により job frequency が下がり得る。 | threshold default 3、count > threshold で true。 |
| Android 16 / mitigation reduces job frequency | reschedule backoff policy が exponential/aggressive 側になる。 | `shouldUseAggressiveBackoff()`。 |
| Android 16 / WorkManager task | 公式文書上は非影響。WorkManager が lifecycle を管理。 | Jetpack 詳細は外部 evidence。 |
| Android 16 / DownloadManager task | 公式文書上は非影響。DownloadManager が lifecycle を管理。 | DownloadProvider 詳細は別 repo / module evidence。 |
| Android 16 / AsyncTask usage | 公式文書上は非影響。ただし direct JobService 内で AsyncTask を自前利用し `jobFinished()` を漏らす場合は direct JobScheduler bug として扱う。 | JobScheduler lifecycle 管理との境界に注意。 |
| Android 16 / app logs JobParameters#getStopReason() | `STOP_REASON_TIMEOUT_ABANDONED` を検出可能。 | recommended。 |
| Android 16 / app does not log stop reason | abandoned lifecycle bug の発見が遅れる。 | customer risk。 |
| Android 15 / targetSdkVersion 36 / same app behavior if technically comparable | Android 16 all-apps behavior ではない。flag 状態を記録して比較。 | API surface だけで同一挙動とは判断しない。 |

---

# 影響対象（Affected Apps）

- JobScheduler を直接使うアプリ。
- JobService を独自実装しているアプリ。
- `onStartJob()` から非同期処理を開始するアプリ。
- `JobParameters` を strong reference として保持していないアプリ。
- `jobFinished()` 呼び出し漏れがあり得るアプリ。
- timeout / retry / reschedule を前提にしているアプリ。
- stop reason を `STOP_REASON_TIMEOUT` としてしか扱っていないアプリ。
- `JobParameters#getStopReason()` をログ化していないアプリ。
- repeated timeout / job frequency mitigation に影響を受けるアプリ。
- WorkManager を使うアプリ。
- DownloadManager を使うアプリ。
- AsyncTask を使う legacy app。

---

# テスト観点（Testing Guidance）

## OS / targetSdkVersion 比較

- Android 15 端末上の targetSdkVersion 35。
- Android 16 端末上の targetSdkVersion 35。
- Android 16 端末上の targetSdkVersion 36。
- Android 15 端末上の targetSdkVersion 36 が検証可能な場合の比較。

## direct JobScheduler lifecycle

- direct JobScheduler / JobService 実装。
- `onStartJob()` で true を返す async job。
- `JobParameters` を strong reference で保持する場合。
- `JobParameters` reference を意図的に失う場合。
- `jobFinished()` を呼ぶ場合。
- `jobFinished()` を呼ばない場合。
- normal timeout。
- abandoned timeout。

## stop reason / mitigation

- `JobParameters#getStopReason()`。
- `STOP_REASON_TIMEOUT`。
- `STOP_REASON_TIMEOUT_ABANDONED`。
- repeated abandoned occurrences。
- mitigation による job frequency 低下。
- dumpsys jobscheduler / logs / metrics の確認。
- retry / reschedule / backoff behavior。
- user-visible failure / silent failure。
- lifecycle fix 後に `STOP_REASON_TIMEOUT_ABANDONED` が減ること。
- regression testing for long-running jobs。

## managed APIs

- WorkManager 実装。
- DownloadManager 実装。
- AsyncTask usage。
- managed API では lifecycle が管理されるという公式非影響主張を実機挙動で確認。

---

# 推奨対応候補（Recommended Action Candidates）

- direct `JobService` で `onStartJob()` が true を返す場合、`JobParameters` を strong reference として保持する。
- 非同期 work 完了時に必ず `JobService#jobFinished(params, wantsReschedule)` を呼ぶ。
- `onStartJob()` 内で完了できる work は false を返し、active job として残さない。
- `JobParameters#getStopReason()` をログ化し、`STOP_REASON_TIMEOUT_ABANDONED` を `STOP_REASON_TIMEOUT` と分けて集計する。
- `STOP_REASON_TIMEOUT_ABANDONED` が発生した jobId / namespace / source package / retry count / backoff を記録する。
- frequent occurrences がある場合、job frequency mitigation の前に app lifecycle bug を修正する。
- WorkManager / DownloadManager に移行できる work は managed API への移行を検討する。

---

# 顧客向け説明（Customer-facing Explanation）

Android 16 では、直接 `JobScheduler` / `JobService` を使うアプリで、非同期 job の `JobParameters` を失い、`jobFinished()` を呼ばないまま timeout した場合、`STOP_REASON_TIMEOUT_ABANDONED` が報告される可能性があります。これは targetSdkVersion 36 に上げた時だけの変更ではなく、Android 16 へ OS アップデートした時の all-apps behavior として説明してください。

この stop reason は、job が単に長時間実行されたというよりも、アプリが job lifecycle を失っている可能性を示す診断 signal です。頻発すると backoff が強くなり、job の再実行頻度が下がる可能性があります。WorkManager、DownloadManager、AsyncTask など lifecycle を管理する API を使っている場合は公式文書上は非影響ですが、direct JobService 内で自前非同期処理を行う場合は `JobParameters` の保持と `jobFinished()` の呼び出しを確認してください。

---

# Human Decision Placeholder

最終優先度（Final Priority）:
- Critical / High / Medium / Low

判断（Decision）:
- Explain / Monitor / Ignore / Further investigation required

補足:
- 最終優先度、顧客通知要否、release readiness は repository owner が判断する。
