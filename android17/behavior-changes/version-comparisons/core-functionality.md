# Android 16 → 17 Core functionality 挙動比較

## 1. 比較範囲

- [比較一覧](README.md)
- [Android 17対応例](../implementation-examples/core-functionality.md)
- Baseline: Android 16 / `android-16.0.0_r4`
- Target: Android 17 / `android-17.0.0_r1`
- App build: 同一build
- Observed: 対象アプリで未実施

## 2. 先に結論

App memory limitsはOS updateだけでも端末条件次第で影響する。
MessageQueueとstatic final fieldはAndroid 17 + targetSdkVersion 37が主gateであり、
Android 17へ更新しただけのtarget 36 appには原則として新defaultを適用しない。

## 3. 項目別比較

### App memory limits

- [主レポート](../all/core-functionality/app-memory-limits.md)
- [要約](../../summaries/all/core-functionality/app-memory-limits-summary.md)
- 適用: `OS_UPDATE_ALL_APPS` + vendor config / RAM / process state

| 観点 | Android 16 | Android 17 |
| --- | --- | --- |
| System behavior | Android 17の`MemoryLimiter`によるapp process別上限なし | total RAMとprocess visibilityに応じたlimitを設定し、極端なoutlierを終了させ得る |
| App signal |通常のLMK / OOM / process death | `ApplicationExitInfo`、`MemoryLimiter:AnonSwap` description、process death |
| 対応 | peak RSS / anon swapをbaseline化 | image / video / cache / leakのpeakを削減し、process recreationとresumeを保証 |

状態差:

```text
Android 16: memory growth -> system-wide pressure時の既存memory management
Android 17: memory growth -> per-process configured limit超過 -> process終了
```

すべてのAndroid 17端末がlimitを課すわけではない。
`/vendor/etc/memory-limiter-config.xml`と`am memory-limiter status`で端末条件を確認する。

### New lock-free implementation of MessageQueue

- [主レポート](../target/core-functionality/messagequeue-lock-free.md)
- [要約](../../summaries/target/core-functionality/messagequeue-lock-free-summary.md)
- 適用: `TARGET_SDK_37`
- Compat Change ID: `USE_NEW_MESSAGEQUEUE = 421623328`

| 観点 | Android 16 / target 36 | Android 17 / target 37 |
| --- | --- | --- |
| System behavior | legacy lock-based `MessageQueue` | lock-free / concurrent implementation |
| App signal | private fields / methodsへのreflectionが偶然動く場合がある | private layout依存でreflection failure、test failure、SDK不整合 |
| 対応 | hidden / private accessを検出 | public Looper / Handler APIへ移行し、Robolectric legacy modeも更新 |

通常のpublic APIだけを使うappでは、主な差はperformance / missed frame改善として現れる。

### Static final fields are now unmodifiable

- [主レポート](../target/core-functionality/static-final-fields.md)
- [要約](../../summaries/target/core-functionality/static-final-fields-summary.md)
- 適用: `TARGET_SDK_37_CONDITIONAL`

| 観点 | Android 16 / target 36 | Android 17 / target 37 |
| --- | --- | --- |
| System behavior | Android 17のtarget37強制ruleなし。runtime / field条件によりmutation pathが残る | reflection / JNIによる`static final`書き換えを拒否 |
| App signal | test hook / patchが動作し得る | reflectionは`IllegalAccessException`、JNI `SetStatic*Field()`はcrash |
| 対応 | app / SDK / testのfield mutationを検索 | dependency更新、DI / mutable test seam / supported configurationへ移行 |

「Java上推奨されない操作がAndroid 16で常に成功する」という意味ではない。
比較対象はAndroid 17で追加されたtarget37 enforcementである。

## 4. OS / targetSdk マトリクス

| 項目 | Android 16 / target36 | Android 17 / target36 | Android 17 / target37 |
| --- | --- | --- | --- |
| App memory limits |新limiterなし | device条件で適用 | target36と同じ |
| MessageQueue | legacy | legacy default | lock-free default |
| Static final | target37 enforcementなし | legacy compatibility | mutation拒否 |

## 5. 比較試験

| Case | Trigger | Expected Android 16 | Expected Android 17 | Observed |
| --- | --- | --- | --- | --- |
| C1 | large image / cacheでmemory増加 |既存memory management | configured deviceでlimit終了 | 未実施 |
| C2 | Handler / Looper stress | legacy queue | target37でlock-free | 未実施 |
| C3 | MessageQueue private reflection |動作し得る | target37で破損可能性 | 未実施 |
| C4 | reflection static final write | runtime依存 | `IllegalAccessException` | 未実施 |
| C5 | JNI static final write | runtime依存 | crash | 未実施 |

## 6. Evidence / Human Decision

Facts、AOSP gate、device条件、confidenceは主レポートを正とする。
このファイルはExpected behaviorのsynthesisであり、Observed resultとHuman Decisionは確定しない。
