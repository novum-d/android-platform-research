# 固定間隔処理のスケジューリング最適化（Fixed rate work scheduling optimization）調査レポート

## 基本情報（Metadata）

### 調査対象 Android バージョン（Android Versions）

比較元:
- android-15.0.0_r36

比較先:
- android-16.0.0_r4

注記:
- `frameworks-base` checkout に未コミットの変更はない。指定した `android-15.0.0_r36` / `android-16.0.0_r4` タグはどちらも存在する。
- ローカルに `libcore` checkout がなかったため、AOSP 公式 Gitiles のタグ指定 URL で `platform/libcore` を確認した。

### Behavior Change 文書（Behavior Change Source）

文書:
- https://developer.android.com/about/versions/16/behavior-changes-16#schedule-at-fixed-rate

セクション:
- Fixed rate work scheduling optimization

### 分類スナップショット（Classification Snapshot）

主分類（Primary classification）:
- `TARGET_SDK_36_CONDITIONAL`

早見表（At-a-glance impact）:

| 確認項目（Question） | 回答（Answer） | 根拠（Evidence） |
| --- | --- | --- |
| Android 16 に OS アップデートしただけで適用されるか | いいえ | 公式文書では、Android 16 / API level 36 以上を対象とするアプリの Behavior Change として掲載されている。公開 compat ページでも、Change ID 288912692 は Android 16 以上を対象とする場合に有効になると説明されている |
| targetSdkVersion 36 以上が必要か | はい | AOSP libcore の STPE Change ID 288912692 と Timer Change ID 351566728 には、どちらも `@EnabledAfter(targetSdkVersion = VersionCodes.VANILLA_ICE_CREAM)` が付いている。つまり targetSdkVersion 36 以上で既定で有効になる |
| 追加の実行時条件があるか | はい | `ScheduledExecutorService` / `ScheduledThreadPoolExecutor` または `Timer` の `scheduleAtFixedRate` を使い、CPU の一時停止、Cached Apps Freezer、プロセスの凍結などで複数周期を実行できないまま復帰した場合に、実質的な影響が出る |
| Compat Change ID が関係するか | はい | STPE: `STPE_SKIP_MULTIPLE_MISSED_PERIODIC_TASKS` / 288912692。Timer: `SKIP_MULTIPLE_MISSED_PERIODIC_TASKS` / 351566728。公開 compat ページに掲載されているのは STPE 側である |

### 調査日（Investigation Date）

2026-07-01（2026-07-16 Timer 調査・実装例追記）

### 信頼度（Confidence）

- High

理由:
- 公式 Behavior Change 文、公開 compat framework changes、AOSP libcore の STPE / Timer 両方の Change ID、targetSdkVersion gate、`scheduleAtFixedRate` 再スケジュール実装が一致している。
- Android 15 r36 tag にも同じ libcore 実装は存在するため、指定 tag 間の純粋な実装 diff ではなく、compat default state と targetSdkVersion 36 policy として説明する必要がある。この点は report に明記した。

### 適用条件分類（Applicability Classification）

適用される条件（Applies when）:
- [ ] OS update / all apps on Android 16 regardless of targetSdkVersion
- [ ] targetSdkVersion >= 36 on Android 16+
- [x] targetSdkVersion >= 36, with additional runtime conditions
- [ ] Mainline / Google Play system update dependent
- [ ] API addition only, not a behavior change
- [ ] Unknown / needs more evidence

必要な実行時条件（Required runtime conditions）:
- Android version: 公式 Behavior Change としては Android 16 以上。Android 15 r36 tag にも同じ libcore gate が存在するため、Android 15 / targetSdkVersion 36 の実機挙動は環境条件つきで確認対象。
- targetSdkVersion: 36 以上。
- Device/form factor: 条件なし。
- Permission/API/component condition: `ScheduledThreadPoolExecutor#scheduleAtFixedRate`、`ScheduledExecutorService#scheduleAtFixedRate`、または `Timer#scheduleAtFixedRate` の fixed-rate periodic task。
- App state/process condition: process が CPU suspend、Cached Apps Freezer、frozen state 等により複数 period の実行機会を missed し、その後実行可能状態へ戻ること。

Compat framework:
- Change ID: 288912692
- Change name: `STPE_SKIP_MULTIPLE_MISSED_PERIODIC_TASKS`
- Default state: Android Developers の compat page では Android 16 / API level 36 以上を target するアプリで enabled。AOSP annotation は `@EnabledAfter(targetSdkVersion = VersionCodes.VANILLA_ICE_CREAM)`。
- Toggleable for testing: Yes。公式文書は app compatibility framework で `STPE_SKIP_MULTIPLE_MISSED_PERIODIC_TASKS` を enabled にしてテストできると説明している。
- Timer の AOSP Change ID: 351566728
- Timer の AOSP Change name: `SKIP_MULTIPLE_MISSED_PERIODIC_TASKS`
- Timer の AOSP default state: `@EnabledAfter(targetSdkVersion = VersionCodes.VANILLA_ICE_CREAM)`。公開 Android 16 compat page には個別項目として掲載されていない。

分類信頼度（Classification confidence）:
- High

分類根拠（Classification evidence）:
- Official documentation page: `behavior-changes-16` の `Core functionality` セクション。
- Original applicability statement: targeting Android 16 では missed `scheduleAtFixedRate` execution の即時実行が最大 1 回になる。
- AOSP targetSdk gate: `@EnabledAfter(targetSdkVersion = VersionCodes.VANILLA_ICE_CREAM)` on STPE Change ID 288912692 and Timer Change ID 351566728。
- Compat framework entry: 公開 compat page に `STPE_SKIP_MULTIPLE_MISSED_PERIODIC_TASKS` / 288912692、default enabled for apps targeting Android 16 / API level 36 or higher と掲載あり。

---

# エグゼクティブサマリー（Executive Summary）

Android 16 では、targetSdkVersion 36 以上のアプリで、`ScheduledThreadPoolExecutor` / `ScheduledExecutorService` と `Timer` の `scheduleAtFixedRate` が、未実行分を復帰直後にまとめて実行する挙動が抑制される。
従来は、プロセスが凍結や一時停止などから戻ったときに、複数回分の fixed-rate 処理が連続実行される可能性があった。新しい挙動では、復帰時に即時実行される未実行分は最大1回になる。
Android 16 へ OS アップデートしただけで targetSdkVersion 35 以下のアプリに適用される変更ではない。
影響があるのは、fixed-rate の未実行分がまとめて実行されることを業務ロジックとして期待している、ポーリング、同期、メトリクス送信、再試行、後処理などである。

`scheduleAtFixedRate` は API として `@Deprecated` にはなっていない。一方、Android Lint は `DiscouragedApi` として、cached process が通常状態へ戻った際の大量の連続実行を理由に、使用を強く非推奨としている。この Lint 警告と Android 16 Behavior Change は無関係ではなく、どちらも未実行分をまとめて処理する問題を扱っている。Android 16 / targetSdkVersion 36 の変更は、まとめて実行する回数を最大1回へ抑える緩和策である。しかし、古い OS、targetSdkVersion 35 以下、fixed-rate 固有の挙動、プロセスのライフサイクルとの不整合は残るため、Lint 警告を無視してよい根拠にはならない。

---

# 公式ドキュメント確認（Original Documentation）

## 原文（Statement）

検証対象 statement:

```text
Prior to targeting Android 16, when scheduleAtFixedRate missed a task execution due to being outside a valid process lifecycle, all missed executions immediately execute when the app returns to a valid lifecycle.
```

```text
When targeting Android 16, at most one missed execution of scheduleAtFixedRate is immediately executed when the app returns to a valid lifecycle.
```

```text
This behavior change is expected to improve app performance.
```

```text
You can also test by using the app compatibility framework and enabling the STPE_SKIP_MULTIPLE_MISSED_PERIODIC_TASKS compat flag.
```

## 解釈（Interpretation）

公式文書は、targetSdkVersion 36 化により `scheduleAtFixedRate` の catch-up 実行回数が変わることを説明している。
対象は fixed-rate periodic task であり、`scheduleWithFixedDelay` は同じ catch-up モデルではない。
「valid process lifecycle」は libcore の executor / Timer が直接 lifecycle state を問い合わせる意味ではなく、AOSP 実装コメントでは CPU suspend や Cached Apps Freezer により app process が scheduled periods を missed する状況として説明されている。

追加の公式 API reference:
- https://developer.android.com/reference/java/util/Timer#scheduleAtFixedRate(java.util.TimerTask,long,long)
- Android `Timer` API reference も API level 36 以降の fixed-rate behavior として、復帰時の catch-up が最大 1 回になることを説明している。

## API の非推奨状態と Lint 警告

確認結果:
- `Timer#scheduleAtFixedRate` と `ScheduledExecutorService#scheduleAtFixedRate` は public API から削除予定の `@Deprecated` API ではない。
- Android Studio / Lint の取り消し線は `DiscouragedApi` 警告であり、Java / Android API の formal deprecation とは異なる。
- `scheduleAtFixedRate` を残したまま `run()` の中身だけを idempotent / reconciliation 方式へ変更しても、Behavior Change に対する業務ロジックの耐性は改善するが、API 利用に対する Lint 警告は消えない。
- `Timer#scheduleAtFixedRate` の警告は `Timer#schedule(TimerTask, delay, period)`、executor の警告は `scheduleWithFixedDelay` を代替候補として示す。どちらも missed period の backlog を蓄積しないが、基準時刻は異なる。Timer の `schedule` は前回の実際の実行開始時刻、executor の `scheduleWithFixedDelay` は前回処理の完了時刻から次回を決める。
- 警告の原因である cached process 復帰時の連続 catch-up と、本 Behavior Change が抑制する missed execution は同じ問題領域である。

判断:
- Behavior Change 調査から `Timer#scheduleAtFixedRate` を削除しない。
- 新規実装では absolute-time fixed-rate が明確に必要な場合を除き、fixed-delay、lifecycle に紐づく one-shot rescheduling、または OS 管理の background work を優先する。
- 既存実装を維持する場合も、callback 回数を retry 回数や論理 period 数として扱わず、Android 15 以下と Android 16 / targetSdkVersion 36 の両方をテストする。

---

# 変更内容（What Changed）

- `ScheduledThreadPoolExecutor` に Change ID `STPE_SKIP_MULTIPLE_MISSED_PERIODIC_TASKS` / 288912692 があり、targetSdkVersion 36 以上で default enabled になる。
- `Timer` に Change ID `SKIP_MULTIPLE_MISSED_PERIODIC_TASKS` / 351566728 があり、同じく targetSdkVersion 36 以上で default enabled になる。
- fixed-rate task の `setNextRunTime()` は、従来どおり `time += period` した後、新 compat change が enabled の場合、次回 scheduled time が現在時刻より 1 period 以上過去なら「最後に missed した period」に補正する。
- `TimerThread#mainLoop()` も、fixed-rate task の次回時刻が複数 period 過去に残る場合、次回時刻を最新の missed period に補正する。
- この補正により、freeze / suspend から復帰した直後に複数回分の fixed-rate task を連続実行して過去の全 period に追いつく挙動が抑制される。
- `scheduleWithFixedDelay` は `period` が負値として扱われ、`setNextRunTime()` では `triggerTime(-p)` により「前回実行終了から delay 後」に再スケジュールされる。fixed-rate の missed catch-up 補正対象ではない。
- public API signature の差分は確認していない。挙動変更は既存 API の runtime scheduling behavior である。

## 適用条件（Applicability）

### OS アップデート時の挙動（OS Update Behavior）

- Android 16 にアップデートしただけで適用されるか: 原則 No。
- targetSdkVersion に依存しない根拠: なし。公式 compat page と AOSP annotation は targetSdkVersion gate を示している。
- Android 15 以前での挙動: targetSdkVersion 35 以下では compat change が default disabled のため、従来どおり複数 missed executions が連続実行され得る。

### targetSdkVersion 36 以上での挙動（targetSdkVersion 36 Behavior）

- targetSdkVersion 36 以上で適用されるか: Yes。
- Android 16 以外で targetSdkVersion 36 にした場合の挙動: Android 15 r36 の libcore tag にも同じ Change ID / `@EnabledAfter(VANILLA_ICE_CREAM)` / `setNextRunTime()` 補正が存在する。実機・module・package install 条件によっては Android 15 / targetSdkVersion 36 でも新挙動になる可能性があるため、テストマトリクスでは確認対象として扱う。
- opt-out / temporary override の有無: 公式文書は compat framework で `STPE_SKIP_MULTIPLE_MISSED_PERIODIC_TASKS` を enable してテストできると説明している。compat override により force-enable / force-disable テストが可能。

### その他の条件（Other Conditions）

- device/form factor: 条件なし。
- permission: 条件なし。
- API usage: `ScheduledExecutorService` / `ScheduledThreadPoolExecutor` または `Timer` の `scheduleAtFixedRate` を利用する fixed-rate periodic task。
- manifest attribute: 条件なし。
- component boundary: app process の Java executor / Timer / libcore runtime 内。WorkManager、JobScheduler、AlarmManager は本件の fixed-rate catch-up 仕様に直接依存しないが、内部やアプリコードで executor / Timer を併用している場合は別途確認が必要。
- process freeze と process death の区別: 本件は process が生存し scheduler queue が残ったまま CPU 実行機会を missed し、復帰後に queue を再開する挙動を扱う。process death では Timer / executor とその in-memory queue 自体が失われるため、本件の catch-up 経路ではない。

---

# AOSP 調査（AOSP Investigation）

## 関連ファイル（Related Files）

- `platform/libcore/ojluni/src/main/java/java/util/concurrent/ScheduledThreadPoolExecutor.java`
- `platform/libcore/ojluni/src/main/java/java/util/Timer.java`
- `platform/libcore/libcore.aconfig`
- `platform/libcore/api/current.txt`
- `frameworks-base/core/java/android/app/ActivityManager.java`
- `frameworks-base/services/core/java/com/android/server/am/Freezer.java`
- `frameworks-base/services/core/java/com/android/server/am/OomAdjuster.java`
- `frameworks-base/core/java/android/os/Build.java`

## 確認したソース文脈（Source Context Reviewed）

| ファイル / シンボル（File / symbol） | Android 15 の基準挙動（baseline） | Android 16 の挙動 | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| `ScheduledThreadPoolExecutor.STPE_SKIP_MULTIPLE_MISSED_PERIODIC_TASKS` | Android 15 r36 tag にも Change ID 288912692 と `@EnabledAfter(VANILLA_ICE_CREAM)` が存在 | 同じ。公開 compat page では Android 16 target 以上で default enabled | targetSdkVersion 36 gate の直接根拠 |
| `Timer.SKIP_MULTIPLE_MISSED_PERIODIC_TASKS` | Android 15 r36 tag にも Change ID 351566728 と `@EnabledAfter(VANILLA_ICE_CREAM)` が存在 | 同じ | Timer 側の targetSdkVersion 36 gate の直接根拠 |
| `skipMultipleMissedPeriodicTasks()` | compat change または `Flags.scheduleAtFixedRateNewBehavior()` が enabled なら true | 同じ | compat override と force-enable aconfig flag の入口 |
| `ScheduledFutureTask#setNextRunTime()` | fixed-rate (`p > 0`) で `time += p`。change enabled 時は過去に残った next schedule を最後の missed period へ補正 | 同じ | 複数 missed execution の catch-up を抑制する実装本体 |
| `ScheduledThreadPoolExecutor#scheduleAtFixedRate()` | positive period の `ScheduledFutureTask` を作る | 同じ。API doc に API 36 の説明あり | executor 側の entry point |
| `scheduleWithFixedDelay()` | negative period の `ScheduledFutureTask` を作る | 同じ | fixed-delay は `triggerTime(-p)` 経路で、fixed-rate catch-up 補正対象ではない |
| `TimerThread#mainLoop()` | fixed-rate (`p > 0`) で次回時刻を計算し、change enabled 時は最新の missed period へ補正 | 同じ | Timer の複数 catch-up を抑制する実装本体 |
| `Timer#scheduleAtFixedRate()` | positive period の task を `sched()` へ渡す | 同じ。Android API reference に API 36 の説明あり | Timer 側の entry point |
| `libcore.aconfig` / `schedule_at_fixed_rate_new_behavior` | Android 15 r36 tag に flag 定義あり | Android 16 r4 tag にも flag 定義あり | AppCompat flag / SDK_INT に関係なく新挙動を force-enable するための flag |
| `ActivityManager.PROCESS_CAPABILITY_CPU_TIME` | process が CPU time を保証され、freeze されない capability と説明 | 同じ | process freeze / CPU availability が missed periods の背景条件であることの補助根拠 |
| `Freezer#setProcessFrozen()` | process freeze/unfreeze を `Process.setProcessFrozen` に委譲 | 同じ | Cached Apps Freezer が process execution を止め得る補助文脈 |
| `OomAdjuster#getFreezePolicy()` | cached adj / CPU capability などから freeze policy を決める | 同じ | cached process が freeze 対象になり得る補助文脈 |

必須記入項目（Required context）:
- Entry point / caller: executor path は app code -> `ScheduledExecutorService#scheduleAtFixedRate()` -> `ScheduledThreadPoolExecutor#scheduleAtFixedRate()` -> `ScheduledFutureTask#run()` -> `setNextRunTime()` -> `reExecutePeriodic()`。Timer path は app code -> `Timer#scheduleAtFixedRate()` -> `sched()` -> `TimerThread#mainLoop()` -> `TaskQueue#rescheduleMin()`。
- Relevant class or service responsibility: `ScheduledThreadPoolExecutor` と `TimerThread` は periodic task の実行時刻と queue への再投入を管理する。`Freezer` / `OomAdjuster` は app process が frozen state に入る背景条件を管理するが、catch-up 回数を直接決めるわけではない。
- Runtime path from app API / system event to changed code: executor は fixed-rate task の `runAndReset()` 後に `setNextRunTime()`、Timer は task 実行前の `TimerThread#mainLoop()` で次回時刻を計算する。process が frozen / suspended で複数 period を missed した場合、復帰後の `now` と scheduled time の差により補正が入る。
- Why unrelated code paths were excluded: WorkManager / JobScheduler / AlarmManager は OS scheduling API であり、本件の executor / Timer `scheduleAtFixedRate` missed execution catch-up 仕様を直接決めないため、主証拠から除外した。`Timer#scheduleAtFixedRate` は別 Change ID 351566728 で同じ最適化の対象となるため、除外対象から調査対象へ訂正した。

## 差分解釈（Diff Interpretation）

| 確認した差分（Observed diff） | 解釈（Interpretation） | Behavior Change との関係 | 信頼度（Confidence） |
| --- | --- | --- | --- |
| Android 15 r36 と Android 16 r4 の該当 libcore 実装は同じ | No behavior change found between selected tags for core implementation | 指定 tag 間の実装 diff ではなく、targetSdkVersion 36 の compat default として説明される | High |
| `@EnabledAfter(targetSdkVersion = VersionCodes.VANILLA_ICE_CREAM)` | Changed condition / gate | targetSdkVersion 36 以上で default enabled | High |
| `setNextRunTime()` が change enabled 時に `time` を最後の missed period へ補正 | Changed behavior | 復帰時の immediate catch-up を最大 1 missed execution に抑制する | High |
| `TimerThread#mainLoop()` が change enabled 時に次回時刻を最新の missed period へ補正 | Changed behavior | Timer の復帰時 immediate catch-up も最大 1 missed execution に抑制する | High |
| `scheduleWithFixedDelay()` は negative period 経路 | No behavior change found for fixed-delay catch-up | fixed-delay は本件の fixed-rate missed period catch-up とは別挙動 | High |
| `api/current.txt` の public signatures に差分なし | No API surface change | 既存 API の runtime behavior change | High |

必須分類（Required interpretation）:
- Added behavior: `STPE_SKIP_MULTIPLE_MISSED_PERIODIC_TASKS` が enabled の場合、fixed-rate の next run time を最後の missed period へ補正する。
- Added behavior: Timer Change ID 351566728 が enabled の場合も、`TimerThread#mainLoop()` が次回時刻を最新の missed period へ補正する。
- Removed behavior: targetSdkVersion 36 以上では、複数 missed periods をすべて即時 catch-up する挙動が抑制される。
- Changed condition / gate: `@EnabledAfter(targetSdkVersion = VersionCodes.VANILLA_ICE_CREAM)`。Android 15 / API 35 より後、つまり targetSdkVersion 36 以上。
- Changed default: targetSdkVersion 36 以上で compat change が default enabled。
- No behavior change found: `scheduleWithFixedDelay` と public API signature には本件に相当する差分なし。指定 tag 間の core implementation 差分もなし。

## 事実（Facts）

- 公式文書は、この項目を apps targeting Android 16 / API level 36 の Behavior Change として掲載している。
- 公開 compat page は `STPE_SKIP_MULTIPLE_MISSED_PERIODIC_TASKS` / 288912692 を掲載し、Android 16 / API level 36 以上を target するアプリで default enabled と説明している。
- Android `Timer` API reference は API level 36 以降の fixed-rate task で catch-up が最大 1 回になることを説明している。
- AOSP libcore の `ScheduledThreadPoolExecutor` は Change ID 288912692 を持ち、`@EnabledAfter(targetSdkVersion = VersionCodes.VANILLA_ICE_CREAM)` が付いている。
- AOSP libcore の `Timer` は Change ID 351566728 を持ち、同じ `@EnabledAfter(targetSdkVersion = VersionCodes.VANILLA_ICE_CREAM)` が付いている。
- Android 16 の `Build.VERSION_CODES.VANILLA_ICE_CREAM` は 35、`BAKLAVA` は 36。
- executor の `skipMultipleMissedPeriodicTasks()` は Change ID 288912692、Timer の同名 method は Change ID 351566728 を確認し、どちらも各 compat change または `Flags.scheduleAtFixedRateNewBehavior()` が true のとき true を返す。
- fixed-rate task は `period > 0`、fixed-delay task は `period < 0` として内部表現される。
- fixed-rate では change enabled 時、次回時刻が過去に残っている場合に最後の missed period へ補正する。
- Timer の fixed-rate path でも change enabled 時、`TimerThread#mainLoop()` が次回時刻を最新の missed period へ補正する。
- Android 15 r36 tag にも同じ libcore 実装と aconfig flag が存在する。

## 観察（Observations）

- `ScheduledThreadPoolExecutor` と `Timer` は Activity lifecycle callback や process state API を直接参照していない。
- 「outside a valid process lifecycle」の実装上の具体例は、libcore コメント上は CPU suspend と Cached Apps Freezer である。
- AOSP の framework 側には process freeze/unfreeze を管理する `Freezer`、freeze policy を決める `OomAdjuster`、CPU time capability を示す `ActivityManager.PROCESS_CAPABILITY_CPU_TIME` があるが、catch-up 回数の最終判断は executor の `setNextRunTime()` または Timer の `mainLoop()` が行う。
- `scheduleAtFixedRate` の missed backlog を「実行されなかった回数分の処理」として意味づけているアプリでは、処理回数が減る。

## 仮説（Hypotheses）

- Android 15 端末でも、Mainline / libcore / ART module の状態や targetSdkVersion 36 の扱いによっては同じ挙動になる可能性がある。ただし公式 Behavior Change と公開 compat page は Android 16 target 以上の項目として説明しているため、顧客向け primary scope は Android 16 / targetSdkVersion 36 とする。
- `Flags.scheduleAtFixedRateNewBehavior()` が true の build では compat change や targetSdkVersion に関係なく新挙動が force-enabled される可能性がある。ただし通常顧客端末の default としては公開 compat page の default state を優先する。

## 結論（Conclusions）

- 主分類は `TARGET_SDK_36_CONDITIONAL`。
- Android 16 / targetSdkVersion 35 では、compat change は default disabled のため、従来の複数 missed execution catch-up が維持される想定である。
- Android 16 / targetSdkVersion 36 では、`scheduleAtFixedRate` の復帰時 immediate missed execution は最大 1 回になる。
- 実質影響は `scheduleAtFixedRate` を使い、process freeze / suspend 等で複数 period を missed する可能性があるアプリに限定される。

## 適用ゲート根拠（Applicability Gate Evidence）

- targetSdkVersion gate: `@EnabledAfter(targetSdkVersion = VersionCodes.VANILLA_ICE_CREAM)`。Android 15 / API 35 より後、targetSdkVersion 36 以上で enabled。
- CompatChanges.isChangeEnabled / ChangeId: executor は `Compatibility.isChangeEnabled(STPE_SKIP_MULTIPLE_MISSED_PERIODIC_TASKS)` / 288912692、Timer は `Compatibility.isChangeEnabled(SKIP_MULTIPLE_MISSED_PERIODIC_TASKS)` / 351566728。
- @EnabledAfter / @EnabledSince / default state: 公開 compat page は Android 16 / API level 36 以上を target するアプリで default enabled と説明。
- Build.VERSION / SDK_INT gate: libcore 実装上の明示的 `SDK_INT` 分岐は確認していない。compat framework と aconfig flag による gate。
- DeviceConfig / resources config: `libcore.aconfig` に `schedule_at_fixed_rate_new_behavior` があり、AppCompat flag / SDK_INT に関係なく force-enable する説明がある。
- Permission/AppOps gate: 該当なし。
- Manifest/property gate: 該当なし。
- No gate found: OS update only / all apps を示す primary gate は確認していない。
- Gate conclusion: Android 16 以上かつ targetSdkVersion 36 以上、さらに `scheduleAtFixedRate` の missed fixed-rate periods が発生する場合。
- Reasoning from source context: executor は復帰後の `setNextRunTime()`、Timer は `TimerThread#mainLoop()` で compat change enabled 時に次回時刻を最新の missed period へ補正するため、複数 missed executions の連続 catch-up が抑制される。

---

# 影響分析（Impact Analysis）

## 影響を受けるアプリ（Affected Apps）

- `ScheduledThreadPoolExecutor#scheduleAtFixedRate` を使うアプリ。
- `Timer#scheduleAtFixedRate` を使うアプリ。
- periodic task の missed execution がまとめて実行されることに依存しているアプリ。
- missed execution の backlog を「実行回数」として処理する設計のアプリ。
- 定期 polling、sync、metrics upload、retry、cleanup を fixed-rate で実装しているアプリ。
- fixed-rate task が idempotent でなく、実行回数がビジネスロジックに影響するアプリ。

## 影響を受けない、または影響が小さいアプリ（Non-Affected Apps）

- `scheduleAtFixedRate` を使っていないアプリ。
- `scheduleWithFixedDelay` を使い、前回完了から一定 delay 後の実行で問題ないアプリ。
- WorkManager / JobScheduler / AlarmManager のみで periodic work を実装しているアプリ。ただし内部で executor / Timer の fixed-rate task を併用している場合は確認が必要。
- fixed-rate task が idempotent で、missed period ごとの catch-up を必要としないアプリ。

## アプリ種別別の影響

| アプリ種別 | 影響 |
| --- | --- |
| `ScheduledThreadPoolExecutor#scheduleAtFixedRate` 利用 | targetSdkVersion 36 以上で復帰時 catch-up 回数が最大 1 回になる |
| `Timer#scheduleAtFixedRate` 利用 | 別 Change ID 351566728 により同じく復帰時 catch-up 回数が最大 1 回になる |
| missed execution をまとめて処理する前提 | 処理回数が減り、polling / retry / cleanup 等の設計見直しが必要になる可能性 |
| backlog を業務データとして扱う | missed period 数を別途計算・保存する必要がある可能性 |
| WorkManager / JobScheduler / AlarmManager 利用 | 本件 API の直接影響は小さい |
| `scheduleWithFixedDelay` 利用 | fixed-rate catch-up 仕様ではないため、本件の直接影響は小さい |

---

# 期待挙動マトリクス（Expected Behavior Matrix）

| 端末 OS | targetSdkVersion | compat flag | 期待挙動 |
| --- | --- | --- | --- |
| Android 15 | 35 | default | 複数 missed fixed-rate executions が復帰時に連続実行され得る |
| Android 16 | 35 | default | OS update だけでは新挙動は default enabled にならない想定 |
| Android 16 | 36 | default enabled | 復帰時に即時実行される missed execution は最大 1 回 |
| Android 16 | 35 | force-enabled | 新挙動をテスト可能。復帰時 immediate missed execution は最大 1 回 |
| Android 16 | 36 | force-disabled | 旧挙動を再現可能な可能性。複数 missed executions が連続実行され得る |
| Android 15 | 36 | 環境依存 | Android 15 r36 tag に同じ gate があるため要実機確認 |

---

# 推奨対応候補（Recommended Action Candidates）

- `ScheduledExecutorService` / `ScheduledThreadPoolExecutor` と `Timer` の `scheduleAtFixedRate` 利用箇所を棚卸しする。
- Lint `DiscouragedApi` を単に suppress せず、fixed-rate が必要な absolute-time 要件を確認する。
- 前回の実際の開始時刻を基準にしてよい Timer task は `Timer#schedule(..., period)`、前回処理の完了から一定間隔を空けたい task は `ScheduledExecutorService#scheduleWithFixedDelay` へ移行する。
- missed period の回数自体が必要な処理は、callback の catch-up 回数に依存せず、現在時刻と最終処理時刻から明示的に差分計算する。
- network、DB、UI 更新、file I/O を fixed-rate task で行う場合、復帰直後の連続実行がなくなっても正しいか確認する。
- idempotent でない periodic task は、最大 1 回実行でもデータ欠落や retry 不足にならないか確認する。
- WorkManager / JobScheduler は本 Behavior Change の公式移行先でも、`scheduleAtFixedRate` の等価な置換 API でもない。process death 後も再実行するという別要件が確認された場合だけ、background work の別設計として検討する。
- 詳細な Before / After、Timer、Java、テストコードは [Fixed rate work scheduling optimization - 実装例](../../case-guides/fixed-rate-work-scheduling-optimization-implementation-examples.md) を参照する。
- 5 秒周期での予定時刻、実開始、完了、process 復帰、長時間 task の違いは [Fixed rate work scheduling optimization - 実行挙動比較](fixed-rate-work-scheduling-optimization-runtime-behavior-comparison.md) を参照する。

代表例:

```kotlin
// missed callback 回数ではなく、最後に成功した時刻から必要な処理量を求める。
executor.scheduleAtFixedRate({
    reconciler.reconcile(lastSuccessfulAt = checkpoint.read(), now = clock.instant())
}, 0, periodSeconds, TimeUnit.SECONDS)
```

---

# テスト観点（Test Considerations）

| 端末 OS（Device OS） | targetSdkVersion | 条件 | 期待挙動 |
| --- | --- | --- | --- |
| Android 15 | 35 | default | missed fixed-rate tasks が複数回 catch-up され得る |
| Android 16 | 35 | default | 旧挙動が維持される想定 |
| Android 16 | 36 | default | missed fixed-rate task の即時 catch-up は最大 1 回 |
| Android 16 | 35/36 | executor 288912692 / Timer 351566728 enabled / disabled | executor / Timer の新旧挙動を個別に比較 |

確認対象:
- app を Cached Apps Freezer / suspend 相当の状態に置き、復帰時に `scheduleAtFixedRate` task が何回実行されるか。
- executor path と `Timer#scheduleAtFixedRate` path の両方で復帰時の実行回数を確認する。
- `scheduleAtFixedRate` と `scheduleWithFixedDelay` の比較。
- fixed-rate task が idempotent でない場合のデータ整合性。
- fixed-rate task が network、DB、UI 更新、file I/O を行う場合の負荷と欠落。
- missed period 数を業務上補填する必要があるか。

---

# Traceability Checklist

- Investigated Android versions: `android-15.0.0_r36` -> `android-16.0.0_r4`
- Related Behavior Change document: https://developer.android.com/about/versions/16/behavior-changes-16#schedule-at-fixed-rate
- Original statement being verified: 上記「公式ドキュメント確認」に記載。
- Evidence from AOSP source: `ScheduledThreadPoolExecutor.java`、`Timer.java`、`libcore.aconfig`、`api/current.txt`、`ActivityManager.java`、`Freezer.java`、`OomAdjuster.java`。
- AOSP source context reviewed: executor path は app API -> `ScheduledThreadPoolExecutor` -> `setNextRunTime()` -> Change ID 288912692、Timer path は app API -> `TimerThread#mainLoop()` -> Change ID 351566728。
- Diff interpretation: changed behavior、changed condition / gate、changed default、no public API surface change、no core implementation diff between selected tags。
- Applicability classification: `TARGET_SDK_36_CONDITIONAL`
- Confidence level: High

---

# 人間の判断欄（Human Decision Placeholder）

最終優先度（Final Priority）:
- 未判断

判断（Decision）:
- 未判断

管理者向け注記:
- 最終優先度、影響度、リリース判断、顧客通知の優先度は、リポジトリ管理者が判断する。

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
| `platform/libcore` | `https://android.googlesource.com/platform/libcore` | `tmp/aosp-checkouts/libcore/` | 展開中 | `android-15.0.0_r36` / `89a6322812dc8573315e60046e7959c50dad91d4` | `android-16.0.0_r4` / `1c599b67bcd3de5c50c79d0622e40b6de99b4cb4` | `git -C tmp/aosp-checkouts/libcore diff --no-renames --name-only android-15.0.0_r36 android-16.0.0_r4` | 部分クローンの working tree 展開中。根拠は解決済みタグの object 比較だけを使用し、展開途中のファイルを含めない。 |

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
