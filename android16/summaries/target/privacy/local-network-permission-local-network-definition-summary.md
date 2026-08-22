# Local Network Permission - Local Network Definition summary

## One Page Summary

### 対象

- Android version: Android 16
- From tag: `android-15.0.0_r36`
- To tag: `android-16.0.0_r4`
- Previous targetSdkVersion: 35
- Target targetSdkVersion: 36
- Official documentation URL: https://developer.android.com/about/versions/16/behavior-changes-16#local-network-definition
- Category: Privacy
- Parent section: Local Network Permission
- Report: `android16/behavior-changes/target/privacy/local-network-permission-local-network-definition.md`

### 結論

Local Network Definition は、Local Network Permission の対象になる address / interface の範囲を定義する項目である。Android 16 current stage では opt-in testing feature であり、Android 16 へ OS アップデートしただけ、または targetSdkVersion 36 にしただけで local network access が default 制限される evidence はない。

AOSP Android 16 r4 では、公式文書に列挙された IPv4 ranges、multicast、IPv4 broadcast が local network prefix として定義され、BPF `local_net_access_map` に interface index 付き longest-prefix rule として登録される。IPv6 は prefix length が 0 でない `LinkAddress` を local prefix として扱う。

### Applicability Classification

- Primary classification: `OPT_IN_ONLY`
- Confidence: High

理由:

- 公式文書は current stage を opt-in feature と明記している。
- Android 16 r4 AOSP の `RESTRICT_LOCAL_NETWORK` は Change ID `365139289L`。
- `RESTRICT_LOCAL_NETWORK` は `@EnabledAfter(targetSdkVersion = 36)` で、targetSdkVersion 36 では default-enabled ではない。
- IPv4 / multicast / broadcast definition は強く確認できるが、WWAN / VPN exclusion、Thread 固有 path、multiple-subnets TBD、future permission enforcement は未確定要素が残る。

### Facts

- `IPV4_LOCAL_PREFIXES` は `169.254.0.0/16`、`100.64.0.0/10`、`10.0.0.0/8`、`172.16.0.0/12`、`192.168.0.0/16`。
- `MULTICAST_AND_BROADCAST_PREFIXES` は `224.0.0.0/4`、`ff00::/8`、`255.255.255.255/32`。
- IPv6 は `LinkAddress` の prefix length が 0 でなければ local prefix として扱われる。
- BPF key は interface index、remote IP、protocol、remote port を含む。
- Local DNS server port 53 は allow rule。AOSP r4 では TCP 853 も allow。
- Current opt-in restore access は `NEARBY_WIFI_DEVICES` grant。

### Observations

- Local network definition は address-prefix だけでなく interface にも依存する。
- Current impact は `RESTRICT_LOCAL_NETWORK` enabled、25Q2 相当 build、reboot、permission denied / missing、app UID local traffic の組み合わせで発生する。
- 公式文書の cellular WWAN / VPN exclusion は今回の source pass では explicit gate まで確認できていない。
- Thread stub network と multiple-subnets は追加確認が必要。

### Hypotheses

- Future enforcement では `ACCESS_LOCAL_NETWORK` が `NEARBY_WIFI_DEVICES` を置き換える可能性が高い。
- Cellular / VPN exclusion は network eligibility / interface registration path で担保される可能性がある。
- Thread / Matter 系 network は stacked link / IPv6 prefix path で local network として扱われる可能性が高い。

### 期待挙動

| Scenario | Expected behavior |
|---|---|
| Android 16 / targetSdkVersion 35 / flag disabled | 従来どおり |
| Android 16 / targetSdkVersion 36 / flag disabled | 従来どおり。target 36 だけでは current enforcement なし |
| Android 16 / targetSdkVersion 36 / flag enabled / permission denied | local network prefix 宛 traffic が fail し得る |
| Android 16 / targetSdkVersion 36 / `NEARBY_WIFI_DEVICES` granted | current opt-in phase では access restored |
| Android 15 / targetSdkVersion 36 | Android 15 r36 には同等 BPF infrastructure / compat change を確認できない |
| IPv4 private / CGNAT / link-local | local network prefix |
| IPv4 / IPv6 multicast、IPv4 broadcast | local network address |
| IPv6 link-local / directly-connected prefix | local network prefix |
| Cellular WWAN / VPN | 公式上は除外。AOSP explicit path は追加確認が必要 |
| DNS local server port 53 | exception |
| Output Switcher | 公式上 permission 不要 |

### Developer Action Candidates

- LAN 宛先を prefix ごとに棚卸しする。
- RFC1918 だけでなく CGNAT、link-local、multicast、broadcast、IPv6 link-local / directly-connected、Thread / Matter 系を確認する。
- `RESTRICT_LOCAL_NETWORK` enabled / disabled と `NEARBY_WIFI_DEVICES` grant / deny / revoke を比較する。
- DNS port 53、Output Switcher、direct casting discovery を分けてテストする。
- Future local network runtime permission の deny / revoke に備えた UX と fallback を用意する。

### Test Focus

- Android 16 / targetSdkVersion 35 vs 36
- 25Q2 Beta 3 以降相当 build
- `RESTRICT_LOCAL_NETWORK` enabled / disabled、reboot 有無
- `NEARBY_WIFI_DEVICES` declared / granted / denied / revoked
- Wi-Fi / Ethernet / cellular / VPN
- IPv4 `169.254.0.0/16`、`100.64.0.0/10`、`10.0.0.0/8`、`172.16.0.0/12`、`192.168.0.0/16`
- IPv4 `224.0.0.0/4`、`255.255.255.255`
- IPv6 link-local、directly-connected route、Thread stub network、`ff00::/8`
- DNS local server port 53
- mDNS / SSDP / NsdManager / WebView / native socket / managed socket
- local network address 判定と socket error の対応

### Human Decision Placeholder

- Human decision: 未判断
- Priority: 未判断
- Severity: 未判断
- Release readiness: 未判断
- Customer communication priority: 未判断

## 再検証記録（2026-08-22）

- Android 16 の公式 Behavior Change 一覧と最新通常AOSPタグを再確認した。
- 対応する[主レポート](../../../behavior-changes/target/privacy/local-network-permission-local-network-definition.md)で official section、AOSP project / remote / checkout、解決済み commit、比較 command、dirty risk を再検証した。
- 主レポートの分類、confidence、未確認事項を維持し、実機未実施の項目を Observed 済みへ変更していない。
- 全件の結果は[再検証台帳](../../../analysis/REVALIDATION_2026-08-22.md)を参照する。
