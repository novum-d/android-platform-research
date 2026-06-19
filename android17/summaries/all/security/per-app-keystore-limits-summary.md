# Per-app keystore limits - 1ページ要約

## 対象（Target）

Android 17 Behavior Change

比較元:
- android-16.0.0_r4

比較先:
- android-17.0.0_r1

以前の targetSdkVersion:
- 36

対象 targetSdkVersion:
- 37

## 適用条件（Applicability）

- 主分類（Primary classification）: OS_UPDATE_ALL_APPS
- OS アップデート / 全アプリ（OS update / all apps）: 該当。Android 17 で per-app key ownership limit が導入され、all other apps は 200,000 key limit と説明されている。
- targetSdkVersion 37 以上: non-system app では stricter 50,000 key limit と `ERROR_TOO_MANY_KEYS` numeric error code が関係する。
- その他の必須条件（Other required conditions）: Android Keystore keys を作成し、app-owned key count が limit に達する / 超えること。system / non-system app 判定も関係する。
- Compat Change ID: framework API 側では確認できず
- Compat default state: 未確認
- Confidence: Medium

## 早見マトリクス（At-a-Glance Matrix）

| シナリオ（Scenario） | 影響（Impact） |
| --- | --- |
| Android 17 / targetSdkVersion 36 | all other apps として 200,000 key limit の対象。limit 超過時は `ERROR_INCORRECT_USAGE` と説明されている。 |
| Android 17 / targetSdkVersion 37 | non-system app では 50,000 key limit、limit 超過時は `ERROR_TOO_MANY_KEYS`。 |
| Android 17 / targetSdkVersion 37 + 必須条件 | key count が limit を超えると key creation が `KeyStoreException` で失敗する。 |

## 要約（Summary）

Android 17 では、Android Keystore が shared resource であることを踏まえ、app が所有できる key 数に per-app limit が導入される。non-system app targeting Android 17+ は 50,000 keys、all other apps は 200,000 keys、system apps は target API level に関係なく 200,000 keys と説明されている。

AOSP framework では `KeyStoreException.ERROR_TOO_MANY_KEYS` と response code mapping が追加されている。ただし keystore2 service 側の 50,000 / 200,000 enforcement 本体はこの checkout では未確認。

## 顧客影響（Customer Impact）

- 大量の Keystore key を作成するアプリで、新規 key creation が失敗する可能性がある。
- secure storage、wallet、credential、encrypted document、enterprise security、per-record encryption などで影響が出る可能性がある。

## 影響対象（Who Is Affected）

- 対象アプリ: Android Keystore keys を大量に作成するアプリ。
- 対象機能: secure storage、wallet、credential、encrypted document、enterprise security、per-record encryption。
- 対象条件: app-owned key count が 50,000 または 200,000 の limit に近い / 超える場合。

## 対応要否（Required Action）

- 必須対応: Keystore key creation 箇所と app-owned key count を棚卸しし、limit 超過時の `KeyStoreException` handling を確認する。
- 推奨対応: targetSdkVersion 37 以上では `ERROR_TOO_MANY_KEYS` を handling し、key lifecycle / cleanup / reuse を見直す。
- 不要: Android Keystore を使わない、または key count が十分少ないアプリでは直接影響は限定的。

## テストマトリクス（Test Matrix）

| 端末 OS（Device OS） | targetSdkVersion | 期待挙動（Expected behavior） |
| --- | --- | --- |
| Android 16 | 36 | baseline。per-app key limit enforcement の有無を確認する。 |
| Android 17 | 36 | all other apps として 200,000 key limit の対象。 |
| Android 17 | 37 | non-system app では 50,000 key limit、limit 超過時に `ERROR_TOO_MANY_KEYS`。 |

## 顧客向け説明（Explanation for Customers）

Android 17 では、Android Keystore に app ごとの key ownership limit が導入されます。limit を超えて key を作成しようとすると `KeyStoreException` で失敗します。

targetSdkVersion 37 以上の non-system app は 50,000 key limit と説明されており、limit 超過時の `getNumericErrorCode()` は `ERROR_TOO_MANY_KEYS` になります。targetSdkVersion 36 など all other apps では 200,000 key limit と `ERROR_INCORRECT_USAGE` が説明されているため、OS update 影響と targetSdkVersion 37 影響を分けて検証してください。

## 根拠（Evidence）

- 公式ドキュメント: https://developer.android.com/about/versions/17/behavior-changes-all
- 検証対象の原文: Android 17 から app-owned Keystore keys に limit が enforce され、non-system target 37+ は 50,000 keys、all other apps は 200,000 keys。
- AOSP ファイル: `keystore/java/android/security/KeyStoreException.java`, `keystore/java/android/security/KeyStore2.java`, `keystore/java/android/security/KeyStoreSecurityLevel.java`, `core/api/current.txt`
- AOSP ソース文脈: `ERROR_TOO_MANY_KEYS` API surface と response code 29 / 30 から public error code への mapping。
- 差分解釈: added API surface / changed error-code mapping。
- Gate conclusion: OS update で all-apps limit、target 37 で stricter limit / new numeric error code。enforcement 本体は keystore2 service 側の追加確認が必要。

## 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- 人間による判断が必要

判断（Decision）:
- 未判断
