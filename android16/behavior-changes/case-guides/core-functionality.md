# Android 16 Core Functionality - ケース別対応手順

## 位置づけ

このファイルは Android 16 の core functionality 変更をケース別に実装・検証へ落とす companion guide である。
適用条件と根拠はリンク先の調査レポートを正とする。

## JobScheduler quota optimizations

Report: [JobScheduler quota optimizations](../all/core-functionality/jobscheduler-quota-optimizations.md)

Detection:
- `JobScheduler`、WorkManager、DownloadManager、expedited job、foreground service と job の併用を検索する。
- long-running upload / download / sync、stop reason、retry / resume の実装を確認する。

| ケース | 判定条件 | 対応手順 | 最低限の検証 |
| --- | --- | --- | --- |
| Quota-managed work なし | 対象 API を使わない | 通常の Android 16 regression のみ実施 | Android 16 smoke test |
| 短時間 job | active bucket の quota 内で安定して完了 | stop / pending reason のログを追加し現状維持 | standby bucket 別の完了確認 |
| top で開始し background へ継続 | Activity 離脱後も job が走る | 中断可能・idempotent にし、`STOP_REASON_QUOTA` 後の retry / resume を実装 | top-started override の有効 / 無効 |
| FGS と job を同時実行 | FGS 中の job を quota-free と仮定 | FGS と job の責務を整理し、quota stop を前提にする | FGS override の有効 / 無効 |
| User-visible data transfer | ユーザー操作で開始する長時間転送 | user-initiated data transfer job への移行候補を評価 | permission、notification、cancel、resume |
| WorkManager / DownloadManager | platform backend が quota 対象 | framework 固有の retry と `WorkInfo#getStopReason()` を確認 | quota stop 後の再実行と UX |

## Abandoned empty jobs stop reason

Report: [Abandoned empty jobs stop reason](../all/core-functionality/abandoned-empty-jobs-stop-reason.md)

Detection:
- direct `JobService` で `onStartJob()` が `true` を返す箇所を検索する。
- `JobParameters` の保持と `jobFinished()` の全完了経路を確認する。

| ケース | 判定条件 | 対応手順 | 最低限の検証 |
| --- | --- | --- | --- |
| Managed API のみ | WorkManager / DownloadManager、または direct JobService 外の AsyncTask | platform finding と分離して通常回帰 | stop reason と framework retry |
| 同期完了 | `onStartJob()` 内で完了 | `false` を返し active job を残さない | timeout が発生しないこと |
| 正常な非同期 job | strong reference 保持 + 必ず `jobFinished()` | `STOP_REASON_TIMEOUT` / abandoned を別集計 | complete / cancel / exception |
| Abandoned risk | reference 喪失または `jobFinished()` 漏れ | lifecycle bug を修正し、jobId / retry / backoff を記録 | `STOP_REASON_TIMEOUT_ABANDONED` の減少 |
| Frequent abandoned | 同 reason が反復 | frequency mitigation より先に lifecycle を修正 | aggressive backoff と復旧 |

## Fully deprecating `setImportantWhileForeground`

Report: [Fully deprecating JobInfo#setImportantWhileForeground](../all/core-functionality/fully-deprecating-jobinfo-setimportantwhileforeground.md)

| ケース | 判定条件 | 対応手順 | 最低限の検証 |
| --- | --- | --- | --- |
| API 未使用 | app / SDK とも利用なし | 対応不要。dependency update 時に再確認 | code search |
| `false` のみ | 特別扱いを要求していない | deprecated call を削除候補とする | `isImportantWhileForeground()==false` |
| 即時の短時間 work | `true` で速やかな実行を期待 | expedited job を用途・quota と合わせて評価 | timing / quota / fallback |
| User-started transfer | `true` で転送継続を期待 | user-initiated data transfer job を評価 | permission / user-visible state |
| User-visible continuous work | job より継続表示が主目的 | FGS policy と照合して foreground service を評価 | notification / stop / background |
| SDK内部利用 | app codeにないがdependencyが使用 | SDKを更新し、呼び出しても実際の動作を変えないことをvendorと確認 | dependency scan / Android 16 execution |

## Fixed rate work scheduling optimization

Report: [Fixed rate work scheduling optimization](../target/core-functionality/fixed-rate-work-scheduling-optimization.md)

Examples: [Implementation examples](fixed-rate-work-scheduling-optimization-implementation-examples.md)

| ケース | 判定条件 | 対応手順 | 最低限の検証 |
| --- | --- | --- | --- |
| Fixed-rate 未使用 | executor / Timer の fixed-rate catch-up なし | 対応不要 | code search |
| Missed count が不要 | 復帰時1回で最新状態へ同期できる | `scheduleAtFixedRate` を維持し処理を idempotent にする | compat flag on / off |
| Missed count が業務要件 | 未実行回数に応じた課金・集計・進行がある | 最終確定時刻から差分を明示計算する | 長時間 lifecycle gap |
| 前回開始基準で1回 | 複数 catch-up は不要 | `Timer#schedule(..., period)` を候補とする | pause / resume timeline |
| 完了後に間隔が必要 | task duration 後から一定間隔 | `scheduleWithFixedDelay` を候補とする | long-running task |
| Process death 後も必要 | in-process scheduler では要件不足 | WorkManager / JobScheduler を別要件として設計 | process kill / reboot |

## Ordered broadcast priority scope

Report: [Ordered broadcast priority scope no longer global](../all/core-functionality/ordered-broadcast-priority-scope-no-longer-global.md)

| ケース | 判定条件 | 対応手順 | 最低限の検証 |
| --- | --- | --- | --- |
| Ordered broadcast 未使用 | 順序依存なし | 対応不要 | receiver inventory |
| Same process 内のみ | receiver が同一 process | priority を維持可能だが依存を文書化 | high-to-low order |
| Same app / different process | `android:process` が異なる | cross-process order を削除し明示的 IPC へ移行 | receiver 順を変えても成立 |
| Different apps / SDK receiver | cross-app priority 依存 | service / provider / AIDL / queue 等へ移行 | install order / process state |
| `abortBroadcast()` / result mutation | priority 順を前提に後続を制御 | same process に閉じるか protocol 化 | abort / result propagation |
| System priority 値を使用 | app が high / low system boundary を指定 | app range 内へ修正 | priority clamp |

## ART internal changes

Report: [ART internal changes](../all/core-functionality/art-internal-changes.md)

| ケース | 判定条件 | 対応手順 | 最低限の検証 |
| --- | --- | --- | --- |
| Public API のみ | hidden / non-SDK / runtime layout 依存なし | 通常 regression | Android 16 + updated ART module |
| Reflection / hidden API | non-SDK member を参照 | public API へ移行し warning / exception を収集 | `NoSuchMethodError` / access error |
| JNI / native runtime assumption | object layout、GC、class internals 等に依存 | dependency vendor と更新し、runtime 別 native test | JNI failure / native crash |
| Third-party SDK dependency | app source外に internal access | known issues と SDK release を確認 | dependency update 前後 |
| Older OS + ART Mainline | Android 12+ で module 更新済み | OS version だけで除外せず regression | module version を記録 |

## 16 KB page size compatibility mode

Report: [16 KB page size compatibility mode](../all/core-functionality/16-kb-page-size-compatibility-mode.md)

| ケース | 判定条件 | 対応手順 | 最低限の検証 |
| --- | --- | --- | --- |
| Native code なし | APK / AAB に `.so` なし | 通常 regression | 16 KB device 起動 |
| Fully 16 KB aligned | 全 native library が対応 | 対応状態を維持し third-party 更新時に再検査 | startup / native feature |
| 4 KB aligned + compatibility mode 可 | Android 16 が compatibility mode を適用 | SDK / NDK 更新までの一時 mitigation とし、必要なら `pageSizeCompat` を評価 | dialog、crash、performance |
| Incompatible native SDK | mode でも crash / corruption /性能問題 | SDK 更新または rebuild を行う | full 16 KB build との比較 |
| 複数 ABI / dynamic feature | 一部 artifact のみ未対応 | ABI / split / feature ごとに alignment を検査 | install variant matrix |

## Verification status

- この分冊は documentation synthesis であり、対象アプリでの observed result は未実施。
- JobScheduler は stop reason、pending history、retry state を同一 test run で記録する。
- Native / ART は dependency version と build artifact hash を記録する。
