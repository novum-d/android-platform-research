# Improved security against Intent redirection attacks 調査レポート

## 基本情報（Metadata）

### 調査対象 Android バージョン（Android Versions）

From:
- android-15.0.0_r36

To:
- android-16.0.0_r4

Note:
- AOSP checkout `frameworks-base` は clean で、`android-15.0.0_r36` / `android-16.0.0_r4` tag の存在を確認した。

Previous targetSdkVersion:
- 35

Target targetSdkVersion:
- 36

### Behavior Change 文書（Behavior Change Source）

Document:
- https://developer.android.com/about/versions/16/behavior-changes-all#intent-redirect-attacks

Page:
- Behavior changes: all apps

Category:
- Security

Section:
- Improved security against Intent redirection attacks

Subsections:
- Opt out of Intent redirection handling
- For applications compiling against Android 16 (API level 36) SDK or higher
- For applications compiling against Android 15 (API level 35) or lower

### 分類スナップショット（Classification Snapshot）

主分類（Primary classification）:
- `OS_UPDATE_ALL_APPS`

早見表（At-a-glance impact）:

| 確認項目（Question） | 回答（Answer） | 根拠（Evidence） |
| --- | --- | --- |
| Android 16 に OS アップデートしただけで適用されるか | Yes / Conditional | 公式 all apps ページは Android 16 上の全アプリ向け変更として掲載している。AOSP Activity launch path では targetSdkVersion 36 gate は見つからず、`prevent_intent_redirect` aconfig と creator token / compat change で制御される。影響は nested Intent launch pattern を持つ場合に発生する。 |
| targetSdkVersion 36 以上が必要か | No | `ActivityStarter` / `ActivityManagerService` / `Intent` の確認範囲では targetSdkVersion 36 gate は見つからない。 |
| 追加の実行時条件があるか | Yes | 外部入力由来の top-level Intent から extras / ClipData 内の nested Intent を取得し、その nested Intent を activity launch するような Intent redirection pattern が必要。 |
| Compat Change ID が関係するか | Yes | AOSP `ActivityStarter` に `ENABLE_PREVENT_INTENT_REDIRECT_TAKE_ACTION = 29623414` があり、`@ChangeId` / `@Overridable` と `CompatChanges.isChangeEnabled(..., callingUid)` を確認した。公式 compat framework 一覧では該当 ID を確認できなかった。 |

### 調査日（Investigation Date）

2026-07-06

### 信頼度（Confidence）

- Medium

理由:
- 公式文書は all apps 変更として明記している。
- AOSP では `Intent#removeLaunchSecurityProtection()`、nested Intent key collection、creator token、Activity launch 時の token / permission / URI grant 再検証、blocking / exception path を確認した。
- Android 15 tag にも `prevent_intent_redirect` flagged implementation と `removeLaunchSecurityProtection()` の痕跡が存在するため、Android 15 baseline は「前段実装あり」として扱う。Android 16 では公式 Behavior Change として公開され、AOSP diff では server-side collection、ClipData token verification、stats logging が強化されている。
- `startService()` / `bindService()` / broadcast では `Intent.prepareToLeaveProcess()` 呼び出しは確認したが、Activity launch と同じ creator-token enforcement path は確認できなかった。このため activity launch 以外は evidence gap とする。

### 適用条件分類（Applicability Classification）

適用される条件（Applies when）:
- [x] OS update / all apps on Android 16 regardless of targetSdkVersion
- [ ] targetSdkVersion >= 36 on Android 16+
- [ ] targetSdkVersion >= 36, with additional runtime conditions
- [ ] Mainline / Google Play system update dependent
- [ ] API addition only, not a behavior change
- [ ] Unknown / needs more evidence

必要な実行時条件（Required runtime conditions）:
- Android version: Android 16
- targetSdkVersion: 条件なし。targetSdkVersion 35 / 36 の両方が影響対象になり得る。
- Device/form factor: 条件なし。
- Permission/API/component condition: nested / embedded / forwarded Intent を activity launch すること。特に extras / Parcelable array / Parcelable list / ClipData 内の Intent。
- App state/process condition: untrusted caller から受けた Intent を別 component launch に使う flow。

Compat framework:
- Change ID: `29623414`
- Change name: `ENABLE_PREVENT_INTENT_REDIRECT_TAKE_ACTION`
- Default state: AOSP annotation は `@ChangeId` / `@Overridable`。`@Disabled` / `@EnabledAfter` は確認できないため、source 上は targetSdkVersion gate ではない。ただし公式 compat framework 一覧では未確認。
- Toggleable for testing: `@Overridable` のため platform compat override 対象になり得るが、公式 testing command は確認できない。

分類信頼度（Classification confidence）:
- Medium

分類根拠（Classification evidence）:
- Official documentation page: `behavior-changes-all` の Security section。
- Original applicability statement: Android 16 all apps ページは、Android 16 上で実行される全アプリに適用される変更として説明している。
- AOSP targetSdk gate: 見つからない。
- Compat framework entry: AOSP `@ChangeId` は確認したが、公式 compat framework 一覧には見つからない。

---

# エグゼクティブサマリー（Executive Summary）

Android 16 では、外部アプリが制御できる top-level Intent の extras / ClipData に含まれる nested Intent を、脆弱なアプリが自分の context で launch する Intent redirection attack に対して、platform 側の hardening が既定で入る。

主な実装は Activity launch path にあり、nested Intent の creator token を使って「誰がその nested Intent を作ったか」を追跡し、token がない / 不正な場合、または creator が launch 権限や URI grant 権限を満たさない場合に、log / stats / abort / SecurityException の対象になる。

この変更は targetSdkVersion 36 化だけの影響ではなく、Android 16 OS 上で nested Intent forwarding を行うアプリに影響し得る。一方、`Intent#removeLaunchSecurityProtection()` による opt-out は security protection を弱めるため、通常は nested Intent の allowlist validation / IntentSanitizer 等で安全に処理することが推奨される。

---

# 公式ドキュメント確認（Original Documentation）

## 原文（Statement）

公式文書は以下を説明している。

- Android 16 は一般的な Intent redirection attack に対して既定の security hardening を提供する。
- 多くの通常の Intent 利用では互換性問題は起きない見込みであり、開発中に breakage の metrics を監視していた。
- Intent redirection は、攻撃者が top-level Intent の内容を部分的または完全に制御し、被害アプリが extras 内の untrusted sub-level Intent を launch する場合に起きる。
- これにより、被害アプリの context で private component が起動されたり、privileged action が実行されたり、URI access を得たりする可能性がある。
- Android 16 は launch security protections から opt out する新 API を導入する。
- Android 16 SDK / API 36 以上で compile するアプリは `Intent#removeLaunchSecurityProtection()` を直接使える。
- Android 15 SDK / API 35 以下で compile するアプリは reflection でアクセスできるが、推奨されない。

## 解釈（Interpretation）

この Behavior Change は、app が外部由来の nested Intent をそのまま launch する unsafe forwarding pattern を platform 側で検知 / 抑止するもの。`targetSdkVersion` ではなく Android 16 OS の実装差分として扱う。

ただし、opt-out API をソースコードから直接参照できるかは `compileSdkVersion 36` の API availability の話であり、`targetSdkVersion 36` の runtime gate とは別である。

---

# 変更内容（What Changed）

## 変更点

- Android 16 の Activity launch path は nested Intent の creator token を検証し、missing / invalid token を `EXTENDED_FLAG_MISSING_CREATOR_OR_INVALID_TOKEN` として扱う。
- creator token が有効な nested Intent では、launch caller だけでなく nested Intent creator の UID / package も考慮して start permission / IntentFirewall / PermissionPolicy / URI grant を再検証する。
- Android 16 diff では `INTENT_REDIRECT_BLOCKED` stats logging、error code 化、server-side nested key collection、ClipData token verification が強化されている。
- `Intent#removeLaunchSecurityProtection()` は `EXTENDED_FLAG_MISSING_CREATOR_OR_INVALID_TOKEN` を消し、creator token info を削除する opt-out API として公開されている。

## 適用条件（Applicability）

### OS アップデート時の挙動（OS Update Behavior）

- Android 16 にアップデートしただけで適用されるか: Yes / Conditional。
- targetSdkVersion に依存しない根拠: AOSP の `ActivityStarter` / `ActivityManagerService` / `Intent` で targetSdkVersion 36 gate は見つからない。公式ページも all apps ページ。
- Android 15 以前での挙動: `android-15.0.0_r36` にも flagged implementation は存在する。ただし公式 Android 16 Behavior Change としての説明、Android 16 diff の enforcement 強化、API 36 compile guidance を踏まえると、顧客説明では Android 16 OS 上の既定 hardening として扱う。Android 15 実機 / flag state は別途検証が必要。

### targetSdkVersion 36 以上での挙動（targetSdkVersion 36 Behavior）

- targetSdkVersion 36 以上で適用されるか: targetSdkVersion 36 は必要条件ではない。
- Android 16 以外で targetSdkVersion 36 にした場合の挙動: AOSP evidence だけでは Android 15 device 上の targetSdkVersion 36 が同じ enforcement を受けるとは結論できない。
- opt-out / temporary override の有無: `Intent#removeLaunchSecurityProtection()`。compileSdkVersion 36 以上なら直接 API、compileSdkVersion 35 以下は reflection fallback と公式文書にあるが非推奨。

### その他の条件（Other Conditions）

- device/form factor: 条件なし。
- permission: URI grant / component permission / exported state / IntentFirewall / PermissionPolicy と相互作用する。
- API usage: `startActivity()` / `startActivityForResult()` / `startActivities()` 等の Activity launch path で確認。
- manifest attribute: private / non-exported component、permission-protected component、exported component の違いが影響する。
- component boundary: untrusted source から nested Intent を受け取り、別 component を launch する場合。

---

# AOSP 調査（AOSP Investigation）

## 関連ファイル（Related Files）

- `frameworks-base/core/java/android/content/Intent.java`
- `frameworks-base/core/java/android/content/ClipData.java`
- `frameworks-base/core/java/android/os/Bundle.java`
- `frameworks-base/core/java/android/app/ContextImpl.java`
- `frameworks-base/core/java/android/app/Instrumentation.java`
- `frameworks-base/core/java/android/app/IntentSender.java`
- `frameworks-base/services/core/java/com/android/server/am/ActivityManagerService.java`
- `frameworks-base/services/core/java/com/android/server/wm/ActivityStarter.java`
- `frameworks-base/services/core/java/com/android/server/wm/ActivityStartController.java`
- `frameworks-base/core/java/android/security/responsible_apis_flags.aconfig`
- `frameworks-base/core/api/current.txt`
- `frameworks-base/core/tests/coretests/src/android/content/IntentTest.java`
- `frameworks-base/services/tests/mockingservicestests/src/com/android/server/am/ActivityManagerServiceTest.java`

## 確認したソース文脈（Source Context Reviewed）

| ファイル / シンボル（File / symbol） | Android 15 の基準挙動（baseline） | Android 16 の挙動 | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| `Intent#collectExtraIntentKeys()` | flagged implementation は存在するが、client-side collection が中心。 | `collectExtraIntentKeys(boolean forceUnparcel)` が追加され、system server 側で fallback collection できる。parceled value を不用意に unparcel しない分岐も追加。 | nested Intent の key を収集し、creator token を付与する入口。 |
| `Intent#checkCreatorToken()` / `maybeMarkAsMissingCreatorToken()` | extras の token verification は存在。 | ClipData の token verification も追加。foreign Intent かつ trusted creator token がない場合に missing / invalid flag を付ける。 | target app process で nested Intent を取り出す時に、不正 token を flag 化する経路。 |
| `Intent#removeLaunchSecurityProtection()` | flagged public API surface に存在。 | 同じく `@FlaggedApi("android.security.prevent_intent_redirect")`。missing / invalid flag を消し、creator token info を削除する。 | 公式 opt-out API の実体。 |
| `ContextImpl#startActivityAsUser()` / `Instrumentation#execStartActivity()` | Activity launch 前に `collectExtraIntentKeys()` / `prepareToLeaveProcess()` を呼ぶ。 | 同様の path により nested Intent keys が収集される。 | app API から ActivityTaskManager へ行く前の preparation path。 |
| `ActivityManagerService#addCreatorToken()` | nested Intent に creator token を付与。未収集時は `intent.collectExtraIntentKeys()`。 | 未収集時は `EXTRA_INTENT_KEYS_COLLECTED_ON_SERVER` を stats log し、`intent.collectExtraIntentKeys(true)` により server-side collection。 | top-level Intent の nested Intent に creator UID/package を紐づける server-side path。 |
| `ActivityStarter#executeRequest()` | missing token / creator URI grant / permission check failure で log / exception / abort path が存在。 | `INTENT_REDIRECT_BLOCKED` stats logging と structured error code が追加。creator の start permission / IntentFirewall / PermissionPolicy / URI grant を再検証。 | Activity launch の実 enforcement path。 |
| `ActivityStartController#startActivities()` | creator token を見て creator UID を考慮する。 | 同様。 | 複数 Activity launch path でも creator token を見る根拠。 |
| `ContextImpl#startServiceCommon()` / bind service | `prepareToLeaveProcess()` は呼ぶ。 | 同様。ActivityStarter 相当の creator-token enforcement は確認できない。 | request には service / bind / broadcast も含まれるが、実 enforcement は activity path と分ける必要があるため。 |

必須記入項目（Required context）:
- Entry point / caller: `ContextImpl.startActivity*()` / `Instrumentation.execStartActivity()` -> `ActivityTaskManagerService` -> `ActivityStarter`。
- Relevant class or service responsibility: `Intent` は nested Intent keys / creator token metadata を保持し、`ActivityManagerService` は creator token を付与し、`ActivityStarter` は launch 時に権限・URI grant を再検証する。
- Runtime path from app API / system event to changed code: app が top-level Intent を launch 前に `prepareToLeaveProcess()` し、nested Intent keys が収集され、system server で creator token が付与され、target app が nested Intent を取り出して再 launch する時に token / grant check が走る。
- Why unrelated code paths were excluded: call redirection / profile redirection / Ravenwood redirection は別機能。service / broadcast path は `prepareToLeaveProcess()` 以外の ActivityStarter 相当 enforcement が見つからないため、今回の confirmed behavior からは分けた。

## 差分解釈（Diff Interpretation）

| 確認した差分（Observed diff） | 解釈（Interpretation） | Behavior Change との関係 | 信頼度（Confidence） |
| --- | --- | --- | --- |
| `Intent#collectExtraIntentKeys(boolean forceUnparcel)` 追加 | nested Intent key collection を system server fallback でも可能にする changed behavior。 | default hardening の取りこぼしを減らす。 | High |
| `ClipData.Item#getIntent()` が token verification enabled 時のみ `maybeMarkAsMissingCreatorToken()` を呼ぶよう変更 | ClipData 内 nested Intent の token verification を明示的に制御する changed condition。 | ClipData 経由の nested Intent も hardening 対象に含める。 | High |
| `ActivityManagerService#addCreatorToken()` が未収集時に stats logging し `collectExtraIntentKeys(true)` を呼ぶ | server-side safety net の追加。 | client-side collection 不備を補う。 | High |
| `ActivityStarter` が error code と `INTENT_REDIRECT_BLOCKED` stats logging を追加 | blocked / exception / abort の observability 強化。 | 公式文書の metrics / hardening と整合する。 | Medium-High |
| `removeLaunchSecurityProtection()` が missing flag と creator token info を削除 | opt-out API。 | 公式 opt-out guidance の実装根拠。 | High |
| targetSdkVersion 36 gate が見つからない | OS update / all apps 変更として解釈。 | classification を `OS_UPDATE_ALL_APPS` とする根拠。 | Medium-High |
| Android 15 tag にも flagged implementation が存在 | Android 15 baseline は単純な「完全に存在しない」ではない。 | Android 16 公式挙動としての既定適用と、Android 15 前段実装を混同しない。 | Medium |

必須分類（Required interpretation）:
- Added behavior: Android 16 diff で server-side nested key collection、ClipData token verification、stats logging / error code 化が追加。
- Removed behavior: 今回の主機能に関する明確な removal は確認していない。
- Changed condition / gate: `collectExtraIntentKeys` に `forceUnparcel` 条件、ClipData token verification enabled 条件が追加。
- Changed default: 公式上は Android 16 で by-default hardening。AOSP tag diff だけでは flag default の Android 15/16差は直接確認できない。
- No behavior change found: `removeLaunchSecurityProtection()` method 自体は `android-15.0.0_r36` `current.txt` にも flagged API として見えるため、API symbol の単純追加だけを Android 16 diff としては扱わない。

## 事実（Facts）

- 公式文書はこの項目を Android 16 all apps / Security として掲載している。
- `Intent#removeLaunchSecurityProtection()` は `@FlaggedApi("android.security.prevent_intent_redirect")` で public API surface に存在する。
- `Intent#removeLaunchSecurityProtection()` は `EXTENDED_FLAG_MISSING_CREATOR_OR_INVALID_TOKEN` を clear し、`removeCreatorTokenInfo()` を呼ぶ。
- `Intent#prepareToLeaveProcess(..., isTopLevel=true)` は top-level Intent に対して `collectExtraIntentKeys()` を呼ぶ。
- `ActivityManagerService.IntentCreatorToken` は creator UID / package と Intent key fields を保持する Binder token。
- `ActivityStarter` は missing / invalid token、creator URI grant failure、creator start permission failure、IntentFirewall failure、PermissionPolicy failure を intent redirect error として扱う。
- `ActivityStarter` の action-taking path は `ENABLE_PREVENT_INTENT_REDIRECT_TAKE_ACTION = 29623414` と `preventIntentRedirectAbortOrThrowException()` に依存する。
- `ActivityStarter` に targetSdkVersion 36 gate は見つからない。
- `IntentTest` / `ActivityManagerServiceTest` は nested Intent key collection、creator token 付与、foreign Intent の missing token flag を検証している。

## 観察（Observations）

- 公式文書の「Android 16 introduces a new API」は SDK availability / documentation の観点で妥当だが、AOSP `android-15.0.0_r36` tag には flagged API symbol と関連実装の一部が存在する。
- Android 16 diff は「完全新規実装」よりも「既存 flagged hardening の強化・公開・既定化」に近い。
- `startService()` / `bindService()` / broadcast は `Intent.prepareToLeaveProcess()` により nested key collection には関与し得るが、確認できた block / throw / URI grant creator check は Activity launch path である。
- `removeLaunchSecurityProtection()` は app-wide opt-out ではなく、その Intent object の creator-token protection を削除する局所的 opt-out である。

## 仮説（Hypotheses）

- Android 15 tag に含まれる flagged implementation は、Android 16 公開前の feature flag / staged rollout / metrics collection 用の前段実装だった可能性がある。
- 公式文書の「metrics」は、AOSP の `INTENT_REDIRECT_BLOCKED` / `INTENT_CREATOR_TOKEN_ADDED` / `EXTRA_INTENT_KEYS_COLLECTED_ON_SERVER` stats logging と関連する可能性がある。
- service / broadcast については nested Intent preparation は共有されるが、ActivityStarter と同等の redirection block は activity-specific である可能性が高い。

## 結論（Conclusions）

- 顧客向け分類は `OS_UPDATE_ALL_APPS`。Android 16 OS 上で nested Intent forwarding pattern がある場合、targetSdkVersion 35 のままでも影響し得る。
- targetSdkVersion 36 は適用条件ではない。compileSdkVersion 36 は `removeLaunchSecurityProtection()` を直接呼べるかどうかの条件である。
- 影響の中心は Activity launch。service / bind / broadcast については同じ enforcement を確認できないため、実機・CTS で追加検証が必要。
- 推奨対応は opt-out ではなく、nested Intent を launch する前の allowlist validation / IntentSanitizer / component・package・action・data・flags・ClipData・URI grant の検証である。

## 適用ゲート根拠（Applicability Gate Evidence）

- targetSdkVersion gate: 見つからない。
- CompatChanges.isChangeEnabled / ChangeId: `ActivityStarter` の `ENABLE_PREVENT_INTENT_REDIRECT_TAKE_ACTION = 29623414`。
- @EnabledAfter / @EnabledSince / default state: 見つからない。`@ChangeId` / `@Overridable` のみ確認。
- Build.VERSION / SDK_INT gate: enforcement path には見つからない。
- DeviceConfig / resources config: `android.security.Flags` aconfig flags を確認。`prevent_intent_redirect` は `is_fixed_read_only: true` / `is_exported: true`。
- Permission/AppOps gate: nested Intent creator の launch permission / URI permission / IntentFirewall / PermissionPolicy が再検証される。
- Manifest/property gate: opt-out manifest property は確認していない。API opt-out は `Intent#removeLaunchSecurityProtection()`。
- No gate found: targetSdkVersion gate は見つからない。
- Gate conclusion: Android 16 OS 上で、nested Intent activity launch pattern を持つ全アプリに影響し得る。

---

# 影響分析（Impact Analysis）

## 影響を受けるアプリ（Affected Apps）

- deep link router / navigation router を持つアプリ
- OAuth / SSO / authentication redirect handler を持つアプリ
- notification click / workflow router を持つアプリ
- share target / file open / document handoff を扱うアプリ
- nested Intent extras を受け取って launch するアプリ
- external app から受け取った Intent extras を信頼しているアプリ
- private / non-exported component を内部 Intent で起動するアプリ
- URI permission grant / ClipData を伴う Intent forwarding を行うアプリ
- plugin framework / mini app / SDK dispatcher / cross-app workflow を持つアプリ
- WebView / browser / custom tabs / URL router と Intent launch を連携するアプリ
- SDK / library が nested Intent forwarding を内部利用するアプリ

## 影響を受けない / 低影響のアプリ（Non-Affected Apps）

- nested / forwarded Intent を launch しないアプリ
- 外部入力に由来しない自前生成の explicit Intent だけを launch するアプリ
- nested Intent を launch 前に allowlist validation しているアプリ
- component / package / action / data / categories / flags / ClipData / URI grants を検証・削除しているアプリ
- `IntentSanitizer` または同等の sanitizer を使うアプリ
- opt-out を使わず Android 16 hardening 下で動作するアプリ

---

# 顧客影響（Customer Impact）

## Android 16 へ OS アップデートしただけの影響

Android 16 端末上では、targetSdkVersion 35 のままでも unsafe nested Intent forwarding が Activity launch 時に block / exception / abort / log の対象になる可能性がある。影響は Intent redirection pattern を持つ機能に限定される。

## targetSdkVersion 36 化した時の影響

この項目自体は targetSdkVersion 36 化で有効になる変更ではない。targetSdkVersion 36 への移行影響として説明しない。

## compileSdkVersion 36 化した時の影響

compileSdkVersion 36 以上では `Intent#removeLaunchSecurityProtection()` を直接参照できる。ただしこれは opt-out API の利用可否であり、runtime enforcement の適用条件ではない。

## opt-out risk

`removeLaunchSecurityProtection()` は nested Intent の launch security protection を外す。互換性回避のために必要な場合でも、first-party / allowlisted flow に限定し、security review と regression test を必須にすべきである。

---

# 期待挙動マトリクス（Expected Behavior Matrix）

## OS / targetSdkVersion matrix

| シナリオ | 期待挙動 | 根拠 / 備考 |
| --- | --- | --- |
| Android 16 / targetSdkVersion 35 | nested Intent activity launch hardening の対象になり得る | targetSdkVersion gate は見つからない |
| Android 16 / targetSdkVersion 36 | targetSdkVersion 35 と同様に対象になり得る | targetSdkVersion 36 固有ではない |
| Android 15 / targetSdkVersion 36 | 要検証 | Android 15 tag に flagged implementation はあるが、公式 Android 16 behavior としての既定適用は別扱い |

## Detailed matrix

| シナリオ | 期待挙動 / 影響 |
| --- | --- |
| Android 16 / targetSdkVersion 35 / normal Intent launch | 通常は影響なし |
| Android 16 / targetSdkVersion 36 / normal Intent launch | 通常は影響なし |
| Android 16 / targetSdkVersion 35 / nested Intent from untrusted extras | hardening 対象になり得る |
| Android 16 / targetSdkVersion 36 / nested Intent from untrusted extras | hardening 対象になり得る |
| Android 16 / attacker-controlled top-level Intent | nested Intent が含まれる場合に risk |
| Android 16 / sub-level Intent in extras | creator token / missing token check の対象 |
| Android 16 / explicit private component launch via nested Intent | creator 側の launch 権限が再検証され、block / exception 対象になり得る |
| Android 16 / exported component launch via nested Intent | 通常は launch 可能だが creator / permission / firewall policy に依存 |
| Android 16 / URI grant forwarding via nested Intent | creator UID でも URI grant が再検証され、失敗時は exception 対象になり得る |
| Android 16 / ClipData forwarding via nested Intent | ClipData 内 Intent も token verification 対象 |
| Android 16 / startActivity with nested Intent | confirmed enforcement path |
| Android 16 / startService with nested Intent | `prepareToLeaveProcess()` は確認。ActivityStarter 相当 enforcement は未確認 |
| Android 16 / bindService with nested Intent | `prepareToLeaveProcess()` は確認。ActivityStarter 相当 enforcement は未確認 |
| Android 16 / sendBroadcast with nested Intent | 今回の AOSP 確認範囲では未確定 |
| Android 16 / removeLaunchSecurityProtection() not called | default hardening 維持 |
| Android 16 / removeLaunchSecurityProtection() called | missing / invalid token flag と creator token info が削除され、protection が弱まる |
| Android 16 / compileSdkVersion 36 / direct removeLaunchSecurityProtection() | 直接 API 呼び出し可能 |
| Android 16 / compileSdkVersion 35 or lower / reflection opt-out | 公式は技術的に可能とするが非推奨 |
| Android 16 / app validates nested Intent before launch | 推奨対応。compat risk と security risk を下げる |
| Android 16 / app does not validate nested Intent before launch | block / exception / security risk の両方がある |
| Android 16 / IntentSanitizer or equivalent allowlist used | 推奨 |
| Android 16 / legitimate flow requiring opt-out | first-party / allowlisted flow に限定して要 review |
| Android 16 / malicious flow blocked by default hardening | 期待される security improvement |
| Android 15 / targetSdkVersion 36 / same app behavior if technically comparable | 要実機検証 |
| app migrates away from unsafe intent forwarding | 推奨 |
| app opts out without validation | 非推奨。脆弱性 risk が残る |

---

# 推奨対応候補（Recommended Action Candidates）

- 外部入力由来の `Intent` extras / ClipData から `Intent` を取り出して launch している箇所を棚卸しする。
- nested Intent を launch する前に component / package / action / data scheme / host / categories / flags / ClipData / URI grants を allowlist validation する。
- private / non-exported component を nested Intent 経由で起動する設計を見直す。
- URI grant flags は必要最小限にし、untrusted nested Intent からの grant forwarding を避ける。
- `IntentSanitizer` または同等の sanitizer を導入する。
- `removeLaunchSecurityProtection()` は互換性上どうしても必要な first-party flow のみに限定し、security review とテストを行う。
- compileSdkVersion 35 以下で reflection opt-out を使う設計は避け、可能なら compileSdkVersion 36 へ更新する。

---

# テスト観点（Test Matrix / QA）

- Android 15 端末上の targetSdkVersion 35
- Android 16 端末上の targetSdkVersion 35
- Android 16 端末上の targetSdkVersion 36
- Android 15 端末上の targetSdkVersion 36 が検証可能な場合の比較
- compileSdkVersion 36
- compileSdkVersion 35 or lower
- normal explicit / implicit Intent launch
- attacker-controlled top-level Intent
- nested / sub-level Intent stored in extras
- nested Intent to exported component
- nested Intent to non-exported / private component
- nested Intent with action / data / categories / package / component variations
- nested Intent with URI grants
- nested Intent with ClipData
- startActivity / startActivityForResult
- startService / bindService
- sendBroadcast / ordered broadcast, if relevant
- removeLaunchSecurityProtection() not called
- removeLaunchSecurityProtection() called directly
- removeLaunchSecurityProtection() accessed by reflection
- IntentSanitizer / allowlist validation
- malicious input blocked / sanitized / logged
- legitimate flow still works
- exception type / logcat message / stack trace / user-visible failure
- security regression test for intent redirection
- URI access leakage test
- private component launch prevention test
- opt-out review / threat model / user data exposure review
- graceful fallback / error handling

---

# Evidence gaps / Follow-up

- 公式 compat framework changes page では `29623414` を確認できなかった。AOSP source 上は `@ChangeId` / `@Overridable`。
- Android 15 tag に flagged implementation が存在するため、Android 15 実機上の default flag state / SDK exposure / behavior は端末 build で別途確認が必要。
- service / bind / broadcast path については request の対象に含まれているが、ActivityStarter と同じ enforcement path は未確認。実機・CTS・追加 AOSP 調査が必要。
- `IntentSanitizer` は app-side mitigation guidance として有用だが、この platform hardening の enforcement 実装そのものではない。

---

# 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- Critical / High / Medium / Low

判断（Decision）:
- Explain / Monitor / Ignore / Further investigation required

顧客説明優先度（Customer communication priority）:
- TBD by human

リリース判定（Release readiness decision）:
- TBD by human
