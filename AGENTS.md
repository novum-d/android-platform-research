# Android Platform Research Agent

## Primary Goal

This repository exists to investigate Android Behavior Changes.

Source code analysis is not the goal.
Source code analysis is used only to verify and explain Behavior Changes.

Human-facing reports, summaries, and explanations must be written in Japanese.
Codex-facing instructions, headings, and checklist item names may be written in English.

## Research Scope

The primary unit of investigation is a Behavior Change section.

Do NOT start from source code.

Always follow:

```text
Behavior Change Documentation
-> AOSP Evidence
-> Customer-facing Investigation Report
-> One Page Summary
-> Human Decision
```

Version-specific scope, AOSP tags, targetSdkVersion, templates, classification rules, and priority focus belong under the relevant `android<version>/` directory.

When working on a version-specific investigation, read:

- Root `AGENTS.md`
- `<version-dir>/AGENTS.md` when present
- `<version-dir>/README.md`
- `<version-dir>/GETTING_STARTED.md`
- `<version-dir>/behavior-changes/APPLICABILITY_CLASSIFICATION.md`

## Target Audience

The audience is:

- Customers
- Android application developers
- Technical stakeholders

Reports must be understandable without reading AOSP source code.

## Traceability Requirements

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

## Applicability Classification

Every finding must classify when the change is applied.

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

Priority order:

1. AOSP source code
2. API surface changes (`current.txt`)
3. Android official documentation
4. Android release notes
5. External articles

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

The following are generally out of scope unless a developer-facing Behavior Change can be explained:

- OWNERS
- TEST_MAPPING
- lint baseline
- test-only changes
- build configuration only changes
- internal refactors
- changes without explainable Android application developer impact

## Research Completion Criteria

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
