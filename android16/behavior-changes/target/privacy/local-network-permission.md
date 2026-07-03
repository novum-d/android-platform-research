# Local Network Permission

## 調査メタデータ

- Android version: Android 16
- Version directory: `android16`
- From tag: `android-15.0.0_r36`
- To tag: `android-16.0.0_r4`
- Previous targetSdkVersion: 35
- Target targetSdkVersion: 36
- Behavior Change section: Local Network Permission
- Official documentation URL: https://developer.android.com/about/versions/16/behavior-changes-16#local-network-permission
- Official documentation category: Privacy
- Report output file: `android16/behavior-changes/target/privacy/local-network-permission.md`
- Summary output file: `android16/summaries/target/privacy/local-network-permission-summary.md`
- Applicability classification: `UNKNOWN_NEEDS_MORE_EVIDENCE`
- Confidence: Medium

Scope note: `android16/AGENTS.md` は To tag を `android-16.0.0_r1` としているが、本調査では依頼どおり `android-16.0.0_r4` を使用した。

Classification note: 現在の Android 16 evidence では、Local Network Protections は `RESTRICT_LOCAL_NETWORK` compat change による opt-in testing behavior として実装されており、default は disabled である。targetSdkVersion 36 gate は確認できない。一方、将来 release で runtime permission enforcement される計画が公式文書と TODO に存在する。許可済み分類に「targetSdk 非依存の opt-in-only compat testing behavior」に対応する label がないため、primary label は `UNKNOWN_NEEDS_MORE_EVIDENCE` とし、実質条件を追加条件として記録する。

## Official Documentation Review

2026-07-03 に公式ドキュメントの `#local-network-permission` セクションを再確認した。対象ページは 2026-07-01 UTC 更新として表示されていた。

確認した公式記述:

- LAN 上の device は、従来 `INTERNET` permission を持つ任意の app からアクセスできる。
- これは local device への接続を容易にする一方、fingerprinting や location proxy など privacy implications がある。
- Local Network Protections は、local network access を新しい runtime permission behind に置くことで user privacy を保護することを目的にしている。
- この変更は 25Q2 と 26Q2 の 2 release に分けて deploy される。
- 現在の stage では LNP は opt-in feature であり、opt in した app だけが影響を受ける。
- raw sockets / libraries による local network address へのアクセス、mDNS、SSDP、NsdManager など local network にアクセスする framework classes が影響対象。
- local network address への traffic to / from には local network access permission が必要。
- outgoing TCP、incoming TCP、UDP unicast / multicast / broadcast send / receive は permission required。
- 制限は networking stack の深い層に実装され、native / managed sockets、Cronet、OkHttp、およびそれらの上に実装された API に適用される。
- `.local` suffix の service resolution は local network permission が必要。
- WebView 由来の local network traffic は host app の permission state を継承する。
- local network 上の DNS server への port 53 traffic は例外。
- Output Switcher を in-app picker として使う app は local network permission が不要。
- media casting の多くは local network access に依存し影響を受けるが、casting app のすべてが新 permission を request する必要があるわけではない。future API / guidance は 25Q4 とされる。
- opt-in 手順は 25Q2 Beta 3 以降の build、app install、`adb shell am compat enable RESTRICT_LOCAL_NETWORK <package>`、device reboot。
- opt-in 後、local network access は socket errors になる。
- opt-in phase では、NsdManager など app process 外で local network operations を実行する API は影響されない。
- access restore には app が `NEARBY_WIFI_DEVICES` を manifest に宣言し、Settings から Nearby devices permission を allow する。
- future Android release では Nearby devices permission group の new permission で guard される。
- enforcement 開始後は、permission granted なら outbound LAN / Internet / inbound LAN が work、not granted なら outbound LAN / inbound LAN は fail し Internet は work。
- errors は `send` / send variants 呼び出し時に calling socket へ返る。例は `EPERM` と `ECONNABORTED`。
- local network は Wi-Fi / Ethernet など broadcast-capable interface を使う IP network を指し、cellular WWAN / VPN は除外される。
- IPv4 link-local、CGNAT、RFC1918、IPv6 link-local、directly-connected routes、Thread など stub networks、multicast、IPv4 broadcast が local network とされる。

依頼文の Original statements / Applicability details と公式本文に実質差分はない。ただし「new runtime permission」は Android 16 current opt-in では `NEARBY_WIFI_DEVICES` を temporary restore permission として使い、future release で new permission に移る、と公式本文上も段階が分かれている。

## AOSP Evidence Scope

Primary evidence:

- `platform/frameworks/base`
  - `android-15.0.0_r36`
  - `android-16.0.0_r4`
- `platform/packages/modules/Connectivity`
  - `android-15.0.0_r36`
  - `android-16.0.0_r4`

Checkout hygiene:

- `frameworks-base` は clean。
- `frameworks-base` に `android-15.0.0_r36` / `android-16.0.0_r4` tag が存在することを確認した。
- `packages/modules/Connectivity` に `android-15.0.0_r36` / `android-16.0.0_r4` tag が存在することを確認した。

Compat official page note:

- 公式 compat framework changes ページを `curl` で確認する tool call は環境側の自動承認で拒否されたため、公式 compat page 上の掲載有無は未確認。
- AOSP の `ConnectivityCompatChanges.java` では Change ID、default state、targetSdk gate annotation を確認した。

## Facts

### Android 16 で `RESTRICT_LOCAL_NETWORK` compat change が追加されている

Reviewed source:

- `packages/modules/Connectivity/framework/src/android/net/connectivity/ConnectivityCompatChanges.java`
- Symbol: `RESTRICT_LOCAL_NETWORK = 365139289L`

Android 16 `android-16.0.0_r4` では次が定義されている。

- `@ChangeId`
- `@Disabled`
- `public static final long RESTRICT_LOCAL_NETWORK = 365139289L`
- comment: local network access を制限し、Android V より後の release を target する app では local network access に permission が必要になる予定。
- TODO: target SDK version が final になったら更新する。

Android 15 `android-15.0.0_r36` には `RESTRICT_LOCAL_NETWORK` は存在しない。

AOSP source context:

- Entry point / caller: `PermissionMonitor.Dependencies.shouldEnforceLocalNetRestrictions(uid)`
- Why relevant: opt-in flag / compat change が有効な UID だけ local network restriction の permission / BPF block map 更新対象になる。
- Baseline Android behavior: Android 15 に `RESTRICT_LOCAL_NETWORK` はない。
- Target Android behavior: Android 16 に Change ID はあるが `@Disabled` default。
- Diff kind: added behavior, disabled by default。
- Classification support: targetSdkVersion 36 gate ではなく、current stage は compat opt-in gate。

### Android 16 で `restrict_local_network` feature flag が追加されている

Reviewed source:

- `packages/modules/Connectivity/common/flags.aconfig`
- Flag: `restrict_local_network`

Android 16 では、local network access を新しい runtime permission behind に置く flag が定義されている。description は `ConnectivityCompatChanges.RESTRICT_LOCAL_NETWORK` が feature enable に必要と説明する。

また `common/mainline_beta.aconfig` には `lnp_developer_opt_in` があり、description は LNP developer opt-in を enable する flag と説明する。

### Android 16 で future new permission `ACCESS_LOCAL_NETWORK` が追加されている

Reviewed source:

- `frameworks-base/core/res/AndroidManifest.xml`
- `frameworks-base/core/api/current.txt`
- `frameworks-base/core/java/android/permission/flags.aconfig`
- `frameworks-base/core/java/android/app/AppOpsManager.java`

Android 16 `android-16.0.0_r4` では `android.permission.ACCESS_LOCAL_NETWORK` が追加されている。

- `@FlaggedApi(android.permission.flags.Flags.FLAG_ACCESS_LOCAL_NETWORK_PERMISSION_ENABLED)`
- `android:permissionGroup="android.permission-group.UNDEFINED"`
- `android:protectionLevel="dangerous"`
- `android:featureFlag="android.permission.flags.access_local_network_permission_enabled"`

`core/api/current.txt` には flagged public API として `Manifest.permission.ACCESS_LOCAL_NETWORK` がある。

`access_local_network_permission_enabled` flag の description は、この flag が new `ACCESS_LOCAL_NETWORK` runtime permission を enable し、local network protection で `NEARBY_WIFI_DEVICES` を置き換えると説明する。

`AppOpsManager` には次が追加されている。

- `OP_ACCESS_LOCAL_NETWORK`
- `OPSTR_ACCESS_LOCAL_NETWORK = "android:access_local_network"`
- AppOpInfo は flag enabled 時に `Manifest.permission.ACCESS_LOCAL_NETWORK` と関連付けられる。

Android 15 `android-15.0.0_r36` には `ACCESS_LOCAL_NETWORK` permission / AppOp は確認できない。

Interpretation:

- Android 16 tag には future new permission の基盤が入っている。
- ただし公式 Android 16 opt-in guidance では、current-stage restore access は `NEARBY_WIFI_DEVICES` grant で行う。

### Current opt-in phase では `NEARBY_WIFI_DEVICES` が restore access に使われる

Reviewed source:

- `packages/modules/Connectivity/service/src/com/android/server/connectivity/PermissionMonitor.java`
- `frameworks-base/services/core/java/com/android/server/media/MediaRouter2ServiceImpl.java`

`PermissionMonitor.Dependencies.shouldEnforceLocalNetRestrictions(uid)` は次を満たす時だけ true を返す。

- `BpfNetMaps.isAtLeast25Q2()`
- `CompatChanges.isChangeEnabled(RESTRICT_LOCAL_NETWORK, uid)`

`PermissionMonitor.setLocalNetworkPermissions(uid, packageName)` は、enforcement 対象 UID について `PermissionManager.checkPermissionForPreflight(NEARBY_WIFI_DEVICES, AttributionSource)` を確認する。

- granted: `mBpfNetMaps.removeUidFromLocalNetBlockMap(uid)`
- not granted: `mBpfNetMaps.addUidToLocalNetBlockMap(uid)`
- SDK sandbox UID は runtime permission を持てないため block map に追加される。

`MediaRouter2ServiceImpl.permissionAllowedForAppCompat("android.permission.ACCESS_LOCAL_NETWORK")` は、Change ID `365139289L` が disabled の UID では permission を満たした扱いにする。Change ID が enabled の場合は `NEARBY_WIFI_DEVICES` permission を確認する。

Interpretation:

- Android 16 current opt-in phase では、`RESTRICT_LOCAL_NETWORK` enabled の app が `NEARBY_WIFI_DEVICES` を grant されていない場合、local network block map に入る。
- `ACCESS_LOCAL_NETWORK` は future new permission として存在するが、current opt-in enforcement の permission check は `NEARBY_WIFI_DEVICES` である。

### Android 16 で BPF map による local network blocking が追加されている

Reviewed source:

- `packages/modules/Connectivity/bpf/progs/netd.c`
- `packages/modules/Connectivity/service/src/com/android/server/BpfNetMaps.java`
- `packages/modules/Connectivity/service/src/com/android/server/ConnectivityService.java`

Android 16 `netd.c` には次の BPF maps が追加されている。

- `local_net_access_map`
  - `LPM_TRIE`
  - `LocalNetAccessKey -> bool`
  - `BPFLOADER_MAINLINE_25Q2_VERSION`
- `local_net_blocked_uid_map`
  - `HASH`
  - `uid -> bool`
  - `BPFLOADER_MAINLINE_25Q2_VERSION`

`should_block_local_network_packets(...)` は:

- system UID は block しない。
- UID が `local_net_blocked_uid_map` に存在しない、または value が false なら block しない。
- packet から remote IP / protocol / remote port を抽出する。
- `local_net_access_map` を longest prefix match で引き、値が false の場合に local network packet を block する。

packet processing path では、SDK level が 25Q2 以上で、既に drop 判定でない packet について `should_block_local_network_packets(...)` が true なら `DROP` になる。

`BpfNetMaps` は Java 側から次を提供する。

- `addLocalNetAccess(...)`
- `removeLocalNetAccess(...)`
- `getLocalNetAccess(...)`
- `addUidToLocalNetBlockMap(uid)`
- `removeUidFromLocalNetBlockMap(uid)`
- `isUidBlockedFromUsingLocalNetwork(uid)`

Android 15 `android-15.0.0_r36` では、`local_net_access_map` / `local_net_blocked_uid_map` / `should_block_local_network_packets` は確認できない。

Diff interpretation:

- Android 16 で BPF-based local network restriction infrastructure が追加された。
- ただし UID が block map に入るのは `RESTRICT_LOCAL_NETWORK` が enabled かつ permission not granted の場合である。

### Local network address definition は AOSP でも確認できる

Reviewed source:

- `packages/modules/Connectivity/staticlibs/framework/com/android/net/module/util/NetworkStackConstants.java`
- `packages/modules/Connectivity/service/src/com/android/server/ConnectivityService.java`
- `packages/modules/Connectivity/tests/unit/java/com/android/server/connectivityservice/CSLocalNetworkProtectionTest.kt`

`NetworkStackConstants.IPV4_LOCAL_PREFIXES`:

- `169.254.0.0/16`
- `100.64.0.0/10`
- `10.0.0.0/8`
- `172.16.0.0/12`
- `192.168.0.0/16`

`NetworkStackConstants.MULTICAST_AND_BROADCAST_PREFIXES`:

- `224.0.0.0/4`
- `ff00::/8`
- `255.255.255.255/32`

`ConnectivityService.getLocalNetworkPrefixesForAddress(...)`:

- IPv6 は prefix length が 0 でなければ local prefix として扱う。
- IPv4 は `IPV4_LOCAL_PREFIXES` に含まれる prefix を local network prefix として返す。

`CSLocalNetworkProtectionTest` は IPv4 private / IPv6 link-local / multicast / broadcast が `local_net_access_map` に追加されることを検証している。

### DNS port exception は AOSP でも確認できる

Reviewed source:

- `packages/modules/Connectivity/service/src/com/android/server/ConnectivityService.java`
- Methods: `addLocalDnsesToBpfMap(...)`, `removeLocalDnsesFromBpfMap(...)`

`addLocalDnsesToBpfMap(...)` は local prefix 内の DNS server について、`local_net_access_map` に allow rule を追加する。

- UDP port 53
- TCP port 53
- TCP port 853 (DNS over TLS)

公式文書は port 53 exception を述べる。AOSP は port 53 に加えて DNS over TLS port 853 も allow rule として追加している。

### NsdManager は opt-in phase で app process outside operation として扱われる公式記述と整合する

公式文書は、NsdManager など app process 外で local network operation を行う API は opt-in phase では影響されないと述べる。

AOSP evidence:

- opt-in enforcement は packet owner UID が `local_net_blocked_uid_map` に入っているかを BPF で見る構造である。
- app process 自身の UID から出る native / managed socket traffic は block map の影響を受ける。
- system service / daemon 側で処理される operation は、app UID packet として出ない場合、current opt-in phase の app UID block map とは別扱いになり得る。

ただし、NsdManager の具体的 call path / daemon UID / mDNS backend の全分岐までは今回の調査では深掘りしていない。

### WebView / Cronet / OkHttp

公式文書は、制限が networking stack 深部にあるため all networking APIs に適用され、native / managed sockets、Cronet、OkHttp、上位 API が対象になると述べる。WebView traffic は host app permission state を継承すると述べる。

AOSP evidence:

- BPF packet path は socket API の種類ではなく packet / UID / interface / remote address / protocol / port を見て drop する。
- そのため app UID から出る Cronet / OkHttp / WebView / native socket / managed socket traffic は、同じ UID permission state によって影響を受ける、という公式説明と整合する。

ただし、WebView が host app permission state を継承する個別コード path は今回の AOSP evidence では未確認である。

## Observations

### Android 16 current stage は targetSdkVersion 36 ではなく opt-in compat flag が実質 gate

`RESTRICT_LOCAL_NETWORK` は Android 16 tag で `@Disabled` であり、`@EnabledSince(targetSdkVersion = 36)` や `@EnabledAfter(targetSdkVersion = 35)` ではない。`PermissionMonitor` も `CompatChanges.isChangeEnabled(RESTRICT_LOCAL_NETWORK, uid)` を見ている。

したがって、Android 16 / targetSdkVersion 35 と Android 16 / targetSdkVersion 36 の差分は、current opt-in stage では確認できない。差分を作るのは `adb shell am compat enable RESTRICT_LOCAL_NETWORK <package>` と 25Q2 以降 build 条件である。

### Future enforcement は別物として扱う必要がある

公式文書は 25Q2 / 26Q2 の release plan と future new permission を述べ、AOSP comment も target SDK の finalization TODO を残している。Android 16 tag には `ACCESS_LOCAL_NETWORK` permission / AppOps / BPF enforcement infrastructure が入っているが、current stage の default behavior は disabled opt-in testing である。

顧客向けには次を混ぜない。

- Android 16 へ OS update しただけの影響
- targetSdkVersion 36 化した影響
- `RESTRICT_LOCAL_NETWORK` を明示 opt-in した testing impact
- future release で runtime permission enforcement が default / target gated になった時の影響

### `ACCESS_LOCAL_NETWORK` は Android 16 API surface にあるが current guidance は `NEARBY_WIFI_DEVICES`

Android 16 AOSP には `ACCESS_LOCAL_NETWORK` が flagged dangerous permission として存在する。ただし公式 Android 16 guidance と `PermissionMonitor` 実装では、current opt-in restore access は `NEARBY_WIFI_DEVICES` を grant する。

これは `ACCESS_LOCAL_NETWORK` が将来の final permission で、Android 16 current stage では compatibility / developer testing のため `NEARBY_WIFI_DEVICES` を temporarily 使っている状態と解釈できる。

### Error mapping は packet drop path から発生すると考えられる

AOSP BPF path は packet を `DROP` する。公式文書は calling socket の `send` / `sendto` variants で `EPERM` / `ECONNABORTED` の例を示す。AOSP の Java / BPF evidence だけでは errno の全 mapping を完全には追跡していないが、BPF drop により socket API へ error が返るという説明とは整合する。

### Output Switcher / casting は MediaRouter path が関係する

公式文書は Output Switcher in-app picker は local network permission 不要、casting scenarios は多くが影響を受けるが future guidance があると述べる。

AOSP evidence:

- `MediaRouter2ServiceImpl` に `ACCESS_LOCAL_NETWORK` permission を app-compat 互換処理する path が追加されている。
- Change ID disabled では permission を満たした扱い、enabled では `NEARBY_WIFI_DEVICES` grant を見る。

ただし、Output Switcher の具体的 UI flow や future 25Q4 casting APIs は今回の Android 16 tag evidence では未確認である。

## Hypotheses

- Future enforcement では `RESTRICT_LOCAL_NETWORK` が targetSdkVersion 37 以降などで default-enabled になり、`ACCESS_LOCAL_NETWORK` が `NEARBY_WIFI_DEVICES` を置き換える可能性が高い。
- BPF `local_net_access_map` / `local_net_blocked_uid_map` は、future runtime permission grant state を network stack に伝える中核 infrastructure になる。
- NsdManager は opt-in phase では system process / daemon path により app UID block map の直接対象外だが、future enforcement では framework-level local network operations にも permission gate が広がる可能性がある。
- WebView の host app permission inheritance は、最終的には host app UID に紐づく BPF / permission state により実現されると推測される。

これらは AOSP comment / flag / official release plan からの推論であり、future release tag で再確認が必要である。

## Applicability Classification

Primary classification: `UNKNOWN_NEEDS_MORE_EVIDENCE`

理由:

- 公式文書は Android 16 targeting apps ページに掲載されているが、current stage は opt-in feature と明記している。
- AOSP `RESTRICT_LOCAL_NETWORK` は Android 16 tag で `@Disabled` であり、targetSdkVersion 36 gate は確認できない。
- Android 16 に BPF enforcement infrastructure と `ACCESS_LOCAL_NETWORK` flagged API は追加されているが、current default behavior と future enforcement behavior が分かれている。
- 許可済み分類に「default disabled compat opt-in testing behavior」を表す label がない。

実質適用条件:

- 25Q2 Beta 3 以降相当の build / BPFLOADER 25Q2 以降
- `RESTRICT_LOCAL_NETWORK` compat flag enabled for package
- app UID が `NEARBY_WIFI_DEVICES` を grant されていない
- app process から local network address へ packet を送受信
- local address / multicast / broadcast / DNS exception などの BPF map 判定に該当

Compat framework:

- Change name: `RESTRICT_LOCAL_NETWORK`
- Change ID: `365139289L`
- AOSP default state: `@Disabled`
- AOSP target gate: Android 16 tag では targetSdkVersion 36 gate なし。comment / TODO は future target SDK update を示す。
- Force-enable / force-disable: `adb shell am compat enable|disable RESTRICT_LOCAL_NETWORK <package>` による opt-in / opt-out testing が公式 guidance と一致する。

## Expected Behavior Matrix

| Scenario | Expected behavior |
|---|---|
| Android 16 / targetSdkVersion 35 | default では local network restriction は無効。`RESTRICT_LOCAL_NETWORK` enabled なら影響し得る |
| Android 16 / targetSdkVersion 36 | target 35 と同様。targetSdkVersion 36 固有 gate は確認できない |
| Android 15 / targetSdkVersion 36 | Android 16 の `RESTRICT_LOCAL_NETWORK` / BPF local network block infrastructure は確認できない |

## Detailed Scenario Matrix

| Scenario | Expected behavior |
|---|---|
| Android 16 / targetSdkVersion 35 / RESTRICT_LOCAL_NETWORK disabled | 従来どおり。`INTERNET` permission による local network access が可能な想定 |
| Android 16 / targetSdkVersion 35 / RESTRICT_LOCAL_NETWORK enabled | `NEARBY_WIFI_DEVICES` 未許可なら app UID が block map に入り local network traffic が fail し得る |
| Android 16 / targetSdkVersion 36 / RESTRICT_LOCAL_NETWORK disabled | 従来どおり。target 36 だけでは current opt-in restriction は有効化されない |
| Android 16 / targetSdkVersion 36 / RESTRICT_LOCAL_NETWORK enabled | target 35 と同様に opt-in restriction がかかる |
| Android 16 / targetSdkVersion 36 / NEARBY_WIFI_DEVICES declared and granted | current opt-in phase では local network access が restored される |
| Android 16 / targetSdkVersion 36 / NEARBY_WIFI_DEVICES declared but denied | current opt-in phase では local network access が fail し得る |
| Android 16 / targetSdkVersion 36 / NEARBY_WIFI_DEVICES not declared | grant できず、opt-in 時は local network access が fail し得る |
| Android 16 / future enforcement / permission granted | outbound LAN / inbound LAN / Internet が work する想定 |
| Android 16 / future enforcement / permission not granted | outbound LAN / inbound LAN は fail、Internet は work する想定 |
| Android 15 / targetSdkVersion 36 / same app behavior | local network permission restriction は確認できない |
| Outbound TCP to LAN | opt-in + permission denied なら fail し得る |
| Incoming TCP from LAN | opt-in + permission denied なら fail し得る |
| UDP unicast send / receive on LAN | opt-in + permission denied なら fail し得る |
| UDP multicast send / receive | multicast prefix が local map に入るため fail し得る |
| UDP broadcast send / receive | broadcast prefix が local map に入るため fail し得る |
| Internet request | local network address でなければ影響しない想定 |
| DNS to local DNS server port 53 | AOSP allow rule があり例外 |
| DNS over TLS to local DNS server port 853 | AOSP allow rule がある。公式文書には port 53 のみ記載 |
| .local service resolution | 公式文書上、permission required |
| mDNS | multicast / local discovery として影響対象 |
| SSDP | multicast / local discovery として影響対象 |
| NsdManager during opt-in phase | 公式文書上、app process 外 operation は opt-in phase では影響なし |
| WebView local network request | host app permission state を継承する想定 |
| Cronet local network request | app UID packet として BPF restriction の影響を受ける想定 |
| OkHttp local network request | app UID packet として BPF restriction の影響を受ける想定 |
| Native socket local network request | app UID packet として BPF restriction の影響を受ける想定 |
| Managed socket local network request | app UID packet として BPF restriction の影響を受ける想定 |
| Media casting discovery | 多くの scenario が影響。future guidance 待ち |
| Output Switcher in-app picker | 公式文書上、local network permission 不要 |
| Wi-Fi / Ethernet local network | local network definition に該当 |
| Cellular WWAN | 公式文書上、local network definition から除外 |
| VPN | 公式文書上、local network definition から除外 |
| IPv4 private address | AOSP `IPV4_LOCAL_PREFIXES` に該当 |
| IPv4 CGNAT | AOSP `IPV4_LOCAL_PREFIXES` に該当 |
| IPv4 link-local | AOSP `IPV4_LOCAL_PREFIXES` に該当 |
| IPv4 multicast / broadcast | AOSP `MULTICAST_AND_BROADCAST_PREFIXES` に該当 |
| IPv6 link-local / multicast / Thread stub network | IPv6 prefix / multicast として local map に入り得る |

## Customer-facing Impact

顧客向け説明では次を分ける。

- Android 16 へ OS update しただけ: current stage では default disabled のため、通常 app は即時影響を受けない想定。
- targetSdkVersion 36 化: AOSP evidence では targetSdkVersion 36 gate は確認できず、target update だけでは current opt-in restriction は有効化されない。
- `RESTRICT_LOCAL_NETWORK` opt-in: 25Q2 Beta 3 以降 build で compat flag を enable し reboot すると、local network access が socket errors で失敗し得る。
- permission restore: current opt-in phase では `NEARBY_WIFI_DEVICES` を宣言し Nearby devices を allow すると復旧する。
- future enforcement: 将来 release では `ACCESS_LOCAL_NETWORK` など new permission による runtime permission handling が必要になる可能性が高い。

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
- OkHttp / Cronet など network library 経由で LAN に接続するアプリ
- WebView から local network resource に接続するアプリ
- Output Switcher 以外の casting picker / direct device discovery を持つアプリ
- LAN permission denial / revocation に備える必要があるアプリ

影響が限定的と考えられる対象:

- local network access を行わないアプリ
- Internet endpoint のみへ通信するアプリ
- cellular WWAN / VPN のみを扱い、LAN address へ直接通信しないアプリ
- Output Switcher in-app picker だけで casting selection が完結するアプリ

## Recommended Action Candidates

- local network access 箇所を棚卸しする。
- mDNS / SSDP / NSD / `.local` / LAN IP / UDP multicast / broadcast / TCP server / WebView LAN access を検索する。
- Android 16 25Q2 Beta 3 以降 build で `RESTRICT_LOCAL_NETWORK` を enable し、reboot 後に local network scenarios を実行する。
- `NEARBY_WIFI_DEVICES` declared / granted / denied / revoked の状態で差分を確認する。
- socket error `EPERM` / `ECONNABORTED` を app 側で適切に扱う。
- future `ACCESS_LOCAL_NETWORK` runtime permission に備え、permission request、denied / revoked UX、Settings 導線を設計する。
- casting は Output Switcher / future system-mediated API で permission prompt を避けられるか、direct local network permission が必要かを分ける。

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
- permission rationale / settings flow
- existing user upgrade path
- CI / manual test with local network devices

## Conclusions

- Android 16 の Local Network Permission は、現在の release stage では default-on の targetSdkVersion 36 behavior change ではなく、`RESTRICT_LOCAL_NETWORK` compat flag による opt-in testing behavior である。
- AOSP `ConnectivityCompatChanges.RESTRICT_LOCAL_NETWORK` は Change ID `365139289L`、default `@Disabled` で、targetSdkVersion 36 gate は確認できない。
- Android 16 には `ACCESS_LOCAL_NETWORK` permission / AppOp / BPF maps / packet drop path が追加されており、future runtime permission enforcement の infrastructure は存在する。
- current opt-in phase では `NEARBY_WIFI_DEVICES` grant が local network access restore に使われる実装が確認できる。
- local network restriction は BPF の UID block map と local address prefix map によって packet level で実現されるため、native sockets、managed sockets、OkHttp、Cronet、WebView など app UID から出る networking API に横断的に影響し得る。
- 顧客向けには「Android 16 / targetSdkVersion 36 で即時必須」ではなく、「Android 16 では opt-in で準備・検証し、将来 runtime permission enforcement に備える」と説明するのが適切である。
