# Improved bond loss handling - Android 15 → 16 挙動比較

このファイルは
[Android OS バージョン間挙動比較テンプレート](../../../../docs/templates/android-os-version-behavior-comparison-template.md)
を使い、remote bond loss 後の自動接続、認証失敗、bond 保持、再ペアリングの
違いを、同じ条件で Android 15 と Android 16 に並べた companion file である。

---

## 1. 関連資料と比較範囲

- Behavior Change: Improved bond loss handling
- [主レポート](improved-bond-loss-handling.md)
- [1ページ要約](../../../summaries/all/connectivity/improved-bond-loss-handling-summary.md)
- [新 intent の調査](../../target/connectivity/new-intents-to-handle-bond-loss-and-encryption-changes.md)
- [OEM 実装差の調査](../../target/connectivity/adapting-to-varying-oem-implementations-bond-loss.md)
- 比較対象: remote 側だけが bond key を失った後、保存済み bond を使って次の接続または incoming pairing が起きる場合
- 比較対象外: 初回 pairing、通常の切断、ユーザーが Android 側で「削除」した local unpair

| 項目 | Baseline | Target |
| --- | --- | --- |
| Android OS | Android 15 | Android 16 |
| AOSP tag | `android-15.0.0_r36` | `android-16.0.0_r4` |
| targetSdkVersion | 35 を主比較条件とする | 35 を主比較条件とする |
| アプリ build | 同一 build | 同一 build |
| local bond | `BOND_BONDED`、鍵あり | `BOND_BONDED`、鍵あり |
| remote bond | factory reset / key deletion 済み | factory reset / key deletion 済み |
| transport | BR/EDR と LE / GATT を個別確認 | BR/EDR と LE / GATT を個別確認 |

主分類:
- `OS_UPDATE_ALL_APPS`。主レポートの分類を正とする。

信頼度:
- High。OEM variation の範囲は Medium。

## 2. 比較契約（Comparison Contract）

比較で固定する条件:

- 同一アプリ build と targetSdkVersion 35
- `BLUETOOTH_CONNECT` を許可済み
- 同一 Bluetooth accessory または同等の test peer
- Android 側は対象 device を `BOND_BONDED` として保持
- remote 側だけ bond key を削除
- app、system profile、または peripheral が同じ接続契機を作る
- AOSP default path を主比較とし、OEM variation は別 scenario に分ける

targetSdkVersion 36 と API 36 の public intent 採用は、OS 差とは別の比較軸にする。

## 3. 用語

| 用語 | この資料での意味 |
| --- | --- |
| bond loss | Android と remote の保存済み鍵が一致せず、認証または暗号化を継続できない状態 |
| 自動接続 | ユーザーが pairing UI を操作せず、app、system profile、または peripheral が ACL / GATT / profile 接続を試すこと |
| 自動再ペアリング | system が local bond を削除し、新しい pairing をそのまま開始または継続すること |
| local bond retained | 接続が失敗しても Android の bonded devices list では `BOND_BONDED` が維持されること |
| user-driven re-pair | system UI または app の案内を受け、ユーザーが device settings から再ペアリングまたは削除を選ぶこと |

重要:

- Android 16 でも自動接続の「試行」自体は起こり得る。
- 変わる中心は、その試行が stale key で失敗した後に、system が local bond を
  自動削除して pairing を続けるか、bond loss として停止してユーザーへ委ねるかである。
- Android 15 の自動削除と pairing continuation は、確認済み AOSP 根拠では
  BR/EDR の bonded incoming pairing path に対する説明であり、すべての transport と
  接続 API が必ず同じ順序になるという意味ではない。

## 4. 先に結論

Android 15 では bond loss 関連処理が複数の経路に分かれており、BR/EDR の
bonded incoming pairing では local bond を自動削除して pairing を続ける経路がある。
Android 16 の AOSP default は、bond loss を共通処理で検出し、link を認証失敗として
切断し、local bond を保持したまま `ACTION_KEY_MISSING` と system UI で
user-driven re-pair へ誘導する。

したがって、Android 16 で `BOND_BONDED` が残っていることは「次の自動接続も成功する」
という意味ではない。アプリが bond state だけを見て retry すると、認証失敗を繰り返す
可能性がある。

| 観点 | Android 15 | Android 16 AOSP default | アプリへの影響 |
| --- | --- | --- | --- |
| 自動接続の開始 | app / profile / peripheral により起こり得る | 同左 | 接続開始 API を一律に止める変更ではない |
| key missing 後の処理 | 経路・flag 依存。BR/EDR incoming pairing では bond 自動削除と pairing continuation がある | `btm_sec_report_bond_loss()` に集約し、key missing 通知と切断 | 失敗後の retry 方針を変える必要がある |
| local bond | 削除される経路がある | 原則保持 | `BOND_NONE` だけでは検出できない |
| app-visible signal | flag / permission /経路に依存 | `ACTION_KEY_MISSING`、ACL / GATT の auth failure | 複数 signal を統合して扱う |
| system UI | key-missing dialog から直接 `removeBond()` する実装がある | dialog / notification / toast から device settings へ誘導 | app 独自 UI との二重表示を避ける |
| recovery の主体 | system が自動 pairing へ進む経路がある | ユーザーが再ペアリングまたは削除を選ぶ | retry loop を止め、ユーザー操作を待つ |

## 5. 同一条件での状態遷移

### Android 15: BR/EDR bonded incoming pairing の確認済み経路

```text
Android: BOND_BONDED / remote: key lost
-> remote から incoming pairing request
-> bonded device を検出
-> local bond を自動削除
-> pairing request 処理を継続
-> 新しい pairing へ進み得る
```

### Android 16: AOSP default

```text
Android: BOND_BONDED / remote: key lost
-> reconnect auth failure または bonded incoming pairing
-> remote bond loss として reason 付きで集約
-> ACTION_KEY_MISSING
-> ACL / GATT を auth failure として切断
-> local bond は BOND_BONDED のまま
-> system UI から user-driven re-pair / forget
```

差分の要点:

- 追加: reason 付きの集約処理、key-missing count、retained-bond test、
  app-facing auth failure 変換
- 変更: BR/EDR bonded incoming pairing を継続せず、reject / disconnect する
- default 変更: automatic removal / pairing continuation から bond retention /
  user-guided handling へ変更
- 不変: remote が鍵を失った状態では保存済み鍵による認証は成功しない

## 6. シナリオ別比較

### Scenario 1: app または system profile が自動再接続する

前提:

- remote 側だけが bond key を失っている
- app の `BluetoothGatt.connect()`、`connectGatt(..., autoConnect = true, ...)`、
  socket retry、または HID / A2DP / HFP profile が接続を試す

| Phase | Android 15 | Android 16 |
| --- | --- | --- |
| 1. 接続開始 | 保存済み bond を使って接続を試す | 同左 |
| 2. 認証 / 暗号化 | stale key により key missing / auth failure | 同左 |
| 3. system 処理 | transport、flag、相手の応答により通知・切断・key removal が分かれる | bond loss として集約し、AOSP default は切断して local bond を保持 |
| 4. app-visible signal | disconnect、bond state 変化、flag-dependent intent | `ACTION_KEY_MISSING`、ACL / GATT auth failure。`BOND_NONE` は原則来ない |
| 5. 次の操作 | 再試行または経路により pairing | retry を停止し、user-driven re-pair を待つ |

アプリの対応:

1. key missing または連続する auth failure を受けたら、通常の一時切断とは別状態へ移す。
2. GATT / socket を閉じ、profile 固有の自動 retry を可能な範囲で抑制する。
3. system UI と競合しない案内を出し、device settings での再ペアリングを待つ。

### Scenario 2: remote から incoming pairing が来る

| Phase | Android 15 | Android 16 |
| --- | --- | --- |
| 1. 初期状態 | Android は bonded、link は非暗号化 | 同左 |
| 2. trigger | remote が pairing request | 同左 |
| 3. native stack | local bond を削除して pairing request を継続する経路 | pairing request を reject し、bond loss として通知・切断 |
| 4. bond state | `BOND_NONE` へ遷移し得る | AOSP default は `BOND_BONDED` を保持 |
| 5. recovery | system 主導で新 pairing へ進み得る | ユーザーが re-pair / forget を選ぶ |

この scenario が、公式文書の「以前は bond を自動削除して新しい pairing process を
開始していた」に対する最も直接的な Android 15 baseline evidence である。

### Scenario 3: `BOND_BONDED` だけを見て retry する

Android 16 で起こり得る誤った loop:

```text
BOND_BONDED を確認
-> connect
-> authentication failure
-> disconnect
-> local bond は BOND_BONDED のまま
-> 即時 reconnect
-> authentication failure を反復
```

推奨状態:

```text
Connected
-> KeyMissingOrRepeatedAuthFailure
-> BondLostAwaitingUser
-> retry 停止 / resource close / user guidance
-> re-pair と暗号化成功
-> Connected
```

単発の transient disconnect だけで `BondLostAwaitingUser` に入れない。
`ACTION_KEY_MISSING`、認証失敗、bond state、直前の接続履歴を組み合わせる。

### Scenario 4: 回復

- Android 15: local bond removal 後に pairing が続く経路では、新しい鍵の確立で回復する。
- Android 16: system UI または app の案内からユーザーが re-pair / forget を行う。
- `ACTION_ENCRYPTION_CHANGE` で encryption enabled が確認できる場合は、bond restored の
  signal として使える。
- 回復後に初めて抑制していた auto-connect / retry を再開する。

### Scenario 5: OEM / fallback

- AOSP default: `ACTION_KEY_MISSING`、ACL disconnect、local bond retained。
- 公式文書上の variation: intent が broadcast されない実装では、ACL が接続したまま
  bond information が Android 15 と同様に削除される場合がある。
- AOSP 内にも特定 package / device 向けに `removeBond()` する IOP workaround がある。
- fallback として `ACTION_BOND_STATE_CHANGED` / `BOND_NONE`、ACL / GATT auth failure、
  profile disconnect、app protocol error を監視する。
- 単発の disconnect や timeout だけで bond を削除しない。複数 signal と再現性で判定する。

## 7. OS 差と targetSdkVersion 差

| Android OS | targetSdkVersion | System behavior | App-visible API / signal | 判定 |
| --- | --- | --- | --- | --- |
| Android 15 | 35 | 分散・flag-dependent。BR/EDR incoming pairing では automatic remove + pairing continuation の経路 | intents は flagged / permission 条件。`BOND_NONE` へ進む経路あり | Baseline |
| Android 15 | 36 | OS 側は Android 15 のまま | targetSdk だけでは Android 16 の stack behavior にならない | OS 差なし |
| Android 16 | 35 | AOSP default は bond loss を集約し、切断、local bond retained | sender path に targetSdk gate は見つからない。action string、permission、receiver、OEM 条件により観測可能 | OS update で影響 |
| Android 16 | 36 | targetSdk 35 と同じ system behavior | API 36 では intent constants が flag なし public API | API 採用が容易 |

注意:

- OS update だけで変わる: Bluetooth stack の detection、disconnect、bond retention、
  Settings UI。
- API 36 で変わる: `ACTION_KEY_MISSING` / `ACTION_ENCRYPTION_CHANGE` を public API として
 正式に参照できること。
- 見つからないもの: この behavior 専用の targetSdkVersion gate と Compat Change ID。

## 8. System behavior とアプリ観測の対応

| System event / state | App-visible signal | Android 15 | Android 16 | 注意点 |
| --- | --- | --- | --- | --- |
| remote key missing | `ACTION_KEY_MISSING` | flag / permission /経路依存 | AOSP default の primary signal | OEM で届かない可能性 |
| link disconnect | ACL / profile callback | 発生し得る | auth failure として見える場合がある | disconnect だけで bond loss と断定しない |
| GATT disconnect | GATT status | 経路依存 | key-missing count があると auth failure へ変換され得る | status code を log に残す |
| local bond removal | `ACTION_BOND_STATE_CHANGED` / `BOND_NONE` | automatic removal path で発生し得る | AOSP default では発生しない | OEM / workaround / user forget は例外 |
| local bond retained | `bondState == BOND_BONDED` | key missing と同時には一貫しない | default | 接続可能を意味しない |
| encryption restored | `ACTION_ENCRYPTION_CHANGE` | flagged | API 36 public signal | enabled / status を確認 |

## 9. アプリ側の対応手順

### 最小対応

1. `BOND_NONE` だけを bond loss の条件にしない。
2. `ACTION_KEY_MISSING` を primary signal としつつ、auth failure と bond state change を
   fallback として残す。
3. Android 16 の key missing 後は即時 retry を止め、GATT / socket を閉じる。
4. system dialog と重複しない形で、再ペアリングが必要なことを説明する。
5. re-pair と encryption success を確認してから自動接続を再開する。

### 推奨状態モデル

| App state | 進入条件 | 許可する処理 | 終了条件 |
| --- | --- | --- | --- |
| `Connected` | 接続・暗号化成功 | 通常通信 | disconnect / key missing |
| `TransientDisconnected` | 通常切断、単発 timeout | 制限付き backoff retry | reconnect success / auth failure |
| `BondLostAwaitingUser` | key missing、または反復する auth failure と bond 不整合 | retry 停止、resource close、案内、診断 log | re-pair / forget 後の新 bond |
| `Restoring` | user-driven re-pair 開始 | pairing 状態を監視 | encryption success / failure |

### やってはいけない前提

- `BOND_BONDED` なら保存済み鍵で必ず接続できる。
- remote bond loss では必ず直後に `BOND_NONE` が来る。
- Android 16 が自動接続の試行自体を禁止する。
- 全 OEM で `ACTION_KEY_MISSING` が必ず届く。
- 単発の disconnect はすべて bond loss である。

## 10. 検証仕様

### テストマトリクス

| Case | OS | targetSdk | Trigger | Expected | Observed |
| --- | --- | --- | --- | --- | --- |
| 1 | Android 15 | 35 | BR/EDR remote key delete → incoming pairing | automatic local bond removal と pairing continuation の経路を確認 | 未実施 |
| 2 | Android 16 | 35 | Case 1 と同じ | pairing reject、key missing、disconnect、local bond retained | 未実施 |
| 3 | Android 15 | 35 | app / profile auto-connect → auth failure | legacy notification / disconnect / bond state の順序を記録 | 未実施 |
| 4 | Android 16 | 35 | Case 3 と同じ | key missing、auth failure disconnect、local bond retained | 未実施 |
| 5 | Android 16 | 36 | Case 4 と同じ | system behavior は Case 4 と同じ。public intents の受信を確認 | 未実施 |
| 6 | Android 16 OEM 端末 | 35 / 36 | remote bond loss | intent あり / なし、bond retained / removed の分岐を記録 | 未実施 |
| 7 | Android 16 | 35 / 36 | 通常切断 | bond loss 状態へ誤遷移せず、backoff reconnect | 未実施 |
| 8 | Android 16 | 36 | user-driven re-pair | encryption success 後に retry を再開 | 未実施 |

### 観測点

- `ACTION_KEY_MISSING`
- `ACTION_ENCRYPTION_CHANGE`
- `ACTION_BOND_STATE_CHANGED`
- ACL / profile / GATT callback と status
- `BluetoothDevice.getBondState()`
- system dialog / notification / toast
- app の retry 回数と間隔
- `logcat`、`dumpsys bluetooth_manager`、bugreport、必要に応じて btsnoop

### 合格条件

- Android 16 で key missing 後の無限 reconnect が起きない。
- system UI と app UI が同時に競合しない。
- `BOND_BONDED` retained と接続成功を混同しない。
- `ACTION_KEY_MISSING` がない OEM path でも fallback が機能する。
- 通常切断を bond loss と誤判定しない。

## 11. Facts / Observations / Hypotheses / Conclusions

### Facts

- Android 16 all-apps 文書は、remote bond loss 時の link disconnect、local bond retention、
  system dialog による re-pair guidance を説明している。
- Android 15 の BR/EDR bonded incoming pairing path には、local bond を削除して
  pairing request 処理を継続する経路がある。
- Android 16 には `btm_sec_report_bond_loss()`、reason、key-missing count、
  retained-bond を検証する `BondLossTest` がある。
- Android 16 sender path に targetSdkVersion 36 gate は見つからない。

### Observations

- 実機比較は未実施。上記の Observed 列はすべて「未実施」。
- Android 16 は auto-connect の開始契機をなくすのではなく、bond loss 検出後の
  automatic re-pair を user-driven recovery に変える。

### Hypotheses

- OEM / controller / profile retry policy により callback 順序、dialog 表示、bond removal
  の有無には差が出る可能性がある。

### Conclusions

- Android 15 の `BOND_NONE` / automatic re-pair 前提を Android 16 に持ち込まない。
- Android 16 では key missing 後を明示的な `BondLostAwaitingUser` として扱い、
  retry を止める設計が安全である。
- OS 挙動変更と API 36 intent 採用は別々にテストする。

## 12. Evidence と信頼度

| Fact | Evidence | Confidence |
| --- | --- | --- |
| Android 15 の BR/EDR incoming pairing に automatic remove + pairing continuation がある | `btm_sec.cc#btm_io_capabilities_req` の tag diff | High |
| Android 16 は bond loss を集約し、通知・切断する | `btm_sec.cc#btm_sec_report_bond_loss` | High |
| Android 16 AOSP default は local bond を保持する | `BondLossTest` の bonded devices list assertion | High |
| Android 16 Settings は user-guided recovery へ寄せている | `BluetoothKeyMissingReceiver` / `BluetoothKeyMissingDialog*` | High |
| OEM で intent / retention behavior が異なり得る | 公式 target apps 文書と AOSP IOP workaround | Medium |

確認した AOSP source context:

| File / symbol / caller | Android 15 | Android 16 | 関連性 |
| --- | --- | --- | --- |
| Bluetooth `btm_sec.cc` / BR/EDR incoming pairing | `bta_dm_process_remove_device()` 後に pairing 継続 | pairing reject、`btm_sec_report_bond_loss(... BREDR_INCOMING_PAIRING)` | automatic re-pair から user-driven handling への直接差分 |
| Bluetooth `btm_sec.cc` / auth・LE encryption failure | 分散・flag-dependent key missing path | reason 付き共通処理 | auto-connect 後の認証失敗経路 |
| `RemoteDevices#keyMissingCallback` | flag / permission 分岐 | bonded device へ reason 付き ordered broadcast、count 更新 | app-visible signal |
| `RemoteDevices#aclStateChangeCallback` / `GattService#onDisconnected` | key-missing count による変換なし | auth failure へ変換し得る | app retry 判断 |
| `BondLossTest` | 該当 test なし | key missing、disconnect、bond retained を検証 | target end state の直接根拠 |
| Settings `BluetoothKeyMissingDialogFragment` | positive action が `removeBond()` | device settings へ誘導 | recovery 主体の UI 差 |

除外した経路:

- local user unpair / app の明示的 `removeBond()`
- normal disconnect
- initial pairing
- PBAP 固有通知や CompanionDeviceManager association 自体の作成

## 13. 制約と未検証事項

- 実機 / OEM 端末での callback 順序と UI 表示は未検証。
- Android 15 の automatic remove + pairing continuation の直接根拠は BR/EDR incoming
  pairing path。LE / GATT を同一挙動として一般化しない。
- `connectGatt(autoConnect = true)` の scheduling 自体はこの Behavior Change の主対象ではなく、
 接続後の authentication / encryption failure handling を比較している。
- AOSP checkout `frameworks-base` は clean で両 tag を確認した。Bluetooth / Settings
  checkout の hygiene は主レポートの記録を参照する。

## 14. References

Entry Point:

- [Android 16: Improved bond loss handling](https://developer.android.com/about/versions/16/behavior-changes-all#improved-bond-loss-handling)

Primary evidence:

- [主レポート](improved-bond-loss-handling.md)
- `tmp/aosp-checkouts/Bluetooth/system/stack/btm/btm_sec.cc`
- `tmp/aosp-checkouts/Bluetooth/android/app/src/com/android/bluetooth/btservice/RemoteDevices.java`
- `tmp/aosp-checkouts/Bluetooth/framework/tests/bumble/src/android/bluetooth/pairing/BondLossTest.java`
- `tmp/aosp-checkouts/Settings/src/com/android/settings/bluetooth/BluetoothKeyMissingDialogFragment.java`

Related:

- [1ページ要約](../../../summaries/all/connectivity/improved-bond-loss-handling-summary.md)
- [新 intent の調査](../../target/connectivity/new-intents-to-handle-bond-loss-and-encryption-changes.md)
- [OEM 実装差の調査](../../target/connectivity/adapting-to-varying-oem-implementations-bond-loss.md)

## 15. Human Decision

この companion file では判断しない。
[主レポートの Human Decision](improved-bond-loss-handling.md#人間の判断欄human-decision)
および [Android 16 decision log](../../../decisions/DECISION_LOG.md) を参照する。
