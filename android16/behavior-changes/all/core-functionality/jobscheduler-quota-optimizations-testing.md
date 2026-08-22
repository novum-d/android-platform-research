# JobScheduler quota optimizations - Testing 調査レポート

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
- https://developer.android.com/about/versions/16/behavior-changes-all#job-quota-opt-testing

Page:
- Behavior changes: all apps

Category:
- Core functionality

Parent section:
- JobScheduler quota optimizations

Section:
- Testing

### 分類スナップショット（Classification Snapshot）

主分類（Primary classification）:
- `OS_UPDATE_ALL_APPS`

補足条件:
- 初期分類仮説の `OS_UPDATE_ALL_APPS_WITH_TESTING_OVERRIDE` は `android16/behavior-changes/APPLICABILITY_CLASSIFICATION.md` の正式ラベルではないため、primary classification は `OS_UPDATE_ALL_APPS` とする。
- Testing override / compat override は追加条件として扱う。

早見表（At-a-glance impact）:

| 確認項目（Question） | 回答（Answer） | 根拠（Evidence） |
| --- | --- | --- |
| Android 16 に OS アップデートしただけで適用されるか | Yes | 公式 all apps ページは Android 16 上で実行される全アプリに影響し得る変更として掲載している。AOSP `QuotaController` に targetSdkVersion 36 gate は見つからない。 |
| targetSdkVersion 36 以上が必要か | No | quota 判定と testing override 判定は uid、standby bucket、process state、compat override、job type に基づき、targetSdkVersion を参照しない。 |
| Testing section 固有の条件はあるか | Yes | Android 16 端末上で `am compat enable` により package 単位の override を設定すること、または `am set-standby-bucket` / `am get-standby-bucket` を使って standby bucket を操作・確認すること。 |
| `am compat enable` は新制限を有効化するか | No | AOSP `QuotaController` では該当 Change ID が enabled のとき、top-started job / FGS-concurrent job の quota enforcement を無効化する方向に働く。 |
| Compat Change ID が関係するか | Yes | `OVERRIDE_QUOTA_ENFORCEMENT_TO_FGS_JOBS` = `341201311`、`OVERRIDE_QUOTA_ENFORCEMENT_TO_TOP_STARTED_JOBS` = `374323858`。どちらも `@Disabled` / `@Overridable`。 |

### 調査日（Investigation Date）

2026-07-04

### 信頼度（Confidence）

- High

理由:
- 公式文書の Testing セクションを再確認し、依頼された Original statements と一致することを確認した。
- AOSP `QuotaController` で Change ID、default state、override enabled 時の分岐を確認した。
- `am compat enable` が `PlatformCompat` override に反映される経路を確認した。
- `am set-standby-bucket` / `am get-standby-bucket` が `UsageStatsManager` / `AppStandbyController` に接続される経路を確認した。
- targetSdkVersion 36 gate は見つからない。

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
- App API condition: JobScheduler quota 管理対象 work を使うこと。WorkManager / JobScheduler / DownloadManager の task が対象になり得る。
- Testing condition: `OVERRIDE_QUOTA_ENFORCEMENT_TO_TOP_STARTED_JOBS` または `OVERRIDE_QUOTA_ENFORCEMENT_TO_FGS_JOBS` を package に対して enable する、または standby bucket を shell command で変更・確認する。
- App state/process condition: standby bucket、top / visible state、invisible 後の継続、foreground service 同時実行、user-initiated job かどうか。

Compat framework:
- Change ID: `341201311`
- Change name: `OVERRIDE_QUOTA_ENFORCEMENT_TO_FGS_JOBS`
- Default state: `@Disabled`
- Toggleable for testing: Yes。`@Overridable`。`adb shell am compat enable OVERRIDE_QUOTA_ENFORCEMENT_TO_FGS_JOBS <package>`
- Semantics: enabled のとき FGS-concurrent job の Android 16 quota enforcement を無効化し、旧来の quota-free threshold に近い挙動へ戻す。

- Change ID: `374323858`
- Change name: `OVERRIDE_QUOTA_ENFORCEMENT_TO_TOP_STARTED_JOBS`
- Default state: `@Disabled`
- Toggleable for testing: Yes。`@Overridable`。`adb shell am compat enable OVERRIDE_QUOTA_ENFORCEMENT_TO_TOP_STARTED_JOBS <package>`
- Semantics: enabled のとき top-started job の Android 16 quota enforcement を無効化し、top state 中に開始した job を quota-free tracking に戻す。

補足:
- Android 16 compat framework 公式一覧ページでは上記 2 名は検索で確認できなかった。一方、Behavior Change 本文の testing command と AOSP `@ChangeId` / `@Disabled` / `@Overridable` 定義で確認できる。

分類信頼度（Classification confidence）:
- High

分類根拠（Classification evidence）:
- Official documentation page: `behavior-changes-all` の `JobScheduler quota optimizations > Testing`。
- Original applicability statement: Android 16 上で running する全アプリ向けの all apps ページに掲載。
- AOSP targetSdk gate: 見つからない。
- Compat framework entry: AOSP `QuotaController` の Change ID と公式 testing command。

---

# エグゼクティブサマリー（Executive Summary）

Android 16 の JobScheduler quota optimizations では、top state 中に開始して visible でなくなった後も続く job と、foreground service と同時実行される job が default で runtime quota に従う。Testing セクションは、この default Android 16 挙動をアプリごとに比較検証するための手順を説明している。

重要な点は、公式文書の `adb shell am compat enable OVERRIDE_QUOTA_ENFORCEMENT_TO_TOP_STARTED_JOBS <package>` と `adb shell am compat enable OVERRIDE_QUOTA_ENFORCEMENT_TO_FGS_JOBS <package>` は、Android 16 の enforcement を有効化するコマンドではなく、該当 enforcement を無効化する testing override であること。AOSP `QuotaController` でも、これらの Change ID が enabled の場合に top-started job / FGS-concurrent job を旧来の quota-free に近い扱いへ戻す分岐になっている。

この Testing 項目は targetSdkVersion 36 化の影響ではない。Android 16 OS 上で JobScheduler / WorkManager / DownloadManager の quota-managed work を使うアプリが対象であり、targetSdkVersion 35 と 36 のどちらでも同じ testing override と standby bucket 操作を使って検証する。

---

# 公式ドキュメント確認（Original Documentation）

## 原文（Statements）

公式文書では、Testing セクションで次を説明している。

- Android 16 端末上では、特定の job quota optimizations の override を enable してアプリ挙動をテストできる。
- "top state will adhere to job runtime quota" の enforcement を無効化するには、`adb shell am compat enable OVERRIDE_QUOTA_ENFORCEMENT_TO_TOP_STARTED_JOBS APP_PACKAGE_NAME` を実行する。
- "jobs that are executing while concurrently with a foreground service will adhere to the job runtime quota" の enforcement を無効化するには、`adb shell am compat enable OVERRIDE_QUOTA_ENFORCEMENT_TO_FGS_JOBS APP_PACKAGE_NAME` を実行する。
- standby bucket の挙動をテストするには、`adb shell am set-standby-bucket APP_PACKAGE_NAME active|working_set|frequent|rare|restricted` を使う。
- 現在の standby bucket を理解するには、`adb shell am get-standby-bucket APP_PACKAGE_NAME` を使う。

## ドキュメント差分確認（Documentation Delta）

- 依頼された Original statements と、2026-07-04 時点で確認した公式本文に実質的な差分はない。
- Testing セクションは親項目の base behavior を前提にしている。つまり、default Android 16 では top-started job と FGS-concurrent job が quota に従い、testing override を enable すると該当 enforcement を無効化して比較できる。

---

# 変更内容（What Changed）

## Testing section の中心

- `OVERRIDE_QUOTA_ENFORCEMENT_TO_TOP_STARTED_JOBS`:
  - default: disabled。Android 16 の default enforcement が有効。
  - enabled: top state 中に開始した job を quota-free tracking に戻す。
  - 公式 command は「top state job の quota enforcement を無効化する」ために `enable` する。

- `OVERRIDE_QUOTA_ENFORCEMENT_TO_FGS_JOBS`:
  - default: disabled。Android 16 の default enforcement が有効。
  - enabled: foreground service process state を quota-free threshold に戻す。
  - 公式 command は「FGS 同時実行 job の quota enforcement を無効化する」ために `enable` する。

- `am set-standby-bucket` / `am get-standby-bucket`:
  - standby bucket による quota 差を手動テストするための diagnostic / setup command。
  - AOSP では ActivityManager shell command から `IUsageStatsManager` に接続され、`AppStandbyController` の bucket state に反映される。

## 適用条件（Applicability）

### OS アップデート時の挙動（OS Update Behavior）

- Android 16 に OS アップデートしただけで、JobScheduler quota policy の default 挙動が変わる。
- targetSdkVersion 35 のアプリでも、Android 16 端末上で quota-managed work を使えば影響し得る。
- Testing override は Android 16 の default policy と override policy の比較に使う。

### targetSdkVersion 36 化時の挙動（targetSdkVersion 36 Behavior）

- targetSdkVersion 36 は必要条件ではない。
- Android 15 端末上で targetSdkVersion 36 にしても、Android 16 の default quota enforcement と testing override 挙動そのものは発生しない。
- 顧客向け説明では「Android 16 へ OS アップデートしただけの影響」と「targetSdkVersion 36 化した時の影響」を混ぜない。

### Compat override 有効時の挙動（Testing Override Behavior）

- `am compat enable` は package に対する compat change override を enabled にする。
- この 2 つの Change ID は名前に `OVERRIDE_` があり、AOSP 実装でも enabled の場合に enforcement を緩和する。
- default Android 16 挙動を確認したい場合は、これらの override を有効にしない、または無効化した状態でテストする。

---

# AOSP 調査（AOSP Investigation）

## 関連ファイル（Related Files）

- `frameworks-base/apex/jobscheduler/service/java/com/android/server/job/controllers/QuotaController.java`
- `frameworks-base/services/core/java/com/android/server/am/ActivityManagerShellCommand.java`
- `frameworks-base/services/core/java/com/android/server/compat/PlatformCompat.java`
- `frameworks-base/apex/jobscheduler/service/java/com/android/server/usage/AppStandbyController.java`
- `frameworks-base/apex/jobscheduler/service/java/com/android/server/job/controllers/JobStatus.java`
- `frameworks-base/apex/jobscheduler/service/java/com/android/server/job/JobSchedulerService.java`
- `frameworks-base/apex/jobscheduler/framework/java/android/app/job/JobScheduler.java`
- `frameworks-base/apex/jobscheduler/framework/java/android/app/job/JobParameters.java`
- `frameworks-base/apex/jobscheduler/framework/java/android/app/job/JobInfo.java`
- `frameworks-base/services/tests/mockingservicestests/src/com/android/server/job/controllers/QuotaControllerTest.java`

## Checkout hygiene

- `frameworks-base` は status 確認時点で clean。
- `android-15.0.0_r36` と `android-16.0.0_r4` tag を明示して比較した。
- local working tree の未追跡ファイルや別作業ファイルは AOSP evidence として扱っていない。

## 確認したソース文脈（Source Context Reviewed）

| ファイル / シンボル（File / symbol） | Android 15 baseline | Android 16 behavior | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| `QuotaController.OVERRIDE_QUOTA_ENFORCEMENT_TO_FGS_JOBS` | Android 15 tag にも `@Disabled` / `@Overridable` の Change ID として存在。FGS enforcement は feature flag と override の組み合わせで判定。 | `341201311`。`@Disabled` / `@Overridable`。default では enforcement が有効で、enabled の場合に override で緩和。 | Testing command の Change ID、default state、force enable 可能性を確認する根拠。 |
| `QuotaController.OVERRIDE_QUOTA_ENFORCEMENT_TO_TOP_STARTED_JOBS` | Android 15 tag にも `@Disabled` / `@Overridable` の Change ID として存在。top-started enforcement は feature flag と override の組み合わせで判定。 | `374323858`。`@Disabled` / `@Overridable`。default では enforcement が有効で、enabled の場合に override で緩和。 | Testing command の Change ID、default state、force enable 可能性を確認する根拠。 |
| `QuotaController.prepareForExecutionLocked()` | `!Flags.enforceQuotaPolicyToTopStartedJobs()` または compat override enabled の場合、top job は `mTopStartedJobs` に入り timer tracking から外れる。 | compat override enabled の場合だけ、top job は `mTopStartedJobs` に入り timer tracking から外れる。default では timer tracking される。 | top-started job の enforcement を `am compat enable` で無効化できる直接根拠。 |
| `QuotaController.isTopStartedJobLocked()` | feature flag off または override enabled なら top-started exemption を認める。 | override enabled の場合だけ `mTopStartedJobs` を参照する。 | override disabled/default では top-started job が quota-free 扱いにならない根拠。 |
| `QuotaController.getProcessStateQuotaFreeThreshold()` | `Flags.enforceQuotaPolicyToFgsJobs()` が true かつ override disabled の場合だけ threshold は `PROCESS_STATE_BOUND_TOP`。それ以外は `PROCESS_STATE_FOREGROUND_SERVICE`。 | override disabled/default では threshold は `PROCESS_STATE_BOUND_TOP`。override enabled の場合だけ `PROCESS_STATE_FOREGROUND_SERVICE`。 | FGS-concurrent job の enforcement を `am compat enable` で無効化できる直接根拠。 |
| `ActivityManagerShellCommand.runCompat()` | shell の `am compat` command を処理する。 | `enable` は change id / name を解決し、`CompatibilityChangeConfig` の enabled set に入れて `PlatformCompat#setOverrides` へ渡す。 | 公式 `adb shell am compat enable ...` が package compat override に反映される根拠。 |
| `PlatformCompat.setOverrides()` | compat override を package 単位で設定し、必要に応じて対象 package を kill する。 | enabled / disabled override を `PackageOverride` として保存する。 | `am compat enable` が `CompatChanges.isChangeEnabled` / `PlatformCompat.isChangeEnabledByUid` の結果を変える根拠。 |
| `ActivityManagerShellCommand.runSetStandbyBucket()` | shell から app standby bucket を設定する command。 | `active|working_set|frequent|rare|restricted` を bucket value に変換し、`IUsageStatsManager#setAppStandbyBucket(s)` を呼ぶ。 | 公式 `am set-standby-bucket` の testing setup の根拠。 |
| `ActivityManagerShellCommand.runGetStandbyBucket()` | shell から app standby bucket を取得する command。 | package 指定時は `IUsageStatsManager#getAppStandbyBucket` の値を出力する。 | 公式 `am get-standby-bucket` の diagnostic command の根拠。 |
| `AppStandbyController.setAppStandbyBucket()` / `getAppStandbyBucket()` | UsageStats 側で standby bucket を保持・返却する。 | shell caller は reason を付けて bucket を設定できる。`getAppStandbyBucket` は idle history から current bucket を返す。 | set/get command が JobScheduler quota の standby bucket 入力に接続される根拠。 |
| `QuotaController.maybeUpdateConstraintForPkgLocked()` / `isWithinQuotaLocked()` | standby bucket と timing session に基づき quota constraint を更新する。 | real standby bucket を使って regular / expedited job の quota を判定する。 | standby bucket manipulation が quota behavior testing に有効である根拠。 |
| `QuotaControllerTest` | Android 15 では feature flag と override の組み合わせで挙動を検証。 | Android 16 test は default で top job も out-of-quota になり、override enabled で top-started job が quota-free 側に残ることを検証する。 | Testing override の actual runtime behavior を unit test で裏付ける根拠。 |
| `JobStatus.setExpeditedJobQuotaApproved()` / `constraintToStopReason()` | quota constraint が false になると `STOP_REASON_QUOTA` へ対応。 | 同左。Android 16 で quota enforcement 対象が増えるため観測点として重要。 | `JobParameters#getStopReason()` で quota stop を確認する根拠。 |
| `JobScheduler#getPendingJobReasonsHistory()` / `JobSchedulerService#getPendingJobReasonsHistory()` | tag 上は API / service 実装が存在。 | Android 16 公式文書は pending job reason history の利用を推奨。service は calling uid の job について履歴を返す。 | stopped jobs と never-started jobs を切り分ける testing guidance の根拠。 |

必須記入項目（Required context）:
- Entry point / caller: アプリは `JobScheduler.schedule()`、WorkManager、DownloadManager などから job を登録する。Job 実行時に `JobSchedulerService` が `QuotaController` を通じて quota constraint と timer tracking を管理する。
- Runtime path: app scheduled job -> `JobSchedulerService` -> `JobStatus` -> `QuotaController.prepareForExecutionLocked()` -> quota timer / constraint update -> stop reason / pending reason history。
- Testing command path: `adb shell am compat enable ...` -> `ActivityManagerShellCommand.runCompat()` -> `PlatformCompat.setOverrides()` -> `QuotaController` の `isChangeEnabledByUid(...)` 判定。
- Standby bucket command path: `adb shell am set-standby-bucket ...` -> `ActivityManagerShellCommand.runSetStandbyBucket()` -> `IUsageStatsManager` -> `AppStandbyController` -> JobScheduler quota の bucket 入力。
- Excluded code paths: AlarmManager、abandoned empty jobs stop reason、`setImportantWhileForeground` deprecation、battery saver global policy は JobScheduler 周辺の別変更であり、本 Testing セクションの compat override / standby bucket 操作を直接決めないため主根拠から除外した。

## 差分解釈（Diff Interpretation）

| 確認した差分（Observed diff） | 解釈（Interpretation） | Behavior Change との関係 | 信頼度（Confidence） |
| --- | --- | --- | --- |
| Android 16 `QuotaController` では top-started job exemption が `OVERRIDE_QUOTA_ENFORCEMENT_TO_TOP_STARTED_JOBS` enabled 時だけに限定される。 | Changed condition / changed default。default で top-started job は quota 対象。override enabled で enforcement を無効化。 | Testing command が「top state will adhere to job runtime quota」を disable する根拠。 | High |
| Android 16 `QuotaController` では FGS quota-free threshold が default で `PROCESS_STATE_BOUND_TOP` になり、`OVERRIDE_QUOTA_ENFORCEMENT_TO_FGS_JOBS` enabled 時だけ `PROCESS_STATE_FOREGROUND_SERVICE` へ戻る。 | Changed condition / changed default。default で FGS-concurrent job は quota 対象。override enabled で enforcement を無効化。 | Testing command が「FGS concurrent jobs will adhere to quota」を disable する根拠。 | High |
| Android 15 には `Flags.enforceQuotaPolicyToTopStartedJobs()` / `Flags.enforceQuotaPolicyToFgsJobs()` が残るが、Android 16 では default policy 側に組み込まれる。 | Removed / changed gate。Android 16 では feature flag ではなく compat override が testing 比較軸になる。 | Android 16 default behavior と testing override behavior を分ける根拠。 | High |
| `ActivityManagerShellCommand.runCompat()` は `enable` された change name を enabled set に入れ、`PlatformCompat` override として package に設定する。 | Command behavior evidence。`enable` は change を enabled にするが、本 Change ID は enabled の意味が「enforcement override」。 | 公式 command の `enable` と実際の quota enforcement disabled semantics を接続する。 | High |
| `ActivityManagerShellCommand.runSetStandbyBucket()` / `runGetStandbyBucket()` は UsageStats service に bucket 操作を委譲する。 | Testing diagnostic behavior。bucket を手動設定・確認できる。 | standby bucket quota testing の根拠。 | High |
| `QuotaController` は targetSdkVersion を参照せず、uid / standby bucket / process state / job type / compat override を見る。 | No targetSdk gate found。 | `OS_UPDATE_ALL_APPS` 分類を支持する。 | High |

---

# Facts / Observations / Hypotheses / Conclusions

## Facts

- 公式文書は Android 16 all apps ページにこの項目を掲載しており、Android 16 上で実行される全アプリに影響し得る変更として説明している。
- Testing セクションは `OVERRIDE_QUOTA_ENFORCEMENT_TO_TOP_STARTED_JOBS` と `OVERRIDE_QUOTA_ENFORCEMENT_TO_FGS_JOBS` を `am compat enable` することで、それぞれの quota enforcement を無効化できると説明している。
- AOSP `QuotaController` では 2 つの Change ID が `@Disabled` / `@Overridable` として定義されている。
- AOSP `QuotaController` では、該当 Change ID が enabled の場合に top-started job または FGS-concurrent job の quota enforcement が緩和される。
- `am set-standby-bucket` / `am get-standby-bucket` は ActivityManager shell command と UsageStats/AppStandbyController 経由で実装されている。

## Observations

- command 名が `am compat enable` であるため、表面的には「制限を有効化する」ように見えるが、この Change ID の意味は `OVERRIDE_...` であり、AOSP 実装上は Android 16 default enforcement を無効化する。
- Testing セクションは base behavior の説明ではなく、Android 16 default behavior と旧挙動に近い override behavior を比較するための手順である。
- `am get-standby-bucket` は diagnostic として有効だが、出力は実装上 numeric bucket になり得るため、テスト記録では入力 bucket name と取得結果の対応を明記する必要がある。

## Hypotheses

- WorkManager と DownloadManager は公式文書で影響対象とされるが、WorkManager の stop reason API は Jetpack 側、DownloadManager の詳細動作は platform JobScheduler 利用箇所に依存する。アプリ単位の最終挙動は実機 / library version での確認が必要。
- Android 15 tag には同名 Change ID と feature flag 分岐が準備済みだが、Android 15 製品上での default flag 状態は端末 build に依存し得る。Android 16 behavior の比較対象としては、明示 tag / build 条件を記録する必要がある。

## Conclusions

- Primary classification は `OS_UPDATE_ALL_APPS`。
- Android 16 / targetSdkVersion 35 と Android 16 / targetSdkVersion 36 の期待挙動は同じ。targetSdkVersion 36 化だけでこの Testing 項目の影響が発生する evidence はない。
- `OVERRIDE_QUOTA_ENFORCEMENT_TO_TOP_STARTED_JOBS` / `OVERRIDE_QUOTA_ENFORCEMENT_TO_FGS_JOBS` は default enforcement を disable する testing override として扱う。
- standby bucket testing では `set-standby-bucket` で状態を作り、`get-standby-bucket`、`JobParameters#getStopReason()`、`JobScheduler#getPendingJobReasonsHistory()` を組み合わせて、stopped job と never-started job を分けて確認する。

---

# 期待挙動マトリクス（Required OS / targetSdkVersion Matrix）

| OS | targetSdkVersion | 期待挙動（Expected behavior） | 顧客向け説明での扱い |
| --- | --- | --- | --- |
| Android 15 | 35 | Android 16 の default quota optimization は適用されない。Android 15 tag には準備コードがあるが、feature flag / build 状態との比較が必要。 | baseline。 |
| Android 16 | 35 | JobScheduler quota optimization と Testing override が利用可能。top-started / FGS-concurrent jobs は default で quota 対象。 | OS update impact。targetSdkVersion 36 化と混ぜない。 |
| Android 16 | 36 | targetSdkVersion 35 と同じ platform policy。default enforcement と compat override testing が利用可能。 | OS update impact。targetSdkVersion 36 は必要条件ではない。 |
| Android 15 | 36 | targetSdkVersion 36 の値だけでは Android 16 の default policy は発生しない。比較可能な build では Android 15 側 feature flag 状態を記録する。 | targetSdkVersion 36 単独影響ではないことの比較対象。 |

---

# 詳細マトリクス（Required Scenario Matrix）

| シナリオ（Scenario） | 期待挙動（Expected behavior） | 根拠 / 備考 |
| --- | --- | --- |
| Android 16 / targetSdkVersion 35 / default quota enforcement | 適用される。 | targetSdkVersion gate なし。 |
| Android 16 / targetSdkVersion 36 / default quota enforcement | 適用される。 | targetSdkVersion 35 と同じ。 |
| Android 16 / regular job / default enforcement | standby bucket / runtime quota の対象。 | `QuotaController.isWithinQuotaLocked()`。 |
| Android 16 / expedited job / default enforcement | expedited quota の対象。 | `isWithinEJQuotaLocked()` と EJ timing session。 |
| Android 16 / job starts while app is top / visible / default enforcement | app が invisible 後も継続すると quota 対象。 | top-started exemption は override enabled 時のみ。 |
| Android 16 / job continues after app becomes invisible / default enforcement | quota に従い、quota exhausted なら stop / pending になり得る。 | `maybeUpdateConstraintForPkgLocked()`。 |
| Android 16 / job running concurrently with foreground service / default enforcement | quota 対象。 | default threshold は `PROCESS_STATE_BOUND_TOP`。 |
| Android 16 / `OVERRIDE_QUOTA_ENFORCEMENT_TO_TOP_STARTED_JOBS` enabled | top-started enforcement が無効化され、top state 中に開始した job は quota-free 側に戻る。 | `prepareForExecutionLocked()` / `isTopStartedJobLocked()`。 |
| Android 16 / `OVERRIDE_QUOTA_ENFORCEMENT_TO_TOP_STARTED_JOBS` disabled/default | top-started job は quota 対象。 | Change ID は `@Disabled`。 |
| Android 16 / `OVERRIDE_QUOTA_ENFORCEMENT_TO_FGS_JOBS` enabled | FGS-concurrent enforcement が無効化され、FGS process state が quota-free threshold 側に戻る。 | `getProcessStateQuotaFreeThreshold()`。 |
| Android 16 / `OVERRIDE_QUOTA_ENFORCEMENT_TO_FGS_JOBS` disabled/default | FGS-concurrent job は quota 対象。 | Change ID は `@Disabled`。 |
| Android 16 / active standby bucket | generous だが finite quota。 | active allowed / window constants。 |
| Android 16 / working_set standby bucket | active より小さい quota 条件で検証する。 | App standby bucket quota table。 |
| Android 16 / frequent standby bucket | working_set より厳しい quota 条件で検証する。 | App standby bucket quota table。 |
| Android 16 / rare standby bucket | frequent より厳しい quota 条件で検証する。 | App standby bucket quota table。 |
| Android 16 / restricted standby bucket | 最も厳しい bucket として検証する。 | App standby bucket quota table。 |
| Android 16 / `am set-standby-bucket active` | UsageStats bucket を active に設定して quota 差をテスト。 | `runSetStandbyBucket()`。 |
| Android 16 / `am set-standby-bucket working_set` | working_set quota をテスト。 | `runSetStandbyBucket()`。 |
| Android 16 / `am set-standby-bucket frequent` | frequent quota をテスト。 | `runSetStandbyBucket()`。 |
| Android 16 / `am set-standby-bucket rare` | rare quota をテスト。 | `runSetStandbyBucket()`。 |
| Android 16 / `am set-standby-bucket restricted` | restricted quota をテスト。 | `runSetStandbyBucket()`。 |
| Android 16 / `am get-standby-bucket` | 現在 bucket を diagnostic として取得。 | `runGetStandbyBucket()`。 |
| Android 16 / WorkManager task | JobScheduler backend 経由なら platform quota の影響を受け得る。 | 公式文書。Jetpack 詳細は別 evidence。 |
| Android 16 / DownloadManager task | platform job 経由の長時間転送は影響を受け得る。 | 公式文書。実装詳細は個別確認。 |
| Android 16 / direct JobScheduler job | 直接影響を受ける。 | `QuotaController`。 |
| Android 16 / user-initiated data transfer job | ordinary job とは別扱い。長時間ユーザー可視転送の移行候補。 | `setUserInitiated(true)` / `shouldTreatAsUserInitiatedJob()`。 |
| Android 16 / ordinary upload/download job | quota stop / pending の影響を受け得る。 | 公式文書の移行推奨。 |
| Android 16 / JobParameters#getStopReason() | quota stop は `STOP_REASON_QUOTA` として観測可能。 | `JobStatus.constraintToStopReason()`。 |
| Android 16 / JobScheduler#getPendingJobReasonsHistory() | job が実行されない理由履歴を取得可能。 | `JobSchedulerService#getPendingJobReasonsHistory()`。 |
| Android 15 / targetSdkVersion 36 / same app behavior if technically comparable | Android 16 default policy ではない。Android 15 feature flag 状態を記録して比較する。 | r15 / r16 diff。 |

---

# 影響対象（Affected Apps）

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
- battery optimization / background execution 制限に敏感なアプリ。

---

# テスト観点（Testing Guidance）

## OS / targetSdkVersion 比較

- Android 15 端末上の targetSdkVersion 35。
- Android 16 端末上の targetSdkVersion 35。
- Android 16 端末上の targetSdkVersion 36。
- Android 15 端末上の targetSdkVersion 36 が検証可能な場合の比較。

## quota / state 比較

- regular job runtime quota。
- expedited job runtime quota。
- app standby bucket: active / working_set / frequent / rare / restricted。
- `adb shell am set-standby-bucket`。
- `adb shell am get-standby-bucket`。
- app top / visible state で job start。
- app invisible 後に job 継続。
- foreground service と job の同時実行。
- foreground service なしの job 実行。

## compat override 比較

- `OVERRIDE_QUOTA_ENFORCEMENT_TO_TOP_STARTED_JOBS` enabled / disabled。
- `OVERRIDE_QUOTA_ENFORCEMENT_TO_FGS_JOBS` enabled / disabled。
- enabled 状態で旧挙動に近い結果になるか。
- disabled/default 状態で Android 16 default enforcement が発生するか。

## diagnostic / logging

- WorkManager task stop reason。
- JobScheduler `JobParameters#getStopReason()`。
- JobScheduler `JobScheduler#getPendingJobReasonsHistory()`。
- DownloadManager long-running transfer。
- ordinary job vs user-initiated data transfer job。
- job stopped / rescheduled / never started の切り分け。
- logs / metrics / user-visible failure / retry behavior。
- battery optimization settings との相互作用。

---

# 推奨対応候補（Recommended Action Candidates）

- Android 16 実機または emulator で default enforcement と compat override enabled の両方を比較する。
- `am compat enable` の意味を test plan に明記する。これは enforcement を無効化する override であり、Android 16 default behavior の確認には使わない。
- standby bucket を `set-standby-bucket` で固定し、`get-standby-bucket` で確認してから job runtime / stop reason を測定する。
- top-started job と FGS-concurrent job の両方で、override enabled / disabled の差を見る。
- `STOP_REASON_QUOTA` と pending reason history をログ化し、stopped job と never-started job を分ける。
- ユーザーが明示的に開始した長時間 upload / download / sync は user-initiated data transfer job への移行を検討する。

---

# 顧客向け説明（Customer-facing Explanation）

Android 16 では、JobScheduler の quota enforcement が変わります。これは targetSdkVersion 36 に上げた時だけの変更ではなく、targetSdkVersion 35 のままでも Android 16 端末上では影響し得ます。

Testing セクションの `adb shell am compat enable OVERRIDE_QUOTA_ENFORCEMENT_TO_TOP_STARTED_JOBS <package>` と `adb shell am compat enable OVERRIDE_QUOTA_ENFORCEMENT_TO_FGS_JOBS <package>` は、Android 16 の新しい quota enforcement を有効化するコマンドではありません。AOSP 実装上は、該当 enforcement を無効化して旧挙動に近い状態と比較するための testing override です。

検証では、default Android 16 挙動、compat override enabled、standby bucket 差、stop reason、pending reason history を分けて記録してください。特に WorkManager / JobScheduler / DownloadManager で長時間 work を行うアプリ、foreground service と job を併用するアプリ、visible 中に開始した job が invisible 後も続くアプリは確認が必要です。

---

# Human Decision Placeholder

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
