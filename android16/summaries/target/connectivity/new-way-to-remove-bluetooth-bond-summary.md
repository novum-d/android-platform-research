# CompanionDeviceManager による Bluetooth bond 削除 API - 1ページ要約

## 対象

- Android 15 `android-15.0.0_r36` -> Android 16 `android-16.0.0_r4`
- 公式文書: https://developer.android.com/about/versions/16/behavior-changes-16#bond-removal-api
- 主レポート: [CompanionDeviceManager による Bluetooth bond 削除 API](../../../behavior-changes/target/connectivity/new-way-to-remove-bluetooth-bond.md)

## 適用条件

- 主分類: `API_ADDITION_ONLY`
- OS update だけで既存アプリへ適用: No
- targetSdkVersion 36 の runtime gate: AOSP では確認できない
- 必須条件: CDM association、device MAC address、`BLUETOOTH_CONNECT`、明示的な API 呼び出し
- Compat Change ID: なし
- Confidence: Medium

## 要約

Android 16 では、CDM association で管理している Bluetooth device に対して `CompanionDeviceManager.removeBond(associationId)` を呼び、bond 削除を要求できる。これは自動的な挙動変更ではなく、アプリが採用する新しい公開 API である。

API は非同期である。戻り値 `true` は削除完了ではなく開始要求を受け付けたことを示し、最終状態は `ACTION_BOND_STATE_CHANGED` で確認する。CDM association の削除と Bluetooth bond の削除は別操作として管理する。

## シナリオマトリクス

| シナリオ | 期待結果 |
| --- | --- |
| API を呼ばない既存アプリ | 挙動変更なし。 |
| 有効な association + permission + MAC address | bond 削除の非同期処理を開始し得る。 |
| association を管理できない | service の caller check により許可されない。 |
| association に MAC address がない | `IllegalArgumentException`。 |
| `removeBond()` が `true` を返す | 完了ではない。broadcast で最終状態を確認する。 |

## 顧客影響

- CDM で Bluetooth 周辺機器を管理し、アプリ内に unpair 導線を持つ場合は採用候補。
- Bluetooth bond を扱わない、または system Settings に任せるアプリは対応不要。
- bond、connection、CDM association を一つの状態として扱う既存実装は状態遷移の整理が必要。

## 対応候補

- 既存 architecture の device repository / use case に API 呼び出しを組み込む。
- 戻り値の即時エラーと broadcast による完了結果を分ける。
- association 削除を同時に行うかは製品要件として別途判断する。
- Android 15 / 16 SDK artifact で API 公開差を確認し、minSdk / compileSdk の条件をコード側で表す。

## 根拠

- 公式 Android 16 Behavior Change section。
- `CompanionDeviceManager.removeBond(int)`、`ICompanionDeviceManager.removeBond(...)`。
- `CompanionDeviceManagerService.removeBond(...)` の association ownership / MAC address / `BluetoothDevice.removeBond()` 経路。
- 比較元と比較先の両タグに `@FlaggedApi` 付き source があるため、source追加ではなく API 公開・採用機会として分類。

## Facts / Observations / Hypotheses / Conclusions

- Facts: Android 16 公式文書が public API と非同期監視方法を案内する。AOSP runtime target gate はない。
- Observations: Android 15 AOSP tag にも flagged source があるため、製品 SDK surface の確認が必要。
- Hypotheses: baseline tag の flagged surface は Android 15 一般 SDK の利用可否と一致しない可能性がある。
- Conclusions: `API_ADDITION_ONLY`。API を採用する CDM 管理アプリだけが対応対象。

## Human Decision

- Status: Pending Human Decision
- 最終優先度と採用可否は repository owner が決定する。

## 再検証記録（2026-08-22）

- Android 16 の公式 Behavior Change 一覧と最新通常AOSPタグを再確認した。
- 対応する[主レポート](../../../behavior-changes/target/connectivity/new-way-to-remove-bluetooth-bond.md)で official section、AOSP project / remote / checkout、解決済み commit、比較 command、dirty risk を再検証した。
- 主レポートの分類、confidence、未確認事項を維持し、実機未実施の項目を Observed 済みへ変更していない。
- 全件の結果は[再検証台帳](../../../analysis/REVALIDATION_2026-08-22.md)を参照する。
