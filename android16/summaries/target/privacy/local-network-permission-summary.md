# Local Network Permission summary

## One Page Summary

### 対象

- Android version: Android 16
- From tag: `android-15.0.0_r36`
- To tag: `android-16.0.0_r4`
- Previous targetSdkVersion: 35
- Target targetSdkVersion: 36
- Official documentation URL: https://developer.android.com/about/versions/16/behavior-changes-16#local-network-permission
- Category: Privacy
- Report: `android16/behavior-changes/target/privacy/local-network-permission.md`

### 結論

Android 16 の Local Network Permission は、現時点では default-on の targetSdkVersion 36 behavior change ではなく、`RESTRICT_LOCAL_NETWORK` compat flag による opt-in testing behavior として扱うのが妥当である。

Android 16 AOSP には `ACCESS_LOCAL_NETWORK` permission / AppOp / BPF maps / packet drop path が追加されており、将来の runtime permission enforcement の基盤は存在する。ただし Android 16 current opt-in guidance では、`NEARBY_WIFI_DEVICES` grant で local network access を restore する。

### Applicability Classification

- Primary classification: `OPT_IN_ONLY`
- Confidence: High

理由:

- `RESTRICT_LOCAL_NETWORK` は Android 16 tag で Change ID `365139289L` として存在し、`@EnabledAfter(targetSdkVersion = 36)` が付く。
- targetSdkVersion 36 は default-enable 条件ではない。
- current stage は opt-in feature で、future enforcement は別 release として公式文書に記載されている。
- `OPT_IN_ONLY` は current opt-in testing behavior を表す分類である。

### Facts

- 公式文書は current stage を opt-in feature と説明する。
- opt-in 手順は 25Q2 Beta 3 以降 build、`adb shell am compat enable RESTRICT_LOCAL_NETWORK <package>`、reboot。
- Android 16 `ConnectivityCompatChanges.RESTRICT_LOCAL_NETWORK` は `365139289L` / `@EnabledAfter(targetSdkVersion = 36)`。targetSdkVersion 36 では default-enabled ではない。
- Android 16 では `ACCESS_LOCAL_NETWORK` が flagged dangerous permission として追加されている。
- current opt-in phase の restore access は `NEARBY_WIFI_DEVICES` grant を確認する実装。
- BPF `local_net_access_map` / `local_net_blocked_uid_map` と packet drop path が Android 16 に追加されている。
- Android 15 tag には `RESTRICT_LOCAL_NETWORK` と BPF local network block infrastructure は確認できない。

### Observations

- Android 16 OS update だけ、または targetSdkVersion 36 化だけでは、current opt-in restriction は有効化されない。
- 影響は `RESTRICT_LOCAL_NETWORK` を package に enable し、local network access を行い、permission がない場合に発生する。
- native / managed sockets、OkHttp、Cronet、WebView などは app UID packet として BPF restriction の影響を受け得る。
- DNS local server port 53 は公式例外。AOSP では local DNS port 53 に加えて TCP 853 も allow rule が追加される。

### Hypotheses

- future release では `ACCESS_LOCAL_NETWORK` が `NEARBY_WIFI_DEVICES` を置き換え、targetSdkVersion 37 以降などで default enforcement される可能性が高い。
- BPF maps は future runtime permission grant state を network stack に渡す中核 infrastructure になる。

### 期待挙動

| Scenario | Expected behavior |
|---|---|
| Android 16 / targetSdkVersion 35 / flag disabled | 従来どおり |
| Android 16 / targetSdkVersion 36 / flag disabled | 従来どおり。target 36 固有ではない |
| Android 16 / flag enabled / NEARBY_WIFI_DEVICES granted | local network access restored |
| Android 16 / flag enabled / NEARBY_WIFI_DEVICES denied | LAN traffic が fail し得る |
| Android 15 / targetSdkVersion 36 | Android 16 の LNP BPF infrastructure は未確認 |
| Future enforcement / permission granted | outbound LAN / inbound LAN / Internet が work |
| Future enforcement / permission not granted | outbound LAN / inbound LAN は fail、Internet は work |

### Developer Action Candidates

- LAN access 箇所を棚卸しする。
- mDNS / SSDP / NSD / `.local` / LAN IP / UDP multicast / broadcast / TCP server / WebView LAN access を確認する。
- Android 16 25Q2 Beta 3 以降 build で `RESTRICT_LOCAL_NETWORK` を enable してテストする。
- `NEARBY_WIFI_DEVICES` declared / granted / denied / revoked の差を確認する。
- `EPERM` / `ECONNABORTED` を graceful に扱う。
- future `ACCESS_LOCAL_NETWORK` runtime permission UX に備える。

### Test Focus

- Android 16 / targetSdkVersion 35 vs 36
- `RESTRICT_LOCAL_NETWORK` enabled / disabled
- reboot 有無
- `NEARBY_WIFI_DEVICES` grant state
- outbound / inbound TCP LAN
- UDP unicast / multicast / broadcast
- mDNS / SSDP / `.local`
- NsdManager opt-in phase
- WebView / OkHttp / Cronet / native socket
- DNS port 53 / 853
- Output Switcher / media casting
- Wi-Fi / Ethernet vs cellular / VPN

### Human Decision Placeholder

- Human decision: 未判断
- Priority: 未判断
- Severity: 未判断
- Release readiness: 未判断
- Customer communication priority: 未判断
