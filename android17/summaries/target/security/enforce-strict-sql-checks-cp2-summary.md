# CP2 での strict SQL checks の強制 - 1ページ要約

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
- その他の必須条件（Other required conditions）: `READ_CONTACTS` permission なし、`ContactsContract.Data` table query、strict columns / strict grammar と互換性のない query pattern。Contact Picker を使う場合は、Session URI に custom `selection` / `selectionArgs` を指定しないこと。
- Compat Change ID: 未確認
- Compat default state: 未確認

## 早見マトリクス（At-a-Glance Matrix）

| シナリオ（Scenario） | 影響（Impact） |
| --- | --- |
| Android 17 / targetSdkVersion 36 | 未確認。この section は targetSdkVersion 37 以上向けだが、AOSP gate 未確認。 |
| Android 17 / targetSdkVersion 37 | 公式文書上、`READ_CONTACTS` なしの `ContactsContract.Data` query に strict SQL validation が適用される。 |
| Android 17 / targetSdkVersion 37 + 必須条件 | strict columns / grammar と非互換の query は rejected され、exception が発生する。 |

## 要約（Summary）

Android 17 では、targetSdkVersion 37 以上のアプリが `READ_CONTACTS` なしで `ContactsContract.Data` table を query する場合、CP2 が strict SQL checks を強制する、と公式文書は説明している。

Android 17 Contact Picker は、`READ_CONTACTS` permission で連絡先全体へアクセスする代わりに、ユーザーが選択した contact data だけを Session URI 経由で共有する仕組みである。Session URI は `ContactsContract.Data` schema の cursor として読めるが、custom `selection` / `selectionArgs` は support されない。

## 顧客影響（Customer Impact）

- 要確認

## 影響対象（Who Is Affected）

- 対象アプリ: `READ_CONTACTS` permission なしで Contacts Provider の `ContactsContract.Data` を query しているアプリ。
- 対象機能: contacts search、lookup、候補表示、matching、連携機能、Contact Picker へ移行する連絡先選択 UI。
- 対象条件: targetSdkVersion 37 以上、permission denied / not granted、strict SQL と互換性のない projection / selection / sort order。Contact Picker では Session URI に custom `selection` / `selectionArgs` を指定する path。

## 対応要否（Required Action）

- 必須対応: `ContactsContract.Data` query と `READ_CONTACTS` permission なしで実行される path を棚卸しする。
- 必須対応: Contact Picker の結果 Session URI を query する path は通常の `ContactsContract.Data.CONTENT_URI` query helper と分離し、custom `selection` / `selectionArgs` を指定しない。
- 推奨対応: query を documented columns と parameterized selection に寄せ、strict columns / strict grammar と互換性のある形へ修正する。
- 推奨対応: `READ_CONTACTS` permission なしでユーザー選択済み contact data だけが必要な機能は、Contact Picker の requested data fields と Session URI query へ移行できるか検討する。
- 不要: Contacts Provider を使わないアプリ、または `ContactsContract.Data` を permission なしで query しないアプリでは直接影響は限定的。Contact Picker の Session URI を selection なしで読むだけの path も、通常の Data table strict SQL query とは分けて扱う。

## テストマトリクス（Test Matrix）

| 端末 OS（Device OS） | targetSdkVersion | 期待挙動（Expected behavior） |
| --- | --- | --- |
| Android 16 | 36 | Android 16 baseline。具体挙動は Android 17 tag 比較待ち。 |
| Android 17 | 36 | 未確認。この section は targetSdkVersion 37 以上向けだが、AOSP gate 未確認。 |
| Android 17 | 37 | `READ_CONTACTS` なし Data query で strict validation が適用され、非互換 query は exception と公式文書は説明。 |

## 顧客向け説明（Explanation for Customers）

Android 17 では、targetSdkVersion 37 以上のアプリが `READ_CONTACTS` permission を持たずに `ContactsContract.Data` table を query する場合、CP2 が `StrictColumns` と `StrictGrammar` を有効にします。これにより、provider が許容しない column や SQL grammar に依存した query は拒否され、exception が発生します。

Contact Picker を使う場合、picker が返す Session URI はユーザーが選択した data だけへの一時的な read access です。結果 cursor は `ContactsContract.Data` schema に従いますが、Session URI は custom `selection` / `selectionArgs` を support しないため、既存の Data query helper をそのまま流用しないでください。

Contacts Provider への query は documented columns と安全な selection pattern に寄せ、permission なしで動く path と Contact Picker path を targetSdkVersion 37 環境で検証してください。現時点では local AOSP checkout に Android 17 tag がないため、targetSdkVersion gate、実際の exception type、compat flag の有無は未確認です。

## 根拠（Evidence）

- 公式ドキュメント: https://developer.android.com/about/versions/17/behavior-changes-17
- Related Contact Picker documentation: https://developer.android.com/about/versions/17/features/contact-picker
- 検証対象の原文: targetSdkVersion 37 以上のアプリでは、`READ_CONTACTS` なしで `ContactsContract.Data` table にアクセスする場合、CP2 が strict SQL query validation を強制し、非互換 query は rejected され exception が throw される。
- Contact Picker statement: Android 17 以上では Contact Picker が broad `READ_CONTACTS` permission の代替として利用でき、Session URI は selected data への temporary read access を与える。Session URI は `ContactsContract.Data` schema の cursor として読めるが、custom `selection` / `selectionArgs` は support しない。
- AOSP ファイル: 未確認。local `frameworks-base` に `android-17*` tag がない。
- AOSP ソース文脈: 未確認。tag 間 diff が実行できない。
- 差分解釈: 未分類。公式文書上は added behavior / changed condition と読めるが、AOSP diff による確認は Android 17 tag 待ち。
- Gate conclusion: 未確認。公式文書は targetSdkVersion 37 以上と `READ_CONTACTS` permission condition を示すが、AOSP gate evidence は未取得。

## 人間の判断欄（Human Decision）

最終優先度（Final Priority）:
- 人間による判断が必要

判断（Decision）:
- 追加調査が必要
