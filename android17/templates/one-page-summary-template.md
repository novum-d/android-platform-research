# [Behavior Change Title] - 1ページ要約（One Page Summary）

## 対象（Target）

Android 17 Behavior Change

From:
- android-16.0.0_r4

To:
- android-17.0.0_r1

## 適用条件（Applicability）

- 主分類（Primary classification）:
- OS アップデート / 全アプリ（OS update / all apps）:
- targetSdkVersion 37 以上:
- その他の必須条件（Other required conditions）:
- Compat Change ID:
- Compat default state:

記入例:
- 主分類: `TARGET_SDK_37_CONDITIONAL`
- OS アップデート / 全アプリ: `No。targetSdkVersion 37 以上でない場合は適用されない`
- targetSdkVersion 37 以上: `Yes`
- その他の必須条件: `ContactsContract.Data data view を query する場合`
- Compat default state: `targetSdkVersion 37 以上で default enabled`

## 早見マトリクス（At-a-Glance Matrix）

| シナリオ（Scenario） | 影響（Impact） |
| --- | --- |
| Android 17 / targetSdkVersion 36 | |
| Android 17 / targetSdkVersion 37 | |
| Android 17 / targetSdkVersion 37 + 必須条件 | |

## 要約（Summary）

1〜3行で説明。

## 顧客影響（Customer Impact）

- 影響あり / 影響軽微 / 影響なし / 要確認

## 影響対象（Who Is Affected）

- 対象アプリ
- 対象機能
- 対象条件

## 対応要否（Required Action）

- 必須対応
- 推奨対応
- 不要

## テストマトリクス（Test Matrix）

| 端末 OS（Device OS） | targetSdkVersion | 期待挙動（Expected behavior） |
| --- | --- | --- |
| Android 16 | 36 | |
| Android 17 | 36 | |
| Android 17 | 37 | |

記入例:
- `Android 17 / targetSdkVersion 36`: 旧挙動が維持される
- `Android 17 / targetSdkVersion 37`: 新挙動が適用される
- `Android 17 / targetSdkVersion 37 + 必須条件`: 実際にユーザー影響が発生する条件を確認する

## 顧客向け説明（Explanation for Customers）

顧客にそのまま説明できる文面。

## 根拠（Evidence）

- Official documentation:
- AOSP files:
- AOSP source context:
- Diff interpretation:
- Gate conclusion:

記入例:
- Official documentation: `Android Developers の Behavior changes ページ URL`
- AOSP source context: `対象 API の entry point、gate 条件、除外した code path`
- Diff interpretation: `added behavior / removed behavior / changed condition / changed default / no behavior change found`
- Gate conclusion: `Android 17 以上かつ targetSdkVersion 37 以上で適用`

## 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- Critical / High / Medium / Low

判断（Decision）:
- Explain / Monitor / Ignore / Further investigation required
