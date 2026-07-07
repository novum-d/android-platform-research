# Build System Research Design

この文書は、`android-platform-research` に Build System 調査基盤を追加・保守するための設計書兼プロンプト資産です。

このリポジトリの既存思想を維持しながら、Android Platform の Behavior Changes 調査だけでなく、AGP、Gradle、Kotlin、NDK、CI などの Build System 更新調査も、実際のアップデート判断に使える形で管理します。

## Repository Purpose

このリポジトリは単なるメモ置き場ではありません。

目的は、Android や Build System をアップデートするときに、このリポジトリだけを見れば以下を判断できる状態を作ることです。

- 何が変わるのか
- 何を確認すべきか
- どこまで影響するか
- どのように検証するか
- どの単位で PR を分けるべきか
- どの判断が人間に残されているか

Android Platform 側では Behavior Change section を調査単位とします。
Build System 側では tool version update または migration topic を調査単位とします。

## Design Principles

- 調査結果は顧客、Android アプリ開発者、技術ステークホルダーが読める形で残す。
- Human-facing reports、summaries、checklists、explanations は日本語で書く。
- Codex-facing instructions、headings、checklist item names は英語でもよい。
- Build System 調査は Official Documentation、Release Notes、Compatibility Matrix、実プロジェクト検証から始める。
- Release Notes は最終根拠ではなく、一次情報をたどるための entry point として扱う。
- AOSP / tools/base の差分調査は通常必須にしない。
- Source diff は、一次情報だけでは判断できない場合に限定して使う。
- 変更はできる限り小さな単位で管理する。
- AGP、Gradle、Kotlin、compileSdk、targetSdkVersion、minSdk、NDK、依存ライブラリ更新は原則として同じ PR に混ぜない。
- `compileSdk` 更新は Build 互換性として扱う。
- `targetSdkVersion` 更新は Android Behavior Changes 対応として扱う。
- `minSdk` 更新は別の product / compatibility 判断として扱う。
- Agent は evidence と analysis を提供し、final priority、final severity、release readiness、customer communication priority は人間が判断する。

## Scope

初期対象:

- Android Gradle Plugin (AGP)
- Gradle
- Kotlin
- NDK
- CI

将来追加候補:

- KSP
- Compose Compiler

将来対象を追加する場合は、既存構成に合わせて `build-system/<area>/README.md`、`build-system/<area>/versions/`、`build-system/<area>/summaries/` を追加します。

## Directory Structure

基本構成:

```text
build-system/
  README.md
  AGENTS.md

  templates/
    version-diff-template.md
    one-page-summary-template.md
    migration-checklist-template.md

  agp/
    README.md
    versions/
      README.md
    summaries/
      README.md

  gradle/
    README.md
    versions/
      README.md
    summaries/
      README.md

  kotlin/
    README.md
    versions/
      README.md
    summaries/
      README.md

  ndk/
    README.md
    versions/
      README.md
    summaries/
      README.md

  ci/
    README.md
    summaries/
      README.md
```

将来拡張例:

```text
build-system/
  ksp/
    README.md
    versions/
      README.md
    summaries/
      README.md

  compose-compiler/
    README.md
    versions/
      README.md
    summaries/
      README.md
```

## Build System README Policy

`build-system/README.md` は Build System 調査の入口です。

最低限、以下を整理します。

- Goal
- Scope
- Research Flow
- Change Isolation Policy
- Version Update Policy
- Common Sections
- Investigation Entry Point
- Change Inventory
- Evidence
- References
- Minimum Required Versions
- Compatibility Matrix
- Breaking Changes Classification
- Risk Level
- Detection Method
- Verification Commands
- Test Scope
- Rollback Plan
- Affected Modules
- Decision Log
- Completion Criteria
- Follow-up Tasks
- Source Policy
- Source Diff Policy
- Deep Dive Criteria

`build-system/README.md` には具体的な AGP / Gradle / Kotlin version 固有の判断を書きません。
version 固有の調査結果は `build-system/<area>/versions/` に置きます。
判断用の 1ページサマリは `build-system/<area>/summaries/` に置きます。

## Investigation Entry Points

このリポジトリでは、調査テーマごとの入口を明確にします。

| Area | Entry Point |
| --- | --- |
| Android Behavior Changes | Android Developers の Behavior Changes ページ |
| AGP | AGP Release Notes |
| Gradle | Gradle Release Notes |
| Kotlin | Kotlin What's New |
| NDK | NDK Release Notes |
| CI | 利用している CI provider の release notes / runner image documentation |
| KSP | KSP Release Notes |
| Compose Compiler | Compose Compiler / Kotlin compatibility documentation |

Release Notes は入口です。
Release Notes だけで調査を完了しません。

Release Notes から変更点を抽出し、影響がありそうな項目だけ一次情報へ深掘りします。

Entry Point と References は分けて記録します。

- Entry Point: 調査を開始した公式文書
- References: 調査中に参照したすべての資料

## Investigation Workflow

Build System 調査は以下の順序で行います。

1. 対象 area の entry point を読む
2. 変更点を一覧化する
3. 各変更について影響の有無を判定する
4. 必要なものだけ一次情報を深掘りする
5. 必要な場合のみ AOSP / tools/base の差分を確認する
6. 調査結果をテンプレートへまとめる
7. 検証方法と PR 分割方針まで記載する

AGP の例:

```text
AGP Release Notes
  -> 変更点を抽出
  -> 影響がありそうな項目だけ深掘り
     -> Compatibility Matrix
     -> API Reference
     -> Migration Guide
     -> Issue Tracker
     -> tools/base（必要時のみ）
  -> Facts を整理
  -> 自分のプロジェクトへの影響を判断
  -> 検証方法を作成
  -> PR 戦略まで決める
```

## Deep Dive Criteria

すべての変更を毎回深掘りしません。
調査コストを制御するため、深掘り対象と対象外を分けます。

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

対象外にした変更も、判断理由を短く残します。

## Evidence Model

事実には必ず根拠となる公式文書を紐付けます。

Evidence は以下の単位で整理します。

| Fact | Evidence | Confidence |
| --- | --- | --- |
|  |  | High / Medium / Low |

この形式により、なぜその結論に至ったのかを第三者がたどれるようにします。

## References Model

References は、調査中に参照したすべての資料を記録する場所です。

最低限、以下に分けます。

- Entry Point
- Official References
- Additional References

推奨分類:

- Official Documentation
- Source Code
- Issue
- Validation

## Common Templates

Build System 全体で再利用するテンプレート:

- `build-system/templates/version-diff-template.md`
- `build-system/templates/one-page-summary-template.md`
- `build-system/templates/migration-checklist-template.md`

調査手順そのものは、共通プロンプトとして `.codex/prompts/investigation.md` に置きます。
Build System 固有のテンプレートは「調査結果をどこにどう残すか」を定義し、共通プロンプトは「どう調査するか」を定義します。

`version-diff-template.md` は、version update や release note review の調査結果を残すために使います。

`one-page-summary-template.md` は、詳細調査を読まなくても意思決定に必要な概要、主要リスク、検証方針、PR 分割方針が分かるようにするために使います。
詳細根拠は詳細調査へ委譲し、1ページサマリには Evidence / References への参照を残します。

`migration-checklist-template.md` は、実際の更新作業で確認すべき pre-check、file changes、verification、rollback を管理するために使います。

Android Platform と Build System で、完全に同一テンプレートを使うことは推奨しません。
共通の思想は揃えますが、必要な traceability が異なるためです。

- Android Platform: Behavior Change statement、AOSP evidence、applicability、OS update impact、targetSdkVersion impact が中心
- Build System: compatibility、minimum / recommended versions、affected modules、verification commands、rollback plan が中心

## Minimum Required Versions

必ず `Minimum` と `Recommended` を分けます。

対象に応じて以下を整理します。

| Item | Current | Minimum | Recommended | Source | Notes |
| --- | --- | --- | --- | --- | --- |
| AGP |  |  |  |  |  |
| Gradle |  |  |  |  |  |
| JDK |  |  |  |  |  |
| Kotlin |  |  |  |  |  |
| compileSdk |  |  |  |  |  |
| targetSdk |  |  |  |  |  |
| minSdk |  |  |  |  |  |
| NDK |  |  |  |  |  |

`Minimum` は動作や互換性のために必要な下限です。
`Recommended` は実運用で推奨する組み合わせです。

両者を混ぜると、必須対応と任意改善が混在して PR 分離が難しくなるため、必ず分けます。

## Compatibility Matrix

Build System 間の互換性を表で整理します。

| AGP | Gradle | JDK | Kotlin | NDK | Status | Notes |
| --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  | Supported / Unsupported / Unknown |  |

互換性判断では、公式 documentation、release notes、compatibility matrix を優先します。

## Breaking Changes

変更は以下で分類します。

| Classification | Meaning |
| --- | --- |
| Must Fix | 更新前または同時に修正しないと build / test / release が壊れる可能性が高い |
| Should Fix | 更新後の安定性、将来互換性、警告削減のため対応した方がよい |
| Watch | 直ちに対応不要だが、特定条件で影響する可能性がある |
| No Action | 対象プロジェクトへの影響なし、または確認のみで足りる |

分類は人間の最終 priority ではありません。
調査上の影響整理として使います。

## Change Isolation Policy

以下は原則として同じ PR に混ぜません。

- AGP 更新
- Gradle 更新
- Kotlin 更新
- compileSdk 更新
- targetSdkVersion 更新
- minSdk 更新
- NDK 更新
- 依存ライブラリ更新
- CI 更新

目的は、変更ごとの影響範囲を最小化することです。

互換性上、同時更新が必要な場合は例外として扱えます。
その場合は以下を必ず記録します。

- 同時更新が必要な理由
- 根拠となる一次情報
- 影響ファイル
- 検証コマンド
- rollback plan

## Version Update Policy

- 必須でない更新は混ぜない。
- `compileSdk` 更新は Build 互換性として扱う。
- `targetSdkVersion` 更新は Behavior Changes 対応として扱う。
- `minSdk` 更新は別判断として扱う。
- 依存ライブラリ更新は Build System 更新と分離する。
- ただし互換性上必須の場合は例外とし、理由を記録する。

## Detection Method

各変更について「影響があるか」をどう確認するかを記載します。

確認対象例:

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

確認用コマンドを対象プロジェクトに合わせて整理します。

基本例:

```bash
./gradlew assembleDebug
./gradlew test
./gradlew lint
./gradlew dependencies
```

追加例:

```bash
./gradlew assembleRelease
./gradlew connectedDebugAndroidTest
./gradlew :app:dependencies
./gradlew --scan
```

## Test Scope

検証範囲は以下から必要なものを選びます。

- Build
- Unit Test
- Lint
- Instrumentation Test
- Release Build
- Smoke Test

対象外にする test scope がある場合は、理由を記録します。

## Rollback Plan

最低限、以下を記載します。

- 戻すバージョン
- 戻すファイル
- 確認コマンド
- 副作用

rollback plan は、更新作業の安全装置として必須です。

## Affected Modules

どの module に影響するかを明記します。

| Module | Impact | Evidence | Required Action |
| --- | --- | --- | --- |
|  |  |  |  |

module が不明な場合は `Unknown` とし、不明な理由と次に確認することを記録します。

## Risk Level

Risk は以下で分類します。

| Risk | Meaning |
| --- | --- |
| High | build failure、release artifact 変更、runtime 影響、CI 全体停止の可能性がある |
| Medium | 一部 module、warning、test、CI job、developer environment に影響する可能性がある |
| Low | 影響範囲が限定的、または確認だけで完了できる可能性が高い |

Risk は final severity ではありません。
人間が判断するための調査上の分類です。

## Decision Log

なぜその判断をしたかを残します。

| Date | Decision | Reason | Owner |
| --- | --- | --- | --- |
| YYYY-MM-DD | Pending Human Decision |  |  |

Agent は判断材料を残し、人間の判断欄を空欄または pending として残します。

## Completion Criteria

調査完了条件:

- Official Documentation 確認済み
- Entry Point Release Notes 確認済み
- Change Inventory 作成済み
- Deep Dive 要否を判定済み
- Investigation Exit Criteria を満たしている
- Entry Point と References を分離済み
- 事実に Evidence と Confidence を紐付け済み
- Release Notes 確認済み
- Compatibility Matrix 確認済み
- Minimum と Recommended を分離済み
- Breaking Changes を分類済み
- Change Isolation Policy への影響を確認済み
- Affected Modules 記載済み
- Detection Method 記載済み
- Verification Commands 記載済み
- Test Scope 記載済み
- Rollback Plan 記載済み
- Follow-up Tasks 記載済み
- PR 分割方針記載済み
- 1ページサマリ作成済み
- Human Decision placeholder 記載済み

## Follow-up Tasks

調査後の実作業を分離して書きます。

例:

- AGP 更新 PR
- Gradle wrapper 更新 PR
- compileSdk 更新 Issue
- targetSdkVersion 更新 Issue
- NDK 更新 PR
- CI image 更新 PR
- KSP 更新 Issue
- Compose Compiler 更新 Issue

## Source Policy

一次情報を優先します。

優先順位:

1. Official Documentation
2. Release Notes
3. Compatibility Matrix
4. Issue Tracker
5. 実機・実プロジェクト検証
6. Blog

Blog や個人記事は、一次情報の補助としてのみ使います。

Release Notes は調査の entry point として優先します。
ただし、Release Notes の要約だけを根拠にせず、必要に応じて Compatibility Matrix、API Reference、Migration Guide、Issue Tracker などの一次情報をたどります。

## Source Diff Policy

通常調査では以下を利用します。

- Official Documentation
- Release Notes
- Compatibility Matrix
- Issue Tracker
- 実プロジェクト検証

AOSP / tools/base の差分調査は、以下のような必要がある場合のみ実施します。

- Release Notes だけでは判断できない
- DSL 変更の根拠確認が必要
- Build 挙動変更の根拠確認が必要
- Release Notes 未記載の変更を調査する必要がある

通常の Build System 調査では、AOSP / tools/base 差分は必須ではありません。

## Design Review

### 改善できる点

- Prompt / design を `.codex/prompts/` に置くことで、実装前の設計意図を資産として残せる。
- `build-system/AGENTS.md` を追加することで、Build System 調査時に Android Platform 側の AOSP 必須ルールを誤適用しにくくなる。
- 各 area の `versions/README.md` と `summaries/README.md` を置くことで、空ディレクトリを Git 管理しつつ、命名規則も残せる。

### 不足しやすい観点

- 実プロジェクトごとの module 構成、CI provider、release pipeline は調査対象ごとに異なるため、テンプレートでは空欄として残す。
- KSP / Compose Compiler は Kotlin / AGP と密接に関係するため、将来追加時には compatibility matrix に列を追加する可能性がある。
- Android Platform と Build System の exact same template 運用は避ける。共通思想は揃えるが、traceability fields は分ける。

### 冗長になりやすい内容

- `Minimum Required Versions` と `Compatibility Matrix` は重複しやすい。
  - `Minimum Required Versions`: 必須下限と推奨値を整理する。
  - `Compatibility Matrix`: 組み合わせの可否を整理する。
- `Risk Level` と `Breaking Changes` も重複しやすい。
  - `Breaking Changes`: 個別変更の分類。
  - `Risk Level`: 調査対象全体のリスク分類。

### 将来拡張しやすい構成

- `build-system/<area>/versions/` と `build-system/<area>/summaries/` を基本にする。
- area を追加するだけで KSP / Compose Compiler に対応できる。
- area 固有の調査ルールが増えた場合は `build-system/<area>/README.md` に閉じ込める。
- 共通テンプレートは `build-system/templates/` に置き、area 固有テンプレートは必要になるまで作らない。

## Goal of This Repository

最終的に、Android や Build System をアップデートするとき、このリポジトリだけを見れば以下を判断できる状態を目指します。

- 何が変わるのか
- 何を確認すべきか
- どこまで影響するか
- どのように検証するか
- どの単位で PR を分けるべきか
- どの判断が人間に残されているか

この設計は、調査、判断、検証、実装のすべてを支援するための基盤です。
