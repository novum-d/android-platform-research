# BC-002: Improved bond loss handling

## 基本情報

Behavior Change 文書:
- URL: https://developer.android.com/about/versions/16/behavior-changes-all#improved-bond-loss-handling
- Section: Improved bond loss handling

既存調査:
- [android16/behavior-changes/all/connectivity/improved-bond-loss-handling.md](../../../behavior-changes/all/connectivity/improved-bond-loss-handling.md)
- [android16/summaries/all/connectivity/improved-bond-loss-handling-summary.md](../../../summaries/all/connectivity/improved-bond-loss-handling-summary.md)

## 対象アプリとの関係

関連するアプリ機能:
- Bluetooth 初期ペアリング。
- BLE / GATT または Bluetooth Classic によるカメラ制御。
- Wi-Fi 起動、時刻同期、位置情報連携、再接続の補助。
- カメラ factory reset / bond reset 後の復旧。

アプリが該当する可能性:
- Conditional。bonded Bluetooth device を扱う場合は該当可能性が高い。

## 適用条件分類

主分類:
- `OS_UPDATE_ALL_APPS`

OS update と targetSdkVersion:
- Android 16 OS 上で remote bond loss / authentication failure が起きる場合、targetSdkVersion 35 / 36 の両方が影響対象になり得る。
- targetSdkVersion 36 化そのものの影響ではない。

Confidence:
- High。

## AOSP / 公式根拠

既存 Android16 調査で確認済み:
- `btm_sec_report_bond_loss()` 追加。
- `ACTION_KEY_MISSING` 送出。
- key missing count 記録。
- ACL / GATT disconnect reason の auth failure 変換。
- `BondLossTest` は remote bond loss 後も bonded devices list に残ることを検証。
- Settings の `BluetoothKeyMissingReceiver` / dialog path。
- targetSdkVersion gate / compat framework gate は確認できない。

## アプリ影響

想定される影響:
- remote bond loss 直後に `BOND_NONE` へ落ちる前提が崩れる。
- system が自動で bond を削除して再ペアリングを開始する前提が崩れる。
- app 独自 re-pair UI と system dialog が競合する可能性。
- connection failure analytics が `auth failure` として見える可能性。

推奨対応:
- `ACTION_BOND_STATE_CHANGED` / `BOND_NONE` だけで bond loss を判定しない。
- `ACTION_KEY_MISSING`、GATT / profile auth failure、disconnect callback、system dialog を含めて扱う。
- aggressive retry を避け、user-driven re-pairing と整合させる。

## テスト観点

- Android 15 / targetSdkVersion 35 baseline。
- Android 16 / targetSdkVersion 35。
- Android 16 / targetSdkVersion 36。
- remote device bond deleted / factory reset / key missing。
- normal disconnect / reconnect。
- local user unpair / forget。
- `BOND_BONDED` / `BOND_NONE` transition。
- system bond loss dialog。

## Human Decision

- Final priority: TBD by human
- Release readiness impact: TBD by human
