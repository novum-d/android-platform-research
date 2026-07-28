# Android 15 → 16 Core functionality 挙動比較

## 1. 比較範囲

- [比較一覧](README.md)
- [ケース別対応手順](../case-guides/core-functionality.md)
- Baseline: Android 15 / `android-15.0.0_r36`
- Target: Android 16 / `android-16.0.0_r4`
- Observed: 全項目とも対象アプリでの実機結果は未実施

同一アプリ build、同一 targetSdkVersion、同一 job / receiver / native artifact を基本条件とする。
targetSdkVersion 36 が gate の項目だけ、target 35 / 36 build を追加比較する。

## 2. 先に結論

Core functionality では、Android 16 への OS update だけで変わる項目が多い。
特に JobScheduler quota、abandoned job、ordered broadcast は targetSdkVersion 35 のままでも
影響し得る。fixed-rate scheduling だけは Android 16 + targetSdkVersion 36 が主条件である。

## 3. 項目別比較

### JobScheduler quota optimizations

- [主レポート](../all/core-functionality/jobscheduler-quota-optimizations.md)
- [要約](../../summaries/all/core-functionality/jobscheduler-quota-optimizations-summary.md)
- 適用: `OS_UPDATE_ALL_APPS`

| 観点 | Android 15 | Android 16 |
| --- | --- | --- |
| System behavior | top state 中に開始した job や FGS と同時実行する job を quota-free にする feature-flag path がある | default では top-started / FGS-concurrent job も quota を消費し、active bucket も generous but finite |
| App signal | 長時間 job が従来どおり継続し得る | `STOP_REASON_QUOTA`、pending reason、再実行遅延 |
| 対応 | baseline runtime を記録 | work を中断可能・idempotent にし、retry / resume と user-initiated data transfer job を評価 |

状態差:

```text
Android 15: visible中に開始 -> background継続 -> exemption経路ではquota外
Android 16: visible中に開始 -> background継続 -> quota消費 -> stop / pending
```

### Abandoned empty jobs stop reason

- [主レポート](../all/core-functionality/abandoned-empty-jobs-stop-reason.md)
- [要約](../../summaries/all/core-functionality/abandoned-empty-jobs-stop-reason-summary.md)
- 適用: `OS_UPDATE_ALL_APPS`

| 観点 | Android 15 | Android 16 |
| --- | --- | --- |
| System behavior | `jobFinished()` 未呼び出しの timeout は一般的な timeout として扱われる | `JobParameters` が abandoned された timeout を識別し、反復時は aggressive backoff に進み得る |
| App signal | `STOP_REASON_TIMEOUT` | `STOP_REASON_TIMEOUT_ABANDONED` |
| 対応 | lifecycle leak を見落としやすい | strong reference と全完了経路の `jobFinished()` を保証し、abandoned を別集計 |

### Fully deprecating `setImportantWhileForeground`

- [主レポート](../all/core-functionality/fully-deprecating-jobinfo-setimportantwhileforeground.md)
- [要約](../../summaries/all/core-functionality/fully-deprecating-jobinfo-setimportantwhileforeground-summary.md)
- 適用: `OS_UPDATE_ALL_APPS`

| 観点 | Android 15 | Android 16 |
| --- | --- | --- |
| System behavior | deprecated だが flag と scheduler path が残る | `setImportantWhileForeground(true)` は warning を出す no-op |
| App signal | `isImportantWhileForeground()` が flag を反映し得る | 常に `false` |
| 対応 | 利用箇所と期待する優先度を特定 | call を削除し、expedited job、user-initiated transfer、FGS を用途別に選択 |

### Fixed rate work scheduling optimization

- [主レポート](../target/core-functionality/fixed-rate-work-scheduling-optimization.md)
- [要約](../../summaries/target/core-functionality/fixed-rate-work-scheduling-optimization-summary.md)
- 適用: `TARGET_SDK_36_CONDITIONAL`

| 観点 | Android 15 または target 35 | Android 16 / target 36 |
| --- | --- | --- |
| System behavior | freeze / pause 中の未実行回数を復帰直後に連続 catch-up し得る | 復帰直後に実行する未実行分を最大1回へ抑制 |
| App signal | callback が短時間に複数回 | callback は最大1回、その後は通常 cadence |
| 対応 | missed count を暗黙に callback 数から推測しない | 必要な差分は確定時刻から明示計算。要件により fixed-delay / WorkManager を選択 |

状態差:

```text
Android 15: t1,t2,t3をmiss -> resume -> run(t1),run(t2),run(t3)
Android 16 target36: t1,t2,t3をmiss -> resume -> run(latest相当を最大1回)
```

### Ordered broadcast priority scope

- [主レポート](../all/core-functionality/ordered-broadcast-priority-scope-no-longer-global.md)
- [要約](../../summaries/all/core-functionality/ordered-broadcast-priority-scope-no-longer-global-summary.md)
- 適用: `OS_UPDATE_ALL_APPS`

| 観点 | Android 15 | Android 16 |
| --- | --- | --- |
| System behavior | receiver priority が別 process / 別 app を含む global order として働き得る | priority order は同一 application process 内に限定。process 間順序は非保証 |
| App signal | high priority receiver が先に result / abort を変更する前提 | 別 process receiver の到着順が入れ替わり得る |
| 対応 | cross-process 順序依存を検出 | service、provider、AIDL、queue など明示的 protocol へ移行 |

### ART internal changes

- [主レポート](../all/core-functionality/art-internal-changes.md)
- [要約](../../summaries/all/core-functionality/art-internal-changes-summary.md)
- 適用: `MAINLINE_OR_PLAY_SYSTEM_UPDATE`

| 観点 | Android 15 baseline | Android 16 / updated ART module |
| --- | --- | --- |
| System behavior | その時点の ART internal layout / runtime behavior | internal implementation、performance、Java support が更新される |
| App signal | public API 利用では通常差なし | hidden API access error、JNI failure、instrumentation不整合、native crash など実装依存 |
| 対応 | SDK / library が runtime internals に依存するか棚卸し | public API へ移行し、Android 12+ の ART Mainline 更新端末も含めて回帰 |

単一の一律 callback 差ではない。OS version だけでなく ART module version と dependency versionを記録する。

### 16 KB page size compatibility mode

- [主レポート](../all/core-functionality/16-kb-page-size-compatibility-mode.md)
- [要約](../../summaries/all/core-functionality/16-kb-page-size-compatibility-mode-summary.md)
- 適用: `OS_UPDATE_ALL_APPS` + 16 KB device + native artifact 条件

| 観点 | Android 15 | Android 16 |
| --- | --- | --- |
| System behavior | 16 KB page support と staging / flagged backcompat code | 4 KB-aligned native app を検出し、compat mode、alignment detail、公開 manifest 制御へ統合 |
| App signal | product / flag 依存 | compat warning、native load / startup、性能差 |
| 対応 | 4 KB / 16 KB artifact を区別 | `pageSizeCompat` は一時 mitigation とし、全 `.so` を16 KB alignedで再build |

Android 15 tag にも staging code があるため、「コードが完全になかった」とは扱わない。
公式公開挙動と API surface の比較として Android 16 を target にする。

## 4. OS / targetSdk マトリクス

| 項目 | Android 15 / target 35 | Android 16 / target 35 | Android 16 / target 36 |
| --- | --- | --- | --- |
| JobScheduler quota | baseline | 新 quota policy | target 35 と同じ |
| Abandoned job | generic timeout | abandoned reason | target 35 と同じ |
| Important while foreground | legacy flag path | no-op | target 35 と同じ |
| Fixed-rate | legacy catch-up | legacy catch-up | catch-up 最大1回 |
| Ordered broadcast | cross-process global order が働き得る | process間非保証 | target 35 と同じ |
| ART | module version依存 | platform / module更新 | target 35 と同じ |
| 16 KB compat | staging / product依存 | 公開compat mode | target 35 と同じ |

## 5. 比較試験

| Case | 固定条件 | Trigger | Expected Android 15 | Expected Android 16 | Observed |
| --- | --- | --- | --- | --- | --- |
| C1 | 同一 long-running job | topからbackgroundへ | exemption経路を記録 | quota stop / pending | 未実施 |
| C2 | `jobFinished()`漏れ | timeout | generic timeout | abandoned reason | 未実施 |
| C3 | 同一 fixed-rate task | process freeze / resume | 複数catch-up | target36で最大1回 | 未実施 |
| C4 | 別process receivers | ordered broadcast | priority順になり得る | 順序非保証 | 未実施 |
| C5 | 同一 APK / `.so` | 16 KB device起動 | product依存 | compat mode / warning | 未実施 |

## 6. Evidence / Human Decision

各比較の Facts、AOSP source context、confidence はリンク先主レポートを正とする。
このファイルの内容は documentation synthesis であり、Observed result と Human Decision は確定しない。
