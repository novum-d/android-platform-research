# Demo Matrix

この matrix は、Android 15 / 16 / 17 の OS update impact と targetSdkVersion impact を分けて確認するための管理表です。

## Version Matrix

| Matrix ID | Device OS | API level | targetSdkVersion | 目的 | 期待する使い方 | Status |
| --- | --- | --- | --- | --- | --- | --- |
| M-15-35 | Android 15 | 35 | 35 | baseline | Android 15 時点の既存挙動を確認する | Runnable skeleton |
| M-16-35 | Android 16 | 36 | 35 | OS update impact | targetSdkVersion を上げずに Android 16 端末へ移行した影響を確認する | Runnable skeleton |
| M-16-36 | Android 16 | 36 | 36 | targetSdkVersion impact | Android 16 向け targetSdkVersion 更新時の影響を確認する | Runnable skeleton |
| M-17-36 | Android 17 | 37 | 36 | OS update impact | targetSdkVersion 36 のまま Android 17 端末へ移行した影響を確認する | Runnable skeleton |
| M-17-37 | Android 17 | 37 | 37 | targetSdkVersion impact | Android 17 向け targetSdkVersion 更新時の影響を確認する | Runnable skeleton |

必要に応じて、compat flag の force-enabled / force-disabled 行を追加します。

## Demo Case Matrix

| Demo case ID | Behavior Change | Report | Demo path | Primary matrix rows | Verification type | Status |
| --- | --- | --- | --- | --- | --- | --- |
| DC-001 | Predictive back migration | `android16/behavior-changes/target/user-experience-and-system-ui/migration-or-opt-out-required-for-predictive-back.md` | `demo-cases/predictive-back/` | M-15-35, M-16-35, M-16-36, M-17-36, M-17-37 | Manual gesture, build verification | Implemented skeleton |
| DC-002 | Edge-to-edge enforcement / opt-out | TBD | `demo-cases/edge-to-edge/` | M-15-35, M-16-35, M-16-36 | Screenshot, manual UI check | Planned |
| DC-003 | Local network permission | TBD | `demo-cases/local-network/` | M-16-36, M-17-36, M-17-37 | Manual permission flow, adb, instrumentation candidate | Planned |

## Demo Case Template

各 demo case は、この形で記録します。

```text
Demo case ID:
Title:
Related Behavior Change:
Related report:
Primary matrix rows:

Facts:
- Official documentation:
- AOSP / compat evidence:
- Known gates:

Demo purpose:
- What this demonstrates:
- What this does not prove:

Implementation:
- Module / package:
- Before path:
- After path:
- targetSdkVersion variants:

Verification:
- Manual steps:
- Automated commands:
- Expected behavior:
- Observed behavior:
- Evidence artifacts:

Limitations:
- Device / image dependency:
- Preview / beta risk:
- Unverified paths:

Human decision:
- Use in customer-facing explanation:
- Priority:
- Notes:
```

## Evidence Policy

デモの observed behavior は、調査レポートの補助 evidence として扱います。

High confidence の根拠にする場合でも、以下を別途満たす必要があります。

- 公式 Behavior Change statement を確認している。
- AOSP gate または targetSdkVersion gate 不在を確認している。
- compat framework Change ID と default state を確認している、または該当なしと説明している。
- OS update impact と targetSdkVersion impact を分けて説明している。
- 追加条件、例外、device / image dependency を記録している。

## Open Questions

| ID | Question | Owner | Status |
| --- | --- | --- | --- |
| Q-001 | 初期 demo project の AGP / Gradle / Kotlin version をどこまで新しくするか | Human | Open |
| Q-002 | Android 17 の確認対象を beta image にするか final image にするか | Human | Open |
| Q-003 | CI で emulator matrix を回す範囲をどこまで許容するか | Human | Open |
