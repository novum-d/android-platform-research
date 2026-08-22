# CP2 での strict SQL checks の強制 - 1ページ要約

## 対象

Android 17 Behavior Change

比較元:
- android-16.0.0_r4

比較先:
- android-17.0.0_r1

## 適用条件

- 主分類（Primary classification）: TARGET_SDK_37_CONDITIONAL
- OS アップデート / 全アプリ: 非該当。ContactsProvider gate は targetSdkVersion 37 以上で有効。
- targetSdkVersion 37 以上: 該当。`READ_CONTACTS` なしの Data query に strict columns / strict grammar が適用される。
- その他の必須条件: `READ_CONTACTS` なしで `ContactsContract.Data` table を query し、strict columns / strict grammar と互換性のない query を使う。
- Compat Change ID: `484953293` (`ENFORCE_STRICT_SQL_CHECKS`)
- Compat default state: `@EnabledAfter(targetSdkVersion = Build.VERSION_CODES.BAKLAVA)`
- Confidence: High

## 要約

Android 17 では、targetSdkVersion 37 以上のアプリが `READ_CONTACTS` permission なしで CP2 `ContactsContract.Data` table を query する場合、strict SQL validation が強制される、と公式文書は説明している。

ContactsProvider の Data query path で、`READ_CONTACTS` なし、flag enabled、ChangeId enabled の caller に対し `SQLiteQueryBuilder#setStrictColumns(true)` と `setStrictGrammar(true)` が設定されることを確認した。

## 根拠（Evidence）

- 公式ドキュメント: https://developer.android.com/about/versions/17/behavior-changes-17
- AOSP checkout: `frameworks-base` と `tmp/aosp-checkouts/ContactsProvider` の `android-16.0.0_r4` / `android-17.0.0_r1` tag を確認。
- AOSP: `core/java/android/provider/ContactsContract.java` の `ContactsContract.Data`
- AOSP: `core/java/android/database/sqlite/SQLiteQueryBuilder.java` の `setStrictColumns` / `setStrictGrammar`
- AOSP: `core/res/AndroidManifest.xml` の `READ_CONTACTS`
- AOSP: `ContactsProvider/src/com/android/providers/contacts/ChangeIds.java` に `ENFORCE_STRICT_SQL_CHECKS = 484953293` と `@EnabledAfter(targetSdkVersion = Build.VERSION_CODES.BAKLAVA)`。
- AOSP: `ContactsProvider2.java` の `canEnforceStrictSqlChecksForQueries()` は `READ_CONTACTS` なし、flag enabled、compat enabled を条件に true を返す。
- AOSP: `DATA` / `DATA_ID` query path は上記条件で `setStrictColumns(true)` / `setStrictGrammar(true)` を呼ぶ。
- 差分解釈: targetSdkVersion 37 以上かつ `READ_CONTACTS` なしで Data query validation が厳格化される changed condition。

## 対応候補（Action Candidates）

- `READ_CONTACTS` なしの `ContactsContract.Data` query を棚卸しする。
- projection / selection / sort order を provider が許容する column と grammar に絞る。
- Contact Picker Session URI では custom `selection` / `selectionArgs` を使わない。

## 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- 人間による判断が必要

判断（Decision）:
- 未判断

## 再検証記録（2026-08-22）

- Android 17 の公式 Behavior Change 一覧と最新通常AOSPタグを再確認した。
- 対応する[主レポート](../../../behavior-changes/target/security/enforce-strict-sql-checks-cp2.md)で official section、AOSP project / remote / checkout、解決済み commit、比較 command、dirty risk を再検証した。
- 主レポートの分類、confidence、未確認事項を維持し、実機未実施の項目を Observed 済みへ変更していない。
- 全件の結果は[再検証台帳](../../../analysis/REVALIDATION_2026-08-22.md)を参照する。
