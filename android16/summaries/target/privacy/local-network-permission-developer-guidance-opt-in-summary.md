# Local Network Permission - Developer Guidance (Opt-in) summary

## One Page Summary

### 対象

- Android version: Android 16
- From tag: `android-15.0.0_r36`
- To tag: `android-16.0.0_r4`
- Previous targetSdkVersion: 35
- Target targetSdkVersion: 36
- Official documentation URL: https://developer.android.com/about/versions/16/behavior-changes-16#developer-guidance-opt-in
- Category: Privacy
- Parent section: Local Network Permission
- Report: `android16/behavior-changes/target/privacy/local-network-permission-developer-guidance-opt-in.md`

### 結論

Developer Guidance (Opt-in) は、Android 16 current stage で Local Network Permission の将来 enforcement に備えるための testing workflow である。Android 16 / targetSdkVersion 36 だけで local network restriction が default で有効になるわけではない。

Current testing impact は、25Q2 以降相当 build で app を install し、`adb shell am compat enable RESTRICT_LOCAL_NETWORK <package>` を実行し、reboot した後、`NEARBY_WIFI_DEVICES` が未許可の app が local network traffic を行う場合に発生し得る。Current restore access は `NEARBY_WIFI_DEVICES` grant で行われる。

### Applicability Classification

- Primary classification: `UNKNOWN_NEEDS_MORE_EVIDENCE`
- Confidence: Medium

理由:

- 公式文書は current opt-in testing 手順を説明している。
- Android 16 r4 AOSP の `RESTRICT_LOCAL_NETWORK` は Change ID `365139289L`。
- `RESTRICT_LOCAL_NETWORK` は `@EnabledAfter(targetSdkVersion = 36)` で、targetSdkVersion 36 では default-enabled ではない。
- Future enforcement の `ACCESS_LOCAL_NETWORK` infrastructure はあるが、final release / permission UX / target gate は未確定。

### Facts

- Opt-in 手順は 25Q2 Beta 3 以降 build、app install、`RESTRICT_LOCAL_NETWORK` enable、reboot。
- Current opt-in gate は `isAtLeast25Q2()` と `CompatChanges.isChangeEnabled(RESTRICT_LOCAL_NETWORK, uid)`。
- `PermissionMonitor` は boot 時 mass update、package add/remove、permission changes で block map を更新する。
- Current restore access は `NEARBY_WIFI_DEVICES` grant。
- Android 16 r4 には future `ACCESS_LOCAL_NETWORK` dangerous permission / AppOp がある。
- BPF packet path は blocked UID の local network packet を drop し得る。

### Observations

- Android 16 OS update だけ、または targetSdkVersion 36 化だけでは current testing impact は発生しない。
- Reboot guidance は、boot 時 mass update で compat state を反映した block map を構築する実装と整合する。
- `NEARBY_WIFI_DEVICES` grant / revoke は permission listener によって block map update を起こす。
- NsdManager など app process 外 operation は current opt-in phase では影響されないと公式文書に明記されている。
- Compat flag disable 後の即時復旧は block map 再計算 timing の実機確認が必要。

### Hypotheses

- Compat flag enable 後 reboot が必要なのは、compat state を反映した UID block map 再構築が boot 時に行われるためである可能性が高い。
- Future enforcement では `ACCESS_LOCAL_NETWORK` が `NEARBY_WIFI_DEVICES` を置き換える可能性が高い。
- Current opt-in で NsdManager が fail しなくても、future enforcement では permission guard 対象になる可能性がある。

### 期待挙動

| Scenario | Expected behavior |
|---|---|
| Android 16 / targetSdkVersion 35 / flag disabled | 従来どおり |
| Android 16 / targetSdkVersion 36 / flag disabled | 従来どおり。target 36 固有の current enforcement はない |
| Android 16 / flag enabled before reboot | block map 未同期の可能性。公式手順では reboot required |
| Android 16 / flag enabled after reboot / NEARBY_WIFI_DEVICES denied | LAN traffic が fail し得る |
| Android 16 / flag enabled after reboot / NEARBY_WIFI_DEVICES granted | local network access restored |
| Android 16 / flag disabled after toggle-off | gate は disabled。既存 block map の即時更新は実機確認が必要 |
| NsdManager during opt-in | 公式 guidance 上、app process 外 operation は影響なし |
| Future enforcement / new permission denied | outbound LAN / inbound LAN は fail、Internet は work |

### Developer Action Candidates

- 公式手順どおり、app install、compat flag enable、reboot の順で testing する。
- `NEARBY_WIFI_DEVICES` declared / granted / denied / revoked の差を確認する。
- Compat flag disable 後の挙動は reboot / app reinstall / permission change と組み合わせて確認する。
- LAN dependency を mDNS / SSDP / NSD / `.local` / LAN IP / UDP multicast / broadcast / TCP server / WebView LAN access で棚卸しする。
- Future `ACCESS_LOCAL_NETWORK` または new Nearby devices permission の denied / revoked UX に備える。

### Test Focus

- 25Q2 Beta 3 以降の build
- app install before compat flag enable
- `RESTRICT_LOCAL_NETWORK` enabled / disabled
- reboot 有無
- `NEARBY_WIFI_DEVICES` declared / granted / denied / revoked
- Settings > Apps > Permissions > Nearby devices > Allow flow
- outbound / inbound TCP LAN
- UDP unicast / multicast / broadcast
- mDNS / SSDP / `.local`
- NsdManager during opt-in
- WebView / OkHttp / Cronet / native socket
- DNS port 53 / 853
- access restored after permission grant
- access restored after compat flag disable

### Human Decision Placeholder

- Human decision: 未判断
- Priority: 未判断
- Severity: 未判断
- Release readiness: 未判断
- Customer communication priority: 未判断
