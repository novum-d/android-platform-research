# ART internal changes 調査レポート

## 基本情報（Metadata）

### 調査対象 Android バージョン（Android Versions）

From:
- android-15.0.0_r36

To:
- android-16.0.0_r4

Note:

Previous targetSdkVersion:
- 35

Target targetSdkVersion:
- 36

### Behavior Change 文書（Behavior Change Source）

Document:
- https://developer.android.com/about/versions/16/behavior-changes-all#art-changes

Page:
- Behavior changes: all apps

Category:
- Core functionality

Section:
- ART internal changes

Related official sources:
- https://source.android.com/docs/core/ota/modular-system/art
- https://source.android.com/docs/core/runtime
- https://developer.android.com/guide/app-compatibility/restrictions-non-sdk-interfaces
- https://developer.android.com/about/versions/16/release-notes

### 分類スナップショット（Classification Snapshot）

主分類（Primary classification）:
- `MAINLINE_OR_PLAY_SYSTEM_UPDATE`

早見表（At-a-glance impact）:

| 確認項目（Question） | 回答（Answer） | 根拠（Evidence） |
| --- | --- | --- |
| Android 16 に OS アップデートしただけで適用されるか | Yes, Android 16 platform image に含まれる ART 更新として適用され得る。 | 公式 all apps ページは Android 16 が最新 ART updates を含むと説明している。 |
| targetSdkVersion 36 以上が必要か | No | 公式文書は targetSdkVersion 条件を述べず、AOSP `art` / `libcore` の module 実装更新にも targetSdkVersion 36 固有 gate は確認できない。 |
| Android 12+ 端末にも影響し得るか | Yes | 公式文書は Google Play System updates により Android 12 / API 31 以上にも ART improvements が提供されると説明している。AOSP でも `com.android.art` APEX module として ART / libcore boundary を確認した。 |
| 追加の実行時条件があるか | Yes | app code または依存 library / SDK が ART internal structures、non-SDK interfaces、hidden API、unsupported reflection / JNI / runtime layout assumptions に依存する場合。public API のみを使う通常アプリは低リスク。 |
| Compat Change ID が関係するか | No, this Behavior Change 全体を切り替える compat Change ID は確認できない。 | Android 16 compat framework 公式一覧に ART internal changes 固有の toggle は見つからない。hidden API enforcement 内には既存の internal compat IDs があるが、本項目全体の opt-out ではない。 |

### 調査日（Investigation Date）

2026-07-05

### 信頼度（Confidence）

- High

理由:
- 公式文書が all apps ページで Android 16 と Android 12+ ART Mainline delivery の両方を明記している。
- AOSP `art` は `com.android.art` APEX として構成され、`build/README.md` は Android S 以降の device に install 可能な ART module と説明している。
- AOSP `build/apex/Android.bp` と `build/boot/Android.bp` で ART / libcore が ART module boundary と bootclasspath fragment に含まれることを確認した。
- Android 15 -> Android 16 tag diff で `runtime`、`libdexfile`、`libartbase`、`artd`、`libcore` に大規模な差分があり、ART internals 依存コードが影響を受け得る根拠を確認した。
- known issues に HiddenApiBypass / FlyCore が ART internal structures 依存 library として掲載されていることを確認した。

### 適用条件分類（Applicability Classification）

適用される条件（Applies when）:
- [ ] OS update / all apps on Android 16 regardless of targetSdkVersion
- [ ] targetSdkVersion >= 36 on Android 16+
- [ ] targetSdkVersion >= 36, with additional runtime conditions
- [x] Mainline / Google Play system update dependent
- [ ] API addition only, not a behavior change
- [ ] Unknown / needs more evidence

必要な実行時条件（Required runtime conditions）:
- Android version: Android 16、または Android 12+ で ART Mainline module が更新された device。
- targetSdkVersion: 条件なし。35 と 36 の差は本項目の主要 gate ではない。
- Device/form factor: 条件なし。ただし Google Play System Update / ART APEX update の配信状態に依存する。
- Permission/API/component condition: public API のみなら低リスク。ART internals / non-SDK / hidden API / JNI runtime assumptions / bytecode instrumentation などに依存する場合にリスクがある。
- App state/process condition: app startup、class loading、reflection、JNI、dynamic loading、profiling / tracing / hooking SDK 初期化など。

Compat framework:
- 本 Behavior Change 全体を force-enable / force-disable する Android 16 compat Change ID は確認できない。
- `runtime/hidden_api.cc` には `kHideMaxtargetsdkPHiddenApis` (`149997251`)、`kHideMaxtargetsdkQHiddenApis` (`149994052`)、`kAllowTestApiAccess` (`166236554`) など hidden API enforcement 用の internal compat checks がある。
- これらは non-SDK / hidden API enforcement の一部であり、ART Mainline update 全体の opt-out ではない。

分類信頼度（Classification confidence）:
- High

分類根拠（Classification evidence）:
- Official documentation page: `behavior-changes-all` の ART internal changes。
- Original applicability statement: Android 16 に ART updates が含まれ、Google Play System updates により Android 12+ にも提供される。
- AOSP module boundary: `com.android.art` APEX、`art-bootclasspath-fragment`、ART / libcore module boundary。
- AOSP targetSdk gate: 本項目全体を targetSdkVersion 36 に限定する gate は見つからない。

---

# エグゼクティブサマリー（Executive Summary）

Android 16 には ART の最新更新が含まれる。これらは runtime performance 改善や Java feature support を含むが、ART internal structures に依存する app code / library / SDK は Android 16 で動かなくなる可能性がある。

この変更は targetSdkVersion 36 化だけの影響ではない。さらに、ART は Mainline / Google Play System Update で配信されるため、Android 16 端末だけでなく Android 12 / API 31 以上の端末でも、ART module update により同種の互換性リスクが発生し得る。

通常の public Android SDK / Java / Kotlin API のみを使うアプリは低リスクである。一方、hidden API reflection、JNI での runtime 内部前提、bytecode instrumentation、hooking、hotfix、anti-tamper、profiling / monitoring SDK などは重点的に確認する必要がある。

---

# 公式ドキュメント確認（Original Documentation）

## 原文（Statement）

公式文書では、Android 16 は ART の最新更新を含み、ART performance improvement と追加 Java feature support を提供すると説明している。また Google Play System updates により、これらの改善は Android 12 / API 31 以上の 10億台超の device にも提供されると説明している。

公式文書は、ART internal structures に依存する libraries / app code は Android 16 端末、および Google Play system updates で ART module が更新された過去 Android version 端末で正しく動作しない可能性があると述べている。non-SDK interfaces などの internal structure 依存は常に互換性問題につながり得るため、Android 16 で thorough testing を行い、known issues に掲載された library 依存も確認するよう案内している。

## 解釈（Interpretation）

この項目は、単一の public API behavior change ではない。ART / libcore / dex / class loading / JNI / hidden API enforcement / runtime implementation が module として更新されることにより、unsupported な runtime assumptions に依存する app / library が壊れる可能性を扱う。

顧客向けには、以下を混ぜずに説明する必要がある。

- Android 16 platform image に含まれる ART 更新の影響。
- targetSdkVersion 36 化の影響ではないこと。
- Android 12+ の ART Mainline / Google Play System Update による影響。
- public API 利用ではなく ART internals / non-SDK / unsupported runtime behavior 依存がリスク条件であること。

---

# 変更内容（What Changed）

## 変更点

- ART / libcore は `com.android.art` APEX module として構成される。Android 16 tag では `art` repo の `runtime`、`libdexfile`、`libartbase`、`artd`、`libartpalette`、`compiler` などに大規模差分がある。
- `libcore` repo では `api/current.txt`、`dalvik/system`、`java.lang`、`java.lang.invoke`、`java.nio.file`、`java.util.concurrent` などに差分がある。追加 Java feature support の一部は public API surface にも現れる。
- hidden API enforcement の実装は `runtime/hidden_api.cc` と `libartbase/base/hiddenapi_flags.h` にあり、reflection / JNI / linking / check 経路で non-SDK access を判定する。
- ART module は platform OS version と完全には連動しない。Google Play System Update により、Android 12+ 端末にも ART / libcore update が提供され得る。
- known issues には、ART internal structures に依存する library として HiddenApiBypass (`org.lsposed.hiddenapibypass:hiddenapibypass`) と FlyCore (`cn.fly:FlyCore`) before `v2025.0224.1629` が掲載されている。

## 適用条件（Applicability）

### Android 16 OS アップデート時の挙動（OS Update Behavior）

- Android 16 にアップデートしただけで適用されるか: Yes。Android 16 platform image は updated ART を含む。
- targetSdkVersion 35 のままでも影響するか: Yes。ART internals に依存している場合、targetSdkVersion と無関係に runtime implementation update の影響を受け得る。
- public API のみのアプリ: 原則として低リスク。ただし通常の regression testing は必要。

### targetSdkVersion 36 以上での挙動（targetSdkVersion 36 Behavior）

- targetSdkVersion 36 が必要条件か: No。
- Android 16 / targetSdkVersion 35 と Android 16 / targetSdkVersion 36 の差: 本項目全体では差を確認できない。
- 注意: non-SDK interface restrictions には max-target list など targetSdkVersion に依存する既存制度がある。しかし本 Behavior Change は targetSdkVersion 36 gate そのものではなく、ART module / implementation update による互換性リスクである。

### ART Mainline / Google Play System Update の挙動

- Android 12 / API 31 以上で ART module が更新された場合、Android 16 platform image でなくても同種の ART runtime / libcore update 影響を受け得る。
- 影響有無は OS version だけでなく、`com.android.art` APEX / ART module version、Google Play System Update 状態、vendor / device の module delivery 状態を記録して確認する必要がある。
- `targetSdkVersion` を変更しなくても ART module update だけで挙動差が出る可能性がある。

---

# AOSP / ART 調査（AOSP Investigation）

## 関連ファイル（Related Files）

- `platform/art/build/README.md`
- `platform/art/build/apex/Android.bp`
- `platform/art/build/boot/Android.bp`
- `platform/art/runtime/hidden_api.cc`
- `platform/art/libartbase/base/hiddenapi_flags.h`
- `platform/art/libartbase/base/hiddenapi_domain.h`
- `platform/art/runtime/class_linker.cc`
- `platform/art/runtime/art_method.cc`
- `platform/art/libdexfile/dex/*`
- `platform/art/artd/*`
- `platform/libcore/api/current.txt`
- `platform/libcore/dalvik/src/main/java/dalvik/system/*`
- `platform/libcore/luni/src/main/java/*`

## AOSP checkout hygiene

確認結果:
- 一時 checkout `platform/art`: clean
- 一時 checkout `platform/art`: `android-15.0.0_r36` tag exists
- 一時 checkout `platform/art`: `android-16.0.0_r4` tag exists
- 一時 checkout `platform/libcore`: clean
- 一時 checkout `platform/libcore`: `android-15.0.0_r36` tag exists
- 一時 checkout `platform/libcore`: `android-16.0.0_r4` tag exists

## 確認したソース文脈（Source Context Reviewed）

| ファイル / シンボル（File / symbol） | Android 15 の基準挙動（baseline） | Android 16 の挙動 | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| `art/build/README.md` | ART module build / install の説明がある。 | ART は `com.android.art.apex` として build され、Android S 以降の device に install 可能と説明する。 | ART が platform image だけでなく module として配信され得る根拠。 |
| `art/build/apex/Android.bp` | `com.android.art` APEX 定義がある。 | `com.android.art-base-defaults` は `s-launched-apex-module`、`com.android.art` は `libart` などを含む APEX として定義される。 | ART Mainline / APEX boundary の根拠。 |
| `art/build/boot/Android.bp` | ART bootclasspath fragment がある。 | `art-bootclasspath-fragment` は `core-oj`、`core-libart`、`okhttp`、`bouncycastle`、`apache-xml` を含む。 | libcore / managed core library が ART module boundary に含まれる根拠。 |
| `source.android.com ART module doc` | ART / libcore は Android 10 Runtime module effort、Android 11 non-updateable APEX と説明される。 | ART module は latest managed runtime optimizations / features / bug fixes を提供し、`com.android.art` APEX として ship される。 | 公式 AOSP doc による module delivery 根拠。 |
| `art/runtime/hidden_api.cc` | hidden API access 判定を実装する。 | reflection / JNI / linking / check で access context、target SDK、compat checks、log / StrictMode notification を扱う。 | non-SDK / hidden API 依存が ART internal change と交差する根拠。 |
| `art/libartbase/base/hiddenapi_flags.h` | hidden API list value と max-target categories を定義する。 | `Sdk` / `Unsupported` / `Blocked` / `MaxTargetO..S` / `CorePlatformApi` / `TestApi` などを扱う。 | non-SDK interface restrictions の runtime representation。 |
| `art/runtime/class_linker.cc` | class loading / linking / hidden API checks を行う。 | hidden API flags を field / method access flags に反映し、class loading / linking 時に access checks を行う。 | class loading / reflection / linking assumptions が壊れ得る根拠。 |
| `art/libdexfile/dex/*` | dex file / dex instruction / verifier 関連実装。 | Android 15 -> 16 で `compact_dex_file` 削除、dex file / verifier / instruction handling などに差分がある。 | dex / bytecode manipulation / instrumentation library へのリスク根拠。 |
| `art/artd/*` | ART daemon / dexopt 管理。 | AIDL / artd / secure dex metadata / pre-reboot staged files などに大きな差分がある。 | dexopt / runtime service implementation が module 内で変わる根拠。 |
| `libcore/api/current.txt` | Android 15 public API surface。 | Android 16 で HPKE、`android.system.Os` / `OsConstants`、Java / OpenJDK 21 flagged APIs などに差分がある。 | additional Java feature support / public API additions の根拠。 |

必須記入項目（Required context）:
- Entry point / caller: app startup、class loading、reflection、JNI `GetMethodID` / `GetFieldID`、dynamic code loading、bytecode verification、profiling / tracing / instrumentation SDK initialization。
- Relevant class or service responsibility: ART は DEX bytecode 実行、class loading、JIT/AOT、GC、hidden API enforcement、JNI bridge、dexopt を担う。libcore は Java / Android core libraries を提供する。
- Runtime path from app API / system event to changed code: APK 起動 -> ART / libcore module code -> class loading / linking / verification -> reflection / JNI / hidden API checks -> app code / library behavior。
- Why unrelated code paths were excluded: ART の performance tuning や compiler optimization は多数あるが、個別 commit の性能効果そのものは customer-facing behavior change ではないため、ART internal dependency risk に関係する module boundary / hidden API / dex / class loading / libcore API surface に絞った。

## 差分解釈（Diff Interpretation）

| 確認した差分（Observed diff） | 解釈（Interpretation） | Behavior Change との関係 | 信頼度（Confidence） |
| --- | --- | --- | --- |
| `art` repo の Android 15 -> 16 diff は `runtime`、`libdexfile`、`libartbase`、`artd`、`compiler` などで数万行規模。 | Changed implementation。ART internal layout / behavior に依存するコードは影響を受け得る。 | 「ART internal structures に依存する app / library は動かない可能性」を支持する。 | High |
| `art/build/README.md` は ART が `com.android.art.apex` module として build / install 可能と説明する。 | Module boundary evidence。 | 「ART changes aren't tied to platform version」を支持する。 | High |
| `art/build/apex/Android.bp` は `com.android.art` APEX を定義し、`build/boot/Android.bp` は `core-oj` / `core-libart` を bootclasspath fragment に含める。 | APEX / bootclasspath boundary evidence。 | ART / libcore が Mainline module update に含まれる根拠。 | High |
| `runtime/hidden_api.cc` は hidden API access を target SDK、compat checks、access context、reflection / JNI / linking path で判定する。 | Existing enforcement plus changed implementation。 | non-SDK / hidden API 依存が互換性リスクになる根拠。 | High |
| `libcore/api/current.txt` に public API additions / flagged Java APIs 差分がある。 | API addition evidence。 | 公式文書の additional Java feature support を部分的に支持する。 | Medium-High |
| Android 16 compat framework 公式一覧に ART internal changes 全体の toggleable change は見つからない。 | No app-level compat opt-out found。 | ART module update は targetSdkVersion 36 toggle ではなく module-delivered runtime behavior と扱う。 | High |

---

# Facts / Observations / Hypotheses / Conclusions

## Facts

- 公式文書は Android 16 all apps ページで、Android 16 が最新 ART updates を含むと説明している。
- 公式文書は Google Play System updates により、ART improvements が Android 12 / API 31 以上にも提供されると説明している。
- AOSP docs は ART module が latest managed runtime optimizations / features / bug fixes を提供し、`com.android.art` APEX として ship されると説明している。
- AOSP `art/build/README.md` は ART が `com.android.art.apex` module として build され、Android S 以降の device に install 可能と説明している。
- AOSP `art/build/apex/Android.bp` は `com.android.art` APEX を定義している。
- AOSP `art/build/boot/Android.bp` は `core-oj` / `core-libart` などを `art-bootclasspath-fragment` に含めている。
- `art/runtime/hidden_api.cc` は hidden API access の deny / warning / StrictMode notification / event log path を持つ。
- `libartbase/base/hiddenapi_flags.h` は `blocked`、`unsupported`、`max-target-*`、`core-platform-api`、`test-api` の runtime representation を持つ。
- Android 16 release notes の known issues には、ART internal structures に依存する library として HiddenApiBypass と FlyCore before `v2025.0224.1629` が掲載されている。

## Observations

- この項目の primary risk は、public API の挙動変更ではなく、ART internal implementation に依存する app / library / SDK の互換性である。
- targetSdkVersion 36 に上げなくても、Android 16 platform ART または ART Mainline module update により影響が出る可能性がある。
- non-SDK interface restrictions には targetSdkVersion に応じた max-target behavior があるが、本項目の ART Mainline update risk とは分けて扱う必要がある。
- hidden API / runtime internals 依存は app code だけでなく transitive dependency に含まれることが多い。SDK / library inventory が必要である。
- ART APEX / module version を記録しないと、Android 12+ 端末で再現差分を OS version だけでは説明できない。

## Hypotheses

- bytecode weaving、hotfix、hooking、anti-tamper、anti-cheat、profiling / monitoring SDK は、public API 利用アプリよりも ART internal change の影響を受けやすい。
- Android 16 で発生する `ClassNotFoundException`、`NoSuchMethodError`、`IllegalAccessError`、JNI lookup failure、hidden API warning は、app code ではなく transitive SDK が原因の可能性がある。
- Android 12+ の updated ART module でだけ発生し、Android 15 platform image だけの比較では再現しない issue があり得る。

## Conclusions

- この変更の primary classification は `MAINLINE_OR_PLAY_SYSTEM_UPDATE` である。
- Android 16 OS update と targetSdkVersion 36 化を混同してはいけない。targetSdkVersion 36 は本項目の主要 gate ではない。
- Android 12+ 端末でも ART Mainline module update により同種の互換性リスクがあるため、Android 16 端末だけを見れば十分とは言えない。
- public API のみを使うアプリは低リスクだが、ART internals / non-SDK / hidden API / JNI runtime assumptions / bytecode instrumentation に依存する app / library は重点的に検証する必要がある。
- 影響がある場合は public API alternative へ移行し、必要な public API がない use case は issue tracker で feature request するのが推奨対応である。

---

# 期待挙動マトリクス（Expected Behavior Matrix）

## OS / targetSdkVersion matrix

| OS / targetSdkVersion | 期待挙動（Expected behavior） | 顧客説明 |
| --- | --- | --- |
| Android 16 / targetSdkVersion 35 | ART update が適用される。ART internals 依存があれば影響し得る。 | OS update / module update impact。 |
| Android 16 / targetSdkVersion 36 | targetSdkVersion 35 と同じく ART update が適用される。 | targetSdkVersion 36 化だけの影響ではない。 |
| Android 15 / targetSdkVersion 36 / ART module 未更新 | Android 16 ART update は適用されない。 | targetSdkVersion 36 だけでは本項目の主要リスクは発生しない。 |
| Android 15 / targetSdkVersion 36 / ART module 更新済み | Android 16 platform でなくても ART Mainline update の影響を受け得る。 | OS version ではなく ART APEX version を記録する。 |
| Android 12+ / updated ART Mainline module | Android 16 相当または同系統の ART update 影響を受け得る。 | Google Play System Update impact。 |

## Required scenario matrix

| Scenario | 期待挙動 / リスク | Notes |
| --- | --- | --- |
| Android 16 / targetSdkVersion 35 / app uses only public APIs | 原則低リスク。通常 regression test は必要。 | public API 利用。 |
| Android 16 / targetSdkVersion 36 / app uses only public APIs | 原則低リスク。targetSdk 36 固有ではない。 | public API 利用。 |
| Android 16 / targetSdkVersion 35 / app uses ART internals | 影響あり得る。 | targetSdk に依存しない。 |
| Android 16 / targetSdkVersion 36 / app uses ART internals | 影響あり得る。 | targetSdk 35 と同じリスク。 |
| Android 16 / app uses non-SDK interfaces | hidden API enforcement / internal change の影響あり得る。 | max-target list と module update を分けて確認。 |
| Android 16 / app uses reflection into hidden runtime APIs | warning / deny / linkage error / behavior change の可能性。 | logs を確認。 |
| Android 16 / app uses JNI assumptions about ART internals | JNI lookup failure / crash / behavior change の可能性。 | native library 検証。 |
| Android 16 / app includes bytecode instrumentation / hooking SDK | 高リスク。 | runtime / dex / class loading assumptions。 |
| Android 16 / app includes crash reporting / profiling / monitoring SDK | 中から高リスク。 | SDK が runtime internals を読む場合。 |
| Android 16 / app includes obfuscation / anti-tamper / hotfix framework | 高リスク。 | dex / classloader / method layout assumptions。 |
| Android 16 / affected third-party library from known issues | 影響あり得る。 | HiddenApiBypass / FlyCore before fixed version。 |
| Android 16 / dependency updated to public API-compatible version | リスク低下。 | SDK release note を確認。 |
| Android 12+ / updated ART Mainline module / same app behavior | Android 16 以外でも再現し得る。 | ART APEX version を記録。 |
| targetSdkVersion changed to 36 without ART module change | 本項目単独の主要リスクは増えない。 | non-SDK max-target restrictions は別途確認。 |
| ART module updated without targetSdkVersion change | 本項目の互換性リスクが発生し得る。 | Mainline impact。 |
| public API alternative exists | 移行推奨。 | unsupported dependency を除去。 |
| public API alternative missing / feature request needed | issue tracker で feature request。 | 公式推奨。 |

---

# 影響対象（Who Is Affected）

- ART internals に依存するアプリ。
- non-SDK interfaces を使うアプリ。
- hidden API reflection を使うアプリ。
- JNI / native code で runtime internals を前提にするアプリ。
- bytecode weaving / instrumentation / hooking / hotfix framework を使うアプリ。
- plugin / dynamic loading framework を使うアプリ。
- obfuscation / anti-tamper / anti-cheat SDK を使うアプリ。
- crash reporting / profiling / tracing / monitoring SDK を使うアプリ。
- third-party SDK / library が ART internals に依存するアプリ。
- Android 12+ 端末で ART Mainline update の影響を受け得るアプリ。
- known issues に掲載された library を含むアプリ。
- dependency update / replacement が必要なアプリ。

低影響または非影響になりやすいケース:
- public Android SDK API のみを使うアプリ。
- supported Java / Kotlin language / runtime behavior のみを使うアプリ。
- hidden API / non-SDK / runtime internal reflection を使わないアプリ。
- 依存 SDK が ART internal usage を除去済みのアプリ。

---

# 推奨対応（Recommended Action Candidates）

- app code と third-party dependencies に hidden API / non-SDK / ART internal usage がないか棚卸しする。
- known issues に掲載された HiddenApiBypass / FlyCore before `v2025.0224.1629` を含まないか確認する。
- runtime hooking / hotfix / instrumentation / profiling / monitoring / anti-tamper SDK は Android 16 と updated ART module device で個別に検証する。
- hidden API warning、StrictMode hidden API signal、`NoSuchMethodError`、`IllegalAccessError`、`ClassNotFoundException`、JNI lookup failure、native crash をログ化する。
- public API alternative がある場合は移行する。
- public API がない use case は Android issue tracker で feature request する。
- Android 12+ の検証端末では OS version だけでなく ART APEX / module version、Google Play System Update 状態を記録する。

---

# テスト観点（Test Guidance）

- Android 15 端末上の targetSdkVersion 35。
- Android 16 端末上の targetSdkVersion 35。
- Android 16 端末上の targetSdkVersion 36。
- Android 15 端末上の targetSdkVersion 36 が検証可能な場合の比較。
- Android 12+ 端末で ART Mainline module が更新された場合。
- ART APEX / module version の記録。
- targetSdkVersion 変更なしで ART module update した場合。
- targetSdkVersion 36 化のみで ART module change がない場合。
- app startup。
- class loading。
- reflection。
- JNI calls。
- dynamic code loading。
- bytecode instrumentation。
- hooking / hotfix framework。
- crash reporting / profiling SDK initialization。
- obfuscation / anti-tamper behavior。
- hidden API / non-SDK usage logs。
- StrictMode / hidden API warning / crash / `NoSuchMethodError` / `IllegalAccessError` / linkage errors。
- known issues listed libraries。
- dependency update before / after。
- public API alternative migration。
- regression testing across Android 16 and Android 12+ updated ART devices。

---

# 顧客向け説明（Customer-facing Explanation）

Android 16 には ART の最新更新が含まれます。この更新は performance improvement や Java feature support を提供しますが、ART internal structures、hidden API、non-SDK interfaces、JNI の内部前提に依存する app code / library / SDK は動作しなくなる可能性があります。

これは targetSdkVersion 36 に上げた時だけの変更ではありません。Android 16 端末では targetSdkVersion 35 のままでも影響し得ます。また ART は Google Play System Update で Android 12 以上にも配信されるため、Android 16 以外の端末でも ART module update により同種の影響が出る可能性があります。

public API のみを使うアプリは低リスクですが、hooking、hotfix、bytecode instrumentation、profiling / monitoring、anti-tamper、hidden API bypass 系の SDK を含む場合は重点的に検証してください。問題がある場合は public API へ移行し、不足する API は feature request として報告する必要があります。

---

# 未確認点・リスク（Open Questions / Residual Risk）

- ART Mainline module の実配信 version は device / channel / Google Play System Update 状態に依存する。AOSP tag だけでは個別端末の ART APEX version は確定できない。
- 個別 library の破壊有無は、library version と利用 code path に依存する。known issues に掲載された library 以外にも transitive dependency risk があり得る。
- hidden API restrictions の max-target behavior は targetSdkVersion と関係するが、本項目全体は targetSdkVersion 36 gate ではない。アプリ別評価では non-SDK restrictions 調査と合わせて確認する必要がある。

---

# Human Decision

最終優先度（Final Priority）:
- Critical / High / Medium / Low

判断（Decision）:
- Explain / Monitor / Ignore / Further investigation required

補足:
- 最終優先度、顧客通知要否、release readiness は repository owner が判断する。

---

## 再検証記録（2026-08-22）

### 調査日（Investigation Date）

- 2026-08-22

### 公式ドキュメント再確認（Original Documentation Recheck）

- Android 16 の all-apps / target Behavior Change ページを再取得し、このレポートが参照する公式 section の掲載と適用範囲を再確認した。
- 公式ページの最終更新表示: all-apps: 2026-08-14 UTC / target: 2026-08-17 UTC。
- Android 16 compat framework 一覧も 2026-08-22 に再取得した。
- 既存の引用は短い要約として扱い、適用条件は公式ページ種別と AOSP gate の両方で再評価した。

### AOSP 証拠ワークスペース（AOSP Evidence Workspaces）

| AOSP project | Official remote URL | Checkout path | Working tree | From tag / resolved commit | To tag / resolved commit | Comparison command | Dirty risk / limitations |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `platform/art` | `https://android.googlesource.com/platform/art` | `tmp/aosp-checkouts/art/` | 展開中 | `android-15.0.0_r36` / `795d594fd825385562da6b089ea9b2033f3abf5a` | `android-16.0.0_r4` / `1690c6912a7972c9e62c39b48c706de9b8b18b4a` | `git -C tmp/aosp-checkouts/art diff --no-renames --name-only android-15.0.0_r36 android-16.0.0_r4` | 部分クローンの working tree 展開中。根拠は解決済みタグの object 比較だけを使用し、展開途中のファイルを含めない。 |
| `platform/libcore` | `https://android.googlesource.com/platform/libcore` | `tmp/aosp-checkouts/libcore/` | 展開中 | `android-15.0.0_r36` / `89a6322812dc8573315e60046e7959c50dad91d4` | `android-16.0.0_r4` / `1c599b67bcd3de5c50c79d0622e40b6de99b4cb4` | `git -C tmp/aosp-checkouts/libcore diff --no-renames --name-only android-15.0.0_r36 android-16.0.0_r4` | 部分クローンの working tree 展開中。根拠は解決済みタグの object 比較だけを使用し、展開途中のファイルを含めない。 |

### ソース文脈・差分解釈の再確認（Source Context Reviewed / Diff Interpretation）

- 各 official remote で Android 15 / 16 の最新通常リリースタグが `android-15.0.0_r36` / `android-16.0.0_r4` のままであることを確認した。
- 上表の project-level `--name-only` 比較を再実行し、既存本文の path / symbol 別 source context、gate、追加・削除・条件変更・既定値変更・差分なしの解釈を再確認した。
- タグと解決済み commit が既存調査の比較対象から変わっていないため、本文の evidence record を別タグへ機械的に置換していない。
- 実機 Observed は新規実施していない。既存の「未実施」「未確認」および不足根拠はそのまま維持した。

### 事実（Facts）

- `android-15.0.0_r36` と `android-16.0.0_r4` は 2026-08-22 時点の最新通常リリースタグである。
- 上表に再検証時の working tree 状態を記録し、official remote、両タグ、解決済み commit を確認した。展開中または dirty の working tree は根拠に使用していない。
- 公式 section と AOSP evidence の比較 pair は一致している。

### 観察（Observations）

- 最新タグが変わっていないため、今回の再検証で既存の source diff 解釈を変更する新しい AOSP tag evidence は生じなかった。
- report 内に残る Medium / Low confidence、OEM / Mainline / QPR 条件、未確認の module enforcement は解消したものとして扱わない。

### 仮説（Hypotheses）

- 新しい仮説は追加しない。既存本文で仮説または可能性として記載した事項は、実機・製品 build・未確認 module の evidence が得られるまで事実へ昇格しない。

### 結論（Conclusions）

- 既存本文の主分類、confidence、対応候補を維持する。既存の不足根拠がある場合はその制約も維持する。
- 全件再検証の横断記録は [`android16/analysis/REVALIDATION_2026-08-22.md`](../../../analysis/REVALIDATION_2026-08-22.md) を参照する。

### Human Decision

- この再検証では最終 priority、severity、release readiness、顧客説明優先度を変更していない。
- 人間の判断は [Android 16 Decision Log](../../../decisions/DECISION_LOG.md) を正とする。
