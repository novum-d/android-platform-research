# AGP 8.7.0 1ページサマリ

## Target

対象領域:
- AGP

調査対象:
- From: 未指定
- To: 8.7.0

詳細調査:
- `build-system/agp/versions/agp-8.7.0.md`

## Decision Summary

AGP 8.7.0 は API 35 対応と Gradle 8.9 / JDK 17 / SDK Build Tools 34.0.0 / NDK 27.0.12077973 の互換性条件を持つ major release です。

最大の注意点は Lint behavior change です。lint baseline に genuine `LintError` が残っている project では、`./gradlew lint` や CI が失敗する可能性があります。

更新前に、現行 Gradle wrapper、JDK、SDK setup、NDK pin、lint baseline、native module、release build / R8 設定を確認してください。

- 何が変わるか: AGP 8.7.0 の互換性要件、API 35 support、LintError 処理、8.7.x fixed issues
- 誰に影響するか: Android Gradle build 全体、lint 対象 module、native module、minify enabled release build、CI
- 必須対応: Gradle 8.9 / JDK 17 を満たすこと、lint baseline の `LintError` 確認
- 推奨対応: AGP 8.7.3 への patch 適用、release build / lint / CI smoke test
- 主な不確実性: 対象 project の現行 version / lint baseline / native module / CI setup が未確認

## Minimum Required Versions

| Item | Current | Minimum | Recommended | Notes |
| --- | --- | --- | --- | --- |
| AGP | 未指定 | 8.7.0 | 8.7.3 | 8.7.3 まで fixed issues が掲載されているため patch 適用を推奨候補にする |
| Gradle | 未指定 | 8.9 | 8.9 | AGP 8.7.0 の minimum / default |
| JDK | 未指定 | 17 | 17 | local / CI で確認 |
| Kotlin | 未指定 | 未記載 | Project constraints に従う | Release Notes では確認不可 |
| compileSdk | 未指定 | Project constraints に従う | 35 までサポート | compileSdk 更新は別 PR |
| targetSdk | 未指定 | Project constraints に従う | 別判断 | Behavior Changes 対応として分離 |
| minSdk | 未指定 | Project constraints に従う | 別判断 | 別判断 |
| SDK Build Tools | 未指定 | 34.0.0 | 34.0.0 | CI SDK setup 確認 |
| NDK | 未指定 | N/A | 27.0.12077973 | native module がある場合に確認 |

## Compatibility Matrix

| AGP | Gradle | JDK | Kotlin | NDK | Status | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| 8.7.0 | 8.9 | 17 | 未記載 | 27.0.12077973 default | Supported | Release Notes に基づく |
| 8.7.0 | < 8.9 | 17 | 未記載 | 27.0.12077973 default | Unsupported / Unknown | Gradle minimum を満たさない |
| 8.7.0 | 8.9 | < 17 | 未記載 | 27.0.12077973 default | Unsupported / Unknown | JDK minimum を満たさない |

## Breaking Changes Summary

| Classification | Change | Impact | Required Action |
| --- | --- | --- | --- |
| Must Fix | Gradle 8.9 未満 | AGP 8.7.0 適用時に build 失敗の可能性 | Gradle wrapper を 8.9 に更新 |
| Must Fix | JDK 17 未満 | local / CI build 失敗の可能性 | JDK 17 を設定 |
| Must Fix / Should Fix | lint baseline に genuine `LintError` | `lint` task / CI 失敗の可能性 | baseline 修正、dependency 更新、または一時 disable |
| Watch | NDK default 27.0.12077973 | native build / artifact 差分の可能性 | native module と NDK pin を確認 |
| Watch | R8 / Shrinker fixed issues | release artifact 差分の可能性 | `assembleRelease` と artifact 確認 |

## Risk Level

Risk:
- Medium

理由:
- Gradle 8.9 / JDK 17 は満たす必要がある。
- Lint behavior change は CI failure に直結しうる。
- native / R8 / release build がある project では追加確認が必要。

## Affected Modules

| Module | Impact | Required Action |
| --- | --- | --- |
| 全 Android module | AGP / Gradle / JDK 互換性 | version 棚卸し |
| lint 対象 module | `LintError` による lint failure | `./gradlew lint` と baseline 確認 |
| native module | NDK default version 影響 | NDK pin / native build 確認 |
| minify enabled module | R8 / release artifact 差分 | `assembleRelease` 確認 |
| CI | JDK / SDK / Gradle setup 影響 | workflow / runner / cache 確認 |

## Verification

最低限の確認コマンド:

```bash
./gradlew --version
./gradlew assembleDebug
./gradlew lint
./gradlew test
```

追加で必要な検証:
- Build
- Unit Test
- Lint
- Release Build
- Smoke Test
- native module がある場合は native build

## PR Strategy

推奨する PR 分割方針:

- AGP 更新: AGP 8.7.x 更新 PR として単独化
- Gradle 更新: 8.9 未満なら最小必須変更として先行または同時
- Kotlin 更新: 分離
- compileSdk 更新: 分離。AGP 8.7.0 は API 35 をサポートするが別 PR
- targetSdkVersion 更新: Behavior Changes 対応として分離
- minSdk 更新: 別判断
- NDK 更新: explicit pin を変えるなら分離
- 依存ライブラリ更新: LintError 解消に必須な場合のみ例外
- CI 更新: JDK 17 / Gradle 8.9 対応に必要な最小変更のみ同時可

## Evidence / References

詳細な Evidence と References は詳細調査を参照する。

重要な根拠:

| Fact | Evidence | Confidence |
| --- | --- | --- |
| AGP 8.7.0 は API level 35 までをサポートする | AGP 8.7.0 Release Notes | High |
| AGP 8.7.0 の Gradle minimum / default は 8.9 | AGP 8.7.0 Release Notes | High |
| AGP 8.7.0 の JDK minimum / default は 17 | AGP 8.7.0 Release Notes | High |
| AGP 8.7.0 の SDK Build Tools minimum / default は 34.0.0 | AGP 8.7.0 Release Notes | High |
| AGP 8.7.0 の NDK default は 27.0.12077973 | AGP 8.7.0 Release Notes | High |
| `LintError` がある場合に lint analysis task が例外を投げる | AGP 8.7.0 Release Notes | High |

## Follow-up Tasks

| Task | Type | Owner | Status |
| --- | --- | --- | --- |
| 現行 AGP / Gradle / JDK / SDK / NDK version の棚卸し | Investigation |  | Todo |
| lint baseline の `LintError` 有無確認 | Investigation |  | Todo |
| Gradle 8.9 wrapper 更新 PR | PR |  | Todo |
| AGP 8.7.x 更新 PR | PR |  | Todo |
| native module がある場合の NDK 27 impact 確認 | Investigation |  | Todo |
| release build / R8 smoke test | Verification |  | Todo |
| compileSdk 35 更新 Issue | Issue |  | Todo |
| targetSdkVersion 更新 Issue | Issue |  | Todo |

## Human Decision

最終判断:
- Pending Human Decision

判断者:
- （記入）

判断日:
- YYYY-MM-DD

判断理由:
- 対象 project の現行 version / lint baseline / native module / CI setup を確認した後に判断する。
