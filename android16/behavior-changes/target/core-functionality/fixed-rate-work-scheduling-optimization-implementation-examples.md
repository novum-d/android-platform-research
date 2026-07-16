# Fixed rate work scheduling optimization - 実装例（Implementation Examples）

## 位置づけ（Scope）

このファイルは、Fixed rate work scheduling optimization の調査レポートに対する実装例である。
根拠、適用条件、classification、confidence、Human Decision は primary report / one-page summary を正とする。

Primary report:
- [fixed-rate-work-scheduling-optimization.md](fixed-rate-work-scheduling-optimization.md)

One-page summary:
- [fixed-rate-work-scheduling-optimization-summary.md](../../../summaries/target/core-functionality/fixed-rate-work-scheduling-optimization-summary.md)

Runtime behavior comparison:
- [fixed-rate-work-scheduling-optimization-runtime-behavior-comparison.md](fixed-rate-work-scheduling-optimization-runtime-behavior-comparison.md)

## 対象（Target）

Android 16 Behavior Change:
- Document: https://developer.android.com/about/versions/16/behavior-changes-16#schedule-at-fixed-rate
- Section: Fixed rate work scheduling optimization

適用条件の要点:
- OS アップデート / 全アプリ: No。targetSdkVersion 35 以下のアプリに OS アップデートだけで default 適用される根拠は確認していない。
- targetSdkVersion 36 以上: Yes。executor 側 Change ID 288912692 と Timer 側 Change ID 351566728 はどちらも `@EnabledAfter(VANILLA_ICE_CREAM)`。
- その他の必須条件: executor または Timer の `scheduleAtFixedRate` を使い、freeze / suspend 等で複数 period を missed した後に復帰すること。

対象 API:
- `ScheduledExecutorService#scheduleAtFixedRate`
- `ScheduledThreadPoolExecutor#scheduleAtFixedRate`
- `Timer#scheduleAtFixedRate(TimerTask, long, long)`
- `Timer#scheduleAtFixedRate(TimerTask, Date, long)`

## 使い方（How to Use）

- この Behavior Change は API の単純置換を要求するものではない。まず「missed callback が複数回呼ばれること」を業務ロジックが必要としているかを判定する。
- 最新状態を取得できればよい polling は、復帰後に 1 回だけ refresh して正しい状態へ収束する設計にする。
- missed period ごとの処理が必要な場合は、callback 回数ではなく、最後に成功した時刻と現在時刻から論理 period 数を計算する。
- 実装例はそのまま貼り付ける完成コードではない。永続化、排他制御、retry 上限、network 制約、process lifecycle に合わせて調整する。

## 対応方針（Implementation Strategy）

推奨方針:
- fixed-rate callback の実行回数を業務データとして扱わない。
- polling / reconnect / sync は idempotent な「現在状態との reconciliation」として実装する。
- 全 period の処理が必要な場合は checkpoint を保存し、経過 period 数を明示的に計算する。
- 1 回の復帰処理で無制限に backlog を消化せず、batch 上限と次回継続位置を持つ。

条件付きの移行先:
- 前回処理の完了から一定 delay 後でよい場合は `scheduleWithFixedDelay`。
- `Timer` の single-thread、例外処理、cancel 管理が問題の場合は `ScheduledExecutorService`。

重要:
- `scheduleAtFixedRate` は `@Deprecated` API ではないが、Android Lint は cached process 復帰時の大量 catch-up を理由に `DiscouragedApi` として警告する。この警告は本 Behavior Change と同じ問題領域を扱う。
- `scheduleAtFixedRate` を残したまま `run()` の中身だけを idempotent / reconciliation 方式へ変える対応は、Android 16 で callback 回数が変わっても業務結果を壊さないための互換性対応である。API 利用自体は残るため Lint 警告は消えず、古い OS で callback が連続投入される可能性も残る。
- `Timer#scheduleAtFixedRate` から `ScheduledExecutorService#scheduleAtFixedRate` へ置き換えるだけでは、この Behavior Change を回避できない。Android 16 では両方が missed catch-up 最大 1 回の対象である。
- `scheduleWithFixedDelay` への変更は cadence semantics を変える。絶対時刻基準の fixed-rate が本当に必要かを確認してから選択する。
- WorkManager / JobScheduler は本 Behavior Change の移行先ではない。process death 後も再実行するという別要件がある場合のみ、実行保証、制約、間隔、retry を再定義する独立した設計変更として扱う。

## 対応レベルと解消できる問題

| 対応 | Android 16 の callback 回数変更への耐性 | 復帰時の高コスト処理集中 | Lint 警告 |
| --- | --- | --- | --- |
| `run()` を idempotent reconciliation に変更 | 改善する | 同じ処理を繰り返しても結果は壊れにくいが、呼び出し負荷は残る | 消えない |
| `run()` に実時刻 throttle / coalescing を追加 | 改善する | 高コストな network / DB 処理を間引けるが、callback 自体は呼ばれる | 消えない |
| `Timer#schedule` / `scheduleWithFixedDelay` へ移行 | 改善する設計へ変更可能 | fixed-rate backlog の根本原因を避ける | 対象 call site の警告は解消される |
| `scheduleAtFixedRate` を維持して suppress | 実装次第 | fixed-rate risk は残る | 表示だけ消える。問題解消ではない |

## 移行対象の見つけ方（Finding Existing Code）

探すコード:
- executor / Timer の fixed-rate scheduling。
- callback ごとに retry count、sequence、progress、課金量、upload 件数などを増やす処理。
- 「freeze 中に呼ばれなかった回数は復帰時の連続 callback で補える」という前提。
- wrapper、SDK、utility class の内部に隠れた scheduling。

```bash
rg -n "scheduleAtFixedRate|ScheduledExecutorService|ScheduledThreadPoolExecutor|new Timer|Timer\(" app src
```

分類:

| 既存実装（Existing pattern） | 対応先（Migration target） | 優先度 | Notes |
| --- | --- | --- | --- |
| callback ごとに最新 camera state を取得 | 1 回の idempotent reconciliation | Recommended | missed 回数を補う必要はない |
| callback ごとに retry count を加算 | deadline / current connection state ベース | Must | callback 回数を retry semantics にしない |
| callback ごとに 1 period 分のデータを確定 | checkpoint + elapsed period calculation | Must | logical period を明示的に計算する |
| `Timer#scheduleAtFixedRate`、前回の実際の開始時刻を基準にしてよい | `Timer#schedule(..., period)` | Recommended | 最小差分。fixed-delay になり backlog を作らない |
| Timer の single-thread / cancel / exception handling も見直す | `ScheduledExecutorService#scheduleWithFixedDelay` | Recommended | fixed-delay 化と lifecycle 制御を同時に行う |
| absolute-time fixed-rate が必須 | fixed-rate を維持し business logic を時刻ベースへ変更 | Conditional | Lint 警告理由と Android 15 以下を含むリスク受容が必要 |
| process death 後も必要な deferrable work | 本件から分離し、WorkManager / JobScheduler を別途設計 | Separate concern | `scheduleAtFixedRate` の移行ではない |

## 移行マップ（Migration Map）

| Before | After | 目的 |
| --- | --- | --- |
| missed callback 1 回を retry 1 回として数える | 現在の接続状態と deadline から retry 要否を決める | callback 回数依存をなくす |
| missed callback 1 回を 1 period 分の処理として数える | checkpoint と現在時刻から未処理 period 数を計算する | 論理処理の欠落を防ぐ |
| Timer を executor に置き換えるだけ | scheduling API と business semantics を分けて見直す | 同じ Behavior Change を別 API へ移すだけにしない |
| Timer の fixed-rate polling | Timer の fixed-delay `schedule`、または executor の `scheduleWithFixedDelay` | cached process 復帰時の backlog を作らない |
| 復帰直後に無制限 catch-up | bounded batch + checkpoint | CPU / network / DB の集中負荷を防ぐ |

## 例 1: `scheduleAtFixedRate` を維持して業務ロジックを安全にする

目的:
- absolute-time fixed-rate が必要な場合に、callback 回数を業務データとして扱わず、現在の camera state へ収束させる。
- この例は Behavior Change 互換性を改善するが、Lint 警告を解消する API 移行ではない。

既存実装で探す箇所:
- polling callback ごとに sequence や retry count を増やしてから状態取得する処理。

移行前:

```kotlin
executor.scheduleAtFixedRate({
    retryCount += 1
    cameraClient.pollStatus(retryCount)
}, 0, 5, TimeUnit.SECONDS)
```

対応後 A: 最小限の reconciliation 化

```kotlin
executor.scheduleAtFixedRate({
    runCatching {
        val remote = cameraClient.fetchCurrentStatus()
        cameraRepository.reconcile(remote)
    }.onFailure { logger.warn(it) }
}, 0, 5, TimeUnit.SECONDS)
```

この状態で解消できること:
- Android 16 / targetSdkVersion 36 で missed callback が最大 1 回になっても、現在の camera state を取得できる。
- callback 回数が減っても `retryCount` や sequence に欠番が生じる設計ではなくなる。
- 同じ remote state を複数回取得しても `reconcile()` が idempotent なら、通知や DB 更新を重複させずに済む。

この状態で解消できないこと:
- `scheduleAtFixedRate` の Lint `DiscouragedApi` 警告。
- Android 15 以下などで復帰時に callback が連続して呼ばれること。
- 各 callback が network request を開始する場合の CPU / network 集中。

対応後 B: API を維持する必要がある場合に高コスト処理も coalesce する

```kotlin
class CameraStatusReconciler(
    private val cameraClient: CameraClient,
    private val cameraRepository: CameraRepository,
    private val minimumActualIntervalMillis: Long = 5_000L,
    private val elapsedRealtime: () -> Long = SystemClock::elapsedRealtime,
) {
    private val nextAllowedAt = AtomicLong(0L)

    fun runIfDue() {
        val now = elapsedRealtime()

        while (true) {
            val currentNextAllowedAt = nextAllowedAt.get()
            if (now < currentNextAllowedAt) {
                return // 復帰直後の連続 callback では高コスト処理を繰り返さない。
            }

            if (nextAllowedAt.compareAndSet(
                    currentNextAllowedAt,
                    now + minimumActualIntervalMillis,
                )
            ) {
                break
            }
        }

        val remote = cameraClient.fetchCurrentStatus()
        cameraRepository.reconcile(remote)
    }
}

val reconciler = CameraStatusReconciler(
    cameraClient = cameraClient,
    cameraRepository = cameraRepository,
)

executor.scheduleAtFixedRate(
    {
        runCatching(reconciler::runIfDue)
            .onFailure { logger.warn(it) }
    },
    0L,
    5L,
    TimeUnit.SECONDS,
)
```

13 秒に process が復帰し、fixed-rate callback が短時間に複数回来た場合のイメージ:

```text
callback 1 at 13.0s -> nextAllowedAt を 18.0s に更新 -> cameraへ問い合わせ
callback 2 at 13.1s -> 18.0s より前なので return
callback 3 at 13.2s -> 18.0s より前なので return
callback   at 18.0s -> cameraへ問い合わせ可能
```

注意:
- callback 自体と Lint 警告は残る。間引かれるのは `runIfDue()` 内の高コスト処理である。
- 同じ periodic task は通常 overlap しないが、別 scheduler / lifecycle source からも呼ばれる可能性を考え、例では `AtomicLong` で gate を共有している。
- elapsed time は process 内の throttle に使う。reboot / process death を跨ぐ checkpoint には wall-clock policy を別途定義する。

対応後 C: executor の fixed-rate が不要なら `scheduleWithFixedDelay` へ移行する

```kotlin
executor.scheduleWithFixedDelay(
    {
        runCatching {
            val remote = cameraClient.fetchCurrentStatus()
            cameraRepository.reconcile(remote)
        }.onFailure { logger.warn(it) }
    },
    0L,
    5L,
    TimeUnit.SECONDS,
)
```

- 前回の処理完了から 5 秒後に次回を開始する。
- fixed-rate backlog を作らないため、対象 `scheduleAtFixedRate` call site の Lint 警告もなくなる。

`Timer#scheduleAtFixedRate` に警告が出ている場合は、要件が合えば `Timer#schedule` へ置き換える。

```kotlin
val timer = Timer("camera-status", true)

timer.schedule(
    object : TimerTask() {
        override fun run() {
            runCatching {
                val remote = cameraClient.fetchCurrentStatus()
                cameraRepository.reconcile(remote)
            }.onFailure { logger.warn(it) }
        }
    },
    0L,
    5_000L,
)
```

- `Timer#schedule` は前回の実際の開始時刻から 5 秒後を次回基準にする。
- `scheduleWithFixedDelay` の「前回完了から 5 秒後」とは異なる。
- `Timer#scheduleAtFixedRate` の call site がなくなるため、質問にある `prefer using schedule` の Lint 警告は解消される。

移行手順:
1. fixed-rate が本当に必要かを確認する。不要なら executor は `scheduleWithFixedDelay`、Timer は `schedule` を選ぶ。
2. 維持が必要なら callback 回数を status request / retry count の意味から外す。
3. camera が返す現在状態を source of truth として local state を更新する。
4. 同じ状態を複数回受け取っても副作用が重複しないようにする。
5. 古い OS の連続 callback で network / DB 負荷が問題になるなら対応 B の実時刻 gate を追加する。
6. Lint suppression を使う場合は、fixed-rate 要件と Android 15 以下を含む検証結果を理由として残す。

確認観点:
- freeze 前後で callback 回数が変わっても最終 camera state が一致する。
- 同じ response を複数回処理しても transfer や通知が重複しない。
- 対応 B では連続 callback が来ても、5 秒以内の camera request が 1 回だけになる。
- 対応 A / B は Lint 警告が残り、対応 C では対象 call site の警告が消える。

## 例 2: missed period を checkpoint から計算する

目的:
- period ごとの処理が必要な場合に、executor が callback を何回 catch-up したかへ依存しない。

移行前:

```kotlin
executor.scheduleAtFixedRate({
    aggregateOnePeriod()
}, 0, 1, TimeUnit.MINUTES)
```

移行後:

```kotlin
class PeriodReconciler(
    private val clock: Clock,
    private val checkpoint: Checkpoint,
    private val period: Duration,
    private val maxBatch: Long = 20,
    private val processPeriod: (Instant) -> Unit,
) {
    init {
        require(period.toMillis() > 0) { "period must be at least 1 ms" }
        require(maxBatch > 0) { "maxBatch must be positive" }
    }

    fun runOnce() {
        val last = checkpoint.read()
        val now = clock.instant()
        val elapsed = Duration.between(last, now)
        val due = (elapsed.toMillis() / period.toMillis()).coerceIn(0L, maxBatch)

        var cursor = last
        repeat(due.toInt()) {
            cursor = cursor.plus(period)
            processPeriod(cursor)
            checkpoint.write(cursor)
        }
    }
}

executor.scheduleAtFixedRate(
    reconciler::runOnce,
    0,
    1,
    TimeUnit.MINUTES,
)
```

移行手順:
1. 最後に成功した logical period を checkpoint として保存する。
2. `now - checkpoint` から due period 数を計算する。
3. 1 period 成功するごとに checkpoint を進める。
4. 1 回の batch 上限を設け、残りは次回へ送る。

確認観点:
- 5 period missed 後に callback が 1 回だけでも、必要な論理処理数を計算できる。
- 途中失敗時に成功済み checkpoint から再開できる。
- process restart を跨ぐ場合は checkpoint と wall-clock policy が永続化されている。

注意点:
- `Instant` / wall clock は時刻補正の影響を受ける。経過時間だけが必要で process 内に閉じる処理は `SystemClock.elapsedRealtime()` も検討する。
- `elapsedRealtime()` は reboot を跨いで永続化する checkpoint には使わない。

## 例 3: `Timer#scheduleAtFixedRate` を `Timer#schedule` へ最小差分で移行する

目的:
- Timer を使い続けながら fixed-rate を fixed-delay に変え、cached process 復帰時の backlog を作らない。

移行前:

```kotlin
val timer = Timer("camera-poll", true)

timer.scheduleAtFixedRate(object : TimerTask() {
    override fun run() {
        cameraRepository.poll()
    }
}, 0L, 5_000L)
```

移行後:

```kotlin
val timer = Timer("camera-poll", true)

timer.schedule(object : TimerTask() {
    override fun run() {
        runCatching {
            cameraRepository.reconcileCurrentState()
        }.onFailure { logger.warn(it) }
    }
}, 0L, 5_000L)
```

Java:

```java
Timer timer = new Timer("camera-poll", true);
timer.schedule(new TimerTask() {
    @Override
    public void run() {
        try {
            cameraRepository.reconcileCurrentState();
        } catch (RuntimeException error) {
            logger.warn(error);
        }
    }
}, 0L, 5_000L);
```

移行手順:
1. 要件が「初回予定時刻を基準に 5 秒ごと」ではなく「前回の実際の開始時刻を基準に 5 秒ごと」でよいことを確認する。
2. `scheduleAtFixedRate(task, delay, period)` を `schedule(task, delay, period)` へ置き換える。
3. callback 回数依存を削除し、現在状態を取得する idempotent な処理へ変更する。
4. owner の終了時に `timer.cancel()` を呼ぶ。
5. task 内の未処理例外で Timer thread が終了しないように failure handling を明示する。

確認観点:
- task が 2 秒かかった場合、次回開始は前回開始から約 5 秒後、つまり完了から約 3 秒後になることを確認する。
- cached / uncached 復帰後に missed period 数の連続実行が発生しないことを確認する。
- task failure 後も、設計した retry / reschedule 経路が維持される。
- Activity / service 終了後に Timer thread が残らない。

注意点:
- Timer の `schedule` は fixed-delay と呼ばれるが、executor の `scheduleWithFixedDelay` と違い、前回 task の完了時刻ではなく実際の開始時刻を基準にする。task が period より長い場合、完了直後に次回が開始され得る。完了後に必ず delay を空けたい場合は `scheduleWithFixedDelay` を使う。
- 初回予定時刻を基準とする絶対時刻同期が必要な処理には使わない。
- `delay` 版と `Date firstTime` 版の双方を棚卸しする。

## 例 4: Timer を `ScheduledExecutorService#scheduleWithFixedDelay` へ移行する Java 例

目的:
- fixed-delay 化に加え、Timer の single-thread、cancel、例外処理を executor の lifecycle 管理へ移す。

移行前:

```java
Timer timer = new Timer("camera-poll", true);
timer.scheduleAtFixedRate(new TimerTask() {
    @Override
    public void run() {
        cameraRepository.poll();
    }
}, 0L, 5_000L);
```

移行後:

```java
ScheduledExecutorService executor =
        Executors.newSingleThreadScheduledExecutor();

ScheduledFuture<?> polling = executor.scheduleWithFixedDelay(
        () -> {
            try {
                cameraRepository.reconcileCurrentState();
            } catch (RuntimeException error) {
                logger.warn(error);
            }
        },
        0L,
        5L,
        TimeUnit.SECONDS);

// owner の終了時
polling.cancel(false);
executor.shutdown();
```

移行手順:
1. `TimerTask` の処理を `Runnable` へ移す。
2. `Timer#cancel()` の lifecycle を `ScheduledFuture#cancel()` と `ExecutorService#shutdown()` に分ける。
3. periodic task 内の未処理例外を捕捉し、次回実行を止めるか継続するかを明示する。
4. `scheduleAtFixedRate` ではなく `scheduleWithFixedDelay` を選び、callback 回数依存の logic は reconciliation / checkpoint 方式へ変更する。

確認観点:
- cancel 後に polling が継続しない。
- 例外時の次回実行方針が要件どおりである。
- cached / uncached 復帰後に backlog が連続実行されない。

## 例 5: fixed-delay が要件に合う場合だけ切り替える

目的:
- 「前回処理の完了から一定時間後に次回を実行」でよい処理を fixed-delay として表現する。

```kotlin
executor.scheduleWithFixedDelay({
    cameraRepository.refreshIfConnected()
}, 0, 5, TimeUnit.SECONDS)
```

移行手順:
1. fixed-rate が必要だった理由を確認する。
2. 実行開始時刻ではなく、前回処理の完了からの delay でよいことを確認する。
3. 復帰時に missed periods を補填しない semantics をテストする。

確認観点:
- 処理時間が 2 秒なら次回開始は完了から 5 秒後でよいか。
- 絶対時刻や他 task との同期が不要か。
- background / process death 後の実行保証を別 API で扱う必要がないか。

注意点:
- fixed-rate から fixed-delay へ変えると実行開始間隔が変わる。Android 16 対応という理由だけで機械的に置き換えない。

## 例 6: fixed-rate を維持できる例外条件

次をすべて満たす場合に限り、`scheduleAtFixedRate` の維持を検討する。

1. absolute-time の周期、複数 task 間の同期、または固定回数を一定時間内に完了する要件が明文化されている。
2. Android 15 以下で長時間 cached になった後の大量 catch-up を許容または独自に抑制できる。
3. Android 16 / targetSdkVersion 36 で catch-up が最大 1 回になっても業務結果が壊れない。
4. callback は idempotent で、復帰時の CPU、network、DB 負荷に上限がある。
5. Lint suppression を使う場合、理由、対象範囲、対応 OS のテストがコードレビュー可能な形で残っている。

Lint suppression は移行ではない。まず fixed-delay へ変更できない理由を確認し、必要な呼び出しだけに局所化する。

## 別要件: process death 後も再実行する background work

この section は本 Behavior Change の対応手順ではなく、棚卸し中に「process death 後も処理を再実行したい」という別要件が見つかった場合の設計分岐である。
cached / frozen process は process と in-memory scheduler queue が残るが、process death では Timer / executor queue は失われる。両者を同じ復帰問題として扱わない。

| 要件 | 移行先 | 理由 |
| --- | --- | --- |
| 画面表示中 / 接続中だけ数秒間隔で polling | lifecycle owner が cancel する coroutine loop、または `scheduleWithFixedDelay` | Activity / service の終了に合わせて停止できる |
| process 終了後も再実行したい deferrable work | WorkManager | 永続化、制約、retry を OS 管理へ移せる |
| JobScheduler を直接管理する既存基盤がある | JobScheduler | process lifecycle から切り離せる |
| user-visible な正確な時刻通知 | AlarmManager を要件と権限制約込みで検討 | exact alarm は periodic polling の代替ではない |

WorkManager の periodic work は短周期 polling や `scheduleAtFixedRate` の等価な置換先ではない。接続中だけ必要な短周期処理は lifecycle-bound とし、process death を跨ぐ同期や cleanup という別要件がある場合だけ WorkManager 等へ責務を分ける。

## テスト観点（Verification）

- Android 16 / targetSdkVersion 35: 旧 catch-up behavior と business logic の最終結果を記録する。
- Android 16 / targetSdkVersion 36: executor / Timer とも復帰時 immediate catch-up が最大 1 回でも正しく収束することを確認する。
- executor: Change ID 288912692 enabled / disabled を比較する。
- Timer: Change ID 351566728 enabled / disabled を対象 build で比較する。
- latest-state polling: callback 回数ではなく最終 remote / local state が一致することを確認する。
- logical-period processing: 0、1、複数、batch 上限超過の missed periods を確認する。
- error handling: network error、DB error、task exception、process restart 後の再開位置を確認する。
- lifecycle: Activity / service / repository 終了後に Timer / executor が残らないことを確認する。

Compat override 例:

```bash
adb shell am compat enable 288912692 <PACKAGE_NAME>
adb shell am compat disable 288912692 <PACKAGE_NAME>

adb shell am compat enable 351566728 <PACKAGE_NAME>
adb shell am compat disable 351566728 <PACKAGE_NAME>
```

注意点:
- Android Developers の公開 compat page と Behavior Change 文書が明示する test flag は STPE 側 288912692 である。
- Timer 側 351566728 は AOSP `Timer.java` / libcore test から確認した Change ID であり、override 可否や aconfig force-enable 状態は対象 device build で確認する。

## テストコード例（Test Code Examples）

目的:
- freeze 自体を unit test で再現せず、「callback が 1 回しか来なくても経過 period を正しく計算できる」business logic を deterministic に検証する。

### Java / JUnit: due period を上限付きで計算する

```java
final class MissedPeriodCalculator {
    static long duePeriods(
            Instant lastSuccessfulAt,
            Instant now,
            Duration period,
            long maxBatch) {
        if (now.isBefore(lastSuccessfulAt)) {
            return 0L;
        }
        long due = Duration.between(lastSuccessfulAt, now).toMillis()
                / period.toMillis();
        return Math.min(due, maxBatch);
    }
}

@Test
public void calculatesMissedPeriodsWithoutDependingOnCallbackCount() {
    Instant last = Instant.parse("2026-07-16T00:00:00Z");
    Instant now = Instant.parse("2026-07-16T00:05:30Z");

    long due = MissedPeriodCalculator.duePeriods(
            last,
            now,
            Duration.ofMinutes(1),
            20L);

    assertEquals(5L, due);
}

@Test
public void capsCatchUpBatch() {
    Instant last = Instant.parse("2026-07-16T00:00:00Z");
    Instant now = Instant.parse("2026-07-16T01:00:00Z");

    long due = MissedPeriodCalculator.duePeriods(
            last,
            now,
            Duration.ofMinutes(1),
            20L);

    assertEquals(20L, due);
}
```

確認できること:
- platform callback が 1 回でも、時刻差から 5 logical periods を求められる。
- 長時間 freeze 後も 1 回の batch が上限を超えない。

### Instrumentation / manual test で確認すること

- targetSdkVersion 35 / 36 と Change ID enabled / disabled で process を freeze / unfreeze し、callback timestamps を記録する。
- executor と Timer の両方で、復帰直後に連続実行される回数を比較する。
- callback 回数が異なっても、camera connection、transfer state、sync checkpoint の最終状態が同じであることを確認する。
- `Timer#scheduleAtFixedRate(TimerTask, Date, long)` の過去 first time、task 実行時間が period を超えるケースも確認する。

## References

- https://developer.android.com/about/versions/16/behavior-changes-16#schedule-at-fixed-rate
- https://developer.android.com/about/versions/16/reference/compat-framework-changes#stpe_skip_multiple_missed_periodic_tasks
- https://developer.android.com/reference/java/util/concurrent/ScheduledExecutorService#scheduleAtFixedRate(java.lang.Runnable,long,long,java.util.concurrent.TimeUnit)
- https://developer.android.com/reference/java/util/Timer#scheduleAtFixedRate(java.util.TimerTask,long,long)
- https://developer.android.com/reference/java/util/Timer#scheduleAtFixedRate(java.util.TimerTask,java.util.Date,long)
- https://android.googlesource.com/platform/libcore/+/refs/tags/android-16.0.0_r4/ojluni/src/main/java/java/util/concurrent/ScheduledThreadPoolExecutor.java
- https://android.googlesource.com/platform/libcore/+/refs/tags/android-16.0.0_r4/ojluni/src/main/java/java/util/Timer.java
