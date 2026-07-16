# Fixed rate work scheduling optimization - 1ページ要約（One Page Summary）

## 対象（Target）

Android 16 Behavior Change

From:
- android-15.0.0_r36

To:
- android-16.0.0_r4

Note:
- `android16/AGENTS.md` の既定 scope は `android-16.0.0_r1` だが、この調査では依頼に従い `android-16.0.0_r4` を使用した。

## 適用条件（Applicability）

- 主分類（Primary classification）: `TARGET_SDK_36_CONDITIONAL`
- OS アップデート / 全アプリ（OS update / all apps）: No。Android 16 へ OS アップデートしただけで targetSdkVersion 35 以下に default 適用される根拠は確認していない。
- targetSdkVersion 36 以上: Yes。executor 側 Change ID 288912692 と Timer 側 Change ID 351566728 はいずれも targetSdkVersion 36 以上で default enabled。
- その他の必須条件（Other required conditions）: `ScheduledExecutorService` / `ScheduledThreadPoolExecutor` または `Timer` の `scheduleAtFixedRate` を使い、process freeze / suspend 等で複数 period を missed してから復帰すること。
- Compat Change ID: executor は `STPE_SKIP_MULTIPLE_MISSED_PERIODIC_TASKS` / 288912692、Timer は `SKIP_MULTIPLE_MISSED_PERIODIC_TASKS` / 351566728
- Compat default state: Android 16 / API level 36 以上を target するアプリで enabled。

## 早見マトリクス（At-a-Glance Matrix）

| シナリオ（Scenario） | 影響（Impact） |
| --- | --- |
| Android 16 / targetSdkVersion 35 | 旧挙動。複数 missed executions が連続実行され得る |
| Android 16 / targetSdkVersion 36 | 新挙動。復帰時に即時実行される missed execution は最大 1 回 |
| Android 16 / targetSdkVersion 36 + 必須条件 | fixed-rate backlog catch-up に依存する処理で実行回数が減る |
| Android 15 / targetSdkVersion 36 | Android 15 r36 tag に同じ gate があり、実機・module 条件つきで要確認 |

## 要約（Summary）

targetSdkVersion 36 以上では、`ScheduledThreadPoolExecutor` / `ScheduledExecutorService` と `Timer` の `scheduleAtFixedRate` が missed period を複数回分まとめて即時 catch-up しない。
復帰時に即時実行される missed execution は最大 1 回になり、復帰直後の負荷は下がるが、実行回数に依存する処理は見直しが必要。
API は `@Deprecated` ではないが、Android Lint は同じ cached-process catch-up 問題を理由に `DiscouragedApi` として警告する。Android 16 の変更は警告理由を緩和するが、古い OS や fixed-rate semantics のリスクは残る。

## 顧客影響（Customer Impact）

- 要確認

理由:
- `scheduleAtFixedRate` を使わないアプリには直接影響しない。
- fixed-rate の missed backlog を polling、retry、sync、cleanup、metrics upload の実行回数として期待している場合は影響がある。

## 影響対象（Who Is Affected）

- `ScheduledThreadPoolExecutor` / `ScheduledExecutorService` または `Timer` の `scheduleAtFixedRate` を使うアプリ。
- missed execution がまとめて実行されることに依存している処理。
- 定期 polling / sync / metrics upload / retry / cleanup を fixed-rate で実装している処理。
- fixed-rate task が idempotent でない処理。

## 対応要否（Required Action）

- 必須対応: missed execution の回数を業務ロジックとして扱っている場合は、最終処理時刻から明示的に差分計算する設計へ見直す。
- 推奨対応: `scheduleAtFixedRate` 利用箇所を棚卸しし、compat flag enabled / disabled で復帰時の実行回数を比較する。
- 移行候補: 前回の実際の開始時刻基準でよい場合は `Timer#schedule(..., period)`、前回処理完了から一定間隔を空ける場合は `ScheduledExecutorService#scheduleWithFixedDelay`。process death 後も必要な deferrable work は WorkManager / JobScheduler。
- 不要: WorkManager / JobScheduler / AlarmManager のみを使い、executor / Timer の fixed-rate catch-up に依存していない場合。
- 実装例: [Fixed rate work scheduling optimization - 実装例](../../../behavior-changes/target/core-functionality/fixed-rate-work-scheduling-optimization-implementation-examples.md) に Before / After、Timer、Java、テストコードを記載。

## テストマトリクス（Test Matrix）

| 端末 OS（Device OS） | targetSdkVersion | 期待挙動（Expected behavior） |
| --- | --- | --- |
| Android 15 | 35 | missed fixed-rate executions が複数回 catch-up され得る |
| Android 16 | 35 | OS update だけでは新挙動は default enabled にならない想定 |
| Android 16 | 36 | missed fixed-rate execution の即時 catch-up は最大 1 回 |

追加テスト:
- `STPE_SKIP_MULTIPLE_MISSED_PERIODIC_TASKS` compat flag enabled / disabled。
- `Timer#scheduleAtFixedRate` は AOSP Change ID 351566728 の enabled / disabled を対象 build で比較。
- app を freeze / suspend 相当の状態に置いた後、復帰時に fixed-rate task が何回実行されるか。
- `scheduleAtFixedRate` と `scheduleWithFixedDelay` の比較。
- network、DB、UI 更新、file I/O、retry、cleanup の各処理で実行回数減少が問題にならないか。

## 顧客向け説明（Explanation for Customers）

Android 16 へ OS アップデートしただけで、targetSdkVersion 35 以下のアプリにこの変更が default 適用されるとは判断しません。
targetSdkVersion 36 以上に上げると、Android 16 端末上では `scheduleAtFixedRate` の missed execution が復帰時に最大 1 回しか即時実行されません。
missed period の回数分だけ処理する必要がある場合は、callback の catch-up 回数に依存せず、最終処理時刻と現在時刻から必要な処理量を明示的に計算してください。

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

Owner notes:
- 最終優先度、severity、release readiness、顧客 communication priority は repository owner が判断する。
