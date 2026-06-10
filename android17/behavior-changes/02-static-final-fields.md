# Static final fields are now unmodifiable

## Metadata

### Android Versions

From:
- android-16.0.0_r4

To:
- TBD: Android 17 AOSP tag

Previous targetSdkVersion:
- 36

Target targetSdkVersion:
- 37

### Behavior Change Source

Document:
https://developer.android.com/about/versions/17/behavior-changes-17

Section:
Static final fields are now unmodifiable

Page type:
- Apps targeting Android 17 or higher

### Classification Snapshot

Primary classification:
- UNKNOWN_NEEDS_MORE_EVIDENCE

Initial applicability assumption from official documentation:
- 公式文書は、Android 17 以上で動作し、かつ targetSdkVersion 37 以上のアプリに適用される変更として説明している。
- static final field を reflection または JNI で変更しようとする場合に影響するため、一次分類としては `TARGET_SDK_37_CONDITIONAL` が近い。
- ただし、local `frameworks-base` に Android 17 AOSP tag がないため、AOSP gate、Compat Change ID、default state を検証できていない。確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

At-a-glance impact:

| Question | Answer | Evidence |
| --- | --- | --- |
| Android 17 OS update only? | Unknown | 原文は Android 17+ と targetSdkVersion 37+ の両方を条件としているが、AOSP gate 未確認。 |
| targetSdkVersion 37 required? | Likely, but unverified | 原文は target Android 17 / API level 37 以上を明示している。AOSP evidence は未取得。 |
| Additional runtime conditions? | Yes, from documentation | static final field を reflection または JNI で変更しようとする場合に問題化する。 |
| Compat Change ID involved? | Unknown | Android 17 tag と compat framework evidence が未確認。 |

### Investigation Date

2026-06-10

### Confidence

- Low

### Applicability Classification

Applies when:
- [ ] OS update / all apps on Android 17 regardless of targetSdkVersion
- [ ] targetSdkVersion >= 37 on Android 17+
- [ ] targetSdkVersion >= 37, with additional runtime conditions
- [ ] Mainline / Google Play system update dependent
- [ ] API addition only, not a behavior change
- [x] Unknown / needs more evidence

Required runtime conditions:
- Android version: 公式文書上は Android 17 以上。
- targetSdkVersion: 公式文書上は 37 以上。
- Device/form factor: 公式抜粋では条件なし。
- Permission/API/component condition: reflection で static final field を変更する、または JNI API で static final field を変更する。
- App state/process condition: 公式抜粋では条件なし。

Compat framework:
- Change ID: Unknown
- Change name: Unknown
- Default state: Unknown
- Toggleable for testing: Unknown

Classification confidence:
- Low

Classification evidence:
- Official documentation page: `behavior-changes-17`
- Original applicability statement: Android 17+ で動作し、targetSdkVersion 37+ のアプリが対象。
- AOSP targetSdk gate: 未確認。local `frameworks-base` に `android-17*` tag がない。
- Compat framework entry: 未確認。Android 17 compat framework evidence が未取得。

---

# Executive Summary

Android 17 では、Android 17 以上で動作し targetSdkVersion 37 以上のアプリが static final field を変更できなくなる、と公式 Behavior Change 文書は説明している。reflection で変更しようとすると `IllegalAccessException`、JNI の static field 書き換え API ではアプリ crash が発生するとされている。

影響を受けるのは、定数、feature flag、SDK 内部値、テスト用 hook などの static final field を実行時に書き換えるアプリや SDK である。local `frameworks-base` に Android 17 AOSP tag がないため、現時点では AOSP gate と compat framework default state を検証できていない。

---

# Original Documentation

## Statement

Page title:
- Behavior changes: Apps targeting Android 17 or higher

Page URL:
- https://developer.android.com/about/versions/17/behavior-changes-17

Page type:
- apps targeting Android 17

Section title:
- Static final fields are now unmodifiable

Original statement being verified:

> cannot change static final fields

The supplied official text states that apps running on Android 17 or higher and targeting API level 37 or higher cannot modify static final fields. It also states that reflection attempts throw `IllegalAccessException`, while JNI attempts such as `SetStaticLongField()` crash the app.

## Interpretation

この変更は、static final field を実行時に変更する実装パターンを禁止する互換性変更である。公式文書は OS 条件として Android 17 以上、targetSdkVersion 条件として 37 以上を明示している。

開発者への意味は、Java/Kotlin reflection や JNI を使って static final field を後から変更する実装が、targetSdkVersion 37 更新後に失敗する可能性があるということ。通常の field 読み取りや、static final field を変更しない通常の public API 利用は、この文言だけでは影響対象とは言えない。

---

# What Changed

公式文書上の変更点:
- Android 17 以上で動作し、targetSdkVersion 37 以上のアプリは static final field を変更できない。
- reflection による変更 attempt は `IllegalAccessException` になる。
- JNI API による変更 attempt はアプリ crash になる。

AOSP で未確認の点:
- Android 16 baseline で static final field 変更 attempt がどこまで許容されていたか。
- Android 17 で reflection と JNI それぞれの制御がどの層に追加されたか。
- targetSdkVersion 37 gate の実装箇所。
- Compat Change ID と default state。
- opt-out または temporary override の有無。

## Applicability

公式文書の一次判断では、Android 17 以上、targetSdkVersion 37 以上、かつ static final field を変更しようとする場合に影響する。AOSP tag が未取得のため、確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

### OS Update Behavior

- Android 17 にアップデートしただけで適用されるか: Unknown
- targetSdkVersion に依存しない根拠: なし。公式文書は targetSdkVersion 37 以上を明示している。
- Android 16 以前での挙動: AOSP tag 比較未実施。Android 16 baseline source は Android 17 tag との比較ができないため、この調査では platform evidence として採用していない。

### targetSdkVersion 37 Behavior

- targetSdkVersion 37 以上で適用されるか: 公式文書上は Yes と読めるが、AOSP gate 未確認。
- Android 17 以外で targetSdkVersion 37 にした場合の挙動: Unknown。公式文書は Apps running on Android 17 or higher を条件にしているため、Android 17 platform behavior として扱う。
- opt-out / temporary override の有無: Unknown。compat framework evidence 未確認。

### Other Conditions

- device/form factor: 公式抜粋では条件なし。
- permission: 公式抜粋では条件なし。
- API usage: reflection または JNI で static final field を変更しようとすること。
- manifest attribute: Unknown。
- component boundary: アプリコード、自社ライブラリ、サードパーティ SDK、native code のいずれでも static final field 変更 attempt があれば影響し得る。

---

# AOSP Investigation

## Checkout Status

Commands checked before evidence use:

```bash
git -C frameworks-base status --short
git -C frameworks-base tag --list android-16.0.0_r4
git -C frameworks-base tag --list 'android-17*'
```

Result:
- `frameworks-base` working tree: clean at the time of investigation.
- From tag: `android-16.0.0_r4` exists.
- To tag: no local `android-17*` tag found.

Evidence limitation:
- Android 17 AOSP tag が local `frameworks-base` に存在しないため、`git -C frameworks-base diff android-16.0.0_r4 <android-17-tag> -- ...` による明示的な tag 比較を実行できない。
- Repository rule に従い、Android 17 working tree や推測による source evidence は採用しない。
- この制約により、AOSP-backed conclusion は High confidence にできない。

## Related Files

未確認。Android 17 AOSP tag 取得後に、少なくとも以下の候補を確認する必要がある。

- `frameworks-base` 内の compat framework 定義ファイルで、static final field / reflection / JNI field update に関連する Change ID。
- `frameworks-base` 内に runtime behavior を参照する framework-side gate があるか。
- 実際の reflection / JNI enforcement は ART 側に存在する可能性があるが、本ミッションの AOSP evidence 範囲は `frameworks-base` の tag 比較に限定されているため、必要に応じて別途調査範囲の拡張判断が必要。

## Source Context Reviewed

Android 17 AOSP tag がないため、source context は未レビュー。

| File / symbol | Android 16 baseline | Android 17 behavior | Why this code path matters |
| --- | --- | --- | --- |
| Not reviewed | Not reviewed | Not reviewed | Android 17 tag がないため、公式文書の記述を AOSP diff で検証できない。 |

Required context:
- Entry point / caller: 未確認。想定される entry point は Java reflection field write と JNI static field write だが、AOSP evidence としては未採用。
- Relevant class or service responsibility: 未確認。
- Runtime path from app API / system event to changed code: 未確認。
- Why unrelated code paths were excluded: Android 17 tag 不在のため、source path の採否判断自体を保留。

## Diff Interpretation

| Observed diff | Interpretation | Behavior Change relevance | Confidence |
| --- | --- | --- | --- |
| No Android 17 tag diff available | Source diff type cannot be classified yet | 公式文書の static final field enforcement を source diff で裏取りできていない | Low |

Required interpretation:
- Added behavior: 未確認。
- Removed behavior: 未確認。
- Changed condition / gate: 未確認。
- Changed default: 未確認。
- No behavior change found: 未確認。tag 不在のため「no behavior change」とは判断しない。

## Evidence

Facts:
- 公式 Behavior Change 文書は、Android 17 以上で動作し targetSdkVersion 37 以上のアプリが static final field を変更できないと述べている。
- 公式文書は、reflection で static final field を変更しようとすると `IllegalAccessException` が発生すると述べている。
- 公式文書は、JNI API で static final field を変更しようとするとアプリが crash すると述べている。
- local `frameworks-base` には `android-16.0.0_r4` tag がある。
- local `frameworks-base` には `android-17*` tag がない。
- 調査時点で `frameworks-base` working tree は clean。

Observations:
- 公式ページ種別と原文は targetSdkVersion 37 以上の変更を示している。
- 原文は Android 17 以上という OS 条件も明示している。
- static final field を変更しようとする reflection / JNI usage が追加条件になる。
- AOSP tag がないため、実装が本当に targetSdkVersion 37 gate で制御されているかは未確認。
- Compat framework entry の有無も未確認。

Hypotheses:
- Android 17 上で targetSdkVersion 37 以上のアプリに対し、reflection と JNI の static final field write が runtime enforcement により拒否される可能性が高い。
- targetSdkVersion 36 のアプリでは互換性維持のため旧挙動が残る可能性があるが、AOSP gate 未確認のため断定しない。
- 実装本体は `frameworks-base` ではなく ART / runtime 側にある可能性がある。

Conclusions:
- 現時点で顧客向けに確定できるのは、「公式文書上は Android 17 以上かつ targetSdkVersion 37 以上で static final field 書き換えが禁止される」という範囲まで。
- AOSP gate と compat framework default state が未確認のため、primary classification は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

## Applicability Gate Evidence

- targetSdkVersion gate: 未確認。Android 17 AOSP tag がないため、`targetSdkVersion` / `ApplicationInfo.targetSdkVersion` 検索は実施していない。
- CompatChanges.isChangeEnabled / ChangeId: 未確認。Android 17 AOSP tag がないため、`CompatChanges.isChangeEnabled` / `@ChangeId` / `@EnabledAfter` / `@EnabledSince` 検索は実施していない。
- @EnabledAfter / @EnabledSince / default state: 未確認。
- Build.VERSION / SDK_INT gate: 未確認。
- DeviceConfig / resources config: 未確認。
- Permission/AppOps gate: 未確認。
- Manifest/property gate: 未確認。
- No gate found: 未判断。検索不能のため「gate なし」とは扱わない。
- Gate conclusion: Unknown。公式文書上の Android 17+ / targetSdkVersion 37+ 条件はあるが、AOSP evidence が不足している。
- Reasoning from source context: source context 未取得のため不可。

Searched:
- `frameworks-base` checkout status。
- `android-16.0.0_r4` tag の存在。
- `android-17*` tag の存在。

Not searched yet:
- Android 17 implementation files。
- Android 17 compat framework definitions。
- ART / runtime 側の reflection / JNI enforcement 実装。

Reason:
- Android 17 target tag が local checkout に存在しないため、tag 間 diff による platform evidence が作れない。

---

# Impact Analysis

## Affected Apps

影響を受ける可能性があるアプリ:
- targetSdkVersion 37 以上への更新を予定しているアプリ。
- reflection で static final field を書き換える自社コードを持つアプリ。
- JNI で static final field を書き換える native code を持つアプリ。
- feature flag、SDK 内部定数、build-time constant、テスト用 override、互換性回避のために static final field を実行時に変更しているアプリまたは SDK。
- 古い instrumentation、hot patch、mocking、hooking、diagnostics 系 SDK を組み込んでいるアプリ。

## Non-Affected Apps

影響が限定的と考えられるケース:
- static final field を読み取るだけで変更しないアプリ。
- reflection や JNI による static final field 書き換えを行っていないアプリ。
- targetSdkVersion 37 へ上げないアプリ。ただし、これは公式文書からの一次判断であり、AOSP gate 未確認。

---

# Customer Impact

## Impact Level

- Human decision required

※ 最終 severity / priority は人間が判断する。このレポートでは確定しない。

## Business Impact

- ユーザー影響: 該当コードパスが実行されると、reflection では例外処理漏れによる機能停止や crash、JNI では直接 crash が発生する可能性がある。
- 運用影響: サードパーティ SDK や native library が原因の場合、アプリ側で検出しにくく、SDK vendor への確認や更新が必要になる可能性がある。
- 開発影響: targetSdkVersion 37 更新前に reflection / JNI field write の棚卸し、代替設計、Android 17 テストが必要。

---

# Service Impact Examples（サービス影響例）

このセクションは、公式文書と AOSP evidence から導いた「起こりうる影響例」を記録する。特定サービスで実際に発生確認した事実ではない。

## Example 1（例1）: 設定値を reflection で差し替えるアプリ / SDK

- 対象サービス例: A/B test SDK、feature flag framework、社内 debug tool。
- 影響を受ける実装パターン: `static final` fields を reflection / Unsafe / instrumentation で書き換える実装。
- 発生条件: Android 17 / targetSdkVersion 37 で `static final` fields が unmodifiable と扱われる場合。
- ユーザーに見える症状: feature flag が切り替わらない、debug menu の変更が反映されない、初期化時に例外が出る可能性。
- 開発・運用への影響: runtime patching 前提の設定更新、テスト環境の差し替え、SDK initialization の見直しが必要になる可能性。
- 推奨対応候補: mutable holder / DI / build-time config に移行し、`static final` 直接変更を避ける。
- 根拠: 公式 Behavior Change statement と report の AOSP evidence limitation。
- Confidence（信頼度）: Low
- 注意: どの API path で例外または no-op になるかは Android 17 AOSP tag 待ち。

## Example 2（例2）: テスト / mocking framework に依存するアプリ

- 対象サービス例: 大規模 Android app の instrumented test、E2E test、SDK integration test。
- 影響を受ける実装パターン: production code の `static final` constant を test runtime で書き換える test utility。
- 発生条件: targetSdkVersion 37 の test build / app process で static final mutation が拒否される場合。
- ユーザーに見える症状: 直接の本番ユーザー影響は限定的だが、テスト失敗により release validation が詰まる可能性。
- 開発・運用への影響: test fixture、mocking strategy、CI の Android 17 対応が必要になる可能性。
- 推奨対応候補: constructor injection、interface abstraction、test-only build variants に移行する。
- 根拠: 公式 statement と report の targetSdkVersion gate 未確認事項。
- Confidence（信頼度）: Low
- 注意: 実サービス障害ではなく開発・検証 pipeline への影響例。

---

# Required Actions

## Must

- static final field を reflection で変更している自社コードがないか確認する。
- JNI API で static final field を変更している native code がないか確認する。
- サードパーティ SDK に static final field の runtime override、hot patch、mocking、hooking が含まれていないか確認する。
- targetSdkVersion 37 更新前に Android 17 device / emulator で該当機能をテストする。

## Recommended

- static final field の実行時変更に依存しない設計へ移行する。
- 設定値や feature flag は mutable な設定 API、dependency injection、設定ファイル、server-side config などに移す。
- reflection failure を crash にしないため、例外処理と fallback を確認する。
- native library / SDK を Android 17 対応版に更新する。

## Optional

- Android 17 AOSP tag 公開後、static final field enforcement の diff と compat Change ID を再調査する。
- テスト用の static final override がある場合、test-only mechanism と production code を分離する。

---

# Verification Method

## Matrix

| Device OS | targetSdkVersion | Compat flag | Expected behavior |
| --- | --- | --- | --- |
| Android 16 | 36 | default | Android 16 baseline。static final field 変更 attempt の挙動は Android 17 tag 比較待ち。 |
| Android 17 | 36 | default | Unknown。公式文書上は targetSdkVersion 37 以上向けのため旧挙動維持が期待されるが、AOSP gate 未確認。 |
| Android 17 | 37 | default | 公式文書上は static final field 変更が拒否される。reflection は `IllegalAccessException`、JNI は app crash。 |
| Android 17 | 36 | force-enabled if available | Unknown。Compat Change ID 未確認。 |
| Android 17 | 37 | force-disabled if available | Unknown。Compat Change ID 未確認。 |

## Steps

- targetSdk変更: test app を targetSdkVersion 36 と 37 で build し、Android 17 上の挙動差を確認する。
- compat framework command: Change ID 未確認のため未定。Android 17 tag / compat page 確認後に追加する。
- テスト方法: static final field を reflection で変更する最小再現コードと、JNI で変更する最小 native test を用意する。
- 再現手順: Android 17 上で targetSdkVersion 36 / 37 の両 APK を実行し、reflection の例外種別、JNI crash、stack trace、compat flag 有無を比較する。
- 期待結果: targetSdkVersion 37 では公式文書どおり static final field 変更が拒否される。targetSdkVersion 36 の結果は AOSP gate 確認待ち。

---

# Conclusion

公式文書は、Android 17 以上で動作し targetSdkVersion 37 以上のアプリが static final field を変更できなくなると説明している。主な互換性リスクは、reflection または JNI で static final field を実行時に書き換えるコードである。

一方で、local `frameworks-base` に Android 17 AOSP tag がないため、実装差分、targetSdkVersion gate、Compat Change ID、default state を検証できていない。現時点の primary classification は `UNKNOWN_NEEDS_MORE_EVIDENCE`、confidence は Low とする。

Human decision placeholder:
- Final priority: Human decision required
- Final severity: Human decision required
- Release readiness: Human decision required
- Customer communication priority: Human decision required
- Next required human decision: Android 17 AOSP tag 公開後に再調査するか、公式 documentation ベースの暫定注意喚起として扱うかを判断する。
