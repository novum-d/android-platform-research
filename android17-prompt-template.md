You are analyzing Android platform Behavior Changes in this repository.

Human-facing reports, summaries, and explanations must be written in Japanese.
Codex-facing instructions, headings, and checklist item names may remain in English.

Research target:

- Android version: Android 17
- Version directory: android17
- From tag: android-16.0.0_r4
- To tag: TBD: Android 17 AOSP tag
- Previous targetSdkVersion: 36
- Target targetSdkVersion: 37
- Behavior Change section title: <公式ドキュメント上のセクション名>
- Official documentation URL: <公式ドキュメントURL>
- Report output file: android17/behavior-changes/01-<topic-slug>.md
- Summary output file: android17/summaries/01-<topic-slug>-summary.md

Official documentation excerpt:
Page title: <ページタイトル>
Page URL: <公式ドキュメントURL>
Page type: all apps / apps targeting Android 17 / compat framework changes

Section title: <セクション名>

Original text:
<ここに公式ドキュメントの該当セクション本文を貼る>

Additional notes:
<追加条件、例外、opt-out、移行方法、関連リンクがあれば貼る>

Mission:
Investigate this single Behavior Change section end to end.
Start from the official Behavior Change documentation excerpt above.
Do not start from source code.
Use AOSP source only to verify and explain the official Behavior Change statement.

Repository rules:

- Read README.md, AGENTS.md, android17/AGENTS.md, docs/GETTING_STARTED.md, docs/workflow/INVESTIGATION_PLAYBOOK.md, docs/workflow/REVIEW_CHECKLIST.md, docs/workflow/CONFIDENCE.md, docs/workflow/AOSP_CHECKOUT.md, and android17/behavior-
changes/APPLICABILITY_CLASSIFICATION.md before writing outputs.
- Use android17/templates/customer-report-template.md for the report.
- Use android17/templates/one-page-summary-template.md for the summary.
- Keep version-specific outputs under android17/.
- Do not overwrite existing unrelated files.
- Do not edit docs/notes/PERSONAL_NOTES.md.
- Do not decide final priority, final severity, release readiness, or customer communication priority. Leave those as human decisions.
- Check `git -C frameworks-base status --short` before using AOSP evidence. If frameworks-base is dirty, do not use local working tree changes as evidence. Use explicit tag comparisons only.
- Local frameworks-base currently has no android-17* tag. If Android 17 AOSP tag evidence is unavailable, record that limitation and do not assign High confidence to AOSP-backed conclusions.

Required investigation steps:

1. Extract the original official documentation statement being verified.
2. Identify the documentation page type and initial applicability assumption.
3. Inspect AOSP evidence under frameworks-base only if a target Android 17 AOSP tag is available.
4. Identify relevant files, symbols, entry points, and callers when AOSP evidence is available.
5. Explain why each reviewed code path is relevant to the Behavior Change.
6. Describe baseline behavior from android-16.0.0_r4.
7. Describe target Android behavior from Android 17 documentation and AOSP evidence when available.
8. Classify the source diff type: added behavior, removed behavior, changed condition, changed default, or no behavior change.
9. Check targetSdkVersion gates.
10. Check compat framework evidence when available.
11. If no gate or compat evidence is found, explicitly record what was searched and why the evidence was not found.
12. Separate OS update impact from targetSdkVersion impact.
13. Compare expected behavior for:
    - Android 17 with targetSdkVersion 36
    - Android 17 with targetSdkVersion 37
    - compat force-enabled if available
    - compat force-disabled if available
14. Separate facts, observations, hypotheses, and conclusions.
15. Assign exactly one applicability classification using android17/behavior-changes/APPLICABILITY_CLASSIFICATION.md.
16. Assign a confidence level and explain missing evidence.
17. Write recommended action candidates for Android app developers.
18. Create or update the report file.
19. Create or update the summary file.
20. Review both outputs against docs/workflow/REVIEW_CHECKLIST.md and fix any missing required sections before finishing.

Output requirements:

- The report must include investigated Android versions, related official document, original statement, AOSP source evidence or missing AOSP tag limitation, source context, diff interpretation, applicability classification, confidence
level, developer impact, recommended action candidates, and human decision placeholder.
- The summary must be understandable without reading AOSP source.
- Every finding must be traceable from official statement to evidence to conclusion.
- If evidence is insufficient, classify as Unknown / needs more evidence and explain what is missing.

Before final response:

- Run a repository search to ensure old template paths such as shared/templates or docs/templates were not introduced.
- Check root git status and `git -C frameworks-base status --short`; mention dirty checkout risk if present.
- Summarize what was completed and what still needs human decision.
