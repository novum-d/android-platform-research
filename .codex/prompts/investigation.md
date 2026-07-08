# Investigation

以下のドキュメントを起点として調査を行ってください。

このプロンプトは、Android Behavior Changes、AGP、Gradle、Kotlin、NDK、CI、KSP、Compose Compiler などの調査で共通利用する調査手順テンプレートです。

## Entry Point

調査対象に応じて、以下の entry point から開始してください。

| Area | Entry Point | 必要に応じて追加で確認する情報 |
| --- | --- | --- |
| Android Behavior Changes | Android Developers の Behavior Changes ページ | Compat Framework、AOSP、API Reference、CTS |
| AGP | AGP Release Notes | Compatibility Matrix、API Reference、Migration Guide、tools/base |
| Gradle | Gradle Release Notes | User Guide、DSL Reference、Upgrade Guide |
| Kotlin | Kotlin What's New | Compatibility Guide、Compiler options、YouTrack、API Reference |
| NDK | NDK Release Notes | NDK Guides、CMake documentation、Issue Tracker |
| CI | CI provider release notes / runner image documentation | runner image changelog、setup action docs、cache docs |
| KSP | KSP Release Notes | Kotlin compatibility、API Reference、Issue Tracker |
| Compose Compiler | Compose Compiler / Kotlin compatibility documentation | Kotlin compatibility map、Release Notes、Issue Tracker |

Release Notes は入口です。
Release Notes だけで調査を完了しないでください。

Entry Point と References は分けて記録してください。

- Entry Point: 調査を開始した公式文書
- References: 調査中に参照したすべての資料

## Goal

単なる要約ではなく、以下を整理してください。

- 何が変わったのか
- なぜ変わったのか
- 誰が影響を受けるのか
- 何を確認する必要があるのか
- どのように検証するか
- どのようなアップデート戦略を取るべきか

## Investigation Workflow

以下の順序で調査してください。

1. 起点ドキュメントを読む
2. 変更点を一覧化する
3. 変更点ごとに影響範囲を分類する
4. 必要な項目のみ一次情報を深掘りする
5. 実装レベルで何が変わるか調査する
6. 検証方法を整理する
7. PR 戦略を考える

## Deep Dive Policy

以下の場合のみ追加調査してください。

- Breaking Change
- Deprecated
- Compatibility 変更
- Default 値変更
- DSL 変更
- API 変更
- Build 挙動変更
- Runtime 挙動変更
- Performance 影響
- CI 影響

追加調査しない変更についても、対象外にした理由を短く記録してください。

## Primary Sources

優先順位:

1. Official Documentation
2. Release Notes
3. Migration Guide
4. Compatibility Matrix
5. Issue Tracker
6. Source Code
7. 実機検証

Source Code の調査は必要な場合のみ実施してください。

## References

調査中に参照した公式ドキュメントはすべて記録してください。

最低限、以下を調査レポートへ記載してください。

- Entry Point
- Official References
- Additional References

References は以下の分類で整理してください。

### Official Documentation

- Release Notes
- Compatibility Matrix
- Migration Guide
- API Reference
- User Guide / DSL Reference

### Source Code

- AOSP
- tools/base
- Gradle source
- Kotlin source

### Issue

- Google Issue Tracker
- Gradle issue tracker
- Kotlin YouTrack
- GitHub issues

### Validation

- Sample Project
- Production Project
- CI run
- 実機検証

## Evidence

事実には必ず根拠となる公式文書を紐付けてください。

Evidence は以下の単位で整理してください。

| Fact | Evidence | Confidence |
| --- | --- | --- |
|  |  | High / Medium / Low |

記入例:

| Fact | Evidence | Confidence |
| --- | --- | --- |
| AGP 9.0 requires Gradle 9.1. | AGP Release Notes、Compatibility Matrix | High |

## Output

調査結果は、対象に応じて以下のテンプレートへまとめてください。

| Area | Output Template |
| --- | --- |
| Android Behavior Changes | `android<version>/templates/customer-report-template.md` |
| Android one-page summary | `android<version>/templates/one-page-summary-template.md` |
| Android implementation examples | Use the version-specific implementation examples template when present, for example `android16/templates/implementation-examples-template.md` |
| Build System version diff | `build-system/templates/version-diff-template.md` |
| Build System one-page summary | `build-system/templates/one-page-summary-template.md` |
| Build System migration checklist | `build-system/templates/migration-checklist-template.md` |

Behavior Change の対応候補に複数のコード例、framework 別実装例、temporary opt-out の具体例を載せる場合は、primary report へ長いコードを直接集約しない。
version directory に implementation examples template がある場合は、そのテンプレートを使って実装例ファイルを作成し、primary report の「対応候補」には代表的な短い例と実装例ファイルへのリンクを置く。

## Investigation Exit Criteria

以下を満たしたら調査完了としてください。

- 変更内容を説明できる
- 影響範囲を説明できる
- 必要な対応を説明できる
- 検証方法を説明できる
- 一次情報へ辿れる
- Entry Point と References を分けて記録した
- 事実に Evidence と Confidence を紐付けた
- 必要な場合は 1ページサマリを作成した
- 未調査事項があれば明記した

## Required Reporting Rules

この調査の目的はリリースノートの要約ではありません。

アップデート時の意思決定に必要な情報を整理し、将来同じ調査を別バージョンでも再現できる品質でまとめてください。

「事実」と「推測」は必ず分けて記載してください。
