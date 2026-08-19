# Local Network Permission - Impact

## 調査メタデータ

- Android version: Android 16
- Version directory: `android16`
- From tag: `android-15.0.0_r36`
- To tag: `android-16.0.0_r4`
- Previous targetSdkVersion: 35
- Target targetSdkVersion: 36
- Behavior Change section: Local Network Permission / Impact
- Official documentation URL: https://developer.android.com/about/versions/16/behavior-changes-16#impact
- Official documentation category: Privacy
- Report output file: `android16/behavior-changes/target/privacy/local-network-permission-impact.md`
- Summary output file: `android16/summaries/target/privacy/local-network-permission-impact-summary.md`
- Applicability classification: `OPT_IN_ONLY`
- Confidence: High


Classification note: Impact セクションは Android 16 targeting apps ページにあるが、本文は current stage を opt-in feature と明記している。AOSP `android-16.0.0_r4` の `RESTRICT_LOCAL_NETWORK` は `@EnabledAfter(targetSdkVersion = 36)` であり、targetSdkVersion 36 では default-enabled ではない。現在の影響は `RESTRICT_LOCAL_NETWORK` force-enable に依存するため、`OPT_IN_ONLY` を primary label とし、current opt-in / future enforcement / permission-gated behavior を追加条件として記録する。

## Official Documentation Review

2026-07-03 に公式ドキュメントの `#impact` 周辺を再確認した。対象ページは `Last updated 2026-07-01 UTC` と表示されていた。

確認した公式記述:

- Current stage では LNP は opt-in feature であり、opt in した app だけが影響を受ける。
- Opt-in phase の目的は、app が implicit local network access に依存している箇所を開発者が把握し、next release で permission guard できるよう準備すること。
- Local network address への raw sockets の direct / library use が影響対象。例として mDNS / SSDP が挙げられている。
- NsdManager など local network にアクセスする framework-level classes が影響対象。
- Local network address への traffic to / from には local network access permission が必要。
- Outgoing TCP connection、incoming TCP connection、UDP unicast / multicast / broadcast send / receive は permission required。
- 制限は networking stack の深い層に実装されるため all networking APIs に適用される。
- Native / managed sockets、Cronet、OkHttp、およびそれらの上に実装された API が含まれる。
- `.local` suffix の service resolution は local network permission が必要。
- Android WebView 由来の local network traffic は host app の permission state を継承する。
- Local network 上の DNS server への port 53 traffic は exception。
- Output Switcher を in-app picker として使う app は local network permission が不要。
- 多くの media casting scenarios は local network access に依存し、影響を受ける。
- ただし casting を提供する全 app が new permission を request する必要があるわけではなく、future APIs / guidance は 25Q4 とされている。

依頼文の Original statements / Applicability details と公式本文に実質差分はない。なお、公式 Impact section と Developer Guidance section を合わせると、current opt-in phase では NsdManager など app process 外 operation は影響されない、と説明されているため、Impact section の一般論と current opt-in testing behavior は分けて扱う。

## AOSP Evidence Scope

Primary evidence:

- `platform/frameworks/base`
  - `android-15.0.0_r36`
  - `android-16.0.0_r4`
- `platform/packages/modules/Connectivity`
  - `android-15.0.0_r36`
  - `android-16.0.0_r4`

Checkout hygiene:

- `frameworks-base` checkout は clean。
- `packages/modules/Connectivity` checkout は clean。
- `frameworks-base` / `packages/modules/Connectivity` の両方で `android-15.0.0_r36` / `android-16.0.0_r4` tag が存在することを確認済み。
- `frameworks-base` の `ACCESS_LOCAL_NETWORK` evidence は、working tree ではなく `git show android-16.0.0_r4:<path>` で tag から直接確認した。

Compat official page:

- 公式 Android 16 compatibility framework changes ページを確認したが、`RESTRICT_LOCAL_NETWORK` / `365139289` の掲載は見つからなかった。
- AOSP `ConnectivityCompatChanges.java` を compat framework evidence の primary source として扱う。

## Original Statements Verification

| Original statement | Verification |
|---|---|
| "At the current stage, LNP is an opt-in feature..." | 公式文書で確認。AOSP `PermissionMonitor.shouldEnforceLocalNetRestrictions()` は `isAtLeast25Q2()` と `CompatChanges.isChangeEnabled(RESTRICT_LOCAL_NETWORK, uid)` を要求する。 |
| "The goal of the opt-in phase..." | 公式文書で確認。AOSP には 25Q2 BPF infrastructure と compat force-enable path があり、dependency discovery 用の opt-in testing と整合する。 |
| "raw sockets ... mDNS or SSDP" | AOSP BPF path は socket API 名ではなく packet / UID / address / protocol / port を見るため、raw sockets や discovery protocol traffic に影響し得る。 |
| "framework level classes ... NsdManager" | 公式文書で確認。ただし Developer Guidance では current opt-in phase の app process 外 operation は影響されないとされる。AOSP evidence でも current BPF gate は app UID packet 中心である。 |
| "Traffic to and from a local network address requires..." | AOSP `local_net_access_map` と `local_net_blocked_uid_map` により local prefix への packet が drop される path を確認。 |
| "Making outgoing TCP / accepting incoming TCP / UDP send/receive..." | AOSP BPF path は ingress / egress の packet を処理し、TCP / UDP など L4 protocol と remote port を抽出する。 |
| "implemented deep in networking stack..." | AOSP `netd.c` の BPF cgroup packet path で `DROP` するため、socket API 層に依存しない説明と整合する。 |
| "native or managed code, Cronet and OkHttp..." | BPF は app UID packet を見るため、native / managed socket / libraries など API layer を横断して影響し得る。Cronet / OkHttp 個別 code path ではなく共通 packet path による根拠。 |
| ".local suffix" | 公式文書で確認。AOSP の `.local` resolver-specific path は今回未確認。mDNS / multicast local traffic は BPF local map の対象になり得る。 |
| "WebViews inherit permission state from host app" | 公式文書で確認。AOSP 個別 WebView path は未確認だが、host app UID に基づく packet enforcement と整合する。 |
| "DNS server ... port 53 exception" | AOSP `ConnectivityService.addLocalDnsesToBpfMap()` は local DNS server に UDP/TCP 53 allow rule を追加する。AOSP では TCP 853 も allow。 |
| "Output Switcher ... won't need local network permissions" | 公式文書で確認。AOSP `MediaRouter2ServiceImpl` に local network compat workaround があるが、Output Switcher UI flow の完全な exception path は今回未確認。 |
| "Many media casting scenarios..." | 公式文書で確認。AOSP MediaRouter path には `ACCESS_LOCAL_NETWORK` / `RESTRICT_LOCAL_NETWORK` compatibility handling が見えるが、25Q4 future guidance は未確認。 |

## Facts

### Current impact gate は opt-in compat flag である

Reviewed source:

- `packages/modules/Connectivity/framework/src/android/net/connectivity/ConnectivityCompatChanges.java`
- `packages/modules/Connectivity/service/src/com/android/server/connectivity/PermissionMonitor.java`

Android 16 r4 では `RESTRICT_LOCAL_NETWORK = 365139289L` が定義されている。

- `@ChangeId`
- `@EnabledAfter(targetSdkVersion = 36)`
- comment: apps targeting a release after V will require permissions to access the local network
- TODO: target SDK version が finalized されたら更新する

`PermissionMonitor.Dependencies.shouldEnforceLocalNetRestrictions(uid)` は `BpfNetMaps.isAtLeast25Q2()` と `CompatChanges.isChangeEnabled(RESTRICT_LOCAL_NETWORK, uid)` の両方を要求する。

AOSP source context:

- Entry point / caller: package install / permission change 時の `setLocalNetworkPermissions(uid, packageName)`。
- Why relevant: current opt-in phase でどの UID を local network block map に入れるかを決める。
- Baseline Android behavior: Android 15 r36 には `RESTRICT_LOCAL_NETWORK` と local network BPF maps は確認できない。
- Target Android behavior: Android 16 r4 には compat change と BPF infrastructure が追加されている。
- Diff kind: added behavior / opt-in gate / future target gate。
- Applicability support: targetSdkVersion 36 だけでは default-enabled ではなく、current impact は compat flag force-enable が必要。

### Current opt-in restore access は `NEARBY_WIFI_DEVICES` grant に依存する

Reviewed source:

- `packages/modules/Connectivity/service/src/com/android/server/connectivity/PermissionMonitor.java`
- `frameworks-base/services/core/java/com/android/server/media/MediaRouter2ServiceImpl.java` at `android-16.0.0_r4`

`PermissionMonitor.setLocalNetworkPermissions(...)` は `NEARBY_WIFI_DEVICES` を `checkPermissionForPreflight` する。

- granted: UID を `local_net_blocked_uid_map` から削除する。
- denied / missing: UID を `local_net_blocked_uid_map` に追加する。
- SDK sandbox UID は runtime permission を持てないため block map に追加される。

`MediaRouter2ServiceImpl.permissionAllowedForAppCompat("android.permission.ACCESS_LOCAL_NETWORK")` は Change ID `365139289L` が disabled の UID では permission satisfied と扱い、enabled の UID では `NEARBY_WIFI_DEVICES` grant を確認する。この method は temporary workaround とコメントされている。

Interpretation:

- Android 16 current opt-in phase では、future `ACCESS_LOCAL_NETWORK` ではなく `NEARBY_WIFI_DEVICES` によって access restore が行われる。
- `NEARBY_WIFI_DEVICES` denied / missing の状態で opt-in すると、LAN traffic が fail し得る。

### Future permission infrastructure として `ACCESS_LOCAL_NETWORK` が追加されている

Reviewed source:

- `frameworks-base/core/res/AndroidManifest.xml` at `android-16.0.0_r4`
- `frameworks-base/core/api/current.txt` at `android-16.0.0_r4`
- `frameworks-base/core/java/android/permission/flags.aconfig` at `android-16.0.0_r4`
- `frameworks-base/core/java/android/app/AppOpsManager.java` at `android-16.0.0_r4`

Android 16 r4 には `android.permission.ACCESS_LOCAL_NETWORK` が追加されている。

- `@FlaggedApi(android.permission.flags.Flags.FLAG_ACCESS_LOCAL_NETWORK_PERMISSION_ENABLED)`
- `android:protectionLevel="dangerous"`
- `android:featureFlag="android.permission.flags.access_local_network_permission_enabled"`

`access_local_network_permission_enabled` flag の description は、この flag が new `ACCESS_LOCAL_NETWORK` runtime permission を enable し、local network protection で `NEARBY_WIFI_DEVICES` を置き換えると説明する。

`AppOpsManager` には `OP_ACCESS_LOCAL_NETWORK` / `OPSTR_ACCESS_LOCAL_NETWORK` と AppOpInfo が追加され、flag enabled 時に `Manifest.permission.ACCESS_LOCAL_NETWORK` に紐づく。

Android 15 r36 では `ACCESS_LOCAL_NETWORK` は確認できない。

### Networking stack 深部の enforcement は BPF packet path にある

Reviewed source:

- `packages/modules/Connectivity/bpf/progs/netd.c`

Android 16 r4 では次の BPF maps が追加されている。

- `local_net_access_map`
- `local_net_blocked_uid_map`
- both gated by `BPFLOADER_MAINLINE_25Q2_VERSION`

`should_block_local_network_packets(...)` は次を行う。

- system UID は block しない。
- UID が `local_net_blocked_uid_map` にいない場合は block しない。
- IPv4 / IPv6 packet から remote IP を取得する。
- TCP / UDP / DCCP / UDPLITE / SCTP の remote port を抽出する。
- `local_net_access_map` で local access が allowed でない場合に block 判定を返す。

`bpf_traffic_account(...)` は `SDK_LEVEL_IS_AT_LEAST(lvl, 25Q2)` かつまだ drop されていない packet について `should_block_local_network_packets(...)` を呼び、true なら `DROP` にする。

Interpretation:

- Enforcement point は Java/Kotlin API や native API の上位層ではなく、BPF の packet path である。
- そのため native sockets、managed sockets、OkHttp、Cronet、WebView など、host app UID から出る traffic は同じ UID / address / protocol 判定に乗り得る。

### TCP / UDP / ingress / egress の扱い

AOSP `netd.c` は egress / ingress の両方で packet owner / remote endpoint を見ており、TCP / UDP を含む L4 protocol と remote port を抽出する。公式文書の次の影響範囲と整合する。

- outgoing TCP connection
- incoming TCP connection
- UDP unicast send / receive
- UDP multicast send / receive
- UDP broadcast send / receive

ただし、Java の `Socket.connect()` / `DatagramSocket.send()` / native `sendto()` から具体的 errno に変換される全 path は今回の AOSP evidence では完全追跡していない。公式 Errors section は `sendto failed: EPERM` と `sendto failed: ECONNABORTED` を例示している。

### Local network definition は AOSP map population と整合する

Reviewed source:

- `packages/modules/Connectivity/staticlibs/framework/com/android/net/module/util/NetworkStackConstants.java`
- `packages/modules/Connectivity/service/src/com/android/server/ConnectivityService.java`

`IPV4_LOCAL_PREFIXES`:

- `169.254.0.0/16`
- `100.64.0.0/10`
- `10.0.0.0/8`
- `172.16.0.0/12`
- `192.168.0.0/16`

`MULTICAST_AND_BROADCAST_PREFIXES`:

- `224.0.0.0/4`
- `ff00::/8`
- `255.255.255.255/32`

`ConnectivityService.getLocalNetworkPrefixesForAddress(...)` は、IPv6 では prefix length が 0 でなければ local prefix として扱い、IPv4 では `IPV4_LOCAL_PREFIXES` に含まれる prefix を返す。

`ConnectivityService.addLocalAddressesToBpfMap(...)` は 25Q2 以降で local prefixes を `local_net_access_map` に deny rule として追加する。

Interpretation:

- Wi-Fi / Ethernet 上の local address、private IPv4、CGNAT、link-local、multicast、broadcast は BPF map に入る対象になる。
- Cellular WWAN / VPN exclusion logic の完全な call path は今回深掘りしていないが、BPF map population は interface / LinkProperties に紐づくため、local network として map に入った interface / prefix が impact の中心になる。

### DNS port 53 exception は AOSP で確認できる

Reviewed source:

- `packages/modules/Connectivity/service/src/com/android/server/ConnectivityService.java`
- Method: `addLocalDnsesToBpfMap(...)`

Local DNS server が local prefix 内にある場合、AOSP は次を allow rule として `local_net_access_map` に追加する。

- UDP port 53
- TCP port 53
- TCP port 853

公式 Impact section は port 53 exception を述べる。AOSP r4 では DNS over TLS の TCP 853 も allow rule として実装されている。

### NsdManager は current opt-in phase と future enforcement で分ける

公式 Impact section は NsdManager を影響対象に挙げる。一方、Developer Guidance section は、NsdManager のように app process 外で local network operations を行う API は current opt-in phase では影響されないと述べる。

AOSP evidence:

- Current opt-in enforcement は app UID を `local_net_blocked_uid_map` に入れ、packet path の UID を見て drop する。
- app process 自身の socket traffic は直接対象になり得る。
- system service / daemon 側で local network operation が行われる場合、current opt-in phase の app UID packet block とは別扱いになり得る。

Interpretation:

- NsdManager は future enforcement で permission guard が必要になる影響候補として扱う。
- Current opt-in testing で NsdManager が fail しない場合でも、future enforcement の非影響を意味しない。

### WebView / OkHttp / Cronet は host app UID による共通 enforcement と整合する

公式文書は、WebView local network traffic は host app permission state を継承し、Cronet / OkHttp など networking libraries も対象になると述べる。

AOSP evidence:

- BPF enforcement は API library 名ではなく packet / UID / remote address / protocol / port で判定する。
- Host app UID が `local_net_blocked_uid_map` に入ると、その UID から出る networking library traffic は同じ判定に乗り得る。

Limit:

- WebView 内部が host app permission state を参照する個別 code path は今回未確認。
- Cronet / OkHttp 個別実装は AOSP platform 外または library 側に属するため、AOSP evidence は共通 packet path による推論である。

### Output Switcher / media casting

公式文書は、Output Switcher を in-app picker として使う app は local network permission 不要、多くの media casting scenarios は影響を受ける、と述べる。

AOSP evidence:

- `MediaRouter2ServiceImpl.permissionAllowedForAppCompat(...)` に `android.permission.ACCESS_LOCAL_NETWORK` と Change ID `365139289L` を扱う temporary workaround がある。
- Change disabled では permission satisfied、Change enabled では `NEARBY_WIFI_DEVICES` grant を確認する。

Interpretation:

- Media routing / casting 周辺に Local Network Permission transition が関係していることは確認できる。
- Output Switcher exception の complete UI / system-mediated picker path と 25Q4 future guidance は Android 16 r4 evidence だけでは未確認。

## Observations

### Current impact は "opt-in した app" に限定される

Android 16 / targetSdkVersion 35 または 36 の app が、`RESTRICT_LOCAL_NETWORK` disabled のまま通常実行される場合、AOSP evidence では current LNP restriction は有効にならない。Impact section の "only the apps that opt in will be affected" は AOSP gate と整合する。

### targetSdkVersion 36 化だけでは current LNP impact は発生しない

`RESTRICT_LOCAL_NETWORK` は Android 16 r4 で `@EnabledAfter(targetSdkVersion = 36)` であり、targetSdkVersion 36 では default-enabled ではない。したがって、customer-facing explanation では target 36 化だけの影響として説明しない。

### API layer ではなく packet / UID layer の影響として説明するのが実装に近い

AOSP の core enforcement は BPF packet path で、UID と local address / protocol / port に基づく。したがって、native socket / Java socket / OkHttp / Cronet / WebView という API 名は「異なる入口」だが、実装上は同じ packet-level gate に合流する可能性がある。

### Impact section の NsdManager 記述は future enforcement と current opt-in phase で読み分ける

NsdManager は公式 Impact section では影響対象だが、current opt-in guidance では app process 外 operation は影響されないとされる。レポートでは「current opt-in では限定的、future enforcement では影響候補」と分ける。

## Hypotheses

- Future enforcement では `ACCESS_LOCAL_NETWORK` が `NEARBY_WIFI_DEVICES` を置き換え、local network access の final runtime permission になる可能性が高い。
- Future enforcement では current opt-in phase で直接 fail しない NsdManager など framework-level APIs にも permission guard が広がる可能性がある。
- Output Switcher は system-mediated flow として direct LAN discovery permission を app に要求しない設計へ誘導される可能性がある。
- Casting app は direct discovery / control traffic を自前で行う場合と、system picker / future APIs を使う場合で permission need が分かれる可能性がある。

## Applicability Classification

Primary classification: `OPT_IN_ONLY`

理由:

- 公式 Impact section は current stage を opt-in feature と説明する。
- Android 16 r4 の current impact は `RESTRICT_LOCAL_NETWORK` force-enable に依存する。
- `RESTRICT_LOCAL_NETWORK` は `@EnabledAfter(targetSdkVersion = 36)` であり、targetSdkVersion 36 では default-enabled ではない。
- Future enforcement は公式文書と AOSP infrastructure で方向性を確認できるが、final release / target gate / permission UX は未確定。
- `OPT_IN_ONLY` は current opt-in testing behavior を表す分類であり、future permission enforcement は別 release の計画として分ける。

Compat framework:

- Change name: `RESTRICT_LOCAL_NETWORK`
- Change ID: `365139289L`
- AOSP state in Android 16 r4: `@EnabledAfter(targetSdkVersion = 36)`
- Android 16 / targetSdkVersion 35: default では有効化されない
- Android 16 / targetSdkVersion 36: default では有効化されない
- Force-enable / force-disable: `adb shell am compat enable|disable RESTRICT_LOCAL_NETWORK <package>` による testing が公式 guidance と一致する。
- Official Android 16 compat page: `RESTRICT_LOCAL_NETWORK` / `365139289` の掲載は確認できなかった。

Current opt-in impact conditions:

- 25Q2 Beta 3 以降相当 build / `BpfNetMaps.isAtLeast25Q2()`
- Package に `RESTRICT_LOCAL_NETWORK` compat flag enabled
- App UID が `NEARBY_WIFI_DEVICES` を grant されていない
- App process から local network address へ packet を送受信する
- DNS exception など BPF allow rule に該当しない

Future enforcement impact conditions:

- Later Android release で local network permission enforcement が有効
- App が raw sockets / framework API / library / WebView などで LAN access を行う
- User が new local network permission を deny / revoke する、または app が permission handling を実装していない

## Expected Behavior Matrix

| Scenario | Expected behavior |
|---|---|
| Android 16 / targetSdkVersion 35 | default では local network restriction は無効。`RESTRICT_LOCAL_NETWORK` enabled なら opt-in 影響あり |
| Android 16 / targetSdkVersion 36 | target 35 と同様。targetSdkVersion 36 だけでは current LNP restriction は default-enabled ではない |
| Android 15 / targetSdkVersion 36 | Android 16 の `RESTRICT_LOCAL_NETWORK` / BPF local network block infrastructure は確認できない |

## Detailed Impact Matrix

| Scenario | Expected behavior |
|---|---|
| Android 16 / targetSdkVersion 35 / RESTRICT_LOCAL_NETWORK disabled | 従来どおり。implicit LAN access は原則維持 |
| Android 16 / targetSdkVersion 35 / RESTRICT_LOCAL_NETWORK enabled | `NEARBY_WIFI_DEVICES` 未許可なら LAN traffic が fail し得る |
| Android 16 / targetSdkVersion 36 / RESTRICT_LOCAL_NETWORK disabled | 従来どおり。target 36 化だけでは current restriction は有効化されない |
| Android 16 / targetSdkVersion 36 / RESTRICT_LOCAL_NETWORK enabled | target 35 と同様に opt-in restriction が発生し得る |
| Android 16 / targetSdkVersion 36 / NEARBY_WIFI_DEVICES declared and granted | current opt-in phase では local network access が restored される |
| Android 16 / targetSdkVersion 36 / NEARBY_WIFI_DEVICES declared but denied | app UID が block map に入り LAN traffic が fail し得る |
| Android 16 / targetSdkVersion 36 / NEARBY_WIFI_DEVICES not declared | grant できず、opt-in 時は LAN traffic が fail し得る |
| Android 16 / future enforcement / permission granted | outbound LAN / inbound LAN / Internet が work する想定 |
| Android 16 / future enforcement / permission not granted | outbound LAN / inbound LAN は fail、Internet は work する想定 |
| Android 15 / targetSdkVersion 36 / same app behavior | LNP BPF restriction は確認できない |
| Outbound TCP to LAN | opt-in + permission denied なら fail し得る |
| Incoming TCP from LAN | opt-in + permission denied なら fail し得る |
| UDP unicast send / receive on LAN | opt-in + permission denied なら fail し得る |
| UDP multicast send / receive | multicast prefix が local map に入り、opt-in + permission denied なら fail し得る |
| UDP broadcast send / receive | broadcast prefix が local map に入り、opt-in + permission denied なら fail し得る |
| Internet request | local network address でなければ影響しない想定 |
| DNS to local DNS server port 53 | AOSP allow rule があり exception |
| DNS over TLS to local DNS server port 853 | AOSP allow rule がある。公式 Impact section には port 53 のみ記載 |
| .local service resolution | 公式文書上 permission required。resolver-specific path は未確認 |
| mDNS | multicast / local discovery として影響対象 |
| SSDP | multicast / local discovery として影響対象 |
| NsdManager during opt-in phase | 公式 guidance 上、app process 外 operation は opt-in phase では影響なし |
| WebView local network request | host app permission state を継承。AOSP 上は host app UID packet path と整合 |
| Cronet local network request | app UID packet として BPF restriction の影響を受け得る |
| OkHttp local network request | app UID packet として BPF restriction の影響を受け得る |
| Native socket local network request | app UID packet として BPF restriction の影響を受け得る |
| Managed socket local network request | app UID packet として BPF restriction の影響を受け得る |
| Media casting discovery | 多くの scenario が影響候補。25Q4 guidance / future APIs は未確認 |
| Output Switcher in-app picker | 公式文書上、local network permission 不要 |
| Wi-Fi / Ethernet local network | local network definition に該当 |
| Cellular WWAN | 公式文書上、local network definition から除外 |
| VPN | 公式文書上、local network definition から除外 |

## Customer-facing Impact

Android 16 へ OS update しただけ:

- Current stage は opt-in であり、通常 app に default enforcement はかからない。

targetSdkVersion 36 化:

- Android 16 r4 evidence では targetSdkVersion 36 だけで current LNP restriction は有効化されない。

`RESTRICT_LOCAL_NETWORK` opt-in:

- 25Q2 Beta 3 以降相当 build で compat flag を enable し reboot すると、`NEARBY_WIFI_DEVICES` 未許可の LAN traffic が fail し得る。
- Impact の中心は raw sockets / native sockets / managed sockets / OkHttp / Cronet / WebView など host app UID から出る local network packets。

Future enforcement:

- Later Android release では new local network runtime permission により LAN access が guarded になる見込み。
- User denial / revocation を前提に、LAN-dependent features は graceful fallback と permission UX が必要になる。

## Impacted App Categories

影響対象候補:

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
- Java / Kotlin managed sockets を使うアプリ
- OkHttp / Cronet など network library 経由で LAN に接続するアプリ
- WebView から local network resource に接続するアプリ
- Output Switcher 以外の direct casting picker / discovery を持つアプリ
- VPN / cellular only と LAN access を明確に分離していないアプリ
- LAN permission denial / revocation に備える必要があるアプリ

影響が限定的な対象:

- local network access を行わないアプリ
- Internet endpoint のみへ通信するアプリ
- cellular WWAN / VPN のみを扱い LAN address へ直接通信しないアプリ
- Output Switcher in-app picker だけで casting selection が完結するアプリ

## Recommended Action Candidates

- LAN access 箇所を棚卸しする。
- mDNS / SSDP / NSD / `.local` / LAN IP literals / UDP multicast / broadcast / TCP server / WebView LAN access を検索する。
- Android 16 25Q2 Beta 3 以降相当 build で `RESTRICT_LOCAL_NETWORK` を enable し、reboot 後に local network scenarios を実行する。
- `NEARBY_WIFI_DEVICES` declared / granted / denied / revoked の差を確認する。
- socket error `EPERM` / `ECONNABORTED` や connection failure を app feature ごとに graceful handling する。
- Future `ACCESS_LOCAL_NETWORK` または new Nearby devices permission に備え、permission request、denied / revoked UX、Settings 導線を設計する。
- Casting は Output Switcher / future system-mediated API で permission prompt を避けられるか、direct LAN permission が必要かを分ける。

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
- Future new Nearby devices permission / `ACCESS_LOCAL_NETWORK` が有効な build での grant / deny / revoke
- outbound TCP LAN connection
- incoming TCP LAN connection
- UDP unicast / multicast / broadcast send / receive
- mDNS / SSDP discovery
- `.local` name resolution
- NsdManager discovery / registration / resolution
- WebView LAN resource access
- OkHttp / Cronet LAN request
- native socket LAN request
- DNS local server port 53
- DNS over TLS local server port 853
- Output Switcher
- media casting discovery and playback initiation
- Wi-Fi / Ethernet vs cellular / VPN
- `EPERM` / `ECONNABORTED` socket errors
- user denial / revocation UX
- graceful fallback / feature degradation
- existing user upgrade path
- CI / manual test with local network devices

## Facts / Observations / Hypotheses / Conclusions

### Facts

- 公式 Impact section は current stage を opt-in feature と説明する。
- Android 16 r4 AOSP には `RESTRICT_LOCAL_NETWORK = 365139289L` が存在する。
- Android 16 r4 AOSP の `RESTRICT_LOCAL_NETWORK` は `@EnabledAfter(targetSdkVersion = 36)` であり、targetSdkVersion 36 では default-enabled ではない。
- Current opt-in gate は `isAtLeast25Q2()` と `CompatChanges.isChangeEnabled(RESTRICT_LOCAL_NETWORK, uid)`。
- Current opt-in restore access は `NEARBY_WIFI_DEVICES` grant で判定される。
- Android 16 r4 AOSP には BPF `local_net_access_map` / `local_net_blocked_uid_map` と packet drop path がある。
- Android 16 r4 AOSP には future `ACCESS_LOCAL_NETWORK` permission / AppOp がある。

### Observations

- Android 16 OS update だけ、または targetSdkVersion 36 化だけでは、current LNP impact は default で発生しない。
- Impact は app UID packet が local network address に向かうか、local network address から来るかで決まるため、API layer を横断する。
- NsdManager は current opt-in phase と future enforcement で影響の読み分けが必要。
- DNS port 53 exception は AOSP allow rule で確認でき、AOSP では TCP 853 も allow される。

### Hypotheses

- Future enforcement では `ACCESS_LOCAL_NETWORK` が final runtime permission になり、`NEARBY_WIFI_DEVICES` を置き換える可能性が高い。
- Future enforcement では NsdManager など framework-level local network operations にも permission gate が広がる可能性がある。
- Output Switcher / future casting APIs は、direct LAN permission を app に要求しない system-mediated path として扱われる可能性がある。

### Conclusions

- Local Network Permission / Impact は、Android 16 current stage では opt-in testing impact として扱う。
- Current opt-in で影響するのは、`RESTRICT_LOCAL_NETWORK` enabled かつ `NEARBY_WIFI_DEVICES` 未許可の app が、local network traffic を行う場合である。
- BPF packet path による enforcement のため、native / managed sockets、OkHttp、Cronet、WebView など host app UID の local network traffic は横断的に影響し得る。
- Android 16 / targetSdkVersion 36 だけでは current restriction は default-enabled ではない。
- Future enforcement に備え、LAN-dependent features は permission denial / revocation を前提に設計する必要がある。

## Missing Evidence / Follow-up

- Future release tag での final targetSdkVersion gate / default state。
- Future `ACCESS_LOCAL_NETWORK` prompt UI / permission group / revocation behavior。
- NsdManager の future enforcement path。
- WebView host app permission inheritance の個別 implementation path。
- Output Switcher exception の complete system UI / MediaRouter path。
- 25Q4 casting guidance / future APIs。
