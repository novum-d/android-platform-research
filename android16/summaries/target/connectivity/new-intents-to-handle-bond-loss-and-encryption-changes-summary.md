# New intents to handle bond loss and encryption changes - 1ページ要約

## 対象

Android 16 Behavior Change

From:
- android-15.0.0_r36

To:
- android-16.0.0_r4

Document:
- https://developer.android.com/about/versions/16/behavior-changes-16#new-intents-to-handle-bond-loss

## 適用条件

- 主分類: `OS_UPDATE_ALL_APPS`
- OS アップデート / 全アプリ: Conditional。Android 16 Bluetooth stack 側に broadcast 実装があり、targetSdk gate は見つからない。ただし Bluetooth bonded device と該当 event handling があるアプリに限られる。
- targetSdkVersion 36 以上: 実行時 gate としては未確認。API 36 public constants を正式に使うための開発条件。
- その他の必須条件: bonded Bluetooth device、remote bond loss または encryption change、`BLUETOOTH_CONNECT`、receiver 登録、OEM 実装差。
- Compat Change ID: 該当なし
- Compat default state: 該当なし

## 早見マトリクス

| シナリオ | 影響 |
| --- | --- |
| Android 16 / targetSdkVersion 35 | target gate は見つからないため、action string と receiver 条件を満たす場合は受信可能性あり。ただし API 36 constants としての正式利用は不可。 |
| Android 16 / targetSdkVersion 36 | `ACTION_KEY_MISSING` / `ACTION_ENCRYPTION_CHANGE` を public API として実装可能。 |
| Android 15 / targetSdkVersion 36 | Android 16 の Bluetooth stack behavior は保証されない。Android 15 tag では該当 API は flagged / broadcast は flags dependent。 |

## 要約

Android 16 では Bluetooth remote bond loss と link encryption change を通知する `ACTION_KEY_MISSING` / `ACTION_ENCRYPTION_CHANGE` が public API として利用可能になる。AOSP では targetSdkVersion 36 gate は見つからず、Android 16 の Bluetooth stack / event / receiver 条件に依存する。

## 顧客影響

- 影響あり: bonded Bluetooth device の reconnect、forget、re-pairing、encryption state handling を持つアプリ。
- 影響軽微またはなし: Bluetooth bonding を扱わないアプリ。
- 要確認: `ACTION_BOND_STATE_CHANGED` や disconnect event のみに依存して bond loss を推定しているアプリ。

## 影響対象

- Bluetooth bonded device を管理するアプリ
- paired peripheral と reconnect するアプリ
- `ACTION_BOND_STATE_CHANGED` のみに依存しているアプリ
- disconnect event で bond loss を推定しているアプリ
- device forgetting / re-pairing flow を持つアプリ
- encryption status / algorithm / key size を確認する必要があるアプリ
- OEM ごとの Bluetooth behavior 差に影響を受けるアプリ
- Companion Device Manager と組み合わせるアプリ

## 対応要否

- 必須対応候補: bonded Bluetooth device を扱う場合、`ACTION_KEY_MISSING` と `ACTION_ENCRYPTION_CHANGE` を評価する。
- 推奨対応: new intent を primary signal として追加しつつ、受信できない OEM/device 向けに legacy fallback を残す。
- 不要: Bluetooth bonding / reconnect flow を持たないアプリ。

## テストマトリクス

| 端末 OS | targetSdkVersion | 期待挙動 |
| --- | --- | --- |
| Android 15 | 35 | 従来挙動。new intent は public API として前提にしない。 |
| Android 16 | 35 | target gate なしのため受信可能性あり。ただし公式 API 採用は target/compile SDK 36 で確認。 |
| Android 16 | 36 | `ACTION_KEY_MISSING` / `ACTION_ENCRYPTION_CHANGE` を public API として受信・処理できる。 |

追加テスト:
- `ACTION_KEY_MISSING` broadcast 受信有無
- `ACTION_ENCRYPTION_CHANGE` broadcast 受信有無
- encryption status / algorithm / key size extra
- remote bond loss 時の ACL link と local bond information
- `ACTION_BOND_STATE_CHANGED` sequence
- `ACTION_KEY_MISSING` 後の reconnect
- `ACTION_ENCRYPTION_CHANGE` による bond restored 判定
- OEM / device / Bluetooth chipset 差
- foreground / background receiver behavior
- Bluetooth permission と receiver registration mode

## 顧客向け説明

Android 16 では Bluetooth の bond loss と encryption change をアプリが検知するための新しい intent が正式に使えるようになります。`ACTION_KEY_MISSING` が届く場合は、bond loss の primary signal として扱い、ユーザーに remote device 側の状態確認や re-pair を案内してください。

ただし `ACTION_KEY_MISSING` がすべての OEM/device で必ず broadcast されるとは限りません。新 intent を使いつつ、Android 15 と同様の `ACTION_BOND_STATE_CHANGED` や disconnect based fallback を残す必要があります。

## 根拠

- Official documentation: Android 16 target apps / Connectivity / New intents to handle bond loss and encryption changes
- AOSP files: `packages/modules/Bluetooth/framework/api/current.txt`, `BluetoothDevice.java`, `RemoteDevices.java`, `btm_sec.cc`, `bta_dm_sec.cc`, `btif_dm.cc`, `bluetooth.cc`
- AOSP source context: native HCI key missing / encryption change -> Bluetooth stack callback -> JNI -> `RemoteDevices` -> Android broadcast
- Diff interpretation: API surface の `@FlaggedApi` removal、broadcast gate removal、bond loss reporting path の追加/集約
- Gate conclusion: AOSP では targetSdkVersion 36 gate なし。Android 16 OS/module behavior + Bluetooth event/API usage 条件。

## Facts / Observations / Hypotheses / Conclusions

Facts:
- Android 16 API surface で `ACTION_KEY_MISSING` / `ACTION_ENCRYPTION_CHANGE` が flag なし public API。
- Android 16 `RemoteDevices` は key missing / encryption change broadcast を送る。
- Compat Change ID は確認できない。

Observations:
- 公式 target apps 文書にあるが、AOSP 実装は targetSdk gate より OS/module behavior に近い。
- OEM によって `ACTION_KEY_MISSING` broadcast 有無が異なる可能性が公式に明記されている。

Hypotheses:
- “Apps targeting Android 16 can now receive” は、API 36 SDK で public API として使えることを指す可能性が高い。

Conclusions:
- Bluetooth bonding を扱うアプリは new intent と legacy fallback を併用すべき。
- 顧客説明では OS アップデート影響と targetSdkVersion 36 化による API 採用を分ける。

## 人間の判断欄

最終優先度:
- 未判断

判断:
- Human decision required

補足:
- Bluetooth bonded device を扱う顧客アプリで優先度を人間が判断する。
