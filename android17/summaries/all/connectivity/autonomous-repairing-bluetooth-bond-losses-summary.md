# Bluetooth bond loss に対する autonomous re-pairing - 1ページ要約

## 対象

Android 17 Behavior Change

比較元:
- android-16.0.0_r4

比較先:
- android-17.0.0_r1

## 適用条件

- 主分類（Primary classification）: OS_UPDATE_ALL_APPS
- OS アップデート / 全アプリ（OS update / all apps）: 公式文書上は該当候補。targetSdkVersion 条件なし。
- targetSdkVersion 37 以上: 公式文書上は不要。
- その他の必須条件: Bluetooth peripheral bond loss、system autonomous re-pairing attempt、Bluetooth module feature flag が有効、companion app の pairing / key missing handling。
- Compat Change ID: 見つからない。AOSP 根拠 は Bluetooth module feature flag と platform flag。
- Confidence: High

## 要約

Android 17 では、Bluetooth bond loss 後に system が autonomous re-pairing を試行できる。`ACTION_PAIRING_REQUEST` の context と `ACTION_KEY_MISSING` の timing が変わるため、companion app / peripheral app は recovery flow を確認する必要がある。

Bluetooth module では `EXTRA_PAIRING_CONTEXT`、`PAIRING_CONTEXT_REPAIRING`、bond loss 検出後の autonomous repairing、失敗時の `ACTION_KEY_MISSING` broadcast path を確認した。targetSdkVersion ゲートは見つからないため、OS 更新で Bluetooth bond loss recovery flow に影響する all-apps change と扱う。

## 根拠（Evidence）

- 公式ドキュメント: https://developer.android.com/about/versions/17/behavior-changes-all
- AOSP checkout: `frameworks-base` と `tmp/aosp-checkouts/Bluetooth` の `android-16.0.0_r4` / `android-17.0.0_r1` tag を確認。
- AOSP: `platform/packages/modules/Bluetooth` の `BluetoothDevice.java` に `EXTRA_PAIRING_CONTEXT`、`PAIRING_CONTEXT_USER_PARTICIPATION_REQUESTED`、`PAIRING_CONTEXT_USER_APPROVAL_REQUESTED`、`PAIRING_CONTEXT_REPAIRING` が追加。
- AOSP: `BondStateMachine.java` は autonomous repairing 時に pairing context を `ACTION_PAIRING_REQUEST` / bond state change intent に含める。
- AOSP: `RemoteDevices.java` は bond loss 検出時に autonomous repairing を開始し、repairing 失敗時に `ACTION_KEY_MISSING` を送る path を持つ。
- AOSP: `flags/framework.aconfig` の `autonomous_repairing_initiation` flag は bond loss 検出時の autonomous re-pairing initiation を説明する。
- AOSP: `packages/SettingsLib` に `EXTRA_PAIRING_CONTEXT` / `PAIRING_CONTEXT_REPAIRING` を Bluetooth 診断表示で扱う差分があるが、Bluetooth stack 実装ではない。
- 残る確認事項: release build での flag default / device config override と、実機での peripheral 別 recovery 結果。

## 対応候補（Action Candidates）

- manual unpair / re-pair guidance を棚卸しする。
- `EXTRA_PAIRING_CONTEXT` で standard pairing と autonomous re-pairing attempt を区別する。
- `ACTION_KEY_MISSING` が failed autonomous re-pairing 時だけ届く前提でテストする。

## 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- 人間による判断が必要

判断（Decision）:
- 未判断
