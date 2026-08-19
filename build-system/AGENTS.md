# Build System Research Agent

## Primary Goal

This directory exists to investigate Android Build System updates.

Human-facing reports, summaries, checklists, and explanations must be written in Japanese.
Codex-facing instructions, headings, and checklist item names may be written in English.

The goal is not to collect notes. The goal is to create upgrade decision material:

- 何が変わるのか
- 何を確認すべきか
- どこまで影響するか
- どのように検証するか
- どの単位で PR を分けるべきか

## Research Scope

The primary unit of investigation is a Build System version update or migration topic.

Use `.codex/prompts/investigation.md` as the shared investigation workflow prompt.

## URL-Only Research Requests

Use `CODEX_CLI_RESEARCH_GUIDE.md` as the source of truth when an official Build
System entry-point URL is provided. AGP Release Notes URLs are supported by the
complete URL-only workflow.

For an AGP Release Notes URL, the agent must:

1. Read the official page and identify one target AGP version or release line.
2. Extract a complete change inventory before deciding which items need a deep
   dive.
3. Resolve the From version using the deterministic precedence defined in
   `CODEX_CLI_RESEARCH_GUIDE.md`.
4. Derive the output filenames from existing AGP conventions.
5. Generate a placeholder-free intermediate prompt under
   `tmp/research-prompts/build-system/agp/`.
6. Read the file back, validate the URL, versions, channel, and output paths,
   and then execute it in the current Codex session.
7. Continue through the detailed investigation, one-page summary, migration
   checklist, and human-decision placeholder. Prompt generation alone is not
   completion.

Do not ask the user to manually copy release-note content or the generated
prompt. Ask only when the URL or comparison baseline is genuinely ambiguous,
the official page cannot be read, or an unrelated output collision would be
overwritten.

Always follow:

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

Release Notes are an entry point, not the final source of truth.
Extract changes from release notes, then deep dive only the changes that may affect the target project.

Do not start from AOSP or tools/base source diffs in normal Build System investigations.

AOSP / tools/base diff investigation is optional and should be used only when:

- Release Notes are insufficient
- DSL change evidence is needed
- Build behavior change evidence is needed
- A change appears to be undocumented

Deep dive required for:

- Compatibility changes
- Breaking changes
- Deprecations
- Default value changes
- DSL changes
- Task behavior changes
- Build performance impact
- CI impact
- Native / NDK impact
- Lint changes
- Release artifact impact
- Changes related to APIs, plugins, tasks, or modules used by the target project

Usually skip deep dive for:

- Simple bug fixes
- Typo fixes
- Internal refactors
- Changes irrelevant to the target project
- Test-only or documentation-only changes

## Target Areas

Initial target areas:

- Android Gradle Plugin (AGP)
- Gradle
- Kotlin
- NDK
- CI

Future target areas should follow the same structure:

- KSP
- Compose Compiler

## Change Isolation Policy

Do not mix the following updates in the same PR unless a documented compatibility requirement makes it unavoidable:

- AGP update
- Gradle update
- Kotlin update
- compileSdk update
- targetSdkVersion update
- minSdk update
- NDK update
- dependency library update

The purpose is to minimize the impact surface of each change.

When an update must be combined with another update, record:

- Required combined change
- Source that proves the requirement
- Files affected
- Verification commands
- Rollback plan

## Version Update Policy

- Do not mix non-required updates.
- Treat `compileSdk` updates as Build System compatibility work.
- Treat `targetSdkVersion` updates as Android Behavior Changes work.
- Treat `minSdk` updates as a separate product and compatibility decision.
- Keep dependency library updates separate unless required by the Build System update.

## Evidence Hierarchy

Priority order:

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

## Required Common Sections

Each version investigation should include:

Detailed investigation:

- Summary
- Investigation Entry Point
- Change Inventory
- Evidence
- References
- Minimum Required Versions
- Compatibility Matrix
- Breaking Changes
- Risk Level
- Affected Modules
- Detection Method
- Verification Commands
- Test Scope
- Rollback Plan
- Decision Log
- Completion Criteria
- Follow-up Tasks
- References

One-page summary:

- Decision Summary
- Scope
- Minimum Required Versions
- Compatibility Matrix
- Breaking Changes Summary
- Risk Level
- Verification Commands
- PR Strategy
- Follow-up Tasks
- Human Decision

## Human Responsibilities

The agent must NOT determine:

- Final priority
- Final severity
- Release readiness
- Customer communication priority
- Whether the upgrade should ship

These decisions belong to the repository owner.

The agent provides evidence and analysis only.

## Completion Criteria

A Build System research item is complete only if:

- The investigation exit criteria in `.codex/prompts/investigation.md` are satisfied
- Official documentation or release notes were checked
- Entry point release notes were checked
- Change inventory is documented
- Deep dive decisions are documented
- Entry Point and References are documented separately
- Facts are linked to Evidence and Confidence
- Minimum and recommended versions are separated
- Compatibility matrix is filled
- Breaking changes are classified as Must Fix / Should Fix / Watch / No Action
- Change isolation impact is recorded
- Detection method is documented
- Verification commands are documented
- Test scope is documented
- Rollback plan is documented
- Affected modules are documented
- Decision log placeholder is recorded
- Follow-up tasks are documented
- PR split strategy is documented
- One page summary is created
- References are listed
