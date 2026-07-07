# BC-003: New intents to handle bond loss and encryption changes

## 基本情報

Behavior Change 文書:
- URL: https://developer.android.com/about/versions/16/behavior-changes-16#new-intents-to-handle-bond-loss
- Section: New intents to handle bond loss and encryption changes

既存調査:
- [android16/behavior-changes/target/connectivity/new-intents-to-handle-bond-loss-and-encryption-changes.md](../../../behavior-changes/target/connectivity/new-intents-to-handle-bond-loss-and-encryption-changes.md)
- [android16/summaries/target/connectivity/new-intents-to-handle-bond-loss-and-encryption-changes-summary.md](../../../summaries/target/connectivity/new-intents-to-handle-bond-loss-and-encryption-changes-summary.md)

## 対象アプリとの関係

関連するアプリ機能:
- Bluetooth reconnect state machine。
- ペアリング復旧 UI。
- BLE / GATT 暗号化状態に依存する制御チャネル。
- customer support / analytics。

アプリが該当する可能性:
- Conditional。Bluetooth bonded device を扱い、Android 16 の新 signal を取り込む場合に関係する。

## 適用条件分類

主分類:
- 既存調査では `OS_UPDATE_ALL_APPS`。API 採用面では compile / target SDK 36 が関係する。

OS update と targetSdkVersion:
- AOSP broadcast path に明確な targetSdkVersion 36 gate は見つかっていない。
- API 定数を通常参照するには Android 16 SDK / API 36 採用が現実的な前提。

Confidence:
- Medium。OEM implementation variation が公式に示されているため。

## AOSP / 公式根拠

既存 Android16 調査で確認済み:
- `BluetoothDevice.ACTION_KEY_MISSING`
- `BluetoothDevice.ACTION_ENCRYPTION_CHANGE`
- `EXTRA_BOND_LOSS_REASON`
- encryption status / algorithm / key size extras
- `RemoteDevices.keyMissingCallback()`
- `RemoteDevices.encryptionChangeCallback()`
- Bluetooth ChangeIds に該当 compat gate は見つからない。

## アプリ影響

想定される影響:
- remote bond loss / encryption change をより明示的に扱える。
- 既存の `ACTION_BOND_STATE_CHANGED` だけに依存すると Android 16 の retained bond path を見逃す可能性。
- OEM により broadcast 有無やタイミングが変わる可能性。

推奨対応:
- `ACTION_KEY_MISSING` / `ACTION_ENCRYPTION_CHANGE` を受けられる場合は取り込む。
- 受けられない場合の fallback として disconnect / auth failure / bond state を残す。
- `BLUETOOTH_CONNECT` permission と receiver registration を確認する。

## テスト観点

- Android 16 / targetSdkVersion 35 / action string receiver。
- Android 16 / targetSdkVersion 36 / API 定数利用。
- remote bond loss。
- encryption disabled / enabled transition。
- OEM device 差。

## Human Decision

- Final priority: TBD by human
- Release readiness impact: TBD by human
