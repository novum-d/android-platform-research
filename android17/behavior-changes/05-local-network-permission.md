# Local network permission required for apps targeting Android 17

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
- https://developer.android.com/reference/android/Manifest.permission#ACCESS_LOCAL_NETWORK
- https://developer.android.com/privacy-and-security/local-network-permission

Section:
Local network permission required for apps targeting Android 17

Page type:
- Apps targeting Android 17 or higher

### Classification Snapshot

Primary classification:
- UNKNOWN_NEEDS_MORE_EVIDENCE

Initial applicability assumption from official documentation:
- 公式文書は、Android 17 / targetSdkVersion 37 以上のアプリでは local network access に `ACCESS_LOCAL_NETWORK` runtime permission が必要になると説明している。
- 追加条件として、LAN device discovery / connection、local network traffic、system-mediated picker を使わない direct local network communication が関係する。
- ただし、local `frameworks-base` に Android 17 AOSP tag がないため、AOSP gate、permission enforcement path、Compat Change ID、default state は未検証である。確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

At-a-glance impact:

| Question | Answer | Evidence |
| --- | --- | --- |
| Android 17 OS update only? | Unknown | 公式文書は targetSdkVersion 37+ の mandatory enforcement を示すが、AOSP gate 未確認。 |
| targetSdkVersion 37 required? | Likely, but unverified | 公式文書と local network permission docs は targetSdkVersion 37+ の default block / mandatory enforcement を示す。 |
| Additional runtime conditions? | Yes | LAN device discovery / connection、local network traffic、permission grant state、system picker 利用有無。 |
| Compat Change ID involved? | Unknown | Android 17 tag と compat framework evidence が未確認。Android 16 opt-in 用の `RESTRICT_LOCAL_NETWORK` は公式 docs に記載あり。 |

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
- Device/form factor: 公式抜粋では条件なし。LAN / Wi-Fi / Ethernet など local network interface が関係する。
- Permission/API/component condition: `ACCESS_LOCAL_NETWORK` declaration / runtime grant、`NEARBY_DEVICES` permission group、system-mediated picker、LAN device discovery / connection。
- App state/process condition: local network access を試みる時点。

Compat framework:
- Change ID: Unknown
- Change name: Unknown
- Default state: Unknown
- Toggleable for testing: Unknown。Android 16 opt-in guidance では `RESTRICT_LOCAL_NETWORK` compat config が言及されているが、Android 17 default enforcement の compat entry は未確認。

Classification confidence:
- Low

Classification evidence:
- Official documentation page: `behavior-changes-17`
- Original applicability statement: apps targeting Android 17 / API level 37 or higher must use picker path or request `ACCESS_LOCAL_NETWORK` at runtime.
- AOSP targetSdk gate: 未確認。local `frameworks-base` に `android-17*` tag がない。
- Compat framework entry: 未確認。Android 17 compat framework evidence が未取得。

---

# Executive Summary

Android 17 では、targetSdkVersion 37 以上のアプリが LAN device を discover / connect するには、新しい `ACCESS_LOCAL_NETWORK` runtime permission、または system-mediated な privacy-preserving picker の利用が必要になる、と公式文書は説明している。目的は、 unrestricted local network access を使った covert tracking / fingerprinting を防ぐこと。

この permission は既存の `NEARBY_DEVICES` permission group に属するため、ユーザーが同 group の他 permission をすでに許可している場合は再 prompt されない可能性がある。一方、Android 17 / targetSdkVersion 37 以上では local network access が default block になるため、スマートホーム、casting、IoT、mDNS / NSD、LAN device discovery などの機能は対応確認が必要である。

ただし、現時点の local `frameworks-base` には Android 17 AOSP tag がないため、実装差分、targetSdkVersion gate、permission enforcement path、Compat Change ID、default state は未確認である。

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
- Local network permission required for apps targeting Android 17

Original statement being verified:

> ACCESS_LOCAL_NETWORK runtime permission

The supplied official text states that Android 17 introduces `ACCESS_LOCAL_NETWORK` to protect users from unauthorized local network access. It also states that apps targeting Android 17 / API level 37 or higher must either use system-mediated privacy-preserving device pickers or explicitly request the runtime permission to maintain local network communication.

## Interpretation

この変更は、Android 17 / targetSdkVersion 37 以上のアプリに対し、LAN device discovery / connection を dangerous runtime permission または system-mediated picker の制御下に置く privacy behavior change である。

アプリ開発者にとって重要なのは、従来 `INTERNET` permission や socket / NSD / mDNS の利用だけで成立していた local network communication が、targetSdkVersion 37 更新後には default block される可能性がある点である。system picker で十分な use case では広い permission request を避けられるが、home automation や IoT device management のような broad / persistent access には runtime permission request が必要になる。

---

# What Changed

公式文書上の変更点:
- Android 17 は `ACCESS_LOCAL_NETWORK` runtime permission を導入する。
- permission は existing `NEARBY_DEVICES` permission group に属する。
- すでに他の `NEARBY_DEVICES` permission を許可済みのユーザーには、local network access で再 prompt されない場合がある。
- targetSdkVersion 37 以上のアプリは、LAN device との通信維持に 2 つの path を持つ。
- Path A: system-mediated / privacy-preserving device picker を採用し、permission prompt を避ける。
- Path B: `ACCESS_LOCAL_NETWORK` を manifest で宣言し、runtime permission として request する。
- Android 16 では local network permission に opt in できたが、Android 17 では targetSdkVersion 37 以上で enforcement が mandatory になる。
- API reference は `ACCESS_LOCAL_NETWORK` を API level 37 追加の dangerous permission と説明している。
- Local network permission docs は、targetSdkVersion 37 以上では local network が default block になり、legacy app には一時的な implicit grant があると説明している。

AOSP で未確認の点:
- Android 16 baseline の opt-in compat behavior と Android 17 mandatory enforcement の diff。
- local network traffic を block する networking stack enforcement path。
- `ACCESS_LOCAL_NETWORK` permission definition、permission group、split permission migration の implementation。
- targetSdkVersion 37 gate の実装箇所。
- `RESTRICT_LOCAL_NETWORK` または Android 17 対応 Change ID の default state。
- WebView、NsdManager、socket、Cronet、OkHttp など API / library 別の enforcement boundary。

## Applicability

公式文書の一次判断では、Android 17 以上、targetSdkVersion 37 以上、local network access を行うアプリに適用される。system-mediated picker を使う場合は broad runtime permission を回避できる。AOSP tag が未取得のため、確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

### OS Update Behavior

- Android 17 にアップデートしただけで適用されるか: Unknown
- targetSdkVersion に依存しない根拠: なし。公式文書は targetSdkVersion 37 以上で mandatory enforcement と述べる。
- Android 16 以前での挙動: 公式 docs は Android 16 では opt-in 可能、targetSdkVersion 36 では local network access が open と説明しているが、AOSP tag 比較は未実施。

### targetSdkVersion 37 Behavior

- targetSdkVersion 37 以上で適用されるか: 公式文書上は Yes と読めるが、AOSP gate 未確認。
- Android 17 以外で targetSdkVersion 37 にした場合の挙動: Unknown。API reference は permission を API level 37 追加としているため、Android 17 platform behavior として扱う。
- opt-out / temporary override の有無: system-mediated picker path により permission prompt を避ける option がある。compat framework による force enable / disable は未確認。

### Other Conditions

- device/form factor: 公式抜粋では条件なし。
- permission: `ACCESS_LOCAL_NETWORK` runtime permission。`NEARBY_DEVICES` permission group。
- API usage: sockets、platform / managed networking APIs、Cronet / OkHttp など networking libraries、mDNS / `.local` service resolution、NsdManager、WebView host app traffic。
- manifest attribute: `android.permission.ACCESS_LOCAL_NETWORK` declaration が必要。
- component boundary: app process、networking stack、permission controller、system pickers、local network devices にまたがる。

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

- `core/res/AndroidManifest.xml`
- `core/api/current.txt`
- `core/api/system-current.txt`
- `core/java/android/Manifest.java`
- permission controller / permission group definitions linked from `frameworks-base`
- networking stack enforcement entry points exposed through `frameworks-base`, if present
- `NsdManager` / local service picker related APIs
- compat framework 定義ファイル内の `ACCESS_LOCAL_NETWORK` / `RESTRICT_LOCAL_NETWORK` / local network permission 関連 Change ID

Note:
- 公式 local network permission docs は enforcement が networking stack の深い層にあると説明している。実装本体は `frameworks-base` 以外の networking module にある可能性があるが、本 mission では `frameworks-base` evidence の有無を優先して記録する。

## Source Context Reviewed

Android 17 AOSP tag がないため、source context は未レビュー。

| File / symbol | Android 16 baseline | Android 17 behavior | Why this code path matters |
| --- | --- | --- | --- |
| Not reviewed | Not reviewed | Not reviewed | Android 17 tag がないため、公式文書の記述を AOSP diff で検証できない。 |

Required context:
- Entry point / caller: 未確認。想定される entry point は socket / networking library access、NsdManager service discovery、runtime permission request、system picker flow だが、AOSP evidence としては未採用。
- Relevant class or service responsibility: 未確認。
- Runtime path from app API / system event to changed code: 未確認。
- Why unrelated code paths were excluded: Android 17 tag 不在のため、source path の採否判断自体を保留。

## Diff Interpretation

| Observed diff | Interpretation | Behavior Change relevance | Confidence |
| --- | --- | --- | --- |
| No Android 17 tag diff available | Source diff type cannot be classified yet | 公式文書の permission addition / mandatory enforcement / split permission behavior を source diff で裏取りできていない | Low |

Required interpretation:
- Added behavior: 未確認。
- Removed behavior: 未確認。
- Changed condition / gate: 未確認。
- Changed default: 未確認。
- No behavior change found: 未確認。tag 不在のため「no behavior change」とは判断しない。

## Evidence

Facts:
- 公式 Behavior Change 文書は、Android 17 が `ACCESS_LOCAL_NETWORK` runtime permission を導入すると述べている。
- 公式文書は、permission が `NEARBY_DEVICES` group に属すると述べている。
- 公式文書は、targetSdkVersion 37 以上のアプリが LAN device との通信を維持する path として system-mediated picker または explicit runtime permission request を示している。
- 公式文書は、Android 16 では opt-in 可能だった local network permission enforcement が、Android 17 では targetSdkVersion 37 以上で mandatory になると述べている。
- API reference は `ACCESS_LOCAL_NETWORK` を API level 37 追加の dangerous permission と説明している。
- Local network permission docs は、targetSdkVersion 37 以上では local network が default block、targetSdkVersion 37 未満の legacy app は `INTERNET` permission による temporary implicit grant を受けると説明している。
- Local network permission docs は、restrictions が networking stack の深い層に実装され、platform / managed sockets、Cronet、OkHttp などにも適用されると説明している。
- local `frameworks-base` には `android-16.0.0_r4` tag がある。
- local `frameworks-base` には `android-17*` tag がない。
- 調査時点で `frameworks-base` working tree は clean。

Observations:
- 公式ページ種別は targetSdkVersion 37 以上向けである。
- この項目は new dangerous permission、runtime permission prompt、permission group behavior、network stack enforcement を含む。
- system-mediated picker は broad permission request を避ける mitigation path として位置づけられている。
- WebView traffic は host app の permission state を継承する、と公式 docs に記載がある。
- AOSP tag がないため、実装が本当に targetSdkVersion 37 gate で制御されているかは未確認。
- Compat framework entry の有無も未確認。

Hypotheses:
- Android 17 / targetSdkVersion 37 以上では、`ACCESS_LOCAL_NETWORK` grant がない direct local network traffic が networking stack で block される可能性が高い。
- targetSdkVersion 36 の legacy app は temporary implicit grant により従来通り access できる可能性が高いが、AOSP gate 未確認のため断定しない。
- mDNS / `.local` resolution、casting、IoT device management、browser local network access は特に影響を受けやすい可能性がある。

Conclusions:
- 現時点で顧客向けに確定できるのは、「公式文書上は Android 17 / targetSdkVersion 37 以上で local network access が default block になり、picker または `ACCESS_LOCAL_NETWORK` runtime permission が必要になる」という範囲まで。
- AOSP gate、permission definition diff、networking stack enforcement、compat framework default state が未確認のため、primary classification は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

## Applicability Gate Evidence

- targetSdkVersion gate: 未確認。Android 17 AOSP tag がないため、`targetSdkVersion` / `ApplicationInfo.targetSdkVersion` 検索は実施していない。
- CompatChanges.isChangeEnabled / ChangeId: 未確認。Android 17 AOSP tag がないため、`CompatChanges.isChangeEnabled` / `@ChangeId` / `@EnabledAfter` / `@EnabledSince` 検索は実施していない。
- @EnabledAfter / @EnabledSince / default state: 未確認。
- Build.VERSION / SDK_INT gate: API reference は API level 37 追加と説明しているが、AOSP implementation 未確認。
- DeviceConfig / resources config: 未確認。
- Permission/AppOps gate: `ACCESS_LOCAL_NETWORK` runtime permission が公式 docs で説明されている。AOSP permission / AppOps linkage は未確認。
- Manifest/property gate: `android.permission.ACCESS_LOCAL_NETWORK` declaration が必要。AOSP manifest diff は未確認。
- No gate found: 未判断。検索不能のため「gate なし」とは扱わない。
- Gate conclusion: Unknown。公式文書上の Android 17 / targetSdkVersion 37 / permission grant / picker 条件はあるが、AOSP evidence が不足している。
- Reasoning from source context: source context 未取得のため不可。

Searched:
- `frameworks-base` checkout status。
- `android-16.0.0_r4` tag の存在。
- `android-17*` tag の存在。

Not searched yet:
- Android 17 implementation files。
- Android 17 compat framework definitions。
- Android 17 API surface files。
- networking stack enforcement implementation。
- permission controller / AppOps implementation。

Reason:
- Android 17 target tag が local checkout に存在しないため、tag 間 diff による platform evidence が作れない。

---

# Impact Analysis

## Affected Apps

影響を受ける可能性があるアプリ:
- targetSdkVersion 37 以上への更新を予定しているアプリ。
- LAN device discovery / connection を行うアプリ。
- smart home、IoT device management、casting、media receiver discovery、printer / camera / NAS / local server 連携を行うアプリ。
- mDNS / NSD / `.local` resolution を使うアプリ。
- sockets、Cronet、OkHttp、WebView などを通じて local network endpoint に接続するアプリ。
- browser / embedded browser 的に local network resources へアクセスするアプリ。

## Non-Affected Apps

影響が限定的と考えられるケース:
- local network access を行わないアプリ。
- system-mediated picker だけで use case を満たせるアプリ。
- targetSdkVersion 37 へ上げない legacy app。ただし temporary implicit grant は将来維持が保証されるとは限らず、AOSP gate も未確認。
- cellular / VPN のみの通信で、broadcast-capable local network interface を使わないアプリ。

---

# Customer Impact

## Impact Level

- Human decision required

※ 最終 severity / priority は人間が判断する。このレポートでは確定しない。

## Business Impact

- ユーザー影響: permission 未対応のまま targetSdkVersion 37 に上げると、LAN device discovery / connection が失敗し、casting、smart home、IoT、local device setup が動かなくなる可能性がある。
- 運用影響: `NEARBY_DEVICES` group の既存 grant がある場合とない場合で prompt 体験が異なるため、support 手順や permission rationale の整備が必要。
- 開発影響: direct access が必要な機能は manifest declaration、runtime permission request、denial / revocation handling が必要。picker で代替できる機能は broad permission を避ける設計検討が必要。

---

# Required Actions

## Must

- アプリが local network access を行う箇所を棚卸しする。
- targetSdkVersion 37 更新対象アプリで `ACCESS_LOCAL_NETWORK` が必要な use case を特定する。
- direct LAN access が必要な場合、manifest に `android.permission.ACCESS_LOCAL_NETWORK` を宣言し、runtime permission request と denial / revocation handling を実装する。
- Android 17 / targetSdkVersion 37 で LAN device discovery / connection の回帰テストを行う。

## Recommended

- casting や device selection では、system-mediated picker で broad permission を避けられないか検討する。
- mDNS / NSD 利用箇所では `DiscoveryRequest.FLAG_SHOW_PICKER` など、permission 不要の picker path を検討する。
- permission rationale を用意し、local network access が必要な理由をユーザーに説明する。
- WebView / embedded browser が local network endpoint にアクセスする場合、host app の permission state と failure handling を確認する。
- UDP `EPERM`、TCP block reason、socket error、service discovery failure を区別できる telemetry / logging を検討する。

## Optional

- Android 17 AOSP tag 公開後、permission definition、targetSdkVersion gate、networking stack enforcement、compat Change ID を再調査する。
- Android 16 opt-in compat (`RESTRICT_LOCAL_NETWORK`) を使い、targetSdkVersion 37 移行前に影響範囲を先行確認する。

---

# Verification Method

## Matrix

| Device OS | targetSdkVersion | Compat flag | Expected behavior |
| --- | --- | --- | --- |
| Android 16 | 36 | default | 公式 docs 上は local network access は open。Android 16 opt-in は可能。AOSP baseline diff は未確認。 |
| Android 17 | 36 | default | 公式 docs 上は legacy app に temporary implicit grant があり、`INTERNET` permission で access 維持の可能性。AOSP gate 未確認。 |
| Android 17 | 37 | default | 公式文書上は local network が default block。picker path または `ACCESS_LOCAL_NETWORK` runtime grant が必要。 |
| Android 17 | 36 | force-enabled if available | Unknown。Compat Change ID 未確認。Android 16 guidance の `RESTRICT_LOCAL_NETWORK` と Android 17 default enforcement の対応は未確認。 |
| Android 17 | 37 | force-disabled if available | Unknown。Compat Change ID 未確認。 |

## Steps

- targetSdk変更: test app を targetSdkVersion 36 と 37 で build し、Android 17 上で同じ LAN endpoint に接続する。
- compat framework command: Android 17 Change ID 未確認のため未定。Android 16 opt-in guidance では `adb shell am compat enable RESTRICT_LOCAL_NETWORK <package_name>` が記載されている。
- テスト方法: permission 未宣言、permission 宣言のみ、runtime grant 済み、runtime deny / revoke、system picker 利用の各ケースを比較する。
- 再現手順: mDNS / NSD discovery、`.local` resolution、UDP / TCP socket、WebView local endpoint access、casting / IoT device connection を実行する。
- 期待結果: targetSdkVersion 37 では、picker で許可された endpoint または `ACCESS_LOCAL_NETWORK` grant がある場合に通信できる。grant がない direct local network access は block される。targetSdkVersion 36 の結果は AOSP gate 確認待ち。

---

# Conclusion

公式文書は、Android 17 で targetSdkVersion 37 以上のアプリに `ACCESS_LOCAL_NETWORK` runtime permission が必要になり、local network access が default block になると説明している。アプリは system-mediated picker を使って broad permission prompt を避けるか、manifest declaration と runtime permission request により direct LAN access を維持する必要がある。

一方で、local `frameworks-base` に Android 17 AOSP tag がないため、実装差分、targetSdkVersion gate、permission / AppOps linkage、networking stack enforcement、Compat Change ID、default state を検証できていない。現時点の primary classification は `UNKNOWN_NEEDS_MORE_EVIDENCE`、confidence は Low とする。

Human decision placeholder:
- Final priority: Human decision required
- Final severity: Human decision required
- Release readiness: Human decision required
- Customer communication priority: Human decision required
- Next required human decision: Android 17 AOSP tag 公開後に再調査するか、公式 documentation ベースの暫定 privacy / networking guidance として扱うかを判断する。
