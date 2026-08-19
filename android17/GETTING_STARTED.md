# Android 17 はじめに（Getting Started）

このファイルは、Android 17 調査を進める時に読む場所をまとめる。

## 読む順番

1. [README.md](README.md) で Android 17 の version scope を確認する
2. [behavior-changes/README.md](behavior-changes/README.md) で Behavior Change 一覧と分類を見る
3. [behavior-changes/APPLICABILITY_CLASSIFICATION.md](behavior-changes/APPLICABILITY_CLASSIFICATION.md) で適用条件分類を確認する
4. [templates/customer-report-template.md](templates/customer-report-template.md) で調査レポートの書式を確認する
5. [templates/one-page-summary-template.md](templates/one-page-summary-template.md) で 1ページ要約の書式を確認する
6. Kotlin、Manifest、XML、native、testの対応例が必要な場合は [Android 17対応例テンプレート](templates/implementation-examples-template.md) を使う
7. Android 16 / 17 間の挙動差を比較する場合は [Android OS バージョン間挙動比較テンプレート](../docs/templates/android-os-version-behavior-comparison-template.md) を使う
8. 調査済み項目の差は [Android 16 → 17 挙動比較一覧](behavior-changes/version-comparisons/README.md) で確認する
9. 調査済み項目の実装・設定例は [Android 17対応例一覧](behavior-changes/implementation-examples/README.md) で確認する
10. [summaries/README.md](summaries/README.md) で要約一覧を確認する
11. [decisions/DECISION_LOG.md](decisions/DECISION_LOG.md) で人間の判断ログを確認する

## 公式ドキュメント

主要ドキュメント（Primary documentation）:

- All apps: https://developer.android.com/about/versions/17/behavior-changes-all
- Apps targeting Android 17+: https://developer.android.com/about/versions/17/behavior-changes-17
- Android 17 overview: https://developer.android.com/about/versions/17

注意:
- Android 17 の公式 Behavior Change 文書と `android-17.0.0_r1` release tag は公開済み。
- 公式一覧は更新されるため、比較一覧の確認日と未収録項目を併記する。
- AOSP evidence should use explicit tag comparisons from `android-16.0.0_r4` to `android-17.0.0_r1`.

## 計画とバックログ

| 確認したいこと（Need） | リンク（Link） |
| --- | --- |
| Android 17 planning | [planning/ROADMAP.md](planning/ROADMAP.md) |
| Android 17 backlog | [planning/RESEARCH_BACKLOG.md](planning/RESEARCH_BACKLOG.md) |

## Codex CLI

Codex CLI で Android 17 調査を実行する場合は、共通手順書を読んだ上で、このディレクトリの version scope と template path を使う。

通常の入力は公式 Behavior Change セクション URL 1件だけとする。Codex が公式セクションを解析し、version scope、category、output path を補完した中間プロンプトを `tmp/research-prompts/` に生成して、同じセッション内で調査を実行する。

```text
../docs/workflow/CODEX_CLI_RESEARCH_GUIDE.md
```

## analysis 生成（Analysis Generation）

Android 17 の AOSP tag が利用可能になったら、analysis files を生成する。

```bash
VERSION_DIR=android17 \
OLD_TAG=android-16.0.0_r4 \
NEW_TAG=android-17.0.0_r1 \
TARGET_CODENAME=CINNAMON_BUN \
scripts/generate_target.sh
```
