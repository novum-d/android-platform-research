# Android 16 はじめに（Getting Started）

このファイルは、Android 16 調査を進める時に読む場所をまとめる。

## 読む順番

1. [README.md](README.md) で Android 16 のバージョンスコープを確認する
2. [behavior-changes/README.md](behavior-changes/README.md) で Behavior Change 一覧と分類を見る
3. [behavior-changes/CASE_BASED_ACTION_GUIDE.md](behavior-changes/CASE_BASED_ACTION_GUIDE.md) で項目ごとのケース別対応手順を確認する
4. [behavior-changes/APPLICABILITY_CLASSIFICATION.md](behavior-changes/APPLICABILITY_CLASSIFICATION.md) で適用条件分類を確認する
5. [templates/customer-report-template.md](templates/customer-report-template.md) で調査レポートの書式を確認する
6. [templates/one-page-summary-template.md](templates/one-page-summary-template.md) で 1ページ要約の書式を確認する
7. 読者向け FAQ が必要な場合は [templates/behavior-change-faq-template.md](templates/behavior-change-faq-template.md) を使い、主レポートとは別のファイルにする
8. コード例や framework 別の移行例が必要な場合は [templates/implementation-examples-template.md](templates/implementation-examples-template.md) を使い、`behavior-changes/case-guides/` に置く
9. 複数の API / 実装方式について、実行時刻、callback の順序、fallback を比較する場合は [templates/runtime-behavior-comparison-template.md](templates/runtime-behavior-comparison-template.md) を使う
10. 同じ操作の Android 15 / 16 間の挙動差を比較する場合は [Android OS バージョン間挙動比較テンプレート](../docs/templates/android-os-version-behavior-comparison-template.md) を使う
11. 調査済み項目の Android 15 / 16 差は [Android 15 → 16 挙動比較一覧](behavior-changes/version-comparisons/README.md) で確認する
12. [summaries/README.md](summaries/README.md) で要約一覧を確認する
13. [decisions/DECISION_LOG.md](decisions/DECISION_LOG.md) で人間の判断ログを確認する

## 計画とバックログ

| 確認したいこと | リンク |
| --- | --- |
| Android 16 の計画 | [planning/ROADMAP.md](planning/ROADMAP.md) |
| Android 16 のバックログ | [planning/RESEARCH_BACKLOG.md](planning/RESEARCH_BACKLOG.md) |

## Codex CLI

Codex CLI で Android 16 調査を実行する場合は、共通手順書を読んだ上で、このディレクトリのバージョンスコープとテンプレートのパスを使う。

```text
../docs/workflow/CODEX_CLI_RESEARCH_GUIDE.md
```

## 分析ファイルの生成

Android 16 の分析ファイルを再生成する場合:

```bash
VERSION_DIR=android16 \
OLD_TAG=android-15.0.0_r36 \
NEW_TAG=android-16.0.0_r4 \
TARGET_CODENAME=BAKLAVA \
scripts/generate_target.sh
```
