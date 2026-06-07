# Android 16 Behavior Changes

Behavior Changes の各セクションごとに、顧客説明向け調査レポートを作成する。

## Quick View

最初にここを見る。各 Behavior Change は必ず 1 つの primary classification に入れる。

| Classification | When it applies | Customer-facing meaning | List |
| --- | --- | --- | --- |
| [`OS_UPDATE_ALL_APPS`](APPLICABILITY_CLASSIFICATION.md#os_update_all_apps) | Android 16 上の全アプリ。targetSdkVersion に依存しない | OS アップデートだけで影響する可能性がある | [OS update / all apps](#os-update--all-apps) |
| [`TARGET_SDK_36`](APPLICABILITY_CLASSIFICATION.md#target_sdk_36) | Android 16+ で targetSdkVersion >= 36 | targetSdkVersion 36 化で有効になる | [targetSdkVersion 36](#targetsdkversion-36) |
| [`TARGET_SDK_36_CONDITIONAL`](APPLICABILITY_CLASSIFICATION.md#target_sdk_36_conditional) | targetSdkVersion >= 36 に加えて追加条件あり | targetSdkVersion 36 化だけでは不十分。端末条件、API 利用、権限なども必要 | [targetSdkVersion 36 + conditions](#targetsdkversion-36--conditions) |
| [`MAINLINE_OR_PLAY_SYSTEM_UPDATE`](APPLICABILITY_CLASSIFICATION.md#mainline_or_play_system_update) | Mainline / Google Play system update に依存 | Android 16 platform image だけで決まらない | [Mainline / Play system update](#mainline--play-system-update) |
| [`API_ADDITION_ONLY`](APPLICABILITY_CLASSIFICATION.md#api_addition_only) | 既存挙動変更ではなく API 追加 | 互換性リスクではなく採用機会 | [API addition only](#api-addition-only) |
| [`UNKNOWN_NEEDS_MORE_EVIDENCE`](APPLICABILITY_CLASSIFICATION.md#unknown_needs_more_evidence) | 根拠不足 | 顧客向け結論に使わない | [Unknown / needs evidence](#unknown--needs-evidence) |

## Applicability Classification

Each report must classify when the behavior is applied:

- OS update / all apps on Android 16 regardless of targetSdkVersion
- targetSdkVersion >= 36 on Android 16+
- targetSdkVersion >= 36, with additional runtime conditions
- Mainline / Google Play system update dependent
- API addition only, not a behavior change
- Unknown / needs more evidence

Use:

```text
android16/behavior-changes/APPLICABILITY_CLASSIFICATION.md
```

## Naming

```text
01-jobscheduler.md
02-companion-device.md
03-broadcast.md
```

## Template

Use:

```text
android16/templates/customer-report-template.md
```

## OS Update / All Apps

Android 16 へ OS アップデートすると、targetSdkVersion を変更していないアプリにも影響する可能性がある項目。

| Report | Summary | Evidence section | One page summary | Status |
| --- | --- | --- | --- | --- |
| まだありません |  |  |  |  |

## targetSdkVersion 36

Android 16+ で targetSdkVersion を 36 以上にした場合に有効になる項目。

| Report | Summary | Evidence section | One page summary | Status |
| --- | --- | --- | --- | --- |
| まだありません |  |  |  |  |

## targetSdkVersion 36 + Conditions

targetSdkVersion 36 以上に加えて、端末条件、権限、API 利用、manifest property、process state などの追加条件を満たす場合に影響する項目。

| Report | Summary | Evidence section | One page summary | Status |
| --- | --- | --- | --- | --- |
| まだありません |  |  |  |  |

## Mainline / Play System Update

Mainline module または Google Play system update の配信状態に依存する項目。

| Report | Summary | Evidence section | One page summary | Status |
| --- | --- | --- | --- | --- |
| まだありません |  |  |  |  |

## API Addition Only

既存アプリの挙動変更ではなく、新 API の利用機会として扱う項目。

| Report | Summary | Evidence section | One page summary | Status |
| --- | --- | --- | --- | --- |
| まだありません |  |  |  |  |

## Unknown / Needs Evidence

分類根拠が不足しており、顧客向け結論に使えない項目。

| Report | Missing evidence | Next check | Status |
| --- | --- | --- | --- |
| 現在 tracked item はありません |  |  |  |

## Link Targets For Reports

各レポートを追加したら、上の一覧から該当箇所へ直接飛べるように以下の形式でリンクする。

| Destination | Link format |
| --- | --- |
| Report top | `[Title](NN-title.md)` |
| Applicability section | `[Applicability](NN-title.md#applicability)` |
| AOSP gate evidence | `[Gate evidence](NN-title.md#applicability-gate-evidence)` |
| Verification matrix | `[Matrix](NN-title.md#matrix)` |
| One page summary | `[Summary](../summaries/NN-title-summary.md)` |
