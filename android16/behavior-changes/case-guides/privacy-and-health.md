# Android 16 Privacy and Health - ケース別対応手順

## 位置づけ

このファイルは Android 16 の privacy / health 変更をケース別に実装・検証へ落とす companion guide である。
適用条件と根拠はリンク先の調査レポートを正とする。

## Health and fitness permissions

Reports:
- [Health and fitness permissions](../target/health-and-fitness/health-and-fitness-permissions.md)
- [Mobile apps](../target/health-and-fitness/mobile-apps-health-fitness-permissions.md)

| ケース | 判定条件 | 対応手順 | 最低限の検証 |
| --- | --- | --- | --- |
| Health sensor API 未使用 | 対象 data type / FGS なし | 対応不要 | manifest / API inventory |
| targetSdkVersion 35 以下 | Android 16 上でも旧 permission path | target 36 移行前 baseline を記録 | Android 16 target 35 |
| While-in-use health data | target 36 で heart rate 等を foreground 利用 | data type ごとの `android.permissions.health` permission へ移行 | grant / deny / revoke |
| Background health access | background read が必要 | `READ_HEALTH_DATA_IN_BACKGROUND` と foreground service type / runtime state を確認 | foreground / background |
| Mobile app | granular permission を要求 | privacy policy / rationale Activity を宣言し revoke flow を処理 | rationale missing / present |
| Wear OS | Health Services / ProtoLayout / sensor | Wear SDK version と実機 / emulator で permission mapping を検証 | API別 data read |

## App-owned photos

Report: [App-owned photos](../target/privacy/app-owned-photos.md)

| ケース | 判定条件 | 対応手順 | 最低限の検証 |
| --- | --- | --- | --- |
| Android 16 / target 35 | compat gate default off | baseline として owner access を記録 | target 35 / 36 comparison |
| Full media access | user が full grant | limited picker flow と分けて通常 access を確認 | query / open / thumbnail |
| Limited access + owned media kept | pre-selected item を保持 | selected grant / owner access を区別してログ化 | prompt後 access |
| Limited access + owned media deselected | user が pre-selected item を解除 | missing media を revoke として扱い、説明・再選択・fallback を用意 | query / openFile before / after |
| Other-app media | requesting app が owner ではない | selected grant のみで扱う | owner package comparison |
| Reinstall / package change | owner semantics が変わり得る | app-owned 前提を再構築せず、MediaStore結果を正とする | update / uninstall / reinstall |

## Local Network Permission

Report: [Local Network Permission](../target/privacy/local-network-permission.md)

Detection:
- raw / managed socket、OkHttp、Cronet、WebView、mDNS、SSDP、NSD、`.local`、LAN IP、UDP multicast / broadcast、TCP server、casting を棚卸しする。

| ケース | 判定条件 | 対応手順 | 最低限の検証 |
| --- | --- | --- | --- |
| Compat flag disabled | Android 16 current default | 従来挙動を baseline として記録 | target 35 / 36 |
| Flag enabled + Nearby granted | opt-in restriction + `NEARBY_WIFI_DEVICES` allow | 全 LAN flow が復旧することを確認 | reboot後 outbound / inbound |
| Flag enabled + denied / revoked | LAN packet が block | permission explanation、retry、Internet-only fallback、socket error handling を実装 | `EPERM` / `ECONNABORTED` |
| NsdManager opt-in phase | app process外 operation | raw socket と同じ結果を仮定せず個別確認 | discovery / resolve |
| WebView / library / native | host UID packet として影響 | wrapper API だけで除外せず end-to-end test | HTTP LAN / `.local` |
| DNS / Output Switcher exception | documented exception path | permission不要と一般化せず対象 port / picker を限定 | DNS 53、media route |
| Future enforcement | `ACCESS_LOCAL_NETWORK` が本格適用される将来 release | Android 16 current behavior と分け、permission UX の設計候補を残す | current flag test + future backlog |

Opt-in test:

```bash
adb shell am compat enable RESTRICT_LOCAL_NETWORK <package>
# device reboot
adb shell am compat disable RESTRICT_LOCAL_NETWORK <package>
```

## Verification status

- この分冊は documentation synthesis であり、対象アプリの permission UI、media ownership、LAN traffic の observed result は未実施。
- Permission は grant / deny / revoke に加え、upgrade、reinstall、secondary user / work profile を必要に応じて含める。
- Local Network Permission の Android 16 current opt-in phase と将来 enforcement を同じ expected result にしない。
