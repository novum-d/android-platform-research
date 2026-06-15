# Per-app keystore limits - 1ページ要約（One Page Summary）

## 対象（Target）

Android 17 Behavior Change

From:
- android-16.0.0_r4

To:
- TBD: Android 17 AOSP tag

Previous targetSdkVersion:
- 36

Target targetSdkVersion:
- 37

## 適用条件（Applicability）

- 主分類（Primary classification）: UNKNOWN_NEEDS_MORE_EVIDENCE
- OS アップデート / 全アプリ（OS update / all apps）: 公式文書上は該当候補。Android 17 で per-app keystore key ownership limit を enforce すると説明されている。
- targetSdkVersion 37 以上: non-system app では stricter 50,000 key limit と `ERROR_TOO_MANY_KEYS` numeric error code が関係する。AOSP gate 未確認。
- その他の必須条件（Other required conditions）: Android Keystore keys を作成し、app-owned key count が limit に達する / 超えること。system / non-system app 判定も関係する。
- Compat Change ID: Unknown
- Compat default state: Unknown

## 早見マトリクス（At-a-Glance Matrix）

| シナリオ（Scenario） | 影響（Impact） |
| --- | --- |
| Android 17 / targetSdkVersion 36 | 公式文書上、all other apps として 200,000 key limit の対象になる可能性がある。AOSP gate 未確認。 |
| Android 17 / targetSdkVersion 37 | non-system app では 50,000 key limit、limit 超過時は `ERROR_TOO_MANY_KEYS` と公式文書は説明。 |
| Android 17 / targetSdkVersion 37 + 必須条件 | key count が limit を超えると key creation が `KeyStoreException` で失敗する。 |

## 要約（Summary）

Android 17 では、Android Keystore が shared resource であることを踏まえ、app が所有できる key 数に per-app limit が導入される。non-system app targeting Android 17+ は 50,000 keys、all other apps は 200,000 keys、system apps は target API level に関係なく 200,000 keys と説明されている。

## 顧客影響（Customer Impact）

- 要確認

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
| Android 17 | 36 | all other apps として 200,000 key limit の対象になる可能性がある。 |
| Android 17 | 37 | non-system app では 50,000 key limit、limit 超過時に `ERROR_TOO_MANY_KEYS` と公式文書は説明。 |

## 顧客向け説明（Explanation for Customers）

Android 17 では、Android Keystore に app ごとの key ownership limit が導入されます。limit を超えて key を作成しようとすると `KeyStoreException` で失敗します。通常の少数 key 利用では影響しにくい一方、record / account / session ごとに Keystore key を増やし続ける設計では、将来的に key creation failure が発生する可能性があります。

特に targetSdkVersion 37 以上の non-system app は 50,000 key limit と説明されており、limit 超過時の `getNumericErrorCode()` は `ERROR_TOO_MANY_KEYS` になります。targetSdkVersion 36 など all other apps では 200,000 key limit と `ERROR_INCORRECT_USAGE` が説明されているため、OS update 影響と targetSdkVersion 37 影響を分けて検証してください。

## 根拠（Evidence）

- Official documentation: https://developer.android.com/about/versions/17/behavior-changes-all
- Original statement: Android 17 から app-owned Keystore keys に limit が enforce され、non-system target 37+ は 50,000 keys、all other apps は 200,000 keys、system apps は target API level に関係なく 200,000 keys。limit 超過時は `KeyStoreException` で失敗する。
- AOSP files: 未確認。local `frameworks-base` に `android-17*` tag がない。
- AOSP source context: 未確認。tag 間 diff が実行できない。
- Diff interpretation: 未分類。公式文書上は added behavior / changed condition と読めるが、AOSP diff による確認は Android 17 tag 待ち。
- Gate conclusion: Unknown。公式文書上は Android 17 all apps + app type + targetSdkVersion + key count condition。targetSdkVersion gate / compat framework evidence は未取得。

## 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- Human decision required

判断（Decision）:
- Further investigation required after Android 17 AOSP tag is available
