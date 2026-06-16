# Enforce strict SQL checks in CP2

## 基本情報（Metadata）

### 調査対象 Android バージョン（Android Versions）

From:
- android-16.0.0_r4

To:
- TBD: Android 17 AOSP tag

Previous targetSdkVersion:
- 36

Target targetSdkVersion:
- 37

### Behavior Change 文書（Behavior Change Source）

Document:
https://developer.android.com/about/versions/17/behavior-changes-17

Related documents:
- https://developer.android.com/reference/android/provider/ContactsContract.Data
- https://developer.android.com/reference/android/Manifest.permission#READ_CONTACTS
- https://developer.android.com/reference/android/database/sqlite/SQLiteQueryBuilder#setStrictColumns(boolean)
- https://developer.android.com/reference/android/database/sqlite/SQLiteQueryBuilder#setStrictGrammar(boolean)
- https://developer.android.com/about/versions/17/features/contact-picker

Section:
Enforce strict SQL checks in CP2

Page type:
- Apps targeting Android 17 or higher

### 分類スナップショット（Classification Snapshot）

主分類（Primary classification）:
- UNKNOWN_NEEDS_MORE_EVIDENCE

公式文書からの初期適用条件判断:
- 公式文書は、targetSdkVersion 37 以上のアプリが `READ_CONTACTS` permission なしで `ContactsContract.Data` table にアクセスする場合、Contacts Provider 2 (CP2) が strict SQL query validation を強制すると説明している。
- 変更が有効な場合、`READ_CONTACTS` permission を持たないアプリの `ContactsContract.Data` query では `StrictColumns` と `StrictGrammar` options が set される。
- query がこれらの strict options と互換性のない pattern を使うと、query は rejected され、exception が throw される。
- Android 17 の Contact Picker は `READ_CONTACTS` permission の広範な付与を避ける privacy-preserving alternative として提供される。picker が返す Session URI は選択された data への一時的な read access を与え、`ContactsContract.Data` schema に従う cursor として query できる。ただし Session URI は custom `selection` / `selectionArgs` を support せず、これらを指定すると exception になる。
- ただし、local `frameworks-base` に Android 17 AOSP tag がないため、CP2 query validation 実装、targetSdkVersion gate、permission gate、strict option 設定箇所、exception type、Compat Change ID、default state は未検証である。確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

早見表（At-a-glance impact）:

| 確認項目（Question） | 回答（Answer） | 根拠（Evidence） |
| --- | --- | --- |
| Android 17 に OS アップデートしただけで適用されるか | Unknown | 公式文書は apps targeting Android 17 / API level 37 and higher と述べるが、AOSP gate 未確認。 |
| targetSdkVersion 37 以上が必要か | Likely, but unverified | 原文は targetSdkVersion 37 以上を明示している。 |
| 追加の実行時条件があるか | Yes | `READ_CONTACTS` permission なしで `ContactsContract.Data` table を query し、strict SQL と互換性のない query pattern を使う場合。 |
| Compat Change ID が関係するか | Unknown | Android 17 tag と compat framework evidence が未確認。 |

### 調査日（Investigation Date）

2026-06-11

### 信頼度（Confidence）

- Low

### 適用条件分類（Applicability Classification）

適用される条件（Applies when）:
- [ ] OS update / all apps on Android 17 regardless of targetSdkVersion
- [ ] targetSdkVersion >= 37 on Android 17+
- [ ] targetSdkVersion >= 37, with additional runtime conditions
- [ ] Mainline / Google Play system update dependent
- [ ] API addition only, not a behavior change
- [x] Unknown / needs more evidence

必要な実行時条件（Required runtime conditions）:
- Android version: Android 17 以上が前提と考えられるが、AOSP tag 未取得。
- targetSdkVersion: 公式文書上は 37 以上。
- Device/form factor: 公式抜粋では条件なし。
- Permission/API/component condition: `READ_CONTACTS` permission なし、`ContactsContract.Data` table access、`SQLiteQueryBuilder#setStrictColumns(true)`、`SQLiteQueryBuilder#setStrictGrammar(true)`。
- Related Contact Picker condition: Android 17 Contact Picker の Session URI は selected data の一時 read access を与えるが、custom `selection` / `selectionArgs` は非対応。picker 結果を通常の `ContactsContract.Data` table query と混同しないこと。
- App state/process condition: アプリが CP2 の `ContactsContract.Data` query を実行する時点。

Compat framework:
- Change ID: Unknown
- Change name: Unknown
- Default state: Unknown
- Toggleable for testing: Unknown

分類信頼度（Classification confidence）:
- Low

分類根拠（Classification evidence）:
- Official documentation page: `behavior-changes-17`
- Original applicability statement: apps targeting Android 17 / API level 37 and higher, without `READ_CONTACTS`, CP2 enforces strict SQL checks on `ContactsContract.Data` access.
- AOSP targetSdk gate: 未確認。local `frameworks-base` に `android-17*` tag がない。
- Compat framework entry: 未確認。Android 17 compat framework evidence が未取得。

---

# エグゼクティブサマリー（Executive Summary）

Android 17 では、targetSdkVersion 37 以上のアプリが `READ_CONTACTS` permission なしで `ContactsContract.Data` table を query する場合、CP2 が strict SQL query validation を強制する、と公式文書は説明している。`StrictColumns` と `StrictGrammar` が有効になり、互換性のない query pattern は rejected され、exception が throw される。

この変更は、Contacts Provider への query で raw SQL 的な selection / sort / projection、未許可 column、複雑な expression などに依存しているアプリに影響する可能性がある。特に `READ_CONTACTS` を持たずに Data table へ限定アクセスしている実装は、targetSdkVersion 37 更新前に query を棚卸しする必要がある。

Android 17 では Contact Picker も追加され、アプリは `READ_CONTACTS` permission で address book 全体にアクセスする代わりに、必要な data fields を指定し、ユーザーが選択した contact data だけを Session URI 経由で受け取れる。picker 結果の Session URI は `ContactsContract.Data` schema の cursor として読めるが、custom `selection` / `selectionArgs` は非対応である。したがって、Contact Picker を使う path は、通常の `ContactsContract.Data.CONTENT_URI` への任意 query と分けて扱う必要がある。

ただし、現時点の local `frameworks-base` には Android 17 AOSP tag がないため、実装差分、targetSdkVersion gate、permission 判定、exception type、Compat Change ID は未確認である。

---

# 公式ドキュメント確認（Original Documentation）

## 原文（Statement）

Page title:
- Behavior changes: Apps targeting Android 17 or higher

Page URL:
- https://developer.android.com/about/versions/17/behavior-changes-17

Page type:
- apps targeting Android 17

Section title:
- Enforce strict SQL checks in CP2

Original statement being verified:

> For apps targeting Android 17 (API level Android 17 (API level 37)) and higher, Contacts Provider 2 (CP2) enforces strict SQL query validation when the ContactsContract.Data table is accessed without READ_CONTACTS permission.

The supplied official text states that if an app doesn't have `READ_CONTACTS` permission, `StrictColumns` and `StrictGrammar` options are set when querying the `ContactsContract.Data` table. If a query uses a pattern that isn't compatible with these options, it is rejected and causes an exception.

## 解釈（Interpretation）

この変更は、Contacts Provider に対する SQL query surface を厳格化し、`READ_CONTACTS` permission を持たないアプリが `ContactsContract.Data` table へアクセスする際の query pattern を制限する privacy / security behavior change である。

アプリ開発者にとって重要なのは、targetSdkVersion 37 更新後、これまで動作していた `ContactsContract.Data` query が、strict columns / strict grammar に合わない場合に runtime exception として失敗する可能性がある点である。permission を取得するだけでなく、query を provider が許容する column と grammar に沿った形へ修正する必要がある。

---

# 変更内容（What Changed）

公式文書上の変更点:
- Android 17 / targetSdkVersion 37 以上のアプリでは、CP2 が `ContactsContract.Data` table access に strict SQL query validation を適用する。
- 適用条件は、アプリが `READ_CONTACTS` permission を持たずに `ContactsContract.Data` table にアクセスする場合。
- `READ_CONTACTS` permission がない場合、`StrictColumns` と `StrictGrammar` options が set される。
- query が strict options と互換性のない pattern を使う場合、query は rejected され、exception が throw される。
- Contact Picker は `ACTION_PICK_CONTACTS` と requested data fields により、ユーザーが選択した data だけを返す別 path である。結果の Session URI は一時 read access を与え、`ContactsContract.Data` schema に沿った cursor を返す。
- Contact Picker Session URI は custom `selection` / `selectionArgs` を support しない。公式ページは、これらを指定すると exception が発生すると説明している。

AOSP で未確認の点:
- Android 16 baseline で `READ_CONTACTS` なしの `ContactsContract.Data` query に strict columns / grammar が適用されていなかったか。
- Android 17 で `setStrictColumns(true)` / `setStrictGrammar(true)` が設定される実装箇所。
- targetSdkVersion 37 gate の実装箇所。
- `READ_CONTACTS` permission 判定の具体的な path。
- incompatible query pattern の具体例と exception type。
- Contacts Provider 実装が `frameworks-base` ではなく `packages/providers/ContactsProvider` に存在する場合の evidence boundary。
- Compat Change ID と default state。

## 適用条件（Applicability）

公式文書の一次判断では、Android 17 以上、targetSdkVersion 37 以上、`READ_CONTACTS` permission を持たずに `ContactsContract.Data` table を query するアプリに適用される。AOSP tag が未取得のため、確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

### OS アップデート時の挙動（OS Update Behavior）

- Android 17 にアップデートしただけで適用されるか: Unknown
- targetSdkVersion に依存しない根拠: なし。原文は apps targeting Android 17 / API level 37 and higher と明示している。
- Android 16 以前での挙動: 未確認。Android 17 tag との明示的な比較ができないため、Android 16 source だけから platform evidence として断定しない。

### targetSdkVersion 37 以上での挙動（targetSdkVersion 37 Behavior）

- targetSdkVersion 37 以上で適用されるか: 公式文書上は Yes と読めるが、AOSP gate 未確認。
- Android 17 以外で targetSdkVersion 37 にした場合の挙動: Unknown。公式文書は Android 17 Behavior Changes として説明しているため、Android 17 platform behavior として扱う。
- opt-out / temporary override の有無: Unknown。公式抜粋には opt-out は示されていない。compat framework による force enable / disable は未確認。

### その他の条件（Other Conditions）

- device/form factor: 公式抜粋では条件なし。
- permission: `READ_CONTACTS` permission がないことが公式文書上の追加条件。
- API usage: `ContactsContract.Data` query、Contact Picker Session URI query、`SQLiteQueryBuilder#setStrictColumns(boolean)`、`SQLiteQueryBuilder#setStrictGrammar(boolean)`、projection / selection / sort order / query grammar。
- manifest attribute: `android.permission.READ_CONTACTS` declaration と runtime grant state が関係する。
- component boundary: app process、ContentResolver query、Contact Picker Session URI、Contacts Provider 2 query validation、SQLiteQueryBuilder strict columns / grammar にまたがる。

---

# AOSP 調査（AOSP Investigation）

## checkout 状態（Checkout Status）

Commands checked before evidence use:

```bash
git -C frameworks-base status --short
git -C frameworks-base tag --list android-16.0.0_r4
git -C frameworks-base tag --list 'android-17*'
```

Result:
- `frameworks-base` working tree: clean at the time of investigation.
- From tag: `android-16.0.0_r4` exists.
- To tag: no local `android-17*` tag found.

根拠上の制約（Evidence limitation）:
- Android 17 AOSP tag が local `frameworks-base` に存在しないため、`git -C frameworks-base diff android-16.0.0_r4 <android-17-tag> -- ...` による明示的な tag 比較を実行できない。
- Repository rule に従い、Android 17 working tree や推測による source evidence は採用しない。
- CP2 の実装本体は `frameworks-base` ではなく ContactsProvider project 側にある可能性が高いが、この mission は `frameworks-base` evidence を対象としているため、Android 17 tag 入手後も API surface / constants / compat framework の確認と、必要に応じた provider project evidence の追加が必要である。
- この制約により、AOSP-backed conclusion は High confidence にできない。

## 関連ファイル（Related Files）

未確認。Android 17 AOSP tag 取得後に、少なくとも以下の候補を tag 比較で確認する必要がある。

- `core/java/android/provider/ContactsContract.java`
- `core/java/android/database/sqlite/SQLiteQueryBuilder.java`
- `core/java/android/Manifest.java`
- `core/api/current.txt`
- compat framework 定義ファイル内の CP2 / ContactsProvider / strict SQL / targetSdkVersion 37 関連 Change ID
- `packages/providers/ContactsProvider` 側の ContactsProvider2 実装、Data table query routing、permission check、`SQLiteQueryBuilder` strict option 設定箇所

Note:
- `frameworks-base` には `ContactsContract` constants、`SQLiteQueryBuilder` API、`READ_CONTACTS` permission definition が含まれる可能性がある。一方、`READ_CONTACTS` がない場合に CP2 query へ strict options を設定する実装は ContactsProvider 側にある可能性が高い。最終 confidence には provider implementation evidence が必要である。

## 確認したソース文脈（Source Context Reviewed）

Android 17 AOSP tag がないため、source context は未レビュー。

| File / symbol | Android 16 baseline | Android 17 behavior | Why this code path matters |
| --- | --- | --- | --- |
| Not reviewed | Not reviewed | Not reviewed | Android 17 tag がないため、公式文書の記述を AOSP diff で検証できない。 |

Required context:
- Entry point / caller: 未確認。想定される entry point は app の `ContentResolver.query(ContactsContract.Data.CONTENT_URI, ...)`、ContactsProvider query routing、`READ_CONTACTS` permission check、`SQLiteQueryBuilder` strict options だが、AOSP evidence としては未採用。
- Relevant class or service responsibility: 未確認。
- Runtime path from app API / system event to changed code: 未確認。
- Why unrelated code paths were excluded: Android 17 tag 不在のため、source path の採否判断自体を保留。

## 差分解釈（Diff Interpretation）

| Observed diff | Interpretation | Behavior Change relevance | Confidence |
| --- | --- | --- | --- |
| No Android 17 tag diff available | Source diff type cannot be classified yet | 公式文書の strict SQL validation、permission condition、targetSdkVersion gate、exception behavior を source diff で裏取りできていない | Low |

Required interpretation:
- Added behavior: 未確認。公式文書上は strict validation の追加または適用拡大の可能性がある。
- Removed behavior: 未確認。
- Changed condition / gate: 未確認。targetSdkVersion 37 と `READ_CONTACTS` permission gate がある可能性は高いが、AOSP 未確認。
- Changed default: 未確認。
- No behavior change found: 未確認。tag 不在のため「no behavior change」とは判断しない。

## 事実（Evidence）

Facts:
- 公式 Behavior Change 文書は、targetSdkVersion 37 以上のアプリに対し、`READ_CONTACTS` permission なしで `ContactsContract.Data` table にアクセスする場合に CP2 が strict SQL query validation を強制すると述べている。
- 公式文書は、`READ_CONTACTS` permission がない場合に `StrictColumns` と `StrictGrammar` options が set されると述べている。
- 公式文書は、query がこれらと互換性のない pattern を使う場合、query が rejected され exception が throw されると述べている。
- 公式 Contact Picker 文書は、Android 17 以上で Contact Picker が broad `READ_CONTACTS` permission の代替として利用でき、アプリが必要な data fields を指定し、ユーザーが選択した contact data だけを共有できると説明している。
- 公式 Contact Picker 文書は、picker 完了時に Session URI が返り、その URI が selected data への temporary read access を与えると説明している。
- 公式 Contact Picker 文書は、Session URI を standard `ContentResolver` で query でき、結果 cursor は `ContactsContract.Data` schema に従うと説明している。
- 公式 Contact Picker 文書は、Contact Picker Session URI が custom `selection` / `selectionArgs` を support せず、これらを設定すると exception になると説明している。
- local `frameworks-base` には `android-16.0.0_r4` tag がある。
- local `frameworks-base` には `android-17*` tag がない。
- 調査時点で `frameworks-base` working tree は clean。

Observations:
- 公式ページ種別は targetSdkVersion 37 以上向けである。
- 原文は targetSdkVersion 37 以上を明示しており、targetSdkVersion 37 gate がある可能性が高い。
- この項目は targetSdkVersion 37 条件に加えて、`READ_CONTACTS` permission がないこと、`ContactsContract.Data` table access、SQL query pattern という runtime / API usage condition を含む。
- `StrictColumns` と `StrictGrammar` は `SQLiteQueryBuilder` の query validation 機能であり、raw SQL expression や未許可 column への依存を制限する方向の変更と読める。
- Contact Picker は permission なし contacts access の推奨代替 path になり得るが、picker が返す Session URI も任意の SQL query surface ではない。custom selection / selectionArgs を使う既存の Data query logic をそのまま流用すると、picker path でも exception が発生し得る。
- Contact Picker が `ContactsContract.Data` schema の cursor を返すことは、アプリ側の data parsing を既存 Data cursor に近い形へ寄せられる一方、通常の `ContactsContract.Data.CONTENT_URI` query と同じ permission / query grammar で扱えることを意味しない。
- AOSP tag がないため、実装が本当に targetSdkVersion 37 gate で制御されているかは未確認。
- Compat framework entry の有無も未確認。

Hypotheses:
- Android 17 / targetSdkVersion 37 以上で `READ_CONTACTS` を持たないアプリは、`ContactsContract.Data` query の projection / selection / sort order に strict validation と互換性のない SQL fragment を含めると exception を受ける可能性が高い。
- Android 17 / targetSdkVersion 36 のアプリでは旧 query behavior が維持される可能性があるが、AOSP gate 未確認のため断定しない。
- `READ_CONTACTS` permission を持つアプリではこの strict setting が適用されない可能性があるが、permission grant state、provider policy、other access restrictions は未確認である。
- Contact Picker へ移行するアプリでは、Session URI から選択済み data を読む設計にすれば broad `READ_CONTACTS` を避けられる可能性がある。ただし、既存の `ContactsContract.Data` query と同じ selection / selectionArgs / sortOrder 前提の helper を流用する場合は修正が必要になる可能性がある。

結論:
- 現時点で顧客向けに確定できるのは、「公式文書上は Android 17 / targetSdkVersion 37 以上のアプリが `READ_CONTACTS` なしで `ContactsContract.Data` を query する場合、strict SQL validation により互換性のない query が exception で失敗する」という範囲まで。
- Contact Picker はこのリスクを避ける代替導線になり得るが、picker 結果の Session URI は selected data 専用の一時 access であり、custom selection / selectionArgs は使えない。通常の CP2 Data query 厳格化とは別に、picker result query の制約として説明する必要がある。
- AOSP gate、ContactsProvider の permission / query validation 実装、exception type、compat framework default state が未確認のため、primary classification は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

## 適用ゲート根拠（Applicability Gate Evidence）

- targetSdkVersion gate: 未確認。公式文書は targetSdkVersion 37 以上を示すが、AOSP gate evidence はない。
- CompatChanges.isChangeEnabled / ChangeId: 未確認。Android 17 tag がないため検索未実施。
- @EnabledAfter / @EnabledSince / default state: 未確認。Android 17 tag がないため検索未実施。
- Build.VERSION / SDK_INT gate: 未確認。
- DeviceConfig / resources config: 未確認。
- Permission/AppOps gate: 未確認。公式文書上は `READ_CONTACTS` permission なしが条件だが、AOSP の permission / AppOps path は未確認。
- Manifest/property gate: `READ_CONTACTS` permission declaration / runtime grant state が関係するが、AOSP gate evidence は未確認。
- No gate found: 未確認。Android 17 tag がないため「gate がない」とは判断しない。
- Gate conclusion: Unknown。公式文書の wording から targetSdkVersion 37 + no `READ_CONTACTS` + `ContactsContract.Data` query condition と推定されるが、AOSP で検証できていない。
- Reasoning from source context: source context 未レビューのため未確定。

---

# 影響分析（Impact Analysis）

## 影響を受けるアプリ（Affected Apps）

影響を受ける可能性があるアプリ:
- `READ_CONTACTS` permission なしで `ContactsContract.Data` table を query しているアプリ。
- `ContactsContract.Data` query の projection、selection、sort order に SQL expression、関数、subquery、未定義 column、alias など strict validation と互換性がない可能性のある pattern を使っているアプリ。
- contacts data への限定アクセスを前提に、permission なしで lookup / filtering / search / matching を行うアプリ。
- Contact Picker へ移行する際に、picker が返す Session URI に対して既存の `ContactsContract.Data` query helper をそのまま流用し、custom `selection` / `selectionArgs` を指定するアプリ。
- targetSdkVersion 37 への更新を予定しており、Contacts Provider query grammar をまだ棚卸ししていないアプリ。

## 影響を受けないアプリ（Non-Affected Apps）

影響が限定的または対象外と考えられるケース:
- Contacts Provider を使わないアプリ。
- `ContactsContract.Data` table を query しないアプリ。
- Contact Picker の Session URI だけを query し、custom `selection` / `selectionArgs` を指定せず、返された selected data の cursor を処理するアプリ。
- `READ_CONTACTS` permission を取得済みで、該当 provider access が許可されているアプリ。ただし AOSP gate 未確認のため断定しない。
- `ContactsContract.Data` query が strict columns / strict grammar と互換性のある単純な projection / selection / sort order だけを使うアプリ。
- Android 17 AOSP tag 取得後に対象外 gate や exemption が確認されたケース。

---

# 顧客影響（Customer Impact）

顧客説明用。

## 影響度（Impact Level）

- Human decision required

※ 仮評価。最終判断は人間が行う。

## ビジネス影響（Business Impact）

- ユーザー影響: contacts search、lookup、候補表示、連携先 matching が query exception により失敗し、該当機能が動作しなくなる可能性がある。Contact Picker へ移行した場合でも、Session URI に非対応 query parameter を渡すと picker 後の data 取得が失敗する可能性がある。
- 運用影響: Contacts Provider query の SQL pattern、permission model、Contact Picker 移行 path、exception handling、targetSdkVersion 37 テストを確認する必要がある可能性がある。
- 開発影響: raw SQL 的な query fragment の削減、許可された columns / grammar への修正、`READ_CONTACTS` permission の必要性再評価、Contact Picker Session URI 用 query path の分離、query exception handling の追加が必要になる可能性がある。

---

# サービス影響例（Service Impact Examples）

このセクションは、公式文書と AOSP evidence から導いた「起こりうる影響例」を記録する。特定サービスで実際に発生確認した事実ではない。

## 例1（Example 1）: READ_CONTACTS なしの連絡先検索

- 対象サービス例: 共有先候補、連絡先候補表示、電話番号 / メール補完。
- 影響を受ける実装パターン: `READ_CONTACTS` なしで `ContactsContract.Data` を query し、selection / sortOrder に raw SQL fragment を含める実装。
- 発生条件: Android 17 / targetSdkVersion 37 で strict columns / strict grammar と非互換の query を実行する場合。
- ユーザーに見える症状: 候補が表示されない、検索が失敗する、query exception で feature が停止する可能性。
- 開発・運用への影響: query grammar 修正、permission denied path の QA、exception handling の追加が必要になる可能性。
- 推奨対応候補: documented columns と parameterized selection に寄せ、strict-compatible query に修正する。
- 根拠: 公式 statement と report の expected behavior。
- Confidence（信頼度）: Low
- 注意: exception type と exact validation は AOSP tag 待ち。

## 例2（Example 2）: Contact Picker へ移行する連絡先選択 UI

- 対象サービス例: メール宛先選択、SMS 送信先選択、共有先選択、招待先選択。
- 影響を受ける実装パターン: `ACTION_PICK_CONTACTS` または Android 17 で自動 upgrade された `ACTION_PICK` の結果 Session URI に対し、既存の `ContactsContract.Data` query helper を流用して custom `selection` / `selectionArgs` を指定する実装。
- 発生条件: Contact Picker の Session URI を query する際に、公式文書で非対応とされる custom `selection` / `selectionArgs` を設定する場合。
- ユーザーに見える症状: picker では選択できるが、選択後の data 取得が exception で失敗し、宛先や連絡先情報が反映されない可能性。
- 開発・運用への影響: picker result 用の query path を通常の `ContactsContract.Data.CONTENT_URI` query と分離し、Session URI は projection のみで直接 query する設計へ修正する必要がある可能性。
- 推奨対応候補: Contact Picker では requested data fields を intent extra で指定し、返された Session URI に対して custom selection を使わず、cursor の `LOOKUP_KEY` / `MIMETYPE` / `DATA1` などを app 側で group / filter する。
- 根拠: 公式 Contact Picker 文書と report の expected behavior。
- Confidence（信頼度）: Medium for documentation behavior / Low for AOSP implementation details
- 注意: Contact Picker 自体は broad `READ_CONTACTS` permission の代替であり、通常の CP2 Data table query strict SQL change と同一の gate かは AOSP 未確認。

## 例3（Example 3）: CRM / matching 機能の provider query

- 対象サービス例: CRM 連携、名刺管理、営業支援、messaging matching。
- 影響を受ける実装パターン: permission なしで Data table へ複雑な SQL expression / alias / function を投げる matching query。
- 発生条件: strict grammar が有効になり、provider が query pattern を reject する場合。
- ユーザーに見える症状: matching 精度低下、連絡先連携失敗、機能の一部が空表示になる可能性。
- 開発・運用への影響: query simplification、local DB への同期設計、permission request の必要性再評価が必要になる可能性。
- 推奨対応候補: provider query を単純化し、必要な処理は app 側で post-process する。
- 根拠: 公式 statement と report の action candidates。
- Confidence（信頼度）: Low
- 注意: 実サービスでの発生確認ではない。

---

# 対応候補（Required Actions）

## 必須対応（Must）

- `ContactsContract.Data` query を棚卸しし、`READ_CONTACTS` permission なしで実行される path を特定する。
- projection、selection、selectionArgs、sortOrder に raw SQL fragment、関数、subquery、alias、未定義 column がないか確認する。
- strict columns / strict grammar と互換性がある query へ修正する。
- Contact Picker を使う path では、Session URI に custom `selection` / `selectionArgs` を指定していないか確認し、通常の `ContactsContract.Data.CONTENT_URI` query helper と分離する。
- query exception を捕捉し、機能全体が crash しないよう error handling を確認する。
- Android 17 / targetSdkVersion 37 のテスト環境が利用可能になったら、`READ_CONTACTS` grant あり / なしの両方で query 結果を検証する。
- Android 17 AOSP tag 入手後に、targetSdkVersion gate、permission gate、exception type、compat Change ID を再確認する。

## 推奨対応（Recommended）

- contacts access が本当に `READ_CONTACTS` permission なしで成立する必要があるか、privacy / UX 観点で見直す。
- ユーザーが選択した contact data だけで要件を満たせる機能は、Contact Picker への移行を検討する。
- query をできるだけ documented columns と parameterized selection に寄せ、provider-specific SQL behavior への依存を減らす。
- Contact Picker では intent の requested data fields で必要最小限の MIME type を指定し、返却 cursor は app 側で group / post-process する。
- test data と query test を追加し、targetSdkVersion 36 / 37、permission grant / denied の matrix を自動化する。
- Contacts Provider query failure をログとメトリクスで検出できるようにする。

## 任意対応（Optional）

- `SQLiteQueryBuilder#setStrictColumns` / `setStrictGrammar` の既存仕様を参考に、アプリ内 query builder でも同等の validation を早期に走らせる。
- contacts feature の fallback UX を用意し、permission なしで query が拒否された場合の表示を整理する。

---

# 検証方法（Verification Method）

## 検証マトリクス（Matrix）

| Device OS | targetSdkVersion | Compat flag | Expected behavior |
| --- | --- | --- | --- |
| Android 16 | 36 | default | Android 16 baseline。`READ_CONTACTS` なし Data query の strict validation は Android 17 tag 比較待ち。 |
| Android 17 | 36 | default | Unknown。この section は targetSdkVersion 37+ 向けだが、AOSP gate 未確認。 |
| Android 17 | 37 | default | 公式文書上、`READ_CONTACTS` なしで `ContactsContract.Data` を query すると strict columns / grammar が適用され、非互換 query は exception。 |
| Android 17 | 36 | force-enabled if available | Unknown。Compat Change ID 未確認。 |
| Android 17 | 37 | force-disabled if available | Unknown。Compat Change ID 未確認。 |

## 手順（Steps）

- targetSdk変更: targetSdkVersion 36 と 37 の test build を用意する。
- compat framework command: 未確認。Android 17 compat framework entry / Change ID が判明後に記録する。
- テスト方法: `READ_CONTACTS` grant あり / なし、strict-compatible query / incompatible query を分けて `ContactsContract.Data` query を実行する。
- Contact Picker テスト方法: `ACTION_PICK_CONTACTS` で phone / email などの requested data fields を指定し、返却 Session URI を custom `selection` / `selectionArgs` なしで query する path と、誤って指定する path を分けて結果を確認する。
- 再現手順: Android 17 device / emulator で対象アプリを install し、`READ_CONTACTS` を deny した状態で Data table query を実行する。projection、selection、sortOrder の pattern ごとに cursor / exception を記録する。
- 期待結果: targetSdkVersion 37 かつ `READ_CONTACTS` なしの場合、strict SQL validation と互換性のない query は rejected され exception が throw される。具体的な exception type は AOSP tag と実機検証待ち。

---

# 結論（Conclusion）

公式文書上、Android 17 / targetSdkVersion 37 以上のアプリでは、`READ_CONTACTS` permission なしで `ContactsContract.Data` table を query する場合に CP2 が strict SQL checks を強制する。非互換 query は exception で失敗するため、permission なし Data query を持つアプリは SQL pattern と error handling の棚卸しが必要である。

Android 17 Contact Picker は、address book 全体への `READ_CONTACTS` access を避け、ユーザーが選択した contact data だけを Session URI として返す代替 path である。Contact Picker を使う場合は、通常の Data table query と同じ selection logic を流用せず、Session URI の制約に合わせて query / parsing を分離する必要がある。

ただし、Android 17 AOSP tag が local checkout にないため、実装 gate、ContactsProvider validation path、exception type、compat framework の確認は未完了である。最終的な適用分類と顧客向け確定説明は、Android 17 AOSP tag 入手後に再調査が必要である。

---

# 人間の判断欄（Human Decision Placeholder）

最終優先度（Final Priority）:
- Human decision required

Final Severity:
- Human decision required

Release Readiness:
- Human decision required

Customer Communication Priority:
- Human decision required

判断（Decision）:
- Further investigation required

Decision notes:
- Android 17 AOSP tag 入手後に、AOSP evidence と compat framework evidence を確認してから最終判断する。

---

# 参照（References）

## ドキュメント（Documentation）

- https://developer.android.com/about/versions/17/behavior-changes-17
- https://developer.android.com/reference/android/provider/ContactsContract.Data
- https://developer.android.com/reference/android/Manifest.permission#READ_CONTACTS
- https://developer.android.com/reference/android/database/sqlite/SQLiteQueryBuilder#setStrictColumns(boolean)
- https://developer.android.com/reference/android/database/sqlite/SQLiteQueryBuilder#setStrictGrammar(boolean)
- https://developer.android.com/about/versions/17/features/contact-picker

## AOSP

- Not available for Android 17 in local `frameworks-base`.
- From tag checked: `android-16.0.0_r4`
- To tag checked: no local `android-17*` tag found.
