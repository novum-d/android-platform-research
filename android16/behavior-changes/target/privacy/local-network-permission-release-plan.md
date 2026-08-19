# Local Network Permission - Release plan

## 調査メタデータ

- Android version: Android 16
- Version directory: `android16`
- From tag: `android-15.0.0_r36`
- To tag: `android-16.0.0_r4`
- Previous targetSdkVersion: 35
- Target targetSdkVersion: 36
- Behavior Change section: Local Network Permission / Release plan
- Official documentation URL: https://developer.android.com/about/versions/16/behavior-changes-16#release-plan
- Official documentation category: Privacy
- Report output file: `android16/behavior-changes/target/privacy/local-network-permission-release-plan.md`
- Summary output file: `android16/summaries/target/privacy/local-network-permission-release-plan-summary.md`
- Applicability classification: `OPT_IN_ONLY`
- Confidence: High


Classification note: Release plan セクションは、Android 16 時点の default-on behavior ではなく、25Q2 opt-in phase と later Android release enforcement への移行計画を説明している。AOSP `android-16.0.0_r4` では `RESTRICT_LOCAL_NETWORK` は `@EnabledAfter(targetSdkVersion = 36)` であり、targetSdkVersion 36 では default-enabled ではない。現在の developer testing は compat flag force-enable に依存するため、`OPT_IN_ONLY` を primary label とし、opt-in / future enforcement 条件を追加条件として記録する。

## Official Documentation Review

2026-07-03 に公式ドキュメントの `#release-plan` 周辺を再確認した。対象ページは `Last updated 2026-07-01 UTC` と表示されていた。

確認した公式記述:

- Local Network Protections project は、local network access を new runtime permission behind に置くことで user privacy を保護する。
- 変更は 25Q2 と 26Q2 の 2 release に分けて deploy される。
- 25Q2 guidance に従い feedback を共有することが重要である。理由は、protections が later Android release で enforced されるため。
- implicit local network access に依存する scenarios は guidance に沿って更新が必要になる。
- developers は new permission の user rejection / revocation に備える必要がある。
- current stage では LNP は opt-in feature であり、opt in した app だけが影響を受ける。
- Developer Guidance では、25Q2 Beta 3 以降 build、`adb shell am compat enable RESTRICT_LOCAL_NETWORK <package_name>`、device reboot により opt-in する。
- current opt-in phase で access restore するには `NEARBY_WIFI_DEVICES` を宣言し grant する。
- future Android release では Nearby devices permission group の new permission で guard される。

依頼文の Original statements / Applicability details と公式本文に実質差分はない。ただし、公式文書は Android 16 targeting apps ページに掲載されている一方で、Release plan 本文は current stage を opt-in と明記しているため、targetSdkVersion 36 化だけの影響として扱わない。

## AOSP Evidence Scope

Primary evidence:

- `platform/frameworks/base`
  - `android-15.0.0_r36`
  - `android-16.0.0_r4`
- `platform/packages/modules/Connectivity`
  - `android-15.0.0_r36`
  - `android-16.0.0_r4`

Checkout hygiene:

- `frameworks-base` checkout は clean であることを確認した。
- `frameworks-base` に `android-15.0.0_r36` / `android-16.0.0_r4` tag が存在することを確認した。
- `packages/modules/Connectivity` checkout は clean であることを確認した。
- `packages/modules/Connectivity` に `android-15.0.0_r36` / `android-16.0.0_r4` tag が存在することを確認した。
- `frameworks-base` working tree と tag 内容に差がある可能性を避けるため、`ACCESS_LOCAL_NETWORK` evidence は `git show android-16.0.0_r4:<path>` で tag から直接確認した。

## Original Statements Verification

| Original statement | Verification |
|---|---|
| "This change will be deployed between two releases, 25Q2 and 26Q2 respectively." | 公式文書で確認。AOSP では 25Q2 gate に対応する `BPFLOADER_MAINLINE_25Q2_VERSION` / `BpfNetMaps.isAtLeast25Q2()` / `SdkUtil.isAtLeast25Q2()` が確認できる。26Q2 enforcement の完成形は Android 16 r4 では未確定。 |
| "developers follow this guidance for 25Q2 and share feedback..." | 公式文書で確認。AOSP では `RESTRICT_LOCAL_NETWORK` compat change と BPF infrastructure が 25Q2 opt-in testing を可能にする根拠になる。feedback channel 自体は AOSP code path では確認対象外。 |
| "protections will be enforced at a later Android release" | 公式文書で確認。AOSP `RESTRICT_LOCAL_NETWORK` は `@EnabledAfter(targetSdkVersion = 36)` かつ TODO 付きで、Android 16 target 36 ではなく future target / later release を示す evidence と整合する。 |
| "update scenarios which depend on implicit local network access" | 公式文書で確認。AOSP BPF path は app UID の local network packets を drop できるため、implicit LAN access は将来 permission guarded になる前提で棚卸しが必要。 |
| "prepare for user rejection and revocation of the new permission" | 公式文書で確認。Android 16 r4 には `ACCESS_LOCAL_NETWORK` dangerous permission / AppOp が追加されているが、current opt-in restore は `NEARBY_WIFI_DEVICES`。future permission UX は未確定。 |
| "Local Network Protections ... new runtime permission" | 公式文書で確認。Android 16 r4 `frameworks-base` tag には flagged `ACCESS_LOCAL_NETWORK` dangerous permission と AppOp がある。 |
| "At the current stage, LNP is an opt-in feature..." | 公式文書で確認。AOSP `PermissionMonitor` は `CompatChanges.isChangeEnabled(RESTRICT_LOCAL_NETWORK, uid)` を current enforcement gate として使う。 |

## Facts

### `RESTRICT_LOCAL_NETWORK` は Android 16 r4 に存在するが targetSdkVersion 36 では default-enabled ではない

Reviewed source:

- `packages/modules/Connectivity/framework/src/android/net/connectivity/ConnectivityCompatChanges.java`
- Symbol: `RESTRICT_LOCAL_NETWORK = 365139289L`

Android 16 `android-16.0.0_r4` では次が定義されている。

- `@ChangeId`
- `@EnabledAfter(targetSdkVersion = 36)`
- `public static final long RESTRICT_LOCAL_NETWORK = 365139289L`
- comment: apps targeting a release after V will require permissions to access the local network
- TODO: target SDK version が finalized されたら更新する

Android 15 `android-15.0.0_r36` では `RESTRICT_LOCAL_NETWORK` は確認できない。

AOSP source context:

- Entry point / caller: `PermissionMonitor.Dependencies.shouldEnforceLocalNetRestrictions(uid)`
- Why relevant: current opt-in と future default enforcement の gate になる compat change。
- Baseline Android behavior: Android 15 にはこの compat change がない。
- Target Android behavior: Android 16 r4 には compat change があるが、targetSdkVersion 36 では default-enabled ではない。
- Diff kind: added behavior / future target gate / opt-in capable compat change。
- Applicability support: Android 16 / targetSdkVersion 36 の自動適用ではなく、current phase は force-enable opt-in。future release では target 36 より後の target SDK gate になる可能性がある。

### Current opt-in gate は 25Q2 build 条件と compat flag 条件の組み合わせ

Reviewed source:

- `packages/modules/Connectivity/service/src/com/android/server/connectivity/PermissionMonitor.java`
- Method: `Dependencies.shouldEnforceLocalNetRestrictions(int uid)`

`shouldEnforceLocalNetRestrictions(uid)` は次の両方を要求する。

- `BpfNetMaps.isAtLeast25Q2()`
- `CompatChanges.isChangeEnabled(RESTRICT_LOCAL_NETWORK, uid)`

このため、Android 16 r4 の current testing behavior は、OS が 25Q2 相当であることに加え、package に対して `RESTRICT_LOCAL_NETWORK` が enabled であることを必要とする。

Reviewed source:

- `packages/modules/Connectivity/staticlibs/framework/com/android/net/module/util/SdkUtil.java`
- Method: `isAtLeast25Q2()`

`isAtLeast25Q2()` は `SDK_INT >= 36` または `SDK_INT == 35 && CODENAME == "Baklava"` を true とする。公式文書の 25Q2 Beta 3 以降 build 条件と整合する。

### Current opt-in restore access は `NEARBY_WIFI_DEVICES` grant に依存する

Reviewed source:

- `packages/modules/Connectivity/service/src/com/android/server/connectivity/PermissionMonitor.java`
- Method: `setLocalNetworkPermissions(int uid, String packageName)`

`setLocalNetworkPermissions` は、local network restriction 対象 UID について `PermissionManager.checkPermissionForPreflight(NEARBY_WIFI_DEVICES, AttributionSource)` を確認する。

- `PERMISSION_GRANTED`: `removeUidFromLocalNetBlockMap(uid)`
- not granted: `addUidToLocalNetBlockMap(uid)`
- SDK sandbox UID は runtime permission を持てないため block map に追加される

Reviewed source:

- `frameworks-base/services/core/java/com/android/server/media/MediaRouter2ServiceImpl.java`
- Method: `permissionAllowedForAppCompat(String permission)`

`android.permission.ACCESS_LOCAL_NETWORK` について、Change ID `365139289L` が disabled の UID は permission satisfied と扱う。Change ID が enabled の UID では `Manifest.permission.NEARBY_WIFI_DEVICES` grant を確認する。この method には "temporary workaround" と next release で remove 希望の TODO がある。

Interpretation:

- Android 16 current opt-in phase では、future permission ではなく `NEARBY_WIFI_DEVICES` が restore access に使われる。
- Release plan の "new permission" は future enforcement 用の計画として扱う必要がある。

### Android 16 r4 には future `ACCESS_LOCAL_NETWORK` permission / AppOp の基盤がある

Reviewed source:

- `frameworks-base/core/res/AndroidManifest.xml` at `android-16.0.0_r4`
- `frameworks-base/core/api/current.txt` at `android-16.0.0_r4`
- `frameworks-base/core/java/android/permission/flags.aconfig` at `android-16.0.0_r4`
- `frameworks-base/core/java/android/app/AppOpsManager.java` at `android-16.0.0_r4`

Android 16 r4 には `android.permission.ACCESS_LOCAL_NETWORK` が追加されている。

- `@FlaggedApi(android.permission.flags.Flags.FLAG_ACCESS_LOCAL_NETWORK_PERMISSION_ENABLED)`
- `android:permissionGroup="android.permission-group.UNDEFINED"`
- `android:protectionLevel="dangerous"`
- `android:featureFlag="android.permission.flags.access_local_network_permission_enabled"`

`access_local_network_permission_enabled` flag の description は、new `ACCESS_LOCAL_NETWORK` runtime permission を enable し、local network protection で `NEARBY_WIFI_DEVICES` を置き換えると説明する。

`AppOpsManager` には `OP_ACCESS_LOCAL_NETWORK` / `OPSTR_ACCESS_LOCAL_NETWORK` と AppOpInfo が追加され、flag enabled 時に `Manifest.permission.ACCESS_LOCAL_NETWORK` に紐づく。

Android 15 r36 では `ACCESS_LOCAL_NETWORK` permission / AppOp は確認できない。

Interpretation:

- Future permission enforcement の platform API surface / AppOp infrastructure は Android 16 r4 に入っている。
- ただし current opt-in phase の app restore path は `NEARBY_WIFI_DEVICES` であり、future permission の UI / final gate は Android 16 r4 だけでは確定しない。

### 25Q2 以降の BPF infrastructure は local network packets を UID 単位で block できる

Reviewed source:

- `packages/modules/Connectivity/bpf/progs/netd.c`
- `packages/modules/Connectivity/service/src/com/android/server/BpfNetMaps.java`

Android 16 r4 `netd.c` では 25Q2 以降用に次の map が追加されている。

- `local_net_access_map`
- `local_net_blocked_uid_map`
- both use `BPFLOADER_MAINLINE_25Q2_VERSION`

`should_block_local_network_packets(...)` は、UID が `local_net_blocked_uid_map` に存在し、remote IP / protocol / port が `local_net_access_map` 上 disallowed なら packet を block する。

`bpf_traffic_account(...)` は `SDK_LEVEL_IS_AT_LEAST(lvl, 25Q2)` かつまだ `DROP` でない packet について `should_block_local_network_packets(...)` を実行し、true なら `DROP` にする。

Android 15 r36 では `local_net_access_map` / `local_net_blocked_uid_map` は確認できない。

Interpretation:

- 25Q2 opt-in phase の technical enforcement は AOSP 上確認できる。
- この path は socket API 名ではなく UID / packet / local address 判定に基づくため、native socket / managed socket / OkHttp / Cronet / WebView など app UID から出る traffic に横断的に影響し得る。

### Local network definition と DNS exception は BPF map population に反映されている

Reviewed source:

- `packages/modules/Connectivity/staticlibs/framework/com/android/net/module/util/NetworkStackConstants.java`
- `packages/modules/Connectivity/service/src/com/android/server/ConnectivityService.java`

`IPV4_LOCAL_PREFIXES` は次を含む。

- `169.254.0.0/16`
- `100.64.0.0/10`
- `10.0.0.0/8`
- `172.16.0.0/12`
- `192.168.0.0/16`

`ConnectivityService` は interface / link property 変化時に local prefixes、multicast / broadcast prefixes を BPF `local_net_access_map` に入れる。DNS server が local prefix 内にある場合、UDP port 53、TCP port 53、TCP port 853 は allow rule として追加される。

Interpretation:

- Release plan の future permission enforcement は、単なる API-level check ではなく local address definition と exception rule を BPF map に反映する設計になっている。
- 公式文書は port 53 exception を述べるが、AOSP r4 では DNS over TLS の TCP 853 も allow rule として追加される。

### NsdManager と app process outside operations は current opt-in phase では限定的に扱う

公式文書は、NsdManager など app process 外で local network operation を実行する API は opt-in phase では影響されないと述べる。

AOSP evidence:

- Current opt-in enforcement は app UID を `local_net_blocked_uid_map` に入れ、BPF packet path で socket UID を見る。
- app process 自身の UID から出る packet は block され得る。
- system service / daemon で処理され、app UID の packet として出ない operation は、current opt-in phase の direct socket block とは別扱いになり得る。

NsdManager の full path / daemon UID / future enforcement path は今回の Release plan 調査では深掘りしていない。Release plan 上は、current opt-in と future enforcement を分けるための caveat として扱う。

## Observations

### Release plan の中心は "Android 16 target 36 で即時 enforcement" ではない

公式文書は Android 16 targeting apps ページにあるが、Release plan 本文は 25Q2 opt-in と later release enforcement を説明している。AOSP r4 の `RESTRICT_LOCAL_NETWORK` は `@EnabledAfter(targetSdkVersion = 36)` であり、targetSdkVersion 36 では default-enabled ではない。

したがって、Android 16 / targetSdkVersion 36 の app が、`RESTRICT_LOCAL_NETWORK` を force-enable していない状態でただちに local network access を失う、とは結論できない。

### 25Q2 は dependency discovery と feedback の期間

25Q2 phase の実装は、developer が compat flag を enable して local network dependency を検出するためのものと読める。`NEARBY_WIFI_DEVICES` で restore できる現在の挙動は、future permission UX の完全な再現ではなく、developer testing 用の transition mechanism である。

### Future enforcement は Android 16 r4 evidence だけでは最終仕様として確定できない

Android 16 r4 には `ACCESS_LOCAL_NETWORK` permission / AppOp / BPF infrastructure が入っている。一方で、公式文書は future Android release の new permission と述べ、AOSP には target SDK TODO が残っている。したがって future enforcement は "確度の高い方向性" として説明できるが、final UX / permission group / targetSdk gate / rollout 条件は future tag で再確認が必要である。

### OS update impact / targetSdk impact / opt-in testing impact / future enforcement impact を分ける必要がある

顧客向けには次を混ぜない。

- Android 16 へ OS update しただけの影響
- targetSdkVersion 36 化しただけの影響
- 25Q2 opt-in testing で `RESTRICT_LOCAL_NETWORK` を enable した時の影響
- future release で runtime permission enforcement が default になった時の影響
- user が future permission を deny / revoke した時の影響

## Hypotheses

- Android 16 r4 の `@EnabledAfter(targetSdkVersion = 36)` は、API 37 以降など later target で default enforcement する計画を示している可能性がある。ただし TODO が残るため final gate は future tag で再確認が必要。
- `ACCESS_LOCAL_NETWORK` は future runtime permission の最終候補であり、current opt-in phase の `NEARBY_WIFI_DEVICES` は temporary substitute と考えられる。
- BPF `local_net_access_map` / `local_net_blocked_uid_map` は future enforcement でも中核 infrastructure として使われる可能性が高い。
- NsdManager など app process 外 operation は current opt-in phase では direct socket block から外れるが、future enforcement では framework API 側に permission checks が追加される可能性がある。

## Applicability Classification

Primary classification: `OPT_IN_ONLY`

理由:

- Release plan は Android 16 current opt-in behavior と future release enforcement をまたぐ計画である。Android 16 current impact は `OPT_IN_ONLY` に分類し、future enforcement は別 release の再確認事項として扱う。
- Android 16 r4 の current developer testing は `RESTRICT_LOCAL_NETWORK` compat flag force-enable に依存する。
- `RESTRICT_LOCAL_NETWORK` は `@EnabledAfter(targetSdkVersion = 36)` で、targetSdkVersion 36 では default-enabled ではない。
- Future permission enforcement は公式文書と AOSP infrastructure で方向性を確認できるが、final release / target gate / permission UX は未確定。

Compat framework:

- Change name: `RESTRICT_LOCAL_NETWORK`
- Change ID: `365139289L`
- AOSP default state in Android 16 r4: `@EnabledAfter(targetSdkVersion = 36)`
- Android 16 / targetSdkVersion 36: default では有効化されない
- Android 16 / targetSdkVersion 35: default では有効化されない
- Force-enable / force-disable: `adb shell am compat enable|disable RESTRICT_LOCAL_NETWORK <package>` による opt-in testing が公式 guidance と一致する。

実質適用条件 current opt-in:

- 25Q2 Beta 3 以降相当の build / `isAtLeast25Q2()`
- package に `RESTRICT_LOCAL_NETWORK` compat flag enabled
- app UID が `NEARBY_WIFI_DEVICES` を grant されていない
- app process から local network address へ packet を送受信する

実質適用条件 future enforcement:

- later Android release で local network protection enforcement が有効
- app が implicit LAN access に依存する
- user が new local network permission を deny / revoke する、または app が permission を request / handle しない
- final permission / targetSdk / rollout gate は future evidence が必要

## Expected Behavior Matrix

| Scenario | Expected behavior |
|---|---|
| Android 16 / targetSdkVersion 35 | default では local network restriction は無効。`RESTRICT_LOCAL_NETWORK` force-enable なら opt-in 影響あり |
| Android 16 / targetSdkVersion 36 | target 35 と同様。r4 evidence では targetSdkVersion 36 だけでは default enforcement されない |
| Android 15 / targetSdkVersion 36 | Android 16 の `RESTRICT_LOCAL_NETWORK` / BPF local network block infrastructure は確認できない |

## Release Plan Matrix

| Scenario | Expected behavior |
|---|---|
| Android 16 / targetSdkVersion 35 / RESTRICT_LOCAL_NETWORK disabled | 従来どおり。implicit LAN access は原則維持 |
| Android 16 / targetSdkVersion 35 / RESTRICT_LOCAL_NETWORK enabled | `NEARBY_WIFI_DEVICES` 未許可なら current opt-in restriction が発生し得る |
| Android 16 / targetSdkVersion 36 / RESTRICT_LOCAL_NETWORK disabled | 従来どおり。target 36 化だけでは current restriction は有効化されない |
| Android 16 / targetSdkVersion 36 / RESTRICT_LOCAL_NETWORK enabled | target 35 と同様に opt-in restriction が発生し得る |
| Android 16 / targetSdkVersion 36 / NEARBY_WIFI_DEVICES declared and granted | current opt-in phase では local network access が restored される |
| Android 16 / targetSdkVersion 36 / NEARBY_WIFI_DEVICES declared but denied | current opt-in phase では app UID の LAN traffic が fail し得る |
| Android 16 / targetSdkVersion 36 / NEARBY_WIFI_DEVICES not declared | grant できず、opt-in testing では LAN traffic が fail し得る |
| Android 16 / current 25Q2 opt-in phase | dependency discovery / feedback / migration preparation の期間 |
| Future enforcement / permission granted | outbound LAN / inbound LAN / Internet が work する想定 |
| Future enforcement / permission denied | outbound LAN / inbound LAN は fail、Internet は work する想定 |
| Future enforcement / permission revoked after initial grant | LAN-dependent features は runtime degradation / fallback が必要 |
| Android 15 / targetSdkVersion 36 | Android 16 LNP opt-in infrastructure は未確認 |
| App uses implicit LAN access | 25Q2 opt-in で依存箇所を検出し、future permission guard が必要 |
| App updates LAN scenarios to request permission | future enforcement 時の user denial / revocation handling が可能になる |
| App handles user rejection / revocation | LAN 機能を graceful degradation できる |
| App does not handle user rejection / revocation | future enforcement 時に discovery / casting / device setup などが失敗し得る |
| App uses NsdManager during opt-in phase | 公式文書上、app process 外 operation は opt-in phase では影響されない |
| App uses raw sockets during opt-in phase | app UID packet として BPF restriction の対象になり得る |
| App uses WebView / OkHttp / Cronet LAN access | host app UID / permission state による影響を受け得る |
| Media casting scenario before future guidance | 多くの casting scenario は影響候補。25Q4 guidance / future API を追跡する |
| Output Switcher in-app picker | 公式文書上、local network permission は不要 |

## Customer-facing Impact

Android 16 へ OS update しただけ:

- Release plan evidence では、current phase は opt-in であり、通常 app に default enforcement はかからない。

targetSdkVersion 36 化:

- AOSP r4 の `RESTRICT_LOCAL_NETWORK` は `@EnabledAfter(targetSdkVersion = 36)` であり、targetSdkVersion 36 では default-enabled ではない。
- target 36 化だけで local network access が失敗するとは説明しない。

25Q2 opt-in testing:

- `adb shell am compat enable RESTRICT_LOCAL_NETWORK <package>` と reboot 後、`NEARBY_WIFI_DEVICES` 未許可の app は LAN traffic が fail し得る。
- これは future enforcement に備えて implicit LAN dependency を見つけるための testing impact である。

Future enforcement:

- later Android release では new Nearby devices permission group permission により local network access が guarded になる見込み。
- user denial / revocation に備え、LAN-dependent feature は permission rationale、settings flow、fallback、feature degradation を設計する必要がある。

## Impacted App Categories

影響対象候補:

- implicit local network access に依存するアプリ
- LAN device discovery を行うアプリ
- mDNS / SSDP を使うアプリ
- NsdManager を使うアプリ
- media casting / remote playback / second screen を扱うアプリ
- smart home / IoT device setup を行うアプリ
- printer / scanner / camera / NAS / router / speaker / TV と接続するアプリ
- local development server / companion app / desktop bridge と接続するアプリ
- TCP server を app 内で立てるアプリ
- UDP multicast / broadcast に依存するアプリ
- native socket を使うアプリ
- OkHttp / Cronet など network library 経由で LAN に接続するアプリ
- WebView から local network resource に接続するアプリ
- Output Switcher 以外の direct casting discovery を持つアプリ
- LAN permission denial / revocation に備える必要があるアプリ

影響が限定的な対象:

- local network access を行わないアプリ
- Internet endpoint のみへ通信するアプリ
- cellular WWAN / VPN のみを扱い LAN address へ直接通信しないアプリ
- Output Switcher in-app picker のみで casting selection が完結するアプリ

## Recommended Action Candidates

- implicit LAN access の棚卸しを行う。
- mDNS / SSDP / NSD / `.local` / LAN IP literals / UDP multicast / broadcast / TCP server / WebView LAN access を検索する。
- Android 16 25Q2 Beta 3 以降相当 build で `RESTRICT_LOCAL_NETWORK` を enable し、reboot 後に local network scenarios を実行する。
- `NEARBY_WIFI_DEVICES` declared / granted / denied / revoked の状態差を確認する。
- future `ACCESS_LOCAL_NETWORK` または new Nearby devices permission に備え、permission request、denied / revoked UX、Settings 導線を設計する。
- LAN access 失敗時の `EPERM` / `ECONNABORTED` / connection failure を feature-specific に graceful handling する。
- casting は Output Switcher / future system-mediated API で permission prompt を避けられるか、direct LAN permission が必要かを分ける。
- 25Q4 casting guidance と 26Q2 / later enforcement evidence を継続監視する。

## Test Considerations

- Android 15 端末上の targetSdkVersion 35
- Android 16 端末上の targetSdkVersion 35
- Android 16 端末上の targetSdkVersion 36
- Android 15 端末上の targetSdkVersion 36 が検証可能な場合の比較
- 25Q2 Beta 3 以降の build
- `RESTRICT_LOCAL_NETWORK` compat flag enabled / disabled
- flag enabled 後の reboot 有無
- `NEARBY_WIFI_DEVICES` declared / not declared
- `NEARBY_WIFI_DEVICES` granted / denied / revoked
- 将来 new Nearby devices permission / `ACCESS_LOCAL_NETWORK` が有効な build での grant / deny / revoke
- implicit LAN access の棚卸し結果
- user rejection / revocation UX
- permission rationale / settings flow
- graceful fallback / feature degradation
- mDNS / SSDP discovery
- NsdManager discovery / registration / resolution
- WebView LAN resource access
- OkHttp / Cronet LAN request
- native socket LAN request
- Output Switcher
- media casting discovery and playback initiation
- existing user upgrade path
- CI / manual test with local network devices

## Facts / Observations / Hypotheses / Conclusions

### Facts

- 公式文書は Release plan を 25Q2 と 26Q2 の 2 release deployment と説明する。
- 公式文書は current stage を opt-in feature と説明する。
- Android 16 r4 AOSP には `RESTRICT_LOCAL_NETWORK = 365139289L` が存在する。
- Android 16 r4 AOSP の `RESTRICT_LOCAL_NETWORK` は `@EnabledAfter(targetSdkVersion = 36)` であり、targetSdkVersion 36 では default-enabled ではない。
- Android 16 r4 AOSP には 25Q2 BPF maps / packet drop path がある。
- Android 16 r4 AOSP には flagged `ACCESS_LOCAL_NETWORK` dangerous permission / AppOp がある。
- Current opt-in restore access は `NEARBY_WIFI_DEVICES` grant で判定される。

### Observations

- Release plan は Android 16 / targetSdkVersion 36 の即時必須対応ではなく、25Q2 opt-in testing と future enforcement preparation の説明である。
- Android 16 OS update だけ、または targetSdkVersion 36 化だけで current LNP restriction が default で有効になる evidence はない。
- Future enforcement の infrastructure は Android 16 r4 に存在するが、final permission UX / target gate / rollout は future evidence が必要。

### Hypotheses

- API 37 以降など、targetSdkVersion 36 より後の target で default enforcement される可能性がある。
- `ACCESS_LOCAL_NETWORK` は future new Nearby devices permission として `NEARBY_WIFI_DEVICES` を置き換える可能性が高い。
- Future enforcement では current opt-in phase で対象外の framework-level operations にも permission gate が広がる可能性がある。

### Conclusions

- Local Network Permission / Release plan は、Android 16 current stage では opt-in testing behavior として扱う。
- Android 16 / targetSdkVersion 36 だけでは current LNP restriction は default-enabled ではない。
- 25Q2 phase では `RESTRICT_LOCAL_NETWORK` を force-enable して implicit LAN access dependency を見つけ、feedback と migration preparation を行う。
- Future enforcement では user denial / revocation を前提に、LAN-dependent features を permission guarded な workflow に更新する必要がある。
- 顧客向けには「Android 16 で即時破壊」ではなく、「Android 16 で準備・検証し、later release enforcement に備える」と説明するのが適切である。

## Missing Evidence / Follow-up

- Official compat framework changes page 上の `RESTRICT_LOCAL_NETWORK` 掲載有無と default state。
- Future release tag での final targetSdkVersion gate。
- Future new permission の final group / prompt UI / revocation behavior。
- NsdManager など framework-level local network operations の future enforcement path。
- 25Q4 casting guidance / APIs。
