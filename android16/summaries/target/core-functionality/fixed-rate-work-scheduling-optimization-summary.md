# 固定間隔処理のスケジューリング最適化（Fixed rate work scheduling optimization）- 1ページ要約

## 対象（Target）

Android 16 Behavior Change

比較元:
- android-15.0.0_r36

比較先:
- android-16.0.0_r4

注記:
- `android16/AGENTS.md` の既定の比較先は `android-16.0.0_r1` だが、この調査では依頼に従い `android-16.0.0_r4` を使用した。

## 適用条件（Applicability）

- 主分類（Primary classification）: `TARGET_SDK_36_CONDITIONAL`
- OS アップデート / 全アプリ: いいえ。Android 16 へ OS アップデートしただけで、targetSdkVersion 35 以下のアプリに既定で適用される根拠は確認していない。
- targetSdkVersion 36 以上: はい。executor 側の Change ID 288912692 と Timer 側の Change ID 351566728 は、いずれも targetSdkVersion 36 以上で既定で有効になる。
- その他の必須条件: `ScheduledExecutorService` / `ScheduledThreadPoolExecutor` または `Timer` の `scheduleAtFixedRate` を使用し、プロセスの凍結や一時停止などによって複数周期を実行できないまま復帰すること。
- Compat Change ID: executor は `STPE_SKIP_MULTIPLE_MISSED_PERIODIC_TASKS` / 288912692、Timer は `SKIP_MULTIPLE_MISSED_PERIODIC_TASKS` / 351566728
- Compat の既定状態: Android 16 / API level 36 以上を対象とするアプリで有効。

## 早見マトリクス（At-a-Glance Matrix）

| シナリオ（Scenario） | 影響（Impact） |
| --- | --- |
| Android 16 / targetSdkVersion 35 | 旧挙動。複数回分の未実行処理が連続実行される可能性がある |
| Android 16 / targetSdkVersion 36 | 新挙動。復帰時に即時実行される未実行処理は最大1回 |
| Android 16 / targetSdkVersion 36 + 必須条件 | fixed-rate の未実行分をまとめて処理する挙動に依存している場合、実行回数が減る |
| Android 15 / targetSdkVersion 36 | Android 15 r36 タグにも同じ gate があるため、実機と module の条件を含めて確認が必要 |

## 要約（Summary）

targetSdkVersion 36 以上では、`ScheduledThreadPoolExecutor` / `ScheduledExecutorService` と `Timer` の `scheduleAtFixedRate` は、実行できなかった複数周期分の処理を復帰直後にまとめて実行しない。
復帰時に即時実行される未実行処理は最大1回となる。復帰直後の負荷は下がる一方で、実行回数に依存する処理は見直しが必要である。
API 自体は `@Deprecated` ではない。ただし Android Lint は、cached process の復帰時に処理が集中する同じ問題を理由に、`DiscouragedApi` として警告する。Android 16 の変更で警告理由の一部は緩和されるが、古い OS や fixed-rate 固有の挙動に起因するリスクは残る。

## 顧客影響（Customer Impact）

- 要確認

理由:
- `scheduleAtFixedRate` を使わないアプリには直接影響しない。
- fixed-rate の未実行分を、ポーリング、再試行、同期、後処理、メトリクス送信の実行回数として見込んでいる場合は影響がある。

## 影響対象（Who Is Affected）

- `ScheduledThreadPoolExecutor` / `ScheduledExecutorService` または `Timer` の `scheduleAtFixedRate` を使うアプリ。
- 未実行分がまとめて実行されることに依存している処理。
- 定期的なポーリング、同期、メトリクス送信、再試行、後処理を fixed-rate で実装している処理。
- fixed-rate の処理が冪等でない実装。

## 対応要否（Required Action）

- 必須対応: 未実行回数を業務ロジックとして扱っている場合は、最終処理時刻から明示的に差分を計算する設計へ見直す。
- 推奨対応: `scheduleAtFixedRate` の利用箇所を棚卸しし、compat flag の有効時 / 無効時で復帰時の実行回数を比較する。
- 移行候補: 前回の実際の開始時刻基準でよい場合は `Timer#schedule(..., period)`、前回処理完了から一定間隔を空ける場合は `ScheduledExecutorService#scheduleWithFixedDelay`。
- スコープ注記: WorkManager / JobScheduler は本件の移行先ではない。プロセス終了後も再実行するという別の要件がある場合に限り、バックグラウンド処理として別途設計する。
- 不要: WorkManager / JobScheduler / AlarmManager のみを使い、executor / Timer の fixed-rate catch-up に依存していない場合。
- 実装例: [Fixed rate work scheduling optimization - 実装例](../../../behavior-changes/target/core-functionality/fixed-rate-work-scheduling-optimization-implementation-examples.md) に Before / After、Timer、Java、テストコードを記載。
- 実行挙動比較: [Fixed rate work scheduling optimization - 実行挙動比較](../../../behavior-changes/target/core-functionality/fixed-rate-work-scheduling-optimization-runtime-behavior-comparison.md) に 5 秒周期、process 復帰、長時間 task のタイムラインを記載。

## テストマトリクス（Test Matrix）

| 端末 OS（Device OS） | targetSdkVersion | 期待挙動（Expected behavior） |
| --- | --- | --- |
| Android 15 | 35 | fixed-rate の未実行分が複数回まとめて実行される可能性がある |
| Android 16 | 35 | OS アップデートだけでは新しい挙動は既定で有効にならない想定 |
| Android 16 | 36 | fixed-rate の未実行分が復帰時に即時実行される回数は最大1回 |

追加テスト:
- `STPE_SKIP_MULTIPLE_MISSED_PERIODIC_TASKS` compat flag の有効時 / 無効時。
- `Timer#scheduleAtFixedRate` は AOSP Change ID 351566728 の有効時 / 無効時を対象ビルドで比較する。
- アプリを凍結または一時停止に相当する状態へ置いた後、復帰時に fixed-rate の処理が何回実行されるか。
- `scheduleAtFixedRate` と `scheduleWithFixedDelay` の比較。
- ネットワーク、DB、UI 更新、ファイル I/O、再試行、後処理の各処理で、実行回数の減少が問題にならないか。

## 顧客向け説明（Explanation for Customers）

Android 16 へ OS アップデートしただけで、targetSdkVersion 35 以下のアプリにこの変更が既定で適用されるとは判断しません。
targetSdkVersion を 36 以上に上げると、Android 16 端末上では、`scheduleAtFixedRate` で実行できなかった周期分の処理が、復帰時に即時実行される回数は最大1回になります。
実行できなかった周期の回数分だけ処理する必要がある場合は、callback がまとめて呼ばれる回数に依存せず、最終処理時刻と現在時刻から必要な処理量を明示的に計算してください。

## 根拠（Evidence）

- Official documentation: https://developer.android.com/about/versions/16/behavior-changes-16#schedule-at-fixed-rate
- Compat framework: https://developer.android.com/about/versions/16/reference/compat-framework-changes#stpe_skip_multiple_missed_periodic_tasks
- AOSP files: `platform/libcore/ojluni/src/main/java/java/util/concurrent/ScheduledThreadPoolExecutor.java`、`platform/libcore/ojluni/src/main/java/java/util/Timer.java`、`platform/libcore/libcore.aconfig`、`platform/libcore/api/current.txt`、`frameworks-base/services/core/java/com/android/server/am/Freezer.java`
- AOSP source context: executor path は `scheduleAtFixedRate()` -> `ScheduledFutureTask#setNextRunTime()` -> Change ID 288912692、Timer path は `Timer#scheduleAtFixedRate()` -> `TimerThread#mainLoop()` -> Change ID 351566728。
- Diff interpretation: targetSdkVersion 36 で fixed-rate missed catch-up を最大 1 回に抑制。public API signature 変更なし。指定 tag 間の core implementation 差分はなし。
- Gate conclusion: Android 16 以上かつ targetSdkVersion 36 以上、さらに `scheduleAtFixedRate` の missed periods が発生する場合。

## 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- 未判断

判断（Decision）:
- 未判断

管理者向け注記:
- 最終優先度、影響度、リリース判断、顧客通知の優先度は、リポジトリ管理者が判断する。
