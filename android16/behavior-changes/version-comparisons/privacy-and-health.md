# Android 15 → 16 Privacy and Health 挙動比較

## 1. 比較範囲

- [比較一覧](README.md)
- [ケース別対応手順](../case-guides/privacy-and-health.md)
- Baseline: Android 15 / `android-15.0.0_r36`
- Target: Android 16 / `android-16.0.0_r4`
- Observed: permission UI、MediaStore access、LAN traffic とも未実施

## 2. 先に結論

Privacy / Health の3項目はいずれも追加条件が重要である。
Android 16 へ更新しただけで一律に permission が失われるわけではない。
Health と app-owned photos は targetSdkVersion 36、Local Network Permission は現在の
Android 16 では compat opt-in が主 gate になる。

## 3. 項目別比較

### Health and fitness permissions

- [主レポート](../target/health-and-fitness/health-and-fitness-permissions.md)
- [要約](../../summaries/target/health-and-fitness/health-and-fitness-permissions-summary.md)
- 適用: `TARGET_SDK_36_CONDITIONAL`

| 観点 | Android 15 / target 35 | Android 16 / target 36 |
| --- | --- | --- |
| System behavior | body sensor accessを`BODY_SENSORS` / `BODY_SENSORS_BACKGROUND`で管理 | health data typeごとの`android.permission.health.*`へ移行 |
| App signal | legacy permission grant / denial | `READ_HEART_RATE`等のgranular grant / denial / revoke |
| Background | `BODY_SENSORS_BACKGROUND`中心 | `READ_HEALTH_DATA_IN_BACKGROUND`、health FGS type、runtime state |
| 対応 |使用sensor / data typeを棚卸し | permission mapping、rationale Activity、privacy policy、revoke flowを実装 |

例:

```text
Android 15: heart rate -> BODY_SENSORS
Android 16 target36: heart rate -> READ_HEART_RATE
```

### App-owned photos

- [主レポート](../target/privacy/app-owned-photos.md)
- [要約](../../summaries/target/privacy/app-owned-photos-summary.md)
- 適用: `TARGET_SDK_36_CONDITIONAL`

| 観点 | Android 15 | Android 16 / target 36 |
| --- | --- | --- |
| System behavior | app-owned mediaをlimited pickerで自動pre-selected / revokeする専用pathなし | owned image/videoをpre-selected。ユーザーdeselect時にgrantと`owner_package_name`を更新 |
| App signal | owner accessを継続できる前提になりやすい | deselect後のquery / open失敗、selected set変化 |
| 対応 | owner accessとselected grantを分けていない実装を検出 | deselectをrevokeとして扱い、説明・再選択・fallbackを用意 |

full media permission、URI grant、limited selected access は別経路としてテストする。

### Local Network Permission

- [主レポート](../target/privacy/local-network-permission.md)
- [要約](../../summaries/target/privacy/local-network-permission-summary.md)
- 適用: Android 16 current stage は `OPT_IN_ONLY`

| 観点 | Android 15 | Android 16 default | Android 16 opt-in |
| --- | --- | --- | --- |
| System behavior | `INTERNET` permissionでLAN / Internet traffic | target 35 / 36とも従来挙動 | `RESTRICT_LOCAL_NETWORK`有効UIDをBPF mapでblock |
| App signal | LAN socket成功 | defaultではbaseline | denied時に`EPERM` / `ECONNABORTED`等。Internetは継続 |
| Permission | 新LNPなし | future `ACCESS_LOCAL_NETWORK`基盤はあるがcurrent enforcement外 | current restoreは`NEARBY_WIFI_DEVICES` grant |
| 対応 | LAN API / libraryを棚卸し | baseline logを採取 | permission説明、retry、Internet-only fallback、inbound / outbound試験 |

`ACCESS_LOCAL_NETWORK` の将来 enforcement と Android 16 current opt-in test を同じ expected result にしない。

## 4. OS / targetSdk / opt-in マトリクス

| 項目 | Android 15 / target35 | Android 16 / target35 | Android 16 / target36 | 追加 gate |
| --- | --- | --- | --- | --- |
| Health | legacy sensor permissions | legacy path | granular health permissions | health API / data type |
| App-owned photos | dedicated featureなし | compat default off | preselect / deselect revoke | limited picker + owned media |
| Local Network | unrestricted LAN | default unrestricted | default unrestricted | compat opt-in + permission state |

## 5. シナリオ別対応

| Scenario | 判定条件 | Android 15 | Android 16対応 |
| --- | --- | --- | --- |
| Foreground heart rate | sensor read | `BODY_SENSORS` | target36では`READ_HEART_RATE` |
| Background health | background read | legacy background permission | health background permission + FGS state |
| Owned photo kept | limited picker |専用preselectionなし | owner access / selected grantを維持 |
| Owned photo deselected | user revoke | owner accessが残り得る | access lossを処理 |
| LAN denied | compat opt-in + no grant |該当gateなし | socket error、UX、fallback |
| LAN granted | compat opt-in + Nearby granted |該当gateなし | outbound / inboundを再検証 |

## 6. 比較試験

| Case | 固定条件 | Expected Android 15 | Expected Android 16 | Observed |
| --- | --- | --- | --- | --- |
| P1 | 同一heart-rate read | legacy permission | target36でgranular permission | 未実施 |
| P2 | 同一owned media + limited picker | dedicated preselectなし | target36でpreselected | 未実施 |
| P3 | P2でdeselect | owner pathを記録 | access revoke | 未実施 |
| P4 | LAN outbound / inbound | `INTERNET`で成功 | defaultは成功、opt-in deniedは失敗 | 未実施 |
| P5 | WebView / native / OkHttp LAN |成功 | host UID permissionに従う | 未実施 |

## 7. Evidence / Human Decision

Facts、permission定義、compat Change ID、例外、confidence は各主レポートを正とする。
grant / deny / revoke、upgrade / reinstall、secondary user / work profile を必要に応じて分離する。
この資料では Human Decision を確定しない。
