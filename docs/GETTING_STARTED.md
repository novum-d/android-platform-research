# Getting Started

このファイルは、初めてこのリポジトリを見る人向けの共通導線です。

特定 Android バージョンの読み進め方は、各 `android<version>/GETTING_STARTED.md` を確認してください。

## 読む順番

1. ルートの `README.md` でリポジトリ全体の目的を確認する
2. 調査対象バージョンの `GETTING_STARTED.md` を読む
3. 対象バージョンの `behavior-changes/README.md` で調査対象一覧と分類を確認する
4. `docs/workflow/INVESTIGATION_PLAYBOOK.md` で調査手順を確認する
5. `docs/workflow/REVIEW_CHECKLIST.md` で完成条件を確認する
6. AOSP checkout の扱いを `docs/workflow/AOSP_CHECKOUT.md` で確認する
7. Codex CLI を使う場合は `docs/workflow/CODEX_CLI_RESEARCH_GUIDE.md` を確認する

## 調査対象の選び方

1 回の調査では、Behavior Change セクションを 1 つだけ選びます。

広すぎる例:

```text
Android の変更を全部調べる
```

適切な例:

```text
対象 Android バージョンの Behavior Change セクションを 1 件選び、公式文書を起点に調査する
```

## 作業の流れ

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
| version scope | `android<version>/README.md` |
| AOSP tag pair | `android<version>/README.md` |
| targetSdkVersion focus | `android<version>/README.md` |
| applicability classification | `android<version>/behavior-changes/` |
| report / summary template | `android<version>/templates/` |
| release-specific backlog / roadmap | `android<version>/planning/` |

## 迷った時

バージョンに依存する内容なら `android<version>/` に置きます。

複数 Android バージョンで使う運用ルール、調査手順、用語、情報源ポリシーなら `docs/` に置きます。
