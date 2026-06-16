# Autonomous re-pairing for Bluetooth bond losses - 1ページ要約（One Page Summary）

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
- OS アップデート / 全アプリ（OS update / all apps）: 公式文書上は該当候補。Android 17 の all apps ページに掲載され、targetSdkVersion 条件は示されていない。
- targetSdkVersion 37 以上: 公式文書上は不要。AOSP gate 未確認。
- その他の必須条件（Other required conditions）: Bluetooth peripheral bond loss が発生し、system が autonomous re-pairing を試行すること。companion app が pairing / key missing broadcast を扱う場合は特に確認が必要。
- Compat Change ID: Unknown
- Compat default state: Unknown

## 早見マトリクス（At-a-Glance Matrix）

| シナリオ（Scenario） | 影響（Impact） |
| --- | --- |
| Android 17 / targetSdkVersion 36 | bond loss 後、system が autonomous re-pairing を試行する可能性。AOSP gate 未確認。 |
| Android 17 / targetSdkVersion 37 | targetSdkVersion 36 と同様の可能性。公式文書に targetSdkVersion 条件なし。 |
| Android 17 / companion app listens to pairing broadcasts | `ACTION_PAIRING_REQUEST` の context と `ACTION_KEY_MISSING` timing を確認する必要がある。 |

## 要約（Summary）

Android 17 では、Bluetooth bond loss 後に system が autonomous re-pairing を試行できる。従来のように users が Settings で manual unpair / re-pair する必要が減る可能性がある。

## 顧客影響（Customer Impact）

- 要確認

## 影響対象（Who Is Affected）

- 対象アプリ: Bluetooth companion app、peripheral manufacturer app、wearable / audio / IoT / health device app。
- 対象機能: pairing UX、bond loss recovery、manual unpair / re-pair guidance、`ACTION_PAIRING_REQUEST` / `ACTION_KEY_MISSING` handling。
- 対象条件: Bluetooth bond loss が発生し、system-managed autonomous re-pairing が試行される場合。

## 対応要否（Required Action）

- 必須対応: bond loss recovery flow と pairing / key-missing broadcast handling を棚卸しする。
- 推奨対応: `ACTION_PAIRING_REQUEST` の `EXTRA_PAIRING_CONTEXT` を確認し、standard pairing と autonomous re-pairing attempt を区別する。
- 注意: `ACTION_KEY_MISSING` は autonomous re-pairing failure 時だけ broadcast されるため、successful recovery 時に届く前提の error handling は見直す。

## テストマトリクス（Test Matrix）

| 端末 OS（Device OS） | targetSdkVersion | 期待挙動（Expected behavior） |
| --- | --- | --- |
| Android 16 | 36 | baseline。bond loss 後の manual recovery flow を確認。 |
| Android 17 | 36 | system が autonomous re-pairing を試行する可能性。 |
| Android 17 | 37 | targetSdkVersion 36 と同じ期待。targetSdkVersion 条件は公式文書に記載なし。 |

## 顧客向け説明（Explanation for Customers）

Android 17 では、Bluetooth peripheral の bond が失われた場合、system が autonomous re-pairing によって background で bond の再確立を試行できます。

多くの app では code change は不要ですが、companion app や peripheral manufacturer app は、`EXTRA_PAIRING_CONTEXT`、`ACTION_KEY_MISSING` の timing、system-managed notification / dialog と app 側 recovery UI の整合を確認してください。

## 根拠（Evidence）

- Official documentation: https://developer.android.com/about/versions/17/behavior-changes-all
- Original statement: Android 17 は Bluetooth bond loss を自動的に解決する autonomous re-pairing を導入する。`ACTION_PAIRING_REQUEST` に `EXTRA_PAIRING_CONTEXT` が追加され、`ACTION_KEY_MISSING` は autonomous re-pairing failure 時だけ broadcast される。
- AOSP files: 未確認。local `frameworks-base` に `android-17*` tag がない。
- AOSP source context: 未確認。tag 間 diff が実行できない。Bluetooth stack は `packages/modules/Bluetooth` など `frameworks-base` 外も確認対象になる可能性が高い。
- Diff interpretation: 未分類。公式文書上は added behavior / changed broadcast timing / API surface addition と読めるが、AOSP diff による確認は Android 17 tag 待ち。
- Gate conclusion: Unknown。公式文書上は Android 17 all apps + Bluetooth bond loss condition。targetSdkVersion gate / compat framework evidence は未取得。

## 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- Human decision required

判断（Decision）:
- Further investigation required after Android 17 AOSP tag is available
