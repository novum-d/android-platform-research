# Safer Intents - One Page Summary

## Summary

Android 16 の Safer Intents は、receiving app が manifest で opt-in することで、cross-app incoming intents をより厳格に検証する security feature。`android:intentMatchingFlags="enforceIntentFilter"` を指定した component では、explicit intent が target component の intent filter と一致する必要があり、action が null の intent は原則 match しない。

Android 16 初期時点では opt-in 方式のため、既存アプリ破壊リスクは限定される。ただし公式文書は、将来 release で strict intent resolution を default にする roadmap を示している。

## Applicability

- Classification: `TARGET_SDK_36_CONDITIONAL`
- Practical conditions:
  - Android 16 以上
  - `enable_intent_matching_flags` feature flag が有効
  - receiving app / component が `android:intentMatchingFlags` で `enforceIntentFilter` に opt-in
  - cross-app intent resolution が発生
  - explicit intent が target component の filter と一致しない、または action が null
- Caveat:
  - AOSP の enforcement path では明示的な targetSdkVersion 36 gate は確認できなかった。
  - `targetSdkVersion 36 化だけ` ではなく `manifest opt-in` が実質的な impact 条件。

## Key Evidence

- `android:intentMatchingFlags` は `<application>`, `<activity>`, `<activity-alias>`, `<receiver>`, `<service>`, `<provider>` で指定可能。
- supported flags は `enforceIntentFilter`, `none`, `allowNullAction`。
- component-level flags は application-level flags を override する。
- flags 未指定、`none`、または `enforceIntentFilter` なしの場合は enforcement されない。
- same-app caller は `UserHandle.isSameApp(...)` により skip される。
- blocked 時は `PackageManager` tag で `"Intent does not match component's intent filter:"` と `"Access blocked:"` が出る。

## Expected Behavior

| Scenario | Expected behavior |
|---|---|
| Android 16 / targetSdkVersion 35 / no opt-in | 従来挙動 |
| Android 16 / targetSdkVersion 36 / no opt-in | 従来挙動 |
| Android 16 / targetSdkVersion 36 / application-level opt-in | component に継承。component-level override 可能 |
| Android 16 / targetSdkVersion 36 / component-level `none` | 該当 component は enforcement なし |
| same-app explicit intent | enforcement 対象外 |
| cross-app explicit intent / filter mismatch | opt-in 済みなら block |
| null action intent | `allowNullAction` がなければ opt-in 済み component で block |

## Customer Impact

Android 16 へ OS update しただけ、または targetSdkVersion 36 にしただけでは、通常 Safer Intents の runtime impact は発生しない。影響が出るのは、receiving app が Safer Intents に opt-in し、外部 app から filter に一致しない explicit intent や action なし intent を受ける場合。

注意対象:

- exported activity / receiver / service を持つ
- partner app / SDK / launcher / shortcut / notification / broadcast sender と連携する
- deep link / app link / custom action / cross-app IPC を使う
- action なし intent を受ける互換実装がある
- application-level enforcement と component-level override を混在させる

## Recommended Actions

- exported components と外部 app から届く intents を棚卸しする。
- opt-in 前に partner integration と blocked intent log を検証する。
- 互換性が必要な component は `android:intentMatchingFlags="none"` で除外する。
- null action を許容する必要がある場合だけ `allowNullAction` を使う。
- 将来 default enforcement に備え、送信側 intent が受信側 filter と一致するよう修正する。

## Human Decision Placeholder

- Final priority: TBD by human
- Final severity: TBD by human
- Release readiness impact: TBD by human
- Customer communication priority: TBD by human
- Owner decision / next action: TBD by human
