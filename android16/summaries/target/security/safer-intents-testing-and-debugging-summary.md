# Safer Intents: Testing and debugging - One Page Summary

## Summary

Android 16 の Safer Intents を testing / debugging する際は、`PackageManager` tag の warning log を見る。公式文書が示す message は `"Intent does not match component's intent filter:"` と `"Access blocked:"`。

AOSP では、この warning は `blockIntent = true` の branch で出力され、その直後に該当 component が `resolveInfos.remove(i)` で resolution result から除外される。したがって warning log は actual block の強い signal。

## Applicability

- Classification: `OPT_IN_ONLY`
- Practical conditions:
  - Android 16 以上
  - `enable_intent_matching_flags` feature flag が有効
  - receiving app / component が `android:intentMatchingFlags="enforceIntentFilter"` に opt-in
  - cross-app intent resolution が発生
  - explicit intent が target component の filter と一致しない、または action が null
- Caveat:
  - AOSP の enforcement path では明示的な targetSdkVersion 36 gate は確認できなかった。
  - `targetSdkVersion 36 化だけ` ではなく `manifest opt-in` が実質的な条件。

## Debug Signals

| Signal | Meaning |
|---|---|
| `PackageManager` warning | actual block と強く対応 |
| `"Intent does not match component's intent filter:"` | incoming intent が target component filter に一致しない |
| `"Access blocked:"` | component が resolution result から除外された |
| `Intent.EXTENDED_FLAG_FILTER_MISMATCH` | mismatch marker。block と同義ではない |
| Unsafe intent stats / StrictMode | diagnostic signal。blocked boolean を分けて見る必要 |

## Expected Behavior

| Scenario | Expected behavior |
|---|---|
| no `android:intentMatchingFlags` | warning なし、従来挙動 |
| `enforceIntentFilter` + filter match | warning なし |
| `enforceIntentFilter` + filter mismatch | warning + block |
| `enforceIntentFilter` + null action | `allowNullAction` なしなら warning + block |
| same-app intent | enforcement 対象外、warning なし |
| component-level `none` | warning なし |

## Customer Impact

Android 16 へ OS update しただけ、または targetSdkVersion 36 にしただけでは、通常この warning / block は発生しない。影響が出るのは Safer Intents に opt-in し、外部 app から filter 不一致または action なし intent を受けた場合。

QA では partner app / SDK / launcher / shortcut / notification / broadcast sender から届く legacy explicit intent を重点的に確認する。

## Recommended Actions

- logcat filter: `tag=:PackageManager & (message:"Intent does not match component's intent filter:" | message:"Access blocked:")`
- warning が出たら、送信側 intent の action / category / data / type と受信側 intent filter を照合する。
- 互換性が必要な component は `android:intentMatchingFlags="none"` で一時除外する。
- null action を許容する必要がある場合だけ `allowNullAction` を検討する。

## Human Decision Placeholder

- Final priority: TBD by human
- Final severity: TBD by human
- Release readiness impact: TBD by human
- Customer communication priority: TBD by human
- Owner decision / next action: TBD by human
