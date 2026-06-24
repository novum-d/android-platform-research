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
- pairing / bond loss recovery / key missing broadcast を扱うアプリ

対応候補:
- manual unpair / re-pair guidance を棚卸しする。
- `ACTION_PAIRING_REQUEST` の `EXTRA_PAIRING_CONTEXT` を見て standard pairing と autonomous re-pairing を区別する。
- `ACTION_KEY_MISSING` が successful autonomous recovery では届かない前提で error handling を見直す。
- Android 17 device で bond loss、successful re-pairing、failed re-pairing、user confirmation flow をテストする。

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

---

# 追加調査 TODO

- 実機または Bluetooth module test で successful re-pairing / failed re-pairing / user rejection の broadcast timing を確認する。
- release config における `autonomous_repairing_initiation` flag default を確認する。
- device vendor / peripheral ごとの bond loss reason と retry behavior を確認する。

---

# 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- 人間による判断が必要

判断（Decision）:
- 未判断
