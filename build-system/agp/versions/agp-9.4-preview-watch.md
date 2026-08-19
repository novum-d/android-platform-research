# AGP 9.4 preview 監視資料

## 1. 調査メタデータ

| 項目 | 内容 |
| --- | --- |
| Entry Point | [AGP 9.4 Release Notes](https://developer.android.com/build/releases/agp-9-4-0-release-notes) |
| 確認日 | 2026-08-19 |
| 最新確認版 | AGP 9.4.0-rc01 |
| Channel | Preview / RC |
| stable migration target | No |
| stable baseline | AGP 9.3.1 |
| 対象プロジェクト | 未指定 |
| Project Verification | 未実施 |
| Confidence | High（公開済み preview と compatibility）、Medium（entry page の alpha05-rc01 inventory と将来 stable 仕様） |

Release Notes の page title は `Android Gradle plugin 9.4.0` だが、これだけでは stable の根拠にならない。2026-08-19 時点の[公式 AGP API Reference](https://developer.android.com/reference/tools/gradle-api)は Current Release を 9.3.1、Preview Releases を 9.4.0-rc01 としている。このため 9.4 は preview watch とし、production の推奨移行先にはしない。

この資料の artifact identity は `(9.4 release line, preview channel, preview watch)` である。将来の 9.4 stable version diff は別成果物として作成し、この記録を上書きしない。

## 2. Summary

AGP 9.4 preview の decision-relevant な変更は、Gradle 9.6.0 への更新、新 DSL / Variant API 移行を module 単位で段階化する一時 opt-out、base app と dynamic feature の flavor dimension parity 警告である。parity 不一致は 9.4 では warning だが、property で先行して error 化でき、AGP 10 では fatal が既定になると公式文書に記載されている。

rc01 の存在は公式 API Reference と Android Studio Quail 4 の release 情報で確認できる一方、AGP 9.4 entry page の Fixed Issues は alpha04 までしか掲載していない。この document drift が解消するまで、alpha05 から rc01 の AGP 固有差分を網羅したとは扱わない。

## 3. Investigation Entry Point

### Entry Point

- [Android Gradle plugin 9.4.0 Release Notes](https://developer.android.com/build/releases/agp-9-4-0-release-notes)

### Entry Point から抽出した範囲

- compatibility table
- Variant API module opt-out
- base app / dynamic feature の strict 1:1 variant parity
- alpha01-alpha04 の Fixed Issues

Release Notes は入口であり、release channel と最新版の確定には以下の Official References を追加で照合した。

## 4. Release Channel 判定

| 根拠 | 確認内容 | 判定 |
| --- | --- | --- |
| AGP 9.4 Release Notes | title は 9.4.0、Fixed Issues は alpha01-alpha04 | title 単独では stable を証明しない |
| AGP API Reference | Current Release 9.3.1、Preview Releases 9.4.0-rc01 | 9.4 は preview |
| Android Studio Quail 4 fixed issues | Canary と RC、alpha05-rc01 の同時 release を記録 | 最新確認版は rc01 |
| AGP 9.3 Release Notes | 9.3.1 に public fixed issue なし | stable baseline は 9.3.1 |

## 5. Compatibility Matrix

| 項目 | AGP 9.3.1 stable | AGP 9.4 preview | 影響 |
| --- | --- | --- | --- |
| Gradle minimum / default | 9.5.0 | 9.6.0 | wrapper と CI cache を同じ preview 検証単位で更新 |
| JDK minimum / default | 17 | 17 | daemon / CI が実際に使う JDK を確認 |
| SDK Build Tools minimum / default | 36.0.0 | 36.0.0 | 変更なし |
| NDK minimum / default | N/A / 28.2.13676358 | N/A / 28.2.13676358 | 変更なし。project pin は別判断 |
| 最大 API level | 37 | 37 | `compileSdk` 上限。`targetSdk` 更新要求ではない |
| Channel | Stable | Preview / RC | production target と preview CI を分離 |

### Minimum / Recommended

| Item | Minimum for preview test | Recommended | Notes |
| --- | --- | --- | --- |
| AGP | 9.4.0-rc01 を明示 pin | production は 9.3.1 のまま | dynamic version を使わない |
| Gradle | 9.6.0 | preview job のみ 9.6.0 | AGP と同じ rollback 単位 |
| JDK | 17 | project baseline に合わせて 17 を固定 | 実行 JDK を `--version` で確認 |
| Build Tools | 36.0.0 | 36.0.0 | |
| NDK | N/A | project の既存 pin を維持 | AGP preview と同時に任意更新しない |

## 6. Change Inventory

| ID | 変更 | Category | Deep Dive | 理由 / 影響候補 | Confidence |
| --- | --- | --- | --- | --- | --- |
| 9.4-P1 | Gradle 9.6.0 が minimum / default | Compatibility | Yes | 全 module、developer environment、CI | High |
| 9.4-P2 | `android.newDsl.optOut` による module 単位 opt-out | Migration aid / DSL | Yes | multi-module build、custom plugin | High |
| 9.4-P3 | app / dynamic feature の flavor dimension parity warning | Build behavior / future breaking | Yes | dynamic feature module | High |
| 9.4-P4 | `android.enforceDynamicFeatureVariantMatching=true` で error 化 | Verification control | Yes | AGP 10 readiness | High |
| 9.4-P5 | alpha03: L8 mapping issue 146403477 | R8 bug fix | Conditional | desugared library、mapping 運用時のみ | High |
| 9.4-P6 | alpha01/02: eager SigningConfig issue 499166350 | AGP bug fix | Conditional | signing configuration 症状がある場合のみ | High |
| 9.4-P7 | alpha02: dynamic feature provider issue 257765153 | Test / dynamic feature bug fix | Conditional | connected test + provider + dynamic feature | High |
| 9.4-P8 | alpha04: public fixed issue なし | Fixed issues | No | deep dive 対象がない | High |
| 9.4-P9 | alpha05-rc01 の AGP entry-page inventory 欠落 | Documentation drift | Yes | preview 差分の網羅性に影響 | Medium |

Fixed issue は対象プロジェクト未指定のため issue 本文まで一律に深掘りせず、症状と利用条件が一致した場合の追跡対象とする。tools/base source diff は、公式文書で decision-relevant な条件を説明できるため実施していない。

## 7. 主要差分

### 7.1 Module 単位の新 DSL / Variant API opt-out

AGP 10 では新 Variant API が全 project で必須になる予定であり、AGP 9.4 は移行途中の module を一時的に除外する property を提供する。

```properties
android.newDsl.optOut=:example-lib1
```

これは migration aid であり、完了状態ではない。利用時は次を project 側の issue / PR に記録する。

- 除外 module
- block している旧 API / third-party plugin
- owner
- 削除期限
- opt-out なしで実行する CI job

### 7.2 Dynamic feature の strict 1:1 variant parity

AGP 9.4 は base app と dynamic feature の flavor dimension が 1:1 で対応しない場合に warning を出す。missing、extra、mismatched dimension が対象である。

```properties
android.enforceDynamicFeatureVariantMatching=true
```

この property は warning を execution error に昇格する。AGP 10 では strict parity が既定で fatal になると entry page に明記されているため、dynamic feature を持つ project は production を 9.4 preview に上げなくても先行検査の価値がある。

### 7.3 Fixed issues

| Issue | 該当条件 | 検証候補 |
| --- | --- | --- |
| [146403477](https://issuetracker.google.com/issues/146403477) | core library desugaring / L8 と mapping.txt を利用 | mapping に L8 obfuscation mapping が含まれるか |
| [499166350](https://issuetracker.google.com/issues/499166350) | signing configuration の eager evaluation が症状に一致 | configuration phase、credential access、variant 別 signing |
| [257765153](https://issuetracker.google.com/issues/257765153) | dynamic feature に provider があり connected test を実行 | `connectedDebugAndroidTest` の provider class loading |

### 7.4 alpha05-rc01 documentation drift

公式 Android Studio Quail 4 page は AGP 9.4.0-alpha05 から rc01 が Canary / RC と同時 release されたことを示し、AGP API Reference も rc01 を preview としている。しかし AGP 9.4 entry page は alpha04 より新しい Fixed Issues を掲載していない。

したがって、次を分離する。

- Fact: rc01 が公式 preview として存在する。
- Observation: entry page の inventory は alpha04 で止まっている。
- Conclusion: alpha05-rc01 に変更がないとは結論しない。stable migration 判断にこの watch だけを使わない。

## 8. Breaking Changes Classification

| Classification | Change | Impact | Required Action |
| --- | --- | --- | --- |
| Must Fix | AGP 9.4 preview には Gradle 9.6.0 が必要 | sync / build failure | preview job の wrapper を同時更新 |
| Should Fix | dynamic feature の flavor dimension mismatch | 9.4 warning、AGP 10 fatal | parity 表を作り warning / error を解消 |
| Should Fix | module opt-out の残存 | AGP 10 migration blocker | owner と削除期限を設定 |
| Watch | alpha05-rc01 の entry-page inventory 欠落 | 変更網羅性が不十分 | 公式 page 更新時に再確認 |
| No Action | dynamic feature を持たない project の parity check | 該当 path なし | module 検出結果を記録 |

## 9. Risk Level

Risk: **Medium（preview 検証）**。

production へ採用しない前提では影響を preview branch / CI job に限定できる。dynamic feature の variant mismatch や旧 DSL / plugin 依存が見つかった場合は AGP 10 migration risk として別途扱う。対象 project が未指定のため、実際の module 別 risk は未評価である。

## 10. Affected Modules / Detection Method

| 候補 | Detection | 影響 |
| --- | --- | --- |
| 全 Android module / CI | plugin version、wrapper、`./gradlew --version` | Gradle 9.6.0 compatibility |
| `buildSrc` / `build-logic` / custom plugin | 旧 DSL / Variant API の検索 | module opt-out の要否 |
| dynamic feature | `com.android.dynamic-feature` の検索 | parity warning / future fatal |
| signing 利用 module | `signingConfigs` と provider 利用の確認 | issue 499166350 の該当性 |
| core library desugaring / minified app | desugaring と mapping 保存の確認 | issue 146403477 の該当性 |
| instrumentation test | provider を持つ dynamic feature | issue 257765153 の該当性 |

```bash
rg -n "android\.newDsl|android\.builtInKotlin|android\.newDsl\.optOut" \
  --glob '*.properties' --glob '*.gradle' --glob '*.gradle.kts'

rg -n "com\.android\.dynamic-feature|flavorDimensions|flavorDimensionList|productFlavors|matchingFallbacks|missingDimensionStrategy" \
  --glob '*.gradle' --glob '*.gradle.kts'

rg -n "signingConfigs|coreLibraryDesugaring|androidx\.startup\.InitializationProvider|<provider" \
  --glob '*.gradle' --glob '*.gradle.kts' --glob '*.xml'
```

## 11. Verification Commands / Test Scope

以下は実行候補であり、この repository では対象 project がないため未実行である。

```bash
./gradlew --version
./gradlew help
./gradlew projects
./gradlew assembleDebug
./gradlew bundleRelease
./gradlew test
./gradlew lint
./gradlew connectedDebugAndroidTest
```

dynamic feature がある場合:

1. 通常設定で parity warning を収集する。
2. preview 専用設定で `android.enforceDynamicFeatureVariantMatching=true` を有効にする。
3. 全 flavor / build type と Play 配布用 bundle を検証する。

Test Scope 候補:

- Gradle configuration / configuration cache
- 全 application / library / dynamic feature module
- debug / release / minified release
- unit / instrumentation / connected test
- signing / bundle / mapping artifact
- CI cache / artifact upload

## 12. Change Isolation / PR Strategy

- production version update と preview 検証を同じ PR にしない。
- preview AGP と Gradle 9.6.0 は専用 branch または CI matrix entry で同じ rollback 単位にする。
- flavor parity 修正は、可能なら stable baseline で先に適用する。
- module opt-out を追加する変更と、旧 API / plugin を移行して opt-out を削除する変更を追跡可能にする。
- compileSdk、targetSdkVersion、Kotlin、NDK、依存 library の任意更新を混ぜない。

## 13. Rollback Plan

1. preview 用 plugin version と wrapper change を単独 commit にする。
2. stable AGP 9.3.1 + Gradle 9.5.0 の CI job を残す。
3. preview 固有 property を production 設定へ残さない。
4. rollback 後に baseline の assemble、test、lint、bundle を再実行する。
5. preview で見つけた parity 問題の修正は、stable でも有効なら独立 PR として維持できるようにする。

## 14. Evidence

| Fact | Evidence | Confidence |
| --- | --- | --- |
| 9.4 は rc01 preview で、current stable は 9.3.1 | AGP API Reference | High |
| 9.4 の minimum/default Gradle は 9.6.0 | AGP 9.4 Release Notes compatibility table | High |
| module opt-out が提供される | AGP 9.4 Release Notes / AGP roadmap | High |
| dynamic feature parity は 9.4 で warning、AGP 10 で fatal default | AGP 9.4 Release Notes | High |
| alpha05-rc01 が release されている | Android Studio Quail 4 fixed-issues page / AGP API Reference | High |
| alpha05-rc01 の AGP 固有 inventory は entry page から確定できない | AGP 9.4 Release Notes と上記公式一覧の比較 | Medium |
| 対象 project への影響 | Project 未指定・未検証 | Low / Unknown |

## 15. Facts / Observations / Hypotheses / Conclusions

### Facts

- 2026-08-19 時点で AGP 9.4 は preview、最新版は rc01、stable は 9.3.1 である。
- preview compatibility は Gradle 9.6.0、JDK 17、Build Tools 36.0.0、既定 NDK 28.2.13676358、最大 API 37 である。
- module opt-out と dynamic feature parity check が公式に文書化されている。

### Observations

- AGP 9.4 entry page と公式の preview version 表の更新範囲が一致していない。
- 9.4 の主要機能は、AGP 10 の breaking enforcement を前倒しで検出する性質が強い。

### Hypotheses

- dynamic feature と多段の convention plugin を持つ project ほど先行検証の価値が高い。
- alpha05-rc01 の追加差分は entry page 更新後に inventory が増える可能性がある。

### Conclusions

AGP 9.4 preview を production migration target にしない。stable 9.3.1 を baseline とし、preview は module opt-out 依存と dynamic feature parity を発見する専用 CI に限定する。stable 昇格または entry page の inventory 更新時に再調査する。

## 16. Follow-up Tasks

| Task | Trigger | Status |
| --- | --- | --- |
| alpha05-rc01 の AGP change inventory を再確認 | AGP 9.4 entry page 更新 | Pending |
| preview CI で parity error mode を実行 | 対象 project が指定され、dynamic feature が検出された場合 | Pending |
| module opt-out の対象と期限を記録 | opt-out が必要と判明した場合 | Pending |
| stable version diff / summary / checklist を新規作成 | 公式 API Reference が 9.4.x を Current Release とした場合 | Pending |

## 17. Research Complete Criteria

- [x] Entry Point と References を分離した
- [x] release channel を複数の公式情報で確定した
- [x] entry-page inventory 全件へ Deep Dive 要否と理由を付けた
- [x] compatibility、Minimum / Recommended、breaking classification を記録した
- [x] document drift と confidence への影響を記録した
- [x] Affected Modules、Detection、Verification、Test Scope、Rollback、PR Strategy を記録した
- [x] project 未指定・commands 未実行を明記した
- [x] Facts / Observations / Hypotheses / Conclusions を分離した
- [x] Human Decision を owner に残した

この watch は Research Complete である。preview の変化を固定するものではなく、stable 昇格と公式 inventory 更新を follow-up trigger とする。

## 18. Human Decision

Status: **Pending Human Decision**

- preview CI job を追加するか
- module 単位 opt-out を許容するか、その削除期限
- dynamic feature parity を AGP 9.4 採用前に修正するか
- stable 昇格後の再調査担当と時期

## 19. References

### Official Documentation

- Entry Point: [AGP 9.4 Release Notes](https://developer.android.com/build/releases/agp-9-4-0-release-notes)
- [AGP API Reference](https://developer.android.com/reference/tools/gradle-api)
- [Android Studio Quail 4 fixed issues](https://developer.android.com/studio/releases/fixed-bugs/studio/2026.1.4)
- [AGP 9.3 Release Notes](https://developer.android.com/build/releases/agp-9-3-0-release-notes)
- [AGP DSL/API migration timeline](https://developer.android.com/build/releases/gradle-plugin-roadmap)
- [AGP / Gradle compatibility](https://developer.android.com/build/releases/about-agp)

### Source Code

- AOSP / tools-base: 未調査。公式文書で decision-relevant な条件を説明できるため不要と判断した。

### Issue

- [Issue 146403477](https://issuetracker.google.com/issues/146403477)
- [Issue 499166350](https://issuetracker.google.com/issues/499166350)
- [Issue 257765153](https://issuetracker.google.com/issues/257765153)

### Validation

- Target project / CI run: 未指定・未実施。
