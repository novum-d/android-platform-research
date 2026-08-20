# AGP 8.7 系から 9.3.1 への更新: 1ページサマリ

## Target

| 項目 | 内容 |
| --- | --- |
| From | AGP 8.7.x |
| To | AGP 9.3.1 |
| 調査日 | 2026-08-19 |
| 対象プロジェクト | 未指定 |

## Outcome

2026-08-19 時点の最新 stable は AGP 9.3.1 である。公式 Release Notes では 9.3.1 に public fixed issue は掲載されていない。AGP 8.7 系からの更新は、単純な plugin version 更新ではなく AGP 9.0 を境界とする major migration として扱う。

## Compatibility

| 項目 | AGP 8.7 系 | AGP 9.3.1 |
| --- | --- | --- |
| Gradle | 8.9 | 9.5.0 |
| JDK | 17 | 17 |
| Build Tools | 34.0.0 | 36.0.0 |
| 既定 NDK | 27.0.12077973 | 28.2.13676358 |
| 最大 API level | 35 | 37 |
| Kotlin Android | 外部 plugin | Built-in Kotlin が既定 |
| Android Studio | Ladybug で対応 | Quail 2 が AGP 9.3 に対応 |

`compileSdk` の上限と `targetSdk` の採用判断は別である。AGP 更新だけを理由に Android OS behavior change を同じ PR へ混ぜない。

## Minimum Required Versions

- AGP 9.3.1
- Gradle 9.5.0
- JDK 17
- Build Tools 36.0.0
- 最大 API level 37

## 重要差分

### Must Fix

- 旧 `applicationVariants` / `libraryVariants` / `variantFilter` や内部実装型を public `androidComponents` API へ移す
- Built-in Kotlin に合わせて `org.jetbrains.kotlin.android`、KAPT、`android.kotlinOptions`、source set を見直す
- 削除された Wear app 埋め込み、density split、旧 report task、DSL / Variant API、global build feature property を除去する
- AGP 9.3.1 と Gradle 9.5.0 を同じ移行段階で更新し、Gradle 実行 JDK 17 を確認する

### Should Verify

- AGP 9.0 の既定値変更: unique package、AndroidX test runner、dependency constraint、app の non-final R
- library consumer の `compileSdk` と AAR metadata
- AGP 9.1 の R8 package 再配置
- AGP 9.2 の `-keepattributes` wildcard semantics
- NDK r28c、JNI、CMake、prefab

### Optional / Separate

- AGP 9.2 の experimental report aggregation
- AGP 9.3 の新 `optimization` DSL
- `src/<variant>/keepRules/*.keep` への整理
- compileSdk / targetSdk / NDK pin の独立更新

## 推奨アプローチ

1. 旧 DSL / Variant API、Kotlin plugin、KAPT、削除 property、R8、native build を静的検出する。
2. 必要なら AGP 8.13.2 で public API への準備変更を安定させる。
3. AGP 9.0 境界で新 DSL と Built-in Kotlin を検証する。一時 opt-out は期限付きの退避策にする。
4. AGP 9.3.1 + Gradle 9.5.0 へ更新する。
5. release build、minification、instrumentation、native build、CI を検証する。
6. `:app:analyzeReleaseR8Config` の結果に基づく rule 整理は別 PR にする。

## Risk

総合リスクは **High**。ただし対象プロジェクトが未指定のため、これは変更量に基づく暫定評価である。custom build logic、KAPT、R8、native module、dynamic feature の有無で実リスクは変わる。

## Affected Modules

app、Android library、dynamic feature、Wear、native、KMP、`buildSrc` / `build-logic`、CI が候補となる。

## Verification

- Gradle configuration、debug / release assemble、bundle
- unit / instrumentation test、Lint
- minified release、R8 analyzer、reflection / serialization
- native build、JNI、CI cache / report / artifact

## PR Strategy

診断、8.xでのpublic API準備、AGP 9.0境界、Built-in Kotlin、AGP 9.3 stable、R8最適化の順に分離する。小規模プロジェクトでは検出結果に基づき中間段階を省略できる。

## Official References

- [AGP 9.3 release notes](https://developer.android.com/build/releases/agp-9-3-0-release-notes)
- [AGP 9.0 release notes](https://developer.android.com/build/releases/agp-9-0-0-release-notes)
- [AGP / Gradle compatibility](https://developer.android.com/build/releases/about-agp)
- [Built-in Kotlin への移行](https://developer.android.com/build/migrate-to-built-in-kotlin)
- [Variant API](https://developer.android.com/build/extend-agp)
- [R8 configuration analyzer](https://developer.android.com/topic/performance/app-optimization/r8-configuration-analyzer)
- 全 minor の公式リンクと詳細は [差分調査本編](../versions/agp-8.7-to-9.3.md) を参照

## Follow-up Tasks

- [ ] 対象プロジェクトで静的検出を実行する
- [ ] plugin / Kotlin / KSP / KMP compatibility を確認する
- [ ] release、R8、native、CI の検証結果を記録する

## Human Decision

Status: **Pending Human Decision**

- [ ] AGP 9.3.1 を移行先とするか
- [ ] 中間版を経由するか
- [ ] 一時 opt-out と削除期限を認めるか
- [ ] Kotlin / KAPT / KSP、R8、native 対応の PR 分割
- [ ] 最終優先度、severity、release readiness
