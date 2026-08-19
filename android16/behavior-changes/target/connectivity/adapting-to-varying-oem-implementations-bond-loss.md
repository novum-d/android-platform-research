# Adapting to varying OEM implementations 調査レポート

## 基本情報

### 調査対象 Android バージョン

From:
- android-15.0.0_r36

To:
- android-16.0.0_r4

Scope note:

### Behavior Change 文書

Document:
- https://developer.android.com/about/versions/16/behavior-changes-16#bond-loss-oem-impletations

Section:
- Adapting to varying OEM implementations

Parent section:
- New intents to handle bond loss and encryption changes

Category:
- Connectivity

### 分類スナップショット

主分類:
- `OS_UPDATE_ALL_APPS`

補足:
- ユーザー指定の初期仮説は `TARGET_SDK_36_CONDITIONAL_WITH_OEM_VARIABILITY` だが、`android16/behavior-changes/APPLICABILITY_CLASSIFICATION.md` にこの exact label はない。
- 公式文書は target apps ページ上で「Apps targeting Android 16 can now receive」と説明する。しかし AOSP の broadcast path には `targetSdkVersion >= 36` gate が見つからない。
- そのため、primary classification は `OS_UPDATE_ALL_APPS` とし、Android 16 Bluetooth stack、Bluetooth bonded device、remote bond loss、receiver / permission、OEM implementation variability を追加条件として扱う。

| 確認項目 | 回答 | 根拠 |
| --- | --- | --- |
| Android 16 に OS アップデートしただけで適用されるか | Conditional | Android 16 Bluetooth stack は targetSdk gate なしに `ACTION_KEY_MISSING` / `ACTION_ENCRYPTION_CHANGE` を送る path を持つ。 |
| targetSdkVersion 36 以上が必要か | No / API adoption には Yes | AOSP に targetSdk 36 gate は見つからない。API 36 では action constants が flag なし public API になる。 |
| 追加の実行時条件があるか | Yes | bonded Bluetooth device、remote bond loss、OEM が `ACTION_KEY_MISSING` を broadcast するか、receiver / permission 条件。 |
| Compat Change ID が関係するか | No | Bluetooth `ChangeIds.java` と公式 compat framework で該当 Change ID なし。 |

### 調査日

2026-07-03

### 信頼度

- Medium

理由:
- AOSP の `ACTION_KEY_MISSING` broadcast path、ACL disconnect path、Android 15 legacy key removal path、`ACTION_ENCRYPTION_CHANGE` restoration path は確認できた。
- ただし OEM / vendor / controller 実装差は AOSP では完全に検証できないため、OEM variability の範囲は公式文書と AOSP の境界整理に留まる。

## エグゼクティブサマリー

Android 16 では remote bond loss 検出時に `ACTION_KEY_MISSING` を broadcast し、ACL link を切断しつつ local bond information を保持する AOSP path が追加・整理されている。一方、公式文書は OEM によってこの intent の実装・broadcast が異なる可能性を明記している。

この項目の要点は、新 intent の追加そのものではなく、`ACTION_KEY_MISSING` が届く場合と届かない場合の両方に対応する必要がある点である。`ACTION_KEY_MISSING` が届く場合は primary signal として扱い、届かない場合は Android 15 と同様に `ACTION_BOND_STATE_CHANGED`、ACL disconnect、connection failure など既存の bond loss handling を継続する。

顧客向けには、Android 16 OS 側の Bluetooth behavior と targetSdkVersion 36 で public API として採用できることを分けて説明する必要がある。

## 公式ドキュメント確認

### Original statements

- Android 16 は新 intent を導入するが、implementation / broadcasting は OEM によって異なる可能性がある。
- アプリは bond loss handling をこれらの variation に適応できるよう設計すべきである。
- `ACTION_KEY_MISSING` が broadcast される場合、ACL link は system により切断されるが、bond information は保持される。
- アプリは `ACTION_KEY_MISSING` を bond loss detection の primary signal として使うべきである。
- `ACTION_KEY_MISSING` の後に device が disconnect した場合、device が system とまだ bonded とは限らないため reconnect は慎重に行うべきである。
- `ACTION_KEY_MISSING` が broadcast されない場合、ACL link は接続されたまま、bond information は Android 15 と同様に削除される。
- その場合、以前の Android release と同様の既存 bond loss handling を続けるべきである。

### 公式本文との差分

- 調査開始時点の公式 HTML はユーザー提示の statements と一致していた。
- 公式 anchor は `bond-loss-oem-impletations` であり、綴りは公式 URL のまま記録する。
- 公式ページの Last updated は 2026-06-24 UTC。

## 変更内容

### AOSP-defined behavior

- Android 16 `btm_sec_report_bond_loss()` は remote bond loss を検出すると `bta_dm_remote_key_missing()` を呼び、その後 HCI disconnect を送る。
- Android 16 `RemoteDevices.keyMissingCallback(byte[] address, int reason)` は、対象 device が `BOND_BONDED` である場合に `BluetoothDevice.ACTION_KEY_MISSING` を作成し、`BLUETOOTH_CONNECT` permission の ordered broadcast として送信する。
- Android 16 `RemoteDevices.encryptionChangeCallback()` は `ACTION_ENCRYPTION_CHANGE` を送信し、`EXTRA_ENCRYPTION_STATUS`、`EXTRA_ENCRYPTION_ENABLED`、`EXTRA_KEY_SIZE`、`EXTRA_ENCRYPTION_ALGORITHM` を付与する。
- Android 16 では encryption enabled かつ key missing count が残っている場合、`ACTION_KEY_MISSING_TO_ENCRYPTION_CHANGE` transition を記録し、key missing count を reset する。これは後続の successful encryption を bond restored と扱う根拠になる。

### OEM / implementation-dependent behavior

- 公式文書は、Android 16 が新 intent を導入しても implementation / broadcasting は OEM により異なる可能性があると明記している。
- AOSP には `ACTION_KEY_MISSING` が broadcast される標準 path があるが、OEM が同じ path を完全に採用する保証は AOSP だけでは確認できない。
- AOSP 内にも app / device 相性向けの `bondLossIopFixNeeded()` があり、特定 package / device name では `device.removeBond()` を呼ぶ workaround が存在する。これは標準 path とは別に、実装差・相性差があり得ることを示す補助 evidence である。

### Android 15 baseline

- Android 15 tag では `ACTION_KEY_MISSING` / `ACTION_ENCRYPTION_CHANGE` は `@FlaggedApi` 付き API surface として存在する。
- Android 15 `RemoteDevices.keyMissingCallback()` は flags により `BLUETOOTH_CONNECT` broadcast または `BLUETOOTH_CONNECT` + `BLUETOOTH_PRIVILEGED` broadcast に分岐する。
- Android 15 LE encryption failure path では `HCI_ERR_KEY_MISSING` 等で LE link key flag と key type を削除する分岐がある。これは公式文書が説明する「ACTION_KEY_MISSING が来ない場合は Android 15 と同様に bond information が removed」の baseline と整合する。

## 適用条件

### OS アップデート時の挙動

- Android 16 の Bluetooth stack に更新されると、AOSP-defined path では remote bond loss 時に `ACTION_KEY_MISSING` broadcast と ACL disconnect が行われる。
- この path に `targetSdkVersion >= 36` gate は見つからない。
- したがって、targetSdkVersion 35 のアプリでも、action string を直接扱い、receiver と permission が適切なら、Android 16 端末上で broadcast を受信する可能性がある。
- ただし実際には OEM implementation、Bluetooth event、receiver visibility、`BLUETOOTH_CONNECT` permission に依存する。

### targetSdkVersion 36 以上での挙動

- targetSdkVersion 36 以上にしたこと自体で `ACTION_KEY_MISSING` broadcast path が有効化される AOSP gate は確認できない。
- targetSdkVersion / compile SDK 36 では `BluetoothDevice.ACTION_KEY_MISSING` と `ACTION_ENCRYPTION_CHANGE` が flag なし public API として参照できるため、新 signal を正式 API として実装しやすくなる。
- Android 15 端末上で targetSdkVersion 36 にしても、Android 16 の標準 bond loss handling は保証されない。

### その他の条件

- Bluetooth bonded device を扱う。
- remote device 側の bond loss、key missing、encryption failure、または bonded unencrypted pairing request が発生する。
- `ACTION_KEY_MISSING` を受け取る receiver と `BLUETOOTH_CONNECT` permission がある。
- OEM / vendor / controller / Bluetooth module が AOSP path と同等に `ACTION_KEY_MISSING` を broadcast する。
- `ACTION_KEY_MISSING` が来ない場合の fallback が実装されている。

## AOSP 調査

### 使用 checkout

- `frameworks-base`: clean。`android-15.0.0_r36` と `android-16.0.0_r4` tag を確認済み。
- `tmp/aosp-checkouts/Bluetooth`: clean。`android-15.0.0_r36` と `android-16.0.0_r4` tag を確認済み。

### 関連ファイル

- `packages/modules/Bluetooth/framework/api/current.txt`
- `packages/modules/Bluetooth/framework/java/android/bluetooth/BluetoothDevice.java`
- `packages/modules/Bluetooth/android/app/src/com/android/bluetooth/btservice/RemoteDevices.java`
- `packages/modules/Bluetooth/system/stack/btm/btm_sec.cc`
- `packages/modules/Bluetooth/system/bta/dm/bta_dm_sec.cc`
- `packages/modules/Bluetooth/system/btif/src/btif_dm.cc`
- `packages/modules/Bluetooth/system/btif/src/bluetooth.cc`
- `packages/modules/Bluetooth/android/app/change-ids/com/android/bluetooth/ChangeIds.java`
- `frameworks/base/core/res/AndroidManifest.xml`

### 確認したソース文脈

| ファイル / シンボル | Android 15 の基準挙動 | Android 16 の挙動 | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| `BluetoothDevice.ACTION_KEY_MISSING` | `@FlaggedApi(key_missing_public)` 付き。 | flag なし public API。 | 新 signal をアプリが扱える API surface の根拠。 |
| `RemoteDevices.keyMissingCallback()` | flag により permission / broadcast path が分岐。 | `BOND_BONDED` の場合に `ACTION_KEY_MISSING` ordered broadcast を送信。 | `ACTION_KEY_MISSING` broadcast path のアプリ到達点。 |
| `btm_sec_report_bond_loss()` | Android 15 では分散・flag dependent path。 | `bta_dm_remote_key_missing()` 後に `btm_sec_disconnect()`。 | `ACTION_KEY_MISSING` 時の ACL disconnect の native 根拠。 |
| Android 15 `btm_sec.cc` LE key missing branch | `sec_flags` から LE link key known を落とし、key type を none にする branch。 | Android 16 では `btm_sec_report_bond_loss()` により key missing event / disconnect path へ進む。 | no `ACTION_KEY_MISSING` / legacy path で bond information が removed される説明の baseline。 |
| `RemoteDevices.encryptionChangeCallback()` | flag が true の時だけ broadcast。 | flag gate なしで `ACTION_ENCRYPTION_CHANGE` を broadcast。 | bond restored 判定に使う後続 signal の根拠。 |
| `RemoteDevices.bondLossIopFixNeeded()` | なし。 | 特定 app/device 向けに `device.removeBond()` workaround。 | AOSP 標準 path 以外の相性差処理があることの補助 evidence。 |
| `ChangeIds.java` | Bluetooth behavior 専用 Change ID なし。 | 同左。 | compat framework gate がない根拠。 |

Entry point / caller:
- HCI security event / encryption change -> `btm_sec_report_bond_loss()` または `bta_dm_on_encryption_change()` -> `BTA_DM_KEY_MISSING_EVT` / `BTA_DM_ENCRYPTION_CHANGE_EVT` -> `btif_dm.cc` -> JNI -> `RemoteDevices` -> Android broadcast。

Unrelated / excluded code paths:
- Bluetooth socket、A2DP、LE subrate など同じ Bluetooth API diff に含まれる変更は、bond loss OEM variation の適用条件判断に直接関係しないため除外した。
- DevicePolicyManager の `THROW_EXCEPTION_WHEN_KEY_MISSING` は Bluetooth bond loss intent ではないため除外した。

## 差分解釈

| 確認した差分 | 解釈 | Behavior Change との関係 | 信頼度 |
| --- | --- | --- | --- |
| Android 16 `btm_sec_report_bond_loss()` が `bta_dm_remote_key_missing()` 後に disconnect | added / consolidated behavior | `ACTION_KEY_MISSING` broadcast 時に ACL link が disconnected される根拠 | High |
| Android 16 `RemoteDevices.keyMissingCallback()` が `BOND_BONDED` のみ broadcast | changed condition | bond information retained 状態で key missing signal を出す根拠 | High |
| Android 15 LE key missing branch が key flags / key type を消す | baseline behavior | `ACTION_KEY_MISSING` が来ない場合に Android 15 と同様 bond information removed とされる根拠 | Medium |
| Android 16 `RemoteDevices.encryptionChangeCallback()` が status / enabled / key size / algorithm を broadcast | added / changed gate | successful encryption を bond restored と扱う後続 signal の根拠 | High |
| `targetSdkVersion >= 36` gate が見つからない | no target SDK gate found | primary classification を `TARGET_SDK_36_CONDITIONAL` にしない根拠 | Medium |
| OEM variation は公式文書に明記、AOSP では全 OEM を検証不可 | implementation-dependent | AOSP-defined behavior と OEM-dependent behavior を分ける根拠 | Medium |

## Facts

- 公式文書は、`ACTION_KEY_MISSING` / `ACTION_ENCRYPTION_CHANGE` の implementation / broadcasting が OEM によって異なる可能性を明記している。
- Android 16 AOSP には `ACTION_KEY_MISSING` を broadcast する path がある。
- Android 16 AOSP では `ACTION_KEY_MISSING` path が `BOND_BONDED` の device に限定される。
- Android 16 AOSP では `btm_sec_report_bond_loss()` が `bta_dm_remote_key_missing()` の後に ACL disconnect を実行する。
- Android 16 AOSP では `ACTION_ENCRYPTION_CHANGE` に status / enabled / key size / algorithm が含まれる。
- Android 15 AOSP には key missing 時に LE bond key 情報を消す legacy branch がある。
- この behavior 専用の compat Change ID は見つからない。

## Observations

- 公式文書が示す `ACTION_KEY_MISSING` あり / なしの二分岐は、AOSP-defined path と legacy path の両方をアプリが考慮すべきという実装指針として読める。
- AOSP-defined path では `ACTION_KEY_MISSING` が先に出て、ACL disconnect は system 側で行われる。したがって disconnect だけを bond loss と扱う実装は、Android 16 では signal の解釈順序を見直す必要がある。
- `ACTION_KEY_MISSING` が来ない場合は、公式文書どおり従来の bond state / disconnect / reconnect failure based handling が必要になる。
- `bondLossIopFixNeeded()` のような app/device specific workaround は、標準 path から外れる例外が現実にあることを示している。

## Hypotheses

- 公式文書の targetSdkVersion 36 applicability は API 36 で public constants として実装できることを主に指し、runtime broadcast gate を意味していない可能性が高い。
- OEM が `ACTION_KEY_MISSING` を broadcast しない場合、Android 15 と同様の bond removal / reconnect failure sequence が観測される可能性がある。
- Bluetooth controller / vendor stack / device-specific workaround により、ACL disconnect、bond retention、bond removal、broadcast sequence は端末ごとに差が出る可能性がある。

## Conclusions

- この項目の primary classification は `OS_UPDATE_ALL_APPS`。ただし実影響は Bluetooth bonded device を扱い、remote bond loss handling を実装しているアプリに限定される。
- `ACTION_KEY_MISSING` が broadcast される場合は primary signal として扱うべきだが、全端末で必ず届く前提にしてはいけない。
- `ACTION_KEY_MISSING` が来ない場合に備え、Android 15 と同様の existing bond loss handling を残す必要がある。
- 顧客向け説明では、Android 16 への OS update で Bluetooth stack behavior が変わる可能性と、targetSdkVersion 36 で新 API を正式利用できることを分離する。

## 期待挙動マトリクス

| シナリオ | 期待挙動 |
| --- | --- |
| Android 16 / targetSdkVersion 35 | target gate は見つからないため、receiver / permission / event 条件を満たせば broadcast を受ける可能性がある。API constants としての正式利用は API 36 で行う。 |
| Android 16 / targetSdkVersion 36 | `ACTION_KEY_MISSING` / `ACTION_ENCRYPTION_CHANGE` を public API として実装可能。OEM implementation により受信有無は変動し得る。 |
| Android 15 / targetSdkVersion 36 | Android 16 の AOSP-defined bond loss path はない。Android 15 tag では flagged / flags dependent path と legacy key removal path が中心。 |

### 詳細マトリクス

| 条件 | 期待挙動 |
| --- | --- |
| Android 16 / targetSdkVersion 36 / `ACTION_KEY_MISSING` broadcast あり | primary bond loss signal として扱う。ACL link は system により disconnect、bond information は原則 retained。 |
| Android 16 / targetSdkVersion 36 / `ACTION_KEY_MISSING` broadcast なし | Android 15 と同様の fallback handling が必要。公式文書では ACL link は残り、bond information は removed。 |
| Android 16 / targetSdkVersion 36 / `ACTION_ENCRYPTION_CHANGE` received / encryption success | bond restored とみなし、key missing 状態や user guidance を解除する候補。 |
| Android 16 / targetSdkVersion 36 / `ACTION_ENCRYPTION_CHANGE` received / encryption failure | bond loss / reconnect failure / re-pair guidance の候補 signal として扱う。 |
| Android 16 / targetSdkVersion 36 / ACL disconnected after `ACTION_KEY_MISSING` | AOSP-defined path。自動 reconnect は慎重に扱う。 |
| Android 16 / targetSdkVersion 36 / ACL remains connected without `ACTION_KEY_MISSING` | legacy / OEM-dependent path。bond state と connection failure を併用して検出する。 |
| Android 16 / targetSdkVersion 36 / bond information retained | `ACTION_KEY_MISSING` path の期待値。ただし IOP workaround や OEM 差に注意。 |
| Android 16 / targetSdkVersion 36 / bond information removed | no `ACTION_KEY_MISSING` / legacy path、または workaround path。 |
| Android 16 / targetSdkVersion 36 / OEM implementation broadcasts new intents | AOSP path に近い。new intent を primary signal とする。 |
| Android 16 / targetSdkVersion 36 / OEM implementation does not broadcast `ACTION_KEY_MISSING` | legacy fallback 必須。new intent 受信前提の state machine は避ける。 |
| Android 16 / targetSdkVersion 36 / app handles only `ACTION_BOND_STATE_CHANGED` | Android 16 の primary signal を取りこぼす可能性がある。 |
| Android 16 / targetSdkVersion 36 / app handles `ACTION_KEY_MISSING` and `ACTION_ENCRYPTION_CHANGE` | Android 16 path と bond restored path を扱える。fallback は残す。 |

## 影響対象

- bonded Bluetooth device を扱うアプリ
- BLE / Classic Bluetooth peripheral と reconnect するアプリ
- `ACTION_BOND_STATE_CHANGED` のみに依存するアプリ
- `ACTION_ACL_CONNECTED` / `ACTION_ACL_DISCONNECTED` に依存するアプリ
- `ACTION_KEY_MISSING` を新たに利用するアプリ
- `ACTION_ENCRYPTION_CHANGE` を新たに利用するアプリ
- remote bond loss を user guidance / re-pairing flow に反映するアプリ
- 自動 reconnect / retry / re-pairing を行うアプリ
- Companion Device Manager と Bluetooth bonding を併用するアプリ
- OEM device 差を吸収する必要がある Bluetooth アプリ

## 推奨対応候補

- `ACTION_KEY_MISSING` を受信した場合は bond loss の primary signal とし、ユーザーに remote device 側の bond / range / re-pairing 状態確認を促す。
- `ACTION_KEY_MISSING` 後の自動 reconnect は、remote device が system と bonded ではない可能性を考慮して抑制または user confirmation を挟む。
- `ACTION_KEY_MISSING` が来ない端末では、従来の `ACTION_BOND_STATE_CHANGED`、ACL disconnect、connection failure、app protocol error による bond loss detection を使い続ける。
- `ACTION_ENCRYPTION_CHANGE` の successful encryption を bond restored signal として扱う。
- OEM / Bluetooth chipset / device model ごとの broadcast sequence をテストし、new intent が届かない場合でも UX が破綻しないようにする。

## テスト観点

- Android 15 端末上の targetSdkVersion 35
- Android 16 端末上の targetSdkVersion 35
- Android 16 端末上の targetSdkVersion 36
- Android 15 端末上の targetSdkVersion 36 が検証可能な場合の比較
- `ACTION_KEY_MISSING` broadcast の受信有無
- `ACTION_ENCRYPTION_CHANGE` broadcast の受信有無
- encryption status / algorithm / key size extra の内容
- remote device 側で bond を削除した後の reconnect
- Android 側で bond retained / removed の確認
- ACL connected / disconnected broadcast sequence
- `ACTION_BOND_STATE_CHANGED` sequence
- `ACTION_KEY_MISSING` 後に app が reconnect した場合の挙動
- `ACTION_KEY_MISSING` が来ない OEM / device での fallback behavior
- 複数 OEM / device / Bluetooth chipset での behavior 差
- user feedback / re-pairing / forgetting flow の UX
- app process が background の場合の broadcast 受信可否
- receiver manifest / runtime registration の違い
- permission requirement / Bluetooth runtime permission の確認

## Compat framework

- Change ID: 該当なし
- Change name: 該当なし
- Default state: 該当なし
- Toggleable for testing: 該当なし

根拠:
- Bluetooth module の `android/app/change-ids/com/android/bluetooth/ChangeIds.java` には `ENFORCE_CONNECT = 211757425L` のみで、この behavior 専用 Change ID はない。
- Android 16 compat framework 公式ページで `KEY_MISSING` / `ENCRYPTION_CHANGE` / Bluetooth bond loss に一致する entry は確認できなかった。

## 顧客向け説明

Android 16 では、remote device の bond loss を検出した場合に `ACTION_KEY_MISSING` を通知し、system が ACL link を切断しながら local bond information を保持する path が用意されています。この intent が届く端末では、アプリはそれを bond loss の primary signal として扱うべきです。

ただし、公式文書は OEM によって implementation / broadcasting が異なる可能性を明記しています。`ACTION_KEY_MISSING` が届かない端末では、Android 15 と同様に bond information が削除される path があり得るため、既存の bond state / disconnect / reconnect failure handling を残してください。Android 16 への OS update の影響と、targetSdkVersion 36 で新 API を採用する影響は分けて説明する必要があります。

## Human Decision

最終優先度:
- 未判断

判断:
- Human decision required

確認事項:
- 対象アプリが bonded Bluetooth device と reconnect / re-pairing flow を持つか
- `ACTION_KEY_MISSING` が届かない端末での fallback があるか
- 顧客向けに OEM 差分をどの程度説明するか
- 複数 OEM / chipset の実機テストを必須にするか
