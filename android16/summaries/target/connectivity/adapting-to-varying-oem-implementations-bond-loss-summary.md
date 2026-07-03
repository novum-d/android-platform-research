# Adapting to varying OEM implementations - 1ページ要約

## 対象

Android 16 Behavior Change

From:
- android-15.0.0_r36

To:
- android-16.0.0_r4

Document:
- https://developer.android.com/about/versions/16/behavior-changes-16#bond-loss-oem-impletations

## 適用条件

- 主分類: `OS_UPDATE_ALL_APPS`
- OS アップデート / 全アプリ: Conditional。Android 16 Bluetooth stack 側に `ACTION_KEY_MISSING` path があるが、Bluetooth bonded device と該当 event handling があるアプリに限られる。
- targetSdkVersion 36 以上: runtime gate としては未確認。API 36 public constants を正式利用するための開発条件。
- その他の必須条件: bonded Bluetooth device、remote bond loss、receiver / permission、OEM が `ACTION_KEY_MISSING` を broadcast するかどうか。
- Compat Change ID: 該当なし
- Compat default state: 該当なし

## 早見マトリクス

| シナリオ | 影響 |
| --- | --- |
| Android 16 / targetSdkVersion 35 | target gate は見つからない。action string と receiver 条件を満たせば受信可能性あり。 |
| Android 16 / targetSdkVersion 36 | `ACTION_KEY_MISSING` / `ACTION_ENCRYPTION_CHANGE` を public API として実装可能。OEM により broadcast 有無は変動し得る。 |
| Android 15 / targetSdkVersion 36 | Android 16 の標準 bond loss path はない。Android 15 tag では flagged / flags dependent path と legacy key removal path。 |

## 要約

この項目は、新 intent の追加そのものではなく、`ACTION_KEY_MISSING` が届く端末と届かない端末の両方に対応する必要がある点を扱う。AOSP path では `ACTION_KEY_MISSING` 後に ACL link が切断され bond information は保持されるが、OEM により broadcast されない場合は Android 15 と同様の fallback が必要。

## 顧客影響

- 影響あり: bonded Bluetooth device の reconnect / re-pairing / forget flow を持つアプリ。
- 要確認: `ACTION_BOND_STATE_CHANGED`、ACL disconnect、connection failure のみに依存しているアプリ。
- 影響なし: Bluetooth bonding を扱わないアプリ。

## 影響対象

- bonded Bluetooth device を扱うアプリ
- BLE / Classic Bluetooth peripheral と reconnect するアプリ
- `ACTION_BOND_STATE_CHANGED` のみに依存するアプリ
- `ACTION_ACL_CONNECTED` / `ACTION_ACL_DISCONNECTED` に依存するアプリ
- `ACTION_KEY_MISSING` / `ACTION_ENCRYPTION_CHANGE` を使うアプリ
- remote bond loss を user guidance / re-pairing flow に反映するアプリ
- OEM device 差を吸収する必要がある Bluetooth アプリ

## 対応要否

- 必須対応候補: bonded Bluetooth device を扱う場合、`ACTION_KEY_MISSING` あり / なしの両方を state machine に入れる。
- 推奨対応: `ACTION_ENCRYPTION_CHANGE` の successful encryption を bond restored signal として扱う。
- 不要: Bluetooth bonding / reconnect flow を持たないアプリ。

## テストマトリクス

| 端末 OS | targetSdkVersion | 期待挙動 |
| --- | --- | --- |
| Android 15 | 35 | 従来挙動。legacy bond loss handling を確認。 |
| Android 16 | 35 | target gate なしのため受信可能性あり。OEM 差分を確認。 |
| Android 16 | 36 | new intent を public API として実装し、fallback と併用。 |

追加テスト:
- `ACTION_KEY_MISSING` broadcast あり / なし
- `ACTION_ENCRYPTION_CHANGE` success / failure
- ACL link disconnected / retained
- bond information retained / removed
- `ACTION_BOND_STATE_CHANGED` sequence
- `ACTION_KEY_MISSING` 後の reconnect
- OEM / device / Bluetooth chipset 差
- background receiver と runtime receiver
- `BLUETOOTH_CONNECT` permission

## 顧客向け説明

Android 16 では、remote bond loss 検出時に `ACTION_KEY_MISSING` が届く場合があります。この場合、アプリはそれを primary signal として扱い、すぐに自動 reconnect するのではなく、ユーザーに remote device 側の bond 状態確認や re-pair を案内するのが安全です。

ただし、すべての OEM/device で `ACTION_KEY_MISSING` が届くとは限りません。届かない場合に備えて、Android 15 と同様の `ACTION_BOND_STATE_CHANGED`、ACL disconnect、connection failure による fallback handling を残す必要があります。

## 根拠

- Official documentation: Android 16 target apps / Connectivity / Adapting to varying OEM implementations
- AOSP files: `BluetoothDevice.java`, `RemoteDevices.java`, `btm_sec.cc`, `framework/api/current.txt`, `ChangeIds.java`
- AOSP source context: HCI key missing / encryption change -> Bluetooth stack callback -> `RemoteDevices` -> Android broadcast
- Diff interpretation: Android 16 AOSP path は `ACTION_KEY_MISSING` broadcast + ACL disconnect。Android 15 baseline は flagged / legacy key removal path。
- Gate conclusion: targetSdkVersion 36 runtime gate は未確認。OEM variation は公式文書上の追加条件。

## Facts / Observations / Hypotheses / Conclusions

Facts:
- 公式文書は OEM により implementation / broadcasting が異なる可能性を明記。
- Android 16 AOSP には `ACTION_KEY_MISSING` broadcast と ACL disconnect path がある。
- Android 15 AOSP には key missing 時に bond key 情報を消す legacy branch がある。
- Compat Change ID は確認できない。

Observations:
- `ACTION_KEY_MISSING` が届く場合と届かない場合で app state machine を分ける必要がある。
- AOSP 内にも app/device specific workaround があり、実装差への注意が必要。

Hypotheses:
- 公式の targetSdkVersion 36 条件は public API 採用条件を指し、runtime broadcast gate ではない可能性が高い。

Conclusions:
- New intent を primary signal として使いつつ、legacy fallback を必ず残すべき。
- OS update 影響と targetSdkVersion 36 化による API 採用を分けて説明する。

## 人間の判断欄

最終優先度:
- 未判断

判断:
- Human decision required

補足:
- 複数 OEM / chipset の検証要否と顧客説明の優先度は人間が判断する。
