# Android Behavior Change 調査依頼テンプレート

`docs/workflow/CODEX_CLI_RESEARCH_GUIDE.md` の固定調査指示に従い、Behavior Change 1件をend-to-endで調査するための共通テンプレートです。

通常は人間が埋めません。Codexが公式セクションURLを解析し、`<version-dir>/research-scope.json`、version-specific instructions、公式本文から値を補完して、`tmp/research-prompts/`配下へ中間プロンプトを生成します。URLを利用できない場合の手動fallback、または生成内容のレビューにのみ使用します。

## 調査対象

Android version: <android-version>

Version directory: <version-dir>

From tag: <from-tag>

To tag: <to-tag>

Previous targetSdkVersion: <previous-target-api>

Target targetSdkVersion: <target-api>

Behavior Change section title: <official-section-title>

Official documentation URL: <official-section-url>

Official documentation category: <official-category>

Report output file: <version-dir>/behavior-changes/<all-or-target>/<official-category-slug>/<topic-slug>.md

Summary output file: <version-dir>/summaries/<all-or-target>/<official-category-slug>/<topic-slug>-summary.md

## 公式セクション解析

Page title: <page-title>

Canonical page URL: <canonical-page-url>

Page type: all apps / apps targeting Android <android-version> / compat framework changes

Page category: <official-category>

Parent section title: <parent-section-title-or-none>

Section title: <official-section-title>

Subsections:
- <subsection-or-none>

Original statements to verify:
- <official-statement-1>
- <official-statement-2>

Applicability details:
- <OS / targetSdkVersion / permission / API / device / app-state conditions>

Exceptions / opt-in / opt-out / migration details:
- <detail-or-none>

Official related links:
- <official-related-link>

## Repository metadata

Metadata source: <version-dir>/research-scope.json

Allowed applicability labels: <version-dir>/behavior-changes/APPLICABILITY_CLASSIFICATION.md

Report template: <version-dir>/templates/customer-report-template.md

Summary template: <version-dir>/templates/one-page-summary-template.md

## Required investigation focus

- 公式statementとAOSP evidenceを対応付ける。
- `<from-tag>`と`<to-tag>`を明示的に比較する。
- 関係する各AOSP repositoryについてproject path、checkout状態、tag、commit hash、比較commandを記録する。
- OS update impactとtargetSdkVersion impactを分離する。
- targetSdkVersion gate、compat Change ID、default state、追加条件、例外を確認する。
- Facts / Observations / Hypotheses / Conclusionsを分ける。
- ReportとSummaryを日本語で作成する。
- One page summaryに`Pending Human Decision`を残す。

## Additional notes

- <追加の調査観点。なければ「なし」>
