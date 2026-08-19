Route Codex CLI research prompts by area:
- Android Behavior Changes: docs/workflow/CODEX_CLI_RESEARCH_GUIDE.md
- Build System and AGP: build-system/CODEX_CLI_RESEARCH_GUIDE.md

Core rules:
- When the user supplies an official Behavior Change section URL, accept the URL as sufficient input and follow the URL-only workflow in root AGENTS.md.
- Analyze the official section, derive version metadata and output paths from the repository, and write the completed intermediate prompt to tmp/research-prompts/.
- Read the generated prompt back and execute it in the current Codex session without asking the user to paste it again or launching a nested Codex process.
- When the user supplies an official AGP Release Notes URL, accept it as sufficient input when the From version can be derived by the build-system guide.
- Generate AGP intermediate prompts under tmp/research-prompts/build-system/agp/, then read and execute them in the current Codex session.
- Start from the specified official entry point: the Behavior Change section for Android Platform research or Release Notes for AGP research.
- Do not start from source code.
- Write human-facing reports, summaries, and explanations in Japanese.
- Read root AGENTS.md and <version-dir>/AGENTS.md when present.
- Treat frameworks-base/ as a local temporary AOSP checkout.
- Do not use local frameworks-base working tree changes as platform evidence.
- Use explicit tag comparisons between <from-tag> and <to-tag>.
- Do not edit docs/notes/PERSONAL_NOTES.md.
- Do not decide final priority, final severity, release readiness, or customer communication priority.
