# Re-evaluation: Applicability Classification Readiness

Date:
- 2026-06-07

Version scope:
- From: android-15.0.0_r36
- To: android-16.0.0_r1

## Result

The repository is now ready to classify Android 16 Behavior Changes by applicability with high precision, provided that each individual finding still completes the required AOSP evidence checks.

Overall readiness:
- Classification process: High
- AOSP checkout availability: High
- Generated candidate lists: High
- Individual Behavior Change findings: Not yet rated, because per-section reports have not been written.

## AOSP Availability

Confirmed:
- `frameworks-base` is a git repository.
- Tag `android-15.0.0_r36` exists.
- Tag `android-16.0.0_r1` exists.
- `scripts/generate_target.sh` runs successfully.

## Generated Analysis

The analysis script now generates:
- `changed_files.txt`: full raw AOSP diff file list
- `relevant_changed_files.txt`: diff file list excluding OWNERS, TEST_MAPPING, lint baseline, and test-only paths
- `runtime_candidates.txt`: runtime implementation candidates
- `compat_candidates.txt`: compat framework candidates
- `api_surface_candidates.txt`: API surface candidates
- domain-specific lists for app, platform, UI, companion, hardware, and JobScheduler
- `target.txt`: union of relevant candidate lists, not the full raw diff

Latest observed counts:
- changed files: 12079
- relevant changed files: 9329
- runtime candidates: 1720
- compat candidates: 20
- target candidates: 1748

## Fixes Made During Re-evaluation

The previous script produced an imprecise `target.txt` because it included `changed_files.txt` in the union. That made `target.txt` equivalent to the full raw diff.

Fixed:
- `target.txt` now unions only curated candidate lists.
- `git diff` uses `--no-renames` to avoid large-diff rename detection warnings.
- generated candidate lists exclude ignored files and test-only paths.

## Spot Checks

Large screen / adaptive layout:
- AOSP evidence found for `UNIVERSAL_RESIZABLE_BY_DEFAULT`.
- Change ID: `357141415`
- Evidence includes `ActivityInfo.UNIVERSAL_RESIZABLE_BY_DEFAULT` and `appInfo.isChangeEnabled(...)`.
- Classification can proceed as targetSdkVersion 36 conditional, with large-screen/runtime-condition verification.

Touch opaque activities:
- AOSP evidence found for `ENABLE_TOUCH_OPAQUE_ACTIVITIES`.
- Evidence includes `@EnabledSince(targetSdkVersion = Build.VERSION_CODES.BAKLAVA)` and `CompatChanges.isChangeEnabled(...)`.
- Classification can proceed as targetSdkVersion 36 where linked to an official Behavior Change section.

Companion Device remove bond:
- AOSP evidence found for `CompanionDeviceManager.removeBond(int)`.
- Evidence includes `removeBond(int associationId)` and `ICompanionDeviceManager.removeBond(...)`.
- Classification still needs official Behavior Change statement and implementation-side permission/association checks before High confidence.

Fixed rate work scheduling optimization:
- `frameworks/base` search did not find `STPE_SKIP_MULTIPLE_MISSED_PERIODIC_TASKS`.
- This likely requires evidence outside `frameworks/base` or another source package.
- Do not assign High confidence for this item using `frameworks/base` evidence alone.

## Remaining Requirement For High Confidence Findings

Each individual Behavior Change report must still include:
- official Behavior Change page and original statement
- applicability classification
- AOSP source evidence
- targetSdkVersion or no-targetSdk gate evidence
- compat framework Change ID and default state when available
- Android 16 / targetSdkVersion 35 and Android 16 / targetSdkVersion 36 expected behavior
- additional device, permission, API usage, manifest, opt-out, and exception conditions
- confidence reason and missing evidence

## Current Assessment

The research framework can now support High confidence classification. The repository should not claim High confidence for all Android 16 Behavior Changes globally until each Behavior Change section has a completed report.
