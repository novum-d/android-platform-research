# CP2 data view における PII fields の制限 - 1ページ要約

## 対象（Target）

Android 17 Behavior Change

比較元:
- android-16.0.0_r4

比較先:
- android-17.0.0_r1

## 適用条件（Applicability）

- 主分類（Primary classification）: TARGET_SDK_37_CONDITIONAL
- OS アップデート / 全アプリ: 非該当。ContactsProvider gate は targetSdkVersion 37 以上で有効。
- targetSdkVersion 37 以上: 該当。Data view projection から account PII columns が制限される。
- その他の必須条件: `ContactsContract.Data` data view で `ACCOUNT_NAME` / `ACCOUNT_TYPE` / `ACCOUNT_TYPE_AND_DATA_SET` を読む。
- Compat Change ID: `437318646` (`RESTRICT_DATA_URI_COLUMNS`)
- Compat default state: `@EnabledAfter(targetSdkVersion = Build.VERSION_CODES.BAKLAVA)`
- Confidence: High

## 要約（Summary）

Android 17 では、targetSdkVersion 37 以上のアプリに対し、CP2 の `ContactsContract.Data` data view から account PII columns が制限される、と公式文書は説明している。

ContactsProvider の projection map で、targetSdkVersion 37 以上の caller に対し `ACCOUNT_NAME` / `ACCOUNT_TYPE` / `ACCOUNT_TYPE_AND_DATA_SET` を除外する restricted projection が選択されることを確認した。

## 根拠（Evidence）

- 公式ドキュメント: https://developer.android.com/about/versions/17/behavior-changes-17
- AOSP checkout: `frameworks-base` と `tmp/aosp-checkouts/ContactsProvider` の `android-16.0.0_r4` / `android-17.0.0_r1` tag を確認。
- AOSP: `ContactsProvider/src/com/android/providers/contacts/ChangeIds.java` に `RESTRICT_DATA_URI_COLUMNS = 437318646` と `@EnabledAfter(targetSdkVersion = Build.VERSION_CODES.BAKLAVA)`。
- AOSP: `ContactsProvider2.java` の `sRawContactColumnsRestricted` は account PII columns を除外する。
- AOSP: `setTablesAndProjectionMapForData(...)` は `isDataProjectionRestricted()` により restricted projection map を選択する。
- 差分解釈: targetSdkVersion 37 以上で projection map が制限版に切り替わる changed condition。

## 対応候補（Action Candidates）

- `ContactsContract.Data` query projection を棚卸しする。
- account columns が必要な場合は `RAW_CONTACT_ID` で `RawContacts` から取得する。
- `getColumnIndex()` が `-1` になるケースを防ぐ。

## 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- 人間による判断が必要

判断（Decision）:
- 未判断
