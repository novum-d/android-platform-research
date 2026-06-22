# CP2 での strict SQL checks の強制

## 基本情報（Metadata）

### 調査対象 Android バージョン（Android Versions）

比較元:
- android-16.0.0_r4

比較先:
- android-17.0.0_r1

以前の targetSdkVersion:
- 36

対象 targetSdkVersion:
- 37

### Behavior Change 文書（Behavior Change Source）

文書:
https://developer.android.com/about/versions/17/behavior-changes-17

関連文書:
- https://developer.android.com/reference/android/provider/ContactsContract.Data
- https://developer.android.com/reference/android/Manifest.permission#READ_CONTACTS
- https://developer.android.com/reference/android/database/sqlite/SQLiteQueryBuilder#setStrictColumns(boolean)
- https://developer.android.com/reference/android/database/sqlite/SQLiteQueryBuilder#setStrictGrammar(boolean)
- https://developer.android.com/about/versions/17/features/contact-picker

セクション:
- Enforce strict SQL checks in CP2

ページ種別:
- Android 17 以上をターゲットにするアプリ

### 分類スナップショット（Classification Snapshot）

主分類（Primary classification）:
- TARGET_SDK_37_CONDITIONAL

公式文書からの初期適用条件判断:
- 公式文書は、targetSdkVersion 37 以上のアプリが `READ_CONTACTS` permission なしで `ContactsContract.Data` table にアクセスする場合、CP2 が strict SQL query validation を強制すると説明している。
- `StrictColumns` と `StrictGrammar` が有効になり、互換性のない query pattern は rejected され exception になる。
- `frameworks-base` では `READ_CONTACTS` permission、`ContactsContract.Data` API surface、`SQLiteQueryBuilder#setStrictColumns` / `setStrictGrammar` API は確認できた。
- 追加 checkout の `platform/packages/providers/ContactsProvider` で、targetSdkVersion 37 / permission 条件に応じて `setStrictColumns` / `setStrictGrammar` を有効化する実装を確認した。

### 調査日（Investigation Date）

2026-06-19

### 信頼度（Confidence）

- High

### 適用条件分類（Applicability Classification）

適用される条件（Applies when）:
- [ ] targetSdkVersion に関係なく Android 17 の全アプリへ適用
- [ ] Android 17 以上かつ targetSdkVersion 37 以上で適用
- [x] targetSdkVersion 37 以上かつ追加の実行時条件を満たす場合に適用
- [ ] Mainline / Google Play system update に依存
- [ ] API 追加のみであり、挙動変更ではない
- [ ] 追加 evidence が必要

必要な実行時条件（Required runtime conditions）:
- Android version: Android 17 以上。
- targetSdkVersion: 公式文書上は 37 以上。
- Permission condition: `READ_CONTACTS` permission なし。
- API condition: `ContactsContract.Data` table query。
- Query condition: strict columns / strict grammar と互換性のない projection / selection / sort order / expression を使う。
- Contact Picker condition: Picker Session URI は別 path。公式文書上、custom `selection` / `selectionArgs` は非対応。

Compat framework:
- Change ID: `484953293`
- 変更名: `ENFORCE_STRICT_SQL_CHECKS`
- 既定状態: `@EnabledAfter(targetSdkVersion = Build.VERSION_CODES.BAKLAVA)`
- テスト時に切り替え可能か: compat change と `enforce_strict_sql_checks` flag により切り替え可能

分類信頼度（Classification confidence）:
- High

分類根拠（Classification evidence）:
- 公式 Behavior Change 文書は targetSdkVersion 37 以上、`READ_CONTACTS` なし、`ContactsContract.Data` query、strict SQL validation を明示している。
- `frameworks-base` Android 17 tag では `SQLiteQueryBuilder#setStrictColumns` / `setStrictGrammar` API と `ContactsContract.Data` contract を確認できる。
- `platform/packages/providers/ContactsProvider` Android 17 tag では `ChangeIds.ENFORCE_STRICT_SQL_CHECKS = 484953293L`、`@EnabledAfter(BAKLAVA)`、`ContactsProvider2.canEnforceStrictSqlChecksForQueries()`、Data query path の `setStrictColumns(true)` / `setStrictGrammar(true)` を確認した。

---

# エグゼクティブサマリー

Android 17 では、targetSdkVersion 37 以上のアプリが `READ_CONTACTS` permission なしで `ContactsContract.Data` table を query する場合、CP2 が strict SQL query validation を強制する、と公式文書は説明している。`StrictColumns` と `StrictGrammar` が有効になり、互換性のない query は exception になる。

ContactsProvider 側で targetSdkVersion ゲート、`READ_CONTACTS` permission 判定、`setStrictColumns` / `setStrictGrammar` の呼び出し、Compat ChangeId を確認できたため、信頼度は High とする。

---

# AOSP 調査（AOSP Investigation）

## チェックアウト状態

根拠利用前に確認したコマンド:

```bash
git -C frameworks-base status --short
git -C frameworks-base tag --list android-16.0.0_r4
git -C frameworks-base tag --list android-17.0.0_r1
```

結果:
- `frameworks-base` working tree: clean at the time of investigation.
- From tag: `android-16.0.0_r4` exists.
- To tag: `android-17.0.0_r1` exists.

## 関連ファイル（Related Files）

frameworks-base で確認:
- `core/java/android/provider/ContactsContract.java`
- `core/java/android/database/sqlite/SQLiteQueryBuilder.java`
- `core/java/android/Manifest.java`
- `core/res/AndroidManifest.xml`
- `core/java/android/provider/ContactsPickerSessionContract.java`
- `core/java/android/provider/OWNERS`

追加で必要な AOSP project:
- なし。`tmp/aosp-checkouts/ContactsProvider` に `platform/packages/providers/ContactsProvider` の Android 16 / Android 17 tag を取得して確認済み。

差分確認メモ:
- 広域の `frameworks-base` tag diff では rename detection が skipped される警告が出るため、根拠確認では `--no-renames` と provider / sqlite / contact contract path 限定の diff を併用した。
- `ContactsContract.java` には directory provider permission に関する Android 17 追記があり、`ContactsPickerSessionContract.java` には Contact Picker session URI の selection / selectionArgs 制限文言が追加されている。
- ただし、通常の `ContactsContract.Data.CONTENT_URI` query に対して CP2 が `SQLiteQueryBuilder#setStrictColumns` / `setStrictGrammar` を targetSdkVersion 37 / `READ_CONTACTS` 条件で有効化する実装は `frameworks-base` では確認できない。
- ContactsProvider 側では `ChangeIds.java`、`ContactsProvider2.java`、`contactsprovider_flags.aconfig` を確認した。

## 確認したソース文脈（Source Context Reviewed）

| File / symbol | Android 16 baseline | Android 17 behavior | 関連性 |
| --- | --- | --- | --- |
| `ContactsContract.Data` | Data table API surface | Data table API surface | app-facing query URI / schema。provider enforcement ではない。 |
| `SQLiteQueryBuilder#setStrictColumns` | API exists | API exists | 公式文書の strict columns option。CP2 が呼ぶかは provider 側確認が必要。 |
| `SQLiteQueryBuilder#setStrictGrammar` | API exists | API exists | 公式文書の strict grammar option。CP2 が呼ぶかは provider 側確認が必要。 |
| `Manifest.permission.READ_CONTACTS` | dangerous permission | dangerous permission | strict SQL 適用条件の permission。 |
| `ContactsPickerSessionContract` | Android 17 API surface に存在 | Contact Picker session URI contract | `READ_CONTACTS` を避ける代替 path。selection / selectionArgs 制限は provider 側確認が必要。 |
| `ChangeIds.ENFORCE_STRICT_SQL_CHECKS` | なし | `484953293L`、`@EnabledAfter(BAKLAVA)` | targetSdkVersion 37 gate。 |
| `ContactsProvider2.canEnforceStrictSqlChecksForQueries()` | なし | session provider forwarded query、または `READ_CONTACTS` なし + flag + compat change enabled で true | strict SQL 適用条件の本体。 |
| `ContactsProvider2` Data / Data ID query path | strict options 設定なし | `setStrictColumns(true)` / `setStrictGrammar(true)` を設定 | CP2 query enforcement 本体。 |

Source context の補足:
- Entry point / caller: app の `ContentResolver.query(ContactsContract.Data.CONTENT_URI, ...)`。
- 関連性: strict SQL options は `SQLiteQueryBuilder` の機能で、ContactsProvider が Data query path で有効化する。
- Baseline Android behavior: Android 16 tag では `ENFORCE_STRICT_SQL_CHECKS` ChangeId と Data query path の strict options gate は確認できない。
- Target Android behavior: Android 17 tag では targetSdkVersion 37 以上、`READ_CONTACTS` なし、flag enabled、compat change enabled の場合に strict options が有効化される。
- Source diff type: added compat gate / changed condition / added enforcement。
- Excluded code paths: Telephony provider の restricted query helper、CallLog provider の strict SQL comment、SettingsProvider query builder は CP2 ではないため除外した。

## 事実・観察・仮説・結論

事実:
- `frameworks-base` の `android-16.0.0_r4` と `android-17.0.0_r1` tag は存在し、調査時点の working tree は clean。
- 公式文書は targetSdkVersion 37 以上かつ `READ_CONTACTS` なしの `ContactsContract.Data` query に strict SQL validation が適用されると説明している。
- `SQLiteQueryBuilder#setStrictColumns` / `setStrictGrammar` は frameworks-base API surface に存在する。
- `platform/packages/providers/ContactsProvider` Android 17 tag に `ENFORCE_STRICT_SQL_CHECKS = 484953293L` と strict SQL gate がある。

観察:
- targetSdkVersion ゲート / permission gate は ContactsProvider 側で確認できた。
- Contact Picker session forwarded query は `READ_CONTACTS` なしでも strict SQL path に入る別条件として扱われる。

結論:
- `TARGET_SDK_37_CONDITIONAL` と分類する。
- Android 17 / targetSdkVersion 37 以上、`READ_CONTACTS` なし、`ContactsContract.Data` query、strict grammar と互換性のない query が条件。
- Confidence は High。

---

# 開発者影響

影響を受ける可能性が高いアプリ:
- `READ_CONTACTS` なしで `ContactsContract.Data` を query するアプリ。
- raw SQL 的な selection / sort order / projection expression に依存するアプリ。
- Contact Picker session URI と通常の Data query を同じ query builder で扱うアプリ。

対応候補:
- `ContactsContract.Data` query を棚卸しする。
- provider が許容する column 名と grammar だけを使う。
- Contact Picker Session URI では custom `selection` / `selectionArgs` を渡さない。
- exception を想定した fallback を実装する。

---

# 追加調査 TODO

- `platform/packages/providers/ContactsProvider` の Android 16 / Android 17 tag を取得する。
- `READ_CONTACTS` なしかつ targetSdkVersion 37 以上で `setStrictColumns(true)` / `setStrictGrammar(true)` を設定する箇所を確認する。
- Compat ChangeId、default state、exception type を確認する。

---

# 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- 人間による判断が必要

判断（Decision）:
- 未判断
