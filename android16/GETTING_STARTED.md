# Android 16 Getting Started

このファイルは、Android 16 調査を進める時に読む場所をまとめる。

## 読む順番

1. [README.md](README.md) で Android 16 の version scope を確認する
2. [behavior-changes/README.md](behavior-changes/README.md) で Behavior Change 一覧と分類を見る
3. [behavior-changes/APPLICABILITY_CLASSIFICATION.md](behavior-changes/APPLICABILITY_CLASSIFICATION.md) で適用条件分類を確認する
4. [templates/customer-report-template.md](templates/customer-report-template.md) で調査レポートの書式を確認する
5. [templates/one-page-summary-template.md](templates/one-page-summary-template.md) で 1ページ要約の書式を確認する
6. [summaries/README.md](summaries/README.md) で要約一覧を確認する
7. [decisions/DECISION_LOG.md](decisions/DECISION_LOG.md) で人間の判断ログを確認する

## 計画とバックログ

| Need | Link |
| --- | --- |
| Android 16 planning | [planning/ROADMAP.md](planning/ROADMAP.md) |
| Android 16 backlog | [planning/RESEARCH_BACKLOG.md](planning/RESEARCH_BACKLOG.md) |

## Codex CLI

Codex CLI で Android 16 調査を実行する場合は、共通手順書を読んだ上で、このディレクトリの version scope と template path を使う。

```text
../docs/workflow/CODEX_CLI_RESEARCH_GUIDE.md
```

## Analysis Generation

Android 16 の analysis files を再生成する場合:

```bash
VERSION_DIR=android16 \
OLD_TAG=android-15.0.0_r36 \
NEW_TAG=android-16.0.0_r1 \
TARGET_CODENAME=BAKLAVA \
scripts/generate_target.sh
```
