# Android 15 → 16 Connectivity and Security 挙動比較

## 1. 比較範囲

- [比較一覧](README.md)
- [ケース別対応手順](../case-guides/connectivity-and-security.md)
- Baseline: Android 15 / `android-15.0.0_r36`
- Target: Android 16 / `android-16.0.0_r4`
- Observed: 対象アプリ、peripheral、OEM で未実施

## 2. 先に結論

Android 16 では、system が failure をより安全な形へ寄せる変更が多い。
その結果、Android 15 で届いていた timeout code、暗黙の nested Intent forwarding、
cross-app Intent filter mismatch、GPU development IOCTL、共有可能な MediaStore token などを
前提にした処理は成立しなくなる場合がある。

## 3. 項目別比較

### Bluetooth bond loss

- [Android 15→16 詳細比較](../all/connectivity/improved-bond-loss-handling-android15-to-16-behavior-comparison.md)
- [主レポート](../all/connectivity/improved-bond-loss-handling.md)

要点:

```text
Android 15: 経路によりlocal bond自動削除 -> pairing継続
Android 16: key missing通知 -> auth failure切断 -> local bond保持 -> user-driven re-pair
```

自動接続の試行自体がなくなるのではなく、bond loss 検出後の復旧主体が変わる。

### CompanionDeviceManager による Bluetooth bond 削除 API

- [主レポート](../target/connectivity/new-way-to-remove-bluetooth-bond.md)
- [要約](../../summaries/target/connectivity/new-way-to-remove-bluetooth-bond-summary.md)
- 適用: `API_ADDITION_ONLY`

| 観点 | Android 15 | Android 16 |
| --- | --- | --- |
| API availability | AOSP tag には `@FlaggedApi` 付き source があるため、製品 SDK の公開状態は別確認が必要 | 公式文書が `CompanionDeviceManager.removeBond(int)` を public API として案内 |
| Runtime behavior | API を呼ばないアプリへ自動適用されない | valid association / `BLUETOOTH_CONNECT` / MAC address 条件で明示的に bond 削除を開始 |
| App signal | 製品 SDK と既存 unpair 実装に依存 | 即時戻り値と `ACTION_BOND_STATE_CHANGED` を分けて扱う |
| 対応 | system Settings または既存経路 | CDM 管理機器の unpair 導線へ選択的に採用 |

### Companion Device Manager discovery timeout

- [主レポート](../all/security/companion-apps-no-longer-notified-of-discovery-timeouts.md)
- [要約](../../summaries/all/security/companion-apps-no-longer-notified-of-discovery-timeouts-summary.md)
- 適用: `OS_UPDATE_ALL_APPS`

| 観点 | Android 15 | Android 16 |
| --- | --- | --- |
| System behavior | 20秒で discovery timeout として終了 | 20秒は soft timeout。UI message 後も探索し、5分 hard timeout または user close で終了 |
| App signal | `RESULT_DISCOVERY_TIMEOUT` | flow close 時に `RESULT_USER_REJECTED` |
| 対応 | timeout code で retry UI を分岐 | result だけで timeout / cancel を断定せず、elapsed time と UI context を補助 signal にする |

### Intent redirection hardening

- [主レポート](../all/security/improved-security-against-intent-redirection-attacks.md)
- [要約](../../summaries/all/security/improved-security-against-intent-redirection-attacks-summary.md)
- 適用: `OS_UPDATE_ALL_APPS`

| 観点 | Android 15 | Android 16 |
| --- | --- | --- |
| System behavior | 外部 top-level Intent 内の nested Intent を受信 app context で launch できる経路 | creator token、launch permission、URI grant を検証し、不正なら log / abort / `SecurityException` |
| App signal | 脆弱な forwarding も成功し得る | legitimate flow も入力不整合なら block され得る |
| 対応 | external nested Intent entryを棚卸し | component / package / action / data / flags / grants を allowlist・sanitize。opt-outは最小範囲 |

### Safer Intents

- [主レポート](../target/security/safer-intents.md)
- [要約](../../summaries/target/security/safer-intents-summary.md)
- 適用: `OPT_IN_ONLY`

| 観点 | Android 15 | Android 16 |
| --- | --- | --- |
| System behavior | sender-side compat pathはあるが、receiving app の strict manifest matching は一般適用されない | `android:intentMatchingFlags="enforceIntentFilter"` を指定した receiver側でcross-app explicit Intentを厳格照合 |
| App signal | filter不一致のexplicit Intentもtargetに届き得る | filter不一致、null actionはblock。PackageManager warning |
| 対応 | partner trafficを記録 | opt-in前にfilters/senderを修正し、必要なcomponentだけ`allowNullAction`または一時`none` |

targetSdkVersion 36 だけでは有効にならず、manifest opt-in と feature flag が主 gate。
same-app Intent は対象外である。

### GPU syscall filtering

- [主レポート](../target/security/gpu-syscall-filtering.md)
- [要約](../../summaries/target/security/gpu-syscall-filtering-summary.md)
- 適用: `OS_UPDATE_ALL_APPS` + Pixel 6～9 Mali + production policy

| 観点 | Android 15 | Android 16 |
| --- | --- | --- |
| System behavior | `set_xperm_filter` mechanismなし。GPU device accessは従来policy | IOCTL commandをunprivileged / restricted / instrumentationに分類し、production appを制限 |
| App signal | direct IOCTL / profiling toolが動作し得る | `avc: denied { ioctl }`、機能失敗。shell / debuggableは例外になり得る |
| 対応 | direct `/dev/mali0` dependencyを検出 | Vulkan / OpenGL / EGLまたは更新SDKへ移行し、release buildを実機検証 |

通常の supported graphics API 全体を禁止する変更ではない。

### MediaStore version lockdown

- [主レポート](../target/security/mediastore-version-lockdown.md)
- [要約](../../summaries/target/security/mediastore-version-lockdown-summary.md)
- 適用: `TARGET_SDK_36_CONDITIONAL`

| 観点 | Android 15 / legacy gate | Android 16 / target 36 |
| --- | --- | --- |
| System behavior | legacy token `dbVersion:dbUuid` | feature flag + Change ID `343977174` で `hash(dbUuid + callingUid)` |
| App signal | app間で同じvolume tokenを比較・parseできてしまう | app / UIDごとに異なるopaque token。format前提が壊れる |
| 対応 | equality以外の利用を検出 | same-app cache invalidationだけに限定し、item差分はgeneration APIへ |

Android 15 tag に guarded code は存在するため、製品 flag と公式 Android 16 適用条件を分ける。

## 4. System behavior と App signal

| 項目 | Primary system event | App-visible signal | Fallback |
| --- | --- | --- | --- |
| Bond loss | key missing / auth failure | key-missing intent、disconnect、bond state | OEM pathでは`BOND_NONE`等 |
| CDM timeout | soft / hard timeout UI | `RESULT_USER_REJECTED` | elapsed time / user action |
| Intent redirection | creator / permission validation | abort、exception、log | sanitized rebuilt Intent |
| Safer Intents | strict receiver matching | resolve failure、PM warning | component-scoped exception |
| GPU | SELinux IOCTL xperm | denial / native feature failure | supported graphics API |
| MediaStore | per-UID token | opaque string | generation API |
| CDM bond removal API | association を検証して明示的に unpair | 即時戻り値 + bond-state broadcast | system Settings / 既存 unpair 導線 |

## 5. OS / targetSdk マトリクス

| 項目 | Android 15 / target35 | Android 16 / target35 | Android 16 / target36 |
| --- | --- | --- | --- |
| Bond loss | legacy / path-dependent | retained-bond default | target35と同じ。public intents採用可 |
| CDM timeout | timeout result | user-rejected result | target35と同じ |
| Intent redirection | baseline | hardening適用 | target35と同じ |
| Safer Intents | receiving opt-in対象外 | manifest opt-in時のみ | manifest opt-in時のみ |
| GPU | legacy policy | device / build条件でfilter | target35と同じ |
| MediaStore version | legacy | target35はlegacy見込み | per-UID opaque token |
| CDM bond removal API | Android 15 SDK 公開状態を別確認 | API を呼ばなければ変更なし | API 36 として選択的に採用 |

## 6. 比較試験

| Case | Trigger | Expected Android 15 | Expected Android 16 | Observed |
| --- | --- | --- | --- | --- |
| S1 | CDMでdevice未発見 | timeout result | UI継続後user-rejected | 未実施 |
| S2 | tampered nested Intent | launchし得る | block / exception | 未実施 |
| S3 | filter不一致explicit Intent | deliveryし得る | opt-in時block | 未実施 |
| S4 | restricted Mali IOCTL / release | legacy policy | SELinux deny | 未実施 |
| S5 | 2 appで`getVersion()`比較 |同値になり得る | target36ではUID別 | 未実施 |
| S6 | CDM association に `removeBond()` | Android 15 SDK 公開状態を別確認 | 開始結果 + `BOND_NONE` / failureを監視 | 未実施 |

## 7. Evidence / Human Decision

Facts、例外、confidence は各主レポートを正とする。Security test は成功経路だけでなく、
tampered input、denied permission、non-debuggable build が拒否されることも確認する。
この資料では Human Decision を確定しない。
