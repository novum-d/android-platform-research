# Android Platform Research（Android 挙動変更調査）

このリポジトリは、Android Platform の Behavior Changes を、顧客や Android アプリ開発者に説明できる形で調査・整理するためのものです。

ソースコード分析そのものは目的ではありません。公式 Behavior Change 文書の内容を検証し、説明するための根拠として AOSP source を使います。

## まず読むもの

初めて見る人は、この順番で読む。

1. この `README.md` でリポジトリ全体の目的と構成を確認する
2. [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md) で共通の読み進め方を確認する
3. 調査対象バージョンの `android<version>/GETTING_STARTED.md` を読む
4. [docs/workflow/INVESTIGATION_PLAYBOOK.md](docs/workflow/INVESTIGATION_PLAYBOOK.md) で調査手順を確認する
5. [docs/workflow/REVIEW_CHECKLIST.md](docs/workflow/REVIEW_CHECKLIST.md) でレポート完成条件を確認する
6. Codex CLI で調査する場合は [docs/workflow/CODEX_CLI_RESEARCH_GUIDE.md](docs/workflow/CODEX_CLI_RESEARCH_GUIDE.md) を確認する

バージョンごとの読み進め方、対象 tag、targetSdkVersion、テンプレート、分類ルールは、各 `android<version>/` 配下に置きます。ルート README には、特定 Android バージョン専用の作業手順を書きません。

## 調査の基本形

調査は必ず公式 Behavior Change 文書から始めます。

```text
Behavior Change Documentation
  -> AOSP 根拠（AOSP Evidence）
  -> 顧客向け調査レポート（Customer-facing Investigation Report）
  -> 1ページ要約（One Page Summary）
  -> 人間の判断（Human Decision）
```

AOSP source は、公式文書の記述を裏取りするために使います。AOSP diff だけを起点に結論を作らないでください。

## リポジトリ構成

ルート直下のファイルは、原則として入口だけにします。

| パス（Path） | 目的（Purpose） |
| --- | --- |
| `README.md` | リポジトリ全体の入口 |
| `AGENTS.md` | Codex / agent 向けの操作指示 |
| `android<version>/` | Android バージョン固有の調査成果物 |
| `docs/` | バージョン非依存の調査手順、記録、知識、メモ |
| `frameworks-base/` | Git 管理しない一時的な AOSP source checkout |
| `scripts/` | ローカル補助スクリプト |

## 置き場所の原則

| 追加するもの | 置き場所 |
| --- | --- |
| バージョン固有の Behavior Change 調査レポート | `android<version>/behavior-changes/` |
| バージョン固有の 1ページ要約 | `android<version>/summaries/` |
| バージョン固有の人間の判断ログ | `android<version>/decisions/` |
| バージョン固有の backlog / roadmap | `android<version>/planning/` |
| バージョン固有の関連概念・調査テーマ | `android<version>/knowledge/` |
| バージョン固有の report / summary template | `android<version>/templates/` |
| バージョン横断の調査ルール | `docs/workflow/` |
| バージョン横断の情報源ポリシー・用語 | `docs/overview/` |
| バージョン横断の未解決質問・仮説 | `docs/knowledge/` |
| 個人的な下書きメモ | `docs/notes/` |

## バージョニング

`docs/` はバージョン非依存の資料だけを置きます。

Android バージョン固有の調査成果物は `android<version>/` に置きます。

```text
android<version>/
  analysis/
  behavior-changes/
  decisions/
  knowledge/
  planning/
  summaries/
  templates/
```

新しい Android バージョンを調査する場合は、既存バージョンの成果物を上書きせず、新しい `android<version>/` を作ります。詳しくは [docs/VERSIONING.md](docs/VERSIONING.md) を参照してください。

## AOSP checkout の扱い（AOSP Checkout）

`frameworks-base/` は一時的な evidence workspace として扱い、Git 管理対象にしません。

調査では local working tree の差分ではなく、必ず AOSP tag 間の明示的な比較を使います。詳しくは [docs/workflow/AOSP_CHECKOUT.md](docs/workflow/AOSP_CHECKOUT.md) を参照してください。

## docs 索引（Docs Index）

| カテゴリ（Category） | 目的（Purpose） | パス（Path） |
| --- | --- | --- |
| Getting Started | 初見向けの共通導線 | [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md) |
| Overview | 目的、情報源ポリシー、タイムライン、用語集 | [docs/overview/](docs/overview/) |
| Workflow | 調査原則、手順、confidence 基準、レビュー観点、anti-patterns | [docs/workflow/](docs/workflow/) |
| Planning | バージョン横断の将来調査候補 | [docs/planning/](docs/planning/) |
| Records | findings index、人間の判断、lessons learned | [docs/records/](docs/records/) |
| Knowledge | バージョン横断の仮説と未解決質問 | [docs/knowledge/](docs/knowledge/) |
| Notes | 個人的なメモ・下書き | [docs/notes/](docs/notes/) |

## 人間が判断すること

Codex や自動化ツールは、根拠収集と分析を支援します。以下は人間が判断します。

- final priority
- final severity
- release readiness
- customer communication priority
