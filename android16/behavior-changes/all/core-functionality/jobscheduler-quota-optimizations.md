# JobScheduler quota optimizations 調査レポート

## 基本情報（Metadata）

### 調査対象 Android バージョン（Android Versions）

From:
- android-15.0.0_r36

To:
- android-16.0.0_r4

Note:
- `android16/AGENTS.md` は To tag を `android-16.0.0_r1` としているが、本調査では依頼スコープに従い公開済み Android 16 tag として `android-16.0.0_r4` を使用した。

Previous targetSdkVersion:
- 35

Target targetSdkVersion:
- 36

### Behavior Change 文書（Behavior Change Source）

Document:
- https://developer.android.com/about/versions/16/behavior-changes-all#job-quota-opt

Page:
- Behavior changes: all apps

Category:
- Core functionality

Section:
- JobScheduler quota optimizations

Subsection:
- Testing

### 分類スナップショット（Classification Snapshot）

主分類（Primary classification）:
- `OS_UPDATE_ALL_APPS`

早見表（At-a-glance impact）:

| 確認項目（Question） | 回答（Answer） | 根拠（Evidence） |
| --- | --- | --- |
| Android 16 に OS アップデートしただけで適用されるか | Yes | 公式 all apps ページは Android 16 で実行される全アプリに適用される変更として掲載している。AOSP `QuotaController` の Android 16 実装に targetSdkVersion 36 gate は見つからない。 |
| targetSdkVersion 36 以上が必要か | No | `QuotaController` の quota 判定は source uid / standby bucket / process state / compat override / job type に基づき、targetSdkVersion を参照しない。 |
| 追加の実行時条件があるか | Yes | JobScheduler quota 管理対象の work を使うこと。特に regular / expedited job、top state 開始後に継続する job、foreground service と同時実行する job、standby bucket の quota に依存する job。 |
| Compat Change ID が関係するか | Yes | `OVERRIDE_QUOTA_ENFORCEMENT_TO_FGS_JOBS` = `341201311`、`OVERRIDE_QUOTA_ENFORCEMENT_TO_TOP_STARTED_JOBS` = `374323858`。どちらも `@Disabled` / `@Overridable` で、enable すると Android 16 の enforcement をテスト用に無効化する方向で働く。 |

### 調査日（Investigation Date）

2026-07-04

### 信頼度（Confidence）

- High

理由:
- 公式文書が all apps 変更として明記している。
- AOSP の `QuotaController` 差分で top-started jobs / foreground-service-concurrent jobs / active bucket quota の enforcement 経路を確認した。
- targetSdkVersion gate は見つからず、compat override の Change ID / default state を AOSP annotation で確認した。
- WorkManager と DownloadManager は公式文書上の影響対象だが、WorkManager は Jetpack 側、DownloadManager の実装詳細は `frameworks-base` 外にもまたがるため、直接 evidence と間接 evidence を分けて記録する。

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
- targetSdkVersion: 条件なし。35 と 36 の両方で同じ platform quota policy が適用される見込み。
- Device/form factor: 条件なし。
- Permission/API/component condition: JobScheduler quota 管理対象の API を使うこと。WorkManager / JobScheduler / DownloadManager の job が対象になり得る。
- App state/process condition: standby bucket、top / visible state、invisible 後の継続、foreground service 同時実行、user-initiated job かどうか。

Compat framework:
- Change ID: `341201311`
- Change name: `OVERRIDE_QUOTA_ENFORCEMENT_TO_FGS_JOBS`
- Default state: `@Disabled`
- Toggleable for testing: Yes。`adb shell am compat enable OVERRIDE_QUOTA_ENFORCEMENT_TO_FGS_JOBS <package>`

- Change ID: `374323858`
- Change name: `OVERRIDE_QUOTA_ENFORCEMENT_TO_TOP_STARTED_JOBS`
- Default state: `@Disabled`
- Toggleable for testing: Yes。`adb shell am compat enable OVERRIDE_QUOTA_ENFORCEMENT_TO_TOP_STARTED_JOBS <package>`

補足:
- Android 16 compat framework 公式一覧ページでは上記 2 名は検索で確認できなかった。一方、Behavior Change 本文の testing command と AOSP `@ChangeId` / `@Disabled` / `@Overridable` 定義で確認できる。

分類信頼度（Classification confidence）:
- High

分類根拠（Classification evidence）:
- Official documentation page: `behavior-changes-all` の JobScheduler quota optimizations。
- Original applicability statement: Android 16 の all apps ページは、Android 16 上で実行される全アプリに適用される変更として説明している。
- AOSP targetSdk gate: 見つからない。
- Compat framework entry: AOSP `QuotaController` の `@ChangeId` と公式 testing command。

---

# エグゼクティブサマリー（Executive Summary）

Android 16 では、JobScheduler の regular job / expedited job の実行時間 quota がより明確に適用される。active standby bucket でも十分大きいが有限の runtime quota が適用され、top state 中に開始して visible でなくなった後も続く job、foreground service と同時に走る job も quota に従う。

この変更は Android 16 の all apps 変更であり、targetSdkVersion 36 への更新だけで発生する変更ではない。targetSdkVersion 35 のまま Android 16 端末で動くアプリにも、JobScheduler / WorkManager / DownloadManager を通じた長時間 work では影響し得る。

長時間のユーザー可視データ転送を ordinary job で実装している場合は、user-initiated data transfer job への移行、`JobParameters#getStopReason()` / `WorkInfo#getStopReason()` のログ化、`JobScheduler#getPendingJobReasonsHistory()` による pending reason 確認を推奨する。

---

# 公式ドキュメント確認（Original Documentation）

## 原文（Statement）

公式文書では、Android 16 から regular / expedited job の runtime quota を以下の要素に基づいて調整すると説明している。

- アプリの app standby bucket。Android 16 では active bucket にも generous な runtime quota を適用する。
- job が app top state 中に開始された場合。ユーザーに visible な間に開始し、その後 invisible になっても続く job は runtime quota に従う。
- job が foreground service と同時に実行されている場合。FGS と同時実行中の job も runtime quota に従う。
- WorkManager、JobScheduler、DownloadManager で schedule された task に影響する。
- stop reason は WorkManager なら `WorkInfo.getStopReason()`、JobScheduler なら `JobParameters.getStopReason()` でログ化することが推奨される。
- Android 16 の新 API `JobScheduler#getPendingJobReasonsHistory()` を使い、job が実行されなかった理由を確認することが推奨される。
- testing では Android 16 端末上で `OVERRIDE_QUOTA_ENFORCEMENT_TO_TOP_STARTED_JOBS` / `OVERRIDE_QUOTA_ENFORCEMENT_TO_FGS_JOBS` を enable して、一部 quota optimization を無効化できる。
- standby bucket は `adb shell am set-standby-bucket <package> active|working_set|frequent|rare|restricted` で切り替えて検証できる。

## 解釈（Interpretation）

この項目は targetSdkVersion 36 化の挙動変更ではなく、Android 16 OS / JobScheduler module 側の quota policy 変更である。既存コードが「active bucket なら実質的に長時間走れる」「visible 中に開始した job は invisible 後も quota-free」「FGS と併用すれば job quota を回避できる」といった前提を置いている場合、Android 16 で stop / reschedule / pending が増える可能性がある。

---

# 変更内容（What Changed）

## 変更点

- Android 16 の `QuotaController` は top-started job の quota exemption を default では付与しない。`OVERRIDE_QUOTA_ENFORCEMENT_TO_TOP_STARTED_JOBS` を enable した場合だけ、top state 中に開始した job を `mTopStartedJobs` に入れて quota-free 扱いに戻す。
- Android 16 の `QuotaController#getProcessStateQuotaFreeThreshold()` は default で `PROCESS_STATE_BOUND_TOP` を quota-free threshold にする。FGS process state は quota-free threshold から外れる。`OVERRIDE_QUOTA_ENFORCEMENT_TO_FGS_JOBS` を enable した場合だけ `PROCESS_STATE_FOREGROUND_SERVICE` が quota-free threshold になる。
- active / exempted bucket の quota default constants が調整される。active bucket は legacy の「10分 allowed / 10分 window」から current の「20分 allowed / 60分 window」へ移り、active bucket でも generous だが有限の runtime quota になる。
- user-initiated jobs は `QuotaController.prepareForExecutionLocked()` で timer tracking から外されるため、公式文書の「ユーザー開始データ転送は user initiated data transfer jobs を検討」という推奨と整合する。

## 適用条件（Applicability）

### OS アップデート時の挙動（OS Update Behavior）

- Android 16 にアップデートしただけで適用されるか: Yes。JobScheduler quota 管理対象 work を使うアプリは targetSdkVersion 35 のままでも影響し得る。
- targetSdkVersion に依存しない根拠: `QuotaController` の該当分岐は uid、standby bucket、process state、job type、compat override を見るが、targetSdkVersion を参照しない。
- Android 15 以前での挙動: Android 15 tag では `Flags.enforceQuotaPolicyToTopStartedJobs()` / `Flags.enforceQuotaPolicyToFgsJobs()` の feature flag 分岐が残っている。Android 16 では FGS enforcement flag が削除され、top-started job enforcement も default policy 側に組み込まれている。

### targetSdkVersion 36 以上での挙動（targetSdkVersion 36 Behavior）

- targetSdkVersion 36 以上で適用されるか: targetSdkVersion 36 は必要条件ではない。
- Android 16 以外で targetSdkVersion 36 にした場合の挙動: Android 15 platform 上では Android 16 の `QuotaController` policy 変更は存在しない。targetSdkVersion 36 の値だけで Android 16 quota optimization が発生する evidence はない。
- opt-out / temporary override の有無: app-compat override はある。ただし通常の「opt-out manifest」ではなく、testing 用の compat change enable command として公式文書が案内している。

### その他の条件（Other Conditions）

- API usage: JobScheduler、WorkManager、DownloadManager、regular job、expedited job。
- App state/process condition: standby bucket、top / visible state、foreground service 同時実行、user-initiated job。
- Job type condition: ordinary job / expedited job は quota 対象。user-initiated job は別扱い。

---

# AOSP 調査（AOSP Investigation）

## 関連ファイル（Related Files）

- `frameworks-base/apex/jobscheduler/service/java/com/android/server/job/controllers/QuotaController.java`
- `frameworks-base/apex/jobscheduler/service/aconfig/job.aconfig`
- `frameworks-base/apex/jobscheduler/service/java/com/android/server/job/JobSchedulerService.java`
- `frameworks-base/apex/jobscheduler/service/java/com/android/server/job/JobServiceContext.java`
- `frameworks-base/apex/jobscheduler/service/java/com/android/server/job/controllers/JobStatus.java`
- `frameworks-base/apex/jobscheduler/framework/java/android/app/job/JobScheduler.java`
- `frameworks-base/apex/jobscheduler/framework/java/android/app/job/JobParameters.java`
- `frameworks-base/apex/jobscheduler/framework/java/android/app/job/JobInfo.java`
- `frameworks-base/core/api/current.txt`

## 確認したソース文脈（Source Context Reviewed）

| ファイル / シンボル（File / symbol） | Android 15 の基準挙動（baseline） | Android 16 の挙動 | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| `QuotaController.prepareForExecutionLocked()` | `Flags.enforceQuotaPolicyToTopStartedJobs()` が false、または compat override が enabled の場合、top state 中に開始した job を `mTopStartedJobs` として timer tracking から外す。 | compat override が enabled の場合だけ top-started job を timer tracking から外す。default では timer tracking され、quota 消費対象になる。 | job 実行開始時に quota timer に入るかを決める entry point。top-started jobs の runtime quota 適用の直接根拠。 |
| `QuotaController.isTopStartedJobLocked()` | feature flag が off なら top-started exemption を認める。 | compat override enabled の場合だけ `mTopStartedJobs` を参照する。 | visible 中に開始した job が invisible 後も quota-free かどうかを決める。 |
| `QuotaController.getProcessStateQuotaFreeThreshold()` | `Flags.enforceQuotaPolicyToFgsJobs()` が true かつ override disabled の場合だけ `PROCESS_STATE_BOUND_TOP`。それ以外は `PROCESS_STATE_FOREGROUND_SERVICE`。 | override disabled の default では `PROCESS_STATE_BOUND_TOP`。override enabled の場合だけ `PROCESS_STATE_FOREGROUND_SERVICE`。 | FGS 同時実行中の job が quota-free か quota 対象かを決める。 |
| `QuotaController.QcConstants` / `adjustDefaultBucketWindowSizes()` | active allowed time は legacy 10分、active window は legacy 10分。 | active allowed time は current 20分、active window は latest 60分。 | active bucket でも generous だが有限 quota を適用する根拠。 |
| `QuotaController.isWithinEJQuotaLocked()` / `mEJTimingSessions` | expedited job quota を timing session / debit で管理する。 | expedited job も quota / top / foreground / temp allowlist 条件で判定される。 | official statement の regular and expedited quota を確認する根拠。 |
| `JobStatus.setConstraintSatisfied()` / `constraintToStopReason()` | quota constraint が false になると stop reason に `STOP_REASON_QUOTA` を割り当てる。 | 同左。Android 16 では対象 job が増えるため quota stop reason を観測しやすくなる。 | `JobParameters#getStopReason()` で quota stop をログ化する推奨の根拠。 |
| `JobSchedulerService#getPendingJobReasonsHistory()` / binder API | `@FlaggedApi` として tag 内に存在。 | Android 16 API として公式文書が紹介。service は calling uid の job を取得して `JobStatus` の履歴を返す。 | pending reason history API の実装根拠。 |
| `JobInfo.Builder#setUserInitiated(boolean)` / `JobStatus.shouldTreatAsUserInitiatedJob()` | user-initiated job は quota 対象外の job type として定義される。 | `QuotaController.prepareForExecutionLocked()` で user-initiated job は timer tracking されない。 | 長時間ユーザー可視データ転送は ordinary job ではなく UIJ を使うべき根拠。 |

必須記入項目（Required context）:
- Entry point / caller: アプリが `JobScheduler.schedule()`、WorkManager、DownloadManager などから job を schedule し、JobSchedulerService が job を管理する。実行開始時に `QuotaController.prepareForExecutionLocked()` が quota timer tracking を決め、constraint 更新時に `JobStatus` が ready / unready と stop reason を更新する。
- Relevant class or service responsibility: `QuotaController` は JobScheduler の execution quota、expedited job quota、standby bucket 別 runtime limit、process state exemption を管理する。
- Runtime path from app API / system event to changed code: `JobScheduler` job scheduling -> `JobSchedulerService` -> `JobStatus` 作成 / standby bucket キャッシュ -> `QuotaController` tracking -> job execution timer -> quota exhaustion -> `JobServiceContext` stop callback / `JobParameters#getStopReason()`。
- Why unrelated code paths were excluded: AlarmManager、thermal restriction、wakelock tag、abandoned job timeout は JobScheduler 周辺の別変更であり、本件の top / FGS / standby bucket runtime quota 適用条件を直接決めないため除外した。

## 差分解釈（Diff Interpretation）

| 確認した差分（Observed diff） | 解釈（Interpretation） | Behavior Change との関係 | 信頼度（Confidence） |
| --- | --- | --- | --- |
| Android 16 `QuotaController` で `Flags.enforceQuotaPolicyToFgsJobs()` 分岐が削除され、`OVERRIDE_QUOTA_ENFORCEMENT_TO_FGS_JOBS` の compat override だけが残る。 | Changed default / changed condition。default で FGS 同時実行 job を quota 対象にし、compat enable 時だけ旧挙動に戻す。 | 「jobs that are executing concurrently with a foreground service will adhere to the job runtime quota」を支持する。 | High |
| Android 16 `QuotaController` で top-started job exemption が `OVERRIDE_QUOTA_ENFORCEMENT_TO_TOP_STARTED_JOBS` enabled 時だけに限定される。 | Changed default / changed condition。default で top-started job も quota timer に入る。 | 「Jobs started while visible and continuing after invisible will adhere to runtime quota」を支持する。 | High |
| active bucket の default constants が legacy 10分/10分 window から current 20分/60分 window に調整される。 | Changed default。active bucket の quota が generous but finite になる。 | 「active standby buckets will start being enforced by a generous runtime quota」を支持する。 | High |
| `JobStatus` が quota constraint change を pending reason history に記録し、quota unready を `STOP_REASON_QUOTA` に変換する。 | Existing / API-supporting behavior。Android 16 の quota stop / pending debug guidance を支える。 | `getStopReason()` / `getPendingJobReasonsHistory()` の debugging guidance を支持する。 | High |
| `JobScheduler#getPendingJobReasonsHistory()` は Android 15 tag にも `@FlaggedApi` として存在する。 | API surface は Android 15 tag にも準備済み。ただし公式文書は Android 16 introduced API として案内している。 | 「API introduced in Android 16」は公開 SDK / feature availability の文脈として扱う。tag 差分のみをもって Android 15 製品挙動と同一とは判断しない。 | Medium |

必須分類（Required interpretation）:
- Added behavior: Android 16 default policy として top-started jobs / FGS-concurrent jobs を quota enforcement の通常経路に入れる。
- Removed behavior: Android 15 側に残っていた `Flags.enforceQuotaPolicyToFgsJobs()` による feature flag 分岐が Android 16 側では削除される。
- Changed condition / gate: compat override は「新制限を有効化する」ものではなく、「新制限を無効化して旧挙動に戻す」ものとして働く。
- Changed default: active / exempted bucket の allowed time / window size の default が変更される。
- No behavior change found: targetSdkVersion 36 gate は見つからない。WorkManager Jetpack 実装の差分は AOSP `frameworks-base` の範囲外。

## 事実（Facts）

- 公式文書は `behavior-changes-all` ページに本項目を掲載しており、Android 16 実行時の all apps 変更として説明している。
- AOSP `QuotaController` には `OVERRIDE_QUOTA_ENFORCEMENT_TO_FGS_JOBS = 341201311` と `OVERRIDE_QUOTA_ENFORCEMENT_TO_TOP_STARTED_JOBS = 374323858` が定義され、いずれも `@Disabled` / `@Overridable`。
- Android 16 `prepareForExecutionLocked()` は `OVERRIDE_QUOTA_ENFORCEMENT_TO_TOP_STARTED_JOBS` が enabled かつ UID が top の場合だけ job を `mTopStartedJobs` に入れて timer tracking から外す。
- Android 16 `getProcessStateQuotaFreeThreshold()` は `OVERRIDE_QUOTA_ENFORCEMENT_TO_FGS_JOBS` が disabled の場合 `PROCESS_STATE_BOUND_TOP` を返し、enabled の場合 `PROCESS_STATE_FOREGROUND_SERVICE` を返す。
- Android 16 `QcConstants` には active bucket の current default として allowed time 20分、window size 60分が定義される。
- `JobParameters.STOP_REASON_QUOTA` は quota 消費時の stop reason として定義される。
- `JobParameters#getStopReason()` は `JobService#onStopJob()` が呼ばれた理由を診断用途で返す。
- `JobScheduler#getPendingJobReasonsHistory(int)` は `@FlaggedApi` として定義され、`JobSchedulerService` は calling uid の job から `JobStatus.getPendingJobReasonsHistory()` を返す。
- `JobInfo.Builder#setUserInitiated(true)` の API doc は、user-initiated jobs が quota 対象外で、条件が満たされれば即時開始されることを説明している。

## 観察（Observations）

- Android 15 tag の `QuotaController` には top-started / FGS enforcement を feature flag で切り替える準備コードが存在した。Android 16 ではその feature flag 分岐が整理され、default policy と compat override に寄せられている。
- 公式文書の testing command は `am compat enable` で override を有効化するが、これは新制限を有効化するのではなく、新制限を無効化する方向で働く。テスト手順で誤解しやすい。
- active bucket は unrestricted ではなくなり、ユーザーが最近使ったアプリでも長時間 job は quota stop / pending になり得る。ただし allowed time は他 bucket より generous。
- WorkManager の `WorkInfo#getStopReason()` は Jetpack API であり、AOSP `frameworks-base` では直接実装を確認しない。platform 側では JobScheduler stop reason の根拠を確認した。
- DownloadManager の詳細実装は `frameworks-base` 外の provider 実装にも依存する可能性がある。`JobStatus` コメントには built-in system app / DownloadManager proxied job への言及がある。

## 仮説（Hypotheses）

- WorkManager が JobScheduler backend を使う構成では、Android 16 の JobScheduler quota policy による stop reason が WorkManager の stop reason に反映される可能性が高い。ただし Jetpack library version による API availability / mapping は別途確認が必要。
- DownloadManager の長時間 download は、JobScheduler 経由で管理される場合に quota policy の影響を受ける可能性がある。ただし built-in exempted app / proxy job policy による緩和がある可能性があるため、実機検証が必要。
- `JobScheduler#getPendingJobReasonsHistory()` は Android 15 tag にも `@FlaggedApi` として存在するため、AOSP tag 差分だけでは「コード追加日」は説明しにくい。顧客説明では Android 16 SDK/API として利用可能になる debugging API として扱うのが安全。

## 結論（Conclusions）

- 本件の primary classification は `OS_UPDATE_ALL_APPS`。
- Android 16 OS 上で JobScheduler quota 管理対象 work を実行するアプリに影響し得る。targetSdkVersion 36 は必要条件ではない。
- 影響が大きいのは、long-running upload / download / sync を ordinary job または expedited job で実装しているアプリ、visible 中に job を開始して invisible 後も継続させるアプリ、FGS と job を併用して quota 回避を期待していたアプリ。
- ユーザー可視の長時間データ転送は user-initiated data transfer job への移行を検討すべき。
- stop / pending の切り分けには `JobParameters#getStopReason()`、WorkManager 側では `WorkInfo#getStopReason()`、未実行理由には `JobScheduler#getPendingJobReasonsHistory()` をログ化する。

## 適用ゲート根拠（Applicability Gate Evidence）

- targetSdkVersion gate: 見つからない。
- CompatChanges.isChangeEnabled / ChangeId:
  - `OVERRIDE_QUOTA_ENFORCEMENT_TO_TOP_STARTED_JOBS` = `374323858`
  - `OVERRIDE_QUOTA_ENFORCEMENT_TO_FGS_JOBS` = `341201311`
- @EnabledAfter / @EnabledSince / default state:
  - どちらも `@Disabled`。targetSdkVersion 36 以上で default enabled になる change ではない。
- Build.VERSION / SDK_INT gate: 該当コード内には見つからない。Android 16 の platform / module 実装差分として適用される。
- DeviceConfig / resources config:
  - quota constants は `DeviceConfig.NAMESPACE_JOB_SCHEDULER` から取得可能。default constants は Android 16 で調整されている。
- Permission/AppOps gate:
  - ordinary / expedited quota enforcement には permission gate はない。
  - user-initiated job には `RUN_USER_INITIATED_JOBS` permission と scheduling state check が関係する。
- Manifest/property gate: なし。
- No gate found:
  - targetSdkVersion gate は確認できない。
- Gate conclusion:
  - Android 16 OS / JobScheduler 実装上の all apps 変更。実際の影響は quota 管理対象 work、standby bucket、process state、job type、compat override に依存する。

---

# 期待挙動マトリクス（Expected Behavior Matrix）

## OS / targetSdkVersion

| シナリオ | 期待挙動 |
| --- | --- |
| Android 16 / targetSdkVersion 35 | JobScheduler quota optimization は適用される。targetSdkVersion 35 のままでも top-started / FGS-concurrent / active bucket quota の影響を受け得る。 |
| Android 16 / targetSdkVersion 36 | targetSdkVersion 35 と同様に適用される。targetSdkVersion 36 化だけによる追加 gate は見つからない。 |
| Android 15 / targetSdkVersion 36 | Android 16 の default quota policy 変更は存在しない。Android 15 tag には feature flag 準備コードがあるため、製品 build / flag 状態による差はあり得るが、Android 16 all-apps 変更そのものではない。 |

## 詳細シナリオ

| シナリオ | 期待挙動 / 確認結果 |
| --- | --- |
| Android 16 / targetSdkVersion 35 / regular job | quota 対象。active bucket でも有限 runtime quota。 |
| Android 16 / targetSdkVersion 36 / regular job | targetSdkVersion 35 と同じ。 |
| Android 16 / targetSdkVersion 35 / expedited job | expedited job quota 対象。QuotaController は EJ timing session / debit を管理する。 |
| Android 16 / targetSdkVersion 36 / expedited job | targetSdkVersion 35 と同じ。 |
| Android 16 / job starts while app is top / visible | default では top-started exemption なし。timer tracking に入る。 |
| Android 16 / job continues after app becomes invisible | quota を消費し、quota 切れで stop / pending になり得る。 |
| Android 16 / job running concurrently with foreground service | default では FGS state は quota-free threshold から外れる。quota 対象。 |
| Android 16 / job not running with foreground service | 通常の quota 判定。 |
| Android 16 / active standby bucket | generous だが finite quota。default 20分 allowed / 60分 window。 |
| Android 16 / working_set standby bucket | bucket 別 quota に従う。active より制限が厳しい。 |
| Android 16 / frequent standby bucket | bucket 別 quota に従う。 |
| Android 16 / rare standby bucket | bucket 別 quota に従う。 |
| Android 16 / restricted standby bucket | bucket 別 quota に従い、背景制限も合わせて影響し得る。 |
| Android 16 / WorkManager task | WorkManager が JobScheduler backend を使う場合、platform JobScheduler quota の影響を受け得る。Jetpack 側 mapping は別途確認が必要。 |
| Android 16 / DownloadManager task | 公式文書上は影響対象。AOSP `JobStatus` は DownloadManager proxied jobs に言及する。実装詳細は provider 側も確認が必要。 |
| Android 16 / direct JobScheduler job | 直接影響対象。 |
| Android 16 / user-initiated data transfer job | `shouldTreatAsUserInitiatedJob()` の場合 timer tracking から外れる。permission / state 要件あり。 |
| Android 16 / ordinary upload/download job | quota 対象。長時間転送では stop / retry / pending が増える可能性。 |
| Android 16 / `OVERRIDE_QUOTA_ENFORCEMENT_TO_TOP_STARTED_JOBS` enabled | top-started job は旧挙動寄りに quota-free として扱われる。testing 用 override。 |
| Android 16 / `OVERRIDE_QUOTA_ENFORCEMENT_TO_TOP_STARTED_JOBS` disabled/default | top-started job も quota 対象。 |
| Android 16 / `OVERRIDE_QUOTA_ENFORCEMENT_TO_FGS_JOBS` enabled | FGS process state が quota-free threshold になり、旧挙動寄りに扱われる。testing 用 override。 |
| Android 16 / `OVERRIDE_QUOTA_ENFORCEMENT_TO_FGS_JOBS` disabled/default | FGS 同時実行 job も quota 対象。 |
| Android 16 / `JobParameters#getStopReason()` | quota stop は `STOP_REASON_QUOTA` として診断できる。 |
| Android 16 / `JobScheduler#getPendingJobReasonsHistory()` | job が pending だった理由の履歴を取得できる。履歴は reboot で永続化されない。 |
| Android 15 / targetSdkVersion 36 / same app behavior | Android 16 default policy とは異なる可能性。Android 15 tag には feature flag 分岐があるため、flag 状態を合わせた比較が必要。 |

---

# 影響分析（Impact Analysis）

## 影響を受けるアプリ（Affected Apps）

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
- battery optimization / background execution 制限に敏感なアプリ。

## 影響を受けない、または影響が小さいケース（Non-Affected / Lower-Impact Apps）

- JobScheduler / WorkManager / DownloadManager など quota-managed work を使わないアプリ。
- job が quota 内で短時間に完了するアプリ。
- FGS のみで work を行い、JobScheduler job を同時に走らせないケース。
- user-initiated data transfer job として適切に実装され、必要 permission / state を満たすケース。
- quota stop / pending を想定した retry / resume / user notification が既に実装されているケース。

---

# 顧客影響（Customer Impact）

## 影響度（Impact Level）

- 要確認。長時間 background work / data transfer を JobScheduler 系 API で行うアプリでは Medium 以上になり得る。

## 顧客向け説明

Android 16 へ OS アップデートすると、JobScheduler の実行時間 quota がより厳密に適用されます。これは targetSdkVersion 36 に上げた時だけの変更ではありません。targetSdkVersion 35 のままでも、Android 16 端末上で JobScheduler / WorkManager / DownloadManager を通じた長時間 work を実行する場合は、quota により job が停止または待機になる可能性があります。

特に、ユーザーが画面を見ている間に開始した job が画面から離れた後も走り続けるケースや、foreground service と job を併用しているケースでは、Android 16 で quota 対象になる点に注意が必要です。ユーザーが明示的に開始した長時間データ転送は、ordinary job ではなく user-initiated data transfer job を検討してください。

---

# 推奨対応候補（Recommended Action Candidates）

- JobScheduler / WorkManager / DownloadManager 経由の long-running work を棚卸しする。
- `JobParameters#getStopReason()` を `onStopJob()` 内でログ化する。
- WorkManager を使う場合は `WorkInfo#getStopReason()` の取得・ログ化を検討する。
- Android 16 では `JobScheduler#getPendingJobReasonsHistory()` を使い、job が start しない理由を調査できるようにする。
- ordinary job で実装している user-visible upload / download / sync は user-initiated data transfer job への移行を検討する。
- app standby bucket を active / working_set / frequent / rare / restricted に切り替えて、quota stop / retry / pending の UX を検証する。
- `OVERRIDE_QUOTA_ENFORCEMENT_TO_TOP_STARTED_JOBS` / `OVERRIDE_QUOTA_ENFORCEMENT_TO_FGS_JOBS` を使い、Android 16 default enforcement と override 時の差を比較する。

---

# テスト観点（Test Matrix）

| 観点 | 検証内容 |
| --- | --- |
| Android 15 端末上の targetSdkVersion 35 | 既存挙動の baseline。 |
| Android 16 端末上の targetSdkVersion 35 | OS update だけで quota behavior が変わるか確認。 |
| Android 16 端末上の targetSdkVersion 36 | targetSdkVersion 35 と差がないことを確認。 |
| Android 15 端末上の targetSdkVersion 36 | 可能なら targetSdkVersion だけでは Android 16 behavior が発生しないことを確認。 |
| regular job runtime quota | quota 消費、stop reason、reschedule を確認。 |
| expedited job runtime quota | EJ quota、minimum execution guarantee、quota stop を確認。 |
| app standby bucket: active / working_set / frequent / rare / restricted | `adb shell am set-standby-bucket` で bucket を切り替え、実行時間と pending を比較。 |
| app top / visible state で job start | visible 中に開始し、invisible 後に継続させる。 |
| foreground service と job の同時実行 | FGS と ordinary / expedited job の併用時に quota stop するか確認。 |
| foreground service なしの job 実行 | 通常 quota と比較。 |
| WorkManager task stop reason | `WorkInfo#getStopReason()` の値と platform stop reason の対応を確認。 |
| JobScheduler `JobParameters#getStopReason()` | `STOP_REASON_QUOTA` をログ化。 |
| `JobScheduler#getPendingJobReasonsHistory()` | job が未実行の理由履歴を取得。 |
| DownloadManager long-running transfer | 大きな download が Android 16 で stop / retry / pending するか確認。 |
| ordinary job vs user-initiated data transfer job | 同じ転送処理で quota 挙動を比較。 |
| compat override enabled / disabled | `am compat enable` で top / FGS enforcement を無効化し差分を確認。 |
| job stopped / rescheduled / never started | stop reason と pending reason history で切り分ける。 |
| logs / metrics / user-visible failure / retry behavior | ユーザーに見える失敗、重複 retry、通知の有無を確認。 |
| battery optimization settings との相互作用 | battery saver / background restriction と quota reason の違いを確認。 |

---

# Human Decision Placeholder

最終優先度（Final Priority）:
- 未判断（Human decision required）

判断（Decision）:
- 未判断（Explain / Monitor / Ignore / Further investigation required）

判断メモ:
- 本調査は evidence と影響条件を整理したもの。最終的な顧客通知優先度、severity、release readiness は repository owner が判断する。
