# AGP 8.7 系から 9.3.1 までの差分調査

## 1. 調査メタデータ

| 項目 | 内容 |
| --- | --- |
| 調査対象 | Android Gradle Plugin |
| From | AGP 8.7.x |
| To | AGP 9.3.1 |
| 最新 stable の確認日 | 2026-08-19 |
| 調査方式 | 各 minor の公式 release notes を inventory 化し、互換性・破壊的変更・移行経路を深掘り |
| 対象プロジェクト | 未指定。実プロジェクトへの適用判定は未実施 |
| 総合リスク | High。AGP 9.0 で DSL、Kotlin 統合、既定値、削除 API がまとまって変更される |
| Confidence | High（公式 release notes、公式移行ガイド、公式互換性表に基づく） |

この文書は既存の [AGP 8.7.0 調査](agp-8.7.0.md) を baseline とし、AGP 8.8 から 9.3.1 までの累積差分を扱う。2026-08-19 に公式 9.3 Release Notes を再確認し、9.3.1 に public fixed issue が掲載されていないこと、公式 API Reference で current stable が 9.3.1 であることを確認した。最新 preview である AGP 9.4.0-rc01 は stable の移行先に含めず、[preview 監視資料](agp-9.4-preview-watch.md)へ分離した。

関連成果物:
- [1ページサマリ](../summaries/agp-8.7-to-9.3-summary.md)
- [移行チェックリスト](../checklists/agp-8.7-to-9.3-migration-checklist.md)

## Investigation Workflow

1. AGP 8.7 の既存調査を baseline とする。
2. 8.8 から 9.3 までの公式 release notes を change inventory にする。
3. 公式 compatibility matrix で Gradle、JDK、Build Tools、NDK、API level を照合する。
4. source / behavior breaking change を公式 migration guide と API guide で深掘りする。
5. 対象プロジェクト未指定のため、実装検出と build validation は再利用可能な手順として残す。

## 2. 結論

AGP 8.7 系からの最新 stable 移行先は AGP 9.3.1 である。必要な build toolchain は Gradle 8.9 から 9.5.0、Build Tools 34.0.0 から 36.0.0、既定 NDK は 27.0.12077973 から 28.2.13676358 へ進む。JDK の最低要件は 17 のまま変わらない。

移行の中心はバージョン番号の更新ではなく、AGP 9.0 の次の変更である。

- 新 DSL が既定となり、内部実装型や旧 Variant API に依存する build logic は移行が必要
- Built-in Kotlin が既定となり、`org.jetbrains.kotlin.android`、KAPT、`android.kotlinOptions` の扱いが変わる
- AndroidX、package 一意性、app の compile-time R class などの既定値が変わる
- Wear app 埋め込み、density split、旧 report task、複数の DSL / Variant API が削除される
- R8 の package 再配置と `-keepattributes` の解釈が 9.1、9.2 で変わる

したがって、実プロジェクトでは AGP 9.0 境界の検出を先に行い、build logic、Kotlin、R8、native build を別々に検証できる移行計画が必要である。

## 3. Entry Point

### Entry Point

- [Android Gradle plugin release notes](https://developer.android.com/build/releases/gradle-plugin)
- [AGP と Gradle の互換性](https://developer.android.com/build/releases/about-agp)
- [AGP 9.0 release notes](https://developer.android.com/build/releases/agp-9-0-0-release-notes)

### Version ごとの公式 release notes

| 系列 | 公式リンク | この調査での扱い |
| --- | --- | --- |
| 8.7 | [AGP 8.7.0](https://developer.android.com/build/releases/agp-8-7-0-release-notes) | baseline |
| 8.8 | [AGP 8.8.0](https://developer.android.com/build/releases/agp-8-8-0-release-notes) | inventory |
| 8.9 | [AGP 8.9.0](https://developer.android.com/build/releases/agp-8-9-0-release-notes) | inventory |
| 8.10 | [AGP 8.10.0](https://developer.android.com/build/releases/agp-8-10-0-release-notes) | API 変更を深掘り |
| 8.11 | [AGP 8.11.0](https://developer.android.com/build/releases/agp-8-11-0-release-notes) | inventory |
| 8.12 | [AGP 8.12.0](https://developer.android.com/build/releases/agp-8-12-0-release-notes) | unit test resource の変更を深掘り |
| 8.13 | [AGP 8.13.0](https://developer.android.com/build/releases/agp-8-13-0-release-notes) | API 36.1 / Kotlin 2.3 対応を確認 |
| 9.0 | [AGP 9.0.0](https://developer.android.com/build/releases/agp-9-0-0-release-notes) | major migration の中心 |
| 9.1 | [AGP 9.1.0](https://developer.android.com/build/releases/agp-9-1-0-release-notes) | R8 package 再配置を深掘り |
| 9.2 | [AGP 9.2.0](https://developer.android.com/build/releases/agp-9-2-0-release-notes) | R8 attribute と report aggregation を深掘り |
| 9.3 | [AGP 9.3.1](https://developer.android.com/build/releases/agp-9-3-0-release-notes) | stable target |

### 補助資料

- [Built-in Kotlin への移行](https://developer.android.com/build/migrate-to-built-in-kotlin)
- [AGP の拡張と Variant API](https://developer.android.com/build/extend-agp)
- [AGP API updates](https://developer.android.com/build/releases/gradle-plugin-api-updates)
- [AGP roadmap](https://developer.android.com/build/releases/gradle-plugin-roadmap)
- [Gradle API reference](https://developer.android.com/reference/tools/gradle-api)
- [R8 configuration analyzer](https://developer.android.com/topic/performance/app-optimization/r8-configuration-analyzer)
- [アプリ最適化の有効化](https://developer.android.com/topic/performance/app-optimization/enable-app-optimization)

## 4. Compatibility Matrix

| AGP | 最新 patch | 必須 Gradle | JDK | Build Tools | 既定 NDK | 最大 API level |
| --- | --- | --- | --- | --- | --- | --- |
| 8.7 | 8.7.3 | 8.9 | 17 | 34.0.0 | 27.0.12077973 | 35 |
| 8.8 | 8.8.2 | 8.10.2 | 17 | 35.0.0 | 27.0.12077973 | 35 |
| 8.9 | 8.9.2 | 8.11.1 | 17 | 35.0.0 | 27.0.12077973 | 35 |
| 8.10 | 8.10.1 | 8.11.1 | 17 | 35.0.0 | 27.0.12077973 | 36 |
| 8.11 | 8.11.1 | 8.13 | 17 | 35.0.0 | 27.0.12077973 | 36 |
| 8.12 | 8.12.2 | 8.13 | 17 | 35.0.0 | 27.0.12077973 | 36 |
| 8.13 | 8.13.2 | 8.13 | 17 | 35.0.0 | 27.0.12077973 | 36.1 |
| 9.0 | 9.0.1 | 9.1.0 | 17 | 36.0.0 | 28.2.13676358 | 36.1 |
| 9.1 | 9.1.1 | 9.3.1 | 17 | 36.0.0 | 28.2.13676358 | 37 |
| 9.2 | 9.2.1 | 9.4.1 | 17 | 36.0.0 | 28.2.13676358 | 37 |
| 9.3 | 9.3.1 | 9.5.0 | 17 | 36.0.0 | 28.2.13676358 | 37 |

### Kotlin / IDE compatibility

| 項目 | 8.7 系 | 9.0 以降 | 確認方法 |
| --- | --- | --- | --- |
| Kotlin Android | 外部 `org.jetbrains.kotlin.android` plugin | Built-in Kotlin が既定 | plugin 適用と resolved dependency を確認 |
| KGP | 対象プロジェクト側で選択 | AGP 9.0 の runtime baseline は 2.2.10 | 使用する AGP minor の release notes と dependency report |
| KAPT | Kotlin KAPT plugin | KSP 推奨、移行中は同じ AGP version の `com.android.legacy-kapt` | annotation processor inventory |
| KMP | KMP plugin と従来 Android plugin の組み合わせ | KMP plugin + Android KMP library plugin を個別確認 | KMP module ごとに plugin compatibility を検証 |
| Android Studio | Ladybug は AGP 8.7 まで | Quail 2（2026.1.2）は AGP 7.1〜9.3 | 公式 IDE / AGP compatibility |

注記:

- 表の Gradle は各 AGP 系列の公式な必須バージョンであり、任意の最新版 Gradle を意味しない。
- 最大 API level は利用可能な `compileSdk` の上限であり、`targetSdk` の更新要求ではない。
- API 37.0 の最小 AGP は 9.1.1、API 36.1 は 8.13.0、API 36 は 8.9.1、API 35 は 8.6.0 である。
- JDK 17 は最低要件である。CI と開発端末では Gradle daemon が実際に使用する JDK を確認する。

## 5. Change Inventory

| ID | 変更 | 初出 | 区分 | Deep Dive | 主な影響 |
| --- | --- | --- | --- | --- | --- |
| AGP-01 | Gradle / Build Tools / NDK / API 上限の更新 | 各版 | compatibility | Yes | 全 module、CI |
| AGP-02 | `finalizeDsl` の型指定が必須 | 8.10 | source breaking | Yes | convention plugin、custom plugin |
| AGP-03 | unit test resource で test manifest を merge 可能 | 8.12 | behavior | Conditional | unit test module |
| AGP-04 | API 36.1 と Kotlin 2.3 対応 | 8.13 | compatibility | Conditional | compileSdk、Kotlin |
| AGP-05 | 新 DSL が既定、内部実装型と旧 Variant API を非公開化 | 9.0 | breaking | Yes | build-logic、plugin |
| AGP-06 | Built-in Kotlin が既定 | 9.0 | breaking | Yes | Kotlin Android module、KAPT |
| AGP-07 | 複数の既定値変更 | 9.0 | behavior | Yes | 全 Android module |
| AGP-08 | DSL、Variant API、feature、task、property の削除 | 9.0 | breaking | Yes | build-logic、Wear、APK packaging |
| AGP-09 | consumer の compileSdk 検証強化 | 9.0 | compatibility | Yes | Android library |
| AGP-10 | R8 の unnamed package への再配置が既定 | 9.1 | behavior | Yes | minified build、reflection |
| AGP-11 | R8 `-keepattributes` wildcard の解釈厳格化 | 9.2 | behavior | Yes | minified build |
| AGP-12 | test / coverage report aggregation | 9.2 | experimental | No | CI report |
| AGP-13 | R8 config analyzer task | 9.3 | tooling | Yes | app module |
| AGP-14 | 新 `optimization` DSL と keep rule source set | 9.3 | API / tooling | Conditional | optimized app/library |
| AGP-15 | 9.3.1 patch。public fixed issue の掲載なし | 9.3.1 | patch | No | 追加の公開変更がないため、stable baseline の patch 固定だけ更新 |

### Deep Dive しない変更

8.8、8.9、8.11 の個別 bug fix と、各 patch release の全 issue は inventory の入口だけ確認し、対象プロジェクトが未指定のため一件ずつ深掘りしていない。該当するビルド失敗、Lint、R8、resource processing の症状がある場合に issue 単位で再調査する。

## 6. 主要差分の詳細

### 6.1 AGP 8.10: `finalizeDsl` の型

AGP API を利用する custom plugin では、`finalizeDsl` callback の receiver / parameter を具体的な DSL 型として扱う必要がある。型推論や内部実装型に依存した build logic は source compile error になる可能性がある。

対象候補:

- `buildSrc`
- included build の convention plugin
- 社内 Gradle plugin
- AGP API を直接利用する third-party plugin

検出:

```bash
rg -n "finalizeD[Ss]l|CommonExtension<|ApplicationExtension|LibraryExtension" \
  buildSrc build-logic .
```

### 6.2 AGP 8.12: unit test resource と manifest

`includeAndroidResources` を使う unit test で、test source directory の manifest を merge できる。test manifest を既に置いている場合は、実行環境、resource、component 宣言の見え方が変わる可能性がある。

これは全アプリの production behavior を変える変更ではなく、該当設定を持つ unit test に限定される。

### 6.3 AGP 9.0: 新 DSL と Variant API

AGP 9.0 は public DSL interface のみを既定で公開し、旧 API や AGP 内部実装型への依存を表面化させる。

代表的な移行:

| 旧方式 | 移行先 |
| --- | --- |
| `applicationVariants` / `libraryVariants` | `androidComponents.onVariants` |
| `variantFilter` | `androidComponents.beforeVariants` |
| SDK component への旧アクセス | `androidComponents.sdkComponents` |
| `ComponentBuilder.enabled` | `ComponentBuilder.enable` |
| `finalizeDSl` | `finalizeDsl` |
| legacy transform API | Artifact API または instrumentation API |

一時的な global opt-out として `android.newDsl=false` が提供されるが、AGP 10 で削除予定である。これは互換性確認や段階移行のための退避策であり、完了状態にしない。

### 6.4 AGP 9.0: Built-in Kotlin

Built-in Kotlin が既定で有効となる。一般的な Android Kotlin module では次を確認する。

- `org.jetbrains.kotlin.android` / `kotlin-android` を削除する
- `android.kotlinOptions` を新しい Kotlin compiler options に移す
- Kotlin source set の設定場所を確認する
- KAPT は KSP へ移すか、移行まで `com.android.legacy-kapt` を利用する
- KSP の互換バージョンを確認する

AGP 9.0 の runtime KGP baseline は 2.2.10 で、古い KSP plugin は互換版へ更新される。Kotlin Multiplatform module は built-in Kotlin の単純な置き換え対象ではなく、KMP plugin と Android KMP library plugin の互換性を別途確認する。

一時 opt-out は `android.builtInKotlin=false` であり、`android.newDsl=false` も必要となる。これらは AGP 10 で利用できなくなる予定のため、恒久対応として扱わない。

### 6.5 AGP 9.0: 既定値変更

| property / behavior | 8.x | 9.0+ | 確認点 |
| --- | --- | --- | --- |
| `android.newDsl` | false | true | build logic の public API 化 |
| `android.builtInKotlin` | false | true | Kotlin plugin / KAPT / compiler options |
| `android.uniquePackageNames` | false | true | library namespace / package の衝突 |
| `android.useAndroidx` | false | true | legacy support library の残存 |
| `android.default.androidx.test.runner` | false | true | instrumentation runner |
| `android.dependency.useConstraints` | true | false | dependency resolution |
| `android.enableAppCompileTimeRClass` | false | true | app の R が non-final になるコード経路 |

特に app の compile-time R class 変更では、resource ID を Java / Kotlin の compile-time constant とみなす `switch` / annotation 引数などを検出する。

### 6.6 AGP 9.0: 削除された feature、task、API

代表例:

- embedded Wear OS app と `wearApp`
- density split APK。配布では Android App Bundle を利用する
- `androidDependencies`、`sourceSets` report task
- `AndroidSourceSet.jni`
- `DependencyVariantSelection`
- PostProcessing block
- `LanguageSplitOptions`、`DensitySplit`
- `registerTransform` を含む legacy transform API
- `android.defaults.buildfeatures.aidl`
- `android.defaults.buildfeatures.renderscript`

また、次の property を設定したままでは AGP 9.0 が error にする。

- `android.r8.integratedResourceShrinking`
- `android.enableNewResourceShrinker.preciseShrinking`

AIDL / RenderScript の build feature が必要な module は、global property ではなく module の `android.buildFeatures` へ明示する。

### 6.7 AGP 9.0: library consumer の compileSdk

Android library の consumer は、原則として library と同じかそれ以上の `compileSdk` が必要になる。library producer が本当に要求する最低値は AAR metadata の `minCompileSdk` で明示できる。

これは `targetSdk` 更新とは別である。AGP update PR に Android OS behavior change の採用を混ぜず、必要な compileSdk 変更だけを根拠付きで分離する。

### 6.8 AGP 9.1: R8 package 再配置

R8 は、明示的な `-flattenpackagehierarchy` または `-repackageclasses` がない場合、既定で class を unnamed package へ再配置する。opt-out は `-dontrepackage` である。

影響候補:

- class name / package name を文字列で扱う reflection
- JNI から class 名を参照するコード
- serialization や plugin discovery
- stack trace / mapping の運用
- package-private access を前提にした特殊な構成

`-dontrepackage` はまず原因切り分けに利用し、必要性を確認せず恒久追加しない。

### 6.9 AGP 9.2: R8 `-keepattributes`

`-keepattributes` の wildcard pattern は runtime invisible annotation を暗黙に保持しなくなる。実行時に必要な attribute / annotation は明示的な名前で保持する。

次を検査する。

- wildcard を多用する keep rule
- annotation-driven framework
- reflection、DI、serialization
- consumer ProGuard rule と app rule の重複・相互作用

### 6.10 AGP 9.2: report aggregation

統合 test / coverage dashboard は experimental であり、`android.experimental.reportAggregationSupport=true` で試行する。stable migration の必須作業ではないため、CI report 改修とは別 PR にする。

### 6.11 AGP 9.3: R8 analyzer と optimization DSL

AGP 9.3 は app module に standalone R8 configuration analyzer task を提供する。

```bash
./gradlew :app:analyzeReleaseR8Config
```

また、新しい `optimization` DSL と `src/<variant>/keepRules/*.keep` source set が追加された。legacy 設定も継続サポートされるため、AGP version update と同時に全 keep rule を書き換える必要はない。まず analyzer で broad rule、競合、不要 rule を検出し、最適化設定の整理を別変更として行う。

## 7. Minimum Required Versions と推奨値

### Minimum Required

AGP 9.3.1 を採用する場合:

| 項目 | 最低 / 必須値 |
| --- | --- |
| AGP | 9.3.1 |
| Gradle | 9.5.0 |
| JDK | 17 |
| Build Tools | 36.0.0 |
| 既定 NDK | 28.2.13676358 |
| 最大 compileSdk | API 37 |

### 推奨 baseline

この調査時点の stable baseline 候補は AGP 9.3.1 + Gradle 9.5.0 + JDK 17 である。ただし次はプロジェクト事情で決める。

- `compileSdk`: AGP だけを理由に API 37 へ上げない
- `targetSdk`: OS behavior change 調査と別に判断する
- `ndkVersion`: native module がある場合は暗黙の既定値に任せず、検証済みの版を明示する候補とする
- Kotlin / KSP / Compose compiler: version catalog と plugin の実使用状況に基づいて互換性を確認する

## 8. Change Isolation

| 変更 | AGP update と同一変更が必要か | 分離方針 |
| --- | --- | --- |
| Gradle wrapper 9.5.0 | Yes | AGP 9.3 と同じ移行段階で更新 |
| JDK 17 | Yes | 既に 17 なら CI 設定確認のみ |
| 旧 Variant API の移行 | 実質 Yes | version bump 前の準備 PR に分離可能 |
| Built-in Kotlin | 既定では Yes | 一時 opt-out で段階化可能だが最終的に移行 |
| KAPT → KSP | No | legacy-kapt を使って別 PR 化可能 |
| compileSdk / targetSdk 更新 | No | AGP 互換性上必要な compileSdk だけ例外 |
| NDK 更新 | native module のみ | explicit pin と native test を別 PR 候補 |
| R8 rule 整理 | No | analyzer 導入後の独立 PR |
| report aggregation | No | experimental 検証として独立 |

## 9. Breaking Change 分類

### Must Fix

- Gradle 9.5.0 と実行 JDK 17 を用意する
- build logic の旧 Variant API / 内部型依存を public API へ移す
- Kotlin Android plugin、KAPT、compiler options、source set を Built-in Kotlin に合わせる
- 削除された DSL、task、feature、property を除去または代替する
- `CommonExtension` の型引数など、AGP API の source breaking change を修正する
- KMP module がある場合、Android KMP plugin の対応を別途検証する

### Should Verify

- unique package name
- AndroidX test runner
- app R class の non-final 化
- AAR `minCompileSdk`
- R8 の package 再配置
- `-keepattributes` の明示性
- NDK r28c と CMake / JNI / prefab

### Optional / Separate

- AGP 9.2 の report aggregation
- AGP 9.3 の `optimization` DSL への書き換え
- keep rule source set への整理
- compileSdk / targetSdk の独立更新

## 10. Fact / Evidence / Confidence

| Fact | Evidence | Confidence |
| --- | --- | --- |
| 調査時点の最新 stable は AGP 9.3.1 | 公式 AGP 9.3 release notes | High |
| AGP 9.3 は Gradle 9.5.0、JDK 17 を要求する | 公式 9.3 compatibility | High |
| AGP 9.0 で新 DSL と Built-in Kotlin が既定になる | 公式 9.0 release notes / migration guide | High |
| 旧 opt-out は AGP 10 で削除予定 | 公式 roadmap / 9.0 documentation | High。ただし将来計画は変更可能 |
| AGP 9.1 で R8 の既定 package 再配置が変わる | 公式 9.1 release notes | High |
| AGP 9.2 で `-keepattributes` wildcard semantics が変わる | 公式 9.2 release notes | High |
| AGP 9.3 に R8 analyzer task がある | 公式 9.3 release notes / analyzer guide | High |
| 対象プロジェクトの移行リスクは High | 上記変更量からの解釈。実プロジェクト未確認 | Medium |

## Risk Level

| 項目 | 評価 |
| --- | --- |
| 総合 | High |
| Build logic | High。旧 DSL / Variant API / 内部型の利用量に依存 |
| Kotlin | High。Built-in Kotlin、KAPT、KMP の構成に依存 |
| Runtime | Medium〜High。R8、reflection、JNI の利用量に依存 |
| CI | Medium。Gradle、JDK、SDK image、cache の更新が必要 |
| 評価限界 | 対象プロジェクト未指定のため暫定 |

## 11. Detection Method

対象 repository root で次を実行する。

```bash
rg -n "applicationVariants|libraryVariants|testVariants|unitTestVariants|variantFilter|BaseExtension|CommonExtension<|registerTransform|finalizeDSl|transformClassesWith|setAsmFramesComputationMode" \
  --glob '*.gradle' --glob '*.gradle.kts' --glob '*.kt' --glob '*.java'

rg -n "org\.jetbrains\.kotlin\.android|kotlin-android|org\.jetbrains\.kotlin\.kapt|kotlin-kapt|android\.kotlinOptions|kotlinOptions|kotlin\.sourceSets" \
  --glob '*.gradle' --glob '*.gradle.kts' --glob '*.toml'

rg -n "android\.newDsl|android\.builtInKotlin|android\.uniquePackageNames|android\.enableAppCompileTimeRClass|android\.dependency\.useConstraints" \
  --glob 'gradle.properties' --glob '*.properties'

rg -n "wearApp|density|androidDependencies|sourceSets|android\.r8\.integratedResourceShrinking|preciseShrinking|android\.defaults\.buildfeatures" \
  --glob '*.gradle' --glob '*.gradle.kts' --glob '*.properties'

rg -n --glob '*.pro' --glob '*.rules' --glob '*.gradle' --glob '*.gradle.kts' \
  -- "-keepattributes|-repackageclasses|-flattenpackagehierarchy|-dontrepackage|minifyEnabled|isMinifyEnabled"

rg -n "externalNativeBuild|ndkVersion|CMakeLists|prefab" \
  --glob '*.gradle' --glob '*.gradle.kts' --glob 'CMakeLists.txt'
```

追加で、version catalog、included build、`buildSrc`、CI image、Dockerfile、IDE の Gradle JDK を確認する。

## 12. Affected Modules

| module / 領域 | 影響候補 |
| --- | --- |
| app | Built-in Kotlin、R class、R8、packaging、instrumentation |
| Android library | namespace、AAR metadata、consumer rule、compileSdk |
| dynamic feature | variant / flavor、packaging |
| Wear module | embedded Wear app の削除 |
| native module | NDK r28c、CMake、JNI、R8 と class 名 |
| `buildSrc` / `build-logic` | DSL、Variant API、AGP API source compatibility |
| KMP module | Kotlin / Android plugin architecture |
| CI | Gradle 9.5、JDK 17、Build Tools 36、cache key、report |

## 13. Verification Commands

プロジェクトの実在 task に合わせて調整する。

```bash
./gradlew --version
./gradlew help
./gradlew projects
./gradlew tasks
./gradlew assembleDebug
./gradlew assembleRelease
./gradlew test
./gradlew lint
./gradlew connectedCheck
./gradlew :app:analyzeReleaseR8Config
```

native module がある場合:

```bash
./gradlew externalNativeBuildDebug
./gradlew externalNativeBuildRelease
```

## 14. Test Scope

- Gradle configuration cache を含む configuration phase
- 全 build type / product flavor / dynamic feature
- debug / release の assemble と bundle
- unit test、Android resources を含む unit test
- instrumentation test と runner
- Lint
- minified release の起動、主要導線、reflection / serialization
- APK / AAB の resource、manifest、native library、mapping
- JNI / NDK / prefab / CMake
- CI の cache、report、artifact upload

## Investigation Exit Criteria

- 公式 release notes と compatibility の inventory が揃っている
- Must Fix / Should Verify / Optional が分離されている
- minimum version と推奨 baseline が分離されている
- 検出、影響 module、検証、rollback、PR 分割が記録されている
- 実プロジェクト適用時は静的検出と全対象 task の結果が追記されている

## 15. Rollback Plan

1. 変更前の AGP / Gradle / JDK / Kotlin / NDK の組み合わせを記録する。
2. version bump、build logic、Built-in Kotlin、R8 rule、native 対応を別 commit / PR に分ける。
3. 各段階で戻せるよう wrapper と plugin version を同じ rollback 単位にする。
4. `android.newDsl=false`、`android.builtInKotlin=false`、`-dontrepackage` は原因切り分け用に限定し、使用理由と削除期限を記録する。
5. rollback 後に baseline の assemble、test、lint、release artifact hash / size を再確認する。

## 16. PR Strategy

以下は対象プロジェクト未確認時の候補であり、最終方針ではない。

1. **診断 PR**: 旧 API、Kotlin plugin、削除 property、R8 / native usage を inventory 化する。
2. **8.x 準備 PR**: public DSL / Variant API へ先行移行し、可能なら AGP 8.13.2 + Gradle 8.13 で安定させる。
3. **9.0 境界 PR**: AGP 9.0.1 + Gradle 9.1.0 へ更新し、一時 opt-out が必要なら期限付きで記録する。
4. **Kotlin PR**: Built-in Kotlin へ移行し、KAPT / KSP と compiler options を整理する。
5. **最新 stable PR**: AGP 9.3.1 + Gradle 9.5.0 へ更新する。
6. **最適化 PR**: R8 analyzer の結果に基づき keep rule と optimization DSL を整理する。
7. **別テーマ**: compileSdk / targetSdk、NDK pin、experimental report は独立して判断する。

小規模で旧 API が存在しないプロジェクトでは中間 version を省略できる。省略可否は検出結果と CI の再現性で判断する。

## Follow-up Tasks

- [ ] 対象プロジェクトで detection command を実行する
- [ ] third-party Gradle plugin の AGP 9.3 対応表を作る
- [ ] Kotlin / KSP / KMP の実 version で compatibility を確認する
- [ ] minified release と native build の runtime test を追加する
- [ ] AGP 9.4 stable 公開時に preview watch を再評価する

## Decision Log

| 日付 | 判断 | 根拠 | Owner |
| --- | --- | --- | --- |
| 未決定 | AGP 9.3.1 を候補とする | 2026-08-19 時点の最新 stable | Repository owner |

## 17. Research Complete Criteria

対象 project が未指定でも満たせる調査成果物の完成条件である。project 固有の command 実行は Follow-up Tasks とし、Research Complete を妨げない。

- [x] 公式 release notes を 8.7 から 9.3 まで確認した
- [x] change inventory を作成した
- [x] deep dive 対象と見送り理由を記録した
- [x] compatibility matrix を作成した
- [x] minimum と推奨 baseline を分離した
- [x] breaking change を分類した
- [x] affected modules を列挙した
- [x] detection method を記録した
- [x] verification commands と test scope を記録した
- [x] rollback plan と PR 分割案を記録した

Status: **Research Complete / Pending Human Decision**

## 18. Facts / Observations / Hypotheses / Conclusions

### Facts

- AGP 9.3.1 が調査時点の最新 stable である。
- AGP 9.3.1 は Gradle 9.5.0 と JDK 17 を要求する。
- AGP 9.0 で新 DSL と Built-in Kotlin が既定になる。
- AGP 9.1、9.2 で R8 の挙動変更がある。

### Observations

- 8.8 から 8.13 は互換 version が段階的に上がる一方、移行リスクは AGP 9.0 に集中している。
- AGP 9.3 の analyzer は、9.1 / 9.2 の R8 変更を検査する入口として利用できる。

### Hypotheses

- custom convention plugin、KAPT、minified release、native build を多用するプロジェクトほど移行工数が増える。
- 標準的な application module だけで旧 Variant API を使わない場合、段階数を減らせる可能性がある。

### Conclusions

AGP 8.7 系から 9.3.1 への更新は major migration として扱う。まず静的検出で AGP 9.0 の境界条件を可視化し、build logic、Kotlin、R8、native を分離して検証する。

## References

### Official Documentation

この調査で利用した全 minor の release notes と公式 migration guide は [Entry Point](#3-entry-point) に列挙した。

### Source Code

Build System 調査では公式 release notes と compatibility を一次 evidence とした。AOSP / tools-base source diff は、対象プロジェクト固有の未解決挙動がないため実施していない。

### Issue

個別 issue の深掘りは未実施。対象プロジェクトで該当症状が検出された場合に、各 release notes の Fixed Issues から追跡する。

### Validation

文書内リンクと Markdown whitespace は確認済み。対象プロジェクトの build validation は未実施。

## 19. Human Decision

Repository owner が決める項目:

- [ ] AGP 9.3.1 を移行先にするか
- [ ] AGP 8.13.2 / 9.0.1 を経由するか
- [ ] 一時 opt-out を許可するか、許可する場合の削除期限
- [ ] Built-in Kotlin と KAPT / KSP 移行の PR 構成
- [ ] compileSdk / targetSdk / NDK を同時に変更するか
- [ ] release readiness、最終優先度、顧客説明の要否
