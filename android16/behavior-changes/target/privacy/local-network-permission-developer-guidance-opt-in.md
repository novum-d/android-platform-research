# Local Network Permission - Developer Guidance (Opt-in)

## 調査メタデータ

- Android version: Android 16
- Version directory: `android16`
- From tag: `android-15.0.0_r36`
- To tag: `android-16.0.0_r4`
- Previous targetSdkVersion: 35
- Target targetSdkVersion: 36
- Behavior Change section: Local Network Permission / Developer Guidance (Opt-in)
- Official documentation URL: https://developer.android.com/about/versions/16/behavior-changes-16#developer-guidance-opt-in
- Official documentation category: Privacy
- Report output file: `android16/behavior-changes/target/privacy/local-network-permission-developer-guidance-opt-in.md`
- Summary output file: `android16/summaries/target/privacy/local-network-permission-developer-guidance-opt-in-summary.md`
- Applicability classification: `OPT_IN_ONLY`
- Confidence: High


Classification note: Developer Guidance (Opt-in) は、Android 16 current stage の developer testing 手順を説明する項目である。AOSP `android-16.0.0_r4` の `RESTRICT_LOCAL_NETWORK` は `@EnabledAfter(targetSdkVersion = 36)` であり、targetSdkVersion 36 では default-enabled ではない。現在の影響は `RESTRICT_LOCAL_NETWORK` force-enable と reboot / permission state に依存するため、`OPT_IN_ONLY` を primary label とし、current opt-in / future enforcement / AppCompat flag testing behavior を追加条件として記録する。

## Official Documentation Review

2026-07-03 に公式ドキュメントの `#developer-guidance-opt-in` セクションを再確認した。対象ページは `Last updated 2026-07-01 UTC` と表示されていた。

確認した公式記述:

- Local network restrictions に opt in するには、25Q2 Beta 3 以降の build を flash する。
- Test 対象 app を install する。
- `adb shell am compat enable RESTRICT_LOCAL_NETWORK <package_name>` で AppCompat flag を toggle する。
- Device を reboot する。
- Reboot 後、app の local network access は restricted になり、local network access の試行は socket errors につながる。
- NsdManager など app process 外で local network operations を行う API は opt-in phase では影響されない。
- Access を restore するには `NEARBY_WIFI_DEVICES` permission を grant する必要がある。
- App manifest で `NEARBY_WIFI_DEVICES` を宣言し、Settings > Apps > [Application Name] > Permissions > Nearby devices > Allow で許可する。
- Future Android release では、Nearby devices permission group の new permission で guard される。
- Access restored 後は、opt-in 前と同様に scenarios が work するはず。
- Enforcement 開始後は、permission granted なら outbound LAN / outbound-inbound Internet / inbound LAN が works、not granted なら outbound LAN / inbound LAN は fails、Internet は works。
- `adb shell am compat disable RESTRICT_LOCAL_NETWORK <package_name>` で AppCompat flag を toggle-off する。

依頼文の Original statements / Applicability details と公式本文に実質差分はない。なお、公式文書は "Appcompat" / "App-Compat" と表記ゆれがあるが、AOSP evidence 上は compatibility framework change `RESTRICT_LOCAL_NETWORK` と対応する。

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
- 両 checkout に `android-15.0.0_r36` / `android-16.0.0_r4` tag が存在することを確認済み。
- `frameworks-base` の `ACCESS_LOCAL_NETWORK` evidence は `git show android-16.0.0_r4:<path>` で tag から直接確認した。

## Original Statements Verification

| Original statement | Verification |
|---|---|
| "Flash the device to a build with 25Q2 Beta 3 or later." | AOSP では `BpfNetMaps.isAtLeast25Q2()` / `SdkUtil.isAtLeast25Q2()` と `BPFLOADER_MAINLINE_25Q2_VERSION` が current opt-in infrastructure の gate として確認できる。 |
| "Install the app to be tested." | `PermissionMonitor` は package install (`onPackageAdded`) で `setLocalNetworkPermissions(uid, packageName)` を呼ぶ。 |
| "adb shell am compat enable RESTRICT_LOCAL_NETWORK..." | AOSP `ConnectivityCompatChanges.RESTRICT_LOCAL_NETWORK = 365139289L` が存在し、`PermissionMonitor` は `CompatChanges.isChangeEnabled(RESTRICT_LOCAL_NETWORK, uid)` を enforcement gate に使う。 |
| "Reboot The device" | AOSP `PermissionMonitor` は boot/startMonitoring 時に全 user / installed apps を mass update し、package add/remove と permission change を監視する。Compat flag change 自体の listener は確認できないため、flag enable 後 reboot で block map を再構築する公式手順と整合する。 |
| "any attempt to access the local network will lead to socket errors" | AOSP BPF path は blocked UID の local network packet を `DROP` する。具体 errno は公式 Errors section の `EPERM` / `ECONNABORTED` が primary source。 |
| "NsdManager ... won't be impacted during the opt-in phase" | Current opt-in は app UID の packet block map に基づく。System service / daemon 側 operation は app process socket traffic と別扱いになり得る。NsdManager full path は未確認。 |
| "restore access ... NEARBY_WIFI_DEVICES" | `PermissionMonitor.setLocalNetworkPermissions` は `NEARBY_WIFI_DEVICES` を `checkPermissionForPreflight` し、granted なら UID を block map から削除、denied なら追加する。 |
| "future Android release ... new permission" | Android 16 r4 には flagged `ACCESS_LOCAL_NETWORK` dangerous permission / AppOp が追加され、flag description は `NEARBY_WIFI_DEVICES` を置き換えると説明する。 |
| "compat disable ..." | AOSP compat framework change と対応する。`PermissionMonitor` は compat state を enforcement gate として読む。ただし disable 直後の block map 再計算 trigger は明示的には確認できない。 |

## Facts

### `RESTRICT_LOCAL_NETWORK` は current opt-in testing の compat change である

Reviewed source:

- `packages/modules/Connectivity/framework/src/android/net/connectivity/ConnectivityCompatChanges.java`
- Symbol: `RESTRICT_LOCAL_NETWORK = 365139289L`

Android 16 r4 では次が定義されている。

- `@ChangeId`
- `@EnabledAfter(targetSdkVersion = 36)`
- `public static final long RESTRICT_LOCAL_NETWORK = 365139289L`
- comment: apps targeting a release after V will require permissions to access the local network
- TODO: target SDK version が finalized されたら更新する

Android 15 r36 では `RESTRICT_LOCAL_NETWORK` は確認できない。

AOSP source context:

- Entry point / caller: `PermissionMonitor.Dependencies.shouldEnforceLocalNetRestrictions(uid)`
- Why relevant: `adb shell am compat enable|disable RESTRICT_LOCAL_NETWORK <package>` が影響する compatibility change。
- Baseline Android behavior: Android 15 r36 には LNP compat change / BPF local network maps は確認できない。
- Target Android behavior: Android 16 r4 には compat change が存在するが targetSdkVersion 36 では default-enabled ではない。
- Diff kind: added behavior / opt-in capable compat change / future target gate。
- Applicability support: current guidance は targetSdkVersion 36 自動適用ではなく AppCompat flag testing である。

### Current opt-in gate は 25Q2 以降 build と compat flag enabled

Reviewed source:

- `packages/modules/Connectivity/service/src/com/android/server/connectivity/PermissionMonitor.java`
- `packages/modules/Connectivity/staticlibs/framework/com/android/net/module/util/SdkUtil.java`
- `packages/modules/Connectivity/bpf/progs/netd.c`

`PermissionMonitor.Dependencies.shouldEnforceLocalNetRestrictions(uid)` は次を要求する。

- `BpfNetMaps.isAtLeast25Q2()`
- `CompatChanges.isChangeEnabled(RESTRICT_LOCAL_NETWORK, uid)`

`SdkUtil.isAtLeast25Q2()` は `SDK_INT >= 36` または `SDK_INT == 35 && CODENAME == "Baklava"` を true とする。

`netd.c` の `local_net_access_map` / `local_net_blocked_uid_map` は `BPFLOADER_MAINLINE_25Q2_VERSION` で定義される。

Interpretation:

- 公式の 25Q2 Beta 3 以降 build 条件は、AOSP の 25Q2 gate / BPF map availability と整合する。
- Android 16 / targetSdkVersion 36 だけでは current opt-in restriction は有効化されない。

### Install before flag enable / reboot guidance は PermissionMonitor の update timing と整合する

Reviewed source:

- `packages/modules/Connectivity/service/src/com/android/server/connectivity/PermissionMonitor.java`

`PermissionMonitor` class comment は、boot 時に mass update を行い、その後 app install/remove を monitor すると説明する。

`startMonitoring()` は:

- package add/remove receiver を登録する。
- user add/remove receiver を登録する。
- `UIDS_ALLOWED_ON_RESTRICTED_NETWORKS` observer を登録する。
- `onUserAdded(user)` を各 user について呼び、installed apps の permissions を更新する。

`onPackageAdded(packageName, uid)` は `setLocalNetworkPermissions(uid, packageName)` を呼ぶ。

`PermissionChangeListener.onPermissionsChanged(uid)` は `setLocalNetworkPermissions(uid, null)` を呼ぶ。

Observation:

- AOSP では、compat flag change 自体を `PermissionMonitor` が listener で受ける path は確認できない。
- そのため、app install 後に compat flag を enable し、reboot で `startMonitoring()` / mass update を通して block map を再構築する公式手順は実装と整合する。
- Permission grant / revoke は permission listener で再計算されるため、`NEARBY_WIFI_DEVICES` grant による restore は reboot なしでも反映される可能性がある。ただし公式 guidance は Settings で grant 後の挙動確認を求めており、実機での UI / timing は検証が必要である。

### `NEARBY_WIFI_DEVICES` grant が current opt-in restore access に使われる

Reviewed source:

- `packages/modules/Connectivity/service/src/com/android/server/connectivity/PermissionMonitor.java`
- Method: `setLocalNetworkPermissions(int uid, String packageName)`

`setLocalNetworkPermissions(...)` は enforcement 対象 UID について `NEARBY_WIFI_DEVICES` を `PermissionManager.checkPermissionForPreflight(...)` する。

- `PERMISSION_GRANTED`: `mBpfNetMaps.removeUidFromLocalNetBlockMap(uid)`
- not granted: `mBpfNetMaps.addUidToLocalNetBlockMap(uid)`
- SDK sandbox UID は runtime permission を持てないため block map に追加される。

Reviewed source:

- `frameworks-base/services/core/java/com/android/server/media/MediaRouter2ServiceImpl.java` at `android-16.0.0_r4`

`permissionAllowedForAppCompat("android.permission.ACCESS_LOCAL_NETWORK")` は Change ID `365139289L` が disabled の UID では permission satisfied と扱い、enabled の UID では `NEARBY_WIFI_DEVICES` grant を確認する。この method は temporary workaround とコメントされている。

Interpretation:

- 公式の "To restore access, grant NEARBY_WIFI_DEVICES" は AOSP 実装で確認できる。
- `NEARBY_WIFI_DEVICES` が manifest にない / denied の場合、current opt-in phase では UID が block map に入り local network traffic が fail し得る。

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

`access_local_network_permission_enabled` flag の description は、new `ACCESS_LOCAL_NETWORK` runtime permission を enable し、local network protection で `NEARBY_WIFI_DEVICES` を置き換えると説明する。

`AppOpsManager` には `OP_ACCESS_LOCAL_NETWORK` / `OPSTR_ACCESS_LOCAL_NETWORK` と AppOpInfo が追加される。

Android 15 r36 では `ACCESS_LOCAL_NETWORK` は確認できない。

Interpretation:

- Future Android release の new permission 計画は AOSP API surface と整合する。
- Current opt-in phase では `ACCESS_LOCAL_NETWORK` ではなく `NEARBY_WIFI_DEVICES` が restore access に使われる点を明確に分ける必要がある。

### Socket restriction は BPF packet path で発生する

Reviewed source:

- `packages/modules/Connectivity/bpf/progs/netd.c`

Android 16 r4 では:

- `local_net_access_map`
- `local_net_blocked_uid_map`
- `should_block_local_network_packets(...)`

が追加されている。

`should_block_local_network_packets(...)` は blocked UID の IPv4 / IPv6 packet から remote IP / protocol / port を抽出し、`local_net_access_map` で local access が allowed でない場合に block 判定を返す。

`bpf_traffic_account(...)` は `SDK_LEVEL_IS_AT_LEAST(lvl, 25Q2)` かつまだ `DROP` でない packet について `should_block_local_network_packets(...)` を呼び、true なら `DROP` にする。

Interpretation:

- Opt-in 後に socket errors が発生するという公式説明は、BPF packet drop path と整合する。
- Native sockets、managed sockets、OkHttp、Cronet、WebView などは app UID packet として同じ gate に乗り得る。
- `EPERM` / `ECONNABORTED` の errno mapping 全体は Errors section の調査対象であり、本項目では socket error が起きる根拠までを扱う。

### DNS / Output Switcher / NsdManager は opt-in testing で区別する

DNS:

- `ConnectivityService.addLocalDnsesToBpfMap(...)` は local DNS server に UDP/TCP port 53 allow rule を追加する。
- AOSP r4 では TCP 853 も allow rule として追加される。

Output Switcher:

- 公式文書は Output Switcher in-app picker は local network permission 不要とする。
- AOSP では `MediaRouter2ServiceImpl` に `ACCESS_LOCAL_NETWORK` / `RESTRICT_LOCAL_NETWORK` compatibility handling が見えるが、Output Switcher UI flow 全体は今回未確認。

NsdManager:

- 公式 guidance は、NsdManager など app process 外 operations は opt-in phase では影響されないとする。
- AOSP current opt-in gate は app UID block map に基づくため、この説明と整合する。
- Future enforcement では NsdManager も permission guarded になる可能性があり、current opt-in 非影響とは分ける。

## Observations

### `adb compat enable` だけではなく reboot が guidance に含まれる理由

AOSP evidence では、`PermissionMonitor` は boot/startMonitoring 時に全 installed apps を mass update し、package add/remove と permission changes を監視する。一方、compat flag change 自体を受けて `setLocalNetworkPermissions` を呼ぶ listener は確認できない。

したがって、公式手順が app install 後に compat flag を enable し reboot する理由は、reboot によって current compat state を読んだ上で UID block map を再構築させるため、と解釈できる。

### Restore access は current testing 用の `NEARBY_WIFI_DEVICES` と future permission を混ぜない

Current opt-in restore:

- `NEARBY_WIFI_DEVICES` declared and granted。
- Permission change listener により block map から UID が外れる。

Future enforcement:

- `ACCESS_LOCAL_NETWORK` など new Nearby devices permission が想定される。
- Final prompt / revocation behavior / target gate は future release evidence が必要。

### Android 16 / targetSdkVersion 36 だけでは opt-in testing と同じ状態にならない

`RESTRICT_LOCAL_NETWORK` は `@EnabledAfter(targetSdkVersion = 36)` であり、targetSdkVersion 36 では default-enabled ではない。Developer Guidance の adb command を実行して初めて current testing impact が発生する。

### Toggle-off の即時性は実機確認が必要

公式文書は `adb shell am compat disable RESTRICT_LOCAL_NETWORK <package_name>` で toggle-off できると述べる。AOSP gate は `CompatChanges.isChangeEnabled(...)` だが、UID がすでに `local_net_blocked_uid_map` に入った後、compat disable だけで map が即時再計算される path は今回確認できない。

実務テストでは、compat disable 後に permission change / app reinstall / reboot の有無で block map がどう更新されるかを確認する必要がある。

## Hypotheses

- Compat flag enable 後の reboot は、boot 時 mass update で `local_net_blocked_uid_map` を current compat state に同期させるために必要とされている可能性が高い。
- `NEARBY_WIFI_DEVICES` grant / revoke は permission listener によって block map に反映されるため、compat flag より即時性が高い可能性がある。
- Future enforcement では `ACCESS_LOCAL_NETWORK` が `NEARBY_WIFI_DEVICES` を置き換え、current testing 手順の restore permission は変更される可能性が高い。
- Current opt-in phase で NsdManager が影響されない場合でも、future enforcement では framework API 側に permission gate が追加される可能性がある。

## Applicability Classification

Primary classification: `OPT_IN_ONLY`

理由:

- 公式 Developer Guidance は current opt-in testing 手順を説明しており、Android 16 / targetSdkVersion 36 の default behavior ではない。
- AOSP `RESTRICT_LOCAL_NETWORK` は Android 16 r4 で `@EnabledAfter(targetSdkVersion = 36)` であり、targetSdkVersion 36 では default-enabled ではない。
- Current impact は 25Q2+ build、compat flag enabled、reboot / block map update、`NEARBY_WIFI_DEVICES` permission state に依存する。
- Future enforcement は公式文書と `ACCESS_LOCAL_NETWORK` infrastructure で方向性を確認できるが、final release / target gate / permission UX は未確定。

Compat framework:

- Change name: `RESTRICT_LOCAL_NETWORK`
- Change ID: `365139289L`
- AOSP state in Android 16 r4: `@EnabledAfter(targetSdkVersion = 36)`
- Android 16 / targetSdkVersion 35: default では有効化されない
- Android 16 / targetSdkVersion 36: default では有効化されない
- Force-enable / force-disable: `adb shell am compat enable|disable RESTRICT_LOCAL_NETWORK <package>` による testing が公式 guidance と一致する。

Current opt-in testing conditions:

- 25Q2 Beta 3 以降相当 build / `isAtLeast25Q2()`
- App installed
- `RESTRICT_LOCAL_NETWORK` compat flag enabled
- Reboot または block map 再構築 trigger
- `NEARBY_WIFI_DEVICES` not granted の場合に local network traffic が fail し得る
- `NEARBY_WIFI_DEVICES` granted の場合に current access が restored される

## Expected Behavior Matrix

| Scenario | Expected behavior |
|---|---|
| Android 16 / targetSdkVersion 35 | default では local network restriction は無効。`RESTRICT_LOCAL_NETWORK` enabled + reboot なら opt-in 影響あり |
| Android 16 / targetSdkVersion 36 | target 35 と同様。targetSdkVersion 36 だけでは current LNP restriction は default-enabled ではない |
| Android 15 / targetSdkVersion 36 | Android 16 の `RESTRICT_LOCAL_NETWORK` / BPF local network block infrastructure は確認できない |

## Detailed Opt-in Matrix

| Scenario | Expected behavior |
|---|---|
| Android 16 / targetSdkVersion 35 / RESTRICT_LOCAL_NETWORK disabled | 従来どおり |
| Android 16 / targetSdkVersion 35 / RESTRICT_LOCAL_NETWORK enabled before reboot | block map 未同期の可能性がある。公式手順では reboot required |
| Android 16 / targetSdkVersion 35 / RESTRICT_LOCAL_NETWORK enabled after reboot | `NEARBY_WIFI_DEVICES` 未許可なら LAN traffic が fail し得る |
| Android 16 / targetSdkVersion 36 / RESTRICT_LOCAL_NETWORK disabled | 従来どおり。target 36 化だけでは current restriction は有効化されない |
| Android 16 / targetSdkVersion 36 / RESTRICT_LOCAL_NETWORK enabled before reboot | block map 未同期の可能性がある。公式手順では reboot required |
| Android 16 / targetSdkVersion 36 / RESTRICT_LOCAL_NETWORK enabled after reboot | target 35 と同様に opt-in restriction が発生し得る |
| Android 16 / targetSdkVersion 36 / RESTRICT_LOCAL_NETWORK disabled after toggle-off | AOSP gate は disabled になるが、既存 block map の即時更新は実機確認が必要 |
| Android 16 / targetSdkVersion 36 / NEARBY_WIFI_DEVICES declared and granted | current opt-in phase では UID が block map から外れ、access restored |
| Android 16 / targetSdkVersion 36 / NEARBY_WIFI_DEVICES declared but denied | UID が block map に入り、LAN traffic が fail し得る |
| Android 16 / targetSdkVersion 36 / NEARBY_WIFI_DEVICES not declared | grant できず、opt-in 時は LAN traffic が fail し得る |
| Android 16 / future enforcement / new permission granted | outbound LAN / inbound LAN / Internet が work する想定 |
| Android 16 / future enforcement / new permission not granted | outbound LAN / inbound LAN は fail、Internet は work する想定 |
| Android 16 / future enforcement / new permission revoked | LAN-dependent features は runtime fallback が必要 |
| Android 15 / targetSdkVersion 36 | LNP opt-in infrastructure は未確認 |
| App-process raw socket LAN access during opt-in | app UID packet として BPF restriction の対象 |
| Native socket LAN access during opt-in | app UID packet として BPF restriction の対象 |
| Managed socket LAN access during opt-in | app UID packet として BPF restriction の対象 |
| OkHttp / Cronet LAN access during opt-in | app UID packet として BPF restriction の対象 |
| WebView LAN access during opt-in | host app permission state を継承する想定 |
| NsdManager during opt-in phase | 公式 guidance 上、app process 外 operation は影響なし |
| Outbound LAN request | opt-in + permission denied なら fail |
| Inbound LAN request | opt-in + permission denied なら fail |
| Outbound/inbound Internet request | local address でなければ work する想定 |
| DNS to local DNS server port 53 | AOSP allow rule があり exception |
| Output Switcher in-app picker | 公式文書上 permission 不要 |
| Media casting discovery | direct LAN discovery は影響候補。future guidance 待ち |
| Socket error appears | BPF drop により socket error が発生し得る |
| Socket access restored after NEARBY_WIFI_DEVICES grant | Permission listener / block map remove path と整合 |
| Socket restriction removed after compat flag disabled | Gate は disabled になるが map 更新 timing は実機確認が必要 |

## Customer-facing Impact

Android 16 へ OS update しただけ:

- Current opt-in testing は自動では有効にならない。

targetSdkVersion 36 化:

- target 36 化だけでは current opt-in restriction は有効化されない。

`RESTRICT_LOCAL_NETWORK` を enable + reboot:

- `NEARBY_WIFI_DEVICES` 未許可の app は LAN traffic が fail し得る。
- これは future enforcement に備えて LAN dependency を見つけるための testing impact。

`NEARBY_WIFI_DEVICES` grant:

- Current opt-in phase では access restored と扱われる。
- Future release では new permission に置き換わる可能性が高い。

Future enforcement:

- Permission denied / revoked 時に outbound LAN / inbound LAN が fail し、Internet は work する想定。

## Impacted App Categories

影響対象候補:

- opt-in testing を実施するアプリ
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

## Recommended Action Candidates

- 公式手順どおり、25Q2 Beta 3 以降相当 build、app install、compat flag enable、reboot の順で testing する。
- `NEARBY_WIFI_DEVICES` declared / granted / denied / revoked の差を確認する。
- Compat flag disable 後の挙動は、必要に応じて reboot / app reinstall / permission change と組み合わせて確認する。
- LAN dependency を mDNS / SSDP / NSD / `.local` / LAN IP / UDP multicast / broadcast / TCP server / WebView LAN access で棚卸しする。
- Socket errors を feature-specific に graceful handling する。
- Future `ACCESS_LOCAL_NETWORK` または new Nearby devices permission に備え、permission request、denied / revoked UX、Settings 導線を設計する。
- NsdManager は current opt-in で fail しない可能性があるため、future enforcement での検証対象として残す。

## Test Considerations

- Android 15 端末上の targetSdkVersion 35
- Android 16 端末上の targetSdkVersion 35
- Android 16 端末上の targetSdkVersion 36
- Android 15 端末上の targetSdkVersion 36 が検証可能な場合の比較
- 25Q2 Beta 3 以降の build
- app install before compat flag enable
- `RESTRICT_LOCAL_NETWORK` compat flag enabled / disabled
- flag enabled 後の reboot 有無
- compat flag disabled 後の挙動
- `NEARBY_WIFI_DEVICES` declared / not declared
- `NEARBY_WIFI_DEVICES` granted / denied / revoked
- Settings > Apps > Permissions > Nearby devices > Allow flow
- Future new Nearby devices permission / `ACCESS_LOCAL_NETWORK` が有効な build での grant / deny / revoke
- outbound TCP LAN connection
- incoming TCP LAN connection
- UDP unicast / multicast / broadcast send / receive
- mDNS / SSDP discovery
- `.local` name resolution
- NsdManager discovery / registration / resolution during opt-in
- WebView LAN resource access
- OkHttp / Cronet LAN request
- native socket LAN request
- DNS local server port 53
- Output Switcher
- media casting discovery and playback initiation
- Wi-Fi / Ethernet vs cellular / VPN
- `EPERM` / `ECONNABORTED` socket errors
- access restored after permission grant
- access restored after compat flag disable
- user denial / revocation UX
- graceful fallback / feature degradation
- existing user upgrade path
- CI / manual test with local network devices

## Facts / Observations / Hypotheses / Conclusions

### Facts

- 公式 Developer Guidance は 25Q2 Beta 3 以降 build、app install、`RESTRICT_LOCAL_NETWORK` enable、reboot を opt-in 手順としている。
- Android 16 r4 AOSP には `RESTRICT_LOCAL_NETWORK = 365139289L` が存在する。
- Android 16 r4 AOSP の `RESTRICT_LOCAL_NETWORK` は `@EnabledAfter(targetSdkVersion = 36)` であり、targetSdkVersion 36 では default-enabled ではない。
- Current opt-in gate は `isAtLeast25Q2()` と `CompatChanges.isChangeEnabled(RESTRICT_LOCAL_NETWORK, uid)`。
- Current restore access は `NEARBY_WIFI_DEVICES` grant で判定される。
- Android 16 r4 AOSP には future `ACCESS_LOCAL_NETWORK` permission / AppOp がある。

### Observations

- Android 16 OS update だけ、または targetSdkVersion 36 化だけでは、current opt-in testing impact は default で発生しない。
- Reboot guidance は、PermissionMonitor の boot mass update と block map update timing と整合する。
- `NEARBY_WIFI_DEVICES` grant / revoke は permission listener により block map update を起こす。
- NsdManager は current opt-in phase と future enforcement で影響を分ける必要がある。

### Hypotheses

- Compat flag enable 後 reboot が必要なのは、compat state を反映した UID block map 再構築が boot 時 mass update で行われるためである可能性が高い。
- Future enforcement では `ACCESS_LOCAL_NETWORK` が `NEARBY_WIFI_DEVICES` を置き換える可能性が高い。
- Compat flag disable 後の access restore は、block map 再計算 trigger の有無に依存する可能性があり、実機確認が必要。

### Conclusions

- Developer Guidance (Opt-in) は、Android 16 current stage で LAN dependency を検出するための testing workflow である。
- Current impact は `RESTRICT_LOCAL_NETWORK` enabled + reboot + `NEARBY_WIFI_DEVICES` 未許可 + local network traffic で発生し得る。
- Current restore は `NEARBY_WIFI_DEVICES` grant で行われる。
- Android 16 / targetSdkVersion 36 だけでは current opt-in restriction は default-enabled ではない。
- Future enforcement は new permission に移る見込みであり、current testing と future production behavior を混ぜて説明しない。

## Missing Evidence / Follow-up

- Compat flag disable 後に `local_net_blocked_uid_map` が即時更新されるかの実機確認。
- Reboot なしで compat flag enable 後に block map が更新される alternate trigger の有無。
- Future release tag での final targetSdkVersion gate / permission UX。
- NsdManager の future enforcement path。
- Output Switcher exception の complete system-mediated path。
- 25Q4 casting guidance / future APIs。
