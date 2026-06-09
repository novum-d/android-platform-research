# Android 17 Behavior Changes

Behavior Changes の各セクションごとに、顧客説明向け調査レポートを作成する。

## Current Status

Android 17 official Behavior Change documentation is available.

Local AOSP status:
- `frameworks-base` currently has no `android-17*` tag.
- AOSP-backed High confidence conclusions must wait until the target Android 17 AOSP tag is available.

## Quick View

最初にここを見る。各 Behavior Change は必ず 1 つの primary classification に入れる。

| Classification | When it applies | Customer-facing meaning | List |
| --- | --- | --- | --- |
| [`OS_UPDATE_ALL_APPS`](APPLICABILITY_CLASSIFICATION.md#os_update_all_apps) | Android 17 上の全アプリ。targetSdkVersion に依存しない | OS アップデートだけで影響する可能性がある | [OS update / all apps](#os-update--all-apps) |
| [`TARGET_SDK_37`](APPLICABILITY_CLASSIFICATION.md#target_sdk_37) | Android 17+ で targetSdkVersion >= 37 | targetSdkVersion 37 化で有効になる | [targetSdkVersion 37](#targetsdkversion-37) |
| [`TARGET_SDK_37_CONDITIONAL`](APPLICABILITY_CLASSIFICATION.md#target_sdk_37_conditional) | targetSdkVersion >= 37 に加えて追加条件あり | targetSdkVersion 37 化だけでは不十分。端末条件、API 利用、権限なども必要 | [targetSdkVersion 37 + conditions](#targetsdkversion-37--conditions) |
| [`MAINLINE_OR_PLAY_SYSTEM_UPDATE`](APPLICABILITY_CLASSIFICATION.md#mainline_or_play_system_update) | Mainline / Google Play system update に依存 | Android 17 platform image だけで決まらない | [Mainline / Play system update](#mainline--play-system-update) |
| [`API_ADDITION_ONLY`](APPLICABILITY_CLASSIFICATION.md#api_addition_only) | 既存挙動変更ではなく API 追加 | 互換性リスクではなく採用機会 | [API addition only](#api-addition-only) |
| [`UNKNOWN_NEEDS_MORE_EVIDENCE`](APPLICABILITY_CLASSIFICATION.md#unknown_needs_more_evidence) | 根拠不足 | 顧客向け結論に使わない | [Unknown / needs evidence](#unknown--needs-evidence) |

## Official Documentation

Use:

```text
https://developer.android.com/about/versions/17/behavior-changes-all
https://developer.android.com/about/versions/17/behavior-changes-17
```

## Template

Use:

```text
android17/templates/customer-report-template.md
```

## OS Update / All Apps

Android 17 へ OS アップデートすると、targetSdkVersion を変更していないアプリにも影響する可能性がある項目。

| Report | Summary | Evidence section | One page summary | Status |
| --- | --- | --- | --- | --- |
| まだありません |  |  |  |  |

## targetSdkVersion 37

Android 17+ で targetSdkVersion を 37 以上にした場合に有効になる項目。

| Report | Summary | Evidence section | One page summary | Status |
| --- | --- | --- | --- | --- |
| まだありません |  |  |  |  |

## targetSdkVersion 37 + Conditions

targetSdkVersion 37 以上に加えて、端末条件、権限、API 利用、manifest property、process state などの追加条件を満たす場合に影響する項目。

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
