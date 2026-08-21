# Local Network Permission - Local Network Definition

## 調査メタデータ

- Android version: Android 16
- Version directory: `android16`
- From tag: `android-15.0.0_r36`
- To tag: `android-16.0.0_r4`
- Previous targetSdkVersion: 35
- Target targetSdkVersion: 36
- Behavior Change section: Local Network Permission / Local Network Definition
- Official documentation URL: https://developer.android.com/about/versions/16/behavior-changes-16#local-network-definition
- Official documentation category: Privacy
- Report output file: `android16/behavior-changes/target/privacy/local-network-permission-local-network-definition.md`
- Summary output file: `android16/summaries/target/privacy/local-network-permission-local-network-definition-summary.md`
- Applicability classification: `OPT_IN_ONLY`
- Confidence: High


Classification note: Local Network DefinitionはAndroid 16 targeting appsページにあるが、Local Network Permission全体はcurrent stageでopt-in featureと説明されている。AOSP `android-16.0.0_r4`の`RESTRICT_LOCAL_NETWORK`は`@EnabledAfter(targetSdkVersion = 36)`であり、targetSdkVersion 36ではdefault-enabledではない。現時点で実際に影響が発生するかどうかは`RESTRICT_LOCAL_NETWORK` force-enableとpermission stateに依存するため、`OPT_IN_ONLY`をprimary labelとし、current opt-in / future enforcement / local network definition / address-prefix classificationを追加条件として記録する。

## Official Documentation Review

2026-07-03 に公式ドキュメントの `#local-network-definition` 周辺を再確認した。対象ページは `Last updated 2026-07-01 UTC` と表示されていた。

確認した公式記述:

- Local Network Protections は local network access を新しい runtime permission の背後に置く privacy project。
- Current stage では LNP は opt-in feature であり、opt in した app だけが影響を受ける。
- Developer Guidance では、25Q2 Beta 3 以降 build、app install、`adb shell am compat enable RESTRICT_LOCAL_NETWORK <package_name>`、reboot によって opt-in testing を行う。
- Current opt-in phase で access restore するには `NEARBY_WIFI_DEVICES` を宣言し、Nearby devices permission を allow する。
- Future Android release では Nearby devices permission group の新 permission で guard される。
- Local Network Definition では、local network を broadcast-capable interface を使う IP network と説明し、Wi-Fi / Ethernet を例示し、cellular WWAN / VPN を除外している。
- IPv4 local network として `169.254.0.0/16`、`100.64.0.0/10`、`10.0.0.0/8`、`172.16.0.0/12`、`192.168.0.0/16` が列挙されている。
- IPv6 local network として link-local、directly-connected routes、Thread などの stub networks、multiple-subnets (TBD) が列挙されている。
- IPv4 multicast `224.0.0.0/4`、IPv6 multicast `ff00::/8`、IPv4 broadcast `255.255.255.255` は local network addresses とされている。

依頼文の Original statements / Applicability details と公式本文に実質差分はない。なお、公式文書の「local network definition」と「permission denial 時に socket error が返る挙動」は別の層の説明なので、本レポートでは分けて扱う。

## AOSP Evidence Scope

Primary evidence:

- `platform/packages/modules/Connectivity`
  - `android-15.0.0_r36`
  - `android-16.0.0_r4`
- `platform/frameworks/base`
  - `android-15.0.0_r36`
  - `android-16.0.0_r4`

Checkout hygiene:

- `frameworks-base` checkout は clean。
- `packages/modules/Connectivity` checkout は clean。
- 両 checkout で `android-15.0.0_r36` / `android-16.0.0_r4` tag が存在することを確認済み。
- Android 15 baseline では `RESTRICT_LOCAL_NETWORK`、`local_net_access_map`、`local_net_blocked_uid_map`、`IPV4_LOCAL_PREFIXES`、`MULTICAST_AND_BROADCAST_PREFIXES` は見つからなかった。

Compat official page:

- 公式 Android 16 compatibility framework changes ページでは `RESTRICT_LOCAL_NETWORK` / `365139289` の掲載を確認できなかった。
- AOSP `ConnectivityCompatChanges.java` を compat framework evidence の primary source として扱う。

## Original Statements Verification

| Original statement | Verification |
|---|---|
| "A local network ... broadcast-capable network interface ... Wi-Fi or Ethernet ... excludes cellular (WWAN) or VPN" | 公式文書で確認。AOSP では local prefix rule が `LinkProperties` / interface name / ifindex に紐づいて BPF map に登録される。ただし、今回確認した code path では explicit な broadcast-capable 判定、cellular 除外、VPN 除外の条件分岐は未確証。 |
| IPv4 `169.254.0.0/16`, `100.64.0.0/10`, `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16` | AOSP `NetworkStackConstants.IPV4_LOCAL_PREFIXES` と一致。 |
| IPv6 link-local | AOSP `ConnectivityService.getLocalNetworkPrefixesForAddress()` は IPv6 address の prefix length が 0 でなければ local prefix として扱う。test でも `fe80.../64` と `fe80::/10` が BPF map 登録対象として検証されている。 |
| IPv6 directly-connected routes | AOSP は `LinkProperties.getLinkAddresses()` から IPv6 prefix を local prefix に登録するため、directly connected な link address / route と整合する。 |
| IPv6 stub networks like Thread | AOSP は stacked links も処理し、`NetworkCapabilities` には `TRANSPORT_THREAD` が存在する。Thread 固有の local network definition path は今回未確証。 |
| IPv6 multiple-subnets (TBD) | 公式文書でも TBD。AOSP r4 で final semantics を示す実装・コメントは未確認。 |
| Multicast `224.0.0.0/4`, `ff00::/8`, IPv4 broadcast `255.255.255.255` | AOSP `NetworkStackConstants.MULTICAST_AND_BROADCAST_PREFIXES` と一致。test でも BPF map への add/remove が検証されている。 |

## Facts

### Current opt-in gate は targetSdkVersion 36 default ではない

Reviewed source:

- `packages/modules/Connectivity/framework/src/android/net/connectivity/ConnectivityCompatChanges.java`
- `packages/modules/Connectivity/service/src/com/android/server/connectivity/PermissionMonitor.java`

Android 16 r4 では `RESTRICT_LOCAL_NETWORK = 365139289L` が定義されている。

- `@ChangeId`
- `@EnabledAfter(targetSdkVersion = 36)`
- comment: apps targeting a release after V will require permissions to access the local network
- TODO: target SDK version が finalized されたら更新する

`PermissionMonitor.Dependencies.shouldEnforceLocalNetRestrictions(uid)` は `BpfNetMaps.isAtLeast25Q2()` と `CompatChanges.isChangeEnabled(RESTRICT_LOCAL_NETWORK, uid)` の両方を要求する。

Source context:

- Entry point / caller: package install / permission change 時の `PermissionMonitor.setLocalNetworkPermissions(uid, packageName)`。
- Relevant responsibility: app UID を local network block map に入れるかを決める。
- Android 15 baseline: 該当 compat change と local network BPF maps は確認できない。
- Android 16 target: compat change、permission monitor、BPF maps が追加されている。
- Diff kind: added behavior / changed gate / current opt-in.
- Applicability support: targetSdkVersion 36 だけでは current default enforcement にならない。

### Current opt-in restore access は `NEARBY_WIFI_DEVICES` grant に依存する

Reviewed source:

- `packages/modules/Connectivity/service/src/com/android/server/connectivity/PermissionMonitor.java`

`setLocalNetworkPermissions(...)` は `NEARBY_WIFI_DEVICES` を `checkPermissionForPreflight` する。

- granted: UID を `local_net_blocked_uid_map` から削除する。
- denied / missing: UID を `local_net_blocked_uid_map` に追加する。
- SDK sandbox UID は runtime permission を持てないため block map に追加される。

Interpretation:

- Android 16 current opt-in phase では future new permission ではなく `NEARBY_WIFI_DEVICES` が access restore に使われる。
- `NEARBY_WIFI_DEVICES` denied / missing の状態で `RESTRICT_LOCAL_NETWORK` を enable すると、local network と定義された宛先への app UID traffic が fail し得る。

### Local network IPv4 prefix は AOSP 定数で明示されている

Reviewed source:

- `packages/modules/Connectivity/staticlibs/framework/com/android/net/module/util/NetworkStackConstants.java`

`IPV4_LOCAL_PREFIXES`:

- `169.254.0.0/16`
- `100.64.0.0/10`
- `10.0.0.0/8`
- `172.16.0.0/12`
- `192.168.0.0/16`

`ConnectivityService.getLocalNetworkPrefixesForAddress(...)` は IPv4 link address がこれらの prefix に含まれる場合、対応する broad prefix を local prefix として返す。例えば `10.0.10.0/24` と `10.0.11.0/24` はどちらも `10.0.0.0/8` の local prefix として扱われる。

Diff interpretation:

- Added behavior: Android 16 r4 の Connectivity module に local network prefix 定数と BPF map population path が追加されている。
- Baseline: Android 15 r36 では同名定数を確認できない。
- Behavior Change relation: 公式の IPv4 range list と一致する。

### Multicast / broadcast prefix は AOSP 定数と test で確認できる

Reviewed source:

- `packages/modules/Connectivity/staticlibs/framework/com/android/net/module/util/NetworkStackConstants.java`
- `packages/modules/Connectivity/tests/unit/java/com/android/server/connectivityservice/CSLocalNetworkProtectionTest.kt`

`MULTICAST_AND_BROADCAST_PREFIXES`:

- `224.0.0.0/4`
- `ff00::/8`
- `255.255.255.255/32`

`ConnectivityService.updateLocalNetworkAddresses(...)` は interface が追加された場合、これらの multicast / broadcast prefixes を `addLocalAddressesToBpfMap(...)` に渡す。unit test は `addLocalNetAccess(...)` がこれら 3 prefix で呼ばれることを検証している。

Interpretation:

- 公式の multicast / IPv4 broadcast statement は AOSP evidence で高く裏付けられる。
- Prefix は interface name / ifindex と組み合わせて BPF LPM trie に入る。

### IPv6 は prefix length が 0 でない LinkAddress を local prefix として扱う

Reviewed source:

- `packages/modules/Connectivity/service/src/com/android/server/ConnectivityService.java`
- `packages/modules/Connectivity/tests/unit/java/com/android/server/connectivityservice/CSLocalNetworkProtectionTest.kt`

`getLocalNetworkPrefixesForAddress(LinkAddress)` は IPv6 の場合、prefix length が 0 でなければ `new IpPrefix(address, prefixLength)` を local prefix として返す。unit test は `fe80.../64`、`2601.../64`、`fe80::/10` などの IPv6 prefix が BPF map に追加されることを検証している。

Interpretation:

- IPv6 link-local は local network definition と整合する。
- Directly-connected routes は `LinkProperties.getLinkAddresses()` から得られる IPv6 prefix を local prefix として扱う実装と整合する。
- Thread stub networks は `LinkProperties.getStackedLinks()` と `TRANSPORT_THREAD` の存在から関連が推定できるが、Thread 固有の判定条件は未確証。
- Multiple-subnets は公式文書上も TBD であり、final behavior としては未確定。

### Local network rule は interface index と remote endpoint による longest-prefix match で評価される

Reviewed source:

- `packages/modules/Connectivity/service/src/com/android/server/BpfNetMaps.java`
- `packages/modules/Connectivity/bpf/progs/netd.h`
- `packages/modules/Connectivity/bpf/progs/netd.c`

`LocalNetAccessKey` は次の fields を持つ。

- `lpm_bitlen`
- `if_index`
- `remote_ip6`
- `protocol`
- `remote_port`

IPv4 は IPv4-mapped IPv6 として保存される。`ConnectivityService.addLocalAddressesToBpfMap(...)` は prefix length に interface index 32 bit と IPv4-mapped IPv6 の 96 bit を加えて LPM trie の key length を作る。

`netd.c` の `should_block_local_network_packets(...)` は app UID が block map に存在する場合に、egress では destination、ingress では source を remote IP として取り出し、protocol / remote port と合わせて `local_net_access_map` を検索する。map に disallowed entry があれば packet を drop する。

Interpretation:

- Local network definition は単純な app-level string / API 判定ではなく、interface index、remote IP prefix、protocol、port の LPM rule として実装されている。
- 「どのアドレスが local network と判定されるか」と「permission denial 時に packet が drop されるか」は、この BPF map population と UID block map の組み合わせで決まる。

### DNS local server exception は local network definition より具体的な allow rule として入る

Reviewed source:

- `packages/modules/Connectivity/service/src/com/android/server/ConnectivityService.java`

`addLocalDnsesToBpfMap(...)` は local prefix 内に含まれる DNS server に対して、block rule より前に allow rule を追加する。

- UDP port 53
- TCP port 53
- TCP port 853

Interpretation:

- 公式文書は local DNS server port 53 を exception として説明している。
- AOSP r4 では TCP 853 も allow されている。
- DNS exception は local network ではないと再分類するのではなく、local network prefix 内の特定 protocol / port を allow rule で上書きする実装と解釈できる。

### `ACCESS_LOCAL_NETWORK` は future permission infrastructure として存在するが current default enforcement は未確定

Reviewed source:

- `frameworks-base/core/api/current.txt` at `android-16.0.0_r4`
- `frameworks-base/core/res/AndroidManifest.xml`
- `frameworks-base/core/java/android/app/AppOpsManager.java`

Android 16 r4 API surface には `android.permission.ACCESS_LOCAL_NETWORK` が `@FlaggedApi("android.permission.flags.access_local_network_permission_enabled")` として存在する。Android 15 r36 API surface には見つからない。`NEARBY_WIFI_DEVICES` は Android 15 r36 / Android 16 r4 の両方に存在する。

Interpretation:

- Future new Nearby devices permission に向けた API / AppOp infrastructure は追加されている。
- ただし公式 current guidance は opt-in testing の access restore に `NEARBY_WIFI_DEVICES` を使う。
- Future enforcement の final default、permission UX、targetSdkVersion gate はこの調査では確定しない。

## Observations

- 公式文書の IPv4 prefix list と AOSP `IPV4_LOCAL_PREFIXES` は一致する。
- 公式文書の multicast / broadcast list と AOSP `MULTICAST_AND_BROADCAST_PREFIXES` は一致する。
- AOSP は IPv6 について「link-local だけ」ではなく、prefix length が 0 でない IPv6 `LinkAddress` を local prefix として扱う。これは directly-connected routes / stub network という公式説明と整合するが、範囲は広い。
- BPF map は interface index を key に含むため、address prefix だけでなく interface も local network 判定に関与する。
- 公式文書の cellular WWAN / VPN exclusion は、今回確認した local prefix map population の範囲では明示的な除外条件としては確認できなかった。`NetworkCapabilities.NET_CAPABILITY_LOCAL_NETWORK` の doc には「Internet access 用 network は local network ではない」とあるが、これは Local Network Permission の address-prefix enforcement と同一概念ではないため、補助情報に留める。
- Current opt-in phaseでは`RESTRICT_LOCAL_NETWORK`をenableしてrebootし、`NEARBY_WIFI_DEVICES`がgrantされていないapp UIDがlocal network trafficを行う場合に、実際の通信影響が出る。

## Hypotheses

- Wi-Fi / Ethernet は `LinkProperties` と broadcast-capable interface として local prefix map population の主対象になる可能性が高い。
- Cellular WWAN / VPN は ConnectivityService の network selection / interface population / NetworkCapabilities 側で local network address registration 対象から外される可能性があるが、今回の証拠だけでは explicit gate としては未確証。
- Thread stub networks は stacked link / IPv6 prefix handling により local network として扱われる可能性が高い。
- Multiple-subnets は公式文書上 TBD であり、今後の Connectivity module 更新で挙動が変わる可能性がある。
- Future enforcement では `ACCESS_LOCAL_NETWORK` が `NEARBY_WIFI_DEVICES` を置き換える可能性が高い。

## Conclusions

- Local Network Definition のうち、IPv4 listed ranges、IPv4/IPv6 multicast、IPv4 broadcast は AOSP r4 の定数・BPF map population・unit test により確認できた。
- IPv6 は `LinkAddress` の prefix length を使う実装であり、link-local / directly-connected route / stub network という公式説明と概ね整合する。ただし Thread 固有・multiple-subnets の final semantics は未確定。
- Local network 判定は address-prefix だけでなく interface index と protocol / remote port を含む BPF longest-prefix match で扱われる。
- Android 16 OS updateだけ、またはtargetSdkVersion 36化だけでは、current stageのLocal Network Permission restrictionがdefaultで発生するとは言えない。現時点で実際に通信へ影響するかどうかは、25Q2以降相当build、`RESTRICT_LOCAL_NETWORK` enable、reboot、permission denied / missingに依存する。
- 顧客向けには「どの宛先が local network に分類されるか」と「その宛先への access が実際に失敗する条件」を分けて説明する必要がある。

## Applicability Gate Evidence

| Gate | Evidence | Conclusion |
|---|---|---|
| Android OS / module version | BPF maps は `BPFLOADER_MAINLINE_25Q2_VERSION`。`BpfNetMaps.isAtLeast25Q2()` が必要。 | Android 16 という名前だけでなく 25Q2 相当の Connectivity / BPF infrastructure が必要。 |
| targetSdkVersion | `RESTRICT_LOCAL_NETWORK` は `@EnabledAfter(targetSdkVersion = 36)`。 | targetSdkVersion 36 では default-enabled ではない。 |
| Compat Change ID | `RESTRICT_LOCAL_NETWORK = 365139289L`。 | Current testing は `adb shell am compat enable RESTRICT_LOCAL_NETWORK <package>` で opt-in。 |
| Permission | Current restore access は `NEARBY_WIFI_DEVICES` grant。Future は new Nearby devices permission / `ACCESS_LOCAL_NETWORK` が示唆される。 | Current と future permission model を分ける。 |
| Address/interface | `IPV4_LOCAL_PREFIXES`、`MULTICAST_AND_BROADCAST_PREFIXES`、IPv6 `LinkAddress` prefix、interface index。 | Local network definition は BPF map に prefix + ifindex として入る。 |
| Exceptions | Local DNS server UDP/TCP 53 と TCP 853 は allow rule。Output Switcher は公式文書上 exception。 | Definition と allow exception を分ける。 |

## Expected Behavior Matrix

| Scenario | Expected behavior |
|---|---|
| Android 16 / targetSdkVersion 35 | `RESTRICT_LOCAL_NETWORK` が disabled なら従来どおり。targetSdkVersion 35 だけでは current restriction は default で有効にならない。 |
| Android 16 / targetSdkVersion 36 | `RESTRICT_LOCAL_NETWORK` が disabled なら従来どおり。targetSdkVersion 36 だけでは current restriction は default で有効にならない。 |
| Android 15 / targetSdkVersion 36 | Android 15 r36 には今回の local network BPF infrastructure / compat change は確認できないため、同等の opt-in restriction は原則なし。 |
| Android 16 / targetSdkVersion 35 / `RESTRICT_LOCAL_NETWORK` disabled | 従来どおり。 |
| Android 16 / targetSdkVersion 35 / `RESTRICT_LOCAL_NETWORK` enabled | 25Q2 相当 build かつ permission denied / missing なら app UID の local network traffic が fail し得る。 |
| Android 16 / targetSdkVersion 36 / `RESTRICT_LOCAL_NETWORK` disabled | 従来どおり。 |
| Android 16 / targetSdkVersion 36 / `RESTRICT_LOCAL_NETWORK` enabled | 25Q2 相当 build かつ permission denied / missing なら app UID の local network traffic が fail し得る。 |
| Android 16 / targetSdkVersion 36 / `NEARBY_WIFI_DEVICES` granted | Current opt-in phase では block map から UID が外れ、local network access は restored。 |
| Android 16 / targetSdkVersion 36 / `NEARBY_WIFI_DEVICES` denied | Current opt-in phase では UID が block map に入り、local network traffic が fail し得る。 |
| Android 16 / future enforcement / permission granted | 公式 guidance 上、outbound LAN / Internet / inbound LAN は works。 |
| Android 16 / future enforcement / permission denied | 公式 guidance 上、outbound LAN / inbound LAN は fails、Internet は works。 |
| Wi-Fi interface / IPv4 RFC1918 address | Local prefix として扱われる可能性が高い。AOSP test は Wi-Fi interface で `10.0.0.0/8` 登録を確認。 |
| Ethernet interface / IPv4 RFC1918 address | 公式文書では local network 例。今回の AOSP test は Wi-Fi 中心で、Ethernet 固有 test は未確認。 |
| Cellular WWAN / IPv4 private-like destination | 公式文書では除外。今回の AOSP evidence では explicit exclusion path 未確証。 |
| VPN connection / local-looking destination | 公式文書では除外。今回の AOSP evidence では explicit exclusion path 未確証。 |
| IPv4 `169.254.0.0/16` | `IPV4_LOCAL_PREFIXES` に含まれる。 |
| IPv4 `100.64.0.0/10` | `IPV4_LOCAL_PREFIXES` に含まれる。 |
| IPv4 `10.0.0.0/8` | `IPV4_LOCAL_PREFIXES` に含まれる。unit test あり。 |
| IPv4 `172.16.0.0/12` | `IPV4_LOCAL_PREFIXES` に含まれる。 |
| IPv4 `192.168.0.0/16` | `IPV4_LOCAL_PREFIXES` に含まれる。 |
| IPv4 `224.0.0.0/4` multicast | `MULTICAST_AND_BROADCAST_PREFIXES` に含まれる。unit test あり。 |
| IPv4 `255.255.255.255` broadcast | `MULTICAST_AND_BROADCAST_PREFIXES` に `/32` として含まれる。unit test あり。 |
| IPv6 link-local | IPv6 prefix length != 0 なら local prefix。`fe80` 系 test あり。 |
| IPv6 directly-connected route | `LinkProperties.getLinkAddresses()` 由来の prefix として local prefix になり得る。 |
| IPv6 Thread stub network | 公式文書では対象。AOSP は stacked links / IPv6 prefix handling と `TRANSPORT_THREAD` を持つが Thread 固有 path は未確証。 |
| IPv6 `ff00::/8` multicast | `MULTICAST_AND_BROADCAST_PREFIXES` に含まれる。unit test あり。 |
| IPv6 multiple-subnets TBD | 公式文書上 TBD。AOSP final behavior 未確定。 |
| Internet public IP destination | local prefix map に該当しなければ allowed。 |
| DNS local server port 53 | local prefix 内でも allow rule。 |
| Output Switcher in-app picker | 公式文書上 permission 不要。definition 自体ではなく exception。 |
| mDNS / SSDP | multicast / local network traffic として影響候補。 |
| NsdManager during opt-in phase | 公式 guidance 上、app process 外 operation は current opt-in phase では影響されない。 |
| WebView local network request | host app UID の permission state を継承する。 |
| Native socket local network request | app UID packet として BPF path に乗り得る。 |
| Managed socket local network request | app UID packet として BPF path に乗り得る。 |

## Customer Impact

この項目の主な価値は、アプリがアクセスしている宛先が将来の Local Network Permission 対象になるかを棚卸しするための definition を明確にすることにある。Android 16 へ OS アップデートしただけ、または targetSdkVersion 36 にしただけで current stage の制限が default 適用されるとは説明しない。

顧客向けには次のように分けて説明する。

- Local network に分類される可能性が高い宛先: RFC1918 private IPv4、CGNAT、IPv4 link-local、IPv4/IPv6 multicast、IPv4 broadcast、IPv6 link-local / directly-connected prefix。
- Current opt-in testing で実際に失敗し得る条件: 25Q2 以降相当 build、`RESTRICT_LOCAL_NETWORK` enabled、reboot 済み、`NEARBY_WIFI_DEVICES` denied / missing、app process / app UID から local network traffic を送受信。
- Future enforcement で備えるべき条件: new Nearby devices permission の deny / revoke、outbound LAN / inbound LAN fail、Internet traffic は継続。
- 例外: local DNS server port 53、Output Switcher in-app picker。AOSP r4 では DNS over TLS TCP 853 も allow rule がある。

## Affected Apps

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
- Thread / Matter / smart home networking に関係するアプリ
- address range allowlist / denylist を独自実装しているアプリ
- LAN permission denial / revocation に備える必要があるアプリ

## Non-Affected or Lower-Risk Cases

- Public Internet destination のみへ接続するアプリ。
- Cellular / VPN のみを使い、公式 definition 上の local network に接続しないアプリ。ただし今回の AOSP evidence では WWAN / VPN exclusion path は未確証なので、実機確認は必要。
- Local DNS server port 53 の DNS traffic。
- Output Switcher を in-app picker として使う flow。
- Current opt-in phase で `RESTRICT_LOCAL_NETWORK` を enable していないアプリ。
- Current opt-in phase で `RESTRICT_LOCAL_NETWORK` enabled でも `NEARBY_WIFI_DEVICES` が granted のアプリ。

## Recommended Action Candidates

- LAN / local network 宛先を prefix ごとに棚卸しする。
- IPv4 private address だけでなく、CGNAT、link-local、multicast、broadcast、IPv6 link-local、directly-connected IPv6 prefix、Thread / Matter 系の stub network を確認する。
- `RESTRICT_LOCAL_NETWORK` を enable した Android 16 25Q2 以降相当 build で、`NEARBY_WIFI_DEVICES` granted / denied / revoked の差を確認する。
- DNS port 53 / Output Switcher / direct casting discovery を分けてテストする。
- 独自の address classifier がある場合、AOSP の `IPV4_LOCAL_PREFIXES` / multicast / broadcast / IPv6 prefix handling とずれないか確認する。
- Future `ACCESS_LOCAL_NETWORK` または new Nearby devices permission の request / denial / revocation UX を設計する。
- LAN access denied 時の graceful fallback、retry suppression、ユーザー説明を用意する。

## Test Focus

- Android 15 端末上の targetSdkVersion 35
- Android 16 端末上の targetSdkVersion 35
- Android 16 端末上の targetSdkVersion 36
- Android 15 端末上の targetSdkVersion 36 が検証可能な場合の比較
- 25Q2 Beta 3 以降の build
- `RESTRICT_LOCAL_NETWORK` enabled / disabled
- flag enabled 後の reboot 有無
- `NEARBY_WIFI_DEVICES` declared / granted / denied / revoked
- Wi-Fi / Ethernet / cellular / VPN の比較
- IPv4 `169.254.0.0/16`
- IPv4 `100.64.0.0/10`
- IPv4 `10.0.0.0/8`
- IPv4 `172.16.0.0/12`
- IPv4 `192.168.0.0/16`
- IPv4 `224.0.0.0/4` multicast
- IPv4 `255.255.255.255` broadcast
- IPv6 link-local
- IPv6 directly-connected routes
- IPv6 Thread stub network
- IPv6 `ff00::/8` multicast
- Internet public IP destination
- DNS local server port 53
- mDNS / SSDP discovery
- NsdManager discovery / registration / resolution
- WebView LAN resource access
- OkHttp / Cronet LAN request
- native socket LAN request
- Output Switcher
- media casting discovery and playback initiation
- local network address 判定と実際の socket error の対応
- graceful fallback / feature degradation

## Missing Evidence / Residual Risk

- Broadcast-capable interface 判定の explicit code path は今回確認できていない。
- Cellular WWAN / VPN exclusion の explicit enforcement path は今回確認できていない。
- Ethernet 固有 test は今回確認できていない。
- Thread stub network 固有の local network definition path は今回確認できていない。
- IPv6 multiple-subnets は公式文書上 TBD であり、final implementation は未確定。
- Output Switcher exception の UI / routing flow 全体は今回の Local Network Definition 調査では深掘りしていない。
- Future `ACCESS_LOCAL_NETWORK` permission の default UX / targetSdkVersion gate / release timing は未確定。

## Facts / Observations / Hypotheses / Conclusions

### Facts

- 公式文書は current stage を opt-in feature と説明している。
- AOSP Android 16 r4 には `RESTRICT_LOCAL_NETWORK = 365139289L` が追加されている。
- `RESTRICT_LOCAL_NETWORK` は `@EnabledAfter(targetSdkVersion = 36)` であり、targetSdkVersion 36 では default-enabled ではない。
- AOSP Android 16 r4 の IPv4 local prefixes は公式文書の IPv4 list と一致する。
- AOSP Android 16 r4 の multicast / broadcast prefixes は公式文書の multicast / broadcast list と一致する。
- AOSP Android 16 r4 は IPv6 `LinkAddress` prefix length が 0 でなければ local prefix として扱う。
- AOSP Android 16 r4 は local DNS server UDP/TCP 53 と TCP 853 に allow rule を追加する。

### Observations

- Local network definition は address-prefix と interface index を組み合わせた BPF LPM rule として実装される。
- Current opt-in impact は `RESTRICT_LOCAL_NETWORK` enabled、25Q2 相当 build、permission denied / missing、app UID traffic の組み合わせで発生する。
- 公式文書の WWAN / VPN exclusion は重要だが、今回の source pass では explicit gate まで確認できていない。
- IPv6 directly-connected / stub network の扱いは、LinkProperties / stacked links の仕組みと整合する。

### Hypotheses

- Future enforcement では `ACCESS_LOCAL_NETWORK` が current opt-in の `NEARBY_WIFI_DEVICES` を置き換える。
- Cellular / VPN exclusion は ConnectivityService より前後の network eligibility / interface registration path で担保される可能性がある。
- Thread / Matter 系の local network は stacked link / IPv6 prefix path で扱われる可能性が高い。

### Conclusions

- IPv4 range、multicast、broadcast の definition は AOSP evidence で確認済み。
- IPv6 definition は AOSP の broad IPv6 prefix handling と整合するが、Thread 固有・multiple-subnets は追加確認が必要。
- Android 16 OS update と targetSdkVersion 36 化だけを Local Network Permission current impact として説明してはいけない。
- 顧客説明では、local network に分類される address / interface と、実際に access failure が起きる opt-in / permission 条件を分ける。

## Human Decision Placeholder

- Final priority: 未判断
- Final severity: 未判断
- Release readiness: 未判断
- Customer communication priority: 未判断
- Decision: 未判断
