# [Area] [From Version] -> [To Version] 調査

## Summary

何が変わるか、どのプロジェクトに影響しそうか、対応が必要かを 3〜7 行で説明する。

## Metadata

対象領域:
- AGP / Gradle / Kotlin / NDK / CI / Other:

調査対象:
- From:
- To:

調査日:
- YYYY-MM-DD

調査者:
- （記入）

関連作業:
- Issue:
- PR:

## Investigation Workflow

調査は以下の順序で行う。

1. 対象 area の entry point を読む
2. 変更点を一覧化する
3. 各変更について影響の有無を判定する
4. 必要なものだけ一次情報を深掘りする
5. 必要な場合のみ AOSP / tools/base の差分を確認する
6. 調査結果をこのテンプレートへまとめる
7. 検証方法と PR 分割方針まで記載する

## Entry Point

以下の公式ドキュメントを調査の起点とする。

| Document | Purpose | URL | Checked Date |
| --- | --- | --- | --- |
| AGP / Gradle / Kotlin / NDK / CI / Other Release Notes | 調査開始点 |  | YYYY-MM-DD |

## Change Inventory

Release Notes / entry point から抽出した変更点を一覧化する。

| Change | Category | Deep Dive | Reason | Primary Sources |
| --- | --- | --- | --- | --- |
|  | Compatibility / Breaking Change / Deprecated / Default / DSL / Task / Performance / CI / Native / Lint / Bug fix / Docs / Other | Yes / No |  |  |

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

## Minimum Required Versions

`Minimum` と `Recommended` を必ず分ける。

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

## Compatibility Matrix

| AGP | Gradle | JDK | Kotlin | NDK | Status | Notes |
| --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  | Supported / Unsupported / Unknown |  |

## Change Isolation

この調査で扱う変更:
- [ ] AGP 更新
- [ ] Gradle 更新
- [ ] Kotlin 更新
- [ ] compileSdk 更新
- [ ] targetSdkVersion 更新
- [ ] minSdk 更新
- [ ] NDK 更新
- [ ] 依存ライブラリ更新
- [ ] CI 更新

同じ PR に混ぜない変更:
- （記入）

同時更新が必要な変更:
- （記入）

同時更新が必要な根拠:
- （記入）

## Breaking Changes

| Classification | Change | Impact | Affected Modules | Detection Method | Required Action | Source |
| --- | --- | --- | --- | --- | --- | --- |
| Must Fix / Should Fix / Watch / No Action |  |  |  |  |  |  |

## Evidence

事実には必ず根拠となる公式文書を紐付ける。

| Fact | Evidence | Confidence |
| --- | --- | --- |
|  |  | High / Medium / Low |

## Risk Level

Risk:
- High / Medium / Low

理由:
- （記入）

不確実性:
- （記入）

## Affected Modules

| Module | Impact | Evidence | Required Action |
| --- | --- | --- | --- |
|  |  |  |  |

## Detection Method

影響有無の確認方法:

- Gradle version:
- JDK version:
- `settings.gradle` / `settings.gradle.kts`:
- root `build.gradle` / `build.gradle.kts`:
- module `build.gradle` / `build.gradle.kts`:
- `gradle/libs.versions.toml`:
- `gradle-wrapper.properties`:
- `.so` の有無:
- native build files:
- CI 設定:
- release build 設定:

## Verification Commands

```bash
./gradlew assembleDebug
./gradlew test
./gradlew lint
./gradlew dependencies
```

追加コマンド:

```bash
# 必要に応じて記載
```

## Test Scope

- [ ] Build
- [ ] Unit Test
- [ ] Lint
- [ ] Instrumentation Test
- [ ] Release Build
- [ ] Smoke Test

対象外:
- （記入）

対象外にする理由:
- （記入）

## Investigation Exit Criteria

- [ ] 変更内容を説明できる
- [ ] 影響範囲を説明できる
- [ ] 必要な対応を説明できる
- [ ] 検証方法を説明できる
- [ ] 一次情報へ辿れる
- [ ] 未調査事項があれば明記した

## Rollback Plan

戻すバージョン:
- （記入）

戻すファイル:
- （記入）

確認コマンド:
- （記入）

副作用:
- （記入）

## Decision Log

| Date | Decision | Reason | Owner |
| --- | --- | --- | --- |
| YYYY-MM-DD | Pending Human Decision |  |  |

## Research Complete Criteria

以下は調査成果物の完成条件である。Human Decision が `Pending Human Decision` のままでも満たせる。owner が判断を記録した後にのみ Decision Complete とする。

- [ ] Entry Point Release Notes 確認済み
- [ ] Change Inventory 作成済み
- [ ] Deep Dive 要否を判定済み
- [ ] Entry Point と References を分離済み
- [ ] 事実に Evidence と Confidence を紐付け済み
- [ ] Official Documentation 確認済み
- [ ] Release Notes 確認済み
- [ ] Compatibility Matrix 確認済み
- [ ] Minimum と Recommended を分離済み
- [ ] Breaking Changes を分類済み
- [ ] Change Isolation Policy への影響を確認済み
- [ ] Affected Modules 記載済み
- [ ] Detection Method 記載済み
- [ ] Verification Commands 記載済み
- [ ] Test Scope 記載済み
- [ ] Rollback Plan 記載済み
- [ ] Follow-up Tasks 記載済み
- [ ] PR 分割方針記載済み
- [ ] 1ページサマリ作成済み
- [ ] Human Decision placeholder 記載済み

## Follow-up Tasks

| Task | Type | Owner | Status | Notes |
| --- | --- | --- | --- | --- |
|  | PR / Issue / Investigation |  | Todo / Doing / Done |  |

## PR Strategy

この調査結果から推奨する PR 分割方針:

- AGP 更新:
- Gradle 更新:
- Kotlin 更新:
- compileSdk 更新:
- targetSdkVersion 更新:
- minSdk 更新:
- NDK 更新:
- 依存ライブラリ更新:
- CI 更新:

## References

### Official Documentation

| Document | URL | Checked Date | Notes |
| --- | --- | --- | --- |
| Release Notes |  | YYYY-MM-DD | Entry Point |
| Compatibility Matrix |  | YYYY-MM-DD |  |
| Migration Guide |  | YYYY-MM-DD |  |
| API Reference |  | YYYY-MM-DD |  |

### Source Code

| Source | URL / Path | Checked Date | Notes |
| --- | --- | --- | --- |
| AOSP / tools-base |  | YYYY-MM-DD | 必要時のみ |

### Issue

| Issue Tracker | URL | Checked Date | Notes |
| --- | --- | --- | --- |
| Google Issue Tracker / GitHub / YouTrack |  | YYYY-MM-DD |  |

### Validation

| Validation Target | Method | Checked Date | Notes |
| --- | --- | --- | --- |
| Sample Project / Production Project / CI run |  | YYYY-MM-DD |  |

### Additional References

| Source Type | Title | URL | Checked Date | Notes |
| --- | --- | --- | --- | --- |
| Blog / Article / Other |  |  | YYYY-MM-DD | 補助情報としてのみ使用 |

## Facts / Observations / Hypotheses / Conclusions

### Facts

- （記入）

### Observations

- （記入）

### Hypotheses

- （記入）

### Conclusions

- （記入）
