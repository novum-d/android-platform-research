# CP2 data view における PII fields の制限

## 基本情報（Metadata）

### 調査対象 Android バージョン（Android Versions）

比較元:
- android-16.0.0_r4

比較先:
- TBD: Android 17 AOSP tag

以前の targetSdkVersion:
- 36

対象 targetSdkVersion:
- 37

### Behavior Change 文書（Behavior Change Source）

文書:
https://developer.android.com/about/versions/17/behavior-changes-17

関連文書:
- https://developer.android.com/reference/android/provider/ContactsContract.SyncColumns#ACCOUNT_NAME
- https://developer.android.com/reference/android/provider/ContactsContract.SyncColumns#ACCOUNT_TYPE
- https://developer.android.com/reference/android/provider/ContactsContract.RawContactsColumns#ACCOUNT_TYPE_AND_DATA_SET
- https://developer.android.com/reference/android/provider/ContactsContract.Data
- https://developer.android.com/reference/android/provider/ContactsContract.RawContacts
- https://developer.android.com/reference/android/provider/ContactsContract.DataColumns#RAW_CONTACT_ID

セクション:
Restrict PII fields in CP2 data view

ページ種別:
- Android 17 以上をターゲットにするアプリ

### 分類スナップショット（Classification Snapshot）

主分類（Primary classification）:
- UNKNOWN_NEEDS_MORE_EVIDENCE

公式文書からの初期適用条件判断:
- 公式文書は、targetSdkVersion 37 以上のアプリに対して、Contacts Provider 2 (CP2) の data view から Personally Identifiable Information (PII) を含む一部 columns を制限すると説明している。
- 制限対象として `ACCOUNT_NAME`、`ACCOUNT_TYPE`、`ACCOUNT_TYPE_AND_DATA_SET` が示されている。
- これらの columns を `ContactsContract.Data` から使っているアプリは、`RAW_CONTACT_ID` で join し、`ContactsContract.RawContacts` から取得するよう案内されている。
- ただし、local `frameworks-base` に Android 17 AOSP tag がないため、data view projection filtering、targetSdkVersion gate、ContactsProvider 実装、compat framework entry、default state は未検証である。確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

早見表（At-a-glance impact）:

| 確認項目 | 回答 | 根拠 |
| --- | --- | --- |
| Android 17 に OS アップデートしただけで適用されるか | 未確認 | 公式文書は Android 17 / API level 37 以上をターゲットにするアプリと述べるが、AOSP gate は未確認。 |
| targetSdkVersion 37 以上が必要か | 可能性は高いが未検証 | 原文は targetSdkVersion 37 以上を明示している。 |
| 追加の実行時条件があるか | ある | CP2 `ContactsContract.Data` data view で PII columns を query する場合。 |
| Compat Change ID が関係するか | 未確認 | Android 17 tag と compat framework evidence が未確認。 |

### 調査日（Investigation Date）

2026-06-10

### 信頼度（Confidence）

- Low

### 適用条件分類（Applicability Classification）

適用される条件（Applies when）:
- [ ] targetSdkVersion に関係なく Android 17 の全アプリへ適用
- [ ] Android 17 以上かつ targetSdkVersion 37 以上で適用
- [ ] targetSdkVersion 37 以上かつ追加の実行時条件を満たす場合に適用
- [ ] Mainline / Google Play system update に依存
- [ ] API 追加のみであり、挙動変更ではない
- [x] 未確認 / 追加 evidence が必要

必要な実行時条件（Required runtime conditions）:
- Android version: Android 17 以上が前提と考えられるが、AOSP tag 未取得。
- targetSdkVersion: 公式文書上は 37 以上。
- Device/form factor: 公式抜粋では条件なし。
- Permission/API/component condition: Contacts Provider / `ContactsContract.Data` data view query、`ACCOUNT_NAME`、`ACCOUNT_TYPE`、`ACCOUNT_TYPE_AND_DATA_SET`、`RAW_CONTACT_ID`、`ContactsContract.RawContacts`。
- App state/process condition: アプリが CP2 data view に対して該当 columns を query する時点。

Compat framework:
- Change ID: 未確認
- 変更名: 未確認
- 既定状態: 未確認
- テスト時に切り替え可能か: 未確認

分類信頼度（Classification confidence）:
- Low

分類根拠（Classification evidence）:
- 公式ドキュメントページ: `behavior-changes-17`
- 検証対象の適用条件文: apps targeting Android 17 / API level 37 and higher, CP2 data view restricts PII columns, affected apps should read from `RawContacts` by joining with `RAW_CONTACT_ID`。
- AOSP targetSdk gate: 未確認。local `frameworks-base` に `android-17*` tag がない。
- Compat framework entry: 未確認。Android 17 compat framework evidence が未取得。

---

# エグゼクティブサマリー（Executive Summary）

Android 17 では、targetSdkVersion 37 以上のアプリに対し、Contacts Provider 2 (CP2) の `ContactsContract.Data` data view から `ACCOUNT_NAME`、`ACCOUNT_TYPE`、`ACCOUNT_TYPE_AND_DATA_SET` が削除される、と公式文書は説明している。目的は account information という PII の露出を減らし、ユーザー privacy を強化することである。

これらの columns を `ContactsContract.Data` から直接読んでいるアプリは、targetSdkVersion 37 更新後に cursor projection / column lookup / data mapping が壊れる可能性がある。公式文書は代替として、`RAW_CONTACT_ID` で `ContactsContract.RawContacts` と join し、RawContacts 側から取得する方法を案内している。

ただし、現時点の local `frameworks-base` には Android 17 AOSP tag がないため、実装差分、targetSdkVersion gate、ContactsProvider の filtering path、Compat Change ID は未確認である。

---

# 公式ドキュメント確認

## 原文（Statement）

ページタイトル:
- Behavior changes: Apps targeting Android 17 or higher

ページ URL:
- https://developer.android.com/about/versions/17/behavior-changes-17

ページ種別:
- Android 17 をターゲットにするアプリ

セクションタイトル:
- Restrict PII fields in CP2 data view

検証対象の原文:

> For apps targeting Android 17 (API level Android 17 (API level 37)) and higher, Contacts Provider 2 (CP2) restricts certain columns containing Personally Identifiable Information (PII) from the data view.

公式文書は、変更が enabled の場合、`ACCOUNT_NAME`、`ACCOUNT_TYPE`、`ACCOUNT_TYPE_AND_DATA_SET` が data view から removed されると説明している。これらの columns を `ContactsContract.Data` から使っているアプリは、`RAW_CONTACT_ID` で join し、代わりに `ContactsContract.RawContacts` から取得する必要がある。

## 解釈（Interpretation）

この変更は、Contacts Provider の data view から account identity に関係する columns を直接取得できないようにする privacy behavior change である。`ContactsContract.Data` は連絡先の詳細データを扱う view であり、そこに account name / type が混在すると、必要以上に account PII が取得される可能性がある。

アプリ開発者にとって重要なのは、`ContactsContract.Data` query の projection に該当 columns を含めている場合、targetSdkVersion 37 以降で column が存在しない、または値が得られない可能性がある点である。account 情報が必要な場合は、`RAW_CONTACT_ID` を使って `ContactsContract.RawContacts` 側から取得する設計へ変更する必要がある。

---

# 変更内容（What Changed）

公式文書上の変更点:
- Android 17 / targetSdkVersion 37 以上のアプリでは、CP2 data view から PII を含む一部 columns が制限される。
- 制限対象 columns は `ACCOUNT_NAME`、`ACCOUNT_TYPE`、`ACCOUNT_TYPE_AND_DATA_SET`。
- 変更が enabled の場合、これらの columns は data view から removed される。
- `ContactsContract.Data` からこれらの columns を使っているアプリは、`RAW_CONTACT_ID` で join して `ContactsContract.RawContacts` から取得する必要がある。

AOSP で未確認の点:
- Android 16 baseline で `ContactsContract.Data` data view が `ACCOUNT_NAME`、`ACCOUNT_TYPE`、`ACCOUNT_TYPE_AND_DATA_SET` を返していたか。
- Android 17 で data view から該当 columns を削除 / filter する実装箇所。
- targetSdkVersion 37 gate の実装箇所。
- projection に制限対象 column を指定した場合の failure mode。例: column missing、ignored projection、query exception、cursor column index -1、null。
- `ContactsContract.RawContacts` での代替取得 path と permission / visibility 条件。
- Contacts Provider 実装が `frameworks-base` ではなく `packages/providers/ContactsProvider` に存在する場合の evidence boundary。
- Compat Change ID と default state。

## 適用条件（Applicability）

公式文書の一次判断では、Android 17 以上、targetSdkVersion 37 以上、`ContactsContract.Data` data view から制限対象 PII columns を query するアプリに適用される。AOSP tag が未取得のため、確定分類は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

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
- permission: contacts read permission / Contacts Provider access が関係する可能性があるが、今回の変更自体の permission gate は AOSP 未確認。
- API usage: `ContactsContract.Data` query、`ContactsContract.RawContacts` query、`RAW_CONTACT_ID` join、`ACCOUNT_NAME`、`ACCOUNT_TYPE`、`ACCOUNT_TYPE_AND_DATA_SET`。
- manifest attribute: 公式抜粋では条件なし。contacts permission declaration が関係する可能性はあるが AOSP 未確認。
- component boundary: app process、ContentResolver query、Contacts Provider 2 data view、RawContacts table / view、projection filtering にまたがる。

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
- `core/api/current.txt`
- `core/api/system-current.txt`
- compat framework 定義ファイル内の CP2 / ContactsProvider / Data view / targetSdkVersion 37 関連 Change ID
- `packages/providers/ContactsProvider` 側の ContactsProvider2 実装、data view projection / query builder / account column filtering path

Note:
- `frameworks-base` には `ContactsContract` constants と API surface が含まれる可能性がある。一方、実際の CP2 query filtering は ContactsProvider 実装側にある可能性が高い。今回の repository rule では `frameworks-base` evidence を優先するが、最終 confidence には provider implementation evidence が必要である。

## 確認したソース文脈（Source Context Reviewed）

Android 17 AOSP tag がないため、source context は未レビュー。

| File / symbol | Android 16 baseline | Android 17 behavior | 関連性 |
| --- | --- | --- | --- |
| 未レビュー | 未レビュー | 未レビュー | Android 17 tag がないため、公式文書の記述を AOSP diff で検証できない。 |

必要な context:
- Entry point / caller: 未確認。想定される entry point は app の `ContentResolver.query(ContactsContract.Data.CONTENT_URI, projection, ...)`、ContactsProvider query routing、data view projection filtering、RawContacts join だが、AOSP evidence としては未採用。
- 関連 class / service の責務: 未確認。
- app API / system event から変更箇所までの runtime path: 未確認。
- 関係しない code path を除外した理由: Android 17 tag 不在のため、source path の採否判断自体を保留。

## 差分解釈（Diff Interpretation）

| 観測した diff | 解釈 | Behavior Change との関連 | 信頼度 |
| --- | --- | --- | --- |
| Android 17 tag diff なし | Source diff type はまだ分類できない | 公式文書の PII column removal、targetSdkVersion gate、Data view filtering、RawContacts 代替 path を source diff で裏取りできていない | Low |

必要な解釈:
- Added behavior: 未確認。
- Removed behavior: 未確認。公式文書上は data view から columns が removed されるため removed behavior の可能性がある。
- Changed condition / gate: 未確認。targetSdkVersion 37 gate がある可能性は高いが、AOSP 未確認。
- Changed default: 未確認。
- No behavior change found: 未確認。tag 不在のため「no behavior change」とは判断しない。

## 事実（Evidence）

事実:
- 公式 Behavior Change 文書は、targetSdkVersion 37 以上のアプリに対し、CP2 data view から PII を含む certain columns を制限すると述べている。
- 公式文書は、変更が enabled の場合、これらの columns が data view から removed されると述べている。
- 公式文書は、制限対象 columns として `ACCOUNT_NAME`、`ACCOUNT_TYPE`、`ACCOUNT_TYPE_AND_DATA_SET` を列挙している。
- 公式文書は、これらを `ContactsContract.Data` から使っているアプリに、`RAW_CONTACT_ID` で join して `ContactsContract.RawContacts` から取得するよう案内している。
- local `frameworks-base` には `android-16.0.0_r4` tag がある。
- local `frameworks-base` には `android-17*` tag がない。
- 調査時点で `frameworks-base` working tree は clean。

観察:
- 公式ページ種別は targetSdkVersion 37 以上向けである。
- 原文は targetSdkVersion 37 以上を明示しており、targetSdkVersion 37 gate がある可能性が高い。
- この項目は targetSdkVersion 37 条件に加えて、`ContactsContract.Data` data view query と特定 PII columns の projection / access という API usage condition を含む。
- 代替取得先として `ContactsContract.RawContacts` が示されているため、account 情報そのものが完全に取得不能になる変更ではなく、Data view からの露出を減らす変更と読める。
- AOSP tag がないため、実装が本当に targetSdkVersion 37 gate で制御されているかは未確認。
- Compat framework entry の有無も未確認。

仮説:
- Android 17 / targetSdkVersion 37 以上では、`ContactsContract.Data` query の projection に `ACCOUNT_NAME`、`ACCOUNT_TYPE`、`ACCOUNT_TYPE_AND_DATA_SET` を含めると、cursor から該当 columns が得られない可能性が高い。
- Android 17 / targetSdkVersion 36 のアプリでは旧 Data view behavior が維持される可能性があるが、AOSP gate 未確認のため断定しない。
- `ContactsContract.RawContacts` への join は代替 path として機能する可能性が高いが、contacts permission、profile / account visibility、sync adapter context などの追加条件は未確認である。

結論:
- 現時点で顧客向けに確定できるのは、「公式文書上は Android 17 / targetSdkVersion 37 以上のアプリで、CP2 Data view から account PII columns が removed され、RawContacts + RAW_CONTACT_ID join への移行が必要になる」という範囲まで。
- AOSP gate、ContactsProvider の filtering 実装、failure mode、compat framework default state が未確認のため、primary classification は `UNKNOWN_NEEDS_MORE_EVIDENCE` とする。

## 適用ゲート根拠（Applicability Gate Evidence）

- targetSdkVersion gate: 未確認。公式文書は targetSdkVersion 37 以上を示すが、AOSP gate evidence はない。
- CompatChanges.isChangeEnabled / ChangeId: 未確認。Android 17 tag がないため検索未実施。
- @EnabledAfter / @EnabledSince / default state: 未確認。Android 17 tag がないため検索未実施。
- Build.VERSION / SDK_INT gate: 未確認。
- DeviceConfig / resources config: 未確認。
- Permission/AppOps gate: 未確認。contacts permission / provider access が関係する可能性はあるが、今回の behavior gate としては未確認。
- Manifest/property gate: 未確認。
- No gate found: 未確認。Android 17 tag がないため「gate がない」とは判断しない。
- Gate conclusion: 未確認。公式文書の wording から targetSdkVersion 37 + `ContactsContract.Data` query + restricted columns と推定されるが、AOSP で検証できていない。
- Reasoning from source context: source context 未レビューのため未確定。

---

# 影響分析（Impact Analysis）

## 影響を受けるアプリ（Affected Apps）

影響を受ける可能性があるアプリ:
- `ContactsContract.Data` query で `ACCOUNT_NAME`、`ACCOUNT_TYPE`、`ACCOUNT_TYPE_AND_DATA_SET` を projection に含めているアプリ。
- contacts の data row と account identity を同じ cursor で処理しているアプリ。
- 連絡先の同期元 account、account type、data set を使って UI filtering、重複排除、同期、移行、backup / restore、CRM 連携を行うアプリ。
- targetSdkVersion 37 への更新を予定しており、Contacts Provider query の projection / cursor column handling をまだ棚卸ししていないアプリ。

## 影響を受けないアプリ（Non-Affected Apps）

影響が限定的または対象外と考えられるケース:
- Contacts Provider を使わないアプリ。
- `ContactsContract.Data` を query していても、制限対象 columns を projection に含めていないアプリ。
- account information を `ContactsContract.RawContacts` から取得しているアプリ。
- Android 17 AOSP tag 取得後に対象外 gate や exemption が確認されたケース。

---

# 顧客影響（Customer Impact）

## 影響度

- 人間による判断が必要

※ 最終 severity / priority は人間が判断する。このレポートでは確定しない。

## ビジネス影響（Business Impact）

- ユーザー影響: contacts feature の account 表示、filtering、同期元識別、重複排除が壊れると、連絡先管理や連携機能の表示・分類が不正確になる可能性がある。
- 運用影響: contacts query の projection と cursor handling、RawContacts join の導入、permission / privacy review を確認する必要がある可能性がある。
- 開発影響: `ContactsContract.Data` 依存の修正、`RAW_CONTACT_ID` join logic、missing column に強い cursor handling、targetSdkVersion 37 環境での contacts query test が必要になる可能性がある。

---

# サービス影響例（Service Impact Examples）

このセクションは、公式文書と AOSP evidence から導いた「起こりうる影響例」を記録する。特定サービスで実際に発生確認した事実ではない。

## 例1（Example 1）: 連絡先同期 / CRM 連携

- 対象サービス例: CRM、営業支援、顧客管理、連絡先 backup / restore。
- 影響を受ける実装パターン: `ContactsContract.Data` query から `ACCOUNT_NAME` / `ACCOUNT_TYPE` を直接読み、同期元 account を識別する実装。
- 発生条件: Android 17 / targetSdkVersion 37 で CP2 Data view から restricted columns が removed される場合。
- ユーザーに見える症状: 連絡先の同期元表示、filtering、重複排除が不正確になる可能性。
- 開発・運用への影響: RawContacts join、cursor handling、privacy review の見直しが必要になる可能性。
- 推奨対応候補: `RAW_CONTACT_ID` で `ContactsContract.RawContacts` と join して account 情報を取得する。
- 根拠: 公式 statement と report の expected behavior。
- 信頼度: Low
- 注意: 実際の failure mode は AOSP tag / 実機検証待ち。

## 例2（Example 2）: 連絡先 picker / account filter UI

- 対象サービス例: メール、電話帳、メッセージ、グループウェア。
- 影響を受ける実装パターン: Data row と account type を同一 cursor で処理し、UI 上の account filter に使う実装。
- 発生条件: Data view query の projection に restricted columns を含めている場合。
- ユーザーに見える症状: account filter が空になる、表示分類が崩れる、cursor column lookup でクラッシュする可能性。
- 開発・運用への影響: projection 修正、missing column 耐性、RawContacts query の performance 検証が必要になる可能性。
- 推奨対応候補: Data view から account PII を取る前提をやめ、RawContacts 側の documented columns を使う。
- 根拠: 公式 statement と report の action candidates。
- 信頼度: Low
- 注意: ContactsProvider implementation evidence は未確認。

---

# 対応候補（Required Actions）

## 必須対応（Must）

- `ContactsContract.Data` query の projection に `ACCOUNT_NAME`、`ACCOUNT_TYPE`、`ACCOUNT_TYPE_AND_DATA_SET` が含まれていないか検索する。
- 該当 columns を使っている場合、`ContactsContract.RawContacts` を `RAW_CONTACT_ID` で join する取得設計へ移行する。
- cursor column index が存在しない場合に crash しないよう、`getColumnIndex()` / projection handling / null handling を確認する。
- Android 17 / targetSdkVersion 37 のテスト環境が利用可能になったら、Data view と RawContacts join の query 結果を比較する。
- Android 17 AOSP tag 入手後に、targetSdkVersion gate、failure mode、compat Change ID を再確認する。

## 推奨対応（Recommended）

- account PII を本当にアプリ機能に必要としているか見直し、不要な取得を削減する。
- contacts permission と privacy disclosure を見直し、Data view から得られなくなる情報を別経路で取得する必要性を説明できるようにする。
- Contacts Provider query を projection 固定ではなく、missing column に耐える実装へ寄せる。
- RawContacts join の performance と paging / batching 影響を検証する。

## 任意対応（Optional）

- contacts sync / backup / CRM 連携など account type に依存する機能について、account 情報が取得できない場合の fallback UX を用意する。
- profile contacts、work profile、複数 account、data set あり / なしの test data を増やす。

---

# 検証方法（Verification Method）

## 検証マトリクス（Matrix）

| 端末 OS | targetSdkVersion | Compat flag | 期待される挙動 |
| --- | --- | --- | --- |
| Android 16 | 36 | default | Android 16 baseline。Data view の restricted columns 可視性は Android 17 tag 比較待ち。 |
| Android 17 | 36 | default | 未確認。この section は targetSdkVersion 37 以上向けだが、AOSP gate 未確認。 |
| Android 17 | 37 | default | 公式文書上、CP2 Data view から `ACCOUNT_NAME`、`ACCOUNT_TYPE`、`ACCOUNT_TYPE_AND_DATA_SET` が removed。 |
| Android 17 | 36 | force-enabled if available | 未確認。Compat Change ID 未確認。 |
| Android 17 | 37 | force-disabled if available | 未確認。Compat Change ID 未確認。 |

## 手順（Steps）

- targetSdk変更: targetSdkVersion 36 と 37 の test build を用意する。
- compat framework command: 未確認。Android 17 compat framework entry / Change ID が判明後に記録する。
- テスト方法: 同じ contact database に対して、`ContactsContract.Data` の projection に restricted columns を含める query と、`ContactsContract.RawContacts` へ `RAW_CONTACT_ID` で join する query を比較する。
- 再現手順: Android 17 device / emulator で対象アプリを install し、targetSdkVersion 36 / 37 の両方で Data view query を実行する。cursor column list、column index、値、exception の有無を記録する。
- 期待結果: targetSdkVersion 37 のアプリでは、Data view から restricted columns が取得できず、RawContacts 経由の取得が必要になる。具体的な failure mode は AOSP tag と実機検証待ち。

---

# 結論（Conclusion）

公式文書上、Android 17 / targetSdkVersion 37 以上のアプリでは CP2 Data view から `ACCOUNT_NAME`、`ACCOUNT_TYPE`、`ACCOUNT_TYPE_AND_DATA_SET` が removed される。これらを `ContactsContract.Data` から直接読んでいるアプリは、`RAW_CONTACT_ID` で `ContactsContract.RawContacts` と join する設計へ移行する必要がある。

ただし、Android 17 AOSP tag が local checkout にないため、実装 gate、ContactsProvider filtering path、failure mode、compat framework の確認は未完了である。最終的な適用分類と顧客向け確定説明は、Android 17 AOSP tag 入手後に再調査が必要である。

---

# 人間の判断欄

最終優先度（Final Priority）:
- 人間による判断が必要

最終影響度:
- 人間による判断が必要

リリース判断:
- 人間による判断が必要

顧客連絡の優先度:
- 人間による判断が必要

判断（Decision）:
- 追加調査が必要

判断メモ:
- Android 17 AOSP tag 入手後に、AOSP evidence と compat framework evidence を確認してから最終判断する。

---

# 参照（References）

## ドキュメント（Documentation）

- https://developer.android.com/about/versions/17/behavior-changes-17
- https://developer.android.com/reference/android/provider/ContactsContract.SyncColumns#ACCOUNT_NAME
- https://developer.android.com/reference/android/provider/ContactsContract.SyncColumns#ACCOUNT_TYPE
- https://developer.android.com/reference/android/provider/ContactsContract.RawContactsColumns#ACCOUNT_TYPE_AND_DATA_SET
- https://developer.android.com/reference/android/provider/ContactsContract.Data
- https://developer.android.com/reference/android/provider/ContactsContract.RawContacts
- https://developer.android.com/reference/android/provider/ContactsContract.DataColumns#RAW_CONTACT_ID

## AOSP

- local `frameworks-base` では Android 17 は利用不可。
- 確認済みの比較元 tag: `android-16.0.0_r4`
- 確認済みの比較先 tag: local `android-17*` tag なし。
