# ECH (Encrypted Client Hello) enabled

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
- https://developer.android.com/privacy-and-security/security-config#domainEncryption
- https://developer.android.com/privacy-and-security/security-config#EncryptedClientHelloSummary
- https://www.rfc-editor.org/rfc/rfc9849.html#name-grease-ech

Section:
ECH (Encrypted Client Hello) enabled

Page type:
- Apps targeting Android 17 or higher

### Classification Snapshot

Primary classification:
- UNKNOWN_NEEDS_MORE_EVIDENCE

Initial applicability assumption from official documentation:
- 公式 Behavior Change 文書は、targetSdkVersion 37 以上のアプリでは TLS connection に ECH が使われると説明している。
- ただし ECH が実際に有効になるには、アプリが使う networking library が ECH を統合していること、remote server が ECH protocol をサポートしていることが必要。
- Network Security Configuration の `<domainEncryption>` により、global または per-domain で ECH mode を `"enabled"` / `"disabled"` に設定できる。
- local `frameworks-base` に Android 17 AOSP tag がないため、AOSP gate、Network Security Configuration parser diff、Compat Change ID、default state は未検証である。確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

At-a-glance impact:

| Question | Answer | Evidence |
| --- | --- | --- |
| Android 17 OS update only? | Unknown | 公式ページは targetSdkVersion 37+ 向け。AOSP gate 未確認。 |
| targetSdkVersion 37 required? | Likely, but unverified | 公式文書と Network Security Configuration docs は API 37+ の default enabled を示す。AOSP evidence は未取得。 |
| Additional runtime conditions? | Yes | networking library ECH support、remote server ECH support、TLS connection、`<domainEncryption>` mode が条件。 |
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
- Permission/API/component condition: TLS connection、ECH 対応 networking library、ECH 対応 server、Network Security Configuration の `<domainEncryption>` mode。
- App state/process condition: remote endpoint への TLS handshake 実行時。

Compat framework:
- Change ID: Unknown
- Change name: Unknown
- Default state: Unknown
- Toggleable for testing: Unknown

Classification confidence:
- Low

Classification evidence:
- Official documentation page: `behavior-changes-17`
- Original applicability statement: targetSdkVersion 37 以上のアプリでは TLS connection に ECH が使われる。
- AOSP targetSdk gate: 未確認。local `frameworks-base` に `android-17*` tag がない。
- Compat framework entry: 未確認。Android 17 compat framework evidence が未取得。

---

# Executive Summary

Android 17 では、targetSdkVersion 37 以上のアプリに対して Encrypted Client Hello (ECH) の platform support が導入される、と公式文書は説明している。ECH は TLS handshake の Server Name Indication (SNI) を暗号化し、ネットワーク観測者が接続先ドメインを特定しにくくするための privacy 機能である。

実際に ECH が使われるには、アプリが使う networking library が ECH に対応し、接続先 server も ECH をサポートしている必要がある。ECH を negotiated できない場合は ECH GREASE が送信される。また、Android 17 では Network Security Configuration に `<domainEncryption>` が追加され、global または per-domain で ECH を enabled / disabled にできる。

ただし、現時点の local `frameworks-base` には Android 17 AOSP tag がないため、実装差分、targetSdkVersion gate、Compat Change ID、default state は未確認である。

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
- ECH (Encrypted Client Hello) enabled

Original statement being verified:

> ECH is used for TLS connections

The supplied official text states that for apps targeting Android 17 / API level 37 or higher, ECH is used for TLS connections. It also states that ECH only becomes active when both the app's networking library and the remote server support ECH, that failed negotiation results in ECH GREASE, and that `<domainEncryption>` can customize the behavior globally or per domain.

## Interpretation

この変更は、targetSdkVersion 37 以上のアプリにおける TLS 接続の privacy behavior を変更する。従来の TLS handshake では SNI により接続先ドメインが観測され得るが、ECH は SNI を含む ClientHello の機微情報を暗号化し、接続先ドメインの露出を減らす。

ただし、アプリ単体の targetSdkVersion だけで必ず ECH が negotiated されるわけではない。networking library、server support、DNS / ECH configuration、Network Security Configuration の `<domainEncryption>` mode が実際の挙動を左右する。

---

# What Changed

公式文書上の変更点:
- Android 17 は ECH の platform support を導入する。
- targetSdkVersion 37 以上のアプリでは TLS connection に ECH が使われる。
- ECH は networking library が ECH support を統合し、remote server も ECH protocol をサポートしている場合に active になる。
- ECH を negotiated できない場合、client は randomized contents を持つ ECH extension、つまり ECH GREASE を送る。
- Android 17 は Network Security Configuration に `<domainEncryption>` element を追加する。
- `<domainEncryption>` は `<base-config>` または `<domain-config>` 内で使え、global または per-domain に ECH mode を `"enabled"` / `"disabled"` へ設定できる。
- Network Security Configuration docs は、`<domainEncryption>` の default mode が targetSdkVersion 37 以上では `"enabled"`、それ以外では `"disabled"` と説明している。

AOSP で未確認の点:
- Android 16 baseline で ECH / `<domainEncryption>` が存在しなかったこと。
- Android 17 で追加された Network Security Configuration parser / policy の diff。
- targetSdkVersion 37 gate の実装箇所。
- ECH mode default `"enabled"` / `"disabled"` の実装。
- HttpEngine、WebView、OkHttp など library integration との接続点。
- Compat Change ID と default state。

## Applicability

公式文書の一次判断では、Android 17 以上、targetSdkVersion 37 以上、TLS connection、ECH 対応 networking library、ECH 対応 server、`<domainEncryption>` mode が条件となる。AOSP tag が未取得のため、確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

### OS Update Behavior

- Android 17 にアップデートしただけで適用されるか: Unknown
- targetSdkVersion に依存しない根拠: なし。公式文書は targetSdkVersion 37 以上を明示している。
- Android 16 以前での挙動: Network Security Configuration docs は Android 16 以下では ECH は available ではないと説明しているが、AOSP tag 比較は未実施。

### targetSdkVersion 37 Behavior

- targetSdkVersion 37 以上で適用されるか: 公式文書上は Yes と読めるが、AOSP gate 未確認。
- Android 17 以外で targetSdkVersion 37 にした場合の挙動: Unknown。公式文書と Network Security Configuration docs は Android 17 / API level 37 以上の機能として説明している。
- opt-out / temporary override の有無: `<domainEncryption mode="disabled"/>` による opt-out が公式 docs で説明されている。compat framework による force enable / disable は未確認。

### Other Conditions

- device/form factor: 公式抜粋では条件なし。
- permission: 公式抜粋では条件なし。
- API usage: TLS connection を行う networking library。例として HttpEngine、WebView、OkHttp が挙げられている。
- manifest attribute: Network Security Configuration file の指定が関係する可能性がある。
- component boundary: platform Network Security Configuration、networking library、remote server の三者にまたがる。

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

- `core/java/android/security/net/config/NetworkSecurityConfig.java`
- `core/java/android/security/net/config/XmlConfigSource.java`
- `core/java/android/security/net/config/ConfigSource.java`
- `core/java/android/security/net/config/ApplicationConfig.java`
- `core/java/android/security/NetworkSecurityPolicy.java`
- API surface files for Network Security Configuration / policy exposure, if any
- compat framework 定義ファイル内の ECH / domain encryption / Network Security Configuration 関連 Change ID

Note:
- 実際の ECH handshake implementation は networking library や TLS stack 側にある可能性がある。今回の mission は `frameworks-base` evidence に限定されているため、library / TLS stack 側は Android 17 tag 公開後の追加調査対象として扱う。

## Source Context Reviewed

Android 17 AOSP tag がないため、source context は未レビュー。

| File / symbol | Android 16 baseline | Android 17 behavior | Why this code path matters |
| --- | --- | --- | --- |
| Not reviewed | Not reviewed | Not reviewed | Android 17 tag がないため、公式文書の記述を AOSP diff で検証できない。 |

Required context:
- Entry point / caller: 未確認。想定される entry point は app TLS connection、Network Security Configuration parsing、networking library の TLS handshake setup だが、AOSP evidence としては未採用。
- Relevant class or service responsibility: 未確認。
- Runtime path from app API / system event to changed code: 未確認。
- Why unrelated code paths were excluded: Android 17 tag 不在のため、source path の採否判断自体を保留。

## Diff Interpretation

| Observed diff | Interpretation | Behavior Change relevance | Confidence |
| --- | --- | --- | --- |
| No Android 17 tag diff available | Source diff type cannot be classified yet | 公式文書の ECH default behavior と `<domainEncryption>` 追加を source diff で裏取りできていない | Low |

Required interpretation:
- Added behavior: 未確認。
- Removed behavior: 未確認。
- Changed condition / gate: 未確認。
- Changed default: 未確認。
- No behavior change found: 未確認。tag 不在のため「no behavior change」とは判断しない。

## Evidence

Facts:
- 公式 Behavior Change 文書は、Android 17 が ECH platform support を導入すると述べている。
- 公式文書は、targetSdkVersion 37 以上のアプリでは TLS connection に ECH が使われると述べている。
- 公式文書は、ECH が active になるには networking library と remote server の ECH support が必要と述べている。
- 公式文書は、ECH を negotiated できない場合に ECH GREASE が送信されると述べている。
- 公式文書は、Network Security Configuration に `<domainEncryption>` が追加され、`<base-config>` / `<domain-config>` 内で ECH mode を指定できると述べている。
- Network Security Configuration docs は、`<domainEncryption>` の default mode が API level 37 以上で `"enabled"`、それ以外で `"disabled"` と説明している。
- RFC 9849 は、ECH を実装する client が実 ECH extension または GREASE ECH extension を送る client behavior を定義している。
- local `frameworks-base` には `android-16.0.0_r4` tag がある。
- local `frameworks-base` には `android-17*` tag がない。
- 調査時点で `frameworks-base` working tree は clean。

Observations:
- 公式ページ種別は targetSdkVersion 37 以上向けである。
- この項目は privacy behavior change と Network Security Configuration の新要素追加の両方を含む。
- 実際の ECH negotiated behavior は、app targetSdkVersion だけでなく networking library と server support に依存する。
- `<domainEncryption mode="disabled"/>` により opt-out できる。
- AOSP tag がないため、実装が本当に targetSdkVersion 37 gate で制御されているかは未確認。
- Compat framework entry の有無も未確認。

Hypotheses:
- Android 17 / targetSdkVersion 37 以上では、Network Security Configuration の default domain encryption mode が enabled になり、ECH 対応 library が TLS handshake 時に ECH または ECH GREASE を送る可能性が高い。
- targetSdkVersion 36 のアプリでは default mode が disabled の可能性が高いが、AOSP gate 未確認のため断定しない。
- 一部の enterprise network、TLS inspection、domain-based filtering、allowlist / blocklist 運用では、SNI visibility 低下または GREASE extension により観測・制御の前提が変わる可能性がある。

Conclusions:
- 現時点で顧客向けに確定できるのは、「公式文書上は Android 17 / targetSdkVersion 37 以上で ECH が default enabled になり、library / server support と `<domainEncryption>` 設定に依存する」という範囲まで。
- AOSP gate、Network Security Configuration parser diff、compat framework default state が未確認のため、primary classification は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

## Applicability Gate Evidence

- targetSdkVersion gate: 未確認。Android 17 AOSP tag がないため、`targetSdkVersion` / `ApplicationInfo.targetSdkVersion` 検索は実施していない。
- CompatChanges.isChangeEnabled / ChangeId: 未確認。Android 17 AOSP tag がないため、`CompatChanges.isChangeEnabled` / `@ChangeId` / `@EnabledAfter` / `@EnabledSince` 検索は実施していない。
- @EnabledAfter / @EnabledSince / default state: 未確認。
- Build.VERSION / SDK_INT gate: 未確認。
- DeviceConfig / resources config: 未確認。
- Permission/AppOps gate: 公式文書上は permission 条件なし。AOSP 未確認。
- Manifest/property gate: Network Security Configuration の `<domainEncryption>` mode が関係する。manifest で network security config file を指定する構成は未確認。
- No gate found: 未判断。検索不能のため「gate なし」とは扱わない。
- Gate conclusion: Unknown。公式文書上の Android 17 / targetSdkVersion 37 / library support / server support / config 条件はあるが、AOSP evidence が不足している。
- Reasoning from source context: source context 未取得のため不可。

Searched:
- `frameworks-base` checkout status。
- `android-16.0.0_r4` tag の存在。
- `android-17*` tag の存在。

Not searched yet:
- Android 17 implementation files。
- Android 17 compat framework definitions。
- Android 17 API surface files。
- networking library / TLS stack integration points。

Reason:
- Android 17 target tag が local checkout に存在しないため、tag 間 diff による platform evidence が作れない。

---

# Impact Analysis

## Affected Apps

影響を受ける可能性があるアプリ:
- targetSdkVersion 37 以上への更新を予定しているアプリ。
- HTTPS / TLS connection を行い、ECH 対応 networking library を使うアプリ。
- HttpEngine、WebView、OkHttp などの ECH 対応版を使うアプリ。
- 接続先 server が ECH をサポートしているアプリ。
- Network Security Configuration を使い、domain ごとに通信ポリシーを制御しているアプリ。
- enterprise network、TLS inspection、SNI ベースの allowlist / blocklist、通信監視環境で動作するアプリ。

## Non-Affected Apps

影響が限定的と考えられるケース:
- TLS connection を行わないアプリ。
- ECH 非対応 networking library のみを使うアプリ。
- 接続先 server が ECH をサポートせず、かつ ECH GREASE も disabled にしている構成。
- `<domainEncryption mode="disabled"/>` で対象 domain の ECH / ECH GREASE を無効化している構成。
- targetSdkVersion 37 へ上げないアプリ。ただし、これは公式文書からの一次判断であり、AOSP gate 未確認。

---

# Customer Impact

## Impact Level

- Human decision required

※ 最終 severity / priority は人間が判断する。このレポートでは確定しない。

## Business Impact

- ユーザー影響: SNI が暗号化されることで、ユーザーの接続先ドメインがネットワーク観測者に見えにくくなり privacy が向上する可能性がある。
- 運用影響: SNI を前提とする enterprise proxy、TLS inspection、domain filtering、traffic monitoring では、接続判定や可観測性の前提が変わる可能性がある。
- 開発影響: targetSdkVersion 37 更新前に、利用 networking library の ECH 対応状況、server support、Network Security Configuration の `<domainEncryption>` policy を確認する必要がある。

---

# Required Actions

## Must

- アプリが使う networking library が ECH をサポートしているか確認する。
- 接続先 server / CDN / hosting provider が ECH をサポートしているか確認する。
- enterprise network、TLS inspection、SNI ベース制御が関係する顧客環境があるか確認する。
- targetSdkVersion 37 更新前に Android 17 上で主要 endpoint への TLS 接続テストを行う。

## Recommended

- Network Security Configuration に `<domainEncryption>` を追加する必要がある domain がないか確認する。
- ECH を許可したい domain と、互換性理由で一時的に disable したい domain を分ける。
- failure 時の telemetry を用意し、ECH negotiation failure、ECH GREASE、TLS handshake failure、HTTP layer failure を区別できるようにする。
- WebView / OkHttp / HttpEngine などの library version と Android 17 support note を確認する。

## Optional

- Android 17 AOSP tag 公開後、`<domainEncryption>` parser / policy diff と compat Change ID を再調査する。
- packet capture / TLS handshake logging が可能な検証環境で、ECH enabled / disabled の差分を観測する。

---

# Verification Method

## Matrix

| Device OS | targetSdkVersion | Compat flag | Expected behavior |
| --- | --- | --- | --- |
| Android 16 | 36 | default | Android 16 baseline。公式 docs では ECH は available ではない。AOSP baseline diff は未確認。 |
| Android 17 | 36 | default | Unknown。Network Security Configuration docs は API 37 未満で default disabled と示すが、AOSP gate 未確認。 |
| Android 17 | 37 | default | 公式文書上は ECH が TLS connection に使われる。library / server support がある場合に active。未 negotiated 時は ECH GREASE。 |
| Android 17 | 36 | force-enabled if available | Unknown。Compat Change ID 未確認。`<domainEncryption mode="enabled"/>` による config 明示は別途検証対象。 |
| Android 17 | 37 | force-disabled if available | Unknown。Compat Change ID 未確認。`<domainEncryption mode="disabled"/>` による opt-out は公式 docs 上あり。 |

## Steps

- targetSdk変更: test app を targetSdkVersion 36 と 37 で build し、Android 17 上で同じ endpoint へ TLS connection を行う。
- compat framework command: Change ID 未確認のため未定。Android 17 tag / compat page 確認後に追加する。
- テスト方法: ECH 対応 server と非対応 server、ECH 対応 networking library と非対応 library、`<domainEncryption mode="enabled"/>` / `"disabled"` を組み合わせる。
- 再現手順: TLS handshake、connection success / failure、server support、network observer 上の SNI visibility、GREASE extension の有無を比較する。
- 期待結果: targetSdkVersion 37 かつ ECH 対応 library / server では ECH が active になる。ECH negotiated 不可の場合は ECH GREASE が送信される。targetSdkVersion 36 の結果は AOSP gate 確認待ち。

---

# Conclusion

公式文書は、Android 17 で targetSdkVersion 37 以上のアプリに ECH support が導入され、TLS connection の SNI 露出を減らすと説明している。実際の効果は、networking library、server support、Network Security Configuration の `<domainEncryption>` mode に依存する。

一方で、local `frameworks-base` に Android 17 AOSP tag がないため、実装差分、targetSdkVersion gate、Network Security Configuration parser diff、Compat Change ID、default state を検証できていない。現時点の primary classification は `UNKNOWN_NEEDS_MORE_EVIDENCE`、confidence は Low とする。

Human decision placeholder:
- Final priority: Human decision required
- Final severity: Human decision required
- Release readiness: Human decision required
- Customer communication priority: Human decision required
- Next required human decision: Android 17 AOSP tag 公開後に再調査するか、公式 documentation ベースの暫定 privacy / networking guidance として扱うかを判断する。
