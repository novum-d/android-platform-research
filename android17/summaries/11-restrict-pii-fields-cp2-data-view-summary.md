# Restrict PII fields in CP2 data view - One Page Summary

## Target

Android 17 Behavior Change

From:
- android-16.0.0_r4

To:
- TBD: Android 17 AOSP tag

Previous targetSdkVersion:
- 36

Target targetSdkVersion:
- 37

## Applicability

- Primary classification: UNKNOWN_NEEDS_MORE_EVIDENCE
- OS update / all apps: Unknown。原文は targetSdkVersion 37+ を明示しているが、AOSP gate 未確認。
- targetSdkVersion 37+: 公式文書上は該当。AOSP gate 未確認。
- Other required conditions: `ContactsContract.Data` data view query、`ACCOUNT_NAME`、`ACCOUNT_TYPE`、`ACCOUNT_TYPE_AND_DATA_SET` の利用。
- Compat Change ID: Unknown
- Compat default state: Unknown

## At-a-Glance Matrix

| Scenario | Impact |
| --- | --- |
| Android 17 / targetSdkVersion 36 | Unknown。この section は targetSdkVersion 37+ 向けだが、AOSP gate 未確認。 |
| Android 17 / targetSdkVersion 37 | 公式文書上、CP2 Data view から account PII columns が removed。 |
| Android 17 / targetSdkVersion 37 + required conditions | `ContactsContract.Data` から restricted columns を読めなくなり、`RawContacts` + `RAW_CONTACT_ID` join が必要になる可能性。 |

## Summary

Android 17 では、targetSdkVersion 37 以上のアプリで、CP2 `ContactsContract.Data` data view から `ACCOUNT_NAME`、`ACCOUNT_TYPE`、`ACCOUNT_TYPE_AND_DATA_SET` が削除される、と公式文書は説明している。

## Customer Impact

- 要確認

## Who Is Affected

- 対象アプリ: Contacts Provider を使い、`ContactsContract.Data` から account 情報を読んでいるアプリ。
- 対象機能: contacts account 表示、sync 元識別、filtering、重複排除、backup / restore、CRM 連携。
- 対象条件: targetSdkVersion 37 以上、Data view query、restricted columns の projection / column access。

## Required Action

- 必須対応: `ContactsContract.Data` query で `ACCOUNT_NAME`、`ACCOUNT_TYPE`、`ACCOUNT_TYPE_AND_DATA_SET` を使っていないか棚卸しする。
- 推奨対応: 必要な account 情報は `RAW_CONTACT_ID` で `ContactsContract.RawContacts` と join して取得する。
- 不要: Contacts Provider を使わないアプリ、または restricted columns を Data view から読んでいないアプリでは直接影響は限定的。

## Test Matrix

| Device OS | targetSdkVersion | Expected behavior |
| --- | --- | --- |
| Android 16 | 36 | Android 16 baseline。具体挙動は Android 17 tag 比較待ち。 |
| Android 17 | 36 | Unknown。この section は targetSdkVersion 37+ 向けだが、AOSP gate 未確認。 |
| Android 17 | 37 | CP2 Data view から restricted columns が removed と公式文書は説明。 |

## Explanation for Customers

Android 17 では、targetSdkVersion 37 以上のアプリに対して、Contacts Provider 2 の Data view から account name / account type などの PII columns が削除されます。`ContactsContract.Data` からこれらの columns を直接読んでいる実装は、targetSdkVersion 37 更新後に column が見つからない、値が取れない、cursor handling が失敗する可能性があります。

account 情報が必要な場合は、`ContactsContract.DataColumns.RAW_CONTACT_ID` を使って `ContactsContract.RawContacts` と join し、RawContacts 側から取得する設計へ移行してください。現時点では local AOSP checkout に Android 17 tag がないため、targetSdkVersion gate、実際の failure mode、compat flag の有無は未確認です。

## Evidence

- Official documentation: https://developer.android.com/about/versions/17/behavior-changes-17
- Original statement: targetSdkVersion 37 以上のアプリでは、CP2 Data view から PII を含む `ACCOUNT_NAME`、`ACCOUNT_TYPE`、`ACCOUNT_TYPE_AND_DATA_SET` が removed。必要な場合は `RAW_CONTACT_ID` で `RawContacts` から取得する。
- AOSP files: 未確認。local `frameworks-base` に `android-17*` tag がない。
- AOSP source context: 未確認。tag 間 diff が実行できない。
- Diff interpretation: 未分類。公式文書上は removed behavior / changed condition と読めるが、AOSP diff による確認は Android 17 tag 待ち。
- Gate conclusion: Unknown。公式文書は targetSdkVersion 37+ を示すが、AOSP gate evidence は未取得。

## Human Decision

Final Priority:
- Human decision required

Decision:
- Further investigation required
