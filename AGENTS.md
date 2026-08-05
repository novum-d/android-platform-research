# Android Platform Research Agent

## Primary Goal

This repository exists to investigate Android Behavior Changes and Android Build System updates.

Source code analysis is not the goal.
Source code analysis is used only to verify and explain Behavior Changes.

Build System investigations live under `build-system/`.
For Build System investigations, official documentation, release notes, compatibility matrices, and project verification are the primary evidence.
AOSP / tools/base source diff analysis is optional and should be used only when documentation and release notes are insufficient.

Human-facing reports, summaries, and explanations must be written in Japanese.
Codex-facing instructions, headings, and checklist item names may be written in English.

## Git Workflow

- Make all repository updates directly on `main`.
- Before editing, verify that the current branch is `main`; switch to `main` if necessary.
- Do not create or use topic, feature, or agent branches.
- Commit and push repository changes to `origin/main`.
- If uncommitted changes prevent a safe switch to `main`, stop and ask the repository owner how to proceed.

## Research Scope

For Android Platform investigations, the primary unit of investigation is a Behavior Change section.

For Build System investigations, the primary unit of investigation is a tool version update or migration topic.

For Android Platform Behavior Changes, do NOT start from source code.

Always follow:

```text
Behavior Change Documentation
-> AOSP Evidence
-> Customer-facing Investigation Report
-> One Page Summary
-> Human Decision
```

For Build System investigations, read `build-system/AGENTS.md` and follow:

```text
Release Notes / Entry Point
-> Change Inventory
-> Impact Triage
-> Primary Source Deep Dive
-> Compatibility Matrix
-> Version Diff Investigation
-> Migration Checklist
-> Human Decision
```

For Build System investigations, release notes are an entry point, not the final source of truth.
Extract changes from release notes, then deep dive only the changes that may affect the target project.

Version-specific scope, AOSP tags, targetSdkVersion, templates, classification rules, and priority focus belong under the relevant `android<version>/` directory.

When working on a version-specific investigation, read:

- Root `AGENTS.md`
- `.codex/prompts/investigation.md`
- `<version-dir>/AGENTS.md` when present
- `<version-dir>/README.md`
- `<version-dir>/GETTING_STARTED.md`
- `<version-dir>/behavior-changes/APPLICABILITY_CLASSIFICATION.md`

When working on a Build System investigation, read:

- Root `AGENTS.md`
- `.codex/prompts/investigation.md`
- `build-system/AGENTS.md`
- `build-system/README.md`
- Relevant `build-system/<area>/README.md`

## Android OS Version Behavior Comparison

When a Behavior Change needs to explain how the same trigger, initial state, or
application operation behaves differently between two Android OS versions,
create a companion comparison file from:

```text
docs/templates/android-os-version-behavior-comparison-template.md
```

The comparison file must:

- identify the baseline and target Android versions and AOSP tags;
- use the same app build, targetSdkVersion, device role, transport, initial
  state, and trigger on both OS versions unless a difference is explicitly
  called out;
- show the baseline and target timelines or state transitions side by side;
- separate OS-version behavior from targetSdkVersion conditions;
- separate system behavior from app-visible broadcasts, callbacks, API
  availability, and system UI;
- include Expected / Observed results and leave unexecuted observations marked
  as not tested;
- link to the primary investigation report and one-page summary.

This companion does not replace the customer-facing investigation report or
one-page summary. Applicability classification, confidence, evidence, and Human
Decision remain authoritative in the primary report.

## Target Audience

The audience is:

- Customers
- Android application developers
- Technical stakeholders

Reports must be understandable without reading AOSP source code.

## Traceability Requirements

For Android Platform Behavior Changes:

Every finding must include:

1. Investigated Android versions
2. Related Behavior Change document
3. Original statement being verified
4. Evidence from AOSP source
5. AOSP source context reviewed
6. Diff interpretation
7. Applicability classification
8. Confidence level

AOSP source context must specify:

- File / symbol / entry point / caller
- Why the reviewed code path is relevant to the Behavior Change
- Baseline Android behavior
- Target Android behavior
- Which kind of source diff was found: added behavior, removed behavior, changed condition, changed default, or no behavior change
- How that diff supports the applicability classification
- Unrelated or excluded code paths when relevant

A finding without traceability is incomplete.

For Build System investigations, every finding must include:

1. Investigated tool and versions
2. Related official documentation or release notes
3. Original statement being verified
4. Compatibility evidence
5. Entry Point and References
6. Fact / Evidence / Confidence mapping
7. Detection method
8. Affected modules
9. Verification commands
10. Rollback plan
11. Risk level
12. Confidence level

## Applicability Classification

For Android Platform Behavior Changes, every finding must classify when the change is applied.

Use the target version's `APPLICABILITY_CLASSIFICATION.md` as the source of truth for allowed labels and wording.

The classification must separate OS version conditions from targetSdkVersion conditions.

High confidence requires:

- Official Behavior Change statement
- AOSP gate evidence, or evidence that no targetSdkVersion gate exists
- Compat framework Change ID and default state when available
- Expected behavior for target Android version with previous targetSdkVersion
- Expected behavior for target Android version with target targetSdkVersion
- Additional conditions and exceptions

## Evidence Hierarchy

For Android Platform Behavior Changes:

Priority order:

1. AOSP source code
2. API surface changes (`current.txt`)
3. Android official documentation
4. Android release notes
5. External articles

For Build System investigations:

1. Entry point release notes
2. Official Documentation
3. Compatibility Matrix
4. API Reference / Migration Guide
5. Issue Tracker
6. 実機・実プロジェクト検証
7. Blog

## Fact vs Interpretation

Always separate:

- Facts
- Observations
- Hypotheses
- Conclusions

## Human Responsibilities

The agent must NOT determine:

- Final priority
- Final severity
- Release readiness
- Customer communication priority

These decisions belong to the repository owner.

The agent provides evidence and analysis only.

## Protected Notes

Do not edit:

```text
docs/notes/PERSONAL_NOTES.md
```

This file is reserved for the repository owner's private notes.

## AOSP Checkout Hygiene

Before using `frameworks-base` as evidence, check:

```bash
git -C frameworks-base status --short
git -C frameworks-base tag --list '<from-tag>'
git -C frameworks-base tag --list '<to-tag>'
```

If `frameworks-base` is dirty, do not treat local working tree changes as platform evidence.
Use explicit tag comparisons such as:

```bash
git -C frameworks-base diff <from-tag> <to-tag> -- <path>
```

Record any dirty checkout risk in the investigation report if it may affect confidence.

## Ignore

For Android Platform Behavior Changes, the following are generally out of scope unless a developer-facing Behavior Change can be explained:

- OWNERS
- TEST_MAPPING
- lint baseline
- test-only changes
- build configuration only changes
- internal refactors
- changes without explainable Android application developer impact

## Research Completion Criteria

For Android Platform Behavior Changes:

A research item is complete only if:

- Original statement is identified
- Source code evidence is collected
- Applicability classification is assigned
- OS update impact and targetSdkVersion impact are separated
- Compat framework evidence is checked when available
- Developer impact is explained
- Recommended action candidates are documented
- Confidence level is assigned
- One page summary is created
- Human decision placeholder is recorded

For Build System investigations:

- Official documentation or release notes are checked
- Entry point release notes are checked
- Change inventory is documented
- Deep dive decisions are documented
- Entry Point and References are documented separately
- Facts are linked to Evidence and Confidence
- Minimum and recommended versions are separated
- Compatibility matrix is filled
- Breaking changes are classified
- Change isolation impact is recorded
- Affected modules are documented
- Detection method is documented
- Verification commands are documented
- Test scope is documented
- Rollback plan is documented
- Follow-up tasks are documented
- PR split strategy is documented
- One page summary is created
- References are listed
- Human decision placeholder is recorded
