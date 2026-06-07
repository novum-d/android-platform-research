Use docs/workflow/CODEX_CLI_RESEARCH_GUIDE.md as the source of truth for Codex CLI research prompts.

Core rules:
- Start from the specified official Behavior Change documentation section.
- Do not start from source code.
- Write human-facing reports, summaries, and explanations in Japanese.
- Read root AGENTS.md and <version-dir>/AGENTS.md when present.
- Treat frameworks-base/ as a local temporary AOSP checkout.
- Do not use local frameworks-base working tree changes as platform evidence.
- Use explicit tag comparisons between <from-tag> and <to-tag>.
- Do not edit docs/notes/PERSONAL_NOTES.md.
- Do not decide final priority, final severity, release readiness, or customer communication priority.
