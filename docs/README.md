# 共通ドキュメント（Docs）

このディレクトリは、バージョン非依存の運用・知識を用途別に分類する場所です。

Android バージョン固有の調査成果物、テンプレート、バックログ、ナレッジは `android<version>/` に置きます。
新しい Android バージョンの調査を始める場合は、新しい `android<version>/` を作り、既存バージョンの成果物を上書きしません。

バージョニング方針:

```text
docs/VERSIONING.md
```

## カテゴリ（Categories）

| パス（Path） | 目的（Purpose） | ファイル（Files） |
| --- | --- | --- |
| `GETTING_STARTED.md` | 初見向けの共通導線 | `GETTING_STARTED.md` |
| `overview/` | リポジトリの目的、位置づけ、情報源、時系列、用語 | `WHY.md`, `META.md`, `SOURCES.md`, `TIMELINE.md`, `glossary.md` |
| `workflow/` | 調査手順、判断基準、レビュー観点、避けるべき進め方 | `RESEARCH_PRINCIPLES.md`, `INVESTIGATION_PLAYBOOK.md`, `REVIEW_CHECKLIST.md`, `CONFIDENCE.md`, `ANTI_PATTERNS.md` |
| `planning/` | 複数 Android バージョンにまたがる将来テーマ | `FUTURE_INVESTIGATIONS.md` |
| `records/` | 完了 findings、人間の判断、学び | `FINDINGS.md`, `DECISIONS.md`, `LESSONS_LEARNED.md` |
| `knowledge/` | 複数 Android バージョンにまたがる仮説、未解決質問 | `hypotheses.md`, `questions.md` |
| `translation/` | 調査レポートを日本語化するときの用語、文体、翻訳メモリ | `GLOSSARY.md`, `STYLE_GUIDE.md`, `TRANSLATION_MEMORY.md` |
| `notes/` | 正式成果物に入れる前の個人メモ | `PERSONAL_NOTES.md` |

## よくある作業（Common Tasks）

| 作業（Task） | 最初に見る場所（Start here） |
| --- | --- |
| 初めて読む | `GETTING_STARTED.md` |
| 調査手順を確認する | `workflow/INVESTIGATION_PLAYBOOK.md` |
| レポート完成条件を確認する | `workflow/REVIEW_CHECKLIST.md` |
| Codex CLI で調査を実行する | `workflow/CODEX_CLI_RESEARCH_GUIDE.md` |
| Codex CLI で AGP 差分調査を実行する | `../build-system/CODEX_CLI_RESEARCH_GUIDE.md` |
| AOSP checkout の扱いを確認する | `workflow/AOSP_CHECKOUT.md` |
| confidence の基準を確認する | `workflow/CONFIDENCE.md` |
| やってはいけない進め方を確認する | `workflow/ANTI_PATTERNS.md` |
| 情報源の優先順位を確認する | `overview/SOURCES.md` |
| 用語の意味を揃える | `overview/glossary.md` |
| 日本語翻訳の用語・文体を確認する | `translation/GLOSSARY.md`, `translation/STYLE_GUIDE.md` |
| バージョニング方針を確認する | `VERSIONING.md` |

## ルート配置方針（Root Policy）

ルート直下に残す Markdown は、原則として入口になるものだけにします。

- `README.md`: リポジトリ全体の入口
- `AGENTS.md`: Codex / agent 向けの運用指示

調査プロセス、判断基準、横断的な記録、メモは `docs/<用途>/` に置きます。
バージョン固有のバックログ、テンプレート、分類、分析結果は `android<version>/` に置きます。
