# Build System 調査

このディレクトリでは、Android アプリの Build System 更新に関する調査を管理する。

対象は AGP、Gradle、Kotlin、NDK、CI など。将来的に KSP や Compose Compiler も同じ構成で追加する。

## Goal

Build System 更新時に、このリポジトリだけを見れば以下を判断できる状態を目指す。

- 何が変わるのか
- 何を確認すべきか
- どこまで影響するか
- どのように検証するか
- どの単位で PR を分けるべきか

このディレクトリは単なるメモ置き場ではなく、実際のアップデート作業の判断材料を残す場所として扱う。

設計方針の詳細は [../.codex/prompts/build-system-design.md](../.codex/prompts/build-system-design.md) に残す。

## Scope

初期対象:

- [agp/](agp/) - Android Gradle Plugin
- [gradle/](gradle/) - Gradle
- [kotlin/](kotlin/) - Kotlin
- [ndk/](ndk/) - Android NDK
- [ci/](ci/) - CI / build environment

将来追加候補:

- KSP
- Compose Compiler

将来追加する場合は、原則として次の形にする。

```text
build-system/<area>/
  README.md
  versions/
  summaries/
```

## Policy

### Research Flow

Build System 調査は通常、対象 area の release notes などの entry point から開始し、必要な一次情報をたどる。

Release Notes は入口であり、最終根拠ではない。

```text
Release Notes / Entry Point
  -> 変更点を抽出
  -> 影響がありそうな項目だけ一次情報を深掘り
  -> Compatibility Matrix
  -> Version Diff Investigation
  -> Migration Checklist
  -> Human Decision
```

通常調査では AOSP / tools/base の差分調査を必須にしない。

AOSP / tools/base の差分調査は、以下の場合のみ実施する。

- Release Notes だけでは判断できない
- DSL 変更の根拠確認が必要
- Build 挙動変更の根拠確認が必要
- Release Notes 未記載の変更を調査する必要がある

### Investigation Entry Points

| Area | Entry Point |
| --- | --- |
| Android Behavior Changes | Android Developers の Behavior Changes ページ |
| AGP | AGP Release Notes |
| Gradle | Gradle Release Notes |
| Kotlin | Kotlin What's New |
| NDK | NDK Release Notes |
| CI | CI provider の release notes / runner image documentation |
| KSP | KSP Release Notes |
| Compose Compiler | Compose Compiler / Kotlin compatibility documentation |

### Deep Dive Criteria

すべての変更を毎回深掘りしない。
Release Notes から変更点を抽出し、影響がありそうな項目だけ一次情報を確認する。

深掘り対象:

- Compatibility 変更
- Breaking Change
- Deprecated
- Default 値変更
- DSL 変更
- Task 挙動変更
- Build 速度へ影響する変更
- CI へ影響する変更
- Native / NDK へ影響する変更
- Lint 変更
- release artifact へ影響する変更
- 自分のプロジェクトで利用している API / plugin / task / module に関係する変更

通常は深掘り対象外:

- 単なるバグ修正
- 誤字修正
- 内部リファクタリング
- 自分のプロジェクトへ影響しない変更
- test-only / documentation-only の変更

対象外にした変更も、判断理由を短く残す。

### Entry Point / References / Evidence

`Entry Point` と `References` は分けて記録する。

- Entry Point: 調査を開始した公式文書
- References: 調査中に参照したすべての資料

事実には必ず根拠を紐付ける。

| Fact | Evidence | Confidence |
| --- | --- | --- |
|  |  | High / Medium / Low |

References は以下に分けて整理する。

- Official Documentation
- Source Code
- Issue
- Validation

### Change Isolation Policy

以下は原則として同じ PR に混ぜない。

- AGP 更新
- Gradle 更新
- Kotlin 更新
- compileSdk 更新
- targetSdkVersion 更新
- minSdk 更新
- NDK 更新
- 依存ライブラリ更新

目的は、変更ごとの影響範囲を最小化すること。

互換性要件により同時更新が必要な場合は、以下を必ず記録する。

- 同時更新が必要な理由
- 根拠となる一次情報
- 影響ファイル
- 検証コマンド
- rollback plan

### Version Update Policy

- 必須でない更新は混ぜない。
- `compileSdk` 更新は Build 互換性として扱う。
- `targetSdkVersion` 更新は Behavior Changes 対応として扱う。
- `minSdk` 更新は別判断として扱う。
- ライブラリ依存更新は Build System 更新と分離する。ただし互換性上必須の場合は例外とし、理由を記録する。

## Common Sections

Build System 調査の成果物は、詳細調査、1ページサマリ、移行チェックリストに分ける。

| Artifact | Template | Output |
| --- | --- | --- |
| 詳細調査 | `templates/version-diff-template.md` | `build-system/<area>/versions/` |
| 1ページサマリ | `templates/one-page-summary-template.md` | `build-system/<area>/summaries/` |
| 移行チェックリスト | `templates/migration-checklist-template.md` | 実作業 PR / issue に紐付く場所 |

詳細調査ファイルは最低限以下を持つ。

- Summary
- Investigation Entry Point
- Change Inventory
- Evidence
- References
- Minimum Required Versions
- Compatibility Matrix
- Breaking Changes
- Risk Level
- Affected Modules
- Detection Method
- Verification Commands
- Test Scope
- Rollback Plan
- Decision Log
- Completion Criteria
- Follow-up Tasks

推奨テンプレート:

- [../.codex/prompts/investigation.md](../.codex/prompts/investigation.md) - 共通の調査手順プロンプト
- [templates/version-diff-template.md](templates/version-diff-template.md)
- [templates/one-page-summary-template.md](templates/one-page-summary-template.md)
- [templates/migration-checklist-template.md](templates/migration-checklist-template.md)

共通プロンプトは「どう調査するか」を定義する。
Build System の Markdown テンプレートは「調査結果をどこにどう残すか」を定義する。

1ページサマリは、詳細調査を読まなくても意思決定に必要な概要、主要リスク、検証方針、PR 分割方針が分かる状態にする。
詳細根拠は詳細調査へ委譲し、1ページサマリには Evidence / References への参照を残す。

## Android Platform 調査との関係

Android Platform と Build System で、完全に同一テンプレートを使うことは推奨しない。
共通の思想は揃えるが、必要な traceability が異なるため。

| Area | 主な traceability |
| --- | --- |
| Android Platform | Behavior Change statement、AOSP evidence、applicability、OS update impact、targetSdkVersion impact |
| Build System | compatibility、minimum / recommended versions、affected modules、verification commands、rollback plan |

そのため、構成と completion criteria の考え方は揃えつつ、テンプレートは別管理にする。

## Minimum Required Versions

`Minimum` と `Recommended` は必ず分ける。

対象に応じて以下を整理する。

| Item | Minimum | Recommended | Source | Notes |
| --- | --- | --- | --- | --- |
| AGP |  |  |  |  |
| Gradle |  |  |  |  |
| JDK |  |  |  |  |
| Kotlin |  |  |  |  |
| compileSdk |  |  |  |  |
| targetSdk |  |  |  |  |
| minSdk |  |  |  |  |
| NDK |  |  |  |  |

## Compatibility Matrix

Build System 間の互換性を表で整理する。

| AGP | Gradle | JDK | Kotlin | NDK | Notes |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |  |

## Breaking Changes Classification

変更は以下で分類する。

| Classification | Meaning |
| --- | --- |
| Must Fix | 更新前または同時に修正しないと build / test / release が壊れる可能性が高い |
| Should Fix | 更新後の安定性、将来互換性、警告削減のため対応した方がよい |
| Watch | 直ちに対応不要だが、特定条件で影響する可能性がある |
| No Action | 対象プロジェクトへの影響なし、または確認のみで足りる |

## Risk Level

| Risk | Meaning |
| --- | --- |
| High | build failure、release artifact 変更、runtime 影響、CI 全体停止の可能性がある |
| Medium | 一部 module、warning、test、CI job、developer environment に影響する可能性がある |
| Low | 影響範囲が限定的、または確認だけで完了できる可能性が高い |

Risk は最終判断ではない。人間が判断するための材料として記録する。

## Detection Method

各変更について、影響があるかを確認する方法を記載する。

確認例:

- Gradle version
- JDK version
- `settings.gradle` / `settings.gradle.kts`
- root `build.gradle` / `build.gradle.kts`
- module `build.gradle` / `build.gradle.kts`
- `gradle/libs.versions.toml`
- `gradle-wrapper.properties`
- `.so` の有無
- `CMakeLists.txt` / `Android.mk` / `Application.mk`
- CI 設定
- release build 設定

## Verification Commands

確認用コマンドは、対象プロジェクトに合わせて明記する。

例:

```bash
./gradlew assembleDebug
./gradlew test
./gradlew lint
./gradlew dependencies
```

必要に応じて以下も追加する。

```bash
./gradlew assembleRelease
./gradlew connectedDebugAndroidTest
./gradlew :app:dependencies
./gradlew --scan
```

## Test Scope

検証範囲は以下から必要なものを選ぶ。

- Build
- Unit Test
- Lint
- Instrumentation Test
- Release Build
- Smoke Test

## Investigation Exit Criteria

共通の調査完了条件は [../.codex/prompts/investigation.md](../.codex/prompts/investigation.md) に従う。

最低限、以下を説明できる状態にする。

- 変更内容
- 影響範囲
- 必要な対応
- 検証方法
- 一次情報への参照
- 未調査事項

## Rollback Plan

最低限、以下を記載する。

- 戻すバージョン
- 戻すファイル
- 確認コマンド
- 副作用

## Affected Modules

どの module に影響するかを明記する。

| Module | Impact | Evidence | Required Action |
| --- | --- | --- | --- |
|  |  |  |  |

## Decision Log

判断の理由を残す。

ただし、最終的な priority、severity、release readiness、customer communication priority は人間が判断する。

| Date | Decision | Reason | Owner |
| --- | --- | --- | --- |
|  |  |  |  |

## Completion Criteria

調査完了条件:

- Release Notes 確認済み
- Entry Point Release Notes 確認済み
- Change Inventory 作成済み
- Deep Dive 要否を判定済み
- Entry Point と References を分離済み
- 事実に Evidence と Confidence を紐付け済み
- Compatibility 確認済み
- Minimum と Recommended を分離済み
- Breaking Changes を分類済み
- Change Isolation Policy への影響を確認済み
- 影響範囲記載済み
- 検証コマンド記載済み
- rollback plan 記載済み
- follow-up task 記載済み
- PR 分割方針記載済み
- 1ページサマリ作成済み
- Human Decision placeholder 記載済み

## Follow-up Tasks

調査後の実作業を分離して書く。

例:

- AGP 更新 PR
- Gradle wrapper 更新 PR
- compileSdk 更新 Issue
- targetSdkVersion 更新 Issue
- NDK 更新 PR
- CI image 更新 PR

## Source Policy

一次情報を優先する。

優先順位:

1. Official Documentation
2. Release Notes
3. Compatibility Matrix
4. Issue Tracker
5. 実機・実プロジェクト検証
6. Blog

Blog や個人記事は、一次情報の補助としてのみ使う。

Release Notes は調査の entry point として優先する。
ただし、Release Notes の要約だけを根拠にせず、必要に応じて Compatibility Matrix、API Reference、Migration Guide、Issue Tracker などの一次情報をたどる。

## Source Diff Policy

通常調査では以下を利用する。

- Official Documentation
- Release Notes
- Compatibility Matrix
- Issue Tracker
- 実プロジェクト検証

AOSP / tools/base の差分調査は、以下のような必要がある場合のみ実施する。

- Release Notes だけでは判断できない
- DSL 変更の根拠確認が必要
- Build 挙動変更の根拠確認が必要
- Release Notes 未記載の変更を調査する必要がある

通常の Build System 調査では、AOSP / tools/base 差分は必須ではない。
