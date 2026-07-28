# AGP 9.4 preview 監視資料

## Status

| 項目 | 内容 |
| --- | --- |
| 確認日 | 2026-07-28 |
| 最新確認版 | AGP 9.4.0-alpha04 |
| Channel | Preview / alpha |
| stable migration target | No |
| 比較 baseline | AGP 9.3.0 |
| Confidence | High（公開済み preview の事実）、Medium（将来の stable 仕様） |

AGP 9.4.0-alpha04 は調査時点の preview であり、[AGP 8.7 系から 9.3.0 までの差分調査](agp-8.7-to-9.3.md)の推奨 stable target には含めない。この資料は先行検証と AGP 10 に向けた準備のための watch list である。

## Entry Point と References

- [AGP 9.4 release notes](https://developer.android.com/build/releases/agp-9-4-0-release-notes)
- [AGP roadmap](https://developer.android.com/build/releases/gradle-plugin-roadmap)
- [AGP / Gradle compatibility](https://developer.android.com/build/releases/about-agp)
- [Built-in Kotlin への移行](https://developer.android.com/build/migrate-to-built-in-kotlin)

## Compatibility

| 項目 | AGP 9.3.0 | AGP 9.4.0-alpha04 |
| --- | --- | --- |
| Gradle | 9.5.0 | 9.6.0 |
| JDK | 17 | 17 |
| Build Tools | 36.0.0 | 36.0.0 |
| 既定 NDK | 28.2.13676358 | 28.2.13676358 |
| 最大 API level | 37 | 37 |

preview の互換要件は stable 公開まで変わる可能性がある。検証 branch では release notes の対象 alpha と Gradle wrapper を固定する。

## Change Inventory

| ID | 変更 | 分類 | 影響候補 | Confidence |
| --- | --- | --- | --- | --- |
| 9.4-P1 | 新 DSL の module 単位 opt-out | migration aid | multi-module build | High |
| 9.4-P2 | dynamic feature の flavor dimension parity 検証 | behavior / future breaking | dynamic feature | High |
| 9.4-P3 | AGP 10 で旧 DSL / Built-in Kotlin opt-out を削除予定 | roadmap | 全 Android module | Medium |

## 主要差分

### Module 単位の新 DSL opt-out

AGP 9.4 preview では、新 DSL から一時的に除外する module を指定できる。

```properties
android.newDsl.optOut=:example-lib1
```

これは multi-module migration を段階化するための一時機構である。利用する場合は次を必須記録とする。

- 除外 module
- block している旧 API / plugin
- owner
- 削除期限
- opt-out なしで実行する CI job

global の `android.newDsl=false` と同様、恒久対応として扱わない。

### Dynamic feature の variant matching

base app と dynamic feature の flavor dimension が厳密な 1:1 対応でない構成に warning が追加される。先行して error として検証する property:

```properties
android.enforceDynamicFeatureVariantMatching=true
```

AGP 10 では fatal が既定になる予定とされているため、dynamic feature を持つ project は AGP 9.4 の採用有無にかかわらず flavor dimension と flavor の対応表を作る。

確認点:

- base app と全 dynamic feature の `flavorDimensions`
- dimension ごとの flavor 名
- missing dimension / fallback 設定
- CI が実際に生成する variant
- Play 配布用 bundle の module 組み合わせ

## Detection

```bash
rg -n "android\.newDsl|android\.builtInKotlin|android\.newDsl\.optOut" \
  --glob '*.properties' --glob '*.gradle' --glob '*.gradle.kts'

rg -n "com\.android\.dynamic-feature|flavorDimensions|flavorDimensionList|productFlavors|matchingFallbacks|missingDimensionStrategy" \
  --glob '*.gradle' --glob '*.gradle.kts'
```

## Preview Verification

preview 専用 branch / CI job で次を実施する。

```bash
./gradlew --version
./gradlew help
./gradlew projects
./gradlew assembleDebug
./gradlew bundleRelease
./gradlew test
./gradlew lint
```

- [ ] AGP 9.4 alpha と Gradle 9.6.0 を固定した
- [ ] production release branch に preview を混ぜていない
- [ ] module opt-out の理由と削除条件を記録した
- [ ] dynamic feature variant warning を収集した
- [ ] `android.enforceDynamicFeatureVariantMatching=true` で検証した
- [ ] alpha 更新ごとに release notes と既知問題を再確認した

## Rollback

- preview 用 version catalog / wrapper change を単独 commit にする
- preview 専用 branch または CI matrix entry に限定する
- stable AGP 9.3.0 + Gradle 9.5.0 の job を残す
- preview 固有 property を production 設定へ残さない

## Facts / Interpretation

### Facts

- 2026-07-28 時点で AGP 9.4 は alpha channel である。
- alpha04 の互換 Gradle は 9.6.0 である。
- module 単位の新 DSL opt-out と dynamic feature variant matching の検証が公開されている。

### Interpretation

- module opt-out は大規模 project の段階移行を容易にするが、技術的負債を固定化する可能性がある。
- dynamic feature の warning は AGP 10 前に直すべき構成不整合の早期検出として利用できる。

### Conclusion

AGP 9.4 preview を production の移行先にはしない。AGP 9.3.0 を stable baseline とし、9.4 は新 DSL の残存依存と dynamic feature variant の先行検証に使う。

## Human Decision

- [ ] preview CI job を追加するか
- [ ] module 単位 opt-out を試行するか
- [ ] dynamic feature parity を AGP 9.4 採用前に修正するか
- [ ] stable 昇格後の再調査担当と時期
