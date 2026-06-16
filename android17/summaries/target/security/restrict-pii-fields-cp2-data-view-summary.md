# CP2 data view における PII fields の制限 - 1ページ要約

## 対象（Target）

Android 17 Behavior Change

比較元:
- android-16.0.0_r4

比較先:
- TBD: Android 17 AOSP tag

以前の targetSdkVersion:
- 36

対象 targetSdkVersion:
- 37

## 適用条件（Applicability）

- 主分類（Primary classification）: UNKNOWN_NEEDS_MORE_EVIDENCE
- OS アップデート / 全アプリ（OS update / all apps）: 未確認。原文は targetSdkVersion 37 以上を明示しているが、AOSP gate 未確認。
- targetSdkVersion 37 以上: 公式文書上は該当。AOSP gate 未確認。
- その他の必須条件（Other required conditions）: `ContactsContract.Data` data view query、`ACCOUNT_NAME`、`ACCOUNT_TYPE`、`ACCOUNT_TYPE_AND_DATA_SET` の利用。
- Compat Change ID: 未確認
- Compat default state: 未確認

## 早見マトリクス（At-a-Glance Matrix）

| シナリオ（Scenario） | 影響（Impact） |
| --- | --- |
| Android 17 / targetSdkVersion 36 | 未確認。この section は targetSdkVersion 37 以上向けだが、AOSP gate 未確認。 |
| Android 17 / targetSdkVersion 37 | 公式文書上、CP2 Data view から account PII columns が removed。 |
| Android 17 / targetSdkVersion 37 + 必須条件 | `ContactsContract.Data` から restricted columns を読めなくなり、`RawContacts` + `RAW_CONTACT_ID` join が必要になる可能性。 |

## 要約（Summary）

Android 17 では、targetSdkVersion 37 以上のアプリで、CP2 `ContactsContract.Data` data view から `ACCOUNT_NAME`、`ACCOUNT_TYPE`、`ACCOUNT_TYPE_AND_DATA_SET` が削除される、と公式文書は説明している。

## 顧客影響（Customer Impact）

- 要確認

## 影響対象（Who Is Affected）

- 対象アプリ: Contacts Provider を使い、`ContactsContract.Data` から account 情報を読んでいるアプリ。
- 対象機能: contacts account 表示、sync 元識別、filtering、重複排除、backup / restore、CRM 連携。
- 対象条件: targetSdkVersion 37 以上、Data view query、restricted columns の projection / column access。

## 対応要否（Required Action）

- 必須対応: `ContactsContract.Data` query で `ACCOUNT_NAME`、`ACCOUNT_TYPE`、`ACCOUNT_TYPE_AND_DATA_SET` を使っていないか棚卸しする。
- 推奨対応: 必要な account 情報は `RAW_CONTACT_ID` で `ContactsContract.RawContacts` と join して取得する。
- 不要: Contacts Provider を使わないアプリ、または restricted columns を Data view から読んでいないアプリでは直接影響は限定的。

## テストマトリクス（Test Matrix）

| 端末 OS（Device OS） | targetSdkVersion | 期待挙動（Expected behavior） |
| --- | --- | --- |
| Android 16 | 36 | Android 16 baseline。具体挙動は Android 17 tag 比較待ち。 |
| Android 17 | 36 | 未確認。この section は targetSdkVersion 37 以上向けだが、AOSP gate 未確認。 |
| Android 17 | 37 | CP2 Data view から restricted columns が removed と公式文書は説明。 |

## 顧客向け説明（Explanation for Customers）

Android 17 では、targetSdkVersion 37 以上のアプリに対して、Contacts Provider 2 の Data view から account name / account type などの PII columns が削除されます。`ContactsContract.Data` からこれらの columns を直接読んでいる実装は、targetSdkVersion 37 更新後に column が見つからない、値が取れない、cursor handling が失敗する可能性があります。

account 情報が必要な場合は、`ContactsContract.DataColumns.RAW_CONTACT_ID` を使って `ContactsContract.RawContacts` と join し、RawContacts 側から取得する設計へ移行してください。現時点では local AOSP checkout に Android 17 tag がないため、targetSdkVersion gate、実際の failure mode、compat flag の有無は未確認です。

## 根拠（Evidence）

- 公式ドキュメント: https://developer.android.com/about/versions/17/behavior-changes-17
- 検証対象の原文: targetSdkVersion 37 以上のアプリでは、CP2 Data view から PII を含む `ACCOUNT_NAME`、`ACCOUNT_TYPE`、`ACCOUNT_TYPE_AND_DATA_SET` が removed。必要な場合は `RAW_CONTACT_ID` で `RawContacts` から取得する。
- AOSP ファイル: 未確認。local `frameworks-base` に `android-17*` tag がない。
- AOSP ソース文脈: 未確認。tag 間 diff が実行できない。
- 差分解釈: 未分類。公式文書上は removed behavior / changed condition と読めるが、AOSP diff による確認は Android 17 tag 待ち。
- Gate conclusion: 未確認。公式文書は targetSdkVersion 37 以上を示すが、AOSP gate evidence は未取得。

## 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- 人間による判断が必要

判断（Decision）:
- 追加調査が必要
