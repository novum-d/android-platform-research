# Safer Native DCL-C

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

Related documents:
- None supplied

Section:
Safer Native DCL-C

Page type:
- Apps targeting Android 17 or higher

### Classification Snapshot

Primary classification:
- UNKNOWN_NEEDS_MORE_EVIDENCE

Initial applicability assumption from official documentation:
- 公式文書は、targetSdkVersion 37 以上のアプリでは Android 14 で DEX / JAR files に導入された Safer Dynamic Code Loading (DCL) protection が native libraries にも拡張されると説明している。
- `System.load()` で読み込まれる native files は read-only として mark されている必要があり、そうでない場合は system が `UnsatisfiedLinkError` を throw すると説明している。
- 追加条件として、native file を `System.load()` で動的に読み込むこと、ファイルが writable ではなく read-only として扱われることが関係する。
- ただし、local `frameworks-base` に Android 17 AOSP tag がないため、native DCL read-only check、targetSdkVersion gate、`System.load()` / runtime native loading path、error condition、Compat Change ID、default state は未検証である。確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

At-a-glance impact:

| Question | Answer | Evidence |
| --- | --- | --- |
| Android 17 OS update only? | Unknown | 公式文書は If your app targets Android 17 / API level 37 or higher と述べるが、AOSP gate 未確認。 |
| targetSdkVersion 37 required? | Likely, but unverified | 原文は targetSdkVersion 37 以上を明示している。 |
| Additional runtime conditions? | Yes | `System.load()` による native file loading と read-only file state が関係する。 |
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
- Android version: Android 17 以上が前提と考えられるが、AOSP tag 未取得。
- targetSdkVersion: 公式文書上は 37 以上。
- Device/form factor: 公式抜粋では条件なし。
- Permission/API/component condition: `System.load()`、dynamic native library loading、native file の read-only state。
- App state/process condition: アプリプロセスが native file を `System.load()` で読み込む時点。

Compat framework:
- Change ID: Unknown
- Change name: Unknown
- Default state: Unknown
- Toggleable for testing: Unknown

Classification confidence:
- Low

Classification evidence:
- Official documentation page: `behavior-changes-17`
- Original applicability statement: apps targeting Android 17 / API level 37 or higher, `System.load()` で読み込まれる native files は read-only 必須、違反時は `UnsatisfiedLinkError`。
- AOSP targetSdk gate: 未確認。local `frameworks-base` に `android-17*` tag がない。
- Compat framework entry: 未確認。Android 17 compat framework evidence が未取得。

---

# Executive Summary

Android 17 では、targetSdkVersion 37 以上のアプリに対し、Safer Dynamic Code Loading (DCL) protection が native libraries にも拡張される、と公式文書は説明している。`System.load()` で読み込む native file は read-only として mark されている必要があり、条件を満たさない場合は `UnsatisfiedLinkError` が発生する。

この変更は、アプリが実行時に `.so` などの native library をダウンロード、生成、展開、更新してから `System.load()` で読み込む設計に影響する可能性がある。公式文書は、dynamic code loading 自体が code injection / code tampering risk を高めるため、可能な限り避けることを推奨している。

ただし、現時点の local `frameworks-base` には Android 17 AOSP tag がないため、実装差分、targetSdkVersion gate、read-only 判定の正確な条件、Compat Change ID は未確認である。

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
- Safer Native DCL-C

Original statement being verified:

> If your app targets Android 17 (API level 37) or higher, the Safer Dynamic Code Loading (DCL) protection introduced in Android 14 for DEX and JAR files now extends to native libraries.

The supplied official text also states that all native files loaded using `System.load()` must be marked as read-only. Otherwise, the system throws `UnsatisfiedLinkError`. It recommends avoiding dynamically loading code whenever possible because it increases the risk of code injection or code tampering.

## Interpretation

この変更は、Android 14 で DEX / JAR files に導入された「動的に読み込むコードは writable な状態であってはならない」という保護を、Android 17 で native libraries に拡張する security behavior change である。

アプリ開発者にとって重要なのは、targetSdkVersion 37 へ更新したアプリで、実行時に配置した native file を `System.load()` する場合、読み込み時点でその file が read-only として mark されていないと native library load が失敗し、`UnsatisfiedLinkError` として現れる可能性がある点である。

---

# What Changed

公式文書上の変更点:
- Android 14 で DEX / JAR files に導入された Safer Dynamic Code Loading protection が、Android 17 では native libraries にも拡張される。
- 対象は targetSdkVersion 37 以上のアプリ。
- `System.load()` で読み込まれる all native files は read-only として mark されている必要がある。
- native file が read-only でない場合、system は `UnsatisfiedLinkError` を throw する。
- 公式文書は、dynamic code loading は code injection / code tampering による compromise risk を大きくするため、可能な限り避けることを推奨している。

AOSP で未確認の点:
- Android 16 baseline で `System.load()` が writable native file を許容していたか。
- Android 17 で native file read-only check が追加された実装箇所。
- `System.load()` と `System.loadLibrary()` の扱いの差。
- read-only 判定が file mode、open fd、filesystem property、mount option、SELinux label、signature / integrity check のどれに依存するか。
- targetSdkVersion 37 gate の実装箇所。
- Android 14 DEX / JAR DCL protection との shared implementation / compat relation。
- Compat Change ID と default state。

## Applicability

公式文書の一次判断では、Android 17 以上、targetSdkVersion 37 以上、native file を `System.load()` で動的に読み込むアプリに適用される。AOSP tag が未取得のため、確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

### OS Update Behavior

- Android 17 にアップデートしただけで適用されるか: Unknown
- targetSdkVersion に依存しない根拠: なし。原文は If your app targets Android 17 / API level 37 or higher と明示している。
- Android 16 以前での挙動: 未確認。Android 17 tag との明示的な比較ができないため、Android 16 source だけから platform evidence として断定しない。

### targetSdkVersion 37 Behavior

- targetSdkVersion 37 以上で適用されるか: 公式文書上は Yes と読めるが、AOSP gate 未確認。
- Android 17 以外で targetSdkVersion 37 にした場合の挙動: Unknown。公式文書は Android 17 Behavior Changes として説明しているため、Android 17 platform behavior として扱う。
- opt-out / temporary override の有無: Unknown。公式抜粋には opt-out は示されていない。compat framework による force enable / disable は未確認。

### Other Conditions

- device/form factor: 公式抜粋では条件なし。
- permission: 公式抜粋では条件なし。file access permission / app private storage permission は実装上関係する可能性があるが AOSP 未確認。
- API usage: `System.load()`、dynamic native library loading、native file deployment / extraction / download / update。
- manifest attribute: 公式抜粋では条件なし。
- component boundary: app process、Java `System.load()` API、ART / runtime native loader、filesystem metadata、native linker にまたがる可能性がある。

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

未確認。Android 17 AOSP tag 取得後に、少なくとも以下の候補を tag 比較で確認する必要がある。

- `core/java/java/lang/System.java` または `System.load()` の framework-visible API source
- `core/java/dalvik/system/Runtime.java` / native loading 関連の Java boundary
- `core/java/dalvik/system/BaseDexClassLoader.java` など Android 14 Safer DCL との関連候補
- `core/java/android/os/Build.java` / target SDK gate 参照候補
- compat framework 定義ファイル内の native DCL / safer DCL / dynamic code loading / targetSdkVersion 37 関連 Change ID

Note:
- `System.load()` の最終的な native loader、ART runtime、bionic linker、filesystem check は `frameworks-base` 以外の AOSP project にある可能性が高い。ただし、この mission は `frameworks-base` evidence を対象としているため、Android 17 tag 入手後は `frameworks-base` 内の app-facing API boundary、compat framework、targetSdkVersion gate の有無を優先して確認する。

## Source Context Reviewed

Android 17 AOSP tag がないため、source context は未レビュー。

| File / symbol | Android 16 baseline | Android 17 behavior | Why this code path matters |
| --- | --- | --- | --- |
| Not reviewed | Not reviewed | Not reviewed | Android 17 tag がないため、公式文書の記述を AOSP diff で検証できない。 |

Required context:
- Entry point / caller: 未確認。想定される entry point は app code の `System.load(path)`、Java runtime boundary、native loader / linker だが、AOSP evidence としては未採用。
- Relevant class or service responsibility: 未確認。
- Runtime path from app API / system event to changed code: 未確認。
- Why unrelated code paths were excluded: Android 17 tag 不在のため、source path の採否判断自体を保留。

## Diff Interpretation

| Observed diff | Interpretation | Behavior Change relevance | Confidence |
| --- | --- | --- | --- |
| No Android 17 tag diff available | Source diff type cannot be classified yet | 公式文書の native DCL extension、read-only native file requirement、`UnsatisfiedLinkError`、targetSdkVersion gate を source diff で裏取りできていない | Low |

Required interpretation:
- Added behavior: 未確認。公式文書上は native files への DCL protection extension なので added behavior の可能性がある。
- Removed behavior: 未確認。
- Changed condition / gate: 未確認。targetSdkVersion 37 gate がある可能性は高いが、AOSP 未確認。
- Changed default: 未確認。
- No behavior change found: 未確認。tag 不在のため「no behavior change」とは判断しない。

## Evidence

Facts:
- 公式 Behavior Change 文書は、targetSdkVersion 37 以上のアプリで Safer Dynamic Code Loading protection が native libraries にも拡張されると述べている。
- 公式文書は、この DCL protection が Android 14 で DEX / JAR files 向けに導入されたものだと述べている。
- 公式文書は、`System.load()` で読み込まれる all native files は read-only として mark されている必要があると述べている。
- 公式文書は、条件を満たさない場合 system が `UnsatisfiedLinkError` を throw すると述べている。
- 公式文書は、dynamic code loading は code injection / code tampering による compromise risk を高めるため、可能な限り避けることを推奨している。
- local `frameworks-base` には `android-16.0.0_r4` tag がある。
- local `frameworks-base` には `android-17*` tag がない。
- 調査時点で `frameworks-base` working tree は clean。

Observations:
- 公式ページ種別は targetSdkVersion 37 以上向けである。
- 原文は `If your app targets Android 17 (API level 37) or higher` と明示しており、targetSdkVersion 37 gate がある可能性が高い。
- この項目は targetSdkVersion 37 条件に加えて、`System.load()`、native file、read-only file state という runtime / API usage condition を含む。
- 影響は dynamic native library loading を使うアプリに集中し、通常の APK / AAB に同梱された native library を標準ロードするだけのアプリでは限定的な可能性がある。ただし AOSP 未確認。
- AOSP tag がないため、実装が本当に targetSdkVersion 37 gate で制御されているかは未確認。
- Compat framework entry の有無も未確認。

Hypotheses:
- Android 17 / targetSdkVersion 37 以上では、writable な temporary file や app private storage に展開した native library をそのまま `System.load()` すると `UnsatisfiedLinkError` になる可能性が高い。
- Android 17 / targetSdkVersion 36 のアプリでは旧挙動が維持される可能性があるが、AOSP gate 未確認のため断定しない。
- dynamic native library を使う必要がある場合、書き込み完了後に file permission を read-only に変更してから load する必要がある可能性が高い。ただし exact requirement は AOSP / 実機検証待ち。

Conclusions:
- 現時点で顧客向けに確定できるのは、「公式文書上は Android 17 / targetSdkVersion 37 以上のアプリで、`System.load()` する native files は read-only 必須となり、違反時は `UnsatisfiedLinkError` が発生する」という範囲まで。
- AOSP gate、read-only 判定、native loader path、compat framework default state が未確認のため、primary classification は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

## Applicability Gate Evidence

- targetSdkVersion gate: 未確認。公式文書は targetSdkVersion 37 以上を示すが、AOSP gate evidence はない。
- CompatChanges.isChangeEnabled / ChangeId: 未確認。Android 17 tag がないため検索未実施。
- @EnabledAfter / @EnabledSince / default state: 未確認。Android 17 tag がないため検索未実施。
- Build.VERSION / SDK_INT gate: 未確認。
- DeviceConfig / resources config: 未確認。
- Permission/AppOps gate: 未確認。
- Manifest/property gate: 未確認。
- No gate found: 未確認。Android 17 tag がないため「gate がない」とは判断しない。
- Gate conclusion: Unknown。公式文書の wording から targetSdkVersion 37 + `System.load()` + native file read-only condition と推定されるが、AOSP で検証できていない。
- Reasoning from source context: source context 未レビューのため未確定。

---

# Impact Analysis

## Affected Apps

影響を受ける可能性があるアプリ:
- 実行時に `.so` などの native library をダウンロード、生成、展開、更新してから `System.load()` するアプリ。
- plugin、hotfix、feature module、ML / game engine / media engine などで native code を動的に扱うアプリ。
- app private storage や temporary directory に native file を書き込み、その直後に writable なまま load しているアプリ。
- targetSdkVersion 37 への更新を予定しており、native DCL の file permission をまだ検証していないアプリ。

## Non-Affected Apps

影響が限定的または対象外と考えられるケース:
- dynamic native library loading を行わないアプリ。
- APK / AAB に同梱された native libraries を通常の `System.loadLibrary()` / platform loader 経由で読み込むだけのアプリ。ただし `System.loadLibrary()` との境界は AOSP 未確認。
- dynamic code loading を避け、配布時に native code を固定しているアプリ。
- Android 17 AOSP tag 取得後に対象外 gate や exemption が確認されたケース。

---

# Customer Impact

顧客説明用。

## Impact Level

- Human decision required

※ 仮評価。最終判断は人間が行う。

## Business Impact

- ユーザー影響: native library load が `UnsatisfiedLinkError` で失敗すると、アプリ起動、特定機能、plugin、ゲームエンジン、メディア処理などが利用不能になる可能性がある。
- 運用影響: dynamic native library の配布、更新、展開、permission 設定、rollback 手順を確認する必要がある可能性がある。
- 開発影響: DCL 自体の削減、`System.load()` 利用箇所の棚卸し、file permission の read-only 化、targetSdkVersion 37 環境での native load test が必要になる可能性がある。

---

# Required Actions

## Must

- `System.load()` の利用箇所を検索し、読み込む native file の生成元、保存先、permission を棚卸しする。
- 実行時に書き込んだ native file を load している場合、書き込み完了後に read-only として mark される設計に変更できるか確認する。
- dynamic native code loading が本当に必要かを見直し、可能なら APK / AAB 配布時に native library を同梱する方式へ寄せる。
- Android 17 / targetSdkVersion 37 のテスト環境が利用可能になったら、writable / read-only の native file で `System.load()` の結果を検証する。
- Android 17 AOSP tag 入手後に、targetSdkVersion gate、read-only 判定、compat Change ID を再確認する。

## Recommended

- dynamic native library の download / extraction / verification / permission change / load の順序を明文化する。
- native file の integrity check、signature verification、atomic write、permission hardening を組み合わせて code tampering risk を下げる。
- `UnsatisfiedLinkError` 発生時の fallback、ログ、メトリクス、リカバリ手順を整備する。
- Android 14 の DEX / JAR Safer DCL 対応状況も併せて確認し、dynamic code loading 全体の棚卸しを行う。

## Optional

- plugin / hotfix framework を利用している場合、vendor documentation で Android 17 / targetSdkVersion 37 対応状況を確認する。
- dynamic loading をやめられない場合、security review で code injection / code tampering threat model を更新する。

---

# Verification Method

## Matrix

| Device OS | targetSdkVersion | Compat flag | Expected behavior |
| --- | --- | --- | --- |
| Android 16 | 36 | default | Android 16 baseline。native file の read-only requirement は Android 17 tag 比較待ち。 |
| Android 17 | 36 | default | Unknown。この section は targetSdkVersion 37+ 向けだが、AOSP gate 未確認。 |
| Android 17 | 37 | default | 公式文書上、`System.load()` する native files は read-only 必須。違反時は `UnsatisfiedLinkError`。 |
| Android 17 | 36 | force-enabled if available | Unknown。Compat Change ID 未確認。 |
| Android 17 | 37 | force-disabled if available | Unknown。Compat Change ID 未確認。 |

## Steps

- targetSdk変更: targetSdkVersion 36 と 37 の test build を用意する。
- compat framework command: 未確認。Android 17 compat framework entry / Change ID が判明後に記録する。
- テスト方法: 同一 native library file を writable / read-only の 2 状態で用意し、`System.load()` の成功 / `UnsatisfiedLinkError` を比較する。
- 再現手順: Android 17 device / emulator で対象アプリを install し、app private storage に native file を展開する。permission を writable のまま load するケースと read-only に変更してから load するケースを比較する。
- 期待結果: targetSdkVersion 37 のアプリでは、read-only でない native file の `System.load()` が `UnsatisfiedLinkError` で失敗する。具体的な file mode requirement は AOSP tag と実機検証待ち。

---

# Conclusion

公式文書上、Android 17 / targetSdkVersion 37 以上のアプリでは Safer DCL protection が native libraries に拡張され、`System.load()` で読み込む native files は read-only 必須になる。違反時は `UnsatisfiedLinkError` が発生するため、dynamic native library loading を使うアプリは targetSdkVersion 37 更新前に棚卸しと検証が必要である。

ただし、Android 17 AOSP tag が local checkout にないため、実装 gate、read-only 判定、native loader path、compat framework の確認は未完了である。最終的な適用分類と顧客向け確定説明は、Android 17 AOSP tag 入手後に再調査が必要である。

---

# Human Decision Placeholder

Final Priority:
- Human decision required

Final Severity:
- Human decision required

Release Readiness:
- Human decision required

Customer Communication Priority:
- Human decision required

Decision:
- Further investigation required

Decision notes:
- Android 17 AOSP tag 入手後に、AOSP evidence と compat framework evidence を確認してから最終判断する。

---

# References

## Documentation

- https://developer.android.com/about/versions/17/behavior-changes-17

## AOSP

- Not available for Android 17 in local `frameworks-base`.
- From tag checked: `android-16.0.0_r4`
- To tag checked: no local `android-17*` tag found.
