# [Migration Title] チェックリスト

> Ownership: このテンプレートから作る repository-wide checklist は再利用可能な手順を定義する。`Current`、実行済みチェック、command result、対象 branch / commit、Decision Log は、対象プロジェクト側へコピーした実行用 checklist または PR / issue でのみ記入する。

## Summary

この migration で実施する変更と、実施しない変更を明記する。

## Scope

実施する変更:
- [ ] AGP 更新
- [ ] Gradle 更新
- [ ] Kotlin 更新
- [ ] compileSdk 更新
- [ ] targetSdkVersion 更新
- [ ] minSdk 更新
- [ ] NDK 更新
- [ ] 依存ライブラリ更新
- [ ] CI 更新

実施しない変更:
- （記入）

分離する follow-up:
- （記入）

## Pre-check

- [ ] 現在の AGP version を確認
- [ ] 現在の Gradle version を確認
- [ ] 現在の JDK version を確認
- [ ] 現在の Kotlin version を確認
- [ ] 現在の compileSdk / targetSdk / minSdk を確認
- [ ] 現在の NDK version を確認
- [ ] CI の JDK / Gradle cache / image を確認
- [ ] native module の有無を確認
- [ ] release build の有無を確認

## Minimum Required Versions

| Item | Current | Minimum | Recommended | Action |
| --- | --- | --- | --- | --- |
| AGP |  |  |  |  |
| Gradle |  |  |  |  |
| JDK |  |  |  |  |
| Kotlin |  |  |  |  |
| compileSdk |  |  |  |  |
| targetSdk |  |  |  |  |
| minSdk |  |  |  |  |
| NDK |  |  |  |  |

## File Changes

| File | Expected Change | Reason | Rollback |
| --- | --- | --- | --- |
| `gradle/wrapper/gradle-wrapper.properties` |  |  |  |
| `settings.gradle` / `settings.gradle.kts` |  |  |  |
| root `build.gradle` / `build.gradle.kts` |  |  |  |
| module `build.gradle` / `build.gradle.kts` |  |  |  |
| `gradle/libs.versions.toml` |  |  |  |
| CI config |  |  |  |

## Verification Commands

```bash
./gradlew assembleDebug
./gradlew test
./gradlew lint
./gradlew dependencies
```

Release / device verification:

```bash
./gradlew assembleRelease
./gradlew connectedDebugAndroidTest
```

## Test Scope

- [ ] Build
- [ ] Unit Test
- [ ] Lint
- [ ] Instrumentation Test
- [ ] Release Build
- [ ] Smoke Test

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

## Completion Criteria

- [ ] 対象変更が Change Isolation Policy に沿っている
- [ ] 必須でない更新を混ぜていない
- [ ] Compatibility Matrix を確認済み
- [ ] Breaking Changes を確認済み
- [ ] Affected Modules を確認済み
- [ ] Verification Commands を実行済み
- [ ] Rollback Plan を記載済み
- [ ] Follow-up Tasks を分離済み

## Follow-up Tasks

| Task | Type | Owner | Status | Notes |
| --- | --- | --- | --- | --- |
|  | PR / Issue / Investigation |  | Todo / Doing / Done |  |

## References

### Official Documentation

- Release Notes:
- Compatibility Matrix:
- Migration Guide:
- API Reference:

### Source Code

- AOSP / tools-base:

### Issue

- Issue Tracker:

### Validation

- Project Verification:
- CI run:
