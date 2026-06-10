# Enforce strict SQL checks in CP2

## Metadata

### Android Versions

From:
- android-16.0.0_r4

To:
- TBD: Android 17 AOSP tag

Previous targetSdkVersion:
- 36

Target targetSdkVersion:
- 37

### Behavior Change Source

Document:
https://developer.android.com/about/versions/17/behavior-changes-17

Related documents:
- https://developer.android.com/reference/android/provider/ContactsContract.Data
- https://developer.android.com/reference/android/Manifest.permission#READ_CONTACTS
- https://developer.android.com/reference/android/database/sqlite/SQLiteQueryBuilder#setStrictColumns(boolean)
- https://developer.android.com/reference/android/database/sqlite/SQLiteQueryBuilder#setStrictGrammar(boolean)

Section:
Enforce strict SQL checks in CP2

Page type:
- Apps targeting Android 17 or higher

### Classification Snapshot

Primary classification:
- UNKNOWN_NEEDS_MORE_EVIDENCE

Initial applicability assumption from official documentation:
- 公式文書は、targetSdkVersion 37 以上のアプリが `READ_CONTACTS` permission なしで `ContactsContract.Data` table にアクセスする場合、Contacts Provider 2 (CP2) が strict SQL query validation を強制すると説明している。
- 変更が有効な場合、`READ_CONTACTS` permission を持たないアプリの `ContactsContract.Data` query では `StrictColumns` と `StrictGrammar` options が set される。
- query がこれらの strict options と互換性のない pattern を使うと、query は rejected され、exception が throw される。
- ただし、local `frameworks-base` に Android 17 AOSP tag がないため、CP2 query validation 実装、targetSdkVersion gate、permission gate、strict option 設定箇所、exception type、Compat Change ID、default state は未検証である。確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

At-a-glance impact:

| Question | Answer | Evidence |
| --- | --- | --- |
| Android 17 OS update only? | Unknown | 公式文書は apps targeting Android 17 / API level 37 and higher と述べるが、AOSP gate 未確認。 |
| targetSdkVersion 37 required? | Likely, but unverified | 原文は targetSdkVersion 37 以上を明示している。 |
| Additional runtime conditions? | Yes | `READ_CONTACTS` permission なしで `ContactsContract.Data` table を query し、strict SQL と互換性のない query pattern を使う場合。 |
| Compat Change ID involved? | Unknown | Android 17 tag と compat framework evidence が未確認。 |

### Investigation Date

2026-06-11

### Confidence

- Low

### Applicability Classification

Applies when:
- [ ] OS update / all apps on Android 17 regardless of targetSdkVersion
- [ ] targetSdkVersion >= 37 on Android 17+
- [ ] targetSdkVersion >= 37, with additional runtime conditions
- [ ] Mainline / Google Play system update dependent
- [ ] API addition only, not a behavior change
- [x] Unknown / needs more evidence

Required runtime conditions:
- Android version: Android 17 以上が前提と考えられるが、AOSP tag 未取得。
- targetSdkVersion: 公式文書上は 37 以上。
- Device/form factor: 公式抜粋では条件なし。
- Permission/API/component condition: `READ_CONTACTS` permission なし、`ContactsContract.Data` table access、`SQLiteQueryBuilder#setStrictColumns(true)`、`SQLiteQueryBuilder#setStrictGrammar(true)`。
- App state/process condition: アプリが CP2 の `ContactsContract.Data` query を実行する時点。

Compat framework:
- Change ID: Unknown
- Change name: Unknown
- Default state: Unknown
- Toggleable for testing: Unknown

Classification confidence:
- Low

Classification evidence:
- Official documentation page: `behavior-changes-17`
- Original applicability statement: apps targeting Android 17 / API level 37 and higher, without `READ_CONTACTS`, CP2 enforces strict SQL checks on `ContactsContract.Data` access.
- AOSP targetSdk gate: 未確認。local `frameworks-base` に `android-17*` tag がない。
- Compat framework entry: 未確認。Android 17 compat framework evidence が未取得。

---

# Executive Summary

Android 17 では、targetSdkVersion 37 以上のアプリが `READ_CONTACTS` permission なしで `ContactsContract.Data` table を query する場合、CP2 が strict SQL query validation を強制する、と公式文書は説明している。`StrictColumns` と `StrictGrammar` が有効になり、互換性のない query pattern は rejected され、exception が throw される。

この変更は、Contacts Provider への query で raw SQL 的な selection / sort / projection、未許可 column、複雑な expression などに依存しているアプリに影響する可能性がある。特に `READ_CONTACTS` を持たずに Data table へ限定アクセスしている実装は、targetSdkVersion 37 更新前に query を棚卸しする必要がある。

ただし、現時点の local `frameworks-base` には Android 17 AOSP tag がないため、実装差分、targetSdkVersion gate、permission 判定、exception type、Compat Change ID は未確認である。

---

# Original Documentation

## Statement

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

## Interpretation

この変更は、Contacts Provider に対する SQL query surface を厳格化し、`READ_CONTACTS` permission を持たないアプリが `ContactsContract.Data` table へアクセスする際の query pattern を制限する privacy / security behavior change である。

アプリ開発者にとって重要なのは、targetSdkVersion 37 更新後、これまで動作していた `ContactsContract.Data` query が、strict columns / strict grammar に合わない場合に runtime exception として失敗する可能性がある点である。permission を取得するだけでなく、query を provider が許容する column と grammar に沿った形へ修正する必要がある。

---

# What Changed

公式文書上の変更点:
- Android 17 / targetSdkVersion 37 以上のアプリでは、CP2 が `ContactsContract.Data` table access に strict SQL query validation を適用する。
- 適用条件は、アプリが `READ_CONTACTS` permission を持たずに `ContactsContract.Data` table にアクセスする場合。
- `READ_CONTACTS` permission がない場合、`StrictColumns` と `StrictGrammar` options が set される。
- query が strict options と互換性のない pattern を使う場合、query は rejected され、exception が throw される。

AOSP で未確認の点:
- Android 16 baseline で `READ_CONTACTS` なしの `ContactsContract.Data` query に strict columns / grammar が適用されていなかったか。
- Android 17 で `setStrictColumns(true)` / `setStrictGrammar(true)` が設定される実装箇所。
- targetSdkVersion 37 gate の実装箇所。
- `READ_CONTACTS` permission 判定の具体的な path。
- incompatible query pattern の具体例と exception type。
- Contacts Provider 実装が `frameworks-base` ではなく `packages/providers/ContactsProvider` に存在する場合の evidence boundary。
- Compat Change ID と default state。

## Applicability

公式文書の一次判断では、Android 17 以上、targetSdkVersion 37 以上、`READ_CONTACTS` permission を持たずに `ContactsContract.Data` table を query するアプリに適用される。AOSP tag が未取得のため、確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

### OS Update Behavior

- Android 17 にアップデートしただけで適用されるか: Unknown
- targetSdkVersion に依存しない根拠: なし。原文は apps targeting Android 17 / API level 37 and higher と明示している。
- Android 16 以前での挙動: 未確認。Android 17 tag との明示的な比較ができないため、Android 16 source だけから platform evidence として断定しない。

### targetSdkVersion 37 Behavior

- targetSdkVersion 37 以上で適用されるか: 公式文書上は Yes と読めるが、AOSP gate 未確認。
- Android 17 以外で targetSdkVersion 37 にした場合の挙動: Unknown。公式文書は Android 17 Behavior Changes として説明しているため、Android 17 platform behavior として扱う。
- opt-out / temporary override の有無: Unknown。公式抜粋には opt-out は示されていない。compat framework による force enable / disable は未確認。

### Other Conditions

- device/form factor: 公式抜粋では条件なし。
- permission: `READ_CONTACTS` permission がないことが公式文書上の追加条件。
- API usage: `ContactsContract.Data` query、`SQLiteQueryBuilder#setStrictColumns(boolean)`、`SQLiteQueryBuilder#setStrictGrammar(boolean)`、projection / selection / sort order / query grammar。
- manifest attribute: `android.permission.READ_CONTACTS` declaration と runtime grant state が関係する。
- component boundary: app process、ContentResolver query、Contacts Provider 2 query validation、SQLiteQueryBuilder strict columns / grammar にまたがる。

---

# AOSP Investigation

## Checkout Status

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

Evidence limitation:
- Android 17 AOSP tag が local `frameworks-base` に存在しないため、`git -C frameworks-base diff android-16.0.0_r4 <android-17-tag> -- ...` による明示的な tag 比較を実行できない。
- Repository rule に従い、Android 17 working tree や推測による source evidence は採用しない。
- CP2 の実装本体は `frameworks-base` ではなく ContactsProvider project 側にある可能性が高いが、この mission は `frameworks-base` evidence を対象としているため、Android 17 tag 入手後も API surface / constants / compat framework の確認と、必要に応じた provider project evidence の追加が必要である。
- この制約により、AOSP-backed conclusion は High confidence にできない。

## Related Files

未確認。Android 17 AOSP tag 取得後に、少なくとも以下の候補を tag 比較で確認する必要がある。

- `core/java/android/provider/ContactsContract.java`
- `core/java/android/database/sqlite/SQLiteQueryBuilder.java`
- `core/java/android/Manifest.java`
- `core/api/current.txt`
- compat framework 定義ファイル内の CP2 / ContactsProvider / strict SQL / targetSdkVersion 37 関連 Change ID
- `packages/providers/ContactsProvider` 側の ContactsProvider2 実装、Data table query routing、permission check、`SQLiteQueryBuilder` strict option 設定箇所

Note:
- `frameworks-base` には `ContactsContract` constants、`SQLiteQueryBuilder` API、`READ_CONTACTS` permission definition が含まれる可能性がある。一方、`READ_CONTACTS` がない場合に CP2 query へ strict options を設定する実装は ContactsProvider 側にある可能性が高い。最終 confidence には provider implementation evidence が必要である。

## Source Context Reviewed

Android 17 AOSP tag がないため、source context は未レビュー。

| File / symbol | Android 16 baseline | Android 17 behavior | Why this code path matters |
| --- | --- | --- | --- |
| Not reviewed | Not reviewed | Not reviewed | Android 17 tag がないため、公式文書の記述を AOSP diff で検証できない。 |

Required context:
- Entry point / caller: 未確認。想定される entry point は app の `ContentResolver.query(ContactsContract.Data.CONTENT_URI, ...)`、ContactsProvider query routing、`READ_CONTACTS` permission check、`SQLiteQueryBuilder` strict options だが、AOSP evidence としては未採用。
- Relevant class or service responsibility: 未確認。
- Runtime path from app API / system event to changed code: 未確認。
- Why unrelated code paths were excluded: Android 17 tag 不在のため、source path の採否判断自体を保留。

## Diff Interpretation

| Observed diff | Interpretation | Behavior Change relevance | Confidence |
| --- | --- | --- | --- |
| No Android 17 tag diff available | Source diff type cannot be classified yet | 公式文書の strict SQL validation、permission condition、targetSdkVersion gate、exception behavior を source diff で裏取りできていない | Low |

Required interpretation:
- Added behavior: 未確認。公式文書上は strict validation の追加または適用拡大の可能性がある。
- Removed behavior: 未確認。
- Changed condition / gate: 未確認。targetSdkVersion 37 と `READ_CONTACTS` permission gate がある可能性は高いが、AOSP 未確認。
- Changed default: 未確認。
- No behavior change found: 未確認。tag 不在のため「no behavior change」とは判断しない。

## Evidence

Facts:
- 公式 Behavior Change 文書は、targetSdkVersion 37 以上のアプリに対し、`READ_CONTACTS` permission なしで `ContactsContract.Data` table にアクセスする場合に CP2 が strict SQL query validation を強制すると述べている。
- 公式文書は、`READ_CONTACTS` permission がない場合に `StrictColumns` と `StrictGrammar` options が set されると述べている。
- 公式文書は、query がこれらと互換性のない pattern を使う場合、query が rejected され exception が throw されると述べている。
- local `frameworks-base` には `android-16.0.0_r4` tag がある。
- local `frameworks-base` には `android-17*` tag がない。
- 調査時点で `frameworks-base` working tree は clean。

Observations:
- 公式ページ種別は targetSdkVersion 37 以上向けである。
- 原文は targetSdkVersion 37 以上を明示しており、targetSdkVersion 37 gate がある可能性が高い。
- この項目は targetSdkVersion 37 条件に加えて、`READ_CONTACTS` permission がないこと、`ContactsContract.Data` table access、SQL query pattern という runtime / API usage condition を含む。
- `StrictColumns` と `StrictGrammar` は `SQLiteQueryBuilder` の query validation 機能であり、raw SQL expression や未許可 column への依存を制限する方向の変更と読める。
- AOSP tag がないため、実装が本当に targetSdkVersion 37 gate で制御されているかは未確認。
- Compat framework entry の有無も未確認。

Hypotheses:
- Android 17 / targetSdkVersion 37 以上で `READ_CONTACTS` を持たないアプリは、`ContactsContract.Data` query の projection / selection / sort order に strict validation と互換性のない SQL fragment を含めると exception を受ける可能性が高い。
- Android 17 / targetSdkVersion 36 のアプリでは旧 query behavior が維持される可能性があるが、AOSP gate 未確認のため断定しない。
- `READ_CONTACTS` permission を持つアプリではこの strict setting が適用されない可能性があるが、permission grant state、provider policy、other access restrictions は未確認である。

Conclusions:
- 現時点で顧客向けに確定できるのは、「公式文書上は Android 17 / targetSdkVersion 37 以上のアプリが `READ_CONTACTS` なしで `ContactsContract.Data` を query する場合、strict SQL validation により互換性のない query が exception で失敗する」という範囲まで。
- AOSP gate、ContactsProvider の permission / query validation 実装、exception type、compat framework default state が未確認のため、primary classification は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

## Applicability Gate Evidence

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

# Impact Analysis

## Affected Apps

影響を受ける可能性があるアプリ:
- `READ_CONTACTS` permission なしで `ContactsContract.Data` table を query しているアプリ。
- `ContactsContract.Data` query の projection、selection、sort order に SQL expression、関数、subquery、未定義 column、alias など strict validation と互換性がない可能性のある pattern を使っているアプリ。
- contacts data への限定アクセスを前提に、permission なしで lookup / filtering / search / matching を行うアプリ。
- targetSdkVersion 37 への更新を予定しており、Contacts Provider query grammar をまだ棚卸ししていないアプリ。

## Non-Affected Apps

影響が限定的または対象外と考えられるケース:
- Contacts Provider を使わないアプリ。
- `ContactsContract.Data` table を query しないアプリ。
- `READ_CONTACTS` permission を取得済みで、該当 provider access が許可されているアプリ。ただし AOSP gate 未確認のため断定しない。
- `ContactsContract.Data` query が strict columns / strict grammar と互換性のある単純な projection / selection / sort order だけを使うアプリ。
- Android 17 AOSP tag 取得後に対象外 gate や exemption が確認されたケース。

---

# Customer Impact

顧客説明用。

## Impact Level

- Human decision required

※ 仮評価。最終判断は人間が行う。

## Business Impact

- ユーザー影響: contacts search、lookup、候補表示、連携先 matching が query exception により失敗し、該当機能が動作しなくなる可能性がある。
- 運用影響: Contacts Provider query の SQL pattern、permission model、exception handling、targetSdkVersion 37 テストを確認する必要がある可能性がある。
- 開発影響: raw SQL 的な query fragment の削減、許可された columns / grammar への修正、`READ_CONTACTS` permission の必要性再評価、query exception handling の追加が必要になる可能性がある。

---

# Required Actions

## Must

- `ContactsContract.Data` query を棚卸しし、`READ_CONTACTS` permission なしで実行される path を特定する。
- projection、selection、selectionArgs、sortOrder に raw SQL fragment、関数、subquery、alias、未定義 column がないか確認する。
- strict columns / strict grammar と互換性がある query へ修正する。
- query exception を捕捉し、機能全体が crash しないよう error handling を確認する。
- Android 17 / targetSdkVersion 37 のテスト環境が利用可能になったら、`READ_CONTACTS` grant あり / なしの両方で query 結果を検証する。
- Android 17 AOSP tag 入手後に、targetSdkVersion gate、permission gate、exception type、compat Change ID を再確認する。

## Recommended

- contacts access が本当に `READ_CONTACTS` permission なしで成立する必要があるか、privacy / UX 観点で見直す。
- query をできるだけ documented columns と parameterized selection に寄せ、provider-specific SQL behavior への依存を減らす。
- test data と query test を追加し、targetSdkVersion 36 / 37、permission grant / denied の matrix を自動化する。
- Contacts Provider query failure をログとメトリクスで検出できるようにする。

## Optional

- `SQLiteQueryBuilder#setStrictColumns` / `setStrictGrammar` の既存仕様を参考に、アプリ内 query builder でも同等の validation を早期に走らせる。
- contacts feature の fallback UX を用意し、permission なしで query が拒否された場合の表示を整理する。

---

# Verification Method

## Matrix

| Device OS | targetSdkVersion | Compat flag | Expected behavior |
| --- | --- | --- | --- |
| Android 16 | 36 | default | Android 16 baseline。`READ_CONTACTS` なし Data query の strict validation は Android 17 tag 比較待ち。 |
| Android 17 | 36 | default | Unknown。この section は targetSdkVersion 37+ 向けだが、AOSP gate 未確認。 |
| Android 17 | 37 | default | 公式文書上、`READ_CONTACTS` なしで `ContactsContract.Data` を query すると strict columns / grammar が適用され、非互換 query は exception。 |
| Android 17 | 36 | force-enabled if available | Unknown。Compat Change ID 未確認。 |
| Android 17 | 37 | force-disabled if available | Unknown。Compat Change ID 未確認。 |

## Steps

- targetSdk変更: targetSdkVersion 36 と 37 の test build を用意する。
- compat framework command: 未確認。Android 17 compat framework entry / Change ID が判明後に記録する。
- テスト方法: `READ_CONTACTS` grant あり / なし、strict-compatible query / incompatible query を分けて `ContactsContract.Data` query を実行する。
- 再現手順: Android 17 device / emulator で対象アプリを install し、`READ_CONTACTS` を deny した状態で Data table query を実行する。projection、selection、sortOrder の pattern ごとに cursor / exception を記録する。
- 期待結果: targetSdkVersion 37 かつ `READ_CONTACTS` なしの場合、strict SQL validation と互換性のない query は rejected され exception が throw される。具体的な exception type は AOSP tag と実機検証待ち。

---

# Conclusion

公式文書上、Android 17 / targetSdkVersion 37 以上のアプリでは、`READ_CONTACTS` permission なしで `ContactsContract.Data` table を query する場合に CP2 が strict SQL checks を強制する。非互換 query は exception で失敗するため、permission なし Data query を持つアプリは SQL pattern と error handling の棚卸しが必要である。

ただし、Android 17 AOSP tag が local checkout にないため、実装 gate、ContactsProvider validation path、exception type、compat framework の確認は未完了である。最終的な適用分類と顧客向け確定説明は、Android 17 AOSP tag 入手後に再調査が必要である。

---

# Human Decision Placeholder

Final Priority:
- Human decision required

Final Severity:
- Human decision required

Release Readiness:
- Human decision required

Customer Communication Priority:
- Human decision required

Decision:
- Further investigation required

Decision notes:
- Android 17 AOSP tag 入手後に、AOSP evidence と compat framework evidence を確認してから最終判断する。

---

# References

## Documentation

- https://developer.android.com/about/versions/17/behavior-changes-17
- https://developer.android.com/reference/android/provider/ContactsContract.Data
- https://developer.android.com/reference/android/Manifest.permission#READ_CONTACTS
- https://developer.android.com/reference/android/database/sqlite/SQLiteQueryBuilder#setStrictColumns(boolean)
- https://developer.android.com/reference/android/database/sqlite/SQLiteQueryBuilder#setStrictGrammar(boolean)

## AOSP

- Not available for Android 17 in local `frameworks-base`.
- From tag checked: `android-16.0.0_r4`
- To tag checked: no local `android-17*` tag found.
