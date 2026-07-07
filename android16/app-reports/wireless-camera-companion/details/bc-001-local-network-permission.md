# BC-001: Local Network Permission

## 基本情報

Behavior Change 文書:
- URL: https://developer.android.com/about/versions/16/behavior-changes-16#local-network-permission
- Section: Local Network Permission

調査対象 Android バージョン:
- From: android-15.0.0_r36
- To: android-16.0.0_r4

既存調査:
- [android16/behavior-changes/target/privacy/local-network-permission.md](../../../behavior-changes/target/privacy/local-network-permission.md)
- [android16/summaries/target/privacy/local-network-permission-summary.md](../../../summaries/target/privacy/local-network-permission-summary.md)

## 対象アプリとの関係

関連するアプリ機能:
- カメラ探索。
- カメラ側 Wi-Fi AP / 同一 LAN 上のカメラ接続。
- mDNS / NSD / SSDP / `.local` resolution。
- local IP への HTTP / WebSocket / socket 接続。
- ライブビュー、リモート撮影、画像 / 動画転送、再接続。

アプリが該当する可能性:
- Conditional / 要確認。

判断理由:
- カメラ連携アプリは direct local network access を使う可能性が高い。
- ただし Android 16 current stage は Android 17 の default runtime permission enforcement ではなく、`RESTRICT_LOCAL_NETWORK` compat flag による opt-in testing behavior として扱う。

確認したアプリ実装:
- 未確認。

## 適用条件分類

主分類:
- `UNKNOWN_NEEDS_MORE_EVIDENCE`

実質条件:
- Android 16 25Q2 以降相当 build。
- `RESTRICT_LOCAL_NETWORK` を対象 package に enable。
- reboot 後、app が local network traffic を行う。
- current opt-in phase では `NEARBY_WIFI_DEVICES` が grant されていない場合に failure surface が出る。

OS update と targetSdkVersion:
- Android 16 へ OS update しただけでは default restriction にはならない。
- targetSdkVersion 36 化だけでも default restriction にはならない。
- Android 16 では opt-in testing と future permission readiness として扱う。

Confidence:
- Medium。

## AOSP / 公式根拠

既存 Android16 調査で確認済み:
- `ConnectivityCompatChanges.RESTRICT_LOCAL_NETWORK = 365139289L`
- Android 16 tag では `@Disabled`
- `restrict_local_network` / `lnp_developer_opt_in` flags
- flagged dangerous permission `ACCESS_LOCAL_NETWORK`
- `OPSTR_ACCESS_LOCAL_NETWORK`
- current opt-in phase では `NEARBY_WIFI_DEVICES` permission state を確認
- BPF map / packet drop path

## アプリ影響

想定される影響:
- opt-in testing では、permission denied 状態で camera discovery / local IP connection / image transfer が socket error になる可能性。
- Android 17 以降の default enforcement に備え、Android 16 で failure handling を先行確認できる。

推奨対応:
- LAN access entry point を棚卸しする。
- `NEARBY_WIFI_DEVICES` declaration / grant / denied / revoked を確認する。
- Android 16 で `RESTRICT_LOCAL_NETWORK` を enable して mDNS / NSD / `.local` / HTTP / socket / WebView / native socket をテストする。
- future `ACCESS_LOCAL_NETWORK` runtime permission UX に備える。

## テスト観点

- Android 16 / targetSdkVersion 35 / flag disabled。
- Android 16 / targetSdkVersion 36 / flag disabled。
- Android 16 / flag enabled / `NEARBY_WIFI_DEVICES` granted。
- Android 16 / flag enabled / `NEARBY_WIFI_DEVICES` denied。
- カメラ探索、手動 IP、mDNS / NSD、UDP multicast / broadcast、画像 / 動画転送。

## Human Decision

- Final priority: TBD by human
- Release readiness impact: TBD by human
