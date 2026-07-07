# AGP 8.7.0 調査

## Summary

AGP 8.7.0 は、API 35 対応、Gradle 8.9 / JDK 17 / SDK Build Tools 34.0.0 / NDK 27.0.12077973 を中心とする互換性更新と、Lint 実行時の `LintError` 扱いの変更を含む major release です。

最も注意すべき変更は Lint behavior change です。Gradle 経由の lint 実行で `LintError` が存在する場合に lint analysis task が例外を投げるため、lint baseline に genuine `LintError` が残っているプロジェクトでは build / CI が失敗する可能性があります。

AGP 8.7.0 への更新 PR には、原則として Gradle wrapper 更新、compileSdk 更新、targetSdkVersion 更新、NDK 更新、依存ライブラリ更新を混ぜないでください。ただし AGP 8.7.0 の最小要件を満たすために Gradle 8.9 への更新が必要な場合は、根拠と rollback plan を記録したうえで同時更新を検討します。

## Metadata

対象領域:
- AGP

調査対象:
- From: 未指定
- To: 8.7.0

調査日:
- 2026-07-07

調査者:
- Codex

関連作業:
- Issue:
- PR:

## Investigation Workflow

調査は以下の順序で行った。

1. AGP 8.7.0 Release Notes を entry point として確認
2. Compatibility、Lint behavior change、Fixed issues を変更点として一覧化
3. 変更点ごとに impact / deep dive 要否を分類
4. 互換性項目について関連する公式ドキュメントを references に記録
5. Source Code / tools-base 差分は、Release Notes と関連公式ドキュメントで判断可能なため未実施
6. 検証方法と PR 分割方針を整理
7. 1ページサマリを作成

## Entry Point

以下の公式ドキュメントを調査の起点とする。

| Document | Purpose | URL | Checked Date |
| --- | --- | --- | --- |
| Android Gradle Plugin 8.7.0 Release Notes | 調査開始点 | https://developer.android.com/build/releases/agp-8-7-0-release-notes | 2026-07-07 |

## Change Inventory

Release Notes / entry point から抽出した変更点を一覧化する。

| Change | Category | Deep Dive | Reason | Primary Sources |
| --- | --- | --- | --- | --- |
| AGP 8.7.0 は API level 35 までをサポート | Compatibility | Yes | compileSdk 35 / Android 15 対応可否の判断に関係する | AGP 8.7.0 Release Notes |
| Gradle minimum / default version が 8.9 | Compatibility | Yes | Gradle wrapper と CI Gradle cache / wrapper の影響がある | AGP 8.7.0 Release Notes |
| SDK Build Tools minimum / default version が 34.0.0 | Compatibility | Yes | SDK setup / CI image の確認が必要 | AGP 8.7.0 Release Notes、SDK Build Tools docs |
| JDK minimum / default version が 17 | Compatibility | Yes | local / CI の JDK 設定に影響する | AGP 8.7.0 Release Notes、Android Studio configuration docs |
| NDK default version が 27.0.12077973 | Compatibility / Native | Yes | native module がある場合に ABI / toolchain / CI NDK setup へ影響する | AGP 8.7.0 Release Notes、NDK install docs |
| Gradle 経由 lint 実行時の `LintError` が例外になる | Build behavior / Lint / Breaking Change | Yes | lint baseline に genuine `LintError` があると build / CI が失敗しうる | AGP 8.7.0 Release Notes |
| Lint 関連 fixed issues | Lint / Bug fix | Conditional | 対象 warning / false positive に遭遇している project では改善または差分発生の可能性がある | AGP 8.7.x Release Notes、Issue Tracker |
| R8 / Shrinker 関連 fixed issues | R8 / Shrinker / Bug fix | Conditional | minify / release build に該当 issue がある project では影響する可能性がある | AGP 8.7.2 Release Notes、Issue Tracker |
| Build performance / task execution 関連 fixed issue | Performance / Bug fix | Conditional | resource merge task 増加に遭遇している project では改善の可能性がある | AGP 8.7.0 Release Notes、Issue Tracker |
| BuildType#initWith の postprocessing block 関連 fixed issue | DSL / Build behavior / Bug fix | Conditional | `BuildType#initWith` と proguard 設定を使う project で確認対象 | AGP 8.7.0 Release Notes、Issue Tracker |
| foregroundServiceType manifest merge 関連 fixed issue | Build behavior / Manifest | Conditional | foreground service type を manifest merge している project で確認対象 | AGP 8.7.0 Release Notes、Issue Tracker |

通常は深掘り対象外:

- 対象 project で再現していない false positive / warning の単独修正
- documentation fix のみの issue
- 対象 project に native module がない場合の NDK default version 変更

## Minimum Required Versions

`Minimum` と `Recommended` を必ず分ける。

| Item | Current | Minimum | Recommended | Source | Notes |
| --- | --- | --- | --- | --- | --- |
| AGP | 未指定 | 8.7.0 | 8.7.3 | AGP 8.7.0 Release Notes | 8.7 系の最新 patch として 8.7.3 まで fixed issues が掲載されているため、実運用では patch 適用を推奨候補にする |
| Gradle | 未指定 | 8.9 | 8.9 | AGP 8.7.0 Release Notes | AGP 8.7.0 の minimum / default |
| JDK | 未指定 | 17 | 17 | AGP 8.7.0 Release Notes | local / CI とも確認対象 |
| Kotlin | 未指定 | 未記載 | Project constraints に従う | AGP 8.7.0 Release Notes | Release Notes 上では AGP 8.7.0 の Kotlin minimum は確認できない |
| compileSdk | 未指定 | Project constraints に従う | 35 までサポート | AGP 8.7.0 Release Notes | AGP 8.7 supports max API level 35。compileSdk 更新は別 PR とする |
| targetSdk | 未指定 | Project constraints に従う | 別判断 | Build System policy | targetSdkVersion 更新は Behavior Changes 対応として分離 |
| minSdk | 未指定 | Project constraints に従う | 別判断 | Build System policy | minSdk 更新は別判断 |
| SDK Build Tools | 未指定 | 34.0.0 | 34.0.0 | AGP 8.7.0 Release Notes | CI image / SDK setup 確認対象 |
| NDK | 未指定 | N/A | 27.0.12077973 | AGP 8.7.0 Release Notes | default version。native module がある場合に確認対象 |

## Compatibility Matrix

| AGP | Gradle | JDK | Kotlin | NDK | Status | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| 8.7.0 | 8.9 | 17 | 未記載 | 27.0.12077973 default | Supported | AGP 8.7.0 Release Notes の compatibility 情報に基づく |
| 8.7.0 | < 8.9 | 17 | 未記載 | 27.0.12077973 default | Unsupported / Unknown | Release Notes 上の minimum を満たさないため更新不可と扱う |
| 8.7.0 | 8.9 | < 17 | 未記載 | 27.0.12077973 default | Unsupported / Unknown | Release Notes 上の JDK minimum を満たさないため更新不可と扱う |

## Change Isolation

この調査で扱う変更:
- [x] AGP 更新
- [x] Gradle 更新要否の確認
- [ ] Kotlin 更新
- [ ] compileSdk 更新
- [ ] targetSdkVersion 更新
- [ ] minSdk 更新
- [x] NDK default version 影響確認
- [ ] 依存ライブラリ更新
- [x] CI 更新要否の確認

同じ PR に混ぜない変更:
- compileSdk 35 への更新
- targetSdkVersion 更新
- minSdk 更新
- Kotlin 更新
- 任意の依存ライブラリ更新
- 任意の NDK version pin 更新

同時更新が必要な変更:
- Gradle wrapper が 8.9 未満の場合、Gradle 8.9 への更新が AGP 8.7.0 更新に必要。

同時更新が必要な根拠:
- AGP 8.7.0 Release Notes の compatibility table に Gradle minimum 8.9 と記載されているため。

## Breaking Changes

| Classification | Change | Impact | Affected Modules | Detection Method | Required Action | Source |
| --- | --- | --- | --- | --- | --- | --- |
| Must Fix | Gradle 8.9 未満の project で AGP 8.7.0 を適用する | build が失敗する可能性が高い | 全 Gradle build | `gradle/wrapper/gradle-wrapper.properties` を確認 | Gradle wrapper を 8.9 に更新するか、AGP 更新を延期 | AGP 8.7.0 Release Notes |
| Must Fix | JDK 17 未満の local / CI で AGP 8.7.0 を使う | build / CI が失敗する可能性が高い | 全 build / CI | `java -version`、CI setup を確認 | JDK 17 を設定 | AGP 8.7.0 Release Notes |
| Must Fix / Should Fix | lint baseline に genuine `LintError` が残っている | `lint` task が例外で失敗しうる | lint 対象 module | `./gradlew lint`、baseline 内の `LintError` を確認 | baseline 修正、関連 library 更新、または対象 lint check の一時 disable を検討 | AGP 8.7.0 Release Notes |
| Watch | NDK default version 27.0.12077973 | native build / ABI / CI NDK install に影響しうる | native module | `.so`、`externalNativeBuild`、NDK pin を確認 | NDK pin の有無を確認し、release build / smoke test を実施 | AGP 8.7.0 Release Notes |
| Watch | R8 / Shrinker fixed issues | release build / minify 挙動差分の可能性 | minify enabled module | `minifyEnabled`、release build を確認 | `assembleRelease`、mapping / artifact 差分確認 | AGP 8.7.2 Release Notes |
| Watch | Build performance / mergeDebugResources task 関連修正 | build time 改善または task graph 差分の可能性 | Android module | build scan / task list を確認 | 更新前後の build time を比較 | AGP 8.7.0 Release Notes |

## Evidence

事実には必ず根拠となる公式文書を紐付ける。

| Fact | Evidence | Confidence |
| --- | --- | --- |
| AGP 8.7.0 は API level 35 までをサポートする | AGP 8.7.0 Release Notes / Compatibility | High |
| AGP 8.7.0 の Gradle minimum / default は 8.9 | AGP 8.7.0 Release Notes / Compatibility | High |
| AGP 8.7.0 の SDK Build Tools minimum / default は 34.0.0 | AGP 8.7.0 Release Notes / Compatibility | High |
| AGP 8.7.0 の JDK minimum / default は 17 | AGP 8.7.0 Release Notes / Compatibility | High |
| AGP 8.7.0 の NDK default は 27.0.12077973 | AGP 8.7.0 Release Notes / Compatibility | High |
| AGP 8.7.0-alpha08 以降、Gradle 経由 lint で `LintError` がある場合に lint analysis task が例外を投げる | AGP 8.7.0 Release Notes / Lint behavior change | High |
| lint baseline に genuine `LintError` がある project では build が壊れる可能性がある | AGP 8.7.0 Release Notes / Lint behavior change | High |
| Release Notes には 8.7.1 / 8.7.2 / 8.7.3 の fixed issues が掲載されている | AGP 8.7.0 Release Notes / Fixed issues | High |
| Kotlin minimum は AGP 8.7.0 Release Notes からは確認できない | AGP 8.7.0 Release Notes に該当記載なし | Medium |
| tools/base diff 調査は今回未実施 | Release Notes と関連公式 docs で主要判断が可能だったため | High |

## Risk Level

Risk:
- Medium

理由:
- 互換性要件として Gradle 8.9 / JDK 17 を満たす必要がある。
- Lint behavior change により、既存の lint baseline 品質によっては build / CI が失敗する。
- native module がある場合、NDK default version 変更の影響を確認する必要がある。

不確実性:
- 対象 project の現在の AGP / Gradle / JDK / NDK / lint baseline / native module の状態が未指定。
- Issue Tracker の個別 issue は Release Notes からリンクを確認したが、個別 issue の詳細本文までは今回の調査では深掘りしていない。

## Affected Modules

| Module | Impact | Evidence | Required Action |
| --- | --- | --- | --- |
| 全 Android module | AGP / Gradle / JDK 互換性の影響 | AGP 8.7.0 Release Notes | Gradle wrapper、JDK、CI 設定を確認 |
| lint 対象 module | `LintError` がある場合に lint task 失敗の可能性 | AGP 8.7.0 Release Notes | `./gradlew lint` と baseline 確認 |
| minify enabled module | R8 / Shrinker fixed issues による release artifact 差分の可能性 | AGP 8.7.2 fixed issues | `assembleRelease`、artifact / mapping 確認 |
| native module | default NDK 27.0.12077973 の影響可能性 | AGP 8.7.0 Release Notes | NDK pin、native build、release build 確認 |
| CI | Gradle / JDK / SDK / NDK setup の影響 | AGP 8.7.0 Release Notes | CI image、setup-java、SDK install、cache key 確認 |

## Detection Method

影響有無の確認方法:

- Gradle version: `gradle/wrapper/gradle-wrapper.properties`
- JDK version: `java -version`、CI の JDK setup
- AGP version: root `build.gradle(.kts)`、`settings.gradle(.kts)`、`gradle/libs.versions.toml`
- SDK Build Tools: installed SDK packages、CI SDK setup、explicit `buildToolsVersion`
- NDK: `android.ndkVersion`、`local.properties`、CI NDK install、`externalNativeBuild`
- Lint baseline: `lint-baseline.xml`、module-level lint configuration
- R8 / Shrinker: `minifyEnabled`、`proguardFiles`、default proguard files
- Native module: `.so`、`CMakeLists.txt`、`Android.mk`、`Application.mk`
- CI 設定: workflow、runner image、cache key、JDK / Android SDK / NDK setup
- release build 設定: signing、minify、resource shrink、artifact upload

## Verification Commands

```bash
./gradlew --version
./gradlew assembleDebug
./gradlew lint
./gradlew test
./gradlew dependencies
```

追加コマンド:

```bash
./gradlew assembleRelease
./gradlew :app:dependencies
./gradlew connectedDebugAndroidTest
```

native module がある場合:

```bash
./gradlew externalNativeBuildDebug
./gradlew assembleRelease
```

## Test Scope

- [x] Build
- [x] Unit Test
- [x] Lint
- [ ] Instrumentation Test
- [x] Release Build
- [x] Smoke Test

対象外:
- Instrumentation Test は対象 project の device / emulator / CI 環境が未指定のため、この汎用調査では必須にしない。

対象外にする理由:
- AGP 8.7.0 の主要リスクは build / lint / release artifact / CI setup に集中しているため。ただし対象 project が instrumentation-heavy の場合は追加する。

## Investigation Exit Criteria

- [x] 変更内容を説明できる
- [x] 影響範囲を説明できる
- [x] 必要な対応を説明できる
- [x] 検証方法を説明できる
- [x] 一次情報へ辿れる
- [x] 未調査事項があれば明記した

## Rollback Plan

戻すバージョン:
- AGP: 更新前の project version
- Gradle: 更新前の wrapper version
- JDK: 更新前の CI / local setup。ただし AGP 8.7.0 を維持するなら JDK 17 未満へ戻さない
- NDK: project が明示的に pin していた version

戻すファイル:
- `gradle/wrapper/gradle-wrapper.properties`
- root `build.gradle` / `build.gradle.kts`
- `settings.gradle` / `settings.gradle.kts`
- `gradle/libs.versions.toml`
- module `build.gradle` / `build.gradle.kts`
- CI workflow
- `lint-baseline.xml`
- native build config if changed

確認コマンド:
- `./gradlew --version`
- `./gradlew assembleDebug`
- `./gradlew lint`
- `./gradlew test`
- `./gradlew assembleRelease`

副作用:
- AGP rollback と Gradle rollback を分けると互換性が崩れる可能性がある。
- lint baseline 修正を rollback すると、AGP 8.7.0 再適用時に同じ lint failure が再発する可能性がある。
- NDK pin を戻すと native artifact が変わる可能性がある。

## Decision Log

| Date | Decision | Reason | Owner |
| --- | --- | --- | --- |
| 2026-07-07 | Pending Human Decision | 対象 project の現行 AGP / Gradle / JDK / lint baseline / native module 状態が未確認のため |  |

## Completion Criteria

- [x] Entry Point Release Notes 確認済み
- [x] Change Inventory 作成済み
- [x] Deep Dive 要否を判定済み
- [x] Entry Point と References を分離済み
- [x] 事実に Evidence と Confidence を紐付け済み
- [x] Official Documentation 確認済み
- [x] Release Notes 確認済み
- [x] Compatibility Matrix 確認済み
- [x] Minimum と Recommended を分離済み
- [x] Breaking Changes を分類済み
- [x] Change Isolation Policy への影響を確認済み
- [x] Affected Modules 記載済み
- [x] Detection Method 記載済み
- [x] Verification Commands 記載済み
- [x] Test Scope 記載済み
- [x] Rollback Plan 記載済み
- [x] Follow-up Tasks 記載済み
- [x] PR 分割方針記載済み
- [x] 1ページサマリ作成済み
- [x] Human Decision placeholder 記載済み

## Follow-up Tasks

| Task | Type | Owner | Status | Notes |
| --- | --- | --- | --- | --- |
| 現行 AGP / Gradle / JDK / SDK / NDK version の棚卸し | Investigation |  | Todo | AGP 8.7.0 適用前の前提確認 |
| lint baseline の `LintError` 有無確認 | Investigation |  | Todo | Lint behavior change の最重要確認 |
| Gradle 8.9 wrapper 更新 PR | PR |  | Todo | 現行 Gradle が 8.9 未満の場合のみ |
| AGP 8.7.x 更新 PR | PR |  | Todo | patch level は 8.7.3 推奨候補 |
| native module がある場合の NDK 27 impact 確認 | Investigation |  | Todo | NDK pin / artifact 差分確認 |
| release build / R8 smoke test | Verification |  | Todo | minify enabled module がある場合 |
| compileSdk 35 更新 Issue | Issue |  | Todo | AGP 更新とは分離 |
| targetSdkVersion 更新 Issue | Issue |  | Todo | Behavior Changes 対応として分離 |

## PR Strategy

この調査結果から推奨する PR 分割方針:

- AGP 更新: AGP 8.7.x 更新 PR として単独化する
- Gradle 更新: 8.9 未満なら AGP 更新に必要な最小変更として同時または先行 PR
- Kotlin 更新: 原則分離
- compileSdk 更新: 原則分離。AGP 8.7.0 は API 35 をサポートするが、compileSdk 35 更新は別 PR
- targetSdkVersion 更新: Behavior Changes 対応として分離
- minSdk 更新: 別判断
- NDK 更新: 明示 pin を変える場合は分離。default 影響の確認は AGP 更新 PR 内で可
- 依存ライブラリ更新: LintError 解消に必須な場合のみ、根拠を記録して例外扱い
- CI 更新: JDK 17 / Gradle 8.9 対応に必要な最小変更は同時可。それ以外の runner / image 更新は分離

## References

### Official Documentation

| Document | URL | Checked Date | Notes |
| --- | --- | --- | --- |
| AGP 8.7.0 Release Notes | https://developer.android.com/build/releases/agp-8-7-0-release-notes | 2026-07-07 | Entry Point |
| Update the IDE and SDK tools | https://developer.android.com/studio/intro/update | 2026-07-07 | SDK / tools 更新の関連情報 |
| SDK Build Tools release notes | https://developer.android.com/tools/releases/build-tools | 2026-07-07 | SDK Build Tools 34.0.0 確認用 |
| Install and configure the NDK and CMake | https://developer.android.com/studio/projects/install-ndk | 2026-07-07 | NDK install / configure 確認用 |
| Configure Android Studio | https://developer.android.com/studio/intro/studio-config | 2026-07-07 | JDK 設定確認用 |

### Source Code

| Source | URL / Path | Checked Date | Notes |
| --- | --- | --- | --- |
| AOSP / tools-base |  |  | 今回未実施。Release Notes と関連公式 docs で主要判断が可能だったため |

### Issue

| Issue Tracker | URL | Checked Date | Notes |
| --- | --- | --- | --- |
| Issue #374488858 | https://issuetracker.google.com/issues/374488858 | 2026-07-07 | Release Notes 8.7.3 Lint fixed issue |
| Issue #375352607 | https://issuetracker.google.com/issues/375352607 | 2026-07-07 | Release Notes 8.7.3 Lint fixed issue |
| Issue #370694831 | https://issuetracker.google.com/issues/370694831 | 2026-07-07 | Release Notes 8.7.2 Lint fixed issue |
| Issue #363492038 | https://issuetracker.google.com/issues/363492038 | 2026-07-07 | Release Notes 8.7.2 R8 fixed issue |
| Issue #372749733 | https://issuetracker.google.com/issues/372749733 | 2026-07-07 | Release Notes 8.7.2 R8 fixed issue |
| Issue #353579998 | https://issuetracker.google.com/issues/353579998 | 2026-07-07 | Release Notes 8.7.0 NDK default issue |
| Issue #355397971 | https://issuetracker.google.com/issues/355397971 | 2026-07-07 | Release Notes 8.7.0 resource task / performance issue |
| Issue #307784512 | https://issuetracker.google.com/issues/307784512 | 2026-07-07 | Release Notes 8.7.0 BuildType#initWith issue |
| Issue #359245746 | https://issuetracker.google.com/issues/359245746 | 2026-07-07 | Release Notes 8.7.0 manifest merge issue |

### Validation

| Validation Target | Method | Checked Date | Notes |
| --- | --- | --- | --- |
| Target project | Not run |  | 対象 project 未指定のため未実施 |
| CI run | Not run |  | 対象 CI 未指定のため未実施 |

### Additional References

| Source Type | Title | URL | Checked Date | Notes |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

## Facts / Observations / Hypotheses / Conclusions

### Facts

- AGP 8.7.0 は API level 35 までをサポートする。
- AGP 8.7.0 は Gradle 8.9 と JDK 17 を minimum / default としている。
- AGP 8.7.0 は SDK Build Tools 34.0.0 を minimum / default としている。
- AGP 8.7.0 は NDK 27.0.12077973 を default としている。
- AGP 8.7.0-alpha08 以降、Gradle 経由 lint で `LintError` がある場合に lint analysis task が例外を投げる。
- Release Notes には 8.7.1 / 8.7.2 / 8.7.3 の fixed issues が掲載されている。

### Observations

- Lint behavior change は、単なる bug fix ではなく build / CI failure に直結しうるため、AGP 8.7.0 更新前の重点確認項目。
- Compatibility table は Gradle / JDK / SDK Build Tools / NDK を明示しているが、Kotlin minimum はこの Release Notes からは読み取れない。
- AGP 8.7.0 は API 35 をサポートするが、compileSdk 35 への更新は AGP 更新と分けて扱う方が影響範囲を切り分けやすい。

### Hypotheses

- lint baseline に古い third-party library 由来の `LintError` が残っている project では、AGP 8.7.0 更新時に CI lint が失敗する可能性がある。
- native module がある project では、NDK default version 変更により native artifact や warning が変わる可能性がある。
- minify enabled release build では、R8 fixed issues により artifact または warning が変わる可能性がある。

### Conclusions

- AGP 8.7.0 更新の主要リスクは、Gradle / JDK 互換性、Lint behavior change、NDK default version、R8 / release build 差分である。
- 最初に現行 version と lint baseline を棚卸しし、Gradle 8.9 / JDK 17 を満たせることを確認する。
- AGP 更新 PR は小さく保ち、compileSdk / targetSdkVersion / Kotlin / 任意 dependency 更新は分離する。
