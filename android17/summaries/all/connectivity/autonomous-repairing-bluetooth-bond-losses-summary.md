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

公式文書によると、既存のセキュリティ鍵が置き換えられるのは、再ペアリングに成功し、新しい接続が以前の bond と同等以上のセキュリティレベルを満たす場合に限られる。セキュリティレベルの比較と鍵の置き換え条件については、Bluetooth module と周辺機器を使った検証が残っている。

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

- 手動でのペアリング解除 / 再ペアリング手順を棚卸しする。
- `EXTRA_PAIRING_CONTEXT` を使い、通常のペアリングと自動再ペアリングを区別する。
- `ACTION_KEY_MISSING` は自動再ペアリングに失敗した場合だけ届くことを前提にテストする。
- `ACTION_BOND_STATE_CHANGED` / `getBondState()` から `BOND_NONE`、`BOND_BONDING`、`BOND_BONDED` の全分岐を確認する。特に、`BOND_NONE` で即座に `createBond()` や独自のペアリング UI を開始する実装は、システムによる自動修復と競合する可能性がある。
- ペアリング / 復旧に関する broadcast や独自 UI を持たない一般的なアプリは、コード変更が必要になる可能性が低い。連携アプリでは、自動修復の成功 / 失敗、ユーザーによる拒否、システム UI とアプリ UI が重複しないことを確認する。

## カメラ連携アプリの例

- LUMIX Sync は、Bluetooth ペアリング、登録済みカメラ、Bluetooth を起点とした Wi-Fi 接続、スリープ復帰後の再接続を公開仕様としている。そのため、Android の Bluetooth bond を作成する機種では優先して確認する必要がある。
- Panasonic Image App は、Wi-Fi のみで接続する機種では直接影響を受けにくい。Bluetooth ペアリングを使う機種は、LUMIX Sync と同様に確認対象となる。
- カメラ側のペアリング情報だけを削除し、Bluetooth の自動修復後に、Wi-Fi 接続への引き継ぎ、リモート撮影、画像転送、手動登録への切り替えが正常に動くことを確認する。
- Panasonic アプリのソースコードは未確認であり、公開されている接続仕様に基づく影響の仮説である。

## 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- 人間による判断が必要

判断（Decision）:
- 未判断

## 再検証記録（2026-08-22）

- Android 17 の公式 Behavior Change 一覧と最新通常AOSPタグを再確認した。
- 対応する[主レポート](../../../behavior-changes/all/connectivity/autonomous-repairing-bluetooth-bond-losses.md)で official section、AOSP project / remote / checkout、解決済み commit、比較 command、dirty risk を再検証した。
- 主レポートの分類、confidence、未確認事項を維持し、実機未実施の項目を Observed 済みへ変更していない。
- 全件の結果は[再検証台帳](../../../analysis/REVALIDATION_2026-08-22.md)を参照する。
