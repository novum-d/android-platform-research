# AGP 8.7 系から 9.3.0 への移行チェックリスト

## Summary

AGP 8.7 系から 9.3.0 への更新を、AGP 9.0 の新 DSL、Built-in Kotlin、削除 API、R8 変更を含めて検出・実装・検証する。

## Scope

- Android application / library / dynamic feature / Wear / native / KMP module
- `buildSrc`、included build、convention plugin
- Gradle wrapper、JDK、SDK / NDK、CI

関連資料:

- [詳細差分](../versions/agp-8.7-to-9.3.md)
- [1ページサマリ](../summaries/agp-8.7-to-9.3-summary.md)
- [公式 AGP 9.3 release notes](https://developer.android.com/build/releases/agp-9-3-0-release-notes)

## 0. Human Decision

- [ ] 移行先を AGP 9.3.0 とする
- [ ] 直接更新か、8.13.2 / 9.0.1 を経由するか決める
- [ ] 一時 opt-out の可否と削除期限を決める
- [ ] compileSdk / targetSdk / NDK 更新を分離するか決める
- [ ] PR 分割と rollback owner を決める

## 1. Baseline

- [ ] 現在の AGP、Gradle、JDK、Kotlin、KSP、NDK、Build Tools を記録する
- [ ] `./gradlew --version` の結果を保存する
- [ ] debug / release assemble、test、lint の baseline を保存する
- [ ] release artifact の size、mapping、主要画面の smoke test 結果を保存する
- [ ] CI image、Gradle JDK、cache key、artifact task を記録する
- [ ] working tree と lockfile の状態を記録する

## 2. Static Detection

### DSL / Variant API

```bash
rg -n "applicationVariants|libraryVariants|testVariants|unitTestVariants|variantFilter|BaseExtension|CommonExtension<|registerTransform|finalizeDSl|transformClassesWith|setAsmFramesComputationMode" \
  --glob '*.gradle' --glob '*.gradle.kts' --glob '*.kt' --glob '*.java'
```

- [ ] `buildSrc` を確認した
- [ ] included build / convention plugin を確認した
- [ ] 社内 / third-party Gradle plugin の AGP 9 対応を確認した
- [ ] `applicationVariants` / `libraryVariants` を `androidComponents.onVariants` へ移す対象を記録した
- [ ] `variantFilter` を `beforeVariants` へ移す対象を記録した
- [ ] legacy transform API を Artifact / instrumentation API へ移す対象を記録した

### Kotlin / KAPT / KSP

```bash
rg -n "org\.jetbrains\.kotlin\.android|kotlin-android|org\.jetbrains\.kotlin\.kapt|kotlin-kapt|android\.kotlinOptions|kotlinOptions|kotlin\.sourceSets" \
  --glob '*.gradle' --glob '*.gradle.kts' --glob '*.toml'
```

- [ ] Kotlin Android plugin の適用箇所を記録した
- [ ] KAPT processor と KSP 対応状況を記録した
- [ ] compiler options と source set の移行対象を記録した
- [ ] KMP module を通常の Android Kotlin module と分離して確認した

### Property / Removed Feature

```bash
rg -n "android\.newDsl|android\.builtInKotlin|android\.uniquePackageNames|android\.enableAppCompileTimeRClass|android\.dependency\.useConstraints|wearApp|androidDependencies|android\.r8\.integratedResourceShrinking|preciseShrinking|android\.defaults\.buildfeatures" \
  --glob '*.gradle' --glob '*.gradle.kts' --glob '*.properties'
```

- [ ] 削除 property を除去する
- [ ] AIDL / RenderScript が必要なら module の `buildFeatures` に移す
- [ ] embedded Wear app を独立 app / 配布方式へ移す
- [ ] density split を App Bundle ベースへ移す
- [ ] 削除 report task を CI が参照していないか確認する

### R8 / Optimization

```bash
rg -n --glob '*.pro' --glob '*.rules' --glob '*.gradle' --glob '*.gradle.kts' \
  -- "-keepattributes|-repackageclasses|-flattenpackagehierarchy|-dontrepackage|minifyEnabled|isMinifyEnabled"
```

- [ ] reflection、DI、serialization、JNI の class name 依存を確認する
- [ ] runtime に必要な annotation / attribute を明示する
- [ ] `-dontrepackage` を使う場合、理由と削除条件を記録する
- [ ] consumer rule と app rule を両方確認する

### Native

```bash
rg -n "externalNativeBuild|ndkVersion|CMakeLists|prefab" \
  --glob '*.gradle' --glob '*.gradle.kts' --glob 'CMakeLists.txt'
```

- [ ] native module の有無を記録する
- [ ] NDK 28.2.13676358 での build / runtime 検証要否を記録する
- [ ] NDK を pin するか決める

## 3. Compatibility Update

- [ ] AGP を 9.3.0 へ更新する
- [ ] Gradle wrapper を 9.5.0 へ更新する
- [ ] Gradle daemon / CI の JDK 17 を確認する
- [ ] Build Tools 36.0.0 の取得方法を確認する
- [ ] plugin portal / repository / dependency verification を確認する
- [ ] Android Studio が AGP 9.3 をサポートする版であることを確認する

## Minimum Required Versions

| 項目 | 値 |
| --- | --- |
| AGP | 9.3.0 |
| Gradle | 9.5.0 |
| JDK | 17 |
| Build Tools | 36.0.0 |
| 最大 API level | 37 |

## File Changes

- [ ] plugin version / version catalog
- [ ] `gradle-wrapper.properties`
- [ ] root / module build script
- [ ] `gradle.properties`
- [ ] `buildSrc` / `build-logic`
- [ ] Kotlin / KAPT / KSP 設定
- [ ] R8 / consumer keep rule
- [ ] CI image / workflow / cache key

## 4. AGP 9.0 Migration

- [ ] build logic を public DSL interface のみで compile できる
- [ ] Variant API を `androidComponents` ベースへ移した
- [ ] `CommonExtension` の型引数など source breaking change を修正した
- [ ] Built-in Kotlin で全 Android Kotlin module が compile できる
- [ ] `org.jetbrains.kotlin.android` を重複適用していない
- [ ] KAPT を KSP または `com.android.legacy-kapt` へ移した
- [ ] `android.kotlinOptions` と source set を移した
- [ ] app の non-final R で compile できる
- [ ] unique package と test runner の既定値を確認した
- [ ] library の `minCompileSdk` / consumer `compileSdk` を確認した

一時退避を使う場合:

- [ ] `android.newDsl=false` の理由、owner、削除期限を記録した
- [ ] `android.builtInKotlin=false` の理由、owner、削除期限を記録した
- [ ] AGP 10 前に opt-out を除去する tracking issue を作成した

## 5. Build Verification

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

- [ ] 全 build type / flavor / dynamic feature を検証した
- [ ] unit test と Android resources を使う unit test を検証した
- [ ] instrumentation runner と connected test を検証した
- [ ] minified release の主要導線を検証した
- [ ] mapping / resource / manifest / native library を確認した
- [ ] native build と JNI runtime を確認した
- [ ] configuration cache の利用状況を確認した
- [ ] CI cache、report、artifact upload を確認した

## 6. R8 Verification

- [ ] `:app:analyzeReleaseR8Config` の結果を保存した
- [ ] AGP 9.1 の package 再配置による runtime regression がない
- [ ] AGP 9.2 の `-keepattributes` 変更による regression がない
- [ ] stack trace deobfuscation を確認した
- [ ] broad keep rule の整理は version update と別 PR にした

## Test Scope

- [ ] 全 application / library / dynamic feature module
- [ ] 全 build type / product flavor
- [ ] unit test / instrumentation test / Lint
- [ ] debug / release / minified release
- [ ] reflection / DI / serialization / JNI
- [ ] native build / prefab / packaging
- [ ] CI configuration / cache / report / artifact

## 7. Rollback

- [ ] AGP / Gradle wrapper を同じ rollback 単位にした
- [ ] build logic migration を独立して revert できる
- [ ] Built-in Kotlin migration を独立して revert できる
- [ ] R8 / native 対応を独立して revert できる
- [ ] rollback 後に baseline task が再現する

## 8. Completion Record

| 項目 | 記録 |
| --- | --- |
| 実施日 | |
| 実施者 | |
| 対象 branch / commit | |
| 最終 AGP / Gradle / JDK | |
| 残存 opt-out | |
| 未解決 issue | |
| rollback commit / tag | |
| Human Decision | |

## Decision Log

| 日付 | 判断 | 根拠 | Owner |
| --- | --- | --- | --- |
| | | | |

## Completion Criteria

- [ ] Must Fix をすべて解消した
- [ ] 一時 opt-out に owner と削除期限がある
- [ ] 対象 module の build / test / lint が成功した
- [ ] minified release と native runtime を必要範囲で検証した
- [ ] rollback を確認した
- [ ] 未解決 issue と Human Decision を記録した

## Follow-up Tasks

- [ ] R8 analyzer の指摘を別 PR で整理する
- [ ] compileSdk / targetSdk の更新を別調査へ接続する
- [ ] AGP 9.4 stable 公開時に追加差分を確認する

## References

### Official Documentation

- [AGP 9.3 release notes](https://developer.android.com/build/releases/agp-9-3-0-release-notes)
- [AGP 9.0 release notes](https://developer.android.com/build/releases/agp-9-0-0-release-notes)
- [AGP / Gradle compatibility](https://developer.android.com/build/releases/about-agp)
- [Built-in Kotlin への移行](https://developer.android.com/build/migrate-to-built-in-kotlin)
- [Variant API](https://developer.android.com/build/extend-agp)

### Validation

実行した command、CI run、artifact の参照を Completion Record に追記する。
