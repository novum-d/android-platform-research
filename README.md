# Android Platform Research（Android / Build System アップデート調査）

このリポジトリは、Android Platform の Behavior Changes と Build System の更新影響を、顧客や Android アプリ開発者に説明できる形で調査・整理するためのものです。

ソースコード分析そのものは目的ではありません。Android Platform 調査では公式 Behavior Change 文書の内容を検証し、説明するための根拠として AOSP source を使います。Build System 調査では、公式ドキュメント、Release Notes、互換性情報、実プロジェクト検証を主な根拠として使います。

## まず読むもの

初めて見る人は、この順番で読む。

1. この `README.md` でリポジトリ全体の目的と構成を確認する
2. [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md) で共通の読み進め方を確認する
3. Android Platform 調査では、調査対象バージョンの `android<version>/GETTING_STARTED.md`、[Android調査プレイブック](docs/workflow/INVESTIGATION_PLAYBOOK.md)、[Androidレビュー項目](docs/workflow/REVIEW_CHECKLIST.md) を読む
4. Build System 調査では、[build-system/README.md](build-system/README.md) と対象 area の README を読む
5. Codex CLI で Android Behavior Change を調査する場合は、公式セクション URL だけを入力し、[Android URL-only workflow](docs/workflow/CODEX_CLI_RESEARCH_GUIDE.md) に従う
6. Codex CLI で AGP 差分を調査する場合は、公式 AGP Release Notes URL だけを入力し、[Build System URL-only workflow](build-system/CODEX_CLI_RESEARCH_GUIDE.md) に従う
7. 目的別の依頼例は [Codex プロンプト・ユースケース一覧](docs/workflow/PROMPT_USE_CASES.md) から選ぶ

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

レポート、1ページ要約、`Pending Human Decision`が揃った状態をResearch Complete、
その後にリポジトリ所有者が判断を記録した状態をDecision Completeと呼びます。
調査完了と人間の判断完了を混同しません。

Build System 調査は、対象 area の Release Notes などの entry point から始め、必要な一次情報をたどります。
Release Notes は入口であり、最終根拠ではありません。

```text
Release Notes / Entry Point
  -> 変更点を抽出
  -> 影響がありそうな項目だけ一次情報を深掘り
  -> Compatibility Matrix
  -> Version Diff Investigation
  -> Migration Checklist
  -> Human Decision
```

通常の Build System 調査では、AOSP / tools/base の差分確認は必須ではありません。Release Notes だけでは判断できない場合、DSL 変更や Build 挙動変更の根拠を確認する場合、または未記載の変更を調査する場合に限って使います。

## リポジトリ構成

ルート直下のファイルは、原則として入口だけにします。

| パス（Path） | 目的（Purpose） |
| --- | --- |
| `README.md` | リポジトリ全体の入口 |
| `AGENTS.md` | Codex / agent 向けの操作指示 |
| `.codex/prompts/` | 再利用する調査プロンプトと設計プロンプト |
| `android<version>/` | Android バージョン固有の調査成果物 |
| `build-system/` | AGP、Gradle、Kotlin、NDK、CI などの Build System 更新調査 |
| `demos/` | Behavior Change の説明・再現補助用デモ。調査根拠そのものとしては扱わない |
| `docs/` | バージョン非依存の調査手順、記録、知識、メモ |
| `frameworks-base/` / `tmp/aosp-checkouts/` | Git管理しない一時的なAOSP source checkout |
| `scripts/` | analysis生成・構成検証などのローカル補助スクリプト |

## 置き場所の原則

| 追加するもの | 置き場所 |
| --- | --- |
| バージョン固有の Behavior Change 調査レポート | `android<version>/behavior-changes/` |
| 特定アプリ向けのバージョン横断影響レポート | `android<version>/app-reports/` |
| バージョン固有の 1ページ要約 | `android<version>/summaries/` |
| バージョン固有の人間の判断ログ | `android<version>/decisions/` |
| バージョン固有の backlog / roadmap | `android<version>/planning/` |
| バージョン固有の関連概念・調査テーマ | `android<version>/knowledge/` |
| バージョン固有の report / summary template | `android<version>/templates/` |
| バージョン固有の機械可読scope | `android<version>/research-scope.json` |
| Build System 更新調査 | `build-system/<area>/versions/` |
| Build System 1ページ要約 | `build-system/<area>/summaries/` |
| Build System の再利用可能な移行チェックリスト | `build-system/<area>/checklists/` |
| Build System 共通テンプレート | `build-system/templates/` |
| OS / targetSdkVersion 別の移行デモ | `demos/android-migration-lab/` |
| 共通調査プロンプト | `.codex/prompts/investigation.md` |
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
  app-reports/
  behavior-changes/
  decisions/
  knowledge/
  planning/
  summaries/
  templates/
```

新しい Android バージョンを調査する場合は、既存バージョンの成果物を上書きせず、新しい `android<version>/` を作ります。詳しくは [docs/VERSIONING.md](docs/VERSIONING.md) を参照してください。

Build System の詳細調査は、対象領域ごとに `build-system/<area>/versions/` に置きます。判断用の 1ページ要約は `build-system/<area>/summaries/` に置きます。AGP、Gradle、Kotlin、NDK、CI は初期対象です。将来 KSP や Compose Compiler を追加する場合も同じ構成で `build-system/ksp/` や `build-system/compose-compiler/` を追加します。

## AOSP checkout の扱い（AOSP Checkout）

`frameworks-base/`と`tmp/aosp-checkouts/<project>`は一時的なevidence workspaceとして扱い、Git管理対象にしません。

調査ではlocal working treeの差分ではなく、根拠に使うAOSP projectごとにtagとcommit hashを確認し、明示的なtag間比較を使います。詳しくは[docs/workflow/AOSP_CHECKOUT.md](docs/workflow/AOSP_CHECKOUT.md)を参照してください。

構成やversion scopeを変更した後は、次を実行します。

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
python3 scripts/validate_repository_structure.py
```

新規・更新調査を開始する前は、ネットワークを使う freshness check も実行します。通常の CI は外部状態に依存しない上の検証だけを実行します。

```bash
python3 scripts/validate_repository_structure.py --online
```

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
| Build System | AGP、Gradle、Kotlin、NDK、CI の更新調査 | [build-system/](build-system/) |

## 人間が判断すること

Codex や自動化ツールは、根拠収集と分析を支援します。以下は人間が判断します。

- final priority
- final severity
- release readiness
- customer communication priority
