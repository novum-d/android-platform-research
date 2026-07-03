# Local Network Permission - Errors Summary

## One Page Summary

Android 16 の Local Network Permission / Errors は、Local Network Protection によって LAN 宛て socket operation が失敗した場合の error surface を扱う。公式文書は、restriction による error が local network address への `send` / send variant を呼んだ calling socket に返り、例として `sendto failed: EPERM (Operation not permitted)` と `sendto failed: ECONNABORTED (Operation not permitted)` を示している。

## Classification

Primary classification: `UNKNOWN_NEEDS_MORE_EVIDENCE`

理由: r4 AOSP では `RESTRICT_LOCAL_NETWORK = 365139289` が `@EnabledAfter(targetSdkVersion = 36)` で定義されており、targetSdkVersion 36 では default enabled ではない。current stage は 25Q2+ build で AppCompat flag を明示 enable する opt-in testing behavior として扱うのが妥当である。BPF drop path は確認できたが、`EPERM` / `ECONNABORTED` の完全な syscall-to-Java exception mapping は未確認。

Confidence: Medium

## Key Facts

- 公式 Errors section は、LAN 宛て `send` / send variant に socket error が返ると説明している。
- r4 AOSP は `RESTRICT_LOCAL_NETWORK` Change ID `365139289` を持つ。
- enforcement gate は 25Q2+ かつ compat change enabled。
- current opt-in phase では `NEARBY_WIFI_DEVICES` granted なら UID を local network block map から外し、denied/missing なら block map に入れる。
- BPF `netd.c` は blocked UID の local network packet を `DROP` できる。
- Local DNS server の UDP/TCP 53 は allow rule があるため、通常この restriction error の対象外。

## Customer Explanation

Android 16 へ OS アップデートしただけ、または targetSdkVersion 36 に上げただけで、この socket error が既定で発生するとは説明しない。現在確認できる影響は、25Q2+ build で `RESTRICT_LOCAL_NETWORK` を enable し、reboot 後、`NEARBY_WIFI_DEVICES` が grant されていない UID が LAN 宛て socket operation を行う場合である。

将来 enforcement では、新しい Nearby devices group permission が denied/revoked の場合に同種の LAN failure を扱う必要がある。ただし r4 AOSP では final permission surface と final targetSdk gate は未確定である。

## Behavior Matrix

| Scenario | Expected behavior |
|---|---|
| Android 16 / targetSdkVersion 35 / flag disabled | 影響なし |
| Android 16 / targetSdkVersion 35 / flag enabled | 25Q2+ かつ permission denied/missing なら LAN socket failure あり |
| Android 16 / targetSdkVersion 36 / flag disabled | 影響なし |
| Android 16 / targetSdkVersion 36 / flag enabled | 25Q2+ かつ permission denied/missing なら LAN socket failure あり |
| `NEARBY_WIFI_DEVICES` granted | current opt-in phase では access restored |
| `NEARBY_WIFI_DEVICES` denied / missing | UID blocked; LAN packet drop 可能 |
| `sendto` to LAN | 公式例: `EPERM` または `ECONNABORTED` |
| Internet request | 影響なし |
| DNS local server port 53 | allow rule により影響なし |
| Future enforcement / permission granted | outbound LAN / Internet / inbound LAN works |
| Future enforcement / permission denied | outbound LAN / inbound LAN fails; Internet works |

## Testing Focus

- `RESTRICT_LOCAL_NETWORK` enabled / disabled
- enabled 後の reboot 有無
- `NEARBY_WIFI_DEVICES` declared / granted / denied / revoked
- native `sendto()` to LAN
- Java `DatagramSocket.send()` to LAN
- UDP multicast / broadcast
- TCP `connect()` / `write()`
- OkHttp / Cronet / WebView LAN request
- DNS local server port 53
- errno / exception message / stack trace
- retry suppression and user-facing fallback

## Facts / Observations / Hypotheses / Conclusions

Facts: 公式文書は `EPERM` / `ECONNABORTED` example を示し、AOSP は compat flag、permission-to-block-map、BPF drop path を持つ。

Observations: AOSP evidence は socket failure mechanism を裏付けるが、exact errno mapping までは未完了。

Hypotheses: Java/Kotlin では `SocketException` または API 固有の `IOException` として見える可能性が高い。TCP `connect()` や incoming path は operation timing により error surface が変わり得る。

Conclusions: この subsection は current opt-in testing の socket error guidance として扱う。Android 16 OS update impact、targetSdkVersion 36 impact、future permission enforcement impact は混ぜない。

## Human Decision Placeholder

- Final priority: TBD by human
- Final severity: TBD by human
- Release readiness decision: TBD by human
- Customer communication priority: TBD by human
