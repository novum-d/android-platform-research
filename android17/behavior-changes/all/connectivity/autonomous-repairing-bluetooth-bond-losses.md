# Autonomous re-pairing for Bluetooth bond losses

## 基本情報（Metadata）

### 調査対象 Android バージョン（Android Versions）

比較元:
- android-16.0.0_r4

比較先:
- android-17.0.0_r1

以前の targetSdkVersion:
- 36

対象 targetSdkVersion:
- 37

### Behavior Change 文書（Behavior Change Source）

文書:
- https://developer.android.com/about/versions/17/behavior-changes-all

関連文書:
- https://developer.android.com/reference/android/bluetooth/BluetoothDevice#ACTION_PAIRING_REQUEST
- https://developer.android.com/reference/android/bluetooth/BluetoothDevice#EXTRA_PAIRING_CONTEXT
- https://developer.android.com/reference/android/bluetooth/BluetoothDevice#ACTION_KEY_MISSING

セクション:
- Autonomous re-pairing for Bluetooth bond losses

ページ種別:
- Behavior changes: all apps

### 分類スナップショット（Classification Snapshot）

主分類（Primary classification）:
- OS_UPDATE_ALL_APPS

公式文書からの初期適用条件判断:
- 公式文書は Android 17 の all apps ページにこの項目を掲載し、targetSdkVersion 条件を示していない。
- Android 17 では Bluetooth bond loss 後に system が background で autonomous re-pairing を試行できる。
- `ACTION_PAIRING_REQUEST` に `EXTRA_PAIRING_CONTEXT` が追加され、standard pairing と autonomous system-initiated re-pairing attempt を区別できる。
- 公式文書によると、既存のセキュリティ鍵が置き換えられるのは、再ペアリングに成功し、新しい接続が以前の bond と同等以上のセキュリティレベルを満たす場合に限られる。
- `ACTION_KEY_MISSING` は autonomous re-pairing が失敗した場合だけ broadcast される。
- `frameworks-base` と追加 checkout の `platform/packages/modules/Bluetooth` で、feature flag、`BluetoothDevice` API、`BondStateMachine` / `RemoteDevices` の bond-loss recovery path を確認した。

早見表（At-a-glance impact）:

| 確認項目 | 回答 | 根拠 |
| --- | --- | --- |
| Android 17 に OS アップデートしただけで適用されるか | Yes / Conditional | all apps ページで、targetSdkVersion 条件なし。Bluetooth module 側でも targetSdkVersion ゲートは見つからず、feature flag と bond loss 条件で分岐する。 |
| targetSdkVersion 37 以上が必要か | 公式文書上は不要 | targetSdkVersion 条件は示されていない。 |
| 追加の実行時条件があるか | ある | Bluetooth peripheral bond loss が発生し、system が re-pairing を試行する場合。 |
| Compat Change ID が関係するか | 確認できず | Bluetooth module の該当 path は aconfig flag と bond loss state を参照しており、targetSdkVersion compat gate は見つからない。 |

### 調査日（Investigation Date）

2026-06-19

### 信頼度（Confidence）

- High

### 適用条件分類（Applicability Classification）

適用される条件（Applies when）:
- [x] targetSdkVersion に関係なく Android 17 の全アプリへ適用
- [ ] Android 17 以上かつ targetSdkVersion 37 以上で適用
- [ ] targetSdkVersion 37 以上かつ追加の実行時条件を満たす場合に適用
- [ ] Mainline / Google Play system update に依存
- [ ] API 追加のみであり、挙動変更ではない
- [ ] 追加 evidence が必要

必要な実行時条件（Required runtime conditions）:
- Android version: Android 17 以上。
- targetSdkVersion: 公式文書上は条件なし。
- Device condition: Bluetooth peripheral と bond / pairing する Android device。
- Runtime condition: bond loss が発生し、system が autonomous re-pairing を試行する。
- App condition: companion app / peripheral app が pairing request、key missing broadcast、manual unpair / re-pair guidance を扱う。

Compat framework:
- Change ID: 確認できず
- 変更名: 該当なし
- 既定状態: `autonomous_repairing_initiation` feature flag に依存
- テスト時に切り替え可能か: feature flag / Bluetooth stack test config に依存

分類信頼度（Classification confidence）:
- High

分類根拠（Classification evidence）:
- 公式 Behavior Change 文書は Android 17 all apps change として autonomous re-pairing を説明している。
- `frameworks-base` Android 17 tag では `core/java/android/net/flags.aconfig` に `autonomous_repairing_initiation` flag が追加されている。
- `platform/packages/modules/Bluetooth` Android 17 tag では `BluetoothDevice.EXTRA_PAIRING_CONTEXT`、`PAIRING_CONTEXT_REPAIRING`、`ACTION_KEY_MISSING` の API surface と、`BondStateMachine` / `RemoteDevices` の bond-loss / re-pairing path を確認した。
- Bluetooth module の該当 path では targetSdkVersion ゲートは見つからず、`Utils.isAutonomousRepairingSupported()` と bond loss state が主な条件である。

---

# エグゼクティブサマリー

Android 17 では、Bluetooth bond loss を system が自動的に回復する autonomous re-pairing が導入される。従来は users が Settings で peripheral を unpair / re-pair する必要があったが、Android 17 では system が background で bond の再確立を試行できる。

多くのアプリでは code change は不要とされている。ただし Bluetooth companion app、peripheral manufacturer app、wearable / audio / IoT / health device app など、pairing や key missing broadcast を扱うアプリは、`EXTRA_PAIRING_CONTEXT`、`ACTION_KEY_MISSING` の timing、system-managed notification / dialog と app 側 recovery UI の整合を確認する必要がある。

信頼度は High とする。追加 checkout の `platform/packages/modules/Bluetooth` で、Android 17 tag における API surface、pairing context、bond-loss state、`ACTION_KEY_MISSING` broadcast path を確認できた。

---

# AOSP 調査（AOSP Investigation）

## チェックアウト状態

根拠利用前に確認したコマンド:

```bash
git -C frameworks-base status --short
git -C frameworks-base tag --list android-16.0.0_r4
git -C frameworks-base tag --list android-17.0.0_r1
```

結果:
- `frameworks-base` working tree: clean at the time of investigation.
- From tag: `android-16.0.0_r4` exists.
- To tag: `android-17.0.0_r1` exists.

## 関連ファイル（Related Files）

frameworks-base で確認:
- `core/java/android/net/flags.aconfig`
- `core/api/current.txt`
- `packages/SettingsLib/src/com/android/settingslib/bluetooth/BluetoothEventManager.java`
- `packages/SettingsLib/src/com/android/settingslib/bluetooth/CachedBluetoothDevice.java`

追加で必要な AOSP project:
- なし。`tmp/aosp-checkouts/Bluetooth` に `platform/packages/modules/Bluetooth` の Android 16 / Android 17 tag を取得して確認済み。

差分確認メモ:
- 広域の `frameworks-base` tag diff では rename detection が skipped される警告が出るため、根拠確認では `--no-renames` と対象 path 限定の diff を併用した。
- `packages/SettingsLib` には `EXTRA_PAIRING_CONTEXT` / `PAIRING_CONTEXT_REPAIRING` を使って Bluetooth 診断 UI の bonding failure 表示を調整する差分がある。
- ただし、この差分は SettingsLib 側の表示 / 診断状態更新であり、bond loss 検知、autonomous re-pairing 実行、`ACTION_KEY_MISSING` broadcast の本体ではない。
- `platform/packages/modules/Bluetooth` では `framework/java/android/bluetooth/BluetoothDevice.java`、`android/app/src/com/android/bluetooth/btservice/BondStateMachine.java`、`RemoteDevices.java`、`Utils.java`、`flags/framework.aconfig` を確認した。

## 確認したソース文脈（Source Context Reviewed）

| File / symbol | Android 16 baseline | Android 17 behavior | 関連性 |
| --- | --- | --- | --- |
| `core/java/android/net/flags.aconfig` / `autonomous_repairing_initiation` | flag なし | `namespace: "bluetooth"`、description は Android Bluetooth autonomous repairing changes を有効化する flag と説明 | Android 17 で Bluetooth autonomous repairing feature が追加された frameworks-base 側 evidence。 |
| `SettingsLib` / `BluetoothEventManager`、`CachedBluetoothDevice` | pairing context を bonding failure 判定に使わない | `EXTRA_PAIRING_CONTEXT` を読み取り、`PAIRING_CONTEXT_REPAIRING` の場合は通常の pairing failure と区別 | autonomous re-pairing の存在を UI 側から補強するが、Bluetooth stack 実装ではない。 |
| `BluetoothDevice.EXTRA_PAIRING_CONTEXT` | なし | `ACTION_PAIRING_REQUEST` / `ACTION_BOND_STATE_CHANGED` に pairing context extra を追加 | app が通常 pairing と autonomous re-pairing を区別する API surface。 |
| `BluetoothDevice.PAIRING_CONTEXT_REPAIRING` | なし | autonomous system-initiated re-pairing を示す定数を追加 | 公式文書の re-pairing context に対応。 |
| `BondStateMachine.sendPairingRequestIntent` | pairing context extra なし | autonomous repairing supported 時に `EXTRA_PAIRING_CONTEXT` を broadcast に付与 | app-facing pairing request の変更本体。 |
| `BondStateMachine.broadcastBondStateChangeIntent` | bond state broadcast に pairing context なし | repairing initiator の場合に `PAIRING_CONTEXT_REPAIRING` を付与 | bond state change でも repairing context を伝える path。 |
| `RemoteDevices` / bond-loss path | manual recovery 中心 | bond loss 検知時に autonomous re-pairing を開始し、失敗時に `ACTION_KEY_MISSING` を送る path を追加 | 公式文書の key missing timing と recovery flow に対応。 |

Source context の補足:
- Entry point / caller: Bluetooth stack の bond loss detection、pairing request generation、key missing broadcast、system UI notification / dialog。
- 関連性: Bluetooth module の `BondStateMachine` と `RemoteDevices` が bond transition / repairing context / key missing broadcast を担当する。
- Baseline Android behavior: Android 16 tag には `EXTRA_PAIRING_CONTEXT`、`PAIRING_CONTEXT_REPAIRING`、autonomous repairing initiation path がない。
- Target Android behavior: Android 17 tag では feature flag 有効時、bond loss state で autonomous re-pairing を開始し、pairing/bond state broadcast に repairing context を付与する。
- Source diff type: added behavior / API addition / added feature flag。
- Excluded code paths: SettingsLib の Bluetooth 診断 UI は implementation evidence ではないため補助 evidence に留めた。device repair mode、fingerprint repair strings、CompanionDeviceManager discovery は Bluetooth bond loss recovery ではないため除外した。

## 事実・観察・仮説・結論

事実:
- `frameworks-base` の `android-16.0.0_r4` と `android-17.0.0_r1` tag は存在し、調査時点の working tree は clean。
- 公式文書は Android 17 all apps change として autonomous re-pairing を説明し、targetSdkVersion 条件を示していない。
- `frameworks-base` Android 17 tag には `autonomous_repairing_initiation` flag がある。
- `platform/packages/modules/Bluetooth` Android 17 tag には `autonomous_repairing_initiation` flag、`BluetoothDevice.EXTRA_PAIRING_CONTEXT`、`PAIRING_CONTEXT_REPAIRING`、`BondStateMachine` / `RemoteDevices` の autonomous repairing path がある。

観察:
- 適用条件は targetSdkVersion ではなく、Android 17 Bluetooth module、feature flag、bond loss state、device pairing flow に依存する。
- `ACTION_KEY_MISSING` は bond loss path の失敗 / disconnect path と結びついている。

結論:
- `OS_UPDATE_ALL_APPS` と分類する。
- Android 17 OS update + Bluetooth bond loss + autonomous repairing feature enabled 条件で targetSdkVersion 非依存に適用される。
- Confidence は High。

---

# 開発者影響

影響を受ける可能性が高いアプリ:
- Bluetooth companion app
- peripheral manufacturer app
- wearable / audio / IoT / health device app
- カメラ連携アプリ
- pairing / bond loss recovery / key missing broadcast を扱うアプリ

コード変更が必要になる可能性が低いアプリ:
- Bluetooth のペアリングと復旧を Settings / システム UI に任せ、接続後の通信だけを行うアプリ。
- `ACTION_PAIRING_REQUEST`、`ACTION_BOND_STATE_CHANGED`、`ACTION_KEY_MISSING` を処理しないアプリ。
- bond loss 発生時に独自の `createBond()`、手動でのペアリング解除 / 再ペアリング手順、ペアリング UI を提供しないアプリ。

多くのアプリではコード変更は不要と考えられる。ただし、接続復旧を独自に行う連携アプリについては「問題がない」と断定せず、システムによる自動修復とアプリによる復旧処理が競合しないことを確認する。特に、`BOND_NONE` を受けると直ちに `createBond()` や独自のペアリング UI を開始する実装は、Android 17 の自動再ペアリングと同時に動く可能性がある。

対応候補:
- 手動でのペアリング解除 / 再ペアリング手順を棚卸しする。
- `ACTION_PAIRING_REQUEST` の `EXTRA_PAIRING_CONTEXT` を参照し、通常のペアリングと自動再ペアリングを区別する。
- 自動修復に成功した場合は `ACTION_KEY_MISSING` が届かないことを前提に、エラー処理を見直す。
- Android 17 端末で bond loss、再ペアリングの成功 / 失敗、ユーザー確認の流れをテストする。

既存実装の検索観点:

```bash
rg -n "ACTION_BOND_STATE_CHANGED|EXTRA_BOND_STATE|EXTRA_PREVIOUS_BOND_STATE|getBondState|BOND_NONE|BOND_BONDING|BOND_BONDED|createBond|ACTION_PAIRING_REQUEST|ACTION_KEY_MISSING|EXTRA_PAIRING_CONTEXT|PAIRING_CONTEXT_REPAIRING"
```

- `BOND_NONE`: bond loss、ペアリング解除、ペアリング失敗の後に、アプリが独自の復旧処理を開始していないかを最優先で確認する。
- `BOND_BONDING`: システムによる自動修復中に、アプリが通常の初回ペアリング UI、タイムアウト処理、失敗時の処理を開始しないか確認する。
- `BOND_BONDED`: 自動修復の成功後に、アプリの状態、登録済みデバイス、通信が正常に復旧するか確認する。
- 定数名が直接使われていない実装もあるため、`ACTION_BOND_STATE_CHANGED` receiver と `getBondState()` call site から状態分岐を追う。

---

# サービス影響例

このセクションは、公式文書と AOSP 根拠から導いた「起こりうる影響例」を記録する。特定サービスで実際に発生確認した事実ではない。

## 例1（Example 1）: Fitbit / Garmin Connect / Oura のような wearable companion

- 具体サービス例: Fitbit、Garmin Connect、Oura、Galaxy Wearable。
- 影響を受ける実装パターン: bond loss 時にアプリ独自の「一度ペアリング解除して再ペアリング」案内や key missing broadcast を前提に復旧 UI を出す実装。
- 発生条件: Android 17 Bluetooth module で autonomous re-pairing が成功し、従来なら app が扱っていた key missing / manual recovery flow が system-managed flow で処理される場合。
- ユーザーに見える症状: アプリ側の再ペアリング案内と system dialog / notification が重複する、または app 側が復旧完了を検知しにくい可能性。
- 技術的に起きていること: pairing / bond state broadcast に `EXTRA_PAIRING_CONTEXT=PAIRING_CONTEXT_REPAIRING` が付与され、successful repairing では `ACTION_KEY_MISSING` の timing が従来前提と変わる。
- 推奨対応シーン: wearable / health device / companion app の bond loss recovery。
- 検証観点: successful repairing、failed repairing、user confirmation、app 独自 recovery UI、`ACTION_KEY_MISSING` 受信有無。
- 根拠: 公式文書、`BluetoothDevice.EXTRA_PAIRING_CONTEXT`、`PAIRING_CONTEXT_REPAIRING`、`BondStateMachine` / `RemoteDevices` evidence。
- Confidence（信頼度）: High。
- 注意: 上記サービスで発生確認した事実ではない。実際の影響は peripheral と companion app の recovery 実装に依存する。

## 例2（Example 2）: Sony Headphones Connect / Bose / JBL のような Bluetooth audio companion

- 具体サービス例: Sony Headphones Connect、Bose、JBL Headphones、Sennheiser Smart Control。
- 影響を受ける実装パターン: headphones / earbuds の bond loss をアプリ側で検知し、firmware update、device settings、reconnect guidance を出す実装。
- 発生条件: Android 17 が autonomous re-pairing を試み、pairing context や key missing broadcast の扱いが変わる場合。
- ユーザーに見える症状: 接続復旧中の表示、設定画面の device state、再ペアリング案内が一時的に実状態とずれる可能性。
- 技術的に起きていること: system が bond loss 後の re-pairing initiation を管理し、app-facing broadcast に repairing context を付ける。
- 推奨対応シーン: headphones / earbuds companion の reconnect、firmware update 前後、multi-device pairing。
- 検証観点: bond loss から復旧までの app state machine、system dialog と app UI の整合、failed recovery 時の fallback。
- 根拠: Bluetooth module の autonomous repairing path と SettingsLib の pairing context handling。
- Confidence（信頼度）: High。
- 注意: 上記サービスで発生確認した事実ではない。device firmware と Bluetooth stack の組み合わせで検証が必要。

## 例3（Example 3）: Panasonic LUMIX Sync / Image App のようなカメラ連携アプリ

公開仕様で確認できる事実:
- LUMIX Sync は、カメラと Bluetooth Low Energy でペアリングし、ペアリング済みのカメラを登録済みデバイスとして保持する。ペアリング済みの場合は、Bluetooth を起点に Wi-Fi 接続を確立し、カメラがスリープから復帰した後には Bluetooth 接続を自動的に再確立すると説明されている。
- LUMIX Sync の従来の復旧手順では、ペアリングに時間がかかる場合、スマートフォンとカメラの両方からペアリング情報を削除して再登録する。
- Panasonic Image App の接続方式は機種によって異なる。QR コード / NFC / SSID による Wi-Fi のみの接続は Android の Bluetooth bond を使わないため、直接影響を受けにくい。一方、Bluetooth 対応カメラでは、ペアリング後に Wi-Fi へ自動接続し、リモートシャッター、リモート起動、自動転送、位置情報の記録、時刻同期などに Bluetooth 接続を使う。

調査上の推定:
- LUMIX Sync と、Bluetooth 対応カメラを利用する Image App は、Android の Bluetooth bond を実際に作成している場合、自動再ペアリングの確認対象になる。
- アプリ内の「カメラ登録」がアプリ内だけの登録、または bond を作らない GATT 接続にとどまり、`BluetoothDevice.getBondState()` が `BOND_NONE` のままであれば、この Behavior Change の直接的な影響は小さい。
- システムによる自動修復中に、アプリが従来の手動再登録を開始すると、システムの通知 / ダイアログとアプリ UI の重複、登録処理のループ、Bluetooth 復旧後の Wi-Fi 接続への引き継ぎ失敗が起こる可能性がある。

確認項目:
- カメラ登録後に Android 側の状態が `BOND_BONDED` になるのか、それとも bond を作らない GATT 接続またはアプリ内だけの登録なのかを確認する。
- スマートフォン側の登録を残したまま、カメラ側のペアリング情報だけを削除し、接続先で発生する bond loss を再現する。
- システムによる自動修復の成功後に、Bluetooth の再接続、Wi-Fi 接続への引き継ぎ、リモート撮影、画像転送が正常に復旧することを確認する。
- テスト用周辺機器でセキュリティレベルを変更できる場合は、以前より低いセキュリティレベルで再ペアリングしても、既存の鍵が置き換えられないことを確認する。
- システムによる自動修復の失敗後、またはユーザーが拒否した後に、`ACTION_KEY_MISSING` と手動登録の案内が適切な順序で動くことを確認する。
- Image App は、Wi-Fi のみで接続する機種と Bluetooth 対応機種を分けてテストする。

外部公式資料:
- LUMIX Sync の Bluetooth ペアリング: https://av.jpn.support.panasonic.com/support/global/cs/soft/lumix_sync/en/DC-BS1H/connect_bt.html
- LUMIX Sync の対応 OS / 対応機種: https://av.jpn.support.panasonic.com/support/global/cs/soft/lumix_sync/en/index.html
- Image App の Wi-Fi 接続: https://av.jpn.support.panasonic.com/support/global/cs/soft/image_app/dsc/android/android01.html
- Image App の Bluetooth ペアリング: https://av.jpn.support.panasonic.com/support/spn/global/dsc/help/image_app/en/camera/shared_1/connect_1.html?css=style1&no=1

注意:
- Panasonic アプリのソースコードは確認していない。上記は公開された接続仕様から導いた影響の仮説であり、特定のバージョンですでに問題が発生していることを示すものではない。
- LUMIX Sync の公式サポートページは、調査時点で Android 10〜16 を対応 OS として掲載している。そのため、Android 17 全体との互換性テストも別途必要である。

---

# 検証計画（Testing）

| ケース | 操作 | 期待結果 |
| --- | --- | --- |
| 通常のペアリング | 通常の初回ペアリングを行う | 通常のペアリングとして完了し、自動修復と誤認しない。 |
| 自動修復の成功 | 周辺機器側の bond 情報だけを削除する | システム UI / pairing context を経て `BOND_BONDED` に復旧し、`ACTION_KEY_MISSING` は届かない。 |
| 自動修復の失敗 | 周辺機器を応答不能にするか、ペアリングを失敗させる | 自動再ペアリングの失敗後に `ACTION_KEY_MISSING` が届き、アプリが手動復旧へ切り替えられる。 |
| ユーザーによる拒否 | システムの確認画面で拒否する | アプリの状態が自動修復中のまま残らず、手動での復旧を案内できる。 |
| アプリとシステムの競合 | システムによる自動修復中にアプリの復旧経路を観測する | アプリが `createBond()`、手動のペアリング解除、ダイアログを重複して開始しない。 |

期待する状態遷移の一例は `bond loss detection -> repairing context -> BOND_BONDING -> BOND_BONDED` である。ただし、最初にアプリから観測できる `BOND_NONE` が broadcast されるかどうかや、各 broadcast の順序とタイミングは、端末、周辺機器、Bluetooth module の設定に依存する。そのため、実機で観測した順序を記録する。

公式文書が示す bond loss の再現方法は、周辺機器側の bond 情報を削除する方法、または Android の Settings > Connected devices からデバイスのペアリングを手動で解除する方法である。接続先で bond 情報が失われた場合の復旧を重点的に確認するには、スマートフォン側の bond 情報を残したまま、周辺機器側だけを削除する方法を優先する。

---

# 追加調査 TODO

- 実機または Bluetooth module test で successful re-pairing / failed re-pairing / user rejection の broadcast timing を確認する。
- release config における `autonomous_repairing_initiation` flag default を確認する。
- device vendor / peripheral ごとの bond loss reason と retry behavior を確認する。
- 再ペアリング後のセキュリティレベルの比較と、既存の鍵が置き換えられる条件を Bluetooth module / テスト用周辺機器で確認する。

---

# 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- 人間による判断が必要

判断（Decision）:
- 未判断

---

## 再検証記録（2026-08-22）

### 調査日（Investigation Date）

- 2026-08-22

### 公式ドキュメント再確認（Original Documentation Recheck）

- Android 17 の all-apps / target Behavior Change ページを再取得し、このレポートが参照する公式 section の掲載と適用範囲を再確認した。
- 公式ページの最終更新表示: all-apps / target: 2026-08-14 UTC。
- Android 17 compat framework 一覧は 2026-08-22 時点でも HTTP 404 のため、公式 Behavior Change 文書と AOSP annotation / gate を正とした。
- 既存の引用は短い要約として扱い、適用条件は公式ページ種別と AOSP gate の両方で再評価した。

### AOSP 証拠ワークスペース（AOSP Evidence Workspaces）

| AOSP project | Official remote URL | Checkout path | Working tree | From tag / resolved commit | To tag / resolved commit | Comparison command | Dirty risk / limitations |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `platform/frameworks/base` | `https://android.googlesource.com/platform/frameworks/base` | `frameworks-base/` | Clean | `android-16.0.0_r4` / `45034f0663f960d9ee5fb0a101a4732b71f6e2f4` | `android-17.0.0_r1` / `94b4c163b7dfe5ce3607f7bb8456f9573f7de57d` | `git -C frameworks-base diff --no-renames --name-only android-16.0.0_r4 android-17.0.0_r1` | なし。明示タグ比較のため working tree の内容は根拠に含めない。 |
| `platform/packages/modules/Bluetooth` | `https://android.googlesource.com/platform/packages/modules/Bluetooth` | `tmp/aosp-checkouts/Bluetooth/` | 展開中 | `android-16.0.0_r4` / `5323f31677c7dfa04de2e6e9fce1012ef4edaff2` | `android-17.0.0_r1` / `c77db469de80f86660bc053bec4dee0c5d4b947c` | `git -C tmp/aosp-checkouts/Bluetooth diff --no-renames --name-only android-16.0.0_r4 android-17.0.0_r1` | 部分クローンの working tree 展開中。根拠は解決済みタグの object 比較だけを使用し、展開途中のファイルを含めない。 |

### ソース文脈・差分解釈の再確認（Source Context Reviewed / Diff Interpretation）

- 各 official remote で Android 16 / 17 の最新通常リリースタグが `android-16.0.0_r4` / `android-17.0.0_r1` のままであることを確認した。
- 上表の project-level `--name-only` 比較を再実行し、既存本文の path / symbol 別 source context、gate、追加・削除・条件変更・既定値変更・差分なしの解釈を再確認した。
- タグと解決済み commit が既存調査の比較対象から変わっていないため、本文の evidence record を別タグへ機械的に置換していない。
- 実機 Observed は新規実施していない。既存の「未実施」「未確認」および不足根拠はそのまま維持した。

### 事実（Facts）

- `android-16.0.0_r4` と `android-17.0.0_r1` は 2026-08-22 時点の最新通常リリースタグである。
- 上表に再検証時の working tree 状態を記録し、official remote、両タグ、解決済み commit を確認した。展開中または dirty の working tree は根拠に使用していない。
- 公式 section と AOSP evidence の比較 pair は一致している。

### 観察（Observations）

- 最新タグが変わっていないため、今回の再検証で既存の source diff 解釈を変更する新しい AOSP tag evidence は生じなかった。
- report 内に残る Medium / Low confidence、OEM / Mainline / QPR 条件、未確認の module enforcement は解消したものとして扱わない。

### 仮説（Hypotheses）

- 新しい仮説は追加しない。既存本文で仮説または可能性として記載した事項は、実機・製品 build・未確認 module の evidence が得られるまで事実へ昇格しない。

### 結論（Conclusions）

- 既存本文の主分類、confidence、対応候補を維持する。既存の不足根拠がある場合はその制約も維持する。
- 全件再検証の横断記録は [`android17/analysis/REVALIDATION_2026-08-22.md`](../../../analysis/REVALIDATION_2026-08-22.md) を参照する。

### Human Decision

- この再検証では最終 priority、severity、release readiness、顧客説明優先度を変更していない。
- 人間の判断は [Android 17 Decision Log](../../../decisions/DECISION_LOG.md) を正とする。
