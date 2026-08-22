# Local Network Permission - Impact summary

## One Page Summary

### 対象

- Android version: Android 16
- From tag: `android-15.0.0_r36`
- To tag: `android-16.0.0_r4`
- Previous targetSdkVersion: 35
- Target targetSdkVersion: 36
- Official documentation URL: https://developer.android.com/about/versions/16/behavior-changes-16#impact
- Category: Privacy
- Parent section: Local Network Permission
- Report: `android16/behavior-changes/target/privacy/local-network-permission-impact.md`

### 結論

Local Network Permission の Impact は、Android 16 current stage では opt-in testing impact として扱う。Android 16 / targetSdkVersion 36 だけで local network access が default で制限される evidence はない。

影響が出る current 条件は、25Q2 以降相当 build で `RESTRICT_LOCAL_NETWORK` を app に enable し、`NEARBY_WIFI_DEVICES` が grant されておらず、その app UID が local network traffic を行う場合である。AOSP では BPF packet path が UID / local address / protocol / port を見て drop するため、native / managed sockets、OkHttp、Cronet、WebView など API layer を横断して影響し得る。

### Applicability Classification

- Primary classification: `OPT_IN_ONLY`
- Confidence: High

理由:

- 公式文書は current stage を opt-in feature と明記している。
- Android 16 r4 AOSP の `RESTRICT_LOCAL_NETWORK` は Change ID `365139289L`。
- `RESTRICT_LOCAL_NETWORK` は `@EnabledAfter(targetSdkVersion = 36)` で、targetSdkVersion 36 では default-enabled ではない。
- Future enforcement の infrastructure は確認できるが、final release / permission UX / target gate は未確定。

### Facts

- Current opt-in gate は `isAtLeast25Q2()` と `CompatChanges.isChangeEnabled(RESTRICT_LOCAL_NETWORK, uid)`。
- Current restore access は `NEARBY_WIFI_DEVICES` grant。
- Android 16 r4 には `local_net_access_map` / `local_net_blocked_uid_map` と BPF drop path がある。
- BPF path は TCP / UDP を含む L4 protocol と remote port を抽出する。
- Android 16 r4 には future `ACCESS_LOCAL_NETWORK` dangerous permission / AppOp がある。
- DNS local server port 53 は exception。AOSP では TCP 853 も allow rule がある。

### Observations

- Android 16 OS update だけ、または targetSdkVersion 36 化だけでは、current impact は default で発生しない。
- raw sockets / native sockets / managed sockets / OkHttp / Cronet / WebView は、host app UID の packet として同じ BPF gate に乗り得る。
- NsdManager は Impact section では影響対象だが、current opt-in guidance では app process 外 operation は影響されないため、future enforcement と分けて説明する。
- Output Switcher は公式文書上 exception。Direct media casting discovery は影響候補。

### Hypotheses

- Future enforcement では `ACCESS_LOCAL_NETWORK` が `NEARBY_WIFI_DEVICES` を置き換える可能性が高い。
- Future enforcement では NsdManager など framework-level local network operations にも permission gate が広がる可能性がある。
- Casting は Output Switcher / future APIs と direct LAN discovery で permission need が分かれる可能性がある。

### 期待挙動

| Scenario | Expected behavior |
|---|---|
| Android 16 / targetSdkVersion 35 / flag disabled | 従来どおり |
| Android 16 / targetSdkVersion 36 / flag disabled | 従来どおり。target 36 固有の current enforcement はない |
| Android 16 / flag enabled / NEARBY_WIFI_DEVICES granted | local network access restored |
| Android 16 / flag enabled / NEARBY_WIFI_DEVICES denied | LAN traffic が fail し得る |
| Outbound / inbound TCP LAN | opt-in + permission denied なら fail し得る |
| UDP unicast / multicast / broadcast | opt-in + permission denied なら fail し得る |
| Internet request | local address でなければ影響しない想定 |
| DNS local server port 53 | exception |
| NsdManager during opt-in | 公式 guidance 上、app process 外 operation は影響なし |
| WebView / OkHttp / Cronet / native socket | host app UID の local traffic として影響し得る |
| Output Switcher | 公式文書上 permission 不要 |
| Future enforcement / permission denied | outbound LAN / inbound LAN は fail、Internet は work |

### Developer Action Candidates

- LAN access 箇所を棚卸しする。
- mDNS / SSDP / NSD / `.local` / LAN IP / UDP multicast / broadcast / TCP server / WebView LAN access を確認する。
- Android 16 25Q2 Beta 3 以降相当 build で `RESTRICT_LOCAL_NETWORK` を enable してテストする。
- `NEARBY_WIFI_DEVICES` grant / deny / revoke の差を確認する。
- `EPERM` / `ECONNABORTED` / connection failure を graceful に扱う。
- Future `ACCESS_LOCAL_NETWORK` または new Nearby devices permission の request / denial / revocation UX に備える。

### Test Focus

- Android 16 / targetSdkVersion 35 vs 36
- `RESTRICT_LOCAL_NETWORK` enabled / disabled
- reboot 有無
- `NEARBY_WIFI_DEVICES` declared / granted / denied / revoked
- outbound / inbound TCP LAN
- UDP unicast / multicast / broadcast
- mDNS / SSDP / `.local`
- NsdManager opt-in phase
- WebView / OkHttp / Cronet / native socket
- DNS port 53 / 853
- Output Switcher / media casting
- Wi-Fi / Ethernet vs cellular / VPN
- user denial / revocation UX

### Human Decision Placeholder

- Human decision: 未判断
- Priority: 未判断
- Severity: 未判断
- Release readiness: 未判断
- Customer communication priority: 未判断

## 再検証記録（2026-08-22）

- Android 16 の公式 Behavior Change 一覧と最新通常AOSPタグを再確認した。
- 対応する[主レポート](../../../behavior-changes/target/privacy/local-network-permission-impact.md)で official section、AOSP project / remote / checkout、解決済み commit、比較 command、dirty risk を再検証した。
- 主レポートの分類、confidence、未確認事項を維持し、実機未実施の項目を Observed 済みへ変更していない。
- 全件の結果は[再検証台帳](../../../analysis/REVALIDATION_2026-08-22.md)を参照する。
