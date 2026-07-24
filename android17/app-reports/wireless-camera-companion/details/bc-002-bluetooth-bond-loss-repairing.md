# BC-002: Autonomous re-pairing for Bluetooth bond losses

## 基本情報（Basic Information）

Behavior Change 文書:
- URL: https://developer.android.com/about/versions/17/behavior-changes-all
- Section: Autonomous re-pairing for Bluetooth bond losses

Original statement:
> Android 17 では Bluetooth bond loss 後に system が autonomous re-pairing を試行できる、という趣旨の公式説明。

調査対象 Android バージョン:
- From: android-16.0.0_r4
- To: android-17.0.0_r1

## 対象アプリとの関係（Relevance to Target App）

関連するアプリ機能:
- Bluetooth pairing。
- 接続復旧。
- カメラとの再接続。
- ユーザーへの再ペアリング案内。

関連する API / permission / component:
- `ACTION_PAIRING_REQUEST`
- `ACTION_KEY_MISSING`
- `EXTRA_PAIRING_CONTEXT`
- `PAIRING_CONTEXT_REPAIRING`

アプリが該当する可能性:
- Conditional。Bluetooth pairing / bond state / key missing を扱う場合は該当可能性が高い。

判断理由:
- カメラ連携アプリでは Bluetooth を初期接続、Wi-Fi 起動、時刻同期、位置情報連携、再接続の補助に使う可能性がある。bond loss recovery flow の変化は UX に影響しうる。

公開されているカメラ連携アプリとの比較:
- Panasonic LUMIX Sync は、カメラと Bluetooth Low Energy でペアリングし、登録済みカメラとの Bluetooth 接続を起点に Wi-Fi 接続を確立する。カメラがスリープから復帰した後は、Bluetooth 接続を自動的に再確立すると説明されている。
- Panasonic Image App の接続方式は機種によって異なり、QR コード / NFC / SSID を使う Wi-Fi のみの接続と、Bluetooth ペアリングから Wi-Fi 接続へ引き継ぐ方式がある。Bluetooth 対応機種では、リモートシャッター、リモート起動、自動転送、位置情報の記録、時刻同期などが Bluetooth 接続に依存する。
- 対象アプリも同様の構成で Android の Bluetooth bond を作成する場合は、この変更を直接確認する必要がある。アプリ内だけで機器を登録する場合や、bond を作らずに GATT 接続だけを使う場合は、直接的な影響が小さい。

## 適用条件分類（Applicability Classification）

主分類（Primary classification）:
- OS_UPDATE_ALL_APPS

早見表（At-a-glance impact）:

| 確認項目（Question） | 回答（Answer） | 根拠（Evidence） |
| --- | --- | --- |
| Android 17 に OS アップデートしただけで適用されるか | Yes / Conditional | 公式文書は all apps。Bluetooth module evidence に targetSdkVersion gate は見つからない。 |
| targetSdkVersion 37 以上が必要か | No | targetSdkVersion gate は確認されない。 |
| 追加の実行時条件があるか | Yes | Bluetooth peripheral bond loss、system autonomous re-pairing attempt、feature flag。 |
| Compat Change ID が関係するか | No | compat Change ID は見つからない。 |

必要な実行時条件（Required runtime conditions）:
- Android version: Android 17。
- targetSdkVersion: 条件なし。
- Device/form factor: Bluetooth peripheral と bonding が必要。
- Permission/API/component condition: Bluetooth pairing / bond state handling。
- App state/process condition: bond loss / reconnect / pairing recovery。
- Manifest/property condition: Bluetooth permission / receiver 設計は要確認。
- Mainline/module condition: Bluetooth module feature flag の release default は要確認。

Compat framework:
- Change ID: 見つからない。
- Change name: N/A
- Default state: Bluetooth module feature flag に依存。
- Toggleable for testing: 要確認。

## AOSP 調査（AOSP Investigation）

関連ファイル:
- `platform/packages/modules/Bluetooth/framework/java/android/bluetooth/BluetoothDevice.java`
- `platform/packages/modules/Bluetooth/android/app/src/com/android/bluetooth/btservice/BondStateMachine.java`
- `platform/packages/modules/Bluetooth/android/app/src/com/android/bluetooth/btservice/RemoteDevices.java`
- `platform/packages/modules/Bluetooth/flags/framework.aconfig`

確認したソース文脈（Source Context Reviewed）:

| ファイル / シンボル（File / symbol） | Android 16 の基準挙動（baseline） | Android 17 の挙動 | このコードパスを根拠にする理由 |
| --- | --- | --- | --- |
| `BluetoothDevice` / pairing context extras | pairing context extras なし | `EXTRA_PAIRING_CONTEXT` と `PAIRING_CONTEXT_REPAIRING` などが追加 | アプリが pairing request の文脈を判別できる公開 API。 |
| `BondStateMachine` | autonomous repairing context を intent に含めない | pairing request / bond state change intent に context を含める | アプリが受け取る broadcast 内容が変わる。 |
| `RemoteDevices` | bond loss 復旧 path が限定的 | bond loss 検出時に autonomous repairing を開始し、失敗時に `ACTION_KEY_MISSING` を送る path | 接続復旧 UI / recovery flow に直接関係する。 |

必須記入項目:
- Entry point / caller: Bluetooth stack の bond loss detection -> autonomous repairing -> pairing request / key missing broadcast。
- Relevant class or service responsibility: Bluetooth pairing / bonding state 管理。
- Runtime path from app API / system event to changed code: peripheral bond loss -> system repair attempt -> broadcast / UI flow。
- Why unrelated code paths were excluded: RFCOMM read EOF は別 Behavior Change として分離。

差分解釈（Diff Interpretation）:
- Added behavior: autonomous repairing と pairing context extras。
- Changed condition / gate: Bluetooth module feature flag。

適用ゲート根拠（Applicability Gate Evidence）:
- targetSdkVersion gate: 見つからない。
- CompatChanges.isChangeEnabled / ChangeId: 見つからない。
- No gate found: targetSdkVersion gate は確認されず、OS update / all apps と扱う。
- Gate conclusion: Android 17 の対象 Bluetooth module で bond loss 条件が成立する場合に適用。

## 事実・観察・仮説・結論（Facts / Observations / Hypotheses / Conclusion）

事実（Facts）:
- Android 17 Bluetooth module に pairing context extras と autonomous repairing path が追加されている。
- targetSdkVersion gate は見つからない。

観察（Observations）:
- 対象アプリが bond state や pairing broadcast に依存する場合、Android 17 OS 更新だけで復旧 flow が変わる可能性がある。

仮説（Hypotheses）:
- 手動再ペアリング案内を固定的に出す実装では、system repair attempt 中の UI と競合する可能性がある。

結論（Conclusion）:
- Bluetooth 接続復旧の実機テストが必要。OS update impact として優先度は高い。

## アプリ影響（App Impact）

想定される影響:
- bond loss 後、アプリ側が想定する manual recovery 前に system repair attempt が発生する。
- `ACTION_KEY_MISSING` の timing が変わる。

ユーザー影響:
- 再接続時の案内、ダイアログ、ペアリング要求が従来と異なる可能性。

開発者影響:
- pairing context を見て repairing と通常 pairing を区別する実装が望ましい。

既存実装で確認すべき点:
- ペアリング / bond state の receiver。
- key missing の処理。
- 手動でのペアリング解除 / 再ペアリング手順。
- `ACTION_BOND_STATE_CHANGED` / `getBondState()` の `BOND_NONE`、`BOND_BONDING`、`BOND_BONDED` 分岐。
- `BOND_NONE` で即座に `createBond()`、手動のペアリング解除、独自のペアリング UI を開始していないか。
- Android 17 の `EXTRA_PAIRING_CONTEXT=PAIRING_CONTEXT_REPAIRING` を通常の初回ペアリングと区別できるか。

検索候補:

```bash
rg -n "ACTION_BOND_STATE_CHANGED|EXTRA_BOND_STATE|EXTRA_PREVIOUS_BOND_STATE|getBondState|BOND_NONE|BOND_BONDING|BOND_BONDED|createBond|ACTION_PAIRING_REQUEST|ACTION_KEY_MISSING|EXTRA_PAIRING_CONTEXT|PAIRING_CONTEXT_REPAIRING"
```

推奨対応候補:
- `EXTRA_PAIRING_CONTEXT` を利用できる場合は context を区別する。
- bond loss、repairing 成功、repairing 失敗を実機で確認する。

推奨テスト:
- カメラを登録した後、Android 側の状態が `BOND_BONDED` になるのか、それとも bond を作らない GATT 接続またはアプリ内だけの登録なのかを確認する。
- スマートフォン側の登録を残したまま、カメラ側のペアリング情報だけを削除し、接続先で発生する bond loss を再現する。
- 自動修復に成功した場合は、`BOND_BONDING -> BOND_BONDED` への遷移、`ACTION_KEY_MISSING` が送信されないこと、Bluetooth の再接続、Wi-Fi 接続への引き継ぎ、リモート撮影、画像転送を確認する。
- テスト用カメラまたは周辺機器でセキュリティレベルを変更できる場合は、以前より低いセキュリティレベルで再ペアリングしても、既存の鍵が置き換えられないことを確認する。
- 自動修復の失敗時またはユーザーが拒否した場合は、`ACTION_KEY_MISSING` が届くタイミング、アプリによる手動登録への切り替え、システム UI とアプリ UI が重複しないことを確認する。
- Wi-Fi のみで接続するカメラと、Bluetooth 対応カメラを分けて検証する。

公開仕様の参照:
- LUMIX Sync の Bluetooth ペアリング: https://av.jpn.support.panasonic.com/support/global/cs/soft/lumix_sync/en/DC-BS1H/connect_bt.html
- LUMIX Sync のサポート情報 / 対応 OS: https://av.jpn.support.panasonic.com/support/global/cs/soft/lumix_sync/en/index.html
- Image App の Wi-Fi 接続: https://av.jpn.support.panasonic.com/support/global/cs/soft/image_app/dsc/android/android01.html
- Image App の Bluetooth ペアリング: https://av.jpn.support.panasonic.com/support/spn/global/dsc/help/image_app/en/camera/shared_1/connect_1.html?css=style1&no=1

事実と仮説の境界:
- 上記 Panasonic アプリの接続方式は、公開仕様で確認した事実である。
- 対象アプリが Android の bond、receiver、state machine をどのように利用しているかは、実装を確認できていない。
- Panasonic アプリ自体で不具合が発生することを確認したものではなく、カメラ連携アプリの構成を比較する例として扱う。

## Confidence

Confidence:
- High

Confidence の根拠:
- Bluetooth module evidence と targetSdkVersion gate 不在を確認済み。

不足している根拠:
- release build での flag default / device config override。
- 対象アプリ実装。
- Android 17 実機におけるカメラ周辺機器ごとの broadcast 順序と、Wi-Fi 接続への引き継ぎ結果。
- 再ペアリング後のセキュリティレベルの比較結果と、既存の鍵が置き換えられる条件の実機検証結果。

---
