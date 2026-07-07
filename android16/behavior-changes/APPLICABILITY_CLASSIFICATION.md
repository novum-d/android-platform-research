# Android 16 Applicability Classification

このファイルは、Android 16 Behavior Changes を「OSアップデート時に自動的に適用される差分」と「targetSdkVersion 36 を上げた時に適用される差分」に分類するための基準を定義する。

## Version Scope

From:
- android-15.0.0_r36

To:
- android-16.0.0_r1

## Official Documentation Sources

Primary documentation:
- OS update / all apps: https://developer.android.com/about/versions/16/behavior-changes-all
- targetSdkVersion 36+: https://developer.android.com/about/versions/16/behavior-changes-16
- Compat framework: https://developer.android.com/about/versions/16/reference/compat-framework-changes

## Classification Labels

Use exactly one primary label per finding.

### OS_UPDATE_ALL_APPS

Use when the official document states that the behavior applies to all apps running on Android 16 regardless of targetSdkVersion.

Required evidence:
- Behavior Change source is `behavior-changes-all`, or equivalent official statement exists.
- AOSP evidence does not show a targetSdkVersion 36 gate.
- If implementation is gated, the gate is OS version, device capability, module version, permission state, app state, API usage, or another non-targetSdk condition.

Customer wording:
- Android 16 へ OS アップデートすると、targetSdkVersion を変更していないアプリにも影響する可能性がある。

### TARGET_SDK_36

Use when the behavior applies to apps targeting Android 16 / API level 36 or higher.

Required evidence:
- Behavior Change source is `behavior-changes-16`, or equivalent official statement exists.
- AOSP evidence shows a targetSdkVersion gate, compat ChangeId default-enabled for API 36+, or an API 36 condition.
- Android 16 / targetSdkVersion 35 and Android 16 / targetSdkVersion 36 have different expected behavior.

Customer wording:
- targetSdkVersion を 36 以上に上げると有効になるため、OS アップデートだけでは原則として発生しない。

### TARGET_SDK_36_CONDITIONAL

Use when targetSdkVersion 36 is necessary but not sufficient.

Examples of additional conditions:
- large screen or `sw600dp`
- specific permission group
- specific API usage
- cross-app component boundary
- manifest property or opt-out state
- process lifecycle state

Required evidence:
- Same evidence as `TARGET_SDK_36`.
- Additional runtime condition is documented and verified in AOSP or official docs.

Customer wording:
- targetSdkVersion 36 以上に加えて、特定の端末条件、API 利用、権限、manifest 設定などを満たす場合に影響する。

### OPT_IN_ONLY

Use when the official Android 16 documentation describes the current behavior as explicitly opt-in, and AOSP evidence shows that the behavior is not enabled by OS update alone or targetSdkVersion 36 alone.

Examples of opt-in gates:
- manifest attribute or manifest property
- app compat flag force-enable
- developer testing flag
- feature flag plus explicit app / component configuration

Required evidence:
- Official documentation states the opt-in nature or current opt-in stage.
- AOSP evidence identifies the exact opt-in gate.
- AOSP evidence shows that the default path does not apply the behavior without opt-in.
- Android 16 / targetSdkVersion 35 and Android 16 / targetSdkVersion 36 expected behavior are both stated.
- The report separates current Android 16 opt-in behavior from future default enforcement plans.

Customer wording:
- Android 16 の現時点では、OS アップデートや targetSdkVersion 36 化だけでは有効にならず、manifest 設定、compat flag、developer testing 手順などで明示的に opt-in した場合に影響する。

### MAINLINE_OR_PLAY_SYSTEM_UPDATE

Use when the change is delivered through a Mainline module or Google Play system update and is not strictly tied to the Android 16 platform image.

Required evidence:
- Official documentation states module or Google Play system update delivery.
- AOSP evidence identifies the module or package boundary where possible.
- Impact description separates platform version from module version.

Customer wording:
- Android 16 端末だけでなく、対象モジュールが更新された過去 OS の端末にも影響する可能性がある。

### API_ADDITION_ONLY

Use when the item adds or exposes an API but does not itself change existing app behavior.

Required evidence:
- API surface change is present.
- No Behavior Change statement or no changed behavior for existing apps is identified.
- Developer action is adoption opportunity, not compatibility mitigation.

Customer wording:
- 既存アプリの互換性リスクではなく、新 API の利用機会として扱う。

### UNKNOWN_NEEDS_MORE_EVIDENCE

Use when the classification cannot be defended yet.

Required action:
- Do not assign High confidence.
- Record missing evidence.
- Continue investigation before customer-facing conclusion.

## High Confidence Requirements

A classification can be High confidence only when all of the following are true:

- Original official statement is quoted or paraphrased with source URL.
- The page category and the original statement agree.
- AOSP evidence confirms the applicable gate, or confirms that no targetSdkVersion gate exists.
- Compat framework entry is checked when a Change ID exists.
- Android 16 / targetSdkVersion 35 and Android 16 / targetSdkVersion 36 expected behavior are both stated.
- Additional conditions and exceptions are stated.
- Customer-facing wording does not mix OS update impact with targetSdkVersion impact.

## Evidence Pattern

Record facts in this order:

1. Official documentation page and section.
2. Original applicability statement.
3. AOSP source context reviewed:
   - file / symbol / entry point / caller
   - why this code path is relevant to the Behavior Change
   - Android 15 baseline and Android 16 behavior
   - unrelated code paths excluded, when relevant
4. Diff interpretation:
   - observed source diff
   - whether it adds, removes, gates, or changes default behavior
   - how the diff supports the applicability classification
5. Exact gate evidence.
6. Compat framework Change ID and default state, if any.
7. Expected behavior matrix.
8. Developer impact and action candidates.
9. Confidence and missing evidence.

## Common Misclassifications

- Do not classify an item as `TARGET_SDK_36` only because it appears on Android 16 pages. Confirm the specific page and wording.
- Do not classify an item as `OS_UPDATE_ALL_APPS` only because the implementation changed in AOSP. Check whether the implementation is behind a targetSdkVersion or compat gate.
- Do not force opt-in-only behavior into `TARGET_SDK_36_CONDITIONAL` when AOSP does not show a targetSdkVersion 36 runtime gate.
- Do not treat a new API as a Behavior Change unless existing behavior changes.
- Do not ignore opt-out, exception, device form factor, or permission conditions.
- Do not use High confidence when the AOSP checkout is unavailable.
