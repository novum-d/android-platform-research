# AGP 調査

Android Gradle Plugin (AGP) の version update、DSL 変更、variant API、lint、R8、resource processing、namespace、build feature、release artifact への影響を調査する。

## Scope

- AGP version update
- AGP と Gradle / JDK / Kotlin / compileSdk の互換性
- Android Gradle Plugin DSL 変更
- Variant API 変更
- Lint / R8 / resource processing の挙動変更
- AGP 更新に伴う CI 影響

## Out of Scope

- `targetSdkVersion` 更新そのもの
- `minSdk` 更新そのもの
- 任意の依存ライブラリ更新

これらは AGP 更新と同じ PR に混ぜない。ただし AGP 互換性上必須の場合は、根拠を記録する。

## Directory

| Directory | Purpose |
| --- | --- |
| [versions/](versions/) | AGP 更新の詳細調査 |
| [summaries/](summaries/) | AGP 更新の 1ページサマリ |
| [checklists/](checklists/) | 実プロジェクトへの移行チェックリスト |

## Current Research

| 種別 | 対象 | 資料 |
| --- | --- | --- |
| 詳細調査 | AGP 8.7 系 → 9.3.0 stable | [差分調査](versions/agp-8.7-to-9.3.md) |
| 1ページサマリ | AGP 8.7 系 → 9.3.0 stable | [サマリ](summaries/agp-8.7-to-9.3-summary.md) |
| 移行手順 | AGP 8.7 系 → 9.3.0 stable | [チェックリスト](checklists/agp-8.7-to-9.3-migration-checklist.md) |
| Preview watch | AGP 9.4.0-alpha04 | [監視資料](versions/agp-9.4-preview-watch.md) |

最新版の扱いは調査日を基準とする。stable と preview を分離し、preview を production の推奨移行先として扱わない。

## URL-only research

通常は公式 AGP Release Notes URL 1件だけを Codex CLI へ入力する。詳細な解析・補完・中間プロンプト生成・実行規則は [../CODEX_CLI_RESEARCH_GUIDE.md](../CODEX_CLI_RESEARCH_GUIDE.md) に従う。

比較元の補完順序:

1. ユーザーが同じ依頼で明示した From version
2. 同じ target version を扱う既存の詳細調査に記録された From version
3. requested target より低い、完了済み stable 調査の最新 To version

この順序で比較元が1つに決まらない場合だけ From version を確認する。local machine、demo project、preview watch の version を暗黙の比較元にしない。

stable version diff の標準出力:

```text
build-system/agp/versions/agp-<from>-to-<to>.md
build-system/agp/summaries/agp-<from>-to-<to>-summary.md
build-system/agp/checklists/agp-<from>-to-<to>-migration-checklist.md
```

中間プロンプト:

```text
tmp/research-prompts/build-system/agp/agp-<from>-to-<to>.md
```

既存の同一 target 調査がある場合は、その調査で採用済みの path を再利用する。別調査の path と衝突する場合は上書きしない。preview URL は stable migration target と混ぜず、既存の `preview-watch` convention を使う。
