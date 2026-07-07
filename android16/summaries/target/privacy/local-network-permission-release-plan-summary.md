# Local Network Permission - Release plan summary

## One Page Summary

### 対象

- Android version: Android 16
- From tag: `android-15.0.0_r36`
- To tag: `android-16.0.0_r4`
- Previous targetSdkVersion: 35
- Target targetSdkVersion: 36
- Official documentation URL: https://developer.android.com/about/versions/16/behavior-changes-16#release-plan
- Category: Privacy
- Parent section: Local Network Permission
- Report: `android16/behavior-changes/target/privacy/local-network-permission-release-plan.md`

### 結論

Local Network Permission の Release plan は、Android 16 / targetSdkVersion 36 で即時 default enforcement される変更ではなく、25Q2 opt-in testing と later Android release enforcement への移行計画として扱う。

Android 16 r4 AOSP には `RESTRICT_LOCAL_NETWORK` compat change、25Q2 BPF enforcement infrastructure、future `ACCESS_LOCAL_NETWORK` permission / AppOp が存在する。ただし `RESTRICT_LOCAL_NETWORK` は `@EnabledAfter(targetSdkVersion = 36)` であり、targetSdkVersion 36 では default-enabled ではない。current stage で影響するのは `RESTRICT_LOCAL_NETWORK` を明示的に enable した app である。

### Applicability Classification

- Primary classification: `OPT_IN_ONLY`
- Confidence: High

理由:

- 公式文書は current stage を opt-in feature と明記している。
- Android 16 r4 AOSP の `RESTRICT_LOCAL_NETWORK` は Change ID `365139289L`。
- `RESTRICT_LOCAL_NETWORK` は `@EnabledAfter(targetSdkVersion = 36)` で、targetSdkVersion 36 では default-enabled ではない。
- Future enforcement の infrastructure は確認できるが、final release / permission UX / target gate は未確定。
- `OPT_IN_ONLY` は current opt-in testing と future enforcement plan のうち、現時点で実効影響を持つ opt-in 条件を表す分類である。

### Facts

- Release plan は 25Q2 と 26Q2 の 2 release deployment と説明されている。
- 25Q2 は guidance follow / feedback / implicit LAN dependency discovery の期間。
- Current stage は opt-in feature。
- Opt-in は `adb shell am compat enable RESTRICT_LOCAL_NETWORK <package>` と reboot。
- Current opt-in restore access は `NEARBY_WIFI_DEVICES` grant。
- Android 16 r4 には 25Q2 BPF maps / packet drop path が追加されている。
- Android 16 r4 には flagged `ACCESS_LOCAL_NETWORK` dangerous permission / AppOp が追加されている。

### Observations

- Android 16 OS update だけでは current LNP restriction は default で有効にならない。
- targetSdkVersion 36 化だけでも current LNP restriction は default で有効にならない。
- `RESTRICT_LOCAL_NETWORK` を opt-in した場合、`NEARBY_WIFI_DEVICES` 未許可の LAN traffic は fail し得る。
- Future enforcement では user denial / revocation に備えた runtime permission handling が必要になる。

### Hypotheses

- API 37 以降など、targetSdkVersion 36 より後の target で default enforcement される可能性がある。
- `ACCESS_LOCAL_NETWORK` は future new Nearby devices permission として `NEARBY_WIFI_DEVICES` を置き換える可能性が高い。
- Future enforcement では framework-level local network operations にも permission gate が広がる可能性がある。

### 期待挙動

| Scenario | Expected behavior |
|---|---|
| Android 16 / targetSdkVersion 35 / flag disabled | 従来どおり |
| Android 16 / targetSdkVersion 36 / flag disabled | 従来どおり。target 36 固有の current enforcement はない |
| Android 16 / targetSdkVersion 36 / flag enabled / NEARBY_WIFI_DEVICES granted | local network access restored |
| Android 16 / targetSdkVersion 36 / flag enabled / NEARBY_WIFI_DEVICES denied | LAN traffic が fail し得る |
| Android 16 / current 25Q2 opt-in phase | dependency discovery / feedback / migration preparation |
| Future enforcement / permission granted | outbound LAN / inbound LAN / Internet が work |
| Future enforcement / permission denied or revoked | outbound LAN / inbound LAN は fail、Internet は work |
| Android 15 / targetSdkVersion 36 | Android 16 LNP BPF infrastructure は未確認 |

### Developer Action Candidates

- implicit LAN access を棚卸しする。
- mDNS / SSDP / NSD / `.local` / LAN IP / UDP multicast / broadcast / TCP server / WebView LAN access を確認する。
- Android 16 25Q2 Beta 3 以降相当 build で `RESTRICT_LOCAL_NETWORK` を enable してテストする。
- `NEARBY_WIFI_DEVICES` grant / deny / revoke の差を確認する。
- future `ACCESS_LOCAL_NETWORK` または new Nearby devices permission の request / denial / revocation UX に備える。
- casting は Output Switcher / future API guidance と direct LAN permission 必要ケースを分ける。

### Test Focus

- Android 16 / targetSdkVersion 35 vs 36
- `RESTRICT_LOCAL_NETWORK` enabled / disabled
- reboot 有無
- `NEARBY_WIFI_DEVICES` declared / granted / denied / revoked
- implicit LAN access の棚卸し
- mDNS / SSDP / NsdManager / `.local`
- WebView / OkHttp / Cronet / native socket
- Output Switcher / media casting
- user rejection / revocation UX
- graceful fallback / feature degradation

### Human Decision Placeholder

- Human decision: 未判断
- Priority: 未判断
- Severity: 未判断
- Release readiness: 未判断
- Customer communication priority: 未判断
