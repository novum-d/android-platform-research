# Android 17 Research Agent Scope

This file contains Android 17-specific instructions.
Read it together with the root `AGENTS.md`.

## Version Scope

Android 17 findings must explicitly specify:

From:
- android-16.0.0_r4

To:
- TBD: Android 17 AOSP tag

Until the Android 17 AOSP tag is available in `frameworks-base`, do not assign High confidence based on AOSP evidence.

## Target SDK Focus

The target SDK focus is:

- targetSdkVersion 37

## Priority Focus

1. Behavior Changes
2. targetSdkVersion 37 impacts
3. Security / Privacy
4. Core functionality
5. Audio / Media
6. Bluetooth / Connectivity
7. Contacts Provider / Permissions
8. Large Screen / Window
9. API Additions

## Android 17 Applicability Classification

Every Android 17 finding must classify when the change is applied:

- OS update / all apps on Android 17 regardless of targetSdkVersion
- targetSdkVersion >= 37 on Android 17+
- targetSdkVersion >= 37, with additional runtime conditions
- Mainline / Google Play system update dependent
- API addition only, not a behavior change
- Unknown / needs more evidence

Use:

```text
android17/behavior-changes/APPLICABILITY_CLASSIFICATION.md
```

High confidence requires:

- Official Behavior Change statement
- AOSP gate evidence, or evidence that no targetSdkVersion gate exists
- Compat framework Change ID and default state when available
- Android 17 / targetSdkVersion 36 and Android 17 / targetSdkVersion 37 expected behavior
- Additional conditions and exceptions

## Android 17 Output Files

Use:

```text
android17/templates/customer-report-template.md
android17/templates/one-page-summary-template.md
```

Write outputs under:

```text
android17/behavior-changes/
android17/summaries/
```

Human decisions belong in:

```text
android17/decisions/DECISION_LOG.md
```

## Android 17 Completion Criteria

An Android 17 research item is complete only if:

- Original statement is identified
- Source code evidence is collected, or missing AOSP tag evidence is explicitly recorded
- Applicability classification is assigned
- OS update impact and targetSdkVersion 37 impact are separated
- Compat framework evidence is checked when available
- Developer impact is explained
- Recommended action candidates are documented
- Confidence level is assigned
- One page summary is created
- Human decision placeholder is recorded
