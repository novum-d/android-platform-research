# Android 16 Research Agent Scope

This file contains Android 16-specific instructions.
Read it together with the root `AGENTS.md`.

## Version Scope

All Android 16 findings must explicitly specify:

From:
- android-15.0.0_r36

To:
- android-16.0.0_r1

## Target SDK Focus

The target SDK focus is:

- targetSdkVersion 36

## Priority Focus

1. Behavior Changes
2. targetSdkVersion 36 impacts
3. Security / Privacy
4. JobScheduler / WorkManager
5. Companion Device / Bluetooth
6. Broadcast / Intent / Permission
7. Large Screen / Window
8. API Additions

## Android 16 Applicability Classification

Every Android 16 finding must classify when the change is applied:

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

High confidence requires:

- Official Behavior Change statement
- AOSP gate evidence, or evidence that no targetSdkVersion gate exists
- Compat framework Change ID and default state when available
- Android 16 / targetSdkVersion 35 and Android 16 / targetSdkVersion 36 expected behavior
- Additional conditions and exceptions

## Android 16 Output Files

Use:

```text
android16/templates/customer-report-template.md
android16/templates/one-page-summary-template.md
```

Write outputs under:

```text
android16/behavior-changes/
android16/summaries/
```

Human decisions belong in:

```text
android16/decisions/DECISION_LOG.md
```

## Android 16 Completion Criteria

An Android 16 research item is complete only if:

- Original statement is identified
- Source code evidence is collected
- Applicability classification is assigned
- OS update impact and targetSdkVersion 36 impact are separated
- Compat framework evidence is checked when available
- Developer impact is explained
- Recommended action candidates are documented
- Confidence level is assigned
- One page summary is created
- Human decision placeholder is recorded
