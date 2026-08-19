# はじめに（Getting Started）

このファイルは、初めてこのリポジトリを見る人向けの共通導線です。

特定 Android バージョンの読み進め方は、各 `android<version>/GETTING_STARTED.md` を確認してください。

## 共通の読む順番

1. ルートの `README.md` でリポジトリ全体の目的を確認する
2. Android Platform と Build System のどちらを調査するか選ぶ
3. 目的別の依頼例は `docs/workflow/PROMPT_USE_CASES.md` から選ぶ

## Android Platform 調査

1. 調査対象バージョンの `GETTING_STARTED.md` を読む
2. 対象バージョンの `behavior-changes/README.md` で調査対象一覧と分類を確認する
3. `docs/workflow/INVESTIGATION_PLAYBOOK.md` で Android Behavior Change の調査手順を確認する
4. `docs/workflow/REVIEW_CHECKLIST.md` で完成条件を確認する
5. `docs/workflow/AOSP_CHECKOUT.md` で一時 checkout と tag 比較の扱いを確認する
6. 公式セクション URL から依頼する場合は `docs/workflow/CODEX_CLI_RESEARCH_GUIDE.md` を確認する

## Build System 調査

1. `build-system/README.md` と `build-system/AGENTS.md` を読む
2. `build-system/<area>/README.md` で対象 area の成果物と索引を確認する
3. `.codex/prompts/investigation.md` と `build-system/templates/` で調査手順と出力形式を確認する
4. AGP Release Notes URL から依頼する場合は `build-system/CODEX_CLI_RESEARCH_GUIDE.md` を確認する

## Android Platform の調査対象の選び方

1 回の調査では、Behavior Change セクションを 1 つだけ選びます。

広すぎる例:

```text
Android の変更を全部調べる
```

適切な例:

```text
対象 Android バージョンの Behavior Change セクションを 1 件選び、公式文書を起点に調査する
```

## Android Platform の作業の流れ

```text
公式 Behavior Change 文書を読む
  -> 原文 statement を抜き出す
  -> 関連する AOSP source を確認する
  -> OS update impact と targetSdkVersion impact を分ける
  -> compat framework evidence を確認する
  -> 顧客向け調査レポートを書く
  -> 1ページ要約を書く
  -> 人間が最終判断を記録する
```

## バージョン固有情報の置き場所

| 情報 | 置き場所 |
| --- | --- |
| version / AOSP tag / targetSdkVersion / output rootの正本 | `android<version>/research-scope.json` |
| バージョンスコープの人間向け説明 | `android<version>/README.md` |
| 適用条件分類（applicability classification） | `android<version>/behavior-changes/` |
| レポート / 要約テンプレート（report / summary template） | `android<version>/templates/` |
| バージョン固有 backlog / roadmap | `android<version>/planning/` |

Build System の version diff、summary、migration checklist の置き場所は `build-system/README.md` と各 area の README を正とする。
AGP の version、release channel、purpose、成果物 path、Research / Decision status は `build-system/agp/research-scope.json` を機械可読な正本とする。

scope、索引、リンク、templateを変更した後は、次で構成を検証する。

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
python3 scripts/validate_repository_structure.py
```

新規・更新調査の開始前には、公式 refs と公式文書の公開状態も確認する。

```bash
python3 scripts/validate_repository_structure.py --online
```

## 迷った時

バージョンに依存する内容なら `android<version>/` に置きます。

複数 Android バージョンで使う運用ルール、調査手順、用語、情報源ポリシーなら `docs/` に置きます。
