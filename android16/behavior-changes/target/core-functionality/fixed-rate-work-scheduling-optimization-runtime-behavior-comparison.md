# 固定間隔処理のスケジューリング最適化 - 実行挙動比較

## 位置づけ（Scope）

このファイルは、5秒周期の同じ処理を次の3つの API で実装した場合について、実行時刻、遅延後の再開、長時間処理、キャンセルの違いを比較する補足資料である。
Behavior Change の根拠、適用条件、分類、confidence、人間の判断は、主レポートと1ページ要約を正とする。

主レポート:
- [fixed-rate-work-scheduling-optimization.md](fixed-rate-work-scheduling-optimization.md)

1ページ要約:
- [fixed-rate-work-scheduling-optimization-summary.md](../../../summaries/target/core-functionality/fixed-rate-work-scheduling-optimization-summary.md)

実装例:
- [fixed-rate-work-scheduling-optimization-implementation-examples.md](../../implementation-examples/fixed-rate-work-scheduling-optimization-implementation-examples.md)

## 対象（Target）

Android 16 Behavior Change:
- 文書: https://developer.android.com/about/versions/16/behavior-changes-16#schedule-at-fixed-rate
- セクション: Fixed rate work scheduling optimization

適用条件の要点:
- OS アップデート / 全アプリ: いいえ。targetSdkVersion 35 以下のアプリに、OS アップデートだけで既定適用される変更ではない。
- targetSdkVersion 36 以上: はい。
- その他の必須条件: `scheduleAtFixedRate` を使い、プロセスの凍結や一時停止などで複数周期を実行できない状態になること。

## 比較契約（Comparison Contract）

基本条件:

| 条件 | 値 |
| --- | --- |
| 初回遅延 | 0秒 |
| 周期 / 遅延 | 5秒 |
| スレッド | 1スレッド |
| 時刻 | 説明上は開始時点を0秒とする単調増加の経過時間 |
| 処理 | カメラの現在状態を1回取得する冪等な処理 |
| 重複実行 | 同じ定期処理の実行は重複しない |

シナリオごとに処理時間、プロセスの停止時間、targetSdkVersion を変更する。
タイムラインは API 仕様を理解するための概念上の期待挙動であり、実機で観測した値ではない。

## 比較対象（Comparison Targets）

| ID | API | 次回時刻の基準 | Missed backlog |
| --- | --- | --- | --- |
| A | `Timer#scheduleAtFixedRate(task, 0, 5_000)` | 初回予定時刻を基準とする 0、5、10、15 秒の fixed-rate grid | 元の grid へ追いつこうとする。Android 16 / target 36 では複数 missed execution の catch-up を抑制 |
| B | `Timer#schedule(task, 0, 5_000)` | 前回の実際の開始時刻 + 5 秒 | 遅れた実開始を新しい基準にするため、過去の grid を全件 catch-up しない |
| C | `ScheduledExecutorService#scheduleWithFixedDelay(task, 0, 5, SECONDS)` | 前回の完了時刻 + 5 秒 | 前回完了後に delay を置くため、過去の grid を catch-up しない |

## 早見比較（At-a-Glance）

| 比較項目 | A: fixed-rate | B: Timer schedule | C: fixed-delay executor |
| --- | --- | --- | --- |
| 5 秒の意味 | 初回予定から 5 秒刻み | 前回の実開始から 5 秒 | 前回の完了から 5 秒 |
| 2 秒かかる task の通常開始 | 0、5、10、15 | 0、5、10、15 | 0、7、14、21 |
| process 復帰後 | 元の grid へ追いつく方向 | 復帰時の実開始から再計算 | 復帰 task の完了から再計算 |
| task が period を超える | 完了直後に次回が開始され得る | 完了直後に次回が開始され得る | 完了後に必ず 5 秒 delay |
| Android 16 Behavior Change 対象 | Yes | No | No |
| 主な用途 | absolute-time cadence / task 間同期 | Timer を維持する最小差分 | polling、network、完了後に休止が必要な処理 |

## 用語

- 予定時刻: scheduler が基準時刻から計算した実行予定時刻。
- 実開始時刻: 処理が実際に開始した時刻。
- 実終了時刻: 処理が完了した時刻。
- 未実行処理: プロセスの凍結や一時停止などにより、予定時刻に実行できなかった処理。
- 追いつき実行: 未実行処理を復帰後に連続して実行し、fixed-rate の予定へ追いつくこと。

## 共通コード（Common Task）

```kotlin
private val invocation = AtomicInteger(0)

private fun loggedCameraPoll(
    implementation: String,
    workMillis: Long,
): Runnable = Runnable {
    val run = invocation.incrementAndGet()
    val startedAt = SystemClock.elapsedRealtime()
    logger.info("impl={} run={} event=start elapsed={}", implementation, run, startedAt)

    try {
        cameraRepository.reconcileCurrentState()
        if (workMillis > 0) {
            Thread.sleep(workMillis) // 挙動確認専用。production code では使用しない。
        }
    } finally {
        logger.info(
            "impl={} run={} event=end elapsed={}",
            implementation,
            run,
            SystemClock.elapsedRealtime(),
        )
    }
}
```

比較する登録コード:

```kotlin
timer.scheduleAtFixedRate(
    object : TimerTask() {
        override fun run() = fixedRateTask.run()
    },
    0L,
    5_000L,
)

timer.schedule(
    object : TimerTask() {
        override fun run() = timerScheduleTask.run()
    },
    0L,
    5_000L,
)

executor.scheduleWithFixedDelay(
    fixedDelayTask,
    0L,
    5L,
    TimeUnit.SECONDS,
)
```

## Scenario 1: 2 秒で完了し、遅延がない

条件:
- Task duration: 2 秒。
- Process pause: なし。

### A: `scheduleAtFixedRate`

```text
時刻:  0--2---5--7---10-12--15-17
予定:  0------5------10-----15
実行:  [run1] [run2] [run3] [run4]
```

開始時刻:
- 0、5、10、15 秒。

### B: `Timer#schedule`

```text
時刻:  0--2---5--7---10-12--15-17
実行:  [run1] [run2] [run3] [run4]
基準:  start  start  start  start
```

開始時刻:
- 0、5、10、15 秒。
- 遅れがないため A と同じに見えるが、各次回時刻は前回の actual start から計算される。

### C: `scheduleWithFixedDelay`

```text
時刻:  0--2-----7--9-----14-16----21
実行:  [run1]   [run2]   [run3]   [run4]
待機:       5秒      5秒      5秒
```

開始時刻:
- 0、7、14、21 秒。
- 2 秒の処理が完了してから 5 秒待つため、開始間隔は 7 秒になる。

### 比較結果

| API | Run 1 | Run 2 | Run 3 | Run 4 |
| --- | ---: | ---: | ---: | ---: |
| A | 0 | 5 | 10 | 15 |
| B | 0 | 5 | 10 | 15 |
| C | 0 | 7 | 14 | 21 |

## Scenario 2: 3〜13 秒の間 process が実行できない

条件:
- Task duration: 十分短い。
- Process unavailable: 3 秒から 13 秒。
- 5 秒、10 秒の planned execution を missed する。

### A: `scheduleAtFixedRate`

targetSdkVersion 35 以下 / change disabled:

```text
fixed-rate grid: 0----5----10----15----20
process:             [ unavailable ]
actual:          0              13→catch-up→15→20
```

- 復帰後、missed executions は元の fixed-rate grid へ追いつくため連続実行され得る。
- 長時間 cached だった場合、連続実行数が大きくなることが Lint `DiscouragedApi` の警告理由である。

Android 16 / targetSdkVersion 36 以上:

```text
fixed-rate grid: 0----5----10----15----20
process:             [ unavailable ]
actual:          0              13 [missed catch-upは最大1回] 15→20
```

- Android 16 Behavior Change により、復帰時に即時実行される missed execution は最大 1 回になる。
- 業務上必要な論理 period 数を callback 回数から求めてはならない。

### B: `Timer#schedule`

```text
old start:       0
process:             [ unavailable ]
actual start:    0              13----18----23
```

- 13 秒の actual start を新しい基準とし、次回は 18 秒。
- 5 秒、10 秒の過去 grid を個別には catch-up しない。

### C: `scheduleWithFixedDelay`

task が 13〜15 秒に実行された場合:

```text
process:             [ unavailable ]
task:            0              [13--15]-----20
                                      5秒 delay
```

- 復帰後の task が 15 秒に完了したなら、次回は 20 秒。
- 復帰時刻ではなく完了時刻が次回計算の基準になる。

## Scenario 3: 1 回の処理に 8 秒かかる

条件:
- Period / delay: 5 秒。
- Task duration: 8 秒。
- Process pause: なし。

### A: `scheduleAtFixedRate`

```text
0--------8--------16--------24
[ run1  ][ run2  ][ run3  ]
予定 0,5,10,15... へ追いつけないため完了直後に次が始まる
```

### B: `Timer#schedule`

```text
0--------8--------16--------24
[ run1  ][ run2  ][ run3  ]
次回予定は各 actual start + 5秒だが、完了時には予定を過ぎている
```

- B は missed fixed-rate grid を全件 catch-up しないが、task duration が period より長い場合は完了直後に次回が始まり得る。

### C: `scheduleWithFixedDelay`

```text
0--------8-----13--------21-----26
[ run1  ] 5秒 [ run2  ]  5秒  [ run3
```

- 完了後に必ず 5 秒待つ。
- network polling、camera status refresh など、連続負荷を避けたい処理に合わせやすい。

## Scenario 4: 例外と cancel

| API | 未処理例外 | Cancel / shutdown |
| --- | --- | --- |
| `Timer` A / B | `TimerTask#run()` の未処理例外で Timer thread が終了し、以後の task が実行されなくなる可能性がある | `Timer#cancel()`。Timer 単位で停止する |
| Executor C | periodic command が例外終了すると、その後の実行が抑制される | `ScheduledFuture#cancel()` と `ExecutorService#shutdown()` を分けて管理する |

共通対応:
- periodic callback の失敗方針を `runCatching` / `try-catch` で明示する。
- Activity / Fragment / Service / repository の owner 終了時に cancel する。
- process recreation で scheduler を重複登録しない。

## Android バージョン / targetSdkVersion 比較

| OS | targetSdkVersion | A: fixed-rate | B / C |
| --- | ---: | --- | --- |
| Android 16 | 35 | 複数 missed execution の旧 catch-up が default | 本 Behavior Change の直接対象外 |
| Android 16 | 36 | 復帰時の missed execution immediate catch-up は最大 1 回 | 本 Behavior Change の直接対象外 |
| Android 15 以下 | 35 以下 | 長時間停止後の複数 catch-up リスクを考慮 | 各 API 固有 semantics |

Android 15 / targetSdkVersion 36 は、調査 report に記載した tag / module 条件により実機確認対象とする。

## Expected / Observed

| Scenario | Expected | Observed | Result | Evidence |
| --- | --- | --- | --- | --- |
| 2 秒 task | A / B は 5 秒 start cadence、C は完了 + 5 秒 | 未実施 | 未実施 | API reference |
| Process unavailable | A は target 36 で catch-up 抑制、B / C は過去 grid を全件 catch-up しない | 未実施 | 未実施 | Behavior Change / AOSP |
| 8 秒 task | A / B は完了直後に開始され得る。C は完了後 5 秒待機 | 未実施 | 未実施 | API reference |
| Cancel / exception | API ごとの停止 semantics に従う | 未実施 | 未実施 | API reference |

## 実装選択マップ（Implementation Decision Input）

| 要件 | 実装候補 | 理由 | 追加確認 |
| --- | --- | --- | --- |
| 初回時刻を基準とした absolute-time cadence | `scheduleAtFixedRate` | 元の fixed-rate grid を維持する | Android 15 以下の catch-up、target 36 の最大 1 回化 |
| Timer を維持し、遅れた actual start から再開 | `Timer#schedule` | 最小差分で過去 grid の全件 catch-up を避ける | task が period を超えた場合の連続実行 |
| 前回完了後に必ず 5 秒休止 | `scheduleWithFixedDelay` | task duration を含めず delay を保証する | lifecycle、exception、executor shutdown |
| missed logical periods をすべて処理 | callback とは別の checkpoint reconciliation | scheduler の callback 回数に依存しない | 永続化、batch 上限、idempotency |
| fixed-rate を維持し、連続 callback の高コスト処理だけ抑制 | idempotent reconciliation + elapsed-time coalescing | 業務結果と負荷を守る | Lint 警告と callback 自体は残る |
| process death 後も必要な deferrable work | 本件とは分離して WorkManager / JobScheduler を別途設計 | process death は in-memory queue の catch-up ではない | 実行制約、最小間隔、retry |

この表は最終採用 API や優先度を決定しない。最終判断は Human Decision とする。

## テスト仕様（Verification Specification）

### 2 秒 task

- Given: initial delay 0、period / delay 5 秒、task duration 2 秒。
- When: 4 回分を実行する。
- Then: A / B の actual start は概ね 0、5、10、15 秒、C は 0、7、14、21 秒になる。

### Process unavailable

- Given: 3〜13 秒の間 process を実行不可にする。
- When: targetSdkVersion 35 / 36 と Change ID enabled / disabled を比較する。
- Then: A の復帰時 callback 数が新旧で異なり、B / C は過去 fixed-rate grid を全件 catch-up しない。
- And: callback 数が違っても最終 camera state が一致する。

### 8 秒 task

- Given: period / delay 5 秒、task duration 8 秒。
- When: 3 回分を観測する。
- Then: A / B は完了直後に次回が開始され得る。
- And: C は各完了後に 5 秒以上の gap がある。

## Fact / Evidence / Confidence

| Fact | Evidence | Confidence |
| --- | --- | --- |
| targetSdkVersion 36 では `scheduleAtFixedRate` の missed immediate execution が最大 1 回になる | Android 16 Behavior Change、AOSP libcore | High |
| `Timer#schedule` は actual execution time を基準とする fixed-delay execution | Android `Timer` API reference / AOSP `Timer.java` | High |
| `scheduleWithFixedDelay` は前回終了から delay 後に次回を開始する | `ScheduledExecutorService` API reference | High |
| 実機上の秒単位ログが conceptual timeline と一致する | 未検証 | Low |

## References

### Entry Point

- https://developer.android.com/about/versions/16/behavior-changes-16#schedule-at-fixed-rate

### Official Documentation

- https://developer.android.com/reference/java/util/Timer
- https://developer.android.com/reference/java/util/concurrent/ScheduledExecutorService

### Source Code

- https://android.googlesource.com/platform/libcore/+/refs/tags/android-16.0.0_r4/ojluni/src/main/java/java/util/Timer.java
- https://android.googlesource.com/platform/libcore/+/refs/tags/android-16.0.0_r4/ojluni/src/main/java/java/util/concurrent/ScheduledThreadPoolExecutor.java

### Validation

- 実機 / sample project 検証は未実施。
