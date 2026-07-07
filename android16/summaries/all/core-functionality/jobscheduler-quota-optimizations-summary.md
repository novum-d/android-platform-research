# JobScheduler quota optimizations - 1ページ要約（One Page Summary）

## 対象（Target）

Android 16 Behavior Change:
- JobScheduler quota optimizations

From:
- android-15.0.0_r36

To:
- android-16.0.0_r4

Note:
- `android16/AGENTS.md` は To tag を `android-16.0.0_r1` としているが、本調査では依頼スコープに従い `android-16.0.0_r4` を使用。

## 適用条件（Applicability）

- 主分類（Primary classification）: `OS_UPDATE_ALL_APPS`
- OS アップデート / 全アプリ（OS update / all apps）: Yes。Android 16 上で JobScheduler quota 管理対象 work を使うアプリに targetSdkVersion と無関係に影響し得る。
- targetSdkVersion 36 以上: No。AOSP `QuotaController` に targetSdkVersion 36 gate は見つからない。
- その他の必須条件（Other required conditions）: JobScheduler / WorkManager / DownloadManager など quota-managed work を使うこと。特に long-running regular / expedited job、top state 開始後に invisible でも継続する job、FGS と同時実行する job、standby bucket quota に依存する job。
- Compat Change ID:
  - `OVERRIDE_QUOTA_ENFORCEMENT_TO_TOP_STARTED_JOBS` = `374323858`
  - `OVERRIDE_QUOTA_ENFORCEMENT_TO_FGS_JOBS` = `341201311`
- Compat default state: どちらも `@Disabled`。enable すると Android 16 の enforcement をテスト用に無効化する方向で働く。

## 早見マトリクス（At-a-Glance Matrix）

| シナリオ（Scenario） | 影響（Impact） |
| --- | --- |
| Android 16 / targetSdkVersion 35 | 影響あり。OS update だけで JobScheduler quota policy が変わる。 |
| Android 16 / targetSdkVersion 36 | 影響あり。targetSdkVersion 35 と同じ platform policy。 |
| Android 15 / targetSdkVersion 36 | Android 16 の quota optimization は適用されない。Android 15 側 feature flag 状態との比較は別途必要。 |
| Android 16 / active standby bucket | generous だが有限 quota。active でも長時間 job は quota 対象。 |
| Android 16 / top state 中に開始し invisible 後も継続 | default では quota 対象。 |
| Android 16 / FGS と job 同時実行 | default では quota 対象。 |
| Android 16 / user-initiated data transfer job | quota とは別扱い。permission / state 要件を満たす必要あり。 |

## 要約（Summary）

Android 16 では JobScheduler の regular / expedited job runtime quota がより厳密に適用される。active bucket、top-started job、FGS 併用 job でも quota に従うため、長時間 work を ordinary job で走らせるアプリは stop / pending / retry の増加に注意が必要。

## 顧客影響（Customer Impact）

- 影響あり / 要確認。
- 特に long-running upload / download / sync、WorkManager / DownloadManager 利用、FGS と job の併用、visible 中開始 job の継続に影響し得る。
- targetSdkVersion 36 化の影響ではなく、Android 16 へ OS アップデートした時の影響として説明する。

## 影響対象（Who Is Affected）

- JobScheduler を直接使うアプリ。
- WorkManager を使うアプリ。
- DownloadManager を使うアプリ。
- expedited jobs を使うアプリ。
- foreground service と job を併用するアプリ。
- app visible 中に job を開始し、invisible 後も継続するアプリ。
- active standby bucket なら quota 制限を受けない前提のアプリ。
- long-running upload / download / sync を ordinary job で実装しているアプリ。
- stop reason / pending reason をログ化していないアプリ。

## 対応要否（Required Action）

- 必須対応: 長時間 job が user-visible failure につながるアプリでは、quota stop / retry / resume の確認が必要。
- 推奨対応: `JobParameters#getStopReason()`、WorkManager では `WorkInfo#getStopReason()` をログ化する。Android 16 では `JobScheduler#getPendingJobReasonsHistory()` も利用する。
- 推奨対応: ユーザーが明示的に開始したデータ転送は user-initiated data transfer job への移行を検討する。
- 不要: quota-managed work を使わない、または job が quota 内で短時間に完了するアプリ。

## テストマトリクス（Test Matrix）

| 端末 OS（Device OS） | targetSdkVersion | 期待挙動（Expected behavior） |
| --- | --- | --- |
| Android 15 | 35 | 既存 baseline。Android 16 の default quota policy 変更なし。 |
| Android 16 | 35 | quota optimization が適用される。OS update impact を確認。 |
| Android 16 | 36 | targetSdkVersion 35 と同じ挙動。targetSdkVersion gate はなし。 |
| Android 15 | 36 | 可能なら targetSdkVersion 36 だけでは Android 16 behavior が発生しないことを比較。 |

追加テスト:

| 観点 | 期待確認 |
| --- | --- |
| regular job / expedited job | quota 消費、stop、reschedule を確認。 |
| standby bucket active / working_set / frequent / rare / restricted | `adb shell am set-standby-bucket` で bucket 差を確認。 |
| top / visible 中に job start | invisible 後も継続した時に quota 対象になることを確認。 |
| FGS と job 同時実行 | default で quota 対象になることを確認。 |
| `OVERRIDE_QUOTA_ENFORCEMENT_TO_TOP_STARTED_JOBS` enabled | top-started enforcement が無効化されることを比較。 |
| `OVERRIDE_QUOTA_ENFORCEMENT_TO_FGS_JOBS` enabled | FGS-concurrent enforcement が無効化されることを比較。 |
| ordinary job vs user-initiated data transfer job | 長時間転送で stop / pending の差を確認。 |
| `JobParameters#getStopReason()` | `STOP_REASON_QUOTA` を記録。 |
| `JobScheduler#getPendingJobReasonsHistory()` | job が開始しない理由履歴を取得。 |
| WorkManager / DownloadManager | platform quota による stop / retry / pending を実機で確認。 |

## 顧客向け説明（Explanation for Customers）

Android 16 へ OS アップデートすると、JobScheduler の実行時間 quota がより厳密に適用されます。これは targetSdkVersion 36 に上げた時だけの変更ではなく、targetSdkVersion 35 のままでも Android 16 端末上では影響し得ます。

特に、ユーザーが見ている間に開始した job が画面から離れた後も続く場合や、foreground service と job を同時に使っている場合、Android 16 では quota により job が停止または待機になる可能性があります。ユーザーが明示的に開始した長時間データ転送は、ordinary job ではなく user-initiated data transfer job を検討してください。

## 根拠（Evidence）

- Official documentation: https://developer.android.com/about/versions/16/behavior-changes-all#job-quota-opt
- AOSP files:
  - `frameworks-base/apex/jobscheduler/service/java/com/android/server/job/controllers/QuotaController.java`
  - `frameworks-base/apex/jobscheduler/service/java/com/android/server/job/controllers/JobStatus.java`
  - `frameworks-base/apex/jobscheduler/service/java/com/android/server/job/JobSchedulerService.java`
  - `frameworks-base/apex/jobscheduler/service/java/com/android/server/job/JobServiceContext.java`
  - `frameworks-base/apex/jobscheduler/framework/java/android/app/job/JobScheduler.java`
  - `frameworks-base/apex/jobscheduler/framework/java/android/app/job/JobParameters.java`
  - `frameworks-base/apex/jobscheduler/framework/java/android/app/job/JobInfo.java`
- AOSP source context:
  - `QuotaController.prepareForExecutionLocked()` が top-started job と user-initiated job の timer tracking を決める。
  - `QuotaController.getProcessStateQuotaFreeThreshold()` が FGS process state を quota-free とするかを決める。
  - `QcConstants` が active bucket の allowed time / window を定義する。
  - `JobStatus` が quota constraint を `STOP_REASON_QUOTA` と pending reason history に反映する。
- Diff interpretation:
  - Android 16 で top-started / FGS-concurrent job の quota enforcement が default policy になる。
  - active bucket quota default が generous but finite に変更される。
  - compat override は enforcement を有効化するものではなく、無効化する testing override。
- Gate conclusion:
  - targetSdkVersion gate なし。Android 16 OS / JobScheduler 実装上の all apps 変更。

## 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- Critical / High / Medium / Low

判断（Decision）:
- Explain / Monitor / Ignore / Further investigation required

補足:
- 最終優先度、顧客通知要否、release readiness は repository owner が判断する。
