# Android 16 Research Agent Scope

This file contains Android 16-specific instructions.
Read it together with the root `AGENTS.md`.

## Version Scope

All Android 16 findings must explicitly specify:

From:
- android-15.0.0_r36

To:
- android-16.0.0_r4

This pair is the current latest standard AOSP release-tag pair for Android 15
and Android 16. Before creating or updating a finding, apply the tag freshness
rule in the root `AGENTS.md`. Existing reports must continue to state the tags
actually used for their evidence until they are revalidated.

Machine-readable scope source:

```text
android16/research-scope.json
```

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
android16/templates/behavior-change-faq-template.md
android16/templates/implementation-examples-template.md
android16/templates/runtime-behavior-comparison-template.md
docs/templates/android-os-version-behavior-comparison-template.md
```

Write outputs under:

```text
android16/behavior-changes/
android16/summaries/
```

When a Behavior Change needs concrete code examples, framework-specific migration examples, or temporary opt-out examples, create a companion implementation examples file from:

```text
android16/templates/implementation-examples-template.md
```

Store implementation examples under:

```text
android16/behavior-changes/case-guides/
```

Keep primary reports focused on evidence, applicability, impact, and action candidates.
Place only short representative snippets and a link to the implementation examples file in the primary report.

When reader questions require a FAQ, create a separate companion FAQ from:

```text
android16/templates/behavior-change-faq-template.md
```

Do not place a multi-question FAQ inside the primary report. Keep the primary report as the source of truth for classification, confidence, evidence, and Human Decision, and link to the FAQ companion.

When a Behavior Change needs a side-by-side explanation of runtime timing, callback selection, fallback, delayed execution, or lifecycle behavior, create a companion runtime behavior comparison file from:

```text
android16/templates/runtime-behavior-comparison-template.md
```

Use identical inputs and runtime conditions for every compared implementation. Separate expected behavior derived from official documentation / source from observed device or test results.

When a Behavior Change needs a comparison of the same operation or trigger on
Android 15 and Android 16, create a companion OS version comparison file from:

```text
docs/templates/android-os-version-behavior-comparison-template.md
```

Keep the app build and runtime conditions identical across OS versions, and
separate OS behavior, targetSdkVersion conditions, app-visible signals, and
system UI. Link the companion from the primary report; do not duplicate or
override the primary report's classification, confidence, evidence, or Human
Decision.

Human decisions belong in:

```text
android16/decisions/DECISION_LOG.md
```

## Android 16 Research Complete Criteria

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

The item becomes Decision Complete only after the repository owner records the
decision in `android16/decisions/DECISION_LOG.md`.
