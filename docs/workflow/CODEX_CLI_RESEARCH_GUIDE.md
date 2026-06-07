# Codex CLI Research Guide

この手順書は、Codex CLI に貼り付けるだけで Android Behavior Change 調査を開始できるプロンプトを用意するためのものです。

使い方は、下の「貼り付け用プロンプト」の変数だけを書き換え、そのまま Codex CLI に貼り付けます。Codex への指示文そのもの、見出し、項目名は英語で書いてよいですが、調査レポート、要約、人間向け説明、判断材料は日本語で書かせます。

## 事前準備

調査を始める前に、対象バージョンの以下が存在することを確認します。

```text
<version-dir>/README.md
<version-dir>/AGENTS.md
<version-dir>/behavior-changes/APPLICABILITY_CLASSIFICATION.md
<version-dir>/templates/customer-report-template.md
<version-dir>/templates/one-page-summary-template.md
```

`frameworks-base` に比較対象 tag が存在することも確認します。

```bash
git -C frameworks-base status --short
git -C frameworks-base tag --list '<from-tag>'
git -C frameworks-base tag --list '<to-tag>'
```

`frameworks-base` が dirty な場合は、ローカル working tree の変更を platform evidence として扱わないでください。必ず `<from-tag>` と `<to-tag>` の明示的な tag 比較を使います。

AOSP checkout の扱いは以下も確認します。

```text
docs/workflow/AOSP_CHECKOUT.md
```

## 編集する変数

貼り付け用プロンプト内の以下だけを編集します。

| 変数 | 内容 |
| --- | --- |
| `<android-version>` | 調査対象の Android バージョン名 |
| `<version-dir>` | 調査成果物を置くディレクトリ |
| `<from-tag>` | 比較元 AOSP tag |
| `<to-tag>` | 比較先 AOSP tag |
| `<previous-target-api>` | OS update impact を比較するための直前 targetSdkVersion |
| `<target-api>` | 調査対象の targetSdkVersion / API level |
| `<section-title>` | 調査する Behavior Change セクション名 |
| `<behavior-change-url>` | 公式 Behavior Change 文書の URL |
| `<official-documentation-excerpt>` | 公式文書の該当セクション原文 |
| `<report-file>` | 作成する調査レポートの path |
| `<summary-file>` | 作成する 1ページ要約の path |

`<official-documentation-excerpt>` には、最低限以下を含めます。

- セクションタイトル
- 原文 statement
- 適用条件が書かれている段落
- 追加条件、例外、opt-out が書かれている段落
- 関連リンクがあれば URL

## 貼り付け用プロンプト

以下をコピーし、変数を埋めてから Codex CLI に貼り付けます。

```text
You are analyzing Android platform Behavior Changes in this repository.

Human-facing reports, summaries, and explanations must be written in Japanese.
Codex-facing instructions, headings, and checklist item names may remain in English.

Research target:
- Android version: <android-version>
- Version directory: <version-dir>
- From tag: <from-tag>
- To tag: <to-tag>
- Previous targetSdkVersion: <previous-target-api>
- Target targetSdkVersion: <target-api>
- Behavior Change section title: <section-title>
- Official documentation URL: <behavior-change-url>
- Report output file: <report-file>
- Summary output file: <summary-file>

Official documentation excerpt:
<official-documentation-excerpt>

Mission:
Investigate this single Behavior Change section end to end.
Start from the official Behavior Change documentation excerpt above.
Do not start from source code.
Use AOSP source only to verify and explain the official Behavior Change statement.

Repository rules:
- Read README.md, AGENTS.md, <version-dir>/AGENTS.md if present, docs/GETTING_STARTED.md, docs/workflow/INVESTIGATION_PLAYBOOK.md, docs/workflow/REVIEW_CHECKLIST.md, docs/workflow/CONFIDENCE.md, docs/workflow/AOSP_CHECKOUT.md, and <version-dir>/behavior-changes/APPLICABILITY_CLASSIFICATION.md before writing outputs.
- Use <version-dir>/templates/customer-report-template.md for the report.
- Use <version-dir>/templates/one-page-summary-template.md for the summary.
- Keep version-specific outputs under <version-dir>/.
- Do not overwrite existing unrelated files.
- Do not edit docs/notes/PERSONAL_NOTES.md.
- Do not decide final priority, final severity, release readiness, or customer communication priority. Leave those as human decisions.
- Check `git -C frameworks-base status --short` before using AOSP evidence. If frameworks-base is dirty, do not use local working tree changes as evidence. Use explicit tag comparisons only.

Required investigation steps:
1. Extract the original official documentation statement being verified.
2. Identify the documentation page type and initial applicability assumption.
3. Inspect AOSP evidence under frameworks-base by comparing <from-tag> and <to-tag>.
4. Identify relevant files, symbols, entry points, and callers.
5. Explain why each reviewed code path is relevant to the Behavior Change.
6. Describe baseline behavior from <from-tag>.
7. Describe target Android behavior from <to-tag>.
8. Classify the source diff type: added behavior, removed behavior, changed condition, changed default, or no behavior change.
9. Check targetSdkVersion gates.
10. Check compat framework evidence when available: @ChangeId, @EnabledAfter, @EnabledSince, @Disabled, CompatChanges.isChangeEnabled, default state, and toggleability.
11. If no gate or compat evidence is found, explicitly record what was searched and why the evidence was not found.
12. Separate OS update impact from targetSdkVersion impact.
13. Compare expected behavior for:
    - target Android version with previous targetSdkVersion
    - target Android version with target targetSdkVersion
    - compat force-enabled if available
    - compat force-disabled if available
14. Separate facts, observations, hypotheses, and conclusions.
15. Assign exactly one applicability classification using <version-dir>/behavior-changes/APPLICABILITY_CLASSIFICATION.md.
16. Assign a confidence level and explain missing evidence.
17. Write recommended action candidates for Android app developers.
18. Create or update <report-file>.
19. Create or update <summary-file>.
20. Review both outputs against docs/workflow/REVIEW_CHECKLIST.md and fix any missing required sections before finishing.

Output requirements:
- The report must include investigated Android versions, related official document, original statement, AOSP source evidence, source context, diff interpretation, applicability classification, confidence level, developer impact, recommended action candidates, and human decision placeholder.
- The summary must be understandable without reading AOSP source.
- Every finding must be traceable from official statement to AOSP evidence to conclusion.
- If evidence is insufficient, classify as Unknown / needs more evidence and explain what is missing.

Before final response:
- Run a repository search to ensure old template paths such as shared/templates or docs/templates were not introduced.
- Check root git status and `git -C frameworks-base status --short`; mention dirty checkout risk if present.
- Summarize what was completed and what still needs human decision.
```

## 実行後に人間が確認すること

Codex の出力後、人間が以下を確認します。

- 公式文書の原文が正しく扱われているか
- AOSP evidence が Behavior Change の説明と対応しているか
- OS update impact と targetSdkVersion impact が混ざっていないか
- compat framework evidence の有無が明記されているか
- `High confidence` の根拠が十分か
- 顧客向けの説明になっているか
- final priority / severity を人間が判断できる材料になっているか

人間の最終判断は、対象バージョンの `decisions/` に記録します。

## 追加確認用プロンプト

Codex の出力が弱い場合だけ、以下を追加で貼ります。

```text
作成した report と summary を docs/workflow/REVIEW_CHECKLIST.md に照らして再レビューしてください。
不足している項目を修正してください。
特に original statement、AOSP source context、diff interpretation、applicability classification、OS update impact、targetSdkVersion impact、compat framework evidence、confidence level を確認してください。
```

compat framework の確認が弱い場合:

```text
compat framework evidence を再確認してください。
@ChangeId、@EnabledAfter、@EnabledSince、@Disabled、CompatChanges.isChangeEnabled を検索し、
該当 Change ID、default state、targetSdkVersion との関係を明記してください。
見つからない場合は、検索した file / symbol / query を記録してください。
```

AOSP 根拠がファイル名だけになっている場合:

```text
AOSP source context が不足しています。
file / symbol / entry point / caller、baseline behavior、target Android behavior、
diff type、なぜそのコードパスが Behavior Change の根拠になるかを追記してください。
無関係または除外したコードパスがあれば、それも書いてください。
```
