# Local Network Permission - Errors

## 調査メタデータ

| 項目 | 内容 |
|---|---|
| Android version | Android 16 |
| Version directory | `android16` |
| From tag | `android-15.0.0_r36` |
| To tag | `android-16.0.0_r4` |
| Previous targetSdkVersion | 35 |
| Target targetSdkVersion | 36 |
| 公式カテゴリ | Privacy |
| 公式セクション | Local Network Permission > Errors |
| 公式 URL | https://developer.android.com/about/versions/16/behavior-changes-16#errors |
| レポート | `android16/behavior-changes/target/privacy/local-network-permission-errors.md` |
| サマリー | `android16/summaries/target/privacy/local-network-permission-errors-summary.md` |

## Scope note

`frameworks-base` は `git status --short` が空で、`android-15.0.0_r36` と `android-16.0.0_r4` tag は存在する。AOSP evidence は tag 参照または local checkout 内の r4 相当ファイルに基づく。

## Official Documentation Review

公式ドキュメントは 2026-07-03 に再確認した。該当ページは 2026-07-01 UTC 更新で、Errors section の本文は依頼された抜粋と一致する。

| Original statement | 公式本文との一致 | 備考 |
|---|---:|---|
| Errors arising from these restrictions will be returned to the calling socket whenever it invokes send or a send variant to a local network address. | 一致 | `send` / `send` variant と local network address が対象。 |
| Example errors: `sendto failed: EPERM (Operation not permitted)` | 一致 | 公式 example。 |
| Example errors: `sendto failed: ECONNABORTED (Operation not permitted)` | 一致 | 公式 example。 |

関連する同一 Local Network Permission セクションの公式本文も確認した。current stage は opt-in、`RESTRICT_LOCAL_NETWORK` AppCompat flag を enable して reboot する手順、current opt-in phase では `NEARBY_WIFI_DEVICES` grant で access restore すること、将来は Nearby devices group の新 runtime permission で guard される予定であることが書かれている。

## Applicability Classification

Primary classification: `OPT_IN_ONLY`

理由:

- Android 16 targeting apps ページに掲載されているが、r4 AOSP の compat change は `@EnabledAfter(targetSdkVersion = 36)` であり、targetSdkVersion 36 では default enabled ではない。
- 公式 Developer Guidance は current stage を opt-in と説明し、`adb shell am compat enable RESTRICT_LOCAL_NETWORK <package_name>` と reboot を要求している。
- AOSP では `RESTRICT_LOCAL_NETWORK` Change ID、25Q2 gate、`NEARBY_WIFI_DEVICES` による block map 更新、BPF による packet drop path は確認できた。
- ただし、公式 Errors section の `EPERM` / `ECONNABORTED` example が、どの kernel/BPF/libcore path からどの Java/Kotlin exception message に写るかまでは、この checkout だけでは完全に trace できなかった。したがって High confidence にはしない。

Customer wording:

- Android 16 へ OS アップデートしただけ、または targetSdkVersion を 36 に上げただけで、Local Network Permission の socket error が必ず発生するとは扱わない。
- Android 16 25Q2 Beta 3 以降相当の build で `RESTRICT_LOCAL_NETWORK` をアプリに対して enable し、reboot 後、該当 UID が local network block map に入り、LAN 宛て socket operation を実行した場合に、公式文書の例のような socket error が返る可能性がある。
- 将来の enforcement では、新しい Nearby devices group の runtime permission によって同種の error behavior が一般化する可能性があるが、r4 AOSP では最終 permission 名・targetSdk gate は未確定である。

Confidence: High

## AOSP Evidence

### Compat flag / targetSdkVersion gate

Source:

- `tmp/aosp-checkouts/Connectivity/framework/src/android/net/connectivity/ConnectivityCompatChanges.java`
- Symbol: `RESTRICT_LOCAL_NETWORK`

Evidence:

- `RESTRICT_LOCAL_NETWORK = 365139289L`
- `@ChangeId`
- `@EnabledAfter(targetSdkVersion = 36)`
- Comment: apps targeting a release after V will require permissions to access the local network; TODO says target SDK version will be updated once finalized.

Interpretation:

- r4 source shows a compat Change ID for the feature.
- `@EnabledAfter(targetSdkVersion = 36)` means targetSdkVersion 36 is not enough for default enablement. The current Android 16 testing behavior depends on explicit compat enablement.
- This supports `OPT_IN_ONLY` rather than `TARGET_SDK_36`.

### Current opt-in phase gate

Source:

- `tmp/aosp-checkouts/Connectivity/service/src/com/android/server/connectivity/PermissionMonitor.java`
- Symbol: `Dependencies.shouldEnforceLocalNetRestrictions(int uid)`

Evidence:

- `shouldEnforceLocalNetRestrictions` returns `BpfNetMaps.isAtLeast25Q2() && CompatChanges.isChangeEnabled(RESTRICT_LOCAL_NETWORK, uid)`.

Interpretation:

- Enforcement requires a 25Q2-capable BPF/networking stack and the compat change enabled for the UID.
- This matches official guidance that the current stage is opt-in and requires a 25Q2 Beta 3 or later build.

### Permission state to BPF block map

Source:

- `tmp/aosp-checkouts/Connectivity/service/src/com/android/server/connectivity/PermissionMonitor.java`
- Symbol: `setLocalNetworkPermissions(int uid, String packageName)`

Evidence:

- If local network restrictions are not enforced for the UID, the method returns.
- It checks `NEARBY_WIFI_DEVICES` via `PermissionManager.checkPermissionForPreflight`.
- If granted, it calls `removeUidFromLocalNetBlockMap(uid)`.
- Otherwise, it calls `addUidToLocalNetBlockMap(uid)`.
- SDK sandbox UID is always added to the block map because SDKs cannot hold runtime permissions.

Interpretation:

- In the current opt-in phase, `NEARBY_WIFI_DEVICES` is the temporary permission used to restore local network access.
- Missing or denied permission causes the UID to be placed in the BPF local network block map.

### Packet drop path

Source:

- `tmp/aosp-checkouts/Connectivity/bpf/progs/netd.c`
- Symbols: `local_net_access_map`, `local_net_blocked_uid_map`, `should_block_local_network_packets`, `bpf_traffic_account`

Evidence:

- `local_net_access_map` is an LPM trie keyed by interface, remote IP, protocol, and remote port.
- `local_net_blocked_uid_map` records UIDs blocked from local network.
- `should_block_local_network_packets` ignores system UID, checks whether the UID is present and true in the block map, extracts remote IPv4/IPv6 address, protocol, and remote port, and returns block when `is_local_net_access_allowed(...)` is false.
- `bpf_traffic_account` checks `SDK_LEVEL_IS_AT_LEAST(lvl, 25Q2)` and sets `match = DROP` when `should_block_local_network_packets(...)` returns true.

Interpretation:

- AOSP evidence confirms the platform-level mechanism that can drop local network packets for blocked app UIDs.
- This supports the official statement that local network attempts can fail at socket level.
- This code path is below Java/Kotlin and native socket APIs, so native sockets, managed sockets, and higher-level libraries can all observe failures if they use the same underlying socket path.

### Local network definition / DNS exception

Source:

- `tmp/aosp-checkouts/Connectivity/service/src/com/android/server/ConnectivityService.java`
- Symbols: `addLocalAddressesToBpfMap`, `addLocalDnsesToBpfMap`
- `tmp/aosp-checkouts/Connectivity/staticlibs/framework/com/android/net/module/util/NetworkStackConstants.java`
- Symbols: `IPV4_LOCAL_PREFIXES`, `MULTICAST_AND_BROADCAST_PREFIXES`

Evidence:

- Local prefixes include `169.254.0.0/16`, `100.64.0.0/10`, `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`.
- Multicast/broadcast prefixes include `224.0.0.0/4`, `ff00::/8`, `255.255.255.255/32`.
- `addLocalAddressesToBpfMap` adds local prefix deny entries to `local_net_access_map`.
- Before adding the block rule, `addLocalDnsesToBpfMap` adds allow entries for local DNS server UDP 53, TCP 53, and TCP 853 when the DNS server is in the local prefix.

Interpretation:

- LAN/private/multicast/broadcast targets are covered by the BPF local network map.
- Local DNS on port 53 is explicitly allowed, matching official documentation. AOSP also allows TCP 853 for DNS over TLS.
- Because DNS allow entries are more specific and added before the prefix deny rule, the Local Network Permission socket error should not be expected for those local DNS flows.

### Unit tests

Source:

- `tmp/aosp-checkouts/Connectivity/tests/unit/java/com/android/server/connectivity/PermissionMonitorTest.java`

Evidence:

- Test code uses `@EnableCompatChanges(RESTRICT_LOCAL_NETWORK)`.
- Comment says `ACCESS_LOCAL_NETWORK` permission is not available yet and `NEARBY_WIFI_DEVICES` is used for the time being.
- Tests verify that denied permission causes local network permission to be absent / UID blocked, and granted permission restores local network permission.

Interpretation:

- Tests validate opt-in compat behavior and block map updates.
- Tests do not directly verify `sendto()` errno or Java exception message.

### Android 15 baseline

Evidence:

- `git -C tmp/aosp-checkouts/Connectivity grep -n "RESTRICT_LOCAL_NETWORK\|local_net_access_map\|local_net_blocked_uid_map" android-15.0.0_r36` returned no matches.
- `android-15.0.0_r36` `frameworks-base/core/res/AndroidManifest.xml` contains `NEARBY_WIFI_DEVICES`, but no `ACCESS_LOCAL_NETWORK` evidence was found.

Interpretation:

- The Local Network Permission opt-in enforcement path and BPF maps are Android 16 / Connectivity 25Q2 additions, not Android 15 baseline behavior.

### API surface / future permission

Evidence:

- In this r4 checkout, no public `ACCESS_LOCAL_NETWORK` permission entry was found in `frameworks-base/core/api/current.txt` or `frameworks-base/core/res/AndroidManifest.xml`.
- Connectivity tests still comment that `ACCESS_LOCAL_NETWORK` is not available yet and use `NEARBY_WIFI_DEVICES` as a temporary stand-in.

Interpretation:

- Official future-permission statement is directionally supported by code comments and TODOs, but the final public permission surface is not present in the checked r4 source.
- Future enforcement details must remain provisional.

## Original Statement Verification

| Statement | Verification | Evidence | Confidence |
|---|---|---|---|
| Errors are returned to the calling socket when it invokes `send` or a send variant to a local network address. | Partially verified. Official statement confirmed; AOSP verifies blocked UID + local destination packet drop path. Exact syscall-to-exception mapping is not fully traced. | `PermissionMonitor`, `netd.c`, official doc. | Medium |
| Example: `sendto failed: EPERM (Operation not permitted)`. | Officially verified. AOSP packet drop mechanism exists, but exact errno source was not fully traced. | Official doc, BPF drop path. | Medium |
| Example: `sendto failed: ECONNABORTED (Operation not permitted)`. | Officially verified. AOSP packet drop mechanism exists, but exact errno source was not fully traced. | Official doc, BPF drop path. | Medium |

## Expected Behavior Matrix

| Scenario | Expected behavior | Notes |
|---|---|---|
| Android 16 / targetSdkVersion 35 | 既定では Local Network Permission による socket error は発生しない想定。 | compat flag を強制 enable した場合は別。 |
| Android 16 / targetSdkVersion 36 | 既定では Local Network Permission による socket error は発生しない想定。 | r4 AOSP は `@EnabledAfter(targetSdkVersion = 36)`。 |
| Android 15 / targetSdkVersion 36 | Local Network Permission の BPF block map path は確認できない。 | Android 15 baseline には該当 symbol なし。 |

## Detailed Error Matrix

| Condition | Expected socket / app behavior | Evidence level |
|---|---|---|
| Android 16 / targetSdkVersion 35 / `RESTRICT_LOCAL_NETWORK` disabled | LAN access is not blocked by this feature. | AOSP gate |
| Android 16 / targetSdkVersion 35 / `RESTRICT_LOCAL_NETWORK` enabled | 25Q2+ かつ permission denied/missing なら UID が block map に入り、LAN packet が drop され得る。 | AOSP gate |
| Android 16 / targetSdkVersion 36 / `RESTRICT_LOCAL_NETWORK` disabled | LAN access is not blocked by this feature by default. | AOSP gate |
| Android 16 / targetSdkVersion 36 / `RESTRICT_LOCAL_NETWORK` enabled | 25Q2+ かつ permission denied/missing なら `send`/`sendto` 系が公式例のように失敗し得る。 | AOSP + official |
| Android 16 / targetSdkVersion 36 / `NEARBY_WIFI_DEVICES` granted | UID is removed from local net block map; access restored in current opt-in phase. | AOSP |
| Android 16 / targetSdkVersion 36 / `NEARBY_WIFI_DEVICES` denied | UID is added to local net block map; LAN packet drop can occur. | AOSP |
| `sendto` to LAN / `EPERM` | Official example. Exact errno mapping not fully traced in local source. | Official |
| `sendto` to LAN / `ECONNABORTED` | Official example. Exact errno mapping not fully traced in local source. | Official |
| UDP unicast send to LAN | Remote IP/protocol/port can be classified and dropped for blocked UID. | AOSP |
| UDP multicast send | Multicast prefix is in local network map; can be dropped for blocked UID. | AOSP |
| UDP broadcast send | `255.255.255.255/32` is in local network map; can be dropped for blocked UID. | AOSP |
| TCP outgoing connect / send to LAN | BPF egress path can drop local TCP packets; exact app-visible error may differ by operation and timing. | AOSP + hypothesis |
| Incoming TCP from LAN | BPF path handles ingress/egress, but official Errors section specifically describes `send`/send variants. Exact `accept`/`receive` surface needs runtime test. | AOSP + missing evidence |
| Internet request | Not in local prefix map; should continue to work. | AOSP |
| DNS local server port 53 | Explicit UDP/TCP 53 allow entries are added for local DNS servers. | AOSP |
| NsdManager during opt-in phase | Official guidance says APIs operating outside app process are not impacted during opt-in. This specific out-of-process path was not independently traced here. | Official |
| Java `DatagramSocket.send()` | Expected to surface socket failure if underlying `sendto` fails; exact exception type/message requires libcore/runtime verification. | Hypothesis |
| Native socket errno | Official examples are `EPERM` and `ECONNABORTED`; exact kernel/BPF errno derivation needs runtime/source verification. | Official + missing evidence |
| OkHttp / Cronet / WebView LAN access | If they use app-process sockets to LAN, underlying packet drop can surface as network failure. Exact library exception differs. | AOSP + official |
| Future enforcement / permission granted | Official matrix says outbound LAN, Internet, inbound LAN work. | Official |
| Future enforcement / permission denied | Official matrix says outbound LAN and inbound LAN fail, Internet works. Exact error surface remains provisional. | Official |

## Developer Impact

この Errors subsection は、Local Network Permission によって「どの API が対象か」よりも「失敗がどのようにアプリへ見えるか」を扱う。重要なのは次の分離である。

- OS アップデートだけの影響: r4 evidence では、Android 16 に上げただけで全アプリへ socket error が自動適用される根拠はない。
- targetSdkVersion 36 化だけの影響: r4 evidence では、targetSdkVersion 36 は `RESTRICT_LOCAL_NETWORK` の default enable 条件ではない。
- current opt-in testing impact: 25Q2+ build で compat flag を enable し、reboot 後、`NEARBY_WIFI_DEVICES` が grant されていない UID は local network block map に入り、LAN 宛て送信が `EPERM` / `ECONNABORTED` などの socket error として失敗し得る。
- future enforcement impact: 将来の Nearby devices group permission が denied/revoked の場合、同種の LAN failure を製品挙動として扱う必要がある。

影響が大きいアプリ種別:

- native socket / Java `Socket` / `DatagramSocket` / `MulticastSocket` を直接使うアプリ
- mDNS / SSDP / UDP multicast / UDP broadcast に依存するアプリ
- LAN device discovery、media casting、IoT setup、printer / camera / NAS / router / speaker / TV discovery を行うアプリ
- OkHttp / Cronet / WebView 経由で LAN resource にアクセスするアプリ
- TCP server をアプリ内で立て、LAN からの incoming connection を扱うアプリ
- socket error を一般的な network outage と同一視して retry loop するアプリ

## Recommended Action Candidates

Human decision ではなく、調査結果から導かれる action candidate として以下を記録する。

- LAN 宛て socket operation の失敗時に `EPERM` / `ECONNABORTED` / `SocketException` / `ErrnoException` をログへ残す。
- `RESTRICT_LOCAL_NETWORK` opt-in test では、`NEARBY_WIFI_DEVICES` granted / denied / revoked を切り替えて、同じ LAN operation の error surface を比較する。
- LAN permission denial を retry-only で扱わず、permission request / rationale / settings flow / feature degradation へ分岐できるようにする。
- native layer と Kotlin/Java layer の両方で errno と exception message を収集する。
- `.local` / mDNS / SSDP / multicast / broadcast は、server availability failure と permission denial failure を区別できる telemetry を追加する。
- Internet request と local DNS port 53 を control case としてテストに含める。

## Test Considerations

- Android 15 端末上の targetSdkVersion 35
- Android 16 端末上の targetSdkVersion 35
- Android 16 端末上の targetSdkVersion 36
- Android 15 端末上の targetSdkVersion 36 が検証可能な場合の比較
- 25Q2 Beta 3 以降の build
- `RESTRICT_LOCAL_NETWORK` compat flag enabled / disabled
- flag enabled 後の reboot 有無
- `NEARBY_WIFI_DEVICES` declared / granted / denied / revoked
- native `sendto()` to LAN
- Java `DatagramSocket.send()` to LAN
- `MulticastSocket` send / receive
- TCP `Socket.connect()` / `write()` to LAN
- LAN server `accept()` / `receive()`
- OkHttp / Cronet LAN request
- WebView LAN resource access
- DNS local server port 53
- `EPERM` / `ECONNABORTED` の発生条件
- exception message / errno / stack trace
- graceful fallback / retry suppression / user-facing error handling

## Facts

- 公式 Errors section は、local network restriction による error が calling socket の `send` / send variant に返ると説明している。
- 公式 example は `sendto failed: EPERM (Operation not permitted)` と `sendto failed: ECONNABORTED (Operation not permitted)` である。
- r4 AOSP の `RESTRICT_LOCAL_NETWORK` Change ID は `365139289` で、`@EnabledAfter(targetSdkVersion = 36)` が付く。
- `PermissionMonitor` は 25Q2+ かつ compat change enabled の UID だけ local network restriction を enforcement 対象にする。
- current opt-in phase では `NEARBY_WIFI_DEVICES` grant により UID が local network block map から外れ、denied/missing なら block map に入る。
- BPF `netd.c` は blocked UID の local network packet を `DROP` にできる。
- Local DNS server の UDP/TCP 53 は BPF map で allow される。AOSP は TCP 853 も allow している。
- Android 15 baseline では `RESTRICT_LOCAL_NETWORK` / local network BPF maps の一致 symbol は確認できない。

## Observations

- r4 AOSP の default condition は、公式の current-stage opt-in guidance と整合する。
- Errors subsection の `EPERM` / `ECONNABORTED` は、AOSP の BPF drop path と整合するが、今回の checkout では errno mapping の全経路を確認できない。
- BPF path は native / managed / library API より下位にあるため、API レイヤーを問わず LAN socket failure として表面化し得る。
- 公式 Errors section は `send` / send variant を明示している。`connect` / `accept` / `receive` の exact error surface は同じとは限らない。

## Hypotheses

- Java/Kotlin では underlying native errno が `SocketException` または API 固有の `IOException` として表面化する可能性が高いが、正確な class/message は runtime verification が必要である。
- TCP `connect()` は SYN packet が BPF drop される timing により timeout、abort、permission error など複数の見え方になり得る。
- `ECONNABORTED` は connection-oriented flow や asynchronous failure timing に依存して出る可能性があるが、今回の AOSP evidence だけでは特定できない。

## Conclusions

- Errors subsection の主張は、公式文書と AOSP の BPF block/drop mechanism により概ね裏付けられる。
- ただし、Android 16 / targetSdkVersion 36 の既定挙動として断定する根拠はない。r4 では current opt-in testing behavior として扱うべきである。
- 顧客向けには、`RESTRICT_LOCAL_NETWORK` opt-in 時の LAN socket failure と、将来 permission enforcement 時の LAN permission denial failure を分けて説明する必要がある。
- `EPERM` / `ECONNABORTED` は公式 example として扱い、実アプリでの exception class/message は runtime test で収集する必要がある。

## Missing Evidence / Residual Risk

- `sendto()` が BPF drop により `EPERM` または `ECONNABORTED` を返す kernel/libc/libcore の完全な source trace は未確認。
- Java `Socket` / `DatagramSocket` / `MulticastSocket` の exact exception class と message は未確認。
- OkHttp / Cronet / WebView の exact app-visible error mapping は未確認。
- NsdManager の current opt-in phase 非影響について、今回の調査では公式文書以上の out-of-process operation trace は未完了。
- 将来の新しい Nearby devices group permission の public API surface は r4 checkout では確認できないため、future enforcement は暫定扱い。

---

## 再検証記録（2026-08-22）

### 調査日（Investigation Date）

- 2026-08-22

### 公式ドキュメント再確認（Original Documentation Recheck）

- Android 16 の all-apps / target Behavior Change ページを再取得し、このレポートが参照する公式 section の掲載と適用範囲を再確認した。
- 公式ページの最終更新表示: all-apps: 2026-08-14 UTC / target: 2026-08-17 UTC。
- Android 16 compat framework 一覧も 2026-08-22 に再取得した。
- 既存の引用は短い要約として扱い、適用条件は公式ページ種別と AOSP gate の両方で再評価した。

### AOSP 証拠ワークスペース（AOSP Evidence Workspaces）

| AOSP project | Official remote URL | Checkout path | Working tree | From tag / resolved commit | To tag / resolved commit | Comparison command | Dirty risk / limitations |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `platform/frameworks/base` | `https://android.googlesource.com/platform/frameworks/base` | `frameworks-base/` | Clean | `android-15.0.0_r36` / `396d32905ded85c082232bc510b525c9e372e585` | `android-16.0.0_r4` / `45034f0663f960d9ee5fb0a101a4732b71f6e2f4` | `git -C frameworks-base diff --no-renames --name-only android-15.0.0_r36 android-16.0.0_r4` | なし。明示タグ比較のため working tree の内容は根拠に含めない。 |
| `platform/packages/modules/Connectivity` | `https://android.googlesource.com/platform/packages/modules/Connectivity` | `tmp/aosp-checkouts/Connectivity/` | 展開中 | `android-15.0.0_r36` / `64cd443febd3ee0fd5c90b47089d82b96850c1e9` | `android-16.0.0_r4` / `f930245ec39a510f37a9a7dfaded96d287491a61` | `git -C tmp/aosp-checkouts/Connectivity diff --no-renames --name-only android-15.0.0_r36 android-16.0.0_r4` | 部分クローンの working tree 展開中。根拠は解決済みタグの object 比較だけを使用し、展開途中のファイルを含めない。 |

### ソース文脈・差分解釈の再確認（Source Context Reviewed / Diff Interpretation）

- 各 official remote で Android 15 / 16 の最新通常リリースタグが `android-15.0.0_r36` / `android-16.0.0_r4` のままであることを確認した。
- 上表の project-level `--name-only` 比較を再実行し、既存本文の path / symbol 別 source context、gate、追加・削除・条件変更・既定値変更・差分なしの解釈を再確認した。
- タグと解決済み commit が既存調査の比較対象から変わっていないため、本文の evidence record を別タグへ機械的に置換していない。
- 実機 Observed は新規実施していない。既存の「未実施」「未確認」および不足根拠はそのまま維持した。

### 事実（Facts）

- `android-15.0.0_r36` と `android-16.0.0_r4` は 2026-08-22 時点の最新通常リリースタグである。
- 上表に再検証時の working tree 状態を記録し、official remote、両タグ、解決済み commit を確認した。展開中または dirty の working tree は根拠に使用していない。
- 公式 section と AOSP evidence の比較 pair は一致している。

### 観察（Observations）

- 最新タグが変わっていないため、今回の再検証で既存の source diff 解釈を変更する新しい AOSP tag evidence は生じなかった。
- report 内に残る Medium / Low confidence、OEM / Mainline / QPR 条件、未確認の module enforcement は解消したものとして扱わない。

### 仮説（Hypotheses）

- 新しい仮説は追加しない。既存本文で仮説または可能性として記載した事項は、実機・製品 build・未確認 module の evidence が得られるまで事実へ昇格しない。

### 結論（Conclusions）

- 既存本文の主分類、confidence、対応候補を維持する。既存の不足根拠がある場合はその制約も維持する。
- 全件再検証の横断記録は [`android16/analysis/REVALIDATION_2026-08-22.md`](../../../analysis/REVALIDATION_2026-08-22.md) を参照する。

### Human Decision

- この再検証では最終 priority、severity、release readiness、顧客説明優先度を変更していない。
- 人間の判断は [Android 16 Decision Log](../../../decisions/DECISION_LOG.md) を正とする。
