# Android 16 Connectivity and Security - ケース別対応手順

## 位置づけ

このファイルは Android 16 の connectivity / security 変更をケース別に実装・検証へ落とす companion guide である。
適用条件と根拠はリンク先の調査レポートを正とする。

## Bluetooth bond loss / encryption / unpair

Reports:
- [Improved bond loss handling](../all/connectivity/improved-bond-loss-handling.md)
- [New intents to handle bond loss and encryption changes](../target/connectivity/new-intents-to-handle-bond-loss-and-encryption-changes.md)
- [Adapting to varying OEM implementations](../target/connectivity/adapting-to-varying-oem-implementations-bond-loss.md)

| ケース | 判定条件 | 対応手順 | 最低限の検証 |
| --- | --- | --- | --- |
| Bonding 機能なし | bonded device を扱わない | 対応不要 | Bluetooth feature inventory |
| `ACTION_KEY_MISSING` あり | remote bond loss 後に intent 受信 | primary signal として UI を更新し、自動 reconnect を抑制して user-driven re-pair を案内 | local bond retained、disconnect、system dialog |
| `ACTION_KEY_MISSING` なし | OEM / legacy path | auth failure、disconnect、`BOND_NONE` 等の fallback state machine を維持 | 複数 OEM / peripheral |
| Encryption restored | `ACTION_ENCRYPTION_CHANGE` で成功状態 | bond restored として state を収束し reconnect loop を止める | algorithm / key size / success |
| Manual unpair | ユーザーが forget / re-pair を選択 | `BOND_NONE`、association、app state を同期する | forget → pair → reconnect |
| CDM-associated device | target 36、association ID があり public `removeBond(int)` を利用 | association ownership を確認し、結果は `ACTION_BOND_STATE_CHANGED` で追跡 | valid / invalid association、permission |
| IOP / OEM workaround | 例外的に local bond が削除 | 「常に bond retained」と仮定せず fallback を実行 | affected app/device combination |

注記:
- `CompanionDeviceManager.removeBond(int)` は公式ページにあるが、独立した repository report は未作成である。正式な finding 化までは preliminary procedure として扱う。

## Companion Device Manager discovery timeout

Report: [Companion apps no longer notified of discovery timeouts](../all/security/companion-apps-no-longer-notified-of-discovery-timeouts.md)

| ケース | 判定条件 | 対応手順 | 最低限の検証 |
| --- | --- | --- | --- |
| CDM discovery 未使用 | association flow なし | 対応不要 | feature inventory |
| Device discovered | discovery 中に候補あり | selection / association の通常経路を維持 | first 20 seconds / extended search |
| Timeout dialog dismissal | system timeout UI 後に `RESULT_USER_REJECTED` | timeout と user cancel を断定せず generic failure + safe retry を表示 | dialog dismiss / retry |
| User cancellation | 検索中にユーザーが停止 | 同じ result でも UI context から説明を分ける | cancel timing |
| Legacy timeout code 依存 | `RESULT_DISCOVERY_TIMEOUT` のみで retry | Android 16 では分岐を廃止し state / elapsed time / user action を補助 signal にする | Android 15 / 16 comparison |

## Intent redirection hardening

Reports:
- [Improved security against Intent redirection attacks](../all/security/improved-security-against-intent-redirection-attacks.md)
- [Opt-out](../all/security/improved-security-against-intent-redirection-attacks-opt-out.md)
- [Compile SDK 35 or lower](../all/security/improved-security-against-intent-redirection-attacks-targeting-before-16.md)

| ケース | 判定条件 | 対応手順 | 最低限の検証 |
| --- | --- | --- | --- |
| Nested Intent なし | external extras から Intent を launch しない | 通常 regression | exported entry points |
| Trusted first-party nested Intent | sender / destination が固定 | component、package、action、data、flags、URI grants を allowlist | valid / tampered payload |
| Untrusted nested Intent | 外部入力をそのまま launch | `IntentSanitizer` 等で sanitize、必要なら再構築 | private component / URI grant attack |
| Legitimate flow が block | hardening により既存 integration 失敗 | sender 修正と allowlist を優先し、opt-out は最小 scope | allowed partner / attacker input |
| compileSdk 36+ opt-out | 回避が不可避 | `removeLaunchSecurityProtection()` を対象 Intent のみに適用 | opt-out 有無と security test |
| compileSdk 35 以下 | direct API を呼べない | compile SDK 更新を優先。reflection は temporary / fragile fallback | API absence / exception handling |

## Safer Intents

Report: [Safer Intents](../target/security/safer-intents.md)

| ケース | 判定条件 | 対応手順 | 最低限の検証 |
| --- | --- | --- | --- |
| Opt-in していない | `intentMatchingFlags` なし | partner traffic を先に棚卸しし段階導入 | baseline logs |
| App-wide opt-in | `enforceIntentFilter` を application に指定 | 全 exported component の filter と sender を修正 | Activity / receiver / service / provider |
| 一部 component が非互換 | legacy partner が不一致 Intent を送る | component 単位 `none` を temporary exception として記録 | exception component のみ緩和 |
| Null action が必要 | action なしを正当に受ける | 該当 component のみに `allowNullAction` | null / valid / wrong action |
| Same-app Intent | 複数 app 間ではない | external flow と分け、通常 regression | internal navigation |
| Blocked log 発生 | PackageManager warning / access blocked | sender、filter、explicit target を照合して修正 | log zero / expected exception |

## GPU syscall filtering

Report: [GPU syscall filtering](../target/security/gpu-syscall-filtering.md)

| ケース | 判定条件 | 対応手順 | 最低限の検証 |
| --- | --- | --- | --- |
| Supported API のみ | Vulkan / OpenGL / EGL | 通常 graphics regression | Pixel Mali release build |
| Non-Mali / policy未導入 | device scope 外 | 非影響と断定せず OEM policy を記録 | GPU / build / OEM |
| Direct Mali IOCTL | native / SDK が `/dev/mali0` を操作 | supported graphics API または更新 SDK へ移行 | static scan + feature execution |
| Profiling / instrumentation | debug tooling | debuggable と release を分ける | shell / debug / non-debug |
| SELinux denial | `avc: denied { ioctl }` | ioctlcmd と context を記録し、影響機能を特定。必要なら公式窓口へ報告 | crash / feature loss / safe fallback |

## MediaStore version lockdown

Report: [MediaStore version lockdown](../target/security/mediastore-version-lockdown.md)

| ケース | 判定条件 | 対応手順 | 最低限の検証 |
| --- | --- | --- | --- |
| `getVersion()` 未使用 | API dependency なし | 対応不要 | code search |
| Same-app cache invalidation | equality のみ利用 | opaque token の equality に限定して維持 | token change before / after media update |
| Format parsing | substring / timestamp / schema を推測 | parsing を削除する | arbitrary token |
| Cross-app comparison | 別 app と値共有 | comparison / fingerprint用途を削除 | two packages / same volume |
| Item-level diff が必要 | collection token では不足 | MediaStore generation API を評価 | insert / update / delete |

## Verification status

- この分冊は documentation synthesis であり、対象アプリと peripheral / OEM matrix の observed result は未実施。
- Security opt-out は成功可否だけでなく、tampered input が拒否されることも同時に確認する。
- Bluetooth は intent、bond state、ACL disconnect、system UI、app UI を同一 timeline に記録する。
