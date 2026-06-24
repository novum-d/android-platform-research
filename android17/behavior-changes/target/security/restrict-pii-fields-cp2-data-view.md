# CP2 data view における PII fields の制限

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
- https://developer.android.com/reference/android/provider/ContactsContract.RawContacts
- https://developer.android.com/reference/android/provider/ContactsContract.SyncColumns#ACCOUNT_NAME
- https://developer.android.com/reference/android/provider/ContactsContract.SyncColumns#ACCOUNT_TYPE
- https://developer.android.com/reference/android/provider/ContactsContract.RawContactsColumns#ACCOUNT_TYPE_AND_DATA_SET

セクション:
- Restrict PII fields in CP2 data view

ページ種別:
- Android 17 以上をターゲットにするアプリ

### 分類スナップショット（Classification Snapshot）

主分類（Primary classification）:
- TARGET_SDK_37_CONDITIONAL

公式文書からの初期適用条件判断:
- 公式文書は、targetSdkVersion 37 以上のアプリに対し、Contacts Provider 2 (CP2) の `ContactsContract.Data` data view から PII を含む `ACCOUNT_NAME`、`ACCOUNT_TYPE`、`ACCOUNT_TYPE_AND_DATA_SET` が制限されると説明している。
- 該当 columns が必要な場合は、`RAW_CONTACT_ID` で `ContactsContract.RawContacts` と join して RawContacts 側から取得するよう案内されている。
- `frameworks-base` では `ContactsContract.Data` / `RawContacts` / `DataColumnsWithJoins` の API surface と `RAW_CONTACT_ID` 境界を確認できた。
- 追加 checkout の `platform/packages/providers/ContactsProvider` で、projection filtering、targetSdkVersion ゲート、Compat ChangeId を確認した。

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
- API condition: `ContactsContract.Data` data view query。
- Column condition: `ACCOUNT_NAME`、`ACCOUNT_TYPE`、`ACCOUNT_TYPE_AND_DATA_SET` を projection / mapping で使う。
- Alternative path: `ContactsContract.Data.RAW_CONTACT_ID` を使って `ContactsContract.RawContacts` から account columns を取得する。

Compat framework:
- Change ID: `437318646`
- 変更名: `RESTRICT_DATA_URI_COLUMNS`
- 既定状態: `@EnabledAfter(targetSdkVersion = Build.VERSION_CODES.BAKLAVA)`
- テスト時に切り替え可能か: compat change と `restrict_pii_data_uri_columns` flag により切り替え可能

分類信頼度（Classification confidence）:
- High

分類根拠（Classification evidence）:
- 公式 Behavior Change 文書は targetSdkVersion 37 以上と制限対象 columns を明示している。
- `frameworks-base` Android 17 tag では `ContactsContract.Data` / `RawContacts` API surface と `RAW_CONTACT_ID` は確認できる。
- `core/java/android/provider/OWNERS` は Contacts 関連 provider 実装の owner を `platform/packages/providers/ContactsProvider` と示す。
- `platform/packages/providers/ContactsProvider` Android 17 tag では `ChangeIds.RESTRICT_DATA_URI_COLUMNS = 437318646L`、`@EnabledAfter(BAKLAVA)`、`ContactsProvider2.isDataProjectionRestricted()`、`sRawContactColumnsRestricted` を確認した。

---

# エグゼクティブサマリー

Android 17 では、targetSdkVersion 37 以上のアプリに対し、CP2 の `ContactsContract.Data` data view から account PII に該当する `ACCOUNT_NAME`、`ACCOUNT_TYPE`、`ACCOUNT_TYPE_AND_DATA_SET` が制限される、と公式文書は説明している。

この変更は、`ContactsContract.Data` query の projection にこれらの columns を含めているアプリに影響する。代替は `RAW_CONTACT_ID` を使って `ContactsContract.RawContacts` から account 情報を取得する設計である。

信頼度は High とする。ContactsProvider 側で Compat ChangeId、targetSdkVersion ゲート、restricted projection map を確認した。

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
- `core/api/current.txt`
- `core/java/android/provider/OWNERS`
- `core/java/android/provider/ContactsPickerSessionContract.java`

追加で必要な AOSP project:
- なし。`tmp/aosp-checkouts/ContactsProvider` に `platform/packages/providers/ContactsProvider` の Android 16 / Android 17 tag を取得して確認済み。

差分確認メモ:
- 広域の `frameworks-base` tag diff では rename detection が skipped される警告が出るため、根拠確認では `--no-renames` と provider / sqlite / contact contract path 限定の diff を併用した。
- `ContactsContract.java` と `ContactsPickerSessionContract.java` には Android 17 の Contacts API / picker session contract 差分があるが、`ContactsContract.Data` data view の projection filtering 本体は確認できない。
- `SQLiteConnection` の trace 差分や SQLite 周辺の一般差分は CP2 の projection filtering ではないため除外した。
- ContactsProvider 側では `ChangeIds.java`、`ContactsProvider2.java`、`contactsprovider_flags.aconfig`、`ContactsProvider2Test.java` を確認した。

## 確認したソース文脈（Source Context Reviewed）

| File / symbol | Android 16 baseline | Android 17 behavior | 関連性 |
| --- | --- | --- | --- |
| `ContactsContract.Data` | Data table API surface | Data table API surface | app-facing query URI / columns の定義。filtering 実装ではない。 |
| `ContactsContract.DataColumnsWithJoins` | Data query returned columns の contract | 同じ | Data view が join column を返す contract。 |
| `ContactsContract.Data.RAW_CONTACT_ID` | RawContacts への参照 column | 同じ | 公式文書が示す代替 join path。 |
| `ContactsContract.RawContacts` | account columns を持つ raw contact API | 同じ | 制限対象 PII columns の代替取得先。 |
| `ContactsPickerSessionContract` | なし | Contact Picker session URI contract | `READ_CONTACTS` なしの代替取得 path として関連するが、通常の Data view projection filtering ではない。 |
| `core/java/android/provider/OWNERS` | Contacts owner は ContactsProvider | 同じ | 実 enforcement が別 project にあることを示す。 |
| `ContactsProvider2.sRawContactColumnsRestricted` | なし | `ACCOUNT_NAME` / `ACCOUNT_TYPE` / `ACCOUNT_TYPE_AND_DATA_SET` を含まない restricted map | Data view projection から対象 PII columns を除外する本体。 |
| `ContactsProvider2.isDataProjectionRestricted()` | なし | `restrictPiiDataUriColumns()` と `CompatChanges.isChangeEnabled(RESTRICT_DATA_URI_COLUMNS)` を確認 | feature flag と compat gate。 |
| `ChangeIds.RESTRICT_DATA_URI_COLUMNS` | なし | `437318646L`、`@EnabledAfter(BAKLAVA)` | targetSdkVersion 37 gate。 |

Source context の補足:
- Entry point / caller: app の `ContentResolver.query(ContactsContract.Data.CONTENT_URI, projection, ...)`。
- 関連性: `frameworks-base` は API contract を定義し、ContactsProvider が Data view query の projection map を選択する。
- Baseline Android behavior: Android 16 tag では restricted projection map / compat gate は確認できない。
- Target Android behavior: Android 17 tag では targetSdkVersion 37 以上で compat change が有効になると restricted projection map が選ばれる。
- Source diff type: added compat gate / changed projection map。
- Excluded code paths: CallLog / Telephony / SystemUI の ContactsContract 利用箇所は provider enforcement ではないため除外した。

## 事実・観察・仮説・結論

事実:
- `frameworks-base` の `android-16.0.0_r4` と `android-17.0.0_r1` tag は存在し、調査時点の working tree は clean。
- 公式文書は targetSdkVersion 37 以上で CP2 data view の PII columns が制限されると説明している。
- `ContactsContract.Data`、`ContactsContract.RawContacts`、`RAW_CONTACT_ID` は frameworks-base API surface に存在する。
- `platform/packages/providers/ContactsProvider` Android 17 tag に `RESTRICT_DATA_URI_COLUMNS = 437318646L` と restricted projection map がある。

観察:
- provider query projection filtering と targetSdkVersion ゲートは ContactsProvider 側で確認できた。
- 対象 columns は Data view から除外されるが、RawContacts 側の account columns は代替 path として残る。

結論:
- `TARGET_SDK_37_CONDITIONAL` と分類する。
- Android 17 / targetSdkVersion 37 以上かつ `ContactsContract.Data` で対象 PII columns を読む場合に影響する。
- Confidence は High。

---

# 開発者影響

影響を受ける可能性が高いアプリ:
- `ContactsContract.Data` query で `ACCOUNT_NAME`、`ACCOUNT_TYPE`、`ACCOUNT_TYPE_AND_DATA_SET` を projection に含めるアプリ。
- account 別の同期 / 表示 / grouping を Data view から直接行うアプリ。

対応候補:
- Data query の projection を棚卸しする。
- account 情報が必要な場合は `RAW_CONTACT_ID` で `RawContacts` を query する。
- column missing / `getColumnIndex()` が `-1` になるケースを防ぐ。

---

# サービス影響例

このセクションは、公式文書と AOSP 根拠から導いた「起こりうる影響例」を記録する。特定サービスで実際に発生確認した事実ではない。

## 例1（Example 1）: Salesforce / HubSpot / Sansan の account 別連絡先同期

- 具体サービス例: Salesforce、HubSpot、Sansan、Eight、Microsoft Dynamics 365。
- 影響を受ける実装パターン: `ContactsContract.Data` の projection に `ACCOUNT_NAME`、`ACCOUNT_TYPE`、`ACCOUNT_TYPE_AND_DATA_SET` を含め、連絡先を account 別に分類・同期する実装。
- 発生条件: Android 17 / targetSdkVersion 37 以上で `ContactsContract.Data` data view から制限対象 PII columns を読む場合。
- ユーザーに見える症状: account 別の連絡先分類ができない、同期対象 account の判定が失敗する、CRM 連携で一部連絡先が未分類になる可能性。
- 技術的に起きていること: ContactsProvider が Data view の projection map から account PII columns を除外し、Data query から直接取得できなくなる。
- 推奨対応シーン: CRM sync、business card import、contact deduplication、account grouping。
- 検証観点: `getColumnIndex()`、projection mismatch、`RAW_CONTACT_ID` から `RawContacts` への追加 query、targetSdkVersion 36 / 37。
- 根拠: `RESTRICT_DATA_URI_COLUMNS = 437318646L`、`@EnabledAfter(BAKLAVA)`、`ContactsProvider2.sRawContactColumnsRestricted`、`isDataProjectionRestricted()`。
- Confidence（信頼度）: High。
- 注意: 上記サービスで発生確認した事実ではない。実際の影響は Data view projection の内容に依存する。

## 例2（Example 2）: WhatsApp / Telegram / Outlook の連絡先候補・招待機能

- 具体サービス例: WhatsApp、Telegram、Microsoft Outlook、Gmail。
- 影響を受ける実装パターン: 連絡先候補や招待対象を account provider ごとに表示するため、Data view から account columns を直接読む実装。
- 発生条件: targetSdkVersion 37 以上で Data view query の projection に制限対象 columns を含める場合。
- ユーザーに見える症状: 「Google 連絡先」「Exchange 連絡先」など account 別表示が欠落する、候補の grouping が変わる可能性。
- 技術的に起きていること: account PII は Data view ではなく RawContacts から `RAW_CONTACT_ID` 経由で取得する設計に移行する必要がある。
- 推奨対応シーン: contacts picker replacement、invite screen、account-scoped sync。
- 検証観点: RawContacts query fallback、permission state、cursor column handling、空 / missing column 時の UI。
- 根拠: 公式文書の代替 path と AOSP の restricted projection map。
- Confidence（信頼度）: High。
- 注意: 上記サービスで発生確認した事実ではない。platform / privileged app は一般アプリと条件が異なる可能性がある。

---

# 追加調査 TODO

- 実機または provider test で `getColumnIndex()` / projection mismatch 時の app-visible cursor behavior を確認する。
- release config における `restrict_pii_data_uri_columns` flag default を確認する。

---

# 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- 人間による判断が必要

判断（Decision）:
- 未判断
