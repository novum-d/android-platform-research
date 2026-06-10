# Enable CT by default

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
- https://developer.android.com/privacy-and-security/security-config#CertificateTransparencySummary
- https://developer.android.com/privacy-and-security/security-config#certificateTransparency

Section:
Enable CT by default

Page type:
- Apps targeting Android 17 or higher

### Classification Snapshot

Primary classification:
- UNKNOWN_NEEDS_MORE_EVIDENCE

Initial applicability assumption from official documentation:
- 公式文書は、targetSdkVersion 37 以上のアプリでは certificate transparency (CT) が default で enabled になると説明している。
- Android 16 では CT は利用可能だったが、アプリが opt in する必要があったと説明している。
- 追加条件として、TLS / HTTPS 接続、証明書チェーン、CT log 証明、Network Security Config による opt-in / opt-out などが関係する可能性がある。
- ただし、local `frameworks-base` に Android 17 AOSP tag がないため、CT default の実装差分、targetSdkVersion gate、Network Security Config の解釈、compat framework entry、default state は未検証である。確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

At-a-glance impact:

| Question | Answer | Evidence |
| --- | --- | --- |
| Android 17 OS update only? | Unknown | 公式文書は apps targeting Android 17 / API level 37 or higher と述べるが、AOSP gate 未確認。 |
| targetSdkVersion 37 required? | Likely, but unverified | 原文は If an app targets Android 17 / API level 37 or higher と述べている。 |
| Additional runtime conditions? | Yes | TLS / HTTPS 接続、証明書チェーン、CT policy、Network Security Config が関係する可能性。 |
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
- Permission/API/component condition: TLS / HTTPS 通信、platform trust manager / Network Security Config、certificate transparency policy。
- App state/process condition: アプリがサーバー証明書を検証するネットワーク接続を行う時点。

Compat framework:
- Change ID: Unknown
- Change name: Unknown
- Default state: Unknown
- Toggleable for testing: Unknown

Classification confidence:
- Low

Classification evidence:
- Official documentation page: `behavior-changes-17`
- Original applicability statement: apps targeting Android 17 / API level 37 or higher have CT enabled by default; Android 16 required opt-in.
- AOSP targetSdk gate: 未確認。local `frameworks-base` に `android-17*` tag がない。
- Compat framework entry: 未確認。Android 17 compat framework evidence が未取得。

---

# Executive Summary

Android 17 では、targetSdkVersion 37 以上のアプリで certificate transparency (CT) が default で enabled になる、と公式文書は説明している。Android 16 では CT は利用可能だったが、Network Security Config などでアプリが opt in する必要があった。

この変更により、公開 TLS 証明書を使う HTTPS 接続で CT 要件を満たさない証明書チェーンがある場合、targetSdkVersion 37 更新後に接続失敗などの互換性影響が発生する可能性がある。特に独自 CA、private PKI、検証環境、証明書発行運用が CT に対応していない場合は確認が必要である。

ただし、現時点の local `frameworks-base` には Android 17 AOSP tag がないため、実装差分、targetSdkVersion gate、opt-out / exception、Compat Change ID は未確認である。

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
- Enable CT by default

Original statement being verified:

> If an app targets Android 17 (API level 37) or higher, certificate transparency (CT) is enabled by default. (On Android 16, CT is available but apps had to opt in.)

## Interpretation

この変更は、Network Security Config / platform TLS validation における certificate transparency の default policy を、targetSdkVersion 37 以上のアプリで opt-in から default enabled に変える security behavior change である。

アプリ開発者にとって重要なのは、targetSdkVersion 37 へ更新しただけで、従来 CT に opt in していなかった TLS 接続にも CT 検証が適用される可能性がある点である。証明書やサーバー運用が CT 要件を満たしていない場合、通信失敗として現れる可能性がある。

---

# What Changed

公式文書上の変更点:
- Android 17 / targetSdkVersion 37 以上のアプリでは certificate transparency (CT) が default で enabled になる。
- Android 16 では CT は available だったが、アプリが opt in する必要があった。
- Network Security Config の CT 関連ドキュメントが参照されているため、アプリの network security policy と TLS 証明書検証に関係する変更と考えられる。

AOSP で未確認の点:
- Android 16 baseline で CT が opt-in として実装されている箇所。
- Android 17 で CT default を enabled に変える実装差分。
- targetSdkVersion 37 gate の実装箇所。
- Network Security Config による opt-out / override / domain-specific setting の扱い。
- CT 対象外になる証明書、user-added CA、local trust anchor、debug-overrides、private domain などの例外条件。
- Conscrypt / framework Network Security Config / platform trust manager の境界。
- Compat Change ID と default state。

## Applicability

公式文書の一次判断では、Android 17 以上、targetSdkVersion 37 以上、platform の TLS / HTTPS 証明書検証を使う通信に適用される可能性がある。AOSP tag が未取得のため、確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

### OS Update Behavior

- Android 17 にアップデートしただけで適用されるか: Unknown
- targetSdkVersion に依存しない根拠: なし。原文は If an app targets Android 17 / API level 37 or higher と明示している。
- Android 16 以前での挙動: 公式文書は、Android 16 では CT は available だが opt in が必要だったと述べている。AOSP tag 比較は未実施。

### targetSdkVersion 37 Behavior

- targetSdkVersion 37 以上で適用されるか: 公式文書上は Yes と読めるが、AOSP gate 未確認。
- Android 17 以外で targetSdkVersion 37 にした場合の挙動: Unknown。公式文書は Android 17 Behavior Changes として説明しているため、Android 17 platform behavior として扱う。
- opt-out / temporary override の有無: Unknown。Network Security Config に CT 関連設定があることは関連文書から分かるが、Android 17 default enabled に対する opt-out / domain override の詳細は AOSP 未確認。

### Other Conditions

- device/form factor: 公式抜粋では条件なし。
- permission: 公式抜粋では条件なし。通常のネットワーク通信では `INTERNET` permission が関係するが、CT policy 自体の gate かは未確認。
- API usage: platform trust manager、Network Security Config、HTTPS / TLS、証明書チェーン検証。
- manifest attribute: `android:networkSecurityConfig` が関係する可能性がある。
- component boundary: app process、Network Security Config parser、TrustManager / Conscrypt、certificate transparency verification、server certificate chain にまたがる。

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
- `core/java/android/security/net/config/NetworkSecurityConfigParser.java`
- `core/java/android/security/net/config/CertificatesEntryRef.java`
- `core/java/android/security/net/config/ManifestConfigSource.java`
- `core/res/res/values/attrs_manifest.xml`
- `core/res/res/values/attrs.xml`
- `core/api/current.txt`
- compat framework 定義ファイル内の CT / certificate transparency / targetSdkVersion 37 関連 Change ID

Note:
- 実際の CT verification 実装は Conscrypt や別 project にある可能性がある。ただし、この mission は `frameworks-base` evidence を対象としているため、Android 17 tag 入手後は `frameworks-base` 内の Network Security Config、API surface、compat framework 定義を優先して確認する。

## Source Context Reviewed

Android 17 AOSP tag がないため、source context は未レビュー。

| File / symbol | Android 16 baseline | Android 17 behavior | Why this code path matters |
| --- | --- | --- | --- |
| Not reviewed | Not reviewed | Not reviewed | Android 17 tag がないため、公式文書の記述を AOSP diff で検証できない。 |

Required context:
- Entry point / caller: 未確認。想定される entry point は app の TLS / HTTPS 接続、platform TrustManager、Network Security Config parsing、certificate chain validation だが、AOSP evidence としては未採用。
- Relevant class or service responsibility: 未確認。
- Runtime path from app API / system event to changed code: 未確認。
- Why unrelated code paths were excluded: Android 17 tag 不在のため、source path の採否判断自体を保留。

## Diff Interpretation

| Observed diff | Interpretation | Behavior Change relevance | Confidence |
| --- | --- | --- | --- |
| No Android 17 tag diff available | Source diff type cannot be classified yet | 公式文書の CT default enabled、Android 16 opt-in baseline、targetSdkVersion gate、Network Security Config behavior を source diff で裏取りできていない | Low |

Required interpretation:
- Added behavior: 未確認。
- Removed behavior: 未確認。
- Changed condition / gate: 未確認。
- Changed default: 未確認。公式文書上は opt-in から default enabled への default change だが、AOSP diff 未確認。
- No behavior change found: 未確認。tag 不在のため「no behavior change」とは判断しない。

## Evidence

Facts:
- 公式 Behavior Change 文書は、targetSdkVersion 37 以上のアプリで certificate transparency (CT) が default で enabled になると述べている。
- 公式文書は、Android 16 では CT は available だが、アプリが opt in する必要があったと述べている。
- 公式文書は、Network Security Config の CT summary と CT 設定に関する documentation を参照している。
- local `frameworks-base` には `android-16.0.0_r4` tag がある。
- local `frameworks-base` には `android-17*` tag がない。
- 調査時点で `frameworks-base` working tree は clean。

Observations:
- 公式ページ種別は targetSdkVersion 37 以上向けである。
- 原文は `If an app targets Android 17 (API level 37) or higher` と明示しており、targetSdkVersion 37 gate がある可能性が高い。
- この項目は targetSdkVersion 37 条件に加えて、TLS / HTTPS 証明書検証、CT 対応証明書、Network Security Config の設定という runtime / deployment condition を含む。
- Android 16 で opt-in だったものが Android 17 / targetSdkVersion 37 で default enabled になるため、source diff type は changed default である可能性が高い。ただし AOSP diff 未確認のため確定しない。
- AOSP tag がないため、実装が本当に targetSdkVersion 37 gate で制御されているかは未確認。
- Compat framework entry の有無も未確認。

Hypotheses:
- Android 17 / targetSdkVersion 37 以上では、Network Security Config で明示 opt-in していないアプリでも、platform TLS validation に CT policy が適用される可能性が高い。
- Android 17 / targetSdkVersion 36 のアプリでは Android 16 と同様に opt-in が必要な可能性があるが、AOSP gate 未確認のため断定しない。
- CT に対応していない公開証明書チェーン、検証環境、独自 CA / private PKI を使う通信では、接続失敗または証明書検証エラーが起きる可能性がある。

Conclusions:
- 現時点で顧客向けに確定できるのは、「公式文書上は Android 17 / targetSdkVersion 37 以上のアプリで CT が default enabled になり、Android 16 の opt-in から変わる」という範囲まで。
- AOSP gate、Network Security Config の default 解釈、例外条件、compat framework default state が未確認のため、primary classification は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

## Applicability Gate Evidence

- targetSdkVersion gate: 未確認。公式文書は targetSdkVersion 37 以上を示すが、AOSP gate evidence はない。
- CompatChanges.isChangeEnabled / ChangeId: 未確認。Android 17 tag がないため検索未実施。
- @EnabledAfter / @EnabledSince / default state: 未確認。Android 17 tag がないため検索未実施。
- Build.VERSION / SDK_INT gate: 未確認。
- DeviceConfig / resources config: 未確認。
- Permission/AppOps gate: 未確認。
- Manifest/property gate: 未確認。Network Security Config の CT 設定が関係する可能性はあるが、Android 17 tag で未確認。
- No gate found: 未確認。Android 17 tag がないため「gate がない」とは判断しない。
- Gate conclusion: Unknown。公式文書の wording から targetSdkVersion 37 + TLS / CT conditions と推定されるが、AOSP で検証できていない。
- Reasoning from source context: source context 未レビューのため未確定。

---

# Impact Analysis

## Affected Apps

影響を受ける可能性があるアプリ:
- targetSdkVersion 37 へ更新し、platform TLS / HTTPS 通信を行うアプリ。
- CT に対応していない証明書チェーンを使う backend に接続するアプリ。
- 検証環境、社内環境、private PKI、独自 CA、証明書 pinning と CT policy の組み合わせを持つアプリ。
- Network Security Config で CT に明示 opt-in していなかったが、Android 17 で default enabled の対象になるアプリ。

## Non-Affected Apps

影響が限定的または対象外と考えられるケース:
- ネットワーク通信を行わないアプリ。
- platform TLS / HTTPS 証明書検証を使わない通信だけを行うアプリ。ただし独自 TLS stack の扱いは別途確認が必要。
- すべての接続先証明書チェーンが CT 要件を満たしているアプリ。
- Android 16 ですでに CT に opt in しており、接続先が検証済みのアプリ。
- Android 17 AOSP tag 取得後に対象外 gate や exemption が確認されたケース。

---

# Customer Impact

顧客説明用。

## Impact Level

- Human decision required

※ 仮評価。最終判断は人間が行う。

## Business Impact

- ユーザー影響: CT 要件を満たさない証明書を使う endpoint への接続が失敗すると、ログイン、API 通信、決済、コンテンツ取得などが利用できなくなる可能性がある。
- 運用影響: backend 証明書の発行元、CT log inclusion、検証環境 / staging 環境の証明書運用を確認する必要がある可能性がある。
- 開発影響: Network Security Config、証明書 pinning、debug / staging 設定、targetSdkVersion 37 テストを見直す必要がある可能性がある。

---

# Service Impact Examples（サービス影響例）

このセクションは、公式文書と AOSP evidence から導いた「起こりうる影響例」を記録する。特定サービスで実際に発生確認した事実ではない。

## Example 1（例1）: Public API backend への HTTPS 通信

- 対象サービス例: ログイン API、決済 API、コンテンツ配信 API。
- 影響を受ける実装パターン: CT 要件を満たさない公開証明書チェーンを使う endpoint に platform TLS で接続する実装。
- 発生条件: Android 17 / targetSdkVersion 37 で CT が default enabled になり、証明書チェーンが CT policy を満たさない場合。
- ユーザーに見える症状: API 通信失敗、ログイン不能、決済失敗、コンテンツ取得失敗の可能性。
- 開発・運用への影響: certificate issuance、CT log inclusion、証明書更新手順の確認が必要になる可能性。
- 推奨対応候補: 接続先証明書の CT 対応を棚卸しし、Android 16 opt-in または Android 17 環境で事前検証する。
- 根拠: 公式 statement と report の expected behavior。
- Confidence（信頼度）: Low
- 注意: AOSP gate / exception 条件は未確認。

## Example 2（例2）: Staging / private PKI 環境

- 対象サービス例: QA 環境、社内 API、private CA を使う検証環境。
- 影響を受ける実装パターン: public CT log に載らない証明書や private trust anchor を使う接続。
- 発生条件: Android 17 / targetSdkVersion 37 で CT default policy が staging endpoint にも適用される場合。
- ユーザーに見える症状: 社内検証や beta build でだけ通信失敗する可能性。
- 開発・運用への影響: Network Security Config、debug overrides、private PKI 例外条件の確認が必要になる可能性。
- 推奨対応候補: staging 証明書運用を見直し、CT policy 対象外条件があるか Android 17 AOSP tag 後に確認する。
- 根拠: 公式 statement と report の missing evidence。
- Confidence（信頼度）: Low
- 注意: private CA の扱いは未確認であり、断定しない。

---

# Required Actions

## Must

- アプリの HTTPS / TLS 接続先を棚卸しし、公開証明書チェーンが CT 要件を満たしているか確認する。
- Android 16 で CT に opt in していないアプリは、Android 17 / targetSdkVersion 37 で default enabled になった場合の接続テストを行う。
- Network Security Config の CT 関連設定、debug-overrides、domain-config、certificate pinning の組み合わせを確認する。
- Android 17 AOSP tag 入手後に、targetSdkVersion gate、default policy、opt-out / exception、compat Change ID を再確認する。

## Recommended

- staging / QA / internal API endpoint も含め、証明書発行と CT log inclusion の運用を backend / infra owner と確認する。
- CT 検証失敗時のエラーログ、メトリクス、ユーザー向け fallback を整備する。
- Android 16 の opt-in 設定で事前に CT を有効化し、接続先の互換性を早期検証する。

## Optional

- 証明書 pinning を利用している場合、pin 更新手順と CT policy の関係を security review で確認する。
- 独自 TrustManager / TLS stack を使う箇所があれば、platform CT policy の適用有無を別途整理する。

---

# Verification Method

## Matrix

| Device OS | targetSdkVersion | Compat flag | Expected behavior |
| --- | --- | --- | --- |
| Android 16 | 36 | default | 公式文書上、CT は available だが app opt-in が必要。 |
| Android 17 | 36 | default | Unknown。この section は targetSdkVersion 37+ 向けだが、AOSP gate 未確認。 |
| Android 17 | 37 | default | 公式文書上、CT が default enabled。CT 要件を満たさない証明書チェーンでは接続影響の可能性。 |
| Android 17 | 36 | force-enabled if available | Unknown。Compat Change ID 未確認。 |
| Android 17 | 37 | force-disabled if available | Unknown。Compat Change ID 未確認。 |

## Steps

- targetSdk変更: targetSdkVersion 36 と 37 の test build を用意する。
- compat framework command: 未確認。Android 17 compat framework entry / Change ID が判明後に記録する。
- テスト方法: CT 対応証明書、CT 非対応証明書、staging / private PKI endpoint、Network Security Config の CT 設定あり / なしを分けて HTTPS 接続を確認する。
- 再現手順: Android 17 device / emulator で対象アプリを install し、targetSdkVersion 36 / 37 の両方で同一 endpoint へ接続する。必要に応じて Android 16 opt-in 設定でも比較する。
- 期待結果: targetSdkVersion 37 のアプリでは CT が default enabled になり、CT policy を満たさない証明書チェーンで TLS validation failure が起きる可能性がある。具体的な failure mode は AOSP tag と実機検証待ち。

---

# Conclusion

公式文書上、Android 17 / targetSdkVersion 37 以上のアプリでは certificate transparency が default enabled になり、Android 16 の opt-in 方式から変わる。HTTPS 接続先の証明書が CT 要件を満たしていない場合、targetSdkVersion 37 更新後に通信互換性リスクがある。

ただし、Android 17 AOSP tag が local checkout にないため、実装 gate、Network Security Config の詳細、例外条件、compat framework の確認は未完了である。最終的な適用分類と顧客向け確定説明は、Android 17 AOSP tag 入手後に再調査が必要である。

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
- https://developer.android.com/privacy-and-security/security-config#CertificateTransparencySummary
- https://developer.android.com/privacy-and-security/security-config#certificateTransparency

## AOSP

- Not available for Android 17 in local `frameworks-base`.
- From tag checked: `android-16.0.0_r4`
- To tag checked: no local `android-17*` tag found.
