# Safer Intents: Impact - One Page Summary

## Summary

Android 16 の Safer Intents は、初期時点では opt-in の security feature。`android:intentMatchingFlags="enforceIntentFilter"` を manifest に明示した app / component だけが、より厳格な incoming intent matching の対象になる。

Impact セクションの要点は、Android 16 では既存アプリ破壊リスクを抑えるため opt-in に限定しつつ、将来 release で strict intent resolution を default にする roadmap がある、という点。

## Applicability

- Classification: `OPT_IN_ONLY`
- Practical runtime conditions:
  - Android 16 以上
  - `enable_intent_matching_flags` feature flag が有効
  - app / component が `android:intentMatchingFlags` で `enforceIntentFilter` に opt-in
  - cross-app intent resolution が発生
  - explicit intent が target component の intent filter に一致しない、または action が null
- Caveat:
  - AOSP の enforcement path では明示的な targetSdkVersion 36 gate は確認できなかった。
  - `targetSdkVersion 36 化だけ` ではなく `manifest opt-in` が実質的な impact 条件。

## Key Evidence

- `android:intentMatchingFlags` は `<application>` と `<activity>`, `<activity-alias>`, `<receiver>`, `<service>`, `<provider>` で指定可能。
- supported flags は `enforceIntentFilter`, `none`, `allowNullAction`。
- component-level flags は application-level flags を override する。
- flags 未指定、`none`、または `enforceIntentFilter` なしの場合は enforcement されない。
- same-app caller は skip される。
- blocked 時は `PackageManager` tag で `"Intent does not match component's intent filter:"` と `"Access blocked:"` が出る。

## Expected Behavior

| Scenario | Expected behavior |
|---|---|
| Android 16 / targetSdkVersion 35 / no opt-in | 従来挙動 |
| Android 16 / targetSdkVersion 36 / no opt-in | 従来挙動 |
| Android 16 / targetSdkVersion 36 / application-level opt-in | components に継承。ただし component-level override 可能 |
| Android 16 / targetSdkVersion 36 / component-level `none` | 該当 component は enforcement なし |
| same-app explicit intent | enforcement 対象外 |
| cross-app explicit intent / filter mismatch | opt-in 済みなら block |
| null action intent | `allowNullAction` がなければ opt-in 済み component で block |

## Customer Impact

Android 16 へ OS update しただけ、または targetSdkVersion 36 にしただけでは、通常この Impact は発生しない。影響が出るのは Safer Intents に opt-in したうえで、外部 app から filter に一致しない explicit intent や action なし intent を受けている場合。

特に注意するアプリ:

- exported activity / receiver / service を持つ
- partner app / SDK / launcher / shortcut / notification と連携する
- deep link / custom action / broadcast / cross-app IPC を使う
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

## 再検証記録（2026-08-22）

- Android 16 の公式 Behavior Change 一覧と最新通常AOSPタグを再確認した。
- 対応する[主レポート](../../../behavior-changes/target/security/safer-intents-impact.md)で official section、AOSP project / remote / checkout、解決済み commit、比較 command、dirty risk を再検証した。
- 主レポートの分類、confidence、未確認事項を維持し、実機未実施の項目を Observed 済みへ変更していない。
- 全件の結果は[再検証台帳](../../../analysis/REVALIDATION_2026-08-22.md)を参照する。
